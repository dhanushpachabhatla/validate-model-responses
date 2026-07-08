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
