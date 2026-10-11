# POST_FIX — Day27 A/B hardening

Complete; awaiting human semantic review. Frozen baseline A remains PASS 4 / PARTIAL 4 / FAIL 2. This is not an untouched holdout. No commit/push/Day28 or Candidate C work.

Implementation plan and scope: shared quantity provenance at existing canonical owners, plus exact semantic-to-renderer ownership. Focused/offline gates precede live generation; the production tree was sealed before any live request.

A contract: `source_fixed`, `source_variable`, `hypothetical_exploration`, `derived`. Numeric source assertions retain immutable value/evidence/validated pages. Source variables need explicit `expose_control`; hypothetical controls use separate IDs and optional `source_baseline_ref`. Derived expressions cannot be free controls. Runtime time has its own semantic role. Source values, initial exploration and current exploration are distinct. The trusted Lab/world/analogy commits enforce write permission, bounds, numerical safety, stale event guards and atomic rejection.

Versions: Lab 2.0, Spatial 2.4, Analogy 1.2, shared quantity/ownership 1.0. Legacy Labs remain read-only with no inferred role/ownership; incompatible spatial/analogy caches require explicit rebuilding. AST allowlists and the existing per-expression variable bound are unchanged. No new dependency.

B contract: real accepted graph/comparison objects register existing canonical IDs. Semantic identities remain focusable when their formal renderer is unavailable, with no registration. Lab controls/series/metrics carry explicit, bounded many-to-many `semantic_refs`; registration validates canonical ID, material, specification hash, page compatibility and actual renderer object. IDs are scoped as `lab:{demo}:{group}:{local_id}`. Related lessons, labels and proximity confer no ownership. Representation links never create inverse handles.

Checks: focused 295/295; offline 10 captured cases plus 4 explicitly annotated shapes, 5 deep joins and 2 canaries, API 0; 5 one-attempt live cases, 16 Responses requests; 5 real empty-app browser replays, source/focus preserved, no context mismatch or new network generation.

Live observations:

| Case | Planner / family | Compiler | Rejected Lab demos | Selected representation IDs |
|---|---|---|---|---|
| regression | accepted / static | NOT_APPLICABLE | 1 | ['calculate_intercept'] |
| probability | accepted / structural | rejected | 0 | ['general_addition', 'lab:demo_overlap:series:union_probability'] |
| circuits | rejected / None | NOT_APPLICABLE | 0 | ['flow_model'] |
| harmonic | accepted / dynamic | existing validated numeric lab | 0 | ['spring_model'] |
| signals | accepted / static | NOT_APPLICABLE | 1 | ['input_signal'] |

Usage: 16 Responses; input 187,073, output 60,210, total 247,283; cumulative Response latency 784.056s; 5 PDF uploads recorded separately. Returned model IDs are in request-usage.json. No billing estimate is inferred.

Final complete regression: one actual discovery, 489 tests, 480 passed, 6 failures, 3 errors, 0 skips, 252.150s. Original failing result/log remains unchanged. Subsequent A/B test fixture/cache corrections passed 105/105 focused checks; no second full suite was run. Production seal is unchanged. A prior launcher setup error ran zero tests and is preserved separately.

Immutability/links: explicit offline source shapes retain regression R=-0.499, probability 1/3, Big-O 100 and RC 5/0 and 0/5 facts under legal exploration and rejected forged commits. Live accepted Probability/RC/SHM specs also retain their declared facts under local commits. The new Regression proposal declares R separately but is rejected, so there is no runtime correlation control. Five unchanged captured deep entities go from [] to real formal IDs; exact live IDs differ across new generations and are not assumed equivalent.

Canaries: offline Signals retains its computable legacy curve read-only and formal views; Debugging stays static with no generated code execution. New Signals Lab is rejected by the existing variable bound and uses an operational formal/static fallback. Its interactive capability was not preserved in this generated attempt; no semantic A rescore is assigned.

Remaining limitations: Candidate C Numeric Lab availability bias remains unresolved; planner files match the frozen production hashes. Probability structural compilation rejects an overlong learning goal. RC planner rejects its declaration. Regression and Signals Labs exceed the existing expression variable bound. All failures/omissions remain in the five-case denominator. Grounding/ownership validation establishes internal linkage and write safety, not PDF semantic truth. Human review must decide whether hypothetical experiments are appropriate.

Files changed from the frozen production snapshot:

- `analogy/runtime.py`
- `analogy/schema.py`
- `analogy/state.py`
- `analogy/validator.py`
- `app.py`
- `i18n.py`
- `interactive_lab.py`
- `manipulation/contract.py`
- `manipulation/lab.py`
- `manipulation/runtime.py`
- `manipulation/world.py`
- `quantity_contract.py`
- `representation_contract.py`
- `scene/world/engine.py`
- `scene/world/frontend/index.html`
- `scene/world/runtime.py`
- `scene/world/schema.py`
- `scene/world/state.py`
- `scene/world/validator.py`
- `source_atlas/model.py`
- `workspace/twin_ui.py`

Test fixtures, focused/offline/live/browser/final reporting tools and evidence are separate under tests/ and docs/day27/post_fix/. No new dependency. Run the app: `python -m streamlit run app.py`.

Review: [human packet](post-fix-semantic-review.md), [validation](validation.json), [usage](request-usage.json), [B facts](engineering-scorecard.json).
