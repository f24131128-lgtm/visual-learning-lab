# Clean deployment smoke

Created a fresh isolated Python **3.12.14** environment, installed only declared
production requirements, checked imports and `pip check`. A product-only copy
includes source modules/fixed frontends/prepared assets/config/notices, excluding
tests, ignored Day26/27 corpora, local secrets, bytecode and developer paths.
`tools/day29_clean.py` stages and verifies it reproducibly; evidence is
`clean-smoke-results.json`, `clean-smoke-final.log` and `server-clean.log`.

PASS: homepage, no-key mode, server-disabled upload/generation, prepared-example
load, Source page/Atlas preview, allowed amplitude change, return to Source,
source byte/text equality and zero Responses/files calls. PyMuPDF and optional
pdfplumber are absent. Streamlit started on **127.0.0.1:8549** and genuine browser
screenshots show the Golden Path. The 8550 server is a separate test-only session
harness; it is not a deployment entrypoint.

This is an equivalent fresh dependency/source installation on Windows, not a
Linux container or actual Community Cloud trial. Existing regression separately
uses Python 3.14.7 and test dependencies. No Node build, CDN or system Graphviz
is needed. No site was pushed or exposed publicly. Initial sandbox AppTest runs
did not finish; reviewed local execution of the isolated interpreter completed.
First clean harness attempt used a nonexistent UI key; corrected to existing
workspace controls, with both logs retained.

Run the **default prepared-only app**, from repository root:

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For reproducible reviewed dependency versions, install the resolved
`requirements-day29-lock.txt` instead; verify its wheels on the target platform.
Do not install `requirements-test.txt` into deployment. Do not set `VLL_LIVE_AI`
or configure an owner key on the public demo. Retain third-party notices and the
MIT noncommercial attribution. Public hosting itself requires human approval.

Live mode is private-only and still lacks trustworthy rate/spend enforcement.
Never enable it on Community Cloud merely because a key is in secrets. A separate
approved identity/gateway/cost design must precede public live exposure.

After the final clean AppTest passed, the long-running loopback server still
held an earlier imported module when the staged source changed. The new browser
tab exposed an ImportError; the two inspected agent-owned server processes were
restarted with final source. `server-clean.log` preserves that stale-cache failure;
`server-clean-final.log` and the final homepage capture show the fresh process.
No production code change or second full regression was needed for this restart.
