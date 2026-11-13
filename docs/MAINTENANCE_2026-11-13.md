# 2026-11-13 product completion pass

Current checkout: D:/Projects/visual-learning-lab; the old chat path no longer exists.
Existing modified historical reports and untracked work are excluded from this change.

## Shipped in this change

- Local personal PDF/text launcher bound to 127.0.0.1, with hidden API key input,
  process-environment credentials, explicit paid-action notice and free demo mode.
- Existing private client accepts environment keys while preserving Secrets fallback,
  request bounds, zero automatic retries and public metering boundaries.
- First-use learning instructions and a personal-material notice, both localized.
- GitHub offline CI, bug template, contributor/security docs and user troubleshooting.
- Five launcher/credential isolation tests; historical SQLite quota fixtures use a
  fixed in-policy database date. The explicit expired-price rejection still passes.

## Verified so far

- New tests: 5 passed (including explicit stale environment-key replacement).
- Focused product regression: 110 passed; zero provider attempts.
- Actual isolated Edge: private PDF upload enabled and first-use guidance visible;
  no paid analysis clicked. This does not establish generated source fidelity.
- Read-only model access checks with both Secrets and environment credentials: HTTP 401. No completion
  was generated. A new valid key must be supplied by the owner; do not post it in chat.
- Public price policy expired 2026-11-01. Production expiry protection is unchanged;
  public AI has not been enabled. Public release still needs current pricing review,
  verified identity/ledger and independent acceptance.

## Final validation

- Full offline regression: 566 passed, 0 failures/errors/skips, 417.373 seconds;
  real provider calls and unexpected provider attempts both zero. The full run
  loaded four launcher tests before the replacement-key test was added; the final
  five launcher tests passed separately afterward.
- Current focused/full reports are saved in maintenance-2026-11-13/. Original
  Day30 result files are restored rather than rewriting the historical baseline.
- Draft PR: https://github.com/f24131128-lgtm/visual-learning-lab/pull/2.
  GitHub Actions has started; its remote outcome is separate from local results.
- No paid completion was made; two read-only credential checks both returned 401.

No root software license has been invented; existing notices remain separate.
