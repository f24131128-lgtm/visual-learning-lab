"""Bounded developer trace. Never retain prompts, PDF text, credentials or code."""
import logging
import math
import re
import hashlib

logger = logging.getLogger(__name__)


class Rejection(ValueError):
    def __init__(self, code, path="$", detail=None):
        self.code, self.path, self.detail = code, path, detail
        super().__init__(code + " at " + path)


def safe(value):
    if type(value) in (bool, int) or value is None: return value
    if type(value) is float: return value if math.isfinite(value) else "nonfinite"
    if isinstance(value, str):
        value = re.sub(r"sk-[A-Za-z0-9_-]+|Bearer\s+\S+", "[redacted]", value)
        return re.sub(r"[\x00-\x1f\x7f]|<[^>]*>", "", value)[:160]
    return "unsupported"


def summary(raw):
    if not isinstance(raw, dict): return {"type": type(raw).__name__}
    result = {k: safe(raw.get(k)) for k in ("version", "suitable", "reason", "formal_focus", "selected_candidate", "analogy_domain")}
    fields = {
        "candidates": ("id", "title", "clarity", "visualizability", "interaction", "fidelity", "misconception_risk"),
        "formal_entities": ("id",), "analogy_entities": ("id", "label"),
        "mappings": ("id", "formal_id", "analogy_id", "fidelity", "mode"),
        "parameters": ("id", "mapping_id", "formal_target", "min", "max", "default", "scale", "offset"),
        "primitives": ("id", "entity_id", "type", "control_parameter", "count", "wrap_x", "wrap_min", "wrap_max"),
    }
    for group, keys in fields.items():
        items = raw.get(group)
        result[group] = [{k: safe(item.get(k)) for k in keys} for item in items[:24] if isinstance(item, dict)] if isinstance(items, list) else {"type": type(items).__name__}
    if isinstance(raw.get("time"),dict): result["time"]={k:safe(raw["time"].get(k)) for k in ("duration","frames")}
    primitives=raw.get("primitives")
    if isinstance(primitives,list):
        for item,out in zip([p for p in primitives[:24] if isinstance(p,dict)],result["primitives"]):
            out["math_slots"]={field:dict(length=len(item[field]),blank=not item[field].strip(),fingerprint=hashlib.sha256(item[field].encode()).hexdigest()[:16])
                               for field in ("x","y","x2","y2","radius","value","visible") if isinstance(item.get(field),str) and len(item[field])<=400}
    for item,out in zip(raw.get("formal_entities",[]) if isinstance(raw.get("formal_entities"),list) else [],result["formal_entities"] if isinstance(result["formal_entities"],list) else []):
        pages=item.get("source_pages") if isinstance(item,dict) else None
        if isinstance(pages,list): out["source_pages"]=[p for p in pages[:8] if type(p) is int]
    return result


def record(store, key, stage, error=None, raw=None, normalized=None):
    entry = dict(stage=stage, code=error.code if isinstance(error, Rejection) else type(error).__name__ if error else "accepted",
                 path=error.path if isinstance(error, Rejection) else "$", generated=summary(raw))
    if isinstance(error,Rejection) and isinstance(error.detail,dict):
        entry["detail"]={k:safe(v) for k,v in error.detail.items() if k in ("primitive_type","field","length","fingerprint","problem","used_for_geometry",
            "limit_min","limit_max","observed_min","observed_max","token_index","time","wrap_x","check_stage")}
    if normalized is not None:
        entry["normalized"] = summary(normalized)
        entry["recoveries"] = normalized.get("recoveries", [])[:32]
    # Exception messages from SDK/network/JSON parsing are deliberately omitted.
    if error is not None:
        status = getattr(error, "status_code", None)
        if type(status) is int: entry["http_status"] = status
        # Allowlisted provider classifications only; never its message/body.
        body = getattr(error,"body",None)
        detail = body.get("error",body) if isinstance(body,dict) else {}
        if isinstance(detail,dict):
            for field in ("type","code"):
                if detail.get(field) in ("invalid_json_schema","invalid_request_error","model_not_found","rate_limit_exceeded","insufficient_quota","invalid_api_key"):
                    entry["provider_"+field]=detail[field]
        store["errors"].clear(); store["errors"][key] = entry["code"]
        logger.warning("Analogy rejected stage=%s code=%s path=%s", stage, entry["code"], entry["path"])
        bounds=entry.get("detail",{})
        if "observed_min" in bounds:
            logger.warning("Analogy bounds check=%s field=%s observed=(%s,%s) limit=(%s,%s) wrap_x=%s",
                bounds.get("check_stage"),bounds.get("field"),bounds.get("observed_min"),bounds.get("observed_max"),
                bounds.get("limit_min"),bounds.get("limit_max"),bounds.get("wrap_x"))
    traces = store.setdefault("diagnostics", {})
    traces[key] = entry
    while len(traces) > 4: traces.pop(next(iter(traces)))
    return entry
