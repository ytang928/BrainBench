#!/usr/bin/env python3
"""Main benchmark runner for the AI Brainteaser Benchmark."""

import argparse
import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv
from tqdm import tqdm

from models import ModelConfig, ModelResponse, query_model
from judge import judge_response

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parent.parent

# Default testset: v1 (original)
DEFAULT_TESTSET = "v1"

# Testset registry: maps testset name -> (questions_file, categories_file)
TESTSETS = {
    "v1": ("brainteasers.json", "brainteaser_categories.json"),
    "v2": ("brainteasers_v2.json", "brainteaser_categories_v2.json"),
    "v2_refined": ("brainteasers_v2_refined.json", "brainteaser_categories_v2_refined.json"),
    "v3": ("brainteasers_v3.json", "brainteaser_categories_v3.json"),
    "v3_chinese": ("brainteasers_v3_chinese.json", "brainteaser_categories_v3_chinese.json"),
}


def load_config(config_path: str = "config.yaml") -> dict:
    with open(Path(__file__).parent / config_path) as f:
        return yaml.safe_load(f)


def resolve_testset(testset: str, data_dir: str) -> tuple[str, str]:
    """Resolve testset name to (questions_file, categories_file).

    If testset is a registered name, use the mapping.
    Otherwise treat it as a questions filename directly.
    """
    if testset in TESTSETS:
        return TESTSETS[testset]
    # Fallback: treat as a direct filename
    return (testset, "brainteaser_categories.json")


def load_questions(data_dir: str, testset: str = DEFAULT_TESTSET) -> list[dict]:
    questions_file, _ = resolve_testset(testset, data_dir)
    path = ROOT_DIR / data_dir / questions_file
    with open(path) as f:
        return json.load(f)


def parse_model_configs(config: dict) -> list[ModelConfig]:
    models = []
    for m in config["models"]:
        if not m.get("enabled", True):
            continue
        models.append(ModelConfig(
            name=m["name"],
            provider=m["provider"],
            model_id=m["model_id"],
            enabled=True,
            base_url=m.get("base_url"),
            api_key_env=m.get("api_key_env"),
            reasoning_effort=m.get("reasoning_effort"),
            max_tokens=m.get("max_tokens"),
        ))
    return models


def get_raw_path(output_dir: str, testset: str, model_name: str, question_id: int, run: int) -> Path:
    p = ROOT_DIR / output_dir / testset / "raw" / model_name
    p.mkdir(parents=True, exist_ok=True)
    return p / f"q{question_id:03d}_run{run:02d}.json"


def is_complete(output_dir: str, testset: str, model_name: str, question_id: int, run: int) -> bool:
    path = get_raw_path(output_dir, testset, model_name, question_id, run)
    if not path.exists():
        return False
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("response_text", "") != "" and data.get("error") is None
    except (json.JSONDecodeError, KeyError):
        return False


def save_raw(output_dir: str, testset: str, result: dict) -> None:
    path = get_raw_path(
        output_dir, testset, result["model_name"], result["question_id"], result["run_number"]
    )
    with open(path, "w") as f:
        json.dump(result, f, indent=2)


async def run_single(
    semaphore: asyncio.Semaphore,
    model_config: ModelConfig,
    question: dict,
    run_number: int,
    max_tokens: int,
    output_dir: str,
    testset: str,
    judge_model: str,
) -> dict:
    """Run a single question against a single model, then judge it."""
    async with semaphore:
        # Query model
        resp: ModelResponse = await query_model(
            config=model_config,
            question=question["question"],
            question_id=question["id"],
            run_number=run_number,
            max_tokens=max_tokens,
        )

        result = {
            "model_name": resp.model_name,
            "question_id": resp.question_id,
            "run_number": resp.run_number,
            "testset": testset,
            "question": question["question"],
            "ground_truth": question["answer"],
            "category": question["category"],
            "response_text": resp.response_text,
            "input_tokens": resp.input_tokens,
            "output_tokens": resp.output_tokens,
            "error": resp.error,
        }

        # Judge correctness (skip if model errored)
        if resp.error:
            result["judgment"] = {"correct": False, "reasoning": "Model error", "error": resp.error}
        else:
            judgment = await judge_response(
                question=question["question"],
                ground_truth=question["answer"],
                response=resp.response_text,
                judge_model=judge_model,
            )
            result["judgment"] = judgment

        # Save raw result
        save_raw(output_dir, testset, result)
        return result


async def run_benchmark(
    config: dict,
    testset: str = DEFAULT_TESTSET,
    models: list[ModelConfig] | None = None,
    question_ids: list[int] | None = None,
    runs: int | None = None,
    resume: bool = True,
) -> list[dict]:
    """Run the full benchmark."""
    questions = load_questions(config["data_dir"], testset=testset)
    all_models = models or parse_model_configs(config)
    num_runs = runs or config["runs_per_question"]
    max_tokens = config.get("max_tokens", 8192)
    output_dir = config["output_dir"]
    judge_model = config["judge"]["model_id"]
    max_concurrent = config.get("max_concurrent_requests", 5)

    # Filter questions if specified
    if question_ids:
        questions = [q for q in questions if q["id"] in question_ids]

    # Build task list
    tasks_to_run = []
    for model_config in all_models:
        for question in questions:
            for run in range(1, num_runs + 1):
                if resume and is_complete(output_dir, testset, model_config.name, question["id"], run):
                    continue
                tasks_to_run.append((model_config, question, run))

    total = len(tasks_to_run)
    if total == 0:
        logger.info("All tasks already complete. Nothing to run.")
        return []

    skipped = (len(all_models) * len(questions) * num_runs) - total
    logger.info(
        f"[testset={testset}] Running {total} tasks ({skipped} already complete) | "
        f"{len(all_models)} models × {len(questions)} questions × {num_runs} runs"
    )

    semaphore = asyncio.Semaphore(max_concurrent)

    # Create async tasks with progress bar
    pbar = tqdm(total=total, desc=f"Benchmark ({testset})", unit="task")

    async def run_with_progress(model_config, question, run_num):
        result = await run_single(
            semaphore, model_config, question, run_num,
            max_tokens, output_dir, testset, judge_model,
        )
        pbar.update(1)
        correct = result["judgment"].get("correct", False)
        status = "✓" if correct else "✗"
        pbar.set_postfix_str(f"{model_config.name} q{question['id']} {status}")
        return result

    coros = [
        run_with_progress(mc, q, r)
        for mc, q, r in tasks_to_run
    ]
    results = await asyncio.gather(*coros, return_exceptions=True)
    pbar.close()

    # Filter out exceptions
    valid_results = []
    for r in results:
        if isinstance(r, Exception):
            logger.error(f"Task exception: {r}")
        else:
            valid_results.append(r)

    # Aggregate scores (pass None to discover ALL models with results)
    aggregate_scores(config, testset, None, questions, num_runs)

    return valid_results


def aggregate_scores(
    config: dict,
    testset: str,
    models: list[ModelConfig] | None,
    questions: list[dict],
    num_runs: int,
) -> dict:
    """Aggregate raw results into scores.json.

    Discovers ALL models with results in the raw directory, not just
    the ones passed in. This makes it safe to call from parallel runs.
    """
    output_dir = config["output_dir"]
    raw_dir = ROOT_DIR / output_dir / testset / "raw"

    # Discover all model dirs that have results, merge with passed models
    model_names_from_dir = set()
    if raw_dir.exists():
        model_names_from_dir = {d.name for d in raw_dir.iterdir() if d.is_dir() and any(d.iterdir())}

    # Build model name list: union of passed models + discovered dirs
    all_model_names = set()
    if models:
        all_model_names.update(m.name for m in models)
    all_model_names.update(model_names_from_dir)

    scores = {"testset": testset, "models": {}, "meta": {"num_runs": num_runs, "num_questions": len(questions)}}

    for model_name in sorted(all_model_names):
        model_scores = {
            "overall_correct": 0,
            "overall_total": 0,
            "by_category": {},
            "by_question": {},
            "total_input_tokens": 0,
            "total_output_tokens": 0,
        }

        for question in questions:
            q_correct = 0
            q_total = 0
            cat = question["category"]

            if cat not in model_scores["by_category"]:
                model_scores["by_category"][cat] = {"correct": 0, "total": 0}

            for run in range(1, num_runs + 1):
                path = get_raw_path(output_dir, testset, model_name, question["id"], run)
                if not path.exists():
                    continue

                try:
                    with open(path) as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

                correct = data.get("judgment", {}).get("correct", False)
                q_total += 1
                model_scores["overall_total"] += 1
                model_scores["by_category"][cat]["total"] += 1
                model_scores["total_input_tokens"] += data.get("input_tokens", 0)
                model_scores["total_output_tokens"] += data.get("output_tokens", 0)

                if correct:
                    q_correct += 1
                    model_scores["overall_correct"] += 1
                    model_scores["by_category"][cat]["correct"] += 1

            model_scores["by_question"][str(question["id"])] = {
                "correct": q_correct,
                "total": q_total,
                "accuracy": q_correct / q_total if q_total > 0 else 0,
            }

        # Compute derived metrics
        total = model_scores["overall_total"]
        model_scores["overall_accuracy"] = (
            model_scores["overall_correct"] / total if total > 0 else 0
        )

        for cat_data in model_scores["by_category"].values():
            cat_data["accuracy"] = (
                cat_data["correct"] / cat_data["total"] if cat_data["total"] > 0 else 0
            )

        # Consistency: fraction of questions where model gets 100% of runs correct
        reliable = 0
        q_count = 0
        for q_data in model_scores["by_question"].values():
            if q_data["total"] > 0:
                q_count += 1
                if q_data["accuracy"] == 1.0:
                    reliable += 1
        model_scores["reliability"] = reliable / q_count if q_count > 0 else 0

        scores["models"][model_name] = model_scores

    # Save per-testset scores
    scores_dir = ROOT_DIR / output_dir / testset
    scores_dir.mkdir(parents=True, exist_ok=True)
    scores_path = scores_dir / "scores.json"
    with open(scores_path, "w") as f:
        json.dump(scores, f, indent=2)

    logger.info(f"Scores saved to {scores_path}")
    return scores


def check_completeness(config: dict, testset: str = DEFAULT_TESTSET) -> None:
    """Check which tasks are complete vs missing."""
    questions = load_questions(config["data_dir"], testset=testset)
    models = parse_model_configs(config)
    num_runs = config["runs_per_question"]
    output_dir = config["output_dir"]

    print(f"Testset: {testset}")
    for model_config in models:
        complete = 0
        missing = 0
        errors = 0
        for question in questions:
            for run in range(1, num_runs + 1):
                path = get_raw_path(output_dir, testset, model_config.name, question["id"], run)
                if not path.exists():
                    missing += 1
                else:
                    try:
                        with open(path) as f:
                            data = json.load(f)
                        if data.get("error"):
                            errors += 1
                        else:
                            complete += 1
                    except (json.JSONDecodeError, FileNotFoundError):
                        missing += 1

        total = len(questions) * num_runs
        print(
            f"{model_config.name:25s} | "
            f"complete: {complete:4d}/{total} | "
            f"missing: {missing:4d} | "
            f"errors: {errors:4d}"
        )


def parse_question_range(s: str) -> list[int]:
    """Parse '1-5' or '1,3,5' or '42' into a list of ints."""
    ids = []
    for part in s.split(","):
        if "-" in part:
            start, end = part.split("-", 1)
            ids.extend(range(int(start), int(end) + 1))
        else:
            ids.append(int(part))
    return ids


def main():
    parser = argparse.ArgumentParser(description="AI Brainteaser Benchmark Runner")
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    parser.add_argument("--testset", default=DEFAULT_TESTSET,
                        help=f"Testset name (registered: {list(TESTSETS.keys())}). Default: {DEFAULT_TESTSET}")
    parser.add_argument("--model", help="Run only this model (by name)")
    parser.add_argument("--questions", help="Question IDs to run (e.g., '1-5' or '1,3,5')")
    parser.add_argument("--runs", type=int, help="Override number of runs per question")
    parser.add_argument("--no-resume", action="store_true", help="Don't skip completed tasks")
    parser.add_argument("--check", action="store_true", help="Check completeness only")
    parser.add_argument("--aggregate-only", action="store_true", help="Only re-aggregate scores")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.check:
        check_completeness(config, testset=args.testset)
        return

    if args.aggregate_only:
        questions = load_questions(config["data_dir"], testset=args.testset)
        models = parse_model_configs(config)
        aggregate_scores(config, args.testset, models, questions, config["runs_per_question"])
        return

    # Filter to single model if specified
    models = None
    if args.model:
        all_models = parse_model_configs(config)
        models = [m for m in all_models if m.name == args.model]
        if not models:
            print(f"Model '{args.model}' not found. Available: {[m.name for m in all_models]}")
            sys.exit(1)

    question_ids = None
    if args.questions:
        question_ids = parse_question_range(args.questions)

    asyncio.run(run_benchmark(
        config=config,
        testset=args.testset,
        models=models,
        question_ids=question_ids,
        runs=args.runs,
        resume=not args.no_resume,
    ))


if __name__ == "__main__":
    main()
