"""Offline POST_FIX reporting. No model client or semantic scoring."""
import copy
import datetime
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from day27_postfix_live import OUT,HOME,CASES,gate,usage,production_hashes
from day27_postfix_replay import verify_baseline,prepare,helpers
from day27_benchmark import read,sha,digest,save_work,pure_reason
from interactive_lab import _clean_demo

HUMAN={'circular':'PARTIAL','harmonic':'PASS','circuits':'PARTIAL','signals':'PASS',
       'regression':'FAIL','probability':'FAIL','search':'PARTIAL','complexity':'PARTIAL',
       'spectrum':'PASS','debugging':'PASS'}


def cell(value):return str(value).replace('|',' / ').replace('\n',' ')
def dump(value):return json.dumps(value,ensure_ascii=False,indent=2)


def packet():
    baseline=read(ROOT/'docs/day27/source-evidence-supplement.json')['cases']
    corpus=read(ROOT/'docs/day27/corpus-manifest.json')['materials']
    offline=read(OUT/'offline_runs/02.json')
    lines=['# POST_FIX — human semantic/source review',
        '', 'This replay is not an untouched holdout. The frozen baseline A-axis assignments remain PASS 4 / PARTIAL 4 / FAIL 2. No post-fix A verdict is assigned. Schema, validator and browser checks are engineering evidence only.',
        '', 'Raw proposals, accepted runtime declarations and explicit offline annotations are separate below. A rejected proposal is not presented as a working control. Evaluation page numbers are renumbered subset pages; physical pages are mapped explicitly.',
        '', 'Candidate C ranking is unchanged. A different planner result in one new generation does not establish a general selection repair.']
    for cid in CASES:
        bundle=read(HOME/'cases'/(cid+'.json'));old=read(ROOT/'.day27-local/cases'/(cid+'.json'))
        case=next(c for c in corpus if c['material_id']==cid);row=bundle['result']
        lines+=['',f"## {cid} — {case['title']}",'',f"Frozen baseline human A: **{HUMAN[cid]}** (unchanged). [Source]({case['source_url']}).",
            '', 'Source evidence (frozen concise paraphrases; physical PDF pages):']
        for e in baseline[cid]:lines.append(f"- p.{e['page']}: {e['evidence']} Formula/concept: {e['formula_or_concept']}. Condition: {e['fixed_condition']}")
        lines+=['', 'Evaluation → physical mapping: `'+json.dumps(case['evaluation_to_original_pages'])+'`.',
            '',f"Baseline planner/runtime: `{old['result'].get('representation_family')}` / `{old['result'].get('compiler_result')}`. Baseline Lab parameter declarations:"]
        for d in old.get('lab',{}).get('demos',[]):
            lines.append('- '+d['id']+': '+', '.join(f"{p['id']}={p['default']} [{p['min']}, {p['max']}]" for p in d['parameters']))
        raw=bundle.get('raw_analysis',{})
        lines+=['', 'New main analysis: '+raw.get('quick_summary','No stored analysis.'),
            '', 'New planner/engineering observations:',
            '', '| Observation | Actual result |','|---|---|',
            f"| Planner | {cell(row.get('planner_result'))} |",
            f"| Family | {cell(row.get('representation_family'))} |",
            f"| Compiler | {cell(row.get('compiler_result'))} |",
            f"| Compiler rejection | {cell(row.get('compiler_failure'))} |",
            f"| Lab demos rejected | {row.get('lab_rejected')} |",
            f"| Atlas validator | {row.get('atlas_validator')} |",
            f"| Pipeline exceptions | {cell(row.get('failures'))} |"]
        plan=bundle.get('plan')
        if plan:lines+=['','Planner reason (model text): '+plan['reason']]
        else:lines+=['','Planner diagnostic:','```json',dump(row.get('planner_diagnostic')),'```']
        if bundle.get('raw_scene'):
            proposal=bundle['raw_scene']
            fields=('domain','scene_version','title','learning_goal','source_pages','outcomes','events','views','focus_targets','parameters','quantities')
            lines+=['','Selected compiler raw proposal (retained even when rejected; not installed as a valid runtime):','```json',dump({k:proposal[k] for k in fields if k in proposal}),'```']
        for d in raw.get('interactive_lab',{}).get('demos',[]):
            accepted=next((n for n in bundle.get('lab',{}).get('demos',[]) if n['id']==d['id']),None)
            lines+=['',f"### Proposed Lab `{d['id']}` — runtime {'accepted' if accepted else 'rejected'}",'',d['learning_goal'],'',f"Formula display: `{d['formula_display']}`.",
                '',f"Independent/runtime axis: `{dump(d['x']).replace(chr(10),' ')}`.",
                '', 'Source facts declared by the model (source fidelity is for the reviewer):',
                '', '| ID | Value | Pages (evaluation → physical) | Evidence declared |','|---|---|---|---|']
            for f in d.get('source_facts',[]):
                p=[f"{n}→{case['evaluation_to_original_pages'].get(str(n),'?')}" for n in f['source_pages']]
                lines.append(f"| {f['id']} | {f['value']} {cell(f['unit'])} | {', '.join(p)} | {cell(f['source_evidence'])} |")
            lines+=['', 'Controls/read-only parameters:', '', '| ID | Provenance | Source baseline ref | Min / initial / max | Exposed | Semantic refs |','|---|---|---|---|---|---|']
            for p in d['parameters']:
                lines.append(f"| {p['id']} | {p['provenance']} | {p['source_baseline_ref']} | {p['min']} / {p['default']} / {p['max']} | {p['expose_control']} | {cell(p['semantic_refs'])} |")
            for p in d['parameters']:
                if p.get('source_evidence'):lines.append(f"\nParameter evidence `{p['id']}`: {p['source_evidence']}")
            lines+=['','Series/metrics (declared derived expressions and ownership):','']
            for group in ('series','derived_metrics'):
                for q in d[group]:lines.append(f"- {group}.{q['id']}: `{q['expression']}`; provenance `{q['provenance']}`; refs `{q['semantic_refs']}`.")
            if accepted:
                probe=next(p for p in row['local']['lab'] if p['demo_id']==d['id'])
                lines+=['', 'Trusted local commit observations:','```json',dump(probe),'```']
            else:
                try:_clean_demo(copy.deepcopy(d),row['allowed_pages'],{s['id'] for s in (bundle.get('path') or {}).get('steps',[])},helpers()['valid_source_pages'],version='2.0',catalog=bundle['planner_catalog'],material=bundle['material'])
                except Exception as e:lines+=['','Actual Lab rejection: `'+pure_reason(e)+'`. Source facts and controls in this proposal were not installed in the runtime.']
                from quantity_contract import expression_names
                declared={p['id'] for p in d['parameters']}|{f['id'] for f in d.get('source_facts',[])}|{d['x']['id']}
                for q in d['series']:
                    names=expression_names(q['expression'],declared)
                    if len(names)>5:lines.append(f"- Expression `{q['id']}` references {len(names)} numeric names: `{sorted(names)}`. Existing safe_math per-expression limit: 5.")
        local=row.get('local',{})
        sid=local.get('selected_semantic_id')
        lines+=['','Source → representation observations:','```json',dump(dict(semantic_id=sid,region_id=local.get('selected_region'),
            representation_ids=local.get('representation_ids'),ownership=bundle.get('links',{}).get(sid),
            direct_manipulation=row.get('direct_manipulation'),source_roundtrip=local.get('source_roundtrip'),
            source_pdf_unchanged=local.get('source_pdf_unchanged'),atlas_immutable=local.get('atlas_immutable'),
            post_compilation_api_delta=local.get('post_compilation_api_delta'))),'```',
            '', 'Objective review flags:',
            '- New generated semantic IDs are internal to this material/attempt. Do not treat renamed IDs across generations as proof of semantic equivalence.',
            '- Source facts/evidence text above are model declarations; validation checks their structure/pages and prevents writes, not their truth against the PDF.',
            '- Hypothetical controls remain subject to review for pedagogical/source appropriateness, even when provenance and numeric safety pass.']
        if cid=='regression':lines.append('- Baseline `corr=-0.499` was adjustable. New raw proposal declares `reported_correlation=-0.499` separately from `explore_correlation`; the new Lab is rejected, so no runtime correlation control exists in this attempt. The frozen expectation does not preauthorize an adjustable trial fit.')
        if cid=='probability':lines.append('- Baseline used adjustable `prob_a/prob_b` and no finite-set scene. New Lab uses a card-deck overlap experiment and declared immutable deck/count facts. The structural compiler attempt is rejected. Review finite event membership and exact source probabilities separately from the hypothetical overlap fraction.')
        if cid=='circuits':lines.append('- The new model declares four charging/discharging voltage facts separately from controls. R/C initial exploration values and hypothetical voltages must not be read as measured source conditions. The planner was rejected; the independent validated Lab/formal views remain available.')
        lines+=['','Reviewer (leave blank):','', '- Core source understanding: [ ]','- Fixed / adjustable: [ ]','- Representation appropriateness: [ ]','- Source fidelity: [ ]','- Unsupported invention: [ ]','- Post-fix overall A-axis: [ PASS / PARTIAL / FAIL ]']
    lines+=['','## Big-O — offline shape only; no new live generation','',
        'Frozen baseline human A remains PARTIAL. The original adjustable coefficient `a=100` is retained in immutable baseline evidence. The explicit offline annotation creates `source_linear_coefficient=100` (source_fixed) and a separate hypothetical exploration identity. Trusted commits keep the source fact unchanged. This annotation is test data, not a model-generated improvement or an untouched holdout.']
    for e in baseline['complexity']:lines.append(f"- Physical p.{e['page']}: {e['evidence']} {e['formula_or_concept']}; {e['fixed_condition']}")
    lines+=['','## Five deep cases — unchanged captured IDs, local B replay','',
        'These rows revalidate the same captured source semantic entity against real existing formal renderer objects. No ownership is inferred for legacy Labs and no inverse handle is created.',
        '', '| Case | Source region / evaluation→physical page | Exact semantic ID | Baseline representation_ids | POST_FIX representation_ids | Direct manipulation | Roundtrip |','|---|---|---|---|---|---|---|']
    for row in offline['cases']:
        if 'B' in row:
            b=row['B'];capture=read(ROOT/'.day27-local/deep'/(row['case']+'.json'))
            rid=capture['result']['selected_region'];region=next(r for r in capture['atlas']['regions'] if r['region_id']==rid)
            case=next(c for c in corpus if c['material_id']==row['case']);physical=case['evaluation_to_original_pages'][str(region['page'])]
            lines.append(f"| {row['case']} | {rid} / {region['page']}→{physical} | {b['semantic_id']} | {b['baseline_representation_ids']} | {b['post_fix_representation_ids']} | {b['direct_manipulation']} | {b['source_roundtrip']} |")
    lines+=['','Cross-case facts only:',
        '- All live cases share one sealed production tree, GPT-6.1 Sol / medium, and zero semantic retries.',
        '- Legacy captured Labs are read-only by explicit compatibility policy. Explicit annotations occupy a separate offline lane.',
        '- Formal representation ownership and inverse manipulation ownership remain separate.',
        '- Raw proposals, compiler rejection and normalization omissions remain in the recorded denominator.',
        '- The baseline human A-axis remains 4 PASS / 4 PARTIAL / 2 FAIL.']
    (OUT/'post-fix-semantic-review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def browser_report():
    latest=[];attempts=[]
    for cid in CASES:
        p=HOME/'browser'/(cid+'-desktop-results.json')
        if p.exists():
            r=read(p)
            latest.append({k:r.get(k) for k in ('case','success','error','steps','page_errors','console_errors','focus_preserved','source_pdf_immutable',
                'source_view_unchanged','roundtrip_mode','canonical_value_changed','linked_chart_changed','interaction_absence',
                'post_compilation_response_attempts','post_compilation_network_delta','screenshot')})
    for p in sorted((HOME/'browser').glob('*-results.json')):
        if p.name.endswith('-desktop-results.json'):continue
        attempts.append(dict(path=p.relative_to(ROOT).as_posix(),sha256=sha(p)))
    events=[json.loads(line) for line in (HOME/'browser/events.jsonl').read_text(encoding='utf-8').splitlines()]
    report=dict(stage='POST_FIX',cases=latest,attempts=attempts,
        recorded_response_replays=sum(e['kind']=='recorded_response' for e in events),
        context_mismatches=sum(e.get('context_matches') is False for e in events),
        blocked_unrecorded_responses=sum(e['kind']=='blocked_unrecorded_response' for e in events),
        new_network_requests=sum(e['new_network_requests'] for e in events),
        scope='Real empty-app PDF upload and widget/pointer replay of exactly the saved model output; no model rerun.')
    save_work(OUT/'browser-replay.json',report)
    return report


def main():
    gate();assert all((HOME/'cases'/(c+'.json')).exists() for c in CASES)
    packet();browser=browser_report();u=usage();save_work(OUT/'request-usage.json',u)
    report=read(OUT/'live-replay.json');report['browser']=browser;save_work(OUT/'live-replay.json',report)
    print(json.dumps(dict(stage='POST_FIX',review_packet='written',request_count=u['request_count'],browser_cases=len(browser['cases']),A='HUMAN_REVIEW_PENDING')))


if __name__=='__main__':main()
