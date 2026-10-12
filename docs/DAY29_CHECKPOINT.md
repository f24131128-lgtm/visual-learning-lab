# Day29 checkpoint — stop for human review

Local hardening and red-team work completed; one final full regression passed
515 tests in 355.853 seconds with zero provider calls. See DAY29_EVIDENCE.md and
docs/day29/final-validation.json for actual boundaries, artifacts and limitations.

Default mode is a prepared-only, noncommercial attributed demo candidate. Live
generation remains blocked publicly; `VLL_LIVE_AI=private` is only an explicit
server opt-in, not an authentication or aggregate budget system. Hostile-PDF
process isolation, cloud deployment, real paid model red team, legal review,
high-load behavior and narrow viewport acceptance are unresolved/not tested as
described in release-gate.md. Do not treat local all-green tests as source-fidelity
or public-live certification.

The source is immutable; existing local exploration, lessons, review, navigation
and caches are preserved. Historical Day27/28 frozen inputs were not rewritten.
Existing Day28 uncommitted changes remain; Day29 also remains uncommitted.
No commit/push, public deployment, credential revocation, purchase or Day30 work.

Run `python -m streamlit run app.py` from the repository after installing
requirements.txt. For audited offline tests, requirements-test.txt and the test
interpreter are separate from the production-only environment; use the recorded
request guard and no real key. The active loopback smoke server is for local
review only. Review the exact file inventory before any eventual commit.
