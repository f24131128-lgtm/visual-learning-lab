"""Security, numeric acceptance, localization, and real Streamlit rerun regressions."""

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

import i18n
import interactive_lab as lab
import learning_canvas as canvas
from safe_math import MathExpressionError, evaluate_expression, validate_expression
from lab_fixtures import lab_fixture, learning_fixture, sinusoid_demo
from support import ROOT, focused_fixture, load_app_helpers, source_fixture

APP = load_app_helpers()


class SafeMathTests(unittest.TestCase):
    def test_rejects_code_and_non_math_syntax(self):
        malicious = [
            '__import__("os")', 'open("x")', 'x.__class__', '(lambda: 1)()',
            'foo[0]', 'globals()', 'os.system("...")', 'sin.__call__(x)',
            'x[0]', '[x for x in t]', '{"x": 1}', '{x}', '(x, 1)', 'True', 'None',
            '1j', '"1"', 'x if x else 1', 'x > 0', 'x and 1', 'x // 2', 'x % 2',
            '(x:=1)', 'sin(x=1)', 'sin(*x)', 'sin(x, 2)', 'sum(x)', 'f(x)',
            '__builtins__', 'import os', 'x = 2', 'def f(): pass', 'x; 2',
        ]
        for expression in malicious:
            with self.subTest(expression=expression), self.assertRaises(MathExpressionError):
                validate_expression(expression, {"x", "t", "foo"})

    def test_valid_arithmetic_and_requested_formulas(self):
        t = np.linspace(0, 2, 100)
        values = {"V_m": 2, "omega": 4, "t": t, "theta": 90}
        np.testing.assert_allclose(evaluate_expression("V_m*cos(omega*t + theta*pi/180)", values), 2 * np.cos(4*t + math.pi/2))
        self.assertAlmostEqual(evaluate_expression("2*pi/omega", {"omega": 4}), math.pi/2)
        np.testing.assert_allclose(evaluate_expression("exp(-a*t)*cos(omega*t)", {"a": .5, "t": t, "omega": 2}), np.exp(-.5*t)*np.cos(2*t))
        self.assertEqual(evaluate_expression("sqrt(A**2+B**2)", {"A": 3, "B": 4}), 5)
        self.assertAlmostEqual(evaluate_expression("log(e)+abs(-2)+tan(0)+sin(0)+(+3)", {}), 6)
        for expression, expected in (("a*x+b", 7), ("a*x**2+b", 13), ("a*exp(-x)", 3*math.exp(-2))):
            self.assertAlmostEqual(evaluate_expression(expression, {"a": 3, "x": 2, "b": 1}), expected)

    def test_complexity_and_numeric_limits(self):
        for expression in ["1+"*250+"1", "+"*20+"1", "+".join(["x"]*45), "1e999", "9"*399, "unknown+x"]:
            with self.subTest(expression=expression[:30]), self.assertRaises(MathExpressionError):
                validate_expression(expression, {"x"})
        for expression in ["1/x", "log(x)", "sqrt(-1)", "exp(1000)", "2**1001", "2**(2**100)", "(-1)**0.5"]:
            with self.subTest(expression=expression), self.assertRaises(MathExpressionError):
                evaluate_expression(expression, {"x": 0})
        for value in [float('nan'), float('inf'), True, "1", object(), np.zeros(1001), np.zeros((2, 2)), np.array([object()])]:
            with self.subTest(value=type(value)), self.assertRaises(MathExpressionError):
                evaluate_expression("x+1", {"x": value})
        for name in ["__x", "sin", "pi", "e", "a__b", "9x"]:
            with self.assertRaises(MathExpressionError):
                validate_expression("1", {name})

    def test_no_dynamic_execution_or_external_calls(self):
        tree = ast.parse((ROOT / "safe_math.py").read_text(encoding="utf-8"))
        calls = [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        self.assertFalse(set(calls) & {"eval", "exec", "compile", "open", "__import__"})
        self.assertFalse(any(name.startswith(("os.", "subprocess.", "requests.")) for name in calls))


class LabLogicTests(unittest.TestCase):
    def setUp(self):
        self.state = {}
        patcher = patch.object(st, "session_state", self.state)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.analysis = learning_fixture()
        self.path = self.analysis["learning_path"]

    def clean(self, raw):
        return lab.clean_interactive_lab(raw, [2], self.path, APP["valid_source_pages"])

    def test_strict_schema_pages_and_step_ids(self):
        jsonschema.validate(lab_fixture(), lab.INTERACTIVE_LAB_SCHEMA)
        jsonschema.validate(self.analysis, APP["ANALYSIS_SCHEMA"])
        raw = lab_fixture()
        raw["demos"][0]["source_pages"] = [True, 1, 2, 2, 100]
        raw["demos"][0]["related_step_ids"] = ["s2", "s2", "missing", [], None]
        result = self.clean(raw)
        self.assertEqual(result["demos"][0]["source_pages"], [2])
        self.assertEqual(result["demos"][0]["related_step_ids"], ["s2"])
        self.assertEqual(lab.clean_interactive_lab(raw, [], None, APP["valid_source_pages"])["demos"][0]["source_pages"], [])

    def test_malformed_demos_drop_independently(self):
        mutations = [
            lambda d: d.update(title=""), lambda d: d.update(id="__bad"),
            lambda d: d["x"].update(min=2, max=2), lambda d: d["x"].update(points=100000),
            lambda d: d["x"].update(points=True), lambda d: d["x"].update(max=float('inf')),
            lambda d: d["parameters"][0].update(id="t"), lambda d: d["parameters"][1].update(id="V_m"),
            lambda d: d["parameters"][0].update(default=100), lambda d: d["parameters"][0].update(step=0),
            lambda d: d["parameters"][0].update(step=1e-10), lambda d: d["parameters"][0].update(min=False),
            lambda d: d["parameters"].extend(d["parameters"]),
            lambda d: d["series"][0].update(expression='open("file")'),
            lambda d: d["series"].append(copy.deepcopy(d["series"][0])),
            lambda d: d["series"][0].update(expression="undeclared*t"),
            lambda d: d["series"][0].update(expression="sqrt(-1)"),
            lambda d: d["derived_metrics"][0].update(expression="t*2"),
            lambda d: d.update(try_this="wrong type"), lambda d: d.update(parameters=[None]),
            lambda d: d.update(x=None), lambda d: d.update(series=[None]),
        ]
        for mutate in mutations:
            raw = lab_fixture(two=True)
            mutate(raw["demos"][0])
            with self.subTest(mutation=mutate):
                result = self.clean(raw)
                self.assertTrue(result["suitable"])
                self.assertEqual(result["rejected"], 1)
                self.assertEqual(result["demos"][0]["id"], "damped_wave")
        raw = lab_fixture()
        raw["demos"] *= 2
        self.assertEqual(len(self.clean(raw)["demos"]), 1)
        for raw in [None, {}, {"suitable": False, "demos": [sinusoid_demo()]}, {"suitable": True, "demos": None}]:
            self.assertFalse(self.clean(raw)["suitable"])

    def test_sinusoid_amplitude_frequency_phase_period_and_fixed_baseline(self):
        demo = self.clean(lab_fixture())["demos"][0]
        defaults = lab.default_values(demo)
        x, curves = lab.compute_curves(demo, defaults)
        original = curves["wave"]
        amplitude = lab.compute_curves(demo, {**defaults, "V_m": 3})[1]["wave"]
        np.testing.assert_allclose(amplitude, original * 3)
        fast = lab.compute_curves(demo, {**defaults, "omega": 4})[1]["wave"]
        crossings = lambda y: np.count_nonzero(np.diff(np.signbit(y)))
        self.assertEqual(crossings(fast), 2 * crossings(original))
        shifted = lab.compute_curves(demo, {**defaults, "theta": 90})[1]["wave"]
        np.testing.assert_allclose(shifted, np.cos(2*x+math.pi/2))
        self.assertAlmostEqual(evaluate_expression(demo["derived_metrics"][0]["expression"], {**defaults, "omega": 4}), math.pi/2)
        chart = lab.build_lab_chart(demo, {**defaults, "V_m": 3}, True)
        np.testing.assert_allclose(chart.data[0].y, original)
        np.testing.assert_allclose(chart.data[1].y, amplitude)
        self.assertEqual(chart.data[0].line.dash, "dash")
        self.assertEqual(lab.default_values(demo), defaults)

    def test_material_spec_state_and_local_mapping(self):
        clean = self.clean(lab_fixture(two=True))
        state = lab.ensure_lab_state("m", clean)
        state["demos"]["wave_parameters"]["values"]["V_m"] = 4
        self.assertIs(lab.ensure_lab_state("m", clean), state)
        self.assertEqual(len(lab.related_demos(clean, ["s2"])), 2)
        self.assertEqual(lab.related_demos(clean, ["unknown"]), [])
        lab.select_demo(state, "damped_wave")
        self.assertEqual(state["selected_id"], "damped_wave")
        lab.select_demo(state, "missing")
        self.assertEqual(state["selected_id"], "damped_wave")
        self.state["guided_quiz_answers"] = {"q1": "a"}
        self.state["lab-widget-old"] = 4
        changed = copy.deepcopy(clean)
        changed["demos"][0]["parameters"][0]["default"] = 2
        fresh = lab.ensure_lab_state("m", changed)
        self.assertEqual(fresh["demos"]["wave_parameters"]["values"]["V_m"], 2)
        self.assertNotIn("lab-widget-old", self.state)
        self.assertEqual(lab.ensure_lab_state("new", clean)["demos"]["wave_parameters"]["values"]["V_m"], 1)
        self.assertEqual(self.state["guided_quiz_answers"], {"q1": "a"})

    def test_language_identity_and_context_use_analysis_not_selector(self):
        self.state["product_language"] = "en"
        self.analysis["analysis_language"] = "zh-TW"
        context = APP["build_explanation_context"]("key_concept", self.analysis["key_concepts"][0], self.analysis, source_fixture(), [1, 2])
        self.assertEqual(context["response_language"], "Traditional Chinese")
        self.assertIn("Incoming material enters", context["relevant_extracted_source_text"])
        review = APP["build_focused_review_context"](self.analysis, self.path, self.path["checkpoint_questions"][:1], {"q1": "b"}, source_fixture(), [1, 2])
        self.assertEqual(review["response_language"], "Traditional Chinese")
        self.assertNotEqual(APP["build_analysis_id"]("text", b"same", "zh-TW"), APP["build_analysis_id"]("text", b"same", "en"))
        self.assertEqual(set(i18n.UI_TEXT["en"]), set(i18n.UI_TEXT["zh-TW"]))


class Day15InteractionTests(unittest.TestCase):
    def setUp(self):
        self.client = MagicMock()
        self.client.responses.create.side_effect = AssertionError("Unexpected request during local interaction")
        for patcher in [patch("openai.OpenAI", return_value=self.client),
                        patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state)]:
            patcher.start()
            self.addCleanup(patcher.stop)

    def app(self, analysis=None, language="zh-TW"):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=25)
        if analysis is not None:
            at.session_state["analysis"] = analysis
            at.session_state["analysis_id"] = "lab-material"
            at.session_state["allowed_source_pages"] = [1, 2]
            at.session_state["source_context"] = source_fixture()
        if language:
            at.session_state["product_language"] = language
        at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
        at.run()
        self.assertFalse(at.exception)
        return at

    def click(self, at, label):
        next(button for button in at.button if button.label == label).click().run()
        self.assertFalse(at.exception)

    def test_default_language_switch_and_main_prompt(self):
        at = self.app(language=None)
        self.assertEqual(at.selectbox(key="product_language").value, "zh-TW")
        self.assertTrue(any(button.label == "開始理解" for button in at.button))
        at.text_area[0].set_value("v(t) = V_m cos(omega*t + theta)").run()
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(learning_fixture()))
        self.client.responses.create.side_effect = None
        self.click(at, "開始理解")
        call = self.client.responses.create.call_args.kwargs
        self.assertIn("Required output language: Traditional Chinese", call["instructions"])
        self.assertIn("interactive_lab", call["text"]["format"]["schema"]["required"])
        self.assertEqual(at.session_state["analysis_language"], "zh-TW")
        old_id = at.session_state["analysis_id"]
        at.selectbox(key="product_language").select("en").run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        self.assertEqual(at.session_state["analysis_id"], old_id)
        self.assertEqual(at.text_area[0].value, "v(t) = V_m cos(omega*t + theta)")
        self.assertTrue(any("next analysis" in item.value for item in at.info))
        self.click(at, "Visualize")
        self.assertIn("Required output language: English", self.client.responses.create.call_args.kwargs["instructions"])
        self.assertEqual(at.session_state["analysis_language"], "en")
        self.assertNotEqual(at.session_state["analysis_id"], old_id)

    def test_slider_reset_baseline_and_full_learning_state_preserved(self):
        at = self.app(learning_fixture())
        self.assertEqual(len(at.slider), 3)
        self.assertEqual(len(at.get("plotly_chart")), 1)
        at.selectbox(key="canvas-list-lab-material-concept_map").select("transform").run()
        at.session_state["guided_learning_started"] = True
        at.session_state["guided_learning_step_id"] = "s2"
        at.session_state["guided_quiz_answers"] = {"q1": "b"}
        at.session_state["guided_quiz_checked"] = {"q1": True}
        at.session_state["explanation_cache"] = {"sentinel": {"saved": True}}
        at.session_state["focused_review_cache"] = {"sentinel": focused_fixture()}
        at.session_state["adaptive_review_state"] = {"material_id": "lab-material", "focused_review": focused_fixture()}
        at.slider[0].set_value(3.0).run()
        at.slider[1].set_value(4.0).run()
        at.slider[2].set_value(90.0).run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["interactive_lab_state"]["demos"]["wave_parameters"]["values"], {"V_m": 3, "omega": 4, "theta": 90})
        self.assertTrue(any("1.5708" in metric.value for metric in at.metric))
        at.checkbox[0].uncheck().run()
        self.assertFalse(at.session_state["interactive_lab_state"]["demos"]["wave_parameters"]["compare"])
        self.click(at, "重設參數")
        self.assertEqual([slider.value for slider in at.slider], [1, 2, 0])
        self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "transform")
        self.assertEqual(at.session_state["guided_learning_step_id"], "s2")
        self.assertEqual(at.session_state["guided_quiz_answers"], {"q1": "b"})
        self.assertEqual(at.session_state["adaptive_review_state"]["focused_review"], focused_fixture())
        self.assertIn("sentinel", at.session_state["focused_review_cache"])
        self.assertIn("sentinel", at.session_state["explanation_cache"])
        at.selectbox(key="product_language").select("en").run()
        self.assertEqual([slider.value for slider in at.slider], [1, 2, 0])
        self.client.responses.create.assert_not_called()

    def test_lesson_inspector_review_links_select_real_demo(self):
        at = self.app(learning_fixture(two=True))
        self.click(at, "開始引導學習")
        self.click(at, "下一步")
        at.button(key="lab-open-guided-lab-material-damped_wave").click().run()
        self.assertEqual(at.session_state["interactive_lab_state"]["selected_id"], "damped_wave")
        self.assertEqual(len(at.slider), 4)
        lesson_button = next(button for button in at.button if "-lesson-s2" in str(button.key))
        lesson_button.click().run()
        self.assertEqual(at.session_state["guided_learning_step_id"], "s2")
        at.selectbox(key="canvas-list-lab-material-concept_map").select("transform").run()
        at.button(key="lab-open-inspector-transform-lab-material-wave_parameters").click().run()
        self.assertEqual(at.session_state["interactive_lab_state"]["selected_id"], "wave_parameters")
        self.click(at, "下一步")
        for i in range(3):
            at.radio[i].set_value("b" if i == 1 else "a").run()
            at.button(key=f"guided-quiz-check-lab-material-q{i+1}").click().run()
        at.button(key="lab-open-review-queue-lab-material-damped_wave").click().run()
        self.assertEqual(at.session_state["interactive_lab_state"]["selected_id"], "damped_wave")
        pattern = at.session_state["adaptive_review_state"]["pattern_key"]
        at.session_state["adaptive_review_state"]["focused_review"] = focused_fixture()
        at.session_state["focused_review_cache"][pattern] = focused_fixture()
        at.run()
        at.button(key="lab-open-focused-review-lab-material-wave_parameters").click().run()
        self.assertEqual(at.session_state["interactive_lab_state"]["selected_id"], "wave_parameters")
        self.assertFalse(at.exception)
        self.client.responses.create.assert_not_called()

    def test_source_original_and_explanation_review_language_stays_active(self):
        analysis = learning_fixture()
        analysis["analysis_language"] = "zh-TW"
        at = self.app(analysis, "en")
        at.selectbox(key="canvas-list-lab-material-concept_map").select("input").run()
        self.click(at, "View source")
        self.assertTrue(any("Incoming material enters" in item.value for item in at.text))
        explanation = {"plain_explanation": "保持繁體中文說明。", "why_it_matters": "連結概念。", "intuition_or_example": "", "source_note": "依據來源。"}
        self.client.responses.create.side_effect = lambda **kw: SimpleNamespace(output_text=json.dumps(explanation if kw["text"]["format"]["name"] == "visual_learning_explanation" else focused_fixture()))
        at.button(key="explain-lab-material:concept_map_node:input").click().run()
        self.assertEqual(json.loads(self.client.responses.create.call_args.kwargs["input"])["response_language"], "Traditional Chinese")
        at.button(key="explain-lab-material:concept_map_node:input").click().run()
        self.assertEqual(self.client.responses.create.call_count, 1)
        at.session_state["guided_learning_started"] = True
        at.session_state["guided_learning_step_id"] = "s3"
        at.session_state["guided_quiz_answers"] = {"q1": "a", "q2": "b", "q3": "a"}
        at.session_state["guided_quiz_checked"] = {"q1": True, "q2": True, "q3": True}
        at.run()
        self.click(at, "Build focused review")
        self.assertEqual(json.loads(self.client.responses.create.call_args.kwargs["input"])["response_language"], "Traditional Chinese")
        at.slider[0].set_value(2.0).run()
        self.assertEqual(self.client.responses.create.call_count, 2)

    def test_failures_stay_local_and_new_material_resets(self):
        analysis = learning_fixture()
        analysis["interactive_lab"]["demos"][0]["series"][0]["expression"] = "sqrt(V_m-1)"
        at = self.app(analysis)
        at.slider[0].set_value(.5).run()
        self.assertFalse(at.exception)
        self.assertTrue(any("無法產生有效" in item.value for item in at.info))
        self.assertTrue(any("引導學習" in item.value for item in at.markdown))
        with patch.object(lab, "build_lab_chart", side_effect=RuntimeError("simulated plot failure")):
            at.run()
        self.assertFalse(at.exception)
        self.assertTrue(any("無法顯示" in item.value for item in at.info))
        at.session_state["analysis"] = learning_fixture()
        at.session_state["analysis_id"] = "new-material"
        at.run()
        self.assertEqual(at.slider[0].value, 1)
        self.assertEqual(at.session_state["interactive_lab_state"]["material_id"], "new-material")
        at.session_state["analysis"]["interactive_lab"]["demos"][0]["series"][0]["expression"] = '__import__("os")'
        at.run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.slider), 0)
        self.assertTrue(any("部分實驗資料無效" in item.value for item in at.caption))
        at.session_state["analysis"]["interactive_lab"] = {"suitable": False, "reason": "", "demos": []}
        at.run()
        self.assertFalse(any(item.value == "互動實驗室" for item in at.subheader))
        self.assertTrue(any(item.value == "### 引導學習" for item in at.markdown))
        self.client.responses.create.assert_not_called()


if __name__ == "__main__":
    unittest.main()
