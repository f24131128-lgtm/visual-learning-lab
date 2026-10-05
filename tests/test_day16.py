"""Day 16 scene security, physics, API discipline, and real Streamlit regressions."""

import ast
import copy
import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import jsonschema
import numpy as np
import streamlit as st
from streamlit.testing.v1 import AppTest

import dynamic_simulation as studio
import interactive_lab as lab
import learning_canvas as canvas
import simulation_plot as plot
import simulation_spec as scene
from safe_math import MathExpressionError, evaluate_expression, validate_expression
from simulation_fixtures import damped, helix, phasor, projectile, simulation_analysis, unsuitable
from support import ROOT, focused_fixture, load_app_helpers, source_fixture

APP = load_app_helpers()


class SceneTests(unittest.TestCase):
    def clean(self, fixture=projectile, mutate=None, pages=(1, 2)):
        demo, spec = fixture()
        if mutate:
            mutate(spec)
        path = simulation_analysis()[0]["learning_path"]
        return demo, scene.clean_simulation(spec, demo, pages, path, APP["valid_source_pages"])

    def test_strict_schema_all_scenes_and_unsuitable(self):
        def walk(schema):
            if schema.get("type") == "object":
                self.assertIs(schema["additionalProperties"], False)
                self.assertEqual(set(schema["properties"]), set(schema["required"]))
                for value in schema["properties"].values():
                    walk(value)
            if schema.get("type") == "array":
                walk(schema["items"])
            for value in schema.get("anyOf", []):
                walk(value)
        walk(scene.DYNAMIC_SIMULATION_SCHEMA)
        for fixture in (projectile, damped, phasor, helix):
            demo, raw = fixture()
            jsonschema.validate(raw, scene.DYNAMIC_SIMULATION_SCHEMA)
            clean = scene.clean_simulation(raw, demo, [1, 2], simulation_analysis()[0]["learning_path"], APP["valid_source_pages"])
            self.assertTrue(clean["suitable"])
            self.assertTrue(plot.has_motion(clean, plot.compute_scene(clean, demo, lab.default_values(demo))))
        jsonschema.validate(unsuitable(), scene.DYNAMIC_SIMULATION_SCHEMA)
        demo, _ = projectile()
        self.assertFalse(scene.clean_simulation(unsuitable(), demo, [], None, APP["valid_source_pages"])["suitable"])
        self.assertNotIn("dynamic_simulation", APP["ANALYSIS_SCHEMA"]["properties"])

    def test_rejects_malicious_expressions_and_unknown_time_aliases(self):
        attacks = ['__import__("os")', 'open("file")', 'time.__class__', '().__class__', 'globals()', 'locals()',
                   'lambda: 1', 'foo[0]', 'os.system("...")', 'getattr(time,"x")', 'setattr(time,"x",1)',
                   'eval("1")', 'exec("x=1")', 'time > 0', 'time and 1', 't+1', 'T+1', 'seconds+1', 'tau+1', 'body+1']
        for attack in attacks:
            with self.subTest(expression=attack), self.assertRaises(MathExpressionError):
                validate_expression(attack, {"time", "v0", "theta", "g"})
            demo, raw = projectile()
            raw["objects"][0]["x_expression"] = attack
            with self.assertRaises(ValueError):
                scene.clean_simulation(raw, demo, [], None, APP["valid_source_pages"])
        for module in ("simulation_spec.py", "simulation_plot.py", "dynamic_simulation.py", "safe_math.py"):
            tree = ast.parse((ROOT / module).read_text(encoding="utf-8"))
            calls = [ast.unparse(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)]
            self.assertFalse(set(calls) & {"eval", "exec", "compile", "__import__"})
            self.assertFalse(any(call.startswith(("os.system", "subprocess.")) for call in calls))

    def test_whitelisted_shape_bounds_symbols_and_exact_parameters(self):
        bad = [lambda s: s["scene"].update(dimension="4d"), lambda s: s["scene"].update(x_min=1, x_max=1),
               lambda s: s["scene"].update(y_max=float("nan")), lambda s: s["time"].update(id="t"),
               lambda s: s["time"].update(min=10, max=1), lambda s: s["time"].update(max=True),
               lambda s: s["time"].update(frames=True), lambda s: s["time"].update(max_expression="time+1"),
               lambda s: s["parameter_ids"].append("new_slider"), lambda s: s.update(code="print(1)"),
               lambda s: s.update(stop_when={"expression": "time >= 0", "comparison": "below", "threshold": 0}),
               lambda s: s["objects"][0].update(type="mesh"), lambda s: s["objects"][0].update(id="__bad"),
               lambda s: s["objects"][0].update(z_expression="time"), lambda s: s["objects"][0].update(panel="graph"),
               lambda s: s["objects"].extend(s["objects"] * 4)]
        for mutation in bad:
            with self.subTest(mutation=mutation), self.assertRaises((ValueError, TypeError)):
                self.clean(mutate=mutation)
        demo, spec = self.clean(mutate=lambda s: s["time"].update(frames=5000))
        self.assertEqual(spec["time"]["frames"], 300)
        self.assertEqual(len(plot.compute_scene(spec, demo, lab.default_values(demo))["time"]), 300)
        _, spec = self.clean(mutate=lambda s: s["time"].update(frames=0))
        self.assertEqual(spec["time"]["frames"], 20)
        demo, _ = projectile()
        demo["parameters"][0]["id"] = "time"
        self.assertFalse(scene.simulation_candidate(demo))

    def test_bad_objects_drop_independently_duplicate_ids_trails_pages_and_steps(self):
        def mutate(s):
            s["objects"] += [{**s["objects"][0], "id": "unsafe", "x_expression": "open(1)"}, copy.deepcopy(s["objects"][0]),
                              {**s["objects"][1], "id": "missing_trail", "object_id": "missing"}]
            s["metrics"].append({"id": "bad", "label": "invalid", "expression": "1", "unit": ""})
        # Keep within the hard metric count to exercise independent syntax rejection.
        def valid_mutation(s):
            mutate(s)
            s["metrics"] = [s["metrics"][0], {"id": "bad", "label": "invalid", "expression": "missing", "unit": ""}]
            s["source_pages"] = [True, 1, 2, 2, 99]
            s["related_step_ids"] = ["s2", "missing", "s2", [], None]
        _, spec = self.clean(mutate=valid_mutation, pages=(2,))
        self.assertEqual(spec["source_pages"], [2])
        self.assertEqual(spec["related_step_ids"], ["s2"])
        self.assertEqual([obj["id"] for obj in spec["objects"]], ["body", "flight_trail", "ground"])
        self.assertEqual(spec["rejected"], 4)
        self.assertEqual(self.clean(pages=())[1]["source_pages"], [])

    def test_projectile_equivalence_landing_parameter_changes_and_boundary(self):
        demo, spec = self.clean()
        values = lab.default_values(demo)
        data = plot.compute_scene(spec, demo, values)
        time = data["time"]
        x, y = (data["objects"]["body"]["position"][axis] for axis in "xy")
        np.testing.assert_allclose(x, values["v0"] * math.cos(values["theta"] * math.pi / 180) * time)
        np.testing.assert_allclose(y, values["v0"] * math.sin(values["theta"] * math.pi / 180) * time - .5 * values["g"] * time**2)
        np.testing.assert_allclose(y, evaluate_expression(demo["series"][0]["expression"], {**values, "x": x}), atol=1e-11)
        self.assertGreater(x[-1], x[0])
        self.assertGreater(y.max(), 0)
        self.assertGreaterEqual(y.min(), 0)
        self.assertAlmostEqual(y[-1], 0, places=9)
        faster = plot.compute_scene(spec, demo, {**values, "v0": 30})
        self.assertGreater(faster["objects"]["body"]["position"]["x"][-1], x[-1])
        # Test safe boundary crossing independent of a model-provided flight time.
        spec["time"]["max_expression"] = None
        data = plot.compute_scene(spec, demo, values)
        self.assertTrue(data["stopped"])
        self.assertGreaterEqual(data["objects"]["body"]["position"]["y"].min(), 0)
        self.assertAlmostEqual(data["time"][-1], 2*values["v0"]*math.sin(math.pi/4)/values["g"], places=9)
        spec["stop_when"] = {"expression": "time", "comparison": "above", "threshold": 1}
        self.assertAlmostEqual(plot.compute_scene(spec, demo, values)["time"][-1], 1, places=9)
        spec["stop_when"]["threshold"] = -1
        with self.assertRaises(MathExpressionError):
            plot.compute_scene(spec, demo, values)

    def test_damped_oscillation_decay_frequency_phase_amplitude_and_linked_graph(self):
        demo, spec = self.clean(damped)
        values = lab.default_values(demo)
        data = plot.compute_scene(spec, demo, values)
        x = data["objects"]["body"]["position"]["x"]
        envelope = data["metrics"]["envelope"]
        self.assertGreater(envelope[0], envelope[-1])
        self.assertTrue(np.all(np.abs(x) <= envelope + 1e-12))
        np.testing.assert_allclose(x, data["objects"]["graph_marker"]["position"]["y"])
        larger = plot.compute_scene(spec, demo, {**values, "V_m": 3})
        np.testing.assert_allclose(larger["objects"]["body"]["position"]["x"], 3*x)
        fast = plot.compute_scene(spec, demo, {**values, "omega": 4})["objects"]["body"]["position"]["x"]
        self.assertGreater(np.count_nonzero(np.diff(np.signbit(fast))), np.count_nonzero(np.diff(np.signbit(x))))
        shift = plot.compute_scene(spec, demo, {**values, "theta": 90})["objects"]["body"]["position"]["x"]
        self.assertAlmostEqual(shift[0], 0)
        decay = plot.compute_scene(spec, demo, {**values, "a": 1})["metrics"]["envelope"]
        self.assertLess(decay[-1], envelope[-1])

    def test_phasor_radius_rotation_projection_and_3d_helix(self):
        demo, spec = self.clean(phasor)
        values = {**lab.default_values(demo), "V_m": 3, "theta": 90}
        data = plot.compute_scene(spec, demo, values)
        end = data["objects"]["rotator"]["end"]
        np.testing.assert_allclose(np.hypot(end["x"], end["y"]), 3)
        self.assertAlmostEqual(end["x"][0], 0)
        self.assertAlmostEqual(end["y"][0], 3)
        np.testing.assert_allclose(end["x"], data["objects"]["graph_marker"]["position"]["y"])
        demo, spec = self.clean(helix)
        data = plot.compute_scene(spec, demo, {"radius": 1})
        position = data["objects"]["body"]["position"]
        np.testing.assert_allclose(position["x"], np.cos(data["time"]))
        np.testing.assert_allclose(position["y"], np.sin(data["time"]))
        np.testing.assert_allclose(position["z"], data["time"])
        figure = plot.build_simulation_figure(spec, data)
        self.assertTrue(all(trace.type == "scatter3d" for trace in figure.data))
        self.assertEqual(len(figure.frames), 121)
        self.assertTrue(figure.layout.updatemenus[0].buttons[0].args[1]["frame"]["redraw"])
        fallback = plot.build_simulation_figure(spec, data, static=True, projection=True)
        self.assertTrue(all(trace.type == "scatter" for trace in fallback.data))

    def test_plotly_clock_trail_metrics_speed_and_static_primitives(self):
        demo, spec = self.clean()
        data = plot.compute_scene(spec, demo, lab.default_values(demo))
        figure = plot.build_simulation_figure(spec, data)
        trail_trace = next(i for i, trace in enumerate(figure.data) if trace.name == "已走過的軌跡")
        end_frame = figure.frames[-1]
        trail = end_frame.data[list(end_frame.traces).index(trail_trace)]
        self.assertEqual(len(trail.x), plot.MAX_TRAIL_POINTS)
        self.assertAlmostEqual(trail.x[-1], data["objects"]["body"]["position"]["x"][-1])
        self.assertEqual(len(figure.layout.sliders[0].steps), len(data["time"]))
        self.assertEqual(figure.layout.updatemenus[0].buttons[1].args[0], (None,))
        self.assertEqual([button.label for button in figure.layout.updatemenus[1].buttons], ["0.5×", "1×", "2×"])
        self.assertTrue(all(button.method == "relayout" for button in figure.layout.updatemenus[1].buttons))
        self.assertIn(f"{data['metrics']['horizontal'][-1]:.4g}", end_frame.layout.annotations[1].text)
        self.assertLess(len(figure.to_json().encode()), plot.MAX_FIGURE_BYTES)
        off = plot.build_simulation_figure(spec, data, show_trail=False, full_path=False)
        self.assertLess(len(off.data), len(figure.data))
        self.assertFalse(plot.build_simulation_figure(spec, data, static=True).frames)
        # Cover explicit segments, parameterized markers and static source curves.
        demo, raw = phasor()
        raw["objects"][0]["type"] = "line_segment"
        raw["objects"][2].update(curve_id=None, y_expression="V_m*cos(omega*time+theta*pi/180)")
        raw["static_series"] = [{"id": "reference", "label": "參考曲線", "panel": "graph", "x_expression": "time",
                                 "y_expression": "V_m*cos(omega*time+theta*pi/180)", "z_expression": None}]
        spec = scene.clean_simulation(raw, demo, [1, 2], simulation_analysis()[0]["learning_path"], APP["valid_source_pages"])
        self.assertTrue(plot.build_simulation_figure(spec, plot.compute_scene(spec, demo, lab.default_values(demo))).frames)

    def test_html_contains_only_data_for_model_strings_no_cdn_or_autoplay(self):
        demo, spec = self.clean()
        spec["objects"][0]["label"] = '</script><script>alert(1)</script>'
        data = plot.compute_scene(spec, demo, lab.default_values(demo))
        figure = plot.build_simulation_figure(spec, data)
        fallback = plot.build_simulation_figure(spec, data, static=True)
        with patch.object(plot, "_plotly_bundle", return_value="/* trusted bundled library */"):
            html = plot.animation_html(figure, fallback, "fallback")
        self.assertNotIn('</script><script>alert(1)', html)
        self.assertNotIn('src="https://', html)
        self.assertIn("Plotly.addFrames", html)
        self.assertNotIn("Plotly.animate", html)

    def test_context_is_bounded_source_honest_and_uses_analysis_language(self):
        analysis, _ = simulation_analysis()
        demo = analysis["interactive_lab"]["demos"][0]
        analysis["quick_summary"] *= 5000
        source = {"kind": "pdf", "page_texts": {1: "Original formula. "*10000, 99: "Never send this."}}
        context = studio.build_simulation_context(analysis, demo, analysis["learning_path"], source, [1, 2], APP["valid_source_pages"])
        self.assertLessEqual(len(json.dumps(context, ensure_ascii=False)), studio.MAX_CONTEXT_CHARS)
        self.assertLessEqual(len(context["relevant_extracted_source_text"]), studio.MAX_SOURCE_CHARS)
        self.assertEqual(context["response_language"], "Traditional Chinese")
        self.assertNotIn("Never send this", context["relevant_extracted_source_text"])
        self.assertEqual(context["attached_lab_demo"]["parameters"], demo["parameters"])
        self.assertIn("not", scene.SIMULATION_INSTRUCTIONS.lower())
        self.assertFalse(any(key in context for key in ("pdf_bytes", "input_file", "file_id", "current_values")))

    def test_cache_lru_material_language_spec_identity_and_parameter_separation(self):
        analysis, raw = simulation_analysis()
        clean_lab = lab.clean_interactive_lab(analysis["interactive_lab"], [1, 2], analysis["learning_path"], APP["valid_source_pages"])
        demo, spec = self.clean()
        with patch.object(st, "session_state", {}) as state:
            shared = lab.ensure_lab_state("m", clean_lab)
            sim = studio.ensure_simulation_state("m", clean_lab, analysis, analysis["learning_path"], source_fixture(), [1, 2], APP["valid_source_pages"], APP["MODEL"])
            key = studio.spec_cache_key(sim, demo)
            sim["specs"][key] = spec
            values = shared["demos"][demo["id"]]["values"]
            with patch.object(plot, "compute_scene", wraps=plot.compute_scene) as compute:
                first = plot.cached_scene(sim, spec, demo, values, studio.fingerprint(spec))
                self.assertIs(plot.cached_scene(sim, spec, demo, values, studio.fingerprint(spec)), first)
                self.assertEqual(compute.call_count, 1)
                for value in range(15, 24):
                    plot.cached_scene(sim, spec, demo, {**values, "v0": value}, studio.fingerprint(spec))
                self.assertLessEqual(len(sim["frames"]), plot.MAX_FRAME_CACHE_ENTRIES)
                self.assertLessEqual(sum(plot.numeric_size(data) for data in sim["frames"].values()), plot.MAX_FRAME_CACHE_BYTES)
            self.assertEqual(studio.spec_cache_key(sim, demo), key)
            state["guided_quiz_answers"] = {"q1": "b"}
            state["explanation_cache"] = {"saved": True}
            fresh = studio.ensure_simulation_state("new", clean_lab, analysis, analysis["learning_path"], source_fixture(), [1, 2], APP["valid_source_pages"], APP["MODEL"])
            self.assertFalse(fresh["frames"])
            self.assertFalse(fresh["specs"])
            self.assertEqual(state["guided_quiz_answers"], {"q1": "b"})
            analysis["analysis_language"] = "en"
            another = studio.ensure_simulation_state("new", clean_lab, analysis, analysis["learning_path"], source_fixture(), [1, 2], APP["valid_source_pages"], APP["MODEL"])
            self.assertNotEqual(studio.spec_cache_key(another, demo), studio.spec_cache_key(fresh, demo))
            changed = copy.deepcopy(demo)
            changed["parameters"][0]["default"] = 20
            self.assertNotEqual(studio.spec_cache_key(another, demo), studio.spec_cache_key(another, changed))


class SimulationInteractionTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.responses.create.side_effect = AssertionError("Unexpected model request")
        for patcher in (patch.object(studio, "OpenAI", return_value=self.client),
                        patch("openai.OpenAI", return_value=self.client),
                        patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def app(self, kind="projectile", language="en"):
        analysis, self.raw_scene = simulation_analysis(kind)
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
        at.session_state["analysis"] = analysis
        at.session_state["analysis_id"] = "sim-material"
        at.session_state["learning_workspace"] = dict(material_id="sim-material", mode="explore", focus=None)
        at.session_state["allowed_source_pages"] = [1, 2]
        at.session_state["source_context"] = source_fixture()
        at.session_state["product_language"] = language
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run()
        self.assertFalse(at.exception)
        return at

    def click(self, at, label):
        next(button for button in at.button if button.label == label).click().run()
        self.assertFalse(at.exception)

    def build(self, at):
        self.client.responses.create.side_effect = lambda **kw: SimpleNamespace(output_text=json.dumps(self.raw_scene))
        self.click(at, "Create dynamic simulation")
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertTrue(at.session_state["dynamic_simulation_state"]["specs"])

    def test_build_one_cached_zero_local_options_and_shared_sliders_preserve_learning(self):
        at = self.app()
        self.client.responses.create.assert_not_called()
        at.selectbox(key="canvas-list-sim-material-concept_map").select("transform").run()
        at.session_state["guided_learning_started"] = True
        at.session_state["guided_learning_step_id"] = "s2"
        at.session_state["guided_quiz_answers"] = {"q1": "b"}
        at.session_state["guided_quiz_checked"] = {"q1": True}
        at.session_state["explanation_cache"] = {"saved": True}
        at.session_state["focused_review_cache"] = {"saved": focused_fixture()}
        self.build(at)
        request = self.client.responses.create.call_args.kwargs
        self.assertEqual(request["model"], APP["MODEL"])
        self.assertTrue(request["text"]["format"]["strict"])
        self.assertIn("Traditional Chinese", request["instructions"])
        self.assertIsInstance(request["input"], str)
        self.client.files.create.assert_not_called()
        saved_spec = copy.deepcopy(at.session_state["dynamic_simulation_state"]["specs"])
        at.slider[0].set_value(30.0).run()
        self.assertEqual(len(at.slider), 3)  # No independent simulation sliders.
        for label in ("Show trail", "Full path", "Static view"):
            checkbox = next(item for item in at.checkbox if item.label == label)
            checkbox.set_value(not checkbox.value).run()
        self.click(at, "Reset parameters")
        self.click(at, "Open simulation")
        at.selectbox(key="product_language").select("zh-TW").run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertEqual(at.session_state["dynamic_simulation_state"]["specs"], saved_spec)
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "transform")
        self.assertEqual(at.session_state["guided_learning_step_id"], "s2")
        self.assertEqual(at.session_state["guided_quiz_answers"], {"q1": "b"})
        self.assertIn("saved", at.session_state["focused_review_cache"])
        self.assertIn("saved", at.session_state["explanation_cache"])
        self.assertFalse(at.exception)

    def test_lesson_inspector_review_and_focused_review_use_existing_mapping(self):
        at = self.app()
        at.radio(key="workspace-mode-sim-material").set_value("practice").run()
        self.click(at, "Start guided learning")
        # Build from the existing lesson link, then every subsequent link is local.
        self.client.responses.create.side_effect = lambda **kw: SimpleNamespace(output_text=json.dumps(self.raw_scene))
        at.button(key="sim-widget-link-guided-sim-material-flight_model").click().run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        lesson_button = next(button for button in at.button if str(button.key).startswith("sim-widget-sim-material-") and str(button.key).endswith("-lesson-s2"))
        lesson_button.click().run()
        at.radio(key="workspace-mode-sim-material").set_value("explore").run()
        at.selectbox(key="canvas-list-sim-material-concept_map").select("transform").run()
        at.button(key="sim-widget-link-inspector-transform-sim-material-flight_model").click().run()
        at.radio(key="workspace-mode-sim-material").set_value("practice").run()
        self.click(at, "Next")
        for i in range(3):
            at.radio(key=f"guided-quiz-option-sim-material-q{i+1}").set_value("b" if i == 1 else "a").run()
            at.button(key=f"guided-quiz-check-sim-material-q{i+1}").click().run()
        at.button(key="sim-widget-link-review-queue-sim-material-flight_model").click().run()
        pattern = at.session_state["adaptive_review_state"]["pattern_key"]
        at.session_state["adaptive_review_state"]["focused_review"] = focused_fixture()
        at.session_state["focused_review_cache"][pattern] = focused_fixture()
        at.radio(key="workspace-mode-sim-material").set_value("practice").run()
        at.button(key="sim-widget-link-focused-review-sim-material-flight_model").click().run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertEqual(at.session_state["guided_quiz_answers"]["q2"], "b")
        self.assertEqual(at.session_state["adaptive_review_state"]["focused_review"], focused_fixture())
        self.assertFalse(at.exception)

    def test_api_failure_malformed_scene_and_unsuitable_cached_preserve_analysis(self):
        at = self.app()
        self.client.responses.create.side_effect = RuntimeError("sensitive error must not be displayed")
        self.click(at, "Create dynamic simulation")
        self.assertTrue(at.session_state["analysis"])
        self.assertEqual(len(at.slider), 3)
        self.assertFalse(any("sensitive error" in item.value for item in at.info))
        self.client.responses.create.side_effect = lambda **kw: SimpleNamespace(output_text='{"wrong": true}')
        self.click(at, "Create dynamic simulation")
        self.assertFalse(at.session_state["dynamic_simulation_state"]["specs"])
        self.client.responses.create.side_effect = lambda **kw: SimpleNamespace(output_text=json.dumps(unsuitable()))
        self.click(at, "Create dynamic simulation")
        self.click(at, "Open simulation")
        self.assertEqual(self.client.responses.create.call_count, 3)
        self.assertFalse(any(item.value == "Dynamic Simulation Studio" for item in at.subheader))
        at.radio(key="workspace-mode-sim-material").set_value("practice").run()
        self.assertTrue(any("Guided Learning" in item.value for item in at.markdown))

    def test_numeric_and_plot_failures_fallback_and_new_material_clear_only_simulation(self):
        at = self.app()
        self.build(at)
        original = studio.build_simulation_figure
        def failure(spec, data, *args, **kwargs):
            if not kwargs.get("static"):
                raise RuntimeError("animation construction failed")
            return original(spec, data, *args, **kwargs)
        with patch.object(studio, "build_simulation_figure", side_effect=failure):
            at.run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.get("plotly_chart")), 2)
        self.assertTrue(any("static trajectory" in item.value for item in at.caption))
        with patch.object(studio, "cached_scene", side_effect=MathExpressionError("numeric failure")):
            at.run()
        self.assertFalse(at.exception)
        self.assertTrue(any("undefined for these values" in item.value for item in at.info))
        at.session_state["analysis_id"] = "new-material"
        at.run()
        self.assertFalse(at.session_state["dynamic_simulation_state"]["specs"])
        self.assertFalse(at.session_state["dynamic_simulation_state"]["frames"])
        at.radio(key="workspace-mode-new-material").set_value("explore").run()
        self.assertEqual(at.slider[0].value, 25)
        self.assertEqual(self.client.responses.create.call_count, 1)

    def test_damped_phasor_helix_render_and_api_site_is_isolated(self):
        for kind in ("damped", "phasor", "helix"):
            self.client.responses.create.reset_mock()
            at = self.app(kind)
            self.build(at)
            self.assertFalse(at.exception)
            self.assertTrue(any(item.value == "Dynamic Simulation Studio" for item in at.subheader))
            self.assertTrue(at.get("iframe"))
        for module, expected in (("app.py", 3), ("dynamic_simulation.py", 1), ("simulation_plot.py", 0), ("simulation_spec.py", 0), ("interactive_lab.py", 0)):
            tree = ast.parse((ROOT / module).read_text(encoding="utf-8"))
            sites = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("responses.create")]
            self.assertEqual(len(sites), expected)


if __name__ == "__main__":
    unittest.main()
