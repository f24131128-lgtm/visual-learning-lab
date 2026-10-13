# POST-DAY29 result — 2026-10-13

**Local implementation and regression PASS; public live release BLOCKED pending
external setup and owner approval.** No public deployment, commit or push. HEAD
remains `9b3c6f4`, branch `day17-learning-scene-wip`. Actual paid calls: **0**.

| Verification | Actual result |
|---|---|
| Focused | **79/79 PASS**, 97.165 s — `test_public_ai test_day29 test_day14 test_day22_live`. |
| Final complete regression | **548/548 PASS**, 466.932 s — `python -X utf8 -B -m unittest discover -s tests -q`. |
| Request guard | Zero unexpected real Responses/Files-create attempts; zero paid requests. Actual SDK serialization tested separately with socket-free MockTransport. |
| Pure admission / rejection | Restart/second-connection persistence, 8 contenders/1 reservation winner, global UTC quota, shared extra-generation quota, conservative lifetime budget, duplicates/crashes/timeout/unknown usage, forged identity/requests, pricing expiry. PostgreSQL SQL/TLS adapter tests are mocked. |
| PDF resource boundary | Actual text/raster/native anchors and 600 MiB compressed-page rejection. Windows venv launcher compatibility corrected to two processes with the same aggregate 512 MiB job limit. Linux resource branch untested. |
| Production-only smoke | Python 3.12.14, prepared and unconfigured-public Source navigation PASS; zero API attempts; no PyMuPDF, test tree, ignored corpus or secret file in staged product. |
| Dependencies | 61 pinned distributions; pip check PASS; audit found **0 known advisories**. Seven new distributions, nine license files retained. Other platform/native wheels remain a release gate. |
| Browser | Real loopback root app with **mocked OIDC/provider + SQLite test ledger**. Actual unchanged 2-page PDF upload -> one metered replay -> Source raster -> Flow selection -> Practice step 2 -> forced test-budget exhaustion -> AI buttons disabled -> prepared 8-page material -> local amplitude 3 to 2.9. Request count remained **1** throughout local operations. |
| Platform access | Read-only browser request for actual OpenAI Project settings reached the login form. No Project/key/spend settings read or changed. |
| Additional local preview | Actual `app.py` started on loopback 8549 for manual review, paid access unconfigured/denied. Automated tab retrieval was rejected by browser URL policy; no workaround attempted and no additional browser PASS claimed. The completed smoke above used 8551. |
| Historical / secrets | Final audit records Day28 frozen hashes, Day29 unchanged files and redacted changed-file key-indicator scan. No secret file is tracked. No historical evidence was deliberately rewritten. |

The early focused failures were test-fixture/test-interpreter issues and were
repaired before the green run: the original sample PDF had 3 pages; a Windows
SQLite connection remained open; AppTest state does not expose `pop`; the
compressed-page fixture initially did not trigger extraction; the legacy test
interpreter lacks the new production driver. The genuine browser runtime issue
was Windows venv process redirection; the total job memory ceiling was retained.
No input/semantic validator was weakened to accept a fixture.

## Actual feature availability

- **Immediately reviewable:** prepared demo and its local learning/source/
  visualization/experiment operations without a key. Exhausted or missing AI
  configuration does not remove them.
- **Implemented, requires external setup:** authenticated small PDF/pasted-text
  analysis plus existing explicit visualization, explanation, review, scene,
  Atlas, planner, analogy and simulation builds under one policy. USD 10 lifetime;
  20 requests/day; concurrency 1; 2 analyses + 6 additional generations/account.
- **Currently denied:** real public owner-paid AI. Actual dedicated Project/key/
  GPT-6.1 Sol access/enforced spend configuration, real OIDC and durable PostgreSQL
  TLS/multi-process integration have not been provisioned/verified. No Cloud
  Linux run or external deployment was authorized/performed.

The USD 7 per-request reserve uses worst documented full-context rates, so a
positive balance below USD 7 still denies new generation. An unknown result holds
its reserve and requires operator reconciliation; this intentionally favors
budget preservation over availability. OIDC limits accounts rather than humans.
Host/resource DoS and native PDF exploitation remain risks; the worker is not a
filesystem/network sandbox. Source/learning correctness remains subject to the
existing semantic/grounding limitations. Prepared educational content retains
CC BY-NC-SA 4.0 terms and must remain noncommercial.

## Changed files and dependencies

New policy: `paid_policy.py`, `public_access.py`, `metered_client.py`; PDF boundary:
`pdf_ingest.py`, `pdf_worker.py`. Existing entrypoints/adapters now declare their
paid action and reuse that gate: `app.py`, `production_safety.py`,
`dynamic_simulation.py`, `scene/compiler.py`, `source_atlas/compiler.py`,
`learning_world/runtime.py`, `analogy/runtime.py`; prepared/source adapters,
localization, upload config, requirements, ignore rules and notices updated.
`tests/test_public_ai.py` adds 33 offline tests; the browser wrapper remains
test-only. `tools/public_*.py` and this evidence directory provide reproducibility.
Full file inventory/hashes: [evidence.json](evidence.json).

New direct capabilities are `streamlit[auth]` and `psycopg[binary]`. Authlib is
BSD-3-Clause; psycopg is LGPL-3.0-only. Resolved production pins:
[`requirements-public-lock.txt`](../../requirements-public-lock.txt). Existing
PDFium replacement and test-only PyMuPDF boundary are preserved.

Run the actual product from repository root:

```powershell
.\.day29-local\venv\Scripts\python.exe -B -m streamlit run app.py
```

Default mode denies AI; follow [DEPLOYMENT.md](DEPLOYMENT.md) only after the
required external setup and approval. Budget assumptions/recovery:
[POLICY.md](POLICY.md). Machine-readable local results:
[browser-smoke.json](browser-smoke.json), [clean-smoke.json](clean-smoke.json),
[cloud-preflight.json](cloud-preflight.json), [request-guard.json](request-guard.json).

![Budget exhausted; prepared and local learning remain available](browser-exhausted.jpg)

![Actual uploaded PDF raster, MIT OCW Chapter 23](browser-source-raster.jpg)
