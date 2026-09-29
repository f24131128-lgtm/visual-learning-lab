"""Pure local probability and set-algebra operations for Learning Scenes."""

import random
from fractions import Fraction

MONTE_CARLO_COUNTS = (100, 1_000, 10_000)
MAX_MONTE_CARLO_SAMPLES = 10_000


def outcome_weights(scene):
    return {item["id"]: item["weight"] for item in scene["outcomes"]}


def probability(scene, outcome_ids):
    weights = outcome_weights(scene)
    selected = set(outcome_ids)
    if all(float(value).is_integer() for value in weights.values()):
        numerator = sum(int(value) for key, value in weights.items() if key in selected)
        denominator = sum(int(value) for value in weights.values())
        return Fraction(numerator, denominator)
    total = sum(weights.values())
    return sum(value for key, value in weights.items() if key in selected) / total


def probability_value(value):
    return float(value)


def format_probability(value):
    if isinstance(value, Fraction):
        decimal = float(value)
        return f"{value.numerator}/{value.denominator} = {decimal:.4g}"
    return f"{float(value):.4g}"


def mutually_exclusive(scene, left_id, right_id):
    return not (scene["event_sets"][left_id] & scene["event_sets"][right_id])


def de_morgan(scene, left_id, right_id):
    universe = frozenset(item["id"] for item in scene["outcomes"])
    left, right = scene["event_sets"][left_id], scene["event_sets"][right_id]
    first_a, first_b = universe - (left | right), (universe - left) & (universe - right)
    second_a, second_b = universe - (left & right), (universe - left) | (universe - right)
    return {
        "union_complement": (first_a, first_b, first_a == first_b),
        "intersection_complement": (second_a, second_b, second_a == second_b),
    }


def inclusion_exclusion(scene, left_id, right_id):
    left, right = scene["event_sets"][left_id], scene["event_sets"][right_id]
    overlap, union = left & right, left | right
    p_left, p_right = probability(scene, left), probability(scene, right)
    p_overlap, p_union = probability(scene, overlap), probability(scene, union)
    return {
        "left": p_left, "right": p_right, "intersection": p_overlap, "union": p_union,
        "derived": p_left + p_right - p_overlap,
        "left_count": len(left), "right_count": len(right), "intersection_count": len(overlap),
        "union_count": len(union),
    }


def monte_carlo(scene, target_outcomes, samples, seed=17):
    """Reproducible bounded local trials using the scene's declared weights."""
    if isinstance(samples, bool) or samples not in MONTE_CARLO_COUNTS or samples > MAX_MONTE_CARLO_SAMPLES:
        raise ValueError("Unsupported Monte Carlo sample count.")
    outcomes = [item["id"] for item in scene["outcomes"]]
    weights = [item["weight"] for item in scene["outcomes"]]
    draws = random.Random(int(seed)).choices(outcomes, weights=weights, k=samples)
    target = set(target_outcomes)
    hits = sum(item in target for item in draws)
    empirical = hits / samples
    theoretical = probability_value(probability(scene, target))
    checkpoints = []
    running = 0
    interval = max(1, samples // 100)
    for index, outcome in enumerate(draws, 1):
        running += outcome in target
        if index == 1 or index == samples or index % interval == 0:
            checkpoints.append((index, running / index))
    return {
        "samples": samples, "hits": hits, "empirical": empirical,
        "theoretical": theoretical, "difference": abs(empirical - theoretical),
        "checkpoints": checkpoints,
    }
