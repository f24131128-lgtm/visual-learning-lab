"""Phase C deterministic regression shapes, authored BEFORE production changes.

Not new prospective materials and not replacements for frozen Phase A/B gold.
Resolved numeric call examples are declarations; no user/program code is executed.
"""
import copy
from scene_fixtures import two_toss_scene
from world_fixtures import base, representation


def catalog():
    return {i: dict(label=label, pages=[1], kind="concept_map", equation="", representations=[])
            for i, label in (("call", "Nested call"), ("base", "Base result"), ("return_value", "Return to caller"))}


def execution(nested=False):
    def call(identifier, label, value, child=None, expression="1"):
        return dict(id=identifier, semantic_id="call" if child else "base", label=label,
            arguments=[dict(id="n", label="Argument", value=value)],
            children=[] if child is None else [dict(call_id=child, result_id="answer", result_label="Child result",
                semantic_id="call", label="Call child")], result_expression=expression,
            return_semantic_id="return_value")
    if nested:
        calls = [call("outer", "Package result", 4, "inner", "n+answer"),
                 call("inner", "Double input", 3, expression="2*n")]
    else:
        calls = [call("c3", "f(3)", 3, "c2", "n*answer"), call("c2", "f(2)", 2, "c1", "n*answer"),
                 call("c1", "f(1)", 1, "c0", "n*answer"), call("c0", "f(0)", 0)]
    return dict(root_id=calls[0]["id"], calls=calls, annotations=[])


def equal_labels():
    raw = two_toss_scene()
    for event in raw["events"]: event["label"] = "Choice"
    raw["focus_targets"][1].update(expression="F", label="Choice", source_pages=[1])
    raw["focus_targets"][0].update(label="Choice", source_pages=[2])
    return raw


def fixed_world():
    raw = base("Fixed scale with moving position", [("scale", "Fixed scale", "m", 2., 2., 2., 0.)],
        [("qx", "Horizontal position", "m", "scale*time"), ("qy", "Vertical position", "m", "0")])
    raw["time"].update(max=2., frames=20)
    raw["parameters"][0]["range_source"] = "source"
    representation(raw, "objects", "point", "Moving point", "qx", ["qx", "qy"], "point")
    representation(raw, "series", "wave", "Position over time", "qx", ["qx"])
    representation(raw, "metrics", "distance", "Current position", "qx", ["qx"])
    return raw


def malformed_shapes():
    early = dict(operation="return", destination="", frame="root")
    wrong = dict(operation="return", destination="unrelated", frame="child")
    cyclic = execution(); cyclic["calls"][-1]["children"] = copy.deepcopy(cyclic["calls"][0]["children"])
    return dict(early_return=early, wrong_caller=wrong, cycle=cyclic,
        fixed_domain=dict(min=2., max=2., default=2., step=0.),
        invalid_fixed=dict(min=2., max=2., default=3., step=0.))
