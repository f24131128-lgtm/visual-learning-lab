"""Region security, evidence trace, canonical bridge and normal PDF-path QA."""
import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import jsonschema
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler as scene_compiler
from scene.state import fingerprint, cache_key as scene_key
from scene.validator import normalize_scene
from scene.world.validator import normalize_world
from scene.world.state import new_state, apply_patch
from source_lens import get_page_render, new_source_state
from source_atlas import compiler, state
from source_atlas.schema import ATLAS_SCHEMA, MAX_REGIONS, MAX_PER_PAGE
from source_atlas.model import anchors, bbox_valid, evidence_graph, formula_trace, normalize_atlas, rank_pages, semantic_catalog
from source_atlas.runtime import viewer_payload
try:
    from support import ROOT, fixture
    from atlas_fixtures import atlas_fixture, source_pdf, page_texts, region
    from world_fixtures import three_phase_world, complete_projectile_world, spatial_analysis
    from scene_fixtures import two_toss_scene
except ModuleNotFoundError:
    from .support import ROOT, fixture
    from .atlas_fixtures import atlas_fixture, source_pdf, page_texts, region
    from .world_fixtures import three_phase_world, complete_projectile_world, spatial_analysis
    from .scene_fixtures import two_toss_scene


class AtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scene=normalize_world(three_phase_world(),[1,2])
        cls.catalog=semantic_catalog(cls.scene)
        cls.pdf=source_pdf();cls.texts=page_texts(cls.pdf)

    def setUp(self):
        self.raw=atlas_fixture()
        self.atlas=normalize_atlas(self.raw,[1,2],self.catalog,self.texts)
        self.wrapper=dict(material_id="m",scene=self.scene,world=new_state(self.scene))
        self.key=state.cache_key("m",self.pdf,"zh-TW",[1,2],self.scene,self.catalog)
        self.local=dict(key=self.key,atlas=self.atlas,page=1,region_hint=None,seen_focus=None,last_token=None)

    def test_strict_schema_canonical_fixture(self):
        jsonschema.validate(self.raw,ATLAS_SCHEMA)
        self.assertEqual(len(self.atlas["regions"]),6)
        self.assertTrue(self.atlas["regions"][0]["excerpt_verified"])

    def test_invalid_boxes_rejected(self):
        for bad in ((-.1,.1,.8,.8),(.1,.1,1.1,.8),(.8,.1,.2,.8),(.1,.1,.1,.8),(.1,.1,.1001,.1001),(0.,0.,math.nan,.9),(0.,0.,math.inf,.9)):
            raw=copy.deepcopy(self.raw);raw["regions"][0]["bbox"]=dict(zip(("x0","y0","x1","y1"),bad))
            got=normalize_atlas(raw,[1,2],self.catalog)
            self.assertEqual(len(got["regions"]),5);self.assertIn("regions[0].bbox",got["diagnostics"])
        self.assertTrue(bbox_valid(dict(x0=0,y0=0,x1=1,y1=1)))

    def test_impossible_page_drops_region(self):
        self.raw["regions"][0]["page"]=999
        self.assertEqual(len(normalize_atlas(self.raw,[1,2],self.catalog)["regions"]),5)

    def test_wrong_processed_pages_rejects_atlas(self):
        for pages in ([1,999],[1,1],[1],[True,2],[1,2,3,4]):
            self.raw["processed_pages"]=pages
            with self.assertRaisesRegex(ValueError,"processed_pages"):normalize_atlas(self.raw,[1,2],self.catalog)

    def test_region_bounds(self):
        for count in (MAX_PER_PAGE+1,MAX_REGIONS+1):
            raw=atlas_fixture();raw["regions"]=[region("r"+str(i),1,(.1,.1,.3,.3),"a",["ia"]) for i in range(count)]
            with self.assertRaises(ValueError):normalize_atlas(raw,[1,2],self.catalog)

    def test_unknown_semantic_id_dropped(self):
        self.raw["regions"][0]["semantic_ids"]=["invented"]
        got=normalize_atlas(self.raw,[1,2],self.catalog)
        self.assertIn("regions[0].semantic_ids",got["diagnostics"])

    def test_duplicate_identity_rejects_atlas(self):
        self.raw["regions"][1]["region_id"]="formula_a"
        with self.assertRaisesRegex(ValueError,"duplicate"):normalize_atlas(self.raw,[1,2],self.catalog)

    def test_unknown_type_and_code_dropped(self):
        for field,value in (("type","script"),("label","<script>x()</script>"),("source_text_excerpt","<svg onload=evil>"),("grounding_note","x"*401),("semantic_ids",["ia"]*9),("bbox",{"x0":False,"y0":0,"x1":1,"y1":1})):
            raw=copy.deepcopy(self.raw);raw["regions"][0][field]=value
            self.assertTrue(normalize_atlas(raw,[1,2],self.catalog)["diagnostics"])

    def test_parent_cycle_and_related_reference_integrity(self):
        self.raw["regions"][0]["parent_region_id"]="wave_a"
        self.raw["regions"][1]["parent_region_id"]="formula_a"
        got=normalize_atlas(self.raw,[1,2],self.catalog)
        self.assertEqual(len(got["regions"]),4)
        self.raw=atlas_fixture();self.raw["regions"][2]["related_region_ids"]=["unknown"]
        self.assertIn("regions[2].related_region_ids",normalize_atlas(self.raw,[1,2],self.catalog)["diagnostics"])

    def test_related_count_and_unknown_fields(self):
        self.raw["regions"][0]["related_region_ids"]=["vector_b"]*9
        self.assertTrue(normalize_atlas(self.raw,[1,2],self.catalog)["diagnostics"])
        self.raw["html"]="evil"
        with self.assertRaisesRegex(ValueError,"fields"):normalize_atlas(self.raw,[1,2],self.catalog)

    def test_low_confidence_never_draws_box(self):
        self.assertIsNone(self.atlas["regions"][-1]["bbox"])
        render=get_page_render(new_source_state("m",self.pdf),"m",2,[1,2])
        bundle=self.bundle();bundle["state"]["page"]=2
        self.assertNotIn("uncertain",[r["region_id"] for r in viewer_payload(bundle,None,render)["regions"]])

    def test_visual_transcription_is_not_claimed_verified(self):
        self.raw["regions"][0]["source_text_excerpt"]="A handwritten formula not in native text"
        self.assertFalse(normalize_atlas(self.raw,[1,2],self.catalog,self.texts)["regions"][0]["excerpt_verified"])

    def bundle(self):
        return dict(state=self.local,catalog=self.catalog,wrapper=self.wrapper,material_id="m",source=new_source_state("m",self.pdf),allowed=[1,2],source_context=dict(kind="pdf",page_texts=self.texts))

    def test_source_to_canonical_world_preserves_other_state(self):
        before=copy.deepcopy(self.wrapper["world"])
        self.assertTrue(state.select_region(self.local,"vector_b",self.catalog,self.wrapper))
        self.assertEqual(self.wrapper["world"]["focus"],"ib")
        for key in ("time","parameters","baseline","recorded"):self.assertEqual(before[key],self.wrapper["world"][key])
        self.assertEqual(state.sync_region(self.local,"ib")["region_id"],"vector_b")

    def test_world_to_source_changes_page(self):
        state.sync_region(self.local,"ia")
        self.local["page"]=2
        state.sync_region(self.local,"ib")
        self.assertEqual(self.local["page"],1)
        # A quantity whose sole region is on page two automatically navigates.
        self.local["atlas"]["regions"].append(region("period",2,(.1,.3,.4,.5),"Period",["period"]))
        self.assertEqual(state.sync_region(self.local,"period")["page"],2)
        self.assertEqual(self.local["page"],2)

    def test_atlas_without_world_still_inspects_linked_region(self):
        self.assertTrue(state.select_region(self.local,"formula_b",self.catalog))
        self.assertEqual(state.sync_region(self.local,None)["region_id"],"formula_b")

    def test_mult_page_trace_and_evidence_graph(self):
        self.assertEqual({r["page"] for r in anchors(self.atlas,"ib")},{1,2})
        self.assertEqual(anchors(self.atlas,"ib")[0]["region_id"],"vector_b")
        graph=evidence_graph(self.atlas,self.catalog)
        self.assertTrue(any(e["semantic_id"]=="ib" and e["region_id"]=="vector_b" and "vector_b" in e["representation_ids"] for e in graph))

    def test_formula_trace_uses_equation_dag_and_views(self):
        trace=formula_trace(self.atlas["regions"][0],self.catalog)
        self.assertEqual(set(trace["parameters"]),{"Time","Amplitude","Frequency"})
        self.assertIn("Phase A current",trace["quantities"])
        self.assertTrue(any(v["kind"]=="series" for v in trace["representations"]))
        self.assertFalse(any("ia =" in eq for eq in trace["equations"]))

    def test_cache_identity_excludes_local_state(self):
        apply_patch(self.scene,self.wrapper["world"],dict(op="set_parameter",target_id="frequency",value=60))
        self.local.update(page=2,region_hint="formula_b")
        self.assertEqual(self.key,state.cache_key("m",self.pdf,"zh-TW",[2,1],self.scene,self.catalog))
        for args in (("m",self.pdf,"en",[1,2],self.scene,self.catalog),("m",self.pdf,"zh-TW",[1],self.scene,self.catalog),("m",self.pdf+b"changed","zh-TW",[1,2],self.scene,self.catalog)):
            self.assertNotEqual(self.key,state.cache_key(*args))
        altered=copy.deepcopy(self.scene);altered["quantities"][0]["expression"]="0"
        self.assertNotEqual(self.key,state.cache_key("m",self.pdf,"zh-TW",[1,2],altered,self.catalog))

    def test_rejected_cache_not_reused_as_valid(self):
        session={}
        with patch.object(state.st,"session_state",session):
            current=state.ensure_state(self.key);state.save_result(current,None)
            session.pop("source_atlas_state")
            current=state.ensure_state(self.key)
            self.assertTrue(current["attempted"]);self.assertIsNone(current["atlas"])
            state.save_result(current,self.atlas)
            self.assertIsNone(current["error"]);self.assertIsNotNone(current["atlas"])

    def test_ranking_uses_visual_evidence_focus_and_allowed_pages(self):
        ranked=rank_pages(dict(visual_evidence=[dict(page=2),dict(page=999)]),self.catalog,[1,2],"ib")
        self.assertEqual(set(ranked),{1,2})
        self.assertFalse(compiler.suitable({},dict(kind="text"),new_source_state("m"),[],self.catalog))

    def test_request_sends_only_selected_original_images(self):
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))
        source=new_source_state("m",self.pdf)
        raw=compiler.request_atlas(client,"existing-model",dict(analysis_language="zh-TW"),dict(page_texts=self.texts),source,"m",[1,2],[1,2],self.catalog)
        self.assertEqual(raw,self.raw);self.assertEqual(client.responses.create.call_count,1)
        kwargs=client.responses.create.call_args.kwargs
        content=kwargs["input"][0]["content"]
        self.assertEqual(len([c for c in content if c["type"]=="input_image"]),2)
        self.assertFalse(any(c["type"]=="input_file" for c in content))
        self.assertTrue(kwargs["text"]["format"]["strict"])
        self.assertIn("繁體中文",kwargs["instructions"])
        with self.assertRaises(ValueError):compiler.request_atlas(client,"m",{}, {},source,"m",[999],[1,2],self.catalog)
        self.assertEqual(client.responses.create.call_count,1)

    def test_local_region_events_duplicate_stale_wrong_identity(self):
        event=dict(atlas=fingerprint(self.key),focus_stamp=fingerprint("ia"),token="one",region_id="vector_b")
        self.assertTrue(state.consume_event(self.local,event,self.catalog,self.wrapper))
        self.assertFalse(state.consume_event(self.local,event,self.catalog,self.wrapper))
        event["token"]="two"
        self.assertFalse(state.consume_event(self.local,event,self.catalog,self.wrapper))
        event["focus_stamp"]=fingerprint("ib");event["atlas"]="wrong"
        self.assertFalse(state.consume_event(self.local,event,self.catalog,self.wrapper))

    def test_cross_domain_projectile_same_bridge(self):
        world=normalize_world(complete_projectile_world(),[1,2]);catalog=semantic_catalog(world)
        atlas=normalize_atlas(atlas_fixture("projectile"),[1,2],catalog)
        self.local["atlas"]=atlas
        wrapper=dict(material_id="m",scene=world,world=new_state(world))
        self.assertTrue(state.select_region(self.local,"velocity_arrow",catalog,wrapper))
        # Several linked meanings no longer silently choose array position zero.
        self.assertEqual(wrapper["world"]["focus"],"px")
        self.assertTrue(state.set_focus(wrapper,"vx",catalog))
        self.assertEqual(wrapper["world"]["focus"],"vx")
        self.assertIn("Launch speed",formula_trace(atlas["regions"][0],catalog)["parameters"])

    def test_day17_focus_bridge(self):
        scene=normalize_scene(two_toss_scene(),[1,2]);catalog=semantic_catalog(scene)
        wrapper=dict(material_id="m",scene=scene,active_expression="E",selected_focus_id="focus_e",selected_outcome_id=None)
        with patch.object(state.st,"session_state",{}):
            self.assertTrue(state.set_focus(wrapper,"F",catalog));self.assertEqual(wrapper["active_expression"],"F")
            self.assertTrue(state.set_focus(wrapper,"o_hh",catalog));self.assertEqual(state.current_focus(wrapper),"o_hh")

    def test_day17_more_than_two_events_have_source_focus_control(self):
        raw=two_toss_scene();raw["events"].append(dict(id="G",label="Third event",outcome_ids=["o_tt"],source_pages=[2]))
        for view in raw["views"]:view["semantic_ids"].append("G")
        raw["bindings"].append(dict(id="binding_g",semantic_id="G",view_ids=[v["id"] for v in raw["views"]]))
        scene=normalize_scene(raw,[1,2]);catalog=semantic_catalog(scene)
        wrapper=dict(material_id="m",scene=scene,active_expression="E",selected_focus_id="focus_e",selected_outcome_id=None)
        with patch.object(state.st,"session_state",{}):
            self.assertTrue(state.set_focus(wrapper,"G",catalog));self.assertEqual(wrapper["selected_focus_id"],"source_event_G")

    def test_unequal_rotated_cropped_pdf_coordinates(self):
        import pymupdf
        with pymupdf.open(stream=self.pdf,filetype="pdf") as doc:
            doc[0].set_rotation(90);doc[1].set_cropbox(pymupdf.Rect(30,30,760,460));pdf=doc.tobytes()
        source=new_source_state("m",pdf)
        first=get_page_render(source,"m",1,[1,2]);second=get_page_render(source,"m",2,[1,2])
        self.assertGreater(first["width"],first["height"])
        self.assertNotEqual(first["width"]/first["height"],second["width"]/second["height"])
        self.assertIs(first,get_page_render(source,"m",1,[1,2]))

    def test_fixed_frontend_zoom_layers_masks_keyboard_local(self):
        node=shutil.which("node")
        if not node:self.skipTest("Node unavailable; browser/human checks required")
        render=get_page_render(new_source_state("m",self.pdf),"m",1,[1,2])
        result=subprocess.run([node,str(ROOT/"tests/atlas_frontend_smoke.cjs"),str(ROOT/"source_atlas/frontend/index.html")],input=json.dumps(viewer_payload(self.bundle(),self.atlas["regions"][2],render)),text=True,capture_output=True)
        self.assertEqual(result.returncode,0,result.stderr)


class NormalPDFTests(unittest.TestCase):
    def app(self):
        at=AppTest.from_file(str(ROOT/"app.py"),default_timeout=40)
        pdf=source_pdf();analysis=spatial_analysis();analysis["analysis_language"]="zh-TW"
        at.session_state["analysis"]=analysis;at.session_state["analysis_id"]="pdf19"
        at.session_state["learning_workspace"] = dict(material_id="pdf19", mode="source", focus=None)
        at.session_state["source_context"]=dict(kind="pdf",page_texts=page_texts(pdf))
        at.session_state["allowed_source_pages"]=[1,2]
        at.session_state["learning_canvas"]=dict(material_id="pdf19",selected_id=None,kind=None,component=None,style_signature=None,last_event=-1,fallback=False,component_error=False,source=new_source_state("pdf19",pdf))
        scene=normalize_world(three_phase_world(),[1,2])
        at.session_state["learning_scene_cache"]={scene_key("pdf19","zh-TW","spatial_dynamics"):scene}
        at.secrets["OPENAI_API_KEY"]="offline-placeholder"
        return at

    def test_normal_pdf_build_and_two_way_focus_no_local_api(self):
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(atlas_fixture()))
        with patch.object(compiler,"OpenAI",return_value=client),patch.object(canvas,"streamlit_flow",side_effect=lambda key,state,**kw:state):
            at=self.app().run();self.assertFalse(at.exception)
            self.assertTrue(any("Visual Learning Lab" in str(e.value) for e in at.markdown))
            self.assertEqual(client.responses.create.call_count,0)
            at.button(key="atlas-widget-build-pdf19").click().run();self.assertFalse(at.exception)
            self.assertTrue(any("原始來源" in str(e.value) for e in at.markdown));self.assertFalse(any("互動理解" in str(e.value) for e in at.markdown))
            region_select=next(e for e in at.selectbox if e.label=="選取來源物件")
            region_select.set_value("vector_b").run();self.assertFalse(at.exception)
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"],"ib")
            at.radio(key="workspace-mode-pdf19").set_value("explore").run()
            from world_events import world_patch
            world_patch(at,"set_focus","ia",None);self.assertFalse(at.exception)
            at.radio(key="workspace-mode-pdf19").set_value("source").run()
            self.assertEqual(at.session_state["source_atlas_state"]["region_hint"],"formula_a")
            next(e for e in at.selectbox if e.label=="來源頁面").set_value(2).run()
            self.assertFalse(at.exception);self.assertEqual(client.responses.create.call_count,1)
            self.assertTrue(at.button(key="atlas-widget-build-pdf19").disabled)
            at.run()
            self.assertEqual(client.responses.create.call_count,1)

    def test_bad_atlas_isolated_from_existing_world_and_analysis(self):
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text='{"atlas_version":"evil","processed_pages":[1,2],"regions":[]}')
        with patch.object(compiler,"OpenAI",return_value=client),patch.object(canvas,"streamlit_flow",side_effect=lambda key,state,**kw:state):
            at=self.app().run();at.button(key="atlas-widget-build-pdf19").click().run()
            self.assertFalse(at.exception);self.assertIsNone(at.session_state["source_atlas_state"]["atlas"])
            self.assertIsNotNone(at.session_state["learning_scene_state"]["scene"])
            at.radio(key="workspace-mode-pdf19").set_value("learn").run()
            self.assertTrue(any("學習概覽" in str(e.value) for e in at.markdown))
            at.radio(key="workspace-mode-pdf19").set_value("source").run()
            self.assertTrue(at.button(key="atlas-widget-build-pdf19").disabled)
            self.assertEqual(client.responses.create.call_count,1)

    def test_pasted_text_has_no_atlas_cta(self):
        with patch.object(canvas,"streamlit_flow",side_effect=lambda key,state,**kw:state):
            at=self.app();at.session_state["source_context"]=dict(kind="text",source_text="test",page_texts={});at.run()
            self.assertFalse(at.exception);self.assertFalse(any(e.label=="建立來源互動圖譜" for e in at.button))

if __name__=="__main__":unittest.main()
