# Day 21 checkpoint — implementation complete

Objective: four conditional views over one material and canonical semantic state. Core checkpoint was written before optional follow-up work; completion evidence is in [DAY21_EVIDENCE.md](DAY21_EVIDENCE.md).

Architecture: `workspace/state.py` owns local navigation; existing scene reducer/probability selectors own scene focus. `workspace/ui.py` supplies compact context/actions. Analysis-only stable graph IDs use the same workspace contract. Existing Atlas, Lens, world, quizzes, labs and simulations are reused. Homepage and requirements unchanged.

Files changed: workspace module, app.py, i18n.py, learning_canvas.py, interactive_lab.py, scene/compiler.py/renderers.py, scene/world/state.py/runtime.py/frontend/index.html, source_atlas/compiler.py/state.py/runtime.py, Day 14–20 integration tests, Day 21 tests/offline demo, fixed frontend smoke and reuse ledger.

Works: conditional Learn/Source/Explore/Practice; projectile Gravity g Source→Explore→Source without compiler/parser calls; reverse linking; retained source anchor and numeric state; formula navigation; explicit source explanation with context fingerprint/cache; exact-ref practice; graph focus synchronization; clear selection and recording/replay; text, missing scenes/Atlas/native package, image-only/native fallback, and missing PDF bytes with whitelisted extracted pages.

Focused command: `python -X utf8 -B -m unittest discover -s tests -p test_day21.py -q`. Final coverage: 26 Day 21 tests passed (25 in 19.510 s, added fallback test in 1.478 s). Final affected-regression run: 28 passed in 27.445 s.

Full regression: invoked once, 219 cases with 34 initial errors (one failed module import). Localization/test-routing/indentation issues repaired; 69 targeted repairs left two test view assumptions, both subsequently fixed and verified. Final collection: 236 real cases. No clean final full rerun is claimed; all discovered failures have targeted passing evidence.

Known failures: none remaining from executed tests. Browser gestures and real model-grounding fidelity are unverified. No before/after browser screenshots captured. Existing Streamlit context/deprecation warnings persist.

Next steps: follow live acceptance, especially clear focus during playback/replay and real-PDF source grounding. No unfinished code work; evidence documents limitations and suggested Day 22 direction.

Live production: `python -m streamlit run app.py --server.port 8521`. Offline demo: `python -m streamlit run tests/manual_day21.py --server.port 8522`; Source page 2→Gravity g→Explore→manipulate time/parameters→Source. Exact host Python path and detailed steps are in evidence. Explicit production AI actions retain normal costs; hero navigation needs none.

No paid API calls, new dependencies, commits, pushes or resets performed. Existing work preserved.
# Day 21 Ultra — Analogy World checkpoint

Architecture implemented: `analogy/schema.py` strict v1.0; `compiler.py` one explicit Responses call with bounded stored-language/source/catalog context; `validator.py` exact envelope, IDs, pages, fidelity, mandatory breaks/misconceptions, affine formal parameter binding; `engine.py` reuses safe_math via world expression helpers; `state.py` canonical focus/world reducer adapters plus bounded caches; `runtime.py` conditional Explore representations; `frontend/index.html` independently written numeric-only SVG clock, shape selection and horizontal parameter gestures. `app.py` and `i18n.py` integrate it. No dependency added, no copied upstream code, no paid call, no commit/push.

Primitives: rectangle, disc, segment, repeated tokens, time-sampled curve, numeric meter. Motion/annotations are declarative expressions/plain text; no generated executable code. Frame count <=120, repeated objects <=64, payload <=450 KB, parameter/quantity/spec/numeric caches bounded. Shared focus has no analogy mirror; quantitative values read from formal world/lab stores. Qualitative controls explicitly remain teaching controls.

Completed acceptance: V/R controls update formal V=IR and flow projection; phase updates the pointer and waveform together; queue uses the same engine with a qualitative token-count control. Browser shape/keyboard selection, actual pipe drag, Source round trip, phase playback and queue-count changes were observed on original synthetic fixtures. Three screenshots are in docs. No live AI/source-fidelity accuracy or learning-efficacy claim.

Final verification (2026-10-04): **26 analogy tests passed** (10.621 s; analogy-focused.log), including PDF round trips, canonical lab bindings, failure/static fallback and the three-domain fixed frontend smoke. The single Ultra full regression invocation passed **262 tests** (162.109 s; analogy-regression.log). Subsequent display/navigation refinements exposed and fixed the default representation initialization in older sessions; the final affected suites passed **52 tests** (28.631 s; analogy-workspace-final.log). Do not describe the 262-case invocation as occurring after those last refinements. No paid calls, dependencies, commits or pushes.

Final files: analogy package and fixed frontend; app.py, i18n.py, interactive_lab.py (existing lab links select Formal); tests/analogy_fixtures.py, test_analogy.py, analogy_frontend_smoke.cjs, manual_analogy.py; existing evidence/checkpoint/reuse ledger; logs and three JPEGs. Existing Day 21/earlier dirty changes and tracked bytecode were preserved.

Core work is complete. Optional thermodynamics, generic discrete enqueue/dequeue/state-machine actions, non-affine formal bindings, collision-aware labels and a joint formal/analogy animation clock are deferred. Analogy animation is an explicit teaching clock; it does not overwrite formal committed time. Qualitative controls never alter a formal numerical model. Affine bindings require a validated world dependency or existing lab lesson/visual link; source fidelity and candidate scores remain estimates.

Exact continuation: run `python -B -m streamlit run tests/manual_analogy.py --server.port 8523` to reproduce all three offline cases; then use production `python -m streamlit run app.py --server.port 8521` with a real material, select a formal concept and explicitly build one analogy. Human-review source fidelity, limitations, defaults and legal-range corners; this explicit live build may incur the normal API cost. Do not redo prior-art research: eight decisions are already recorded. If changing core logic, run focused `python -B -m unittest discover -s tests -p test_analogy.py -v`; broaden only for new failures/changes. No optional feature implementation is outstanding for v1.


## Live rejection repair (2026-10-04) — supersedes the earlier core-complete claim

Human diagnostics confirmed normalize/ambiguous_mappings: six valid mappings for five analogy entities, including two formal concepts on pipe_relation. Analogy v1.1 supports explicit many-to-one correspondences with deterministic canonical selection and safely omits inconsistent optional bindings/drag details. Source, fidelity, AST, numeric and work limits remain enforced. Controlled internal diagnostics retain candidate and normalized mapping evidence without prompts/source/keys. Focused analogy 42 passed; final relevant workspace+analogy 68 passed (42.835 s). No full suite, engineering paid requests, dependency, commit or push. See DAY21_ANALOGY_LIVE_FIX.md for exact changed files, policies and retest. Final real-PDF hero acceptance remains pending the human retest; synthetic runtime completions are not live-generation evidence.

### Second live continuation (2026-10-04)

New trace: normalize/unsafe_expression at belt_body rectangle.radius; the actual slot value was not exported, so its emptiness is not established. Added type-specific blank auxiliary defaults, omission of incomplete visuals after full safety checks, exact controlled expression/numeric diagnostics, and schema-valid failed-candidate retention with explicit zero-API local revalidation. Final derived visual budget remains enforced. Final related suites: 83 passed (39.238 s; 57 analogy + 26 workspace). See DAY21_ANALOGY_LIVE_FIX.md for exact files, evidence limits and retest. Real PDF hero acceptance remains pending; no engineering paid call, full suite, dependency, commit or push.

### Final live-bug audit — 2026-10-04

Independent review fixed target reservation by omitted affine links and immediate renderer-diagnostic visibility after mapped-focus changes. Actual hero PDF native text supports all source references retained in trace (2). Final affected suites: **87 passed** (72.504 s; 61 analogy + 26 workspace), analogy-live-audit-focused.log. No new live trace or paid request. Production app.py restarted on 8521 and homepage verified; browser file chooser could not preload PDF. Manual upload/analysis/build remains required in the new session, or local recheck in any session retaining a failed declaration. Real hero rendering acceptance remains pending; do not promote synthetic tests or the homepage screenshot into that proof. Details: DAY21_ANALOGY_LIVE_FIX.md.

### HERO accepted by human — 2026-10-04

Third live trace: suitable water_channel, eight valid mappings, repaired auxiliary defaults, then geometry_bounds. Corrected raw-travel-versus-wrapped-position validation ordering while retaining raw 10,000 / rendered 100 / radius 20 bounds and all fatal security checks. Controlled geometry diagnostics now include field/ranges/wrap metadata. Final affected suites: **94 passed** (51.890 s; 68 analogy + 26 workspace), analogy-geometry-workspace-focused.log. Human confirmed that Rerun now runs successfully: **「ㄟ 終於好了 我就案rerun 可以跑」**. This supersedes the pending build/render status. Human report is the live acceptance evidence; old trace omitted full formulas and the agent's separate in-app tab is still the homepage. No full suite, engineering paid call, new dependency, commit or push. Full evidence and changed files: DAY21_ANALOGY_LIVE_FIX.md.
