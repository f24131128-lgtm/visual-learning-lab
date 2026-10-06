# Day 24 — Direct Manipulation Learning World

2026-10-06, Asia/Taipei. No commit or push. Day23 work present at entry was
preserved; this is an incremental adapter, not a homepage or world replacement.

## Decision and product result

The learner grabs the existing representation: a circular endpoint, launch-vector
endpoint, or mathematical anchor. One fixed **JSXGraph 1.13.3** adapter consumes
numeric projections from **Spatial World** and **Numeric Lab**. Their existing
safe evaluators, parameter stores, metrics, trajectories and source links remain
authoritative. Selection/focus and release commit use the canonical reducers;
mouse movement uses local, explicitly tentative numeric previews.

Focused upstream comparison: JSXGraph supplies mathematical boards, numeric
points/curves, equal scale, coordinate and point-event handling. Konva's general
canvas gestures would still require axes/constraints; PixiJS's GPU scene machinery
is disproportionate for these handles. Plotly remains in existing charts/camera;
shape relayout does not replace a validated semantic inverse. The exact pinned
paths, primary-source links, maintenance evidence, deployment costs and
REUSE / WRAP / LEARN / DEFER decisions are in `OPEN_SOURCE_REUSE_LEDGER.md`.

License: explicitly choose JSXGraph's **MIT** option. Published core JS/CSS are
bundled unchanged, with `LICENSE.jsxgraph.txt`, embedded third-party notices and
`vendor-manifest.json` containing URLs, hashes and byte counts. No examples,
extensions, weights, generated interaction programs or upstream handler code are
copied. No Python dependency, npm build, runtime CDN or service is added.
Existing PyMuPDF AGPL/commercial deployment obligations remain unresolved.

## Contract and ownership

`manipulation/contract.py` defines finite analytic inverse families and strict
events. An opt-in target has existing object/semantic IDs, label, coordinate
space, parameter IDs, bounded inverse coefficients, position, bounds and validated
source pages. These declarations are derived from normalized forward expressions,
not guessed from labels. One adapter handles all three families:

| Family | Supported proof | Existing authority |
|---|---|---|
| Circular | Equal-radius `R*cos(A)` / `R*sin(A)`; `A` affine in one adjustable parameter, frozen time/other values | Spatial DAG, exact snapshot and world reducer |
| Polar endpoint | Same angle proof plus nonnegative affine radius in one other parameter | Atomic two-parameter world commit, shared time policy, complete trajectory and invariant validation |
| Vertical anchors | Exactly one affine series with one adjustable coefficient and one constant parameter; zero inside x domain | Numeric Lab's existing values, safe_math, curves and metrics |

Only bounded `manipulation_focus` and `manipulate` events cross the iframe boundary.
Focus begin carries `{scene, revision, token, kind, target, time}`; release also
carries finite `x,y`. Events cannot provide an arbitrary patch or semantic ID.
The server resolves the existing target's canonical semantic ID. Lab focus uses
one existing lesson reference, or an explicitly declared, uniquely central
concept-map node directly connected to every related lesson reference. Ambiguous
links hide direct manipulation while retaining prior controls.

The browser is not a second canonical parameter store. It receives numeric arrays
only and interpolates a bounded precomputed mesh during drag. No model expression,
JessieCode, string function parent, HTML, Python or generated JavaScript executes.
Focus begin commits once; pointermove commits no formal values; release commits
one validated semantic change. A focus acknowledgment preserves the live board
only while material, formal values, time and labels still match. Release buffers
until that acknowledgment; stale/material-switched gestures cancel or reject.
Rejected releases restore the authoritative object. Escape/pointercancel restore
the preview. Keyboard and the prior sliders remain available.

World batches use the extracted existing candidate checks: snapshot, inverse
consistency, actual invariants, complete frame envelopes and parameter-derived
time bounds. Shortened events clamp time atomically. Semantic recording records
one bounded parameter batch, not pointer coordinates or keystrokes. Replay uses
the same validation. Numeric Lab writes only its existing `saved['values']`;
revision/signature metadata invalidate stale/ABA gestures after other controls.

Source content and compiled baseline are distinct from current exploration.
Stored analysis language governs generated material; UI labels use `i18n.py`.
Source/Explore roundtrips retain parameter values and focus. Existing lessons,
quizzes, review, Atlas/Lens, analogy and cached explanations are preserved.

## Acceptance evidence

Three synthetic declarations reuse existing fixtures; production contains none.
`tests/manual_day24.py` enters the normal `app.py` render path with an original
one-page synthetic PDF, source context and cached formal declaration. It makes no
model request. These are normal-PDF integration tests, not real-document grounding
or a learning efficacy study.

| Case | Real pointer result in normal Streamlit app | Linked result / persistence |
|---|---|---|
| A Phase | Endpoint to `(0,1)` → phase **π/2** | Signal exactly **1**, waveform shifted, Source/Explore values retained |
| B Projectile | Endpoint to approximately `(15,25.980762)` → **30 m/s, 60°** | Exact committed horizontal velocity **15**, full new trajectory, Source/Explore values retained |
| C General math | x=0 anchor to y≈2 → offset≈**2**, coefficient remains **1** | Other x=2 anchor follows to y≈**4**, same existing curve/metrics/sliders, Source/Explore values retained |

`day24/app-browser-results.json` and `day24-app-browser-final.log` record real
pointer events, Python commits and component reruns in a fresh isolated headless
Edge profile against localhost. All three pass, zero page errors. Rounded pointer
coordinates are evaluated exactly by the formal engine; exactness does not mean
the physical mouse lands on a mathematically exact real number.

Separately, `day24/browser-results.json` / `day24-browser-final.log` test the actual
bundled JSXGraph in an isolated iframe: three cases, one focus begin, one release
value commit, zero pointermove commits, equal physical scales and rejected-state
restoration. Fixed-code VM smoke additionally checks inverse parity, state-to-view
sync, iframe reflow, border/letterboxing and CSS transforms. It is separate from
actual browser evidence. Human ergonomics/source fidelity are still pending.

Visual QA inspected `day24/app-phase.png`, `app-projectile.png`, `app-math.png`.
The phase shows the upper endpoint and signal 1; projectile shows speed 30, angle
60°, linked trajectory and velocity 15; math shows two coherent anchors. The
projectile's full legal range makes its initial arrow relatively short. The
existing slider and playback workspace remain accessible.

## Security and API behavior

Focused tests cover unknown/spoofed IDs, wrong scene/material, duplicate/stale
tokens and revisions, extra keys, bool-as-number, NaN/Infinity, huge integers,
unsafe expression ASTs, fixed parameters, unsupported/nonanalytic forward forms,
ambiguous focus, coordinate bounds, parameter bounds, coupled atomic failure,
time clamping, bounded/malformed recordings and optional preview failure.
Invalid features fail locally without removing analysis or prior controls.
The final serialized component envelope, including committed values/ack, is
bounded at **1.5 MB**. Mesh limit: **100,000 numeric values / 900,000 bytes**;
at most four recognized targets; existing 80-step semantic recording limit.
Preview precision is six significant digits and visibly approximate. Exact
commit validation does not reuse rounded preview values.

AST/topic audit scans independently authored production Python branches; labels
renamed to unrelated topical words yield the same inverse declarations. There are
no production branches on phase/projectile/linear/sinusoid/velocity/slope names,
and no eval/exec/compile paths. Parametric affine/trigonometric recognition is a
mathematical structural constraint, not universal formula support.

Real-model probe: **8 paid requests**, **24,759 input + 13,233 output = 37,992
tokens**, existing configured model `gpt-5.6-luna`, SDK retries disabled. Budget
ceiling was 12. Three main analyses, three planners and two spatial compilations;
general math reuses its main-analysis lab. `day24/model/results.json` preserves
the initial conservative math focus rejection. `results-replay.json` revalidates
the same immutable response artifacts after the explicit concept-map bridge and
duplicate-handle removal; all three have valid local targets and commits.
**Zero additional model requests** on replay, drags, sliders, navigation, focus,
preview generation or Source/Explore. Tests mock request clients and assert zero.
Generated phase/projectile focus IDs retain the model's existing IDs; their
pedagogical fidelity needs human inspection, not relabeling to force acceptance.

## Performance

`tests/day24_performance.py` is a reproducible synthetic local benchmark, seven
hot repetitions. Cold measurements include tracemalloc overhead; allocation is
Python peak allocation, **not process RSS**, and not hostile-PDF isolation.

| Case | Cold payload with allocation tracing | Hot median | Exact commit median | Payload / peak Python allocation |
|---|---:|---:|---:|---:|
| Phase | 218 ms | 5.83 ms | 2.34 ms | 91,574 B / 885,350 B |
| Projectile | 1,954 ms | 35.53 ms | 11.44 ms | 692,807 B / 6,254,312 B |
| Math | 129 ms | 3.25 ms | 0.35 ms | 68,074 B / 623,934 B |

The core library is 969,075 bytes, gzip 252,302 bytes (not a guarantee that a host
serves gzip). Mesh caches hold two entries per existing owner and exclude varied
parameters from their keys; fixed parameters/material/spec changes invalidate
appropriate meshes. Drag uses requestAnimationFrame, numeric interpolation and
stable viewport, not per-frame Streamlit reruns. Release/focus have two small
canonical roundtrips. Browser `drag_ms` includes scripted movement, screenshot
and rejection acknowledgment; it is **not** an FPS or gesture latency benchmark.
No performance result establishes mobile responsiveness or Community Cloud load.

## Tests and remaining scope

Day23 Phase C baseline: **20 passed / 13.702s**.
Final Day24 focused: **21 passed / 15.030s** (`day24-focused-final.log`).
Affected suites: **198 passed / 111.247s** before final small focus/DOM fixes
(`day24-focused-regression.log`). The final focused run covers those fixes.
**Full regression ran exactly once: 409 passed / 212.103s**, no failures/skips
reported (`day24-regression.log`).

Reproduce focused: `python -X utf8 -B -m unittest discover -s tests -p test_day24.py -q`.
Full: `python -X utf8 -B -m unittest discover -s tests -q`.
Payload export: `python -X utf8 -B tests/day24_payloads.py`.
Benchmark: `python -X utf8 -B tests/day24_performance.py`.
Browser scripts require Playwright plus Edge in the isolated test environment;
they are developer-only, not app runtime dependencies. Windows sandbox/socket
restrictions required authorized outside-sandbox offline tests. Earlier failed
diagnostic logs are retained; the final successful logs are named above.

Limits: analytic 2D handles only; no arbitrary solver, point dragging on arbitrary
curves, direct time gesture, vector addition, 3D gesture or generated-code runtime.
Mesh interpolation is approximate; no unsupported model is weakened to render.
Canonical release uses exact existing formal engines. Real PDF grounding, touch
ergonomics, human source/model fidelity and learning efficacy remain unmeasured.
No optional stretch beyond shared semantic recording compatibility was pursued.

## Exactly three human tests

Launch the offline package:
`python -X utf8 -B -m streamlit run tests/manual_day24.py --server.port 8527`.
Open `http://localhost:8527`; select the named case in the sidebar. Approximate
mouse placement is sufficient; formal equality is checked by automated tests.
Do not press any AI build/explain button during these tests. API delta is **0**.

1. **A 相位與波形** — exact original material: rotating unit pointer with
   `theta=time+phase`, `(cos(theta),sin(theta))`, signal `sin(theta)`; initial
   time=0, phase=0. Drag the purple endpoint to the top `(0,1)` and release.
   Easiest signal: phase≈1.5708 rad and signal≈1; waveform shifts coherently.
   Move the existing phase slider afterward: endpoint and waveform follow.
   Switch Source then Explore: original one-page text is unchanged and current
   values persist. Capture one screenshot showing pointer, waveform and values,
   plus source/current focus if practical. API delta=0.
2. **B 發射向量與軌跡** — existing Day18 projectile declaration: speed initially
   20 m/s, angle45°, gravity9.8; `vx=speed*cos(angle)`, `vy=speed*sin(angle)`,
   trajectory from the same DAG. Drag launch endpoint toward `(15,26)`; easiest
   signal: speed≈30 m/s, angle≈60°, horizontal velocity≈15 and a newly fitted
   trajectory. Existing speed/angle controls update the endpoint in reverse.
   Canonical focus selects the declared launch quantity; no second source focus.
   Switch Source/Explore: original source is unchanged and values persist.
   Capture vector, trajectory and speed/angle/velocity in one shot. API delta=0.
3. **C 仿射關係與錨點** — exact material `y=a*x+b`, x∈[-2,2], a initially1,
   b initially0. Drag x=0 purple anchor vertically to y≈2. Easiest signal: b≈2,
   x=2 anchor≈4 and the entire line follows. Drag x=2 anchor vertically to alter
   a; use the existing sliders to confirm reverse synchronization. Canonical
   focus is the existing affine-relation concept. Source/Explore preserves
   values and the original formula text. Capture both anchors, line and a/b.
   API delta=0. No developer diagnostics needed unless something fails.

## Day25 recommendation

Prioritize source-to-affordance fidelity and human ergonomics on a small original
real-PDF corpus. Measure whether learners recognize the handle and whether the
selected semantic ID/parameter bounds match the source. The three mechanical
cases now work through two formal engines, while paid probe IDs and legal-range
viewport show the next uncertainties. Defer a new GPU/3D renderer or universal
inverse solver until those observations justify it.
