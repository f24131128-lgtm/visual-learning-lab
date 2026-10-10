"""Explicit vision grounding of at most three already-analyzed page rasters."""

import base64
import json
import logging

from openai import OpenAI
import streamlit as st

from i18n import output_language_instruction, tr
from source_lens import get_page_render
from .model import extracted_page_text, normalize_atlas, rank_pages, semantic_catalog
from .schema import ATLAS_SCHEMA, INSTRUCTIONS, MAX_PAGES
from .state import cache_key, current_focus, ensure_state, optional_scene, save_result

logger = logging.getLogger(__name__)
MAX_INPUT_BYTES = 8 * 1024 * 1024


def suitable(analysis, source_context, source_state, allowed, catalog):
    return bool(source_context.get("kind") == "pdf" and source_state and source_state.get("pdf_bytes") and allowed
                and (analysis.get("visual_evidence") or any(item["pages"] for item in catalog.values())))


def request_atlas(client, model, analysis, source_context, source_state, material_id, pages, allowed, catalog, document=None):
    if not 1 <= len(pages) <= MAX_PAGES or len(set(pages)) != len(pages) or any(type(p) is not int or p not in allowed for p in pages):
        raise ValueError("selected pages: invalid")
    rendered = [get_page_render(source_state, material_id, p, allowed) for p in pages]
    if sum(len(r["png"]) for r in rendered) > MAX_INPUT_BYTES: raise ValueError("page images: payload bound")
    entities = {i: {k: v for k, v in item.items() if k != "representations"} for i, item in catalog.items()}
    context = dict(selected_pages=pages, semantic_entities=entities,
        quick_summary=str(analysis.get("quick_summary", ""))[:2500],
        visual_evidence=[{k: str(item.get(k, ""))[:500] for k in ("page", "type", "description", "learning_value")}
                         for item in analysis.get("visual_evidence", [])[:24] if isinstance(item, dict) and item.get("page") in pages],
        extracted_text={p: extracted_page_text(source_context.get("page_texts"), p)[:2500] for p in pages})
    if document is not None:
        from document_intelligence.model import compiler_context
        remaining = max(0, 24000-len(json.dumps(context, ensure_ascii=False))-100)
        context["native_text_regions"] = compiler_context(document, min(6000, remaining))
    encoded = json.dumps(context, ensure_ascii=False)
    if len(encoded) > 24000: raise ValueError("semantic context: payload bound")
    content = [{"type": "input_text", "text": encoded}]
    for page, render in zip(pages, rendered):
        content.extend([{"type": "input_text", "text": f"Original PDF page {page}, complete raster {render['width']}x{render['height']}."},
                        {"type": "input_image", "image_url": "data:image/png;base64,"+base64.b64encode(render["png"]).decode(), "detail": "high"}])
    response = client.responses.create(model=model,
        instructions=INSTRUCTIONS+"\n"+output_language_instruction(analysis.get("analysis_language", "zh-TW")),
        input=[{"role": "user", "content": content}],
        text={"format": {"type": "json_schema", "name": "source_atlas_v1", "strict": True, "schema": ATLAS_SCHEMA}})
    if not isinstance(response.output_text, str) or len(response.output_text) > 150000: raise ValueError("atlas response: size bound")
    return json.loads(response.output_text)


def source_for(material_id):
    canvas = st.session_state.get("learning_canvas")
    return canvas.get("source") if isinstance(canvas, dict) and canvas.get("material_id") == material_id else None


def _render_atlas_builder(analysis, material_id, source_context, allowed, model, wrapper=None):
    """Always explicit; no input image/API work on ordinary reruns."""
    scene = optional_scene(wrapper)
    catalog = semantic_catalog(scene, analysis)
    for item in catalog.values(): item["pages"] = [p for p in item["pages"] if p in allowed]
    source = source_for(material_id)
    if not suitable(analysis, source_context, source, allowed, catalog): return None
    # Widget cleanup while Explore is open must not replace the selected pages
    # with a newly focus-ranked default and discard an already valid atlas.
    ranked = rank_pages(analysis, catalog, allowed)
    existing = st.session_state.get("source_atlas_state", {})
    defaults = ranked[:MAX_PAGES]
    prior_key = existing.get("key")
    if (isinstance(prior_key, tuple) and len(prior_key) == 6
            and prior_key == cache_key(material_id, source["pdf_bytes"], analysis["analysis_language"], prior_key[4], scene, catalog)
            and all(p in allowed for p in prior_key[4])):
        defaults = list(prior_key[4])
    ready = bool(existing.get("atlas") and existing.get("key", [None])[0] == material_id)
    with st.expander(tr("Source preparation"), expanded=not ready):
        st.markdown("### "+tr("Source Atlas"))
        st.caption(tr("Connect original formulas and diagrams to the same learning-world focus."))
        page_labels = {p: tr("Page {page}", page=p) for p in ranked}
        pages = st.multiselect(tr("Pages to ground (up to 3)"), ranked, default=defaults,
            format_func=lambda p, labels=page_labels: labels[p], max_selections=MAX_PAGES, key="atlas-widget-pages-"+material_id)
        if not pages: return None
        key = cache_key(material_id, source["pdf_bytes"], analysis["analysis_language"], pages, scene, catalog)
        state = ensure_state(key)
        from document_intelligence.ui import render_controls
        native_preview = render_controls(state, source, pages, allowed)
        if st.button(tr("Build Source Atlas"), type="secondary", key="atlas-widget-build-"+material_id, disabled=state["attempted"]) and not state["attempted"]:
            returned = False
            try:
                with st.spinner(tr("Grounding selected source pages…")):
                    raw = request_atlas(OpenAI(api_key=st.secrets["OPENAI_API_KEY"], max_retries=0), model, analysis, source_context, source, material_id, pages, allowed, catalog, state.get("document_model"))
                    returned = True
                    atlas = normalize_atlas(raw, pages, catalog, source_context.get("page_texts"))
                    if state.get("document_model") is not None:
                        from document_intelligence.model import refine_atlas
                        atlas = refine_atlas(atlas, state["document_model"])
                logger.info("Source Atlas accepted pages=%s region_count=%s dropped_count=%s", sorted(pages), len(atlas["regions"]), len(atlas["diagnostics"]))
                if atlas["diagnostics"]: logger.warning("Source Atlas dropped fields=%s", atlas["diagnostics"])
                save_result(state, atlas)
                st.rerun()
            except (KeyError, st.errors.StreamlitSecretNotFoundError): state["error"] = "key"
            except Exception as error:
                # Never log PDF bytes, full source, response body or credentials.
                state["error"] = "invalid" if returned else "api"
                if returned or isinstance(error, json.JSONDecodeError):
                    state["diagnostic"] = str(error).replace("\n", " ")[:500]
                    logger.warning("Source Atlas rejected reason=%s", state["diagnostic"])
                    save_result(state, None)
                    st.rerun()
                else: logger.warning("Source Atlas request failed type=%s", type(error).__name__)
        if state["atlas"] is not None:
            st.caption(tr("Grounded pages: {pages}", pages=" · ".join(str(p) for p in state["atlas"]["processed_pages"])))
        elif state["attempted"] or state.get("error"):
            st.info(tr("Source grounding is unavailable. Existing analysis, sources and learning worlds are unchanged."))
    active = state if state["atlas"] is not None else native_preview
    return dict(state=active, catalog=catalog, source=source, material_id=material_id,
                source_context=source_context, allowed=allowed, wrapper=wrapper,
                native_only=active is native_preview) if active is not None else None


def render_atlas_builder(*args, **kwargs):
    try:
        return _render_atlas_builder(*args, **kwargs)
    except Exception as error:
        logger.warning("Optional Source Atlas unavailable type=%s", type(error).__name__)
        st.info(tr("Source grounding is unavailable. Existing analysis, sources and learning worlds are unchanged."))
        return None
