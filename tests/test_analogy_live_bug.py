"""Captured live semantic structure + explicit synthetic runtime completions.

The developer download omitted formulas, coordinates, pages and teaching prose.
This is a regression for the observed mapping/binding failures, not a verbatim
replay of the original full model response or proof of live visual quality.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch
from analogy import compiler, state, engine
from analogy.schema import VERSION
from analogy.validator import normalize
from analogy.diagnostics import Rejection
from analogy_fixtures import spec, primitive, parameter


def captured_case():
    captured=json.loads((Path(__file__).parent/"fixtures/day21_analogy_live_rejection.json").read_text(encoding="utf-8"))["generated"]
    raw=spec("queue")
    for field in ("reason","formal_focus","selected_candidate","analogy_domain","candidates","analogy_entities"): raw[field]=copy.deepcopy(captured[field])
    raw["version"]=VERSION
    raw["formal_entities"]=[dict(id=e["id"],source_pages=[1]) for e in captured["formal_entities"]]
    raw["mappings"]=[dict(relationship="Synthetic completion: relation correspondence.",explains="Synthetic completion: bounded teaching relation.",**m) for m in captured["mappings"]]
    raw["parameters"]=[parameter(p["id"],p["id"],p["min"],p["max"],p["default"],p["mapping_id"],p["formal_target"]) for p in captured["parameters"]]
    raw["quantities"]=[]; raw["annotations"]=[]
    raw["primitives"]=[primitive(p["id"],p["entity_id"],p["type"],p["entity_id"],control_parameter=p["control_parameter"]) for p in captured["primitives"]]
    catalog={e["id"]:dict(label=e["id"],pages=[1],kind="concept_map",equation="",representations=[]) for e in raw["formal_entities"]}
    registry={"lab:ohms_current_curve:resistance":dict(min=1.,max=15.,default=6.,semantic_ids=["resistance_r"],owner="lab")}
    return raw,catalog,registry


class LiveRejectionTests(unittest.TestCase):
    def setUp(self): self.raw,self.catalog,self.registry=captured_case()

    def normalize(self,raw=None): return normalize(raw or self.raw,self.catalog,self.registry,[1],"ohms_law")

    def test_actual_captured_many_to_one_mappings_survive(self):
        result=self.normalize()
        self.assertTrue(result["suitable"])
        self.assertEqual(len(result["mappings"]),6)
        relation=[m["formal_id"] for m in result["mappings"] if m["analogy_id"]=="pipe_relation"]
        self.assertCountEqual(relation,["ohms_law","parameter_scaling"])
        self.assertEqual(result["parameters"][1]["formal_target"],"")
        self.assertTrue(any(r["code"]=="qualitative_binding_omitted" for r in result["recoveries"]))
        self.assertEqual(next(p for p in result["primitives"] if p["id"]=="iv_curve")["control_parameter"],"")
        self.assertTrue(any(p["entity_id"]=="pipe_relation" for p in result["primitives"]))

    def test_entity_selection_stable_and_preserves_related_canonical_focus(self):
        result=self.normalize(); workspace=dict(material_id="m",focus="current_i",mode="explore"); wrapper=dict(material_id="m")
        for mappings in (result["mappings"],list(reversed(result["mappings"]))):
            result["mappings"]=mappings; workspace["focus"]="current_i"
            self.assertTrue(state.select_entity(result,"pipe_relation",workspace,self.catalog,wrapper))
            self.assertEqual(workspace["focus"],"ohms_law")
            workspace["focus"]="parameter_scaling"
            state.select_entity(result,"pipe_relation",workspace,self.catalog,wrapper)
            self.assertEqual(workspace["focus"],"parameter_scaling")

    def test_duplicates_unknown_formal_refs_missing_focus_provenance_fatal(self):
        changes=[lambda r:r["mappings"].append(r["mappings"][0]|dict(id="duplicate_pair")),
            lambda r:r["mappings"][0].update(formal_id="unknown"),
            lambda r:r["mappings"][3].update(formal_id="scope_limits"),
            lambda r:r["formal_entities"][0].update(source_pages=[99])]
        for change in changes:
            raw=copy.deepcopy(self.raw); change(raw)
            with self.subTest(change=change),self.assertRaises(Rejection): self.normalize(raw)

    def test_trusted_ids_derived_and_references_rewritten_without_formal_changes(self):
        raw=copy.deepcopy(self.raw)
        old=raw["analogy_entities"][0]["id"]; raw["analogy_entities"][0]["id"]="voltage_v"
        for m in raw["mappings"]:
            if m["analogy_id"]==old: m["analogy_id"]="voltage_v"
        for p in raw["primitives"]:
            if p["entity_id"]==old: p["entity_id"]="voltage_v"
        raw["candidates"][0]["id"]="水流候選"; raw["selected_candidate"]="水流候選"
        a=self.normalize(raw); b=self.normalize(raw)
        self.assertEqual(a,b); self.assertNotEqual(a["analogy_entities"][0]["id"],"voltage_v")
        self.assertEqual(a["mappings"][0]["analogy_id"],a["analogy_entities"][0]["id"])
        self.assertEqual(a["mappings"][0]["formal_id"],"voltage_v")

    def test_optional_drag_unsupported_visual_and_static_core_isolate_safely(self):
        for mutate in (lambda r:r["primitives"][0].update(control_parameter="unknown"),
            lambda r:r["primitives"][0].update(type="decorative_pipe"),
            lambda r:r.update(primitives=[],parameters=[],quantities=[])):
            raw=copy.deepcopy(self.raw); mutate(raw); result=self.normalize(raw)
            self.assertEqual(len(result["mappings"]),6)
            self.assertTrue(result["primitives"])
            self.assertTrue(result["recoveries"])
            self.assertTrue(engine.project(result,{p["id"]:p["default"] for p in result["parameters"]})["objects"])

    def test_discarded_optional_visual_cannot_hide_unsafe_code_or_numbers(self):
        for x in ("__import__('os')","voltage.real","voltage[0]","101","1/0"):
            raw=copy.deepcopy(self.raw); raw["primitives"][0].update(type="decoration",x=x)
            with self.subTest(x=x),self.assertRaises(Rejection): self.normalize(raw)

    def test_suitability_is_honest_static_need_not_score_high_on_interaction(self):
        raw=copy.deepcopy(self.raw); raw["candidates"][0]["interaction"]=0.
        self.assertTrue(self.normalize(raw)["suitable"])
        for field,value in (("fidelity",.2),("misconception_risk",.8)):
            raw=copy.deepcopy(self.raw); raw["candidates"][0][field]=value
            with self.assertRaises(Rejection): self.normalize(raw)
        raw=copy.deepcopy(self.raw); raw["suitable"]=False; raw["reason"]="No defensible analogy."
        for k in ("formal_entities","analogy_entities","mappings","parameters","quantities","primitives","annotations"): raw[k]=[]
        self.assertFalse(self.normalize(raw)["suitable"])
        raw["reason"]=""
        with self.assertRaises(Rejection): self.normalize(raw)

    def test_one_request_then_mapping_control_and_projection_are_local(self):
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))
        store=state.ensure({},"m","zh-TW","sig"); key=state.identity("m","zh-TW","sig","ohms_law")
        result=compiler.build(store,key,client,"offline",dict(analysis_language="zh-TW"),self.catalog,self.registry,[1])
        workspace=dict(material_id="m",focus="ohms_law",mode="explore"); wrapper=dict(material_id="m"); lab={}
        state.select_entity(result,"pipe_relation",workspace,self.catalog,wrapper)
        state.set_parameter(store,result,"resistance",7.,self.registry,wrapper,lab)
        engine.project(result,state.values(store,result,self.registry,wrapper,lab))
        compiler.build(store,key,client,"offline",dict(analysis_language="zh-TW"),self.catalog,self.registry,[1])
        self.assertEqual(client.responses.create.call_count,1); self.assertEqual(lab,{})


class CapturedShapeAppTests(unittest.TestCase):
    def app(self):
        from test_analogy import AnalogyAppTests
        at,_=AnalogyAppTests().app("queue")
        raw,catalog,registry=captured_case()
        at.session_state["analysis"]["concept_map"]["nodes"]=[dict(id=i,label=i,source_pages=[1],role="primary") for i in catalog]
        at.session_state["learning_workspace"]["focus"]="ohms_law"
        return at,raw

    def test_build_keeps_six_mappings_then_controls_compare_navigation_local(self):
        from analogy import runtime
        at,raw=self.app(); client=MagicMock()
        client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None):
            at.run(); at.button(key="analogy-build-a").click().run()
            self.assertFalse(at.exception)
            store=at.session_state["analogy_world_state"]
            self.assertEqual(len(store["cache"][store["active"]]["mappings"]),6)
            self.assertTrue(any("不是原文證據" in c.value for c in at.caption))
            self.assertTrue(any("概念對應示意" in c.value for c in at.caption))
            next(b for b in at.button if b.label=="parameter_scaling ↔ 整段管路的推動—流量關係").click().run()
            self.assertEqual(at.session_state["learning_workspace"]["focus"],"parameter_scaling")
            next(s for s in at.slider if s.label=="resistance").set_value(7.).run()
            at.radio(key="workspace-representation-a").set_value("compare").run()
            self.assertFalse(at.exception); self.assertEqual(client.responses.create.call_count,1)
            at.radio(key="workspace-mode-a").set_value("source").run()
            at.radio(key="workspace-mode-a").set_value("explore").run()
            self.assertEqual(at.session_state["learning_workspace"]["focus"],"parameter_scaling")
            self.assertEqual(client.responses.create.call_count,1)

    def test_fatal_mapping_retains_diagnostics_and_download_without_other_requests(self):
        from analogy import runtime
        at,raw=self.app(); raw["mappings"][0]["formal_id"]="missing"
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None):
            at.run(); at.button(key="analogy-build-a").click().run()
            self.assertFalse(at.exception)
            store=at.session_state["analogy_world_state"]; trace=next(iter(store["diagnostics"].values()))
            self.assertEqual(trace["code"],"mapping"); self.assertEqual(trace["path"],"$.mappings[0]")
            self.assertIn("normalized",trace)
            self.assertTrue(any(e.label=="譬喻開發診斷" for e in at.expander))
            self.assertFalse(store["cache"]); self.assertEqual(client.responses.create.call_count,1)


if __name__=="__main__": unittest.main()
