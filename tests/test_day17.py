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
from scene.schema import LEARNING_SCENE_SCHEMA
from scene.validator import SceneValidationError, normalize_scene
from scene_fixtures import probability_analysis, two_toss_scene
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

    def test_mutually_exclusive_events_and_false_declaration(self):
        def exclusive(raw):
            raw["events"][1]["outcome_ids"] = ["o_th", "o_tt"]
            raw["relations"] = [{"id": "exclusive", "type": "mutually_exclusive", "source_event_id": "E", "target_event_id": "F", "source_pages": [2]}]
        self.assertFalse(self.scene(exclusive)["event_sets"]["E"] & self.scene(exclusive)["event_sets"]["F"])
        with self.assertRaises(SceneValidationError):
            self.scene(lambda raw: raw["relations"].append({"id": "false_exclusive", "type": "mutually_exclusive", "source_event_id": "E", "target_event_id": "F", "source_pages": [2]}))

    def test_de_morgan_both_laws_and_inclusion_exclusion_are_derived(self):
        scene = self.scene(); laws = de_morgan(scene, "E", "F")
        self.assertTrue(laws["union_complement"][2]); self.assertTrue(laws["intersection_complement"][2])
        self.assertEqual(laws["union_complement"][0], {"o_tt"})
        values = inclusion_exclusion(scene, "E", "F")
        self.assertEqual(values["left"], probability(scene, scene["event_sets"]["E"]))
        self.assertEqual(values["intersection_count"], 1)
        self.assertEqual(values["union_count"], 3)
        self.assertEqual(values["derived"], values["union"])

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
        at.selectbox(key="scene-widget-focus-probability-material").select("E union F").run()
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
        self.assertTrue(any("Guided Learning" in item.value for item in at.markdown))


if __name__ == "__main__":
    unittest.main()
