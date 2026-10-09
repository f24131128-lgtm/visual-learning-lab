# Day 25 — Grounded Semantic Twin evidence

2026-10-09, Asia/Taipei. Product question: can an unchanged piece of source material and its interactive representation be demonstrably the same semantic object, while exploration stays separate from source truth?

## Recovery and scope

Verified clean starting tree on `day17-learning-scene-wip`, HEAD/upstream `7b8a30de3515fe127041d617554908cded73aa28`, origin `https://github.com/f24131128-lgtm/visual-learning-lab.git`. Saved Day24 full regression: 409 passed / 212.103s; focused recovery run: 21 passed / 16.022s. Read AGENTS, PRODUCT_VISION, Day23/24 checkpoints/evidence, open-source landscape/ledger/notices, and inspected Atlas, Source Lens, Workspace, learning world, scenes, manipulation, Lab, safe_math and app integration. No commit/push/reset; no personal browser profile.

No new parser, RAG, model schema, equation solver, renderer framework or semantic focus. Homepage and pasted-text flow remain. Source-backed twins are optional; a material without Atlas keeps existing behavior.

## Trusted architecture

```text
validated Source Atlas regions (many)
             ↕ exact existing semantic IDs
existing catalog + formal representations (many)
             ↕ trusted Day24 target/object IDs, validated page overlap
existing manipulation targets (zero, one or several)
             ↕ Day24 safe inverse/release protocol
canonical Spatial World reducer / Numeric Lab values
             ↕ existing projections, charts, metrics and controls
```

`workspace/grounded_twin.py` is an ephemeral derived data contract: semantic ID, source IDs/pages, per-region support/provenance, representation IDs, target IDs, formal parameter IDs, manipulable and a local reason. Exact identifiers were sufficient; another generated relation would repeat already declared semantics. There is **no Twin compiler/request/cache or extra focus owner**. `workspace/twin_ui.py` uses the actual material/PDF hash, stored analysis language, Atlas schema/page/semantic identity and existing canonical owners.

Atlas validation remains the input boundary. The bridge rechecks active material/key, analyzed pages, page envelope, ID/link counts and boxes. It joins only engine-produced targets whose exact semantic identity, object membership and page overlap match. Duplicate target IDs across scoped demos fail closed. Dependency representations link explanations, never confer manipulability. Catalog/world focus remains canonical; region hint and viewport are presentation only. Multiple meanings preserve an already matching focus or require an explicit semantic choice, instead of choosing the first list entry.

Source → select existing semantic focus → highlight exact existing target → Open interactive twin. Drag begin resolves the trusted target → existing focus → source support; release uses the unchanged Day24 inverse and canonical engine. Return to source preserves an explicit supporting region while its semantic identity remains focused. Focus changes resolve the best existing anchor. Source/page navigation pauses existing world playback through existing owners. Learning progress, answers, review, explanations, recordings and cached AI specifications are not replaced by the bridge.

## Source truth and provenance

- PDF bytes, raster, excerpts and bounding boxes are never rewritten by exploration. Browser tests compare the complete source payload including image, regions, page, selection and zoom before/after the roundtrip.
- Inspector shows **compiled baseline / current exploration / delta**. Defaults are model values and explicitly require comparison with the unchanged source; no claim that defaults equal source truth. Existing generated ranges are labeled. Fixed/unsupported quantities acquire no invented handle.
- **Native text geometry** requires same PDF hash plus unique exact whitespace-normalized whole-line text, same page/bbox and a native locator from the existing normalized parser. It verifies geometry provenance, not semantic truth, OCR or source fidelity.
- **Estimated visual region** remains estimated; a generated note cannot upgrade it. **Page-level support** keeps `bbox:null`, resets to the whole page and disables rectangle focus. Low-confidence evidence cannot acquire a rectangle. Original language excerpts remain original.
- A safe inverse is a formal capability, **not proof that the source intended that exploration**. The compact card says so. Real source-to-affordance fidelity remains a separate human question.

## Cross-domain normal-app browser acceptance

Existing Day24 phase/projectile/affine engines, projections and inverses were reused. Fresh isolated headless Edge contexts at 1450×1080 run the normal Streamlit app through `tests/manual_day25.py`, with Responses.create blocked. Actual source iframe clicks and actual pointer drags are used, not synthetic Python event-only acceptance.

| Case | Result after release | Roundtrip / honesty |
|---|---|---|
| Phase / phasor | phase π/2; signal metric 1; existing waveform changes | Exact handle highlights; selected page2 source diagram retains original phase0 orientation, image/boxes/zoom; current values survive reopening Explore |
| Projectile | speed ≈30m/s, angle ≈60°, horizontal velocity15m/s, energy≈450 | Existing trajectory and metrics update; original speed20/45° source stays unchanged; state survives Source/Explore |
| Affine math | gain1, offset≈2; existing second anchor≈4 | Both legitimate affine targets join one semantic entity; unchanged source relation through origin remains separate from current relation |
| Derived wave quantity | page3, formal focus, no Twin CTA or focused target | Page-only region has zero overlay rectangles; other entities' legitimate controls are not removed or misassigned |

All three manipulation cases reject a spoofed target and restore canonical values. Four cases: **zero page errors**, **interaction API delta0**. Results: [app-browser-results.json](day25/app-browser-results.json), [final log](day25-browser-final-all.log). Images: [phase source](day25/phase-source.png), [phase exploration](day25/phase-explore.png), [projectile source](day25/projectile-source.png), [projectile exploration](day25/projectile-explore.png), [math source](day25/math-source.png), [math exploration](day25/math-explore.png), [page-only source](day25/non-manipulable.png). These images were inspected; automated evidence is not human learning validation.

Final visible inspector capture: [phase Workspace](day25/phase-workspace.png), showing compiled0 → current1.5708 and provenance. A screenshot-only phase pass initially omitted Source navigation when reselecting the same sidebar case; its harness setup was corrected and [final capture pass](day25/phase-capture-results.json) passed. The affine fixture module was cached by the running helper after its authored baseline diagram correction; restarted only this task's server, then repeated the affine browser path and visually verified the corrected line through the origin. [Final affine result](day25/math-browser-results.json), `day25-math-fixture-final.log`; current b≈2 and source b0 remain distinct. No production code changed after the full regression.

Browser testing exposed a real Numeric Lab synchronization defect: drag release saved offset2, then a callback from a mounted old slider restored0. Direct Lab commits now increment a presentation control generation; sliders from retired generations cannot overwrite canonical values. A targeted regression exercises both retired and current callbacks. Existing initial widget keys are retained; reset retires generations too. This fix does not replace the Lab store, evaluator or inverse. Ambiguous source selection was also made deliberate; the old Day19 test now explicitly selects its alternate semantic meaning.

Earlier failed harness runs are retained in diagnostic logs: Chinese selector labels, page2 placement, partially mounted React select menus, iframe movement during focus rerun, asynchronous postMessage and stale screen coordinates. Final scripts settle actual layout and finish at live DOM coordinates; coordinate/invariant validators were not loosened. Browser failure is not repaired with another paid call.

## Source viewer measurement and OpenSeadragon gate

Current renderer already shares one SVG viewBox/transform between raster and boxes. Added roughly thirty lines of fixed source-viewer logic: bounded fit zoom1–3, center via actual SVG rectangle and scroll offsets, Focus source region button, page-only full-page fallback, and one bounded sessionStorage presentation record across iframe remounts. No generated frontend code. Selection identity changes focus; identical rerenders preserve viewport. Existing keyboard Enter/Space rectangle selection, list selection, layers, masking and reset remain.

Same isolated fixed viewer fixture was measured before/after. Times below are **single draw measurements**, not repeated medians, end-to-end latency, FPS, network or Streamlit roundtrip timing.

| Overlays | Overlay JSON bytes | Before draw ms / zoom | After draw ms / focused zoom | Scope |
|---|---:|---|---|---|
|20|3,718|3.3 / 1|19.1 / 3|Production-bound count; cold focus/layout work is visible|
|24|4,503|1.9 / 1|2.2 / 3|Per-page production bound|
|60|11,488|2.3 / 1|7.6 / 3|Stress only, above production's24-per-page bound|

Measured missing behavior was region focusing, not slow overlay throughput. Verified centered selected bbox remains inside viewport, zoom survives same-selection rerender, boxes align after resize to620px, page switch and null-bbox fallback, keyboard click and zero browser errors. [Before](day25/viewer-before.json), [after](day25/viewer-after.json), reproducible `tests/day25_viewer_browser.cjs` (baseline obtained before edit). No latency improvement claimed. Pan uses scrollbars and zoom is bounded; pinch/kinetic zoom/high-DPI tile parity with OpenSeadragon is not claimed.

[OpenSeadragon6.1.1](https://github.com/openseadragon/openseadragon/releases/tag/v6.1.1), tagged BSD-3-Clause, [Viewport](https://openseadragon.github.io/docs/OpenSeadragon.Viewport.html) and [overlays](https://openseadragon.github.io/examples/ui-overlays/) reviewed. **LEARN FROM / DEFER integration**: fitBounds and coordinate APIs are relevant, but current bounded rasters do not need IIIF/tiles. Integration adds vendor/control assets, conversions and lifecycle. No OSD implementation or installed A/B benchmark; no superiority claim. The small current fix closes the measured acceptance gap.

## OSS and 3D decisions

Details and primary-source license links: [reuse ledger](OPEN_SOURCE_REUSE_LEDGER.md). No copied upstream implementation, weights, textures, assets or new packages. THIRD_PARTY_NOTICES and vendored hashes remain unchanged.

| Actually used existing runtime | Exact tested version / scope | License boundary |
|---|---|---|
|JSXGraph|1.13.3 pinned core JS/CSS|MIT chosen dual-license option; hash manifest and embedded notices unchanged|
|Plotly|Python6.9.0 and its existing bundled browser library|MIT core; no new bundle or CDN|
|pdfplumber|0.11.10 optional native-text public API|MIT; missing package gracefully leaves estimated geometry|
|PyMuPDF|1.26.7 existing raster/native fixture path|AGPL/commercial obligations remain unresolved deployment review|
|pypdf|6.19.0 existing extraction|BSD-3-Clause; unchanged dependency|
|Streamlit / OpenAI SDK|1.64.0 /1.109.1 installed|Apache-2.0; unchanged dependencies|

Three.js **r186**, core MIT, Raycaster/OrbitControls/DragControls/TransformControls reviewed. Plain offline ES modules are feasible, but controls don't establish a semantic inverse. A trusted object-token registry, bounded GPU lifecycle/disposal and source-backed acceptance would still be required. Cleanup tutorial retrieval was unavailable; no deep disposal/performance audit claimed. **DEFER**: no new3D shipped. Brief alternatives: MathBox coreMIT, Babylon.js coreApache-2.0, React Three Fiber coreMIT; no exact package selected, installed, transitive audit or recency claim for those alternatives. New3D does not resolve today's unmeasured source fidelity.

## PDF and model evidence

Repository fixture inspection found project-owned engineering PDFs, not a legally supplied representative user教材 corpus. Used independently authored **three-page PDFs with unequal sizes**, actual embedded native text, diagram/formula/page-only evidence. They exercise extraction/raster/Atlas/normal-app routing; they are **synthetic engineering fixtures**, not real-world textbook validation. The affine diagram was corrected to match its authored b0 formula; production logic does not contain fixtures. Originals are generated reproducibly by `tests/twin_fixtures.py`; no copyrighted textbook download.

After deterministic desktop acceptance, one paid probe used the existing Source Atlas compiler with three source images, bounded text and existing deterministic phase-world semantics. Model **gpt-5.6-luna**, **1 paid attempt / ceiling18**, SDK retries0, input**9,118**, output**2,407**, total**11,525 tokens**. Stage: existing Atlas visual grounding. Not necessary for the derived bridge; useful as one fresh model grounding observation. Persisted attempt before call; probe refuses another paid attempt when record exists. [Attempt/usage](day25/model/attempt.json), [normalized output](day25/model/normalized-atlas.json), [result](day25/model/result.json).

Fourteen regions accepted, zero dropped; source semantic IDs angle/phase/wave join existing catalog; only angle joins an existing validated target. The model did not create a Twin declaration or execution code. Free replay/derivation adds0 calls. This is **one synthetic source observation with an existing deterministic world**, not end-to-end live world-generation acceptance or human fidelity validation. No claim of measured API cost in dollars. Final browser/AppTest interactions block calls; compiler caches and explicit Explain/new-generation actions are unchanged.

## Security, locality and accessibility

Day25 tests cover reordered IDs, one-to-many sources, multiple valid targets, unknown region/semantic/representation, stale material/key, wrong pages, bounded regions/links, invalid/outside/NaN/Infinity/huge/bool boxes, low-confidence pretending exact, ambiguous selection, cross-PDF native provenance, duplicate scoped targets, fixed parameters, immutable source/current comparison and optional viewer failure. Existing Day24 tests retain spoofed target, wrong scene/material, revision/duplicate token, unsupported gesture, range/coordinate/malicious-expression and atomic rejection protections. Model expressions still use safe_math; no eval/exec, calls or generated HTML/JS are introduced.

Normal-PDF AppTest covers source selection → existing focus → direct commit → Source persistence for all3 engines, no client calls, derived page-only honesty and source frontend failure list fallback. Native preview selection remains local without semantic focus. Source list, semantic selector, parameter sliders, existing time controls and formal/inspector remain available. Source zoom/navigation/replay/reset are existing local actions; bridge code makes no compiler calls. Actual browser drag verifies behavior AppTest cannot prove. Original queues/quizzes/learning-state regression is included in the complete suite.

Mobile quick check: isolated Edge mobile/touch emulation, **390×844**, real CDP touch events, source tap, phase endpoint release(0,1), external scroll available and zero page errors. [Touch result](day25/touch-results.json). Fixed component numeric payload only; not a Python canonical mobile integration test or physical phone. Handle width**18 CSS px** is usable in this bounded emulator but small; touch ergonomics/accessibility certification remain pending. No mobile redesign or gesture-parity claim.

## Local performance

31 hot repetitions on original fixtures, medians in milliseconds. Source-click timing resets focus before every sample and includes the existing canonical reducer; an earlier already-selected timing was corrected. No network, frame construction, browser layout or process RSS included. [Measurements](day25/performance.json), script `tests/day25_performance.py`.

|Case|Derived joins ms|Source click→focus ms|Focus→region ms|Navigate ms|Link JSON bytes / targets|
|---|---:|---:|---:|---:|---|
|Phase|0.0977|1.0656|0.0088|0.0049|964 /1|
|Projectile|0.0544|6.3177|0.0060|0.0034|935 /1|
|Affine|0.0587|0.0089|0.0065|0.0039|1,006 /2|

Day24 formal commit engines were reused; those old commit performance measurements are in `day24/performance.json`, not relabeled new benchmarks. Day25 added no second physics/evaluation/recording pipeline. Original source raster payload remains dominant; no fabricated FPS, latency distribution or memory benchmark.

## Automated test record and generality audit

|Run|Result|Evidence|
|---|---|---|
|Recovered Day24 focused|21 passed /16.022s|Recovery terminal output|
|Final focused Day24+Day25|40 passed /19.404s|`day25-focused-final-core.log`|
|Affected Day20/21/23/24|124 passed /72.009s|`day25-affected-regression.log`; before final slider generation fix|
|Source Atlas/Day19|30 passed /13.313s|`day25-source-final.log`|
|Final complete suite, run exactly once|**428 passed /226.441s**, no failures/skips|`day25-regression.log`; final production code|
|Final normal desktop browser|4 cases,0 page errors|`day25/app-browser-results.json`|
|Touch component|Tap/drag/scroll pass,0 page errors|`day25/touch-results.json`|

Generic new production files were searched for phase/phasor/projectile/velocity/linear/affine/sinusoid/orbit/Ohm/queue and eval/exec calls: **no matches**. Routing is exact semantic IDs, capabilities and validated targets. Domain terms remain only in tests/fixtures and existing specialized engines. No test examples in production. Git diff of requirements, notices and pinned JSXGraph assets is empty.

## Known limitations and Day26 recommendation

Exact IDs/page overlap establish a trusted app relation, not philosophical or source-fidelity proof. A generated world can still misunderstand a source. Native line geometry does not verify formula meaning; estimated visual boxes remain approximate. Compiled defaults are explicitly unverified source values. No universal solver or handle for unsupported structures. Page-only evidence is honest but less spatially precise. Current viewer uses bounded scroll zoom, not OSD tile/touch feature parity. SessionStorage contains one presentation record only; semantic state remains Python-owned. Browser animation and model correctness require separate evaluation. Human教材 fidelity, real mobile ergonomics and learning outcomes are not established by these fixtures.

**Day26 recommendation:** a small legally supplied real-PDF holdout with human source-to-affordance labels. Evaluate whether source supports the declared parameter/range, geometry tier and inverse; include fixed/derived/ambiguous examples, measure wrong affordance rate and roundtrip usability. Preserve the current engines. Use this evidence to decide viewport investment or a source-grounded3D case, rather than adding another renderer first.

## Exactly three human acceptance tests

Offline setup: `python -X utf8 -B -m streamlit run tests/manual_day25.py --server.port 8528`, open localhost8528. Model actions are blocked in this harness. Each test asks for **one screenshot**, no developer diagnostics unless it fails.

1. **Source → Twin → Source.** Choose sidebar **A 相位與波形** → source page**2** → select **Source diagram** → **開啟互動分身** → drag the highlighted phasor endpoint to the top of the circle → **回到支持此概念的來源**. Expect current phase≈1.5708/signal1; original horizontal phasor diagram, source selection and viewport stay unchanged. Capture the Twin value card plus selected source. Interaction API delta**0**.
2. **Source truth, with one real user PDF.** In the normal app (`python -m streamlit run app.py`), upload one legally owned text PDF that explicitly defines adjustable phase, or launch speed/angle. Click **開始理解**, then the available **建立空間學習場景** and **建立來源互動圖譜**; these are explicit paid preparation actions. Select its source formula/diagram → **開啟互動分身**, move one supported parameter away from its initial value → return to source. Expect the original literal formula/value unchanged beside a different **編譯初始值／目前探索值／差值**; verify that source actually supports the parameter/range. Take one screenshot of both. After preparation, interaction API delta**0**. If the material is unsuitable or no validated handle exists, honest formal-only fallback is correct; mark real-PDF fidelity pending rather than forcing a handle. This is the single live user-PDF check, not an additional fourth test.
3. **Grounded but non-manipulable.** Return to offline **A 相位與波形**, source page**3**, select **Derived source quantity**. Expect **來源 ↔ 正式表示** for the wave quantity, a clear no-direct-manipulation reason, no **開啟互動分身** button and no invented source rectangle. Capture the formal-only card and unchanged page. Existing controls elsewhere remain available; interaction API delta**0**.

## Changed files and running the app

Production: new `workspace/{grounded_twin,twin_ui}.py`; integrations in `workspace/ui.py`, `app.py`, `i18n.py`, `source_atlas/{state,runtime}.py` and frontend, `manipulation/{lab,runtime}.py` and frontend, `interactive_lab.py`. Tests/helpers: `tests/{test_day25,twin_fixtures,manual_day25,day25_model_probe,day25_performance}.py`, `day25_{app,viewer,touch}_browser.cjs`; adjusted `test_day19.py` and `atlas_frontend_smoke.cjs`. Docs: checkpoint, evidence, reuse ledger, AGENTS and Day25 logs/JSON/screenshots. No new dependencies, pinned asset modifications or notices changes.

Run production: **`python -m streamlit run app.py`**. Focused: `python -X utf8 -B -m unittest discover -s tests -p test_day25.py -q`. Full suite command: `python -X utf8 -B -m unittest discover -s tests -q`; its one final run is recorded above. Local installed Python used here is `C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe`. Browser scripts use existing bundled Playwright/isolated Edge, no runtime dependency addition. Paid probe free replay: `python -X utf8 -B tests/day25_model_probe.py` (omit `--live`).
