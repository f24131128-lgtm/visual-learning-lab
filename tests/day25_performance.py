"""Bounded original fixtures, hot median timings; not RSS, FPS or Cloud latency."""
import copy
import json
import logging
import statistics
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from unittest.mock import patch
import streamlit as st
from twin_fixtures import fixture
from manipulation import world,lab
from scene.world.state import new_state,apply_patch
from source_atlas.state import select_region,sync_region
from workspace.grounded_twin import derive_links
from workspace.state import get_workspace_state,open_workspace
from manipulation_fixtures import math_demo
from interactive_lab import default_values


def timed(fn,n=31,setup=None):
    values=[]
    for _ in range(n):
        if setup:setup()
        start=time.perf_counter();fn();values.append((time.perf_counter()-start)*1000)
    return round(statistics.median(values),4)


def main():
    logging.getLogger('streamlit').setLevel(logging.ERROR)
    rows=[]
    with patch.object(st,'session_state',{}):
        for kind in ('phase','projectile','math'):
            d=fixture(kind);state=d['atlas_state'];workspace=get_workspace_state(d['material'])
            wrapper=dict(material_id=d['material'],scene=d['scene'])
            if d['scene']:
                wrapper['world']=new_state(d['scene']);targets=world.targets(d['scene'],wrapper['world']);reps={}
            else:
                demo=math_demo();targets=lab.targets(demo,default_values(demo),d['semantic']);reps={d['semantic']:[dict(id='relation_curve')]}
            def derive():return derive_links(state,d['material'],[1,2,3],d['catalog'],targets,reps,state['document_model'],state['key'])
            links=derive();blob=json.dumps(links,ensure_ascii=False,allow_nan=False).encode()
            def click():
                sync_region(state,d['derived']);select_region(state,'source_object',d['catalog'],wrapper)
            def unfocus():
                if d['scene']:apply_patch(d['scene'],wrapper['world'],dict(op='set_focus',target_id=d['derived'],value=None))
                else:workspace['focus']=d['derived']
            def reverse():
                sync_region(state,d['derived']);sync_region(state,d['semantic'])
            def navigate():
                open_workspace(workspace,'explore');open_workspace(workspace,'source');sync_region(state,d['semantic'])
            rows.append(dict(case=kind,derivation_median_ms=timed(derive),source_click_focus_median_ms=timed(click,setup=unfocus),
                focus_region_median_ms=timed(reverse),navigation_median_ms=timed(navigate),link_bytes=len(blob),
                manipulation_target_count=sum(len(x['manipulation_target_ids']) for x in links.values())))
    out=ROOT/'docs/day25/performance.json';out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(dict(scope='31 hot local repetitions, original synthetic PDFs, no network requests; bridge only, not frame construction',rows=rows),indent=2),encoding='utf-8')
    print(json.dumps(rows,indent=2))

if __name__=='__main__':main()
