"""
Evaluation pipeline: load model answers, score each against its reference, and report an
overall accuracy plus a per-category breakdown.

Run:
    python pipeline.py --in data/predictions.jsonl --out results.json

A rough first cut — see the README / brief for what to do with it.
"""
import argparse
import json
from collections import defaultdict

import scorer


def load_records(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def evaluate(records, score_fn=scorer.score):
    """Score every record and aggregate into the results contract."""
    total = defaultdict(int)
    correct = defaultdict(int)
    num_skipped = 0
    for r in records:
        if r.get("model_answer") is None or r.get("reference_answer") is None:
            num_skipped += 1
            continue
            
        result = score_fn(r["reference_answer"], r["model_answer"], r.get("question"))
        total[r["category"]] += 1
        if result["is_correct"]:
            correct[r["category"]] += 1

    per_category = {c: correct[c] / total[c] for c in total} if total else {}
    num_evaluated = sum(total.values())
    overall = sum(correct.values()) / num_evaluated if num_evaluated > 0 else 0.0

    return {
        "overall_score": overall,
        "num_evaluated": num_evaluated,
        "num_skipped": num_skipped,
        "per_category": per_category,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="predictions .jsonl")
    ap.add_argument("--out", dest="out", required=True, help="output results .json")
    args = ap.parse_args()

    records = load_records(args.inp)
    results = evaluate(records)

    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
