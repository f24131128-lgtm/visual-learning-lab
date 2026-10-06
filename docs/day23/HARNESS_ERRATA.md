# Phase A harness erratum (before production edits)

The first real-model run is preserved unchanged under `phase_a/`. It generated
real responses against the Day22 production fingerprint. Review found that the
benchmark's final shared-focus navigation probe supplied an empty `{}` wrapper.
The production reducer correctly rejects a wrapper belonging to no material.
This created spurious R2 results after successful local process/numeric probes.

The correction supplies `{material_id: case_id, scene: null}`, just as production
does. It does not change corpus, gold, responses, model, production behavior or
compiler validators. The original results are **not** overwritten.

`phase_a-audit/` replays the same saved model declarations against unchanged
Day22 production, with zero new paid requests. Its corrected mechanical-runtime
results are the Phase A baseline for comparisons. The original `phase_a/`
request attempts/token usage remains authoritative for API accounting.

The first sandbox tooling test also encountered Windows temporary-directory
permissions. Workspace temporary directories and outside-sandbox execution
passed all 11 tooling tests; this is environment evidence, not a product fix.

Both initial and audited results keep human source fidelity, human gold approval
and browser visual-quality review as pending; canonical-reference validity is a
narrower automated measurement. Normal-learning fallback in the runner means
analysis retention; actual UI isolation is separately checked with AppTest.

## Phase B optional-artifact distinction

The first Phase B runner attempted to compile a spatial scene whenever the main
analysis advertised a spatial candidate, even if the planner chose dynamic and
a validated numeric lab already existed. This is stricter than production:
the lab is locally available, and the separate spatial build button is optional.
For damped motion this produced a rejected rich artifact (fixed constants were
declared as zero-span parameters), but did not remove its usable numeric lab.

The original Phase B responses/results and both specialized request attempts
are retained. `phase_b-audit/` replays the same declarations with zero new calls,
counting the ready numeric lab as the selected dynamic artifact. Required
spatial/structural artifacts still go through the same strict scene validator.
The failed optional spatial attempt remains a documented compiler limitation.
No production or gold change occurs in this correction.
