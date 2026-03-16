"""LLM-based answer judge for the AI Brainteaser Benchmark."""

import json
import logging

import anthropic

logger = logging.getLogger(__name__)

JUDGE_PROMPT = """\
You are a strict but fair judge evaluating whether an AI model correctly answered a brainteaser question.

## Question
{question}

## Ground-Truth Answer
{ground_truth}

## Model's Response
{response}

## Instructions
Determine if the model's response arrives at the CORRECT answer. Be strict on correctness but lenient on phrasing:
- The model must clearly commit to the correct answer (not just mention it among options)
- The model may phrase the answer differently — that's fine as long as the core conclusion matches
- If the model hedges with "it depends" and never commits, mark it INCORRECT
- If the model gives the right answer but with wrong reasoning, still mark it CORRECT (we're testing the answer, not the explanation)
- If the model gives no answer (empty, error, refusal), mark it INCORRECT

Respond with ONLY a JSON object, no other text:
{{"correct": true or false, "reasoning": "one sentence explaining your judgment"}}"""


async def judge_response(
    question: str,
    ground_truth: str,
    response: str,
    judge_model: str = "claude-sonnet-4-20250514",
) -> dict:
    """Judge whether a model response is correct.

    Returns:
        {"correct": bool, "reasoning": str, "error": str|None}
    """
    if not response or not response.strip():
        return {"correct": False, "reasoning": "Empty response", "error": None}

    prompt = JUDGE_PROMPT.format(
        question=question,
        ground_truth=ground_truth,
        response=response,
    )

    try:
        client = anthropic.AsyncAnthropic()
        resp = await client.messages.create(
            model=judge_model,
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in resp.content if block.type == "text")

        # Parse JSON from response (handle possible markdown wrapping)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        result = json.loads(text)
        return {
            "correct": bool(result.get("correct", False)),
            "reasoning": result.get("reasoning", ""),
            "error": None,
        }
    except json.JSONDecodeError as e:
        logger.error(f"Judge returned non-JSON: {text[:200]}")
        return {"correct": False, "reasoning": "", "error": f"JSON parse error: {e}"}
    except Exception as e:
        logger.error(f"Judge error: {e}")
        return {"correct": False, "reasoning": "", "error": str(e)}
