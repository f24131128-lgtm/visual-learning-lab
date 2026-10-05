# Day 21 analogy live rejection repair — 2026-10-04

The human-provided `analogy-diagnostics (1).json` establishes the failure at **normalize / ambiguous_mappings**, after one real model response. The model said suitable=true and selected `water_pipe` (fidelity 0.84, misconception risk 0.30). Seven known formal entities, five analogy entities and six mappings survived the earlier checks. Both `map_relation` (ohms_law) and `map_scaling` (parameter_scaling) targeted `pipe_relation`. The old validator required exactly one mapping per analogy entity, so `6 != 5` rejected the entire world. This is evidence from the live response, not a guessed suitability or API failure. A sanitized copy is retained only under tests/fixtures.

Two subsequent inconsistencies are visible in the same trace: resistance declared a formal lab link despite its qualitative mapping; the curve drag named that resistance control even though its entity was the graph rather than the control's mapped obstruction. The relation entity had no primitive. These were previously fatal optional-runtime details; they are now safely omitted or represented by a clearly labeled concept schematic.

## General contract

- Required: exact formal IDs/focus, validated provenance, a defensible selected candidate, known mapping references, unique formal/analogy pairs, coverage of each analogy entity and the build focus, mapping teaching text/fidelity, and explicit limitations. One analogy entity can explain several formal concepts through distinct mappings. Unknown concepts, duplicate pairs, source-page errors and poor fidelity remain fatal.
- Selection: retain the canonical focus when it is among a shape's related mappings; otherwise prefer the build focus, then stable mapping ID. Mapping buttons expose each correspondence directly. No array position or second analogy focus owns semantic identity.
- Derivable: nonnumeric renderer IDs are namespaced deterministically and typed references rewritten; numeric variables and formal IDs retain their strict contracts. Missing safe visuals receive bounded concept discs with generated labels. These discs are a correspondence schematic, not a water/physics fallback.
- Optional: mismatched or missing drag controls are detached. A qualitative formal link is cleared; an otherwise valid quantitative link with inconsistent affine range/default is cleared. Independent controls never patch formal values. Unknown or semantically unrelated quantitative targets remain fatal. Unsupported decorative types are omitted only after their ASTs, numeric projections and workload pass the same safety checks.
- Safety remains fatal: generated markup/code, unsafe expressions, unknown numeric references, cycles, nonfinite/oversized numbers, illegal geometry, excessive arrays/frames/tokens/payload, malformed required fields and invalid references. Nothing is executed from model text. Suitability=false with a nonempty reason remains cached and honest. A static candidate need not have a high interaction score; fidelity, clarity, visualizability and misconception limits are preserved.

Version 1.1 invalidates only analogy caches. Existing analysis, quizzes, reviews, Source Lens/Atlas, lab and formal world state are preserved. The prompt still uses one strict Responses call with bounded stored-language/source/catalog context; it allows empty optional runtime arrays rather than invented low-level detail. The dedicated OpenAI client disables automatic SDK retries. Local selection, sliders, comparison and navigation make no additional requests.

## Diagnostics

Stages distinguish context/client/request/response/normalize/cache/renderer. Controlled reason and schema field path are retained with bounded candidate scores, chosen domain, generated and partially normalized IDs/pages/mappings/bindings, and recovery codes. API messages, prompts, original source bodies, credentials and executable expressions are omitted. Refusal, incomplete output and invalid JSON have separate response codes; selected provider error classifications and HTTP status are allowlisted.

On failure, expand **譬喻開發診斷** and download the sanitized JSON. A successful trace can be inspected with the explicit `analogy_debug=1` query option. Diagnostic and spec caches are separately bounded to four entries. The previous compiler had discarded the old output; the new human download, not process-memory extraction or repeated paid probes, supplied the live evidence.

## Verification and limits

- Focused analogy run: **42 passed**, 15.223 s (`analogy-live-fix-focused.log`).
- Final relevant run: **68 passed**, 42.835 s (`analogy-live-workspace-focused.log`), comprising the same 42 analogy cases and 26 Day 21 workspace cases. No full repository run in this repair.
- Deterministic tests preserve the captured six-to-five mapping structure and subsequent qualitative-link/drag issues. The download omitted expressions, coordinates, teaching prose and page metadata; these fields have explicitly synthetic completions in the regression. This is not a verbatim replay of the original full response or evidence of live visual/source fidelity.
- Tests cover one request/cache reuse, zero local extra calls, canonical focus with reordered mappings, retained formal facts versus generated analogy labels, optional static recovery, unsafe discarded visuals, provenance, honest unsuitability, provider/shape rejection diagnostics and real Streamlit render/navigation paths. Existing three-domain fixed frontend smoke passes in the focused suite.
- Engineering paid calls: **0**. The human performed one diagnostic build and has been asked for a single final live verification after the fix. No random repeat-until-pass requests.
- No new dependencies, copied upstream assets/code, commits, pushes or resets. Existing dirty work and bytecode were preserved.

## Files changed in this repair

`analogy/compiler.py`, `diagnostics.py` (new), `engine.py`, `runtime.py`, `schema.py`, `state.py`, `validator.py`; `i18n.py`; `tests/analogy_fixtures.py`, `test_analogy.py`, `test_analogy_diagnostics.py` (new), `test_analogy_live_bug.py` (new), `fixtures/day21_analogy_live_rejection.json` (new); this document, Day21 evidence/checkpoint/reuse ledger and focused logs. The homepage and app entrypoint were not edited by this repair.

## Exact human retest

```powershell
python -m streamlit run app.py --server.port 8521
```

1. In the existing 8521 session, accept Rerun if a code-update prompt appears. Keep `day21_ohms_law_analogy_test.pdf` and its active analysis; if the session was lost, upload that same PDF and analyze once.
2. Choose 探索 → 譬喻世界 and focus 歐姆定律 V = IR. Press 建立譬喻世界 once. Check the generated correspondence, always-visible limitations and any explicit limited-runtime caption. Do not infer physical equivalence or quantitative synchronization from an independent teaching control.
3. Select each correspondence, change controls and switch 對照/正式模型/來源. Verify canonical focus, unchanged formal values for independent controls, preserved learning state and no new build. If generation still fails, download the **new** diagnostics and stop retrying.

**Status: the observed rejection and its deterministic regressions are fixed; final live PDF generation/render acceptance is awaiting the human retest.** Do not mark the hero accepted using only these offline completions.


## Second live failure: primitive slot contract (2026-10-04)

The second human download establishes **normalize / unsafe_expression / $.primitives[0].radius**, on the rectangle `belt_body`. It selected the conveyor/gate candidate (fidelity 0.82, risk 0.34) and passed the repaired eight-mapping/seven-entity core. The old download did not include the expression value. We therefore cannot assert whether it was blank, a placeholder or unsafe syntax, or claim a verbatim full-response replay. The second sanitized trace is retained only in tests/fixtures/day21_analogy_radius_rejection.json.

The contract unnecessarily required every transport slot to contain mathematics, including a rectangle's non-geometric radius auxiliary. Trusted normalization now supplies finite numeric defaults for blank unused slots and default visibility, and trims harmless surrounding whitespace. If a geometry/value field actually needed by a primitive is blank, the incomplete visual is omitted after safety checks; validated correspondences receive a clearly labeled bounded schematic where necessary. No numeric law is invented and parameter ranges are not shrunk. Nonempty unsafe expressions, unknown symbols, cycles, malformed fields, numeric/geometry violations and workload limits remain fatal, even in discarded visuals. Derived cards also obey the final 24-group/64-object budget. The prompt explains which slots are unused for each primitive.

Diagnostics now include slot lengths, blank flags and hashes, plus controlled empty/syntax/unknown-symbol/unsupported-math/numeric failure detail, primitive type and field use. Numeric evaluation failures retain an exact quantity/primitive field path. Raw expressions, prompts, credentials and original source bodies remain absent from the developer UI and logs.

A schema-valid failed model declaration is retained privately in session memory (at most two declarations, each <=450 KB), never executed or published as a valid spec. The default failure action becomes **本地重驗已保留的譬喻**, which uses the same candidate without initializing OpenAI, reading its API key or making a request. **重新生成譬喻候選** is a separate explicit action. Success removes the pending declaration; a new material/language/model identity clears it. SDK/refusal/invalid JSON/malformed-envelope failures are not replayable candidates. This prevents fixes from requiring another paid model output. The already-downloaded second failure predates retention, so its missing expression cannot be recovered by this mechanism.

Verification for this second repair: initial analogy-focused **54 passed** (18.227 s); the final targeted slot/replay suite **15 passed** (5.868 s); after the final budget guard, all relevant analogy/workspace cases **83 passed** (39.238 s; 57 analogy + 26 workspace, analogy-slots-workspace-focused.log). No full repository suite or engineering paid calls. The reconstructed second structure deliberately uses synthetic blank slots and geometry; these tests do not establish that the missing live radius was blank or that the final real PDF world has rendered.

Files changed in this continuation: analogy/compiler.py, diagnostics.py, engine.py, runtime.py, schema.py, state.py, validator.py; i18n.py; new tests/test_analogy_slots.py and tests/fixtures/day21_analogy_radius_rejection.json; this report, checkpoint/evidence/reuse ledger and focused logs. No new dependency, commit, push, reset or homepage edit.

Retest in the existing 8521 session after Rerun, retaining the same PDF and analysis. Press Build once if no candidate was retained, or use the local-recheck button if one is available. If it fails, preserve the session and share the new diagnostics before requesting another model output. Final live hero acceptance still requires this human confirmation.

## Final contract audit and source cross-check (2026-10-04)

The repasted request contained no new live trace; targeted Downloads inspection found only the two existing failures. A separate native-text check of the actual 127,524-byte, two-page hero PDF verified V=IR, voltage/current/resistance, the closed one-resistor circuit, scaling examples, I–V slope 1/R and Ohmic-model limits. All retained page references in trace (2) agree with those pages. The source explicitly supplies no analogy; water/conveyor descriptions remain generated teaching content. Trace (1) has no page references to audit. This establishes source support only, not full-response replay or analogy rendering/fidelity.

An independent code audit found two related defects, neither established as the observed live cause:

- An omitted invalid affine binding reserved a canonical target and could falsely reject a later valid binding. Only surviving bindings now reserve controls. Tests cover both orders, bad ranges/zero scale/offset, retained mappings, and continued fatal rejection of two surviving links or unrelated semantics.
- Renderer diagnostics appeared before rendering and selected the current focus key rather than the reused build's key. They now appear immediately after an attempted render, including when another mapped concept has canonical focus. A successful local render clears only its prior renderer error. AppTests force both failures and verify safe diagnostics, preserved valid cache and zero further requests.

This continuation changed analogy/validator.py, analogy/runtime.py, tests/test_analogy_slots.py and tests/test_analogy_diagnostics.py, plus documentation and logs. No dependency or homepage change. Targeted runs passed 17 slot/replay/binding tests (9.413 s) and 8 diagnostics tests (6.231 s). Final affected suites passed **87 tests** (72.504 s; 61 analogy + 26 Day21 workspace) in analogy-live-audit-focused.log. No full repository suite, paid API request, commit or push. `git diff --check` passed.

The production port 8521 and old offline demo 8523 were not reachable during this check. Started app.py on 127.0.0.1:8521 (hidden background process, PID 1584), verified the real homepage in the in-app browser, and left that tab for the user. This new browser session has no active analysis. The supported browser file-chooser flow failed to upload the PDF; no model action was clicked. Manually select Downloads/day21_ohms_law_analogy_test.pdf, click 開始理解 once, then 探索 → 譬喻世界 → select 歐姆定律 V = IR → 建立譬喻世界 once. In an existing session with retained analysis, skip upload/analysis; with a retained failed declaration, use 本地重驗已保留的譬喻. Inspect correspondences, controls and always-visible limits; switch 對照/正式模型/來源 without new builds. On failure download the new controlled diagnostics and preserve the session; do not generate repeated candidates. **Real PDF hero acceptance is still pending.**

## Third live trace and human success — 2026-10-04

The new human download, analogy-diagnostics (3).json (23:06), establishes normalize / geometry_bounds / $.primitives after eight mappings and the repaired blank auxiliary defaults. The model chose water_channel with fidelity 0.82 and misconception risk 0.32. Its reason explicitly separates the teaching aid from physical identity. A sanitized copy is retained in tests/fixtures/day21_analogy_geometry_rejection.json. The old trace does not contain wrapping flags, duration, raw expressions or numerical ranges, so it alone cannot identify the precise primitive/coordinate that exceeded the limit.

Code inspection and a deterministic regression established a general projection error: raw token travel was tested against the 100-unit rendered geometry limit before declared wrapping. A safe looping stream could therefore be rejected even though every displayed position lies inside its declared bounded interval. Projection now retains the unchanged 10,000 raw-number limit, applies the existing fixed wrapping operation, then checks actual displayed coordinates against the unchanged 100-unit bound. Radius remains bounded to 20, nonwrapped/other oversized geometry remains fatal, and unsafe expressions, invalid wrap intervals, counts, payload and actual parameter changes still undergo their prior checks. No ranges are shrunk, no source law or topic-specific renderer is added, and nothing is clipped to pass validation.

Geometry failures now identify the exact primitive field and controlled observed min/max, limits, time, token index and check stage. Summaries include only bounded time/count/wrap metadata; developer logs include controlled ranges. Expressions, source bodies, prompts and credentials remain excluded. This is the diagnostic needed to distinguish real oversized geometry from wrapped travel without another model output.

The human then reported: **「ㄟ 終於好了 我就案rerun 可以跑」**. Record the real hero build/render as **accepted by the human after Rerun**. This supersedes the earlier pending status. It is human-observed running behavior, not a recovered full declaration or an agent screenshot of the user's separate session. The agent-visible in-app tab still shows its own unanalysed homepage; no synthetic scene/homepage screenshot is substituted for the live hero. Full analogical fidelity and every interaction were not separately attested in this short report. The observed success is consistent with the projection-order repair; the absent old expression prevents asserting a verbatim reconstruction of the rejected geometry.

Verification: 7 focused geometry regressions passed (0.343 s), then the final affected suites passed **94 tests** (51.890 s; 68 analogy + 26 Day21 workspace; analogy-geometry-workspace-focused.log). These include wrapping array equality at parameter corners, fatal nonwrapped/other bounds, raw-arithmetic/unsafe-code rejection, precise private diagnostics, same-candidate zero-request replay and the existing frontend smoke. No full repository suite or engineering paid requests. `git diff --check` passed.

Files changed in this continuation: analogy/engine.py, analogy/diagnostics.py, analogy/schema.py; new tests/test_analogy_geometry.py and tests/fixtures/day21_analogy_geometry_rejection.json; this report, checkpoint/evidence and focused logs. No dependency, homepage change, commit or push. Run command remains `python -m streamlit run app.py --server.port 8521`. Keep the successful session; local exploration and navigation require no new generation.
