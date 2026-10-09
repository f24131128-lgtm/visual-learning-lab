# Product experience redesign — 2026-10-09

**Completed for review; uncommitted and unpushed.** No new model calls, schemas, dependencies or third-party assets. One full regression ran 431 tests: 429 passed; two obsolete Day-badge expectations were corrected and both passed targeted reruns. Browser, keyboard, touch and responsive evidence is below. Real-document fidelity and real-phone ergonomics remain human-review limits.

## Recovery and design plan (before implementation)

Verified clean `day17-learning-scene-wip`, HEAD `c280882`, with the previous two commits `7b8a30d`, `b6b39c5`. No commit or push. Read AGENTS, PRODUCT_VISION, Day24/25 evidence/checkpoint and the existing presentation, workspace, source, world, manipulation and lab render paths.

Original problems: large repeated input/marketing section above every mode; narrow 1040px workspace; source and its Twin separated vertically; purple accent competing with scientific encodings; dark source iframe disconnected from the page; controls preceding manipulation; large bordered sections; release reconstructs JSXGraph boards, risking focus loss. Existing semantic reducers, source provenance, accessible selectors and explicit build actions are retained.

| Reference (primary sources inspected today) | Learn | Deliberately do not copy | Decision / license scope |
|---|---|---|---|
| [Linear](https://linear.app/now/how-we-redesigned-the-linear-ui), [current interface](https://linear.app/) | Quiet navigation, aligned headers, density through hierarchy | Project management chrome, proprietary assets, AI marketing | LEARN; no code/assets copied |
| [Raycast](https://www.raycast.com/) | One obvious action, secondary actions close to context, keyboard equivalence | Launcher metaphor, dramatic marketing surfaces | LEARN; no code/assets copied |
| [Brilliant](https://brilliant.org/) | Concept immediately beside an interaction | Gamification, illustrations or proprietary lessons | LEARN; public landing/interface examples only, no authenticated lesson claim |
| [shadcn/ui buttons](https://ui.shadcn.com/docs/components/base/button) | Primary/secondary/quiet actions and visible focus | React migration, card-per-section examples | LEARN; [repository license](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md), MIT; no dependency |
| [Radix Themes](https://www.radix-ui.com/themes/docs/theme/overview) | Semantic color roles, compact type/radius scale | Theme provider/component infrastructure | LEARN; [themes LICENSE](https://github.com/radix-ui/themes/blob/main/LICENSE), MIT; no dependency |
| [Mantine](https://mantine.dev/) | Consistent control states and responsive density | Large component library for cosmetic changes | LEARN; [LICENSE](https://github.com/mantinedev/mantine/blob/master/LICENSE), MIT; no dependency |
| [Open Props](https://open-props.style/) | Small explicit token scales for spacing, radius and motion | Bulk token import or decorative animation | LEARN; [LICENSE](https://github.com/argyleink/open-props/blob/main/LICENSE), MIT; independently authored values |
| [Spectrum](https://spectrum.adobe.com/), [Web Components](https://opensource.adobe.com/spectrum-web-components/) | Professional tool hierarchy, clear control states and access | Framework integration, Adobe icons/assets | LEARN; [Web Components LICENSE](https://github.com/adobe/spectrum-web-components/blob/main/LICENSE), Apache-2.0; no dependency |

These are current primary documentation/reference pages, not assertions that every branded asset is covered by its code license. No upstream code, theme files, fonts or icons are imported. Existing offline JSXGraph 1.13.3 MIT and Plotly assets stay unchanged; existing PyMuPDF licensing review remains unresolved.

Design language: warm paper, graphite text, restrained deep teal for actions. Evidence uses a separate muted ochre role. Scientific curves retain distinct encodings. Crisp 4/8px radii, quiet rules instead of enclosing every section.

App shell: slim name/language header; input is central on home and a collapsed change-material disclosure after analysis. Keep Learn / Source / Explore / Practice and the existing state callbacks. No fifth navigation system.

Source: large original document with compact page/object toolbar. Desktop 72/28 stage/context rail. Put selected object, provenance, linked meaning and Twin beside evidence; keep uncertain grounding explicit. Narrow screens stack in source-first order.

Explore: large manipulation board with subordinate waveform and tabular readouts. Put keyboard parameters/time after the stage, with playback/comparison, recording and camera as closed independent disclosures. Context rail follows the shared focus. Sliders remain accessible and canonical.

Motion: 120ms color/border changes, 180ms optional opacity. No dimension animation, decorative effects or source-image animation. Reduced-motion disables transitions. Local hover/drag preview remains browser-owned; focus/release retain the existing validation contract. Attempt same-identity board updates only when representation structure matches; otherwise safely rebuild.

Tokens: one owned presentation layer with semantic colors, 4–48px spacing, 1440px workspace/880px home widths, 4/8px radii, minimal shadows, type scale, 36/44px controls, focus ring, easing and z-index roles. Frontend iframe styles receive the same static token definitions from Python, without introducing a second semantic store.

Removed from default view: future-feature marketing grid, Day counter, full input after analysis, technical provenance repetition, keyboard/recording/camera tooling above the main object. No learning capability removed.

## Evidence and final results

Baseline/browser tests use isolated headless Edge contexts, original synthetic PDFs and the normal app with the paid SDK blocked. Production home runs separately on port 8530.

### Delivered composition

Home centers PDF/pasted-text input and one primary action, with a small product mark and one-line purpose. After analysis, the same input widgets remain mounted inside **Change material**; language and input state survive view changes. The future-feature grid, day badge, purple decoration and repeated marketing copy are gone. Existing analysis/loading stages remain honest spinners; no fake progress, added request or invented execution stage.

Source uses a 2.6:1 document/context layout (72/28 before the gap). Page/object selectors form one toolbar; zoom/reset/focus remain close to the page, with layers/label controls in a local disclosure. The unchanged PDF dominates. Ochre outlines and dashed medium-confidence regions distinguish evidence; low-confidence/page-only semantics are unchanged. Source preparation and related-learning controls remain accessible but recede. The rail contains current focus, Source ↔ Live Twin, support provenance, labeled compiled baseline/current/delta and the primary open-twin action. Compiled values are explicitly model values, never asserted to be source facts. Labels/units in fixed table markup are escaped.

Explore puts the manipulation board first, with a subordinate waveform/path and compact tabular readouts. Representation planning, keyboard parameters/time, playback/comparison, recording and camera remain available via closed disclosures. Numeric Lab now puts its direct board before parameter controls; its original chart/default comparison remains accessible and expands when comparison is enabled. Unsupported direct manipulation retains the original chart/formal controls. Scientific curve palettes are preserved except the direct primary object adopts the product's exploration accent; no physics/color-dependent semantics changed.

### Token and motion system

`presentation.py` owns semantic roles and static iframe tokens: page `#f8f9f6`, surface white, subtle `#eff2ee`, foreground `#26332e`, muted `#59675f`, faint `#647168`, accent/exploration `#216653`, accent-subtle `#e4efe9`, evidence `#85642c`, warning `#91601b`, error `#ae3c37`, border `#d9dfd9`, focus `#26745f`. Spacing 4/8/12/16/24/32/48px; workspace 1440px, home 880px; radii 4/8px; restrained shadows; type 12/14/16/24/32px; controls 36px / touch 44px; 120/180ms easing and three z-index roles. `PLOT_STYLE` keeps chart axes/grid/foreground consistent. `.streamlit/config.toml` aligns native controls with this primary light theme.

Only fast color/background/border transitions are used. No layout-dimension animation, source-image animation, decorative motion or new animation package. `prefers-reduced-motion` removes transitions; browser verification returned `0s`. Source zoom/pan/filtering stays local. The source viewer preserves keyboard region focus when rebuilding overlays; it uses scroll-based pan, not scroll interception.

### Interaction and rerun changes

- Same-identity, structurally identical numeric updates restore the existing JSXGraph board. The structure guard includes parameters, inverse coefficients, target bounds, objects, curves, metrics and labels. A changed structure safely remounts; this is not a universal zero-remount claim.
- Restore replaces authoritative numeric values and clears pending/disabled presentation state, including rejected releases. Existing material/revision/token gates and Python inverse validation are unchanged. No second canonical store or expression execution was added.
- Drag preview remains browser-local; existing focus begin and release are the two semantic events. Duplicate frame-height messages are suppressed. Escape/pointer cancellation remains cancelled through subsequent movement until a new gesture.
- Small 14px visible markers use JSXGraph's existing 20px mouse / 22px touch precision radius. Real touch beginning **18 CSS px from the marker center** successfully grabbed and released the upper endpoint. This verifies a useful invisible target, not a certified device-independent 44px square.
- Hover/focus/drag/busy/invalid states have distinct cursor/outline/opacity/status treatment. Touch and mouse events now share the existing live DOM coordinate conversion. No inverse math or native library assets changed.

### Browser and performance evidence

All browser runs used new isolated headless Edge profiles. The offline harness seeds original synthetic PDFs into normal `app.py` and blocks paid SDK requests. This tests app behavior, not real-document grounding accuracy.

| Evidence | Observed result | File |
|---|---|---|
| Source → Twin → actual drag → Source | Phase → π/2/signal 1; projectile → ~30m/s, ~60°, vx 15; affine offset → ~2. Values survive navigation; PDF raster/boxes/page/selection/viewport unchanged. Forged release restores canonical values. | `ui-redesign/app-browser-results.json`, `acceptance.log` |
| Unsupported derived source | Page-only support; zero invented rectangles or direct handles; formal view still works. | Same browser report |
| Same-scene phase board | Before: 1 rebuild on release. After: 0; same board object retained. Two render messages in both. | `before-browser.json`, `final-browser.json` |
| Payload | 75,607 → 76,531 serialized JSON **characters**, +924 static token characters (~1.2%). The historic JSON field is called `bytes`, but this measurement is string length, not wire bytes. | Same reports |
| Real page scrolling during drag | `stMain.scrollTop` **180 → 180**. Iframe rectangle stays x340/y289.15625/w733.546875/h501. No layout-shift entries during this single observed gesture. | `final-browser.json` |
| Responsive | 1440 desktop; 1280, 768, 390, 430 checks. Source and Explore have no measured main-container horizontal overflow; direct iframe has no body overflow. At ≤900px the stage and rail stack. | `final-browser.json`, `final-*-{width}.png` |
| Touch | Source tap, offset grab/release, outer scrolling available, zero page errors. | `touch-results.json` |
| Keyboard | Native radio ArrowRight changes Source → Explore; source Enter selection retains region focus; focused handle ArrowUp commits phase ~0.046695 and retains its accessible name. | `final-browser.json`, `accessibility.json` |
| Appearance/motion | Dark OS preference retains the deliberate light product theme; readable computed foreground/background. Reduced-motion transition 0s; zero page errors. | `accessibility.json`, `final-explore-dark-os.png` |

This is targeted observation, not FPS/latency certification. No 60FPS claim. The first draft measured the wrong scroll container; only `final-browser.json`'s corrected `stMain` measurement is used above. Initial browser retries exposed stale imported modules in the runpy harness and one navigation-test race; test servers were restarted and the final runs completed. Production is still Streamlit: slow callbacks can show its normal pending treatment, and inverse/structure changes can safely recreate a board.

### Screenshots actually inspected

Desktop viewport is 1440×1000; smaller screenshots are 900px high. Source uses page 2 / Source diagram; Explore uses the same scene. Early baseline framing reflects the old long scroll stack, so these are visual comparisons, not pixel-diff goldens. The sidebar in result screenshots is test-only fixture selection, not production navigation.

| Screen | Before | After |
|---|---|---|
| Homepage | [before-home.png](ui-redesign/before-home.png) | [final-home.png](ui-redesign/final-home.png) |
| Source / Grounded Twin | [before-source.png](ui-redesign/before-source.png) | [final-source.png](ui-redesign/final-source.png) |
| Explore / Direct Manipulation | [before-explore.png](ui-redesign/before-explore.png) | [final-explore.png](ui-redesign/final-explore.png) |

Also inspected `final-source-768.png`, `final-source-390.png`, `final-explore-390.png`, and `final-explore-dark-os.png`. Additional same-fixture source/board screenshots for phase, projectile and math are retained. The screenshots capture Streamlit's viewport; they do not flatten all content inside its scroll container into one image.

### Accessibility and limits

Native labeled widgets, four-mode radio keyboard navigation, source object list, keyboard parameters/time, Graphviz/chart fallbacks and source extraction fallback remain. Selected state uses an underline/outline plus text, not color alone. No hover-only essential action. Static token contrast calculations: main text ~12.46:1, muted text ~5.63:1 and primary white-on-teal ~6.80:1; the faint footer token was darkened after review. These token calculations and tested focus paths are not a full WCAG audit or a screen-reader certification.

Remaining design debt: advanced tool disclosures can still be lengthy for complex scenes; real-phone ergonomics and real-material source fidelity require human review; this sprint prioritizes one light theme, not a complete dark palette; Streamlit's top utility chrome remains; Source uses existing scroll zoom, without pinch/kinetic-viewer parity. Broader performance distributions, contrast of every third-party chart element and all browser/device combinations are not established.

### Tests and files

- First affected run: **182 tests**, one stale Day badge assertion after intentional homepage removal. Updated only that presentational expectation to the product name.
- Corrected focused run: **77 passed / 31.078s**, including UI/input/language preservation, escaped readout markup, Day24 numeric/restore/cancel smoke, Source Atlas and world integration. Earlier Day25 focused run: **19 passed / 14.085s**.
- One full regression: **431 tests / 242.092s — 429 passed, 2 obsolete Day-badge expectations failed** (`full-regression.log`). Those two assertions in Day17/18 now check the product name, retaining all CTA/request-count/render behavior checks. **Both passed targeted reruns / 4.106s** (`full-regression-corrections.log`). No second full run, as requested. This is not represented as a single all-green 431-test run. A final faint-footer contrast adjustment changed only a CSS color token; its contrast was checked separately.
- Final browser acceptance: four cases (three manipulable plus page-only), zero page errors, zero interaction API delta. Touch, keyboard and reduced-motion checks also pass. `git diff --check` has no whitespace errors.

Production changed: `.streamlit/config.toml`, `presentation.py`, `i18n.py`, `app.py`, `interactive_lab.py`, `workspace/{ui,twin_ui}.py`, `source_atlas/{compiler,runtime}.py` and frontend, `scene/compiler.py`, `scene/world/runtime.py` and frontend, `manipulation/runtime.py` and frontend adapter/index. No schema, prompt, semantic reducer or inverse/evaluator module changed. Vendor files, requirements and THIRD_PARTY_NOTICES remain unchanged. No new dependencies or assets; the CSS mark is original.

Tests/evidence: `test_ui_redesign.py`, adapted `test_day17.py`/`test_day18.py`/`test_day19.py`/`test_day25.py` presentational assertions and existing frontend smoke; `manual_ui_redesign.py`, `ui_redesign_{browser,acceptance,accessibility,touch}.cjs`, `ui_layout_probe.cjs`, this checkpoint, reuse ledger and `docs/ui-redesign/` reports/screenshots. The quota pause at 4% remaining was saved; user explicitly resumed after quota reset. Incidental old Day25 log/trace output was restored; intended evidence is under `docs/ui-redesign/`. No commit or push.

Run production: `python -m streamlit run app.py`.

Offline review harness: `python -X utf8 -B -m streamlit run tests/manual_ui_redesign.py --server.port 8531`.

Full suite: `python -X utf8 -B -m unittest discover -s tests -q`.

Browser scripts use the existing bundled Playwright via `NODE_PATH=C:\Users\88690\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\node_modules`. Installed project Python was `C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe`. Windows runtime/Edge launches required reviewed sandbox escalation. Test servers 8530/8531 belong to this chat; the existing server on 8528 was left running.

### Exactly three human review screens

1. **HOMEPAGE** — open [production preview](http://localhost:8530). Check the PDF/pasted-text input and one primary action; switch language. No model call occurs unless you explicitly click Visualize with material.
2. **SOURCE / GROUNDED TWIN** — open [offline preview](http://localhost:8531), choose **A 相位與波形**, Source page **2**, source object **Source diagram**. Review the original source beside its Twin relationship and compiled/current/delta readout. This harness blocks paid calls.
3. **EXPLORE / DIRECT MANIPULATION** — from that Source screen, click **開啟互動分身**, drag the endpoint to the top, then **回到支持此概念的來源**. Review the large board, linked waveform/readouts, retained exploration and unchanged source. No developer logs required.

