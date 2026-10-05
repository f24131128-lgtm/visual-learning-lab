"""Day 17 compiler, validator, local probability, and UI regressions."""

import ast
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import jsonschema
import streamlit as st
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler
from scene.expressions import EventExpressionError, display_expression, evaluate_expression, parse_expression
from scene.probability import de_morgan, inclusion_exclusion, monte_carlo, probability
from scene.renderers import (
    build_set_figure, build_tree_graph, inclusion_exclusion_lines,
    probability_decomposition, semantic_focus, set_view_data, tree_view_data,
)
from scene.schema import LEARNING_SCENE_SCHEMA
from scene.validator import SceneValidationError, normalize_scene
from scene_fixtures import formal_probability_pdf_analysis, probability_analysis, two_toss_scene
from support import ROOT


class LearningSceneCoreTests(unittest.TestCase):
    def scene(self, mutate=None, pages=(2,)):
        raw = two_toss_scene()
        if mutate: mutate(raw)
        return normalize_scene(raw, pages)

    def test_strict_schema_and_finite_sample_space_normalization(self):
        raw = two_toss_scene()
        jsonschema.validate(raw, LEARNING_SCENE_SCHEMA)
        scene = self.scene()
        self.assertEqual([item["id"] for item in scene["outcomes"]], ["o_hh", "o_ht", "o_th", "o_tt"])
        self.assertEqual(scene["event_sets"]["E"], frozenset({"o_hh", "o_ht"}))
        self.assertEqual(scene["focus_sets"]["focus_union"], frozenset({"o_hh", "o_ht", "o_th"}))
        self.assertEqual(scene["universe"]["outcome_ids"], frozenset({"o_hh", "o_ht", "o_th", "o_tt"}))
        self.assertEqual(scene["outcome_by_path"][("H", "T")], "o_ht")
        def walk(schema):
            if schema.get("type") == "object":
                self.assertFalse(schema["additionalProperties"])
                self.assertEqual(set(schema["properties"]), set(schema["required"]))
                for value in schema["properties"].values(): walk(value)
            if schema.get("type") == "array": walk(schema["items"])
        walk(LEARNING_SCENE_SCHEMA)

    def test_event_membership_union_intersection_complement_difference(self):
        scene = self.scene(); events = scene["event_sets"]; universe = [item["id"] for item in scene["outcomes"]]
        self.assertEqual(evaluate_expression("E | F", events, universe), {"o_hh", "o_ht", "o_th"})
        self.assertEqual(evaluate_expression("E & F", events, universe), {"o_ht"})
        self.assertEqual(evaluate_expression("~E", events, universe), {"o_th", "o_tt"})
        self.assertEqual(evaluate_expression("E - F", events, universe), {"o_hh"})
        self.assertIn("o_ht", events["E"]); self.assertNotIn("o_tt", events["E"])
        self.assertEqual(display_expression("~(E | F)"), "(E ∪ F)ᶜ")

    def test_universe_is_not_an_event_or_peer_circle(self):
        for identifier, label in (("S", "S"), ("sample_space", "Sample space"), ("event_s", "Ω")):
            with self.subTest(identifier=identifier), self.assertRaises(SceneValidationError):
                self.scene(lambda raw, identifier=identifier, label=label: raw["events"].insert(0, {
                    "id": identifier, "label": label,
                    "outcome_ids": [item["id"] for item in raw["outcomes"]], "source_pages": [2],
                }))
        scene = self.scene()
        figure = build_set_figure(scene, {"active_expression": "E", "selected_outcome_id": None})
        self.assertEqual(sum(shape.type == "circle" for shape in figure.layout.shapes), 2)
        self.assertEqual(figure.layout.meta["universe"], "S")
        self.assertEqual(figure.layout.meta["event_ids"], ["E", "F"])
        self.assertNotIn("S", scene["event_sets"])

    def test_tuple_outcomes_restore_complete_two_stage_tree(self):
        raw = two_toss_scene()
        raw["experiment"] = {"staged": False, "stages": []}
        for outcome in raw["outcomes"]:
            outcome["path"] = []
        raw["views"] = [view for view in raw["views"] if view["type"] != "probability_tree"]
        valid_view_ids = {view["id"] for view in raw["views"]}
        for binding in raw["bindings"]:
            binding["view_ids"] = [view_id for view_id in binding["view_ids"] if view_id in valid_view_ids]
        scene = normalize_scene(raw, [2])
        self.assertTrue(scene["experiment"]["staged"])
        self.assertTrue(scene["experiment"]["inferred"])
        self.assertIn("probability_tree", {view["type"] for view in scene["views"]})
        self.assertEqual(scene["outcome_by_path"], {
            ("H", "H"): "o_hh", ("H", "T"): "o_ht",
            ("T", "H"): "o_th", ("T", "T"): "o_tt",
        })
        self.assertEqual([stage["branch_values"] for stage in scene["experiment"]["stages"]], [["H", "T"], ["H", "T"]])

    def test_incomplete_tuple_product_does_not_invent_a_tree(self):
        raw = two_toss_scene()
        raw["outcomes"].pop()
        raw["experiment"] = {"staged": False, "stages": []}
        for outcome in raw["outcomes"]:
            outcome["path"] = []
        raw["events"][1]["outcome_ids"] = ["o_ht", "o_th"]
        raw["views"] = [view for view in raw["views"] if view["type"] != "probability_tree"]
        for view in raw["views"]:
            view["semantic_ids"] = [value for value in view["semantic_ids"] if value != "o_tt"]
        raw["bindings"] = [binding for binding in raw["bindings"] if binding["semantic_id"] != "o_tt"]
        valid_view_ids = {view["id"] for view in raw["views"]}
        for binding in raw["bindings"]:
            binding["view_ids"] = [view_id for view_id in binding["view_ids"] if view_id in valid_view_ids]
        scene = normalize_scene(raw, [2])
        self.assertFalse(scene["experiment"]["staged"])
        self.assertFalse(scene["outcome_by_path"])

    def test_mutually_exclusive_events_and_false_declaration(self):
        def exclusive(raw):
            raw["events"][1]["outcome_ids"] = ["o_th", "o_tt"]
            raw["relations"] = [{"id": "exclusive", "type": "mutually_exclusive", "source_event_id": "E", "target_event_id": "F", "source_pages": [2]}]
        self.assertFalse(self.scene(exclusive)["event_sets"]["E"] & self.scene(exclusive)["event_sets"]["F"])
        with self.assertRaises(SceneValidationError):
            self.scene(lambda raw: raw["relations"].append({"id": "false_exclusive", "type": "mutually_exclusive", "source_event_id": "E", "target_event_id": "F", "source_pages": [2]}))

    def test_de_morgan_both_laws_and_inclusion_exclusion_are_derived(self):
        scene = self.scene(); laws = de_morgan(scene, "E", "F")
        self.assertNotIn("S", scene["event_sets"])
        self.assertTrue(laws["union_complement"][2]); self.assertTrue(laws["intersection_complement"][2])
        self.assertEqual(laws["union_complement"][0], {"o_tt"})
        values = inclusion_exclusion(scene, "E", "F")
        self.assertEqual(values["left"], probability(scene, scene["event_sets"]["E"]))
        self.assertEqual(values["intersection_count"], 1)
        self.assertEqual(values["union_count"], 3)
        self.assertEqual(values["derived"], values["union"])

    def test_one_semantic_focus_drives_set_tree_formula_and_monte_carlo_targets(self):
        scene = self.scene()
        state = {"active_expression": "E | F", "selected_outcome_id": None}
        expected = frozenset({"o_hh", "o_ht", "o_th"})
        focus = semantic_focus(scene, state)
        self.assertEqual(focus["outcome_ids"], expected)
        self.assertEqual(set_view_data(scene, state)["focus"]["outcome_ids"], expected)
        self.assertEqual(tree_view_data(scene, state)["focus"]["outcome_ids"], expected)
        self.assertEqual(build_set_figure(scene, state).layout.meta["focus_outcome_ids"], sorted(expected))
        result = monte_carlo(scene, focus["outcome_ids"], 100, seed=17)
        self.assertEqual(result["theoretical"], .75)
        self.assertEqual(probability_decomposition(scene, focus["outcome_ids"]), "3/4 = 0.75")

        state["active_expression"] = "E & F"
        intersection = semantic_focus(scene, state)["outcome_ids"]
        self.assertEqual(intersection, frozenset({"o_ht"}))
        self.assertEqual(set_view_data(scene, state)["focus"]["outcome_ids"], intersection)
        self.assertEqual(tree_view_data(scene, state)["focus"]["outcome_ids"], intersection)

    def test_selected_outcome_maps_to_tree_path_and_membership_zone(self):
        scene = self.scene()
        state = {"active_expression": "E", "selected_outcome_id": "o_ht"}
        focus = semantic_focus(scene, state)
        self.assertEqual(focus["outcome_ids"], frozenset({"o_ht"}))
        self.assertEqual(scene["path_by_outcome"]["o_ht"], ("H", "T"))
        self.assertEqual(tree_view_data(scene, state)["leaves"][("H", "T")], "o_ht")
        self.assertEqual(set_view_data(scene, state)["selected_zone"], "both")
        source = build_tree_graph(scene, state).source
        self.assertIn("(H,T)", source)
        self.assertIn('color="#d97706"', source)

    def test_human_labels_hide_internal_ids_and_inclusion_exclusion_is_exact(self):
        raw = two_toss_scene()
        replacements = {"E": "event_e", "F": "event_f"}
        for event in raw["events"]:
            event["id"] = replacements[event["id"]]
        for view in raw["views"]:
            view["semantic_ids"] = [replacements.get(value, value) for value in view["semantic_ids"]]
        for binding in raw["bindings"]:
            binding["semantic_id"] = replacements.get(binding["semantic_id"], binding["semantic_id"])
        for source_ref in raw["source_refs"]:
            source_ref["semantic_id"] = replacements.get(source_ref["semantic_id"], source_ref["semantic_id"])
        for state in raw["states"]:
            state["semantic_ids"] = [replacements.get(value, value) for value in state["semantic_ids"]]
        for target in raw["focus_targets"]:
            target["expression"] = target["expression"].replace("E", "event_e").replace("F", "event_f")
        raw["events"][1]["outcome_ids"] = ["o_ht", "o_th", "o_tt"]
        scene = normalize_scene(raw, [2])
        self.assertEqual(display_expression("event_e | event_f", scene["event_labels"]), "E ∪ F")
        self.assertTrue(all("event_" not in target["label"] for target in scene["focus_targets"]))
        lines = inclusion_exclusion_lines(scene, scene["events"][0], scene["events"][1])
        self.assertEqual(lines, [
            "P(E) = 2/4 = 0.50",
            "P(F) = 3/4 = 0.75",
            "P(E ∩ F) = 1/4 = 0.25",
            "P(E ∪ F)",
            "= P(E) + P(F) − P(E ∩ F)",
            "= 0.50 + 0.75 − 0.25",
            "= 1.00",
        ])
        self.assertNotIn("event_", "\n".join(lines))

    def test_expression_parser_valid_and_malicious_inputs(self):
        for expression in ("E", "F", "E | F", "E & F", "~E", "E - F", "~(E | F)", "(~E) & F"):
            parse_expression(expression, {"E", "F"})
        attacks = ["__import__('os')", "E.__class__", "E[0]", "open(E)", "E or F", "lambda:E", "E+F", "", "G"]
        for expression in attacks:
            with self.subTest(expression=expression), self.assertRaises(EventExpressionError):
                parse_expression(expression, {"E", "F"})
        with self.assertRaises(EventExpressionError): parse_expression("~(" * 10 + "E" + ")" * 10, {"E"})
        with self.assertRaises(EventExpressionError): parse_expression("E | " * 50 + "E", {"E"})

    def test_duplicate_ids_broken_bindings_unknown_events_pages_and_limits(self):
        bad = [
            lambda raw: raw["events"][1].update(id="E"),
            lambda raw: raw["bindings"][0]["view_ids"].append("missing"),
            lambda raw: raw["focus_targets"][0].update(expression="UNKNOWN"),
            lambda raw: raw["events"][0]["outcome_ids"].append("missing"),
            lambda raw: raw["views"][0].update(type="arbitrary_html"),
            lambda raw: raw["outcomes"][1].update(path=["H", "H"]),
            lambda raw: raw["views"].pop(4),
            lambda raw: raw["experiment"].update(staged=False, stages=[]),
        ]
        for mutation in bad:
            with self.subTest(mutation=mutation), self.assertRaises(SceneValidationError): self.scene(mutation)
        scene = self.scene(lambda raw: raw["events"][0].update(source_pages=[2, 99, True]), pages=(2,))
        self.assertEqual(scene["events"][0]["source_pages"], [2])
        with self.assertRaises(SceneValidationError):
            self.scene(lambda raw: raw["outcomes"].extend(copy.deepcopy(raw["outcomes"]) * 16))
        with self.assertRaises(SceneValidationError):
            self.scene(lambda raw: raw["experiment"]["stages"].append({"id": "stage_3", "label": "3", "branch_values": ["a"], "source_pages": []}) or raw["experiment"]["stages"].append({"id": "stage_4", "label": "4", "branch_values": ["a"], "source_pages": []}) or raw["experiment"]["stages"].append({"id": "stage_5", "label": "5", "branch_values": ["a"], "source_pages": []}))

    def test_malformed_specs_gracefully_reject_and_no_execution_calls(self):
        malformed = [None, {}, {"scene_version": "1.0"}, {**two_toss_scene(), "outcomes": "not a list"}]
        for raw in malformed:
            with self.assertRaises(SceneValidationError): normalize_scene(raw, [2])
        for module in ("scene/expressions.py", "scene/validator.py", "scene/probability.py", "scene/runtime.py"):
            tree = ast.parse((ROOT / module).read_text(encoding="utf-8"))
            calls = {ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)}
            self.assertFalse(calls & {"eval", "exec", "compile", "__import__"})

    def test_monte_carlo_is_deterministic_bounded_and_converges(self):
        scene = self.scene(); target = scene["event_sets"]["E"]
        first = monte_carlo(scene, target, 10_000, seed=42)
        self.assertEqual(first, monte_carlo(scene, target, 10_000, seed=42))
        self.assertLess(first["difference"], .03)
        with self.assertRaises(ValueError): monte_carlo(scene, target, 10_001, seed=42)
        with self.assertRaises(ValueError): monte_carlo(scene, target, 0, seed=42)

    def test_context_is_bounded_grounded_and_cache_identity_excludes_local_state(self):
        analysis = probability_analysis(); analysis["quick_summary"] *= 10_000
        context = compiler.build_scene_context(analysis, {"kind": "pdf", "page_texts": {2: "coin toss " * 10_000, 99: "do not send"}}, [2])
        self.assertLessEqual(len(json.dumps(context, ensure_ascii=False)), compiler.MAX_CONTEXT_CHARS)
        self.assertNotIn("do not send", context["relevant_extracted_source_text"])
        self.assertEqual(context["analysis_language"], "en")
        self.assertTrue(compiler.scene_candidate(analysis))

    def test_pdf_candidate_uses_extracted_pages_and_requires_probability_structure(self):
        analysis = formal_probability_pdf_analysis()
        self.assertTrue(compiler.scene_candidate(analysis, {"kind": "pdf", "page_texts": {}}))
        legacy_analysis = copy.deepcopy(analysis)
        legacy_analysis.pop("learning_scene_candidate")
        self.assertFalse(compiler.scene_candidate(legacy_analysis, {"kind": "pdf", "page_texts": {}}))
        source = {"kind": "pdf", "source_text": "", "page_texts": {
            1: "樣 本 空 間 S 包含所有樣本點。",
            2: "事 件是樣本空間的子集合。",
            3: "事件的聯 集、交 集與補 集。",
            4: "機 率公理與等可能有限樣本空間。",
            5: "德 摩 根定律與互斥事件。",
            6: "容 斥原理計算 P(A ∪ B)。",
        }}
        evidence = compiler.scene_candidate_evidence(legacy_analysis, source)
        self.assertEqual(evidence, {"structured": False, "probability": True,
                                    "sample_space": True, "events": True,
                                    "set_operations": True, "candidate": True})
        self.assertTrue(compiler.scene_candidate_evidence(analysis, {})["structured"])
        generic_sets = {"quick_summary": "集合的子集合可使用聯集與交集運算。"}
        self.assertFalse(compiler.scene_candidate(generic_sets))


class LearningSceneAppTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(two_toss_scene()))
        for patcher in (patch.object(compiler, "OpenAI", return_value=self.client),
                        patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state)):
            patcher.start(); self.addCleanup(patcher.stop)

    def app(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        at.session_state["analysis"] = probability_analysis()
        at.session_state["analysis_id"] = "probability-material"
        at.session_state["learning_workspace"] = dict(material_id="probability-material", mode="explore", focus=None)
        at.session_state["allowed_source_pages"] = [2]
        at.session_state["source_context"] = {"kind": "text", "source_text": "Sample space and probability events.", "page_texts": {}}
        at.session_state["product_language"] = "en"
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run(); self.assertFalse(at.exception)
        return at

    def test_explicit_build_once_then_all_scene_interactions_are_local(self):
        at = self.app(); self.client.responses.create.assert_not_called()
        next(button for button in at.button if button.label == "Build Learning Scene").click().run()
        self.assertFalse(at.exception); self.assertEqual(self.client.responses.create.call_count, 1)
        request = self.client.responses.create.call_args.kwargs
        self.assertTrue(request["text"]["format"]["strict"]); self.assertEqual(request["text"]["format"]["schema"], LEARNING_SCENE_SCHEMA)
        self.assertIn("English", request["instructions"]); self.assertIsInstance(request["input"], str)
        self.assertTrue(at.session_state["learning_scene_state"]["scene"])
        at.button(key="scene-widget-outcome-probability-material-o_ht").click().run()
        at.selectbox(key="scene-widget-focus-probability-material").select("E ∪ F").run()
        at.radio(key="scene-widget-lens-probability-material").set_value("De Morgan").run()
        at.radio(key="scene-widget-lens-probability-material").set_value("Inclusion–Exclusion").run()
        at.radio(key="scene-widget-lens-probability-material").set_value("Explore").run()
        at.select_slider(key="scene-widget-samples-probability-material").set_value(10_000).run()
        at.button(key="scene-widget-rerun-probability-material").click().run()
        at.selectbox(key="product_language").select("zh-TW").run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertFalse(at.exception)

    def test_malformed_scene_is_isolated_from_existing_learning_features(self):
        at = self.app(); self.client.responses.create.return_value = SimpleNamespace(output_text='{"wrong": true}')
        next(button for button in at.button if button.label == "Build Learning Scene").click().run()
        self.assertFalse(at.exception); self.assertTrue(at.session_state["analysis"])
        self.assertFalse(at.session_state["learning_scene_state"]["scene"])
        self.assertTrue(any("incomplete or unsafe" in item.value for item in at.info))
        at.radio(key="workspace-mode-probability-material").set_value("practice").run()
        self.assertTrue(any("Guided Learning" in item.value for item in at.markdown))

    def test_realistic_probability_pdf_exposes_early_localized_entry_and_collapses_relationships(self):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        at.session_state["analysis"] = formal_probability_pdf_analysis()
        at.session_state["analysis_id"] = "real-probability-pdf"
        at.session_state["allowed_source_pages"] = [1, 2, 3, 4, 5, 6, 7]
        at.session_state["source_context"] = {"kind": "pdf", "source_text": "", "page_texts": {
            1: "樣本空間 S 包含所有樣本點。",
            2: "事件 E 與 F 是 S 的子集合。",
            3: "聯集、交集、補集與互斥事件。",
            4: "機率公理以及等可能結果。",
            5: "德摩根定律。",
            6: "容斥原理。",
            7: "P(E)=|E|/|S|。",
        }}
        at.session_state["product_language"] = "zh-TW"
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run(); self.assertFalse(at.exception)
        self.client.responses.create.assert_not_called()
        self.assertTrue(any(item.label == "概念關係" for item in at.expander))
        self.assertTrue(any("Day 20 / 30" in item.value for item in at.markdown))
        at.radio(key="workspace-mode-real-probability-pdf").set_value("explore").run()
        build = next(button for button in at.button if button.label == "建立互動學習場景")
        self.assertFalse(any("學習概覽" in item.value for item in at.markdown))
        build.click().run(); self.assertFalse(at.exception)
        self.assertEqual(self.client.responses.create.call_count, 1)
        values = [item.value for item in at.markdown]
        for heading in ("樣本空間", "集合視圖", "機率樹", "公式／推理視角", "蒙地卡羅模擬"):
            self.assertTrue(any(heading in value for value in values), heading)
        self.assertGreaterEqual(len(at.get("plotly_chart")), 2)
        at.button(key="scene-widget-outcome-real-probability-pdf-o_ht").click().run()
        self.assertEqual(at.session_state["learning_scene_state"]["selected_outcome_id"], "o_ht")
        self.assertTrue(any(button.label == "● (H,T)" for button in at.button))
        self.assertTrue(any("(H,T) ∈ E" in item.value for item in at.markdown))
        self.assertTrue(any("(H,T) ∈ F" in item.value for item in at.markdown))
        self.assertTrue(any(metric.label == "理論值" and "0.2500" in metric.value for metric in at.metric))
        self.assertEqual(self.client.responses.create.call_count, 1)


if __name__ == "__main__":
    unittest.main()
