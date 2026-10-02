"""Fail-closed spatial DSL, reference, inverse and sampled consistency checks."""

import copy
import json
import math
import time

import numpy as np

from safe_math import valid_variable
from .engine import MAX_COORDINATE, check_expression, check_inverses, evaluate, invariant_report, project
from .schema import MAX_PAYLOAD_BYTES, MAX_VECTORS, OPTIONAL_CAPABILITIES, WORLD_SCHEMA
from .policy import declaration_defaults, normalize_parameter, spatial_bounds, time_domain, union_bounds


class WorldValidationError(ValueError):
    pass


def shape(value, schema, path="scene"):
    kinds = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
    kind = {dict: "object", list: "array", str: "string", int: "integer", float: "number", type(None): "null"}.get(type(value))
    if kind not in kinds and not (kind == "integer" and "number" in kinds):
        raise WorldValidationError(path + ": invalid type")
    if "enum" in schema and value not in schema["enum"]:
        raise WorldValidationError(path + ": unsupported declaration")
    if kind == "object":
        if set(value) != set(schema["properties"]):
            missing = sorted(set(schema["properties"]) - set(value))
            extra = sorted(set(value) - set(schema["properties"]))
            raise WorldValidationError(path + ": missing fields=" + repr(missing) + "; unknown fields=" + repr(extra)[:240])
        for key, child in schema["properties"].items():
            shape(value[key], child, path+"."+key)
    elif kind == "array":
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 180):
            raise WorldValidationError(path + ": excessive or empty list")
        for index, item in enumerate(value):
            shape(item, schema["items"], f"{path}[{index}]")
    elif kind in ("integer", "number"):
        if not math.isfinite(value) or abs(value) > 1e9 or value < schema.get("minimum", -1e9) or value > schema.get("maximum", 1e9):
            raise WorldValidationError(path + ": invalid numeric bounds")
    elif kind == "string" and len(value) > (400 if path.endswith("expression") else 240):
        raise WorldValidationError(path + ": text too long")


def validate_patch(scene, patch, path="patch", parameters=None):
    from .schema import PATCH_SCHEMA
    shape(patch, PATCH_SCHEMA, path)
    op, target, value = patch["op"], patch["target_id"], patch["value"]
    if op == "set_parameter":
        p = next((p for p in scene["parameters"] if p["id"] == target), None)
        good = p is not None and value is not None and p["min"] <= value <= p["max"]
    elif op == "set_time":
        domain = time_domain(scene, parameters) if parameters is not None else scene.get("time_envelope", scene["time"])
        good = target == "time" and value is not None and domain["min"] <= value <= domain["max"]
    elif op == "set_focus":
        good = value is None and target in {q["id"] for q in scene["quantities"]}
    else:
        good = target == "" and value is None
    if not good:
        raise WorldValidationError(path + ": invalid " + op + " target/value; set_focus requires a quantity ID, set_parameter a parameter ID, and set_time the canonical time.")
    return dict(patch)


def normalize_world(raw, allowed_pages=()):
    started = time.perf_counter()
    try:
        # Only genuinely optional top-level capabilities get defaults. Required
        # base fields, unknown fields and supplied malformed capabilities still fail.
        scene = declaration_defaults(raw)
        if isinstance(scene, dict):
            for key in OPTIONAL_CAPABILITIES:
                scene.setdefault(key, [])
        shape(scene, WORLD_SCHEMA)
        if len(json.dumps(scene, ensure_ascii=False, allow_nan=False).encode()) > MAX_PAYLOAD_BYTES:
            raise WorldValidationError("Specification exceeds payload limit.")
        def expression_refs(expression, names, path):
            try:
                return check_expression(expression, names)
            except (ValueError, SyntaxError) as error:
                raise WorldValidationError(path + ": " + str(error)) from error
        used = {"time"}
        for name in ("scene_id",):
            if not valid_variable(scene[name]) or scene[name] in used:
                raise WorldValidationError("Invalid scene id.")
            used.add(scene[name])
        for group in ("parameters", "quantities", "objects", "series", "metrics", "bindings", "inverse_bindings", "invariants", "experiments"):
            for item in scene[group]:
                identifier = item["id"]
                if not valid_variable(identifier) or identifier in used:
                    raise WorldValidationError("Invalid or duplicate global id.")
                used.add(identifier)
                if "label" in item and (not item["label"].strip() or (item["label"] == identifier and (len(identifier) > 3 or "_" in identifier))):
                    raise WorldValidationError("A human-facing label is required.")
        for key in ("title", "learning_goal"):
            if not scene[key].strip():
                raise WorldValidationError("Missing human-facing scene text.")
        allowed = {p for p in allowed_pages if type(p) is int and p > 0}
        def pages(value):
            if isinstance(value, dict):
                if "source_pages" in value:
                    value["source_pages"] = list(dict.fromkeys(p for p in value["source_pages"] if p in allowed))
                for child in value.values(): pages(child)
            elif isinstance(value, list):
                for child in value: pages(child)
        pages(scene)
        timer, axes = scene["time"], scene["axes"]
        if not 0 <= timer["min"] < timer["max"] <= 10_000 or timer["max"]-timer["min"] < 1e-9:
            raise WorldValidationError("Invalid time range.")
        if not -MAX_COORDINATE <= axes["x_min"] < axes["x_max"] <= MAX_COORDINATE or not -MAX_COORDINATE <= axes["y_min"] < axes["y_max"] <= MAX_COORDINATE:
            raise WorldValidationError("Invalid spatial axes.")
        if min(axes["x_max"]-axes["x_min"], axes["y_max"]-axes["y_min"]) < 1e-9:
            raise WorldValidationError("Spatial viewport is too small.")
        parameters = {p["id"]: p for p in scene["parameters"]}
        for p in parameters.values():
            normalize_parameter(p)
        if timer["strategy"] == "fixed_duration":
            if timer["duration_expression"] is not None or timer["periods"] != 1:
                raise WorldValidationError("Fixed duration requires null duration_expression and periods=1.")
        else:
            if timer["duration_expression"] is None or (timer["strategy"] == "derived_duration" and timer["periods"] != 1):
                raise WorldValidationError("Derived/periodic duration requires a safe duration expression and valid periods.")
            expression_refs(timer["duration_expression"], parameters, "scene.time.duration_expression (parameters only)")
        quantities = {q["id"]: q for q in scene["quantities"]}
        known = set(parameters) | set(quantities) | {"time"}
        dependencies = {q["id"]: set(expression_refs(q["expression"], known, "scene.quantities["+q["id"]+"].expression")) & quantities.keys() for q in quantities.values()}
        order = []
        while dependencies:
            ready = [identifier for identifier, refs in dependencies.items() if not refs]
            if not ready:
                raise WorldValidationError("Cyclic quantity bindings.")
            order.extend(ready)
            for identifier in ready: dependencies.pop(identifier)
            for refs in dependencies.values(): refs.difference_update(ready)
        scene["quantity_order"] = order
        objects = {o["id"]: o for o in scene["objects"]}
        series = {s["id"]: s for s in scene["series"]}
        metrics = {m["id"]: m for m in scene["metrics"]}
        targets = objects | series | metrics
        if sum(o["type"] == "vector" for o in objects.values()) > MAX_VECTORS:
            raise WorldValidationError("Too many vectors.")
        for item in targets.values():
            if item["semantic_id"] not in quantities:
                raise WorldValidationError("Unknown semantic focus.")
        for o in objects.values():
            if any(abs(n) > MAX_COORDINATE for n in o["origin"]) or len(o["origin_quantity_ids"]) not in (0, 2) or any(q not in quantities for q in o["origin_quantity_ids"]):
                raise WorldValidationError("Invalid spatial origin.")
        bound = set()
        for b in scene["bindings"]:
            target = b["target_id"]
            if target not in targets or target in bound or any(q not in quantities for q in b["quantity_ids"]):
                raise WorldValidationError("Unknown or contradictory forward binding.")
            expected = "vector_components" if target in objects and objects[target]["type"] in ("vector", "axis") else "point_position" if target in objects else "curve_value" if target in series else "metric_value"
            if b["type"] != expected or len(b["quantity_ids"]) != (2 if target in objects else 1):
                raise WorldValidationError("Invalid binding target or arity.")
            if target not in objects and b["quantity_ids"][0] != targets[target]["semantic_id"]:
                raise WorldValidationError("Curve/metric semantic identity contradicts its binding.")
            bound.add(target)
        if bound != set(targets):
            raise WorldValidationError("Every representation needs one canonical binding.")
        inverse_objects = set()
        for b in scene["inverse_bindings"]:
            target = objects.get(b["object_id"])
            if target is None or b["object_id"] in inverse_objects:
                raise WorldValidationError("Invalid or contradictory inverse object.")
            inverse_objects.add(b["object_id"])
            if b["type"] == "nearest_path_time":
                if target["type"] != "trajectory" or b["target_id"] != "time" or b["rate_expression"] is not None or b["offset_expression"] is not None:
                    raise WorldValidationError("Invalid trajectory inverse.")
            else:
                if target["type"] != "vector" or b["offset_expression"] is None:
                    raise WorldValidationError("Invalid angle inverse.")
                expression_refs(b["offset_expression"], parameters, "scene.inverse_bindings["+b["id"]+"].offset_expression (parameters only)")
                if b["type"] == "angle_to_time":
                    if b["target_id"] != "time" or b["rate_expression"] is None:
                        raise WorldValidationError("Invalid time inverse.")
                    expression_refs(b["rate_expression"], parameters, "scene.inverse_bindings["+b["id"]+"].rate_expression (parameters only)")
                else:
                    p = parameters.get(b["target_id"])
                    if p is None or b["rate_expression"] is not None or abs(b["scale"]) < 1e-9 or abs(b["scale"])*(p["max"]-p["min"]) > 2*math.pi:
                        raise WorldValidationError("Invalid parameter inverse.")
                    if p["id"] in expression_refs(b["offset_expression"], parameters, "scene.inverse_bindings["+b["id"]+"].offset_expression"):
                        raise WorldValidationError("Inverse offset must not depend on its target.")
        for inv in scene["invariants"]:
            expression_refs(inv["left_expression"], known, "scene.invariants["+inv["id"]+"].left_expression")
            expression_refs(inv["right_expression"], known, "scene.invariants["+inv["id"]+"].right_expression")
            if not 1e-10 <= inv["tolerance"] <= 1e-4 or inv["lower"] > inv["upper"]:
                raise WorldValidationError("Invalid invariant tolerance or bounds.")
        # Derive a safety envelope from legal ranges and semantic durations,
        # before checking recipes or fitting views. Do not change parameter ranges
        # to accommodate an undersized model-provided axes hint.
        defaults = {p["id"]: p["default"] for p in parameters.values()}
        import itertools
        scenarios = [defaults]
        scenarios.extend(dict(zip(parameters, values)) for values in itertools.product(*[(p["min"], p["max"]) for p in parameters.values()]))
        scenarios.extend(defaults | {p["id"]: value} for p in parameters.values() for value in (p["min"], p["max"]))
        bounds, ends, checks = [], [], 0
        for params in scenarios:
            domain = time_domain(scene, params)
            ends.append(domain["max"])
            values = evaluate(scene, params, np.linspace(domain["min"], domain["max"], timer["frames"]))
            projected = project(scene, values, check_viewport=False)
            bounds.append(spatial_bounds(scene, projected))
            checks += invariant_report(scene, params)
            check_inverses(scene, params, values, projected)
        scene["axes"] = union_bounds(bounds)
        scene["time_envelope"] = {"min": timer["min"], "max": max(ends)}
        focus_aliases = []
        for experiment in scene["experiments"]:
            if any(q not in quantities for q in experiment["observation_targets"]):
                raise WorldValidationError("Unknown experiment observation target.")
            for index, patch in enumerate(experiment["steps"]):
                # Optional recipes may name a declared view entity as focus,
                # exactly as a click does. Resolve only its already-validated
                # semantic_id; never guess an unknown ID or repair operations.
                if patch["op"] == "set_focus" and patch["target_id"] in targets:
                    target = patch["target_id"]
                    patch["target_id"] = targets[target]["semantic_id"]
                    focus_aliases.append(dict(experiment=experiment["id"], step=index, representation=target, quantity=patch["target_id"]))
                validate_patch(scene, patch, "scene.experiments["+experiment["id"]+"].steps["+str(index)+"]")
        # Default, corners, and individual endpoints: bounded evidence, not a proof
        # over a continuous domain. Runtime also checks every accepted local state.
        for params in scenarios:
            domain = time_domain(scene, params)
            project(scene, evaluate(scene, params, np.linspace(domain["min"], domain["max"], timer["frames"])))
        scene["validation_report"] = {"sample_checks": checks, "parameter_scenarios": len(scenarios), "focus_aliases": focus_aliases, "seconds": time.perf_counter()-started}
        return scene
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as error:
        raise WorldValidationError(str(error)) from error
