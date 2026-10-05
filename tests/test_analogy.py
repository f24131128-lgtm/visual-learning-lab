"""Offline safety, cross-domain numerical semantics and workspace request counts."""
import copy
import json
import math
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
import streamlit as st
from streamlit.testing.v1 import AppTest
from analogy import compiler, engine, state, runtime
from analogy.validator import normalize
from analogy.schema import SCHEMA
from workspace.state import get_workspace_focus, set_workspace_focus
from scene.state import fingerprint, cache_key as scene_key
from scene.world.state import new_state, apply_patch, start_recording
from scene.world.engine import snapshot
from analogy_fixtures import formal, spec
from support import ROOT, fixture


class AnalogyLogicTests(unittest.TestCase):
    def setup_case(self,kind="electricity"):
        self.scene,self.catalog=formal(kind)
        self.wrapper=dict(material_id="a",scene=self.scene)
        if self.scene: self.wrapper["world"]=new_state(self.scene)
        self.workspace=dict(material_id="a",mode="explore",focus="fifo" if kind=="queue" else None)
        self.registry=state.parameter_registry(self.wrapper,{},None,self.catalog)
        self.raw=spec(kind); self.spec=normalize(self.raw,self.catalog,self.registry,[1],self.raw["formal_focus"])
        self.store=state.ensure({},"a","zh-TW","signature")
        self.key=state.identity("a","zh-TW","signature",self.raw["formal_focus"])
        state.save(self.store,self.key,self.spec)

    def setUp(self):
        p=patch.object(st,"session_state",{}); p.start(); self.addCleanup(p.stop)
        self.setup_case()

    def test_three_sources_same_strict_schema_and_runtime(self):
        import jsonschema
        for kind in ("electricity","phase","queue"):
            self.setup_case(kind); jsonschema.validate(self.raw,SCHEMA)
            data=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
            self.assertTrue(data["objects"]); self.assertEqual(len(data["times"]),80)
        source=(ROOT/"analogy/runtime.py").read_text()
        self.assertNotIn('kind=="electricity"',source)

    def test_voltage_resistance_flow_are_bidirectional_and_local(self):
        preserved=copy.deepcopy(self.wrapper["world"])
        state.set_parameter(self.store,self.spec,"level",10.,self.registry,self.wrapper,{})
        self.assertEqual(snapshot(self.scene,self.wrapper["world"])["values"]["current"],5.)
        state.set_parameter(self.store,self.spec,"tightness",5.,self.registry,self.wrapper,{})
        self.assertEqual(snapshot(self.scene,self.wrapper["world"])["values"]["current"],2.)
        data=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
        self.assertEqual(next(o for o in data["objects"] if o["id"]=="flow_meter")["data"]["value"][0],2.)
        apply_patch(self.scene,self.wrapper["world"],dict(op="set_parameter",target_id="volts",value=7.))
        self.assertEqual(state.values(self.store,self.spec,self.registry,self.wrapper,{})["level"],7.)
        for k in ("time","focus","baseline"): self.assertEqual(self.wrapper["world"][k],preserved[k])

    def test_phase_updates_pointer_and_wave(self):
        self.setup_case("phase")
        state.set_parameter(self.store,self.spec,"offset",math.pi/2,self.registry,self.wrapper,{})
        data=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
        hand=next(o for o in data["objects"] if o["id"]=="hand")
        signal=next(o for o in data["objects"] if o["id"]=="signal")
        self.assertAlmostEqual(hand["data"]["y2"][0],1.)
        np.testing.assert_allclose(hand["data"]["y2"],signal["data"]["y"])
        self.assertAlmostEqual(snapshot(self.scene,self.wrapper["world"])["values"]["wave"],1.)

    def test_queue_is_qualitative_and_uses_generic_tokens(self):
        self.setup_case("queue"); state.set_parameter(self.store,self.spec,"amount",6.,self.registry,self.wrapper,{})
        data=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
        shown=[o for o in data["objects"] if o["type"]=="tokens" and o["data"]["visible"][0]>=.5]
        self.assertEqual(len(shown),6)
        self.assertFalse(self.spec["parameters"][0]["formal_target"])

    def test_bidirectional_shared_focus_without_shadow(self):
        set_workspace_focus(self.workspace,"resistance",self.catalog,self.wrapper)
        self.assertEqual(state.highlighted(self.spec,self.workspace,self.wrapper),["restriction"])
        self.assertTrue(state.select_entity(self.spec,"flow",self.workspace,self.catalog,self.wrapper))
        self.assertEqual(get_workspace_focus(self.workspace,self.wrapper),"current")
        self.assertNotIn("focus",self.store)
        self.assertFalse(state.select_entity(self.spec,"unknown",self.workspace,self.catalog,self.wrapper))

    def reject(self,mutate):
        raw=copy.deepcopy(self.raw); mutate(raw)
        with self.assertRaises((ValueError,SyntaxError)): normalize(raw,self.catalog,self.registry,[1],self.raw["formal_focus"])

    def test_unsafe_expressions_are_rejected(self):
        for expression in ("__import__('os')","level.real","level[0]","open('x')","[1]*1000000","time > 2","sqrt(-1)","1/0","2**1000000"):
            with self.subTest(expression=expression): self.reject(lambda r:r["primitives"][0].update(x=expression))

    def test_unknown_duplicate_ids_and_broken_refs(self):
        mutations=[lambda r:r["analogy_entities"][0].update(id="voltage"),lambda r:r["mappings"][0].update(formal_id="missing"),lambda r:r["mappings"][0].update(analogy_id="missing"),lambda r:r["primitives"][0].update(entity_id="missing"),lambda r:r["quantities"].append(dict(id="speed",expression="1")),lambda r:r["quantities"][0].update(expression="missing"),lambda r:r["quantities"][1].update(expression="width")]
        for mutation in mutations:
            with self.subTest(mutation=mutation): self.reject(mutation)

    def test_provenance_pages_and_missing_formal_are_rejected(self):
        for pages in ([2],[1,1],[-1]): self.reject(lambda r:r["formal_entities"][0].update(source_pages=pages))
        with self.assertRaises(ValueError): normalize(self.raw,{},self.registry,[1],"voltage")
        self.reject(lambda r:r.update(formal_focus="resistance"))

    def test_limitations_fidelity_and_markup_required(self):
        for mutation in (lambda r:r.update(limitations=[]),lambda r:r["limitations"][0].update(misconception=""),lambda r:r["candidates"][0].update(fidelity=.2),lambda r:r["candidates"][0].update(misconception_risk=.8),lambda r:r["mappings"][0].update(fidelity=.3),lambda r:r["analogy_entities"][0].update(label="<script>alert(1)</script>")):
            self.reject(mutation)

    def test_payload_count_numeric_and_slider_bounds(self):
        for mutation in (lambda r:r["parameters"][0].update(default=float("nan")),lambda r:r["parameters"][0].update(step=True),lambda r:r["primitives"][0].update(count=16),lambda r:r["primitives"][0].update(x="101"),lambda r:r["primitives"][0].update(x2="-1"),lambda r:r["time"].update(frames=10000),lambda r:r.update(primitives=r["primitives"]*8)):
            self.reject(mutation)

    def test_binding_must_have_matching_ranges_and_semantics(self):
        self.reject(lambda r:r["parameters"][0].update(formal_target="world:ohms"))
        # Inconsistent optional affine links are removed, never committed.
        for mutation in (lambda r:r["parameters"][0].update(scale=0),lambda r:r["parameters"][0].update(max=11.),lambda r:r["parameters"][0].update(offset=1.),lambda r:r["mappings"][0].update(mode="qualitative")):
            raw=copy.deepcopy(self.raw); mutation(raw)
            limited=normalize(raw,self.catalog,self.registry,[1],self.raw["formal_focus"])
            self.assertEqual(limited["parameters"][0]["formal_target"],"")
            self.assertTrue(limited["recoveries"])

    def test_actual_changes_fail_atomically(self):
        before=copy.deepcopy(self.wrapper); store=copy.deepcopy(self.store)
        for value in (11.,float("inf"),True,"5"):
            with self.assertRaises(ValueError): state.set_parameter(self.store,self.spec,"level",value,self.registry,self.wrapper,{})
        self.assertEqual(before,self.wrapper); self.assertEqual(store,self.store)
        # A legal corner/default sample does not excuse an unsafe interior value.
        altered=copy.deepcopy(self.spec); altered["primitives"][0]["x"]="1/(level-3)"
        with self.assertRaises(ValueError): state.set_parameter(self.store,altered,"level",3.,self.registry,self.wrapper,{})
        self.assertEqual(before,self.wrapper)

    def test_numeric_payload_contains_no_model_expression(self):
        payload=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
        text=json.dumps(payload)
        self.assertNotIn("level/tightness",text); self.assertNotIn("expression",text)
        self.assertLess(len(text.encode()),450000)

    def test_local_event_stale_duplicate_and_hostile_ignore(self):
        base=dict(identity=fingerprint(self.key),revision=self.store["revision"],token="one",kind="focus",entity="restriction")
        self.assertTrue(state.consume_event(self.store,self.spec,base,self.registry,self.wrapper,{},self.workspace,self.catalog))
        before=copy.deepcopy(self.wrapper)
        for event in (base,base|dict(revision=True),base|dict(identity="old"),base|dict(entity=[],revision=self.store["revision"],token="two")):
            self.assertFalse(state.consume_event(self.store,self.spec,event,self.registry,self.wrapper,{},self.workspace,self.catalog))
        self.assertEqual(before,self.wrapper)

    def test_gesture_updates_formal_and_preserves_recording(self):
        start_recording(self.wrapper["world"])
        event=dict(identity=fingerprint(self.key),revision=self.store["revision"],token="p",kind="parameter",parameter="tightness",value=4.)
        self.assertTrue(state.consume_event(self.store,self.spec,event,self.registry,self.wrapper,{},self.workspace,self.catalog))
        self.assertEqual(self.wrapper["world"]["parameters"]["ohms"],4.)
        self.assertTrue(self.wrapper["world"]["recording"])
        self.assertEqual(len(self.wrapper["world"]["recorded"]),1)

    def test_compiler_one_request_cache_and_retry(self):
        store=state.ensure({},"a","zh-TW","signature")
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))
        data=compiler.context(dict(analysis_language="zh-TW"),dict(kind="text",source_text="V=IR"),self.catalog,self.registry,"voltage",[1])
        for _ in range(3): compiler.build(store,self.key,client,"offline",data,self.catalog,self.registry,[1])
        self.assertEqual(client.responses.create.call_count,1)
        self.assertTrue(client.responses.create.call_args.kwargs["text"]["format"]["strict"])
        self.assertNotIn("pdf",client.responses.create.call_args.kwargs["input"])
        state.set_parameter(store,self.spec,"level",8.,self.registry,self.wrapper,{})
        self.assertEqual(client.responses.create.call_count,1)
        failed=state.ensure({},"b","en","sig")
        client.responses.create.side_effect=RuntimeError("secret")
        self.assertIsNone(compiler.build(failed,self.key,client,"offline",data,self.catalog,self.registry,[1]))
        self.assertNotIn("secret",str(failed)); self.assertNotIn(self.key,failed["cache"])
        client.responses.create.side_effect=None
        self.assertIsNotNone(compiler.build(failed,self.key,client,"offline",data,self.catalog,self.registry,[1]))

    def test_unsuitable_is_cached_and_no_scene(self):
        raw=copy.deepcopy(self.raw); raw["suitable"]=False
        for key in ("formal_entities","analogy_entities","mappings","parameters","quantities","primitives","annotations"): raw[key]=[]
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        store=state.ensure({},"a","en","signature")
        for _ in range(2): result=compiler.build(store,self.key,client,"offline",dict(analysis_language="en"),self.catalog,self.registry,[1])
        self.assertFalse(result["suitable"]); self.assertEqual(client.responses.create.call_count,1)

    def test_cache_bounded_and_identity_excludes_local_values(self):
        original=self.store["identity"]
        for i in range(8): state.save(self.store,self.key[:-1]+(str(i),),self.spec)
        self.assertEqual(len(self.store["cache"]),4)
        self.assertEqual(self.store["identity"],original)
        state.ensure(self.store,"new","zh-TW","signature")
        self.assertFalse(self.store["cache"])

    def test_missing_source_and_oversized_response_isolate_existing_spec(self):
        with self.assertRaises(ValueError): compiler.context({}, {}, self.catalog, self.registry, "voltage", [])
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text=" "*450001)
        before=copy.deepcopy(self.store)
        other=self.key[:-1]+("resistance",)
        self.assertIsNone(compiler.build(self.store,other,client,"offline",dict(analysis_language="en"),self.catalog,self.registry,[1]))
        self.assertEqual(self.store["active"],before["active"]);self.assertEqual(self.store["cache"],before["cache"])

    def test_lab_binding_uses_validated_lesson_ids_and_canonical_values(self):
        self.wrapper["scene"]=None
        demo=dict(id="lab_one",parameters=[dict(id="power",label="Input",min=1.,max=10.,default=5.,step=.1,unit="")],
            related_step_ids=["s1"],x=dict(id="x",min=0.,max=1.,points=50),series=[dict(id="curve",expression="power*x")])
        lab=dict(demos=[demo]); path=dict(steps=[dict(id="s1",visual_refs=[dict(id="voltage")])])
        registry=state.parameter_registry(self.wrapper,lab,path,self.catalog)
        raw=copy.deepcopy(self.raw)
        raw["parameters"][0]["formal_target"]="lab:lab_one:power"
        raw["parameters"][1]["formal_target"]=""
        spec=normalize(raw,self.catalog,registry,[1],"voltage")
        lab_state=dict(demos=dict(lab_one=dict(values=dict(power=5.))))
        state.set_parameter(self.store,spec,"level",8.,registry,self.wrapper,lab_state)
        self.assertEqual(lab_state["demos"]["lab_one"]["values"]["power"],8.)
        lab_state["demos"]["lab_one"]["values"]["power"]=7.
        self.assertEqual(state.values(self.store,spec,registry,self.wrapper,lab_state)["level"],7.)
        self.assertFalse(state.parameter_registry(self.wrapper,lab,None,self.catalog)["lab:lab_one:power"]["semantic_ids"])
        from interactive_lab import select_demo
        st.session_state["learning_workspace"]=self.workspace
        self.workspace["representation"]="analogy"
        select_demo(lab_state,"lab_one")
        self.assertEqual(self.workspace["representation"],"formal")

    def test_static_fallback_and_frontend_clock_transport(self):
        node=shutil.which("node") or str(Path.home()/".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe")
        cases=[]
        for kind in ("electricity","phase","queue"):
            self.setup_case(kind)
            data=engine.project(self.spec,state.values(self.store,self.spec,self.registry,self.wrapper,{}))
            cases.append(dict(identity=kind,numeric_identity=kind,revision=1,data=data,selected=[self.spec["analogy_entities"][0]["id"]],
                parameters=[{k:p[k] for k in ("id","label","min","max")} for p in self.spec["parameters"]],
                labels={k:k for k in ("Play","Pause","Replay","Time","Drag a control horizontally; select a shape to focus its formal concept.")}))
            with patch.object(st,"plotly_chart") as chart:
                runtime.render_static(data,[],kind)
                self.assertTrue(chart.called)
        run=subprocess.run([node,str(ROOT/"tests/analogy_frontend_smoke.cjs"),str(ROOT/"analogy/frontend/index.html")],input=json.dumps(cases),text=True,capture_output=True,timeout=30)
        self.assertEqual(run.returncode,0,run.stdout+run.stderr)

    def test_unsupported_wrap_and_reserved_focus_rejected(self):
        self.reject(lambda r:r["primitives"][0].update(wrap_x=True))
        self.reject(lambda r:r["primitives"][2].update(wrap_min=5.,wrap_max=5.))
        self.reject(lambda r:r["formal_entities"].append(dict(id="time",source_pages=[])))


class AnalogyAppTests(unittest.TestCase):
    def app(self,kind="electricity",cached=False):
        scene,catalog=formal(kind); raw=spec(kind); analysis=fixture()
        if scene: raw["formal_focus"]=scene["objects"][0]["semantic_id"]
        analysis.update(analysis_language="zh-TW",learning_scene_candidate=dict(suitable=bool(scene),domain="spatial_dynamics" if scene else "none",reason="Offline case"))
        if not scene:
            analysis["concept_map"]["nodes"]=[dict(id="fifo",label="先進先出佇列",source_pages=[1],role="primary")]
            analysis["visual_flow"]={"suitable":False,"reason":"","nodes":[],"edges":[]}
        at=AppTest.from_file(str(ROOT/"app.py"),default_timeout=60)
        seed=dict(analysis=analysis,analysis_id="a",source_context=dict(kind="text",source_text="V=IR" if scene else "A queue processes arrivals in first-in-first-out order."),allowed_source_pages=[1],product_language="zh-TW",
            learning_workspace=dict(material_id="a",mode="explore",focus="fifo" if not scene else None,representation="analogy"))
        for key,value in seed.items(): at.session_state[key]=value
        if scene: at.session_state["learning_scene_cache"]={scene_key("a","zh-TW","spatial_dynamics"):scene}
        at.secrets["OPENAI_API_KEY"]="offline"
        return at,raw

    def test_explicit_build_switch_focus_slider_compare_zero_additional_calls(self):
        client=MagicMock(); at,raw=self.app(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None),patch("scene.world.runtime._component",return_value=None):
            at.run(); self.assertFalse(at.exception); client.responses.create.assert_not_called()
            at.button(key="analogy-build-a").click().run(); self.assertFalse(at.exception)
            self.assertEqual(client.responses.create.call_count,1)
            self.assertTrue(at.session_state["analogy_world_state"]["cache"])
            next(s for s in at.slider if s.label=="管道限制").set_value(5.).run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["parameters"]["ohms"],5.)
            next(b for b in at.button if b.label=="電阻 ↔ 管道限制").click().run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"],"resistance")
            self.assertTrue(at.button(key="analogy-build-a").disabled)
            at.radio(key="workspace-representation-a").set_value("compare").run()
            self.assertFalse(at.exception)
            self.assertTrue(any("譬喻在哪裡不成立" in m.value for m in at.markdown))
            self.assertFalse(any("volts/ohms" in c.value for c in at.code))
            at.radio(key="workspace-representation-a").set_value("formal").run(); self.assertFalse(at.exception)
            self.assertEqual(at.selectbox(key="world-widget-a-focus").value,"resistance")
            at.radio(key="workspace-representation-a").set_value("analogy").run()
            self.assertEqual(next(s for s in at.slider if s.label=="管道限制").value,5.)
            next(b for b in at.button if b.label=="重設譬喻控制").click().run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["parameters"]["ohms"],2.)
            self.assertEqual(client.responses.create.call_count,1)

    def test_non_electrical_and_unsuitable_views(self):
        client=MagicMock(); at,raw=self.app("queue"); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None):
            at.run(); at.button(key="analogy-build-a").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(at.session_state["analogy_world_state"]["cache"])
            next(s for s in at.slider if s.label=="排隊人數").set_value(6.).run()
            at.radio(key="workspace-representation-a").set_value("compare").run(); self.assertFalse(at.exception)
            self.assertEqual(client.responses.create.call_count,1)

    def test_frontend_failure_retains_static_controls_and_mappings(self):
        client=MagicMock(); at,raw=self.app(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",side_effect=RuntimeError("unavailable")):
            at.run(); at.button(key="analogy-build-a").click().run()
            self.assertFalse(at.exception)
            self.assertTrue(any(b.label=="電阻 ↔ 管道限制" for b in at.button))
            self.assertTrue(at.get("plotly_chart"))
            next(s for s in at.slider if s.label=="管道限制").set_value(4.).run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["parameters"]["ohms"],4.)
            self.assertEqual(client.responses.create.call_count,1)

    def test_normal_pdf_source_analogy_source_shared_focus_no_compilers(self):
        import pymupdf
        from atlas_fixtures import region,page_texts
        from source_atlas.model import normalize_atlas,semantic_catalog
        from source_atlas.schema import VERSION
        from source_atlas.state import cache_key
        from source_lens import new_source_state
        with pymupdf.open() as doc:
            page=doc.new_page();page.insert_text((50,80),"V = I R");page.insert_text((50,120),"Resistance R")
            pdf=doc.tobytes()
        at,raw=self.app();raw["formal_focus"]="resistance"
        scene=next(iter(at.session_state["learning_scene_cache"].values()))
        catalog=semantic_catalog(scene)
        atlas=normalize_atlas(dict(atlas_version=VERSION,processed_pages=[1],regions=[region("resistor",1,(.05,.12,.6,.23),"電阻 R",["resistance"],"label","labels",excerpt="Resistance R")]),[1],catalog,page_texts(pdf))
        at.session_state["source_context"]=dict(kind="pdf",page_texts=page_texts(pdf))
        at.session_state["learning_workspace"]["mode"]="source"
        at.session_state["learning_canvas"]=dict(material_id="a",selected_id=None,kind=None,component=None,style_signature=None,last_event=-1,fallback=False,component_error=False,source=new_source_state("a",pdf))
        at.session_state["source_atlas_cache"]={cache_key("a",pdf,"zh-TW",[1],scene,catalog):atlas}
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch("source_atlas.runtime._component",return_value=None),patch.object(runtime,"_component",return_value=None),patch("scene.compiler.request_scene") as scene_request,patch("source_atlas.compiler.request_atlas") as atlas_request:
            at.run();self.assertFalse(at.exception)
            at.multiselect(key="atlas-widget-pages-a").set_value([1]).run()
            self.assertFalse(at.exception)
            self.assertTrue(any(s.label=="選取來源物件" for s in at.selectbox))
            next(s for s in at.selectbox if s.label=="選取來源物件").set_value("resistor").run()
            at.radio(key="workspace-mode-a").set_value("explore").run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"],"resistance")
            at.button(key="analogy-build-a").click().run();self.assertFalse(at.exception)
            self.assertTrue(at.session_state["analogy_world_state"]["cache"])
            at.radio(key="workspace-mode-a").set_value("source").run();self.assertFalse(at.exception)
            self.assertEqual(at.session_state["source_atlas_state"]["region_hint"],"resistor")
            self.assertEqual(client.responses.create.call_count,1);scene_request.assert_not_called();atlas_request.assert_not_called()


if __name__=="__main__": unittest.main()
