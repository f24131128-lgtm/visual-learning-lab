"""Small shared mechanics: labels are presentation; numeric domains are explicit."""
from collections import Counter
import math


def display_choices(items, context=None):
    """Return ID→display text; only collisions need contextual presentation.

    Ordinals distinguish choices visually, never resolve identity or provenance.
    Original labels/IDs are unchanged. Callers supply localized context words.
    """
    counts = Counter(item["label"] for item in items)
    labels = {}
    for index, item in enumerate(items, 1):
        label = item["label"]
        if counts[label] > 1:
            label += " · " + (context(item, index) if context else str(index))
        labels[item["id"]] = label
    # A contextual label may itself collide with a literal source label.
    repeated = Counter(labels.values())
    return {identifier: label + (f" · ({index})" if repeated[label] > 1 else "")
            for index, (identifier, label) in enumerate(labels.items(), 1)}


def numeric_domain(parameter, minimum_step=0.):
    """Never widen a singleton. Reject unsafe/reversed/unrepresentable domains."""
    low, high, value, step = (parameter[k] for k in ("min", "max", "default", "step"))
    if any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 1e9 for v in (low, high, value, step)):
        raise ValueError("Invalid numeric domain")
    if low > high or not low <= value <= high or step < 0:
        raise ValueError("Invalid numeric domain")
    if low == high:
        return "fixed"
    if step <= 0 or step < minimum_step or step > high-low or (high-low)/step > 10000 or low+step == low:
        raise ValueError("Invalid adjustable domain")
    return "adjustable"
