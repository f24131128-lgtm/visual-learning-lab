"""Bounded quantity DAG and projections. No renderer owns physical equations."""

import ast
import math

import numpy as np

from safe_math import CONSTANTS, FUNCTIONS, evaluate_expression, validate_expression
from .schema import MAX_FRAMES

MAX_COORDINATE = 1e6
MAX_QUANTITY = 1e9


def references(expression):
    if not isinstance(expression, str) or not 1 <= len(expression) <= 400:
        raise ValueError("Invalid expression length.")
    tree = ast.parse(expression, mode="eval")
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} - FUNCTIONS.keys() - CONSTANTS.keys()


def check_expression(expression, allowed):
    refs = references(expression)
    if not refs <= set(allowed):
        raise ValueError("Unknown expression reference: " + ", ".join(sorted(refs - set(allowed))) + ".")
    validate_expression(expression, refs)
    return sorted(refs)


def calculate(expression, values):
    refs = references(expression)
    result = evaluate_expression(expression, {key: values[key] for key in refs})
    if np.any(np.abs(result) > MAX_QUANTITY):
        raise ValueError("Quantity exceeds world numeric bounds.")
    return result


def evaluate(scene, parameters, time):
    expected = {p["id"] for p in scene["parameters"]}
    if set(parameters) != expected:
        raise ValueError("Invalid parameter state.")
    for p in scene["parameters"]:
        value = parameters[p["id"]]
        if type(value) not in (int, float) or not math.isfinite(value) or not p["min"] <= value <= p["max"]:
            raise ValueError("Parameter outside legal bounds.")
    from .policy import time_domain
    domain = time_domain(scene, parameters)
    times = np.asarray(time, dtype=float)
    if times.ndim > 1 or not 1 <= times.size <= MAX_FRAMES or not np.all(np.isfinite(times)) or np.any(times < domain["min"]) or np.any(times > domain["max"]):
        raise ValueError("Time outside world bounds.")
    values = dict(parameters, time=float(times) if times.ndim == 0 else times)
    quantities = {q["id"]: q for q in scene["quantities"]}
    for identifier in scene["quantity_order"]:
        values[identifier] = calculate(quantities[identifier]["expression"], values)
    return values


def project(scene, values, check_viewport=True):
    """The four forward binding types share this one projection function."""
    result = {}
    for binding in scene["bindings"]:
        numbers = [values[key] for key in binding["quantity_ids"]]
        if binding["type"] in ("point_position", "vector_components") and any(np.any(np.abs(n) > MAX_COORDINATE) for n in numbers):
            raise ValueError("Coordinates exceed spatial bounds.")
        result[binding["target_id"]] = numbers
    for obj in scene["objects"]:
        origin = [values[key] for key in obj["origin_quantity_ids"]] if obj["origin_quantity_ids"] else obj["origin"]
        if any(np.any(np.abs(n) > MAX_COORDINATE) for n in origin):
            raise ValueError("Origin exceeds spatial bounds.")
        if obj["type"] in ("vector", "axis"):
            result[obj["id"]] = list(origin) + result[obj["id"]]
            if any(np.any(np.abs(origin[i] + result[obj["id"]][i+2]) > MAX_COORDINATE) for i in (0, 1)):
                raise ValueError("Endpoint exceeds spatial bounds.")
        nums = result[obj["id"]]
        points = [(nums[0], nums[1]), (nums[0]+nums[2], nums[1]+nums[3])] if obj["type"] in ("vector", "axis") else [(nums[0], nums[1])]
        if obj["type"] == "axis": points.append((nums[0]-nums[2], nums[1]-nums[3]))
        for x, y in points:
            if np.any(np.abs(x) > MAX_COORDINATE) or np.any(np.abs(y) > MAX_COORDINATE):
                raise ValueError("Endpoint exceeds spatial bounds.")
            if not check_viewport: continue
            axes = scene["axes"]
            # A mathematically on-boundary sum can be a few ULPs outside (e.g.
            # 3.0000000000000004 vs 3). Allow machine roundoff only, not clipping,
            # changed geometry, a percentage margin or expanded safety limits.
            x_roundoff = 16 * np.spacing(max(1., abs(axes["x_min"]), abs(axes["x_max"])))
            y_roundoff = 16 * np.spacing(max(1., abs(axes["y_min"]), abs(axes["y_max"])))
            if np.any(np.asarray(x) < axes["x_min"]-x_roundoff) or np.any(np.asarray(x) > axes["x_max"]+x_roundoff) or np.any(np.asarray(y) < axes["y_min"]-y_roundoff) or np.any(np.asarray(y) > axes["y_max"]+y_roundoff):
                raise ValueError("Spatial projection for " + obj["id"] + " lies outside its declared axes; axes must cover the full legal parameter/time range.")
    return result


def snapshot(scene, state):
    from .policy import time_domain
    values = evaluate(scene, state["parameters"], state["time"])
    return {"time": state["time"], "domain": time_domain(scene, state["parameters"]), "parameters": dict(state["parameters"]),
            "focus": state["focus"], "values": {q["id"]: float(values[q["id"]]) for q in scene["quantities"]},
            "projections": {key: [float(n) for n in nums] for key, nums in project(scene, values).items()}}


def frames(scene, parameters):
    from .policy import spatial_bounds, time_domain
    domain = time_domain(scene, parameters)
    times = np.linspace(domain["min"], domain["max"], scene["time"]["frames"])
    values = evaluate(scene, parameters, times)
    projections = project(scene, values)
    check_inverses(scene, parameters, values, projections)
    def vector(number):
        return np.broadcast_to(number, times.shape).astype(float).tolist()
    return {"times": times.tolist(), "domain": domain, "axes": spatial_bounds(scene, projections), "values": {q["id"]: vector(values[q["id"]]) for q in scene["quantities"]},
            "projections": {key: [vector(n) for n in nums] for key, nums in projections.items()}}


def invariant_report(scene, parameters, current_time=None):
    from .policy import time_domain
    domain = time_domain(scene, parameters)
    checks = 0
    for invariant in scene["invariants"]:
        times = np.linspace(domain["min"], domain["max"], invariant["samples"])
        if current_time is not None: times = np.append(times, current_time)
        values = evaluate(scene, parameters, times)
        left = np.broadcast_to(calculate(invariant["left_expression"], values), times.shape)
        right = np.broadcast_to(calculate(invariant["right_expression"], values), times.shape)
        tolerance = invariant["tolerance"]
        kind = invariant["type"]
        if kind == "bounded":
            passed = np.all((left >= invariant["lower"]-tolerance) & (left <= invariant["upper"]+tolerance))
        elif kind == "constant_over_time":
            passed = np.all(np.abs(left-left[0]) <= tolerance)
        elif kind == "phase_difference":
            error = np.arctan2(np.sin(left-right-invariant["lower"]), np.cos(left-right-invariant["lower"]))
            passed = np.all(np.abs(error) <= tolerance)
        else:
            passed = np.all(np.abs(left-right) <= tolerance)
        if not passed:
            raise ValueError("Declared invariant failed: " + invariant["id"])
        checks += len(times)
    return checks


def check_inverses(scene, parameters, values, projections):
    from .policy import time_domain
    for binding in scene["inverse_bindings"]:
        if binding["type"] == "nearest_path_time": continue
        _, _, dx, dy = projections[binding["object_id"]]
        if np.any(np.hypot(dx, dy) < 1e-8):
            raise ValueError("Angle inverse has a zero vector.")
        offset = calculate(binding["offset_expression"], parameters)
        if binding["type"] == "angle_to_time":
            rate = calculate(binding["rate_expression"], parameters)
            if abs(rate) < 1e-9 or abs(rate)*time_domain(scene, parameters)["max"] + abs(offset) > 250*math.pi:
                raise ValueError("Angle inverse exceeds bounded cycle search.")
            expected = rate*values["time"]+offset
        else:
            expected = binding["scale"]*parameters[binding["target_id"]]+offset
        error = np.arctan2(np.sin(np.arctan2(dy, dx)-expected), np.cos(np.arctan2(dy, dx)-expected))
        if np.any(np.abs(error) > 1e-6):
            raise ValueError("Inverse does not match its forward binding.")


def inverse_patch(scene, state, binding_id, value):
    """Only analytic angle mappings and bounded nearest-path lookup, no solver."""
    binding = next((b for b in scene["inverse_bindings"] if b["id"] == binding_id), None)
    if binding is None:
        raise ValueError("Unknown inverse binding.")
    kind = binding["type"]
    if kind == "nearest_path_time":
        if not isinstance(value, list) or len(value) != 2 or any(type(n) not in (int, float) or not math.isfinite(n) or abs(n) > MAX_COORDINATE for n in value):
            raise ValueError("Invalid path point.")
        data = frames(scene, state["parameters"])
        x, y = data["projections"][binding["object_id"]]
        index = int(np.argmin((np.asarray(x)-value[0])**2 + (np.asarray(y)-value[1])**2))
        result = data["times"][index]
    else:
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > math.pi*2:
            raise ValueError("Invalid angle.")
        env = state["parameters"]
        offset = float(calculate(binding["offset_expression"], env))
        if kind == "angle_to_time":
            from .policy import time_domain
            rate = float(calculate(binding["rate_expression"], env))
            domain = time_domain(scene, env)
            low, high, current = domain["min"], domain["max"], state["time"]
        else:
            rate = binding["scale"]
            param = next(p for p in scene["parameters"] if p["id"] == binding["target_id"])
            low, high, current = param["min"], param["max"], env[param["id"]]
        if abs(rate) < 1e-9:
            raise ValueError("Degenerate angle inverse.")
        candidates = [(value-offset+2*math.pi*k)/rate for k in range(-128, 129)]
        candidates = [n for n in candidates if low-1e-12 <= n <= high+1e-12]
        if not candidates:
            raise ValueError("Angle has no solution within the legal range.")
        result = min(candidates, key=lambda n: abs(n-current))
        result = min(high, max(low, result))
    return {"op": "set_time" if binding["target_id"] == "time" else "set_parameter", "target_id": binding["target_id"], "value": result}
