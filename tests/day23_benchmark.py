"""Small prospective runner; ordinary tests/replay never make paid requests.

--live is explicit, bounded, resumable and persists every model declaration
before validation. Gold is never included in model context. Static AST reading
extracts the checked-in app prompt, not generated code. Results distinguish
model proposal, adapted family, artifact, mechanical interaction and grounding.
"""
import argparse
import ast
import copy
import hashlib
import json
import logging
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
from day23_freeze import digest
from support import load_app_helpers
from learning_world import compiler, process
from source_atlas.model import semantic_catalog
from workspace.state import focusable, set_workspace_focus, get_workspace_focus, open_workspace
from interactive_lab import clean_interactive_lab, compute_curves, default_values, LAB_INSTRUCTIONS
from i18n import output_language_instruction
from scene.compiler import build_scene_context, request_scene
from scene.compiler import normalize_scene
from scene.world.state import new_state, apply_patch
from scene.world.engine import snapshot, frames
from scene.probability import probability, monte_carlo
from analogy import compiler as analogy_compiler
from analogy.state import parameter_registry, identity as analogy_identity, ensure as analogy_ensure
from analogy.engine import project

HOME = ROOT / "docs" / "day23"
PRODUCTION = [ROOT / "app.py", ROOT / "interactive_lab.py", ROOT / "workspace/state.py"]
PRODUCTION += sorted(p for folder in ("learning_world", "scene", "analogy", "source_atlas", "document_intelligence")
                     for p in (ROOT / folder).rglob("*.py"))
HELPERS = None


def read_manifest(path=HOME / "phase_a_manifest.json"):
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if digest(manifest["payload"]) != manifest["corpus_sha256"]:
        raise ValueError("Frozen manifest digest changed")
    for case in manifest["payload"]["materials"]:
        if hashlib.sha256(case["text"].encode()).hexdigest() != case["text_sha256"]:
            raise ValueError("Material digest changed")
        file = HOME / "materials" / (case["material_id"] + ".txt")
        if file.read_text(encoding="utf-8").rstrip("\n") != case["text"]:
            raise ValueError("Material file changed")
    return manifest


def production_fingerprint():
    return digest({str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in PRODUCTION})


def analysis_prompt():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8-sig"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            value = node.value.value
            if value.startswith("You are the learning-content analyst"):
                return value + LAB_INSTRUCTIONS + "\n" + output_language_instruction("en")
    raise ValueError("Production analysis prompt unavailable")


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    # OneDrive/Windows may briefly lock a just-replaced JSON file. Retry only
    # the local atomic replace; never retry a model request or delete evidence.
    for attempt in range(8):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt == 7:
                raise
            time.sleep(0.1 * (attempt + 1))


def safe_error(error):
    # No SDK messages, keys, headers, request bodies or source excerpts.
    result = dict(type=type(error).__name__)
    if type(getattr(error, "status_code", None)) is int:
        result["http_status"] = error.status_code
    return result


class Responses:
    def __init__(self, directory, mode, model, budget, replay_directory=None, live_client=None):
        self.directory, self.mode, self.model = directory, mode, model
        self.budget, self.replay_directory, self.live_client = budget, replay_directory, live_client
        self.stage = None
        self.responses = self
        self.calls = 0
        self.local_start = None
        self.missing_recording = None

    def create(self, **kwargs):
        if self.local_start is not None:
            raise AssertionError("Model request during local interaction")
        path = self.directory / (self.stage + ".json")
        origin = path if path.exists() else (self.replay_directory / path.name if self.replay_directory else None)
        if origin and origin.exists():
            recorded = json.loads(origin.read_text(encoding="utf-8"))
            if recorded.get("error"):
                raise RuntimeError("Recorded request failed")
            if not path.exists():
                save(path, {**recorded, "replayed_from": str(origin.relative_to(ROOT)), "paid_this_run": False})
            return SimpleNamespace(output_text=json.dumps(recorded["raw"], ensure_ascii=False),
                                   status=recorded.get("status", "completed"), output=[])
        if self.mode != "live":
            self.missing_recording = self.stage
            raise FileNotFoundError("No recorded declaration for this stage")
        if self.budget["remaining"] <= 0:
            raise RuntimeError("Explicit request budget exhausted")
        self.budget["remaining"] -= 1
        self.calls += 1
        # Persist attempt first; a crash/connection failure cannot hide requests.
        save(path, dict(attempted_at_utc=datetime.now(timezone.utc).isoformat(), stage=self.stage,
                        model=self.model, paid_this_run=True, error=dict(type="AttemptInProgress")))
        try:
            response = self.live_client.responses.create(**kwargs)
            raw = json.loads(response.output_text)
            usage = getattr(response, "usage", None)
            save(path, dict(stage=self.stage, model=self.model, paid_this_run=True,
                status=response.status, response_id=response.id, raw=raw,
                usage={k: getattr(usage, k, None) for k in ("input_tokens", "output_tokens", "total_tokens")}))
            return response
        except Exception as error:
            save(path, dict(stage=self.stage, model=self.model, paid_this_run=True, error=safe_error(error)))
            raise


def prepare_analysis(raw):
    global HELPERS
    if HELPERS is None:
        HELPERS = load_app_helpers()
    h = HELPERS
    analysis = copy.deepcopy(raw)
    analysis["analysis_language"] = "en"
    primary = h["clean_primary_visualization"](raw.get("primary_visualization"))
    analysis["primary_visualization"] = primary
    for key in ("concept_map", "visual_flow", "comparison"):
        analysis[key] = h["clean_" + key](raw.get(key), [])
    visual = analysis.get({"flow": "visual_flow", "concept_map": "concept_map", "comparison": "comparison"}.get(primary["type"]))
    path = h["clean_learning_path"](raw.get("learning_path"), [], primary["type"], visual)
    lab = clean_interactive_lab(raw.get("interactive_lab"), [], path, h["valid_source_pages"])
    return analysis, path, lab


def probe_process(spec):
    state = process.initial(spec)
    original = copy.deepcopy(state)
    observations = []
    for _ in range(min(16, len(spec["transitions"]) * 2)):
        transition = next((t for t in spec["transitions"] if process.enabled(spec, state, t["id"]) and
                           t["id"] not in {o["transition_id"] for o in observations}), None)
        if not transition:
            break
        before = copy.deepcopy(state)
        result = process.apply(spec, state, dict(identity=state["identity"], revision=state["revision"],
                                                 transition_id=transition["id"], value="Probe item"))
        assert result is not None
        state, focus = result
        assert focus == transition["semantic_id"]
        target, operation = transition["target_id"], transition["operation"]
        if operation == "set_state":
            assert state["states"][target] == transition["to_state"]
        else:
            old = [i["text"] for i in before["collections"][target]]
            actual = [i["text"] for i in state["collections"][target]]
            expected = old + ["Probe item"] if operation == "append" else ["Probe item"] + old if operation == "prepend" else old[1:] if operation == "remove_first" else old[:-1]
            assert actual == expected
        assert process.apply(spec, state, dict(identity=before["identity"], revision=before["revision"],
            transition_id=transition["id"], value="Probe item")) is None
        observations.append(dict(transition_id=transition["id"], operation=operation, semantic_id=focus))
    assert observations, "No enabled local transition"
    restored = process.reset(spec, state)
    assert restored["collections"] == original["collections"] and restored["states"] == original["states"]
    return dict(operations=observations, reset=True, stale_event_rejected=True)


def probe_lab(lab):
    assert lab["demos"], "No numeric artifact"
    results = []
    for demo in lab["demos"]:
        values = default_values(demo)
        _, before = compute_curves(demo, values)
        changed = []
        for p in demo["parameters"]:
            for value in (p["min"], p["max"]):
                _, after = compute_curves(demo, {**values, p["id"]: value})
                assert all(np.all(np.isfinite(v)) for v in after.values())
                if any(not np.allclose(before[k], after[k]) for k in before):
                    changed.append(p["id"])
                    break
        assert changed, "Controls do not change curves"
        results.append(dict(demo_id=demo["id"], changed_parameters=changed,
                            lesson_refs=demo["related_step_ids"], source_pages=demo["source_pages"]))
    return dict(demos=results, numeric_comparison=True)


def probe_scene(scene):
    if scene["domain"] == "spatial_dynamics":
        state = new_state(scene)
        before = snapshot(scene, state)
        assert apply_patch(scene, state, dict(op="set_time", target_id="time", value=scene["time"]["max"] / 2))
        after = snapshot(scene, state)
        changed = before["values"] != after["values"]
        for p in scene["parameters"]:
            prior = snapshot(scene, state)["values"]
            for value in (p["min"], p["max"]):
                if apply_patch(scene, state, dict(op="set_parameter", target_id=p["id"], value=value)):
                    changed = changed or snapshot(scene, state)["values"] != prior
        assert changed, "Time and parameters do not change quantities"
        output = frames(scene, state["parameters"])
        return dict(shared_numeric_projection=True, bounded_frames=bool(output), time_and_parameters_local=True)
    events = scene["event_sets"]
    assert events
    left = next(iter(events.values()))
    right = list(events.values())[-1]
    exact = probability(scene, left | right)
    simulation = monte_carlo(scene, left, 100, seed=23)
    return dict(exact_union=float(exact), local_samples=100, simulation_available=bool(simulation))


def evaluate(case, client):
    global HELPERS
    if HELPERS is None:
        HELPERS = load_app_helpers()
    row = dict(material_id=case["material_id"], acceptable_families=case["acceptable_families"],
        proposal_family=None, selected_family=None, selection_pass=None, proposal_selection_pass=None,
        compilation_pass=None, runtime_pass=None, grounding_pass=None, safe_fallback=None,
        failure_category=None, failure_detail=None, interaction=None,
        post_compile_api_calls=None, source_fidelity="human_review_pending", visual_quality="human_review_pending")
    source = dict(kind="text", source_text=case["text"], page_texts={})
    analysis = None
    try:
        client.stage = "analysis"
        response = client.create(model=client.model, instructions=analysis_prompt(), input=case["text"],
            text={"format": dict(type="json_schema", name="visual_learning_analysis", strict=True, schema=HELPERS["ANALYSIS_SCHEMA"])})
        analysis, path, lab = prepare_analysis(json.loads(response.output_text))
        row["native_lab_demos"] = len(lab["demos"])
        row["rejected_lab_demos"] = lab["rejected"]
        catalog = semantic_catalog(None, analysis)
        catalog = {i: v for i, v in catalog.items() if focusable(i, catalog, {})}
        caps = compiler.capabilities(analysis, {}, lab)
        row["capabilities"] = caps
        store = compiler.ensure({}, case["material_id"])
        key = compiler.identity(case["material_id"], "en", source, catalog, caps, None)
        if not catalog:
            row.update(failure_category="P3", failure_detail="No canonical selectable catalog; production planner CTA is disabled")
            return row
        data = compiler.context(analysis, source, catalog, [], caps, None)
        client.stage = "planner"
        plan = compiler.build(store, key, client, client.model, data, catalog, [], caps)
        trace = store.get("diagnostics", {}).get(key, {})
        row["diagnostic"] = trace
        proposed = trace.get("generated", {}).get("planner_family")
        row.update(proposal_family=proposed, proposal_selection_pass=proposed in case["acceptable_families"] if proposed in
                   ("dynamic", "spatial", "structural", "process", "analogy", "static", "none") else None)
        if plan is None:
            if client.missing_recording:
                row.update(failure_category="OTHER", failure_detail="No saved Phase A planner declaration for this newly reachable case; needs explicit live evaluation")
                return row
            row.update(compilation_pass=False, failure_category="C2" if trace.get("code") in
                ("reference", "focus", "identity", "process_focus") else "C1", failure_detail=trace.get("code"))
            return row
        family = plan["family"]
        row.update(selected_family=family, selection_pass=family in case["acceptable_families"],
                   adapted=plan["adapted"], reason=plan["reason"], grounding_pass=
                   set(plan["focus_ids"]) <= set(data["catalog"]) and plan["source_pages"] == [])
        if not row["selection_pass"]:
            row.update(failure_category="C5" if row["proposal_selection_pass"] else "P1",
                       failure_detail="Capability adaptation" if row["proposal_selection_pass"] else "Inappropriate family")
        artifact = None
        if family == "process":
            artifact = plan["process"]
        elif family == "dynamic" and lab["demos"]:
            # The production numeric lab is ready without the optional spatial CTA.
            artifact = lab
        elif family in ("spatial", "structural") or (family == "dynamic" and caps.get("spatial")):
            client.stage = "scene"
            domain = "probability_sets" if family == "structural" else "spatial_dynamics"
            raw = request_scene(client, client.model, build_scene_context(analysis, source, [], domain))
            try:
                artifact = normalize_scene(raw, [])
                assert artifact["domain"] == domain
            except Exception as error:
                row.update(compilation_pass=False, failure_category=row["failure_category"] or "C1",
                    failure_detail=str(error)[:350])
                return row
        elif family == "dynamic":
            artifact = lab if lab["demos"] else None
        elif family == "analogy":
            registry = parameter_registry({}, lab, path, catalog)
            focus = plan["focus_ids"][0]
            astore = analogy_ensure({}, case["material_id"], "en", "day23")
            akey = analogy_identity(case["material_id"], "en", "day23", focus)
            client.stage = "analogy"
            artifact = analogy_compiler.build(astore, akey, client, client.model,
                analogy_compiler.context(analysis, source, catalog, registry, focus, []), catalog, registry, [])
            if artifact and not artifact["suitable"]:
                artifact = None
        else:
            # Existing validated structure / normal explanation are real fallbacks.
            artifact = analysis if family == "none" or caps["graph"] else None
        row["compilation_pass"] = artifact is not None
        if artifact is None:
            row.update(failure_category=row["failure_category"] or "C3", failure_detail="Selected artifact unavailable or unsuitable")
            return row
        client.local_start = client.calls
        if family == "process":
            row["interaction"] = probe_process(artifact)
        elif family == "dynamic" and lab["demos"]:
            row["interaction"] = probe_lab(lab)
        elif family in ("spatial", "structural") or (family == "dynamic" and caps.get("spatial")):
            row["interaction"] = probe_scene(artifact)
        elif family == "dynamic":
            row["interaction"] = probe_lab(lab)
        elif family == "analogy":
            values = {p["id"]: p["default"] for p in artifact["parameters"]}
            before = project(artifact, values)
            changed = False
            for p in artifact["parameters"]:
                for value in (p["min"], p["max"]):
                    changed |= project(artifact, {**values, p["id"]: value}) != before
            assert changed
            row["interaction"] = dict(local_numeric_projection=True)
        else:
            row["interaction"] = dict(static_or_none=True, dynamic_controls=False)
        # Shared focus and all Workspace views use actual production reducers.
        workspace = dict(material_id=case["material_id"], mode="explore", focus=None)
        wrapper = dict(material_id=case["material_id"], scene=None)
        with patch("streamlit.session_state", {}):
            assert set_workspace_focus(workspace, plan["focus_ids"][0], catalog, wrapper)
            focus = get_workspace_focus(workspace, wrapper)
            for mode in ("source", "practice", "learn", "explore"):
                assert open_workspace(workspace, mode)
                assert get_workspace_focus(workspace, wrapper) == focus
        row["runtime_pass"] = not (case["interaction_essential"] and family in ("static", "none"))
        row["post_compile_api_calls"] = client.calls - client.local_start
        if not row["runtime_pass"]:
            row.update(failure_category=row["failure_category"] or "R4", failure_detail="Essential interaction degraded to static/explanation")
    except Exception as error:
        row.update(failure_category=row["failure_category"] or ("R2" if client.local_start is not None else "OTHER"),
                   failure_detail=safe_error(error), runtime_pass=False if client.local_start is not None else None)
        if client.local_start is not None:
            row["post_compile_api_calls"] = client.calls - client.local_start
    finally:
        # Pure isolation assertion; product render safety is separately AppTested.
        row["safe_fallback"] = bool(analysis and analysis.get("quick_summary")) if row["failure_category"] else None
        row["fallback_evidence"] = "validated_analysis_retained; product UI requires separate AppTest" if row["safe_fallback"] else None
    return row


def summarize(rows):
    keys = ("proposal_selection_pass", "selection_pass", "compilation_pass", "runtime_pass", "grounding_pass", "safe_fallback")
    totals = dict(total=len(rows))
    for key in keys:
        totals[key] = {"pass": sum(r.get(key) is True for r in rows), "fail": sum(r.get(key) is False for r in rows),
                      "not_evaluated": sum(r.get(key) is None for r in rows)}
    totals["post_compile_api_calls"] = sum(r.get("post_compile_api_calls") or 0 for r in rows)
    totals["local_api_observed_cases"] = sum(r.get("post_compile_api_calls") is not None for r in rows)
    totals["failure_categories"] = {category: sum(r.get("failure_category") == category for r in rows)
        for category in sorted({r["failure_category"] for r in rows if r.get("failure_category")})}
    return totals


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=("a", "a-audit", "b", "b-audit", "b-replay", "b-replay-audit"))
    parser.add_argument("--live", action="store_true", help="Explicit paid model execution; no automatic retries")
    parser.add_argument("--max-calls", type=int, default=36)
    parser.add_argument("--case", action="append", default=[])
    parser.add_argument("--reuse-analysis", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.max_calls <= 60:
        parser.error("Request budget must be between 1 and 60")
    if args.phase == "a" and not args.live:
        parser.error("Phase A requires explicit --live; no synthetic planner substitution")
    manifest = read_manifest()
    directory = HOME / ("phase_" + args.phase)
    result_file = directory / "results.json"
    mode = "live" if args.live else "replay"
    fingerprint = production_fingerprint()
    if result_file.exists():
        result = json.loads(result_file.read_text(encoding="utf-8"))
        if result["production_sha256"] != fingerprint:
            raise SystemExit("Production changed within phase. Use a separately named comparison phase.")
        if result["corpus_sha256"] != manifest["corpus_sha256"]:
            raise SystemExit("Corpus changed")
    else:
        result = dict(phase=args.phase, execution=mode, started_at_utc=datetime.now(timezone.utc).isoformat(),
            base_commit=manifest["payload"]["base_commit"], production_sha256=fingerprint,
            corpus_sha256=manifest["corpus_sha256"], model="gpt-5.6-luna", gold_status=manifest["payload"]["gold_status"],
            rows=[], summary={}, evidence_scope="Mechanical interactions and canonical references; visual quality/source fidelity need human review")
        save(result_file, result)
    live_client = None
    if args.live:
        import os
        import tomllib
        from openai import OpenAI
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            key = tomllib.loads((ROOT / ".streamlit" / "secrets.toml").read_text(encoding="utf-8"))["OPENAI_API_KEY"]
        live_client = OpenAI(api_key=key, max_retries=0, timeout=120)
    logging.getLogger("streamlit").setLevel(logging.ERROR)
    previous_attempts = sum(json.loads(p.read_text(encoding="utf-8")).get("paid_this_run") is True
                            for p in directory.glob("declarations/*/*.json"))
    budget = dict(remaining=max(0, args.max_calls - previous_attempts))
    done = {r["material_id"] for r in result["rows"]}
    for case in manifest["payload"]["materials"]:
        mid = case["material_id"]
        if mid in done or (args.case and mid not in args.case):
            continue
        replay = HOME / ("phase_b" if args.phase == "b-audit" else "phase_a") / "declarations" / mid if mode == "replay" else None
        target = directory / "declarations" / mid
        if args.reuse_analysis:
            recorded = json.loads((HOME / "phase_a" / "declarations" / mid / "analysis.json").read_text(encoding="utf-8"))
            if not (target / "analysis.json").exists():
                save(target / "analysis.json", {**recorded, "paid_this_run": False, "replayed_from": "phase_a"})
        client = Responses(target, mode, result["model"], budget, replay, live_client)
        row = evaluate(case, client)
        result["rows"].append(row)
        result["summary"] = summarize(result["rows"])
        declarations = list(directory.glob("declarations/*/*.json"))
        records = [json.loads(p.read_text(encoding="utf-8")) for p in declarations]
        result["paid_request_attempts"] = sum(r.get("paid_this_run") is True for r in records)
        result["tokens"] = {k: sum(r.get("usage", {}).get(k) or 0 for r in records if r.get("paid_this_run"))
            for k in ("input_tokens", "output_tokens", "total_tokens")}
        result["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
        save(result_file, result)
        print(json.dumps({k: row[k] for k in ("material_id", "proposal_family", "selected_family", "selection_pass",
              "compilation_pass", "runtime_pass", "failure_category")}), flush=True)
    print(json.dumps(result["summary"], indent=2))
    table = "| Material | Proposed | Selected | Selection | Compile | Runtime | Grounding | Failure |\n|---|---|---|---|---|---|---|---|\n"
    for r in result["rows"]:
        table += "| " + " | ".join(str(r.get(k)) for k in ("material_id", "proposal_family", "selected_family", "selection_pass",
                   "compilation_pass", "runtime_pass", "grounding_pass", "failure_category")) + " |\n"
    (directory / "summary.md").write_text(table, encoding="utf-8")


if __name__ == "__main__":
    main()
