# Day 23 checkpoint

Phase: explicitly paused by user on 2026-10-06 due to remaining usage. Core A/B,
source-semantic review, focused/full regressions and three browser case inspections
are complete. Final evidence consistency check, checkpoint consolidation, screenshot
handoff and concise final delivery remain. Stop work until user resumes.

Latest authoritative state (the earlier recovery narrative below is historical):
- Frozen manifest/gold unchanged; hash below. Gold remains agent-authored before
  execution, independent human approval pending.
- Audited A: acceptable proposals8, wrong1, unavailable3; artifacts5; local passes4.
- Audited B: acceptable proposals12; primary artifacts11; mechanical local passes11;
  source-semantic useful outcomes10, misleading recursion1, unavailable finite sets1.
- Failures: required finite probability duplicate focus labels C1; optional damped
  spatial fixed constants declared as zero-span parameters C1 (numeric Lab survives);
  recursive specific call/result claims unsupported by generic list operations R3.
  Legacy RC probability CTA false positive remains.
- Paid attempts35, input81,366/output49,549/total130,915 tokens. Replays/audits/tests/
  browser recording review add zero paid calls. No further calls after pause.
- Final focused29 passed14.893s; ONE full regression368 passed215.514s.
  Logs: docs/day23-final-focused-repaired.log and docs/day23-regression.log.
- Production changes: source_atlas/model.py; new learning_world/capabilities.py;
  learning_world/compiler.py, planner.py, schema.py, diagnostics.py, runtime.py;
  i18n.py. No new dependency, no commit/push/reset, pre-existing dirty work preserved.
- New tooling: tests/day23_freeze.py, day23_benchmark.py, day23_review.py,
  day23_report.py, test_day23.py, manual_day23.py. Report command completed; comparison
  JSON/Markdown, semantic review and gold packet written without changing recordings.
- docs/DAY23_EVIDENCE.md has been written. Next action is check it for precise browser
  evidence/score wording and consolidate this historical checkpoint, then git diff
  --check/status and final report. No need for another paid run or full suite.
- Browser8526 uses recorded real B outputs in the actual app: RC R2→R4 changes
  τ2→4s/I0 2.5→1.25A, source→explore preservesR4; Future start/completion/terminal/
  reset/cancel/source→explore confirmed; Bytes concept node inspector/source claim,
  zero sliders/process controls confirmed. Bytes Source navigation was clicked but
  final source→explore preservation observation still pending; do not claim that
  final roundtrip as independently completed.
- Saved docs/day23/rc-browser.jpg, future-browser.jpg (running), byte-browser.jpg.
  Narrow default browser viewport; do not resize purely for prettier screenshots.
- Own recorded review server PID38744 port8526 remains; existing prod8521 untouched.
  Browser tab1 URL http://localhost:8526/; task automation stopped on user pause.

Exact continuation: read this checkpoint + DAY23_EVIDENCE.md; finish only final
verification/docs/delivery unless user explicitly authorizes more experiments.
App command: python -B -m streamlit run app.py.
Zero-cost recorded review: python -B -m streamlit run tests/manual_day23.py --server.port 8526.
Interpreter if PATH unavailable: C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe.

---

Historical initial checkpoint (superseded by the state above):

Base branch `day17-learning-scene-wip`, HEAD
`b6b39c5b1888d1094b3e3a446751ce02644d3114` contains Day21/22. Existing dirty
tracked bytecode and untracked Day21/22 logs are preserved. No commit/push/reset.

Frozen manifest: `docs/day23/phase_a_manifest.json`, SHA-256
`0bee312246242b6e2f76446ab8dc900f56c6d72bec6cecc4743832986559027f`.
12 previously unused materials: dynamics, parameterized spatial/function
relationships, circuits, finite sets, discrete collection/lifecycle/recursion,
feedback, comparative economics, biological stages, and a short definition.
Gold is agent-authored before execution and **human review pending**. Three
public Python-documentation paraphrases; nine independently authored teaching
excerpts. Retrieved OpenStax restrictions rule out ingesting its prose/assets.
This is not a real-PDF or independently human-labeled corpus.

Pre-change focused baseline: 35 Day22 tests passed in 27.128s, log
`docs/day23-baseline-unsandboxed.log`. Sandbox run was interrupted because of
the known Windows asyncio socketpair restriction. No production edits yet.

New files so far: corpus/manifest, `tests/day23_freeze.py`,
`tests/day23_benchmark.py`, and Day23 logs/checkpoint. No dependencies added.

The runner saves every raw declaration before validation, persists per-case
results, measures proposal/selection/compilation/local runtime/reference
integrity separately, guards local interactions against requests, and never
puts gold into model input. SDK retries disabled; each phase has a request cap.

Exact continuation (use installed full Python path if `python` is unavailable):

```powershell
python -X utf8 -B tests/day23_benchmark.py --phase a --live --max-calls 36
```

Resume uses saved stages and completed rows without repeating paid calls.
Do not alter production until all Phase A results are persisted and interpreted.
Do not overwrite manifest, materials or labels. After Phase A, record recurring
failures before targeted prior-art study/changes; then replay and fresh Phase B,
focused regressions and one final full suite.
