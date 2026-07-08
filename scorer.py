"""
Decides whether a model answer is correct, given the reference answer.

Right now it only does an exact string match, so "Paris" and "It's Paris." count as
different answers. Improving this is Part 2 of the task.
"""


def score(reference_answer, model_answer, question=None):
    """Return {"is_correct": bool, "confidence": float in [0,1]}.

    Keep this signature and return shape — the pipeline and the grader call it directly.
    """
    is_correct = reference_answer.strip().lower() == model_answer.strip().lower()
    return {"is_correct": is_correct, "confidence": 1.0 if is_correct else 0.0}
