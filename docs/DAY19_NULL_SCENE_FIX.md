# Day 19 — optional scene runtime fix (2026-10-01)

## Root cause and normal product path

`app.py` renders `scene.compiler.render_scene_builder` before the learning
overview. Suitable material without a built scene has a nonempty scene-state
wrapper whose `scene` value is `None`. That wrapper is passed to the Source
Atlas builder and then `source_atlas.runtime.render_atlas`.

The old spatial-caption condition used
`wrapper.get("scene", {}).get("domain")`. The default `{}` applies only when
the key is absent, not when its value is explicitly `None`. Consequently the
render crashed **before** the PDF viewer's isolated rendering block. An AppTest
regression reproduced the exact reported `AttributeError` before the fix.

## Changes and audit

- `source_atlas/runtime.py`: normalize the optional scene once; missing bundle
  wrappers also work in rendering and component payload generation. The PDF
  image, grounded boxes, page/region selectors and source formula trace do not
  require a scene. Only scene-specific caption/link actions depend on it.
- `source_atlas/state.py`: one `optional_scene` helper shared by builder,
  runtime, focus reads and focus writes. Without a scene, focus is `None` and
  linking returns `False`; source-region navigation is retained. Existing
  probability selectors and spatial reducer remain the linking authorities.
- `source_atlas/compiler.py`: reuse the wrapper helper; avoid chaining `.get`
  through nullable `page_texts`. Missing canvas source is also optional rather
  than a required dictionary access.
- `source_atlas/model.py`: absent/null native page text becomes an empty string
  for bounded request context and excerpt verification, never verified evidence.
  New probability rendering coverage also exposed a separate `TypeError`:
  normalized probability scenes contain a tuple-keyed `outcome_by_path` index.
  Atlas fingerprints now use probability schema declaration fields, including
  outcomes, events, expressions, bindings and source references, rather than
  redundant non-JSON derived indexes. The probability scene is not changed.
- Audited `semantic_catalog`, formula/evidence tracing, event handling, the
  builder facade and the Day 19 routes in `scene/compiler.py`. Existing guards
  there already handle an absent scene. No changes were needed to `app.py`,
  scene validators, DSL schemas, renderer math or frontend code.

No security validation was loosened, no scene was fabricated to enable source
viewing, no dependency was added, and no commit or push was made.

## Regression evidence

`tests/test_day19_optional_scene.py` adds nine tests:

1. `scene=None`: actual runtime section, PDF payload/boxes, source formula trace,
   page/region navigation and unavailable scene-link action.
2. Scene key absent: same rendering coverage.
3. Wrapper absent (`None`): same rendering coverage.
4. Bundle wrapper key absent: same rendering coverage.
5. Probability scene rendering and Source ↔ Scene focus.
6. Spatial scene rendering and Source ↔ Scene focus.
7. Actual `app.py` normal PDF path: build Atlas before the spatial world; inspect
   source formula and change page with no extra request; later supply a validated
   cached scene and explicitly rebuild grounding for its new semantic identity;
   verify both linking directions and exact request counts.
8. Nullable/absent native page text still sends the original PDF raster request.
9. Nullable page text never claims a source excerpt is verified.

The component boundary is mocked in new AppTests, with its actual PNG and box
payload inspected. Existing fixed-code frontend smoke coverage remains in the
focused suite. Browser SVG interactions and the real OpenAI response still
require human live testing; these tests make no paid API requests.

Focused command: `python -B -m unittest discover -s tests -p 'test_day19*.py' -q`

Result: **39 tests passed**, 14.252 seconds. Log:
`docs/day19-null-scene-focused.log`.

Full command: `python -B -m unittest discover -s tests -q`

Full-suite result: **182 tests passed**, 133.612 seconds, one complete run.
Log: `docs/day19-null-scene-regression.log`.

## Human live checks

1. Start/reload the app from this checkout:
   `python -m streamlit run app.py --server.port 8520`.
2. In a fresh analysis, upload a probability or three-phase PDF. Do **not** build
   its Learning Scene/Spatial Learning World yet.
3. Click **建立來源互動圖譜**. Confirm **原始來源**, the original PDF and grounded
   regions render without a traceback. Change page, select a grounded formula,
   and verify **公式追溯** and source text remain available. **轉成互動場景**
   must not appear before a scene exists.
4. Build the applicable semantic scene. Its identity changes the Atlas cache;
   explicitly rebuild Atlas grounding if prompted. Select a linked source
   vector/event and check scene focus; select its counterpart in the scene and
   check source emphasis/page. Pause spatial playback before source selection.
5. Repeat with both probability and spatial materials. Also verify a visual PDF
   that is not a scene candidate can use Atlas independently. Page navigation,
   selection and source tracing must not trigger further compiler requests.
