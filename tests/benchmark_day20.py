"""Offline, inspectable synthetic-corpus benchmark; no model accuracy claims."""
import io
import json
from pathlib import Path
import statistics
import sys
import time
import tracemalloc
from importlib.metadata import distribution, version

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pypdf import PdfReader
from PIL import Image, ImageDraw
from document_intelligence.pdfplumber_adapter import parse
from document_intelligence.model import refine_atlas
from source_atlas.model import normalize_atlas, semantic_catalog
from source_lens import get_page_render, new_source_state
from scene.world.validator import normalize_world
from atlas_fixtures import atlas_fixture, source_pdf
from day20_fixtures import corpus, text_pdf
from world_fixtures import three_phase_world


def measure(operation):
    elapsed = []
    tracemalloc.start()
    for _ in range(3):
        started = time.perf_counter()
        result = operation()
        elapsed.append((time.perf_counter()-started)*1000)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, round(statistics.median(elapsed), 3), peak


def run():
    output = ROOT/"docs"
    rows = []
    documents = corpus()
    started = time.perf_counter()
    parse(documents["lecture_phasor"], [1, 2], [1, 2])
    cold = round((time.perf_counter()-started)*1000, 3)
    for name, pdf in documents.items():
        pages = [2] if name == "messy_marks_page" else list(range(1, min(3, len(PdfReader(io.BytesIO(pdf)).pages))+1))
        def existing_text():
            reader = PdfReader(io.BytesIO(pdf))
            return [reader.pages[p-1].extract_text() for p in pages]
        before, before_ms, before_peak = measure(existing_text)
        after, after_ms, after_peak = measure(lambda: parse(pdf, pages, pages))
        rows.append(dict(case=name, source="synthetic, inspectable; not user PDF", pages=pages,
            before_native_geometry_regions=0, before_text_characters=sum(map(len, before)),
            after_native_text_regions=len(after["atlas"]["regions"]),
            parser_order="pdfplumber extraction order, not validated semantic reading order",
            before_pypdf_ms=before_ms, after_parser_ms=after_ms,
            before_python_alloc_peak_bytes=before_peak, after_python_alloc_peak_bytes=after_peak,
            failures="no OCR/figure/vector detection" if name in ("image_only", "messy_marks_page") else None))

    pdf = source_pdf()
    document = parse(pdf, [1, 2], [1, 2])
    scene = normalize_world(three_phase_world(), [1, 2])
    atlas = normalize_atlas(atlas_fixture(), [1, 2], semantic_catalog(scene))
    refined = refine_atlas(atlas, document)
    formula_before, formula_after = atlas["regions"][0], refined["regions"][0]
    area = lambda box: (box["x1"]-box["x0"])*(box["y1"]-box["y0"])
    quality = dict(metric="normalized formula-box area, NOT accuracy",
                   before=area(formula_before["bbox"]), after=area(formula_after["bbox"]),
                   semantic_confidence_unchanged=formula_before["confidence"] == formula_after["confidence"],
                   native_transcription="unique exact whole-line match; vector boxes unchanged")
    render = get_page_render(new_source_state("bench", pdf), "bench", 1, [1, 2])
    for name, box, color in (("before", formula_before["bbox"], "orange"), ("after", formula_after["bbox"], "green")):
        image = Image.open(io.BytesIO(render["png"])).convert("RGB")
        draw = ImageDraw.Draw(image)
        draw.rectangle((box["x0"]*image.width, box["y0"]*image.height,
                        box["x1"]*image.width, box["y1"]*image.height), outline=color, width=3)
        image.save(output/f"day20-native-{name}.png")

    dependencies = []
    for name in ("pdfplumber", "pdfminer.six", "pypdfium2", "cryptography", "cffi", "pycparser"):
        package = distribution(name)
        files = [Path(package.locate_file(f)) for f in package.files]
        dependencies.append(dict(name=name, version=version(name), installed_bytes=sum(f.stat().st_size for f in files if f.is_file()),
            license_paths=[str(f) for f in package.files if "license" in str(f).lower() or "notice" in str(f).lower()]))
    failures = []
    for name, pdf in (("dense_native_page", text_pdf(["A bounded native line"]*25)), ("malformed_pdf", b"not a PDF")):
        try:
            parse(pdf, [1], [1])
            failures.append(dict(case=name, rejected=False))
        except Exception as error:
            failures.append(dict(case=name, rejected=True, type=type(error).__name__))
    result = dict(date="2026-10-02", python=sys.version, cold_first_parse_ms=cold, corpus=rows,
        formula_box_comparison=quality, dependencies=dependencies, failure_cases=failures,
        limitations=["Docling/MinerU/Marker/PaddleOCR not run locally; comparison is documented capabilities, not measured ranking.",
                     "No real user slides/7-page probability/handwritten corpus present. Image-only fixture is not handwriting accuracy ground truth.",
                     "Timing excludes paid API latency. tracemalloc measures Python allocations, NOT native RSS/process peak memory.",
                     "Install bytes include package files; not container size or future platform wheel size.",
                     "No mathematical formula recognition, table or figure classifier is implemented by this adapter."])
    (output/"day20-benchmark.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("dependencies", "limitations")}, ensure_ascii=False, indent=2))


if __name__ == "__main__": run()
