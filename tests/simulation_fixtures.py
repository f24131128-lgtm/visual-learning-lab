"""Source-equivalent acceptance examples. These are never application defaults."""

import math

from lab_fixtures import lab_fixture, learning_fixture


def point(object_id, x, y, z=None, panel="scene", label=None):
    return {"type": "moving_point", "id": object_id, "label": label or object_id, "panel": panel,
            "x_expression": x, "y_expression": y, "z_expression": z}


def trail(object_id, target, panel="scene"):
    return {"type": "trail", "id": object_id, "label": "已走過的軌跡", "panel": panel, "object_id": target}


def marker(curve_id):
    return {"type": "moving_marker_on_curve", "id": "graph_marker", "label": "同一時間的波形",
            "panel": "graph", "curve_id": curve_id, "x_expression": "time", "y_expression": None, "z_expression": None}


def axes(x_min, x_max, y_min, y_max):
    return {"x_label": "水平位置 (m)", "y_label": "高度 (m)", "x_min": x_min, "x_max": x_max, "y_min": y_min, "y_max": y_max}


def base_scene(demo, end, objects):
    return {
        "suitable": True, "reason": "依據來源模型觀察隨時間的變化。", "title": "觀察模型的動態",
        "learning_goal": "共用實驗參數，一次調整一個值並比較運動。",
        "parameter_ids": [p["id"] for p in demo["parameters"]],
        "time": {"id": "time", "label": "時間", "min": 0, "max": end, "frames": 121, "unit": "s", "max_expression": None},
        "scene": {"dimension": "2d", **axes(-5, 5, -5, 5)}, "graph": None, "stop_when": None,
        "objects": objects, "static_series": [],
        "metrics": [{"id": "elapsed", "label": "時間", "expression": "time", "unit": "s"}],
        "observation_prompts": ["固定其他參數，觀察改變一個參數的影響。", "重設參數，比較與預設情況的差異。"],
        "related_step_ids": demo["related_step_ids"], "source_pages": demo["source_pages"],
    }


def projectile():
    demo = {
        "id": "flight_model", "title": "拋體軌跡", "learning_goal": "比較初速、角度與重力對拋體的影響。",
        "formula_display": r"y(x)=x\tan(\theta\pi/180)-\frac{g x^2}{2v_0^2\cos^2(\theta\pi/180)}",
        "x": {"id": "x", "label": "水平位置 x (m)", "min": 0, "max": 100, "points": 401},
        "parameters": [
            {"id": "v0", "label": "初速 v₀", "unit": "m/s", "min": 5, "max": 30, "default": 25, "step": 1},
            {"id": "theta", "label": "發射角度 θ", "unit": "°", "min": 10, "max": 80, "default": 45, "step": 5},
            {"id": "g", "label": "重力加速度 g", "unit": "m/s²", "min": 9.8, "max": 15, "default": 9.8, "step": .1},
        ],
        "series": [{"id": "trajectory", "label": "高度 y(x)", "expression": "x*tan(theta*pi/180)-g*x**2/(2*v0**2*cos(theta*pi/180)**2)"}],
        "derived_metrics": [{"id": "range", "label": "射程", "expression": "v0**2*sin(2*theta*pi/180)/g", "unit": "m"}],
        "try_this": ["保持角度與重力不變，增加初速。", "固定初速，比較不同發射角度。"],
        "source_pages": [1, 2], "related_step_ids": ["s1", "s2", "s3"],
    }
    y = "v0*sin(theta*pi/180)*time-0.5*g*time**2"
    spec = base_scene(demo, 6, [point("body", "v0*cos(theta*pi/180)*time", y, label="拋體"),
                                trail("flight_trail", "body"),
                                {"id": "ground", "label": "地面", "type": "reference_line", "panel": "scene", "axis": "y", "value_expression": "0"}])
    spec["title"] = "拋體的飛行與落地"
    spec["scene"] = {"dimension": "2d", **axes(0, 100, 0, 50)}
    spec["time"]["max_expression"] = "2*v0*sin(theta*pi/180)/g"
    spec["stop_when"] = {"expression": y, "comparison": "below", "threshold": 0}
    spec["metrics"] += [
        {"id": "horizontal", "label": "水平位置", "expression": "v0*cos(theta*pi/180)*time", "unit": "m"},
        {"id": "height", "label": "高度", "expression": y, "unit": "m"},
        {"id": "velocity", "label": "垂直速度", "expression": "v0*sin(theta*pi/180)-g*time", "unit": "m/s"},
    ]
    return demo, spec


def damped():
    demo = lab_fixture(two=True)["demos"][1]
    demo.update(learning_goal="調整位移振幅、阻尼、角頻率與相位，觀察位移隨時間的變化。",
                formula_display=r"x(t)=e^{-at}V_m\cos(\omega t+\theta\pi/180)")
    demo["parameters"][0].update(label="位移振幅 V_m", unit="m")
    demo["series"][0]["label"] = "位移 x(t)"
    expression = "V_m*exp(-a*time)*cos(omega*time+theta*pi/180)"
    spec = base_scene(demo, 2 * math.pi, [point("body", expression, "0", label="振動物體"),
                                        {"type": "reference_line", "id": "equilibrium", "label": "平衡位置", "panel": "scene", "axis": "x", "value_expression": "0"},
                                        marker("wave")])
    spec.update(title="觀察阻尼振盪", scene={"dimension": "2d", **axes(-5, 5, -1, 1),
                                         "x_label": "位移 (m)", "y_label": "示意位置"},
                graph={**axes(0, 2 * math.pi, -5, 5), "x_label": "時間 (s)", "y_label": "位移 (m)"})
    spec["metrics"] += [{"id": "displacement", "label": "位移", "expression": expression, "unit": "m"},
                        {"id": "envelope", "label": "包絡振幅", "expression": "V_m*exp(-a*time)", "unit": "m"}]
    return demo, spec


def phasor():
    demo = lab_fixture()["demos"][0]
    spec = base_scene(demo, 2 * math.pi, [
        {"type": "vector", "id": "rotator", "label": "旋轉向量", "panel": "scene", "x0_expression": "0", "y0_expression": "0", "z0_expression": None,
         "x1_expression": "V_m*cos(omega*time+theta*pi/180)", "y1_expression": "V_m*sin(omega*time+theta*pi/180)", "z1_expression": None},
        {"type": "circle", "id": "reference_circle", "label": "固定半徑", "panel": "scene", "x_expression": "0", "y_expression": "0", "radius_expression": "V_m"},
        marker("wave"), trail("orbit", "rotator"),
    ])
    spec.update(title="相量與餘弦投影", scene={"dimension": "2d", **axes(-5, 5, -5, 5),
                                           "x_label": "實部 (V)", "y_label": "虛部 (V)"},
                graph={**axes(0, 2 * math.pi, -5, 5), "x_label": "時間 (s)", "y_label": "電壓 (V)"})
    spec["metrics"] += [{"id": "projection", "label": "水平投影", "expression": "V_m*cos(omega*time+theta*pi/180)", "unit": "V"},
                        {"id": "angle", "label": "相位角", "expression": "omega*time+theta*pi/180", "unit": "rad"}]
    return demo, spec


def helix():
    demo = lab_fixture()["demos"][0]
    demo.update(id="helix_radius", title="螺旋半徑", related_step_ids=["s2"])
    demo["parameters"] = [{"id": "radius", "label": "半徑", "unit": "m", "min": .5, "max": 3, "default": 1, "step": .1}]
    demo["series"][0]["expression"] = "radius*cos(t)"
    demo["derived_metrics"] = []
    demo["formula_display"] = r"(x,y,z)=(r\cos(t),r\sin(t),t)"
    spec = base_scene(demo, 2 * math.pi, [point("body", "radius*cos(time)", "radius*sin(time)", "time", label="螺旋上的點"), trail("helix_path", "body")])
    spec.update(title="三維螺旋軌跡", scene={"dimension": "3d", **axes(-3, 3, -3, 3), "z_label": "z", "z_min": 0, "z_max": 2 * math.pi})
    return demo, spec


def simulation_analysis(kind="projectile"):
    demo, spec = {"projectile": projectile, "damped": damped, "phasor": phasor, "helix": helix}[kind]()
    analysis = learning_fixture()
    analysis["analysis_language"] = "zh-TW"
    analysis["interactive_lab"] = {"suitable": True, "reason": "公式適合調整參數觀察。", "demos": [demo]}
    analysis["quick_summary"] = demo["learning_goal"]
    labels = {
        "projectile": ["初速與發射角度", "重力與垂直運動", "飛行時間與落地"],
        "damped": ["位移與振幅", "阻尼與包絡", "角頻率與相位"],
        "phasor": ["振幅與半徑", "角頻率與旋轉", "相位與餘弦投影"],
        "helix": ["平面圓周運動", "高度與螺旋", "半徑與三維軌跡"],
    }[kind]
    for node, concept, step, label in zip(analysis["concept_map"]["nodes"], analysis["key_concepts"], analysis["learning_path"]["steps"], labels):
        node["label"] = label
        concept.update(concept=label, explanation=demo["learning_goal"])
        step.update(title=label, learning_goal=demo["learning_goal"], explanation="固定其他參數，觀察來源模型中的這個關係。")
    analysis["learning_path"]["title"] = demo["title"]
    analysis["relationships"][0].update(source=labels[0], relation="共同影響", target=labels[1])
    return analysis, spec


def unsuitable():
    return {"suitable": False, "reason": "這個模型沒有適合的動態學習結構。", "title": "", "learning_goal": "", "parameter_ids": [],
            "time": None, "scene": None, "graph": None, "stop_when": None, "objects": [], "static_series": [], "metrics": [],
            "observation_prompts": [], "related_step_ids": [], "source_pages": []}
