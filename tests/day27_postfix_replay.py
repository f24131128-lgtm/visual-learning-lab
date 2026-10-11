"""POST_FIX offline captured-shape replay; annotations are test data, not model output.

No benchmark expectation or captured response is edited. No model client exists
in this runner. The production planner/ranking remains unchanged.
"""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from support import load_app_helpers
from interactive_lab import clean_interactive_lab, commit_lab_values, compute_curves, default_values
from quantity_contract import can_commit, source_values
from representation_contract import registrations
from source_atlas.model import semantic_catalog, normalize_atlas
from source_atlas.state import cache_key
from workspace.grounded_twin import derive_links
from workspace.state import open_workspace
from manipulation.lab import semantic_target, targets

PUBLIC=ROOT/'docs/day27'
OUT=PUBLIC/'post_fix'
PRIVATE=ROOT/'.day27-local'
H=None


def read(path):return json.loads(path.read_text(encoding='utf-8'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def helpers():
    global H
    if H is None:H=load_app_helpers()
    return H


def verify_baseline():
    index=PUBLIC/'artifact-hashes.json'
    assert sha(index)=='818e71d84f3ec822545b0f4da90cf7978ce9540dd762fcb65f1d33443a572b19'
    hashes=read(index)['files_sha256']
    for name,expected in hashes.items():
        file=ROOT/name
        if name in ('docs/DAY27_EVIDENCE.md','docs/DAY27_CHECKPOINT.md'):
            file=OUT/'frozen_baseline'/Path(name).name
            assert (ROOT/name).read_bytes().startswith(file.read_bytes())
        assert sha(file)==expected,name
    private=read(PUBLIC/'private-evidence-hashes.json')['files_sha256']
    for name,expected in private.items():assert sha(ROOT/name)==expected,name
    baseline=read(PUBLIC/'prebenchmark-baseline.json')['production_file_hashes']
    planner=[name for name in baseline if name.startswith('learning_world/')]
    for name in planner:assert sha(ROOT/name)==baseline[name],name
    return dict(public_files=len(hashes),private_files=len(private),unchanged_planner_files=planner,manifest_sha256=sha(index))


def prepare(raw,pages,material):
    h=helpers();analysis=copy.deepcopy(raw);analysis['analysis_language']='en'
    decision=h['clean_primary_visualization'](raw.get('primary_visualization'))
    structures={key:h['clean_'+key](raw.get(key),pages) for key in ('concept_map','visual_flow','comparison')}
    analysis['_formal_representations']=structures
    visual=structures.get({'flow':'visual_flow','concept_map':'concept_map','comparison':'comparison'}.get(decision['type']))
    path=h['clean_learning_path'](raw.get('learning_path'),pages,decision['type'],visual)
    catalog=semantic_catalog(None,analysis)
    lab=clean_interactive_lab(raw.get('interactive_lab'),pages,path,h['valid_source_pages'],catalog=catalog,material=material)
    return analysis,path,lab,structures,catalog


# Explicit offline reviewer annotations. Nothing here classifies production
# controls by a topic/name. These constants never enter a production prompt.
ANNOTATIONS={
 'regression':dict(facts=[('reported_correlation',-.499,358,'The sample correlation is R=-0.499.', 'corr'),
                        ('sample_mean_income',101780.,358,'The source sample mean family income is 101780 dollars.',None),
                        ('sample_mean_aid',19940.,358,'The source sample mean gift aid is 19940 dollars.',None),
                        ('sample_sd_income',63200.,358,'The source sample standard deviation of family income is 63200 dollars.',None),
                        ('sample_sd_aid',5460.,358,'The source sample standard deviation of gift aid is 5460 dollars.',None)],time=False),
 'probability':dict(facts=[('source_probability_a',1/3,94,'For the fair die, A={1,2} contains two of the six equiprobable outcomes.','prob_a'),
                         ('source_probability_b',1/3,94,'For the fair die, B={4,6} contains two of the six equiprobable outcomes.','prob_b')],time=False),
 'complexity':dict(facts=[('source_linear_coefficient',100.,224,'The source compares 100n+1 with n^2+n+1.','a')],time=False),
 'circuits':dict(facts=[('source_charge_input',5.,13,'The charging example has constant input 5 V.','input_voltage'),
                      ('source_charge_initial',0.,13,'The charging example starts at capacitor voltage 0 V.','initial_voltage'),
                      ('source_discharge_input',0.,13,'The discharging example has constant input 0 V.',None),
                      ('source_discharge_initial',5.,13,'The discharging example starts at capacitor voltage 5 V.',None)],time=True),
}


def annotated_shape(cid,raw,case):
    """Explicit test adaptation of the captured Lab shape, never an AI repair."""
    result=copy.deepcopy(raw);lab=result['interactive_lab'];lab['version']='2.0'
    entry=ANNOTATIONS[cid]
    original_to_evaluation={p:i+1 for i,p in enumerate(case['original_physical_pdf_pages'])}
    for demo in lab['demos']:
        demo['source_facts']=[dict(id=identifier,label=identifier.replace('_',' '),unit='',value=value,
            provenance='source_fixed',source_pages=[original_to_evaluation[page]],source_evidence=evidence)
            for identifier,value,page,evidence,_ in entry['facts']]
        demo['title']='Hypothetical exploration (offline annotated shape)'
        demo['learning_goal']='Compare an immutable source baseline with a separate what-if quantity.'
        demo['x'].update(semantic_role='runtime_time' if entry['time'] else 'independent_variable',
                         provenance=None if entry['time'] else 'hypothetical_exploration')
        renames={p['id']:'exploration_'+p['id'] for p in demo['parameters']}
        for p in demo['parameters']:
            original=p['id'];p['id']=renames[original]
            ref=next((identifier for identifier,_,_,_,control in entry['facts'] if control==original),None)
            p.update(provenance='hypothetical_exploration',source_baseline_ref=ref,source_evidence='',
                     source_pages=list(demo['source_pages']),expose_control=True,semantic_refs=[],label='Hypothetical '+p['label'])
        for group in ('series','derived_metrics'):
            for item in demo[group]:
                item['expression']=re.sub(r'\b[A-Za-z][A-Za-z0-9_]*\b',lambda m:renames.get(m.group(),m.group()),item['expression'])
                item.update(provenance='derived',semantic_refs=[])
                item['label']='Hypothetical '+item['label']
    return result


def deep_replay(cid,bundle,analysis,path,lab,catalog,case,material):
    recorded=read(PRIVATE/'deep'/f'{cid}.json')
    sid=recorded['result']['selected_semantic_id']
    raw=read(PRIVATE/'responses'/f'{cid}--deep-atlas.json')['raw']
    pages=bundle['result']['allowed_pages'];pdf=(ROOT/case['subset_path']).read_bytes()
    atlas=normalize_atlas(raw,recorded['selected_pages'],catalog,bundle['source']['page_texts'])
    state=dict(key=cache_key(material,pdf,'en',atlas['processed_pages'],None,catalog),atlas=atlas)
    regs={};handles=[]
    for demo in lab['demos']:
        for semantic,rows in registrations(demo,catalog,material,pages).items():regs.setdefault(semantic,[]).extend(rows)
        owner=semantic_target(demo,path,catalog,analysis)
        if owner in regs:handles.extend(targets(demo,default_values(demo),owner))
    links=derive_links(state,material,pages,catalog,handles,regs,expected_key=state['key'])
    assert sid in links and sid in catalog
    expected=[r['id'] for r in catalog[sid]['representations']]
    assert expected and links[sid]['representation_ids']==expected
    assert not links[sid]['manipulable']
    workspace=dict(material_id=material,mode='source',focus=sid)
    for mode in ('explore','source'):
        assert open_workspace(workspace,mode,sid,catalog)
        assert workspace['focus']==sid
    assert sha(ROOT/case['subset_path'])==case['subset_sha256']
    return dict(semantic_id=sid,baseline_representation_ids=recorded['links'][sid]['representation_ids'],
        post_fix_representation_ids=links[sid]['representation_ids'],ownership_reason='Existing canonical ID of the accepted formal renderer object; no ownership added to legacy Lab.',
        direct_manipulation=False,source_roundtrip=True,source_pdf_unchanged=True,api_delta=0)


def main():
    baseline=verify_baseline();corpus=read(PUBLIC/'corpus-manifest.json')
    rows=[]
    # A real SDK request is forbidden even if a helper accidentally calls one.
    with patch('openai.resources.responses.responses.Responses.create',side_effect=AssertionError('Offline replay cannot call API')):
        for case in corpus['materials']:
            cid=case['material_id'];bundle=read(PRIVATE/'cases'/f'{cid}.json')
            raw=read(PRIVATE/'responses'/f'{cid}--first-analysis.json')['raw']
            material=helpers()['build_analysis_id']('pdf',(ROOT/case['subset_path']).read_bytes(),'en')
            pages=bundle['result']['allowed_pages']
            analysis,path,lab,structures,catalog=prepare(raw,pages,material)
            assert lab['rejected']==0
            original=digest(raw);legacy=[]
            for demo in lab['demos']:
                assert demo['contract_version']=='legacy_read_only'
                saved=dict(specification=demo,values=default_values(demo),compare=True)
                before=copy.deepcopy(saved)
                compute_curves(demo,saved['values'])
                for p in demo['parameters']:
                    assert not can_commit(p)
                    try:commit_lab_values(demo,saved,{p['id']:p['default']})
                    except ValueError:pass
                    else:raise AssertionError('Legacy parameter unexpectedly writable')
                    assert saved==before
                assert registrations(demo,catalog,material,pages)=={}
                legacy.append(dict(demo_id=demo['id'],parameters_read_only=True,curve_computable=True,roles_not_guessed=True))
            row=dict(stage='POST_FIX',case=cid,kind='UNCHANGED_CAPTURE_LOCAL_REVALIDATION',legacy_lab=legacy,
                     source_artifact_unchanged=digest(raw)==original,api_delta=0)
            if cid in ANNOTATIONS:
                shape=annotated_shape(cid,raw,case)
                _,_,modern,_,_=prepare(shape,pages,material)
                if modern['rejected']:
                    from interactive_lab import _clean_demo
                    for declaration in shape['interactive_lab']['demos']:
                        try:_clean_demo(declaration,pages,{s['id'] for s in (path or {}).get('steps',[])},helpers()['valid_source_pages'],version='2.0',catalog=catalog,material=material)
                        except Exception as error:raise ValueError(cid+': '+str(error)) from error
                assert modern['rejected']==0 and modern['demos'],cid
                adapted=[]
                for demo in modern['demos']:
                    before=copy.deepcopy(demo);saved=dict(specification=demo,values=default_values(demo),compare=True)
                    facts=source_values(demo)
                    for p in demo['parameters']:
                        value=p['max'] if p['default']!=p['max'] else p['min']
                        commit_lab_values(demo,saved,{p['id']:value})
                        assert source_values(demo)==facts and demo==before
                    for fact in demo['source_facts']:
                        snapshot=copy.deepcopy(saved)
                        try:commit_lab_values(demo,saved,{fact['id']:fact['value']+.1})
                        except ValueError:pass
                        else:raise AssertionError('Source baseline was writable')
                        assert saved==snapshot
                    adapted.append(dict(source_facts=demo['source_facts'],parameters=demo['parameters'],
                        derived_roles=[item['provenance'] for group in ('series','derived_metrics') for item in demo[group]],
                        source_baseline_immutable=True,separate_exploration_ids=True))
                row['annotated_shape']=dict(kind='EXPLICIT_OFFLINE_TEST_ANNOTATION_NOT_MODEL_OUTPUT',demos=adapted,
                    limit='Proves the generic contract on captured mathematical shapes; does not establish a newly generated semantic improvement.')
            if cid in ('circular','harmonic','circuits','probability','search'):
                row['B']=deep_replay(cid,bundle,analysis,path,lab,catalog,case,material)
            if cid in ('signals','debugging'):
                row['canary']=dict(formal_renderer_available=any(s and s.get('suitable') for s in structures.values()),
                    lab_curve_available=bool(lab['demos']),generated_code_executed=False,
                    legacy_interactivity='Read-only by explicit compatibility policy' if lab['demos'] else 'Not applicable')
                assert row['canary']['formal_renderer_available']
            rows.append(row)
    report=dict(stage='POST_FIX',kind='OFFLINE_REPLAY',status='PASSED',not_untouched_holdout=True,
        baseline_verification=baseline,cases=rows,case_count=len(rows),api_requests=0,
        scope='Mechanical provenance/ownership checks. No A-axis verdict. Legacy capture and explicit annotation lanes are reported separately.')
    output=OUT/(sys.argv[1] if len(sys.argv)>1 else 'offline-replay.json')
    assert output.resolve().is_relative_to(OUT.resolve())
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(status=report['status'],cases=len(rows),deep_cases=5,annotated_shapes=4,canaries=2,api_requests=0)))


if __name__=='__main__':main()
