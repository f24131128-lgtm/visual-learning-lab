# POST_FIX — human-approved Day27 acceptance completion

Recorded UTC: 2026-10-11T02:54:09.721594+00:00.

**Day27 acceptance gate is met. Work stopped after the authorized final full regression passed.** No functional code, test source, dependency, planner ranking, or representation family changed in this completion. No new model calls, commit, push, or Day28 work occurred.

Human-approved POST_FIX A-axis: **PASS 5 / PARTIAL 5 / FAIL 0**, denominator 10. Frozen baseline remains **PASS 4 / PARTIAL 4 / FAIL 2**. Five cases received explicit live POST_FIX human review; the other five retain their baseline assignments under the approved aggregate. This is not an untouched holdout.

[Human decisions and reasons](human-approved-a-axis.md) · [Machine-readable decisions](human-approved-a-axis.json) · [Acceptance checklist and integrity verification](human-approved-validation.json).

| Check | Result |
|---|---|
| Current focused confirmation | 105/105; failures 0; errors 0; skips 0; 35.454s |
| Final full regression, this authorization | 489/489; failures 0; errors 0; skips 0; 242.890s |
| Final complete runs in this authorization | Exactly one |
| Prior full regression | Historical 480/489, 6 failures and 3 errors, retained unchanged |
| Frozen baseline integrity | 35 public and 212 private files verified |
| Historical POST_FIX integrity | 45 public and 99 private files verified |
| Production / test sources | 78 / 101 files unchanged from this completion's preflight |
| New model requests / functional changes / new dependencies | 0 / 0 / 0 |

Exact final command: **python -X utf8 -B -m unittest discover -s tests -q**.

The shell resolved python to the existing Python 3.14 installation. The [final result](final-regression-human-approved.json) records unittest duration (242.890s) separately from launcher wall time (250.302s). [Full log](final-regression-human-approved.log); exact failure/error cases: none. [Focused result](focused_runs/11.json) and [focused log](focused_runs/11.log).

The initial sandbox focused launcher stalled at Windows asyncio's local socketpair accept. It was stopped without a unittest summary; its parsed zero is not a known number of completed tests. Its [attempt result](focused-human-approved.json) and [log](focused-human-approved.log) remain separate. One completed confirmation of the same 105 focused tests then passed locally without source edits. The final full suite was launched only once and was not retried.

Probability and RC remain human-approved PARTIALs. Signals retains human-approved semantic PASS with recorded interactive capability loss. Regression uses an approved static/formal fallback after Lab rejection. Candidate C remains unresolved and unimplemented. No further hardening followed the green full suite.

Git branch: day17-learning-scene-wip. HEAD: 477de4926220d0960b58500f292ea6df24154da6. The worktree remains dirty: 46 tracked modified entries and 25 untracked entries in git status --short, including existing Day27 work. [Exact git status](human-approved-git-status.txt). No commit or push.

Historical manifests, scorecards, review packet and evidence/checkpoint bytes remain preserved. All new scores and completion evidence reside under docs/day27/post_fix/. The supplemental hash manifest links the existing frozen manifests and hashes new evidence without replacing originals.

No new dependency. App command: python -m streamlit run app.py.
