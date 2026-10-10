# Day 26 — height parameter validation fix

## Evidence and root cause

The learner's 2026-10-10 terminal log reports:
`Positive semantic parameter has a non-positive range: height`.
It contains no generated JSON or parameter policy fields. The compiler does not
retain rejected raw declarations. The available earlier Chinese projectile
capture declares `height` as `quantity_kind="length"`, fixed at 2 m, and was
rejected for an unrelated experiment error. It is **not** the declaration behind
this new report, so that original declaration cannot be certified as passing.

`scene/world/policy.py::normalize_parameter` emitted the reported error because
it grouped `length`, `speed`, `frequency`, and `acceleration` under the same
strictly positive range check. `height` in the error is just the parameter ID;
no ID/label classifier runs. Model-declared `quantity_kind` reaches this policy
through `normalize_world`; missing optional kinds default to `scalar`, not to
`length`. The source text and unit do not override a supplied kind.

An independently written projectile declaration with `height`, kind `length`,
range 0..10 m, default 0 m, positive launch speed/inclination/gravity, and a
derived ground-impact duration reproduced the exact reported error before the
fix. The same declaration now passes, starts at y=0, and ends at ground level.

## Changes

- `scene/world/policy.py`: separate non-negative `length` from existing strictly
  positive speed/frequency/acceleration. Reject negative length before fallback;
  accept fixed zero length. Zero-baseline semantic defaults use a bounded 0..1
  native-unit range; positive-baseline fallback ranges remain unchanged.
- `scene/world/schema.py`: clarify the existing kinds in compiler instructions.
  Ground-level initial height is a length with zero allowed. Signed coordinates
  require scalar declarations, an explicit range and a supported reference frame.
  The JSON schema, scene version and declaration normalization are unchanged.
- `scene/compiler.py`: add kind/range policy to bounded opt-in internal traces;
  keep source bodies and labels out. Keep rejection caching and expose explicit
  regeneration through the existing build button. Reruns/navigation make no call.
- `i18n.py`: replace failure copy in both languages. Traditional Chinese:
  「這次互動場景沒有通過安全驗證；原始教材與分析仍可正常使用。你可以重新產生互動場景。」
  Internal validation reasons remain in session diagnostics/logs only.
- `tests/test_day17.py`, `tests/test_day18.py`, `tests/test_day18_compiler.py`:
  update failure-copy/manual-retry expectations while retaining request checks.
- `tests/test_day26_parameter_semantics.py`: ten regression tests covering
  adjustable/fixed zero initial height, source/pedagogical/semantic-default
  policies, negative length, an explicit signed coordinate reference, strict
  positive kinds, ID independence, NaN/Infinity/bounds/expressions/duration,
  diagnostics, and explicit retry with unchanged material and stored language.

The fix does not infer physical source fidelity from labels or numeric sampling.
Mass and period have no dedicated parameter kinds in the current schema; no
existing range, expression, invariant or time constraints on them were relaxed.
Models singular at zero (for example `1/height`) still fail numeric validation.

## Validation

New targeted suite: **10 tests passed** (6.390 s).

Complete relevant suite: **141 tests passed** (66.929 s), covering `test_day17`,
`test_day18`, `test_day18_compiler`, `test_day18_consolidation`,
`test_day23_phase_c`, `test_day24`, and `test_day26_parameter_semantics`.
All compiler/API interactions in this run were mocked; no new real AI request
or certification of the missing original declaration is implied.

Reproduce the complete relevant suite from the repository root:

```powershell
$env:PYTHONPATH = 'tests'
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m unittest test_day17 test_day18 test_day18_compiler test_day18_consolidation test_day23_phase_c test_day24 test_day26_parameter_semantics -q
```

No new dependency. No UI redesign, commit or push.

Run the app from the repository root:

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m streamlit run app.py --server.port 8521
```
