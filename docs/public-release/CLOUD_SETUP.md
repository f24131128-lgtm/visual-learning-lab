# Existing Cloud site: configuration review, 2026-10-13

The owner reports that the OpenAI Project/key, Google Web OAuth client, exact
Cloud callback and Neon database now exist. This is an owner report, not a
completed Cloud acceptance test. The current uncommitted implementation is
preserved. No commit, push, secret upload, paid request or paid-feature enablement
was performed in this review. Historical EVIDENCE.md is unchanged.

## Secrets and mode

Copy [cloud-secrets.example.toml](cloud-secrets.example.toml) into the Cloud
server-side Secrets editor; replace placeholders there, never in Git or chat.
The example's empty VLL_LIVE_AI keeps the new code in prepared-only mode.
After separate approval and verification, the paid mode is `limited-public`.
Never use `private` on the hosted public site: that development mode bypasses
the public admission ledger.

Exact names are `public_ai.api_key`, `public_ai.project_id`,
`public_ai.dedicated_project_verified`, `public_ai.ledger_dsn`,
`public_ai.ca_cert`, `public_ai.identity_issuer`, `public_ai.quota_hmac_secret`,
`public_ai.budget_microusd`, `public_ai.price_review_date`, plus
`auth.redirect_uri`, `auth.cookie_secret`, `auth.client_id`, `auth.client_secret`,
`auth.server_metadata_url`, `auth.expose_tokens`. Authentication is the default
unnamed `[auth]` provider; `[auth.google]` alone does not match the current code.
`OPENAI_API_KEY`, `DATABASE_URL`, `NEON_DATABASE_URL`, `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET` are not aliases for the limited-public configuration.
An OS environment variable VLL_LIVE_AI takes precedence over the root secret;
ensure it is not `private`, and restart after changing the server configuration.

## Manual settings before activation

1. Keep the existing app private during acceptance. Verify its actual GitHub
   repository, branch, deployed commit and root entrypoint `app.py`; the current
   local changes have not reached that site. Preserve its existing URL.
2. Confirm the Cloud runtime is Python 3.12, using requirements.txt only.
   Do not install requirements-test.txt or optional document parsing extras.
   Cloud cannot change Python in place; if the existing app has a different
   Python version, record URL/settings/secrets and plan redeployment separately.
   Do not delete the existing app during this configuration-only step.
3. In OpenAI verify that the dedicated Project owns the new key, has
   `gpt-6.1-sol` access, and permits Responses plus Files creation/deletion.
   Configure a USD 10 enforced Project spend limit and smaller alerts where
   available. Alerts alone do not reject requests; even an enforced monthly
   platform limit can have delayed overshoot. The PostgreSQL lifetime ledger is
   mandatory. Set dedicated_project_verified=true only after this review.
4. Use a durable Neon database with verified TLS. Initialization uses a temporary
   DDL-capable credential; the eventual runtime credential has schema USAGE and
   SELECT/INSERT/UPDATE on the two ledger tables, without table ownership, DDL or
   DELETE rights. Initialize an empty dedicated database once with
   tools/public_ai_preflight.py --init-ledger using ignored local operator
   secrets. This makes no OpenAI request. Never reinitialize existing tables.
   Record and preserve backups. Runtime and initializer must resolve the same
   tables/search_path; all app instances must share that lifetime ledger.
5. Google OAuth's exact redirect is
   `https://visual-learning-lab-kdemsgmw3swykt5zpqbkc5.streamlit.app/oauth2callback`.
   Keep audience External/Testing with two approved test accounts for staging.
   An Internal audience restricts an organizational account to that organization;
   Testing restricts access to registered testers. Later public Google access
   needs the appropriate audience/publication review and owner approval. Use
   only identity scopes; no additional Google API permissions are required by
   this app. Do not enable exposed ID/access tokens.
6. Generate independent random cookie and quota secrets of at least 32
   characters. Preserve the quota secret, issuer, Project/key and ledger across
   deployments; changes to fingerprint inputs fail closed and require an
   explicit migration preserving all charges and account identities.
7. Before paid activation, perform actual Google login/logout/account isolation,
   TLS/PostgreSQL concurrency and restart persistence, signed-out paid denial,
   browser secret-leak checks and the prepared Golden Path. Synthetic exhaustion
   tests must use a separate test ledger, never reset or drain production credit.
   A real PDF analysis requires a new explicit authorization; none ran here.
8. The pricing review expires on 2026-11-01 UTC. Review pricing before that date;
   the current code denies generation at expiry. Do not increase the USD 10 cap.

## Verification and coverage

The previous frozen evidence records 79 focused and 548 complete tests passing,
including the policy and prepared/browser smoke. It predates the subsequent
Google-specific configuration checks; do not represent those hashes/counts as
a new full regression. This review ran 9 ConfigurationTests and 3
DeploymentBoundaryTests on production Python 3.12.14: all passed, with socket-free
SDK MockTransport and no real provider request. pip check also passed. Actual
Cloud Linux wheels, native PDF worker limits and new cloud acceptance remain
unverified. The Windows lock file is an inventory, not Linux certification.

All eight actions are `analysis`, `explain`, `review`, `scene`, `atlas`,
`planner`, `analogy`, `simulation`. Constructors use production_safety.create_client
and MeteredClient in limited-public mode. Admission requires Google identity and
the same PostgreSQL transaction/row lock: lifetime 2 analyses and 6 shared extra
generations per account, 20 requests per UTC day, concurrency 1, USD 10 lifetime.
PDF upload reserves the same analysis admission before upload. Failed admitted
attempts count; uncertain outcomes retain the USD 7 reserve and pause traffic.
A positive balance below USD 7 rejects new generation. No automatic retries or
credit reset. Prepared and local Source/Explore/Practice operations remain usable.
Production uses PDFium; test-only PyMuPDF and license boundaries are preserved.

## Proposed single commit and push — do not execute until approval

The owner subsequently approved commit and a normal push directly to main.
That authorization supersedes the proposed new-branch-only destination below.
The release checkout is isolated on a codex branch and its reviewed commit is
pushed to main with an ordinary fast-forward push. All exclusions and paid-off
checks remain required; [PUSH_READINESS.md](PUSH_READINESS.md) records this update.

1. Record current HEAD/branch and inspect staged changes. Create
   `codex/post29-limited-public` from the current checkout without resetting or
   discarding changes. Confirm it is not the Cloud app's watched branch.
2. Stage explicit paths only: the 23 product/config/notice files listed below,
   tests/test_public_ai.py, the placeholder templates, POLICY.md, DEPLOYMENT.md,
   CLOUD_SETUP.md, the historical EVIDENCE.md and structured evidence JSON files
   after redacted review, tools/public_ai_preflight.py, and reviewed dependency
   notices under docs/public-release/licenses/ with new-dependency-licenses.json.
   Retain existing prepared attribution, PDFium/JSXGraph notices and license trees.
   Do not stage entire docs/ or use `git add .` / `git add -A`.
3. The 76 already tracked bytecode files need an explicit index-only cleanup
   (`git rm --cached` on reviewed exact .pyc paths); ignore rules alone cannot
   untrack them. The already tracked root file `local` is an empty, zero-byte
   artifact; exclude it from the release index without deleting local data.
4. Exclude .streamlit/secrets.toml, .env files, all .day*-local/ and .post29-local/
   artifacts, databases, private PDF corpora, browser test wrapper
   tests/manual_public_release.py, generated smoke PDFs, screenshots containing
   account information and unnecessary *.log output. Keep synthetic unit tests.
5. Inspect `git diff --cached --name-status`, `git diff --cached --check` and a
   redacted staged secret scan. Run focused and complete offline regression for
   the exact final staged revision, then check production Python 3.12 and Linux
   dependencies in private staging. Current review is not that final regression.
6. Commit once, e.g. `feat: add metered Google-authenticated public AI`, then
   `git push -u origin codex/post29-limited-public`. Pushing a watched branch can
   immediately rebuild Cloud; keep it off the watched branch and retain prepared
   mode/private staging until separately approved. No main merge, branch switch
   in Cloud, paid activation or public sharing change is included in this plan.

Product/config paths: .gitattributes, .gitignore, .streamlit/config.toml, README.md,
THIRD_PARTY_NOTICES.md, docs/OPEN_SOURCE_REUSE_LEDGER.md, app.py,
production_safety.py, public_access.py, paid_policy.py, metered_client.py,
pdf_ingest.py, pdf_worker.py, pdf_renderer.py, prepared_demo.py, i18n.py,
dynamic_simulation.py, scene/compiler.py, source_atlas/compiler.py,
learning_world/runtime.py, analogy/runtime.py, requirements.txt,
requirements-public-lock.txt (23 paths).

Run locally from repository root:
`python -m streamlit run app.py`.

Primary references: [Google authentication](https://docs.streamlit.io/develop/tutorials/authentication/google),
[Cloud Python changes](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python),
[OpenAI spend limits](https://developers.openai.com/api/docs/guides/spend-limits).
