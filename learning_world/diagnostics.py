"""Bounded controlled diagnostics; no prompts, source excerpts or raw declarations exported."""
import hashlib
import logging
import re

logger = logging.getLogger(__name__)


class Rejection(ValueError):
    def __init__(self, code, path="$"):
        self.code, self.path = code, path
        super().__init__(code)


def safe_id(value):
    if isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value) and not value.startswith("sk-"):
        return value
    return "invalid"


def summary(raw):
    if not isinstance(raw, dict): return dict(shape=type(raw).__name__)
    features = raw.get("features", {})
    process = raw.get("process", {})
    reason = raw.get("reason", "")
    result = dict(planner_family=safe_id(raw.get("preferred")),
        reason_length=len(reason) if isinstance(reason, str) else 0,
        reason_fingerprint=hashlib.sha256(reason.encode()).hexdigest()[:16] if isinstance(reason, str) else None,
        required_capabilities=[k for k, v in features.items() if v is True and k in
            ("equations", "continuous_parameters", "time_dynamics", "spatial_relations", "finite_outcomes", "set_relations", "ordered_collection", "transitions", "analogy_suitable", "structure", "interaction_value")] if isinstance(features, dict) else [],
        focus_ids=[safe_id(i) for i in raw.get("focus_ids", [])[:16]] if isinstance(raw.get("focus_ids"), list) else [])
    if isinstance(process, dict):
        result["entities"] = {group: [{k: safe_id(i.get(k)) for k in ("id", "semantic_id", "operation", "target_id") if k in i}
            for i in items[:12] if isinstance(i, dict)] for group in ("collections", "states", "transitions")
            if isinstance(items := process.get(group), list)}
    return result


def record(store, key, stage, error=None, raw=None, normalized=None):
    code = error.code if isinstance(error, Rejection) else str(error) if type(error) is ValueError and str(error) in (
        "fields", "identity", "reference", "label", "count", "capacity", "items", "endpoint", "states", "transition", "core_transition", "required_process", "payload", "plan", "features", "focus", "pages", "provenance", "process_focus", "missing_process", "source", "catalog", "context_bound", "incomplete", "refusal", "response_bound") else "external_failure" if error else "accepted"
    entry = dict(stage=stage, code=code, path=error.path if isinstance(error, Rejection) else "$", generated=summary(raw),
        compiled_family=normalized.get("family") if normalized else None, normalized_entity_ids=[],
        process_runtime_reached=False, legacy_visual_flow_used=False)
    if normalized and normalized.get("process"):
        entry["normalized_entity_ids"] = [safe_id(i["id"]) for g in ("collections", "states", "transitions") for i in normalized["process"][g]]
    if normalized:
        entry["recovery_codes"] = list(normalized.get("recovery_codes", []))[:8]
        entry["degraded"] = normalized.get("degraded", False)
    status = getattr(error, "status_code", None)
    if type(status) is int: entry["http_status"] = status
    body = getattr(error, "body", None)
    detail = body.get("error", body) if isinstance(body, dict) else {}
    if isinstance(detail, dict):
        for field in ("type", "code"):
            if detail.get(field) in ("invalid_json_schema", "invalid_request_error", "rate_limit_exceeded", "insufficient_quota", "invalid_api_key", "model_not_found"):
                entry["provider_"+field] = detail[field]
    store.setdefault("diagnostics", {})[key] = entry
    store["diagnostic_active"] = key
    while len(store["diagnostics"]) > 4: store["diagnostics"].pop(next(iter(store["diagnostics"])))
    if error:
        store["errors"][key] = code
        while len(store["errors"]) > 4: store["errors"].pop(next(iter(store["errors"])))
        logger.warning("Learning representation rejected stage=%s code=%s path=%s", stage, code, entry["path"])
    return entry
