# Day 18 live-test consolidated fix — 2026-10-01

This pass continues the existing Learning Scene architecture. No commit/push,
homepage redesign, Dynamic Simulation changes, quiz changes or new production
dependency. Existing dirty work, live logs, secrets and tracked bytecode are
preserved. Human acceptance on freshly compiled real material remains required.

## Exact causes and fixes

1. **Viewport:** `normalize_world` previously projected parameter endpoints into
   the model's literal axes. A valid circular reference axis at Rmax could exceed
   that small viewport. `policy.py` now derives bounded safety envelopes from
   legal ranges and each scenario's semantic duration before strict projection
   checks. Origins, complete paths, vector endpoints and both reference-axis
   directions participate. Display bounds fit the complete current trajectory
   and baseline union, with equal physical scales and an 8% visual margin.
   No ranges are shrunk to fit the axes. ±1,000,000 coordinate limits, finite
   evaluation and actual-state rechecks remain. Sampling is not analytic proof.
2. **Time:** fixed min/max previously described every physical event. Schema 2.2
   adds `fixed_duration`, parameter-only `derived_duration`, and bounded
   `periodic_duration` (1–8 periods), all ending within 10,000 time units. The
   evaluator, frames, invariants, inverses, keyboard timeline, browser timeline,
   waveforms, camera and replay use the same effective numeric domain.
   Parameter changes locally recompute duration; shortening it atomically clamps
   the old time to the endpoint. The projectile fixture declares the complete
   source-supported `2*speed*sin(angle)/grav` duration. No renderer knows what
   a projectile is. No automatic interpretation of an arbitrary ground condition
   or new numeric termination solver was added; derived endpoint formulas are
   the supported safe termination strategy in this pass.
3. **Ranges:** preserve explicit source or validated pedagogical ranges first.
   A declared semantic fallback derives useful bounds from type and baseline.
   Positive speed/length/frequency use baseline/4..5×baseline; acceleration uses
   .1×..2×baseline; positive inclinations use 5°..85°. These are policy rules, not
   scene-ID/renderer branches. Invalid supplied ranges are rejected *before*
   fallback. Radian angular parameters may display degrees consistently in
   controls, deltas and replay; canonical math/recordings remain radians.
4. **3D:** the prior Python camera rendered committed snapshots while playback
   advanced only inside the SVG browser component. Added a contained local
   Plotly camera consuming exactly the current shared numeric projections.
   Camera mode gates every participating view together, roughly 10 Hz, rather
   than accumulating obsolete camera frames behind the waveform. One pending
   camera update, a 3-second render timeout and WebGL loss handling bound work.
   Camera rotation/zoom persists; failure returns to synchronized 2D.
   All primitives are still planar, **z=0**, not volumetric geometry or a claim
   of 60 FPS. The separate, honestly labeled server snapshot remains a fallback.
5. **Replay:** separate 0.5×/1×/2× pacing gives 3.6/1.8/.9 seconds per meaningful
   state. Quiet progress identifies parameter/time/focus/comparison changes.
   Raw steps stay in order and all are validated; presentation skips identical
   states only and maps commit indices back to the original sequence. Renamed
   all active recording headings to 探索紀錄與回放 / Exploration Recording & Replay.
6. **Cache:** 2.2 separates older scene/rejection identities, rejects mismatched
   cached versions, clears rejection/runtime remnants when a valid scene is
   saved, and includes scene identity in numeric frame-cache keys. `None` is
   never a valid cached scene. Current-schema rejection is still cached, not
   automatically retried; explicit uncached builds remain one targeted request.

The compiler still uses strict Structured Outputs (every wire key required;
optional declarations represented by null/empty arrays), following
[official OpenAI documentation](https://developers.openai.com/api/docs/guides/structured-outputs).
New policy defaults are conservative: fixed duration, unchanged pedagogical
ranges and native units. Missing required base fields, malformed supplied
policies, unsafe expressions and unknown bindings/objects remain failures.
Camera persistence follows [Plotly's uirevision contract](https://plotly.com/javascript/uirevision/).

## Actual development failures, not invented stories

- First focused run: 70 tests, one assertion failure. Range-preservation test
  compared source-page metadata even though pasted text correctly removed it.
  Fixed the test to allow the fixture's page 1; did not change source validation.
- Browser QA found a blank newly integrated camera despite valid numeric
  updates. The broad `.panel svg` styling put an opaque background on Plotly's
  transparent SVG overlay, covering WebGL. Scoped it to `.panel > svg` and added
  a regression assertion. The camera then visibly rendered moving vectors.
- The earlier 41-state replay test expected an identical initial time patch to
  receive its own dwell. Updated the presentation expectation to 40 while
  retaining the original raw recording and reducer-order tests.
- Final review found that accessible recording callbacks can change recording
  metadata without changing physical revision. The identical-layout guard now
  compares recording metadata too; the frontend regression explicitly checks
  that such a change refreshes status, while true layout resends preserve playback.

## Automated evidence

Focused command:

```powershell
python -B -m unittest discover -s tests -p 'test_day18*.py' -q
```

Latest focused result before final frontend-only guards: **71 passed**, 39.537 s,
no skips. Final full regression: **143 passed**, 141.690 s, no skips.
The pre-pause process output was unavailable after resuming, so the full suite
was rerun once to recover verifiable evidence; output is preserved in
`day18-final-regression.log`. Two later frontend-only guard checks each passed
one existing test (not additional tests in the counts). `git diff --check` passed.

Added `test_day18_consolidation.py` (23 tests): circular Rmax and undersized hints,
periodic time, max three-phase vectors, full projectile flight/no post-impact,
speed/angle/gravity changes, atomic endpoint clamp, current/baseline time and
viewport, degrees/radians, semantic fallback/source-priority, invalid ranges,
unsafe duration expressions, absurd bounds, optional policy defaults vs required
fields, waveform→canonical state, replay order/no-op presentation/security/local
requests, numeric cache scene identity, CSS isolation, Day 17 validity, normal
app result-path controls and cache replacement/invalidation. Existing tests also
run the fixed frontend smoke through four systems (original two, complete
projectile and circle), camera numeric projection, common time, paced replay,
inverse gestures and waveform selections. AppTest does not test WebGL pixels.

## Browser evidence (offline fixtures, not live model output)

Separate localhost server on port 8520; did not stop the user's live process.
Desktop 1280×900 and existing narrow viewport inspected. Three-phase camera
visibly renders and moves with shared time/current values; captured a moving
frame at t≈.0016807 s, electrical angle≈.528 rad. Screenshot:
`day18-consolidated-camera.png`. Full projectile controls show 20 m/s,
45°, 9.8 m/s² → t_end≈2.8862 s; 60° → 3.5348 s; endpoint y≈−7.1e−15 m.
This is floating roundoff, not post-impact frames. Real newly generated scene
quality is not claimed from fixtures; this pass has not sent a new paid API call.

After resuming, the offline server was restarted without touching the user's
app process. Browser recording of frequency 50→60 Hz, time 0→0.05 s and Phase B
focus produced six raw steps and four meaningful replay states. At 0.5×,
the browser showed step 3/4 with a time-change summary; final committed state
retained 60 Hz, 0.05 s and Phase B's equation lens. Mid-step pause timing remains
a human live check. Temporary viewport overrides were reset.

## Exact files changed in this pass

- `scene/world/schema.py`, **new** `policy.py`, `engine.py`, `validator.py`,
  `state.py`, `runtime.py`
- `scene/world/frontend/index.html`, **new** `camera.js`, `plotly.min.js`,
  `LICENSE.plotly.txt`
- `scene/state.py`, `i18n.py`
- `tests/world_fixtures.py`, `test_day18.py`, `test_day18_compiler.py`,
  **new** `test_day18_consolidation.py`, `world_frontend_smoke.cjs`, `manual_day18.py`
- `README.md`, `AGENTS.md`, `PRODUCT_VISION.md`, **new** this report and
  `docs/day18-consolidated-camera.png`

No `requirements.txt` change. The 4,851,164-byte MIT Plotly.js 3.7.0 asset and
license were copied from the already-installed Plotly package for offline use;
no CDN, frontend build, Node production runtime or new Python package.

## Exact human live-test steps

1. Stop **your own** old app process, start a fresh one from this checkout:

   ```powershell
   python -B -m streamlit run app.py --server.port 8518
   ```

   Open http://localhost:8518 in a fresh tab/hard reload. Verify Day 18 / 30.
   Reanalyze the material and explicitly 建立空間學習場景; do not use Day 16's
   建立動態模擬. 2.2 avoids incompatible old session/compiler scenes.
2. Circular material: x=R*cos(omega*t+phi), y=R*sin(omega*t+phi). Build once;
   increase R to its legal maximum. Reference axes and full orbit stay visible;
   changing omega updates a declared periodic duration locally.
3. Same-height projectile: x=v0*cos(theta)*t, y=v0*sin(theta)*t−.5*g*t²,
   landing when it returns to y=0. Build once; set v0=20, θ=45–60°, g=9.8.
   Timeline ends at approximately 2.8862/3.5348 s; Play reaches landing.
   Change all three parameters. End time, path, vector origins, waveforms and
   viewport update without another compiler request. Angles display degrees.
4. Three phase: Play in 2D, then select **3D 相機** inside the primary scene.
   Verify camera/vector/waveform/state values move together; drag camera/zoom.
   Pause and click a waveform; phase selection should affect multiple views.
   The expander labeled 靜態備援 is intentionally only a committed snapshot.
5. Set baseline, change parameters, restore/clear comparison. Run an available
   experiment. Open 探索紀錄與回放, record parameter→time→focus, stop, replay at
   0.5× or 1×. Observe the progress/change summary, pause midway and replay again.
   Raw semantic order and final state must agree; no source text/keyboard data.
6. Monitor request/log counts: one explicit build; no requests for any local
   actions above. Exact validation reasons remain internal on rejection.
   Recheck the Day 17 probability PDF and existing lab/simulation features.

Only declare human acceptance after a freshly compiled real scene passes these
checks. Fixed code and sampled numeric checks cannot establish source fidelity.
