"""Deterministic safety, cross-domain routing and actual normal-app local interactions."""
import ast
import copy
import json
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
import streamlit as st
from streamlit.testing.v1 import AppTest
from learning_world import compiler, planner, process, runtime
from learning_world.schema import SCHEMA, MAX_HISTORY
from day22_fixtures import cases, discrete, plan
from workspace import state as ws
from support import ROOT


class PlannerTests(unittest.TestCase):
    def test_six_families(self):
        for c in cases():
            with self.subTest(case=c["name"]):
                caps = compiler.capabilities({}, dict(scene=c["scene"]), {})
                spec = planner.normalize(c["raw"], c["catalog"], [1, 2], caps)
                self.assertEqual(spec["family"], c["family"])

    def test_labels_and_topic_names_cannot_change_routing(self):
        for c in cases():
            caps = compiler.capabilities({}, dict(scene=c["scene"]), {})
            original = planner.normalize(c["raw"], c["catalog"], [1, 2], caps)
            for v in c["catalog"].values(): v["label"] = "ohm queue projectile sinusoid probability"
            c["raw"]["reason"] = "queue projectile"
            self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1, 2], caps)["family"], original["family"])

    def test_unsupported_runtime_falls_back(self):
        c = cases()[0]
        self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1], {})["family"], "none")
        c["raw"]["features"]["structure"] = True
        self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1], {})["family"], "static")

    def test_lab_is_reused_without_second_spatial_engine(self):
        c = cases()[0]
        self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1], dict(lab=True))["family"], "dynamic")

    def test_no_interaction_cannot_force_animation(self):
        c = cases()[0]; c["raw"]["features"]["interaction_value"] = False
        self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1], dict(spatial=True))["family"], "none")
        c["raw"]["features"]["structure"] = True
        self.assertEqual(planner.normalize(c["raw"], c["catalog"], [1], dict(spatial=True))["family"], "static")

    def test_malformed_plans_and_broken_provenance(self):
        _, catalog, raw = discrete()
        mutations = [lambda r: r.update(version="99"), lambda r: r.update(preferred="python"),
            lambda r: r.update(focus_ids=["unknown"]), lambda r: r.update(focus_ids=["remove", "remove"]),
            lambda r: r.update(source_pages=[99]), lambda r: r.update(source_pages=[True]),
            lambda r: r.update(reason="<script>"), lambda r: r.update(script="exec"),
            lambda r: r["features"].update(transitions=1), lambda r: r.update(reason="x"*401),
            lambda r: r["process"]["collections"][0].update(capacity=999),
            lambda r: r["process"]["collections"][0].update(initial=["<img>"]),
            lambda r: r["process"]["transitions"][0].update(operation="eval"),
            lambda r: r["process"]["transitions"][0].update(semantic_id="unknown"),
            lambda r: r["process"]["transitions"][0].update(target_id="unknown"),
            lambda r: r["process"]["transitions"][1].update(id="act_insert"),
            lambda r: r["process"].update(transitions=[]),
            lambda r: r.update(focus_ids=["collection"])]
        for mutate in mutations:
            r = copy.deepcopy(raw); mutate(r)
            with self.subTest(raw_field=mutate), self.assertRaises(ValueError): planner.normalize(r, catalog, [1], {})
        catalog["remove"]["pages"] = []
        r = plan("none", ["remove"], [], pages=[1])
        with self.assertRaises(ValueError): planner.normalize(r, catalog, [1], {})

    def test_optional_annotations_fail_independently(self):
        _, catalog, raw = discrete()
        raw["process"]["annotations"] = [dict(semantic_id="remove", text="Watch the first item"), dict(semantic_id="unknown", text="Bad reference"), dict(semantic_id="remove", text="<script>"), 1]
        spec = planner.normalize(raw, catalog, [1], {})
        self.assertEqual(len(spec["process"]["annotations"]), 1)
        self.assertEqual(spec["family"], "process")

    def test_strict_schema_has_no_open_objects(self):
        def walk(value):
            if isinstance(value, dict):
                if value.get("type") == "object":
                    self.assertFalse(value["additionalProperties"])
                    self.assertEqual(set(value["required"]), set(value["properties"]))
                for v in value.values(): walk(v)
            elif isinstance(value, list):
                for v in value: walk(v)
        walk(SCHEMA)

    def test_core_ast_audit(self):
        forbidden = {"eval", "exec", "compile", "__import__"}
        topics = {"queue", "ohm", "projectile", "sinusoid", "probability"}
        for path in (ROOT/"learning_world").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            self.assertFalse([n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in forbidden])
            # Whole string literals used in production control flow, not docs/module names.
            for n in ast.walk(tree):
                if isinstance(n, (ast.If, ast.IfExp)):
                    self.assertFalse([v for v in ast.walk(n.test) if isinstance(v, ast.Constant) and isinstance(v.value, str) and v.value.lower() in topics])


class ProcessTests(unittest.TestCase):
    def setUp(self):
        self.analysis, self.catalog, raw = discrete()
        self.plan = planner.normalize(raw, self.catalog, [1], {})
        self.spec = self.plan["process"]; self.state = process.initial(self.spec)

    def event(self, transition="act_insert", value="C"):
        return dict(identity=self.state["identity"], revision=self.state["revision"], transition_id=transition, value=value)

    def test_fifo_and_identity_not_array_position(self):
        before = copy.deepcopy(self.state)
        self.state, focus = process.apply(self.spec, self.state, self.event())
        self.assertEqual(before["collections"]["items_state"][0]["id"], self.state["collections"]["items_state"][0]["id"])
        self.assertEqual(focus, "insert")
        self.spec["transitions"].reverse()  # A reordered spec requires a new identity, never positional dispatch.
        self.assertIsNone(process.apply(self.spec, self.state, self.event("act_remove", "")))
        self.spec["transitions"].reverse()
        self.state, focus = process.apply(self.spec, self.state, self.event("act_remove", ""))
        self.assertEqual(self.state["last_removed"], "A")
        self.assertEqual([i["text"] for i in self.state["collections"]["items_state"]], ["B", "C"])
        self.assertEqual(focus, "remove")

    def test_same_reducer_handles_lifo_and_finite_states(self):
        for kind in ("lifo", "states"):
            _, catalog, raw = discrete(kind)
            spec = planner.normalize(raw, catalog, [1], {})["process"]
            state = process.initial(spec)
            for transition in ("act_insert", "act_remove"):
                state, _ = process.apply(spec, state, dict(identity=state["identity"], revision=state["revision"], transition_id=transition, value="C"))
            if kind == "lifo": self.assertEqual(state["last_removed"], "C")
            else: self.assertEqual(state["states"]["status_state"], "done")

    def test_capacity_empty_and_history_bounds(self):
        for _ in range(50):
            while process.enabled(self.spec, self.state, "act_insert"):
                self.state, _ = process.apply(self.spec, self.state, self.event())
            self.assertIsNone(process.apply(self.spec, self.state, self.event()))
            while process.enabled(self.spec, self.state, "act_remove"):
                self.state, _ = process.apply(self.spec, self.state, self.event("act_remove", ""))
            self.assertIsNone(process.apply(self.spec, self.state, self.event("act_remove", "")))
        self.assertEqual(len(self.state["history"]), MAX_HISTORY)

    def test_stale_hostile_and_wrong_scene_are_atomic(self):
        before = copy.deepcopy(self.state)
        for patch_event in (dict(revision=True), dict(revision=-1), dict(identity="old"), dict(transition_id=[]), dict(value="<img>"), dict(value="x"*65), dict(script="exec")):
            self.assertIsNone(process.apply(self.spec, self.state, self.event() | patch_event))
        self.assertEqual(before, self.state)
        event = self.event()
        self.state, _ = process.apply(self.spec, self.state, event)
        self.assertIsNone(process.apply(self.spec, self.state, event))

    def test_malformed_state_rejected(self):
        for field, value in (("history", [dict(transition_id=[], revision=1)]), ("collections", {}), ("serial", True), ("last_removed", "<script>")):
            state = self.state | {field: value}
            self.assertFalse(process.valid(self.spec, state))
            self.assertIsNone(process.apply(self.spec, state, self.event()))

    def test_reset_rejects_prior_events_preserves_focus_and_other_state(self):
        event = self.event()
        state = process.reset(self.spec, self.state)
        self.assertIsNone(process.apply(self.spec, state, event))
        self.assertEqual(state["collections"], self.state["collections"])

    def test_commit_uses_canonical_focus_and_preserves_learning(self):
        session = dict(quiz_answers={"q": "wrong"}, explanation_cache={"x": "saved"})
        with patch.object(st, "session_state", session):
            workspace = ws.get_workspace_state("m")
            store = dict(states={"key": self.state})
            self.assertTrue(runtime.commit(store, "key", self.spec, self.event("act_remove", ""), workspace, self.catalog, dict(material_id="m", scene=None)))
            self.assertEqual(ws.get_workspace_focus(workspace), "remove")
            self.assertEqual(session["quiz_answers"], {"q": "wrong"})
            self.assertEqual(session["explanation_cache"], {"x": "saved"})
            for mode in ws.MODES: ws.open_workspace(workspace, mode)
            self.assertEqual(ws.get_workspace_focus(workspace), "remove")
            region = dict(semantic_ids=["remove"], source_text_excerpt="First item is removed")
            self.assertIn("explore", ws.actions(region, self.catalog, learning_path=self.analysis["learning_path"], process_ids=self.plan["focus_ids"]))
            self.assertEqual(ws.actions(region, self.catalog, learning_path=self.analysis["learning_path"], process_ids=self.plan["focus_ids"])["practice"], ["s1"])


class CompilerTests(unittest.TestCase):
    def setUp(self):
        self.analysis, self.catalog, self.raw = discrete()
        self.source = dict(kind="text", source_text="An ordered collection adds at the last end and removes from the first end.")
        self.caps = compiler.capabilities(self.analysis, {}, {})
        self.store = compiler.ensure({}, "m")
        self.key = compiler.identity("m", "zh-TW", self.source, self.catalog, self.caps, None)
        self.data = compiler.context(self.analysis, self.source, self.catalog, [], self.caps, None)
        self.raw["source_pages"] = []
        self.client = MagicMock()
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(self.raw), status="completed")

    def build(self): return compiler.build(self.store, self.key, self.client, "offline", self.data, self.catalog, [], self.caps)

    def test_one_request_and_local_operations_no_calls(self):
        spec = self.build()
        self.assertIsNotNone(spec)
        self.assertEqual(self.build(), spec)
        state = process.initial(spec["process"])
        for _ in range(10):
            state, _ = process.apply(spec["process"], state, dict(identity=state["identity"], revision=state["revision"], transition_id="act_remove", value=""))
            state = process.reset(spec["process"], state)
        self.assertEqual(self.client.responses.create.call_count, 1)
        call = self.client.responses.create.call_args.kwargs
        self.assertTrue(call["text"]["format"]["strict"])
        self.assertNotIn("pdf", call["input"])

    def test_unsuitable_cached(self):
        self.raw = plan("none", ["collection"], [], pages=[])
        self.client.responses.create.return_value.output_text = json.dumps(self.raw)
        self.assertEqual(self.build()["family"], "none")
        self.build(); self.assertEqual(self.client.responses.create.call_count, 1)

    def test_failure_isolated_and_explicit_retry(self):
        accepted = self.build(); active = self.store["active"]
        self.key = self.key[:-1] + ("remove",)
        self.client.responses.create.side_effect = RuntimeError("secret API credential")
        self.assertIsNone(self.build())
        self.assertEqual(self.store["active"], active)
        self.assertEqual(self.store["cache"][active], accepted)
        self.assertNotIn("credential", str(self.store))
        self.client.responses.create.side_effect = None
        self.assertIsNotNone(self.build())

    def test_refusal_incomplete_and_response_bounds(self):
        for response in (SimpleNamespace(output_text=json.dumps(self.raw), status="incomplete"),
                         SimpleNamespace(output_text=" "*48001), SimpleNamespace(output_text="{}"),
                         SimpleNamespace(output_text=json.dumps(self.raw), output=[SimpleNamespace(content=[SimpleNamespace(type="refusal")])])):
            self.client.responses.create.return_value = response
            self.assertIsNone(self.build())
            self.assertFalse(self.store["cache"])

    def test_cache_identity_material_language_semantics_not_local_values(self):
        first = self.key
        self.assertNotEqual(first, compiler.identity("m", "en", self.source, self.catalog, self.caps, None))
        changed = copy.deepcopy(self.catalog); changed["remove"]["label"] = "Changed meaning"
        self.assertNotEqual(first, compiler.identity("m", "zh-TW", self.source, changed, self.caps, None))
        for n in range(7):
            self.key = first[:-1] + (str(n),); self.build()
        self.assertEqual(len(self.store["cache"]), 4)
        compiler.ensure(self.store, "new"); self.assertFalse(self.store["cache"])

    def test_source_required_bounded_and_page_whitelisted(self):
        with self.assertRaises(ValueError): compiler.context(self.analysis, {}, self.catalog, [], self.caps, None)
        data = compiler.context(self.analysis, dict(kind="pdf", page_texts={1: "Original", 99: "Forbidden"}), self.catalog, [1], self.caps, None)
        self.assertNotIn("Forbidden", json.dumps(data))
        self.assertNotIn("99", json.dumps(data))


class AppTests(unittest.TestCase):
    def app(self):
        at = AppTest.from_file(str(ROOT/"app.py"), default_timeout=30)
        at.secrets["OPENAI_API_KEY"] = "offline"
        analysis, catalog, raw = discrete()
        source = dict(kind="text", source_text="A queue is FIFO: enqueue at rear, dequeue at front. A then B then C.")
        analysis["analysis_language"] = "zh-TW"
        caps = compiler.capabilities(analysis, {}, {})
        store = compiler.ensure({}, "m")
        key = compiler.identity("m", "zh-TW", source, catalog, caps, None)
        raw["source_pages"] = []
        store["cache"][key] = planner.normalize(raw, catalog, [], caps); store["active"] = key
        data = dict(analysis=analysis, analysis_id="m", allowed_source_pages=[], source_context=source,
            learning_world_plans=store, learning_workspace=dict(material_id="m", mode="explore", focus=None, representation="process"))
        for k, v in data.items(): at.session_state[k] = v
        return at

    def test_normal_text_process_round_trip_zero_requests(self):
        with patch("openai.resources.responses.responses.Responses.create", side_effect=AssertionError("unexpected API")) as api:
            at = self.app().run(); self.assertFalse(at.exception)
            self.assertIn("互動流程", [r.options[-1] for r in at.radio if r.key == "workspace-representation-m"])
            item = next(t for t in at.text_input if t.label == "新項目")
            item.set_value("C").run()
            next(b for b in at.button if b.label == "Insert at the last end").click().run()
            next(b for b in at.button if b.label == "Remove at the first end").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(at.session_state["learning_workspace"]["focus"], "remove")
            at.radio(key="workspace-mode-m").set_value("source").run()
            self.assertTrue(any("queue is FIFO" in t.value for t in at.text))
            at.radio(key="workspace-mode-m").set_value("practice").run()
            at.radio(key="workspace-mode-m").set_value("explore").run()
            next(b for b in at.button if b.label == "重設流程").click().run()
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 0)

    def test_explicit_build_selects_process_once_and_switching_is_local(self):
        at = self.app()
        at.session_state["learning_world_plans"] = compiler.ensure({}, "m")
        at.session_state["learning_workspace"]["representation"] = "formal"
        _, _, raw = discrete(); raw["source_pages"] = []
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run(); self.assertEqual(api.call_count, 0)
            at.button(key="world-plan-m").click().run(); self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)
            self.assertEqual(at.session_state["learning_workspace"]["representation"], "process")
            at.radio(key="workspace-representation-m").set_value("formal").run()
            at.radio(key="workspace-representation-m").set_value("process").run()
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 1)

    def test_normal_pdf_process_cta_and_source_round_trip(self):
        from atlas_fixtures import source_pdf, page_texts
        from source_lens import new_source_state
        at = self.app()
        pdf = source_pdf()
        source = dict(kind="pdf", page_texts=page_texts(pdf))
        analysis, catalog, raw = discrete()
        analysis["analysis_language"] = "zh-TW"
        caps = compiler.capabilities(analysis, {}, {})
        at.session_state["source_context"] = source
        at.session_state["allowed_source_pages"] = [1, 2]
        at.session_state["learning_world_plans"] = compiler.ensure({}, "m")
        at.session_state["learning_workspace"]["representation"] = "formal"
        at.session_state["learning_canvas"] = dict(material_id="m", selected_id=None, kind=None, component=None,
            style_signature=None, last_event=-1, fallback=False, component_error=False, source=new_source_state("m", pdf))
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run(); self.assertFalse(at.exception); self.assertEqual(api.call_count, 0)
            at.button(key="world-plan-m").click().run()
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 1)
            next(b for b in at.button if b.label == "Remove at the first end").click().run()
            state = at.session_state["learning_world_plans"]
            before = copy.deepcopy(state["states"][state["active"]])
            at.radio(key="workspace-mode-m").set_value("source").run()
            at.radio(key="workspace-mode-m").set_value("explore").run()
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 1)
            state = at.session_state["learning_world_plans"]
            self.assertEqual(state["states"][state["active"]], before)

    def test_none_suppresses_hidden_interactive_runtimes(self):
        at = self.app()
        store = at.session_state["learning_world_plans"]
        raw = plan("none", ["collection"], [], pages=[])
        _, catalog, _ = discrete()
        store["cache"][store["active"]] = planner.normalize(raw, catalog, [], {})
        at.session_state["learning_workspace"]["representation"] = "formal"
        with patch("interactive_lab.render_interactive_lab") as lab, patch("dynamic_simulation.render_simulation_studio") as sim, patch("scene.compiler.render_scene_builder") as builder:
            at.run(); self.assertFalse(at.exception)
            self.assertFalse(lab.called); self.assertFalse(sim.called); self.assertFalse(builder.called)
            self.assertEqual(at.radio(key="workspace-representation-m").options, ["正式模型"])

    def test_renderer_failure_retains_accessible_process(self):
        with patch("streamlit.graphviz_chart", side_effect=RuntimeError("renderer unavailable")):
            at = self.app().run(); self.assertFalse(at.exception)
            self.assertTrue(any("A → B" in t.value for t in at.text))
            next(b for b in at.button if b.label == "Remove at the first end").click().run()
            self.assertFalse(at.exception)


if __name__ == "__main__": unittest.main()
