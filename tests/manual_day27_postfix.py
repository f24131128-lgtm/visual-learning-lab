"""Empty production app + exact POST_FIX response replay; no paid calls.

Real PDF uploads and normal widget actions; no seeded analysis or generated
code execution. All unrecorded or changed requests are blocked and journaled.
"""
import hashlib
import json
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import streamlit as st
from openai.resources.responses import Responses
from openai.resources.files import Files
from day27_postfix_live import gate, HOME, CASES
from day27_benchmark import read, digest, save_work, helpers

gate()
corpus=read(ROOT/'docs/day27/corpus-manifest.json')
records_dir=HOME/'browser';records_dir.mkdir(parents=True,exist_ok=True)


def replay_log(event):
    with (records_dir/'events.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps(event,ensure_ascii=False)+'\n')


def case_id():
    active=st.session_state.get('analysis_id')
    return next((c['material_id'] for c in corpus['materials'] if c['material_id'] in CASES
        and helpers()['build_analysis_id']('pdf',(ROOT/c['subset_path']).read_bytes(),'en')==active),None)


def upload_replay(client,**kwargs):
    supplied=kwargs.get('file');data=supplied[1] if isinstance(supplied,tuple) else b''
    hashed=hashlib.sha256(data).hexdigest()
    case=next((c for c in corpus['materials'] if c['material_id'] in CASES and c['subset_sha256']==hashed),None)
    if not case:raise ValueError('Not a frozen replay source')
    record=read(HOME/'uploads'/(case['material_id']+'.json'))
    if record.get('error'):raise RuntimeError('Failed upload is retained')
    replay_log(dict(case=case['material_id'],kind='recorded_upload',new_network_requests=0))
    return SimpleNamespace(id=record['file_id'])


def response_replay(client,**kwargs):
    cid=case_id();name=kwargs.get('text',{}).get('format',{}).get('name')
    candidates=[]
    if cid:
        candidates=[read(p) for p in (HOME/'responses').glob(cid+'--*.json')
            if not p.name.endswith(('.request.json','.attempt.json'))]
    record=next((r for r in candidates if r.get('schema_name')==name),None)
    if not record:
        replay_log(dict(case=cid,kind='blocked_unrecorded_response',schema_name=name,new_network_requests=0))
        raise RuntimeError('No recorded POST_FIX attempt; new generation prohibited')
    matches=record['request_sha256']==digest(kwargs)
    replay_log(dict(case=cid,kind='recorded_response',stage=record['stage'],context_matches=matches,new_network_requests=0))
    if not matches:raise ValueError('Production browser request differs from the sealed live request')
    if record.get('error'):raise RuntimeError('Recorded API failure preserved')
    return SimpleNamespace(output_text=record['output_text'],status=record['status'],id=record.get('response_id'),output=[])


Responses.create=response_replay;Files.create=upload_replay
runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
wrapper=st.session_state.get('learning_scene_state') or {}
world=wrapper.get('world') or {};workspace=st.session_state.get('learning_workspace') or {}
atlas=st.session_state.get('source_atlas_state') or {};plans=st.session_state.get('learning_world_plans') or {}
canvas=st.session_state.get('learning_canvas') or {};source=canvas.get('source') or {}
cid=case_id()
save_work(records_dir/(str(cid)+'-session.json'),dict(stage='POST_FIX',case=cid,material=st.session_state.get('analysis_id'),
    mode=workspace.get('mode'),focus=world.get('focus',workspace.get('focus')),world=world,
    scene=wrapper.get('scene'),scene_error=wrapper.get('validation_reason'),
    atlas=atlas.get('atlas'),selected_region=atlas.get('region_hint'),page=atlas.get('page'),
    allowed_pages=st.session_state.get('allowed_source_pages'),
    planner=plans.get('cache',{}).get(plans.get('active')),planner_errors=plans.get('errors'),
    lab=st.session_state.get('interactive_lab_state'),formal_kind=workspace.get('formal_kind'),canvas_selected=canvas.get('selected_id'),
    source_pdf_sha256=hashlib.sha256(source.get('pdf_bytes',b'')).hexdigest(),analysis=st.session_state.get('analysis')))
