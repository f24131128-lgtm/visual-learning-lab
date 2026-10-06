"""Bounded resolved invocation trees; no programming-language/code interpreter.

The model supplies arguments and safe numeric result relationships. Trusted code
owns frames, stack order, waiting/completion, exact caller routing and history.
"""
import copy
import json
import math
from scene.state import fingerprint
from safe_math import valid_variable, validate_expression, evaluate_expression

MAX_CALLS, MAX_DEPTH, MAX_HISTORY = 24, 8, 80
MAX_VALUE = 1e9


def scalar(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > MAX_VALUE:
        raise ValueError("Invalid execution value")
    return float(value)


def normalize(raw, catalog, focus_ids):
    from .planner import exact, identifier, plain, bounded_list
    if len(json.dumps(raw, ensure_ascii=False, allow_nan=False).encode()) > 24000: raise ValueError("execution_payload")
    exact(raw, ("root_id", "calls", "annotations"))
    calls, ids = [], set()
    for item in bounded_list(raw["calls"], MAX_CALLS):
        exact(item, ("id", "semantic_id", "label", "arguments", "children", "result_expression", "return_semantic_id"))
        if not identifier(item["id"]) or item["id"] in ids or not plain(item["label"], 160): raise ValueError("call_identity")
        ids.add(item["id"])
        if any(item[k] not in catalog or item[k] not in focus_ids for k in ("semantic_id", "return_semantic_id")): raise ValueError("call_reference")
        symbols, args, children = set(), [], []
        for arg in bounded_list(item["arguments"], 4):
            exact(arg, ("id", "label", "value"))
            if not valid_variable(arg["id"]) or arg["id"] in symbols or not plain(arg["label"], 80): raise ValueError("argument")
            symbols.add(arg["id"]); args.append(dict(arg, value=scalar(arg["value"])))
        for child in bounded_list(item["children"], 3):
            exact(child, ("call_id", "result_id", "result_label", "semantic_id", "label"))
            if (not identifier(child["call_id"]) or not valid_variable(child["result_id"]) or child["result_id"] in symbols
                    or child["semantic_id"] not in catalog or child["semantic_id"] not in focus_ids
                    or not plain(child["label"], 160) or not plain(child["result_label"], 80)):
                raise ValueError("child_binding")
            symbols.add(child["result_id"]); children.append(dict(child))
        # Existing safe_math supports <=5 bounded symbols; never enlarge its grammar.
        expression = validate_expression(item["result_expression"], symbols)
        calls.append(dict(item, arguments=args, children=children, result_expression=expression))
    by_id = {c["id"]: c for c in calls}
    if raw["root_id"] not in by_id: raise ValueError("execution_root")
    parents, seen, values = {}, set(), {}
    def visit(identifier, depth):
        if depth > MAX_DEPTH or identifier in seen: raise ValueError("execution_topology")
        seen.add(identifier)
        call = by_id[identifier]
        env = {a["id"]: a["value"] for a in call["arguments"]}
        for edge in call["children"]:
            child = edge["call_id"]
            if child not in by_id or child in parents or child == raw["root_id"]: raise ValueError("execution_topology")
            parents[child] = identifier
            env[edge["result_id"]] = visit(child, depth+1)
        result = scalar(float(evaluate_expression(call["result_expression"], env)))
        values[identifier] = result
        return result
    visit(raw["root_id"], 1)
    if seen != ids: raise ValueError("unreachable_calls")
    annotations = [dict(a) for a in bounded_list(raw["annotations"], 8)
        if isinstance(a, dict) and set(a) == {"semantic_id", "text"} and a["semantic_id"] in catalog
        and a["semantic_id"] in focus_ids and plain(a["text"], 400)]
    return dict(root_id=raw["root_id"], calls=calls, annotations=annotations, parents=parents, results=values)


def frame(spec, call_id, caller=None):
    call = next(c for c in spec["calls"] if c["id"] == call_id)
    return dict(id="frame_"+fingerprint([fingerprint(spec), call_id])[:24], call_id=call_id,
        caller=caller, status="active", returned={}, result=None)


def initial(spec):
    return dict(identity=fingerprint(spec), revision=0, frames=[frame(spec, spec["root_id"])], history=[])


def _apply(spec, state, operation):
    trial = copy.deepcopy(state)
    top = trial["frames"][-1]
    call = next(c for c in spec["calls"] if c["id"] == top["call_id"])
    missing = [e for e in call["children"] if e["result_id"] not in top["returned"]]
    if operation == "call" and top["status"] == "active" and missing and len(trial["frames"]) < MAX_DEPTH:
        top["status"] = "waiting"
        trial["frames"].append(frame(spec, missing[0]["call_id"], top["id"]))
        semantic = missing[0]["semantic_id"]
    elif operation == "complete" and top["status"] == "active" and not missing:
        env = {a["id"]: a["value"] for a in call["arguments"]} | top["returned"]
        top.update(status="completed", result=scalar(float(evaluate_expression(call["result_expression"], env))))
        semantic = call["semantic_id"]
    elif operation == "return" and top["status"] == "completed" and len(trial["frames"]) > 1:
        parent = trial["frames"][-2]
        parent_call = next(c for c in spec["calls"] if c["id"] == parent["call_id"])
        edge = next(e for e in parent_call["children"] if e["call_id"] == top["call_id"])
        if parent["status"] != "waiting" or top["caller"] != parent["id"]: return None
        parent["returned"][edge["result_id"]] = top["result"]
        parent["status"] = "active"
        trial["frames"].pop()
        semantic = call["return_semantic_id"]
    else: return None
    trial["revision"] += 1
    trial["history"].append(operation)
    return trial, semantic


def valid(spec, state):
    """Bounded deterministic history proves reachable state, not just shape.

    This rejects forged completed results/callers/stack order and unsafe events.
    At most 3*24 actions are replayed, using only the fixed arithmetic interpreter.
    """
    try:
        if not isinstance(state, dict) or set(state) != {"identity", "revision", "frames", "history"}: return False
        if state["identity"] != fingerprint(spec) or type(state["revision"]) is not int or not 0 <= state["revision"] <= 100000: return False
        history = state["history"]
        if not isinstance(history, list) or len(history) > MAX_HISTORY or any(h not in ("call", "complete", "return") for h in history): return False
        frames = state["frames"]
        if not isinstance(frames, list) or not 1 <= len(frames) <= MAX_DEPTH: return False
        for f in frames:
            if not isinstance(f, dict) or set(f) != {"id", "call_id", "caller", "status", "returned", "result"}: return False
            if not isinstance(f["returned"], dict) or len(f["returned"]) > 3: return False
            for value in f["returned"].values(): scalar(value)
            if f["result"] is not None: scalar(f["result"])
        expected = initial(spec)
        for operation in history:
            result = _apply(spec, expected, operation)
            if result is None: return False
            expected = result[0]
        # Resets advance the monotonic revision without retaining older history.
        return state["revision"] >= len(history) and state["frames"] == expected["frames"]
    except (ValueError, TypeError, KeyError, StopIteration, OverflowError): return False


def enabled(spec, state, operation):
    return bool(valid(spec, state) and state["revision"] < 100000 and len(state["history"]) < MAX_HISTORY
                and _apply(spec, state, operation) is not None)


def event(spec, state, operation):
    top = state["frames"][-1]
    return dict(identity=fingerprint(spec), revision=state["revision"], operation=operation,
                frame=top["id"], destination=top["caller"] if operation == "return" else None)


def apply(spec, state, value):
    if not valid(spec, state) or not isinstance(value, dict) or set(value) != {"identity", "revision", "operation", "frame", "destination"}: return None
    if type(value["revision"]) is not int or value != event(spec, state, value["operation"]): return None
    if not enabled(spec, state, value["operation"]): return None
    return _apply(spec, state, value["operation"])


def reset(spec, state):
    if not valid(spec, state) or state["revision"] >= 100000: return None
    result = initial(spec); result["revision"] = state["revision"]+1
    return result
