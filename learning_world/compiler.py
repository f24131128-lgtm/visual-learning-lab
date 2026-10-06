"""One explicit plan+process request, bounded context/cache, isolated failures."""
import json
from i18n import output_language_instruction
from scene.state import fingerprint
from .schema import VERSION, SCHEMA, INSTRUCTIONS, MAX_PAYLOAD
from .planner import normalize
from .diagnostics import record, Rejection, safe_id
from .capabilities import contracts, POLICY_REVISION


def capabilities(analysis, wrapper, lab, analogy=None):
    scene = (wrapper or {}).get("scene")
    candidate = analysis.get("learning_scene_candidate", {})
    domain = scene.get("domain") if scene else candidate.get("domain") if candidate.get("suitable") is True else None
    return dict(process=True, spatial=domain == "spatial_dynamics", structural=domain == "probability_sets",
                analogy=True, graph=any(isinstance(analysis.get(k), dict) and analysis[k].get("suitable") is True
                for k in ("concept_map", "visual_flow", "comparison")), lab=bool((lab or {}).get("demos")))


def context(analysis, source, catalog, pages, caps, focus):
    if not catalog or len(catalog) > 100: raise ValueError("catalog")
    ids = [focus] if focus in catalog else list(catalog)[:16]
    # Neighbour IDs permit transitions and relationships to share formal identity.
    ids += [i for i in catalog if i not in ids][:16-len(ids)]
    bounded_catalog = {i: dict(label=str(catalog[i]["label"])[:160],
        pages=[p for p in catalog[i].get("pages", []) if type(p) is int and p in pages][:8],
        kind=catalog[i].get("kind", ""), equation=str(catalog[i].get("equation", ""))[:400]) for i in ids}
    if source.get("kind") == "pdf":
        texts = source.get("page_texts", {})
        text = "\n".join(f"[Page {p}]\n{str(texts.get(p, texts.get(str(p), '')))[:1000]}" for p in pages[:8])
        if not any(str(texts.get(p, texts.get(str(p), ""))).strip() for p in pages[:8]): raise ValueError("source")
    else: text = str(source.get("source_text", source.get("text", "")))[:8000]
    if not text.strip(): raise ValueError("source")
    result = dict(analysis_language=analysis.get("analysis_language", "zh-TW"),
        catalog=bounded_catalog, focus=focus if focus in bounded_catalog else None, allowed_pages=list(pages)[:8],
        capabilities=caps, runtime_contracts=contracts(caps),
        quick_summary=str(analysis.get("quick_summary", ""))[:1200], source_context=text)
    if len(json.dumps(result, ensure_ascii=False).encode()) > 24000: raise ValueError("context_bound")
    return result


def identity(material, language, source, catalog, caps, focus):
    # The always-present process adapter was omitted from the old request hints.
    # Advertising it must not invalidate an already safe v1 process or pending
    # candidate. Variable specialized capabilities retain their existing identity.
    return (material, language, VERSION, fingerprint([source, catalog, {k: v for k, v in caps.items() if k != "process"}, POLICY_REVISION]), focus)


def ensure(store, material):
    if store.get("material") != material:
        store.clear(); store.update(material=material, cache={}, active=None, errors={}, states={})
    store.setdefault("pending", {})
    store.setdefault("diagnostics", {})
    store.setdefault("request_count", 0)
    return store


def build(store, key, client, model, data, catalog, pages, caps, force_new=False):
    if key in store["cache"]:
        store["active"] = key
        return store["cache"][key]
    raw = None
    stage = "request"
    try:
        pending = store.setdefault("pending", {})
        if key in pending and not force_new:
            raw = pending[key]
        else:
            language = data["analysis_language"]
            store["request_count"] = store.get("request_count", 0) + 1
            response = client.responses.create(model=model,
                instructions=INSTRUCTIONS + "\n" + output_language_instruction(language),
                input=json.dumps(data, ensure_ascii=False),
                text={"format": dict(type="json_schema", name="learning_world_plan_v1", strict=True, schema=SCHEMA)})
            stage = "response"
            if getattr(response, "status", None) == "incomplete": raise Rejection("incomplete")
            if any(getattr(c, "type", None) == "refusal" for o in getattr(response, "output", []) or [] for c in getattr(o, "content", []) or []): raise Rejection("refusal")
            if not isinstance(response.output_text, str) or len(response.output_text.encode()) > MAX_PAYLOAD: raise Rejection("response_bound")
            raw = json.loads(response.output_text)
            if isinstance(raw, dict) and (set(raw) == set(SCHEMA["properties"]) or
                    (raw.get("version") == "1.0" and set(raw) == set(SCHEMA["properties"]) - {"execution"})):
                pending[key] = raw
                while len(pending) > 2: pending.pop(next(iter(pending)))
        stage = "normalize"
        supplied = {i: catalog[i] for i in data["catalog"] if i in catalog}
        spec = normalize(raw, supplied, pages, caps)
        stage = "cache"
        store["cache"][key] = spec; store["active"] = key
        pending.pop(key, None)
        store["errors"].pop(key, None)
        while len(store["cache"]) > 4:
            old = next(iter(store["cache"])); store["cache"].pop(old); store["states"].pop(old, None)
        trace = record(store, key, "accepted", raw=raw, normalized=spec)
        trace["supplied_semantic_ids"] = [safe_id(i) for i in data["catalog"]]
        trace["runtime_capabilities"] = {k: v for k, v in caps.items() if type(v) is bool}
        return spec
    except Exception as error:
        # Neither SDK messages nor original source are diagnostic display data.
        trace = record(store, key, stage, error, raw=raw)
        trace["supplied_semantic_ids"] = [safe_id(i) for i in data.get("catalog", {})]
        trace["runtime_capabilities"] = {k: v for k, v in caps.items() if type(v) is bool}
        return None
