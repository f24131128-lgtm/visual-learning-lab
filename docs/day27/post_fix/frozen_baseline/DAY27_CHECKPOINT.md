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
