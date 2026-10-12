# Secrets audit

See `secrets-results.json` and `audit-summary.log`. Scanned 885 tracked files and
1,128 unique reachable historical blobs, each at most 5 MiB, using a redacted
OpenAI-key format indicator. Zero indicators and no tracked `secrets.toml`/`.env`
paths were found. No credential values were printed or copied into evidence.

A local ignored secrets file and environment credential exist; the audit records
presence only. They were not transmitted, rotated or revoked. Default mode denies
paid-client initialization even with a key; synthetic canaries verified safe
errors. Compiler contexts contain source/semantic data, never SDK credentials.
Fixed frontend assets have no key-reading API. Product logs avoid SDK exception
bodies; scene debug is opt-in and must remain off in deployment. Do not enable
`OPENAI_LOG=debug` with private source material.

Scope limits: this is not arbitrary-token entropy detection, deleted/unreachable
Git-object forensics, server-log forensics or an account compromise assessment.
The repository already tracks 76 bytecode files; clean staging excludes them.
Day29-generated changes to previously clean tracked bytecode are restored from
their original Git blobs without checkout/reset. Do not distribute ignored local
corpora, secrets, test environments or debug logs as the product bundle.
