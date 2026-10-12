# Day29 evidence — local production hardening

Starting branch `day17-learning-scene-wip`, HEAD/origin main
`5a6ec3c8ab6e70892b2d6a299a7ef315e90cf40d`. Five tracked files were already dirty
and Day28 evidence/tests plus control_navigation.py were untracked. Those inputs
were preserved; historical Day28 hashes remain PASS. No commit, push, paid AI,
public deployment, license purchase or credential rotation.

Final complete command: `python -X utf8 -B -m unittest discover -s tests -q`.
**515 tests, 355.853 seconds, OK, zero failures/errors.** Offline outer guard:
zero provider calls and zero unexpected requests. See
[final validation](day29/final-validation.json), [full log](day29/final-regression.log)
and [guard](day29/final-request-guard.json). Initial failures and repair logs are
retained, not presented as successful runs.

Confirmed findings: default publicly reachable generation could use an owner's
credential without aggregate spending controls; AGPL production dependency was
an unresolved distribution blocker; failed replacement analysis cleared prior
state before success, and source/response resource envelopes were insufficient.
The mode gate, transactional install, finite envelopes and independent PDFium
adapter address the recorded engineering issues. Prompt injection, malformed
JSON/specs, XSS strings, forged semantic owners and stale events were adversarial
tests, not confirmed credential theft or arbitrary-code execution incidents.

Evidence map:

- [Threat model](day29/threat-model.md), [red-team matrix](day29/red-team-matrix.md),
  [fix log](day29/security-fix-log.md), [failure injection](day29/failure-injection.md).
- [Secrets](day29/secrets-audit.md): 885 current files and 1,128 reachable blobs,
  zero scoped key indicators; presence-only ignored credentials never copied.
- [Dependencies](day29/dependency-audit.md): fresh pinned closure of 54 production
  distributions, zero known advisories; [license decision](day29/license-decision.md)
  replaces production PyMuPDF, retains historical/test obligations and exact notices.
- [Cost/abuse](day29/api-cost-and-abuse.md): eight bounded generation paths, default
  disabled; historical usage repriced separately, no Day29 provider request.
- [Clean smoke](day29/deployment-smoke.md): Python 3.12.14 production-only install,
  no PyMuPDF/pdfplumber/tests/local corpus. Cold/warm homepage 2.160/0.309 s,
  prepared load 1.419 s, Source navigation 1.275 s, parameter update 0.344 s;
  Windows peak Working Set 210,137,088 bytes (not Python allocation measurement).
- [Sessions/performance](day29/performance-and-sessions.md): distinct real browser
  sessions A/B on one loopback server, local source bytes/text unchanged and API
  delta 0. Narrow viewport override failed to apply: explicitly NOT TESTED.
- [Release gate](day29/release-gate.md): A restricted noncommercial prepared-only
  candidate; B public live AI FAIL; full product private only.
- [Exact changed files](day29/changed-files.json), [checkpoint](DAY29_CHECKPOINT.md).

Four unedited browser captures from the real local workflow (1280×720):

1. [Default isolated homepage](day29/01-prepared-home.jpg): final upload/generation
   controls disabled; prepared entry available.
2. [Original source](day29/02-original-source.jpg): actual MIT PDF formulas/graph.
3. [Local exploration](day29/03-local-exploration.jpg): source amplitude 3 and
   exploration amplitude 2.90 retain distinct identities.
4. [Return to source](day29/04-return-source.jpg): original PDF after local change;
   reopening controls retained 2.90. Other screenshots were not regenerated or altered.

Final root startup: `python -m streamlit run app.py` (default prepared-only).
New production dependencies: pypdfium2==5.13.0 and direct jsonschema; PyMuPDF is
test-only in requirements-test.txt. requirements-day29-lock.txt captures the
audited Python 3.12 closure, not an assertion about every deployment platform.
