# Day29 competition release gate

Scope: final local/offline tree, not a penetration-test certificate. One complete
regression passed **515 tests in 355.853 s**, no failures/errors, provider calls 0.
Original Day27/28 frozen records remain unchanged. No public deployment occurred.

| Area | Status | Evidence and limit |
|---|---|---|
| Semantic/source integrity | PASS | Prepared Golden Path, original PDF/text equality, stable semantic IDs and return navigation; broader model fidelity is not established |
| Input validation | PARTIAL | Byte/page/object/text/JSON/graph bounds tested; hostile PDF native-process isolation and decompression admission remain unresolved |
| Secret handling | PASS | Scoped redacted current/reachable-history scan, no indicators or tracked secret paths; not arbitrary-token forensics |
| Prompt injection resistance | PARTIAL | Fixed data boundary and mocked injection assertions; no paid model attack trials |
| Expression/runtime safety | PASS | AST/DAG/IDs/inverses/provenance/numeric/revision guards reject recorded malicious declarations |
| XSS safety | PASS | Tested inert text, escaped graph output, fixed frontend text boundaries; not an adversarial browser DOM fuzzing campaign |
| Session isolation | PASS | Bounded two real WebSocket sessions and independent prepared state tests; no multi-instance claim |
| Dependency vulnerabilities | PARTIAL | 54 pinned PyPI distributions, zero known pip-audit advisories; embedded native libraries, JS and unknown vulnerabilities not comprehensively audited |
| PyMuPDF / third-party licensing | PARTIAL | Decision A: production raster adapter replaced with PDFium; clean runtime has no PyMuPDF. Historical AGPL distribution obligations and legal review remain open; prepared source requires CC BY-NC-SA attribution/noncommercial use |
| Cost/abuse control | PASS | Default server denies paid client creation and upload, even with configured key; output/attempt/timeout bounds for private mode are not a dollar quota |
| Prepared demo | PASS | Portable hashed inputs, no secrets/test-corpus dependency, no AI calls, real PDF Golden Path and four genuine screenshots |
| Live AI generation | FAIL | Public access intentionally blocked. No authentication/distributed rate/concurrency/budget enforcement; private env switch is not authentication |
| Clean deployment | PASS | Fresh production-only Python 3.12.14 environment, pip check, root app smoke, loopback browser. Streamlit Cloud deployment NOT TESTED |
| Performance | PARTIAL | Local timing/Working Set and bounded rejection/session smoke; no high-load SLA. Narrow viewport NOT TESTED because override did not apply |
| Final regression | PASS | One complete unittest run: 515/515, 355.853 s; final-request-guard.json records 0 real provider calls |

**A. PUBLIC PREPARED DEMO READY — restricted candidate.** The default genuinely
isolated prepared-only mode passes the local engineering gate for a
noncommercial attributed demo. Human hosting/distribution review must retain
the notices, omit keys/test dependencies/private corpora, and keep `VLL_LIVE_AI`
unset. No public site was created and no commercial/legal approval is asserted.

**B. LIVE AI GENERATION READY — FAIL.** Do not expose private generation publicly.
Budget estimates and token caps do not replace owner authentication, aggregate
rate/concurrency/daily spending limits, cancellation/resource isolation or
account-side controls. Existing source processing remains available privately,
with preserved UI workflows, after the owner establishes an external boundary.

**C. NOT READY / PRIVATE ONLY — the full product.** A does not imply B. Any release
including untrusted uploads or live generation remains restricted; the original
uncontrolled owner-key spending risk is blocked by the default mode, not solved
for a public live service. Stop at Day29 for human review; no Day30 work.
