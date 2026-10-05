"""Explicit Learning Scene compiler request and application integration."""

import json
import logging
import os
import unicodedata

from openai import OpenAI
import streamlit as st

from i18n import RESPONSE_LANGUAGES, output_language_instruction, tr
from .runtime import render_scene
from .schema import DOMAIN, LEARNING_SCENE_SCHEMA, SCENE_INSTRUCTIONS
from .state import ensure_state, reset_scene_state, save_rejection, save_scene
from .validator import normalize_scene
from .world.schema import DOMAIN as WORLD_DOMAIN, WORLD_SCHEMA, INSTRUCTIONS as WORLD_INSTRUCTIONS

MAX_CONTEXT_CHARS = 18_000
MAX_SOURCE_CHARS = 10_000
MAX_CANDIDATE_CHARS = 12_000
logger = logging.getLogger(__name__)
# Opt-in declaration tracing is scoped to this logger, never the OpenAI SDK.
# Do not turn on global SDK debug logging (credentials/source may be sensitive).
if os.environ.get("VLL_SCENE_DEBUG") == "1":
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(name)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    logger.propagate = False

_PROBABILITY_TERMS = (
    "probability", "probabilities", "equiprobable", "equally likely", "p(",
    "機率", "概率", "等可能", "公設", "公理",
)
_SAMPLE_SPACE_TERMS = (
    "sample space", "sample point", "outcome", "outcomes", "finite sample",
    "omega", "樣本空間", "樣本點", "基本結果", "可能結果", "有限樣本",
)
_EVENT_TERMS = (
    "event", "events", "subset", "subsets", "set of outcomes",
    "事件", "子集合", "事件集合",
)
_SET_OPERATION_TERMS = (
    "union", "intersection", "complement", "mutually exclusive", "disjoint",
    "de morgan", "demorgan", "inclusion-exclusion", "inclusion exclusion",
    "∪", "∩", "聯集", "并集", "交集", "補集", "补集", "餘集", "余集",
    "互斥", "德摩根", "戴摩根", "容斥",
)


def _candidate_text(analysis, source_context):
    """Collect bounded semantic evidence from analysis and extracted PDF text."""
    analysis_fragments, source_fragments = [], []

    def collect(value, fragments, limit):
        if sum(len(item) for item in fragments) >= limit:
            return
        if isinstance(value, str):
            fragments.append(value[:2_000])
        elif isinstance(value, dict):
            for item in value.values(): collect(item, fragments, limit)
        elif isinstance(value, list):
            for item in value[:32]: collect(item, fragments, limit)

    for key in ("quick_summary", "key_concepts", "relationships", "visual_evidence",
                "learning_path", "suggested_visualizations"):
        collect(analysis.get(key), analysis_fragments, MAX_CANDIDATE_CHARS // 2)
    source_context = source_context if isinstance(source_context, dict) else {}
    collect(source_context.get("source_text"), source_fragments, MAX_CANDIDATE_CHARS // 2)
    page_texts = source_context.get("page_texts")
    if isinstance(page_texts, dict):
        for page in sorted(page_texts, key=lambda value: str(value))[:8]:
            collect(page_texts.get(page), source_fragments, MAX_CANDIDATE_CHARS // 2)
    return unicodedata.normalize(
        "NFKC", " ".join(analysis_fragments + source_fragments)[:MAX_CANDIDATE_CHARS]
    ).lower()


def scene_candidate_evidence(analysis, source_context=None):
    """Return domain-specific suitability signals without making a model request."""
    analysis = analysis if isinstance(analysis, dict) else {}
    text = _candidate_text(analysis, source_context)
    compact_text = "".join(text.split())

    def contains(terms):
        return any(term in text or "".join(term.split()) in compact_text for term in terms)

    structured = analysis.get("learning_scene_candidate")
    structured_probability = bool(
        isinstance(structured, dict)
        and structured.get("suitable") is True
        and structured.get("domain") == DOMAIN
    )
    signals = {
        "structured": structured_probability,
        "probability": contains(_PROBABILITY_TERMS),
        "sample_space": contains(_SAMPLE_SPACE_TERMS),
        "events": contains(_EVENT_TERMS),
        "set_operations": contains(_SET_OPERATION_TERMS),
    }
    structural_count = sum(signals[key] for key in ("sample_space", "events", "set_operations"))
    signals["candidate"] = structured_probability or (
        signals["probability"] and structural_count >= 2
    ) or structural_count == 3
    return signals


def scene_candidate(analysis, source_context=None):
    """Conservative local routing; it makes no model request."""
    return scene_domain(analysis, source_context) is not None


def spatial_candidate(analysis, source_context=None):
    analysis = analysis if isinstance(analysis, dict) else {}
    structured = analysis.get("learning_scene_candidate", {})
    if isinstance(structured, dict) and structured.get("suitable") is True and structured.get("domain") == WORLD_DOMAIN:
        return True
    text = _candidate_text(analysis, source_context)
    compact = "".join(text.split())
    def has(terms):
        return any(term in text or "".join(term.split()) in compact for term in terms)
    temporal = has(("time-dependent", "time evolution", "cos(", "sin(", "trajectory", "waveform", "時間", "波形", "軌跡"))
    spatial = has(("vector", "phasor", "rotating field", "projectile", "position", "向量", "旋轉磁場", "拋體", "位置"))
    quantitative = has(("frequency", "amplitude", "velocity", "acceleration", "equation", "頻率", "振幅", "速度", "加速度", "方程", "公式"))
    return temporal and spatial and quantitative


def scene_domain(analysis, source_context=None):
    structured = analysis.get("learning_scene_candidate", {}) if isinstance(analysis, dict) else {}
    if isinstance(structured, dict) and structured.get("suitable") is True and structured.get("domain") == WORLD_DOMAIN:
        return WORLD_DOMAIN
    if scene_candidate_evidence(analysis, source_context)["candidate"]:
        return DOMAIN
    return WORLD_DOMAIN if spatial_candidate(analysis, source_context) else None


def build_scene_context(analysis, source_context, allowed_pages, domain=DOMAIN):
    source_context = source_context if isinstance(source_context, dict) else {}
    page_texts = source_context.get("page_texts", {})
    source_parts = []
    if source_context.get("kind") == "text" and isinstance(source_context.get("source_text"), str):
        source_parts.append(source_context["source_text"][:MAX_SOURCE_CHARS])
    elif isinstance(page_texts, dict):
        for page in allowed_pages:
            value = page_texts.get(page)
            if isinstance(value, str): source_parts.append(f"[Page {page}]\n{value}")
            if sum(map(len, source_parts)) >= MAX_SOURCE_CHARS: break
    concepts = []
    for item in analysis.get("key_concepts", [])[:16] if isinstance(analysis.get("key_concepts"), list) else []:
        if isinstance(item, dict):
            concepts.append({
                "concept": str(item.get("concept", ""))[:240],
                "explanation": str(item.get("explanation", ""))[:600],
                "source_pages": item.get("source_pages", [])[:8] if isinstance(item.get("source_pages"), list) else [],
            })
    relationships = []
    for item in analysis.get("relationships", [])[:24] if isinstance(analysis.get("relationships"), list) else []:
        if isinstance(item, dict):
            relationships.append({key: str(item.get(key, ""))[:240] for key in ("source", "relation", "target")})
    raw_path = analysis.get("learning_path", {})
    steps = []
    if isinstance(raw_path, dict) and isinstance(raw_path.get("steps"), list):
        for item in raw_path["steps"][:6]:
            if isinstance(item, dict):
                steps.append({"id": str(item.get("id", ""))[:48], "title": str(item.get("title", ""))[:240],
                              "learning_goal": str(item.get("learning_goal", ""))[:500]})
    context = {
        "domain": domain,
        "analysis_language": analysis.get("analysis_language", "zh-TW"),
        "allowed_source_pages": list(allowed_pages),
        "quick_summary": str(analysis.get("quick_summary", ""))[:3_000],
        "key_concepts": concepts,
        "relationships": relationships,
        "learning_steps": steps,
        "relevant_extracted_source_text": "\n\n".join(source_parts)[:MAX_SOURCE_CHARS],
    }
    if domain == WORLD_DOMAIN:
        # Existing model-supported equations help when PDF formula extraction is
        # imperfect. These remain bounded context, not executable/runtime data.
        lab = analysis.get("interactive_lab", {})
        demos = lab.get("demos", []) if isinstance(lab, dict) else []
        models = []
        for demo in demos[:2] if isinstance(demos, list) else []:
            if not isinstance(demo, dict): continue
            models.append({"title": str(demo.get("title", ""))[:160],
                           "formula": str(demo.get("formula_display", ""))[:400],
                           "curves": [{key: str(curve.get(key, ""))[:400] for key in ("label", "expression")}
                                      for curve in demo.get("series", [])[:3] if isinstance(curve, dict)] if isinstance(demo.get("series"), list) else [],
                           "source_pages": [p for p in demo.get("source_pages", []) if type(p) is int and p in allowed_pages][:8] if isinstance(demo.get("source_pages"), list) else []})
        context["existing_math_experiments"] = models
    encoded = json.dumps(context, ensure_ascii=False)
    if len(encoded) > MAX_CONTEXT_CHARS:
        overflow = len(encoded) - MAX_CONTEXT_CHARS
        context["relevant_extracted_source_text"] = context["relevant_extracted_source_text"][:max(0, len(context["relevant_extracted_source_text"]) - overflow - 64)]
    for key in ("relationships", "key_concepts", "learning_steps", "existing_math_experiments"):
        if key not in context: continue
        while context[key] and len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
            context[key].pop()
    if len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
        context["quick_summary"] = context["quick_summary"][:1_000]
    return context


def request_scene(client, model, context):
    language = context.get("analysis_language", "zh-TW")
    if language not in RESPONSE_LANGUAGES: language = "zh-TW"
    spatial = context.get("domain") == WORLD_DOMAIN
    response = client.responses.create(
        model=model,
        instructions=(WORLD_INSTRUCTIONS if spatial else SCENE_INSTRUCTIONS) + "\n" + output_language_instruction(language),
        input=json.dumps(context, ensure_ascii=False),
        text={"format": {"type": "json_schema", "name": "spatial_learning_world_v2" if spatial else "learning_scene_v1", "strict": True,
                         "schema": WORLD_SCHEMA if spatial else LEARNING_SCENE_SCHEMA}},
    )
    raw = json.loads(response.output_text)
    log_scene_declaration(raw)
    return raw


def log_scene_declaration(raw):
    """Opt-in bounded internal trace; omit labels, source text, pages and keys."""
    logger.debug("Learning Scene compiler result received object=%s", isinstance(raw, dict))
    if not logger.isEnabledFor(logging.DEBUG) or not isinstance(raw, dict): return
    def entries(key, fields, limit=32):
        values = raw.get(key)
        if not isinstance(values, list): return {"type": type(values).__name__}
        return [{field: item.get(field) for field in fields} for item in values[:limit] if isinstance(item, dict)]
    details = dict(domain=raw.get("domain"), version=raw.get("scene_version"), time=raw.get("time"), axes=raw.get("axes"),
                   primitives=entries("objects", ("id", "type", "semantic_id", "origin", "origin_quantity_ids"), 12),
                   parameters=entries("parameters", ("id", "min", "max", "default", "step"), 4),
                   expressions=entries("quantities", ("id", "expression"), 24),
                   bindings=entries("bindings", ("id", "type", "target_id", "quantity_ids")),
                   inverse_bindings=entries("inverse_bindings", ("id", "type", "object_id", "target_id", "rate_expression", "offset_expression", "scale"), 4),
                   invariants=entries("invariants", ("id", "type", "left_expression", "right_expression", "lower", "upper", "tolerance", "samples"), 12),
                   experiments=entries("experiments", ("id", "steps", "observation_targets"), 4),
                   views={"spatial": "objects", "vector": "objects", "waveform": entries("series", ("id", "semantic_id"), 6), "state": entries("metrics", ("id", "semantic_id"), 8)})
    # JSON escaping prevents injected log lines; cap diagnostic work/output.
    logger.debug("Learning Scene declaration %s", json.dumps(details, ensure_ascii=True, default=lambda _: "unsupported")[:24_000])


def ensure_scene_state(material_id, analysis, domain=DOMAIN):
    language = analysis.get("analysis_language", "zh-TW")
    if language not in RESPONSE_LANGUAGES: language = "zh-TW"
    return ensure_state(material_id, language, domain)


def render_scene_builder(analysis, material_id, source_context, allowed_pages, model, format_pages, workspace_mode=None):
    """Show the explicit compiler action and the cached local runtime."""
    domain = scene_domain(analysis, source_context)
    state = ensure_scene_state(material_id, analysis, domain or DOMAIN)
    if workspace_mode == "source":
        from source_atlas.compiler import render_atlas_builder
        from source_atlas.runtime import render_atlas
        bundle = render_atlas_builder(analysis, material_id, source_context, allowed_pages, model, state)
        if bundle: render_atlas(bundle)
        return bundle
    evidence = scene_candidate_evidence(analysis, source_context)
    candidate = domain is not None
    spatial = domain == WORLD_DOMAIN
    logger.debug("Learning Scene route candidate=%s evidence=%s cached=%s", candidate, evidence, bool(state.get("scene")))
    if not candidate and not state.get("scene"):
        if workspace_mode == "explore": return
        from source_atlas.compiler import render_atlas_builder
        from source_atlas.runtime import render_atlas
        bundle = render_atlas_builder(analysis, material_id, source_context, allowed_pages, model)
        if bundle: render_atlas(bundle)
        return
    if not state.get("scene"):
        logger.debug("Learning Scene CTA rendered material=%s", material_id)
        with st.container(border=True):
            st.markdown("### " + tr("Spatial Learning World" if spatial else "Learning Scene"))
            st.caption(tr("Explore one physical system through coordinated spatial, signal and vector views." if spatial else "This material can be explored as a coordinated probability workspace."))
            if st.button(tr("Build Spatial Learning World" if spatial else "Build Learning Scene"), key=f"scene-widget-build-{material_id}", type="primary", disabled=spatial and state.get("attempted", False)):
                returned = False
                try:
                    logger.debug("Learning Scene compiler requested material=%s", material_id)
                    api_key = st.secrets["OPENAI_API_KEY"]
                    context = build_scene_context(analysis, source_context, allowed_pages, domain)
                    with st.spinner(tr("Compiling the Learning Scene…")):
                        raw = request_scene(OpenAI(api_key=api_key), model, context)
                    returned = True
                    logger.debug("Learning Scene compiler returned object=%s", isinstance(raw, dict))
                    scene = normalize_scene(raw, allowed_pages)
                    if scene["domain"] != domain:
                        raise ValueError("Compiler returned the wrong scene domain.")
                    logger.debug("Learning Scene validator accepted scene=%s domain=%s", scene["scene_id"], domain)
                    logger.debug("Learning Scene normalization/validation report=%s", scene.get("validation_report"))
                    save_scene(state, scene)
                except (KeyError, st.errors.StreamlitSecretNotFoundError):
                    state["error"] = "key"
                except Exception as error:
                    if returned:
                        reason = str(error).replace("\n", " ")[:700]
                        state["validation_reason"] = reason  # Internal session diagnostics; never rendered.
                        logger.warning("Learning Scene validator rejected domain=%s reason=%s", domain, reason)
                    else:
                        logger.warning("Learning Scene compiler failed domain=%s error_type=%s", domain, type(error).__name__)
                    state["error"] = "invalid"
                    if spatial and (returned or isinstance(error, json.JSONDecodeError)): save_rejection(state)
            if state.get("error") == "key":
                st.info(tr("Learning Scene API access is not configured yet."))
            elif state.get("error") == "invalid":
                st.info(tr("The Learning Scene was incomplete or unsafe. Your analysis is still available."))
    from source_atlas.compiler import render_atlas_builder
    from source_atlas.runtime import render_atlas
    bundle = None if workspace_mode == "explore" else render_atlas_builder(analysis, material_id, source_context, allowed_pages, model, state)
    if bundle and not state.get("scene"):
        render_atlas(bundle)
    if state.get("scene"):
        try:
            logger.debug("Learning Scene runtime render scene=%s", state["scene"].get("scene_id"))
            if bundle:
                original, meaning = st.columns([1, 1.4], gap="medium")
                # Render world first so synchronous probability controls are
                # reflected in the source pane during this same result pass.
                with meaning:
                    st.markdown("#### "+tr("Interactive Meaning"))
                    render_scene(state["scene"], state, format_pages, source_context, allowed_pages)
                with original: render_atlas(bundle)
            else:
                render_scene(state["scene"], state, format_pages, source_context, allowed_pages)
        except Exception:
            logger.exception("Learning Scene runtime failed domain=%s", domain)
            st.info(tr("This Learning Scene could not be displayed. The rest of your learning material is still available."))


__all__ = [
    "build_scene_context", "ensure_scene_state", "render_scene_builder", "request_scene",
    "reset_scene_state", "scene_candidate", "scene_candidate_evidence",
]
