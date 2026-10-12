# API failure injection

`tests/test_day29.py` runs the real app UI with intercepted SDK sites, synthetic
keys and controlled results/errors. Nine scenarios cover invalid key (401),
timeout, HTTP 429, HTTP 500/503, network loss, malformed JSON, output exhaustion
and unexpected output fields. Each observed one mocked attempt, safe visible
error, no exception-body canary and exact preservation of previous analysis ID,
analysis, source context and Source Lens state. Missing-key/default prepared
operation also passes without SDK initialization. No actual provider response
latency, billing, live key validity or recovery SLA was tested.

HTTP cases are synthetic failure injections at the client boundary, not requests
to a server returning those HTTP codes. The real SDK constructor is independently
checked for owned `max_retries=0` and `timeout=90`; caller overrides cannot widen
them. Local rechecks/cached navigation make no request. An explicit retry may
attempt again; there is no background retry loop. Timeout/browser disconnect does
not establish provider cancellation or zero billing.

Root cause fixed: old main analysis cleared valid state before reading inputs or
requesting AI. New code stages source/response, validates base/transport and only
then resets dependent state and commits. Optional lab/scene/Atlas failures remain
isolated under existing validators. `response_data` also rejects NaN/Infinity,
overflow numbers, duplicate fields, excessive JSON depth/bytes and incomplete
output before consumers can install it.

Initial red-team/repaired focused logs are preserved, including a single-test
harness error caused by clearing Windows home environment variables. The repair
clears only AI configuration, preserving system environment. This was test-harness
behavior, not a product missing-key vulnerability.
