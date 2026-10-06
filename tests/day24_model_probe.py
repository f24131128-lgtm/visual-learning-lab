"""Explicit <=8 live requests, resumable recordings; no regeneration loops.

Uses the three existing acceptance texts, not a new benchmark corpus/holdout.
--live is required for paid calls. Replay revalidates recordings without requests.
"""
import argparse,json,logging,math,os,sys,tomllib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import day23_benchmark as prior
from manipulation_fixtures import SOURCES
from manipulation import world,lab
from learning_world import compiler
from source_atlas.model import semantic_catalog
from scene.compiler import build_scene_context,request_scene,normalize_scene
from scene.world.state import new_state
from scene.world.engine import snapshot
from interactive_lab import default_values

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
 logging.getLogger('streamlit').setLevel(logging.ERROR)
 home=ROOT/'docs/day24/model';home.mkdir(parents=True,exist_ok=True)
 records=list(home.glob('*/analysis.json'))+list(home.glob('*/planner.json'))+list(home.glob('*/scene.json'))
 attempts=sum(json.loads(p.read_text(encoding='utf-8')).get('paid_this_run') is True for p in records)
 budget=dict(remaining=max(0,8-attempts));client=None
 if args.live:
  from openai import OpenAI
  secret=os.environ.get('OPENAI_API_KEY') or tomllib.loads((ROOT/'.streamlit/secrets.toml').read_text(encoding='utf-8'))['OPENAI_API_KEY']
  client=OpenAI(api_key=secret,max_retries=0,timeout=120)
 rows=[];outfile=home/('results.json' if args.live else 'results-replay.json')
 for kind,text in SOURCES.items():
  facade=prior.Responses(home/kind,'live' if args.live else 'replay','gpt-5.6-luna',budget,live_client=client)
  row=dict(case=kind,phase='analysis',target_count=0,postcompile_calls=None,source_fidelity='human review pending')
  try:
   facade.stage='analysis';helpers=prior.load_app_helpers()
   response=facade.create(model=facade.model,instructions=prior.analysis_prompt(),input=text,
      text={'format':dict(type='json_schema',name='visual_learning_analysis',strict=True,schema=helpers['ANALYSIS_SCHEMA'])})
   analysis,path,lab_spec=prior.prepare_analysis(json.loads(response.output_text))
   source=dict(kind='text',source_text=text,page_texts={});catalog=semantic_catalog(None,analysis)
   caps=compiler.capabilities(analysis,{},lab_spec);store=compiler.ensure({},'day24-probe-'+kind)
   key=compiler.identity('day24-probe-'+kind,'en',source,catalog,caps,None)
   facade.stage='planner';row['phase']='planner'
   plan=compiler.build(store,key,facade,facade.model,compiler.context(analysis,source,catalog,[],caps,None),catalog,[],caps)
   row['selected_family']=plan['family'] if plan else None
   row['planner_safe']=bool(plan)
   if kind!='math':
    facade.stage='scene';row['phase']='scene'
    raw=request_scene(facade,facade.model,build_scene_context(analysis,source,[],'spatial_dynamics'))
    scene=normalize_scene(raw,[]);state=new_state(scene);targets=world.targets(scene,state)
    row.update(scene_valid=True,target_count=len(targets),gestures=[t['gesture'] for t in targets])
    facade.local_start=facade.calls
    if targets:
     target=targets[0];angle=.25 if kind=='phase' else math.pi/3
     model=target['inverse'];origin=model['origin'];radius=math.hypot(target['position'][0]-origin[0],target['position'][1]-origin[1])
     ev=dict(scene='probe',revision=0,token='local',kind='manipulate',target=target['id'],x=origin[0]+radius*math.cos(angle),y=origin[1]+radius*math.sin(angle),time=state['time'])
     row['local_commit']=world.commit(scene,state,'probe',ev)
     row['committed_parameters']=state['parameters'];row['focus']=state['focus']
     snapshot(scene,state)
   else:
    facade.local_start=facade.calls;row['phase']='lab'
    demos=lab_spec['demos'];counts=[]
    for demo in demos:
     semantic=lab.semantic_target(demo,path,catalog,analysis);values=default_values(demo);targets=lab.targets(demo,values,semantic);counts.append(len(targets))
     if targets:
      saved=dict(values=values);target=targets[0]
      dy=next(p for p in demo['parameters'] if p['id']==target['inverse']['parameter_id'])
      next_value=(dy['default']+dy['max'])/2
      y=target['inverse']['scale']*next_value+target['inverse']['offset']
      ev=dict(scene='probe',revision=lab.revision(saved),token='local',kind='manipulate',target=target['id'],x=target['position'][0],y=y,time=0.)
      row['local_commit']=lab.commit(demo,saved,'probe',ev,semantic,lambda _:True)
      row['committed_parameters']=saved['values'];row['focus']=semantic
    row['target_count']=sum(counts);row['lab_valid']=bool(demos)
   row['postcompile_calls']=facade.calls-facade.local_start;row['phase']='complete'
  except Exception as error:
   row['failure']=prior.safe_error(error)
  rows.append(row);prior.save(outfile,dict(scope='small recorded declaration probe, no source accuracy score',rows=rows))
 records=list(home.glob('*/analysis.json'))+list(home.glob('*/planner.json'))+list(home.glob('*/scene.json'))
 result=dict(scope='small generated-declaration probe on existing synthetic acceptance texts',rows=rows,
   paid_attempts=sum(json.loads(p.read_text(encoding='utf-8')).get('paid_this_run') is True for p in records),
   tokens={k:sum((json.loads(p.read_text(encoding='utf-8')).get('usage',{}).get(k) or 0) for p in records) for k in ('input_tokens','output_tokens','total_tokens')})
 prior.save(outfile,result);print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
