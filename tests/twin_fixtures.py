"""Original three-page engineering PDFs with native formulas and diagrams.

Synthetic sources, never a real-world fidelity corpus or production import.
Reuse the Day24 engines/declarations unchanged.
"""
import math
import pymupdf

from manipulation_fixtures import analysis, systems
from atlas_fixtures import region, page_texts
from source_atlas.model import normalize_atlas, semantic_catalog
from source_atlas.state import cache_key

FORMULAS = {"phase": "theta = time + phase", "projectile": "launch_y = speed*sin(angle)",
            "math": "y = gain*x + offset"}
BASELINES = {"phase": "Source baseline: phase = 0 rad.",
             "projectile": "Source baseline: speed = 20 m/s; angle = 45 degrees; g = 9.8.",
             "math": "Source baseline: gain = 1; offset = 0."}
RANGES = {"phase": "Explore phase from -pi to pi. signal = sin(theta).",
          "projectile": "Explore speed 5 to 100; angle 5 to 85 degrees; gravity 1 to 20.",
          "math": "Explore gain -3 to 3, offset -4 to 4, and x -2 to 2."}


def fixture(kind):
    scene = systems()[0 if kind == "phase" else 1] if kind != "math" else None
    value = analysis(kind)
    sid = {"phase": "angle", "projectile": "launch_y", "math": "formal_relation"}[kind]
    derived = {"phase": "wave", "projectile": "energy", "math": "source_baseline"}[kind]
    with pymupdf.open() as pdf:
        for n, (width, height) in enumerate([(620, 790), (790, 620), (620, 790)]):
            page = pdf.new_page(width=width, height=height)
            lines = (["Original engineering lesson - " + kind, FORMULAS[kind], BASELINES[kind], RANGES[kind],
                      "Source values remain unchanged during learner exploration."] if n == 0 else
                     ["Geometric representation - independently drawn", FORMULAS[kind], "The object and formula share one semantic identity."] if n == 1 else
                     ["Derived quantity - page-level source support", "This result follows from the model; it has no independent drag handle.",
                      "signal = sin(theta)" if kind == "phase" else "energy = (vx*vx + vy*vy)/2" if kind == "projectile" else "An initial value is evidence, not an adjustable semantic relation."])
            for i, line in enumerate(lines): page.insert_text((42, 65+i*34), line, fontsize=13)
            if n == 1:
                origin = pymupdf.Point(180, 340)
                page.draw_line((80, 340), (520, 340), color=(.2,.3,.4))
                page.draw_line((180, 150), (180, 490), color=(.2,.3,.4))
                if kind == "phase":
                    page.draw_circle(origin, 130, color=(.3,.2,.7)); endpoint = pymupdf.Point(310, 340)
                elif kind == "projectile": endpoint = pymupdf.Point(310, 210)
                else:
                    page.draw_line((80, 440), (330, 190), color=(.3,.2,.7)); endpoint = origin
                if kind != "math": page.draw_line(origin, endpoint, color=(.3,.2,.7), width=3)
                page.draw_circle(endpoint, 7, color=(.3,.2,.7), fill=(.3,.2,.7))
        binary = pdf.tobytes(no_new_id=True)
    texts = page_texts(binary)
    catalog = semantic_catalog(scene, value)
    raw = dict(atlas_version="1.0", processed_pages=[1,2,3], regions=[
        region("source_formula", 1, (.055,.09,.94,.16), FORMULAS[kind], [sid], "formula", "formulas", excerpt=FORMULAS[kind]),
        region("source_object", 2, (.09,.23,.68,.81), "Source diagram", [sid], "diagram", "structure"),
        region("derived_source", 3, None, "Derived source quantity", [derived], "definition", "structure", confidence="low"),
    ])
    atlas = normalize_atlas(raw, [1,2,3], catalog, texts)
    document = None
    try:
        from document_intelligence.pdfplumber_adapter import parse
        from document_intelligence.model import refine_atlas
        document = parse(binary, [1,2,3], [1,2,3])
        atlas = refine_atlas(atlas, document)
    except ImportError: pass
    material = "day25-" + kind
    key = cache_key(material, binary, "zh-TW", [1,2,3], scene, catalog)
    state = dict(key=key, atlas=atlas, attempted=True, error=None, page=1,
                 region_hint=None, seen_focus=None, last_token=None, document_model=document)
    return dict(scene=scene, analysis=value, pdf=binary, texts=texts, catalog=catalog,
                atlas_state=state, material=material, semantic=sid, derived=derived)
