# Day 25 checkpoint — Grounded Semantic Twin

2026-10-09, Asia/Taipei. Source ↔ Twin roundtrip is stable in automated desktop acceptance. No commit, push, reset or new runtime dependency.

## Recovered baseline

Repository `D:\Projects\visual-learning-lab`, branch `day17-learning-scene-wip`, clean starting tree, HEAD/upstream `7b8a30de3515fe127041d617554908cded73aa28`. Git log/remote verified. The saved Day24 full regression was 409 tests / 212.103s. Day24 focused baseline: 21 tests / 16.022s. Existing Day23/24 architecture and documentation were inspected before edits.

## Architecture and behavior

Validated Atlas regions → existing semantic ID → existing representations and Day24 targets → existing World/Lab state. `workspace/grounded_twin.py` derives ephemeral bounded joins. `workspace/twin_ui.py` displays a compact inspector with geometry provenance, compiled baseline/current/delta and Source/Explore navigation. Neither module owns focus, state values, an AI cache or another schema. Ambiguous source meanings require explicit selection. Exact target ID/semantic ID/object membership and source-page overlap are required; dependency links do not create an inverse.

Source bytes, text and region geometry stay immutable. Compiled defaults are explicitly model values, not independently verified source numbers. Native geometry means a unique exact whole-line match through the existing PDF-hashed parser envelope; meaning remains estimated. Page-only evidence never gains a box. Unsupported entities retain formal views and old controls.

Existing fixed SVG viewer now focuses bounded regions, centers through actual viewport geometry and preserves zoom/scroll across reruns. Current scrolling/zoom is retained; OpenSeadragon is deferred, with no claim of latency or touch parity. Three.js/3D is deferred in favor of validating source-to-affordance fidelity.

Real desktop tests passed phase, projectile, affine and non-manipulable cases; original three-page engineering PDFs have unequal page sizes. Actual pointer drags, source iframe clicks, target highlighting, rejection restore and source roundtrips were tested in isolated Edge contexts with paid SDK calls blocked. Numeric Lab's discovered stale slider overwrite was repaired with retired control generations; the old safe evaluator and canonical stores remain.

## Evidence status

- Focused Day24 + Day25: **40 passed / 19.404s**.
- Affected Day20/21/23/24: **124 passed / 72.009s**, before the final slider fix; the complete regression covers the final code.
- Source Atlas suite: **30 passed / 13.313s**, including fixed frontend smoke.
- Desktop normal-app browser: four cases pass, zero page errors, zero interaction model requests.
- Touch emulation: 390px viewport; source tap, endpoint release and outer scrolling pass. Handle hit width 18px; real phone ergonomics remain pending.
- One paid existing Atlas probe: **9,118 input + 2,407 output = 11,525 tokens**, no SDK retries. Fourteen accepted regions, no dropped regions. The bridge needs no additional request.
- Full regression ran exactly once after stable production code: **428 passed / 226.441s**, `day25-regression.log`. No failures/skips reported.
- Real-world PDF fidelity and learning benefit remain human-pending. Exactly three human checks are specified in the evidence document.

## Files and commands

New production files: `workspace/grounded_twin.py`, `workspace/twin_ui.py`.
Integrations: `app.py`, `workspace/ui.py`, `source_atlas/{state,runtime}.py`, source frontend, `manipulation/{runtime,lab}.py`, manipulation frontend, `interactive_lab.py`, `i18n.py`.
Tests: `test_day25.py`, `twin_fixtures.py`, `manual_day25.py`, four browser/measurement scripts plus model probe; adjusted Day19 ambiguity expectation and frontend smoke. Documentation: this checkpoint, evidence, reuse ledger, AGENTS, bounded logs/JSON/screenshots.

```powershell
python -m streamlit run app.py
python -X utf8 -B -m streamlit run tests/manual_day25.py --server.port 8528
python -X utf8 -B -m unittest discover -s tests -p test_day25.py -q
```

The offline harness disables paid actions and seeds the normal app; it is not production code. No changes to requirements, third-party notices or pinned JSXGraph assets.
