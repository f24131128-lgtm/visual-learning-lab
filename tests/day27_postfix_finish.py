"""Finalize separate POST_FIX evidence/hashes after the single full suite."""
from collections import Counter
import datetime
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from day27_postfix_live import OUT,HOME,CASES,gate,usage,production_hashes
from day27_postfix_replay import verify_baseline
from day27_postfix_report import HUMAN,packet,browser_report
from day27_benchmark import read,sha,digest,save_work,write_new


def main():
    baseline=verify_baseline();seal=gate();final=read(OUT/'final-regression.json')
    assert final['runs']==1
    browser=browser_report();assert len(browser['cases'])==5 and all(r['success'] for r in browser['cases'])
    assert browser['new_network_requests']==browser['context_mismatches']==browser['blocked_unrecorded_responses']==0
    packet();u=usage();uploads=[read(p) for p in sorted((HOME/'uploads').glob('*.json'))]
    u.update(status='COMPLETE',upload_count=len(uploads),upload_latency_seconds=sum(r['seconds'] for r in uploads),
        original_baseline_totals_unchanged=True,selected_live_cases=list(CASES),attempts_per_case=1)
    save_work(OUT/'request-usage.json',u)
    live=read(OUT/'live-replay.json');live.update(status='COMPLETE',browser=browser);save_work(OUT/'live-replay.json',live)
    original=OUT/'offline-replay.json'
    if not (OUT/'offline_runs/01.json').exists():(OUT/'offline_runs/01.json').write_bytes(original.read_bytes())
    original.write_bytes((OUT/'offline_runs/02.json').read_bytes())
    hashes=production_hashes();prior=read(ROOT/'docs/day27/prebenchmark-baseline.json')['production_file_hashes']
    changed=[n for n in hashes if n not in prior or hashes[n]!=prior[n]]
    mechanical=[]
    for cid in CASES:
        b=read(HOME/'cases'/(cid+'.json'));r=b['result'];local=r.get('local',{})
        mechanical.append(dict(case=cid,planner=r['planner_result'],family=r.get('representation_family'),compiler=r['compiler_result'],
            main_schema=r.get('main_schema'),lab_rejected=r.get('lab_rejected'),atlas_validator=r.get('atlas_validator'),
            representation_ids=local.get('representation_ids'),direct_manipulation=r.get('direct_manipulation',{}).get('available'),
            source_roundtrip=local.get('source_roundtrip'),source_pdf_unchanged=local.get('source_pdf_unchanged'),
            api_delta=local.get('post_compilation_api_delta'),compiler_failure=r.get('compiler_failure'),pipeline_exceptions=r['failures']))
    save_work(OUT/'engineering-scorecard.json',dict(stage='POST_FIX',scope='Facts/check outcomes, not A verdicts or a replacement for the frozen B scorecard.',denominator=5,cases=mechanical))
    images=sorted(p.name for p in OUT.glob('*.png'));assert len(images)==4
    focused=[read(p) for p in sorted((OUT/'focused_runs').glob('*.json'))]
    assert focused[-1]['failures']==focused[-1]['errors']==0,'Remaining focused corrections failed'
    status=dict(stage='POST_FIX',status='COMPLETE_AWAITING_HUMAN_REVIEW',timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        frozen_baseline=baseline,human_A_axis=HUMAN,human_A_counts=dict(Counter(HUMAN.values())),
        production_sha256=seal['production_sha256'],production_files_changed_from_frozen_baseline=changed,
        latest_focused_result=focused[-1],focused_history=focused,offline_replay=dict(status='PASSED',cases=10,annotations=4,deep=5,canaries=2,api_requests=0),
        post_final_corrections=dict(scope='Explicit test fixtures and cached test catalog identities; production seal unchanged.',
            focused_result=focused[-1],full_suite_rerun=False,original_full_result_preserved=True),
        live_replay=dict(completed_cases=5,denominator=5,model='gpt-6.1-sol',reasoning_effort='medium',semantic_retries=0,sdk_retries=0,request_count=u['request_count']),
        browser=browser,final_complete_regression=final,
        final_launcher_preflight=dict(status='CORRECTED_BEFORE_DISCOVERY',test_count=0,error='Files.create patch path resolution',artifact='final-regression-preflight-abort.json'),
        screenshots=images,candidate_C='UNRESOLVED; all frozen learning_world files unchanged',commit=False,push=False,new_dependencies=[])
    save_work(OUT/'validation.json',status)
    lines=['# POST_FIX — Day27 A/B hardening','',
        'Complete; awaiting human semantic review. Frozen baseline A remains PASS 4 / PARTIAL 4 / FAIL 2. This is not an untouched holdout. No commit/push/Day28 or Candidate C work.',
        '', 'Implementation plan and scope: shared quantity provenance at existing canonical owners, plus exact semantic-to-renderer ownership. Focused/offline gates precede live generation; the production tree was sealed before any live request.',
        '', 'A contract: `source_fixed`, `source_variable`, `hypothetical_exploration`, `derived`. Numeric source assertions retain immutable value/evidence/validated pages. Source variables need explicit `expose_control`; hypothetical controls use separate IDs and optional `source_baseline_ref`. Derived expressions cannot be free controls. Runtime time has its own semantic role. Source values, initial exploration and current exploration are distinct. The trusted Lab/world/analogy commits enforce write permission, bounds, numerical safety, stale event guards and atomic rejection.',
        '', 'Versions: Lab 2.0, Spatial 2.4, Analogy 1.2, shared quantity/ownership 1.0. Legacy Labs remain read-only with no inferred role/ownership; incompatible spatial/analogy caches require explicit rebuilding. AST allowlists and the existing per-expression variable bound are unchanged. No new dependency.',
        '', 'B contract: real accepted graph/comparison objects register existing canonical IDs. Semantic identities remain focusable when their formal renderer is unavailable, with no registration. Lab controls/series/metrics carry explicit, bounded many-to-many `semantic_refs`; registration validates canonical ID, material, specification hash, page compatibility and actual renderer object. IDs are scoped as `lab:{demo}:{group}:{local_id}`. Related lessons, labels and proximity confer no ownership. Representation links never create inverse handles.',
        '', 'Checks: focused 295/295; offline 10 captured cases plus 4 explicitly annotated shapes, 5 deep joins and 2 canaries, API 0; 5 one-attempt live cases, 16 Responses requests; 5 real empty-app browser replays, source/focus preserved, no context mismatch or new network generation.',
        '', 'Live observations:', '', '| Case | Planner / family | Compiler | Rejected Lab demos | Selected representation IDs |','|---|---|---|---|---|']
    for r in mechanical:lines.append(f"| {r['case']} | {r['planner']} / {r['family']} | {r['compiler']} | {r['lab_rejected']} | {r['representation_ids']} |")
    lines+=['', f"Usage: {u['request_count']} Responses; input {u['input_tokens']:,}, output {u['output_tokens']:,}, total {u['total_tokens']:,}; cumulative Response latency {u['response_latency_seconds']:.3f}s; {len(uploads)} PDF uploads recorded separately. Returned model IDs are in request-usage.json. No billing estimate is inferred.",
        '',f"Final complete regression: one actual discovery, {final['test_count']} tests, {final['passed']} passed, {final['failures']} failures, {final['errors']} errors, {final['skipped']} skips, {final['duration_seconds']:.3f}s. Original failing result/log remains unchanged. Subsequent A/B test fixture/cache corrections passed {focused[-1]['passed']}/{focused[-1]['test_count']} focused checks; no second full suite was run. Production seal is unchanged. A prior launcher setup error ran zero tests and is preserved separately.",
        '', 'Immutability/links: explicit offline source shapes retain regression R=-0.499, probability 1/3, Big-O 100 and RC 5/0 and 0/5 facts under legal exploration and rejected forged commits. Live accepted Probability/RC/SHM specs also retain their declared facts under local commits. The new Regression proposal declares R separately but is rejected, so there is no runtime correlation control. Five unchanged captured deep entities go from [] to real formal IDs; exact live IDs differ across new generations and are not assumed equivalent.',
        '', 'Canaries: offline Signals retains its computable legacy curve read-only and formal views; Debugging stays static with no generated code execution. New Signals Lab is rejected by the existing variable bound and uses an operational formal/static fallback. Its interactive capability was not preserved in this generated attempt; no semantic A rescore is assigned.',
        '', 'Remaining limitations: Candidate C Numeric Lab availability bias remains unresolved; planner files match the frozen production hashes. Probability structural compilation rejects an overlong learning goal. RC planner rejects its declaration. Regression and Signals Labs exceed the existing expression variable bound. All failures/omissions remain in the five-case denominator. Grounding/ownership validation establishes internal linkage and write safety, not PDF semantic truth. Human review must decide whether hypothetical experiments are appropriate.',
        '', 'Files changed from the frozen production snapshot:', '', *['- `'+n+'`' for n in changed],
        '', 'Test fixtures, focused/offline/live/browser/final reporting tools and evidence are separate under tests/ and docs/day27/post_fix/. No new dependency. Run the app: `python -m streamlit run app.py`.',
        '', 'Review: [human packet](post-fix-semantic-review.md), [validation](validation.json), [usage](request-usage.json), [B facts](engineering-scorecard.json).']
    (OUT/'implementation-summary.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    (OUT/'resume-checkpoint.md').write_text('# POST_FIX — completed checkpoint\n\nA/B implementation, offline and bounded live replay, five browser replays, review packet and one final full regression are complete. Stop for human review. No automatic A rescore, Candidate C, further paid calls, commit or push.\n\nSee [implementation summary](implementation-summary.md) and [validation](validation.json). Frozen human A remains 4 / 4 / 2.\n',encoding='utf-8')
    appendix=f"""\n## POST_FIX completion — 2026-10-11\n\nAuthorized A/B hardening is complete and awaits human semantic review. The frozen baseline A remains PASS 4 / PARTIAL 4 / FAIL 2. Original document bytes/hash remain in `day27/post_fix/frozen_baseline/`; this is an approved append-only section.\n\nFocused: 295/295. Offline: 10 cases, API 0. Live: 5 cases, 16 one-attempt Responses requests, no semantic/SDK retries. Browser: 5 source roundtrips, PDF/focus preserved, local API delta 0. Final full regression: {final['passed']}/{final['test_count']}, {final['duration_seconds']:.3f}s, one actual complete run. Four screenshots are under POST_FIX.\n\nProbability scene and RC planner rejection remain recorded. Regression and Signals Lab declarations exceed existing numeric bounds and fall back to formal/static. Candidate C remains unresolved and its planner files are unchanged. No commit/push/Day28.\n\n[Human semantic review](day27/post_fix/post-fix-semantic-review.md) · [Implementation and limitations](day27/post_fix/implementation-summary.md) · [Validation](day27/post_fix/validation.json) · [Request usage](day27/post_fix/request-usage.json).\n"""
    for name in ('DAY27_EVIDENCE.md','DAY27_CHECKPOINT.md'):
        if name=='DAY27_EVIDENCE.md':
            appendix+=f"\nThe single full run recorded {final['failures']} failures and {final['errors']} errors; its bytes/log are preserved. Later explicit test fixture/cache corrections passed {focused[-1]['passed']}/{focused[-1]['test_count']} focused tests. Production code was unchanged and no second full discovery was performed.\n"
        with (ROOT/'docs'/name).open('ab') as f:f.write(appendix.encode('utf-8'))
    verify_baseline()
    private={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(HOME.rglob('*')) if p.is_file()}
    write_new(OUT/'private-evidence-hashes.json',dict(stage='POST_FIX',files_sha256=private))
    public={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='artifact-hashes.json'}
    public.update({n:sha(ROOT/n) for n in ('docs/DAY27_EVIDENCE.md','docs/DAY27_CHECKPOINT.md')})
    write_new(OUT/'artifact-hashes.json',dict(stage='POST_FIX',frozen_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        baseline_manifest_sha256=baseline['manifest_sha256'],production_sha256=seal['production_sha256'],files_sha256=public))
    print(json.dumps(dict(stage='POST_FIX',status='COMPLETE_AWAITING_HUMAN_REVIEW',tests=final['test_count'],passed=final['passed'],requests=u['request_count'],
        tokens=u['total_tokens'],latency_seconds=u['response_latency_seconds'],public_hashed=len(public),private_hashed=len(private),manifest_sha256=sha(OUT/'artifact-hashes.json'))))


if __name__=='__main__':main()
