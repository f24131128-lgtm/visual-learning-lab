"""Actual root input→analysis→plan→process paths, with mocked provider calls only."""
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from source_atlas.model import semantic_catalog
from learning_world import compiler, planner, process
from learning_world.diagnostics import Rejection
from support import ROOT
from day22_live_fixtures import EXACT_QUEUE_TEXT, analysis, candidate


class LiveContractTests(unittest.TestCase):
    def setUp(self):
        self.catalog = semantic_catalog(None, analysis())
        self.raw = candidate()
        self.caps = compiler.capabilities(analysis(), {}, {})

    def test_real_like_semantic_ids_compile_without_changing_focus_identity(self):
        # The former core check `item['id'] in catalog` rejected this declaration.
        self.assertIn(self.raw["process"]["collections"][0]["id"], self.catalog)
        spec = planner.normalize(self.raw, self.catalog, [], self.caps)
        self.assertEqual(spec["family"], "process")
        p = spec["process"]
        self.assertNotIn(p["collections"][0]["id"], self.catalog)
        self.assertEqual(p["collections"][0]["semantic_id"], "queue")
        self.assertEqual(p["transitions"][0]["target_id"], p["collections"][0]["id"])
        self.assertEqual(p["transitions"][0]["label"], "enqueue(x)")
        self.assertEqual(len(p["annotations"]), 1)
        # Reordering declarations retains semantic-derived runtime identities.
        raw = copy.deepcopy(self.raw); raw["process"]["transitions"].reverse()
        other = planner.normalize(raw, self.catalog, [], self.caps)
        self.assertEqual({t["semantic_id"]: t["id"] for t in p["transitions"]}, {t["semantic_id"]: t["id"] for t in other["process"]["transitions"]})

    def test_same_adapter_supports_lifo(self):
        for kind, expected in (("fifo", "A"), ("lifo", "C")):
            p = planner.normalize(candidate(kind), self.catalog, [], self.caps)["process"]
            state = process.initial(p)
            for t in p["transitions"]:
                state, focus = process.apply(p, state, dict(identity=state["identity"], revision=state["revision"], transition_id=t["id"], value="C"))
            self.assertEqual(state["last_removed"], expected)
            self.assertEqual(focus, "dequeue")

    def test_fatal_operations_unknown_semantics_duplicates_and_markup_stay_fatal(self):
        mutations = [lambda r: r["process"]["transitions"][0].update(operation="eval"),
            lambda r: r["process"]["transitions"][0].update(semantic_id="unknown"),
            lambda r: r["process"]["transitions"][1].update(id="enqueue"),
            lambda r: r["process"]["collections"][0].update(label="<script>"),
            lambda r: r["process"]["collections"][0].update(capacity=999),
            lambda r: r["process"]["transitions"][0].update(target_id="unknown")]
        for mutate in mutations:
            raw = copy.deepcopy(self.raw); mutate(raw)
            with self.assertRaises(ValueError): planner.normalize(raw, self.catalog, [], self.caps)
        raw = copy.deepcopy(self.raw); raw["process"]["transitions"][0]["operation"] = "eval"
        with self.assertRaises(Rejection) as failure: planner.normalize(raw, self.catalog, [], self.caps)
        self.assertEqual(failure.exception.code, "unsafe_operation")
        self.assertEqual(failure.exception.path, "$.process.transitions[0].operation")

    def test_local_revalidation_no_client_no_paid_retry(self):
        source = dict(kind="text", source_text=EXACT_QUEUE_TEXT)
        data = compiler.context(analysis(), source, self.catalog, [], self.caps, None)
        key = compiler.identity("m", "zh-TW", source, self.catalog, self.caps, None)
        store = compiler.ensure({}, "m")
        client = MagicMock(); client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(self.raw))
        with patch("learning_world.compiler.normalize", side_effect=Rejection("reference", "$.process.collections[0].semantic_id")):
            self.assertIsNone(compiler.build(store, key, client, "offline", data, self.catalog, [], self.caps))
        self.assertIn(key, store["pending"])
        trace = store["diagnostics"][key]
        self.assertEqual((trace["stage"], trace["code"]), ("normalize", "reference"))
        self.assertEqual(trace["generated"]["planner_family"], "process")
        self.assertIsNotNone(compiler.build(store, key, None, "offline", data, self.catalog, [], self.caps))
        self.assertEqual(client.responses.create.call_count, 1)
        self.assertEqual(store["request_count"], 1)
        self.assertNotIn(key, store["pending"])

    def test_diagnostics_exclude_source_and_exception_secrets_and_preserve_valid_state(self):
        source = dict(kind="text", source_text="PRIVATE SOURCE BODY")
        data = compiler.context(analysis(), source, self.catalog, [], self.caps, None)
        store = compiler.ensure({}, "m"); key = compiler.identity("m", "zh-TW", source, self.catalog, self.caps, None)
        client = MagicMock(); client.responses.create.side_effect = RuntimeError("sk-PRIVATE Bearer SECRET PRIVATE SOURCE BODY")
        self.assertIsNone(compiler.build(store, key, client, "offline", data, self.catalog, [], self.caps))
        exported = json.dumps(store["diagnostics"] [key])
        for token in ("PRIVATE", "Bearer", "SECRET", "source_context"): self.assertNotIn(token, exported)
        self.assertEqual(store["diagnostics"][key]["stage"], "request")

    def test_process_capability_is_advertised_without_invalidating_accepted_identity(self):
        self.assertTrue(self.caps["process"])
        source = dict(kind="text", source_text=EXACT_QUEUE_TEXT)
        old_caps = {k: v for k, v in self.caps.items() if k != "process"}
        self.assertEqual(compiler.identity("m", "zh-TW", source, self.catalog, old_caps, None), compiler.identity("m", "zh-TW", source, self.catalog, self.caps, None))


class RootLivePathTests(unittest.TestCase):
    def test_exact_input_analysis_planner_process_beats_legacy_flow_and_all_actions_local(self):
        at = AppTest.from_file(str(ROOT/"app.py"), default_timeout=40)
        at.secrets["OPENAI_API_KEY"] = "offline"
        at.query_params["learning_world_debug"] = "1"
        responses = [SimpleNamespace(output_text=json.dumps(analysis())), SimpleNamespace(output_text=json.dumps(candidate()))]
        with patch("openai.resources.responses.responses.Responses.create", side_effect=responses) as api:
            at.run()
            at.text_area[0].set_value(EXACT_QUEUE_TEXT)
            at.button(key="analyze-material").click().run(); self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)
            material = at.session_state["analysis_id"]
            at.radio(key="workspace-mode-"+material).set_value("explore").run()
            self.assertTrue(any(h.value == "### 視覺流程" for h in at.markdown))
            at.button(key="world-plan-"+material).click().run(); self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 2)
            self.assertEqual(at.session_state["learning_workspace"]["representation"], "process")
            self.assertFalse(any("### 視覺流程" == h.value for h in at.markdown))
            self.assertTrue(any(t.value == "A → B" for t in at.text))
            spec = at.session_state["learning_world_plans"]["cache"][at.session_state["learning_world_plans"]["active"]]["process"]
            prefix = "world-process-"+material+"-"+process.initial(spec)["identity"][:12]
            at.text_input(key=prefix+"-input").set_value("C").run()
            at.button(key=prefix+"-"+spec["transitions"][0]["id"]).click().run()
            self.assertTrue(any(t.value == "A → B → C" for t in at.text))
            at.button(key=prefix+"-"+spec["transitions"][1]["id"]).click().run()
            self.assertTrue(any(t.value == "B → C" for t in at.text))
            self.assertTrue(any(c.value == "Front: B · Rear: C" for c in at.caption))
            self.assertEqual(at.session_state["learning_workspace"]["focus"], "dequeue")
            at.radio(key="workspace-mode-"+material).set_value("source").run()
            at.radio(key="workspace-mode-"+material).set_value("explore").run()
            self.assertTrue(any(t.value == "B → C" for t in at.text))
            at.button(key=prefix+"-reset").click().run()
            self.assertTrue(any(t.value == "A → B" for t in at.text))
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 2)
            store = at.session_state["learning_world_plans"]
            trace = store["diagnostics"][store["active"]]
            self.assertTrue(trace["process_runtime_reached"])
            self.assertFalse(trace["legacy_visual_flow_used"])

    def test_failed_candidate_ui_rechecks_locally_without_openai_initialization(self):
        at = AppTest.from_file(str(ROOT/"app.py"), default_timeout=40)
        at.secrets["OPENAI_API_KEY"] = "offline"
        data = dict(analysis=analysis(), analysis_id="m", allowed_source_pages=[], source_context=dict(kind="text", source_text=EXACT_QUEUE_TEXT), learning_workspace=dict(material_id="m", mode="explore", focus=None, representation="formal"))
        for k, v in data.items(): at.session_state[k] = v
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(candidate()))) as api:
            at.run()
            with patch("learning_world.compiler.normalize", side_effect=Rejection("reference")):
                at.button(key="world-plan-m").click().run()
            self.assertEqual(api.call_count, 1)
            at.run()
            self.assertEqual(at.button(key="world-plan-m").label, "本地重驗已保留的學習表示")
            with patch("openai.OpenAI", side_effect=AssertionError("local recheck must not initialize client")):
                at.button(key="world-plan-m").click().run()
            self.assertFalse(at.exception); self.assertEqual(api.call_count, 1)
            self.assertEqual(at.session_state["learning_workspace"]["representation"], "process")


if __name__ == "__main__": unittest.main()
