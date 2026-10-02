"""Canonical physical state, validated semantic patches and bounded replay."""

import copy
import math

from .engine import check_inverses, evaluate, frames, inverse_patch, invariant_report, project, snapshot
from .schema import MAX_RECORDING_STEPS
from .validator import validate_patch
from .policy import parameter_display, time_domain


def new_state(scene):
    return {"time": scene["time"]["min"],
            "parameters": {p["id"]: p["default"] for p in scene["parameters"]},
            "focus": scene["objects"][0]["semantic_id"], "baseline": None,
            "previous": None, "revision": 0, "recording": False, "recording_origin": None,
            "recorded": [], "last_token": None, "experiment": None, "replay_generation": 0}


def semantic(state):
    return {key: copy.deepcopy(state[key]) for key in ("time", "parameters", "focus", "baseline")}


def apply_patch(scene, state, patch, record=True):
    patch = validate_patch(scene, patch, parameters=state["parameters"])
    candidate = semantic(state)
    op = patch["op"]
    if op == "set_parameter":
        candidate["parameters"][patch["target_id"]] = patch["value"]
        # Preserve physical time if legal; a shortened event cannot retain a
        # post-impact time. The atomic patch moves every view to the new endpoint.
        domain = time_domain(scene, candidate["parameters"])
        candidate["time"] = min(domain["max"], max(domain["min"], candidate["time"]))
    elif op == "set_time": candidate["time"] = patch["value"]
    elif op == "set_focus": candidate["focus"] = patch["target_id"]
    elif candidate["baseline"]:
        candidate.update(copy.deepcopy(candidate["baseline"]))
    else:
        candidate.update({"time": scene["time"]["min"], "parameters": {p["id"]: p["default"] for p in scene["parameters"]}})
    snapshot(scene, candidate)
    values = evaluate(scene, candidate["parameters"], candidate["time"])
    check_inverses(scene, candidate["parameters"], values, project(scene, values))
    invariant_report(scene, candidate["parameters"], candidate["time"])
    # Recheck at the actual parameter state, including full bounded trajectory.
    if candidate["parameters"] != state["parameters"]:
        frames(scene, candidate["parameters"])
        invariant_report(scene, candidate["parameters"])
    state["previous"] = semantic(state)
    state.update(candidate)
    state["revision"] += 1
    if record: record_action(state, {"kind": "patch", "patch": patch})
    return state


def record_action(state, action):
    if state["recording"]:
        if len(state["recorded"]) >= MAX_RECORDING_STEPS:
            state["recording"] = False
        else:
            state["recorded"].append(copy.deepcopy(action))


def baseline_action(state, action, record=True):
    if action not in ("set", "clear"):
        raise ValueError("Invalid baseline action.")
    state["baseline"] = {key: copy.deepcopy(state[key]) for key in ("time", "parameters", "focus")} if action == "set" else None
    state["revision"] += 1
    if record: record_action(state, {"kind": "baseline", "action": action})


def start_recording(state):
    state.update(recording=True, recorded=[], recording_origin=semantic(state))


def run_experiment(scene, state, identifier):
    experiment = next((e for e in scene["experiments"] if e["id"] == identifier), None)
    if experiment is None: raise ValueError("Unknown experiment.")
    # Atomic validation: a failed recipe cannot leave a half-applied world.
    trial = copy.deepcopy(state)
    record_action(trial, {"kind": "experiment", "id": identifier})
    for patch in experiment["steps"]: apply_patch(scene, trial, patch)
    trial["experiment"] = identifier
    state.update(trial)


def validate_semantic(scene, value):
    if not isinstance(value, dict) or set(value) != {"time", "parameters", "focus", "baseline"}:
        raise ValueError("Malformed recording state.")
    snapshot(scene, value)
    validate_patch(scene, {"op": "set_time", "target_id": "time", "value": value["time"]}, parameters=value["parameters"])
    validate_patch(scene, {"op": "set_focus", "target_id": value["focus"], "value": None})
    invariant_report(scene, value["parameters"])
    frames(scene, value["parameters"])
    if value["baseline"] is not None:
        base = value["baseline"]
        if not isinstance(base, dict) or set(base) != {"time", "parameters", "focus"}: raise ValueError("Invalid recorded baseline.")
        validate_semantic(scene, base | {"baseline": None})


def replay_states(scene, state):
    actions = state["recorded"]
    if not isinstance(actions, list) or not 1 <= len(actions) <= MAX_RECORDING_STEPS:
        raise ValueError("Invalid recording length.")
    validate_semantic(scene, state["recording_origin"])
    trial = new_state(scene)
    trial.update(copy.deepcopy(state["recording_origin"]))
    results = [semantic(trial)]
    for action in actions:
        if not isinstance(action, dict): raise ValueError("Malformed recorded action.")
        if action.get("kind") == "patch" and set(action) == {"kind", "patch"}:
            apply_patch(scene, trial, action["patch"], record=False)
        elif action.get("kind") == "baseline" and set(action) == {"kind", "action"}:
            baseline_action(trial, action["action"], record=False)
        elif action.get("kind") == "experiment" and set(action) == {"kind", "id"}:
            if action["id"] not in {e["id"] for e in scene["experiments"]}: raise ValueError("Unknown recorded experiment.")
            # Marker only: the following validated patches contain the changes.
        else:
            raise ValueError("Unsupported recorded action.")
        results.append(semantic(trial))
    return results


def changes(scene, state):
    baseline = state["baseline"] or state["previous"]
    if not baseline: return []
    before, after = snapshot(scene, baseline), snapshot(scene, state)
    rows = []
    for item in scene["parameters"] + scene["metrics"]:
        if item in scene["parameters"]:
            a, b = before["parameters"][item["id"]], after["parameters"][item["id"]]
            display = parameter_display(item)
            a, b = a*display["factor"], b*display["factor"]
        else:
            a, b = before["projections"][item["id"]][0], after["projections"][item["id"]][0]
            display = {"unit": item["unit"]}
        if not math.isclose(a, b, abs_tol=1e-9, rel_tol=1e-9):
            rows.append({"label": item["label"], "unit": display["unit"], "before": a, "after": b, "delta": b-a,
                         "percent": 100*(b-a)/abs(a) if abs(a) > 1e-9 else None})
    return rows


def consume_event(scene, state, identity, event):
    """Ignore stale, duplicated or malformed browser messages without mutation."""
    if not isinstance(event, dict) or event.get("scene") != identity or type(event.get("revision")) is not int or event.get("revision") != state["revision"]:
        return False
    token = event.get("token")
    if not isinstance(token, str) or not 1 <= len(token) <= 80 or token == state["last_token"]:
        return False
    trial = copy.deepcopy(state)
    try:
        kind = event.get("kind")
        common = {"scene", "revision", "token", "kind"}
        if kind == "patch" and set(event) == common | {"patch"}:
            apply_patch(scene, trial, event["patch"])
        elif kind == "batch" and set(event) == common | {"patches"}:
            if not isinstance(event["patches"], list) or not 1 <= len(event["patches"]) <= 2: return False
            for patch in event["patches"]: apply_patch(scene, trial, patch)
        elif kind == "focus" and set(event) == common | {"semantic_id", "time"}:
            apply_patch(scene, trial, {"op": "set_time", "target_id": "time", "value": event["time"]})
            apply_patch(scene, trial, {"op": "set_focus", "target_id": event["semantic_id"], "value": None})
        elif kind == "baseline" and set(event) == common | {"action", "time"}:
            if event["action"] not in ("set", "clear", "restore"): return False
            apply_patch(scene, trial, {"op": "set_time", "target_id": "time", "value": event["time"]})
            if event["action"] == "restore": apply_patch(scene, trial, {"op": "restore_baseline", "target_id": "", "value": None})
            else: baseline_action(trial, event["action"])
        elif kind == "experiment" and set(event) == common | {"id", "time"}:
            apply_patch(scene, trial, {"op": "set_time", "target_id": "time", "value": event["time"]})
            run_experiment(scene, trial, event["id"])
        elif kind == "record" and set(event) == common | {"action", "time"}:
            if event["action"] not in ("start", "stop", "clear", "replay"): return False
            apply_patch(scene, trial, {"op": "set_time", "target_id": "time", "value": event["time"]})
            if event["action"] == "start": start_recording(trial)
            elif event["action"] == "stop": trial["recording"] = False
            elif event["action"] == "clear": trial.update(recorded=[], recording=False, recording_origin=None)
            else:
                replay_states(scene, trial)
                trial.update(recording=False, replay_requested=True, replay_generation=trial["replay_generation"]+1)
        elif kind == "inverse" and set(event) == common | {"binding_id", "value"}:
            patch = inverse_patch(scene, trial, event["binding_id"], event["value"])
            inverse = next(b for b in scene["inverse_bindings"] if b["id"] == event["binding_id"])
            obj = next(o for o in scene["objects"] if o["id"] == inverse["object_id"])
            apply_patch(scene, trial, {"op": "set_focus", "target_id": obj["semantic_id"], "value": None})
            apply_patch(scene, trial, patch)
        elif kind == "inverse" and set(event) == common | {"binding_id", "value", "time"}:
            apply_patch(scene, trial, {"op": "set_time", "target_id": "time", "value": event["time"]})
            legacy = event.copy(); legacy.pop("time"); legacy["revision"] = trial["revision"]
            if not consume_event(scene, trial, identity, legacy): return False
        elif kind == "replay" and set(event) == common | {"index"}:
            states = replay_states(scene, trial)
            index = event["index"]
            if type(index) is not int or not 0 <= index < len(states): return False
            trial.update(states[index]); trial["revision"] += 1
        else: return False
    except (ValueError, TypeError, KeyError, OverflowError):
        return False
    trial["last_token"] = token
    state.update(trial)
    return True


def acknowledge_rejection(state, identity, event):
    """Release a waiting browser after a rejected current-scene gesture.

    Only protocol metadata changes; the last safe physical state is preserved.
    Stale/duplicate/cross-scene messages must not repeatedly advance revisions.
    """
    if (isinstance(event, dict) and event.get("scene") == identity
            and type(event.get("revision")) is int and event["revision"] == state["revision"]
            and isinstance(event.get("token"), str) and 1 <= len(event["token"]) <= 80
            and event["token"] != state["last_token"]):
        state.update(last_token=event["token"], revision=state["revision"]+1)
        return True
    return False
