"""Day28 review-only prepared material; never imported by production.

Revalidate the immutable Day27 human-approved SHM main/Atlas declarations.
No model client, expected answers, participant data, or generated code lives here.
The known mismatched planner explanation is deliberately outside this study lane.
"""
import copy
import hashlib
import io
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "docs/day28"
INPUTS = (
    ".day27-local/subsets/harmonic.pdf",
    ".day27-local/post_fix/responses/harmonic--main.json",
    ".day27-local/post_fix/responses/harmonic--atlas.json",
)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify_inputs():
    expected = read(PUBLIC / "prepared-inputs.json")["files_sha256"]
    if set(expected) != set(INPUTS):
        raise ValueError("Prepared input manifest differs")
    for name in INPUTS:
        if sha(ROOT / name) != expected[name]:
            raise ValueError("Prepared input changed: " + name)


def prepare():
    verify_inputs()
    from support import load_app_helpers
    from day27_postfix_replay import prepare as normalize_analysis
    from source_atlas.model import normalize_atlas
    from source_atlas.state import cache_key
    from source_lens import new_source_state

    helpers = load_app_helpers()
    pdf = (ROOT / INPUTS[0]).read_bytes()
    extracted = helpers["extract_pdf_text"](io.BytesIO(pdf))
    pages = extracted["analyzed_page_numbers"]
    material = helpers["build_analysis_id"]("pdf", pdf, "en")
    raw = read(ROOT / INPUTS[1])["raw"]
    analysis, path, lab, _, catalog = normalize_analysis(raw, pages, material)
    if lab["rejected"] or len(lab["demos"]) != 1:
        raise ValueError("Prepared SHM Lab no longer passes current validation")
    raw_atlas = read(ROOT / INPUTS[2])["raw"]
    atlas_pages = raw_atlas["processed_pages"]
    if not set(atlas_pages) <= set(pages):
        raise ValueError("Prepared Atlas page provenance differs")
    atlas = normalize_atlas(raw_atlas, atlas_pages, catalog, extracted["analyzed_page_texts"])
    key = cache_key(material, pdf, "en", atlas_pages, None, catalog)
    return dict(
        analysis=analysis, analysis_id=material, analysis_language="en",
        source_context=dict(kind="pdf", source_text="", page_texts=extracted["analyzed_page_texts"]),
        source_info=dict(total_count=extracted["total_pages"], found_count=len(pages), analyzed_count=len(pages)),
        allowed_source_pages=pages,
        learning_canvas=dict(material_id=material, selected_id=None, kind=None, component=None,
                             style_signature=None, last_event=-1, fallback=False, component_error=False,
                             source=new_source_state(material, pdf)),
        learning_workspace=dict(material_id=material, mode="learn", focus=None, representation="formal"),
        source_atlas_cache={key: atlas},
        source_atlas_state=dict(key=key, atlas=atlas, attempted=True, error=None, page=min(atlas_pages),
                               region_hint=None, seen_focus=None, last_token=None),
        day28_prepared=True,
    )


def install(session):
    # Prepare everything first. A rejected capture leaves the existing session intact.
    values = prepare()
    language = session.get("product_language", "zh-TW")
    session.clear()
    session.update(copy.deepcopy(values))
    session["product_language"] = language

