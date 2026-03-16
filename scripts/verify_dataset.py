#!/usr/bin/env python3
"""Verify the brainteaser dataset for consistency and completeness."""

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"


def main():
    # Load data
    with open(DATA_DIR / "brainteasers.json") as f:
        questions = json.load(f)
    with open(DATA_DIR / "brainteaser_categories.json") as f:
        categories = json.load(f)

    errors = []
    warnings = []

    # Check questions
    ids_seen = set()
    categories_seen = set()

    for q in questions:
        qid = q.get("id")
        if qid is None:
            errors.append(f"Question missing 'id': {q.get('question', '???')[:50]}")
            continue
        if qid in ids_seen:
            errors.append(f"Duplicate question id: {qid}")
        ids_seen.add(qid)

        if not q.get("question", "").strip():
            errors.append(f"Q{qid}: Empty question text")
        if not q.get("answer", "").strip():
            errors.append(f"Q{qid}: Empty answer text")
        if not q.get("category", "").strip():
            errors.append(f"Q{qid}: Missing category")
        else:
            categories_seen.add(q["category"])

    # Check sequential IDs
    expected_ids = set(range(1, len(questions) + 1))
    missing_ids = expected_ids - ids_seen
    extra_ids = ids_seen - expected_ids
    if missing_ids:
        errors.append(f"Missing question IDs: {sorted(missing_ids)}")
    if extra_ids:
        errors.append(f"Unexpected question IDs: {sorted(extra_ids)}")

    # Check categories
    cat_ids = set()
    for c in categories:
        cid = c.get("id")
        if cid in cat_ids:
            errors.append(f"Duplicate category id: {cid}")
        cat_ids.add(cid)

        if not c.get("name"):
            errors.append(f"Category {cid}: Missing name")
        if not c.get("description"):
            warnings.append(f"Category {cid}: Missing description")
        if not c.get("question_ids"):
            errors.append(f"Category {cid}: No question_ids")

    # Check category references match
    cat_question_ids = set()
    for c in categories:
        for qid in c.get("question_ids", []):
            cat_question_ids.add(qid)
            if qid not in ids_seen:
                errors.append(f"Category '{c['name']}' references non-existent question {qid}")

    unreferenced = ids_seen - cat_question_ids
    if unreferenced:
        warnings.append(f"Questions not referenced by any category: {sorted(unreferenced)}")

    # Check questions per category
    for c in categories:
        count = len(c.get("question_ids", []))
        if count != 5:
            warnings.append(f"Category '{c['name']}' has {count} questions (expected 5)")

    # Check category strings match between files
    cat_strings_in_questions = categories_seen
    cat_strings_from_defs = {f"{c['id']}. {c['name']}" for c in categories}
    unmatched = cat_strings_in_questions - cat_strings_from_defs
    if unmatched:
        warnings.append(f"Category strings in questions not matching definitions: {unmatched}")

    # Report
    print(f"Questions: {len(questions)}")
    print(f"Categories: {len(categories)}")
    print()

    if errors:
        print(f"ERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("No errors found.")

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ⚠ {w}")

    print()
    if errors:
        print("RESULT: FAIL")
        sys.exit(1)
    else:
        print("RESULT: PASS")


if __name__ == "__main__":
    main()
