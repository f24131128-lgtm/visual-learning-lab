"""Live-test consolidated policies, reachable runtime and safety regressions."""

import copy
import math
from types import SimpleNamespace
import json
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene import compiler
from scene import state as cache_state
from scene.validator import normalize_scene
from scene.world import runtime
from scene.world.engine import frames, snapshot
from scene.world.policy import parameter_display, time_domain
from scene.world.schema import VERSION, DOMAIN
from scene.world.state import apply_patch, baseline_action, consume_event, new_state, replay_states, start_recording
from scene.world.validator import normalize_world, WorldValidationError
try:
    from support import ROOT
    from world_fixtures import circular_world, complete_projectile_world, three_phase_world, spatial_analysis
    from scene_fixtures import two_toss_scene
except ModuleNotFoundError:
    from .support import ROOT
    from .world_fixtures import circular_world, complete_projectile_world, three_phase_world, spatial_analysis
    from .scene_fixtures import two_toss_scene


class PolicyTests(unittest.TestCase):
    def assert_inside(self, scene, data):
        a=data["axes"]
        for obj in scene["objects"]:
            n=[np.array(v) for v in data["projections"][obj["id"]]]
            points=[n[:2]]
            if obj["type"] in ("axis", "vector"):
                points.append([n[0]+n[2],n[1]+n[3]])
                if obj["type"] == "axis": points.append([n[0]-n[2],n[1]-n[3]])
            for x,y in points:
                self.assertTrue(np.all((x>=a["x_min"]) & (x<=a["x_max"])))
                self.assertTrue(np.all((y>=a["y_min"]) & (y<=a["y_max"])))

    def projectile(self):
        scene=normalize_world(complete_projectile_world(), [])
        return scene,new_state(scene)

    def test_circular_undersized_hint_normalizes_to_radius_max(self):
        raw=circular_world(); before=copy.deepcopy(raw)
        scene=normalize_world(raw, [])
        self.assertEqual(raw,before)
        self.assertLess(scene["axes"]["x_min"],-10.)
        self.assertGreater(scene["axes"]["y_max"],10.)
        state=new_state(scene);state["parameters"]["radius"]=10.
        self.assert_inside(scene,frames(scene,state["parameters"]))
        self.assertEqual(scene["parameters"][0]["max"],10.)

    def test_periodic_duration_updates_locally(self):
        scene=normalize_world(circular_world(), []);state=new_state(scene)
        before=time_domain(scene,state["parameters"])["max"]
        apply_patch(scene,state,dict(op="set_parameter",target_id="omega",value=4.))
        self.assertAlmostEqual(time_domain(scene,state["parameters"])["max"],before/2)

    def test_three_phase_max_vectors_fit(self):
        raw=three_phase_world();raw["axes"].update(x_min=-.5,x_max=.5,y_min=-.5,y_max=.5)
        scene=normalize_world(raw, [])
        self.assertGreater(scene["axes"]["x_max"],3.)
        self.assert_inside(scene,frames(scene,dict(amplitude=2.,frequency=60.)))

    def test_projectile_complete_flight_ends_at_ground_no_postimpact(self):
        scene,state=self.projectile();data=frames(scene,state["parameters"])
        expected=2*20*math.sin(math.pi/4)/9.8
        self.assertAlmostEqual(data["times"][-1],expected)
        self.assertAlmostEqual(data["values"]["py"][-1],0.,places=10)
        self.assertGreaterEqual(min(data["values"]["py"]),-1e-10)
        self.assert_inside(scene,data)
        with self.assertRaises(ValueError): apply_patch(scene,state,dict(op="set_time",target_id="time",value=expected+.1))

    def test_speed_angle_gravity_each_change_shared_endpoint_and_viewport(self):
        scene,state=self.projectile()
        for identifier,value in (("speed",30.),("angle",math.pi/3),("grav",15.)):
            before=frames(scene,state["parameters"])
            apply_patch(scene,state,dict(op="set_parameter",target_id=identifier,value=value))
            after=frames(scene,state["parameters"])
            self.assertNotEqual(before["domain"],after["domain"])
            self.assertNotEqual(before["axes"],after["axes"])
            self.assertAlmostEqual(after["values"]["py"][-1],0.,places=9)
            self.assert_inside(scene,after)

    def test_shorter_event_clamps_time_atomically(self):
        scene,state=self.projectile()
        end=time_domain(scene,state["parameters"])["max"]
        apply_patch(scene,state,dict(op="set_time",target_id="time",value=end))
        apply_patch(scene,state,dict(op="set_parameter",target_id="speed",value=5.))
        self.assertAlmostEqual(state["time"],time_domain(scene,state["parameters"])["max"])
        self.assertAlmostEqual(snapshot(scene,state)["values"]["py"],0.)

    def test_all_views_and_baseline_share_their_correct_domains(self):
        scene,state=self.projectile();baseline_action(state,"set")
        apply_patch(scene,state,dict(op="set_parameter",target_id="speed",value=40.))
        data=runtime.payload(scene,dict(material_id="flight",world=state))
        d=data["data"];f=data["tables"][d["frames_ref"]];bf=data["tables"][d["baseline_frames_ref"]]
        self.assertEqual(f["domain"],d["current"]["domain"])
        self.assertEqual(bf["domain"],d["baseline"]["domain"])
        self.assertAlmostEqual(f["domain"]["max"],2*bf["domain"]["max"])
        self.assertEqual(f["projections"]["curve_py"][0],f["projections"]["path"][1])
        self.assertNotIn("duration_expression",json.dumps(data))

    def test_angle_degree_radian_display_conversion(self):
        scene,state=self.projectile();p=scene["parameters"][1];d=parameter_display(p)
        self.assertAlmostEqual(d["min"],5.)
        self.assertAlmostEqual(d["max"],85.)
        self.assertAlmostEqual(state["parameters"]["angle"]*d["factor"],45.)
        self.assertAlmostEqual(60/d["factor"],math.pi/3)

    def test_semantic_fallback_expands_usefully_not_renderer_special_case(self):
        raw=complete_projectile_world()
        for p in raw["parameters"]:
            p.update(min=p["default"]*.95,max=p["default"]*1.05,step=p["default"]*.001,range_source="semantic_default")
        scene=normalize_world(raw, [])
        speed,angle,gravity=scene["parameters"]
        self.assertEqual((speed["min"],speed["max"]),(5.,100.))
        self.assertAlmostEqual(parameter_display(angle)["max"],85.)
        self.assertLess(gravity["min"],1.)
        self.assertGreater(gravity["max"],19.)
        for p in scene["parameters"]:self.assertTrue(p["min"]<=p["default"]<=p["max"])
        self.assertGreater(scene["axes"]["x_max"],1000.)

    def test_source_and_pedagogical_ranges_are_preserved(self):
        for source in ("source","pedagogical"):
            raw=complete_projectile_world();raw["parameters"][0]["range_source"]=source
            scene=normalize_world(raw, [1])
            self.assertEqual(scene["parameters"][0],raw["parameters"][0])

    def test_invalid_ranges_never_repaired_by_fallback(self):
        for update in (dict(min=101.),dict(default=1000.),dict(step=0.),dict(min=float("nan"))):
            raw=complete_projectile_world();raw["parameters"][0].update(range_source="semantic_default",**update)
            with self.assertRaises(WorldValidationError):normalize_world(raw, [])

    def test_unsafe_unknown_nonfinite_and_absurd_duration_rejected(self):
        for expression in ("__import__('os')","time+1","py+1","unknown","1/0","-1","10001","exp(1000)"):
            raw=complete_projectile_world();raw["time"]["duration_expression"]=expression
            with self.subTest(expression=expression),self.assertRaises(WorldValidationError):normalize_world(raw, [])

    def test_absurd_viewport_and_coordinates_remain_rejected(self):
        for mutate in (lambda r:r["axes"].update(x_max=1e7),lambda r:r["quantities"][0].update(expression="1e7"),lambda r:r["parameters"][0].update(max=1e9)):
            raw=circular_world();mutate(raw)
            with self.assertRaises(WorldValidationError):normalize_world(raw, [])

    def test_missing_policy_defaults_do_not_supply_missing_base_fields(self):
        raw=three_phase_world()
        for key in ("strategy","duration_expression","periods"):raw["time"].pop(key)
        for p in raw["parameters"]:
            for key in ("quantity_kind","range_source","display_unit"):p.pop(key)
        self.assertEqual(normalize_world(raw, [])["time"]["strategy"],"fixed_duration")
        raw["time"].pop("max")
        with self.assertRaisesRegex(WorldValidationError,"missing fields"):normalize_world(raw, [])

    def test_waveform_patch_propagates_canonical_time_without_compiler(self):
        scene,state=self.projectile();t=time_domain(scene,state["parameters"])["max"]*.65
        event=dict(scene="world",revision=0,token="wave",kind="patch",patch=dict(op="set_time",target_id="time",value=t))
        with patch.object(compiler,"request_scene",side_effect=AssertionError("Local call")):
            self.assertTrue(consume_event(scene,state,"world",event))
        current=snapshot(scene,state)
        self.assertEqual(current["projections"]["body"],current["projections"]["path"])
        self.assertEqual(current["projections"]["body"][1],current["projections"]["curve_py"][0])
        self.assertEqual(current["projections"]["velocity"][:2],current["projections"]["body"])

    def test_replay_preserves_order_filters_only_presentation_noops_and_is_local(self):
        scene,state=self.projectile();start_recording(state)
        for patch_data in (dict(op="set_time",target_id="time",value=0.),dict(op="set_parameter",target_id="speed",value=25.),dict(op="set_time",target_id="time",value=.5),dict(op="set_focus",target_id="py",value=None)):
            apply_patch(scene,state,patch_data)
        state["recording"]=False
        with patch.object(compiler,"request_scene",side_effect=AssertionError("Local call")):
            states=replay_states(scene,state);data=runtime.payload(scene,dict(material_id="record",world=state),states)
        self.assertEqual(data["replay_indices"],[0,2,3,4])
        self.assertEqual(len(state["recorded"]),4)
        self.assertIn("Launch speed",data["replay_summaries"][1])
        self.assertEqual(data["replay"][-1]["current"]["focus"],"py")

    def test_replay_invalid_patch_never_executes(self):
        scene,state=self.projectile();start_recording(state)
        state["recorded"]=[dict(kind="patch",patch=dict(op="set_time",target_id="time",value=100.))]
        before=copy.deepcopy(state)
        with self.assertRaises(ValueError):replay_states(scene,state)
        self.assertEqual(before,state)

    def test_numeric_cache_includes_scene_identity(self):
        scene,state=self.projectile();wrapper=dict(world=state)
        a=runtime.frame_data(scene,wrapper,state["parameters"])
        other=copy.deepcopy(scene);other["title"]="Other validated model"
        b=runtime.frame_data(other,wrapper,state["parameters"])
        self.assertIsNot(a,b)
        self.assertEqual(len(wrapper["world_numeric_cache"]),2)

    def test_probability_still_uses_original_domain_contract(self):
        self.assertEqual(normalize_scene(two_toss_scene(), [1])["domain"],"probability_sets")

    def test_primary_svg_css_does_not_cover_plotly_camera_overlay(self):
        html=(ROOT/"scene/world/frontend/index.html").read_text(encoding="utf-8")
        self.assertNotIn(".panel svg{",html)
        self.assertIn(".panel > svg{",html)
        self.assertIn('src="plotly.min.js"',html)


class ProductPolicyTests(unittest.TestCase):
    def test_normal_result_degrees_derived_duration_and_one_request(self):
        client=MagicMock();client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(complete_projectile_world()))
        with patch.object(compiler,"OpenAI",return_value=client),patch.object(canvas,"streamlit_flow",side_effect=lambda key,state,**kw:state):
            at=AppTest.from_file(str(ROOT/"app.py"),default_timeout=30)
            at.session_state["analysis"]=spatial_analysis();at.session_state["analysis_id"]="complete-flight"
            at.session_state["source_context"]=dict(kind="text",source_text="拋體運動 x=v0 cosθ t，y=v0 sinθ t−g t²/2，回到同一地面。",page_texts={})
            at.session_state["allowed_source_pages"]=[];at.session_state["product_language"]="zh-TW"
            at.session_state["learning_workspace"] = dict(material_id="complete-flight", mode="explore", focus=None)
            at.secrets["OPENAI_API_KEY"]="offline-placeholder";at.run()
            at.button(key="scene-widget-build-complete-flight").click().run()
            self.assertFalse(at.exception)
            from world_events import world_patch
            wrapper=at.session_state["learning_scene_state"]
            angle=next(p for p in runtime.payload(wrapper["scene"],wrapper)["parameters"] if p["id"]=="angle")
            self.assertEqual(angle["display"]["unit"], "°")
            self.assertAlmostEqual(angle["display"]["factor"], 180/math.pi)
            world_patch(at, "set_parameter", "angle", math.pi/3)
            world_patch(at, "set_parameter", "grav", 9.8)
            self.assertFalse(at.exception)
            wrapper=at.session_state["learning_scene_state"]
            self.assertAlmostEqual(wrapper["world"]["parameters"]["angle"],math.pi/3)
            self.assertAlmostEqual(time_domain(wrapper["scene"],wrapper["world"]["parameters"])["max"],2*20*math.sin(math.pi/3)/9.8)
            self.assertFalse(any(e.label=="探索紀錄與回放" for e in at.expander))
            self.assertEqual(client.responses.create.call_count,1)

    def test_new_valid_scene_replaces_rejection_without_reusing_stale_numeric_cache(self):
        scene=normalize_world(three_phase_world(), [])
        session={"learning_scene_cache":{("m","en",VERSION,DOMAIN):None}}
        with patch.object(cache_state.st,"session_state",session):
            state=cache_state.ensure_state("m","en",DOMAIN)
            self.assertIsNone(state["scene"]);self.assertTrue(state["attempted"])
            state["world_numeric_cache"]={"old":"bad"}
            cache_state.save_scene(state,scene)
            self.assertTrue(state["scene"]);self.assertIsNone(state["error"])
            self.assertNotIn("world_numeric_cache",state)
            cache_state.save_rejection(state)
            self.assertIsNone(state["scene"]);self.assertNotIn("world",state)

    def test_incompatible_current_key_cache_does_not_permanently_hide_cta(self):
        scene=normalize_world(three_phase_world(), []);scene["scene_version"]="2.1"
        session={"learning_scene_cache":{("m","en",VERSION,DOMAIN):scene}}
        with patch.object(cache_state.st,"session_state",session):
            state=cache_state.ensure_state("m","en",DOMAIN)
        self.assertFalse(state["attempted"])
        self.assertIsNone(state["scene"])


if __name__=="__main__":unittest.main()
