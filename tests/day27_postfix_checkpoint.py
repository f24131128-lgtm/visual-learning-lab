"""Save an honest, offline resume point; never generate, rescore, or freeze results."""
import datetime
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/day27/post_fix"
SNAP=OUT/"frozen_baseline"


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_text(encoding="utf-8"))
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def main():
    manifest=ROOT/"docs/day27/artifact-hashes.json"
    original=read(manifest)
    checked={}
    for name,expected in original["files_sha256"].items():
        target=SNAP/Path(name).name if name in ("docs/DAY27_EVIDENCE.md","docs/DAY27_CHECKPOINT.md") else ROOT/name
        assert sha(target)==expected,name
        checked[name]=dict(resolved_path=target.relative_to(ROOT).as_posix(),sha256=expected)
    private=read(ROOT/"docs/day27/private-evidence-hashes.json")["files_sha256"]
    assert all(sha(ROOT/name)==expected for name,expected in private.items())
    baseline=read(ROOT/"docs/day27/prebenchmark-baseline.json")["production_file_hashes"]
    changed=[name for name,expected in baseline.items() if sha(ROOT/name)!=expected]
    unchanged_c=[name for name in baseline if name.startswith("learning_world/")]
    assert all(sha(ROOT/name)==baseline[name] for name in unchanged_c)
    human=dict(PASS=["SHM","Signals","NASA spectrum table","Debugging"],
               PARTIAL=["Circular motion","RC circuit","Search algorithm","Big-O"],
               FAIL=["Least-squares regression","Probability"])
    runs=[read(p) for p in sorted((OUT/"focused_runs").glob("*.json"))]
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    write(OUT/"validation.json",dict(stage="POST_FIX",status="USER_REQUESTED_CHECKPOINT",timestamp=stamp,
        frozen_baseline=dict(manifest_sha256=sha(manifest),verified_public_files=len(checked),verified_private_files=len(private),
                             snapshot_resolution=checked,human_A_axis=human,counts=dict(PASS=4,PARTIAL=4,FAIL=2)),
        implementation_status="IN_PROGRESS_NOT_FULLY_VERIFIED",focused_runs=runs,
        latest_focused_result=runs[-1],broader_focused_recheck="PENDING_AFTER_FIXTURE_REPAIRS",
        captured_shape_offline_replay="NOT_STARTED",bounded_live_replay="NOT_STARTED",
        final_complete_regression=dict(status="NOT_STARTED",runs=0),screenshots=dict(status="NOT_STARTED",new_count=0),
        candidate_C=dict(status="UNRESOLVED_NOT_IMPLEMENTED",unchanged_files=unchanged_c),
        production_files_changed_from_frozen_baseline=changed,paid_model_requests=0,commit=False,push=False))
    write(OUT/"request-usage.json",dict(stage="POST_FIX",status="NOT_STARTED",model="gpt-6.1-sol",reasoning_effort="medium",
        planned_live_cases=["regression","probability","circuits","harmonic","signals"],attempts_per_case=1,
        request_count=0,input_tokens=0,output_tokens=0,total_tokens=0,response_latency_seconds=0,
        original_baseline_totals_unchanged=True,gate="All focused checks and offline replay must pass before any paid generation."))
    append="""
## POST_FIX checkpoint — paused at the user's request (2026-10-11)

The user authorized exactly A/B hardening after freezing human A-axis results: PASS 4 / PARTIAL 4 / FAIL 2. Those results remain unchanged. Original bytes/hash of this document are preserved in `day27/post_fix/frozen_baseline/`; this section is append-only, as approved.

A/B implementation is in progress. Latest focused checkpoint: 65 tests passed, 0 failures/errors, 2.400 seconds. The earlier broader focused run exposed fixture/compatibility failures; repairs are made but a complete recheck of that affected subset remains pending. This is not a final full regression and does not establish source-semantic correctness.

Paid post-fix requests: 0. Captured-shape offline replay, bounded live replay, human review packet, one final full regression, and exactly four new screenshots have not begun. No commit or push. Candidate C planner ranking remains unchanged.

Continue from [resume checkpoint](day27/post_fix/resume-checkpoint.md) and [validation](day27/post_fix/validation.json). New evidence belongs exclusively under `day27/post_fix/`.
""".encode("utf-8")
    for name in ("DAY27_EVIDENCE.md","DAY27_CHECKPOINT.md"):
        target=ROOT/"docs"/name
        before=(SNAP/name).read_bytes()
        actual=target.read_bytes()
        assert actual in (before,before+append),name
        if actual==before:target.write_bytes(before+append)
        assert target.read_bytes().startswith(before)
    assert sha(manifest)=="818e71d84f3ec822545b0f4da90cf7978ce9540dd762fcb65f1d33443a572b19"
    print(json.dumps(dict(public_verified=len(checked),private_verified=len(private),latest_tests=runs[-1]["test_count"],
                          latest_passed=runs[-1]["passed"],paid_model_requests=0,full_suite_runs=0,baseline_manifest=sha(manifest))))


if __name__=="__main__":main()
