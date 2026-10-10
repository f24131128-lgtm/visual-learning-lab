"""Zero length is legal; positive kinds and scene safety stay strict."""

import copy
import json
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler
from scene.validator import normalize_scene
from scene.world.engine import frames
from scene.world.policy import normalize_parameter
from scene.world.validator import WorldValidationError
try:
    from support import ROOT
    from world_fixtures import complete_projectile_world, spatial_analysis
except ModuleNotFoundError:
    from .support import ROOT
    from .world_fixtures import complete_projectile_world, spatial_analysis


def projectile_with_height():
    """Independent regression declaration, not a capture of the learner's JSON."""
    raw = complete_projectile_world()
    raw["parameters"].append(dict(id="height", label="初始離地高度", unit="m",
        min=0., max=10., default=0., step=.1, source_pages=[1],
        quantity_kind="length", range_source="pedagogical", display_unit="native"))
    raw["assumptions"] = ["Ground is y=0; vertical coordinates increase upward."]
    raw["time"]["duration_expression"] = "(speed*sin(angle)+sqrt((speed*sin(angle))**2+2*grav*height))/grav"
    next(q for q in raw["quantities"] if q["id"] == "py")["expression"] = "height+speed*sin(angle)*time-0.5*grav*time**2"
    return raw


class ParameterSemanticsTests(unittest.TestCase):
    def test_zero_initial_height_and_ranges_including_zero_are_accepted(self):
        for source in ("source", "pedagogical"):
            for baseline in (0., 2.):
                with self.subTest(source=source, baseline=baseline):
                    raw = projectile_with_height()
                    raw["parameters"][-1].update(range_source=source, default=baseline)
                    before = copy.deepcopy(raw)
                    scene = normalize_scene(raw, [1])
                    self.assertEqual(raw, before)
                    self.assertEqual(scene["parameters"][-1], before["parameters"][-1])
                    params = {p["id"]: p["default"] for p in scene["parameters"]}
                    data = frames(scene, params)
                    self.assertEqual(data["values"]["py"][0], baseline)
                    self.assertAlmostEqual(data["values"]["py"][-1], 0., places=9)
                    self.assertGreaterEqual(min(data["values"]["py"]), -1e-9)

    def test_fixed_ground_level_height_stays_fixed_and_zero(self):
        raw = projectile_with_height()
        raw["parameters"][-1].update(max=0., step=0., range_source="source")
        p = normalize_scene(raw, [1])["parameters"][-1]
        self.assertEqual((p["min"], p["max"], p["default"], p["step"]), (0., 0., 0., 0.))
        self.assertEqual(p["parameter_kind"], "fixed")

    def test_semantic_default_zero_length_has_bounded_nonnegative_range(self):
        raw = projectile_with_height()
        raw["parameters"][-1]["range_source"] = "semantic_default"
        p = normalize_scene(raw, [1])["parameters"][-1]
        self.assertEqual((p["min"], p["max"], p["default"]), (0., 1., 0.))
        self.assertGreater(p["step"], 0.)
        positive = copy.deepcopy(raw["parameters"][-1]); positive["default"] = 2.
        normalize_parameter(positive)
        self.assertEqual((positive["min"], positive["max"]), (.5, 10.))

    def test_negative_length_is_not_repaired_or_reclassified(self):
        for source in ("source", "pedagogical", "semantic_default"):
            for fixed in (False, True):
                with self.subTest(source=source, fixed=fixed):
                    raw = projectile_with_height()
                    p = raw["parameters"][-1]
                    p.update(min=-1., range_source=source)
                    if fixed: p.update(max=-1., default=-1., step=0.)
                    with self.assertRaisesRegex(WorldValidationError, "negative range: height"):
                        normalize_scene(raw, [1])

    def test_signed_coordinate_uses_explicit_scalar_reference_and_range(self):
        raw = projectile_with_height()
        raw["parameters"][-1].update(quantity_kind="scalar", label="Initial vertical coordinate",
            min=-10., max=0., default=-5., range_source="source")
        raw["assumptions"] = ["The coordinate origin is 100 m above ground; ground is y=-100 m."]
        raw["time"]["duration_expression"] = "(speed*sin(angle)+sqrt((speed*sin(angle))**2+2*grav*(height+100)))/grav"
        raw["invariants"][1]["lower"] = -100.
        scene = normalize_scene(raw, [1])
        params = {p["id"]: p["default"] for p in scene["parameters"]}
        data = frames(scene, params)
        self.assertEqual(scene["parameters"][-1]["quantity_kind"], "scalar")
        self.assertEqual(data["values"]["py"][0], -5.)
        self.assertAlmostEqual(data["values"]["py"][-1], -100., places=9)

    def test_strictly_positive_kinds_still_reject_zero_and_negative(self):
        for kind in ("speed", "frequency", "acceleration"):
            for low in (0., -1.):
                for fixed in (False, True):
                    with self.subTest(kind=kind, low=low, fixed=fixed):
                        raw = projectile_with_height()
                        # Name/label cannot override the declared semantic kind.
                        p = raw["parameters"][-1]
                        p.update(quantity_kind=kind, min=low)
                        if fixed: p.update(max=low, default=low, step=0.)
                        with self.assertRaisesRegex(WorldValidationError, "Positive semantic parameter"):
                            normalize_scene(raw, [1])
            p = projectile_with_height()["parameters"][-1]
            p.update(quantity_kind=kind, range_source="semantic_default")
            with self.assertRaisesRegex(ValueError, "positive baseline"):
                normalize_parameter(p)

    def test_semantics_follow_kind_not_height_id_or_label(self):
        p = projectile_with_height()["parameters"][-1]
        p.update(id="ground_offset", label="Ground distance")
        self.assertEqual(normalize_parameter(p)["min"], 0.)

    def test_numeric_and_expression_safety_remain_enforced(self):
        changes = [dict(min=float("nan")), dict(max=float("inf")),
                   dict(default=float("-inf")), dict(min=11.),
                   dict(default=11.), dict(step=0.), dict(max=1e10)]
        for change in changes:
            with self.subTest(change=change):
                raw = projectile_with_height(); raw["parameters"][-1].update(change)
                with self.assertRaises(WorldValidationError): normalize_scene(raw, [1])
        for expression in ("1/height", "__import__('os')", "height.__class__", "exp(1000)"):
            with self.subTest(expression=expression):
                raw = projectile_with_height(); raw["quantities"][0]["expression"] = expression
                with self.assertRaises(WorldValidationError): normalize_scene(raw, [1])
        raw = projectile_with_height(); raw["time"]["duration_expression"] = "0"
        with self.assertRaisesRegex(WorldValidationError, "duration is non-positive"):
            normalize_scene(raw, [1])

    def test_diagnostic_trace_records_policy_without_source_bodies(self):
        raw = projectile_with_height()
        with self.assertLogs(compiler.logger, level="DEBUG") as logs:
            compiler.log_scene_declaration(raw)
        trace = "\n".join(logs.output)
        self.assertIn('"quantity_kind": "length"', trace)
        self.assertIn('"range_source": "pedagogical"', trace)
        self.assertNotIn("初始離地高度", trace)
        self.assertNotIn(raw["assumptions"][0], trace)


class ValidationFailureProductTests(unittest.TestCase):
    def test_failure_copy_and_explicit_retry_preserve_analysis_and_request_bounds(self):
        client = MagicMock()
        bad = projectile_with_height(); bad["parameters"][-1]["min"] = -1.
        client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(bad))
        with patch.object(compiler, "OpenAI", return_value=client), patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            app = AppTest.from_file(str(ROOT/"app.py"), default_timeout=30)
            analysis = spatial_analysis(); analysis["analysis_language"] = "zh-TW"
            context = dict(kind="text", source_text="Ground-level projectile: x=v cosθ t; y=v sinθ t−g t²/2.", page_texts={})
            app.session_state["analysis"] = copy.deepcopy(analysis)
            app.session_state["analysis_id"] = "zero-height"
            app.session_state["source_context"] = copy.deepcopy(context)
            app.session_state["allowed_source_pages"] = []
            app.session_state["product_language"] = "zh-TW"
            app.session_state["learning_workspace"] = dict(material_id="zero-height", mode="explore", focus=None)
            app.secrets["OPENAI_API_KEY"] = "offline-placeholder"
            app.run(); client.responses.create.assert_not_called()
            app.button(key="scene-widget-build-zero-height").click().run()
            self.assertFalse(app.exception)
            copy_text = "這次互動場景沒有通過安全驗證；原始教材與分析仍可正常使用。你可以重新產生互動場景。"
            self.assertTrue(any(i.value == copy_text for i in app.info))
            reason = app.session_state["learning_scene_state"]["validation_reason"]
            self.assertIn("negative range: height", reason)
            for item in list(app.info)+list(app.caption)+list(app.markdown):
                self.assertNotIn(reason, item.value)
            app.run()
            app.selectbox(key="product_language").select("en").run()
            self.assertTrue(any("Your original material and analysis remain available" in i.value for i in app.info))
            self.assertEqual(client.responses.create.call_count, 1)
            retry = app.button(key="scene-widget-build-zero-height")
            self.assertFalse(retry.disabled)
            self.assertEqual(retry.label, "Regenerate Spatial Learning World")
            client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(projectile_with_height()))
            retry.click().run()
            self.assertFalse(app.exception)
            wrapper = app.session_state["learning_scene_state"]
            self.assertTrue(wrapper["scene"])
            self.assertIsNone(wrapper["error"])
            self.assertNotIn("validation_reason", wrapper)
            self.assertEqual(wrapper["world"]["parameters"]["height"], 0.)
            self.assertEqual(wrapper["language"], "zh-TW")
            self.assertIn("Traditional Chinese", client.responses.create.call_args.kwargs["instructions"])
            app.run()
            self.assertEqual(client.responses.create.call_count, 2)
            self.assertEqual(app.session_state["analysis"], analysis)
            self.assertEqual(app.session_state["source_context"], context)


if __name__ == "__main__": unittest.main()
