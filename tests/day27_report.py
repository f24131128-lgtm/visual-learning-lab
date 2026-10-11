"""Write-once report of frozen attempts; no client, generation or repair."""
from collections import Counter
from datetime import datetime, timezone
import copy
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from day27_benchmark import (PUBLIC, PRIVATE, verify, read, write_new, sha,
    digest, usage_summary, records, review_packet, freeze_stage)

OBSERVATIONS={
 'circular': 'The Numeric Lab declares coefA and coefB adjustable at defaults 0.3 and 0.9; its curves implement the source angular-law example rather than a rendered moving circle. Frozen expectations require source-example coefficients to remain identifiable baseline facts. No angular-velocity parameter is declared; do not infer a signed/positive domain from coefA/coefB. time is the Lab x variable, not a parameter.',
 'harmonic': 'The Lab varies stiffness, mass, initial_position and initial_velocity. It renders an analytic position curve, with no compiled spatial object or direct handle. The frozen prospective list names mass/stiffness/amplitude/phase; initial conditions in the actual declaration require review against the general solution on original pp.8–9. time is the Lab x variable, not a parameter.',
 'circuits': 'The main output contains a voltage-response Lab varying input_voltage, initial_voltage and the lumped time_constant; R and C are not separate controls. The first planner was rejected. time is the Lab x variable, not a parameter. The displayed example defaults and hypothetical explorations must be distinguished by the human reviewer.',
 'signals': 'The Lab holds component frequencies at 440 and 880 Hz in expressions and varies amplitudes and a sine phase. It does not resynthesize the recorded bell/violin data. The additional phase control needs source-support review as an explicitly hypothetical exploration.',
 'regression': 'corr is adjustable from -0.6 to 0.6, with the observed correlation -0.499 as its default. The expression consequently changes the fitted slope while sample means and standard deviations are numeric constants. Frozen expectations permit prediction input variation and preserve the sample statistic/fitted result; they do not preauthorize an adjustable trial fit.',
 'probability': 'The selected family is dynamic Numeric Lab, not probability_sets. prob_a and prob_b vary between 0.25 and 0.5; overlap is the plotted x variable. No shared finite-outcome/event-membership declaration, exact set runtime or Monte Carlo scene was compiled. Compare the hypothetical probability sliders with frozen source event memberships and outcome weights.',
 'search': 'The frozen PDF contains basic Python-operation/loop analysis on original p.226 and search algorithms on p.227. The actual selected Lab varies body-cost exponent a and fixed factor k in loop-growth curves; no bisection/linear-search process was compiled. This is an observed focus difference for human review, not a final source-correctness verdict.',
 'complexity': 'The Lab varies coefficient a from 2 to 200 (source-example default 100) and plots a*n+1 against n**2+n+1. Frozen expectations keep source coefficients fixed and permit integer input size n; the generated plot samples n continuously and labels integer sizes as the algorithmic interpretation.',
 'spectrum': 'The selected family is static and the main analysis contains no Lab. This exercises a table/concept presentation rather than frequency/wavelength conversion controls. The frozen expectation permits an honest static table.',
 'debugging': 'The selected family is static, with a concept map and no Numeric Lab. There is no drag/slider expectation for this source. The interpreter/code examples remain source data and were not executed.'
}

def main():
 corpus,gold=verify()
 first=read(PUBLIC/'first-pass-results.json')
 deep=read(PUBLIC/'deep-results.json'); stable=read(PUBLIC/'stability-results.json')
 for name in ('first-pass','deep','stability'):
  frozen=read(PUBLIC/(name+'-freeze.json'))
  for path,expected in frozen['files_sha256'].items():
   assert sha(ROOT/path)==expected, 'Frozen artifact changed: '+path

 # Preserve every timestamped/initial browser observation, including tooling
 # failures. Latest pointers cannot erase an attempt from this report.
 browser_dir=PRIVATE/'browser'
 attempts=[]
 for p in sorted(browser_dir.glob('*-results.json')):
  if p.name.endswith(('-desktop-results.json','-narrow-results.json')):continue
  r=read(p)
  attempts.append(dict(path=str(p.relative_to(ROOT)).replace('\\','/'),sha256=sha(p),observation=r))
 latest={}
 for cid in gold['deep_subset']+['debugging']:
  p=browser_dir/(cid+'-desktop-results.json')
  latest[cid]=read(p) if p.exists() else dict(success=False,error='No browser observation')
 narrow=read(browser_dir/'harmonic-narrow-results.json')
 events=[json.loads(line) for line in (browser_dir/'events.jsonl').read_text(encoding='utf-8').splitlines() if line]
 browser=dict(scope='Empty production app, real PDF upload and exact recorded first-attempt response replay. This is browser acceptance of those attempts, not another paid/independent generation.',
  actual_network_requests=sum(e.get('new_network_requests',0) for e in events),
  replay_context_mismatches=[e for e in events if e.get('context_matches') is False],
  blocked_unrecorded_requests=[e for e in events if e['kind']=='blocked_unrecorded_response'],
  cases=latest,narrow_observation=narrow,all_attempts=attempts,
  tooling_note='Early observer runs advanced before rerun completion; later waits observe real session snapshots. Selecting an already active page makes no rerun. All attempts are preserved. No production code or model declaration was repaired.')
 write_new(PUBLIC/'browser-results.json',browser)

 # Raw planner changes remain observable even when normalized output is absent.
 stability_detail=[]
 for c in stable['cases']:
  cid=c['material_id'];rs=[read(PRIVATE/'responses'/f'{cid}--stability-planner-{n}.json') for n in (1,2,3)]
  request_hashes=[r['request_sha256'] for r in rs]
  assert len(set(request_hashes))==1,'Stability requests differ'
  decl=[{k:r['raw'].get(k) for k in ('version','preferred','focus_ids','source_pages','features','process','execution')} for r in rs]
  drift={k:len({digest(d[k]) for d in decl})>1 for k in decl[0]}
  stability_detail.append(dict(material_id=cid,accepted=[r['accepted'] for r in c['runs']],
    identical_complete_request_sha256=request_hashes[0],raw_contract_declarations=decl,raw_contract_differences=drift,
    normalized_differences=c['drift_categories'],
    not_measured=['parameter generation','quantity kinds','domain constraints','fixed/adjustable generation','ranges','quantities','bindings','inverse bindings','duration policy'],
    limitation='No spatial/probability compiler was selected. Native Lab declarations remain in the fixed main analysis; empty planner fields are not evidence of parameter-generation stability. With fewer than two accepted outputs, normalized stability cannot be established.',
    A='HUMAN_REVIEW_PENDING'))
 write_new(PUBLIC/'stability-comparison.json',dict(cases=stability_detail,accepted_samples=sum(sum(c['accepted']) for c in stability_detail),denominator=12,A='HUMAN_REVIEW_PENDING'))

 usage=usage_summary()
 stage_totals={prefix:usage_summary(prefix) for prefix in ('first-','deep-','stability-')}
 for v in stage_totals.values():
  ts=[r['seconds'] for r in v['requests']]
  v['latency_seconds']={'sum':sum(ts),'mean':statistics.mean(ts),'min':min(ts),'max':max(ts)}
 usage.update(stage_totals=stage_totals,model='gpt-6.1-sol',reasoning_effort='medium',
    browser_replay_model_requests=0,file_upload_count=len(list((PRIVATE/'uploads').glob('*.json'))),
    usage_note='Elapsed request latency sum is not total wall-clock task duration. Billing was not independently observed; no cost is estimated.')
 write_new(PUBLIC/'request-usage-all-stages.json',usage)

 # Do not alter the original packet frozen immediately after first pass.
 # Append more page-specific evidence, raw rejected planner output and later
 # observations as a separately hashed supplement.
 corrected=copy.deepcopy(read(PUBLIC/'source-evidence.json'))
 corrected['cases']['harmonic'][0]['formula_or_concept']='y(t) = A sin(2*pi*t/T); later pages introduce angular frequency and phase'
 corrected['cases']['regression'][2]['formula_or_concept']='Rounded worked line: aid_hat = 24327 - 0.0431*income (dollars); software summary intercept 24319.3'
 corrected['cases']['search']=[
  dict(page=226,evidence='Basic Python-operation costs and general loop-growth rules precede the search section.',formula_or_concept='O(n^a) body repeated n times gives O(n^(a+1)); fixed k does not change growth order',fixed_condition='These are complexity rules, not measured timing data.'),
  dict(page=227,evidence='Linear search scans the collection; bisection halves a sorted sequence, and hash-table lookup is separately discussed.',formula_or_concept='Linear O(n); sorted bisection O(log n)',fixed_condition='Bisection requires sorted input; no resolved hypothetical input sequence is provided.')]
 corrected['preparation_note']='This supplementary evidence clarifies locations/rounded regression estimates in the original evidence draft. Corpus, expectations and the original frozen first-pass packet remain unchanged.'
 write_new(PUBLIC/'source-evidence-supplement.json',corrected)
 packet=review_packet(corpus,gold,first['cases'])
 original_evidence=read(PUBLIC/'source-evidence.json')
 def fact_line(fact):
  return '- Original PDF p.'+str(fact['page'])+': '+fact['evidence']+' Formula/concept: '+fact['formula_or_concept']+'. Fixed condition: '+fact['fixed_condition']
 for cid in ('harmonic','regression','search'):
  old='\n'.join(fact_line(f) for f in original_evidence['cases'][cid])
  new='\n'.join(fact_line(f) for f in corrected['cases'][cid])
  assert old in packet
  packet=packet.replace(old,new,1)
 packet+='\n# Additional objective review observations\n\nThe first-pass packet remains immutable. These later observations do not change expectations, outputs or A-axis verdicts. See source-evidence-supplement.json for precise source-location and rounded-estimate clarifications.\n'
 for row in first['cases']:
  cid=row['material_id'];raw=read(PRIVATE/'responses'/f'{cid}--first-planner.json')['raw']
  packet+='\n## '+cid+'\n\n'+OBSERVATIONS[cid]+'\n\nOriginal planner declaration (including rejected declarations):\n\n```json\n'+json.dumps(raw,ensure_ascii=False,indent=2)+'\n```\n'
  dc=next((d for d in deep['cases'] if d['material_id']==cid),None)
  if dc:
   packet+='\nDeep source-to-runtime objective observation:\n\n```json\n'+json.dumps(dc,ensure_ascii=False,indent=2)+'\n```\n'
   detail=read(PRIVATE/'deep'/(cid+'.json'))
   packet+='\nActual generated Source Atlas regions (estimated boxes/transcriptions, requiring human location/semantic review):\n\n```json\n'+json.dumps(detail.get('atlas'),ensure_ascii=False,indent=2)+'\n```\n'
  if cid in latest:
   b=latest[cid];packet+='\nBrowser observations: '+json.dumps({k:b.get(k) for k in ('success','source_selected','focus_preserved','source_view_unchanged','canonical_value_changed','linked_chart_changed','post_compilation_response_attempts','post_compilation_network_delta','error')},ensure_ascii=False)+'\n'
  sc=next((c for c in stability_detail if c['material_id']==cid),None)
  if sc:packet+='\nStability raw/normalized comparison:\n\n```json\n'+json.dumps(sc,ensure_ascii=False,indent=2)+'\n```\n'
  packet+='\n**Human A verdict: PENDING.**\n'
 with (PUBLIC/'semantic-review-supplement.md').open('x',encoding='utf-8',newline='\n') as f:f.write(packet)

 first_rows=[]
 for r in first['cases']:
  first_rows.append(dict(material_id=r['material_id'],B=r['B'],A='HUMAN_REVIEW_PENDING',
    schema=r.get('main_schema_valid'),planner=r.get('planner_result'),compiler=r.get('compiler_result'),
    validator=r.get('validator_result'),family=r.get('representation_family'),
    runtime=r.get('runtime_result'),raw_analysis_refs=r.get('analysis_refs'),failure=r.get('failure_reason'),
    scope=r.get('B_scope','First planner rejected; later fallback checks cannot replace this first result.')))
 deep_rows=[]
 for c in deep['cases']:
  cid=c['material_id'];b=latest[cid]
  mechanical=bool(b.get('success') and b.get('source_selected') and b.get('focus_preserved') and b.get('source_pdf_immutable') and b.get('source_view_unchanged') and b.get('canonical_value_changed') and b.get('post_compilation_response_attempts')==0 and not b.get('page_errors'))
  compiled_links=(c.get('linked_support') or {}).get('representation_ids',[])
  deep_rows.append(dict(material_id=cid,local_probe_B=c['B'],browser_mechanics='PASS' if mechanical else 'PARTIAL',
    selected_source_semantic_id=c.get('selected_semantic_id'),compiled_twin_representation_ids=compiled_links,
    full_compiled_twin_chain='PASS' if mechanical and compiled_links else 'PARTIAL',
    limitation='Selected semantic source region has no compiled Twin representation IDs. Numeric Lab and source focus work, but a complete explicit source-entity-to-linked-representation chain is not established.' if not compiled_links else None,
    direct_drag='NOT_APPLICABLE_TO_GENERATED_REPRESENTATION' if not c['direct_manipulation']['available'] else 'PRESENT',
    canonical_value_changed=b.get('canonical_value_changed'),linked_chart_changed=b.get('linked_chart_changed'),
    source_roundtrip=b.get('roundtrip_mode'),source_immutable=b.get('source_pdf_immutable'),
    post_compilation_api_delta=b.get('post_compilation_response_attempts'),
    baseline_rejection_scope=c.get('baseline_current_separation'),A='HUMAN_REVIEW_PENDING'))
 score=dict(first_pass_denominator=10,first_pass_counts=dict(Counter(r['B'] for r in first_rows)),
   first_pass=first_rows,deep=deep_rows,
   boundary='First-pass B is backend contract/local runtime only. Later browser fallback success does not replace the two first-pass FAILs. A-axis semantic/source correctness is never assigned by this observer.',
   atomic_rejection_scope='All deep cases used Numeric Lab. Stale generation callbacks were checked; this is not a Spatial World atomic-patch/inverse rejection test.',
   browser_errors=sum(len(b.get('page_errors',[])) for b in latest.values()),
   full_spatial_or_probability_scene_coverage=False,A='HUMAN_REVIEW_PENDING')
 write_new(PUBLIC/'engineering-scorecard.json',score)

 taxonomy=dict(status='DRAFT_FOR_HUMAN_REVIEW; no production repair or final A judgment',
  mechanical=[
    dict(kind='planner source-page provenance rejection',cases=['circular'],first_pass_count=1,observation='A declared page is outside the focused semantic entities\u2019 page union.'),
    dict(kind='planner plain-text contract rejection',cases=['circuits'],first_pass_count=1,observation='Schema-valid reason contains an ASCII greater-than operator rejected by the existing plain-text contract.'),
    dict(kind='stability acceptance drift',cases=['circular'],observation='One accepted and two rejected declarations; original denominator 3 remains. Raw source pages change while the normalized single accepted sample cannot establish stability.'),
    dict(kind='stability contract rejections',cases=['harmonic'],observation='Three schema-valid declarations rejected by the existing plan contract; all contain ASCII greater-than signs.'),
    dict(kind='explicit Twin representation link coverage gap',cases=gold['deep_subset'],observation='Selected source meanings have empty compiled Twin representation_ids; local Lab changes and source focus alone do not prove a full compiled Twin chain.')],
  semantic_review_flags=[dict(case=k,objective_observation=v,A='HUMAN_REVIEW_PENDING') for k,v in OBSERVATIONS.items()],
  observer_limitations=['Planner-only stability does not regenerate native Lab parameters.','Early browser automation timing/same-value-selector timeouts are preserved separately from production failures.','Headless automated browser observations are not human novice acceptance.','Atlas geometry/links remain estimated; source fidelity and materiality need human review.'],
  responsibility='Mechanical rejection boundary is observed. Whether an unsupported model declaration, product contract, source expectation or observer limitation causes a semantic learning problem is not finalized here.')
 write_new(PUBLIC/'failure-taxonomy.json',taxonomy)

 # Freeze raw stage responses and all browser observations without publishing
 # request rasters, source bodies, file credentials, or transport internals.
 private_hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)
  for directory in ('responses','cases','deep','browser','uploads')
  for p in sorted((PRIVATE/directory).glob('*')) if p.is_file()}
 write_new(PUBLIC/'private-evidence-hashes.json',dict(scope='Local ignored evidence; includes exact requests/responses and browser attempts. No secrets/headers are recorded.',files_sha256=private_hashes))
 # Public documentation is a report, not a repaired product/benchmark run.
 table=['| Material | First planner | Family | First B | A |','|---|---|---|---|---|']
 for r in first_rows:
  table.append('| '+r['material_id']+' | '+str(r['planner'])+' | '+str(r['family'])+' | '+r['B']+' | Human review pending |')
 evidence='''# Day 27 — frozen benchmark evidence awaiting human semantic review

This checkpoint completes the authorized FIRST PASS, DEEP and STABILITY generation stages and then stops. It does not mark the entire original Day27 hardening acceptance gate complete. No benchmark-driven production fixes, post-fix replay, commit, push or Day28 work occurred.

Production configuration: exact requested and returned model `gpt-6.1-sol`, reasoning effort `medium`. All 37 actual response requests used this configuration, zero SDK retries and zero semantic retries. The expectation/corpus/subset hashes and the 78-file production baseline were verified before requests and after reporting. Model output was evaluated without changing production prompts, schemas, normalizers, validators or renderers.

## First-pass denominator: all ten

'''+ '\n'.join(table)+'''

The 8 PASS / 2 FAIL count is **B-axis backend contract/local runtime only**. All 20 first-pass responses passed their strict JSON schema. Circular motion was rejected at source-page provenance; RC was rejected by the planner plain-text contract (ASCII `>` in the reason). These failures remain in the original denominator. Later working Numeric Lab or Source fallback does not replace them. There is no final A-axis verdict or overall semantic pass rate.

Raw declarations, first-pass results, request usage and the initial human-review packet were written and hashed immediately after ten cases. [First freeze](day27/first-pass-freeze.json) remains unchanged. A separately hashed [review supplement](day27/semantic-review-supplement.md) adds precise source evidence, raw rejected planner declarations, actual Atlas output, fixed/adjustable observations and later deep/stability evidence. It clarifies two source-location/formula paraphrases and the rounded versus software regression estimates; it does not alter frozen expectations or original results.

## Deep: five cases

The frozen five are circular, harmonic, circuits, probability and search. [Deep local results](day27/deep-results.json) preserve the initial local probe and [browser results](day27/browser-results.json) preserve actual empty-app upload, source-object selection, canonical focus, bounded slider changes, chart updates and Return to Source using the original recorded model output. This is first-attempt response replay through production UI, not a new independent holdout generation.

No case produced a valid direct drag handle. The observer retained existing controls rather than forcing one. The native Lab is the canonical parameter owner. Compiled defaults and current values are separate; stale callback generations were rejected. No Spatial World atomic inverse/patch path or finite-set runtime was selected, so those capabilities are not certified by these cases.

All five selected source meanings have empty compiled Twin `representation_ids`. Therefore local browser mechanics and the complete explicit source-entity-to-linked-representation chain are scored separately: the latter is PARTIAL. Atlas regions/transcriptions remain estimated and require human grounding review. See [engineering scorecard](day27/engineering-scorecard.json).

Early automation observations moved before a rerun completed or waited for a no-op selection; one RC keypress initially pointed beyond its already maximal slider value. Every observation remains in the archive and final browser report. The observer subsequently waited for real production snapshots and selected a legal slider direction. This involved no production fix, declaration edit or new generation. Desktop evidence is 1440×1000, with one 880×1000 SHM observation; this is not broad mobile certification or a timed novice study.

## Stability: fixed stored analysis, three independent identical requests each

| Material | Accepted / 3 | Objective differences |
|---|---|---|
| circular | 1 / 3 | Raw source_pages changes; two provenance rejections. One accepted sample cannot establish normalized stability. |
| harmonic | 0 / 3 | Three plan-contract rejections; no accepted normalized output. |
| circuits | 3 / 3 | Compared planner structure and source pages unchanged. |
| probability | 3 / 3 | spatial_relations feature changes in the second declaration. |

Complete request hashes are identical within each case's three requests. These are the frozen protocol's planner fallback declarations; no spatial/probability compiler was selected in first pass. Native Lab parameters/quantities stay in stored main analysis. Parameter IDs, quantity kinds, domains, fixed/adjustable generation, ranges, bindings/inverses and duration generation are **not measured**, rather than declared stable from empty planner fields. Raw rejected source-page changes are retained alongside accepted normalized comparisons. Materiality/source justification remains human A-axis review. [Comparison](day27/stability-comparison.json), [original stability results](day27/stability-results.json).

## Requests, tokens and latency

| Stage | Requests | Input tokens | Output tokens | Sum of request latency |
|---|---:|---:|---:|---:|
| First pass | 20 | 188,298 | 59,380 | 921.964 s |
| Deep Atlas | 5 | 45,098 | 19,107 | 252.740 s |
| Stability | 12 | 57,795 | 5,366 | 113.879 s |
| Total | 37 | 291,191 | 83,853 | 1,288.583 s |

Latency sum is not elapsed task time. Token detail, request-level models, schema results, reasoning tokens/cache usage, latency and exact request digests are in [all-stage usage](day27/request-usage-all-stages.json). Ten PDF uploads are separate from model generations. Browser replay invokes no network model requests. Post-compilation interaction request delta is 0; explicit Atlas compilation is excluded from this interaction interval. No billing estimate is presented.

## Human semantic review

The [initial packet](day27/semantic-review-packet.md) and [complete supplement](day27/semantic-review-supplement.md) provide source page mappings/evidence/formulas/fixed conditions, actual model content, adjustable declarations, representation choice, grounding, affordance absence, suspected unsupported semantics and objective differences. Human review should inspect particularly adjustable correlation/fitted regression, adjustable die/card probability exploration, the search case's loop-growth focus and adjustable source-example coefficients. These are review flags, never agent-assigned A-axis FAILs.

[Failure taxonomy draft](day27/failure-taxonomy.json) distinguishes observed contract rejection, stability variation, explicit Twin coverage, semantic review flags and observer limitations. Attribution: AI-drafted, human-reviewed and approved before model execution.

## Corpus, tests and artifacts

The ten frozen subsets come from MIT OCW, Think DSP, Think Python, OpenIntro Statistics and NASA teaching materials. [Manifest](day27/corpus-manifest.json) supplies exact original URLs, pages, terms, original/subset SHA-256 and evaluation-page mappings. Original PDFs and request/raster bodies remain ignored local files. NASA's subset is the unit-conversion table only; third-party photographs were excluded. Existing PyMuPDF AGPL/commercial deployment obligations remain unresolved.

The one full pre-benchmark regression run passed 458 tests (251.025 seconds). Final observer-focused verification passed 5 tests (0.201 seconds); a preceding module-style invocation failed because the test-directory import path was absent, then the correct unittest discovery invocation passed. This was a test-runner issue, not a corpus outcome. No full regression was rerun after generation, and no production file changed after the baseline freeze. No new dependencies were added.

[All artifact hashes](day27/artifact-hashes.json) includes frozen expectations/corpus, stage freezes, outputs, review packets and exactly four public screenshots. The hash manifest excludes itself; its own SHA-256 is reported separately. Ignored exact requests/responses/browser histories are sealed by [private evidence hashes](day27/private-evidence-hashes.json).

## Exactly four actual screenshots

1. SHM: analytic curve and baseline/current after local parameter change — [screenshot](day27/01-harmonic-explore.png).
2. Probability: the actual generated Numeric Lab/sliders, offered for source-semantic review — [screenshot](day27/02-probability-explore.png).
3. Debugging: honest static concept map, no invented handle — [screenshot](day27/03-debugging-static.png).
4. Circular: source view after planner rejection and local fallback exploration, preserving original evidence/focus — [screenshot](day27/04-circular-rejection.png).

Stop here and wait for human A-axis review. There is no hardening selection or post-fix score yet.
'''
 with (ROOT/'docs/DAY27_EVIDENCE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(evidence)
 checkpoint='''# Day 27 checkpoint — stopped for human semantic review

Starting branch `day17-learning-scene-wip`, HEAD `477de4926220d0960b58500f292ea6df24154da6`; initial tree clean. No checkout/reset/commit/push. This checkpoint is the three-stage frozen baseline, not completion of failure-driven hardening.

Pre-benchmark changes already frozen before any response:

| Files | Purpose |
|---|---|
| model_config.py; app.py; learning_world/compiler.py; scene/compiler.py; source_atlas/compiler.py; analogy/compiler.py; dynamic_simulation.py | One production `gpt-6.1-sol` / `medium` request configuration across all eight Responses call sites. |
| scene/world/schema.py, policy.py, engine.py, validator.py | Separate quantity kind from explicit positive/non-negative/signed domain; enforce declared bounds in compilation and local state. |
| tests/test_day27.py; tests/world_fixtures.py; tests/test_day26_parameter_semantics.py; tests/test_day23_phase_c.py; tests/manual_phase_c.py | Model/domain regressions and current-version copies of historical fixtures. Historical Day26 evidence/declarations remain unchanged. |
| .gitignore | Ignore .day27-local corpus/request/browser files. |

Benchmark/report files added: tests/day27_sources.py, day27_freeze.py, day27_benchmark.py, day27_browser.cjs, day27_report.py, manual_day27.py, test_day27_benchmark.py; docs/day27/ frozen manifests, raw results, usage, source evidence, review packets, independent B scorecard, drift comparison, taxonomy and hashes; DAY27_EVIDENCE.md and this checkpoint. README status/Day27 row and THIRD_PARTY_NOTICES attribution are documentation updates.

All production changes listed above preceded the frozen baseline. No benchmark-driven production change has been made. All ten first attempts and all twelve stability samples remain in their original denominators. A-axis verdicts remain exclusively human. Deep local mechanics do not establish complete compiled Twin coverage or source fidelity. Read [evidence](DAY27_EVIDENCE.md) before making product-quality claims.

No new dependency. Run the app exactly:

```powershell
python -m streamlit run app.py
```

Do not run another paid benchmark, harden failures, replay repaired cases, start Day28/29, commit or push until the user's next authorization. Frozen first-pass artifacts and expectations must remain unchanged.
'''
 with (ROOT/'docs/DAY27_CHECKPOINT.md').open('x',encoding='utf-8',newline='\n') as f:f.write(checkpoint)
 reports=[PUBLIC/n for n in ('browser-results.json','stability-comparison.json','request-usage-all-stages.json','source-evidence.json','source-evidence-supplement.json','semantic-review-supplement.md','engineering-scorecard.json','failure-taxonomy.json','private-evidence-hashes.json')]
 screenshots=sorted(PUBLIC.glob('*.png'));assert len(screenshots)==4,'Exactly four public screenshots required'
 freeze_stage('final-review',reports+screenshots+[ROOT/'docs/DAY27_EVIDENCE.md',ROOT/'docs/DAY27_CHECKPOINT.md',ROOT/'README.md',ROOT/'THIRD_PARTY_NOTICES.md'])
 verify()
 hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in sorted(PUBLIC.iterdir()) if p.is_file()}
 for p in (ROOT/'docs/DAY27_EVIDENCE.md',ROOT/'docs/DAY27_CHECKPOINT.md',ROOT/'README.md',ROOT/'THIRD_PARTY_NOTICES.md'):
  hashes[str(p.relative_to(ROOT)).replace('\\','/')]=sha(p)
 write_new(PUBLIC/'artifact-hashes.json',dict(algorithm='SHA-256',files_sha256=hashes,
  manifest_excludes_itself=True,package_sha256=digest(hashes),
  frozen_corpus_subset_hashes={c['material_id']:c['subset_sha256'] for c in corpus['materials']},
  production_fingerprint=read(PUBLIC/'prebenchmark-baseline.json')['production_fingerprint']))
 print(json.dumps(dict(request_count=usage['request_count'],input_tokens=usage['input_tokens'],output_tokens=usage['output_tokens'],seconds=usage['seconds'],first_B=score['first_pass_counts'],deep=deep_rows),ensure_ascii=False))

if __name__=='__main__':main()
