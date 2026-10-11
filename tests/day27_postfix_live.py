"""Bounded POST_FIX production replay. One attempt per case/stage, no retry.

--preflight seals the checked-in production tree only after offline gates pass.
--live is explicit. Gold and reviewer annotations never enter model context.
All model responses are saved before validation in separate private evidence.
"""
import argparse
import copy
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from day27_benchmark import (Observer as BaseObserver, read, sha, digest, write_new,
    save_work, safe_error, pure_reason, source_case, references, declarations)
from day27_postfix_replay import verify_baseline, prepare, helpers
from day23_benchmark import analysis_prompt, probe_process
from model_config import MODEL, response_options
from learning_world import compiler as planner
from source_atlas.model import semantic_catalog, normalize_atlas, rank_pages
from source_atlas.compiler import request_atlas
from source_atlas import state as atlas_state
from source_lens import new_source_state
from scene.compiler import build_scene_context, request_scene, normalize_scene
from interactive_lab import default_values, compute_curves, commit_lab_values
from quantity_contract import can_commit, source_values
from representation_contract import registrations
from manipulation import lab as direct_lab, world as direct_world
from workspace.grounded_twin import derive_links
from workspace.state import focusable, set_workspace_focus, get_workspace_focus, open_workspace
from scene.world.state import new_state, apply_patch
from scene.world.engine import snapshot
from scene.world.policy import time_domain

OUT=ROOT/'docs/day27/post_fix'
HOME=ROOT/'.day27-local/post_fix'
CASES=('regression','probability','circuits','harmonic','signals')


def production_hashes():
    paths=set(ROOT.glob('*.py'))
    for folder in ('scene','analogy','learning_world','workspace','manipulation','source_atlas','document_intelligence'):
        paths.update((ROOT/folder).rglob('*.py'))
        paths.update((ROOT/folder).rglob('*.html'))
        paths.update((ROOT/folder).rglob('*.js'))
    return {p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)}


def gate(seal=False):
    baseline=verify_baseline()
    path=OUT/'live-production-seal.json'
    focused_paths=sorted((OUT/'focused_runs').glob('*.json'))
    if path.exists():
        initial=read(path)['focused_gate_sha256']
        focused_path=next(p for p in focused_paths if sha(p)==initial)
    else:focused_path=focused_paths[-1]
    latest=read(focused_path)
    from day27_postfix_checks import MODULES
    assert latest['modules']==MODULES and latest['failures']==latest['errors']==0
    offline=read(OUT/'offline_runs/02.json')
    assert offline['status']=='PASSED' and offline['case_count']==10 and offline['api_requests']==0
    current=production_hashes()
    if seal and not path.exists():
        write_new(path,dict(stage='POST_FIX',created_utc=datetime.now(timezone.utc).isoformat(),
            baseline=baseline,production_file_hashes=current,production_sha256=digest(current),
            focused_gate_sha256=sha(focused_path),
            offline_gate_sha256=sha(OUT/'offline_runs/02.json'),cases=CASES,
            model=MODEL,reasoning_effort='medium',max_response_requests=20,
            attempts_per_case=1,semantic_retries=0,sdk_retries=0))
    assert read(path)['production_file_hashes']==current,'Production changed after live seal'
    return read(path)


class Observer(BaseObserver):
    def __init__(self,live):
        self.live=live;self.case=None;self.stage=None;self.responses=self
        self.local=False;self.client=None;self.calls=0
        self.directory=HOME/'responses';self.directory.mkdir(parents=True,exist_ok=True)
        self.files=SimpleNamespace(create=self.upload)

    def upload(self,**kwargs):
        path=HOME/'uploads'/(self.case+'.json')
        if path.exists():
            r=read(path)
            if r['status']!='completed':raise RuntimeError('Upload attempt already consumed')
            return SimpleNamespace(id=r['file_id'])
        if not self.live:raise RuntimeError('Live upload disabled')
        write_new(path,dict(stage='POST_FIX',status='started'))
        start=time.perf_counter()
        try:
            response=self.native().files.create(**kwargs)
            save_work(path,dict(stage='POST_FIX',status='completed',file_id=response.id,seconds=time.perf_counter()-start))
            return response
        except Exception as e:
            save_work(path,dict(stage='POST_FIX',status='failed',error=safe_error(e),seconds=time.perf_counter()-start));raise

    def create(self,**kwargs):
        if self.local:raise AssertionError('Local action tried to generate')
        gate()
        assert kwargs['model']==MODEL and kwargs['reasoning']=={'effort':'medium'}
        fmt=kwargs['text']['format'];assert fmt['strict']
        path=self.path('.json');attempt=self.path('.attempt.json')
        if path.exists():
            r=read(path)
            if r.get('error'):raise RuntimeError('Recorded failed attempt; no retry')
            assert r['request_sha256']==digest(kwargs),'Request changed after first attempt'
            return SimpleNamespace(output_text=r['output_text'],status=r['status'],output=[])
        if attempt.exists():raise RuntimeError('Unresolved first attempt; no retry')
        if not self.live:raise RuntimeError('Paid generation disabled')
        if len(list(self.directory.glob('*.attempt.json')))>=20:raise RuntimeError('Live request ceiling reached')
        record=dict(evidence_stage='POST_FIX',case=self.case,stage=self.stage,
            started_utc=datetime.now(timezone.utc).isoformat(),model=kwargs['model'],reasoning=kwargs['reasoning'],
            sdk_retries=0,semantic_retries=0,request_sha256=digest(kwargs),schema_name=fmt['name'],schema_sha256=digest(fmt['schema']))
        write_new(attempt,record);write_new(self.path('.request.json'),kwargs)
        self.calls+=1;start=time.perf_counter();print('REQUEST '+self.case+' '+self.stage,flush=True)
        try:
            response=self.native().responses.create(**kwargs)
            self.path('.output.txt').write_text(response.output_text or '',encoding='utf-8')
            record.update(seconds=time.perf_counter()-start,status=response.status,response_id=response.id,
                returned_model=getattr(response,'model',None),output_text=response.output_text,
                usage=response.usage.model_dump() if response.usage else None)
            raw=json.loads(response.output_text);record['raw']=raw
            import jsonschema
            errors=list(jsonschema.Draft202012Validator(fmt['schema']).iter_errors(raw))
            record.update(schema_valid=not errors,schema_errors=[dict(path=list(e.absolute_path),validator=e.validator) for e in errors[:20]])
            write_new(path,record)
            print('RETURN '+self.case+' '+self.stage+' '+str(round(record['seconds'],2))+'s schema='+str(record['schema_valid']),flush=True)
            return response
        except Exception as e:
            record.update(seconds=time.perf_counter()-start,error=safe_error(e))
            if not path.exists():write_new(path,record)
            print('FAILED '+self.case+' '+self.stage+' '+str(record['error']),flush=True);raise


def lab_probe(demo):
    saved=dict(specification=demo,values=default_values(demo),control_generation=0)
    original=copy.deepcopy(demo);facts=source_values(demo);initial=copy.deepcopy(saved['values'])
    before_curves=compute_curves(demo,initial)[1]
    commits=[];rejections=[]
    for p in demo['parameters']:
        before=copy.deepcopy(saved)
        value=p['min']+.6*(p['max']-p['min']) if p['min']<p['max'] else p['default']+.1
        try:
            commit_lab_values(demo,saved,{p['id']:value})
            assert can_commit(p)
            commits.append(dict(id=p['id'],initial=initial[p['id']],current=saved['values'][p['id']]))
        except ValueError as e:
            assert saved==before
            rejections.append(dict(id=p['id'],provenance=p.get('provenance'),reason=pure_reason(e),atomic=True))
    for fact in demo.get('source_facts',[]):
        before=copy.deepcopy(saved)
        try:commit_lab_values(demo,saved,{fact['id']:fact['value']+.1})
        except ValueError:assert saved==before
        else:raise AssertionError('Source fact was writable')
    after=copy.deepcopy(saved)
    try:commit_lab_values(demo,saved,{'undeclared_control':1.})
    except ValueError:assert saved==after
    else:raise AssertionError('Unknown control committed')
    import numpy as np
    curves=compute_curves(demo,saved['values'])[1]
    assert source_values(demo)==facts and demo==original
    return dict(demo_id=demo['id'],source_facts=demo.get('source_facts',[]),
        source_baseline_immutable=True,initial_values=initial,current_values=saved['values'],
        commits=commits,rejections=rejections,unknown_commit_rejected=True,
        curve_changed=any(not np.allclose(before_curves[k],curves[k]) for k in curves))


def local_probes(bundle,pdf,observer):
    analysis=bundle['analysis'];lab=bundle['lab'];pages=bundle['result']['allowed_pages']
    scene=bundle.get('scene');material=bundle['material'];catalog=semantic_catalog(scene,analysis)
    wrapper=dict(material_id=material,scene=scene)
    if scene and scene['domain']=='spatial_dynamics':wrapper['world']=new_state(scene)
    elif scene:
        target=scene['focus_targets'][0]
        wrapper.update(selected_outcome_id=None,selected_focus_id=target['id'],active_expression=target['expression'],open=True)
    workspace=dict(material_id=material,mode='source',focus=None)
    reps={};handles=[]
    for demo in lab.get('demos',[]):
        rows=registrations(demo,catalog,material,pages)
        for sid,rs in rows.items():reps.setdefault(sid,[]).extend(rs)
        sid=direct_lab.semantic_target(demo,bundle['path'],catalog,analysis)
        if sid in rows:handles.extend(direct_lab.targets(demo,default_values(demo),sid))
    if scene and scene['domain']=='spatial_dynamics':handles=direct_world.targets(scene,wrapper['world'])
    selected=rank_pages(analysis,catalog,pages)[:3]
    bundle.update(catalog=catalog,selected_pages=selected)
    observer.stage='atlas'
    try:
        raw=request_atlas(observer,MODEL,analysis,bundle['source'],new_source_state(material,pdf),material,selected,pages,catalog)
        bundle['raw_atlas']=raw
        atlas=normalize_atlas(raw,selected,catalog,bundle['source']['page_texts'])
        bundle['result']['atlas_validator']='accepted'
    except Exception as e:
        atlas=None;bundle['result'].update(atlas_validator='rejected',atlas_failure=pure_reason(e))
    bundle['atlas']=atlas
    observer.local=True;start=observer.calls
    local=dict(lab=[lab_probe(d) for d in lab.get('demos',[])],source_pdf_unchanged=sha(ROOT/bundle['case']['subset_path'])==bundle['case']['subset_sha256'])
    plan=bundle.get('plan')
    if plan and plan['family']=='process':local['process']=probe_process(plan['process'])
    if scene and scene['domain']=='spatial_dynamics':
        state=wrapper['world'];before=snapshot(scene,state);domain=time_domain(scene,state['parameters'])
        apply_patch(scene,state,dict(op='set_time',target_id='time',value=domain['min']+.4*(domain['max']-domain['min'])))
        local['spatial']=dict(runtime_time_committed=True,projection_changed=before['values']!=snapshot(scene,state)['values'])
    if scene and scene['domain']=='probability_sets':
        from scene.probability import probability
        local['probability']={i:float(probability(scene,s)) for i,s in scene['event_sets'].items()}
    bundle['result']['direct_manipulation']=dict(available=bool(handles),targets=handles,absence_is_not_automatic_failure=True)
    if atlas:
        key=atlas_state.cache_key(material,pdf,'en',selected,scene,catalog)
        astore=dict(key=key,atlas=atlas,region_hint=None,page=selected[0],seen_focus=None,last_token=None)
        links=derive_links(astore,material,pages,catalog,handles,reps,expected_key=key)
        bundle['links']=links
        eligible=[r for r in atlas['regions'] if len([i for i in r['semantic_ids'] if focusable(i,catalog,wrapper)])==1]
        eligible.sort(key=lambda r:(not any(links[i]['representation_ids'] for i in r['semantic_ids'] if i in links),r['region_id']))
        if eligible:
            region=eligible[0];sid=next(i for i in region['semantic_ids'] if focusable(i,catalog,wrapper))
            with patch('streamlit.session_state',{'learning_workspace':workspace}):
                assert set_workspace_focus(workspace,sid,catalog,wrapper)
                assert atlas_state.select_region(astore,region['region_id'],catalog,wrapper)
                source_before=dict(page=astore['page'],region=astore['region_hint']);truth=digest(atlas)
                assert open_workspace(workspace,'explore')
                assert get_workspace_focus(workspace,wrapper)==sid
                assert open_workspace(workspace,'source')
                atlas_state.sync_region(astore,sid)
                local.update(selected_semantic_id=sid,selected_region=region['region_id'],representation_ids=links[sid]['representation_ids'],
                    source_roundtrip=get_workspace_focus(workspace,wrapper)==sid and source_before==dict(page=astore['page'],region=astore['region_hint']),
                    atlas_immutable=digest(atlas)==truth)
        else:local['source_roundtrip']='No unambiguous linked source object; explicit choice needed'
    else:local['source_roundtrip']='Source Atlas unavailable; honest page/text fallback'
    local['post_compilation_api_delta']=observer.calls-start
    bundle['local']=local;bundle['result']['local']=local
    bundle['result']['grounding']='Validated IDs/pages/Atlas links; source semantic fidelity awaits human review'


def one_case(case,observer):
    cid=case['material_id'];observer.case=cid;observer.local=False
    target=HOME/'cases'/(cid+'.json')
    if target.exists():return read(target)['result']
    attempt=HOME/'cases'/(cid+'.attempt.json')
    if attempt.exists():raise RuntimeError('Unresolved case attempt; no regeneration')
    write_new(attempt,dict(stage='POST_FIX',case=cid,attempt=1))
    row=dict(stage='POST_FIX',case=cid,attempt=1,A='HUMAN_REVIEW_PENDING',failures=[],planner_result=None,compiler_result='NOT_APPLICABLE')
    bundle=dict(case=case,result=row,scene=None,plan=None)
    try:
        pdf,upload,extracted,pages,source=source_case(case)
        material=helpers()['build_analysis_id']('pdf',pdf,'en')
        row['allowed_pages']=pages;bundle.update(material=material,source=source)
        observer.stage='main';inp=helpers()['build_analysis_input'](observer,extracted['text'],upload)
        response=observer.create(**response_options(),instructions=analysis_prompt(),input=inp,
            text={'format':dict(type='json_schema',name='visual_learning_analysis',strict=True,schema=helpers()['ANALYSIS_SCHEMA'])})
        raw=json.loads(response.output_text)
        analysis,path,lab,structures,catalog=prepare(raw,pages,material)
        bundle.update(raw_analysis=raw,analysis=analysis,path=path,lab=lab,structures=structures)
        row.update(main_schema=read(observer.path('.json'))['schema_valid'],main_refs=references(raw,pages),lab_rejected=lab['rejected'])
        row['quantity_declarations']=[{k:d.get(k) for k in ('id','source_facts','parameters','series','derived_metrics','x')} for d in lab['demos']]
        catalog={i:v for i,v in catalog.items() if focusable(i,catalog,{})}
        caps=planner.capabilities(analysis,{},lab);data=planner.context(analysis,source,catalog,pages,caps,None)
        bundle.update(planner_catalog=catalog,planner_capabilities=caps,planner_data=data)
        if not catalog:raise ValueError('Production planner disabled: no canonical catalog')
        store=planner.ensure({},material);key=planner.identity(material,'en',source,catalog,caps,None)
        observer.stage='planner';plan=planner.build(store,key,observer,MODEL,data,catalog,pages,caps)
        bundle['plan']=plan;row['planner_result']='accepted' if plan else 'rejected'
        row['planner_diagnostic']=store.get('diagnostics',{}).get(key,{})
        if plan:
            family=plan['family'];row.update(representation_family=family,requested_family=plan['requested_family'],adapted=plan['adapted'])
            if family in ('spatial','structural') or family=='dynamic' and not lab['demos'] and caps.get('spatial'):
                domain='probability_sets' if family=='structural' else 'spatial_dynamics'
                data=build_scene_context(analysis,source,pages,domain);bundle['scene_data']=data
                observer.stage='scene';raw_scene=request_scene(observer,MODEL,data);bundle['raw_scene']=raw_scene
                try:
                    scene=normalize_scene(raw_scene,pages)
                    if scene['domain']!=domain:raise ValueError('Selected scene domain mismatch')
                    bundle['scene']=scene;row['compiler_result']='accepted';row['scene_declarations']=declarations(scene)
                except Exception as e:row.update(compiler_result='rejected',compiler_failure=pure_reason(e))
            elif family=='dynamic':row['compiler_result']='existing validated numeric lab' if lab['demos'] else 'unavailable'
            elif family in ('process','execution'):row['compiler_result']='accepted in planner'
            elif family=='analogy':
                from analogy import compiler as ac
                from analogy.state import parameter_registry,ensure,identity
                registry=parameter_registry(dict(material_id=material),lab,path,catalog);focus=plan['focus_ids'][0]
                adata=ac.context(analysis,source,catalog,registry,focus,pages);observer.stage='analogy'
                artifact=ac.build(ensure({},material,'en','postfix'),identity(material,'en','postfix',focus),observer,MODEL,adata,catalog,registry,pages)
                bundle['analogy']=artifact;row['compiler_result']='accepted' if artifact and artifact.get('suitable') else 'unavailable'
        local_probes(bundle,pdf,observer)
        row['B_scope']='Mechanical backend/ownership checks; browser and A review recorded separately'
    except Exception as e:
        row['failures'].append(safe_error(e) if hasattr(e,'status_code') else pure_reason(e))
    finally:
        observer.local=False;write_new(target,bundle)
    return row


def usage():
    rs=[read(p) for p in sorted((HOME/'responses').glob('*.json')) if not p.name.endswith(('.request.json','.attempt.json'))]
    rows=[{k:r.get(k) for k in ('case','stage','model','returned_model','reasoning','status','seconds','usage','error','schema_valid','response_id','request_sha256','schema_sha256','sdk_retries','semantic_retries')} for r in rs]
    return dict(stage='POST_FIX',model=MODEL,reasoning_effort='medium',request_count=len(rs),
        input_tokens=sum((r.get('usage') or {}).get('input_tokens',0) for r in rs),
        output_tokens=sum((r.get('usage') or {}).get('output_tokens',0) for r in rs),
        total_tokens=sum((r.get('usage') or {}).get('total_tokens',0) for r in rs),
        cached_input_tokens=sum(((r.get('usage') or {}).get('input_tokens_details') or {}).get('cached_tokens',0) for r in rs),
        reasoning_output_tokens=sum(((r.get('usage') or {}).get('output_tokens_details') or {}).get('reasoning_tokens',0) for r in rs),
        response_latency_seconds=sum(r.get('seconds',0) for r in rs),failed_requests=sum(bool(r.get('error')) for r in rs),
        usage_unavailable_requests=sum(not r.get('usage') for r in rs),semantic_retries=0,sdk_retries=0,
        requests=rows,billing_observed=False,original_baseline_totals_unchanged=True,
        scope='Responses requests. PDF uploads recorded separately. This replay is not an untouched holdout.')


def main():
    p=argparse.ArgumentParser();p.add_argument('--preflight',action='store_true');p.add_argument('--live',action='store_true');p.add_argument('--case',choices=CASES);args=p.parse_args()
    if args.preflight:
        seal=gate(True);print(json.dumps(dict(status='OFFLINE_GATES_PASSED',production_sha256=seal['production_sha256'],cases=CASES,paid_requests=0)));return
    if not args.live:raise ValueError('Use --preflight for offline checks; --live is required to consume an attempt')
    gate();corpus=read(ROOT/'docs/day27/corpus-manifest.json');observer=Observer(args.live)
    rows=[]
    for cid in ((args.case,) if args.case else CASES):
        case=next(c for c in corpus['materials'] if c['material_id']==cid)
        row=one_case(case,observer);rows.append(row)
        print('CASE '+cid+' planner='+str(row['planner_result'])+' compiler='+str(row['compiler_result'])+' failures='+str(len(row['failures'])),flush=True)
    save_work(OUT/'request-usage.json',usage())
    existing=[read(HOME/'cases'/(cid+'.json'))['result'] for cid in CASES if (HOME/'cases'/(cid+'.json')).exists()]
    save_work(OUT/'live-replay.json',dict(stage='POST_FIX',status='COMPLETE' if len(existing)==5 else 'IN_PROGRESS',not_untouched_holdout=True,
        selected_cases=CASES,denominator=5,completed_cases=len(existing),cases=existing,A='HUMAN_REVIEW_PENDING',browser='PENDING',
        configuration=dict(model=MODEL,reasoning_effort='medium',attempts_per_case=1,semantic_retries=0,sdk_retries=0)))


if __name__=='__main__':main()
