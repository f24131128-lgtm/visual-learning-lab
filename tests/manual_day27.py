"""Normal empty app, real public file uploads, exact first-pass response replay.

No seeded session, fixture, judge, semantic edits or new generation. Responses
are the actual paid first attempts, rechecked by production boundaries. Any
unrecorded request is blocked and journaled. Browser interaction uses unchanged
app.py and its canonical owners. This is replay acceptance, not a second holdout.
"""
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import streamlit as st
from openai.resources.responses import Responses
from openai.resources.files import Files
from day27_benchmark import verify,read,digest,save_work,helpers,PRIVATE,PUBLIC,jsonable

corpus,_=verify()
records_dir=PRIVATE/'browser';records_dir.mkdir(exist_ok=True)
def replay_log(event):
    path=records_dir/'events.jsonl'
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(event,ensure_ascii=False)+'\n')
def case_id():
    active=st.session_state.get('analysis_id')
    for c in corpus['materials']:
        pdf=(ROOT/c['subset_path']).read_bytes()
        if helpers()['build_analysis_id']('pdf',pdf,'en')==active:return c['material_id']
    return None
def upload_replay(client,**kwargs):
    supplied=kwargs.get('file');data=supplied[1] if isinstance(supplied,tuple) else b''
    hashed=hashlib.sha256(data).hexdigest()
    c=next((c for c in corpus['materials'] if c['subset_sha256']==hashed),None)
    if not c:raise ValueError('Not a frozen public source subset')
    record=read(PRIVATE/'uploads'/(c['material_id']+'.json'))
    replay_log(dict(case=c['material_id'],kind='recorded_upload',new_network_requests=0))
    return SimpleNamespace(id=record['file_id'])
def response_replay(client,**kwargs):
    cid=case_id();name=kwargs.get('text',{}).get('format',{}).get('name')
    stage={'visual_learning_analysis':'first-analysis','learning_world_plan_v1':'first-planner',
           'spatial_learning_world_v2':'first-scene','learning_scene_v1':'first-scene',
           'source_atlas_v1':'deep-atlas'}.get(name)
    # Scene names are owned by the production schema; discover matching saved
    # stage by its schema name rather than guess or route by a topic.
    if cid and stage is None:
        for p in (PRIVATE/'responses').glob(cid+'--first-*.json'):
            if p.name.endswith(('.request.json','.attempt.json')):continue
            r=read(p)
            if r.get('schema_name')==name:stage=r['stage'];break
    path=PRIVATE/'responses'/(str(cid)+'--'+str(stage)+'.json')
    if not cid or not stage or not path.exists():
        replay_log(dict(case=cid,kind='blocked_unrecorded_response',schema_name=name,new_network_requests=0))
        raise RuntimeError('No recorded first-attempt response; new generation prohibited')
    record=read(path);matches=record['request_sha256']==digest(kwargs)
    replay_log(dict(case=cid,kind='recorded_response',stage=stage,context_matches=matches,new_network_requests=0))
    if not matches:raise ValueError('Browser production context differs from recorded request')
    if record.get('error'):raise RuntimeError('Recorded API failure preserved')
    return SimpleNamespace(output_text=record['output_text'],status=record['status'],id=record.get('response_id'),output=[])

Responses.create=response_replay;Files.create=upload_replay
runpy.run_path(str(ROOT/'app.py'),run_name='__main__')

wrapper=st.session_state.get('learning_scene_state') or {}
world=wrapper.get('world') or {};workspace=st.session_state.get('learning_workspace') or {}
atlas=st.session_state.get('source_atlas_state') or {};plans=st.session_state.get('learning_world_plans') or {}
canvas=st.session_state.get('learning_canvas') or {};source=canvas.get('source') or {}
cid=case_id()
save_work(records_dir/(str(cid)+'-session.json'),dict(case=cid,material=st.session_state.get('analysis_id'),
    mode=workspace.get('mode'),focus=world.get('focus',workspace.get('focus')),world=world,
    scene=wrapper.get('scene'),scene_error=wrapper.get('validation_reason'),
    atlas=atlas.get('atlas'),selected_region=atlas.get('region_hint'),page=atlas.get('page'),
    allowed_pages=st.session_state.get('allowed_source_pages'),
    planner=plans.get('cache',{}).get(plans.get('active')),planner_errors=plans.get('errors'),
    lab=st.session_state.get('interactive_lab_state'),
    source_pdf_sha256=hashlib.sha256(source.get('pdf_bytes',b'')).hexdigest(),
    analysis=st.session_state.get('analysis')))
