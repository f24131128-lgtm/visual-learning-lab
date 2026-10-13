# Main update checkpoint — 2026-10-13

The owner authorized a normal, non-force update of GitHub main. Actual paid
requests and paid activation remain unauthorized until a separate approval.
This checkpoint preserves EVIDENCE.md as the earlier frozen local baseline.

The deployed Cloud workspace was observed watching
`f24131128-lgtm/visual-learning-lab`, `main`, `app.py`. Its existing log reports
Python 3.12.15 and Streamlit 1.65.0. Cloud replaced pyarrow 25.0.1 with 24.0.0
through its own compatibility guard. These observations precede this update;
successful installation of the new Authlib/psycopg dependencies and refreshed
application behavior must be verified after push.

Current focused regression: 82 tests passed in 69.045 seconds. A local request
guard blocked real Responses and Files endpoints throughout: no unexpected
attempts and zero actual provider calls. Thirteen targeted configuration,
deployment-boundary and paid-off AppTest checks also pass in production Python
3.12.14. Final complete regression: 551 tests passed in 308.816 seconds, with
zero unexpected real requests and zero actual provider calls. Logs remain in
the ignored local directory rather than the published commit.

Prepared mode now permits a Google-only login/logout check when valid auth
configuration exists, while every paid constructor still rejects requests.
After successful login, an existing valid PostgreSQL ledger can be inspected
read-only. This never initializes/reset tables, reserves credit, creates an
OpenAI client or calls the provider. Missing or invalid ledger configuration
keeps the paid feature closed. Prepared material remains usable anonymously.

All eight paid actions retain the common admission policy: 2 lifetime analyses
and 6 shared extra generations per verified Google account, 20 attempts per UTC
day, concurrency 1, USD 10 lifetime budget, USD 7 conservative reservation,
zero automatic retries and fail-closed uncertain-result handling. The pricing
review expires on 2026-11-01 UTC. No budget or pricing expiry was increased.

The commit uses an explicit allowlist of product/configuration code, synthetic
unit tests, operator preflight, placeholder templates, policy/setup documents
and required license notices. Secrets, ignored private corpora/databases,
manual browser wrappers and generated logs are excluded. Previously tracked
bytecode and the empty root `local` artifact are removed from the index only.
Staged content receives a redacted credential scan before commit. A narrow
.gitattributes rule preserves the exact upstream license bytes without stripping
their original whitespace or changing their recorded file hashes.

Cloud login, actual Google OIDC, real Neon TLS/ledger persistence and multi-account
limits are separate live acceptance checks. Synthetic SQLite/mocked PostgreSQL
tests do not certify those services. Keep root VLL_LIVE_AI empty and never use
private mode on this hosted site. A real paid PDF request requires renewed owner
approval after the other safety checks pass.
