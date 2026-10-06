"""Generic bounded parameter, semantic time and numeric viewport policies.

No lesson names, primitive-specific physics or model code execution here.
Sampling establishes bounded evidence, not a continuous-domain proof; every
actual local parameter state is rechecked by the same engine before committing.
"""

import copy
import math

import numpy as np
from semantic_contract import numeric_domain

MAX_TIME = 10_000.


def declaration_defaults(raw):
    """Compatibility defaults for new optional policies; never fill base fields."""
    scene = copy.deepcopy(raw)
    if not isinstance(scene, dict): return scene
    timer = scene.get("time")
    if isinstance(timer, dict):
        timer.setdefault("strategy", "fixed_duration")
        timer.setdefault("duration_expression", None)
        timer.setdefault("periods", 1)
    parameters = scene.get("parameters")
    if isinstance(parameters, list):
        for p in parameters:
            if isinstance(p, dict):
                p.setdefault("quantity_kind", "scalar")
                p.setdefault("range_source", "pedagogical")
                p.setdefault("display_unit", "native")
    return scene


def normalize_parameter(p):
    # Reject malformed input before applying a fallback; a policy is not repair
    # permission for NaN, reversed bounds, an illegal baseline or absurd values.
    mode = numeric_domain(p, minimum_step=1e-9)
    kind, baseline = p["quantity_kind"], p["default"]
    if mode != "fixed" and p["range_source"] == "semantic_default":
        if kind == "inclination_angle":
            low, high = math.radians(5), math.radians(85)
        elif kind in ("length", "speed", "frequency", "acceleration"):
            if baseline <= 0: raise ValueError("Positive semantic parameter requires a positive baseline: " + p["id"])
            low, high = (baseline*.1, baseline*2) if kind == "acceleration" else (baseline/4, baseline*5)
        elif kind == "angle":
            low, high = baseline-math.pi, baseline+math.pi
        else:
            span = max(1., abs(baseline)*2)
            low, high = baseline-span, baseline+span
        if not low <= baseline <= high or max(abs(low), abs(high)) > 1e9:
            raise ValueError("Semantic range cannot safely contain its baseline: " + p["id"])
        p.update(min=low, max=high, step=(high-low)/200)
    if kind in ("length", "speed", "frequency", "acceleration") and p["min"] <= 0:
        raise ValueError("Positive semantic parameter has a non-positive range: " + p["id"])
    if kind == "inclination_angle" and not 0 < p["min"] <= p["max"] < math.pi/2:
        raise ValueError("Inclination angle must be strictly between 0 and pi/2.")
    if p["display_unit"] == "degrees" and (kind not in ("angle", "inclination_angle") or p["unit"] not in ("rad", "radian", "radians")):
        raise ValueError("Degree display requires a declared radian angular parameter.")
    # Preserve the exact existing adjustable representation/cache identity.
    # Singleton domains alone need the new trusted read-only discriminator.
    if numeric_domain(p, minimum_step=1e-9) == "fixed":
        p["parameter_kind"] = "fixed"
    else:
        p.pop("parameter_kind", None)
    return p


def parameter_display(p):
    factor = 180/math.pi if p["display_unit"] == "degrees" else 1.
    return {"factor": factor, "unit": "°" if factor != 1. else p["unit"],
            **{key: p[key]*factor for key in ("min", "max", "default", "step")}}


def time_domain(scene, parameters):
    from .engine import calculate
    timer = scene["time"]
    strategy = timer["strategy"]
    end = timer["max"]
    if strategy != "fixed_duration":
        duration = float(calculate(timer["duration_expression"], parameters))
        if strategy == "periodic_duration": duration *= timer["periods"]
        end = timer["min"] + duration
    if not math.isfinite(end) or not 0 <= timer["min"] < end <= MAX_TIME or end-timer["min"] < 1e-9:
        raise ValueError("Semantic duration is non-positive, non-finite or exceeds time bounds.")
    return {"min": timer["min"], "max": end, "unit": timer["unit"]}


def spatial_bounds(scene, projections):
    """Fit complete numeric paths, origins and +/- reference-axis endpoints."""
    from .engine import MAX_COORDINATE
    xs, ys = [0.], [0.]
    for obj in scene["objects"]:
        n = projections[obj["id"]]
        points = [(n[0], n[1])]
        if obj["type"] in ("axis", "vector"):
            points.append((np.asarray(n[0])+n[2], np.asarray(n[1])+n[3]))
            if obj["type"] == "axis": points.append((np.asarray(n[0])-n[2], np.asarray(n[1])-n[3]))
        for x, y in points:
            xs.extend(np.asarray(x).ravel().tolist()); ys.extend(np.asarray(y).ravel().tolist())
    # Raw points obey exactly the hard safety limit; a visual margin cannot
    # legalize unsafe coordinates or enlarge the hard limit.
    if not all(math.isfinite(v) and abs(v) <= MAX_COORDINATE for v in xs+ys):
        raise ValueError("Coordinates exceed spatial bounds while deriving viewport.")
    result = dict(scene["axes"])
    for name, values in (("x", xs), ("y", ys)):
        low, high = min(values), max(values)
        margin = max((high-low)*.08, 1e-6)
        result[name+"_min"] = max(-MAX_COORDINATE, low-margin)
        result[name+"_max"] = min(MAX_COORDINATE, high+margin)
    return result


def union_bounds(bounds):
    result = dict(bounds[0])
    for axis in ("x", "y"):
        result[axis+"_min"] = min(b[axis+"_min"] for b in bounds)
        result[axis+"_max"] = max(b[axis+"_max"] for b in bounds)
    return result
