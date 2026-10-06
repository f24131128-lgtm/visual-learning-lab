# Day 24 checkpoint — direct manipulation

2026-10-06 Asia/Taipei. Implementation and automated acceptance complete.
**No commit / no push / no reset.** Day23 dirty work preserved.
Branch `day17-learning-scene-wip`, starting HEAD `b6b39c5`.

## Final architecture

One offline **JSXGraph 1.13.3** public-API adapter, explicit MIT option, pinned
JS/CSS/license/hash manifest. Existing **Spatial World** DAG/reducer and
**Numeric Lab** values/safe_math remain the two formal engines. Circle, polar
endpoint and affine anchors use one finite semantic contract. Structural inverse
proof, existing semantic IDs, bounds and exact release validation are mandatory;
unsupported forms retain old controls. No generated interaction code or new
Python dependency. Konva/PixiJS deferred; Plotly and previous coordinated
playback/comparison/recording remain. Ledger/notices document exact scope.

Local pointer preview is approximate numeric interpolation; focus begin and one
release commit update canonical Python state. Source content is unchanged.
Atomic two-parameter changes preserve shared time policy and full validation.
State/revision/material/token guards and acknowledgment handle reruns/rejections.

## Final evidence

- Day23 Phase C baseline: **20 passed / 13.702s**.
- Day24 focused final: **21 passed / 15.030s**, `day24-focused-final.log`.
- Affected regression: **198 passed / 111.247s**, `day24-focused-regression.log`.
- **Full regression ran exactly once: 409 passed / 212.103s**,
  `day24-regression.log`; no failures/skips reported.
- Real isolated JSXGraph browser: A/B/C pointer events, equal scale, focus start,
  zero pointermove commits, release once, rejection restore, zero page errors.
- Normal Streamlit app browser: phase π/2 and signal1; projectile ≈30m/s/60°
  and horizontal velocity15; math offset≈2 and synchronized second anchor≈4.
  All three Source/Explore roundtrips preserve values. Final screenshots inspected.
- **Paid requests: 8 / cap12**, input24,759 + output13,233 = **37,992 tokens**.
  Generated artifacts retained; replay/local interactions add **0** calls.
  Small synthetic-text probe, not a representative real-PDF grounding benchmark.
- Hot payload medians: phase5.83ms, projectile35.53ms, math3.25ms. Exact commit
  medians2.34/11.44/0.35ms; payloads91,574/692,807/68,074B. See bounded benchmark
  scope and cold/allocation measurements in `day24/performance.json`.

Repaired failures retained in diagnostic logs: safe_math variable-list bounds,
preview payload size, offline selector fixtures, iframe material lifecycle,
focus-rerun coordinate transforms and fractional CSS dimensions. No validation
weakened or broad coordinate tolerance substituted for the fixes. Final smoke
covers reflow/borders/equal-scale origin/CSS scaling. No more paid requests needed.

## Day24 files

New `manipulation/{__init__,contract,world,lab,preview,runtime}.py`, fixed
`frontend/{index.html,adapter.js}`, pinned library/CSS/MIT notice/hash manifest.
Integration: `scene/world/{state,runtime,schema}.py`, `interactive_lab.py`,
`learning_world/capabilities.py`, `i18n.py` (Day23 portions preserved).
Tests/helpers: `test_day24.py`, `manipulation_fixtures.py`,
`manipulation_frontend_smoke.cjs`, `manual_day24.py`, `day24_browser.cjs`,
`day24_app_browser.cjs`, `day24_payloads.py`, `day24_model_probe.py`,
`day24_performance.py`. Documentation: this checkpoint, `DAY24_EVIDENCE.md`,
`OPEN_SOURCE_REUSE_LEDGER.md`, `THIRD_PARTY_NOTICES.md`, Day24 logs/results/images.
Other status entries were pre-existing Day23 work, not this sprint's new changes.

App: `python -m streamlit run app.py`.
Offline three-case acceptance: `python -X utf8 -B -m streamlit run tests/manual_day24.py --server.port 8527`.
Focused: `python -X utf8 -B -m unittest discover -s tests -p test_day24.py -q`.
Full suite: `python -X utf8 -B -m unittest discover -s tests -q` (already run once).

## Human acceptance remaining

Exactly three procedures and requested screenshots in `DAY24_EVIDENCE.md`:
A phase endpoint, B launch vector, C affine anchors. API delta0; source remains
unchanged; focus/values survive Source/Explore. Real-PDF/source fidelity, touch
ergonomics and learning efficacy are not established by automated screenshots.
Existing PyMuPDF deployment-license review remains unresolved. No stretch sprint.
Day25: prioritize source-to-affordance fidelity and human usability on original
real PDFs before new GPU/3D renderers or universal inverse solving.
