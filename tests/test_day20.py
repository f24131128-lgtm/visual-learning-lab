"""Day 20 parser/normalization security and real normal-PDF product path."""
import copy
import io
import json
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import learning_canvas as canvas
from document_intelligence import model, pdfplumber_adapter as adapter, service
from document_intelligence import ui
from source_atlas import compiler, runtime
from source_atlas.model import normalize_atlas, semantic_catalog
from scene.world.validator import normalize_world
try:
    from atlas_fixtures import atlas_fixture, source_pdf
    from day20_fixtures import corpus, cropped_rotated, text_pdf
    import test_day19 as day19
    from world_fixtures import three_phase_world
except ModuleNotFoundError:
    from .atlas_fixtures import atlas_fixture, source_pdf
    from .day20_fixtures import corpus, cropped_rotated, text_pdf
    from . import test_day19 as day19
    from .world_fixtures import three_phase_world


@unittest.skipUnless(adapter.available(), "Install requirements-documents.txt for parser acceptance")
class DocumentTests(unittest.TestCase):
    def setUp(self):
        self.pdf = source_pdf()
        self.document = adapter.parse(self.pdf, [1, 2], [1, 2])
        self.raw = copy.deepcopy(self.document)
        self.raw["atlas"].pop("diagnostics")
        for region in self.raw["atlas"]["regions"]:
            region.pop("excerpt_verified")

    def check(self, raw):
        return model.normalize_document(raw, self.pdf, [1, 2], [1, 2])

    def test_actual_parser_native_regions_and_locators(self):
        self.assertEqual(len(self.document["atlas"]["regions"]), 3)
        self.assertEqual(self.document["parser_version"], "0.11.10")
        for r in self.document["atlas"]["regions"]:
            self.assertFalse(r["semantic_ids"])
            self.assertEqual(self.document["locators"][r["region_id"]]["method"], "native_text_geometry")
        self.assertEqual(self.document, adapter.parse(self.pdf, [2, 1], [1, 2]))

    def test_material_identity_and_page_whitelist(self):
        for field, value in (("pdf_sha256", "foreign"), ("version", "bad")):
            bad = copy.deepcopy(self.raw); bad[field] = value
            with self.assertRaises(ValueError): self.check(bad)
        for pages in ([999], [True], [1, 1], [], [1, 2, 3, 4]):
            with self.assertRaises(ValueError): adapter.parse(self.pdf, pages, [1, 2])
        with self.assertRaises(ValueError): adapter.parse(self.pdf, [3], [3])

    def test_malformed_envelope_and_parser_metadata(self):
        for field, value in (("parser", "<script>"), ("parser_version", "x"*65), ("locators", None)):
            bad = copy.deepcopy(self.raw); bad[field] = value
            with self.assertRaises(ValueError): self.check(bad)
        bad = copy.deepcopy(self.raw); bad["code"] = "evil"
        with self.assertRaises(ValueError): self.check(bad)

    def test_boxes_finite_and_nontrivial(self):
        for value in (math.nan, math.inf, -1, 100):
            bad = copy.deepcopy(self.raw); bad["atlas"]["regions"][0]["bbox"]["x0"] = value
            with self.assertRaises(ValueError): self.check(bad)
        bad = copy.deepcopy(self.raw); bad["atlas"]["regions"][0]["bbox"]["x1"] = .080001
        with self.assertRaises(ValueError): self.check(bad)

    def test_types_semantic_links_and_text_bounds_rejected(self):
        for field, value in (("type", "script"), ("type", "formula"), ("semantic_ids", ["ia"]),
                             ("source_text_excerpt", "x"*601), ("label", "<svg onload=evil>")):
            bad = copy.deepcopy(self.raw); bad["atlas"]["regions"][0][field] = value
            with self.assertRaises(ValueError): self.check(bad)

    def test_duplicate_regions_and_locator_collisions(self):
        bad = copy.deepcopy(self.raw); bad["atlas"]["regions"][1]["region_id"] = bad["atlas"]["regions"][0]["region_id"]
        with self.assertRaises(ValueError): self.check(bad)
        for path in ("page/999/text_line/0", "javascript:evil", "page/1/text_line/1"):
            bad = copy.deepcopy(self.raw); bad["locators"]["native_p1_line0"]["path"] = path
            with self.assertRaises(ValueError): self.check(bad)

    def test_total_region_and_pdf_bounds(self):
        bad = copy.deepcopy(self.raw); bad["atlas"]["regions"] *= 65
        with self.assertRaises(ValueError): self.check(bad)
        with self.assertRaises(ValueError): model.pdf_identity(b"x"*(model.MAX_PDF_BYTES+1))
        with self.assertRaises(ValueError): adapter.parse(text_pdf(["a b c"]*25), [1], [1])

    def test_native_geometry_not_transcription_or_semantic_verification(self):
        self.assertFalse(any(r["excerpt_verified"] for r in self.document["atlas"]["regions"]))
        self.assertTrue(all(r["confidence"] == "medium" for r in self.document["atlas"]["regions"]))

    def test_unique_exact_formula_refinement_preserves_meaning(self):
        scene = normalize_world(three_phase_world(), [1, 2])
        atlas = normalize_atlas(atlas_fixture(), [1, 2], semantic_catalog(scene))
        got = model.refine_atlas(atlas, self.document)
        self.assertNotEqual(got["regions"][0]["bbox"], atlas["regions"][0]["bbox"])
        self.assertEqual(got["regions"][0]["bbox"], self.document["atlas"]["regions"][0]["bbox"])
        for left, right in zip(atlas["regions"], got["regions"]):
            for field in ("semantic_ids", "confidence", "type", "source_text_excerpt", "region_id"):
                self.assertEqual(left[field], right[field])
        self.assertEqual(got["regions"][2], atlas["regions"][2])  # Never shrink a vector to its label.

    def test_ambiguous_partial_and_low_confidence_never_refined(self):
        scene = normalize_world(three_phase_world(), [1, 2])
        atlas = normalize_atlas(atlas_fixture(), [1, 2], semantic_catalog(scene))
        for change in ("duplicate", "partial", "low"):
            doc = copy.deepcopy(self.document); raw = copy.deepcopy(atlas)
            if change == "duplicate": doc["atlas"]["regions"].append(copy.deepcopy(doc["atlas"]["regions"][0]))
            elif change == "partial": raw["regions"][0]["source_text_excerpt"] = "A cos(2 pi f t)"
            else: raw["regions"][0].update(confidence="low", bbox=None)
            self.assertEqual(model.refine_atlas(raw, doc)["regions"][0], raw["regions"][0])

    def test_compiler_context_strict_budget(self):
        for budget in (0, 100, 6000):
            rows = model.compiler_context(self.document, budget)
            self.assertLessEqual(len(json.dumps(rows, ensure_ascii=False)), max(2, budget))

    def test_scanned_pdf_not_misrepresented_as_ocr(self):
        scan = corpus()["image_only"]
        self.assertFalse(adapter.parse(scan, [1], [1])["atlas"]["regions"])

    def test_cross_domain_formula_and_probability_same_parser(self):
        for name in ("projectile", "probability", "formula_heavy"):
            pdf = corpus()[name]
            self.assertTrue(adapter.parse(pdf, [1], [1])["atlas"]["regions"])

    def test_crop_rotation_matches_actual_raster_ink(self):
        import pymupdf
        import numpy as np
        for rotation in (0, 90, 180, 270):
            pdf = cropped_rotated(rotation)
            parsed = adapter.parse(pdf, [1], [1, 2])
            with pymupdf.open(stream=pdf, filetype="pdf") as doc:
                pixmap = doc[0].get_pixmap(alpha=False)
                image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(pixmap.height, pixmap.width, 3)
                for region in parsed["atlas"]["regions"]:
                    box = region["bbox"]
                    x0, x1 = int(box["x0"]*pixmap.width), int(box["x1"]*pixmap.width)
                    y0, y1 = int(box["y0"]*pixmap.height), int(box["y1"]*pixmap.height)
                    dark = np.min(image[y0:y1, x0:x1], axis=2) < 150
                    # Rotated extraction may yield a single glyph/word, not
                    # a full line. Test actual ink occupancy, not line length.
                    self.assertGreater(dark.sum(), 3, (rotation, region["label"], box))
                    self.assertGreater(dark.mean(), .03, (rotation, region["label"], box))

    def test_unreliable_page_frames_declined_not_guessed(self):
        for media, crop, rotation in (([10, 0, 610, 700], [20, 30, 570, 650], 0),
                                       ([0, 0, 600, 700], [-1, 0, 500, 500], 0),
                                       ([0, 0, 600, 700], [0, 0, math.inf, 500], 0),
                                       ([0, 0, 600, 700], [0, 0, 600, 700], 45)):
            with self.assertRaises(ValueError):
                adapter.visible_bbox(SimpleNamespace(mediabox=media, cropbox=crop, rotation=rotation))

    def test_cache_bounded_excludes_semantic_exploration(self):
        source = dict(pdf_bytes=self.pdf, material_id="m")
        with patch.object(service.pdfplumber_adapter, "parse", wraps=adapter.parse) as parse:
            a = service.get_document(source, [1, 2], [1, 2])
            source["focus"] = "ib"; source["time"] = .1
            self.assertIs(a, service.get_document(source, [2, 1], [1, 2]))
            self.assertEqual(parse.call_count, 1)
            service.get_document(source, [1], [1, 2]); service.get_document(source, [2], [1, 2])
            self.assertEqual(len(source["document_intelligence"]), 2)


class DocumentProductTests(unittest.TestCase):
    @unittest.skipUnless(adapter.available(), "Install requirements-documents.txt")
    def test_local_preview_without_scene_or_api(self):
        with patch.object(compiler, "OpenAI") as api, \
                patch.object(runtime, "_component", return_value=None) as viewer, \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = day19.NormalPDFTests().app()
            at.session_state["learning_scene_cache"] = {}
            at.run()
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertIsNone(at.session_state["learning_scene_state"]["scene"])
            self.assertTrue(viewer.called)
            self.assertFalse(api.called)
            self.assertFalse(at.button(key="atlas-widget-build-pdf19").disabled)

    def test_missing_optional_dependency_disables_only_local_button(self):
        with patch.object(ui, "available", return_value=False), \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = day19.NormalPDFTests().app().run()
            self.assertFalse(at.exception)
            self.assertTrue(at.button(key="atlas-widget-native-pdf19").disabled)
            self.assertFalse(at.button(key="atlas-widget-build-pdf19").disabled)

    def test_parser_failure_preserves_existing_analysis_and_world(self):
        with patch.object(ui, "available", return_value=True), \
                patch.object(ui, "get_document", side_effect=ValueError("malformed external data")), \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = day19.NormalPDFTests().app().run()
            before = copy.deepcopy(at.session_state["analysis"])
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(before, at.session_state["analysis"])
            self.assertIsNotNone(at.session_state["learning_scene_state"]["scene"])
            self.assertFalse(at.button(key="atlas-widget-build-pdf19").disabled)

    @unittest.skipUnless(adapter.available(), "Install requirements-documents.txt")
    def test_normal_pdf_local_preview_then_semantic_build_no_extra_calls(self):
        client = MagicMock(); client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(atlas_fixture()))
        with patch.object(compiler, "OpenAI", return_value=client), \
                patch.object(runtime, "_component", return_value=None) as viewer, \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state), \
                patch.object(service.pdfplumber_adapter, "parse", wraps=adapter.parse) as parse:
            at = day19.NormalPDFTests().app().run()
            self.assertEqual(parse.call_count, 0)
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(viewer.called)
            self.assertEqual(parse.call_count, 1)
            self.assertEqual(client.responses.create.call_count, 0)
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("native_p1_line0").run()
            self.assertFalse(at.exception)
            self.assertTrue(any("Ia(t)" in e.value for e in at.text))
            self.assertFalse(at.button(key="atlas-widget-build-pdf19").disabled)
            at.button(key="atlas-widget-build-pdf19").click().run()
            self.assertFalse(at.exception)
            document = at.session_state["source_atlas_state"]["document_model"]
            formula = at.session_state["source_atlas_state"]["atlas"]["regions"][0]
            self.assertEqual(formula["bbox"], document["atlas"]["regions"][0]["bbox"])
            at.radio(key="workspace-mode-pdf19").set_value("explore").run()
            from world_events import world_patch
            world_patch(at,"set_focus","ib",None)
            at.radio(key="workspace-mode-pdf19").set_value("source").run()
            self.assertFalse(at.exception)
            self.assertEqual(client.responses.create.call_count, 1)
            self.assertEqual(parse.call_count, 1)
            content = client.responses.create.call_args.kwargs["input"][0]["content"]
            self.assertTrue(json.loads(content[0]["text"])["native_text_regions"])


REAL_PDF = Path(__file__).parent / "fixtures" / "day20_projectile_source_atlas.pdf"


@unittest.skipUnless(adapter.available(), "Install requirements-documents.txt")
class LivePDFRegressionTests(unittest.TestCase):
    """Exact user-named test PDF, copied unchanged; no production fixture path."""
    def setUp(self):
        self.pdf = REAL_PDF.read_bytes()

    def app(self):
        from source_lens import new_source_state
        # Use the real normal result entrypoint, not a standalone UI surrogate.
        at = day19.NormalPDFTests().app()
        at.session_state["learning_scene_cache"] = {}
        at.session_state["source_context"] = dict(kind="pdf", page_texts=day19.page_texts(self.pdf))
        at.session_state["learning_canvas"]["source"] = new_source_state("pdf19", self.pdf)
        return at

    def test_real_chars_and_all_regions_survive_normalization(self):
        import pdfplumber
        with pdfplumber.open(io.BytesIO(self.pdf)) as doc:
            self.assertEqual([(len(p.extract_text()), len(p.chars)) for p in doc.pages], [(275, 256), (640, 622)])
        result = adapter.parse(self.pdf, [1, 2], [1, 2])
        self.assertEqual(len(result["atlas"]["regions"]), 34)
        self.assertEqual(result["atlas"]["diagnostics"], [])
        last = result["atlas"]["regions"][-1]
        self.assertEqual(last["source_text_excerpt"].count(">"), 2)
        self.assertEqual(last["label"], last["source_text_excerpt"])

    def test_real_selected_page_filtering(self):
        for pages, count in (([1], 15), ([2], 19), ([2, 1], 34)):
            result = adapter.parse(self.pdf, pages, [1, 2])
            self.assertEqual(result["atlas"]["processed_pages"], sorted(pages))
            self.assertEqual(len(result["atlas"]["regions"]), count)
            self.assertEqual({r["page"] for r in result["atlas"]["regions"]}, set(pages))

    def test_native_comparisons_not_generated_markup(self):
        pdf = text_pdf(["speed > 0", "time < 5"])
        result = adapter.parse(pdf, [1], [1])
        self.assertEqual([r["source_text_excerpt"] for r in result["atlas"]["regions"]], ["speed > 0", "time < 5"])
        raw = copy.deepcopy(result["atlas"]); raw.pop("diagnostics")
        for r in raw["regions"]: r.pop("excerpt_verified")
        # Generated semantic Atlas policy is NOT widened by the native path.
        self.assertEqual(len(normalize_atlas(raw, [1], {})["diagnostics"]), 2)
        for line in ("<svg onload=evil>", "<script>evil</script>"):
            with self.assertRaises(model.DocumentError): adapter.parse(text_pdf([line]), [1], [1])

    def test_diagnostics_counts_and_precise_safe_reason(self):
        with self.assertLogs("document_intelligence", level="INFO") as logs:
            adapter.parse(self.pdf, [1, 2], [1, 2])
        text = "\n".join(logs.output)
        for expected in ("requested_pages=[1, 2]", "parsed_pages=[1, 2]", "page=1 chars=256",
                         "page=2 chars=622", "regions_produced=19", "produced=34 accepted=34"):
            self.assertIn(expected, text)
        with self.assertLogs("document_intelligence", level="WARNING") as logs:
            with self.assertRaises(model.DocumentError): adapter.parse(text_pdf(["<svg onload=evil>"]), [1], [1])
        self.assertIn("regions[0].plain_text", "\n".join(logs.output))
        self.assertIn("'regions_produced': 1", "\n".join(logs.output))
        self.assertIn("'normalized_regions': 0", "\n".join(logs.output))
        self.assertNotIn("onload=evil", "\n".join(logs.output))

    def test_real_normal_pdf_visible_availability_retry_and_filtering(self):
        with patch.object(compiler, "OpenAI") as api, \
                patch.object(runtime, "_component", return_value=None) as viewer, \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app().run()
            at.session_state["source_atlas_state"]["document_error"] = True
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            state = at.session_state["source_atlas_state"]
            self.assertTrue(state["parser_available"])
            self.assertTrue(state["document_available"])
            self.assertNotIn("document_error", state)
            self.assertTrue(any("34 個文字區域" in e.value for e in at.caption))
            self.assertFalse(any("此 PDF 暫無法" in e.value for e in at.caption))
            self.assertTrue(viewer.called)
            self.assertEqual(len(viewer.call_args.kwargs["payload"]["regions"]), 15)
            next(e for e in at.multiselect if e.key == "atlas-widget-pages-pdf19").set_value([2]).run()
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(at.session_state["source_atlas_state"]["document_available"])
            self.assertTrue(any("19 個文字區域" in e.value for e in at.caption))
            self.assertEqual(viewer.call_args.kwargs["payload"]["page"], 2)
            self.assertEqual(len(viewer.call_args.kwargs["payload"]["regions"]), 19)
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("native_p2_line18").run()
            self.assertFalse(at.exception)
            self.assertTrue(any(">" in e.value for e in at.text))
            self.assertFalse(api.called)

    def test_old_document_contract_can_be_explicitly_rebuilt(self):
        with patch.object(runtime, "_component", return_value=None), \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app().run()
            at.session_state["source_atlas_state"]["document_model"] = dict(version="1.0")
            at.run()
            self.assertFalse(at.exception)
            self.assertFalse(at.button(key="atlas-widget-native-pdf19").disabled)
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertTrue(at.session_state["source_atlas_state"]["document_available"])

    def test_no_text_layer_preserves_graceful_ui_fallback(self):
        with patch.object(compiler, "OpenAI") as api, \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app()
            at.session_state["learning_canvas"]["source"]["pdf_bytes"] = corpus()["image_only"]
            at.session_state["allowed_source_pages"] = [1]
            at.session_state["source_context"] = dict(kind="pdf", page_texts={1: ""})
            at.run(); at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertFalse(at.session_state["source_atlas_state"]["document_available"])
            self.assertIn("no native text regions", at.session_state["source_atlas_state"]["document_diagnostic"])
            self.assertTrue(any("此 PDF 暫無法" in e.value for e in at.caption))
            self.assertFalse(at.button(key="atlas-widget-build-pdf19").disabled)
            self.assertFalse(api.called)

    def test_optional_dependency_gate_is_rechecked_not_cached(self):
        with patch.object(ui, "available", return_value=False) as available, \
                patch.object(runtime, "_component", return_value=None), \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app().run()
            self.assertTrue(at.button(key="atlas-widget-native-pdf19").disabled)
            available.return_value = True
            at.run()
            self.assertFalse(at.button(key="atlas-widget-native-pdf19").disabled)
            at.button(key="atlas-widget-native-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(at.session_state["source_atlas_state"]["document_available"])


if __name__ == "__main__": unittest.main()
