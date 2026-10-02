# Day 18 compiler → validator integration fix

2026-10-01, Asia/Taipei. No commit/push. No new dependency. This is a focused extension of the existing Day 18 implementation, not a runtime redesign or a change to Dynamic Simulation.

## What was actually reproduced

The user's original failed response was not retained by the old app; invalid output became a cached `None` and the reason was hidden behind a debug-only generic traceback. It cannot be forensically recovered from that session here. To avoid inventing a cause, two explicit, bounded real Responses requests used the exact Traditional Chinese acceptance text and the app's configured `gpt-5.6-luna` model. No PDF was resent and no main analysis request was made. The public-text input and both real compiler outputs are preserved as test evidence. They are never production fallbacks.

The first real response reproduced the same generic product rejection. An offline audit isolated the successive failures in the original implementation:

| Generated declaration | Exact rejecting rule |
| --- | --- |
| Currents `A*cos(omega*t+phase_a)` etc. | `t` is undeclared; the only canonical time expression variable is `time` |
| Inverse `rate_expression="omega"` | Inverse rate/offset expressions accept parameter IDs/constants, not derived quantity IDs |
| Recipe `set_focus` target `resultant_field` | Focus patches require a canonical quantity, not a representation/object ID |
| Axes ±2, legal amplitude up to 10 | Phase/resultant endpoints exceed the fixed viewport at legal parameter corners |

The first reason is now reported precisely as:

`scene.quantities[ia].expression: Unknown expression reference: t.`

The source mathematical notation `t` itself is valid; the compiler must translate it into the declared DSL's `time`. The normalizer does **not** rewrite unknown variables into time or infer undeclared parameter names.

Both the compiler request and validator imported the same `WORLD_SCHEMA`; there were not two conflicting JSON schemas. The mismatch was between a syntactically valid Structured Output and stricter local semantic constraints insufficiently specified to the model. Separately, both schemas incorrectly required nonempty inverse/invariant lists, even though a base workspace should not require Ultra capabilities.

## Canonical contract and normalization fixes

- Spatial schema/cache revision is **2.1**. This separates old cached failures without automatic requests or weakening at-most-once compilation within the current identity.
- Compiler instructions/schema descriptions specify literal `time`, declared ASCII identifiers, global uniqueness, exact canonical bindings/focus targets, parameter-only inverse arithmetic and viewport coverage over the entire legal range. Short oscillation windows and a visible boundary margin are requested.
- `inverse_bindings`, `invariants` and `experiments` allow empty lists. Only missing optional top-level capability lists receive `[]` defaults before strict validation. Missing base fields, unknown extra fields, supplied `null`/malformed lists and unsafe entries remain rejected.
- An optional recipe focusing a **declared** representation may normalize through that representation's already-validated `semantic_id`, exactly as selection does. Unknown IDs, wrong operations, invalid parameters/values and broken bindings still fail. This is generic reference normalization, not a hardcoded motor alias or an expansion of reducer patch grammar. The canonicalization is recorded in the internal validation report. Raw input is not mutated.
- The second real response placed the resultant exactly on an axis border. Its floating-point sum was `3.0000000000000004` against `3`. Viewport comparisons now allow **16 machine ULPs at the axis scale**, while retaining finite-value and absolute coordinate safety bounds. There is no geometry clipping, automatic viewport resizing or broad percentage tolerance. Regression tests still reject `3 + 1e-8` and a genuinely undersized viewport.
- Detailed field paths/reasons are retained in active session state and terminal warnings. `VLL_SCENE_DEBUG=1` enables bounded compiler declaration traces scoped to the scene logger; it does not enable OpenAI SDK logging. Product UI remains concise, localized and free of raw specifications, IDs or tracebacks. Compiler result/domain/primitives/parameters/bindings/expressions/inverses/invariants/views and runtime dispatch are traceable internally.
- A base scene without inverses gets a localized selection/waveform hint rather than an unavailable vector-drag instruction. Other Ultra controls remain runtime-owned or appear only when their declaration exists.

Strict Structured Outputs keeps every wire key required with `additionalProperties: false`; optional capability **content** is represented by empty arrays. This preserves the strict API boundary while making features progressive. The official [OpenAI Structured Outputs documentation](https://developers.openai.com/api/docs/guides/structured-outputs) was checked with the OpenAI Docs skill rather than removing required wire keys.

## Real response and runtime outcome

The improved real response used canonical `time`, parameter-only inverse arithmetic and a compact legal range. After safe representation-focus normalization and the roundoff fix, the **unchanged captured response** passes validation:

- 7 spatial objects: 3 reference axes, 3 phase vectors, 1 resultant;
- 3 phase waveform series;
- amplitude/frequency parameters, equation/state metrics and canonical time;
- 90 shared animation frames;
- 4 declared invariants, 9 parameter scenarios, **630 sampled invariant comparisons**;
- validated angle-to-time inverse;
- generic runtime numeric payload successfully prepared.

AppTest then feeds that actual recorded compiler response through the normal repository-root `app.py` result/build/validator/runtime path. It is not a substituted handcrafted demo. A second regression removes Ultra declarations entirely and verifies a valid minimal workspace is reachable, with local parameter/time interactions making no additional API request.

This proves one real generated declaration can enter the product runtime and that base capability gating is fixed. It does not promise every future stochastic compilation will be valid. Unsafe or physically inconsistent future output must still fail safely with a useful internal reason. Human live testing is still required for perception, interaction and source fidelity.

## Tests

Added 15 regressions in `tests/test_day18_compiler.py` covering:

- canonical strict wire schema and empty optional capability arrays;
- missing optional fields/defaults and non-mutating normalization;
- every missing required base field and unknown extra fields;
- malformed supplied Ultra fields, false invariants and invalid inverses/recipes;
- invalid primitives/bindings, undeclared `t`, unsafe calls/attributes, non-finite division and malformed syntax;
- valid three-phase expressions, balanced-current sum, resultant magnitude and shared projections;
- real-response recipe reference normalization, unknown-reference rejection and strict reducer focus IDs;
- precise diagnostics for the captured original response;
- ULP-only viewport handling with meaningful overflow rejection;
- exact Traditional Chinese context, strict compiler schema and internal trace;
- Day 17 probability validation;
- minimal and actual real-response normal app runtime reachability;
- rejection reasons remaining internal while earlier analysis survives;
- old rejected-cache invalidation without an automatic request.

The old Day 18 red-team case that rejected an empty inverse list was corrected to reject a malformed supplied inverse list instead; its 54 meaningful rejection cases remain. All prior functionality/regressions remain in the complete suite.

Focused command:

```powershell
python -B -m unittest discover -s tests -p 'test_day18*.py' -q
```

**48 passed in 27.690 seconds.**

Final full command, run once after the focused suite:

```powershell
python -B -m unittest discover -s tests -q
```

**120 passed in 99.156 seconds, no skips**, including the existing 19 Day 17 tests. `git diff --check` also passed; only the repository's existing LF/CRLF normalization warnings were emitted.

## Files changed in this debugging pass

- `scene/compiler.py`: bounded internal trace, precise rejection/session diagnostics.
- `scene/state.py`: clear stale diagnostics on accepted spatial scene.
- `scene/world/schema.py`: canonical 2.1 contract, progressive Ultra lists and descriptions/instructions.
- `scene/world/validator.py`: optional defaults, field paths, validated recipe focus normalization.
- `scene/world/engine.py`: exact unknown-reference reasons and ULP-only viewport comparisons.
- `scene/world/runtime.py`, `frontend/index.html`, `i18n.py`: truthful localized base-scene interaction hint.
- `tests/world_fixtures.py`, `test_day18.py`: schema version and updated optional-capability expectation.
- New `tests/day18_acceptance.py`, `test_day18_compiler.py`, `probe_day18_compiler.py`, `diagnose_day18_rejection.py` and two public-text captured response fixtures.
- `README.md`, `AGENTS.md` and evidence documents: contract, diagnostic rules and this report.

No new dependency, no secrets changes, no homepage redesign, no Dynamic Simulation changes. Earlier uncommitted work is preserved.

## Exact next live test

1. Stop/restart the actual production Streamlit process from this checkout: `python -m streamlit run app.py`. Confirm you are not using `tests/manual_day18.py`.
2. Paste the exact three-phase text from the request, select Traditional Chinese, and analyze. Locate **建立空間學習場景** before the normal overview.
3. Build once. Schema 2.1 should not reuse the prior rejected 2.0 cache. Verify real spatial axes, contribution/resultant vectors, three waveforms and equation/state values—not Day 16's dynamic-simulation feature.
4. Scrub/click waveform time, change amplitude/frequency and select phase quantities. Check that every view represents the same state. When the generated scene declares a valid inverse, rotate the resultant handle and confirm time/currents follow; a base scene without an inverse should still render normally.
5. Check baseline/source context and any generated recipes. Recipes may require an existing baseline if their first step restores one. No local exploration should call OpenAI or regenerate the scene.
6. If rejected, retain the terminal line `Learning Scene validator rejected ... reason=...`; do not broaden validation. For a development-only full declaration trace, set `$env:VLL_SCENE_DEBUG='1'` before launching, and remove that environment setting afterwards. Never paste credentials or private source dumps into a report.
7. Recheck the Day 17 probability scene. Its domain/schema/cache and set engine were not changed by this fix.
