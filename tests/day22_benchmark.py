"""Representation Suitability Benchmark: deterministic contracts, not live AI accuracy."""
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/"tests")]
import streamlit as st
from day22_fixtures import cases
from learning_world import compiler, process, planner
from workspace.state import get_workspace_state, get_workspace_focus, set_workspace_focus
from scene.world.state import new_state, apply_patch
from scene.world.engine import snapshot
from scene.probability import probability, inclusion_exclusion, monte_carlo
from analogy_fixtures import spec as analogy_raw
from analogy.validator import normalize as normalize_analogy
from analogy.state import parameter_registry, ensure, identity, save, set_parameter, values
from analogy.engine import project


def benchmark():
    rows = []
    for c in cases():
        caps = compiler.capabilities({}, dict(scene=c["scene"]), {})
        store = compiler.ensure({}, c["name"])
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(c["raw"]))
        source = dict(kind="text", source_text="Synthetic acceptance source; runtime equations and references are deterministic test declarations.")
        key = compiler.identity(c["name"], "en", source, c["catalog"], caps, None)
        data = compiler.context(dict(analysis_language="en"), source, c["catalog"], [1, 2], caps, c["raw"]["focus_ids"][0])
        spec = compiler.build(store, key, client, "offline", data, c["catalog"], [1, 2], caps)
        assert spec and spec["family"] == c["family"]
        compiled_calls = client.responses.create.call_count
        wrapper = dict(material_id=c["name"], scene=c["scene"])
        if c["scene"] and c["scene"]["domain"] == "spatial_dynamics": wrapper["world"] = new_state(c["scene"])
        with patch.object(st, "session_state", {}):
            ws = get_workspace_state(c["name"])
            focus = spec["focus_ids"][0]
            assert set_workspace_focus(ws, focus, c["catalog"], wrapper)
            assert get_workspace_focus(ws, wrapper) == focus
            observed = "No forced interaction"
            if c["family"] == "process":
                p = spec["process"]; state = process.initial(p)
                for t, val in (("act_insert", "C"), ("act_remove", "")):
                    state, focus = process.apply(p, state, dict(identity=state["identity"], revision=state["revision"], transition_id=t, value=val))
                    assert set_workspace_focus(ws, focus, c["catalog"], wrapper)
                assert state["last_removed"] == "A"
                assert get_workspace_focus(ws, wrapper) == "remove"
                observed = "A,B + C → remove A → B,C; canonical focus remove"
            elif c["family"] == "dynamic":
                scene = c["scene"]
                assert apply_patch(scene, wrapper["world"], dict(op="set_parameter", target_id="phase", value=math.pi/2))
                data = snapshot(scene, wrapper["world"])["values"]
                assert abs(data["wave"]-1) < 1e-10 and abs(data["horizontal"]) < 1e-10
                observed = "phase π/2 → wave 1, horizontal 0 via existing DAG"
            elif c["family"] == "spatial":
                scene = c["scene"]; before = snapshot(scene, wrapper["world"])["values"]
                assert apply_patch(scene, wrapper["world"], dict(op="set_time", target_id="time", value=.1))
                after = snapshot(scene, wrapper["world"])["values"]
                assert before != after
                observed = "existing world time patch changes validated trajectory projection"
            elif c["family"] == "analogy":
                registry = parameter_registry(wrapper, {}, {}, c["catalog"])
                analogy = normalize_analogy(analogy_raw("electricity"), c["catalog"], registry, [1], "voltage")
                astore = ensure({}, c["name"], "en", "sig"); akey = identity(c["name"], "en", "sig", "voltage"); save(astore, akey, analogy)
                set_parameter(astore, analogy, "level", 10., registry, wrapper, {})
                set_parameter(astore, analogy, "tightness", 5., registry, wrapper, {})
                output = project(analogy, values(astore, analogy, registry, wrapper, {}))
                value = next(o for o in output["objects"] if o["id"] == "flow_meter")["data"]["value"][0]
                assert abs(value-2) < 1e-10
                assert snapshot(c["scene"], wrapper["world"])["values"]["current"] == 2
                observed = "V=10,R=5 → formal current and analogy flow both 2"
            elif c["family"] == "structural":
                scene = c["scene"]
                assert float(probability(scene, scene["event_sets"]["E"])) == .5
                result = inclusion_exclusion(scene, "E", "F")
                monte_carlo(scene, scene["event_sets"]["E"], 100, seed=17)
                observed = "exact P(E)=1/2; existing inclusion–exclusion and seeded sampling"
            assert client.responses.create.call_count == compiled_calls
            rows.append(dict(case=c["name"], semantic_characteristics=[k for k, v in spec["features"].items() if v],
                expected_family=c["family"], planner_result=spec["family"], runtime=c["runtime"], compile_success=True,
                interaction_observed=observed, local_interaction_available=c["family"] != "none",
                source_grounding_available=bool(source["source_text"] and all(i in c["catalog"] for i in spec["focus_ids"])),
                source_grounding="validated synthetic formal page links; not live grounding accuracy",
                shared_focus_available=get_workspace_focus(ws, wrapper) in c["catalog"],
                shared_focus_observed=get_workspace_focus(ws, wrapper),
                graceful_fallback="existing formal view; planner unsupported-capability tests",
                fallback_family_without_specialized_capabilities=planner.choose(spec["features"], c["raw"]["preferred"], {}, spec["process"]),
                mock_compile_calls=compiled_calls, paid_api_calls_after_compilation=client.responses.create.call_count-compiled_calls))
    return dict(kind="Representation Suitability Benchmark", corpus="six synthetic deterministic cases", live_model_accuracy_test=False, cases=rows)


if __name__ == "__main__":
    output = ROOT/"docs"/"day22-representation-benchmark.json"
    output.write_text(json.dumps(benchmark(), indent=2, ensure_ascii=False), encoding="utf-8")
    print(str(output))
