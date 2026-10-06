"""Validate and normalize untrusted Learning Scene specifications."""

import itertools
import math
import re

from .expressions import (
    EventExpressionError, display_expression, evaluate_expression, parse_expression,
)
from .schema import DOMAIN, SCENE_SCHEMA_VERSION, VIEW_TYPES

MAX_OUTCOMES = 64
MAX_EVENTS = 12
MAX_TREE_DEPTH = 4
MAX_TREE_NODES = 96
MAX_BINDINGS = 64
MAX_LABEL_LENGTH = 120
_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,47}$")
_UNIVERSE_NAMES = {"s", "omega", "universe", "samplespace", "sampleuniverse"}


class SceneValidationError(ValueError):
    """Raised when a model-generated scene cannot safely enter the runtime."""


def _object(value, name):
    if not isinstance(value, dict):
        raise SceneValidationError(f"{name} must be an object.")
    return value


def _list(value, name, limit):
    if not isinstance(value, list) or len(value) > limit:
        raise SceneValidationError(f"{name} is invalid or exceeds its limit.")
    return value


def _id(value, name):
    if not isinstance(value, str) or not _ID.fullmatch(value):
        raise SceneValidationError(f"{name} has an invalid id.")
    return value


def _text(value, name, required=True):
    if not isinstance(value, str):
        raise SceneValidationError(f"{name} must be text.")
    value = value.strip()
    if (required and not value) or len(value) > MAX_LABEL_LENGTH:
        raise SceneValidationError(f"{name} is empty or too long.")
    return value


def _pages(value, allowed_pages):
    if not isinstance(value, list):
        return []
    allowed = {page for page in allowed_pages if isinstance(page, int) and not isinstance(page, bool) and page > 0}
    result = []
    for page in value:
        if isinstance(page, int) and not isinstance(page, bool) and page in allowed and page not in result:
            result.append(page)
    return result


def _unique(identifier, used):
    if identifier in used:
        raise SceneValidationError(f"Duplicate id: {identifier}")
    used.add(identifier)


def _name_key(value):
    value = str(value).strip().casefold().replace("ω", "omega")
    return re.sub(r"[^a-z0-9]+", "", value)


def _looks_like_universe(identifier, label):
    keys = {_name_key(identifier), _name_key(label)}
    return any(
        key in _UNIVERSE_NAMES
        or key.startswith("samplespace")
        or key.startswith("universe")
        or key.startswith("omega")
        for key in keys
    )


def _require_human_label(identifier, label, name):
    if _name_key(identifier) == _name_key(label) and (
        len(identifier) > 3 or "_" in identifier or "-" in identifier
    ):
        raise SceneValidationError(f"{name} must have a human-facing label.")
    return label


def _tuple_path(label):
    """Conservatively recognize a complete ordered tuple such as (H,T)."""
    if not isinstance(label, str) or not label.startswith("(") or not label.endswith(")"):
        return None
    parts = [part.strip() for part in label[1:-1].split(",")]
    if not 2 <= len(parts) <= MAX_TREE_DEPTH or any(not part or len(part) > MAX_LABEL_LENGTH for part in parts):
        return None
    return parts


def _infer_complete_product_paths(outcomes):
    """Infer stages only when tuple labels form one complete Cartesian product."""
    if any(outcome["path"] for outcome in outcomes):
        return None
    paths = [_tuple_path(outcome["label"]) for outcome in outcomes]
    if any(path is None for path in paths):
        return None
    depth = len(paths[0])
    if any(len(path) != depth for path in paths) or len({tuple(path) for path in paths}) != len(paths):
        return None
    branch_values = []
    for index in range(depth):
        values = list(dict.fromkeys(path[index] for path in paths))
        if not values or len(values) > 12:
            return None
        branch_values.append(values)
    expected = set(itertools.product(*branch_values))
    if set(map(tuple, paths)) != expected:
        return None
    return paths, branch_values


def _generated_id(prefix, used):
    candidate, suffix = prefix, 2
    while candidate in used:
        candidate = f"{prefix}_{suffix}"
        suffix += 1
    _unique(candidate, used)
    return candidate


def normalize_scene(raw, allowed_pages=()):
    """Return a safe normalized probability scene or raise SceneValidationError."""
    raw = _object(raw, "scene")
    if raw.get("domain") == "spatial_dynamics":
        from .world.validator import normalize_world
        return normalize_world(raw, allowed_pages)
    if raw.get("scene_version") != SCENE_SCHEMA_VERSION or raw.get("domain") != DOMAIN:
        raise SceneValidationError("Unsupported Learning Scene version or domain.")
    used = set()
    scene_id = _id(raw.get("scene_id"), "scene")
    _unique(scene_id, used)

    raw_outcomes = _list(raw.get("outcomes"), "outcomes", MAX_OUTCOMES)
    if not raw_outcomes:
        raise SceneValidationError("A finite sample space is required.")
    outcomes = []
    for index, item in enumerate(raw_outcomes):
        item = _object(item, f"outcomes[{index}]")
        identifier = _id(item.get("id"), "outcome")
        _unique(identifier, used)
        path = _list(item.get("path"), "outcome path", MAX_TREE_DEPTH)
        path = [_text(value, "branch value") for value in path]
        weight = item.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight) or weight <= 0:
            raise SceneValidationError("Outcome weights must be positive finite numbers.")
        label = _require_human_label(identifier, _text(item.get("label"), "outcome label"), "Outcome")
        outcomes.append({"id": identifier, "label": label,
                         "path": path, "weight": float(weight),
                         "source_pages": _pages(item.get("source_pages"), allowed_pages)})
    outcome_ids = {item["id"] for item in outcomes}

    raw_events = _list(raw.get("events"), "events", MAX_EVENTS)
    if not raw_events:
        raise SceneValidationError("At least one event is required.")
    events = []
    for index, item in enumerate(raw_events):
        item = _object(item, f"events[{index}]")
        identifier = _id(item.get("id"), "event")
        _unique(identifier, used)
        members = _list(item.get("outcome_ids"), "event membership", MAX_OUTCOMES)
        if any(member not in outcome_ids for member in members) or len(set(members)) != len(members):
            raise SceneValidationError("An event references an unknown or duplicate outcome.")
        label = _require_human_label(identifier, _text(item.get("label"), "event label"), "Event")
        if _looks_like_universe(identifier, label) or set(members) == outcome_ids:
            raise SceneValidationError("The sample space is the universe and cannot be an ordinary event.")
        events.append({"id": identifier, "label": label,
                       "outcome_ids": list(members), "source_pages": _pages(item.get("source_pages"), allowed_pages)})
    event_map = {item["id"]: frozenset(item["outcome_ids"]) for item in events}

    experiment = _object(raw.get("experiment"), "experiment")
    if not isinstance(experiment.get("staged"), bool):
        raise SceneValidationError("experiment.staged must be boolean.")
    staged = experiment["staged"]
    inferred_staged = False
    raw_stages = _list(experiment.get("stages"), "stages", MAX_TREE_DEPTH)
    stages, tree_nodes = [], 1
    for index, item in enumerate(raw_stages):
        item = _object(item, f"stages[{index}]")
        identifier = _id(item.get("id"), "stage")
        _unique(identifier, used)
        values = _list(item.get("branch_values"), "branch values", 12)
        values = [_text(value, "branch value") for value in values]
        if not values or len(values) != len(set(values)):
            raise SceneValidationError("Stage branch values must be non-empty and unique.")
        tree_nodes += math.prod(len(stage["branch_values"]) for stage in stages) * len(values)
        stages.append({"id": identifier, "label": _text(item.get("label"), "stage label"),
                       "branch_values": values, "source_pages": _pages(item.get("source_pages"), allowed_pages)})
    if not staged and not stages:
        inferred = _infer_complete_product_paths(outcomes)
        if inferred is not None:
            paths, branch_values = inferred
            inferred_staged = staged = True
            inferred_pages = list(dict.fromkeys(
                page for outcome in outcomes for page in outcome["source_pages"]
            ))
            for outcome, path in zip(outcomes, paths):
                outcome["path"] = path
            for index, values in enumerate(branch_values, 1):
                tree_nodes += math.prod(len(stage["branch_values"]) for stage in stages) * len(values)
                stages.append({
                    "id": _generated_id(f"inferred_stage_{index}", used),
                    "label": f"Stage {index}",
                    "branch_values": values,
                    "source_pages": inferred_pages,
                })
    if tree_nodes > MAX_TREE_NODES:
        raise SceneValidationError("Probability tree exceeds the node limit.")
    if staged:
        if not stages:
            raise SceneValidationError("A staged experiment needs stages.")
        for outcome in outcomes:
            if len(outcome["path"]) != len(stages) or any(value not in stages[i]["branch_values"] for i, value in enumerate(outcome["path"])):
                raise SceneValidationError("Outcome paths must match declared stages.")
        if len({tuple(outcome["path"]) for outcome in outcomes}) != len(outcomes):
            raise SceneValidationError("Staged outcome paths must be unique.")
    elif stages or any(outcome["path"] for outcome in outcomes):
        raise SceneValidationError("Non-staged experiments cannot contain stages or paths.")

    views = []
    raw_views = _list(raw.get("views"), "views", 5)
    semantic_ids = outcome_ids | set(event_map)
    for index, item in enumerate(raw_views):
        item = _object(item, f"views[{index}]")
        identifier = _id(item.get("id"), "view")
        _unique(identifier, used)
        view_type = item.get("type")
        if view_type not in VIEW_TYPES:
            raise SceneValidationError("Unsupported renderer type.")
        refs = _list(item.get("semantic_ids"), "view semantic ids", MAX_OUTCOMES)
        views.append({"id": identifier, "type": view_type, "title": _text(item.get("title"), "view title"),
                      "semantic_ids": list(refs)})
    if inferred_staged and not any(view["type"] == "probability_tree" for view in views):
        if len(views) >= 5:
            raise SceneValidationError("There is no room for the inferred probability tree view.")
        views.append({
            "id": _generated_id("inferred_probability_tree", used),
            "type": "probability_tree",
            "title": "Probability Tree",
            "semantic_ids": sorted(outcome_ids),
        })
    if not views or len({view["type"] for view in views}) != len(views):
        raise SceneValidationError("Views must have unique renderer types.")
    view_types = {view["type"] for view in views}
    required_views = {"sample_space", "set", "formula", "monte_carlo"}
    if not required_views <= view_types:
        raise SceneValidationError("A probability scene is missing a required coordinated view.")
    if staged != ("probability_tree" in view_types):
        raise SceneValidationError("Probability tree availability must match the staged experiment.")
    view_ids = {view["id"] for view in views}

    focus_targets = []
    event_labels = {item["id"]: item["label"] for item in events}
    for index, item in enumerate(_list(raw.get("focus_targets"), "focus targets", 16)):
        item = _object(item, f"focus_targets[{index}]")
        identifier = _id(item.get("id"), "focus target")
        _unique(identifier, used)
        expression = item.get("expression")
        try:
            parse_expression(expression, event_map)
        except EventExpressionError as error:
            raise SceneValidationError(str(error)) from error
        raw_label = _require_human_label(
            identifier, _text(item.get("label"), "focus label"), "Focus target"
        )
        focus_targets.append({"id": identifier,
                              "label": display_expression(expression.strip(), event_labels) or raw_label,
                              "expression": expression.strip(), "source_pages": _pages(item.get("source_pages"), allowed_pages)})
    if not focus_targets:
        raise SceneValidationError("At least one focus target is required.")
    # Canonical IDs own identity and provenance; equal display labels are valid.
    semantic_ids |= {item["id"] for item in focus_targets}
    for view in views:
        if any(ref not in semantic_ids for ref in view["semantic_ids"]):
            raise SceneValidationError("A view references an unknown semantic id.")

    relations = []
    for index, item in enumerate(_list(raw.get("relations"), "relations", 24)):
        item = _object(item, f"relations[{index}]")
        identifier = _id(item.get("id"), "relation")
        _unique(identifier, used)
        source, target = item.get("source_event_id"), item.get("target_event_id")
        if source not in event_map or target not in event_map:
            raise SceneValidationError("A relation references an unknown event.")
        relation_type = item.get("type")
        if relation_type not in {"subset", "mutually_exclusive", "equivalent", "complement", "related"}:
            raise SceneValidationError("Unsupported relation type.")
        if relation_type == "subset" and not event_map[source] <= event_map[target]:
            raise SceneValidationError("Declared subset relation is false.")
        if relation_type == "mutually_exclusive" and event_map[source] & event_map[target]:
            raise SceneValidationError("Declared mutually exclusive events overlap.")
        relations.append({"id": identifier, "type": relation_type, "source_event_id": source,
                          "target_event_id": target, "source_pages": _pages(item.get("source_pages"), allowed_pages)})

    bindings = []
    for index, item in enumerate(_list(raw.get("bindings"), "bindings", MAX_BINDINGS)):
        item = _object(item, f"bindings[{index}]")
        identifier = _id(item.get("id"), "binding")
        _unique(identifier, used)
        semantic_id = item.get("semantic_id")
        refs = _list(item.get("view_ids"), "binding view ids", 5)
        if semantic_id not in semantic_ids or not refs or any(ref not in view_ids for ref in refs):
            raise SceneValidationError("A binding is broken.")
        bindings.append({"id": identifier, "semantic_id": semantic_id, "view_ids": list(dict.fromkeys(refs))})

    source_refs = []
    for index, item in enumerate(_list(raw.get("source_refs"), "source refs", 64)):
        item = _object(item, f"source_refs[{index}]")
        identifier = _id(item.get("id"), "source ref")
        _unique(identifier, used)
        if item.get("semantic_id") not in semantic_ids:
            raise SceneValidationError("A source reference targets an unknown semantic id.")
        source_refs.append({"id": identifier, "semantic_id": item["semantic_id"],
                            "source_pages": _pages(item.get("source_pages"), allowed_pages)})

    parameters, states = [], []
    for group, limit in (("parameters", 8), ("states", 12)):
        for index, item in enumerate(_list(raw.get(group), group, limit)):
            item = _object(item, f"{group}[{index}]")
            identifier = _id(item.get("id"), group[:-1])
            _unique(identifier, used)
            if group == "parameters":
                values = _list(item.get("allowed_values"), "parameter values", 12)
                values = [_text(value, "parameter value") for value in values]
                if item.get("kind") not in {"integer", "choice"} or item.get("default_value") not in values:
                    raise SceneValidationError("Parameter definition is invalid.")
                parameters.append({"id": identifier, "label": _text(item.get("label"), "parameter label"),
                                   "kind": item["kind"], "default_value": item["default_value"],
                                   "allowed_values": values, "source_pages": _pages(item.get("source_pages"), allowed_pages)})
            else:
                refs = _list(item.get("semantic_ids"), "state semantic ids", 12)
                if item.get("kind") not in {"focus", "selection", "event_expression"} or any(ref not in semantic_ids for ref in refs):
                    raise SceneValidationError("State definition is invalid.")
                states.append({"id": identifier, "label": _text(item.get("label"), "state label"),
                               "kind": item["kind"], "semantic_ids": list(refs)})

    equally_likely = raw.get("equally_likely")
    if not isinstance(equally_likely, bool):
        raise SceneValidationError("equally_likely must be boolean.")
    if equally_likely and len({item["weight"] for item in outcomes}) != 1:
        raise SceneValidationError("Equally likely outcomes must have equal weights.")

    normalized = {
        "scene_version": SCENE_SCHEMA_VERSION, "scene_id": scene_id,
        "title": _text(raw.get("title"), "scene title"), "domain": DOMAIN,
        "learning_goal": _text(raw.get("learning_goal"), "learning goal"),
        "source_pages": _pages(raw.get("source_pages"), allowed_pages),
        "equally_likely": equally_likely, "outcomes": outcomes, "events": events,
        "parameters": parameters, "states": states, "relations": relations,
        "experiment": {"staged": staged, "stages": stages, "inferred": inferred_staged},
        "views": views, "bindings": bindings, "focus_targets": focus_targets,
        "source_refs": source_refs,
    }
    normalized["universe"] = {
        "id": "S", "label": "S", "outcome_ids": frozenset(outcome_ids)
    }
    normalized["event_sets"] = event_map
    normalized["event_labels"] = event_labels
    normalized["focus_sets"] = {item["id"]: evaluate_expression(item["expression"], event_map, outcome_ids) for item in focus_targets}
    normalized["path_by_outcome"] = {
        outcome["id"]: tuple(outcome["path"]) for outcome in outcomes if outcome["path"]
    }
    normalized["outcome_by_path"] = {
        tuple(outcome["path"]): outcome["id"] for outcome in outcomes if outcome["path"]
    }
    return normalized


def clean_scene(raw, allowed_pages=()):
    """Graceful application boundary: malformed specs become None."""
    try:
        return normalize_scene(raw, allowed_pages)
    except (SceneValidationError, EventExpressionError, KeyError, TypeError, ValueError):
        return None
