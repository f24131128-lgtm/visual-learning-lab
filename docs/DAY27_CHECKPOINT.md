# Day 27 checkpoint — stopped for human semantic review

Starting branch `day17-learning-scene-wip`, HEAD `477de4926220d0960b58500f292ea6df24154da6`; initial tree clean. No checkout/reset/commit/push. This checkpoint is the three-stage frozen baseline, not completion of failure-driven hardening.

Pre-benchmark changes already frozen before any response:

| Files | Purpose |
|---|---|
| model_config.py; app.py; learning_world/compiler.py; scene/compiler.py; source_atlas/compiler.py; analogy/compiler.py; dynamic_simulation.py | One production `gpt-6.1-sol` / `medium` request configuration across all eight Responses call sites. |
| scene/world/schema.py, policy.py, engine.py, validator.py | Separate quantity kind from explicit positive/non-negative/signed domain; enforce declared bounds in compilation and local state. |
| tests/test_day27.py; tests/world_fixtures.py; tests/test_day26_parameter_semantics.py; tests/test_day23_phase_c.py; tests/manual_phase_c.py | Model/domain regressions and current-version copies of historical fixtures. Historical Day26 evidence/declarations remain unchanged. |
| .gitignore | Ignore .day27-local corpus/request/browser files. |

Benchmark/report files added: tests/day27_sources.py, day27_freeze.py, day27_benchmark.py, day27_browser.cjs, day27_report.py, manual_day27.py, test_day27_benchmark.py; docs/day27/ frozen manifests, raw results, usage, source evidence, review packets, independent B scorecard, drift comparison, taxonomy and hashes; DAY27_EVIDENCE.md and this checkpoint. README status/Day27 row and THIRD_PARTY_NOTICES attribution are documentation updates.

All production changes listed above preceded the frozen baseline. No benchmark-driven production change has been made. All ten first attempts and all twelve stability samples remain in their original denominators. A-axis verdicts remain exclusively human. Deep local mechanics do not establish complete compiled Twin coverage or source fidelity. Read [evidence](DAY27_EVIDENCE.md) before making product-quality claims.

No new dependency. Run the app exactly:

```powershell
python -m streamlit run app.py
```

Do not run another paid benchmark, harden failures, replay repaired cases, start Day28/29, commit or push until the user's next authorization. Frozen first-pass artifacts and expectations must remain unchanged.

## POST_FIX checkpoint — paused at the user's request (2026-10-11)

The user authorized exactly A/B hardening after freezing human A-axis results: PASS 4 / PARTIAL 4 / FAIL 2. Those results remain unchanged. Original bytes/hash of this document are preserved in `day27/post_fix/frozen_baseline/`; this section is append-only, as approved.

A/B implementation is in progress. Latest focused checkpoint: 65 tests passed, 0 failures/errors, 2.400 seconds. The earlier broader focused run exposed fixture/compatibility failures; repairs are made but a complete recheck of that affected subset remains pending. This is not a final full regression and does not establish source-semantic correctness.

Paid post-fix requests: 0. Captured-shape offline replay, bounded live replay, human review packet, one final full regression, and exactly four new screenshots have not begun. No commit or push. Candidate C planner ranking remains unchanged.

Continue from [resume checkpoint](day27/post_fix/resume-checkpoint.md) and [validation](day27/post_fix/validation.json). New evidence belongs exclusively under `day27/post_fix/`.

## POST_FIX completion — 2026-10-11

Authorized A/B hardening is complete and awaits human semantic review. The frozen baseline A remains PASS 4 / PARTIAL 4 / FAIL 2. Original document bytes/hash remain in `day27/post_fix/frozen_baseline/`; this is an approved append-only section.

Focused: 295/295. Offline: 10 cases, API 0. Live: 5 cases, 16 one-attempt Responses requests, no semantic/SDK retries. Browser: 5 source roundtrips, PDF/focus preserved, local API delta 0. Final full regression: 480/489, 252.150s, one actual complete run. Four screenshots are under POST_FIX.

Probability scene and RC planner rejection remain recorded. Regression and Signals Lab declarations exceed existing numeric bounds and fall back to formal/static. Candidate C remains unresolved and its planner files are unchanged. No commit/push/Day28.

[Human semantic review](day27/post_fix/post-fix-semantic-review.md) · [Implementation and limitations](day27/post_fix/implementation-summary.md) · [Validation](day27/post_fix/validation.json) · [Request usage](day27/post_fix/request-usage.json).

The single full run recorded 6 failures and 3 errors; its bytes/log are preserved. Later explicit test fixture/cache corrections passed 105/105 focused tests. Production code was unchanged and no second full discovery was performed.
