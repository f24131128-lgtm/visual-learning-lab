# Day 22 checkpoint — implementation and offline regression complete

Latest checkpoint: **exact real Queue HERO PASS** in normal `app.py:8521`.
Initial A→B, enqueue C→A→B→C, dequeue→B→C, front=B/rear=C, shared focus,
Source/Explore preservation and reset A→B were observed in the real browser.
35 focused and 339 full post-repair tests passed. Two paid requests were used
for one fresh normal analysis and one planner; no paid retry loop. Generic ID
namespace repair, private retained-candidate revalidation and controlled debug
traces were added; no dependency, commit or push. Original rejected output was
discarded by old code, so its exact root cause remains unproven. See
[live repair evidence](DAY22_LIVE_QUEUE_FIX.md). The older pending/live-cost
statements below describe the pre-repair checkpoint and are superseded for this
Queue case only.

2026-10-05. No optional stretch started. Do not commit or push.

Architecture: `learning_world/schema.py` defines one strict semantic plan plus
optional generic discrete declaration; `planner.py` validates formal IDs/pages
and selects only structurally eligible capabilities; `compiler.py` makes one
explicit Responses call and bounds material/language/semantic/source caches;
`process.py` interprets five fixed list/finite-state operations with atomic guards,
identity/revision checks and bounded history; `runtime.py` adapts Explore and the
canonical Workspace focus. Existing scene/probability/analogy/lab engines remain
authoritative. Static/none suppress hidden interactive builders/runtimes.

Prior state recovered: all Day21 dirty app/i18n/canvas/lab/scene/source changes,
untracked analogy/workspace/tests/docs and tracked dirty bytecode preserved.
Day21 checkpoint's final human Ohm hero acceptance supersedes earlier pending
claims. No resets, copied upstream code, dependencies or engineering paid calls.

Changed this sprint: new learning_world package; small additions in app.py,
i18n.py, workspace/state.py/ui.py; tests/day22_fixtures.py, test_day22.py,
day22_benchmark.py, manual_day22.py; two text fixtures; reuse ledger, evidence,
checkpoint and Day22 result logs/benchmark JSON. Pre-existing dirty files remain.

Completed deterministic acceptance: phase→existing dynamic DAG; FIFO→generic
process; Ohm→existing analogy V/R; projectile→existing spatial reducer;
finite probability→existing exact/set/sampling engine; definition→none.
Additional same-reducer LIFO and finite-state transitions pass pure tests.
Benchmark artifact: docs/day22-representation-benchmark.json; six synthetic cases,
not real-model accuracy. All observed postcompile model-call deltas are zero.

Tests so far: 24 initial Day22 tests passed, 12.464s (`day22-focused-final.log`).
Expanded 27-case Day22 plus analogy/workspace/Day17/18 focused regression:
**211 passed in 99.767s** (`day22-focused-regression.log`). Includes normal PDF,
none suppression and Graphviz failure AppTests plus fixed frontend smokes.
Windows sandbox blocked asyncio socketpair before app execution; faulthandler
located it (`day22-app-diagnostic.log`); offline AppTest runs outside sandbox.
Interrupted the three blocked diagnostic/test processes; no app service killed.

Exact commands (portable; on this host use the full Python path in evidence):

```powershell
python -X utf8 -B -m unittest discover -s tests -p test_day22.py -v
python -X utf8 -B tests/day22_benchmark.py
python -X utf8 -B -m unittest discover -s tests -q
python -B -m streamlit run tests/manual_day22.py --server.port 8524
python -m streamlit run app.py --server.port 8521
```

Full regression ran ONCE: **331 passed in 188.779s**, `day22-regression.log`.
All focused and full regression failures resolved; none observed in the completed
final runs. `git diff --check` passes (existing CRLF conversion warnings only).
Benchmark regenerated successfully after compiler supplied-ID enforcement.

Unfinished code work: none for this bounded sprint. Manual Day22 live
model/real-source/browser acceptance remains. No known production failure from
the executed tests. Next concrete step: follow DAY22_EVIDENCE.md's four manual
demos and production FIFO/static plan steps; capture true source/world pairs.
Do not spend another paid request on a valid already-built world.

Final focused command reproducing 211 cases:

```powershell
python -X utf8 -B -c "import unittest; loader=unittest.TestLoader(); suite=unittest.TestSuite(loader.discover('tests',pattern=p) for p in ['test_day22.py','test_analogy*.py','test_day21.py','test_day17.py','test_day18*.py']); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())"
```

Limits: planning requires an existing canonical scene/graph catalog; without it
the app retains explanation and disables the CTA. Bounded ordered collections
and finite-state variables, not arbitrary
statecharts/timed flows; source fidelity remains estimated; declaration benchmark
does not assess unseen model output. Legacy lexical scene CTA eligibility remains
in scene/compiler.py and is documented separately. No stretch work planned.
