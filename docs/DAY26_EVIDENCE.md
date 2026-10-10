# Day 26 — Competition Golden Path

2026-10-10, Windows, branch `day17-learning-scene-wip`, starting HEAD
`336d1c8f4cb17642cc131d3c220b3fb68c5e9a6a`. No branch switch, reset,
commit or push. This is one real-document browser proof plus automated
regressions. Independent human acceptance is still pending.

## The approximately 90-second demonstration

Compilation happens beforehand; generation is not part of the 90 seconds.

| Suggested time | Action and observable proof |
|---|---|
| 0–20 s | In Source, view MIT Chapter 5 PDF page 4, Figure 5.3. Select the diagram and explicitly choose Initial horizontal velocity (`vx0`). The source has several meanings; no arbitrary first choice is made. |
| 20–35 s | Open interactive twin. The same `vx0` focus owns the existing Initial velocity vector (`initial_velocity_vector`). |
| 35–60 s | Drag its endpoint and release. Observe the vector, trajectory and numeric/derived values; release commits through the existing validated World reducer. |
| 60–75 s | Return to supporting source. The same diagram, page, focus and committed values survive. Source pixels and boxes remain unchanged. |
| 75–90 s | Select Horizontal position (`x_position`) in the page 6 vector equations. It stays grounded and focusable and explicitly has no direct manipulation. |

These are suggested demonstration timings, not measured novice task times.
Browser automation was performed by Codex; no human participant completed a
timed acceptance in this session.

## Real material and provenance

Used **MIT OpenCourseWare 8.01SC Classical Mechanics, Chapter 5: Two Dimensional
Kinematics**, Peter Dourmashkin / MIT course team. It was written as actual
teaching material, not for this renderer. [Resource page](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter5/),
[original PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter5.pdf),
[OCW terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/).

The PDF is 2,316,314 bytes, 16 pages, SHA-256
`688a232388f914ed834e02b28ba343c10b3866e23c3cd94ff38f859957d0c5ec`.
Only the first eight text-bearing pages are extracted/allowed as citations;
the existing main analysis sends the original PDF as well. Atlas used PDF
pages **4, 5, 6**. PDF page 4 is printed page 3. No OCR, authored replacement
PDF, seeded analysis, hand-edited model declaration or fake judge mode was used.
The original PDF and private responses are not committed.

OCW educational content is CC BY-NC-SA 4.0 under its published terms. The four
screenshots attribute MIT OCW here and in the notices; reproduced educational
content retains that license. UI annotations/model exploration are additions;
the source image is unchanged. This does not relicense software or imply MIT
endorsement. Source licensing is separate from unresolved PyMuPDF deployment
obligations.

## Actual production result and failures

The empty acceptance session used real upload, analysis and explicit production
build buttons through `app.py`. `tests/manual_day26.py` only observes the real
SDK and existing owners, disables SDK retries, limits requests and writes
private diagnostics. It contains no fixture or injected declaration. A fixed
presentation module reload was needed because `runpy` does not watch imported
files like the normal entrypoint; it did not replace learning state.

The first Traditional Chinese pass completed analysis but did not complete the
golden path: its planner candidate was not accepted, and its spatial declaration
was safely rejected. The latter supplied an empty `set_time.target_id` and an
experiment setting fixed gravity 9.8 to 12. Validators were retained. Three
instruction sentences now state those existing constraints and permit omission
of uncertain optional experiments. Schema/version/validators are unchanged.

A separate, explicit **English reanalysis** of the same PDF then produced an
accepted spatial world, an accepted dynamic plan and an accepted Atlas. Language,
analysis and nondeterministic model output also changed; the success cannot be
attributed to the instruction clarification alone. No new material was substituted.

Two real product blockers were discovered and corrected during acceptance:

- The ambiguous source-meaning selector was hidden in Related learning. It now
  appears next to the source's linked meanings, using the existing selector.
- Source → Explore → Source cleaned up the page widget and selected new defaults,
  temporarily hiding the valid Atlas. Defaults now come from the existing Atlas
  key only when material/PDF/language/semantic identity match. Ranking excludes
  local focus. The original 4/5/6 cache was restored through the page selector,
  then the complete roundtrip was repeated successfully without another request.

Observed accepted scene: `ideal_projectile_motion`, v2.2 `spatial_dynamics`.
Source region `p4_velocity_decomposition_diagram` links existing `vx0`; the
structurally recognized polar target is `initial_velocity_vector`. A real pointer
drag, from viewport (413,435) to (444,380), released and changed canonical values:

| Quantity | Before | Committed, settled |
|---|---:|---:|
| Initial speed | 20 m/s | 55.19480162942609 m/s |
| Launch angle | about 45° | about 54.9698° (0.9594044747405803 rad) |
| Initial horizontal velocity | 14.1421 m/s | 31.6822 m/s |
| Maximum height | 12.204 m | 106.22 m |
| Time at maximum height | 1.4431 s | 4.6119 s |
| Impact time | 3.0212 s | 9.2678 s |

Focus remained `vx0`, shared time remained 0, revision became 3 and the committed
token was acknowledged. The final roundtrip kept the exact World state, scene
and Atlas. See [numeric trace](day26/numeric-trace.json) for the existing
projection engine's numeric results and equality checks. Preview values are
tentative; evidence uses settled values after validation. Compiled defaults are
model values, not verified source numbers. The original figure is qualitative.

Synchronization proved here is the vector, linked trajectory and readouts of
the **same spatial world**. The separate Numeric Lab below retains its own
existing state; it was not falsely counted as a synchronized view of this World.

## Non-manipulable control

The learner explicitly selected `x_position` / Horizontal position through the
source meaning selector for `p6_vector_equations`, PDF page 6. Canonical focus
changed to that ID. Source and formal relationships remained visible, the UI
stated that it is derived and has no validated direct manipulation, and
`Open interactive twin` count was **0**. Exact handle ownership in the existing
target engine was **[]**. Existing legitimate velocity handles are not aliases
for this quantity. No inverse or fake handle was added.

## Request discipline and honest measurements

There were **7 explicit generation actions** in the real-material session:
first-pass analysis + plan + rejected scene (3); English analysis + accepted
scene + plan + Atlas (4). The successful language identity's preparation used
4 actions; the failed attempt is not concealed. SDK retries were disabled.

The initial observer accidentally wrapped earlier observers on overlapping
Streamlit reruns. It overwrote the accepted scene's timing and undercounted the
saved aggregate (6 rows); duplicate private response filenames do not mean
additional transport calls. The observer was corrected to retain the original
SDK method before measuring ordinary interaction. Therefore **7 is the audited
explicit-action count, not an independently verified transport/billing count**.
No fabricated accepted-scene latency or complete token/cost total is reported.

| Recorded SDK stage | Seconds |
|---|---:|
| First analysis | 52.132 |
| First plan | 6.013 |
| Rejected first spatial scene | 38.905 |
| English analysis | 40.195 |
| Accepted English spatial scene | Not reliably recorded |
| English plan | 8.847 |
| Atlas | 21.938 |

After observer correction, its file remained at **6 records before/after all
drag, return, replay-free playback, width and control-case actions**; no blocked
request was recorded. **Post-compilation interaction API delta = 0**. No Explain,
Review, Simulation or further compiler action was used during interaction.

- Pointer automation call took 601 ms, including automation/pointer travel.
  This is **not** release-to-commit latency or FPS. Those were not measured.
- Direct-board SVG target ID stayed `board_jxgBoard10100986P30` before and after
  the drag; `stMain.scrollTop` stayed 277.6000061035156. This one observation is
  evidence against a drag remount/context jump, not a general guarantee.
- One existing coordinated numeric payload was 88,058 UTF-8 JSON bytes and took
  about 12.7 ms to build. This excludes library transfer/render/paint/network and
  is not a benchmark distribution.
- Source/Twin navigation remounts views intentionally; a first focus change may
  choose another supporting anchor. After explicitly reselecting Figure 5.3,
  its supporting region survived the tested same-focus roundtrip.

## Browser evidence

Actual Codex in-app browser at 1440×1000 and 900×900: Source → Twin, real pointer
drag, release acknowledgment, multiple spatial representations, corrected Source
roundtrip, unsupported focus, Play/Pause/Reset time passed. At 900 px, Source and
its context stack vertically; document scroll width was 900 and the direct
iframe body client/scroll widths both 850. No horizontal page overflow was
observed. This is a viewport check, not touch-device acceptance.

Play advanced the existing contained clock. Pause committed time
6.775594355710783; Reset time committed 0 while preserving speed/angle/focus.
Recording/replay and camera controls were hidden. No per-frame Streamlit loop or
new shared clock was introduced. The direct board catches up to committed clock
state; two independently mounted iframes are not claimed to share every live frame.

[Console log](day26/browser-console.json) contains two earlier server-unreachable
errors and one WebSocket warning from the deliberate server restart at 10:35 UTC.
No browser error entry was captured during the final gesture/roundtrip/control
pass. Two unregistered-component warnings occurred during view navigation at
10:56 UTC and remain reported. The Windows server also logged a pipe
`ConnectionResetError` during a connection closure. The initial measurement-only
wrapper briefly raised a tuple-key serialization error; that was fixed before
final acceptance. A blanket claim of an error-free entire session would be false.

## Automated evidence

The focused Day18/24/25/UI/26 run passed **80 tests in 66.496 s** before the two
later acceptance fixes. The final Day26 subset passed **6 tests in 12.125 s**,
including explicit source disambiguation and page-subset/widget-cleanup roundtrip.
Existing suites retain forged IDs, stale/duplicate events, NaN/Infinity, unsafe
expressions, bounds, atomic rejection, source integrity, request counts and local
interaction tests. AppTest events test reducer boundaries; they do not simulate
browser dragging. Fixed-code frontend smoke remains separate and tests hidden
learner controls while retaining internal replay/camera contracts.

The **one completed full regression ran 437 tests in 300.886 s: 427 passed,
10 errors**. Every error was an older assertion looking up removed World focus,
parameter/time or recording UI. Those tests now use the existing production
component/reducer event boundary and preserve their source, numeric, policy and
request assertions. Post-repair **Analogy: 26 passed in 13.640 s; the other nine
failed cases: 9 passed in 31.526 s**. No production code changed after that full
run. There was no second full-suite rerun; **a fully green final full run is not
claimed**. An earlier incomplete run was interrupted upon discovering the live
source roundtrip blocker and is not counted as a completed suite.

[Validation summary](day26/validation.json) preserves those separate results.
Private logs remain in ignored `.day26-local` for local inspection; historical
Day25 numeric traces emitted by tests were restored to their exact starting bytes.

Commands from repository root:

```powershell
python -X utf8 -B -m unittest discover -s tests -p test_day26.py -q
python -X utf8 -B -m unittest discover -s tests -q
python -m streamlit run app.py
```

For measurement reproduction, use `python -m streamlit run tests/manual_day26.py`
in a fresh process/session with real secrets and upload the original URL's PDF.
Archive any prior `.day26-local` diagnostics before a fresh reproduction; its
historical request file is intentionally not reset silently. The wrapper caps
real calls at seven and stores ignored private diagnostics.
Model output is nondeterministic; unsuitable/rejected results must remain rejected.
Do not reuse the private historical request file as a fresh session's counter.

## Human acceptance and remaining limits

**Pending:** ask a new viewer to perform the timed sequence above on the compiled
material, describe the source/model distinction and try the unsupported quantity.
Record their actions and time separately. The agent's browser operation is not
human usability or learning-outcome evidence.

One accepted English document proves this particular path only. The initial
rejections demonstrate remaining generation reliability limitations. Boxes and
semantic attribution are estimated; native geometry and mathematical invariants
do not establish general fidelity. Broad PDF/image accuracy, keyboard/touch
ergonomics across devices, learning efficacy, hostile-PDF process isolation and
PyMuPDF AGPL/commercial deployment review remain open. No OCR, new domains,
schemas, dependencies, agent system, generated code, 3D project or new focus
store was introduced. Historical evidence was not rewritten.

## Exactly four screenshots

Actual production UI; no mockups. Educational content attribution above applies.

1. [Original Figure 5.3 and source-linked identity](day26/01-source.jpg)
2. [Opened interactive twin at the compiled values](day26/02-twin.jpg)
3. [Settled committed drag: vector, trajectory and values](day26/03-committed.jpg)
4. [Original source retained with current exploration values](day26/04-roundtrip.jpg)
