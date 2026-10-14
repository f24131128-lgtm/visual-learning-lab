"""Offline regression with preserved historical evidence and zero paid calls.

Usage: python -X utf8 -B tools/day30_verify.py focused|full
Historical tests write reports to older evidence paths. Restore their original
bytes after testing, so executing regressions never rewrites experiment records.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))

def main():
    mode=sys.argv[1]
    if mode not in ('focused','full','recovery'):raise ValueError('Unknown suite')
    tracked=subprocess.check_output(['git','ls-files','docs'],cwd=ROOT).decode('utf8').splitlines()
    before={ROOT/name:(ROOT/name).read_bytes() for name in tracked
            if not name.startswith(('docs/day30/','docs/DAY30_')) and (ROOT/name).is_file()}
    if '--worker' not in sys.argv:
        # Several historical tests emit reports at atexit. Restore in a parent
        # AFTER the worker exits, not before its finalizers can rewrite them.
        restored=[]
        try:
            child=subprocess.run([sys.executable,'-X','utf8','-B',str(Path(__file__).resolve()),mode,'--worker'],cwd=ROOT)
        finally:
            for p,data in before.items():
                if not p.exists() or p.read_bytes()!=data:
                    p.write_bytes(data);restored.append(str(p.relative_to(ROOT)))
        report_path=ROOT/f'docs/day30/{mode}-results.json'
        if report_path.exists():
            report=json.loads(report_path.read_text())
            report['historical_test_reports_restored']=restored
            report['restored_after_worker_finalizers']=True
            report_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
            print(json.dumps(report))
        sys.exit(child.returncode)
    before={}
    blocked=[]
    def deny(*args,**kwargs):
        blocked.append('provider_boundary');raise AssertionError('Day30 regression forbids real provider requests')
    loader=unittest.TestLoader()
    legacy_ids=set(json.loads((ROOT/'docs/day30/regression-recovery-ids.json').read_text()))
    if mode=='full':suite=loader.discover(str(ROOT/'tests'))
    elif mode=='focused':
        patterns=['test_day30.py','test_public_ai.py','test_day26.py','test_day26_parameter_semantics.py','test_day28_red_team.py','test_day24.py','test_day25.py']
        suite=unittest.TestSuite(loader.discover(str(ROOT/'tests'),pattern=p) for p in patterns)
    else:
        # Only explicit failed historical MOCKED-generation test IDs. The
        # server environment stays paid-off; this separate test process uses
        # synthetic fixtures and denied provider/real HTTP transport boundaries.
        names=json.loads((ROOT/'docs/day30/regression-recovery-ids.json').read_text())
        suite=loader.loadTestsFromNames(names)
    start=time.perf_counter();restored=[]
    legacy_seen=[]
    class ConfiguredResult(unittest.TextTestResult):
        def startTest(self,test):
            self.legacy_mode=None
            if test.id() in legacy_ids:
                self.legacy_mode=patch.dict(os.environ,{'VLL_LIVE_AI':'private','OPENAI_API_KEY':''})
                self.legacy_mode.start();legacy_seen.append(test.id())
            super().startTest(test)
        def stopTest(self,test):
            try:super().stopTest(test)
            finally:
                if self.legacy_mode:self.legacy_mode.stop()
    try:
        from contextlib import ExitStack
        with ExitStack() as stack:
            stack.enter_context(patch('openai.resources.responses.Responses.create',side_effect=deny))
            stack.enter_context(patch('openai.resources.files.Files.create',side_effect=deny))
            stack.enter_context(patch('httpx.HTTPTransport.handle_request',side_effect=deny))
            result=unittest.TextTestRunner(verbosity=1,resultclass=ConfiguredResult).run(suite)
    finally:
        for p,data in before.items():
            if not p.exists() or p.read_bytes()!=data:
                p.write_bytes(data);restored.append(str(p.relative_to(ROOT)))
    report=dict(mode=mode,tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
                successful=result.wasSuccessful(),seconds=round(time.perf_counter()-start,3),
                real_provider_calls=0,unexpected_provider_attempts=len(blocked),python=sys.version,
                historical_test_reports_restored=restored,
                isolated_legacy_mocked_generation=bool(legacy_seen),legacy_mocked_methods=len(legacy_seen))
    (ROOT/f'docs/day30/{mode}-results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
    print(json.dumps(report));sys.exit(0 if result.wasSuccessful() and not blocked else 1)

if __name__=='__main__':main()
