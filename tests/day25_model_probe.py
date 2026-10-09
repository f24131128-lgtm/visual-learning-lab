"""One optional paid Atlas probe, no retries/regeneration; replay is free.

Fresh existing-schema grounding on an original engineering PDF observes semantic
links; it is not required by the bridge or a real-world source-fidelity score.
"""
import argparse
import ast
import json
import logging
import os
from pathlib import Path
import sys
import tomllib
from types import SimpleNamespace
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import streamlit as st
from twin_fixtures import fixture
from source_lens import new_source_state
from source_atlas.compiler import request_atlas
from source_atlas.model import normalize_atlas
from document_intelligence.model import refine_atlas
from workspace.grounded_twin import derive_links
from manipulation.world import targets
from scene.world.state import new_state


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--live',action='store_true');args=parser.parse_args()
    logging.getLogger('streamlit').setLevel(logging.ERROR)
    home=ROOT/'docs/day25/model';home.mkdir(parents=True,exist_ok=True)
    attempt=home/'attempt.json';raw_path=home/'atlas.json'
    data=fixture('phase')
    if args.live and not attempt.exists():
        from openai import OpenAI
        secret=os.environ.get('OPENAI_API_KEY')
        if not secret:
            config=ROOT/'.streamlit/secrets.toml'
            if not config.exists():
                print('Credentials unavailable; live probe not attempted.');return
            secret=tomllib.loads(config.read_text(encoding='utf-8'))['OPENAI_API_KEY']
        model=next(ast.literal_eval(n.value) for n in ast.parse((ROOT/'app.py').read_text(encoding='utf-8')).body
                   if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODEL' for t in n.targets))
        client=OpenAI(api_key=secret,max_retries=0,timeout=120)
        record=dict(stage='existing Source Atlas vision grounding',model=model,paid_attempts=1,sdk_retries=0,
                    input_tokens=None,output_tokens=None,total_tokens=None,
                    necessary_for_bridge=False,purpose='one fresh grounding observation after deterministic acceptance',
                    source='original synthetic three-page engineering PDF',postcompile_api_delta=0)
        def create(**kwargs):
            attempt.write_text(json.dumps(record,indent=2),encoding='utf-8')
            response=client.responses.create(**kwargs)
            for key in ('input_tokens','output_tokens','total_tokens'):record[key]=getattr(response.usage,key,None)
            record['response_id']=response.id
            attempt.write_text(json.dumps(record,indent=2),encoding='utf-8')
            return response
        facade=SimpleNamespace(responses=SimpleNamespace(create=create))
        try:
            with patch.object(st,'session_state',{}):
                raw=request_atlas(facade,model,data['analysis'],dict(kind='pdf',page_texts=data['texts']),
                    new_source_state(data['material'],data['pdf']),data['material'],[1,2,3],[1,2,3],data['catalog'],
                    data['atlas_state']['document_model'])
            raw_path.write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding='utf-8')
        except Exception as error:
            record['failure_type']=type(error).__name__
            attempt.write_text(json.dumps(record,indent=2),encoding='utf-8')
            print(json.dumps(record,indent=2));return
    if not raw_path.exists():
        print('No recorded Atlas. Use --live for the single optional paid probe.');return
    raw=json.loads(raw_path.read_text(encoding='utf-8'))
    atlas=normalize_atlas(raw,[1,2,3],data['catalog'],data['texts'])
    if data['atlas_state']['document_model']:atlas=refine_atlas(atlas,data['atlas_state']['document_model'])
    state=data['atlas_state']|dict(atlas=atlas)
    links=derive_links(state,data['material'],[1,2,3],data['catalog'],targets(data['scene'],new_state(data['scene'])),
                       document=state['document_model'])
    result=dict(scope='one fresh Atlas declaration on synthetic original PDF with existing deterministic world; human fidelity pending',
                accepted_regions=len(atlas['regions']),dropped_regions=len(atlas['diagnostics']),
                grounded_semantic_ids=list(links),manipulable_semantic_ids=[i for i,l in links.items() if l['manipulable']],
                postcompile_api_delta=0)
    (home/'normalized-atlas.json').write_text(json.dumps(atlas,ensure_ascii=False,indent=2),encoding='utf-8')
    (home/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
