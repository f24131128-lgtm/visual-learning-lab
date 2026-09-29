"""Representative model output for offline acceptance tests, never app defaults."""

import math

from support import fixture


def sinusoid_demo():
    return {
        "id": "wave_parameters", "title": "振幅、角頻率與相位", "learning_goal": "一次調整一個參數，觀察波形如何改變。",
        "formula_display": r"v(t)=V_m\cos(\omega t+\theta\pi/180)",
        "x": {"id": "t", "label": "時間 t (s)", "min": 0, "max": 2 * math.pi, "points": 501},
        "parameters": [
            {"id": "V_m", "label": "振幅 V_m", "min": 0.5, "max": 5, "default": 1, "step": 0.1, "unit": "V"},
            {"id": "omega", "label": "角頻率 ω", "min": 0.5, "max": 8, "default": 2, "step": 0.5, "unit": "rad/s"},
            {"id": "theta", "label": "相位 θ", "min": -180, "max": 180, "default": 0, "step": 15, "unit": "°"},
        ],
        "series": [{"id": "wave", "label": "波形 v(t)", "expression": "V_m*cos(omega*t + theta*pi/180)"}],
        "derived_metrics": [{"id": "period", "label": "週期 T", "expression": "2*pi/omega", "unit": "s"}],
        "try_this": ["固定角頻率與相位，增加振幅，觀察垂直尺度。", "將角頻率加倍，觀察相同時間內的週期數。", "將相位從 0° 調到 90°，比較波峰的位置。"],
        "source_pages": [1, 2], "related_step_ids": ["s1", "s2", "s3"],
    }


def lab_fixture(two=False):
    demos = [sinusoid_demo()]
    if two:
        second = sinusoid_demo()
        second.update(id="damped_wave", title="阻尼與振盪", related_step_ids=["s2"])
        second["parameters"].append({"id": "a", "label": "衰減率 a", "min": 0, "max": 2, "default": 0.2, "step": 0.1, "unit": "1/s"})
        second["series"][0]["expression"] = "exp(-a*t)*V_m*cos(omega*t + theta*pi/180)"
        second["formula_display"] = r"v(t)=e^{-at}V_m\cos(\omega t+\theta\pi/180)"
        demos.append(second)
    return {"suitable": True, "reason": "教材中的關係適合透過參數變化觀察。", "demos": demos}


def learning_fixture(two=False):
    analysis = fixture()
    analysis["interactive_lab"] = lab_fixture(two)
    analysis["quick_summary"] = "正弦波的振幅決定垂直尺度，角頻率決定振盪速度，相位決定水平對齊。"
    labels = ["振幅與垂直尺度", "角頻率與週期", "相位與水平對齊"]
    for node, concept, step, label in zip(analysis["concept_map"]["nodes"], analysis["key_concepts"], analysis["learning_path"]["steps"], labels):
        node["label"] = label
        concept.update(concept=label, explanation="用數學關係理解波形的變化。")
        step.update(title=label, learning_goal="觀察這個參數如何影響波形。", explanation="固定其他參數，調整目前的參數，並與預設波形比較。", connection_to_previous="從上一個參數的影響繼續探索。")
    analysis["learning_path"].update(title="一步步理解波形", reason="依序觀察三個參數的影響。")
    analysis["concept_map"]["edges"][0]["label"] = "共同決定波形"
    analysis["concept_map"]["edges"][1]["label"] = "搭配觀察"
    analysis["primary_visualization"]["reason"] = "以概念圖連結參數意義，再用互動實驗觀察變化。"
    for index, question in enumerate(analysis["learning_path"]["checkpoint_questions"]):
        question["question"] = f"哪個敘述符合{labels[index]}？"
        question["options"] = [{"id": letter, "text": text} for letter, text in zip("abcd", ["符合教材中的參數關係", "所有參數都只改變振幅", "參數不影響波形", "每次調整都改變原始資料"])]
        question["explanation"] = "應根據公式區分各參數的作用。"
    analysis["visual_evidence"][0].update(type="formula", description="頁面呈現波形公式與各參數。", learning_value="連結公式中的參數與可觀察的波形。")
    analysis["relationships"][0].update(source="角頻率", relation="決定", target="週期")
    return analysis
