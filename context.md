# Repository Context

This file serves as a reference for the current state of the repository (before modifications).

## Goal
The goal of this project is to create an evaluation pipeline to determine how accurate a model is at answering user questions. It loads model answers, scores each against a reference answer, and reports an overall accuracy.

## Files Present
- `README.md`: Instructions for the take-home assignment.
- `pipeline.py`: The main script that loads data, scores it, aggregates it, and reports the accuracy. It contains a bug where it crashes on malformed records (e.g. missing `model_answer`).
- `scorer.py`: The logic to decide if an answer is correct. Currently, it uses a naive exact string match (lowercased and stripped).
- `data/predictions.jsonl`: The dataset containing `id`, `question`, `reference_answer`, `model_answer`, and `category`.
- `data/labeled_dev.jsonl`: A small human-labeled sample of predictions mapped to whether they are correct (`is_correct`). We can use this to calibrate the scorer.
- `tests/test_pipeline.py`: Tests that the pipeline must pass (e.g., checking that it doesn't crash on bad inputs and calculates accuracy correctly).

## What we need to add/fix
1. **Fix `pipeline.py`**: Add a check to skip malformed records (where `model_answer` is null) so that `test_skips_malformed_without_crashing` passes, and track `num_skipped` and `num_evaluated` correctly.
2. **Improve `scorer.py`**: Upgrade the scoring logic to be robust (beyond exact string matching) so it aligns with human judgment. 
3. **Add `REPORT.md`**: A 300-500 word report detailing changes, final accuracy, and future considerations.

## Bugs Encountered & Fixes Applied

When initially trying to run the "rough first cut" of the codebase, we hit three major issues:

1. **`KeyError: 'model_answer'`**: 
   - *Problem*: The original `pipeline.py` blindly accessed `r["model_answer"]`. However, the dataset contained malformed records (e.g., ID `bad002`) that were missing this key entirely, causing the pipeline to crash.
   - *Fix*: We updated `pipeline.py` to use `.get("model_answer")` and safely skip records where either the model answer or reference answer is `None`, incrementing a `num_skipped` counter.
2. **`AttributeError: 'int' object has no attribute 'lower'`**: 
   - *Problem*: In `scorer.py`, the exact match logic called `.lower()` on the answers. Some answers in the JSON dataset were literal integers (e.g., `4`), which crashed the script.
   - *Fix*: We explicitly cast both answers to strings (`str()`) before processing them.
3. **Macro vs Micro Average Bug**:
   - *Problem*: The `test_overall_score_is_micro_average` test failed because the original `pipeline.py` calculated the total accuracy by averaging the per-category percentages (Macro-average).
   - *Fix*: We updated the math to calculate `total correct / total evaluated` (Micro-average) across all records.

## Initial Accuracy Results (Exact Match)
After applying only the basic crash fixes above (retaining the naive exact-match string logic), the initial baseline pipeline run yielded:
- **Overall Score**: 35.1%
- **Evaluated**: 1051
- **Skipped**: 9

## Phase 1 Upgrades (Advanced Heuristics)
To improve the scorer to behave more like a human, we implemented an Advanced Normalization Heuristic in `scorer.py` using Python's standard `string` library. The scorer now:
- Lowercases everything and completely strips all punctuation.
- Removes common conversational filler (e.g., "The answer is", "It's").
- Checks if the normalized reference string is perfectly contained within the model's answer.

**Phase 1 Accuracy Result:**
After applying this advanced heuristic, the pipeline's accuracy nearly doubled, yielding:
- **Overall Score**: 70.8%

## Phase 2 Upgrades (Synonyms & Number Normalization)
We then implemented two further upgrades to catch remaining edge cases:
- **Synonym Mapping**: Maps common alternate names (e.g., "UK" to "United Kingdom") to their full forms.
- **Number Normalization**: Uses the `num2words` library (added to `requirements.txt`) to convert numeric digits to their word forms so `4` matches `four`.

**Final Accuracy Results:**
After applying Phase 2, the pipeline's accuracy jumped an additional 1.7%, yielding the final run contract results:
```json
{
  "overall_score": 0.725023786869648,
  "num_evaluated": 1051,
  "num_skipped": 9,
  "per_category": {
    "medium": 0.6943620178041543,
    "hard": 0.4365482233502538,
    "easy": 0.8549323017408124
  }
}
```
