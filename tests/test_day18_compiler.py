"""Live-style compiler → canonical validator → real app result-path regressions."""

import copy
import json
import math
from pathlib import Path
import re
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import jsonschema
import numpy as np
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler
from scene.validator import normalize_scene
from scene.world import runtime
from scene.world.engine import evaluate, frames, project
from scene.world.schema import DOMAIN, INSTRUCTIONS, OPTIONAL_CAPABILITIES, VERSION, WORLD_SCHEMA
from scene.world.state import new_state, run_experiment
from scene.world.validator import WorldValidationError, normalize_world, validate_patch
from scene.world.policy import declaration_defaults
try:
    from day18_acceptance import THREE_PHASE_TEXT, acceptance_analysis
    from scene_fixtures import two_toss_scene
    from support import ROOT
    from world_fixtures import spatial_analysis
except ModuleNotFoundError:
    from .day18_acceptance import THREE_PHASE_TEXT, acceptance_analysis
    from .scene_fixtures import two_toss_scene
    from .support import ROOT
    from .world_fixtures import spatial_analysis


def recorded(name="compiled"):
    result = json.loads((Path(__file__).parent/"fixtures"/f"day18_three_phase_{name}.json").read_text(encoding="utf-8"))
    # The original capture is immutable historical evidence. Version adjustment
    # here tests its semantic errors against the revised contract, not migration.
    result["raw"]["scene_version"] = VERSION
    return declaration_defaults(result["raw"])


def minimal_scene(missing=False):
    raw = recorded()
    for key in OPTIONAL_CAPABILITIES:
        if missing: raw.pop(key)
        else: raw[key] = []
    return raw


class CompilerContractTests(unittest.TestCase):
    def test_canonical_wire_schema_required_keys_and_optional_empty_lists(self):
        raw = minimal_scene()
        jsonschema.validate(raw, WORLD_SCHEMA)
        def strict(schema):
            if schema.get("type") == "object":
                self.assertEqual(set(schema["required"]), set(schema["properties"]))
                self.assertFalse(schema["additionalProperties"])
                for child in schema["properties"].values(): strict(child)
            elif schema.get("type") == "array": strict(schema["items"])
        strict(WORLD_SCHEMA)
        for key in OPTIONAL_CAPABILITIES:
            self.assertEqual(WORLD_SCHEMA["properties"][key]["minItems"], 0)
        self.assertIn("exactly time, NOT t", INSTRUCTIONS)
        self.assertIn("OPTIONAL capabilities", INSTRUCTIONS)

    def test_missing_optional_fields_default_without_mutating_input(self):
        raw = minimal_scene(missing=True); before = copy.deepcopy(raw)
        scene = normalize_scene(raw, [])
        self.assertEqual(before, raw)
        for key in OPTIONAL_CAPABILITIES: self.assertEqual(scene[key], [])
        self.assertEqual(scene["validation_report"]["sample_checks"], 0)
        data = runtime.payload(scene, dict(material_id="base", world=new_state(scene)))
        self.assertEqual(data["inverse"], [])
        self.assertEqual(data["experiments"], [])
        self.assertEqual(len(data["series"]), 3)

    def test_missing_required_base_fields_and_unknown_fields_are_rejected(self):
        for key in WORLD_SCHEMA["properties"].keys() - set(OPTIONAL_CAPABILITIES):
            with self.subTest(field=key):
                raw = minimal_scene(); raw.pop(key)
                with self.assertRaisesRegex(WorldValidationError, "missing fields"):
                    normalize_world(raw, [])
        raw = minimal_scene(); raw["recording_metadata"] = {"script": "arbitrary"}
        with self.assertRaisesRegex(WorldValidationError, "unknown fields"):
            normalize_world(raw, [])

    def test_present_malformed_ultra_fields_are_not_silently_dropped(self):
        for key in OPTIONAL_CAPABILITIES:
            with self.subTest(field=key):
                raw = minimal_scene(); raw[key] = None
                with self.assertRaisesRegex(WorldValidationError, key): normalize_world(raw, [])
        for key, mutate in (
            ("invariants", lambda r: r["invariants"][0].update(right_expression="1", type="approx_equal")),
            ("inverse_bindings", lambda r: r["inverse_bindings"][0].update(rate_expression="frequency")),
            ("experiments", lambda r: r["experiments"][0]["steps"][1].update(target_id="unknown")),
        ):
            with self.subTest(capability=key):
                raw = recorded(); mutate(raw)
                with self.assertRaises(WorldValidationError): normalize_world(raw, [])

    def test_invalid_primitive_binding_and_unsafe_expression_still_rejected(self):
        mutations = [
            lambda r: r["objects"][0].update(type="sphere"),
            lambda r: r["bindings"][0].update(quantity_ids=["unknown", "axis_a_y"]),
            lambda r: r["bindings"][1].update(target_id=r["bindings"][0]["target_id"]),
            lambda r: r["quantities"][3].update(expression="amplitude*cos(2*pi*frequency*t)"),
            lambda r: r["quantities"][3].update(expression="__import__('os')"),
            lambda r: r["quantities"][3].update(expression="amplitude.__class__"),
            lambda r: r["quantities"][3].update(expression="1/0"),
            lambda r: r["quantities"][3].update(expression="sin("),
        ]
        for mutate in mutations:
            raw = minimal_scene(); mutate(raw)
            with self.subTest(raw=raw["quantities"][3]["expression"]):
                with self.assertRaises(WorldValidationError): normalize_world(raw, [])

    def test_valid_three_phase_base_expressions_and_shared_values(self):
        scene = normalize_world(minimal_scene(missing=True), [])
        params = dict(amplitude=2., frequency=2.)
        values = evaluate(scene, params, np.linspace(0, 1.5, 90))
        np.testing.assert_allclose(values["current_a"]+values["current_b"]+values["current_c"], 0., atol=1e-12)
        np.testing.assert_allclose(values["result_magnitude"], 3., atol=1e-12)
        data = frames(scene, params)
        self.assertEqual(data["values"]["current_a"], data["projections"]["current_a_curve"][0])
        self.assertEqual(data["values"]["result_x"], data["projections"]["result_vector"][2])

    def test_real_response_recipe_focus_resolves_only_declared_representation(self):
        raw = recorded(); before = copy.deepcopy(raw)
        scene = normalize_world(raw, [])
        self.assertEqual(raw, before)
        alias = scene["validation_report"]["focus_aliases"]
        self.assertEqual(alias, [dict(experiment="change_frequency", step=2, representation="result_vector", quantity="result_x")])
        recipe = next(e for e in scene["experiments"] if e["id"] == "change_frequency")
        self.assertEqual(recipe["steps"][2]["target_id"], "result_x")
        state = new_state(scene); state["baseline"] = dict(time=0., parameters=dict(state["parameters"]), focus=state["focus"])
        run_experiment(scene, state, "change_frequency")
        self.assertEqual(state["focus"], "result_x")
        self.assertEqual(state["parameters"]["frequency"], 2.)
        raw["experiments"][1]["steps"][2]["target_id"] = "not_a_declared_object"
        with self.assertRaisesRegex(WorldValidationError, "change_frequency.*set_focus"):
            normalize_world(raw, [])
        with self.assertRaises(WorldValidationError):
            validate_patch(scene, dict(op="set_focus", target_id="result_vector", value=None))

    def test_original_live_style_rejection_has_precise_paths(self):
        raw = recorded("rejected")
        with self.assertRaisesRegex(WorldValidationError, r"quantities\[ia\].*reference: t"):
            normalize_world(raw, [])
        for q in raw["quantities"]: q["expression"] = re.sub(r"\bt\b", "time", q["expression"])
        with self.assertRaisesRegex(WorldValidationError, r"inverse_bindings.*rate_expression.*reference: omega"):
            normalize_world(raw, [])
        raw["inverse_bindings"][0]["rate_expression"] = "2*pi*f"
        scene = normalize_world(raw, [])
        self.assertGreater(scene["axes"]["x_max"], raw["axes"]["x_max"])

    def test_axis_roundoff_is_ulp_bounded_not_real_overflow_acceptance(self):
        scene = normalize_world(minimal_scene(), [])
        scene["axes"].update(x_min=-3., x_max=3., y_min=-3., y_max=3.)
        values = evaluate(scene, dict(amplitude=2., frequency=1.), 0.)
        self.assertGreater(values["result_x"], 3.)  # Actual generated on-border sum.
        self.assertLess(values["result_x"]-3., 16*np.spacing(3.))
        project(scene, values)
        values["result_x"] = 3.+1e-8
        with self.assertRaisesRegex(ValueError, "result_vector.*outside"):
            project(scene, values)
        raw = minimal_scene(); raw["axes"]["x_max"] = 2.99
        self.assertGreater(normalize_world(raw, [])["axes"]["x_max"], 3.)

    def test_exact_traditional_chinese_context_schema_and_internal_trace(self):
        context = compiler.build_scene_context(acceptance_analysis(), dict(kind="text", source_text=THREE_PHASE_TEXT), [], DOMAIN)
        client = MagicMock(); client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(minimal_scene()))
        with self.assertLogs(compiler.logger, level="DEBUG") as logs:
            raw = compiler.request_scene(client, "offline-model", context)
        request = client.responses.create.call_args.kwargs
        self.assertEqual(json.loads(request["input"])["relevant_extracted_source_text"], THREE_PHASE_TEXT)
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertEqual(request["text"]["format"]["schema"], WORLD_SCHEMA)
        self.assertIn("Traditional Chinese", request["instructions"])
        trace = "\n".join(logs.output)
        for key in ("compiler result received", "primitives", "parameters", "bindings", "expressions", "inverse_bindings", "invariants", "views"):
            self.assertIn(key, trace)
        self.assertNotIn(THREE_PHASE_TEXT, trace)
        self.assertEqual(normalize_scene(raw, [])["domain"], DOMAIN)

    def test_probability_scene_still_validates(self):
        scene = normalize_scene(two_toss_scene(), [1])
        self.assertEqual(scene["domain"], "probability_sets")


class CompilerProductRegressionTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        for patcher in (patch.object(compiler, "OpenAI", return_value=self.client), patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state)):
            patcher.start(); self.addCleanup(patcher.stop)

    def app(self, raw, old_rejection=False):
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(raw))
        analysis = spatial_analysis(); analysis.update(acceptance_analysis())
        at = AppTest.from_file(str(ROOT/"app.py"), default_timeout=30)
        at.session_state["analysis"] = analysis
        at.session_state["analysis_id"] = "zh-three-phase"
        at.session_state["learning_workspace"] = dict(material_id="zh-three-phase", mode="explore", focus=None)
        at.session_state["source_context"] = dict(kind="text", source_text=THREE_PHASE_TEXT, page_texts={})
        at.session_state["allowed_source_pages"] = []
        at.session_state["product_language"] = "zh-TW"
        if old_rejection:
            at.session_state["learning_scene_cache"] = {("zh-three-phase", "zh-TW", "2.0", DOMAIN): None}
            at.session_state["learning_scene_state"] = dict(cache_key=("zh-three-phase", "zh-TW", "2.0", DOMAIN), attempted=True, scene=None)
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run(); self.assertFalse(at.exception)
        return at

    def build(self, at):
        at.button(key="scene-widget-build-zh-three-phase").click().run()
        self.assertFalse(at.exception)
        return at.session_state["learning_scene_state"]

    def test_minimal_compiler_output_enters_real_normal_result_runtime(self):
        at = self.app(minimal_scene())
        button = at.button(key="scene-widget-build-zh-three-phase")
        self.assertEqual(button.label, "建立空間學習場景")
        self.client.responses.create.assert_not_called()
        wrapper = self.build(at)
        self.assertTrue(wrapper["scene"])
        for label in ("空間視圖", "訊號／波形", "向量／相量", "方程式／狀態視角"):
            self.assertTrue(any(label in m.value for m in at.markdown))
        self.assertFalse(any("資料不完整" in i.value for i in at.info))
        from world_events import world_patch
        world_patch(at, "set_time", "time", .25)
        world_patch(at, "set_parameter", "amplitude", 1.5)
        wrapper = at.session_state["learning_scene_state"]
        data = runtime.payload(wrapper["scene"], wrapper)
        self.assertEqual(data["inverse"], [])
        self.assertEqual(data["experiments"], [])
        self.assertEqual(data["data"]["current"]["time"], .25)
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_real_captured_response_normalizes_and_reaches_runtime(self):
        at = self.app(recorded())
        wrapper = self.build(at)
        self.assertTrue(wrapper["scene"])
        self.assertEqual(wrapper["scene"]["validation_report"]["sample_checks"], 630)
        self.assertEqual(wrapper["scene"]["experiments"][1]["steps"][2]["target_id"], "result_x")
        data = runtime.payload(wrapper["scene"], wrapper)
        self.assertEqual(len(data["objects"]), 7)
        self.assertEqual(len(data["series"]), 3)
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_precise_rejection_reason_remains_internal_and_old_analysis_survives(self):
        at = self.app(recorded("rejected"))
        with self.assertLogs(compiler.logger, level="WARNING") as logs: wrapper = self.build(at)
        self.assertIsNone(wrapper["scene"])
        self.assertIn("quantities[ia].expression", wrapper["validation_reason"])
        self.assertIn("reference: t", "\n".join(logs.output))
        for item in list(at.info)+list(at.caption)+list(at.markdown):
            self.assertNotIn("Unknown expression reference", item.value)
        self.assertTrue(at.session_state["analysis"])
        at.run()
        self.assertFalse(at.button(key="scene-widget-build-zh-three-phase").disabled)
        self.assertEqual(at.button(key="scene-widget-build-zh-three-phase").label, "重新產生空間學習場景")
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_schema_revision_does_not_reuse_old_invalid_cache(self):
        at = self.app(minimal_scene(missing=True), old_rejection=True)
        self.assertFalse(at.button(key="scene-widget-build-zh-three-phase").disabled)
        self.client.responses.create.assert_not_called()
        wrapper = self.build(at)
        self.assertEqual(wrapper["cache_key"], ("zh-three-phase", "zh-TW", VERSION, DOMAIN))
        self.assertTrue(wrapper["scene"])
        self.assertEqual(self.client.responses.create.call_count, 1)


if __name__ == "__main__": unittest.main()
