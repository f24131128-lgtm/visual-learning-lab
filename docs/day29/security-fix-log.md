# Failure-driven fix log

| Priority / finding | Root cause → minimal correction | Regression / evidence |
|---|---|---|
| P0 public paid-abuse risk, confirmed unprotected request path | Key-configured app permitted owner-paid generation without trustworthy identity/rate/spend control → server factory defaults to denied; UI generation/upload gates; private opt-in retains workflow | Configured synthetic key default-deny test, no-key clean browser, all eight constructors/routes audited. Public live remains blocked. No observed exploitation/billing leak is claimed. |
| P0 production licensing blocker | Production Source Lens imported PyMuPDF → independent PDFium renderer/search adapter; test-only comparator dependency; retain native licenses | Rotation/crop/multipage/image/native-highlight parity; clean no-PyMuPDF Source/Atlas browser. Historical legal obligations not cleared. |
| P1 failed analysis destroys previous learning | Main cleared session before input/API success → validate staged source/response first, atomically replace afterward | Nine main failure scenarios preserve prior source/material exactly; source roundtrip stays local. |
| P1 unbounded source/response/graph envelopes | Main extraction/SDK defaults did not bound total text/page/response/graph work → byte/page/object/text/JSON/graph bounds, 16k output (simulation 8k), zero retries/90s | File attacks, duplicate/deep/nonfinite/incomplete JSON, malformed base, excessive graph; safe generic failures. Input bounds are not a hostile-PDF sandbox. |
| P1 prepared deployment depends on ignored corpus | Test-only Day28 loader reads .day27-local → package same verified declarations/source with hash manifest and production loader | Product-only staging without tests/corpus, prepared load/parameter/Source PASS. No regenerated or fabricated content. |
| P2 existing tracked bytecode / warnings / mobile evidence gap | Old bytecode is tracked; Streamlit deprecation warnings; viewport override did not apply → ignore future bytecode, exclude it in staging, restore only our generated changes; accurately mark narrow test NOT TESTED | Git before/after, clean source copy; viewport dimensions saved. No cosmetic refactor or mobile claim. |

Initial Day29 failures also exposed implementation errors introduced during this
work: a function-local policy import, missing PDFium close context, duplicate
simulation output option and misplaced Explain source check. They were corrected
and the affected focused suites passed. An XSS test initially assumed all titles
must be rejected; fixed-host encoding permits suspicious strings as inert data,
so the test now verifies escaping/text sinks rather than weakening validation.

Unresolved: hostile-PDF process isolation/private upload protection, distributed
rate/concurrency/spend enforcement, live file-retention cleanup, native bundled
advisory coverage, real model prompt-injection behavior, cloud/mobile/high-load
testing and historical license review. No source/provenance/ownership validator
was weakened to make the prepared material pass.
