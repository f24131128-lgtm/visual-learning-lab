# Day 23 — prospective representation generality evidence

Completed 2026-10-06 Asia/Taipei. No commit, push, reset, dependency addition or homepage redesign.

## Question and recovery

For previously unused educational materials, does the system select appropriate
representations, safely compile them, and support source-meaningful local interaction?
This is a small cross-domain prospective material benchmark, not universal accuracy.

Recovery: branch `day17-learning-scene-wip`, HEAD
`b6b39c5b1888d1094b3e3a446751ce02644d3114`, Day21/22 already committed.
Pre-existing dirty tracked bytecode and untracked older logs/caches were preserved.
Read the specified Day20–22 evidence and relevant compiler/scene/analogy/workspace/
Atlas/document-adapter/app abstractions. Pre-change Day22 focused baseline:
**35 passed, 27.128 s** ([log](day23-baseline-unsandboxed.log)). Windows sandbox
socket restrictions required outside-sandbox Streamlit test execution. Interrupted
sandbox runs are retained and not scored as product failures.

## Frozen corpus, provenance and gold

[Manifest](day23/phase_a_manifest.json) frozen before execution/production changes at
`2026-10-05T16:07:06.015331+00:00`; SHA-256:
`0bee312246242b6e2f76446ab8dc900f56c6d72bec6cecc4743832986559027f`.
The runner verifies the canonical payload and each material text hash. Versions:
planner 1.0, spatial 2.2, probability 1.1. No material or gold label changed.

Twelve unused excerpts cover decay dynamics, vector components, RC charging,
quadratic functions, finite sets/sampling, undo history, Future lifecycle,
recursive calls, feedback response, supply/demand, biological stages and a definition
with little benefit from simulation. Semantic traits and acceptable-family sets
precede model results. [Gold review packet](day23/GOLD_REVIEW_PACKET.md):
**agent-authored before execution; independent human approval pending**.

Three excerpts independently paraphrase factual behavior from public Python
[deque docs](https://docs.python.org/3/library/collections.html#collections.deque),
[Future docs](https://docs.python.org/3/library/concurrent.futures.html#future-objects),
and [bytes docs](https://docs.python.org/3/library/stdtypes.html#bytes-objects).
URLs/retrieval dates/status are stored; [documentation license](https://docs.python.org/3/license.html)
was inspected. Nine are independently authored realistic teaching problems,
substituted before evaluation when retrieval/license suitability was unreliable.
[OpenStax restrictions](https://openstax.org/books/university-physics-volume-1/pages/15-5-damped-oscillations)
excluded its prose/assets. No substantial protected excerpts, upstream code or
weights were copied. This is **not a retrieved real-PDF corpus**.

## Execution and scoring

Runner uses the production main-analysis prompt/schema/cleaning functions, planner
compiler and local evaluators/reducers. Gold never enters model input. Raw declarations
are saved before validation. Paid retries are disabled; saved stages resume without
repeating calls; attempts are capped. Source fidelity differs from ID/page validity.

A ran unchanged Day22. Results and [failure interpretation](day23/PHASE_A_INTERPRETATION.md)
were persisted before changes. B used the exact frozen sources and reused A's main
analyses, with fresh downstream planner and artifact requests. This isolates downstream
hardening, **not a second fresh main-analysis generation**. Planner instructions and
capability context changed; corpus/gold/main prompt did not. Fingerprints/timestamps
are in results. No production edit followed the fresh B recording.

Two harness measurement errors were corrected by zero-call audits, with originals
preserved: A supplied an empty material wrapper to focus navigation; B treated an
optional spatial build as required for an available numeric Lab. See
[errata](day23/HARNESS_ERRATA.md). Original live records remain authoritative for
paid usage. Audited A/B are the comparison below.

| Measure, 12 frozen cases | A pass / fail / unmeasured | B pass / fail / unmeasured |
|---|---:|---:|
| Model proposal acceptable | 8 / 1 / 3 | 12 / 0 / 0 |
| Effective selected family acceptable | 4 / 1 / 7 | 12 / 0 / 0 |
| Valid selected artifact | 5 / 4 / 3 | 11 / 1 / 0 |
| Mechanical local behavior | 4 / 1 / 7 | 11 / 0 / 1 |
| Canonical plan/reference/page integrity | 5 / 0 / 7 | 12 / 0 / 0 |
| Failed cases retaining normal analysis | 8 / 0 / 4 N/A | 1 / 0 / 11 N/A |
| Post-compile model calls | 0 across 5 observed artifacts | 0 across 11 observed artifacts |

A: **4/8 acceptable proposals** compiled; all four acceptable artifacts passed
applicable local checks. The fifth valid artifact was an inappropriate static vector
view. Three cases never reached planning due to an empty catalog; seven absent
effective selections are not seven wrong choices. B: **11/12 acceptable proposals**
compiled. Plan references12 includes the rejected finite-set artifact; surviving
artifact references cover11. These counts are not human fidelity scores.

## Per-case changes and taxonomy

| Case | A | B including source-semantic review |
|---|---|---|
| damped_motion | P3 missing Comparison catalog | Dynamic Lab valid; optional spatial C1 zero-span parameters |
| vector_resultant | P1 essential interaction made static | Dynamic Lab valid, component/magnitude control; richer vector scene untested |
| rc_charging | C1, underlying C4 unused process fatal | Dynamic Lab valid, source equations checked |
| quadratic_shape | P3 missing Comparison catalog | Dynamic Lab valid, source function checked |
| finite_sampling | C1, underlying C4 annotation-only process fatal | Structural plan valid, required scene C1 duplicate focus labels |
| undo_history | Process valid | Process valid, append/last removal/reset checked |
| future_lifecycle | C1/C3 invalid state/target declarations | Process valid, allowed/forbidden transitions checked |
| recursive_calls | C1/C3 invalid process | Mechanical valid, **R3 misleading call/return claims** |
| feedback_response | Dynamic valid | Dynamic valid, source equation checked |
| market_equilibrium | P3 missing Comparison catalog | Dynamic valid, curves/equilibrium metrics checked |
| cell_cycle | Safe static accepted by frozen gold | Process valid, cyclic order checked |
| byte_definition | Acceptable static | Acceptable static, no forced simulation |

[Comparison JSON](day23/comparison.json), [table](day23/comparison.md),
[A audit](day23/phase_a-audit/results.json), [B audit](day23/phase_b-audit/results.json).
Original primary categories P1/P3/C1 remain; C4/C3 explain recurring boundary causes
without rewriting A. Adversarial tests check safe rejection; no fabricated G1/G2
failure is inferred from absent human review.

Top A patterns: missing catalog identities3; process coupling4 (two irrelevant
payloads, two genuinely invalid required declarations); numeric parameter exploration
confused with time animation1. These drove fixes, not topic-specific examples.

## Prior art and three architecture fixes

After A, examined four relevant alternatives and exact core licenses. **REUSE
existing Plotly** for numeric curves; **LEARN FROM/DEFER JSXGraph** for interactive
parameter geometry; **LEARN FROM XState** for state/context/guard contracts;
**LEARN FROM/DEFER Cytoscape.js** for stable element identity. Extra offline bundles,
gesture/state adapters and maintenance do not fix missing IDs or malformed semantics.
Repository/docs/release evidence checked; no independent deployment/latency trial
claimed. Links, path/package licenses, costs and decisions:
[reuse ledger](OPEN_SOURCE_REUSE_LEDGER.md). No package/code/assets/weights imported;
requirements/notices unchanged. Existing PyMuPDF AGPL/commercial review remains.

1. `source_atlas/model.py`: include existing Comparison IDs with only their cell
   pages. Only with no structured identities, derive bounded deterministic IDs for
   already analyzed concepts. Preserve graph/scene IDs; no array-position identity
   or invented pages.
2. `learning_world/capabilities.py`, compiler/planner: small explicit contracts
   distinguish ready Lab from explicit-build candidates. Numeric equation/parameter
   exploration need not have time dynamics. Upgrade a static proposal when declared
   useful numeric manipulation has a ready Lab. Process excludes arbitrary arithmetic,
   automatic recursion and scheduling. Revision `day23.1` enters plan cache identity.
3. Planner/schema: discard bounded inert unused process data for non-process plans
   while enforcing envelope/type/count/plain-text/operation security. Required process
   still uses the original strict validator. Clarify one variable/all literal states,
   from/to targets and empty unused arrays. Diagnostics record requested/selected
   family, recovery and degradation; localized UI distinguishes upgrade from fallback.

Existing safe_math, validators, reducers, source whitelist and rendering/state ownership
remain unchanged. Model produces declarations only. No new renderer/plugin framework.
Fallback remains existing formal/static/normal learning, with no unrelated analogy.
Required process failures are isolated rather than guessed into executable semantics.

[Original-response replay audit](day23/phase_b-replay-audit/results.json) independently
shows deterministic RC/vector recovery; original malformed Future/recursion remain
rejected. Fresh prompts produce different valid process data. Three formerly disabled
planners have no saved declarations and are unmeasured. Improvement therefore combines
deterministic boundary fixes and prompt/model variability, not a causal claim per row.

## Useful outcomes and unresolved bottlenecks

[Semantic review](day23/semantic_review.json) compares six numeric materials against
independently written NumPy source equations at defaults and every parameter endpoint;
market equilibrium metrics are checked too. Three process sources are checked for
legal operations; byte remains honest static. Result: **10/12 useful outcomes in this
benchmark**, independent human fidelity/pedagogical review pending.

Recursion is R3: a button requesting a specific call appends arbitrary learner text;
returning `f(3)=6` is enabled before a base case/unwinding. The saved counterexample
and tests reject mechanical operation as evidence of useful recursion teaching.
Required finite probability scene rejects duplicate focus labels. Optional damped
spatial scene rejects fixed constants declared as equal min/max parameters; its
valid Lab survives. At beta0 the time-constant metric is safely unavailable while
curves remain defined. Generated slider ranges/pedagogy need human review.
Browser RC also shows an unrelated legacy probability-build CTA. It was not clicked
and is a suitability/UX issue, not evidence of successful probability support.

## Tests and topic-name audit

Baseline35 passed; tooling11 passed. Systemic plus Day22 **56 passed, 23.177 s**
([log](day23-focused-initial.log)); integration25 passed,13.645s; final Day23
**29 passed,14.893s** ([log](day23-final-focused-repaired.log)). Intermediate new-test
placement/stale AppTest selector errors were repaired; original failed log retained.
No validator was loosened. **One final full suite: 368 passed,215.514s**
([log](day23-regression.log)).

Coverage: capability/fallback/cache revision, reordered stable identity, comparison
provenance, concept fallback, malicious/malformed bounds, unused-field isolation,
strict required-process rejection, stored language, explicit request counts, local
state preservation, synthetic normal-PDF page whitelist, recorded3-case AppTest,
source equations/operations/counterexamples. Ordinary tests make no paid request.
Browser SVG gestures and real-document grounding remain separate evidence.

Audit: `rg -n 'queue|ohm|projectile|phase|probability|recursion|supply|mitosis|feedback'
learning_world scene/compiler.py workspace source_atlas/model.py`.
No new source/topic predicate drives routing. `automatic_recursion` advertises a
limitation; `phase` in prompt describes state; Atlas queue is traversal, and declared
`probability_sets` is a domain. **Legacy exceptions** remain in `scene/compiler.py`:
probability keyword/structural signals and temporal/spatial/quantitative candidate
terms including projectile/phasor. These offer old CTAs and are not generality proof;
the RC false-positive demonstrates the limitation. AST tests reject topic routing
in the modified planner/capability layer.

## Paid API behavior

| Run | Attempts | Input | Output | Total tokens |
|---|---:|---:|---:|---:|
| A:12 analysis+9 planner | 21 | 54,747 | 36,588 | 91,335 |
| B:12 planner+2 scenes | 14 | 26,619 | 12,961 | 39,580 |
| Total | **35** | **81,366** | **49,549** | **130,915** |

Production model `gpt-5.6-luna`. Reused analyses not billed twice. Two B scene attempts
include the unnecessary optional spatial request; it remains counted. Audits/reports/
unit tests/browser replay add zero paid calls. Billing not queried or estimated.
Local probes guard requests; browser harness blocks Responses.create. Sliders,
process transitions/reset, focus and view navigation are local. Explicit Explain This
or new compiler CTA is separately paid and outside this interaction contract.

## Exact three-case human live review

Production command: `python -B -m streamlit run app.py`.
Select English before analysis, paste the entire linked frozen text, click **Visualize**,
then **Explore → Choose a learning representation**. One main analysis plus planner
request is expected; the following local actions must make no further request.
Fresh model output is stochastic: record it separately, never overwrite A/B.

For zero-cost reproduction of actual B output:
`python -B -m streamlit run tests/manual_day23.py --server.port 8526`;
open [recorded review](http://localhost:8526) and use sidebar case selector.
Analysis/plans are already loaded; do not click Visualize/build buttons. Harness runs
the normal app/runtime with actual recordings. Browser automation completed these
checks; independent human judgment remains pending.

| Paste material / representation | Actions and expected behavior | Grounding/failure checks |
|---|---|---|
| [RC](day23/materials/rc_charging.txt), dynamic Lab under Formal model | Interactive Lab default R2:τ2s,I0=2.5A. Set R4:τ4s,I0=1.25A, slower voltage rise; Compare with default stays visible. Source→Explore preserves R4. Reset parameters restores R2. Zero extra calls. | Source has C1,Vs5 and original equations; no fake page. Failure: unchanged curve/metric, lost state, invented page/request. Do not build unrelated optional probability scene. |
| [Future](day23/materials/future_lifecycle.txt), Interactive process | pending:Start/Cancel enabled, completion disabled. Start→running:Cancel disabled. Successful completion→finished:all transitions disabled. Reset→pending; Cancel→cancelled terminal. Source→Explore preserves state. Zero extra calls. | Focus follows source lifecycle entities; no cancellation after running. Failure: illegal/terminal transition, invented concurrency, lost state/request. |
| [Bytes](day23/materials/byte_definition.txt), honest static formal graph | No numeric/process controls. Select Python bytes node; inspector shows immutable sequence,0–255,raw data/encoding context. Source→Explore retains selection. Zero extra calls; Explain this is a separate explicit request. | Exact pasted definition, no fabricated page. Failure: forced physical animation, decoded text equated with raw bytes, lost focus/source/request. |

Actual browser: RC R4 curves/4s/1.25A/source roundtrip; Future guards/terminal/reset/
cancellation/source roundtrip; byte node inspector `Source: pasted text`, zero sliders
or process buttons. Material switching clears prior world once rerun completes.
Narrow browser requires closing sidebar to operate underlying controls. Labels are
learner-facing; process is a clear state/control display, not an animated graph.
Screenshots: [RC page top](day23/rc-browser.jpg), [Future running](day23/future-browser.jpg),
[selected byte graph](day23/byte-browser.jpg). The RC screenshot does not show the
curves/metrics; those were verified in the browser accessibility state, not this
image. The byte screenshot shows selection, not the complete inspector. Streamlit's
internal scroll container means a fullPage capture was still viewport-sized.
The byte Source navigation was clicked before the pause, but its final round-trip
observation was not completed; that step remains a human review instruction.
Human capture suggestions: RC default/R4 curves and metrics; Future running with
disabled Cancel plus terminal/reset; byte graph/inspector/source.

## Files, commands, limitations and Day24

Production: `source_atlas/model.py`, new `learning_world/capabilities.py`,
`learning_world/{compiler,planner,schema,diagnostics,runtime}.py`, `i18n.py`.
Tooling: `tests/day23_{freeze,benchmark,review,report}.py`, `tests/test_day23.py`,
`tests/manual_day23.py`. Evidence/checkpoint/reuse ledger, frozen materials/gold,
declarations/results/audits/review/comparison, screenshots and logs. No dependency
added; no secrets file added. Existing unrelated changes are excluded from this list.

```powershell
python -X utf8 -B tests/day23_report.py
python -X utf8 -B -m unittest discover -s tests -p test_day23.py -q
python -B -m streamlit run app.py
```

Installed interpreter if PATH lacks Python:
`C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe`.
Explicit paid runner: `python -X utf8 -B tests/day23_benchmark.py --phase a --live --max-calls 36`;
then `python -X utf8 -B tests/day23_benchmark.py --phase b --live --reuse-analysis --max-calls 20`. Existing phases resume
recordings, not regenerate another benchmark. Historical audit requires matching
production fingerprint. Freeze refuses overwrite; report regenerates only derived
tables. Do not call current-production replay the historical baseline.

Limitations: small original/paraphrased text corpus; agent gold; reused analyses;
one stochastic sample per stage; no independently labeled real PDFs or learning
efficacy; equation/operation rather than comprehensive pedagogy checks; no broad
spatial browser acceptance. Second untouched holdout omitted to finish A/B/tests/
manual package. B is now a development/re-evaluation set, not untouched evidence.

Day24 measured priorities: enforce semantic operation contracts or honest static
degradation for precise recursive call/result claims; investigate trusted fixed-
constant and duplicate-display-label normalization while preserving IDs/security;
replace false-positive legacy candidate heuristics with explicit evidence. Freeze
a new independent holdout and obtain human gold review before evaluating fixes.
No new animation/runtime expansion is justified by these remaining failures.

---

## Phase C — Semantic Execution Contract

**DAY 23 — REAL-WORLD LEARNING WORLD GAUNTLET + SEMANTIC EXECUTION HARDENING.**
The user explicitly expanded this same sprint. The historical recommendation above
is superseded by this Phase C work, not another calendar-day deliverable. All A/B
numbers, recordings, frozen materials and gold above remain unchanged. No commit/push.

### Decision, prior art, licenses and changes

Use one small, independently written **bounded resolved-call-tree contract** inside
the existing explicit Learning World compiler/Explore adapter. Reuse safe_math,
canonical semantic_catalog/Workspace focus, material caches, Plotly and Graphviz.
No general program interpreter, topic-specific router, copied upstream source,
new renderer framework, downloaded asset/weight, parser or dependency was added.

Targeted prior art and exact inspected licenses are in the
[Phase C reuse ledger](OPEN_SOURCE_REUSE_LEDGER.md): XState guards (MIT core),
Python Tutor stack UX (code/license unverified; no code reuse), JSAV stepping
(MIT-license.txt core; content/extensions separately scoped), Penrose core (MIT;
integration deferred). Four candidates, incremental investigation; prior broad
research not repeated. Requirements/notices unchanged. Existing PyMuPDF deployment
license obligations are not resolved by these changes.

Production files changed in Phase C:

| Area | Files / final behavior |
|---|---|
| Shared declaration boundary | new `semantic_contract.py`: human display disambiguation keyed by IDs; finite fixed/adjustable numeric-domain validation |
| Identity | `scene/validator.py`, `scene/renderers.py`: equal labels accepted with globally unique IDs; selectbox values are IDs; selected focus retains its own source pages even for equal expressions |
| Execution | new `learning_world/execution.py`, `execution_ui.py`; `schema.py`, `planner.py`, `capabilities.py`, `compiler.py`, `runtime.py`: strict v1.1 execution declaration, legacy v1.0 acceptance/pending recheck retained; legal reducer/render integration |
| Numeric controls | `interactive_lab.py`, `scene/world/policy.py`, `runtime.py`, `schema.py`, `frontend/index.html`: source singletons stay fixed/read-only; derived values remain metrics/DAG quantities; adjustable world declarations retain their exact previous shape |
| Navigation/localization | `app.py` adds the existing Explore branch; `workspace/ui.py` reuses source actions for execution focus IDs; `i18n.py` owns new UI translations |
| Verification | new `tests/phase_c_fixtures.py`, `test_day23_phase_c.py`, `phase_c_frontend_smoke.cjs`, freeze/runner/manual scripts; `day22_fixtures.py` supplies the new required null field; `test_day17.py` selects the widget's stable ID |

No homepage redesign or existing learning feature removal. Existing dirty bytecode
and prior A/B changes are not claimed as Phase C source edits and were not reset.

### Contracts and deterministic evidence

Regression shapes were authored before production edits. Pre-fix: **6 tests, 4
errors** (duplicate focus label, fixed spatial singleton, missing execution engine
for two execution tests); then **6 passed in 6.380s**. These are deterministic
Phase C validation shapes, never benchmark materials or production examples.

Identity: IDs identify entities; labels are presentation. Equal labels get local
choice context, without changing stored identity or inventing source pages.
Existing canonical scene/node IDs bind selection and source navigation. A legacy
key-concept fallback lacking explicit IDs still cannot establish two independent
entities merely from repeated words; this change does not claim otherwise.

Execution: model output declares arguments, ordered direct child references,
result variable bindings and safe arithmetic. At most **24 calls, depth 8,
4 arguments, 3 children, 5 expression symbols, 80 actions**. Every child has one
caller, root has none; cycles/unreachable/duplicate IDs are rejected. Trusted
runtime frame IDs differ from declaration and semantic IDs. Parent waits; only
the active deepest frame may complete after its children return. Only a completed
child may return to its immediate waiting caller and validated result variable.
Results are recomputed locally. Learner text cannot inject result values.
Bounded history replay verifies reachable state; forged values/callers, premature
return/completion, wrong-scene/stale/duplicate events are rejected. Reset advances
revision and restores arguments/stack. Both recursive and different-procedure
nested examples share this same implementation. Arbitrary branching/programs and
unbounded recursion remain unsupported and must degrade honestly.

Numbers: finite `min=max=default` is **fixed**, never widened into a slider;
malformed defaults/reversed/nonfinite/negative-step domains reject. Positive-width
domains remain adjustable within source bounds, including the narrow holdout.
Derived results are DAG quantities/metrics. Lab and world show fixed text; fixed
frontend DOM uses `output`, without slider event handlers. World range provenance
continues to use its existing source/pedagogical policy. Lab's old schema has no
range-provenance field, so its adjustable-range caption remains conservative.

Focused: **48 tests passed in 25.272s** (29 previous Day23 +19 Phase C).
Final Phase C/product package: **20 passed in 17.752s**; compatibility suite:
**23 passed in 6.538s**. Tests cover malicious syntax/topology/numeric bounds,
source/ID integrity, forged/stale/reset state, exact caller results, optional
annotation isolation, unchanged 12 recorded B family choices, explicit request
count and local modes, fixed Lab chart/widgets, fixed frontend smoke and all
three new real-model recordings in the production app.

First full regression: **387 tests, one failure, 352.210s**. It caught extra
`parameter_kind=adjustable` metadata changing the old normalized world shape.
Repair preserves adjustable world dictionaries exactly; only fixed declarations
gain the read-only discriminator. This compatibility repair followed the holdout;
final recorded replay validates the same declarations against the final source.
Final complete regression: **388 passed in 292.819s**, no failures/skips,
[final log](day23-phase-c-final-regression.log). `git diff --check` passed.
The second full run was required by that observed compatibility failure; no broad
repetition of A/B paid evaluation occurred.

### New frozen Phase C holdout and results

[Manifest](day23/phase_c/manifest.json): **7 original authored teaching excerpts**,
not retrieved real PDFs, not implementation fixtures, not a representative corpus.
Frozen before any holdout request at `2026-10-06T02:58:52.239057+00:00`.
SHA256 `9f77994ff317818df5b970bf2b1b1fb45f7ec99637eaa6c0003c2b7ae61a861e`.
Agent pre-execution gold, human approval pending. No gold included as an extra
planner instruction. One stochastic request per stage; no polishing/retry.

| Material | Selected | Compile | Bounded semantic check |
|---|---|---|---|
| scoped_labels | structural | rejected | unmeasured; generated required learning_goal exceeds 120-character bound |
| nested_sum | execution | pass | S(4)→…→S(0), return chain 0/1/3/6, root10; caller/stale/reset checks |
| nested_adjustment | execution | pass | Triple(4)=12→Adjust(5)=17; same reducer, distinct procedures |
| fixed_decay | dynamic | pass | amplitude4/rate0.25 read-only; 400 curve samples match source; optional spatial scene/time works |
| narrow_gain | dynamic | pass | exact 2..2.0002/default2.0001/step0.00001 retained; fixed reference2; derived metric not a control |
| guarded_workflow | process | pass | Review→Release guards; terminal Review/Release disabled; source-authorized Reset remains legal |
| term_only | static | pass | no invented execution/parameter interaction |

**7/7 selection; 6/7 compilation; 6 bounded semantic passes, 0 failures, 1
unmeasured; 7/7 plan reference checks. API delta0 in all 6 reached local probes.**
These semantic checks mean declared arithmetic/topology/legal actions and specified
source samples, not complete source-fidelity/learning-efficacy certification.
In `nested_adjustment`, the model bound a child call to `result_returned`; that ID
exists but is a weak source-action match. Numeric routing is correct; references
alone cannot prove that the action selects the pedagogically correct concept.
Human grounding remains pending and this issue is retained as a remaining failure.

Audit history, all preserved:

- [Original live results](day23/phase_c/results.json) falsely marked local checks
  failed after the substantive probes: evaluator passed `{}` as a material wrapper.
- [Audit](day23/phase_c/audit_results.json) fixes that wrapper locally; 5 passes,
  1 apparent workflow failure, 1 unmeasured. No paid requests.
- [Audit v2](day23/phase_c/audit_v2_results.json) also honors the source's explicit
  Reset edges; gold/text unchanged. 6 passes, 1 unmeasured. No paid requests.
- [Final replay](day23/phase_c/final_replay_results.json) revalidates the same raw
  declarations after the adjustable-metadata compatibility repair. Zero paid
  attempts in this execution; historical paid usage is separately retained.

Paid Phase C: **16 attempts** (7 analysis +7 planner +2 scene), under the **18 cap**;
**47,888 input /23,481 output /71,369 total tokens**, model `gpt-5.6-luna`.
Existing A/B usage remains35 attempts/130,915 tokens; combined actual attempts51,
combined tokens202,284. Billing not estimated. Audits/tests/manual replay add0.

### Generality, limits and next evidence-driven work

Routing uses semantic flags, normalized topology, safe expressions and numeric
domain shape; no topic-name branch. The audit test inspects new dispatch/reducer
conditions and revalidates all twelve B planner selections without paid calls.
No specific benchmark material/label is imported by production.

Remaining: required text limits can still reject an otherwise useful probability
scene; old finite candidate also has this error. The unchanged old damped spatial
candidate still has an illegal experiment time patch, despite its fixed parameter
now validating. Do not count either old recording as repaired whole-scene success.
Bounded resolved examples are not a general execution language. Source-action ID
fidelity, human gold/visual quality, browser gestures, representative PDFs and
learning outcomes are not proven by arithmetic tests. Chrome automation returned
`Computer Use was not approved to use Google Chrome`; no browser action was taken.
AppTest and fixed JS smoke are recorded separately from pending human live acceptance.

Next sprint should address strict prompt/schema/validator field-limit alignment
and source-action binding quality, based on these measured failures; obtain human
gold review before another independent evaluation. No new animation/domain system
or benchmark rebuilding is justified here. Phase C engineering stops after final
regression, three-case handoff and this evidence/checkpoint update.

### Exactly three human live tests

Run from the repository root (the earlier launch error occurred because PowerShell
was in `C:\Users\88690`, where `app.py` does not exist):

```powershell
Set-Location -LiteralPath 'C:\Users\88690\OneDrive\桌面\visual-learning-lab'
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m streamlit run tests/manual_phase_c.py --server.port 8526
```

Open `http://localhost:8526/`. This harness replays raw real-model Phase C output
inside `app.py`; live API is blocked. Select exactly these three sidebar materials.
Avoid explicit Analyze/Explain/Build buttons during this local review.
The hidden recorded-review server is running as PID13288, health `ok`; the unrelated
production server was not stopped. Codex browser open request was queued.

| Test / exact material | Exact actions and expected visible state | Disabled actions / source / API |
|---|---|---|
| A — `docs/day23/phase_c/materials/nested_sum.txt` | Choose `nested_sum`. Click **Call child** four times: S(4)→S(3)→S(2)→S(1)→S(0). Click **Complete current call**: result0. Click **Return to caller**, then **Complete current call**, repeating this pair four times: results1,3,6,10. Click **Reset execution** to restore S(4). | Initial Complete/Return disabled; base Call child disabled; completed child allows only Return (plus reset/inspect); completed root Call/Complete/Return disabled. Source shows the original pasted S(n) description with no fake PDF pages; Source→Practice→Explore preserves stack/results. Postcompile API delta0. |
| B — `docs/day23/phase_c/materials/scoped_labels.txt` | Choose `scoped_labels`. Open **Explore this visualization · Choose from list instead**. In **Choose a learning item**, select **Assembly Ready = {p,q}**, then **Inspection Ready = {q,r}**. Inspector changes to each separate entity; shared Ready word does not merge their stable IDs. | No call/return controls. The probability scene's required-field rejection remains honest; retained main graph is the tested fallback, not a successful compiled probability scene. Source shows both departments' original definitions, no invented pages. Source→Explore preserves selection. API delta0. Exact identical-label acceptance is additionally proven by the separate deterministic scene fixture, not relabeled as this holdout result. |
| C — `docs/day23/phase_c/materials/fixed_decay.txt` | Choose `fixed_decay`. Confirm **Initial amplitude=4** and **Decay rate constant=0.25** show fixed values. Open **Keyboard time control**, move **Time (s)** to its right endpoint6; magnitude≈0.892521 and rate≈−0.223130. The coordinated point/wave/metrics share the same scene; the separate static camera is labeled as a snapshot. | Fixed amplitude/rate have no slider. Time remains adjustable; no invented parameter range. Source retains the exact formula and constants; Source→Practice→Explore preserves time6. API delta0. Browser Play/Pause/gesture quality remains a human observation. |

Normal app command:

```powershell
Set-Location -LiteralPath 'C:\Users\88690\OneDrive\桌面\visual-learning-lab'
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m streamlit run app.py
```
