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
EXAMPLES = ("harmonic", "projectile")


def prepare(helpers, example="harmonic"):
    from source_lens import new_source_state
    from source_atlas.model import normalize_atlas, semantic_catalog
    from source_atlas.state import cache_key
    from interactive_lab import clean_interactive_lab
    if example not in EXAMPLES:
        raise ValueError("Unknown prepared example")
    assets = ASSETS if example == "harmonic" else ASSETS.parent / example
    manifest = json.loads((assets / "manifest.json").read_text(encoding="utf-8"))
    expected_names = {"source.pdf", "analysis.json", "atlas.json"}
    if example == "projectile": expected_names |= {"scene.json", "archived_scene.json"}
    if set(manifest["sha256"]) != expected_names:
        raise ValueError("Prepared manifest")
    files = {}
    for name in sorted(expected_names):
        path = assets/name
        # This is a fixed, reviewed asset path, never a visitor upload bypass.
        limit = 4*1024*1024 if name == "source.pdf" else 256*1024
        if not 0 < path.stat().st_size <= limit:
            raise ValueError("Prepared asset bound")
        data = path.read_bytes()
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
    scene = None
    if example == "projectile":
        from scene.validator import normalize_scene
        scene = normalize_scene(json.loads(files["scene.json"]), pages)
        if material != manifest["historical_material"]:
            raise ValueError("Prepared historical material identity")
    visual = structures.get({"flow":"visual_flow", "concept_map":"concept_map", "comparison":"comparison"}.get(decision["type"]))
    path = helpers["clean_learning_path"](analysis.get("learning_path"), pages, decision["type"], visual)
    catalog = semantic_catalog(scene, analysis)
    lab = clean_interactive_lab(analysis.get("interactive_lab"), pages, path,
                               helpers["valid_source_pages"], catalog=catalog, material=material)
    if example == "harmonic" and (lab["rejected"] or len(lab["demos"]) != 1):
        raise ValueError("Prepared experiment validation")
    raw_atlas = json.loads(files["atlas.json"])
    selected = raw_atlas["processed_pages"]
    if not set(selected) <= set(pages):
        raise ValueError("Prepared pages")
    atlas = normalize_atlas(raw_atlas, selected, catalog, extracted["analyzed_page_texts"])
    key = cache_key(material, pdf, "en", selected, scene, catalog)
    values = dict(analysis=analysis, analysis_id=material, analysis_language="en",
        source_context=dict(kind="pdf", source_text="", page_texts=extracted["analyzed_page_texts"]),
        source_info=dict(total_count=extracted["total_pages"], found_count=len(pages), analyzed_count=len(pages)),
        allowed_source_pages=pages,
        learning_canvas=dict(material_id=material, selected_id=None, kind=None, component=None,
                             style_signature=None, last_event=-1, fallback=False, component_error=False,
                             source=new_source_state(material, pdf)),
        learning_workspace=dict(material_id=material, mode="source" if scene else "explore", focus=None, representation="formal"),
        source_atlas_cache={key:atlas},
        source_atlas_state=dict(key=key, atlas=atlas, attempted=True, error=None, page=manifest.get("initial_page", min(selected)),
                               region_hint=manifest.get("initial_region"), seen_focus=None, last_token=None),
        prepared_demo=example)
    if scene:
        from scene.state import cache_key as scene_key
        from scene.world.state import new_state
        identity = scene_key(material, "en", scene["domain"])
        world = new_state(scene)
        world["focus"] = None  # Source ambiguity remains an explicit learner choice.
        values.update(learning_scene_cache={identity:scene}, learning_scene_state=dict(
            cache_key=identity, material_id=material, language="en", scene=scene, world=world,
            open=True, error=None, attempted=True))
    return values


def install_prepared(session, helpers, example="harmonic"):
    import streamlit as st
    from i18n import tr
    try:
        values = prepare(helpers, example)  # Validate fully before replacing any learning state.
    except Exception:
        st.error(tr("The prepared material could not be loaded. Your current work is preserved."))
        return
    language = session.get("product_language", "zh-TW")
    session.clear()
    session.update(copy.deepcopy(values))
    session["product_language"] = language


def attribution(example):
    if example == "projectile":
        return "MIT OpenCourseWare / Peter Dourmashkin · Chapter 5: Two Dimensional Kinematics · CC BY-NC-SA 4.0 · original PDF unchanged."
    return "MIT OpenCourseWare / Peter Dourmashkin · Chapter 23: Simple Harmonic Motion · CC BY-NC-SA 4.0 · original pages 3–10, unchanged."
