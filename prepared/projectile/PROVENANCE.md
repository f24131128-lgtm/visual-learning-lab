# Day26 archive derivative, preparation v1.0

Owner explicitly approved this derivative in the Day30 conversation, 2026-10-14
Asia/Taipei. This is **not an unmodified historical model response**.

Inputs: the actual `.day26-local/open-twin.json` observation of the accepted
English Day26 session; its analysis, normalized scene and normalized Atlas were
still available. The observer caveats and first rejected pass remain in
[Day26 evidence](../../docs/DAY26_EVIDENCE.md). The original accepted raw scene
response was not reliably retained by the overlapping response observer. The
normalized accepted scene snapshot is available; this distinction is preserved.

The original full MIT Chapter 5 PDF was re-fetched from its public OCW URL and
matches the historical 2,316,314-byte SHA-256 exactly. No PDF page, metadata or
source text was rewritten. All sixteen pages remain in the asset, with citations
limited to the original eight analyzed pages. Atlas pages remain 4, 5 and 6.
Figure 5.3 is PDF page 4 / printed page 3.

`archived_scene.json` is the extracted historical normalized scene, including its
original validation report. `analysis.json` is the archived analysis, not a newly
invented successful response. `atlas.json` removes only derived validation fields
so the original declarative regions can be revalidated. Region IDs, boxes,
confidence, pages, excerpts and semantic links are unchanged. The original local
session file itself, request records and unrelated corpus are never packaged.

The independently authored deterministic preparation tool:
`python -X utf8 -B tools/prepare_day30_projectile.py --archive .day26-local/open-twin.json --pdf ORIGINAL.pdf`

This explicit command makes no model request. It requires the reviewed original
PDF hash, exact archive snapshot hash and scene/version. A fresh clone runs from packaged assets;
it never needs ignored archives or imports test fixtures.

## Exact derivative changes

- World declaration version 2.2 → 2.4; remove derived `quantity_order`, viewport,
  `parameter_kind` and validation fields from the compiler declaration. Current
  normalization recomputes these through unchanged production validation.
- Add empty `source_facts`. Figure 5.3 supports the velocity decomposition, not
  the assumed numerical demonstration values. No numeric source assertion is
  invented.
- Add `hypothetical_exploration` to all four parameters with an explicit note,
  null `source_baseline_ref`, and `expose_control` only where the archived range
  is adjustable. The archived singleton gravity=9.8 stays read-only; it is labeled
  as a model assumption, not a verified numerical quotation on pages 5–6.
- All ranges are explicitly pedagogical, including singleton gravity; speed,
  angle and acceleration retain positive domains, height is nonnegative. Archived
  ranges, steps and defaults stay exact (height min remains 0.5 in THIS archive).
- DAG quantities declare `derived`. No formula, binding, inverse, experiment,
  ID, time policy, parameter default/range, semantic owner or source link changed.
- Runtime starts from fresh compiled defaults/revision=0 rather than a historical
  participant's exploration. Initial semantic focus is unset; ambiguous Figure
  5.3 links require a learner choice. Existing reducers and guards remain owners.

`manifest.json` records the original local snapshot hash and every bundled asset
hash. These support reproducibility; they are not a signed independent audit or
proof of grounding accuracy. Current runtime revalidates the derivative and Atlas.

## Educational source and terms

MIT OpenCourseWare, 8.01SC Classical Mechanics (Fall 2016), Peter Dourmashkin /
MIT course team, Chapter 5: Two Dimensional Kinematics.
[Resource](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter5/)
· [Original PDF](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/mit8_01scs22_chapter5.pdf)
· [OCW terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/)
· [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)
· [Legal code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).

Prepared educational material and reproduced source portions are offered for
noncommercial use under these terms; retain attribution and applicable ShareAlike
obligations. UI overlays/declarations are additions. No MIT endorsement. This is
an engineering source/notice review, not legal clearance of every deployment or
past distribution. Commercial use requires separate permission/review. Software
licenses, PDFium binary notices, and historical PyMuPDF obligations are separate.
