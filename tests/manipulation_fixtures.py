"""Day24 deterministic acceptance fixtures; never imported by production."""
import math

from interactive_lab import _clean_demo
from scene.world.validator import normalize_world
from world_fixtures import complete_projectile_world
from analogy_fixtures import formal
from support import fixture

SOURCES={
 "phase":"Phase exploration: theta = time + phase; horizontal = cos(theta), signal = sin(theta). The source baseline is phase = 0 rad. Explore phase from -pi to pi. The geometric pointer endpoint is (cos(theta), sin(theta)).",
 "projectile":"Ideal same-height launch. The source baseline is speed = 20 m/s, angle = 45 degrees, gravity = 9.8 m/s^2. x = speed*cos(angle)*time; y = speed*sin(angle)*time - gravity*time^2/2. Flight ends at 2*speed*sin(angle)/gravity. Explore speed from 5 to 100 m/s, angle from 5 to 85 degrees and gravity from 1 to 20 m/s^2. The launch vector is (speed*cos(angle), speed*sin(angle)).",
 "math":"A general affine relation y = gain*x + offset. Source baseline: gain = 1, offset = 0. Explore gain from -3 to 3 and offset from -4 to 4 for -2 <= x <= 2. The value at x=0 is the offset; at x=2 it is 2*gain+offset. Moving these anchors changes the same formal parameters and equation.",
}


def systems():
    a=formal("phase")[0]
    b=normalize_world(complete_projectile_world(),[1])
    return a,b


def math_demo():
    raw=dict(id="affine_demo",title="仿射關係與錨點",learning_goal="拖曳錨點並觀察同一個正式關係",formula_display="y = a x + b",
        x=dict(id="coordinate",label="x",min=-2.,max=2.,points=100),
        parameters=[dict(id="gain",label="係數 a",min=-3.,max=3.,default=1.,step=.05,unit=""),
                    dict(id="offset",label="常數 b",min=-4.,max=4.,default=0.,step=.05,unit="")],
        series=[dict(id="relation_curve",label="y = ax + b",expression="gain*coordinate+offset")],
        derived_metrics=[dict(id="coefficient_value",label="係數 a",expression="gain",unit=""),
                         dict(id="constant_value",label="常數 b",expression="offset",unit="")],
        try_this=[],source_pages=[1],related_step_ids=["s1"])
    return _clean_demo(raw,[1],{"s1"},lambda pages,allowed:[p for p in pages if p in allowed])


def analysis(kind):
    value=fixture()
    value.update(analysis_language="zh-TW",quick_summary=SOURCES[kind])
    value["learning_scene_candidate"]=dict(suitable=kind!="math",domain="spatial_dynamics" if kind!="math" else "none",reason="Deterministic source-supported acceptance declaration")
    if kind=="math":
        value["interactive_lab"]=dict(suitable=True,reason="Explicit source relation",demos=[math_demo()])
        value["concept_map"]["nodes"]=[dict(id="formal_relation",label="仿射關係",source_pages=[1],role="central"),
            dict(id="source_baseline",label="來源初始值",source_pages=[1],role="supporting")]
        value["concept_map"]["edges"]=[dict(source="source_baseline",target="formal_relation",label="提供初始參數")]
        value["learning_path"]["steps"][0]["visual_refs"]=[dict(type="concept_map_node",id="formal_relation")]
    return value
