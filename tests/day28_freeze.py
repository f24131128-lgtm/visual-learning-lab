"""Freeze/verify a preparation packet only; never collects or scores humans."""
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/day28"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def product():
    seal = json.loads((ROOT / "docs/day27/post_fix/live-production-seal.json").read_text(encoding="utf-8"))
    paths = seal["production_file_hashes"]
    current = {name: sha(ROOT / name) for name in paths}
    if current != paths:
        raise ValueError("Production differs from Day27 final tree")
    tracked = git("ls-files", "-z").split("\0")
    tracked_hashes = {name: sha(ROOT / name) for name in tracked if name and (ROOT / name).is_file()}
    return dict(branch=git("branch", "--show-current"), commit=git("rev-parse", "HEAD"),
                git_tree=git("rev-parse", "HEAD^{tree}"), production_files=len(current),
                production_sha256=digest(current), production_file_hashes=current,
                tracked_worktree_sha256=digest(tracked_hashes))


def packet_files():
    paths = [p for p in OUT.rglob("*") if p.is_file() and p.name != "freeze-manifest.json"]
    paths += [ROOT / "tests" / name for name in
              ("day28_prepared.py", "manual_day28.py", "day28_freeze.py", "test_day28_preparation.py")]
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    path = OUT / "freeze-manifest.json"
    if args.verify:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest["files_sha256"] != packet_files() or manifest["product"] != product():
            raise ValueError("Packet/product changed; approval no longer matches")
        inputs = json.loads((OUT / "prepared-inputs.json").read_text(encoding="utf-8"))["files_sha256"]
        if any(sha(ROOT / name) != value for name, value in inputs.items()):
            raise ValueError("Prepared private input changed")
        print("VERIFIED prep packet; human approval still required; no data collected")
    else:
        if path.exists():
            raise ValueError("Existing freeze must not be silently overwritten")
        files = packet_files()
        manifest = dict(status="PREP_ONLY_REVIEW_PENDING", human_approved=False, human_participants=0,
                        created_utc=datetime.now(timezone.utc).isoformat(), product=product(),
                        questions_sha256=sha(OUT / "FROZEN_TASKS.md"),
                        scoring_sha256=sha(OUT / "FROZEN_SCORING.md"),
                        assignments_sha256=sha(OUT / "TASK_ORDER_ASSIGNMENTS.json"), files_sha256=files)
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print("SEALED", len(files), "prep artifacts; approval pending")
    print("manifest_sha256", sha(path))


if __name__ == "__main__":
    main()
