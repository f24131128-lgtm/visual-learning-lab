"""Exactly one final full discovery after POST_FIX implementation/replay."""
import datetime
import io
import json
import logging
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from day27_postfix_live import OUT,HOME,CASES,gate
from day27_benchmark import write_new,read,save_work


def main():
    gate()
    assert all((HOME/'cases'/(c+'.json')).exists() for c in CASES)
    assert all(read(HOME/'browser'/(c+'-desktop-results.json'))['success'] for c in CASES)
    assert (OUT/'post-fix-semantic-review.md').exists()
    attempt=OUT/'final-regression.attempt.json'
    if attempt.exists():
        assert not (OUT/'final-regression.json').exists()
        assert not (OUT/'final-regression.log').exists()
        # The first launcher failed resolving Files.create before discovery.
        # Preserve it; zero tests ran and no complete suite was consumed.
        attempt.rename(OUT/'final-regression-preflight-abort.json')
    write_new(attempt,dict(stage='POST_FIX',suite='unittest discovery tests/',attempt=1,
        started_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),paid_api_allowed=False))
    for name in ('streamlit','streamlit.runtime.scriptrunner_utils.script_run_context','streamlit.runtime.state.session_state_proxy'):
        logging.getLogger(name).setLevel(logging.ERROR)
    stream=io.StringIO();start=time.perf_counter()
    with patch('openai.resources.responses.responses.Responses.create',side_effect=AssertionError('Final regression cannot call API')),patch('openai.resources.files.Files.create',side_effect=AssertionError('Final regression cannot upload')):
        suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    record=dict(stage='POST_FIX',kind='FINAL_COMPLETE_REGRESSION',runs=1,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),test_count=result.testsRun,
        passed=result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
        failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),
        duration_seconds=time.perf_counter()-start,paid_model_requests=0,
        failures_detail=[dict(test=str(test),traceback=detail) for test,detail in result.failures+result.errors])
    (OUT/'final-regression.log').write_text(stream.getvalue(),encoding='utf-8')
    write_new(OUT/'final-regression.json',record)
    print(json.dumps({k:v for k,v in record.items() if k!='failures_detail'}))
    for row in record['failures_detail']:print(row['test']+'\n'+row['traceback'])
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__':raise SystemExit(main())
