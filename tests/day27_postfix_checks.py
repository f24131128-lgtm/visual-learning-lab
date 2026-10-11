"""Offline focused A/B checks. This is deliberately not the final full suite."""
import datetime
import io
import logging
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
MODULES = ["test_day27_postfix", "test_day15", "test_day16", "test_day18",
           "test_day18_compiler", "test_day18_consolidation", "test_day19",
           "test_analogy", "test_analogy_diagnostics", "test_analogy_geometry",
           "test_analogy_live_bug", "test_analogy_slots", "test_day23_phase_c",
           "test_day24", "test_day25", "test_day26_parameter_semantics"]


def main():
    for name in ("streamlit.runtime.scriptrunner_utils.script_run_context", "streamlit.runtime.state.session_state_proxy", "streamlit"):
        logging.getLogger(name).setLevel(logging.ERROR)
    suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[1:] or MODULES)
    stream = io.StringIO()
    start = time.perf_counter()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    record = dict(stage="POST_FIX", kind="focused_offline", timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  modules=sys.argv[1:] or MODULES, test_count=result.testsRun,
                  passed=result.testsRun-len(result.errors)-len(result.failures)-len(result.skipped),
                  failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                  duration_seconds=time.perf_counter()-start, paid_model_requests=0)
    directory=ROOT/"docs/day27/post_fix/focused_runs"
    directory.mkdir(parents=True,exist_ok=True)
    number=len(list(directory.glob("*.json")))+1
    (directory/f"{number:02}.json").write_text(json.dumps(record,indent=2),encoding="utf-8")
    (directory/f"{number:02}.log").write_text(stream.getvalue(),encoding="utf-8")
    print(json.dumps(record))
    for test, detail in result.errors+result.failures: print(str(test)+"\n"+detail)
    return 0 if result.wasSuccessful() else 1


if __name__=="__main__":raise SystemExit(main())
