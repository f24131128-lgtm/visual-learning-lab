"""Two real engines, one inverse contract; offline security and synchronization."""
import ast
import copy
import json
import math
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import MagicMock,patch

import numpy as np
from streamlit.testing.v1 import AppTest
from manipulation import contract,world,lab
from manipulation import runtime
from manipulation.preview import bake,world_projection
from scene.world.engine import snapshot,frames
from scene.world.state import new_state,apply_patch,apply_parameters,start_recording,replay_states,MAX_RECORDING_STEPS
from scene.state import cache_key
from scene.world.validator import normalize_world
from interactive_lab import default_values,compute_curves
from source_atlas.model import semantic_catalog
from workspace.state import get_workspace_focus,open_workspace
try:
 from manipulation_fixtures import systems,math_demo,analysis,SOURCES
 from support import ROOT
except ModuleNotFoundError:
 from .manipulation_fixtures import systems,math_demo,analysis,SOURCES
 from .support import ROOT


def event(target,revision=0,identity="m",x=None,y=None,clock=0.):
 return dict(scene=identity,revision=revision,token="one",kind="manipulate",target=target["id"],
             x=target["position"][0] if x is None else x,y=target["position"][1] if y is None else y,time=clock)


class ManipulationLogicTests(unittest.TestCase):
 def test_circle_parameter_to_forward_projection_both_directions(self):
  scene,_=systems();state=new_state(scene);original=copy.deepcopy(scene)
  target=world.targets(scene,state)[0]
  self.assertEqual(target["gesture"],"drag_on_circle")
  self.assertTrue(world.commit(scene,state,"m",event(target,x=0.,y=1.)))
  self.assertAlmostEqual(state["parameters"]["phase"],math.pi/2)
  values=snapshot(scene,state)
  self.assertAlmostEqual(values["values"]["wave"],1.)
  self.assertAlmostEqual(values["values"]["horizontal"],0.)
  np.testing.assert_allclose(values["projections"]["pointer"],[0.,0.,0.,1.],atol=1e-12)
  self.assertEqual(state["focus"],"angle")
  apply_patch(scene,state,dict(op="set_parameter",target_id="phase",value=-math.pi/2))
  np.testing.assert_allclose(world.targets(scene,state)[0]["position"],[0.,-1.],atol=1e-12)
  self.assertEqual(scene,original)

 def test_circle_at_displayed_time_not_a_second_waveform_state(self):
  scene,_=systems();state=new_state(scene);target=world.targets(scene,state)[0]
  self.assertTrue(world.commit(scene,state,"m",event(target,x=0.,y=1.,clock=.5)))
  self.assertAlmostEqual(state["parameters"]["phase"],math.pi/2-.5)
  self.assertAlmostEqual(snapshot(scene,state)["values"]["wave"],1.)
  self.assertEqual(state["time"],.5)

 def test_polar_endpoint_two_parameters_atomic_time_clamp_and_fit(self):
  _,scene=systems();state=new_state(scene)
  apply_patch(scene,state,dict(op="set_time",target_id="time",value=2.8))
  target=next(t for t in world.targets(scene,state) if t["id"]=="launch")
  self.assertEqual(target["gesture"],"drag_vector_endpoint")
  self.assertTrue(world.commit(scene,state,"m",event(target,state["revision"],x=10*math.cos(math.pi/6),y=5.,clock=state["time"])))
  self.assertAlmostEqual(state["parameters"]["speed"],10.)
  self.assertAlmostEqual(state["parameters"]["angle"],math.pi/6)
  self.assertAlmostEqual(state["time"],10/9.8)
  sampled=frames(scene,state["parameters"])
  self.assertAlmostEqual(sampled["projections"]["path"][1][-1],0.,places=9)
  self.assertGreaterEqual(sampled["axes"]["x_max"],max(sampled["projections"]["path"][0]))
  apply_patch(scene,state,dict(op="set_parameter",target_id="speed",value=30.))
  np.testing.assert_allclose(next(t for t in world.targets(scene,state) if t["id"]=="launch")["position"],[30*math.cos(math.pi/6),15.],atol=1e-10)

 def test_affine_two_anchors_use_existing_lab_values_curves_and_focus(self):
  demo=math_demo();saved=dict(values=default_values(demo),compare=True);seen=[]
  target=lab.targets(demo,saved["values"],"formal_relation")[0]
  self.assertTrue(lab.commit(demo,saved,"m",event(target,lab.revision(saved),y=2.),"formal_relation",lambda i:seen.append(i) or True))
  self.assertEqual(saved["values"],dict(gain=1.,offset=2.))
  target=lab.targets(demo,saved["values"],"formal_relation")[1]
  self.assertTrue(lab.commit(demo,saved,"m",event(target,lab.revision(saved),y=6.)|{"token":"two"},"formal_relation",lambda i:seen.append(i) or True))
  self.assertEqual(saved["values"],dict(gain=2.,offset=2.))
  x,curves=compute_curves(demo,saved["values"])
  np.testing.assert_allclose(curves["relation_curve"],2*x+2)
  saved["values"]["gain"]=-1.
  self.assertEqual(lab.targets(demo,saved["values"],"formal_relation")[1]["position"],[2.,0.])
  self.assertEqual(seen,["formal_relation"]*2)
  self.assertTrue(saved["compare"])

 def test_unknown_or_malicious_events_preserve_all_state(self):
  scene,_=systems();state=new_state(scene);target=world.targets(scene,state)[0];valid=event(target)
  variants=[dict(target="unknown"),dict(scene="other-material"),dict(revision=-1),dict(revision=True),dict(kind="drag_code"),dict(semantic_id="spoof"),dict(patches=[]),dict(time=-1),dict(time=1e6)]
  variants += [{key:value} for key in ("x","y","time") for value in (float('nan'),float('inf'),-float('inf'),1e12,10**500,True,"0",[],None)]
  for fields in variants:
   with self.subTest(fields=str(fields)[:80]):
    before=copy.deepcopy(state)
    self.assertFalse(world.commit(scene,state,"m",valid|fields));self.assertEqual(state,before)
  for key in valid:
   malformed=valid.copy();malformed.pop(key)
   self.assertFalse(world.commit(scene,state,"m",malformed))

 def test_outside_legal_inverse_zero_radius_stale_and_duplicate(self):
  _,scene=systems();state=new_state(scene);t=next(t for t in world.targets(scene,state) if t["id"]=="launch")
  for x,y in ((0.,0.),(1.,1.),(0.,20.),(101.,0.),(-10.,10.)):
   self.assertFalse(world.commit(scene,state,"m",event(t,x=x,y=y)))
  ev=event(t,x=20*math.cos(.9),y=20*math.sin(.9))
  self.assertTrue(world.commit(scene,state,"m",ev));before=copy.deepcopy(state)
  self.assertFalse(world.commit(scene,state,"m",ev));self.assertEqual(state,before)

 def test_reject_nonanalytic_ambiguous_fixed_and_malicious_formulas(self):
  scene,_=systems()
  for expression in ('phase**2+time','phase+time+phase*time','sin(phase)+time'):
   raw=copy.deepcopy(scene)
   # normalized fixtures carry trusted metadata; change only the forward DAG.
   raw['quantities'][0]['expression']=expression
   self.assertEqual(world.targets(raw,new_state(raw)),[])
  raw=copy.deepcopy(scene);raw['parameters'][0].update(min=0.,max=0.,default=0.)
  self.assertEqual(world.targets(raw,new_state(raw)),[])
  demo=math_demo()
  for expr in ('gain*coordinate**2+offset','gain*offset*coordinate','__import__("os")','coordinate.__class__','gain[0]'):
   candidate=copy.deepcopy(demo);candidate['series'][0]['expression']=expr
   self.assertEqual(lab.targets(candidate,default_values(demo),'formal_relation'),[])

 def test_recording_replays_committed_semantics_not_pointer_events(self):
  scene,_=systems();state=new_state(scene);start_recording(state)
  for n,a in enumerate((math.pi/4,math.pi/2)):
   t=world.targets(scene,state)[0]
   self.assertTrue(world.commit(scene,state,'m',event(t,state['revision'],x=math.cos(a),y=math.sin(a))|{'token':str(n)}))
  self.assertEqual(len(state['recorded']),2)
  self.assertTrue(all(x['kind']=='parameters' for x in state['recorded']))
  replay=replay_states(scene,state)
  self.assertAlmostEqual(replay[-1]['parameters']['phase'],math.pi/2)
  state['recorded']*=MAX_RECORDING_STEPS
  with self.assertRaises(ValueError): replay_states(scene,state)

 def test_atomic_failure_never_half_applies_parameters(self):
  scene,_=systems();state=new_state(scene);before=copy.deepcopy(state)
  with self.assertRaises(ValueError): apply_parameters(scene,state,dict(phase=.5,unknown=3),'angle')
  self.assertEqual(state,before)

 def test_begin_focus_commits_canonical_identity_without_value_change(self):
  _,scene=systems();state=new_state(scene);t=next(t for t in world.targets(scene,state) if t['id']=='launch')
  before=copy.deepcopy(state['parameters'])
  ev={k:v for k,v in event(t).items() if k not in ('x','y')}|{'kind':'manipulation_focus'}
  self.assertTrue(world.commit_focus(scene,state,'m',ev))
  self.assertEqual(state['focus'],t['semantic_id']);self.assertEqual(state['parameters'],before)
  self.assertFalse(world.commit_focus(scene,state,'m',ev))
  invalid=ev|{'revision':state['revision'],'token':'next','semantic_id':'spoof'}
  self.assertFalse(world.commit_focus(scene,state,'m',invalid))
  demo=math_demo();saved=dict(values=default_values(demo));target=lab.targets(demo,saved['values'],'formal_relation')[0]
  ev={k:v for k,v in event(target,lab.revision(saved)).items() if k not in ('x','y')}|{'kind':'manipulation_focus'}
  seen=[];self.assertTrue(lab.commit_focus(demo,saved,'m',ev,'formal_relation',lambda i:seen.append(i) or True))
  self.assertEqual(seen,['formal_relation']);self.assertEqual(saved['values'],default_values(demo))

 def test_all_affine_anchors_follow_changed_constant(self):
  demo=math_demo();values=dict(gain=1.,offset=2.)
  anchors=lab.targets(demo,values,'formal_relation')
  self.assertEqual([t['position'] for t in anchors],[[0.,2.],[2.,4.]])
  altered=copy.deepcopy(demo);altered['parameters'].reverse()
  self.assertEqual([t['id'] for t in lab.targets(altered,values,'formal_relation')],[t['id'] for t in anchors])

 def test_preview_lattice_reuses_changed_target_values_not_changed_other_values(self):
  _,scene=systems();state=new_state(scene);wrapper=dict(material_id='m',world=state)
  with patch.object(runtime,'bake',wraps=runtime.bake) as fake:
   runtime.world_payload(scene,wrapper);self.assertEqual(fake.call_count,1)
   apply_patch(scene,state,dict(op='set_parameter',target_id='speed',value=30.))
   runtime.world_payload(scene,wrapper);self.assertEqual(fake.call_count,1)
   apply_patch(scene,state,dict(op='set_parameter',target_id='grav',value=10.))
   runtime.world_payload(scene,wrapper);self.assertEqual(fake.call_count,2)

 def test_numeric_preview_bounds_and_no_model_expressions(self):
  scene,_=systems();state=new_state(scene);wrapper=dict(material_id='m',world=state)
  data=runtime.world_payload(scene,wrapper)
  self.assertTrue(data['previews']['pointer'])
  self.assertNotIn('expression',json.dumps(data))
  self.assertLess(len(json.dumps(data)),1_500_000)
  self.assertNotEqual(data['identity'],runtime.world_payload(scene,dict(material_id='other',world=state))['identity'])
  with self.assertRaises(ValueError): bake(scene['parameters'],state['parameters'],['phase'],lambda _:dict(x=[0.]*100001))
  with self.assertRaises(ValueError): bake(scene['parameters'],state['parameters'],['phase'],lambda _:dict(x=float('nan')))
  for n in range(5):
   apply_patch(scene,state,dict(op='set_parameter',target_id='phase',value=n*.1));runtime.world_payload(scene,wrapper)
  self.assertLessEqual(len(wrapper['manipulation_numeric_cache']),2)

 def test_semantic_bridge_does_not_invent_or_guess_identity(self):
  demo=math_demo();a=analysis('math');catalog=semantic_catalog(None,a)
  self.assertEqual(lab.semantic_target(demo,a['learning_path'],catalog),'formal_relation')
  a['learning_path']['steps'][0]['visual_refs'].append(dict(type='concept_map_node',id='unknown'))
  self.assertEqual(lab.semantic_target(demo,a['learning_path'],catalog),'formal_relation')
  self.assertIsNone(lab.semantic_target(demo,a['learning_path'],{}))
  self.assertEqual(lab.targets(demo,default_values(demo),None),[])

 def test_declared_central_relation_requires_all_explicit_child_links(self):
  demo=math_demo();a=analysis('math');a['concept_map']['nodes'].append(dict(id='coefficient',label='Any label',source_pages=[1],role='primary'))
  a['concept_map']['edges']=[dict(source='formal_relation',target='source_baseline',label='relates'),dict(source='formal_relation',target='coefficient',label='relates')]
  a['learning_path']['steps'][0]['visual_refs']=[dict(id='source_baseline'),dict(id='coefficient')]
  catalog=semantic_catalog(None,a)
  self.assertEqual(lab.semantic_target(demo,a['learning_path'],catalog,a),'formal_relation')
  a['concept_map']['edges'].pop()
  self.assertIsNone(lab.semantic_target(demo,a['learning_path'],catalog,a))
  a['concept_map']['nodes'][1]['role']='central'
  self.assertIsNone(lab.semantic_target(demo,a['learning_path'],catalog,a))

 def test_lab_other_controls_invalidate_old_gestures_even_after_aba(self):
  demo=math_demo();saved=dict(values=default_values(demo));t=lab.targets(demo,saved['values'],'formal_relation')[0]
  stale=event(t,lab.revision(saved),y=2.)
  saved['values']['offset']=1.;lab.revision(saved);saved['values']['offset']=0.;lab.revision(saved)
  self.assertFalse(lab.commit(demo,saved,'m',stale,'formal_relation',lambda _:True))

 def test_topic_name_renaming_does_not_route_the_adapter(self):
  scene,_=systems();state=new_state(scene);before=world.targets(scene,state)
  for group in ('parameters','quantities','objects'):
   for item in scene[group]: item['label']='projectile linear velocity slope phase sinusoid'
  after=world.targets(scene,state)
  self.assertEqual([t['inverse'] for t in before],[t['inverse'] for t in after])
  for path in (ROOT/'manipulation').glob('*.py'):
   syntax=ast.parse(path.read_text(encoding='utf-8'))
   for n in ast.walk(syntax):
    if isinstance(n,ast.Call) and isinstance(n.func,ast.Name): self.assertNotIn(n.func.id,('eval','exec','compile'))
    if isinstance(n,ast.If):
     literals=[x.value for x in ast.walk(n.test) if isinstance(x,ast.Constant) and isinstance(x.value,str)]
     self.assertFalse(set(literals)&{'phase','projectile','linear','sinusoid','velocity','slope'})


class ManipulationFrontendTests(unittest.TestCase):
 def test_fixed_adapter_smoke_and_numeric_inverse_parity(self):
  node=shutil.which('node')
  if not node: self.skipTest('Node required')
  a,b=systems();payloads=[runtime.world_payload(s,dict(material_id='m'+str(n),world=new_state(s))) for n,s in enumerate((a,b))]
  payloads.append(runtime.lab_payload(math_demo(),dict(values=default_values(math_demo())),'math','formal_relation'))
  result=subprocess.run([node,str(ROOT/'tests/manipulation_frontend_smoke.cjs')],input=json.dumps(payloads),capture_output=True,encoding='utf-8',timeout=30)
  self.assertEqual(result.returncode,0,result.stderr)
  self.assertIn('passed',result.stdout)


class ManipulationProductTests(unittest.TestCase):
 def setUp(self):
  self.client=MagicMock()
  self.block=patch('scene.compiler.OpenAI',return_value=self.client)
  self.block.start();self.addCleanup(self.block.stop)

 def app(self,kind):
  at=AppTest.from_file(str(ROOT/'tests/manual_day24.py'),default_timeout=30)
  at.secrets['OPENAI_API_KEY']='offline-placeholder'
  at.run();self.assertFalse(at.exception)
  if kind!='phase':
   at.selectbox(key='day24-case').set_value(kind).run();self.assertFalse(at.exception)
  return at

 def test_normal_pdf_world_gesture_focus_source_roundtrip_zero_requests(self):
  at=self.app('phase')
  calls=[]
  def component(**kw):
   data=kw['payload']
   if not calls:
    calls.append(data)
    return event(data['targets'][0],data['revision'],data['identity'],0.,1.)
   return None
  with patch.object(runtime,'_component',side_effect=component): at.run()
  self.assertFalse(at.exception)
  state=at.session_state['learning_scene_state']['world']
  self.assertAlmostEqual(state['parameters']['phase'],math.pi/2)
  self.assertEqual(state['focus'],'angle')
  before=copy.deepcopy(state)
  at.radio(key='workspace-mode-day24-phase').set_value('source').run()
  self.assertFalse(at.exception)
  self.assertEqual(at.session_state['source_context']['page_texts'][1],SOURCES['phase'])
  at.radio(key='workspace-mode-day24-phase').set_value('explore').run()
  self.assertFalse(at.exception)
  self.assertEqual(at.session_state['learning_scene_state']['world'],before)
  self.client.responses.create.assert_not_called()

 def test_normal_math_lab_gesture_source_roundtrip_and_control_sync(self):
  at=self.app('math');calls=[]
  def component(**kw):
   data=kw['payload']
   if not calls:
    calls.append(data)
    return event(data['targets'][0],data['revision'],data['identity'],0.,2.)
   return None
  with patch.object(runtime,'_component',side_effect=component): at.run()
  self.assertFalse(at.exception)
  saved=at.session_state['interactive_lab_state']['demos']['affine_demo']
  self.assertEqual(saved['values']['offset'],2.)
  self.assertEqual(at.session_state['learning_workspace']['focus'],'formal_relation')
  slider=next(s for s in at.slider if '常數' in s.label)
  self.assertEqual(slider.value,2.)
  slider.set_value(-1.).run();self.assertFalse(at.exception)
  self.assertEqual(at.session_state['interactive_lab_state']['demos']['affine_demo']['values']['offset'],-1.)
  at.radio(key='workspace-mode-day24-math').set_value('source').run()
  self.assertEqual(at.session_state['source_context']['page_texts'][1],SOURCES['math'])
  at.radio(key='workspace-mode-day24-math').set_value('explore').run()
  self.assertFalse(at.exception)
  self.assertEqual(at.session_state['interactive_lab_state']['demos']['affine_demo']['values']['offset'],-1.)
  self.client.responses.create.assert_not_called()

 def test_preview_failure_keeps_regular_world_and_analysis(self):
  at=self.app('projectile')
  with patch('manipulation.runtime.bake',side_effect=ValueError('bounded preview failure')):
   at.session_state['learning_scene_state'].pop('manipulation_numeric_cache',None)
   at.run()
  self.assertFalse(at.exception)
  self.assertEqual(at.session_state['analysis']['quick_summary'],SOURCES['projectile'])
  self.assertTrue(at.slider)
  self.client.responses.create.assert_not_called()


if __name__=='__main__': unittest.main()
