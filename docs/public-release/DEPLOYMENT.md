# Public paid release gate — activation pending

The owner approved a normal code update to GitHub main; paid activation and real
provider calls remain pending separate approval. See [PUSH_READINESS.md](PUSH_READINESS.md).
`app.py` remains the entrypoint. Default mode
allows prepared exploration and denies AI. `limited-public` adds the policy in
[POLICY.md](POLICY.md). `private` remains a development switch requiring an
external private access boundary and **must never be used for public hosting**.

## Required external setup before paid public access

1. Create a dedicated OpenAI API Project and Project-scoped key used only by this
   application. Permit Responses plus the required Files create/delete APIs;
   disable unrelated endpoints/models where the account controls allow it. Verify
   this Project actually has access to `gpt-6.1-sol`. No existing private key is
   accepted as a fallback in public mode. Do not put real secrets in examples,
   logs, screenshots, Git or chat.
2. In actual Platform settings, distinguish an enforced spend limit from alerts.
   Set the enforced Project ceiling to USD 10 and lower alerts if available;
   capture a redacted record of its scope and enforcement behavior. If only
   alerts are available, record that limitation; the independent PostgreSQL
   admission ceiling is mandatory. Never test exhaustion by spending USD 10.
3. Provision durable PostgreSQL with trusted TLS hostname verification. Preserve
   its lifetime ledger across restarts/migrations. Use `sslmode=verify-full`, a
   valid CA (`system` with compatible libpq/system trust, or a configured CA file),
   backups and least-privilege runtime credentials. Test real multi-process
   contention, transaction rollback, outage and reconnect behavior with synthetic
   traffic before live use. Local SQLite contention and mocked PostgreSQL SQL/TLS
   tests are **not** real PostgreSQL integration evidence.
4. Register an OIDC application for the exact deployed HTTPS
   `/oauth2callback` URL. Configure metadata URL, issuer, client credentials and
   stable random cookie/HMAC secrets. Keep `expose_tokens=[]`. Perform real login,
   logout, second-tab/restart quota persistence and wrong-issuer/expired-session
   checks. Email/session state/IP alone are not accepted quota identities.
5. Add the fields from [secrets.example.toml](secrets.example.toml) to the host's
   server secret store. `dedicated_project_verified=true` is an owner's setup
   attestation, **not** an automated verification of the account. Never set it
   until steps 1–2 are actually complete. Confirm the server mode is exactly
   `limited-public`. XSRF and CORS protection remain enabled; max upload is 2 MiB.
   Until acceptance and separate activation approval, use the empty root
   `VLL_LIVE_AI` in [cloud-secrets.example.toml](cloud-secrets.example.toml).
   Valid Google configuration exposes a login/logout verification button in
   this paid-off mode and can inspect an existing ledger read-only; no paid call
   or automatic ledger initialization occurs.
6. Use Python 3.12 and production requirements only. Do not install
   `requirements-test.txt`, copy test harnesses/ignored corpora, or deploy the
   fixture environment. Graphviz needs no system package. Retain PDFium and new
   dependency license notices. Linux wheels/resource limits must be checked in
   the actual Cloud runtime. Hosted identity/database services may have separate
   costs and require their own account approval.

Read-only preflight (prints flags, never secrets, makes no OpenAI request):

```powershell
.\.day29-local\venv\Scripts\python.exe -B tools/public_ai_preflight.py --output docs/public-release/cloud-preflight.json
```

Initialize an **empty, dedicated database only once**, after configuring secrets
locally and before switching to runtime credentials:

```powershell
.\.day29-local\venv\Scripts\python.exe -B tools/public_ai_preflight.py --init-ledger
```

Existing tables cause an error instead of resetting credit. This mutation was
not performed against a real database in this task. Preflight's `release_ready`
remains false because local checks cannot attest to remote account/login/cloud
evidence; document that evidence separately rather than treating a bool as approval.

## Checks completed locally

- Product-only Windows Python 3.12 directory: no test imports/private corpus/
  secret file/PyMuPDF; prepared and unconfigured-public Source navigation pass;
  zero Responses/file upload attempts. See [clean-smoke.json](clean-smoke.json).
- Resolved 61 runtime distributions; pip check passes, dependency audit reports
  no known advisories at this run. Pins and exact new notices are retained.
  Other platform wheels and future advisories require a new check.
- Focused tests verify atomic quotas, lifetime spend reservation, uncertain-result
  closure, all paid actions, malformed requests, SDK multipart expiry/no retries,
  resource bounds and existing Day29 behavior. See the final evidence record.
- Browser smoke uses a root-app wrapper with mocked OIDC/provider and test-only
  SQLite; uploaded actual two-page source and exercised local UI. It proves the
  public code path/UI, **not** real login, AI quality, PostgreSQL or Cloud hosting.

## Remaining release blockers

Actual dedicated Project/key/access/spend-limit configuration, real OIDC login,
remote PostgreSQL/TLS/concurrency, and actual Streamlit Cloud Linux behavior are
**NOT VERIFIED**. No Cloud deployment or real paid request was performed. Prepared
mode can be reviewed locally; paid public release needs these checks and the
owner's explicit deployment approval. [cloud-preflight.json](cloud-preflight.json)
records the current fail-closed state.

After approval, deploy the approved branch/entrypoint with production secrets;
check prepared exploration while signed out, then one bounded synthetic/mocked
request path in the actual runtime before separately authorized live AI testing.
Confirm shared budget denial preserves prepared/Source/Explore/Practice and that
restarts do not reset the ledger. Never deploy `tests/manual_public_release.py`.

Primary references: [OpenAI spend limits](https://developers.openai.com/api/docs/guides/spend-limits),
[Streamlit authentication](https://docs.streamlit.io/develop/concepts/connections/authentication),
[Community Cloud dependencies](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies),
[PostgreSQL row locks](https://www.postgresql.org/docs/current/explicit-locking.html),
[psycopg transactions](https://www.psycopg.org/psycopg3/docs/basic/transactions.html).
