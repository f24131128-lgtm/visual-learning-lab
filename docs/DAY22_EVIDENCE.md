# Day 22 — Representation Suitability Benchmark and compiler evidence

**Live Queue update:** the exact user-provided Queue input passed the real
`app.py:8521` input→analysis→planner→interactive process path, including enqueue,
dequeue, front/rear, canonical focus, source round trip and reset. Repair focused
tests: 35 passed; one full post-repair suite: 339 passed. Two explicit paid
requests (analysis + plan); subsequent interactions were local. Screenshots,
diagnostics, changes and the unrecoverable original failure limitation are in
[live repair record](DAY22_LIVE_QUEUE_FIX.md). The original offline evidence
below is historical; its pending live Queue status is superseded. Other live
material acceptance remains separate.

## Problem and decision

Different semantic structures need different learning experiences. Add a small
capability-aware semantic plan and a generic bounded discrete reducer, rather
than rewriting existing worlds or building a large ontology. A single explicit
plan request can include process state/transitions; no second process request.
Existing validated phase/spatial/probability/analogy engines remain unchanged.
Unknown capability falls back to static/explanation; false interaction value
cannot force animation. Planning is explicit because it is semantic generation.
On successful planning, the recommended mode is selected automatically.

Recovered Day21 before editing: dirty Workspace and Analogy World, modified
app/i18n/canvas/lab/scene/Atlas modules and tests, untracked evidence and fixtures.
Preserved all of them, including previously dirty tracked bytecode. The final
Day21 live-fix record contains human confirmation of successful Ohm hero rerun;
earlier pending claims are superseded. Day20 parsing/geometry/fallback contracts
and Day21 conditional rendering/focus contracts were inspected. No commit/push.

## Prior art / licenses

Ten focused comparisons and exact license links are in
[reuse ledger](OPEN_SOURCE_REUSE_LEDGER.md#day-22--focused-representationruntime-comparison-2026-10-05).
LEARN: XState pure guards/actions and transitions FSM contracts (MIT), Penrose
declarative decomposition (MIT). REUSE existing Streamlit Apache-2.0, Graphviz
Python MIT, XYFlow MIT core through existing streamlit-flow wrapper, and Plotly
MIT core. DEFER SimPy MIT, JSXGraph MIT option, Cytoscape MIT core, Mermaid MIT;
IGNORE bpmn-js for this sprint (custom watermark terms, not plain MIT).
No upstream code/assets/weights copied or new dependency installed. Library
choices do not grant model/example/Pro asset licenses. PyMuPDF AGPL/commercial
deployment review remains unresolved; prior notices remain intact.

Not built: RAG, parser migration, source viewport rewrite, separate physics
engines, queue application, generic quiz engine, hierarchical/parallel FSM,
giant renderer registry, ontology, homepage or top-level page redesign, stretch.

## Trust, state and requests

Model supplies boolean semantic characteristics, teaching intent, references and
bounded declarations. Trusted code intersects them with existing capabilities;
labels/source words are never planner routing inputs. Five fixed operations:
append, prepend, remove-first, remove-last, finite-state change. Capacity/empty
guards, legal states, coordinates/layout, revision identity, history and rendering
are trusted local mechanics. No model program/expression runs in this reducer.

Strict schema rejects unknown envelope/core fields, invalid IDs/pages/references,
unsupported operations, excessive objects/transitions/items/text/payload and
broken core transitions. Optional annotations drop independently. Process bounds:
3 collections, 3 variables, 12 transitions, 16 items per collection, 12 legal
values per variable, 32 history entries, 48KB declaration, 4 plans/states/errors.
Generated item labels are teaching examples, not literal PDF evidence.

Source links attach to existing formal catalog IDs. Process actions commit
through set_workspace_focus; Source/practice links reuse the same IDs/lesson
refs. No process-specific semantic focus or duplicate formal parameter state.
Atlas/native previews and source rasters remain separate existing subsystems.
Material changes reset only new plan/process state. Parameters, process history,
reset and navigation never enter compiler cache keys. The requested formal focus
distinguishes explicit targeted plans, like existing analogy generation; ordinary
focus changes retain the active compiled process and never request/invalidate it.
Stored analysis language is used; UI language switching does not request a plan.

One strict Responses request per explicit uncached plan; SDK retries disabled.
Unsuitable decisions cached; failures retain accepted plans and learning state,
with bounded controlled error codes and explicit retry. No automatic requests.
Specialized generation still uses existing explicit build actions when no world
exists: the planner does not claim to compile spatial/analogy specs in that same
request. At most one *plan/process* request is not a one-call guarantee for every
unbuilt specialized representation. Already built worlds are reused locally.

Explore renders only the chosen activity. Compare appears only with a valid
material-specific analogy. Unbuilt analogy is an explicit generation activity,
not a fake visual. Static/none suppress interactive builders/lab/simulation;
none shows the existing explanation. Graphviz failure leaves ordered text,
endpoint labels and controls. Existing formal/analogy/Graphviz features remain.

## Deterministic benchmark

[Machine-readable results](day22-representation-benchmark.json), generated by
`python -X utf8 -B tests/day22_benchmark.py`. Six synthetic deterministic
declarations, not a live model benchmark or ground-truth accuracy measurement.
Each plan is accepted through the real compiler with a mocked strict response;
the existing specialized validators/reducers execute actual local changes.

| Case | Expected / selected family | Runtime and observed check |
|---|---|---|
| Sinusoid / phase | dynamic | Existing world DAG: phase π/2 gives wave=1, horizontal=0 |
| FIFO | process | Same ordered reducer: A,B + C, remove A, leaves B,C; focus=remove |
| Ohm | analogy | Existing V/R bindings: V=10,R=5 gives formal current=analogy flow=2 |
| Projectile | spatial | Existing time patch changes validated trajectory projection |
| Probability | structural | Existing exact P(E)=1/2, inclusion–exclusion and seeded sampling |
| Definition | none | No forced interaction, canonical formal focus retained |

Every row has valid synthetic formal page links/shared focus and zero postcompile
mock call delta. Live source fidelity is not established. LIFO and a three-state
workflow additionally use the identical process reducer in focused tests.

## Tests / audit

24 initial Day22 tests passed in 12.464s (`day22-focused-final.log`). Expanded
focused regression: **211 passed in 99.767s** (`day22-focused-regression.log`),
including 27 Day22 cases plus analogy/workspace/Day17/18 regression and existing
fixed-code frontend smokes. Normal text/PDF app paths, explicit one-request build,
source/practice round trips, none suppression and renderer fallback pass.
**Single full regression: 331 passed in 188.779s**, `day22-regression.log`.
No second full invocation. Final benchmark regeneration succeeded; `git diff
--check` passes with pre-existing CRLF conversion notices. No known failure from
the final executed tests. Commands:

```powershell
python -X utf8 -B -m unittest discover -s tests -p test_day22.py -v
python -X utf8 -B -c "import unittest; loader=unittest.TestLoader(); suite=unittest.TestSuite(loader.discover('tests',pattern=p) for p in ['test_day22.py','test_analogy*.py','test_day21.py','test_day17.py','test_day18*.py']); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())"
python -X utf8 -B -m unittest discover -s tests -q
python -X utf8 -B tests/day22_benchmark.py
```

Sandbox AppTest initially stalled in Windows asyncio socketpair; faulthandler
proved the location before app execution. Tests run outside sandbox with all API
calls mocked. No paid requests. Existing Streamlit deprecation warnings remain.

Day22 core audit: `rg -n -i 'queue|ohm|projectile|sinusoid|probability' learning_world`
finds only `probability_sets`, an existing capability/domain enum. An AST test
rejects topic-name literal branches and eval/exec/compile/import execution;
renaming every catalog label to misleading topic names leaves all six routes
unchanged. Legacy scene/compiler.py still has lexical CTA suitability terms,
including projectile/probability, before scene compilation. This sprint does not
claim to have removed that older prefilter or proven source semantic fidelity.

## Files changed this sprint

- New production: learning_world/__init__.py, schema.py, planner.py, compiler.py,
  process.py, runtime.py.
- Existing integration additions: app.py, i18n.py, workspace/state.py, workspace/ui.py.
  Their Day21 changes were retained. No scene/analogy/parser/frontend rewrite.
- Test/demo files: tests/day22_fixtures.py, test_day22.py, day22_benchmark.py,
  manual_day22.py, fixtures/day22_fifo.txt, fixtures/day22_static.txt.
- Documentation: OPEN_SOURCE_REUSE_LEDGER.md, DAY22_EVIDENCE.md,
  DAY22_CHECKPOINT.md, day22-representation-benchmark.json and Day22 logs.
  Diagnostic logs distinguish sandbox attempts from final passing evidence.
- requirements.txt and THIRD_PARTY_NOTICES.md unchanged; no new dependency or
  copied code/assets requiring an added notice.

## Manual demos and screenshots

Production: `python -m streamlit run app.py --server.port 8521`.
This host's Windows Python alias is inaccessible; use:

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B -m streamlit run app.py --server.port 8521
```

Offline fixtures use the same production app, no model calls:

1. **A phase:** `python -B -m streamlit run tests/manual_analogy.py --server.port 8523`.
   Select phase; Formal shows existing pointer/projection/waveform. Change phase
   to π/2: pointer turns, waveform/projection update together. Switch Analogy and
   source then back; values/focus remain. Capture linked pointer and wave.
2. **B FIFO:** `python -B -m streamlit run tests/manual_day22.py --server.port 8524`.
   FIFO initially A→B, Front=A/Rear=B. Enter C, press Insert; Remove returns A,
   leaves B→C and focuses remove. Source→Practice→Explore preserves state.
   Reset restores A→B. LIFO removes C and workflow steps idle→working→done using
   identical reducer. Capture before/after ordered items and canonical focus.
3. **C Ohm:** same 8523 demo, select electricity. V=10/R=5 gives 2 in formal and
   analogy flow; switch Compare/Source/Formal and retain focus/values. Capture
   correspondence, limits and synchronized current/flow. For real live regression,
   reuse the human's Day21 Ohm PDF/session, without rebuilding an accepted world.
4. **D continuity:** `python -B -m streamlit run tests/manual_day21.py --server.port 8522`.
   Source page2 Gravity g→Explore; change time/parameter→Source. Same source
   anchor/semantic focus/numeric state, no recompile. Capture Source and Explore.

**New production generation:** paste tests/fixtures/day22_fifo.txt, Analyze once,
Explore→Choose a learning representation once. Expect Interactive process, rear
insert/front remove, local input/reset/history. Check Source/practice links.
Paste day22_static.txt as new material: Analyze, then choose a representation;
expect no forced interactive world. For real phase/projectile/probability, reuse
existing materials/scenes and explicitly request a plan. Existing world should
be reused; Ohm should offer analogy. These explicit production generations incur
normal API costs and require human source-fidelity inspection, not paid test loops.

Screenshots remain human live acceptance evidence; no screenshots or real-model
success claimed from AppTest alone. Exact observed source/representation pairs
should be captured; an explanation/plan alone is not a rendered-world proof.

## Limits and next evidence-driven step

This is representation selection across six declared structures, not arbitrary
knowledge compilation. Planning requires existing canonical scene/graph IDs;
when analysis has no such catalog, the planning CTA is disabled and the existing
explanation remains available. No new entity identity is invented from a label.
No continuous timing, interacting scheduled resources,
parallel/hierarchical states, general flow conservation or grammar for model
code. Transition/source correctness still needs real materials and human review.
Plan selection estimates pedagogy; no learning-efficacy claim. Probability scene
may still display its compiled Monte Carlo view; structure is not spatial physics.

Day23: run a small real-material plan→build→interaction acceptance corpus with
saved sanitized declarations and human suitability judgments. Measure wrong
selection versus invalid compilation separately. Remove the legacy lexical CTA
gate through evidence-backed structured capability hints before expanding the
process vocabulary or installing an FSM/scheduler. No automatic paid benchmarks.
