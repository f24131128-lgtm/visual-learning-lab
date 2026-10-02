# Day 19 — Visual Source Decompiler / Source-to-Scene Semantic Atlas

Implementation: 2026-10-01. Human acceptance on real PDFs is pending.
No commit/push, homepage redesign, OCR, quiz changes or Day 18 reset/revert.
Existing dirty Day 18 work and tracked bytecode were preserved.

## Architecture and reuse

`normal app.py PDF result → scene/compiler.py optional atlas build →
source_atlas/compiler.py → strict region DATA → model.normalize_atlas →
canonical focus adapter → original-page viewer | existing scene runtime`.

- `source_lens.get_page_render` is unchanged: the original PDF stays in active
  session memory, rasters are bounded/cached, crop/rotation and individual page
  aspect ratios remain authoritative. Coordinates normalize against each full
  displayed raster, never inferred from extraction order.
- Day 6 `visual_evidence` ranks pages, alongside scene source pages, current focus
  and concept references. Learners explicitly choose at most three analyzed
  pages; processed pages stay visible. Ordinary analysis/reruns make no request.
- Day 18 quantity/parameter/time IDs and validated equation DAG are reused.
  Representation links follow forward bindings and their dependencies, not
  copied physics or formulas recomputed by another renderer. Source focus uses
  `world.state.apply_patch(set_focus)`, preserving time/parameters/baseline and
  other learning state; recording follows existing reducer semantics.
- Day 17 event/outcome/focus IDs reuse canonical expressions and existing
  selectors. Source-linked events beyond the first set-operation pair now have
  accessible event controls too; probability mathematics/runtime are unchanged.
- Source `region_hint`, manual page, zoom and filters are navigation/presentation
  only, not another semantic focus. World focus overrides old hints and chooses
  the best grounded region/page. Source selection may disambiguate multiple
  regions for the same focus. Reliability wins first; useful vector/formula
  regions precede labels at equal confidence.
- Fixed SVG viewer overlays the ORIGINAL PDF raster. It does not regenerate the
  source. Numeric boxes and textContent are the only model-derived rendering
  inputs; no model HTML/SVG/JS/Python executes. Keyboard source list and SVG
  Enter/Space access remain usable alongside clicks.
- Formula Trace displays original/estimated source text separately, walks the
  existing safe quantity DAG to parameters/quantities and displays driven view
  categories. It does **not** parse or execute the PDF's formula string. The
  internal evidence graph explicitly maps semantic IDs ↔ regions ↔ pages ↔
  representation IDs. Compact source chips trace multiple pages.

## Fully implemented

Versioned strict Source Atlas schema; explicit normal-PDF build CTA; selected-page
image compiler; optional-region validation; bounded session cache; side-by-side
source/world layout; canonical bidirectional focus and page navigation; compact
Formula Trace and concept-source trace; zoom/scroll; diagram layers (structure,
labels, vectors, formulas, relationships); relevant-focus isolation; reset;
local high-confidence label masks with click-to-reveal; cached-world contextual
open; Chinese/English chrome; internal field diagnostics without debug UI.

Limits: three pages, 64 regions total, 24/page, eight semantic/related links per
region, 256 related edges, minimum box width/height .005 and area .0001,
160-character labels, 400-character notes, 600-character excerpts, four cached
atlases, 8 MiB input raster bytes, 24,000 context characters and 150,000 response
characters. Unknown IDs/pages, nonfinite/out-of-range/inverted/tiny boxes,
unsupported types/tiers/layers, markup and bad refs do not reach overlays.
Parent cycles are dropped; dangling surviving optional links are removed.
Duplicates/global overflow/malformed envelopes reject the atlas only.

## Fallback and uncertainty

Hardest grounding problem: bounding-box validity is **not semantic/visual proof**.
A legal box can still surround the wrong arrow. Model confidence is an estimate,
not calibrated evidence. High boxes still require original-page verification;
medium boxes are dotted and may be broad. Low confidence preserves a page-only
anchor and draws no box. Missing visual anchors retain existing Source Lens
page-level links. Bad optional regions drop independently and are diagnosed
internally; an empty safe atlas retains page context.

Native-text excerpts are called verified only when the supplied excerpt occurs
in extracted text (whitespace normalized). Other visual transcriptions are
explicitly labeled estimated; this does not prove any region's bbox is exact.
The messy fixture has ambiguous drawn marks and a low-confidence anchor, **not
an actual human handwritten page**. Human messy-page acceptance is outstanding.

On viewer/component failure, local source selection remains and an available
original raster is shown; PDF render failure retains existing Source Lens/text
paths. Atlas compilation/rejection never removes a scene, analysis, lesson,
quiz, review or lab/simulation.

The external source pane uses the **committed** Day 18 state. Pause continuous
world playback before source navigation, as the small UI caption says. This is
not claimed to capture the browser's uncommitted per-frame time across iframes.

## Not implemented / not claimed

No generic OCR, source-image regeneration, arbitrary formula parsing, automatic
scene compilation from any isolated region, annotation editing/export, durable
cross-session atlas storage, source-grounded 3D reconstruction or general layout
reconstruction. A region without a cached scene can be inspected but cannot
magically create an interactive physics model. No guarantee of pixel-perfect or
correct real-model grounding. No paid API call was sent during this pass.

## API and cache strategy

One explicit uncached atlas build sends selected original page images (not the
whole PDF), their text, bounded existing analysis and exact semantic IDs to the
repository's existing model. `max_retries=0` prevents automatic SDK retries.
Selection/page/filter/zoom/label/trace/scene-open actions are local (zero calls).
Keys include material ID, SHA256 PDF identity, stored analysis language, atlas
v1.0, sorted selected pages and complete scene/catalog fingerprint. Local values,
time, focus, zoom and filters are excluded. Changed scene equations/bindings/IDs
require an explicit new grounding build. Rejected entries are `None` and never
valid atlases; transient transport failures permit an explicit retry. Rejection
does not automatically spend another request on the same identity.

OpenAI Docs skill informed the strict wire schema and bounded image input:
[Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs),
[Images and vision](https://developers.openai.com/api/docs/guides/images-vision).
PDF skill informed original-raster and coordinate verification; no PDF editing
or new rendering dependency was needed. Computer Use verified actual iframe
interaction separately from AppTest and fixed-code frontend smoke.

## Real implementation findings

- Initial focused run: 28 tests, one error and one failure. The cache test tried
  clicking an already-disabled button, which a real browser cannot do. Corrected
  it to verify disabled state plus ordinary reruns. Separately, rejection state
  was saved after the build widget rendered, leaving its current visible state
  enabled until another rerun. Completion/rejection now reruns immediately and
  the request handler also checks `attempted`, preventing stale-button requests.
- Browser review showed formula traces repeated representation labels and left
  the static Parameters label untranslated. Replaced duplicate labels with
  compact driven-view categories and localized Parameters/canonical time.
- Review found source-only inspection could lose a linked region when no world
  existed; the hint now remains inspectable without creating a semantic focus.
  Added a regression. Also covered third-event source focus for probability.
- The offline server retained imported Python modules during browser-only reload
  after edits. Restarted **our own** port-8521 process and rechecked final labels;
  the user's app processes were not stopped.

## Automated tests

Final focused command:

```powershell
python -B -m unittest discover -s tests -p 'test_day19*.py' -q
```

**30 passed, 7.054 seconds, no skips.** Previous necessary focused run after the
first fix: 28 passed, 6.480 seconds. Counts are unique tests, not cumulative runs.

Coverage includes strict schema, finite/normalized/tiny boxes, impossible pages,
global/per-page bounds, IDs/types/text/injected markup, parent cycles/broken refs,
low-confidence no-box behavior, excerpt honesty, region→canonical focus,
focus→best region/page, evidence graph, multi-page/formula trace, source-only
inspection, cache/local-state identity and rejected cache behavior, bounded
selected-image request shape/count, stale/duplicate/cross-scene events, phasor
and projectile linkage, Day 17 events/outcomes/third event, unequal rotated and
cropped PDF rasters, local frontend zoom/layers/masks/reveal/keyboard/protocol.

Normal `app.py` AppTests verify the PDF atlas CTA, side-by-side section rendering,
one mocked build request, source list → world focus, world focus → source formula,
local page switch/no API, cached button behavior, invalid atlas isolation and no
atlas CTA for pasted text. AppTest is **not** proof of browser SVG pixel hit-testing
or real model region accuracy.

Final full command: `python -B -m unittest discover -s tests -q`.
**173 passed, 144.019 seconds, no skips**, in one complete regression run.
Output is preserved in `day19-final-regression.log`. `git diff --check` passed
(only existing CRLF conversion warnings).

## Browser evidence

Offline `tests/manual_day19.py` uses deterministic original phasor/waveform and
projectile source diagrams, unequal page sizes and the same production viewer
and existing scene renderer. Source phasor selection visibly changed Phase B's
equation lens; generated phase selection returned to source formula grounding.
These fixtures are not presented as live AI grounding. Human live tests remain
required for real PDFs, imprecise handwriting, browser sizes and model fidelity.
The final browser also confirmed high-confidence label masking and keyboard
reveal locally; updated Formula Trace showed localized time/parameters and compact
driven-view categories. Screenshot: `day19-source-world-browser.png` (selected
original Phase B region beside the generated shared-state spatial view).
The projectile source's Velocity arrow also updated the existing world's
Horizontal velocity equation and exposed its page-two formula anchor using the
same adapter. Screenshot: `day19-projectile-source-browser.png`. Label masking
and Enter-to-reveal changed the source overlay locally without a semantic patch.

## Files changed in Day 19

New: `source_atlas/__init__.py`, `schema.py`, `model.py`, `state.py`, `compiler.py`,
`runtime.py`, `frontend/index.html`; `tests/atlas_fixtures.py`, `test_day19.py`,
`atlas_frontend_smoke.cjs`, `manual_day19.py`; this evidence report and the final
regression log/browser evidence images.

Modified: `scene/compiler.py` (optional result-path build/split integration),
`scene/renderers.py` (source focus for all declared events), `presentation.py`
(badge), `app.py` (module description only), `i18n.py`, `README.md`, `AGENTS.md`,
`PRODUCT_VISION.md`. Existing `test_day17.py`/`test_day18.py` only have current badge
assertions advanced to Day 19; their behavior/security regressions are retained.

Dependencies added: **none**. Source Lens, PyMuPDF, Streamlit custom components
and the OpenAI SDK were already available. No CDN or frontend build/runtime added.

## Exact human live-test steps

1. Restart your own production process from this checkout:

   ```powershell
   python -B -m streamlit run app.py --server.port 8518
   ```

   Open http://localhost:8518, verify Day 19 / 30 and reanalyze a text-based PDF.
2. Use sinusoid/phasor or spatial-physics material. Explicitly build a Learning
   Scene/Spatial Learning World first (not Day 16 Dynamic Simulation), then choose
   1–3 relevant pages and **建立來源互動圖譜**. Verify processed-page labels and
   original-source / interactive-meaning workspace before the overview.
3. Pause playback. Click an actual source arrow/phasor/formula overlay. Confirm
   the corresponding scene vector, waveform and equation focus change together.
   Select a world phase/quantity; verify the supporting source region/page changes.
   Use contextual **轉成互動場景**: no additional scene compilation should occur.
4. Select a formula: verify quoted source, model equation, parameter names and
   driven views. Use multi-page concept-source buttons to inspect other anchors.
   Check the box visually: confidence is not proof. Reject falsely precise boxes.
5. Test **拆解圖示**, **僅顯示目前焦點**, **隱藏標籤** then click a label mask to reveal,
   zoom/scroll/reset and keyboard source selection. Repeat with projectile sources.
   Test desktop and narrow viewport; inspect uncertain handwritten/messy content.
6. Check request counts: one explicit atlas build for a given identity, no calls
   for these local actions. Invalid/low-confidence grounding should preserve the
   normal analysis, scene, existing Source Lens, quiz/review and other features.
   Recheck the Day 17 probability PDF and Day 18 baseline/recording/replay.
