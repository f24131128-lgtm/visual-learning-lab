"""Offline Day 14 regression suite: python -m unittest discover -s tests -v."""

import ast
import copy
import io
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import jsonschema
import streamlit as st
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
import source_lens as lens
from support import ROOT, fixture, focused_fixture, load_app_helpers, sample_pdf, source_fixture

APP = load_app_helpers()


class LocalLogicTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        self.session_patch = patch.object(st, "session_state", self.state)
        self.session_patch.start()
        self.addCleanup(self.session_patch.stop)
        self.analysis = fixture()
        self.map = self.analysis["concept_map"]
        self.path = APP["clean_learning_path"](self.analysis["learning_path"], [1, 2], "concept_map", self.map)

    def test_strict_schema_and_all_fixture_types(self):
        def walk(schema):
            if schema.get("type") == "object":
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(set(schema["required"]), set(schema["properties"]))
                for item in schema["properties"].values():
                    walk(item)
            if schema.get("type") == "array":
                walk(schema["items"])
        for name in ("ANALYSIS_SCHEMA", "EXPLANATION_SCHEMA", "FOCUSED_REVIEW_SCHEMA"):
            walk(APP[name])
        for kind in ("flow", "concept_map", "comparison"):
            analysis = fixture(kind)
            if kind == "flow":
                for node in analysis["visual_flow"]["nodes"]:
                    node.pop("role")
            jsonschema.validate(analysis, APP["ANALYSIS_SCHEMA"])

    def test_visual_refs_filter_bad_ids_types_duplicates_without_losing_lesson(self):
        self.analysis["learning_path"]["steps"][0]["visual_refs"] += [
            {"type": "concept_map_node", "id": "input"},
            {"type": "visual_flow_node", "id": "input"},
            {"type": "concept_map_node", "id": "absent"}, {"type": "none", "id": []}, None,
        ]
        path = APP["clean_learning_path"](self.analysis["learning_path"], [1], "concept_map", self.map)
        self.assertTrue(path["suitable"])
        self.assertEqual(path["steps"][0]["visual_refs"], [{"type": "concept_map_node", "id": "input"}])
        self.assertEqual(path["steps"][2]["source_pages"], [])
        self.assertEqual(APP["clean_learning_path"](self.analysis["learning_path"], []) ["steps"][0]["visual_refs"], [])

    def test_component_conversion_and_readonly_flags(self):
        for kind, key in (("concept_map", "concept_map"), ("flow", "visual_flow")):
            graph = fixture(kind)[key]
            component = canvas.build_component_state(kind, graph)
            self.assertEqual([n.id for n in component.nodes], [n["id"] for n in graph["nodes"]])
            self.assertTrue(all(not n.draggable and not n.connectable and not n.deletable for n in component.nodes))
            self.assertTrue(all(not e.deletable for e in component.edges))
            self.assertEqual(component.nodes[0].source_position, "bottom" if kind == "flow" else "right")
            self.assertEqual(bool(component.edges[0].marker_end), kind == "flow")

    def test_model_labels_are_escaped_in_component_html(self):
        self.map["nodes"][0]["label"] = '<img src="https://example.invalid/x">'
        component = canvas.build_component_state("concept_map", self.map)
        self.assertNotIn('<img', component.nodes[0].data["content"])

    def test_selection_event_and_ack_settle_without_loop(self):
        state = canvas.ensure_canvas_state("m")
        state["component"] = canvas.build_component_state("concept_map", self.map)
        canvas.sync_component_styles(state, self.map, set(), set())
        event = copy.deepcopy(state["component"])
        event.timestamp += 5
        event.selected_id = "transform"
        self.assertTrue(canvas.accept_component_event(state, event, self.map))
        canvas.sync_component_styles(state, self.map, set(), set())
        stamp = state["component"].timestamp
        canvas.sync_component_styles(state, self.map, set(), set())
        self.assertEqual(state["component"].timestamp, stamp)
        ack = copy.deepcopy(state["component"])
        ack.timestamp += 5
        ack.selected_id = None
        self.assertFalse(canvas.accept_component_event(state, ack, self.map))
        self.assertEqual(state["selected_id"], "transform")
        self.assertFalse(canvas.accept_component_event(state, event, self.map))
        tampered = copy.deepcopy(ack)
        tampered.timestamp += 5
        tampered.edges.clear()
        with self.assertRaises(ValueError):
            canvas.accept_component_event(state, tampered, self.map)

    def test_material_reset_preserves_other_features_on_click(self):
        state = canvas.ensure_canvas_state("m", b"pdf")
        self.state.update(guided_quiz_answers={"q1": "b"}, adaptive_review_state={"focused_review": focused_fixture()}, explanation_cache={"e": "explanation"})
        saved = copy.deepcopy({k: v for k, v in self.state.items() if k != "learning_canvas"})
        canvas.select_target(state, "transform", self.map)
        state["source"]["view"].update(open=True, page=2)
        self.assertFalse(canvas.select_target(state, "missing", self.map))
        self.assertEqual(saved, {k: v for k, v in self.state.items() if k != "learning_canvas"})
        replacement = canvas.ensure_canvas_state("new")
        self.assertIsNone(replacement["selected_id"])
        self.assertIsNone(replacement["source"]["pdf_bytes"])
        self.assertIsNone(replacement["source"]["view"]["page"])
        self.assertEqual(replacement["source"]["pages"], {})

    def test_lesson_review_focused_highlights_and_priority(self):
        APP["ensure_guided_learning_state"]("m", self.path)
        canvas.go_to_lesson("s1", self.path)
        self.state["guided_quiz_answers"] = {"q3": "b"}
        self.state["guided_quiz_checked"] = {"q3": True}
        self.state["adaptive_review_state"] = {"material_id": "m", "focused_review": focused_fixture()}
        lesson, review = canvas.canvas_highlights(self.path, "m")
        self.assertEqual(lesson, {"input"})
        self.assertEqual(review, {"transform", "output"})
        self.assertEqual(canvas.node_visual_state("input", "input", {"input"}, {"input"}), "selected")
        self.assertEqual(canvas.node_visual_state("input", None, {"input"}, {"input"}), "review")
        self.assertEqual(canvas.node_visual_state("input", None, {"input"}, set()), "lesson")
        self.assertEqual(canvas.related_lessons(self.path, "concept_map_node", "transform")[0][1]["id"], "s2")
        self.assertFalse(canvas.go_to_lesson("absent", self.path))
        self.assertTrue(canvas.go_to_lesson("s2", self.path))
        self.assertEqual(canvas.canvas_highlights(self.path, "m")[0], {"transform"})
        self.assertEqual(canvas.canvas_highlights(self.path, "another"), (set(), set()))

    def test_inspector_reuses_existing_explanation_context_for_all_types(self):
        for kind, key in (("flow", "visual_flow"), ("concept_map", "concept_map"), ("comparison", "comparison")):
            analysis = fixture(kind)
            viz = analysis[key]
            target = canvas.visual_targets(viz)["transform"]
            context = APP["build_explanation_context"](canvas.VISUAL_TARGETS[kind], target, analysis, source_fixture(), [1, 2], viz)
            self.assertEqual(context["selected_item"]["id"], "transform")
            self.assertEqual(context["relevant_pages"], [1, 2])
            if kind == "flow":
                self.assertEqual({e["position"] for e in context["visualization_context"]["connected_relationships"]}, {"previous step", "next step"})
            if kind == "comparison":
                self.assertEqual(context["visualization_context"]["criteria_and_values"][0]["value"], "Material transformation")
            self.assertIsNone(APP["build_explanation_context"](canvas.VISUAL_TARGETS[kind], {"id": "missing", "label": "Missing"}, analysis, source_fixture(), [1, 2], viz))
        for kind, target, viz in (("key_concept", self.analysis["key_concepts"][0], None), ("visual_evidence", self.analysis["visual_evidence"][0], None), ("learning_path_step", self.path["steps"][0], self.path)):
            self.assertIsNotNone(APP["build_explanation_context"](kind, target, self.analysis, source_fixture(), [1, 2], viz))

    def test_pdf_render_cache_source_identity_and_invalid_pages(self):
        pdf = sample_pdf()
        state = lens.new_source_state("m", pdf)
        with patch.object(lens.pymupdf, "open", wraps=lens.pymupdf.open) as opened:
            first = lens.get_page_render(state, "m", 1, [1, 2, 3])
            again = lens.get_page_render(state, "m", 1, [1, 2, 3])
            self.assertIs(first, again)
            self.assertEqual(opened.call_count, 1)
            self.assertTrue(first["png"].startswith(b"\x89PNG"))
            self.assertLessEqual(max(first["width"], first["height"]), lens.MAX_PAGE_SIDE + 1)
            self.assertNotEqual(first["png"], lens.get_page_render(state, "m", 2, [1, 2, 3])["png"])
            self.assertTrue(lens.get_page_render(state, "m", 3, [1, 2, 3])["png"])
        for material, page in (("other", 1), ("m", 0), ("m", 3), ("m", True), ("m", 1.0)):
            with self.assertRaises(ValueError):
                lens.get_page_render(state, material, page, [1, 2])
        with self.assertRaises(ValueError):
            lens.get_page_render(state, "m", 9, [9])
        with self.assertRaises(ValueError):
            lens.get_page_render(lens.new_source_state("m"), "m", 1, [1])

    def test_conservative_text_matching_and_real_highlights(self):
        text = source_fixture()["page_texts"][1]
        anchor = lens.find_text_anchor("Material transformation", text)
        self.assertIn(anchor["excerpt"], text)
        self.assertIsNone(lens.find_text_anchor("Unrelated astronomy", text))
        self.assertIsNone(lens.find_text_anchor("the", text))
        self.assertIsNotNone(lens.find_text_anchor("週期與相位", "我們研究週期與相位的關係。"))
        state = lens.new_source_state("m", sample_pdf())
        render = lens.get_page_render(state, "m", 1, [1, 2])
        rectangles = lens.locate_anchor(state, 1, anchor["phrase"])
        self.assertTrue(rectangles)
        self.assertNotEqual(lens.highlighted_image(render, rectangles), render["png"])
        self.assertEqual(lens.locate_anchor(state, 1, "not in this PDF"), [])
        with patch.object(lens.pymupdf, "open", side_effect=AssertionError("cached anchor should not reopen PDF")):
            self.assertEqual(lens.locate_anchor(state, 1, anchor["phrase"]), rectangles)

    def test_existing_inputs_page_validation_and_graph_builders(self):
        client = MagicMock()
        client.files.create.return_value.id = "file-test"
        self.assertEqual(APP["build_analysis_input"](client, "text", None), "text")
        client.files.create.assert_not_called()
        pdf = io.BytesIO(sample_pdf())
        pdf.name = "test.pdf"
        result = APP["build_analysis_input"](client, "[Page 1] text", pdf)
        self.assertEqual([c["type"] for c in result[0]["content"]], ["input_text", "input_file"])
        data = APP["extract_pdf_text"](pdf)
        self.assertEqual(data["analyzed_page_numbers"], [1, 2])
        self.assertEqual(APP["valid_source_pages"]([True, 1, 2, 999], [1, 2]), [1, 2])
        for kind, cleaner, builder, key in (("flow", "clean_visual_flow", "build_flow_graph", "visual_flow"), ("concept_map", "clean_concept_map", "build_concept_map_graph", "concept_map"), ("comparison", "clean_comparison", "build_comparison_table", "comparison")):
            viz = APP[cleaner](fixture(kind)[key], [1, 2])
            self.assertTrue(APP[builder](viz))

    def test_cache_eviction_and_ambiguous_native_text(self):
        state = lens.new_source_state("m", sample_pdf())
        first = lens.get_page_render(state, "m", 1, [1, 2])
        with patch.object(lens, "MAX_CACHE_BYTES", len(first["png"]) + 1):
            lens.get_page_render(state, "m", 2, [1, 2])
            self.assertLessEqual(sum(len(item["png"]) for item in state["pages"].values()), len(first["png"]) + 1)
        with lens.pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_text((60, 80), "Repeated source phrase")
            page.insert_text((60, 110), "Repeated source phrase")
            state = lens.new_source_state("m", doc.tobytes())
        self.assertEqual(lens.locate_anchor(state, 1, "Repeated source phrase"), [])
        self.assertEqual(lens.highlighted_image(first, []), first["png"])

    def test_quiz_queue_focused_context_retry_and_cache_regressions(self):
        questions = self.path["checkpoint_questions"]
        answers = {"q1": "a", "q2": "b", "q3": "c"}
        checked = dict.fromkeys(answers, True)
        incorrect = APP["get_incorrect_questions"](questions, answers, checked)
        self.assertEqual(APP["calculate_quiz_result"](questions, answers, checked), (1, 3))
        self.assertEqual([item["step_id"] for item in APP["build_review_queue"](self.path, incorrect)], ["s2", "s3"])
        key = APP["build_review_pattern_key"]("m", incorrect, answers)
        self.assertEqual(key, APP["build_review_pattern_key"]("m", list(reversed(incorrect)), answers))
        self.assertNotEqual(key, APP["build_review_pattern_key"]("m", incorrect, {**answers, "q2": "d"}))
        context = APP["build_focused_review_context"](self.analysis, self.path, incorrect, answers, source_fixture(), [1, 2])
        self.assertEqual(context["incorrect_checkpoint_questions"][0]["learner_selected"]["id"], "b")
        self.assertLessEqual(len(context["relevant_extracted_source_text"]), 6000)
        review = APP["clean_focused_review"](focused_fixture(), [1, 2], {"s1", "s2", "s3"})
        self.assertEqual(APP["calculate_quiz_result"](review["retry_questions"], {"retry1": "b"}, {"retry1": True}), (1, 1))
        self.state["focused_review_cache"] = {key: review}
        APP["reset_guided_learning_state"]()
        self.assertNotIn("focused_review_cache", self.state)

    def test_no_new_api_sites_or_api_imports_in_navigation_modules(self):
        for name in ("learning_canvas.py", "source_lens.py"):
            source = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("OpenAI", source)
            self.assertNotIn("responses.create", source)
        tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8-sig"))
        sites = [node for node in ast.walk(tree) if isinstance(node, ast.Call) and ast.unparse(node.func).endswith("responses.create")]
        self.assertEqual(len(sites), 3)


class StreamlitInteractionTests(unittest.TestCase):
    """Run the actual app's widgets/reruns with a fail-on-use OpenAI boundary."""

    def setUp(self):
        self.calls = []
        self.client = MagicMock()
        def response(**kwargs):
            self.calls.append(kwargs)
            name = kwargs["text"]["format"]["name"]
            if name == "visual_learning_explanation":
                value = {"plain_explanation": "A clear explanation.", "why_it_matters": "It connects the steps.", "intuition_or_example": "", "source_note": "Based on supplied source text."}
            elif name == "visual_learning_focused_review":
                value = focused_fixture()
            else:
                raise AssertionError("Main analysis must not run during local interaction")
            return SimpleNamespace(output_text=json.dumps(value))
        self.client.responses.create.side_effect = response
        self.openai_patch = patch("openai.OpenAI", return_value=self.client)
        self.openai_patch.start()
        self.addCleanup(self.openai_patch.stop)
        # The real component transport is exercised separately in browser testing.
        self.component_patch = patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kwargs: state)
        self.component_patch.start()
        self.addCleanup(self.component_patch.stop)

    def app(self, kind="concept_map", pdf=True):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20)
        at.session_state["product_language"] = "en"
        at.session_state["analysis"] = fixture(kind)
        at.session_state["analysis_id"] = "offline-material"
        at.session_state["learning_workspace"] = dict(material_id="offline-material", mode="explore", focus=None)
        at.session_state["allowed_source_pages"] = [1, 2] if pdf else []
        at.session_state["source_context"] = source_fixture() if pdf else {"kind": "text", "source_text": "Incoming material enters the process.", "page_texts": {}}
        at.secrets["OPENAI_API_KEY"] = "offline-test-placeholder"
        at.run()
        self.assertFalse(at.exception)
        state = at.session_state["learning_canvas"]
        state["source"]["pdf_bytes"] = sample_pdf() if pdf else None
        return at

    def click(self, at, label):
        next(button for button in at.button if button.label == label).click().run()
        self.assertFalse(at.exception)

    def test_node_click_source_pages_and_lesson_navigation_are_local(self):
        at = self.app()
        state = at.session_state["learning_canvas"]
        def clicked(key, component, **kwargs):
            returned = copy.deepcopy(component)
            returned.timestamp += 1
            returned.selected_id = "transform"
            return returned
        with patch.object(canvas, "streamlit_flow", side_effect=clicked):
            at.run()
        self.assertFalse(at.exception)
        self.assertEqual(state["selected_id"], "transform")
        self.click(at, "View source")
        self.assertEqual(state["source"]["view"]["page"], 1)
        self.click(at, "p. 2")
        self.assertEqual(state["source"]["view"]["page"], 2)
        self.click(at, "Go to lesson step")
        self.assertEqual(at.session_state["guided_learning_step_id"], "s2")
        self.click(at, "Next")
        self.click(at, "Previous")
        self.assertIsNotNone(state["component"])
        self.assertEqual(self.calls, [])

    def test_accessible_selection_and_explicit_explanation_cache(self):
        at = self.app()
        at.selectbox[1].select("transform").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "transform")
        explain_key = "explain-offline-material:concept_map_node:transform"
        at.button(key=explain_key).click().run()
        self.assertEqual(len(self.calls), 1)
        at.button(key=explain_key).click().run()
        self.assertEqual(len(self.calls), 1)
        self.assertFalse(at.exception)

    def test_comparison_direct_buttons_and_text_source(self):
        at = self.app("comparison", pdf=False)
        self.click(at, "Material transformation")
        self.click(at, "View source")
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "transform")
        self.assertTrue(any("Supplied pasted-text" in cap.value for cap in at.caption))
        self.click(at, "Hide source")
        self.assertFalse(at.session_state["learning_canvas"]["source"]["view"]["open"])
        self.assertTrue(any(button.label == "View source" for button in at.button))
        self.assertEqual(self.calls, [])

    def test_component_error_graphviz_and_list_remain_usable(self):
        with patch.object(canvas, "streamlit_flow", side_effect=RuntimeError("component failed")):
            at = self.app("flow")
        self.assertTrue(at.session_state["learning_canvas"]["fallback"])
        self.assertEqual(len(at.get("graphviz_chart")), 1)
        self.assertFalse(any("Solid purple" in item.value for item in at.caption))
        at.selectbox[1].select("input").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "input")
        self.assertEqual(self.calls, [])

    def test_source_failure_text_fallback_does_not_clear_selection(self):
        at = self.app()
        at.selectbox[1].select("input").run()
        with patch.object(lens, "get_page_render", side_effect=RuntimeError("render failed")):
            self.click(at, "View source")
        self.assertTrue(any("couldn’t preview" in item.value for item in at.info))
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "input")
        self.assertEqual(self.calls, [])

    def test_knowledge_review_focused_cache_retry_and_cross_navigation(self):
        at = self.app()
        at.radio(key="workspace-mode-offline-material").set_value("practice").run()
        self.click(at, "Start guided learning")
        self.click(at, "Next")
        self.click(at, "Next")
        for i in range(3):
            at.radio(key=f"guided-quiz-option-offline-material-q{i+1}").set_value("b" if i == 1 else "a").run()
            at.button(key=f"guided-quiz-check-offline-material-q{i + 1}").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(self.calls, [])
        self.assertTrue(any("1. Material transformation" in m.value for m in at.markdown))
        self.click(at, "Build focused review")
        self.assertEqual(len(self.calls), 1)
        pattern = at.session_state["adaptive_review_state"]["pattern_key"]
        at.run()
        self.assertEqual(len(self.calls), 1)
        at.radio[-1].set_value("b").run()
        self.click(at, "Check answer")  # First original question remains local.
        retry_key = f"adaptive-retry-check-{pattern.rsplit(':', 1)[-1]}-retry1"
        at.button(key=retry_key).click().run()
        self.assertTrue(any("Retry Check: 1 / 1" in msg.value for msg in at.info))
        saved_review = at.session_state["adaptive_review_state"]["focused_review"]
        saved_answers = dict(at.session_state["guided_quiz_answers"])
        self.click(at, "Review step")
        self.assertEqual(at.session_state["guided_learning_step_id"], "s2")
        at.radio(key="workspace-mode-offline-material").set_value("explore").run()
        at.selectbox[1].select("output").run()
        self.assertEqual(at.session_state["guided_quiz_answers"], saved_answers)
        self.assertEqual(at.session_state["adaptive_review_state"]["focused_review"], saved_review)
        self.assertEqual(len(self.calls), 1)
        self.assertFalse(at.exception)

    def test_new_analysis_resets_canvas_source_quiz_and_review(self):
        at = self.app()
        at.selectbox[1].select("transform").run()
        self.click(at, "View source")
        old_state = at.session_state["learning_canvas"]
        at.session_state["focused_review_cache"] = {"old": focused_fixture()}
        self.client.responses.create.side_effect = lambda **kwargs: SimpleNamespace(output_text=json.dumps(fixture("flow")))
        at.text_area[0].set_value("A different supplied text process.")
        self.click(at, "Visualize")
        state = at.session_state["learning_canvas"]
        self.assertNotEqual(state["material_id"], old_state["material_id"])
        self.assertIsNone(state["selected_id"])
        self.assertIsNone(state["source"]["pdf_bytes"])
        self.assertIsNone(state["source"]["view"]["page"])
        self.assertEqual(state["source"]["pages"], {})
        self.assertEqual(at.session_state["guided_quiz_answers"], {})
        self.assertNotIn("focused_review_cache", at.session_state)
        self.client.files.create.assert_not_called()
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_focused_failure_keeps_queue_and_all_correct_needs_no_call(self):
        at = self.app()
        at.session_state["guided_learning_started"] = True
        at.session_state["guided_learning_step_id"] = "s3"
        at.session_state["guided_quiz_answers"] = {"q1": "a", "q2": "b", "q3": "a"}
        at.session_state["guided_quiz_checked"] = {"q1": True, "q2": True, "q3": True}
        at.radio(key="workspace-mode-offline-material").set_value("practice").run()
        self.client.responses.create.side_effect = RuntimeError("offline simulated failure")
        self.click(at, "Build focused review")
        self.assertEqual(len(at.session_state["adaptive_review_state"]["review_queue"]), 1)
        self.assertEqual(at.session_state["guided_quiz_answers"]["q2"], "b")
        self.assertTrue(at.session_state["analysis"])
        self.assertIsNotNone(at.session_state["adaptive_review_state"]["error"])
        at.radio(key="guided-quiz-option-offline-material-q2").set_value("a").run()
        at.button(key="guided-quiz-check-offline-material-q2").click().run()
        self.assertFalse(at.exception)
        self.assertFalse(any(button.label == "Build focused review" for button in at.button))
        self.assertTrue(any("No review areas" in msg.value for msg in at.success))
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_missing_pdf_bytes_and_sparse_page_fallback(self):
        at = self.app()
        at.selectbox[1].select("transform").run()
        at.session_state["learning_canvas"]["source"]["pdf_bytes"] = None
        self.click(at, "View source")
        self.assertTrue(any("couldn’t preview" in item.value for item in at.info))
        self.assertTrue(any("Incoming material enters" in item.value for item in at.text))
        at.session_state["learning_canvas"]["source"]["pdf_bytes"] = sample_pdf()
        at.session_state["source_context"]["page_texts"][1] = ""
        at.run()
        self.assertFalse(at.exception)
        self.assertTrue(any("No extracted text" in item.value for item in at.text))
        self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
