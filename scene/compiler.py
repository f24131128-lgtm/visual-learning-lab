"""Explicit Learning Scene compiler request and application integration."""

import json
import unicodedata

from openai import OpenAI
import streamlit as st

from i18n import RESPONSE_LANGUAGES, output_language_instruction, tr
from .runtime import render_scene
from .schema import DOMAIN, LEARNING_SCENE_SCHEMA, SCENE_INSTRUCTIONS
from .state import ensure_state, reset_scene_state, save_scene
from .validator import normalize_scene

MAX_CONTEXT_CHARS = 18_000
MAX_SOURCE_CHARS = 10_000
MAX_CANDIDATE_CHARS = 12_000

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
    fragments = []

    def collect(value):
        if sum(len(item) for item in fragments) >= MAX_CANDIDATE_CHARS:
            return
        if isinstance(value, str):
            fragments.append(value[:2_000])
        elif isinstance(value, dict):
            for item in value.values(): collect(item)
        elif isinstance(value, list):
            for item in value[:32]: collect(item)

    for key in ("quick_summary", "key_concepts", "relationships", "visual_evidence",
                "learning_path", "suggested_visualizations"):
        collect(analysis.get(key))
    source_context = source_context if isinstance(source_context, dict) else {}
    collect(source_context.get("source_text"))
    page_texts = source_context.get("page_texts")
    if isinstance(page_texts, dict):
        for page in sorted(page_texts, key=lambda value: str(value))[:8]:
            collect(page_texts.get(page))
    return unicodedata.normalize("NFKC", " ".join(fragments)[:MAX_CANDIDATE_CHARS]).lower()


def scene_candidate_evidence(analysis, source_context=None):
    """Return domain-specific suitability signals without making a model request."""
    text = _candidate_text(analysis if isinstance(analysis, dict) else {}, source_context)
    signals = {
        "probability": any(term in text for term in _PROBABILITY_TERMS),
        "sample_space": any(term in text for term in _SAMPLE_SPACE_TERMS),
        "events": any(term in text for term in _EVENT_TERMS),
        "set_operations": any(term in text for term in _SET_OPERATION_TERMS),
    }
    structural_count = sum(signals[key] for key in ("sample_space", "events", "set_operations"))
    signals["candidate"] = (
        signals["probability"] and structural_count >= 2
    ) or structural_count == 3
    return signals


def scene_candidate(analysis, source_context=None):
    """Conservative local routing; it makes no model request."""
    return scene_candidate_evidence(analysis, source_context)["candidate"]


def build_scene_context(analysis, source_context, allowed_pages):
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
        "domain": DOMAIN,
        "analysis_language": analysis.get("analysis_language", "zh-TW"),
        "allowed_source_pages": list(allowed_pages),
        "quick_summary": str(analysis.get("quick_summary", ""))[:3_000],
        "key_concepts": concepts,
        "relationships": relationships,
        "learning_steps": steps,
        "relevant_extracted_source_text": "\n\n".join(source_parts)[:MAX_SOURCE_CHARS],
    }
    encoded = json.dumps(context, ensure_ascii=False)
    if len(encoded) > MAX_CONTEXT_CHARS:
        overflow = len(encoded) - MAX_CONTEXT_CHARS
        context["relevant_extracted_source_text"] = context["relevant_extracted_source_text"][:max(0, len(context["relevant_extracted_source_text"]) - overflow - 64)]
    for key in ("relationships", "key_concepts", "learning_steps"):
        while context[key] and len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
            context[key].pop()
    if len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
        context["quick_summary"] = context["quick_summary"][:1_000]
    return context


def request_scene(client, model, context):
    language = context.get("analysis_language", "zh-TW")
    if language not in RESPONSE_LANGUAGES: language = "zh-TW"
    response = client.responses.create(
        model=model,
        instructions=SCENE_INSTRUCTIONS + "\n" + output_language_instruction(language),
        input=json.dumps(context, ensure_ascii=False),
        text={"format": {"type": "json_schema", "name": "learning_scene_v1", "strict": True,
                         "schema": LEARNING_SCENE_SCHEMA}},
    )
    return json.loads(response.output_text)


def ensure_scene_state(material_id, analysis):
    language = analysis.get("analysis_language", "zh-TW")
    if language not in RESPONSE_LANGUAGES: language = "zh-TW"
    return ensure_state(material_id, language)


def render_scene_builder(analysis, material_id, source_context, allowed_pages, model, format_pages):
    """Show the explicit compiler action and the cached local runtime."""
    state = ensure_scene_state(material_id, analysis)
    candidate = scene_candidate(analysis, source_context)
    if not candidate and not state.get("scene"):
        return
    if not state.get("scene"):
        with st.container(border=True):
            st.markdown("### " + tr("Learning Scene"))
            st.caption(tr("This material can be explored as a coordinated probability workspace."))
            if st.button(tr("Build Learning Scene"), key=f"scene-widget-build-{material_id}", type="primary"):
                try:
                    api_key = st.secrets["OPENAI_API_KEY"]
                    context = build_scene_context(analysis, source_context, allowed_pages)
                    with st.spinner(tr("Compiling the Learning Scene…")):
                        raw = request_scene(OpenAI(api_key=api_key), model, context)
                    scene = normalize_scene(raw, allowed_pages)
                    save_scene(state, scene)
                except (KeyError, st.errors.StreamlitSecretNotFoundError):
                    state["error"] = "key"
                except Exception:
                    state["error"] = "invalid"
            if state.get("error") == "key":
                st.info(tr("Learning Scene API access is not configured yet."))
            elif state.get("error") == "invalid":
                st.info(tr("The Learning Scene was incomplete or unsafe. Your analysis is still available."))
    if state.get("scene"):
        try:
            render_scene(state["scene"], state, format_pages)
        except Exception:
            st.info(tr("This Learning Scene could not be displayed. The rest of your learning material is still available."))


__all__ = [
    "build_scene_context", "ensure_scene_state", "render_scene_builder", "request_scene",
    "reset_scene_state", "scene_candidate", "scene_candidate_evidence",
]
