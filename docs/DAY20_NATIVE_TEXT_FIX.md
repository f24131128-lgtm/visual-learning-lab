# Day 20 live integration fix — native text is not generated markup

## Reproduction and exact root cause

Used the user's actual `C:\Users\88690\Downloads\projectile_source_atlas_test.pdf`, not the earlier small synthetic projectile fixture. Copied it unchanged to the test-only `tests/fixtures/day20_projectile_source_atlas.pdf`; both SHA-256 values are `bbf5911b77561701cb604f87893399724fbadcca1f88d508d61c7bf694ab3fe3` (60,343 bytes). No production code references the fixture or document title.

Direct pdfplumber confirmed page 1: 275 extracted text characters / 256 native chars / 15 lines; page 2: 640 / 622 / 19 lines. These are well within all existing parser limits. The original adapter produced 34 valid-coordinate regions, but `normalize_atlas` kept only 33 and returned `regions[33].plain_text`. The failed region was `native_p2_line18`, the page 2 footer. It contains two literal `>` characters in ordinary ASCII `->` arrows. Its 110-character label/excerpt and coordinates were valid.

The shared generated-text policy rejected every `<` or `>` indiscriminately. `normalize_document` correctly refused to accept a partially dropped native document, but reported only `document: invalid region fields`. The UI caught that exception, stored `document_error=True`, and logged only the exception type; no `document_model` or preview was saved. That boundary mismatch, rather than failed pdfplumber extraction, caused the generic unavailable caption.

## Exact normal-product route audited

`app.py` PDF upload uses `uploaded_pdf.getvalue()` → stored analysis/source context and `learning_canvas.source` via material-specific initialization → `render_scene_builder` → `source_atlas.compiler.render_atlas_builder` → selected analyzed pages → `document_intelligence.ui.render_controls` local button → `service.get_document` → PDF bytes hashed with sorted selected pages → `pdfplumber_adapter.parse` → line regions → `normalize_document` / `normalize_atlas` → successful model in `source_atlas_state.document_model` → native preview returned in Atlas bundle → `source_atlas.runtime.render_atlas` → fixed component numeric boxes and literal labels.

There is no upload pointer read in the local parser. The named file's bytes, page numbering, source hash and selected page filtering were correct. Package availability is checked on reruns, not permanently memoized. Failed parses are not success-cached. No Learning Scene is required, and the original explicit semantic Atlas build remains available. AppTest uses the actual root app result path with the exact PDF bytes; analysis is seeded deterministically, no model/API request is made.

## Fix, without weakening semantic validation

- Add an explicit **native plain-text** policy used only by `normalize_document`. Literal comparison/arrow operators survive unchanged; control characters and tag-shaped markup still reject. Native regions must still be annotation-only, have no semantic links, and pass every existing shape, ID, geometry, page, count, length, payload and locator check. Generated semantic Atlas output keeps the original strict default policy.
- Rendered native text remains opaque: `st.text` and the fixed frontend's `textContent`/attribute APIs, never generated HTML or evaluated formulas. No sanitizer replacement or changed source excerpt. Malicious `<svg onload=...>` and `<script>...</script>` still reject in the native adapter tests.
- Introduce controlled `DocumentError` reasons. INFO logs record availability, requested/parsed pages, per-page native chars, line counts, normalization counts and cache hits. WARNING failures include boundary counts and a precise controlled field reason even if INFO is disabled. External parser errors expose only their type; logs never dump source text, file paths, bytes or secrets. Internal session diagnostics retain the reason/counts, not noisy UI.
- Track `parser_available` separately from `document_available`. Success clears stale local failure state. Native envelope becomes v1.1 and the cache includes adapter revision; old local models/previews are retired for explicit rebuild without deleting semantic Atlas/world state. No automatic API call or whole-app reset.
- A zero-region result does not mean usable local text structure: the service declines it without caching success. Original source/AI Atlas remains usable for image-only or textless handwritten pages. Dense/pathological pages and invalid output retain their rejection rules.

An initial patch failed to propagate the native policy to the excerpt field because of a positional argument; the new exact-PDF tests caught it immediately. Keyword arguments fixed that development error before final validation. This was not the original live bug.

## Regression evidence

Eight new tests (Day 20 now 28) cover the exact PDF chars, all 34 surviving regions including unchanged arrow text, selected-page sets (15/19/34), native comparisons versus unchanged generated-text policy, markup/control/bounds preservation through existing tests, safe diagnostics, actual root-AppTest availability/preview/second-page rendering/no API, retry after old failure, old local-contract rebuild, zero-text graceful fallback and dependency gating becoming available on rerun.

Focused: `python -B -m unittest tests.test_day20 -q` — **28 passed in 16.986 s**, no skips. [Focused log](day20-live-fix-focused.log).

Full: `python -B -m unittest discover -s tests -q` — **210 passed in 160.140 s**, no skips/failures, run once after stabilization. [Regression log](day20-live-fix-regression.log). Existing Day 17/18/19 regressions are included. Browser gestures are not AppTest evidence. Page 2 was rasterized and visually inspected; the failing footer is normal source prose with arrows, not markup. [Raster evidence](day20-live-fix-page2.png).

## Files changed in this fix

Production: `source_atlas/model.py`, `document_intelligence/model.py`, `document_intelligence/pdfplumber_adapter.py`, `document_intelligence/service.py`, `document_intelligence/ui.py`.

Tests/evidence: `tests/test_day20.py`, `tests/fixtures/day20_projectile_source_atlas.pdf`, this report, the two test logs and page-2 PNG. Scoped documentation updates: README, AGENTS, and a historical Day 20 evidence report pointer. No dependency additions/removals, app.py rewrite, commit, push, paid API request or original PDF modification. Unrelated pre-existing dirty files were preserved.

## Exact live-test steps

1. Restart the existing Streamlit server with `python -m streamlit run app.py --server.port 8521` (do not start a competing instance on the same port). No package reinstall is needed for this bug.
2. Analyze `projectile_source_atlas_test.pdf` normally. Before building a semantic scene, select pages 1 and 2 under Source Atlas and click **本機解析文件結構**. Expect **原生 PDF 結構：34 個文字區域** plus the original-source viewer, not the unavailable caption. The local action makes no OpenAI request; normal analysis may incur the app's existing API cost.
3. Set the builder page selection to page 1 only, click the local action: expect 15 regions. Select page 2 only and build locally: expect 19. Choose the last page-2 source object; its original `->` arrows should remain literal text and the footer box should be reachable.
4. Keep a scene/quiz/review state, change source page/selection and verify state remains intact. Building semantic Source Atlas is still a separate explicit API action; cached scene selection/time/parameters and native navigation must not call the compiler.
5. Verify image-only/textless or over-bound pages fall back gracefully; original source and AI grounding stay available. A prior failed local attempt remains retryable. Internal rejection diagnostics appear in logs/session only, not the product UI.
