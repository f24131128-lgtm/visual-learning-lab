# Limited public AI policy — 2026-10-13

The owner approved **USD 10 lifetime model-usage budget**. Code is reviewable;
public deployment, commits and pushes have not been performed. Real Project/key,
OIDC and remote PostgreSQL configuration are still unverified. Missing
configuration keeps paid access closed. Prepared exploration works without login.

| Control | Enforced behavior |
|---|---|
| Identity | Streamlit's verified OIDC `iss` + `sub`, exact configured issuer, valid supplied expiry; HMAC identifier stored in PostgreSQL. New tabs, app restarts and UI reruns do not reset an account's quota. |
| Personal allowance | Lifetime 2 main analyses and 6 additional generations per account. Explain, Focused Review, Scene, Atlas, representation planning, Analogy and Dynamic Simulation share those 6. Failed admitted attempts count. |
| Global allowance | 20 inference attempts per UTC day; one pending/uncertain inference across all processes using the same database. No automatic budget reset. |
| Budget | USD 10 lifetime, reserve USD 7 atomically **before** upload/inference, then replace it with rounded-up conservative usage after a known completed response. Remaining below USD 7 stops new requests even when positive. |
| Model/transport | `gpt-6.1-sol`, medium reasoning, Standard (`service_tier=default`), at most 16,000 output tokens, `store=False`, fixed OpenAI URL, dedicated Project header/key, SDK retries zero, 90-second timeout. No tools, background, streaming, remote image URL or foreign file IDs. |
| Sources | Public PDF <=2 MiB, <=2 total pages, no encryption; original Day29 signature/MIME/name/object/dimension bounds remain. Text <=48,000 characters; original PDF and validated extracted pages remain analysis input. No OCR. |
| Local operations | Source/Explore/Practice, selection, zoom, quizzes, sliders and playback use existing state. They consume no AI allowance. Existing explicitly requested builds/explanations use the same admission ledger. |
| Prepared demo | Always accessible, including without login/configuration, after exhaustion and after an existing analysis. Verified bundled 8-page source is exempt from the visitor-upload page cap. |
| Unknown result | Timeout, API error, incomplete/unknown usage or crash holds the full reservation. Unknown outcomes pause admission; pending reservations never expire automatically. No automatic retries/refunds. |
| Storage failure | Database, configuration, identity, policy fingerprint or pricing-review failures deny generation. SQLite exists only in offline tests; no production fallback. |

## Why the aggregate protection bounds model usage

Current official [GPT-6.1 Sol documentation](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
lists a 1,050,000-token context, Standard pricing, a long-context multiplier and
regional premium. We deliberately reserve using the entire context, including
PDF/image tokenization that cannot be exactly estimated locally:

`1,050,000 × $5.50 / 1M + 16,000 × $16.50 / 1M = $6.039 < $7`.

$5.50/M input includes the higher cache-write, long-context and regional rates;
$16.50/M output includes long-context and regional rates. Completed usage is
charged as `ceil(input_tokens × 5.5 + output_tokens × 16.5)` micro USD, including
reasoning output. Cache hits do not lower this conservative accounting. Usage
outside the documented context/output, an unknown model or non-default tier
retains the full reserve and pauses the app. Tools/additional billed services are
disabled. This is a conservative admission ledger, not an invoice estimate.

Admission and settlement both lock the same persisted PostgreSQL row in a
transaction. Admission requires `committed + $7 <= $10`; outstanding reservations
already count in `committed`. A crash cannot mint new credit or concurrency. The
proof depends on published pricing/model bounds, exclusive use of this Project
through this gate, protected database/configuration and successful real
PostgreSQL validation. Pricing must be reviewed before **2026-11-01 UTC**, when
generation closes automatically. Tax, hosting, database and identity-provider
charges are outside the USD 10 model-usage ceiling.

Current [OpenAI spend limits](https://developers.openai.com/api/docs/guides/spend-limits)
support enforced Project/organization limits, distinct from alert thresholds.
Enforcement can be delayed with slight overshoot. Set the actual Project's
enforced cap to USD 10 and alert thresholds below it where available; do not
mistake an alert for rejection. Account eligibility/UI behavior has **not** been
verified here. The independent persisted admission ledger remains required even
when the platform offers only alerts, or while its enforcement is delayed.

## PDF resource boundary

`pdf_ingest.py` sends data to fixed `pdf_worker.py`, never generated code or a
visitor-controlled path/command. One worker per app process, no queue; 20-second
parent wall timeout; bounded input/output; no inherited API/database/OIDC secrets
or arbitrary PYTHONPATH. Windows uses a Job Object with 512 MiB aggregate memory
and at most two processes (the venv redirector plus Python). Linux declares
768 MiB address space, 15-second CPU and zero file-output resource limits before
third-party imports. Windows extraction/raster/anchor and a compressed 600 MiB
page rejection were tested. Linux limits are **NOT TESTED** on this host.

This is resource isolation, **not a filesystem/network sandbox**. A native
parser exploit runs as the application OS user and could access its files.
Optional pdfplumber is absent from the reviewed production environment; keep it
absent until its public parsing path receives the same process-boundary review.
Unpaid uploads/requests and multiple-account abuse can still exhaust hosting
resources or the shared allowance. OIDC limits accounts, not unique humans.

## Operator recovery

Never delete/reinitialize policy tables to clear a busy state or rotate quota
secrets to reset accounts. Back up and retain this lifetime ledger across
deployments. Use an initialization credential once, then a runtime role with
SELECT/INSERT/UPDATE only on these tables; no visitor access or schema reset.

For uncertain/pending reservations, first disable live access and reconcile the
actual provider request/usage. If its result cannot be proven, retain the full
USD 7 charge. Only after proving the upstream request has ended may an operator
mark it complete and clear the pause without decreasing its charge. Known
conservative usage may replace it only with documented evidence and a locked
transaction. No automatic recovery utility bypasses these requirements.

Key/issuer/HMAC secret changes invalidate the fingerprint and fail closed; migrate
the existing ledger explicitly after reconciliation while preserving charges and
identity mapping. Revoking a key is an emergency option. Prepared content stays
available throughout recovery. API file deletion is one best-effort call; files
also request one-hour expiry. Actual provider deletion/retention is unverified.
