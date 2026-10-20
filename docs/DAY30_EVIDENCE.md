# Day30 — Competition Edition evidence

Work began 2026-10-14 and continued 2026-10-15, Asia/Taipei. Starting commit,
local `origin/main` and fetched remote main: `9502c4b64ce19412d958489d4bc7ed3cace9555d`.
Working directory: `D:\Projects\visual-learning-lab`; branch `codex/day30-competition`.
Tracked files were initially clean; existing untracked research/logs were retained.
No reset, restore, clean, force checkout or force push. No unrelated log/corpus or
secret is part of the release. The reference commit's Google/OIDC/metering work
is preserved. Paid AI stays off; no Cloud secrets or Neon changes.

Latest follow-up: **2026-10-20, after the owner enabled Public**: logged-out public
anonymous acceptance passed for both examples. The browser signed out of Cloud,
closed both previous app tabs, then opened fresh app sessions; this was not an
incognito profile. See [the current public record](day30/cloud-public-20261020/ACCEPTANCE.md).

## What changed

- Two actual prepared buttons before the own-material disclosure. Harmonic opens
  directly into a wide Explore chart; Projectile opens Source at Figure 5.3.
- Harmonic puts the always-visible Plotly chart and compact controls before long
  evidence paragraphs/formal views. Facts/model details remain in a disclosure.
  Traditional Chinese control/curve/metric labels retain unspecified source units.
  The fixed source curve appears once, dashed; optional initial exploration is a
  separate comparison. Existing safe math, provenance and numeric bounds remain.
- Both sources use the existing Workspace, caches, source viewers, reducers and
  learning views. More representations remain available under a disclosure.
  The archived projectile Numeric Lab remains read-only and independent of World.
- A bounded fixed-asset loader validates hashes before admission and revalidates
  scene/Atlas contracts. It does not raise public visitor upload limits.

The original Cloud problem was observed before edits: the chart rendered below
the Visual Flow/inspector; Source-linked controls instead placed a long expanded
facts panel before it. No Cloud chart failure was reproduced. The console had a
KaTeX prose/Unicode warning. [Exact diagnosis](day30/DIAGNOSIS.md) distinguishes
browser evidence from unavailable Cloud server logs. Formula display is now
literal text in details, since model display prose is not guaranteed TeX.

## Historical integrity and the approved derivative

The original Day26 normalized accepted scene, analysis and Atlas survived in
ignored local evidence. The accepted raw scene response was not reliably saved
by that session's overlapping observer. Snapshot World v2.2 lacks mandatory v2.4
provenance; current validators correctly refuse a direct replay. The owner
explicitly approved a labeled derivative in this conversation. No validator was
weakened, no provider was called, and no new successful AI response was invented.

The independently authored [preparation tool](../tools/prepare_day30_projectile.py)
retains formulas, IDs, bindings, inverse, time policy, ranges and default numbers.
It adds conservative provenance/domain declarations, classifies compiled numeric
assumptions as hypothetical, keeps singleton gravity read-only, and starts fresh
session state. [Exact change/provenance record](../prepared/projectile/PROVENANCE.md)
and [manifest](../prepared/projectile/manifest.json) preserve that distinction.

MIT's complete Chapter 5 PDF was re-fetched and matches historical SHA-256
`688a232388f914ed834e02b28ba343c10b3866e23c3cd94ff38f859957d0c5ec`, 2,316,314 bytes,
16 pages. Only original analyzed pages 1–8 may be cited; Atlas remains 4/5/6.
The reviewed, hash-checked fixed asset has a separate bounded admission route.
Public user PDFs remain <=2 MiB / 2 pages in limited-public mode.

Source: MIT OCW / Peter Dourmashkin, Chapter 5 *Two Dimensional Kinematics* and
Chapter 23 *Simple Harmonic Motion*,
[OCW terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/),
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
Unmodified educational content, attribution, source/license links and applicable
ShareAlike requirements are retained for a noncommercial showcase. An engineering
notice review and passing tests are not complete legal clearance. Software,
PDFium binaries and historical PyMuPDF duties remain separate.

## Actual local browser acceptance

This was the production `app.py` through `tests/manual_day30.py`: observation and
provider denial only, no fixture/declaration injection. Browser operator: Codex.
These are not human learner or learning-outcome results.

Fresh session → Projectile → Source page 4 → explicitly choose `vx0` → reanchor
Figure 5.3 → Open interactive twin → physical pointer drag from (412,424) to
(450,360) → release and settle → source → Explore passed. The existing vector
endpoint, linked path and numerical metrics changed. Actual committed values:

| Quantity | Before | After release, settled |
|---|---:|---:|
| Initial speed | 20 m/s | 60.983080863703194 m/s |
| Launch angle | about 45° | about 54.9217° (0.9585637722084824 rad) |
| Initial horizontal velocity | 14.1421 m/s | 35.0467 m/s |
| Maximum height | 12.204 m | 129.07 m |
| Time at maximum height | 1.4431 s | 5.0925 s |
| Ground-impact time | 3.0212 s | 10.225 s |

The exact World state and source hash match after the source roundtrip. Original
source pixels/boxes do not follow exploration values. Opening playback/comparison
and pressing Right on the native speed slider committed 62 m/s through the same
World boundary. Selecting page-6 `x_position` showed the derived/no-target
explanation and **zero Open interactive twin buttons**. No fake inverse added.
[Numeric acceptance](day30/local-acceptance.json), [before](day30/projectile-before.json),
[committed](day30/projectile-after.json), [roundtrip](day30/projectile-roundtrip.json).

Harmonic controls were operated in a real browser. Settled A=5, T=6, φ=−π gave
horizontal shift=3 source time units, angular frequency=1.0472 rad/source time
unit; source facts and PDF hash remained fixed. Rapidly batching three keyboard
actions across overlapping Streamlit reruns initially left T at its prior value;
the period was then explicitly committed separately and verified. No claim of
zero-latency or lossless arbitrary-rate slider gestures is made. The screenshot
and saved values use settled state, not an optimistic input display.

Desktop 1440×1000, source narrow 900×900, harmonic phone-width 390×844 were
inspected. Main document scroll widths were 900 and 390 respectively; controls
stacked and a narrow slider changed A to 4.9. The PDF has its own intentional
bounded pan/zoom. This is viewport/keyboard evidence, not touch-device testing.
The final local browser console captured no warning/error entries. Earlier
intentional server restarts logged Windows connection-reset warnings; absence
of errors is not claimed for the entire development session.

Reload returned to a fresh landing; session navigation preserves values, but no
permanent browser-reload storage is claimed. A second real browser tab loaded default A=3 while the first retained A=4.9,
with a separate fresh landing after reload ([session evidence](day30/session-isolation.json)).
Session isolation, stale/duplicate,
wrong-scene, NaN and out-of-domain atomic rejection are covered by pure/AppTest
checks; those injected bad events are not called physical browser drags.

## Validation and historical counts

Final focused after the localization scope correction: **110/110 PASS**, 76.560 s
(test runner), 78.519 s including historical restoration, failures/errors/skips 0.
Python **3.12.14**; 0 unexpected provider attempts and 0 real calls.
[Machine result](day30/focused-results.json).

The first broad focused run used the product-only environment, lacking test-only
PyMuPDF. A separate requirements-test environment was installed. An earlier
incomplete full run was interrupted to narrow scene suppression to harmonic.
The pre-final completed full run then recorded **561 tests / 17 failures / 45
errors**, 312.752 s; it remains [preserved](day30/first-full-results.json). Those
entries identify 54 unique methods: 53 historical mocked-generation methods had
inherited paid-off mode, and nine subtests of one preservation method compared
Flow node object identities after deepcopy. An isolated field audit found no
changed canvas data. The latter now compares every component `asdict()` field
and all remaining canvas/source data, including exact PDF bytes.

**All 54 affected methods passed** a separate recovery, 133.401 s (135.187 s with
restoration), no real provider or unexpected HTTP attempts.
[Recovery](day30/recovery-results.json), [exact IDs](day30/regression-recovery-ids.json).
The verification tool scopes fixture-private mode to those explicit mocked test
IDs only, denying provider endpoints and real HTTP transport. Public/default-deny
tests retain paid-off mode. The running app and Cloud never change mode.

Final review additionally scoped Chinese label presentation to prepared examples,
so ordinary generated Lab content continues to follow stored analysis language;
a ninth Day30 test verifies that boundary. This actual runtime correction and the
verified fixture repair justify the final integration rerun. It passed **562/562**, failures/errors/skips 0, with
0 real provider calls / unexpected attempts; Python 3.12.14.
[Final complete result](day30/full-results.json).
Previous failed and interrupted runs are retained, never represented as green or
summed into a new denominator. No new production dependency.

Historical report restoration runs in a parent after test-worker finalizers:
older atexit report writers otherwise rewrite preserved records after a test
runner's own finally block. Only historical files are restored; Day30 records
remain independent. No reset/restore/clean Git command is used.

| Historical stage | Evidence supported here |
|---|---|
| Day27 initial human semantic | 4 PASS / 4 PARTIAL / 2 FAIL, unchanged |
| Day27 approved follow-up | 5 PASS / 5 PARTIAL / 0 FAIL; five carried-forward assignments, not an untouched holdout |
| Day28 | five Codex simulations, not five students; owner separately reported two positive informal student impressions, not formal Study A/B or measured gains |
| Day29 | 515/515 in that stage, supported by its committed evidence |
| Original limited-public | 548/548 in its original evidence, not a new Day30 result |
| Later Cloud fix | owner-reported 53 focused / 553 full; local `.post29-local/cloud-fixes-focused.log` and `cloud-final-regression.log` corroborate 53 and 553 with 0 real calls; separate from 548 |

Do not add these denominators. [Day27 approved review](day27/post_fix/human-approved-completion.md),
[Day28](DAY28_EVIDENCE.md), [Day29](DAY29_EVIDENCE.md),
[limited-public evidence](public-release/EVIDENCE.md) retain their actual context.

## Screenshots, presentation and release

Six real local screenshots: [landing](day30/01-landing.jpg),
[harmonic](day30/02-harmonic.jpg), [updated wave](day30/03-harmonic-updated.jpg),
[source](day30/04-projectile-source.jpg), [drag](day30/05-projectile-drag.jpg),
[roundtrip](day30/06-source-roundtrip.jpg). No synthetic frames or optional video.
[Asset notes](day30/ARTICLE_ASSETS.md), [3-minute/60-second script](day30/DEMO_SCRIPT.md),
[competition overview](day30/COMPETITION_OVERVIEW.md),
[development decisions](day30/DEVELOPMENT_DECISIONS.md),
[fair ChatGPT comparison protocol](day30/FAIR_COMPARISON.md).
The comparison was not run; no fake baseline or superior learning-gain claim.

The initial preparation predated the normal push and Cloud checks. Subsequent
deployment observations below retain their original dates; the latest Cloud
status is in the 2026-10-20 follow-up. The agent did not change sharing; the owner
enabled Public before the final anonymous follow-up.

Run from repository root: `python -m streamlit run app.py`.
Paid AI remains disabled (`VLL_LIVE_AI=""`). No model/key, OIDC, secrets, Neon,
ledger initialization/reset, spending policy or release gate was activated.


## Deployment observation — 2026-10-15

Code commit `650f2dad8926b4eac5705c3b3cd4227036de32c5` was pushed normally:
`9502c4b..650f2da HEAD -> main`. Cloud logs confirm a GitHub pull and dependency
processing at 20:16 UTC on Oct 14 (04:16 Oct 15 Asia/Taipei). The fresh browser
then displayed **ImportError: cannot import name attribution from prepared_demo**.
The committed module defines that function; an in-place update retaining an old
imported module is the working explanation, not yet a verified restart result.
Existing server logs identify Python 3.12.15 / Streamlit 1.65.0. Earlier unrelated
warnings/errors remain historical; they are not called new Day30 failures.

Manage app → menu → Reboot app exposed a confirmation warning that all current
users would be disrupted. Automatic approval review rejected confirmation because
explicit authorization for that production interruption was missing. **No reboot
was executed.** Owner approval has been requested; alternatively the owner can
perform Manage app → menu → Reboot app → Reboot manually. No sharing, secrets,
OIDC, ledger or paid-mode setting was changed. Cloud acceptance remains pending,
and local tests/screenshots are not presented as Cloud success.

Cookie-free HTTP probes returned root 303 and the probed app-shell path 404;
those are inconclusive for anonymous interactive acceptance, not a public-access
PASS. The actual fresh browser reached the app's error page without invoking
Google login. Final anonymous/demo acceptance requires a recovered app and real
interaction. [Deployment record](day30/cloud-acceptance.json).

## Authorized Cloud follow-up — 2026-10-20

Owner explicitly authorized exactly one Reboot app, including interruption of
active sessions. It was executed once: Cloud logs show a new main clone/pull at
01:20:45–46 UTC and server start at 01:21:00.459 UTC (09:21 Asia/Taipei), Python
3.12.15 / Streamlit 1.66.0. Remote main was
`b66f07002349f905981d9d831f539a76df3f0c02`. Cloud logs do not expose a process Git
SHA; fresh clone/pull of main plus the unchanged remote SHA is the revision
evidence, not a claim that an in-process `git rev-parse` was obtained.

ImportError did not recur. The landing already worked when first opened this
day before the authorized reboot, so this does not prove the reboot itself was
the causal repair. Post-reboot logs have no ImportError/uncaught traceback, with
nonblocking `use_container_width` deprecation warnings. No runtime fix or further
reboot was needed.

Harmonic: actual separate slider commits A=5, T=6, phi=-pi; rendered SVG curves
changed, shift=3, omega=1.0472. Projectile: physical drag (370,298)→(415,240), release,
wait for acknowledgment, then verify canonical UI table: speed 20→60.895 m/s,
angle 45→49.519 degrees, maximum height 12.204→111.46 m, impact time 3.0212→9.4956 s.
The full spatial trajectory and height/time polyline changed against an independent
default session. The first attempt missed after page movement and did not commit;
tentative preview values were not counted as committed results.

Source roundtrip and reopening Explore preserved the exact displayed committed
metrics. The original page-4 PNG equals the independent unexplored session byte
for byte: SHA-256 `222f7857f26d5e74bf1e6a0bcf988ed32a06b948f4d0cb3344e54a025c44455d`.
This is Cloud page-raster integrity evidence, not a newly downloaded full-PDF hash.

**Access limitation:** New Streamlit sessions were app-Google-unsigned-in, with
the sign-in button and server-paid-off caption visible. The browser still has
Cloud owner authentication. Read-only inspection of Share → Invite after loading
showed **Make this app public unchecked** (`input.checked=false`). Thus both
Cloud functional paths passed in the owner-accessible browser, but genuine
public anonymous acceptance did not pass. No cookie-isolated incognito profile
was available through the browser interface. Sharing was not changed.

Owner action, only if a public showcase is desired: Share → Invite → turn on
Make this app public, then test the app URL in a fresh incognito browser without
Cloud or Google sign-in. That permission change is outside this reboot grant.

No Secrets, Neon, OAuth, spending policy or VLL_LIVE_AI change; no model-generating
action was taken. Zero-call assurance uses the paid-off UI, audited fixed loader
and local reducers, and the existing mocked request-boundary regressions. No
Cloud provider billing/Neon audit was performed. Real screenshots, bounded DOM
witnesses and numerical results: [Cloud acceptance](day30/cloud-20261020/ACCEPTANCE.md).

## Public anonymous acceptance — 2026-10-20, after owner changed sharing

The owner reported changing Cloud sharing to Public. No sharing permission was
changed by the agent. Since the available browser has no incognito/profile or
cookie-clear interface, the agent signed out through Cloud's normal account UI,
verified **Continue to sign-in**, closed both existing app tabs, then opened two
brand-new app sessions. The public app had **Fork** and **Hosted with Streamlit**,
with no Manage app/Share owner controls. Cloud still showed sign-in after a
reload at the end. App Google login was never used. This establishes actual
logged-out anonymous access, not an assertion that all unrelated browser cookies
were deleted or that an independent incognito profile was available.

Harmonic: actual slider actions changed A=3→5, T=pi→6, phi=pi/4→-pi, with each
commit awaited separately. The visible graph and rendered line hashes changed;
settled shift=3 and omega=1.0472, with the fixed source reference still visible.

Projectile: selected Initial horizontal velocity and Figure 5.3, then physically
dragged the endpoint (370,448)→(415,390), released and waited for the canonical
table. Settled speed=61.066 m/s, angle=49.656 degrees, vx0=39.5327 m/s, maximum
height=112.52 m and ground-impact time=9.5412 s. Both space and height/time
polylines changed from the same session's actual pre-drag DOM. Returning to the
source and reopening Explore preserved the exact displayed committed metrics.
Page-4 PNG bytes before/after match SHA-256
`39951cfb15f3ea501012863a8849891ecd5579c8dd3ac6f6693a55f7de20d524`.
This run's raster hash is distinct from the earlier owner-session run; only each
run's direct before/after equality is claimed. No original PDF content was edited.

Cloud UI explicitly showed prepared mode / server-disabled AI and a disabled
Analyze action. The agent made no model-generation action or provider request.
Fixed prepared loading and local reducers reuse the existing request-denial
regression evidence; there was no Cloud billing or Neon audit. VLL_LIVE_AI,
Secrets, Neon, OAuth, USD10 budget and dependencies remain unchanged. No new
feature, runtime patch, reboot or test suite was run during this public follow-up.
The earlier 110/562 results retain their dates; they are not new test counts.

Ten authentic screenshots and bounded machine-readable evidence are under
[public Cloud acceptance](day30/cloud-public-20261020/ACCEPTANCE.md). Earlier
private-phase evidence is retained with its original limits. Only reviewed
documentation, screenshots and evidence JSON are included in the release;
unrelated logs, corpus, bytecode, private account details and secrets are excluded.
