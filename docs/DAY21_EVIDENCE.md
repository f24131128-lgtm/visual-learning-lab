# Day 21 — Learning Workspace v1

Four active views replace the accumulated results page: **Learn**, **Source**, **Explore**, **Practice**. A radio selects a conditional Python branch; inactive major renderers are not invoked. The input homepage is unchanged.

## Prior art actually used

Reuse the existing [Day 20 landscape](OPEN_SOURCE_LANDSCAPE.md) and [reuse ledger](OPEN_SOURCE_REUSE_LEDGER.md), without a new landscape sweep. H5P contributes one active activity and explicit feedback/retry; PhET Joist contributes screen switching independent of system reset; LearnHouse contributes learning-activity navigation without importing an LMS; Augmented Physics contributes source-first entry into interaction. AlgeBench and ViviDoc remain close semantic/state/render prior art. Source-linked interactive documents are not claimed as novel.

This is independently written Streamlit orchestration over existing VLL renderers, reducers and validated IDs. No competitor code/assets/models, new packages or notices added. Existing PyMuPDF licensing remains unresolved for deployment.

## Architecture and behavior

- `workspace/state.py`: material-scoped `get_workspace_state`, `open_workspace`, `get_workspace_focus`, `set_workspace_focus`, `clear_workspace_focus`, and conservative action availability. Scene focus is read directly from the existing spatial reducer/probability selectors; only analysis-only materials use a workspace stable-node selection. Navigation never owns a parallel world state.
- `workspace/ui.py`: localized navigation, compact human-facing Current Focus, validated source pages/verified formula excerpts, supported Atlas actions and existing Source Lens fallback.
- `app.py`: existing structured-data normalization and caches, followed by conditional Learn/Source/Explore/Practice rendering. Relationships and evidence are collapsed; suggested visualization remains available in Explore. No analysis/schema/API-site rewrite.
- `scene/compiler.py`: optional Source/Explore render routes separate the existing Atlas builder from scene rendering. Explicit compiler actions and cache identity remain unchanged. Standalone Day 19 callers retain the prior split-view behavior.
- Source Atlas selection retains its same-focus region hint; world selection wins when focus changes. Native parser regions never gain fabricated semantic links.
- Source explanation reuses the existing bounded explanation context/request/cache, keyed additionally by the exact context fingerprint to prevent reused Atlas region IDs from serving stale explanations. Formula opens an existing same-focus Formula Trace locally. Concept practice appears only for exact validated visual refs, not whole-scene lesson associations.
- Focus clearing preserves time, parameters and baseline. Spatial clearing is a local recorded reducer action; replay accepts an absent selection while model-generated focus patches still require a validated quantity ID. The fixed frontend supports absent selection. Probability clearing uses a valid local empty-set operation.
- Existing lesson/lab/simulation links route between Practice and Explore. No quiz engine, persistent mastery, analogy renderer or renderer registry added. Future Formal/Analogy/Compare activities can be composed inside Explore without changing the top-level contract.

## Hero flow and verification

Offline test fixture extends the existing projectile PDF/Atlas with **Gravity g** and **ay = -g**, mapped to the scene's existing `gravity` quantity. Fixtures remain under tests and are never imported by production.

Source → page 2 → Gravity g → Explore action → existing world focused on gravity → change time → Source keeps the original region and numeric state. Related formula selects the existing formula region. Mocked scene/Atlas requests and native parser remain at **zero calls** throughout navigation. Reverse world selection finds the corresponding source anchor.

Focused command: `python -X utf8 -B -m unittest discover -s tests -p test_day21.py -q`. Final Day 21 coverage: **26 tests**. The final 25-test run passed in **19.510 s** ([log](day21-focused.log)); the subsequently added missing-PDF-byte/validated-text fallback test passed in **1.478 s** ([log](day21-source-fallback.log)).

One full regression invocation: `python -X utf8 -B -m unittest discover -s tests -q`. Initial run: **219 cases, 34 errors**, [log](day21-regression.log). These exposed an uncaptured localized radio formatter, legacy test mode setup and one test indentation error. The first targeted repair ran **69 cases** with two remaining legacy view-assumption failures ([log](day21-repair.log)). These were fixed; **28 targeted cases passed in 27.445 s** ([log](day21-final-focused.log)), followed by the final Day 21 runs above. Final collection contains **236 real test cases**, covering the original full attempt, the previously unimportable 14-test Day 15 module and new focused cases. All discovered failures have a passing targeted verification. This is **not** a claim of one clean final 236-test full run: the full suite was deliberately invoked only once, then failures/affected scopes were retested. Fixed frontend smoke passed in that full attempt, including absent-focus rendering.

Paid OpenAI calls during engineering: **0**. Existing explicit compiler/explanation/review calls are mocked in tests. No commit, push or reset performed. No screenshots or real model-grounding accuracy claims; AppTest and fixed-code frontend smoke are separate from actual browser gestures.

## Changed files

New: `workspace/{__init__,state,ui}.py`, `tests/test_day21.py`, `tests/manual_day21.py`, checkpoint/evidence and verification logs. Scoped production changes: `app.py`, `i18n.py`, `learning_canvas.py`, `interactive_lab.py`, `scene/compiler.py`, `scene/renderers.py`, `scene/world/{state,runtime}.py`, `scene/world/frontend/index.html`, `source_atlas/{compiler,state,runtime}.py`. Existing Day 14–20 integration tests now explicitly select active views; fixed frontend smoke covers clearing. Reuse ledger updated. Requirements unchanged.

## Live acceptance

Run production from the repository root: `python -m streamlit run app.py --server.port 8521`.

On this host Python is not on PATH. Exact PowerShell command:

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m streamlit run app.py --server.port 8521
```

For the repeatable zero-model demo: `python -m streamlit run tests/manual_day21.py --server.port 8522`.

1. In the offline demo, choose Source page 2 and Gravity g. Confirm Current Focus, original page and related formula context.
2. Click the exploration action. Confirm the gravity vector is focused, manipulate time/launch parameters, then switch Source. Confirm the original Gravity g region remains selected and numeric state is preserved.
3. Open related formula; verify the original text and existing Formula Trace. Switch Explore and select a different quantity; return Source and verify its mapped anchor. Clear focus and exercise playback, recording/replay and keyboard selection.
4. Switch Learn and Practice. Check that navigation retains checked quiz answers/review/cache state. Do not expect a gravity-specific quiz unless exact existing visual refs support it.
5. Test production with a real analyzed PDF: build the scene explicitly in Explore and Atlas explicitly in Source; subsequent navigation is local. Existing explicit builds/explanations can incur normal API costs. Test English and Traditional Chinese; generated content keeps the analysis language.
6. Test pasted text, no scene, no Atlas and missing optional pdfplumber. Image-only/no-native-text parser fallback must not fabricate OCR/geometry. Production's existing text-bearing-PDF analysis gate remains unchanged.

## Limits and next move

Workspace navigation preserves committed world state; pause browser playback before leaving Explore to commit the displayed time. Continuous in-flight playback handoff across unmounted views is not claimed. Semantic cross-links require existing stable IDs; labels and page co-occurrence are not treated as identity or proof of concept-targeted practice. Clear focus does not clear physics. Multiple available exploration tools remain composed inside Explore; no generic activity registry is claimed. Browser gestures and real grounding require the live acceptance above.

Recommended Day 22: run a small real-material UX acceptance pass, then define validated analogy suitability/fidelity and semantic-link contracts before adding an Analogy activity. Keep quiz/mastery expansion separate.

## Analogy World v1 — Day 21 Ultra

This section supersedes the earlier analogy-as-future-direction note. The existing Learn/Source/Explore/Practice workspace remains intact. Explore now conditionally renders **正式模型 / 譬喻世界 / 對照**, with Formal the default. Existing lesson/lab links open the formal experiment; ordinary workspace switching preserves the chosen representation.

### Targeted prior art and licenses

Eight systems/papers, without repeating Day 20's landscape: [AnalogyMate](https://arxiv.org/abs/2401.17856), [Cao et al., multi-modal STEM analogies](https://arxiv.org/abs/2308.10454), [Trey & Khan, computer-based analogies](https://www.sciencedirect.com/science/article/pii/S036013150700070X) (publisher abstract only), [Plotly.js core MIT](https://github.com/plotly/plotly.js/blob/main/LICENSE), [JSXGraph](https://github.com/jsxgraph/jsxgraph/blob/main/LICENSE.MIT), [Augmented Physics](https://github.com/adigunturu/AugmentedPhysics), [ViviDoc](https://github.com/MisterBrookT/vividoc) and [PhET Ohm's Law](https://phet.colorado.edu/en/simulations/ohms-law). Candidate assessment, explicit correspondence and linked controls are close prior art, not novelty claims. Research suggests designs worth testing; it does not establish this implementation's learning efficacy.

Decisions: REUSE existing safe_math, world reducer, catalog, installed Plotly public API and component transport; WRAP an independently authored numeric SVG renderer; LEARN the systems' behavior/decomposition; DEFER an additional JSXGraph bundle. No upstream code/assets/weights copied, no downloads or new packages, no notice changes required by this addition. Repository/framework license statements do not grant simulation/artwork/model rights. Existing PyMuPDF AGPL/commercial deployment review remains unresolved. Detailed decisions are in OPEN_SOURCE_REUSE_LEDGER.md.

### Architecture and boundaries

- `analogy/schema.py`: strict v1.0 response with 1–3 candidate assessments, selection/unsuitability, learning goal, formal and analogy entities, explicit relationship/explains/fidelity mappings and mandatory breaks/misconceptions. Six primitives: rectangle, disc, segment, repeated tokens, sampled curve and numeric meter. Parameters/control references are interactions; safe time expressions and numeric visibility describe continuous transitions. Token wrapping is fixed numerical projection for unidirectional streams, not a new executable grammar.
- `compiler.py`: one explicit Responses request, using bounded existing source text, formal catalog and parameter registry in stored `analysis_language`. No PDF resend, no image grounding or OCR. Missing source context or an oversized response fails before a rendered world. No request from navigation or selection.
- `validator.py`: exact fields/types, globally unique local IDs, known formal IDs, analyzed-page provenance, unambiguous entity mappings, required limitations, candidate fidelity >=0.65/risk <=0.45 and other teaching scores >=0.4. Scores are model estimates, not verified source truth. Unknown references, executable/markup content, unsafe ASTs, cycles, nonfinite values and excessive work are rejected in isolation.
- `engine.py`: existing safe_math allowlists via world expression helpers; no eval/exec/generated JS. One numerical projection feeds SVG and the Plotly fallback. Defaults/corners are sampled and actual changes are checked before mutation; sampling is not a proof over a continuous domain or of source fidelity. Full legal sampled envelope plus actual bounds prevents viewport clipping.
- `state.py`: reads canonical workspace/world focus, resolves analogue selection back through validated mappings, and delegates bound world changes to the existing validated reducer. Lab bindings require existing stable lesson/visual links and recheck the lab curve before mutation. Formal values are authoritative; bound values are not mirrored. Affine bindings validate complete ranges/defaults and dependency identity; qualitative controls stay explicitly independent. Reset uses a trial state and commits atomically.
- `runtime.py` / fixed frontend: numeric-only bounded geometry, plain text labels, equal spatial scales, keyboard selection, horizontal parameter dragging with inverse SVG screen coordinates, Play/Pause/replay/scrub and a static fallback. No model expressions sent to the browser. Stale/duplicate/wrong-identity events are ignored; actual-state fingerprints/revisions protect local commits. Formal expression display substitutes human labels without changing original source text or model equations.
- Cache identity: material, stored language, schema version, formal model/lab/lesson signature and build focus. Local parameters, time, selection, quiz progress and recordings are excluded. A compiled analogy covering several mapped concepts is reused as focus changes. Unsuitable results are cached; failed calls preserve the previous valid world and permit explicit retry. Spec cache <=4 and numeric cache <=4; parameters <=4, quantities <=24, mappings/entities <=16, primitive groups <=24, repeated objects <=64, frames <=120, component payload <=450 KB. No new semantic source boxes or independent analogy focus.

What helps explain, where it breaks and misconceptions remain visible in both Analogy and Compare. Generated analogy is labeled as a teaching aid, separately from source-supported formal analysis. Compare reuses an existing formal scene or bound lab chart plus clickable correspondence. Analogy animation has its own teaching clock; formal committed time is preserved. Pause formal playback before comparing instantaneous values or leaving its view.

### Acceptance and evidence

All fixtures live under tests and are absent from production routing. They are original synthetic sources; they demonstrate the general contract/runtime, not live model generation quality.

| Case | Same general renderer / verified behavior | Fidelity boundary |
| --- | --- | --- |
| V = IR ↔ water flow | Water level binds voltage, restriction binds resistance; formal current and numeric flow use V/R. Direct pipe drag changed resistance to about 9.0347 and current/flow to about 0.55342, with V=5. Shape/keyboard selection mapped restriction to canonical resistance; Source selected the existing original PDF anchor. Compare showed the same committed formal values. | Normalized teaching geometry is not a hydraulic solver; water is not electrons, and AC/fields/losses are outside this aid. |
| Sine/phase ↔ rotating pointer | Phase control binds the existing formal phase. Pointer projection and waveform share the same numeric trajectory/clock; unit tests assert their array equality. Browser phase adjustment and playback were observed. | A physical clock hand does not generate the source signal; analogy/formal animation clocks are separate. |
| FIFO queue ↔ people in line | Same repeated-token/curve-independent primitives, no domain branch. Browser count change displayed five tokens, with local ordered traversal. | Count is a qualitative teaching control. Traversal illustrates order; no enqueue/dequeue throughput, priorities or scheduler simulation is claimed. |

Browser screenshots: [water flow after drag](analogy-electricity.jpg), [phase/pointer](analogy-phase.jpg), [queue](analogy-queue.jpg). They are fixture UI evidence. Suggested additional human screenshots: source resistance anchor plus Current Focus, Compare with V/R/I and mappings, the always-visible limitations, and static fallback. Some nearby labels can overlap; automatic text layout is deferred.

Verification: focused **26 passed** (10.621 s, analogy-focused.log), including three-domain fixed-code Node smoke. The single full invocation **262 passed** (162.109 s, analogy-regression.log). Final display/navigation refinements were then checked against both the previous workspace and new analogy suites: **52 passed** (28.631 s, analogy-workspace-final.log), after repairing a missing default for pre-existing sessions. This distinguishes the full run from the last targeted verification; the full suite was not rerun. The fixed smoke checks clock/layout continuity, numeric rendering, selection/drag transport and hostile messages; actual browser interaction was additionally observed. API mocks verify one explicit build and zero additional calls from local actions; paid calls during engineering/browser acceptance: **0**.

### Reproduce / live-test

Production, from repository root:

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -m streamlit run app.py --server.port 8521
```

Repeatable offline browser demo (all three cached validated specs and synthetic source pages):

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B -m streamlit run tests/manual_analogy.py --server.port 8523
```

1. Choose 電路與水流. Select the pipe's unobstructed edge, or focus the 管道限制 SVG button and press Enter. Confirm Current Focus is 電阻. Drag the pipe horizontally; check resistance/flow change, then Compare's formal values. Adjust water level and restriction with sliders; Reset restores their defaults while retaining focus and other learning state.
2. Switch Source: its selector/anchor should select 電阻 on the original PDF. Return Explore → Analogy: the same valid spec and parameters remain; do not press an AI build. Existing mapped concepts reuse the compiled world.
3. Choose 相位與指針. Change phase, Play, Pause, scrub and Replay. Confirm the rotating tip, waveform marker and numeric projection move together. Switch Formal to inspect its bound phase; formal time remains committed.
4. Choose 佇列與排隊. Change count, play the ordered marker, select a token and inspect Source/Compare. Confirm the qualitative-control label and FIFO limitations. Toggle 靜態檢視; accessible correspondence/buttons/sliders stay available.
5. In production analyze your own text/PDF, explicitly build a formal scene/lab when suitable, select a validated concept, choose Analogy and press 建立譬喻世界 once. This optional live AI build may incur the normal API cost; no such build was used for this sprint's evidence. Inspect candidate/source fidelity and limits manually. In unsuitable cases retain Formal; on transient failure retry explicitly.
6. Switch UI language, representations and workspaces; generated labels and build context must retain the stored analysis language. Verify lessons, checked answers/review, explanations, baselines and recordings survive. No model call should result from these local actions.

Changed for Ultra: `analogy/`, `app.py`, `i18n.py`, `interactive_lab.py`, the four analogy test/demo files, this evidence/checkpoint/reuse ledger, logs and screenshots. No dependency, commit or push. Existing dirty Day 21 and earlier work was preserved.

Future work: real-material generation/grounding acceptance, empirical learning evaluation, non-affine validated bindings, richer discrete transitions, joint clock coordination and automatic label layout. Thermodynamics and other stretch domains are deferred; adding a domain must use this same bounded declaration/runtime rather than a topic-specific application.

### Live rejection repair evidence (2026-10-04)

The human-generated sanitized trace establishes normalize/ambiguous_mappings, with water_pipe selected at fidelity 0.84 / risk 0.30 and six mappings for five entities. Version 1.1 repairs that cardinality contract and isolates optional runtime issues. See [repair report](DAY21_ANALOGY_LIVE_FIX.md) for exact evidence, fatal/recoverable policy, changed files, 42/68 passing focused results and the manual PDF retest. The captured trace lacks full math/geometry; regressions use marked synthetic completions. Final live hero acceptance has not yet been confirmed. No engineering paid call, new dependency, full-suite iteration, commit or push.

### Second trace and safe visual-slot repair

The human-provided second trace selected the conveyor/gate candidate and passed semantic mapping validation, then rejected the rectangle radius slot. Its expression text was omitted by the earlier diagnostics. Type-specific blank defaults and safe incomplete-visual omission are now covered by deterministic tests; a replayable failed declaration is retained privately for local revalidation. The final relevant run passed 83 cases in 39.238 s. Actual blankness/live visual acceptance are not claimed. Details and file list: DAY21_ANALOGY_LIVE_FIX.md. No engineering paid request, full repository suite, new dependency, commit or push.

Final contract audit: **87 affected tests passed** (72.504 s; analogy-live-audit-focused.log). An omitted affine link no longer reserves a formal control, and renderer errors are downloadable immediately even while the active cached analogy covers a different mapped focus. The actual two-page hero PDF supports all source-page references in trace (2). The production 8521 homepage was verified after restart; this is service availability evidence only. Browser file selection failed and no live model request was made. Real PDF analogy generation/rendering acceptance remains pending, separately from deterministic tests and source provenance. See DAY21_ANALOGY_LIVE_FIX.md.

**Live HERO build/render accepted by human after Rerun (2026-10-04).** This supersedes earlier pending notes. Third diagnostic establishes geometry_bounds after valid water_channel selection/mappings/defaults; a general wrapped-token projection-order bug was corrected without increasing raw/geometry limits. Final affected suites: **94 passed** (51.890 s; analogy-geometry-workspace-focused.log). Human statement: 「ㄟ 終於好了 我就案rerun 可以跑」. No agent-side screenshot/full-response replay or comprehensive interaction/fidelity review is claimed. Exact geometry expressions were absent from the pre-fix diagnostic. Engineering paid requests, full-suite reruns, dependencies, commits and pushes: none. Details: DAY21_ANALOGY_LIVE_FIX.md.
