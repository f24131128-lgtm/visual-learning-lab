"""Pure capability-aware selection. Labels, topics and source words never route execution."""
import copy
import json
import re
import hashlib
from .schema import VERSION, MAX_PAYLOAD, FEATURES, FAMILIES, OPS, MAX_ITEMS
from .diagnostics import Rejection
from .capabilities import eligible


def plain(value, bound=400, empty=False):
    return isinstance(value, str) and len(value) <= bound and (empty or bool(value.strip())) and not re.search(r"[<>\x00-\x1f]", value)


def exact(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError("fields")


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value)


def bounded_list(value, maximum):
    if not isinstance(value, list) or len(value) > maximum: raise ValueError("count")
    return value


def normalize_process(raw, catalog):
    exact(raw, ("collections", "states", "transitions", "annotations"))
    result = copy.deepcopy(raw)
    # Semantic IDs and representation IDs are different namespaces. A model may
    # legitimately reuse the formal ID as its local declaration ID. Derive a
    # stable trusted runtime identity and rewrite typed target references, never
    # alter the canonical semantic_id or dispatch by array position/label.
    originals, renamed = set(), {}
    for group in ("collections", "states", "transitions"):
        for n, item in enumerate(bounded_list(result[group], 12 if group == "transitions" else 3)):
            path = f"$.process.{group}[{n}].id"
            if not isinstance(item, dict) or not identifier(item.get("id")): raise Rejection("identity", path)
            old = item["id"]
            if old in originals: raise Rejection("duplicate_runtime_id", path)
            originals.add(old)
            if old in catalog:
                derived = "process_" + hashlib.sha256((group+":"+old).encode()).hexdigest()[:24]
                if derived in catalog or derived in originals or derived in renamed.values(): raise Rejection("identity", path)
                renamed[old] = derived
                item["id"] = derived
    # A supplied runtime name may also collide with a previously derived name.
    if set(renamed.values()) & (originals-set(renamed)): raise Rejection("identity", "$.process")
    for item in result["transitions"]:
        if isinstance(item.get("target_id"), str): item["target_id"] = renamed.get(item["target_id"], item["target_id"])
    used = set()
    def core(item, fields, path):
        exact(item, fields)
        if not identifier(item["id"]) or item["id"] in used or item["id"] in catalog: raise Rejection("identity", path+".id")
        used.add(item["id"])
        if not isinstance(item["semantic_id"], str) or item["semantic_id"] not in catalog: raise Rejection("reference", path+".semantic_id")
        if item["label"] == "": item["label"] = catalog[item["semantic_id"]]["label"]
        if not plain(item["label"], 160): raise Rejection("label", path+".label")
    collections, states = {}, {}
    for n, item in enumerate(bounded_list(result["collections"], 3)):
        path = f"$.process.collections[{n}]"
        core(item, ("id", "semantic_id", "label", "initial", "capacity", "first_label", "last_label"), path)
        if type(item["capacity"]) is not int or not 1 <= item["capacity"] <= MAX_ITEMS: raise ValueError("capacity")
        if any(not plain(v, 64) for v in bounded_list(item["initial"], item["capacity"])): raise ValueError("items")
        if not all(plain(item[k], 80, True) for k in ("first_label", "last_label")): raise ValueError("endpoint")
        collections[item["id"]] = item
    for n, item in enumerate(bounded_list(result["states"], 3)):
        core(item, ("id", "semantic_id", "label", "values", "initial"), f"$.process.states[{n}]")
        vals = bounded_list(item["values"], 12)
        if not vals or any(not plain(v, 64) for v in vals) or len(set(vals)) != len(vals) or item["initial"] not in vals: raise ValueError("states")
        states[item["id"]] = item
    transitions = bounded_list(result["transitions"], 12)
    if not (collections or states) or not transitions: raise ValueError("required_process")
    for n, item in enumerate(transitions):
        path = f"$.process.transitions[{n}]"
        core(item, ("id", "semantic_id", "label", "explanation", "operation", "target_id", "from_state", "to_state"), path)
        if item["operation"] not in OPS: raise Rejection("unsafe_operation", path+".operation")
        if item["explanation"] == "": item["explanation"] = item["label"]
        if not plain(item["explanation"]) or not identifier(item["target_id"]): raise Rejection("transition", path)
        if item["operation"] == "set_state":
            target = states.get(item["target_id"])
            if not target or item["from_state"] not in target["values"] or item["to_state"] not in target["values"] or item["from_state"] == item["to_state"]: raise ValueError("core_transition")
        elif item["target_id"] not in collections or item["from_state"] != "" or item["to_state"] != "": raise ValueError("core_transition")
    result["annotations"] = [a for a in bounded_list(result["annotations"], 8)
        if isinstance(a, dict) and set(a) == {"semantic_id", "text"} and isinstance(a["semantic_id"], str)
        and a["semantic_id"] in catalog and plain(a["text"])]
    return result


def choose(features, preferred, capabilities, process):
    """Trusted mechanics use validated semantic flags and runtime contracts only."""
    if not features["interaction_value"]:
        return "static" if features["structure"] else "none"
    choices = eligible(features, capabilities, process)
    # A static diagram cannot deliver declared useful continuous manipulation.
    # Use an already validated numeric lab when those exact needs are supported.
    if preferred == "static" and "dynamic" in choices and capabilities.get("lab"):
        return "dynamic"
    return preferred if preferred in choices else next(iter(choices), "static" if features["structure"] else "none")


def check_unused_process(raw):
    """Discard only bounded inert decorations, never a failed required process.

    Required envelope, field/type/count/text/operation security checks still
    apply. Semantic/runtime references and legal finite-state mechanics are not
    interpreted for an artifact that will never run or publish those fields.
    """
    fields = {
        "collections": ("id", "semantic_id", "label", "initial", "capacity", "first_label", "last_label"),
        "states": ("id", "semantic_id", "label", "values", "initial"),
        "transitions": ("id", "semantic_id", "label", "explanation", "operation", "target_id", "from_state", "to_state"),
    }
    for group in fields:
        for n, item in enumerate(raw[group]):
            exact(item, fields[group])
            path = f"$.process.{group}[{n}]"
            for key in ("id", "semantic_id"):
                if not identifier(item[key]): raise Rejection("identity", path + "." + key)
            if not plain(item["label"], 160, True): raise Rejection("label", path + ".label")
            if group == "collections":
                if type(item["capacity"]) is not int or not 1 <= item["capacity"] <= MAX_ITEMS: raise ValueError("capacity")
                if any(not plain(v, 64) for v in bounded_list(item["initial"], MAX_ITEMS)): raise ValueError("items")
                if not all(plain(item[k], 80, True) for k in ("first_label", "last_label")): raise ValueError("endpoint")
            elif group == "states":
                if any(not plain(v, 64) for v in bounded_list(item["values"], 12)) or not plain(item["initial"], 64, True): raise ValueError("states")
            else:
                if item["operation"] not in OPS: raise Rejection("unsafe_operation", path + ".operation")
                if not identifier(item["target_id"]) or not all(plain(item[k], 400 if k == "explanation" else 64, True)
                        for k in ("explanation", "from_state", "to_state")): raise Rejection("transition", path)


def normalize(raw, catalog, pages, capabilities):
    if len(json.dumps(raw, ensure_ascii=False, allow_nan=False).encode()) > MAX_PAYLOAD: raise ValueError("payload")
    legacy = isinstance(raw, dict) and raw.get("version") == "1.0"
    fields = ("version", "focus_ids", "source_pages", "features", "preferred", "reason", "process")
    exact(raw, fields if legacy else fields + ("execution",))
    if raw["version"] not in ("1.0", VERSION) or raw["preferred"] not in FAMILIES or not plain(raw["reason"]): raise ValueError("plan")
    exact(raw["features"], FEATURES)
    if any(type(v) is not bool for v in raw["features"].values()): raise ValueError("features")
    ids = bounded_list(raw["focus_ids"], 16)
    if not ids or any(not identifier(i) or i not in catalog for i in ids) or len(set(ids)) != len(ids): raise ValueError("focus")
    refs = bounded_list(raw["source_pages"], 8)
    if any(type(p) is not int or p not in pages for p in refs) or len(set(refs)) != len(refs): raise ValueError("pages")
    # Page references must belong to the selected formal entities, not merely this PDF.
    supported = {p for i in ids for p in catalog[i].get("pages", []) if p in pages}
    if not set(refs) <= supported: raise ValueError("provenance")
    exact(raw["process"], ("collections", "states", "transitions", "annotations"))
    for field, maximum in (("collections", 3), ("states", 3), ("transitions", 12), ("annotations", 8)):
        bounded_list(raw["process"][field], maximum)
    recovery = []
    if raw["preferred"] == "process":
        process = normalize_process(raw["process"], catalog) if any(raw["process"].values()) else None
    else:
        process = None
        check_unused_process(raw["process"])
        if any(raw["process"].values()): recovery.append("unused_process_omitted")
    if raw["preferred"] == "process" and process is None: raise ValueError("missing_process")
    if process:
        mapped = {v["semantic_id"] for k in ("collections", "states", "transitions") for v in process[k]}
        if not mapped <= set(ids): raise ValueError("process_focus")
    family = choose(raw["features"], raw["preferred"], capabilities, process)
    execution = None
    if raw["preferred"] == "execution":
        from .execution import normalize as normalize_execution
        execution = normalize_execution(raw.get("execution"), catalog, ids)
        family = "execution" if raw["features"]["interaction_value"] and capabilities.get("process", True) else "static"
    elif not legacy and raw["execution"] is not None:
        # Never silently run an execution payload for an unrelated family.
        raise ValueError("unused_execution")
    return dict(version=raw["version"], focus_ids=list(ids), source_pages=list(refs), features=dict(raw["features"]),
                family=family, reason=raw["reason"], process=process if family == "process" else None,
                execution=execution if family == "execution" else None,
                adapted=family != raw["preferred"], requested_family=raw["preferred"],
                degraded=family in ("static", "none") and family != raw["preferred"], recovery_codes=recovery)
