"""Offline evidence assembly; never invokes a provider or alters historical inputs."""
from pathlib import Path
from collections import defaultdict
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/day29'


def write_json(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')


def costs():
    old = json.loads((ROOT/'docs/day27/post_fix/request-usage.json').read_text(encoding='utf-8'))
    groups = defaultdict(list)
    for row in old['requests']:
        usage = row.get('usage') or {}
        details = usage.get('input_tokens_details') or {}
        total = usage.get('input_tokens', 0)
        cached = details.get('cached_tokens', 0)
        writes = details.get('cache_write_tokens', 0)
        output = usage.get('output_tokens', 0)
        assert 0 <= cached + writes <= total
        groups[row['stage']].append(dict(input_tokens=total, cached_tokens=cached,
            cache_write_tokens=writes, output_tokens=output,
            estimated_usd=((total-cached-writes)*2+cached*.1+writes*2.5+output*10)/1e6))
    write_json('cost-estimates.json', dict(
        measurement='Historical Day27 POST_FIX usage repriced, not Day29 requests or an invoice',
        source='docs/day27/post_fix/request-usage.json', request_count=old['request_count'],
        official_price_source='https://developers.openai.com/api/docs/models/gpt-6.1-sol',
        retrieved='2026-10-12', model='gpt-6.1-sol', reasoning='medium',
        usd_per_million=dict(input=2, cached_input=.1, cache_write=2.5, output=10),
        assumptions='Input detail buckets are disjoint; reasoning is included in output, not charged twice. Standard tier; no tax, long-context premium or contract adjustment.',
        groups={key:dict(count=len(rows), total_estimated_usd=sum(r['estimated_usd'] for r in rows),
                        minimum_estimated_usd=min(r['estimated_usd'] for r in rows),
                        maximum_estimated_usd=max(r['estimated_usd'] for r in rows),
                        totals={k:sum(r[k] for r in rows) for k in ('input_tokens','cached_tokens','cache_write_tokens','output_tokens')})
                for key,rows in groups.items()},
        unmeasured_actions='Explain This, Focused Review, Dynamic Simulation and Analogy have no measurements in this historical record; token caps are not input-cost ceilings.',
        day29_paid_requests=0))


def matrix():
    rows = json.loads((OUT/'red-team-results.json').read_text(encoding='utf-8'))
    text = '# Day29 adversarial matrix\n\nOffline mocked declarations and pure boundary tests. PASS is limited to the recorded attack; no paid model probe or hostile-PDF process sandbox was tested. Rows are emitted after assertions, so the final unittest outcome must also be checked.\n\n'
    text += '| Attack | Expected defense | Observed | Status |\n|---|---|---|---|\n'
    for row in rows:
        text += '| '+' | '.join(str(row[k]).replace('|','/').replace('\n',' ') for k in ('attack','expected_defense','observed','status'))+' |\n'
    text += '\nAdditional observed browser boundary: two distinct Streamlit sessions on the same loopback server, real prepared PDF A and synthetic text B; B showed only its source canary, no A title or PDF page. PASS for this bounded smoke, not a hostile multi-tenant audit. See browser-results.json.\n\nExcessive agency: all eight generation paths use a server-denied default factory, no model tool definitions, fixed instructions and declarative validation. A default-mode configured credential cannot initialize a paid client. Forbidden expression calls/attributes/indexing and forged reducer events are exercised offline. No shell/GitHub/network action is driven by source content. Actual model prompt-injection behavior remains PARTIAL.\n\nCoverage: injection; expression/JSON/semantic attacks; XSS fixed text and escaped graph boundaries; file/resource envelopes; state/session isolation; excessive agency; failure/cost boundaries. Redacted synthetic failures cover nine client outcomes. Refer to test_day29.py for exact payloads and assertions.\n'
    (OUT/'red-team-matrix.md').write_text(text,encoding='utf-8')


def finalize():
    log=(OUT/'final-regression.log').read_text(encoding='utf-8',errors='replace')
    match=re.search(r'Ran (\d+) tests in ([\d.]+)s',log)
    assert match, 'Regression must finish before evidence is finalized'
    exit_code=int((OUT/'final-regression-exit.txt').read_text().strip())
    guard=json.loads((OUT/'final-request-guard.json').read_text(encoding='utf-8'))
    clean=json.loads((OUT/'clean-smoke-results.json').read_text(encoding='utf-8'))
    historical=json.loads((OUT/'historical-integrity.json').read_text(encoding='utf-8'))
    advisory=json.loads((OUT/'dependency-advisories.json').read_text(encoding='utf-8'))
    browser=json.loads((OUT/'browser-results.json').read_text(encoding='utf-8'))
    attacks=json.loads((OUT/'red-team-results.json').read_text(encoding='utf-8'))
    screenshots={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.glob('0[1-4]-*.jpg'))}
    inventory=json.loads((OUT/'changed-files.json').read_text(encoding='utf-8'))
    indicator=re.compile(rb'(?<![A-Za-z0-9])sk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}')
    scanned=0
    for name in inventory['day29_modified_tracked']+inventory['day29_new_untracked']:
        path=ROOT/name
        if path.is_file() and path.stat().st_size<=5*1024*1024:
            scanned+=1
            assert not indicator.search(path.read_bytes()), 'Redacted indicator found; private review required'
    write_json('final-validation.json',dict(
        day=29, mode='offline/local only', starting_branch='day17-learning-scene-wip',
        starting_head='5a6ec3c8ab6e70892b2d6a299a7ef315e90cf40d',
        starting_tree='Five dirty tracked files plus existing Day28 untracked evidence/tests and workspace/control_navigation.py; preserved',
        final_regression=dict(status='PASS' if exit_code==0 else 'FAIL',exit_code=exit_code,
            count=int(match[1]),seconds=float(match[2]),failures=0 if exit_code==0 else 'see log',
            errors=0 if exit_code==0 else 'see log',log='docs/day29/final-regression.log',complete_runs=1),
        request_guard=guard,clean_smoke=clean,historical_integrity=historical,
        dependency_advisories=dict(distributions=len(advisory['dependencies']),known_advisories=sum(len(d['vulns']) for d in advisory['dependencies'])),
        browser=browser,red_team=dict(recorded_asserted_rows=len(attacks),all_recorded_rows_pass=all(r['status']=='PASS' for r in attacks)),
        changed_file_key_indicator_scan=dict(files=scanned,indicators=0,scope='Same redacted format indicator, <=5 MiB; not arbitrary-token entropy detection'),
        area_status=dict(semantic_source_integrity='PASS',input_validation='PARTIAL',secret_handling='PASS',
            prompt_injection_resistance='PARTIAL',expression_runtime_safety='PASS',xss_safety='PASS',
            session_isolation='PASS',dependency_vulnerabilities='PARTIAL',third_party_licensing='PARTIAL',
            cost_abuse_control='PASS',prepared_demo='PASS',public_live_generation='FAIL',
            clean_local_deployment='PASS',performance='PARTIAL',final_regression='PASS' if exit_code==0 else 'FAIL'),
        screenshots_sha256=screenshots,
        public_prepared_demo='Restricted noncommercial prepared-only candidate; no public deployment performed',
        live_generation='NOT READY for public access; default server-denied; private opt-in requires external controls',
        limitations=['No paid model red team','No actual Cloud deploy','Narrow viewport override did not apply: NOT TESTED','No hostile PDF process sandbox','No high-concurrency load test','Historical AGPL and commercial distribution review remain open'],
        commit=False,push=False,credential_rotation=False))


if __name__=='__main__':
    costs()
    matrix()
    finalize()
