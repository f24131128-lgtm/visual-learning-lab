"""Pure bounded sequence/state reducer. No model calls or model-authored mechanics."""
import copy
from scene.state import fingerprint
from .schema import MAX_HISTORY
from .planner import plain


def initial(spec):
    return dict(identity=fingerprint(spec), revision=0, serial=0,
                collections={c["id"]: [dict(id=f"item_{n}", text=v) for n, v in enumerate(c["initial"])] for c in spec["collections"]},
                states={s["id"]: s["initial"] for s in spec["states"]}, history=[], last_removed=None)


def valid(spec, state):
    if not isinstance(state, dict) or set(state) != {"identity", "revision", "serial", "collections", "states", "history", "last_removed"}: return False
    if state["identity"] != fingerprint(spec) or any(type(state[k]) is not int or not 0 <= state[k] <= 100000 for k in ("revision", "serial")): return False
    if not isinstance(state["history"], list) or len(state["history"]) > MAX_HISTORY: return False
    if not isinstance(state["collections"], dict) or set(state["collections"]) != {c["id"] for c in spec["collections"]}: return False
    if not isinstance(state["states"], dict) or set(state["states"]) != {s["id"] for s in spec["states"]}: return False
    for c in spec["collections"]:
        items = state["collections"][c["id"]]
        if not isinstance(items, list) or len(items) > c["capacity"]: return False
        if any(not isinstance(i, dict) or set(i) != {"id", "text"} or not plain(i["text"], 64) or not isinstance(i["id"], str) or len(i["id"]) > 64 for i in items): return False
        if len({i["id"] for i in items}) != len(items): return False
    if any(state["states"][s["id"]] not in s["values"] for s in spec["states"]): return False
    if state["last_removed"] is not None and not plain(state["last_removed"], 64): return False
    allowed = {t["id"] for t in spec["transitions"]}
    return all(isinstance(h, dict) and set(h) == {"transition_id", "revision"} and isinstance(h["transition_id"], str) and h["transition_id"] in allowed
               and type(h["revision"]) is int and 0 < h["revision"] <= state["revision"] for h in state["history"])


def enabled(spec, state, transition_id):
    if not valid(spec, state) or not isinstance(transition_id, str): return False
    t = next((t for t in spec["transitions"] if t["id"] == transition_id), None)
    if not t or state["revision"] >= 100000 or state["serial"] >= 100000: return False
    if t["operation"] == "set_state": return state["states"][t["target_id"]] == t["from_state"]
    items = state["collections"][t["target_id"]]
    if t["operation"].startswith("remove_"): return bool(items)
    capacity = next(c["capacity"] for c in spec["collections"] if c["id"] == t["target_id"])
    return len(items) < capacity


def apply(spec, state, event):
    """Return state and formal focus only on an atomic, current-scene valid event."""
    if not valid(spec, state) or not isinstance(event, dict) or set(event) != {"identity", "revision", "transition_id", "value"}: return None
    if type(event["revision"]) is not int or event["revision"] != state.get("revision") or event["identity"] != fingerprint(spec): return None
    if not enabled(spec, state, event["transition_id"]): return None
    t = next(t for t in spec["transitions"] if t["id"] == event["transition_id"])
    if not plain(event["value"], 64, True): return None
    trial = copy.deepcopy(state)
    if t["operation"] == "set_state": trial["states"][t["target_id"]] = t["to_state"]
    elif t["operation"].startswith("remove_"):
        removed = trial["collections"][t["target_id"]].pop(0 if t["operation"] == "remove_first" else -1)
        trial["last_removed"] = removed["text"]
    else:
        if not plain(event["value"], 64): return None
        trial["serial"] += 1
        item = dict(id=f"added_{trial['serial']}", text=event["value"])
        items = trial["collections"][t["target_id"]]
        items.insert(0 if t["operation"] == "prepend" else len(items), item)
    trial["revision"] += 1
    trial["history"] = (trial["history"] + [dict(transition_id=t["id"], revision=trial["revision"])])[-MAX_HISTORY:]
    return (trial, t["semantic_id"]) if valid(spec, trial) else None


def reset(spec, state):
    if not valid(spec, state) or state["revision"] >= 100000: return None
    result = initial(spec)
    result["revision"] = state["revision"] + 1
    result["serial"] = state["serial"]
    return result
