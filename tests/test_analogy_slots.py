"""Blank-slot regression and retained-candidate replay. Never makes paid calls.

The second human trace proves rejection at rectangle.radius; its value was not
exported. The blank expression used below is an explicitly synthetic completion,
not a claim that the absent live value has been recovered.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from analogy import compiler, engine, state, runtime
from analogy.diagnostics import Rejection, summary
from analogy.schema import VERSION
from analogy.validator import normalize
from analogy_fixtures import formal, spec, primitive, parameter


def second_captured_case():
    trace=json.loads((Path(__file__).parent/"fixtures/day21_analogy_radius_rejection.json").read_text(encoding="utf-8"))
    captured=trace["generated"]; raw=spec("queue")
    for field in ("reason","formal_focus","selected_candidate","analogy_domain","candidates","analogy_entities","formal_entities"): raw[field]=copy.deepcopy(captured[field])
    raw["version"]=VERSION
    raw["mappings"]=[dict(relationship="Synthetic bounded correspondence.",explains="Synthetic teaching completion.",**m) for m in captured["mappings"]]
    raw["parameters"]=[parameter(p["id"],p["id"],p["min"],p["max"],p["default"],p["mapping_id"]) for p in captured["parameters"]]
    raw["quantities"]=[]; raw["annotations"]=[]
    raw["primitives"]=[primitive(p["id"],p["entity_id"],p["type"],p["entity_id"],control_parameter=p["control_parameter"]) for p in captured["primitives"]]
    for p in raw["primitives"]:
        for field in set(engine.FIELDS)-engine.REQUIRED_FIELDS[p["type"]]-{"visible"}: p[field]=""
    catalog={e["id"]:dict(label=e["id"],pages=e["source_pages"],kind="concept_map",equation="",representations=[]) for e in raw["formal_entities"]}
    return raw,catalog,trace


class VisualSlotTests(unittest.TestCase):
    def setUp(self):
        self.scene,self.catalog=formal("electricity")
        self.registry=state.parameter_registry({"scene":self.scene},{},None,self.catalog)
        self.raw=spec("electricity")

    def normalize(self,raw=None): return normalize(raw or self.raw,self.catalog,self.registry,[1],"voltage")

    def test_all_six_primitives_accept_blank_unused_fields_and_preserve_geometry(self):
        for kind in engine.REQUIRED_FIELDS:
            raw=copy.deepcopy(self.raw)
            p=raw["primitives"][0]; p.update(type=kind,x="1",y="2",x2="3",y2="4",radius=".2",value="5")
            for field in set(engine.FIELDS)-engine.REQUIRED_FIELDS[kind]-{"visible"}: p[field]=" \n "
            result=self.normalize(raw)
            normalized=next(v for v in result["primitives"] if v["id"]==p["id"])
            self.assertEqual(normalized["x"],"1"); self.assertEqual(normalized["y"],"2")
            self.assertTrue(any(r["code"]=="unused_visual_default" for r in result["recoveries"]))
            self.assertTrue(engine.project(result,{v["id"]:v["default"] for v in result["parameters"]})["objects"])

    def test_second_captured_structure_no_longer_depends_on_unused_rectangle_radius(self):
        raw,catalog,trace=second_captured_case()
        self.assertEqual((trace["code"],trace["path"]),("unsafe_expression","$.primitives[0].radius"))
        # Reproduce the old all-slot gate with the explicitly synthetic blank.
        with self.assertRaises(Rejection) as failure: engine.validate_math(copy.deepcopy(raw))
        self.assertEqual(failure.exception.path,"$.primitives[0].radius")
        result=normalize(raw,catalog,{},[1,2],"ohm_law")
        self.assertEqual(len(result["mappings"]),8)
        self.assertEqual(result["primitives"][0]["radius"],"0")
        self.assertTrue(any(p["entity_id"]=="scope_notice" for p in result["primitives"]))
        self.assertEqual(result["formal_entities"],raw["formal_entities"])

    def test_missing_used_geometry_omits_visual_and_retains_semantic_core(self):
        for kind,fields in engine.REQUIRED_FIELDS.items():
            for field in fields:
                raw=copy.deepcopy(self.raw)
                raw["primitives"][0].update(type=kind); raw["primitives"][0][field]=""
                result=self.normalize(raw)
                self.assertFalse(any(p["id"]=="tank" for p in result["primitives"]))
                self.assertTrue(any(p["entity_id"]=="head" for p in result["primitives"]))
                self.assertEqual(result["mappings"],self.raw["mappings"])
                self.assertTrue(any(r["code"]=="incomplete_visual_omitted" for r in result["recoveries"]))

    def test_unsafe_nonempty_unused_slot_is_fatal_with_controlled_problem(self):
        for expression in ("__import__('os')","level.real","level[0]","N/A","undefined_name"):
            raw=copy.deepcopy(self.raw); raw["primitives"][0]["radius"]=expression
            with self.assertRaises(Rejection) as failure: self.normalize(raw)
            self.assertEqual(failure.exception.path,"$.primitives[0].radius")
            self.assertFalse(failure.exception.detail["used_for_geometry"])
            self.assertNotIn(expression,repr(failure.exception.detail))

    def test_missing_visual_cannot_hide_unsafe_other_slots_or_numeric_bounds(self):
        for field,expression in (("y","open('x')"),("y","101"),("y2","-1"),("radius","21")):
            raw=copy.deepcopy(self.raw); raw["primitives"][0]["x"]=""; raw["primitives"][0][field]=expression
            with self.assertRaises(Rejection): self.normalize(raw)

    def test_visible_default_and_whitespace_are_trusted_local_normalization(self):
        raw=copy.deepcopy(self.raw); raw["primitives"][0].update(x="  -2  ",visible=" ",radius="")
        result=self.normalize(raw); p=result["primitives"][0]
        self.assertEqual((p["x"],p["visible"],p["radius"]),("-2","1","0"))

    def test_missing_quantitative_expression_is_still_fatal(self):
        raw=copy.deepcopy(self.raw); raw["quantities"][0]["expression"]=""
        with self.assertRaises(Rejection) as failure: self.normalize(raw)
        self.assertEqual(failure.exception.detail["problem"],"empty")
        self.assertEqual(failure.exception.path,"$.quantities[0].expression")

    def test_math_slot_diagnostics_have_lengths_hashes_and_no_expression_text(self):
        raw=copy.deepcopy(self.raw); raw["primitives"][0]["radius"]=""
        result=summary(raw); slot=result["primitives"][0]["math_slots"]["radius"]
        self.assertEqual((slot["length"],slot["blank"]),(0,True)); self.assertEqual(len(slot["fingerprint"]),16)
        self.assertNotIn("level/tightness",json.dumps(result))

    def test_numeric_failure_retains_field_path_without_executing_or_dumping_text(self):
        raw=copy.deepcopy(self.raw); raw["primitives"][0]["radius"]="1/0"
        with self.assertRaises(Rejection) as failure: self.normalize(raw)
        self.assertEqual((failure.exception.code,failure.exception.path),("numeric_expression","$.primitives[0].radius"))
        self.assertEqual(failure.exception.detail["problem"],"numeric")

    def test_derived_schematic_cards_cannot_exceed_the_object_budget(self):
        from analogy.validator import correspondence_cards
        result=self.normalize()
        token=next(p for p in result["primitives"] if p["type"]=="tokens")
        result["primitives"]=[token|dict(id="group_"+str(n),count=16) for n in range(4)]
        with self.assertRaises(Rejection) as failure: correspondence_cards(result,{"head"},self.catalog)
        self.assertEqual(failure.exception.code,"primitive_work")


class OptionalBindingIsolationTests(unittest.TestCase):
    def setUp(self):
        scene,self.catalog=formal("electricity")
        self.registry=state.parameter_registry({"scene":scene},{},None,self.catalog)
        self.raw=spec("electricity")

    def normalize(self,raw):
        return normalize(raw,self.catalog,self.registry,[1],"voltage")

    def test_omitted_affine_link_does_not_reserve_a_formal_target_in_either_order(self):
        for reverse in (False,True):
            for change in (dict(max=11.),dict(scale=0.),dict(offset=1.)):
                raw=copy.deepcopy(self.raw)
                omitted=raw["parameters"][0]|dict(id="unlinked_level",**change)
                raw["parameters"].insert(0,omitted)
                if reverse: raw["parameters"].reverse()
                with self.subTest(reverse=reverse,change=change):
                    result=self.normalize(raw)
                    by_id={p["id"]:p for p in result["parameters"]}
                    self.assertEqual(by_id["unlinked_level"]["formal_target"],"")
                    self.assertEqual(by_id["level"]["formal_target"],"world:volts")
                    self.assertTrue(any(r["code"]=="binding_omitted" for r in result["recoveries"]))
                    self.assertEqual(result["mappings"],self.raw["mappings"])

    def test_duplicate_surviving_links_and_invalid_semantics_still_reject(self):
        for reverse in (False,True):
            for change in ({},dict(formal_target="world:ohms",max=11.)):
                raw=copy.deepcopy(self.raw)
                raw["parameters"].insert(0,raw["parameters"][0]|dict(id="extra_level",**change))
                if reverse: raw["parameters"].reverse()
                with self.subTest(reverse=reverse,change=change),self.assertRaises(Rejection) as failure:
                    self.normalize(raw)
                self.assertEqual(failure.exception.code,"formal_binding")


class RetainedCandidateTests(unittest.TestCase):
    def setUp(self):
        scene,self.catalog=formal("electricity"); self.registry=state.parameter_registry({"scene":scene},{},None,self.catalog)
        self.raw=spec("electricity"); self.raw["primitives"][0]["radius"]=""
        self.store=state.ensure({},"m","zh-TW","sig"); self.key=state.identity("m","zh-TW","sig","voltage")
        self.client=MagicMock(); self.client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))

    def build(self,force_new=False): return compiler.build(self.store,self.key,self.client,"offline",{"analysis_language":"zh-TW"},self.catalog,self.registry,[1],force_new)

    def test_failed_candidate_revalidates_same_data_without_client_context_or_request(self):
        with patch.object(compiler,"normalize",side_effect=Rejection("unsafe_expression","$.primitives[0].radius")):
            self.assertIsNone(self.build())
        self.assertEqual(self.store["pending"][self.key],self.raw)
        result=compiler.build(self.store,self.key,None,"offline",None,self.catalog,self.registry,[1])
        self.assertTrue(result["suitable"]); self.assertEqual(self.client.responses.create.call_count,1)
        self.assertFalse(self.store["pending"])

    def test_unsafe_saved_candidate_stays_rejected_without_fresh_calls(self):
        self.raw["primitives"][0]["radius"]="__import__('os')"
        self.client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))
        for _ in range(3): self.assertIsNone(self.build())
        self.assertEqual(self.client.responses.create.call_count,1)
        self.assertFalse(self.store["cache"])
        self.assertEqual(self.store["diagnostics"][self.key]["detail"]["field"],"radius")
        self.assertNotIn("__import__",json.dumps(self.store["diagnostics"][self.key]))

    def test_new_generation_is_explicit_pending_is_bounded_and_material_specific(self):
        with patch.object(compiler,"normalize",side_effect=Rejection("unsafe_expression")):
            self.build(); self.build(force_new=True)
            self.assertEqual(self.client.responses.create.call_count,2)
            for n in range(4):
                key=self.key[:-1]+(str(n),)
                compiler.build(self.store,key,self.client,"offline",{"analysis_language":"zh-TW"},self.catalog,self.registry,[1])
        self.assertEqual(len(self.store["pending"]),2)
        state.ensure(self.store,"new","zh-TW","sig"); self.assertFalse(self.store["pending"])

    def test_malformed_envelope_is_not_retained_as_a_replayable_candidate(self):
        raw=copy.deepcopy(self.raw); raw["source_context"]="private source"
        self.client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        self.assertIsNone(self.build()); self.assertFalse(self.store["pending"])
        self.assertNotIn("private source",repr(self.store))

    def test_streamlit_local_recheck_works_without_openai_initialization(self):
        from test_analogy import AnalogyAppTests
        at,raw=AnalogyAppTests().app(); raw["primitives"][0]["radius"]=""
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client) as constructor,patch.object(runtime,"_component",return_value=None):
            with patch.object(compiler,"normalize",side_effect=Rejection("unsafe_expression","$.primitives[0].radius")):
                at.run(); at.button(key="analogy-build-a").click().run()
            self.assertTrue(at.session_state["analogy_world_state"]["pending"])
            at.run()
            self.assertEqual(at.button(key="analogy-build-a").label,"本地重驗已保留的譬喻")
            constructor.side_effect=RuntimeError("must not initialize API")
            at.button(key="analogy-build-a").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(at.session_state["analogy_world_state"]["cache"])
            self.assertEqual(constructor.call_count,1); self.assertEqual(client.responses.create.call_count,1)


if __name__=="__main__": unittest.main()
