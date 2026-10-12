"""Owned production Responses configuration; no learner model selector."""

MODEL = "gpt-6.1-sol"
REASONING_EFFORT = "medium"


def response_options(max_output_tokens=None):
    """Fresh options for every explicit generation path."""
    from production_safety import MAX_OUTPUT_TOKENS
    return {"model": MODEL, "reasoning": {"effort": REASONING_EFFORT},
            "max_output_tokens": MAX_OUTPUT_TOKENS if max_output_tokens is None else min(MAX_OUTPUT_TOKENS, max_output_tokens), "store": False}
