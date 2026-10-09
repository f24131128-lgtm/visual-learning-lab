"""Grounded identity, honest affordances, optional isolation and request counts."""
import ast
import copy
import math
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

import streamlit as st
from streamlit.testing.v1 import AppTest
from manipulation import lab, world, runtime
from scene.world.state import new_state, apply_patch
from scene.world.engine import snapshot
from source_atlas.state import select_region, sync_region, consume_event
from scene.state import fingerprint
from workspace.state import get_workspace_state, get_workspace_focus, open_workspace
from workspace.grounded_twin import derive_links, grounding_kind, comparison_rows
from twin_fixtures import fixture
from manipulation_fixtures import math_demo

ROOT = Path(__file__).resolve().parents[1]


class TwinLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.fixtures = {k: fixture(k) for k in ("phase", "projectile", "math")}

    def setUp(self):
        self.data = copy.deepcopy(self.fixtures["phase"])
        self.session = patch.object(st, "session_state", {})
        self.session.start(); self.addCleanup(self.session.stop)

    def links(self, data=None, targets=None):
        d = data or self.data
        ts = world.targets(d["scene"], new_state(d["scene"])) if targets is None and d["scene"] else targets or []
        return derive_links(d["atlas_state"], d["material"], [1,2,3], d["catalog"], ts, document=d["atlas_state"]["document_model"])

    def test_many_regions_exact_identity_and_non_manipulable_quantity(self):
        for k in ("phase", "projectile"):
            d = self.fixtures[k]; links = self.links(d)
            self.assertEqual(links[d["semantic"]]["source_region_ids"], ["source_formula", "source_object"])
            self.assertTrue(links[d["semantic"]]["manipulable"])
            self.assertFalse(links[d["derived"]]["manipulable"])
            self.assertEqual(links[d["derived"]]["support"][0]["kind"], "page_only")

    def test_stable_ids_under_reordering_and_label_changes(self):
        before = self.links()
        self.data["atlas_state"]["atlas"]["regions"].reverse()
        for r in self.data["atlas_state"]["atlas"]["regions"]: r["label"] = "unrelated renamed label"
        after = self.links()
        self.assertEqual(set(before), set(after))
        for identifier in before:
            self.assertEqual(before[identifier]["manipulation_target_ids"], after[identifier]["manipulation_target_ids"])
            self.assertEqual(set(before[identifier]["source_region_ids"]), set(after[identifier]["source_region_ids"]))

    def test_source_twin_source_preserves_original_and_all_learning_state(self):
        for k in ("phase", "projectile"):
            d = copy.deepcopy(self.fixtures[k]); scene = d["scene"]
            wrapper = dict(material_id=d["material"], scene=scene, world=new_state(scene))
            workspace = get_workspace_state(d["material"])
            original_atlas, original_pdf = copy.deepcopy(d["atlas_state"]["atlas"]), d["pdf"]
            st.session_state.update(quizzes={"q":"answer"}, review=["step"], explanations={"cached":"text"})
            self.assertTrue(select_region(d["atlas_state"], "source_object", d["catalog"], wrapper))
            self.assertEqual(get_workspace_focus(workspace, wrapper), d["semantic"])
            open_workspace(workspace, "explore")
            target = world.targets(scene, wrapper["world"])[0]
            radius = 1. if k == "phase" else 30.
            angle = math.pi/2 if k == "phase" else math.pi/3
            self.assertTrue(world.commit(scene, wrapper["world"], "m", dict(scene="m", revision=wrapper["world"]["revision"],
                token="local", kind="manipulate", target=target["id"], x=radius*math.cos(angle), y=radius*math.sin(angle), time=0.)))
            before = copy.deepcopy(wrapper["world"])
            open_workspace(workspace, "source")
            self.assertEqual(sync_region(d["atlas_state"], d["semantic"])["region_id"], "source_object")
            self.assertEqual(wrapper["world"], before)
            self.assertEqual(d["atlas_state"]["atlas"], original_atlas); self.assertEqual(d["pdf"], original_pdf)
            self.assertEqual(st.session_state["quizzes"], {"q":"answer"}); self.assertEqual(st.session_state["review"], ["step"])

    def test_reverse_focus_ranks_bbox_but_retains_selected_same_focus_region(self):
        s = self.data["atlas_state"]
        self.assertEqual(sync_region(s, "angle")["region_id"], "source_formula")
        select_region(s, "source_object", self.data["catalog"])
        s["seen_focus"] = "angle"
        self.assertEqual(sync_region(s, "angle")["region_id"], "source_object")
        self.assertIsNone(sync_region(s, "wave")["bbox"])
        self.assertEqual(s["page"], 3)

    def test_compiled_baseline_current_delta_not_source_truth(self):
        d = self.data; state = new_state(d["scene"])
        apply_patch(d["scene"], state, dict(op="set_parameter",target_id="phase",value=math.pi/2))
        rows = comparison_rows(d["scene"]["parameters"], state["parameters"], ["phase"])
        self.assertAlmostEqual(rows[0]["delta"], math.pi/2)
        self.assertEqual(rows[0]["baseline"], 0.)
        self.assertIn("phase = 0", d["texts"][1])

    def test_provenance_never_promotes_note_or_low_confidence(self):
        r = self.data["atlas_state"]["atlas"]["regions"][0]
        document=self.data["atlas_state"]["document_model"]
        self.assertEqual(grounding_kind(r, document), "native_geometry" if document else "estimated_region")
        r["grounding_note"] = "verified/native/exact"
        self.assertEqual(grounding_kind(r), "estimated_region")
        r["bbox"] = None
        self.assertEqual(grounding_kind(r), "page_only")

    def test_stale_material_pdf_semantic_identity_and_unknown_target(self):
        d = self.data; s = d["atlas_state"]
        self.assertEqual(derive_links(s, "other", [1,2,3], d["catalog"]), {})
        self.assertEqual(derive_links(s, d["material"], [1,2,3], d["catalog"], expected_key=s["key"][:-1]+("changed",)), {})
        ts = world.targets(d["scene"], new_state(d["scene"]))
        ts[0]["object_id"] = "unknown"
        self.assertFalse(self.links(targets=ts)["angle"]["manipulable"])
        wrapper = dict(material_id="other", scene=d["scene"], world=new_state(d["scene"]))
        self.assertFalse(select_region(s, "source_formula", d["catalog"], wrapper))

    def test_hostile_region_coordinates_links_page_and_global_bounds(self):
        base = copy.deepcopy(self.data)
        fields = [dict(page=4), dict(page=True), dict(semantic_ids=["unknown"]), dict(semantic_ids=["angle"]*9),
                  dict(bbox={"x0":0.,"y0":0.,"x1":2.,"y1":1.}), dict(confidence="low")]
        fields += [dict(bbox={"x0":v,"y0":0.,"x1":.8,"y1":.9}) for v in [float('nan'),float('inf'),-1.,10**500,True]]
        for change in fields:
            d = copy.deepcopy(base); d["atlas_state"]["atlas"]["regions"][0].update(change)
            self.assertNotIn("source_formula", self.links(d)["angle"]["source_region_ids"])
        d = copy.deepcopy(base); d["atlas_state"]["atlas"]["regions"] *= 22
        self.assertEqual(self.links(d), {})

    def test_ambiguous_region_preserves_focus_until_explicit_choice(self):
        d = self.data; wrapper = dict(material_id=d["material"],scene=d["scene"],world=new_state(d["scene"]))
        wrapper["world"]["focus"] = "horizontal"
        d["atlas_state"]["atlas"]["regions"][0]["semantic_ids"] = ["angle", "wave"]
        select_region(d["atlas_state"], "source_formula", d["catalog"], wrapper)
        self.assertEqual(wrapper["world"]["focus"], "horizontal")
        self.assertEqual(sync_region(d["atlas_state"], "horizontal")["region_id"], "source_formula")

    def test_source_event_stale_token_focus_page_and_target_spoof(self):
        d = self.data; s = d["atlas_state"]
        wrapper = dict(material_id=d["material"],scene=d["scene"],world=new_state(d["scene"]))
        event = dict(atlas=fingerprint(s["key"]),focus_stamp=fingerprint(wrapper["world"]["focus"]),region_id="source_formula",token="first")
        for change in (dict(region_id="unknown"),dict(atlas="stale"),dict(focus_stamp="stale"),dict(target="pointer")):
            self.assertFalse(consume_event(s,event|change,d["catalog"],wrapper))
        self.assertTrue(consume_event(s,event,d["catalog"],wrapper))
        self.assertFalse(consume_event(s,event,d["catalog"],wrapper))

    def test_fixed_parameter_and_unsupported_form_keep_formal_links(self):
        d = self.data; scene = d["scene"]
        p = scene["parameters"][0]; p.update(min=0.,max=0.,default=0.,step=0.,parameter_kind="fixed")
        ts = world.targets(scene,new_state(scene))
        self.assertFalse(self.links(targets=ts)["angle"]["manipulable"])

    def test_affine_uses_same_bridge_two_targets_one_semantic(self):
        d = self.fixtures["math"]; demo=math_demo(); values={p["id"]:p["default"] for p in demo["parameters"]}
        ts=lab.targets(demo,values,d["semantic"])
        links=derive_links(d["atlas_state"],d["material"],[1,2,3],d["catalog"],ts,
                           {d["semantic"]:[dict(id="relation_curve")]})
        self.assertEqual(len(links[d["semantic"]]["manipulation_target_ids"]),2)
        self.assertFalse(links[d["derived"]]["manipulable"])

    def test_generic_orchestration_no_topic_branches_or_execution(self):
        for file in (ROOT/"workspace/grounded_twin.py", ROOT/"workspace/twin_ui.py"):
            tree=ast.parse(file.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Name): self.assertNotIn(node.func.id,("eval","exec","compile"))
                if isinstance(node,ast.If):
                    values=[n.value.lower() for n in ast.walk(node.test) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
                    for name in ("phase","phasor","projectile","velocity","linear","affine","sinusoid","orbit","ohm","queue"):
                        self.assertFalse(any(name in v for v in values))

    def test_direct_lab_commit_retires_stale_slider_but_new_control_works(self):
        from interactive_lab import _save_parameter, _reset_parameters
        demo=math_demo();saved=dict(values={"gain":1.,"offset":0.},compare=True)
        store=dict(demos={demo["id"]:saved})
        target=lab.targets(demo,saved["values"],"formal_relation")[0]
        event=dict(scene="m",revision=lab.revision(saved),token="one",kind="manipulate",target=target["id"],x=0.,y=2.,time=0.)
        self.assertTrue(lab.commit(demo,saved,"m",event,"formal_relation",lambda _:True))
        st.session_state["old-slider"]=0.
        _save_parameter(store,demo["id"],"offset","old-slider",0)
        self.assertEqual(saved["values"]["offset"],2.)
        st.session_state["current-slider"]=-1.
        _save_parameter(store,demo["id"],"offset","current-slider",saved["control_generation"])
        self.assertEqual(saved["values"]["offset"],-1.)
        generation=saved["control_generation"]
        _reset_parameters(store,demo,"prefix")
        _save_parameter(store,demo["id"],"offset","current-slider",generation)
        self.assertEqual(saved["values"]["offset"],0.)

    def test_colliding_scoped_targets_do_not_choose_arbitrary_owner(self):
        ts=world.targets(self.data["scene"],new_state(self.data["scene"]))
        ts.append(copy.deepcopy(ts[0]))
        self.assertFalse(self.links(targets=ts)["angle"]["manipulable"])

    def test_native_preview_event_remains_local_without_semantic_focus(self):
        from document_intelligence.model import VERSION
        d=self.data;document=d["atlas_state"]["document_model"]
        if document is None:return
        state=d["atlas_state"]|dict(key=d["atlas_state"]["key"]+("native",VERSION),atlas=document["atlas"])
        r=state["atlas"]["regions"][0]
        event=dict(atlas=fingerprint(state["key"]),focus_stamp=fingerprint(None),region_id=r["region_id"],token="native")
        self.assertTrue(consume_event(state,event,d["catalog"]))
        self.assertEqual(state["region_hint"],r["region_id"])

    def test_parser_provenance_from_other_pdf_is_not_claimed(self):
        d=self.data
        document=copy.deepcopy(d["atlas_state"]["document_model"])
        if document is None:return
        document["pdf_sha256"]="other"
        links=derive_links(d["atlas_state"],d["material"],[1,2,3],d["catalog"],document=document)
        self.assertEqual(links["angle"]["support"][0]["kind"],"estimated_region")


class TwinProductTests(unittest.TestCase):
    def app(self, kind):
        at=AppTest.from_file(str(ROOT/"tests/manual_day25.py"),default_timeout=40)
        at.secrets["OPENAI_API_KEY"]="offline-placeholder"
        at.run()
        if kind!="phase": at.selectbox(key="day25-case").set_value(kind).run()
        self.assertFalse(at.exception)
        return at

    def choose(self, at, identifier):
        if identifier=="source_object": next(w for w in at.selectbox if w.label=="來源頁面").set_value(2).run()
        widget=next(w for w in at.selectbox if w.label=="選取來源物件")
        widget.set_value(identifier).run();self.assertFalse(at.exception)

    def test_normal_pdf_source_to_twin_drag_reverse_and_zero_calls(self):
        client=MagicMock()
        with patch("source_atlas.compiler.OpenAI",return_value=client), patch("scene.compiler.OpenAI",return_value=client):
            for kind in ("phase","projectile","math"):
                at=self.app(kind);self.choose(at,"source_object")
                self.assertTrue(any("來源 ↔ 互動分身" in t.value for t in at.markdown))
                source=copy.deepcopy(at.session_state["source_atlas_state"]["atlas"])
                at.button(key="workspace-twin-explore").click().run();self.assertFalse(at.exception)
                fired=[]
                def component(**kwargs):
                    p=kwargs["payload"]
                    if fired:return None
                    fired.append(p)
                    return dict(scene=p["identity"],revision=p["revision"],token="once",kind="manipulate",
                        target=p["targets"][0]["id"],time=0.,x=0. if kind!="projectile" else 15.,
                        y=1. if kind=="phase" else 15*math.sqrt(3) if kind=="projectile" else 2.)
                with patch.object(runtime,"_component",side_effect=component):at.run()
                self.assertFalse(at.exception);self.assertTrue(fired[0]["focused_target_ids"])
                state=copy.deepcopy(at.session_state["learning_scene_state"]["world"] if kind!="math" else at.session_state["interactive_lab_state"]["demos"])
                at.button(key="workspace-twin-source").click().run();self.assertFalse(at.exception)
                self.assertEqual(at.session_state["source_atlas_state"]["atlas"],source)
                self.assertEqual(at.session_state["source_atlas_state"]["region_hint"],"source_object")
                self.assertEqual(at.session_state["learning_scene_state"]["world"] if kind!="math" else at.session_state["interactive_lab_state"]["demos"],state)
            client.responses.create.assert_not_called()

    def test_non_manipulable_page_only_and_frontend_failure_isolation(self):
        at=self.app("phase")
        next(w for w in at.selectbox if w.label=="來源頁面").set_value(3).run()
        self.choose(at,"derived_source")
        self.assertFalse(any(b.key=="workspace-twin-explore" for b in at.button))
        self.assertTrue(any("沒有已驗證" in c.value for c in at.caption))
        with patch("source_atlas.runtime._component",side_effect=ValueError("viewer unavailable")):at.run()
        self.assertFalse(at.exception)
        self.assertTrue(any(w.label=="選取來源物件" for w in at.selectbox))
        at.radio(key="workspace-mode-day25-phase").set_value("explore").run()
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"],"wave")


if __name__=="__main__":unittest.main()
