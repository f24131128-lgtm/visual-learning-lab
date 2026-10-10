# Day 26 checkpoint — reviewable product proof

Starting branch `day17-learning-scene-wip`, HEAD
`336d1c8f4cb17642cc131d3c220b3fb68c5e9a6a`; initial tree clean.
No checkout, reset, commit or push. Changes await human review.

Day 26 stays inside the Day25 architecture: existing source evidence, semantic
catalog, canonical World, structural inverse and fixed renderers. The real MIT
OCW Chapter 5 pass reached Source → `vx0` → initial velocity vector → real drag
release → synchronized world views → unchanged Source. Explicit `x_position`
selection remained grounded without a fake handle. Full measurements, failed
first pass, observer caveat and human acceptance boundary are in
[DAY26_EVIDENCE.md](DAY26_EVIDENCE.md).

## Changes

| Files | Purpose |
|---|---|
| `app.py`, `i18n.py`, `workspace/twin_ui.py` | Clear next actions after analysis and concise source/drag microcopy, translated through the existing layer. |
| `workspace/ui.py`, `source_atlas/runtime.py` | Move the existing ambiguity selector next to evidence; preserve deliberate semantic choice. |
| `source_atlas/compiler.py` | Preserve selected Atlas pages across view/widget cleanup using existing cache identity; exclude local focus from ranking defaults. |
| `scene/world/runtime.py` | Remove server keyboard fallback, recording/replay and camera/static expanders; use an automatic planar fallback on component failure. Internal runtime/reducer contracts remain. |
| `scene/world/frontend/index.html` | Compact playback/speed/time/comparison toolbar; hide recording/replay/camera controls under production learner payload. Fixed local controls and safe internal handlers remain. |
| `scene/world/schema.py` | Clarify existing experiment target/range rules in compiler instructions only. No schema/version/validation relaxation. |
| `tests/test_day18.py`, `tests/test_day24.py` | Migrate removed-widget checks to existing validated component event/state contracts. |
| `tests/test_analogy.py`, `tests/test_day18_compiler.py`, `tests/test_day18_consolidation.py`, `tests/test_day19.py`, `tests/test_day19_optional_scene.py`, `tests/test_day20.py`, `tests/test_day21.py`, `tests/test_day23_phase_c.py`, `tests/world_events.py` | Repair older UI assertions discovered by the one full regression; retain numeric, source, policy and request checks through the same production event boundary. |
| `tests/test_day26.py`, `tests/world_frontend_smoke.cjs` | Presentation, local next actions, failure isolation, source ambiguity/subset regressions, retained rejection shapes and hidden frontend controls. |
| `tests/manual_day26.py`, `.gitignore` | Empty real-pipeline acceptance observer; ignored private source/response diagnostics. No seeded material or production debug UI. |
| `README.md` | Day26/30 front door: concise product/pipeline, current capabilities, 90-second demonstration, run command, compact evolution and honest limits. |
| `docs/DAY26_EVIDENCE.md`, `docs/DAY26_CHECKPOINT.md`, `docs/day26/*` | Reviewable evidence, bounded numeric/console traces and exactly four screenshots. |
| `docs/OPEN_SOURCE_REUSE_LEDGER.md`, `THIRD_PARTY_NOTICES.md` | Reconfirm retained dependencies and attribute the teaching material; no dependency change. |

The normal Explore view no longer offers Keyboard parameter fallback, Keyboard
time fallback, 3D/static engineering controls, Exploration Recording & Replay,
recording counters or recorded-step UI. Play/Pause/Reset time, 0.5/1/2 speed and
baseline comparisons remain in a compact toolbar. Automatic failure fallback
preserves current learning state. Main PDF/text analysis, languages, lessons,
quizzes/review, explanations, Graphviz, labs, probability/process/execution,
simulation, source rendering and internal replay are retained.

No new dependencies. `requirements.txt`, optional document requirements,
vendored libraries and their manifests are unchanged. PyMuPDF deployment
licensing remains unresolved, and screenshot source content is attributed under
MIT OCW CC BY-NC-SA 4.0 terms.

## Validation and review gate

- Focused suites: 80 passed; after live fixes, final Day26 subset: 6 passed.
- One completed full regression: 437 tests / 300.886 s, 427 passed and 10 older
  removed-widget errors. All ten were repaired and passed subsequent focused
  checks (26 Analogy tests + the other nine failing cases). No second full run;
  a completely green final full run is not claimed.
- Browser: actual real-material drag/commit/synchronization/roundtrip/control and
  Play/Pause/Reset passed at desktop and narrower viewport; console caveats are
  retained in evidence.
- Post-compilation interaction API delta 0. Seven audited explicit generation
  actions across the failed and successful passes; accepted-scene timing and
  independent transport total were not reliably measured by the initial observer.
- Human acceptance: not yet performed. The proposed 90-second script excludes
  generation time and is not a measured novice guarantee.

Run from the repository root:

```powershell
python -m streamlit run app.py
```

Review the four screenshots and repeat the compiled-material path before
competition presentation. Stop here; no publishing or repository commit was
authorized by this task.
