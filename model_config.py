"""Owned production Responses configuration; no learner model selector."""

MODEL = "gpt-6.1-sol"
REASONING_EFFORT = "medium"


def response_options():
    """Fresh options for every explicit generation path."""
    return {"model": MODEL, "reasoning": {"effort": REASONING_EFFORT}}
