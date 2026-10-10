"""Day 18 physical state, unsafe declarations, two-domain and product evidence."""

import ast
import copy
import json
import math
from pathlib import Path
import subprocess
import shutil
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler
from scene.state import cache_key
from scene.validator import clean_scene, normalize_scene
from scene.world import runtime
from scene.world.engine import evaluate, frames, inverse_patch, invariant_report, snapshot
from scene.world.schema import DOMAIN, MAX_RECORDING_STEPS, WORLD_SCHEMA
from scene.world.state import apply_patch, baseline_action, changes, consume_event, new_state, replay_states, run_experiment, start_recording
from scene.world.validator import WorldValidationError, normalize_world
try:
    from support import ROOT
    from world_fixtures import circular_world, complete_projectile_world, projectile_world, spatial_analysis, three_phase_world
except ModuleNotFoundError:
    from .support import ROOT
    from .world_fixtures import circular_world, complete_projectile_world, projectile_world, spatial_analysis, three_phase_world


class WorldLogicTests(unittest.TestCase):
    def setUp(self):
        self.scene = normalize_world(three_phase_world(), [1])
        self.state = new_state(self.scene)

    def test_strict_schema_and_both_fixtures(self):
        import jsonschema
        for raw in (three_phase_world(), projectile_world()):
            jsonschema.validate(raw, WORLD_SCHEMA)
            normalized = normalize_scene(raw, [1])
            self.assertEqual(normalized["domain"], DOMAIN)
            self.assertTrue(normalized["quantity_order"])
            self.assertGreater(normalized["validation_report"]["sample_checks"], 0)

    def test_current_sum_phase_separation_and_resultant(self):
        data = frames(self.scene, self.state["parameters"])
        v = {key: np.array(value) for key, value in data["values"].items()}
        np.testing.assert_allclose(v["ia"]+v["ib"]+v["ic"], 0, atol=1e-12)
        np.testing.assert_allclose(v["theta"]-v["theta_b"], 2*math.pi/3, atol=1e-12)
        np.testing.assert_allclose(v["theta_b"]-v["theta_c"], 2*math.pi/3, atol=1e-12)
        np.testing.assert_allclose(v["magnitude"], 1.5, atol=1e-12)
        np.testing.assert_allclose(v["rx"], v["ax"]+v["bx"]+v["cx"], atol=1e-12)
        np.testing.assert_allclose(v["ry"], v["ay"]+v["by"]+v["cy"], atol=1e-12)
        self.assertEqual(invariant_report(self.scene, self.state["parameters"]), 7*48)

    def test_120_degree_spatial_axes_and_phase_offsets(self):
        v = evaluate(self.scene, self.state["parameters"], 0.)
        for phase, angle in (("a", 0), ("b", 2*math.pi/3), ("c", 4*math.pi/3)):
            current = v["i"+phase]
            self.assertAlmostEqual(v[phase+"x"]/current, math.cos(angle))
            self.assertAlmostEqual(v[phase+"y"]/current, math.sin(angle))
            self.assertAlmostEqual(current, math.cos(-angle))
            self.assertAlmostEqual(v["axis_"+phase+"x"]/2.5, math.cos(angle))
            self.assertAlmostEqual(v["axis_"+phase+"y"]/2.5, math.sin(angle))

    def test_time_and_parameter_propagation_all_views(self):
        apply_patch(self.scene, self.state, dict(op="set_time", target_id="time", value=.003))
        apply_patch(self.scene, self.state, dict(op="set_parameter", target_id="amplitude", value=1.5))
        data = snapshot(self.scene, self.state)
        self.assertAlmostEqual(data["values"]["theta"], 2*math.pi*50*.003)
        self.assertAlmostEqual(data["projections"]["vector_a"][2], data["projections"]["wave_a"][0])
        self.assertAlmostEqual(data["projections"]["metric_a"][0], data["values"]["ia"])
        self.assertAlmostEqual(data["values"]["magnitude"], 2.25)
        apply_patch(self.scene, self.state, dict(op="set_parameter", target_id="frequency", value=60.))
        self.assertAlmostEqual(snapshot(self.scene, self.state)["values"]["period"], 1/60)

    def test_every_forward_binding_uses_exact_quantity(self):
        for raw in (three_phase_world(), projectile_world()):
            scene = normalize_world(raw, [1]); state = new_state(scene)
            apply_patch(scene, state, dict(op="set_time", target_id="time", value=scene["time"]["max"]*.37))
            data = snapshot(scene, state)
            for binding in scene["bindings"]:
                nums = data["projections"][binding["target_id"]]
                if binding["type"] == "vector_components": nums = nums[2:]
                self.assertEqual(nums, [data["values"][q] for q in binding["quantity_ids"]])

    def test_vector_inverse_maps_angle_to_nearest_legal_cycle(self):
        self.state["time"] = .025
        patch_data = inverse_patch(self.scene, self.state, "rotate_resultant", math.pi/2)
        self.assertAlmostEqual(patch_data["value"], .025)
        apply_patch(self.scene, self.state, inverse_patch(self.scene, self.state, "rotate_resultant", math.pi))
        values = snapshot(self.scene, self.state)["values"]
        self.assertAlmostEqual(abs(math.atan2(values["ry"], values["rx"])), math.pi)

    def test_projectile_uses_same_projection_and_dynamic_origin(self):
        scene = normalize_world(projectile_world(), [1]); state = new_state(scene)
        apply_patch(scene, state, dict(op="set_time", target_id="time", value=.4))
        data = snapshot(scene, state)
        self.assertEqual(data["projections"]["velocity"][:2], data["projections"]["body"])
        self.assertEqual(data["projections"]["curve_px"][0], data["projections"]["body"][0])
        self.assertEqual(data["projections"]["path"], data["projections"]["body"])
        self.assertAlmostEqual(data["values"]["energy"], 18**2/2)

    def test_second_domain_path_and_launch_angle_inverse(self):
        scene = normalize_world(projectile_world(), [1]); state = new_state(scene)
        data = frames(scene, state["parameters"]); index = 70
        patch_data = inverse_patch(scene, state, "path_time", [data["values"]["px"][index], data["values"]["py"][index]])
        self.assertEqual(patch_data["value"], data["times"][index])
        apply_patch(scene, state, inverse_patch(scene, state, "launch_angle", 1.))
        self.assertEqual(state["parameters"]["angle"], 1.)

    def test_baseline_is_immutable_and_change_lens_is_numeric(self):
        baseline_action(self.state, "set"); saved = copy.deepcopy(self.state["baseline"])
        apply_patch(self.scene, self.state, dict(op="set_parameter", target_id="frequency", value=60.))
        self.assertEqual(saved, self.state["baseline"])
        rows = {row["label"]: row for row in changes(self.scene, self.state)}
        self.assertAlmostEqual(rows["Frequency"]["percent"], 20.)
        self.assertAlmostEqual(rows["Period"]["after"], 1/60)
        apply_patch(self.scene, self.state, dict(op="restore_baseline", target_id="", value=None))
        self.assertEqual(self.state["parameters"]["frequency"], 50.)
        baseline_action(self.state, "clear"); self.assertIsNone(self.state["baseline"])

    def test_experiment_atomic_local_state_operations(self):
        with patch.object(compiler, "request_scene", side_effect=AssertionError("Unexpected compiler call")):
            run_experiment(self.scene, self.state, "higher_frequency")
        self.assertEqual(self.state["parameters"]["frequency"], 60.)
        self.assertEqual(self.state["focus"], "period")
        before = copy.deepcopy(self.state)
        bad = copy.deepcopy(self.scene); bad["experiments"][0]["steps"][1]["target_id"] = "unknown"
        with self.assertRaises(ValueError): run_experiment(bad, self.state, "higher_frequency")
        self.assertEqual(before, self.state)

    def test_record_replay_exact_semantic_sequence_and_baseline(self):
        start_recording(self.state)
        baseline_action(self.state, "set")
        apply_patch(self.scene, self.state, dict(op="set_time", target_id="time", value=.005))
        run_experiment(self.scene, self.state, "higher_frequency")
        self.state["recording"] = False
        states = replay_states(self.scene, self.state)
        for key in ("time", "parameters", "focus", "baseline"): self.assertEqual(states[-1][key], self.state[key])
        self.assertEqual(len(states), len(self.state["recorded"])+1)
        self.assertNotIn("source", json.dumps(self.state["recorded"]))

    def test_recording_is_bounded(self):
        start_recording(self.state)
        for _ in range(MAX_RECORDING_STEPS+2): apply_patch(self.scene, self.state, dict(op="set_time", target_id="time", value=.002))
        self.assertEqual(len(self.state["recorded"]), MAX_RECORDING_STEPS)
        self.assertFalse(self.state["recording"])

    def test_browser_patches_are_scoped_deduplicated_and_atomic(self):
        event = dict(scene="identity", revision=0, token="token", kind="patch", patch=dict(op="set_focus", target_id="ia", value=None))
        self.assertTrue(consume_event(self.scene, self.state, "identity", event))
        self.assertEqual(self.state["focus"], "ia")
        self.assertFalse(consume_event(self.scene, self.state, "identity", event))
        for edit in (dict(scene="other"), dict(revision=100), dict(kind="script"), dict(token=[])):
            self.assertFalse(consume_event(self.scene, self.state, "identity", event | edit))

    def test_browser_focus_baseline_and_parameter_use_displayed_time(self):
        def event(kind, **data):
            return dict(scene="identity", revision=self.state["revision"], token=str(self.state["revision"])+kind, kind=kind, **data)
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("focus", semantic_id="ib", time=.025)))
        self.assertEqual(self.state["time"], .025)
        self.assertEqual(self.state["focus"], "ib")
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("baseline", action="set", time=.03)))
        self.assertEqual(self.state["baseline"]["time"], .03)
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("batch", patches=[dict(op="set_time", target_id="time", value=.035), dict(op="set_parameter", target_id="frequency", value=60.)])))
        self.assertEqual(self.state["time"], .035)
        self.assertEqual(self.state["parameters"]["frequency"], 60.)
        saved = copy.deepcopy(self.state)
        self.assertFalse(consume_event(self.scene, self.state, "identity", event("batch", patches=[dict(op="set_time", target_id="time", value=.01), dict(op="set_parameter", target_id="unknown", value=1.)])))
        self.assertEqual(saved, self.state)
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("record", action="start", time=.04)))
        self.assertEqual(self.state["recording_origin"]["time"], .04)
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("experiment", id="higher_frequency", time=.045)))
        self.assertTrue(consume_event(self.scene, self.state, "identity", event("record", action="stop", time=.047)))
        states = replay_states(self.scene, self.state)
        self.assertEqual(states[0]["time"], .04)
        self.assertEqual(states[-1]["time"], .047)

    def test_inverse_uses_active_cycle_time_and_selects_manipulated_entity(self):
        event = dict(scene="identity", revision=0, token="rotate", kind="inverse", binding_id="rotate_resultant", value=math.pi/2, time=.025)
        self.assertTrue(consume_event(self.scene, self.state, "identity", event))
        self.assertAlmostEqual(self.state["time"], .025)
        self.assertEqual(self.state["focus"], "magnitude")

    def test_malformed_recorded_patch_and_unknown_replay_id(self):
        start_recording(self.state)
        for action in (None, dict(kind="script"), dict(kind="patch", patch=dict(op="set_focus", target_id="unknown", value=None)), dict(kind="experiment", id="unknown")):
            with self.subTest(action=action):
                self.state["recorded"] = [action]
                with self.assertRaises(ValueError): replay_states(self.scene, self.state)

    def test_replay_payload_deduplicates_numeric_tables_and_cache_is_bounded(self):
        start_recording(self.state)
        for index in range(40):
            apply_patch(self.scene, self.state, dict(op="set_time", target_id="time", value=.001*index))
        self.state["recording"] = False
        wrapper = dict(world=self.state, material_id="m")
        data = runtime.payload(self.scene, wrapper, replay_states(self.scene, self.state))
        self.assertEqual(len(data["tables"]), 1)
        self.assertEqual(len(data["replay"]), 40)  # Initial identical time patch is a presentation no-op.
        for value in range(40, 47):
            apply_patch(self.scene, self.state, dict(op="set_parameter", target_id="frequency", value=float(value)))
            runtime.payload(self.scene, wrapper)
        self.assertLessEqual(len(wrapper["world_numeric_cache"]), 4)

    def test_an_unsampled_bad_local_state_cannot_enter_runtime(self):
        # Safe syntax can still be numerically undefined between sampled states.
        scene = copy.deepcopy(self.scene)
        scene["quantities"][0]["expression"] = "2*pi*frequency*time+0/(time-0.0031234)"
        before = copy.deepcopy(self.state)
        with self.assertRaises(ValueError):
            apply_patch(scene, self.state, dict(op="set_time", target_id="time", value=.0031234))
        self.assertEqual(before, self.state)

    def test_payload_contains_numeric_projections_no_executable_expressions(self):
        wrapper = dict(world=self.state, material_id="material")
        data = runtime.payload(self.scene, wrapper)
        self.assertEqual(data["data"]["current"]["time"], 0.)
        self.assertNotIn("rate_expression", json.dumps(data))
        self.assertNotIn("expression", data["quantities"][0])
        self.assertLess(wrapper["world_timings"]["payload_bytes"], 2*1024*1024)
        for quantity in data["quantities"]:
            for ref in ("theta_b", "frequency"):
                self.assertNotIn(ref, quantity["equation"])

    def test_cache_excludes_local_state_and_separates_domains(self):
        identity = runtime.scene_identity(self.scene)
        apply_patch(self.scene, self.state, dict(op="set_time", target_id="time", value=.002))
        self.assertEqual(identity, runtime.scene_identity(self.scene))
        self.assertEqual(cache_key("m", "en", DOMAIN), ("m", "en", WORLD_SCHEMA["properties"]["scene_version"]["enum"][0], DOMAIN))
        self.assertNotEqual(cache_key("m", "en"), cache_key("m", "en", DOMAIN))
        self.assertNotEqual(cache_key("m", "en", DOMAIN), cache_key("m", "zh-TW", DOMAIN))

    def test_source_page_filtering_and_no_pasted_text_pages(self):
        raw = three_phase_world(); raw["quantities"][0]["source_pages"] = [1, 7, 99]
        self.assertEqual(normalize_world(raw, [1])["quantities"][0]["source_pages"], [1])
        self.assertTrue(all(not q["source_pages"] for q in normalize_world(raw, [])["quantities"]))

    def test_conservative_source_routing_not_title_specific(self):
        self.assertEqual(compiler.scene_domain(spatial_analysis()), DOMAIN)
        legacy = dict(quick_summary="A physical system")
        source = dict(kind="pdf", page_texts={1: "Time-dependent vector waveforms with frequency and amplitude equations."})
        self.assertEqual(compiler.scene_domain(legacy, source), DOMAIN)
        for summary in ("Frequency is an important topic.", "Spatial relationships in a city.", "Conceptual vectors without a temporal model."):
            self.assertFalse(compiler.scene_candidate(dict(quick_summary=summary)))

    def test_spatial_modules_never_execute_model_code(self):
        for path in (ROOT/"scene"/"world").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            calls = {ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)}
            self.assertFalse(calls & {"eval", "exec", "compile", "__import__"}, path.name)
        html = (ROOT/"scene/world/frontend/index.html").read_text(encoding="utf-8")
        self.assertNotIn("eval(", html); self.assertNotIn("innerHTML", html); self.assertNotIn("https://", html)


class WorldRedTeamTests(unittest.TestCase):
    def test_invalid_declarations_rejected_and_isolated(self):
        cases = []
        def change(name, function):
            raw = three_phase_world(); function(raw); cases.append((name, raw))
        change("version", lambda s: s.update(scene_version="999"))
        change("primitive", lambda s: s["objects"][0].update(type="script"))
        change("objects", lambda s: s.update(objects=s["objects"]*4))
        change("frames", lambda s: s["time"].update(frames=100000))
        change("negative_time", lambda s: s["time"].update(min=-1))
        change("huge_time", lambda s: s["time"].update(max=10001))
        change("axes", lambda s: s["axes"].update(x_max=1e8))
        change("origin", lambda s: s["objects"][0].update(origin=[float("nan"), 0]))
        change("coordinate", lambda s: s["quantities"][6].update(expression="1e7"))
        change("duplicate_id", lambda s: s["objects"][0].update(id="ia"))
        change("parameter_bounds", lambda s: s["parameters"][0].update(min=3))
        change("parameter_step", lambda s: s["parameters"][0].update(step=0))
        change("parameter_default", lambda s: s["parameters"][0].update(default=10))
        change("unknown_binding", lambda s: s["bindings"][0].update(quantity_ids=["unknown", "ay"]))
        change("unknown_entity", lambda s: s["bindings"][0].update(target_id="unknown"))
        change("contradictory_binding", lambda s: s["bindings"][1].update(target_id=s["bindings"][0]["target_id"]))
        change("missing_binding", lambda s: s["bindings"].pop())
        change("unknown_semantic", lambda s: s["objects"][0].update(semantic_id="unknown"))
        change("unknown_origin", lambda s: s["objects"][0].update(origin_quantity_ids=["unknown", "ay"]))
        change("cyclic", lambda s: s["quantities"][0].update(expression="theta_b+1"))
        change("unknown_parameter", lambda s: s["quantities"][0].update(expression="unknown*time"))
        change("division", lambda s: s["quantities"][0].update(expression="1/0"))
        change("infinite", lambda s: s["quantities"][0].update(expression="exp(1000)"))
        change("inverse_type", lambda s: s["inverse_bindings"][0].update(type="arbitrary_solver"))
        change("inverse_target", lambda s: s["inverse_bindings"][0].update(target_id="unknown"))
        change("false_inverse", lambda s: s["inverse_bindings"][0].update(rate_expression="frequency"))
        change("inverse_zero", lambda s: s["inverse_bindings"][0].update(rate_expression="0"))
        change("inverse_cycles", lambda s: s["inverse_bindings"][0].update(rate_expression="1e8"))
        change("invariant_function", lambda s: s["invariants"][0].update(left_expression="open(ia)"))
        change("false_invariant", lambda s: s["invariants"][0].update(right_expression="1"))
        change("invariant_samples", lambda s: s["invariants"][0].update(samples=100000))
        change("invariant_tolerance", lambda s: s["invariants"][0].update(tolerance=100))
        change("experiment_operation", lambda s: s["experiments"][0]["steps"][0].update(op="execute"))
        change("experiment_parameter", lambda s: s["experiments"][0]["steps"][0].update(target_id="unknown"))
        change("experiment_bounds", lambda s: s["experiments"][0]["steps"][0].update(value=100))
        change("experiment_length", lambda s: s["experiments"][0].update(steps=s["experiments"][0]["steps"]*5))
        change("unknown_field", lambda s: s.update(html="<script/>"))
        change("boolean_number", lambda s: s["time"].update(frames=True))
        change("curve_semantic_mismatch", lambda s: next(b for b in s["bindings"] if b["type"] == "curve_value").update(quantity_ids=["ib"]))
        change("malformed_optional_inverse", lambda s: s.update(inverse_bindings=None))
        change("too_few_frames", lambda s: s["time"].update(frames=19))
        change("pathological_step", lambda s: s["parameters"][0].update(step=1e-12))
        change("inverse_unknown_parameter", lambda s: s["inverse_bindings"][0].update(type="angle_to_parameter", target_id="unknown", rate_expression=None))
        change("excessive_ast", lambda s: s["quantities"][0].update(expression="+".join(["1"]*40)))
        for expression in ("x"*401, "(1).__class__", "__import__('os')", "ia[0]", "lambda: 0", "[i for i in range(10)]", "sin(1,2)", "10**1001", "sqrt(-1)", "1e309"):
            change("expression:"+expression[:24], lambda s, e=expression: s["quantities"][0].update(expression=e))
        for name, raw in cases:
            with self.subTest(name=name):
                with self.assertRaises(WorldValidationError): normalize_world(raw, [1])
                self.assertIsNone(clean_scene(raw, [1]))
        self.assertEqual(len(cases), 54)

    def test_malformed_inverses_and_out_of_range_patches_preserve_state(self):
        scene = normalize_world(three_phase_world(), [1]); state = new_state(scene)
        for binding, value in (("unknown", 0), ("rotate_resultant", float("nan")), ("rotate_resultant", [0]), ("rotate_resultant", 100)):
            with self.assertRaises(ValueError): inverse_patch(scene, state, binding, value)
        for patch_data in (dict(op="set_parameter", target_id="frequency", value=61), dict(op="set_time", target_id="time", value=-1), dict(op="set_focus", target_id="unknown", value=None), dict(op="set_time", target_id="time", value=True)):
            before = copy.deepcopy(state)
            with self.assertRaises(ValueError): apply_patch(scene, state, patch_data)
            self.assertEqual(before, state)


class WorldFrontendTests(unittest.TestCase):
    def test_fixed_component_code_and_numeric_state_transitions(self):
        node = shutil.which("node")
        if not node: self.skipTest("Node is needed for the offline frontend smoke test.")
        inputs = []
        for raw in (three_phase_world(), projectile_world(), circular_world(), complete_projectile_world()):
            scene = normalize_world(raw, []); state = new_state(scene)
            wrapper = dict(material_id="m", world=state)
            normal = runtime.payload(scene, wrapper)
            start_recording(state)
            apply_patch(scene, state, dict(op="set_time", target_id="time", value=scene["time"]["max"]*.25))
            state["recording"] = False; state["replay_generation"] = 1
            inputs.append(dict(normal=normal, replay=runtime.payload(scene, wrapper, replay_states(scene, state))))
        result = subprocess.run([node, str(ROOT/"tests/world_frontend_smoke.cjs"), str(ROOT/"scene/world/frontend/index.html")], input=json.dumps(inputs), capture_output=True, encoding="utf-8", timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("passed", result.stdout)


class WorldProductTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(three_phase_world()))
        for patcher in (patch.object(compiler, "OpenAI", return_value=self.client), patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state)):
            patcher.start(); self.addCleanup(patcher.stop)

    def app(self, language="en"):
        at = AppTest.from_file(str(ROOT/"app.py"), default_timeout=30)
        at.session_state["analysis"] = spatial_analysis()
        at.session_state["analysis_id"] = "physics-pdf"
        at.session_state["learning_workspace"] = dict(material_id="physics-pdf", mode="explore", focus=None)
        at.session_state["source_context"] = dict(kind="pdf", source_text="", page_texts={1: "Ia=A cos(ωt). Three phase vectors 120 degrees apart; frequency and amplitude."})
        at.session_state["allowed_source_pages"] = [1]
        at.session_state["product_language"] = language
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run(); self.assertFalse(at.exception)
        return at

    def build(self, at):
        at.button(key="scene-widget-build-physics-pdf").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(at.session_state["learning_scene_state"]["scene"])

    def local_event(self, at, kind, **data):
        """Exercise the production component/reducer boundary, not retired UI."""
        wrapper = at.session_state["learning_scene_state"]
        event = dict(scene=runtime.scene_identity(wrapper["scene"]),
                     revision=wrapper["world"]["revision"],
                     token="local-"+str(wrapper["world"]["revision"]), kind=kind, **data)
        with patch.object(runtime, "_component", return_value=event): at.run()
        self.assertFalse(at.exception)

    def test_normal_pdf_path_exposes_localized_cta_before_overview(self):
        at = self.app("zh-TW")
        self.client.responses.create.assert_not_called()
        self.assertEqual(at.button(key="scene-widget-build-physics-pdf").label, "建立空間學習場景")
        values = [m.value for m in at.markdown]
        self.assertFalse(any("學習概覽" in v for v in values))
        self.assertTrue(any("Visual Learning Lab" in v for v in values))
        self.build(at)
        for label in ("空間視圖", "訊號／波形", "向量／相量", "方程式／狀態视角".replace("视", "視")):
            self.assertTrue(any(label in m.value for m in at.markdown))
        at.radio(key="workspace-mode-physics-pdf").set_value("learn").run()
        self.assertTrue(any(e.label == "概念關係" for e in at.expander))

    def test_build_once_and_parameter_time_experiment_recording_remain_local(self):
        at = self.app(); self.build(at)
        request = self.client.responses.create.call_args.kwargs
        self.assertEqual(request["text"]["format"]["schema"], WORLD_SCHEMA)
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertIn("English", request["instructions"])
        self.local_event(at, "patch", patch=dict(op="set_time", target_id="time", value=.003))
        self.local_event(at, "baseline", action="set", time=.003)
        self.local_event(at, "batch", patches=[dict(op="set_time", target_id="time", value=.003),
                                             dict(op="set_parameter", target_id="amplitude", value=1.5)])
        self.local_event(at, "focus", semantic_id="ia", time=.003)
        self.local_event(at, "record", action="start", time=.003)
        scene = at.session_state["learning_scene_state"]["scene"]
        self.local_event(at, "experiment", id=scene["experiments"][0]["id"], time=.003)
        self.local_event(at, "record", action="stop", time=.003)
        self.local_event(at, "record", action="replay", time=.003)
        at.selectbox(key="product_language").select("zh-TW").run()
        self.assertFalse(at.exception)
        wrapper = at.session_state["learning_scene_state"]
        state = wrapper["world"]
        self.assertEqual(state["parameters"]["frequency"], 60.)
        data = runtime.payload(wrapper["scene"], wrapper)
        self.assertEqual(data["data"]["current"]["time"], .003)
        self.assertAlmostEqual(data["data"]["current"]["values"]["theta"], 2*math.pi*60*.003)
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertTrue(at.session_state["analysis"])

    def test_browser_inverse_reaches_canonical_state_without_api(self):
        at = self.app(); self.build(at)
        wrapper = at.session_state["learning_scene_state"]
        event = dict(scene=runtime.scene_identity(wrapper["scene"]), revision=wrapper["world"]["revision"], token="gesture", kind="inverse", binding_id="rotate_resultant", value=math.pi/2)
        with patch.object(runtime, "_component", return_value=event): at.run()
        self.assertFalse(at.exception)
        self.assertAlmostEqual(at.session_state["learning_scene_state"]["world"]["time"], .005)
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_invalid_browser_gesture_is_acknowledged_without_losing_world(self):
        at = self.app(); self.build(at)
        wrapper = at.session_state["learning_scene_state"]
        event = dict(scene=runtime.scene_identity(wrapper["scene"]), revision=wrapper["world"]["revision"], token="invalid-gesture", kind="inverse", binding_id="unknown", value=0.)
        with patch.object(runtime, "_component", return_value=event): at.run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["learning_scene_state"]["world"]["time"], 0.)
        self.assertTrue(any("world was preserved" in m.value for m in at.info))
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_invalid_generated_world_does_not_break_old_features(self):
        at = self.app(); self.client.responses.create.return_value = SimpleNamespace(output_text='{"domain":"spatial_dynamics"}')
        at.button(key="scene-widget-build-physics-pdf").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(any("did not pass safety validation" in m.value for m in at.info))
        at.radio(key="workspace-mode-physics-pdf").set_value("practice").run()
        self.assertTrue(any("Guided Learning" in m.value for m in at.markdown))
        at.radio(key="workspace-mode-physics-pdf").set_value("explore").run()
        at.run()
        self.assertFalse(at.button(key="scene-widget-build-physics-pdf").disabled)
        self.assertEqual(at.button(key="scene-widget-build-physics-pdf").label, "Regenerate Spatial Learning World")
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_cached_world_reopens_and_new_material_resets_local_state(self):
        at = self.app(); self.build(at)
        self.local_event(at, "patch", patch=dict(op="set_time", target_id="time", value=.005))
        at.session_state["learning_scene_state"] = None
        at.run(); self.assertFalse(at.exception)
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertEqual(at.session_state["learning_scene_state"]["world"]["time"], 0.)
        at.session_state["analysis_id"] = "different-material"
        at.run(); self.assertFalse(at.exception)
        self.assertFalse(at.session_state["learning_scene_state"]["scene"])
        at.radio(key="workspace-mode-different-material").set_value("explore").run()
        self.assertTrue(at.button(key="scene-widget-build-different-material"))

    def test_projectile_uses_identical_product_runtime(self):
        at = self.app(); self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(projectile_world()))
        self.build(at)
        self.local_event(at, "patch", patch=dict(op="set_time", target_id="time", value=.3))
        self.local_event(at, "batch", patches=[dict(op="set_time", target_id="time", value=.3),
                                             dict(op="set_parameter", target_id="angle", value=1.)])
        self.assertFalse(at.exception)
        wrapper = at.session_state["learning_scene_state"]
        data = runtime.payload(wrapper["scene"], wrapper)["data"]["current"]
        self.assertEqual(data["projections"]["velocity"][:2], data["projections"]["body"])
        self.assertEqual(self.client.responses.create.call_count, 1)


if __name__ == "__main__": unittest.main()
