"""Hash-verified, portable previously generated competition material.

No model client, test fixture imports, hidden local corpus or global user cache.
The demonstration is noncommercial and retains the source's CC BY-NC-SA notice.
"""
import copy
import hashlib
import io
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parent / "prepared" / "harmonic"


def prepare(helpers):
    from source_lens import new_source_state
    from source_atlas.model import normalize_atlas, semantic_catalog
    from source_atlas.state import cache_key
    from interactive_lab import clean_interactive_lab
    manifest = json.loads((ASSETS / "manifest.json").read_text(encoding="utf-8"))
    expected_names = {"source.pdf", "analysis.json", "atlas.json"}
    if set(manifest["sha256"]) != expected_names:
        raise ValueError("Prepared manifest")
    files = {}
    for name in sorted(expected_names):
        data = (ASSETS/name).read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest["sha256"][name]:
            raise ValueError("Prepared material integrity")
        files[name] = data
    pdf = files["source.pdf"]
    extracted = helpers["extract_pdf_text"](io.BytesIO(pdf), public=False)
    pages = extracted["analyzed_page_numbers"]
    material = helpers["build_analysis_id"]("pdf", pdf, "en")
    analysis = json.loads(files["analysis.json"])
    analysis["analysis_language"] = "en"
    decision = helpers["clean_primary_visualization"](analysis.get("primary_visualization"))
    structures = {key: helpers["clean_"+key](analysis.get(key), pages)
                  for key in ("concept_map", "visual_flow", "comparison")}
    analysis["_formal_representations"] = structures
    visual = structures.get({"flow":"visual_flow", "concept_map":"concept_map", "comparison":"comparison"}.get(decision["type"]))
    path = helpers["clean_learning_path"](analysis.get("learning_path"), pages, decision["type"], visual)
    catalog = semantic_catalog(None, analysis)
    lab = clean_interactive_lab(analysis.get("interactive_lab"), pages, path,
                               helpers["valid_source_pages"], catalog=catalog, material=material)
    if lab["rejected"] or len(lab["demos"]) != 1:
        raise ValueError("Prepared experiment validation")
    raw_atlas = json.loads(files["atlas.json"])
    selected = raw_atlas["processed_pages"]
    if not set(selected) <= set(pages):
        raise ValueError("Prepared pages")
    atlas = normalize_atlas(raw_atlas, selected, catalog, extracted["analyzed_page_texts"])
    key = cache_key(material, pdf, "en", selected, None, catalog)
    return dict(analysis=analysis, analysis_id=material, analysis_language="en",
        source_context=dict(kind="pdf", source_text="", page_texts=extracted["analyzed_page_texts"]),
        source_info=dict(total_count=extracted["total_pages"], found_count=len(pages), analyzed_count=len(pages)),
        allowed_source_pages=pages,
        learning_canvas=dict(material_id=material, selected_id=None, kind=None, component=None,
                             style_signature=None, last_event=-1, fallback=False, component_error=False,
                             source=new_source_state(material, pdf)),
        learning_workspace=dict(material_id=material, mode="learn", focus=None, representation="formal"),
        source_atlas_cache={key:atlas},
        source_atlas_state=dict(key=key, atlas=atlas, attempted=True, error=None, page=min(selected),
                               region_hint=None, seen_focus=None, last_token=None), prepared_demo=True)


def install_prepared(session, helpers):
    import streamlit as st
    from i18n import tr
    try:
        values = prepare(helpers)  # Validate fully before replacing any learning state.
    except Exception:
        st.error(tr("The prepared material could not be loaded. Your current work is preserved."))
        return
    language = session.get("product_language", "zh-TW")
    session.clear()
    session.update(copy.deepcopy(values))
    session["product_language"] = language
