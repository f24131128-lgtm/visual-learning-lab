"""Day27 real-source observer. No production overrides, quality retries or A verdicts.

--live is required for paid execution. Each stage has a write-once attempt
journal; an existing successful response can be replayed, never regenerated.
All gold stays outside model context. Production and frozen hashes are checked.
"""
import argparse
import copy
import hashlib
import io
import json
import logging
import math
import os
import sys
import time
import tomllib
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
PUBLIC=ROOT/'docs/day27'; PRIVATE=ROOT/'.day27-local'
from support import load_app_helpers
from day23_benchmark import analysis_prompt, probe_process, probe_lab
from model_config import MODEL, response_options
from learning_world import compiler as planner
from source_atlas.model import semantic_catalog, normalize_atlas, rank_pages
from source_atlas.compiler import request_atlas
from source_atlas import state as atlas_state
from scene.compiler import build_scene_context, request_scene, normalize_scene
from scene.world.state import new_state, apply_patch, apply_parameters
from scene.world.engine import snapshot, frames
from scene.world.policy import time_domain
from scene.probability import probability, monte_carlo
from interactive_lab import clean_interactive_lab, default_values, compute_curves
from manipulation import world as direct_world, lab as direct_lab
from workspace.state import focusable, set_workspace_focus, get_workspace_focus, open_workspace
from workspace.grounded_twin import derive_links, comparison_rows
from source_lens import new_source_state
from scene.state import fingerprint

HELPERS=None
def helpers():
    global HELPERS
    if HELPERS is None:HELPERS=load_app_helpers()
    return HELPERS
def read(path):return json.loads(path.read_text(encoding='utf-8'))
def jsonable(value):
    if isinstance(value,dict):return {k if isinstance(k,str) else json.dumps(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(set,frozenset)):return sorted(jsonable(v) for v in value)
    if isinstance(value,(list,tuple)):return [jsonable(v) for v in value]
    if hasattr(value,'tolist'):return value.tolist()
    return value
def digest(value):return hashlib.sha256(json.dumps(jsonable(value),ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write_new(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf-8',newline='\n') as f:
        json.dump(jsonable(value),f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def save_work(path,value):
    # Only unfrozen per-stage working observations, never source/gold/results.
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(jsonable(value),ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    tmp.replace(path)
def safe_error(error):
    result={'type':type(error).__name__}
    if type(getattr(error,'status_code',None)) is int:result['http_status']=error.status_code
    return result
def pure_reason(error):return str(error).replace('\n',' ')[:500]
def verify():
    lock=read(PUBLIC/'expectation-freeze.json')
    for name,value in lock['files_sha256'].items():
        if sha(PUBLIC/name)!=value:raise ValueError('Frozen file changed: '+name)
    baseline=read(PUBLIC/'prebenchmark-baseline.json')
    for name,value in baseline['production_file_hashes'].items():
        if sha(ROOT/name)!=value:raise ValueError('Production baseline changed: '+name)
    corpus=read(PUBLIC/'corpus-manifest.json')
    for case in corpus['materials']:
        if sha(ROOT/case['subset_path'])!=case['subset_sha256']:raise ValueError('Source subset changed')
    return corpus,read(PUBLIC/'frozen-expectations.json')

class Observer:
    def __init__(self,live=False):
        self.live=live;self.stage=None;self.case=None;self.responses=self
        self.local=False;self.client=None;self.calls=0
        self.directory=PRIVATE/'responses';self.directory.mkdir(exist_ok=True)
        self.files=SimpleNamespace(create=self.upload)
    def native(self):
        if self.client is None:
            from openai import OpenAI
            key=os.environ.get('OPENAI_API_KEY')
            if not key:
                with (ROOT/'.streamlit/secrets.toml').open('rb') as f:key=tomllib.load(f)['OPENAI_API_KEY']
            self.client=OpenAI(api_key=key,max_retries=0,timeout=240)
        return self.client
    def path(self,suffix):return self.directory/(self.case+'--'+self.stage+suffix)
    def upload(self,**kwargs):
        path=PRIVATE/'uploads'/(self.case+'.json');path.parent.mkdir(exist_ok=True)
        if path.exists():
            record=read(path)
            if record.get('error'):raise RuntimeError('Recorded upload failed; no retry')
            return SimpleNamespace(id=record['file_id'])
        if not self.live:raise RuntimeError('Live upload disabled')
        write_new(path,dict(status='started'))
        start=time.perf_counter()
        try:
            response=self.native().files.create(**kwargs)
            save_work(path,dict(status='completed',file_id=response.id,seconds=time.perf_counter()-start))
            return response
        except Exception as error:
            save_work(path,dict(status='failed',error=safe_error(error),seconds=time.perf_counter()-start));raise
    def create(self,**kwargs):
        if self.local:raise AssertionError('Response request attempted during local interaction')
        verify()
        if kwargs.get('model')!=MODEL or kwargs.get('reasoning')!={'effort':'medium'}:raise ValueError('Owned production model configuration changed')
        if not kwargs.get('text',{}).get('format',{}).get('strict'):raise ValueError('Strict output missing')
        path=self.path('.json');attempt=self.path('.attempt.json')
        if path.exists():
            record=read(path)
            if record.get('error'):raise RuntimeError('Recorded request failed; no retry')
            if record['request_sha256']!=digest(kwargs):raise ValueError('Recorded request context changed')
            return SimpleNamespace(output_text=record['output_text'],status=record['status'],output=[])
        if attempt.exists():raise RuntimeError('Earlier unresolved attempt; no retry')
        if not self.live:raise RuntimeError('Paid execution disabled')
        if len(list(self.directory.glob('*.attempt.json')))>=60:raise RuntimeError('Bounded evaluation request ceiling')
        stage_schema=kwargs['text']['format']
        record=dict(case=self.case,stage=self.stage,started_utc=datetime.now(timezone.utc).isoformat(),
            model=kwargs['model'],reasoning=kwargs['reasoning'],sdk_retries=0,semantic_retries=0,
            request_sha256=digest(kwargs),schema_name=stage_schema['name'],schema_sha256=digest(stage_schema['schema']))
        write_new(attempt,record);write_new(self.path('.request.json'),kwargs)
        self.calls+=1;start=time.perf_counter()
        print('REQUEST '+self.case+' '+self.stage,flush=True)
        try:
            response=self.native().responses.create(**kwargs)
            # Persist unparsed response text BEFORE schema/semantic validation.
            self.path('.output.txt').write_text(response.output_text or '',encoding='utf-8')
            record.update(seconds=time.perf_counter()-start,status=response.status,response_id=response.id,
                returned_model=getattr(response,'model',None),output_text=response.output_text,
                usage=response.usage.model_dump() if response.usage else None)
            raw=json.loads(response.output_text)
            record['raw']=raw
            import jsonschema
            errors=list(jsonschema.Draft202012Validator(stage_schema['schema']).iter_errors(raw))
            record['schema_valid']=not errors
            record['schema_errors']=[dict(path=list(e.absolute_path),validator=e.validator) for e in errors[:20]]
            write_new(path,record)
            print('RETURN '+self.case+' '+self.stage+' '+str(round(record['seconds'],2))+'s schema='+str(record['schema_valid']),flush=True)
            return response
        except Exception as error:
            record.update(seconds=time.perf_counter()-start,error=safe_error(error))
            if not path.exists():write_new(path,record)
            print('FAIL '+self.case+' '+self.stage+' '+str(record['error']),flush=True);raise

def source_case(case):
    h=helpers();pdf=(ROOT/case['subset_path']).read_bytes();upload=io.BytesIO(pdf);upload.name=case['material_id']+'.pdf'
    extracted=h['extract_pdf_text'](upload)
    pages=extracted['analyzed_page_numbers']
    source=dict(kind='pdf',page_texts=extracted['analyzed_page_texts'],source_text=extracted['text'])
    return pdf,upload,extracted,pages,source
def prepare(raw,pages):
    h=helpers();analysis=copy.deepcopy(raw);analysis['analysis_language']='en'
    decision=h['clean_primary_visualization'](raw.get('primary_visualization'))
    structures={key:h['clean_'+key](raw.get(key),pages) for key in ('concept_map','visual_flow','comparison')}
    visual=structures.get({'flow':'visual_flow','concept_map':'concept_map','comparison':'comparison'}.get(decision['type']))
    path=h['clean_learning_path'](raw.get('learning_path'),pages,decision['type'],visual)
    lab=clean_interactive_lab(raw.get('interactive_lab'),pages,path,h['valid_source_pages'])
    return analysis,path,lab,structures
def references(value,pages):
    declared=[];invalid=[]
    def visit(v,path='$'):
        if isinstance(v,dict):
            for k,item in v.items():
                if k in ('source_pages','page'):
                    ns=item if isinstance(item,list) else [item]
                    for n in ns:
                        declared.append(dict(path=path+'.'+k,page=n))
                        if type(n) is not int or n not in pages:invalid.append(dict(path=path+'.'+k,page=n))
                else:visit(item,path+'.'+k)
        elif isinstance(v,list):
            for i,item in enumerate(v):visit(item,path+'['+str(i)+']')
    visit(value)
    return dict(declared_count=len(declared),declared=declared,invalid=invalid,valid=not invalid)
def declarations(spec):
    if not isinstance(spec,dict):return {}
    return {k:spec.get(k) for k in ('domain','scene_version','parameters','quantities','bindings','inverse_bindings','time','objects','series','metrics','outcomes','events','focus_targets') if k in spec}
def lab_declarations(lab):
    return [dict(id=d['id'],source_pages=d['source_pages'],parameters=d['parameters'],x=d['x'],series=d['series'],derived_metrics=d['derived_metrics']) for d in lab.get('demos',[])]
def affordances(scene,lab,path,analysis):
    if scene and scene['domain']=='spatial_dynamics':return direct_world.targets(scene,new_state(scene))
    catalog=semantic_catalog(scene,analysis);result=[]
    for demo in lab.get('demos',[]):
        owner=direct_lab.semantic_target(demo,path,catalog,analysis)
        result+=direct_lab.targets(demo,default_values(demo),owner)
    return result
def local_probe(scene,lab,plan):
    if scene and scene['domain']=='spatial_dynamics':
        state=new_state(scene);before=snapshot(scene,state)
        domain=time_domain(scene,state['parameters'])
        apply_patch(scene,state,dict(op='set_time',target_id='time',value=(domain['min']+domain['max'])/2))
        after=snapshot(scene,state);data=frames(scene,state['parameters'])
        return dict(kind='spatial',snapshot_changed=before['values']!=after['values'],frames=len(data['times']),canonical_revision=state['revision'])
    if scene and scene['domain']=='probability_sets':
        sets=list(scene['event_sets'].values());p=probability(scene,sets[0])
        return dict(kind='probability',local_exact_probability=float(p),monte_carlo=monte_carlo(scene,sets[0],100,seed=27))
    if plan and plan['family']=='process':return dict(kind='process',**probe_process(plan['process']))
    if plan and plan['family']=='execution':
        from learning_world import execution
        state=execution.initial(plan['execution']);return dict(kind='execution',initial=state)
    if plan and plan['family']=='dynamic' and lab.get('demos'):return dict(kind='numeric_lab',**probe_lab(lab))
    return dict(kind='formal',local_reading_available=True)

def first_case(case,observer):
    cid=case['material_id'];observer.case=cid;observer.local=False
    bundle_path=PRIVATE/'cases'/(cid+'.json');bundle_path.parent.mkdir(exist_ok=True)
    if bundle_path.exists():return read(bundle_path)['result']
    row=dict(material_id=cid,A='HUMAN_REVIEW_PENDING',B='FAIL',allowed_pages=[],
        planner_result=None,compiler_result=None,validator_result=None,grounding_status='NOT_EVALUATED',
        failure_reason=None,post_compile_api_delta=None)
    bundle=dict(result=row,case=case,analysis=None,scene=None,plan=None)
    try:
        pdf,upload,extracted,pages,source=source_case(case);row['allowed_pages']=pages
        observer.stage='first-analysis';inp=helpers()['build_analysis_input'](observer,extracted['text'],upload)
        response=observer.create(**response_options(),instructions=analysis_prompt(),input=inp,
            text={'format':dict(type='json_schema',name='visual_learning_analysis',strict=True,schema=helpers()['ANALYSIS_SCHEMA'])})
        raw=json.loads(response.output_text)
        analysis,path,lab,structures=prepare(raw,pages)
        row.update(main_schema_valid=read(observer.path('.json'))['schema_valid'],analysis_refs=references(raw,pages),
            native_lab_demos=len(lab['demos']),rejected_lab_demos=lab.get('rejected'),
            fixed_adjustable_declarations=lab_declarations(lab))
        bundle.update(analysis=analysis,path=path,lab=lab,structures=structures,source=source)
        catalog=semantic_catalog(None,analysis)
        catalog={i:v for i,v in catalog.items() if focusable(i,catalog,{})}
        caps=planner.capabilities(analysis,{},lab);row['capabilities']=caps
        row['semantic_ids']=list(catalog)
        if not catalog:raise ValueError('No canonical selectable catalog; production planner CTA disabled')
        data=planner.context(analysis,source,catalog,pages,caps,None)
        bundle.update(planner_data=data,planner_catalog=catalog,planner_capabilities=caps)
        store=planner.ensure({},cid);key=planner.identity(cid,'en',source,catalog,caps,None)
        observer.stage='first-planner'
        plan=planner.build(store,key,observer,MODEL,data,catalog,pages,caps)
        row['planner_diagnostic']=store.get('diagnostics',{}).get(key,{})
        row['planner_result']='accepted' if plan else 'rejected';bundle['plan']=plan
        if plan is None:
            row['failure_reason']=row['planner_diagnostic'];return row
        family=plan['family'];row.update(representation_family=family,requested_family=plan['requested_family'],
            planner_refs=references(plan,pages),adapted=plan['adapted'])
        scene=None;artifact=None;row['compiler_result']='NOT_APPLICABLE'
        if family in ('spatial','structural') or family=='dynamic' and not lab['demos'] and caps.get('spatial'):
            domain='probability_sets' if family=='structural' else 'spatial_dynamics'
            scene_data=build_scene_context(analysis,source,pages,domain);bundle['scene_data']=scene_data
            observer.stage='first-scene';raw_scene=request_scene(observer,MODEL,scene_data)
            bundle['raw_scene']=raw_scene
            row['scene_refs']=references(raw_scene,pages)
            row['raw_scene_declarations']=declarations(raw_scene)
            try:
                scene=normalize_scene(raw_scene,pages)
                if scene['domain']!=domain:raise ValueError('Selected compiler domain mismatch')
                artifact=scene;row['compiler_result']='accepted';row['validator_result']='accepted'
            except Exception as error:
                row.update(compiler_result='rejected',validator_result='rejected',failure_reason=pure_reason(error))
        elif family=='dynamic':artifact=lab if lab['demos'] else None;row['compiler_result']='existing validated numeric lab' if artifact else 'unavailable'
        elif family=='process':artifact=plan['process'];row['compiler_result']='accepted in planner';row['validator_result']='accepted'
        elif family=='execution':artifact=plan['execution'];row['compiler_result']='accepted in planner';row['validator_result']='accepted'
        elif family=='analogy':
            from analogy import compiler as ac
            from analogy.state import parameter_registry,identity,ensure
            registry=parameter_registry({},lab,path,catalog);focus=plan['focus_ids'][0]
            adata=ac.context(analysis,source,catalog,registry,focus,pages)
            observer.stage='first-analogy'
            artifact=ac.build(ensure({},cid,'en','day27'),identity(cid,'en','day27',focus),observer,MODEL,adata,catalog,registry,pages)
            if artifact and not artifact.get('suitable'):artifact=None
            row['compiler_result']='accepted' if artifact else 'unavailable';bundle['analogy']=artifact
        else:artifact=analysis
        bundle['scene']=scene;row['normalized_declarations']=declarations(scene)
        row['direct_manipulation_affordances']=affordances(scene,lab,path,analysis)
        row['grounding_status']='Validated source-page references only; semantic Atlas not compiled in first-pass stages.'
        if artifact is not None:
            observer.local=True;before=observer.calls
            try:
                row['runtime_probe']=local_probe(scene,lab,plan)
                row['runtime_result']='passed';row['B']='PASS'
            except Exception as error:
                row.update(runtime_result='failed',failure_reason=pure_reason(error),B='PARTIAL')
            row['post_compile_api_delta']=observer.calls-before
        else:row['B']='PARTIAL'
        if not row['analysis_refs']['valid'] or not row['main_schema_valid']:row['B']='PARTIAL'
        row['B_scope']='Backend contract and local numeric/reducer checks; source-semantic A and real-browser checks are separate.'
        return row
    except Exception as error:
        row['failure_reason']=safe_error(error) if hasattr(error,'status_code') else pure_reason(error)
        if bundle.get('analysis'):row['B']='PARTIAL'
        return row
    finally:
        observer.local=False;write_new(bundle_path,bundle)

def records():return [read(p) for p in sorted((PRIVATE/'responses').glob('*.json')) if not p.name.endswith(('.attempt.json','.request.json'))]
def usage_summary(stage_prefix=None):
    rs=[r for r in records() if stage_prefix is None or r['stage'].startswith(stage_prefix)]
    rows=[{k:r.get(k) for k in ('case','stage','model','returned_model','reasoning','status','seconds','usage','error','schema_valid','response_id','request_sha256','schema_sha256','sdk_retries','semantic_retries')} for r in rs]
    return dict(request_count=len(rs),input_tokens=sum((r.get('usage') or {}).get('input_tokens',0) for r in rs),
        output_tokens=sum((r.get('usage') or {}).get('output_tokens',0) for r in rs),
        seconds=sum(r.get('seconds',0) for r in rs),failed_requests=sum(bool(r.get('error')) for r in rs),
        semantic_retries=0,sdk_retries=0,requests=rows,usage_unavailable_requests=sum(not r.get('usage') for r in rs),
        billing_observed=False,scope='Responses requests; file uploads are recorded separately and not counted as model generations.')
def review_packet(corpus,gold,rows):
    lines=['# Day27 A-axis human semantic-review packet','',
        'A-axis final verdicts are reserved for the human reviewer. All ten cases remain in the denominator. Compiler/validator acceptance supplies B-axis evidence only. No semantic correctness verdict is assigned here.','',
        'Attribution: AI-drafted, human-reviewed and approved expectations before model execution. Source page labels below are original physical PDF pages; outputs cite renumbered evaluation pages.','']
    expected={c['material_id']:c for c in gold['expectations']}
    for case,row in zip(corpus['materials'],rows):
        cid=case['material_id'];bundle=read(PRIVATE/'cases'/(cid+'.json'));e=expected[cid]
        lines+=['## '+cid+' — '+case['title'],'',
            '[Original source]('+case['source_url']+') · [Terms]('+case['terms_url']+') · '+case['license'],
            '', '### 1. Source evidence and frozen conditions','',
            'Physical PDF pages: '+str(case['original_physical_pdf_pages'])+'. Evaluation → original mapping: '+json.dumps(case['evaluation_to_original_pages'])+'.',
            'Source-grounded concise paraphrases from the reviewed prospective packet: '+ '; '.join(e['concepts_present'])+'.',
            'Fixed source conditions: '+ '; '.join(e['fixed_quantities'])+'.',
            'Permitted adjustment/local operations: '+ '; '.join(e['adjustable_quantities'])+'.','']
        for fact in read(PUBLIC/'source-evidence.json')['cases'][cid]:
            lines.append('- Original PDF p.'+str(fact['page'])+': '+fact['evidence']+' Formula/concept: '+fact['formula_or_concept']+'. Fixed condition: '+fact['fixed_condition'])
        lines+=['',
            '### 2–8. Actual output, declarations, representation, grounding and differences','']
        analysis=bundle.get('analysis') or {}
        actual=dict(quick_summary=analysis.get('quick_summary'),key_concepts=analysis.get('key_concepts'),
            relationships=analysis.get('relationships'),visual_evidence=analysis.get('visual_evidence'),
            primary_visualization=analysis.get('primary_visualization'),planner=bundle.get('plan'),
            numeric_lab_declarations=row.get('fixed_adjustable_declarations'),scene_declarations=row.get('raw_scene_declarations'),
            normalized_declarations=row.get('normalized_declarations'),affordances=row.get('direct_manipulation_affordances'),
            source_refs=row.get('analysis_refs'),grounding_status=row.get('grounding_status'),failure_reason=row.get('failure_reason'))
        lines+=['```json',json.dumps(actual,ensure_ascii=False,indent=2,default=str),'```','',
            'Predefined reasonable families: '+ '; '.join(e['reasonable_families'])+'.',
            'Unsupported semantics to inspect: '+ '; '.join(e['unsupported_semantics'])+'.',
            'Static/formal conditions: '+e['static_degradation_conditions'],
            'Objective observations: selected family = '+str(row.get('representation_family'))+'; invalid raw analysis refs = '+str((row.get('analysis_refs') or {}).get('invalid'))+'; rejected lab count = '+str(row.get('rejected_lab_demos'))+'.',
            'Compare source fixed conditions against the min/max/default and expressions above. A varying fitted/source constant, new formula, added dynamics or unmatched support is a review flag; this packet does not decide its semantic verdict.',
            '**A verdict: HUMAN REVIEW PENDING.**','']
    return '\n'.join(lines)
def freeze_stage(name,paths):
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in paths}
    write_new(PUBLIC/(name+'-freeze.json'),dict(frozen_utc=datetime.now(timezone.utc).isoformat(),
        files_sha256=hashes,package_sha256=digest(hashes),production_fingerprint=read(PUBLIC/'prebenchmark-baseline.json')['production_fingerprint'],
        A_verdicts='HUMAN_REVIEW_PENDING',semantic_retries=0))

def first(observer):
    corpus,gold=verify();rows=[]
    for case in corpus['materials']:
        rows.append(first_case(case,observer));print('CASE '+case['material_id']+' B='+rows[-1]['B'],flush=True)
    raw={r['case']+'--'+r['stage']:{k:r.get(k) for k in ('raw','error','status','schema_valid','response_id','request_sha256')} for r in records() if r['stage'].startswith('first-')}
    paths=[PUBLIC/'first-pass-results.json',PUBLIC/'request-usage.json',PUBLIC/'semantic-review-packet.md',PUBLIC/'first-pass-raw-declarations.json']
    write_new(paths[0],dict(cases=rows,denominator=10,A='HUMAN_REVIEW_PENDING',model=MODEL,reasoning_effort='medium',scope='Frozen first attempts; no quality retry, no production changes.'))
    write_new(paths[1],usage_summary('first-'));write_new(paths[3],raw)
    with paths[2].open('x',encoding='utf-8',newline='\n') as f:f.write(review_packet(corpus,gold,rows))
    freeze_stage('first-pass',paths+[PUBLIC/'source-evidence.json'])
    print('FROZEN first-pass '+str(len(rows))+' cases',flush=True)

def normalized_categories(spec):
    if not isinstance(spec,dict):return {}
    ps=spec.get('parameters',[])
    return dict(parameter_ids=sorted(p.get('id','') for p in ps),
        quantity_kinds={p['id']:p.get('quantity_kind') for p in ps},
        domain_constraints={p['id']:p.get('domain_constraint') for p in ps},
        fixed_adjustable={p['id']:'fixed' if p.get('min')==p.get('max') else 'adjustable' for p in ps},
        ranges={p['id']:{k:p.get(k) for k in ('min','max','default','step','range_source')} for p in ps},
        quantities=spec.get('quantities'),bindings=spec.get('bindings'),inverse_bindings=spec.get('inverse_bindings'),
        duration_policy=spec.get('time'),source_pages=references(spec,list(range(1,9))),
        representation_structure={k:spec.get(k) for k in ('domain','objects','series','metrics','outcomes','events','event_sets','focus_targets','family','features','focus_ids','process','execution') if k in spec})

def rehydrate(bundle):
    source=copy.deepcopy(bundle['source']);source['page_texts']={int(k):v for k,v in source['page_texts'].items()}
    scene=normalize_scene(bundle['raw_scene'],bundle['result']['allowed_pages']) if bundle.get('scene') else None
    return source,scene

def deep_case(cid,observer):
    bundle=read(PRIVATE/'cases'/(cid+'.json'));path=PRIVATE/'deep'/(cid+'.json');path.parent.mkdir(exist_ok=True)
    if path.exists():return read(path)['result']
    row=dict(material_id=cid,A='HUMAN_REVIEW_PENDING',B='PARTIAL',browser_status='PENDING_REAL_BROWSER',
        browser_errors='NOT_EVALUATED',context_jumps='NOT_EVALUATED',direct_manipulation=None,
        post_compilation_api_delta=None)
    detail=dict(result=row)
    if not bundle.get('analysis'):
        row.update(B='FAIL',failure_reason='No stored main analysis; deep pipeline unreachable')
        write_new(path,detail);return row
    observer.case=cid;observer.local=False
    try:
        source,scene=rehydrate(bundle);analysis=bundle['analysis'];pages=bundle['result']['allowed_pages']
        pdf=(ROOT/bundle['case']['subset_path']).read_bytes();pdf_before=hashlib.sha256(pdf).hexdigest()
        catalog=semantic_catalog(scene,analysis)
        for value in catalog.values():value['pages']=[p for p in value['pages'] if p in pages]
        selected=rank_pages(analysis,catalog,pages)[:3]
        detail.update(selected_pages=selected,catalog=catalog)
        observer.stage='deep-atlas'
        try:
            raw=request_atlas(observer,MODEL,analysis,source,new_source_state(cid,pdf),cid,selected,pages,catalog)
            atlas=normalize_atlas(raw,selected,catalog,source['page_texts'])
            row.update(atlas_status='accepted',regions=len(atlas['regions']),atlas_diagnostics=atlas.get('diagnostics'))
        except Exception as error:
            row.update(atlas_status='rejected',failure_reason=pure_reason(error))
            atlas=None
        detail['atlas']=atlas
        observer.local=True;before=observer.calls
        wrapper=dict(material_id=cid,scene=scene)
        if scene and scene['domain']=='spatial_dynamics':wrapper['world']=new_state(scene)
        elif scene:
            target=scene['focus_targets'][0]
            wrapper.update(selected_outcome_id=None,selected_focus_id=target['id'],active_expression=target['expression'],open=True)
        workspace=dict(material_id=cid,mode='source',focus=None)
        ts=affordances(scene,bundle['lab'],bundle['path'],analysis)
        row['direct_manipulation']=dict(available=bool(ts),targets=ts,absence_is_not_automatic_failure=True)
        if not atlas:
            row.update(source_grounding='page-only fallback; Atlas unavailable',post_compilation_api_delta=observer.calls-before)
            detail.update(wrapper=wrapper,workspace=workspace);return row
        key=atlas_state.cache_key(cid,pdf,'en',selected,scene,catalog)
        astore=dict(key=key,atlas=atlas,region_hint=None,page=selected[0],seen_focus=None,last_token=None)
        reps={}
        if not scene:
            for demo in bundle['lab'].get('demos',[]):
                semantic=direct_lab.semantic_target(demo,bundle['path'],catalog,analysis)
                if semantic:reps.setdefault(semantic,[]).extend(dict(id=r['id']) for r in demo['series']+demo['derived_metrics'])
        links=derive_links(astore,cid,pages,catalog,ts,reps)
        detail['links']=links;immutable=digest(atlas)
        with patch('streamlit.session_state',{'learning_workspace':workspace}):
            # Pick a single-meaning supported region; never arbitrarily select
            # the first meaning of an ambiguous source region.
            eligible=[r for r in atlas['regions'] if len([i for i in r['semantic_ids'] if focusable(i,catalog,wrapper)])==1]
            target_owners={t['semantic_id'] for t in ts}
            eligible.sort(key=lambda r:(not bool(set(r['semantic_ids'])&target_owners),r['region_id']))
            if not eligible:
                row.update(source_grounding='No unambiguous focusable region; explicit learner choice required',post_compilation_api_delta=observer.calls-before)
                return row
            region=eligible[0];owner=next(i for i in region['semantic_ids'] if focusable(i,catalog,wrapper))
            assert set_workspace_focus(workspace,owner,catalog,wrapper)
            assert atlas_state.select_region(astore,region['region_id'],catalog,wrapper)
            focus_before=get_workspace_focus(workspace,wrapper)
            source_before=dict(region=astore['region_hint'],page=astore['page'])
            assert open_workspace(workspace,'explore')
            row.update(selected_region=region['region_id'],selected_semantic_id=owner,
                semantic_identity_continuity=get_workspace_focus(workspace,wrapper)==focus_before,
                source_grounding='Validated Atlas link; semantic support/location needs human review',
                target_ownership=all(t['semantic_id'] in catalog and t['object_id'] in {r['id'] for r in catalog[t['semantic_id']]['representations']}
                    for t in ts if scene),linked_support=links.get(owner))
            if scene and scene['domain']=='spatial_dynamics':
                state=wrapper['world'];baseline=copy.deepcopy(state['parameters']);initial=snapshot(scene,state)
                owned=[t for t in ts if t['semantic_id']==owner]
                if owned:
                    t=owned[0];trial=copy.deepcopy(state);changes={}
                    for pid in t['parameter_ids']:
                        p=next(p for p in scene['parameters'] if p['id']==pid)
                        value=p['min']+.6*(p['max']-p['min'])
                        if math.isclose(value,p['default']):value=p['min']+.4*(p['max']-p['min'])
                        changes[pid]=value
                    apply_parameters(scene,trial,changes,owner)
                    nums=snapshot(scene,trial)['projections'][t['object_id']]
                    obj=next(o for o in scene['objects'] if o['id']==t['object_id'])
                    xy=[nums[0]+nums[2],nums[1]+nums[3]] if obj['type']=='vector' else nums[:2]
                    identity=fingerprint(['direct',cid,scene])
                    event=dict(scene=identity,revision=state['revision'],token='day27-valid-release',kind='manipulate',target=t['id'],x=float(xy[0]),y=float(xy[1]),time=state['time'])
                    row['commit_accepted']=direct_world.commit(scene,state,identity,event)
                    committed=copy.deepcopy(state)
                    bad=event|dict(revision=state['revision'],token='day27-invalid-release',target='nonexistent_target')
                    rejected=not direct_world.commit(scene,state,identity,bad)
                    row['atomic_rejection']=rejected and state==committed
                else:
                    domain=time_domain(scene,state['parameters'])
                    apply_patch(scene,state,dict(op='set_time',target_id='time',value=domain['min']+.4*(domain['max']-domain['min'])))
                    row.update(commit_accepted=True,interaction='canonical time change; no source-owned direct handle')
                    committed=copy.deepcopy(state)
                    try:apply_patch(scene,state,dict(op='set_time',target_id='time',value=float('nan')))
                    except ValueError:pass
                    row['atomic_rejection']=state==committed
                row['baseline_current_separation']=comparison_rows(scene['parameters'],state['parameters'],[p['id'] for p in scene['parameters']])
                row['compiled_defaults_unchanged']=baseline=={p['id']:p['default'] for p in scene['parameters']}
                row['linked_projection']=dict(changed=initial['values']!=snapshot(scene,state)['values'],series_metrics_objects_share_snapshot=True)
            elif scene:
                event=next((e for e in scene['events'] if e['id']==owner),None)
                chosen=owner if event else scene['events'][0]['id']
                assert set_workspace_focus(workspace,chosen,catalog,wrapper)
                focus_before=get_workspace_focus(workspace,wrapper)
                row.update(commit_accepted=True,interaction='canonical event selection and local exact/Monte Carlo results',
                    linked_projection=local_probe(scene,bundle['lab'],bundle['plan']),atomic_rejection='NOT_APPLICABLE: no parameter gesture',
                    baseline_current_separation='Fixed declared outcome weights/memberships; selection changes only')
                # Returning support follows the actual current event focus.
                atlas_state.sync_region(astore,focus_before)
                source_before=dict(region=astore['region_hint'],page=astore['page'])
            elif bundle.get('plan') and bundle['plan']['family']=='process':
                row.update(commit_accepted=True,interaction=probe_process(bundle['plan']['process']),
                    baseline_current_separation='Validated process initial state compared to reducer transitions',atomic_rejection=True)
            elif bundle['lab'].get('demos'):
                from interactive_lab import ensure_lab_state,_save_parameter
                import numpy as np
                lab_store=ensure_lab_state(cid,bundle['lab']);observations=[]
                for demo in bundle['lab']['demos']:
                    saved=lab_store['demos'][demo['id']];initial_values=copy.deepcopy(saved['values'])
                    curves_before=compute_curves(demo,saved['values'])[1]
                    p=next((p for p in demo['parameters'] if p['min']<p['max']),None)
                    if p:
                        value=p['min']+.6*(p['max']-p['min'])
                        widget='offline-day27-canonical-slider'
                        # Use the same local callback as the actual slider. A
                        # rejected stale callback is checked without inventing
                        # a generic solver/transaction for this older Lab store.
                        import streamlit as st
                        st.session_state[widget]=value
                        _save_parameter(lab_store,demo['id'],p['id'],widget,0)
                        after=compute_curves(demo,saved['values'])[1]
                        committed=copy.deepcopy(saved['values'])
                        st.session_state[widget]=p['min']
                        _save_parameter(lab_store,demo['id'],p['id'],widget,999)
                        stale_rejected=saved['values']==committed
                        observations.append(dict(demo_id=demo['id'],parameter_id=p['id'],
                            canonical_value=saved['values'][p['id']],baseline=initial_values[p['id']],
                            curve_changed=any(not np.allclose(curves_before[k],after[k]) for k in after),
                            stale_callback_rejected=stale_rejected,
                            comparison_rows=comparison_rows(demo['parameters'],saved['values'],[p['id']])))
                row.update(interaction='existing Numeric Lab canonical slider callbacks',commit_accepted=bool(observations),
                    linked_projection=observations,baseline_current_separation='Compiled defaults retained; callback updates existing Lab store only',
                    atomic_rejection='Stale callback rejection tested; arbitrary out-of-range callback injection not claimed')
                detail['lab_state']=lab_store
            else:
                row.update(interaction=local_probe(scene,bundle['lab'],bundle.get('plan')),
                    commit_accepted=True,baseline_current_separation='Existing numeric lab baseline; formal selection preserved')
            focus_after=get_workspace_focus(workspace,wrapper)
            assert open_workspace(workspace,'source')
            selected_back=atlas_state.sync_region(astore,focus_after)
            row['source_roundtrip']=dict(focus_preserved=get_workspace_focus(workspace,wrapper)==focus_after,
                supporting_region=selected_back['region_id'] if selected_back else None,
                selected_source_context_preserved=dict(region=astore['region_hint'],page=astore['page'])==source_before)
            row['source_immutable']=digest(atlas)==immutable and sha(ROOT/bundle['case']['subset_path'])==pdf_before
            row['post_compilation_api_delta']=observer.calls-before
            row['B']='PASS' if row['source_roundtrip']['focus_preserved'] and row['source_immutable'] and row.get('commit_accepted') and row['semantic_identity_continuity'] else 'PARTIAL'
        detail.update(wrapper=wrapper,workspace=workspace,atlas_state=astore)
        return row
    except Exception as error:
        row['failure_reason']=pure_reason(error);return row
    finally:
        observer.local=False;write_new(path,detail)

def deep(observer):
    _,gold=verify()
    if not (PUBLIC/'first-pass-freeze.json').exists():raise ValueError('First-pass not frozen')
    rows=[]
    for cid in gold['deep_subset']:
        rows.append(deep_case(cid,observer));print('DEEP '+cid+' B='+rows[-1]['B'],flush=True)
    path=PUBLIC/'deep-results.json';write_new(path,dict(cases=rows,selected_materials=5,
        scope='Production source compiler/reducer/twin joins; real browser evidence frozen separately after all generations.',A='HUMAN_REVIEW_PENDING'))
    freeze_stage('deep',[path]);print('FROZEN deep',flush=True)
def stability(observer):
    corpus,gold=verify();runs=[]
    if not (PUBLIC/'first-pass-freeze.json').exists():raise ValueError('First-pass not frozen')
    for cid in gold['stability_subset']:
        bundle=read(PRIVATE/'cases'/(cid+'.json'));observer.case=cid;rows=[]
        if not bundle.get('analysis') or not bundle.get('planner_data'):
            runs.append(dict(material_id=cid,status='BLOCKED_NO_STORED_ANALYSIS_OR_DECLARATION_CONTEXT',runs=[]));continue
        scene_data=bundle.get('scene_data');data=scene_data or bundle['planner_data']
        kind='scene' if scene_data else 'planner'
        for n in range(1,4):
            observer.stage='stability-'+kind+'-'+str(n)
            row=dict(run=n,compiler_kind=kind,input_context_sha256=digest(data),accepted=False)
            try:
                if scene_data:
                    raw=request_scene(observer,MODEL,data);spec=normalize_scene(raw,bundle['result']['allowed_pages'])
                else:
                    store=planner.ensure({},cid);key=('stability',cid,n)
                    spec=planner.build(store,key,observer,MODEL,data,bundle['planner_catalog'],bundle['result']['allowed_pages'],bundle['planner_capabilities'])
                    raw=read(observer.path('.json')).get('raw')
                    if spec is None:raise ValueError(json.dumps(store.get('diagnostics',{}).get(key,{}),ensure_ascii=False))
                row.update(accepted=True,normalized_categories=normalized_categories(spec),raw_declarations=declarations(raw))
            except Exception as error:
                record=read(observer.path('.json')) if observer.path('.json').exists() else {}
                row.update(validator_reason=pure_reason(error) if not record.get('error') else record['error'],
                    raw_declarations=declarations(record.get('raw')),normalized_categories=None)
            rows.append(row)
        accepted=[r['normalized_categories'] for r in rows if r['accepted']]
        cats=set().union(*(v.keys() for v in accepted)) if accepted else set()
        drift={c:len({digest(v[c]) for v in accepted})>1 for c in sorted(cats)}
        drift['validator_outcome']=len({r['accepted'] for r in rows})>1
        runs.append(dict(material_id=cid,compiler_kind=kind,analysis_sha256=digest(bundle['analysis']),
            identical_input_context=True,runs=rows,drift_categories=drift,
            parameter_drift_scope='World declaration parameters regenerated' if scene_data else 'Planner-only declaration: Lab parameters/quantities remain in the fixed main analysis; their generation stability is not measured.',
            interpretation='Mechanical normalized differences only. Source justification/materiality is reserved for human semantic review.'))
    path=PUBLIC/'stability-results.json';write_new(path,dict(cases=runs,selected_materials=4,independent_runs_per_material=3,A='HUMAN_REVIEW_PENDING'))
    freeze_stage('stability',[path]);print('FROZEN stability',flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=['verify','first','deep','stability'],required=True);parser.add_argument('--live',action='store_true')
    args=parser.parse_args();verify()
    if args.phase=='verify':print('Verified frozen corpus/expectations and unchanged production baseline; no network.');return
    logging.getLogger('streamlit').setLevel(logging.ERROR)
    observer=Observer(args.live)
    if args.phase=='first':first(observer)
    elif args.phase=='deep':deep(observer)
    elif args.phase=='stability':stability(observer)

if __name__=='__main__':main()
