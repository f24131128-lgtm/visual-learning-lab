"""Post-run semantic review against frozen source examples, never production routing.

Mechanical probes alone cannot certify meaningful interaction. Numeric formulas
are compared with independently written source equations; captured process
semantics get explicit checks/counterexamples. Gold and raw results are preserved.
"""
import copy
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import day23_benchmark as bench
from learning_world import compiler, planner, process
from source_atlas.model import semantic_catalog
from safe_math import evaluate_expression


def raw(mid, stage):
    return json.loads((bench.HOME / "phase_b" / "declarations" / mid / (stage + ".json")).read_text(encoding="utf-8"))["raw"]


def normalized(mid):
    analysis, path, lab = bench.prepare_analysis(raw(mid, "analysis"))
    catalog = semantic_catalog(None, analysis)
    return planner.normalize(raw(mid, "planner"), catalog, [], compiler.capabilities(analysis, {}, lab)), lab


def apply(spec, state, transition, value=""):
    result = process.apply(spec, state, dict(identity=state["identity"], revision=state["revision"],
                                           transition_id=transition, value=value))
    assert result is not None
    return result[0]


def numeric_checks():
    checks = []
    # IDs below come from recorded data in this evaluation tool, never production.
    references = {
        "damped_motion": lambda x, v: {"displacement": v["amplitude"] * np.exp(-v["decay_rate"]*x) * np.cos(v["angular_frequency"]*x),
            "upper_envelope": v["amplitude"] * np.exp(-v["decay_rate"]*x),
            "lower_envelope": -v["amplitude"] * np.exp(-v["decay_rate"]*x)},
        "vector_resultant": lambda x, v: {"resultant_length": np.sqrt(x*x + v["b"]*v["b"])},
        "rc_charging": lambda x, v: {"capacitor_voltage": 5*(1-np.exp(-x/v["resistance"])),
            "charging_current": (5/v["resistance"])*np.exp(-x/v["resistance"])},
        "quadratic_shape": lambda x, v: {"parabola": v["scale_a"]*(x-v["shift_h"])**2+v["shift_k"]},
        "feedback_response": lambda x, v: {"output_y": v["K"]/(1+v["K"])*(1-np.exp(-(1+v["K"])*x))},
        "market_equilibrium": lambda x, v: {"demand_curve": v["demand_intercept"]-2*x, "supply_curve": 2+x},
    }
    for mid, reference in references.items():
        _, lab = normalized(mid)
        demo = lab["demos"][0]
        defaults = bench.default_values(demo)
        samples = [defaults]
        for p in demo["parameters"]:
            samples.extend({**defaults, p["id"]: value} for value in (p["min"], p["max"]))
        for values in samples:
            x, actual = bench.compute_curves(demo, values)
            expected = reference(x, values)
            assert set(expected) == set(actual)
            for key in actual:
                assert np.allclose(actual[key], expected[key], rtol=1e-10, atol=1e-10)
        checks.append(dict(material_id=mid, source_equation_array_checks=True,
                           parameter_samples=len(samples), scope="numeric consistency, not independent human fidelity/efficacy"))
    _, lab = normalized("market_equilibrium")
    demo = lab["demos"][0]
    for intercept, price, quantity in ((12, 10/3, 16/3), (15, 13/3, 19/3)):
        values = {"demand_intercept": intercept}
        metrics = {m["id"]: evaluate_expression(m["expression"], values) for m in demo["derived_metrics"]}
        assert abs(metrics["equilibrium_price"]-price) < 1e-10
        assert abs(metrics["equilibrium_quantity"]-quantity) < 1e-10
    return checks


def process_checks():
    plan, _ = normalized("future_lifecycle")
    spec = plan["process"]
    initial = process.initial(spec)
    assert process.enabled(spec, initial, "start_future")
    assert process.enabled(spec, initial, "cancel_future")
    running = apply(spec, initial, "start_future")
    assert not process.enabled(spec, running, "cancel_future")
    finished = apply(spec, running, "complete_future")
    assert not any(process.enabled(spec, finished, t["id"]) for t in spec["transitions"])
    cancelled = apply(spec, initial, "cancel_future")
    assert not any(process.enabled(spec, cancelled, t["id"]) for t in spec["transitions"])

    plan, _ = normalized("undo_history")
    spec = plan["process"]
    initial = process.initial(spec)
    added = apply(spec, initial, "append", "Move")
    removed = apply(spec, added, "undo")
    assert removed["last_removed"] == "Move"
    assert [i["text"] for i in removed["collections"]["history"]] == ["Draw", "Color"]
    assert process.reset(spec, removed)["collections"] == initial["collections"]

    plan, _ = normalized("cell_cycle")
    spec = plan["process"]
    state = process.initial(spec)
    for transition, expected in (("g1_to_s", "S"), ("s_to_g2", "G2"), ("g2_to_m", "M"), ("m_to_g1", "G1")):
        state = apply(spec, state, transition)
        assert state["states"]["cell_cycle_phase"] == expected
    return [dict(material_id=mid, source_supported_operations=True) for mid in ("future_lifecycle", "undo_history", "cell_cycle")]


def recursion_counterexample():
    plan, _ = normalized("recursive_calls")
    spec = plan["process"]
    state = process.initial(spec)
    # Button says "Request f(2) from f(3)" but the runtime accepts any text.
    wrong = apply(spec, state, "push_f2", "unrelated token")
    assert wrong["collections"]["stack_main"][-1]["text"] == "unrelated token"
    # It also permits "Return f(3)=6" before reaching a base case or unwinding.
    premature_return = process.enabled(spec, state, "pop_f3")
    assert premature_return
    return dict(material_id="recursive_calls", failure_category="R3", meaningful_runtime_pass=False,
        mechanical_runtime_pass=True, evidence=dict(named_call_accepts_unrelated_input=True,
        specific_result_return_enabled_before_base_case=True),
        reason="Buttons assert exact call/result semantics that generic unguarded list operations do not enforce. Valid DSL is insufficient for useful recursion teaching.")


def review():
    manifest = bench.read_manifest()
    numeric = numeric_checks()
    processes = process_checks()
    failed = recursion_counterexample()
    definition, _ = normalized("byte_definition")
    assert definition["family"] in ("static", "none") and not definition["features"]["interaction_value"]
    audited = json.loads((bench.HOME / "phase_b-audit" / "results.json").read_text(encoding="utf-8"))
    return dict(corpus_sha256=manifest["corpus_sha256"], gold_unchanged=True,
        review_kind="agent_source_equation_and_operation_review; human review pending",
        numeric=numeric, processes=processes, semantic_failure=failed,
        meaningful_runtime_pass=len(numeric) + len(processes) + 1,
        meaningful_runtime_fail=int(failed["meaningful_runtime_pass"] is False),
        unavailable_artifact=sum(r["compilation_pass"] is False for r in audited["rows"]),
        notes=["byte_definition uses an acceptable static conceptual view without forced interaction",
            "finite_sampling required scene rejected for duplicate focus labels; normal learning is retained",
            "damped_motion uses its valid numeric lab; optional spatial attempt is separately rejected for zero-span parameters",
            "damped beta=0 safely leaves the time-constant metric unavailable while curves remain defined",
            "broader generated pedagogical slider ranges and overall visual/source fidelity still need human review"])


if __name__ == "__main__":
    output = review()
    bench.save(bench.HOME / "semantic_review.json", output)
    print(json.dumps({k: output[k] for k in ("meaningful_runtime_pass", "meaningful_runtime_fail", "unavailable_artifact")}, indent=2))
