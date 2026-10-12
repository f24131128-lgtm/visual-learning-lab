# Day29 adversarial matrix

Offline mocked declarations and pure boundary tests. PASS is limited to the recorded attack; no paid model probe or hostile-PDF process sandbox was tested. Rows are emitted after assertions, so the final unittest outcome must also be checked.

| Attack | Expected defense | Observed | Status |
|---|---|---|---|
| Expression 1/0 | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression sqrt(-1) | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression log(0) | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression 10**1000 | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression exp(1000) | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression __import__("os") | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression open("../../secrets.toml") | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression x.__class__ | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression x[0] | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Expression sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(sin(1)))))))))))))))))))) | AST/function/depth/numeric allowlists | Rejected without execution | PASS |
| Stale/forged/nonfinite/action runtime events | Validate trial then atomic commit | Four events ignored; exact state preserved | PASS |
| Forged Atlas source owner / NaN box | Drop broken refs and optional region | No forged owner or invalid box survives | PASS |
| Main malformed base / excessive concepts or graph nodes | Validate required base; isolate bounded optional graphs | Four main envelopes rejected; two oversized optional graphs rejected | PASS |
| unexpected fields | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| unsupported representation | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| malformed semantic ID | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| forged semantic owner | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| invalid provenance | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| fake manipulation target | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| unsupported inverse | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| excessive objects | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| unbounded time | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| malformed range | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| positive radius zero | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| zero wavelength-like divisor | World schema/reference/domain/inverse bounds | World rejected; existing state untouched | PASS |
| traversal | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| misleading extension | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| invalid MIME | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| damaged PDF | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| invalid signature | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| oversized PDF | Byte/signature/name/MIME/parser bounds | Rejected; no path opened | PASS |
| Excessive page/object counts | 80-page/20k-object bounds | Bounded 81 blank pages and lowered object limit rejected | PASS |
| Renderer replacement parity | Whole crop/rotation frame and verified native anchors | 0/90/180/270 dimensions + mean raster error<8/255 + actual ink; second page + equation image rendered | PASS |
| Cross-session prepared mutable state | Fresh per-session object graph | A source/cache/focus mutation absent from B | PASS |
| Caller requests unlimited retry/timeout | Owned limits override caller | max_retries=0; timeout=90s | PASS |
| Injected source instructions/capability/tool/page request | Fixed instructions; data in input; no tools; page whitelist | Captured request isolated; forged pages filtered. Real model obedience NOT TESTED | PASS |
| Configured owner key in public mode | Deny before SDK initialization | SDK calls=0 | PASS |
| NaN | Reject bounded response envelope | Rejected before semantic installation | PASS |
| Infinity | Reject bounded response envelope | Rejected before semantic installation | PASS |
| overflow JSON | Reject bounded response envelope | Rejected before semantic installation | PASS |
| duplicate field | Reject bounded response envelope | Rejected before semantic installation | PASS |
| deep declaration | Reject bounded response envelope | Rejected before semantic installation | PASS |
| oversized response | Reject bounded response envelope | Rejected before semantic installation | PASS |
| output exhaustion | Reject bounded response envelope | Rejected before semantic installation | PASS |
| malformed response | Reject bounded response envelope | Rejected before semantic installation | PASS |
| XSS <script>alert(1)</script> | Treat labels as data; encode fixed output; retain source data | World title and PDF excerpt remain data; Flow component HTML-escapes label | PASS |
| XSS <img src=x onerror=alert(1)> | Treat labels as data; encode fixed output; retain source data | World title and PDF excerpt remain data; Flow component HTML-escapes label | PASS |
| Fixed component labels | DOM textContent | Three fixed hosts inspected; runtime browser XSS probe is separate | PASS |
| invalid key | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| timeout | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| HTTP 429 | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| HTTP 500 | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| HTTP 503 | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| network loss | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| malformed response | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| output exhaustion | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| unexpected field | One attempt; safe error; transaction preserves previous source | 1 mocked request; no exception body; previous material unchanged | PASS |
| Missing key + public prepared load | No-key operation and no paid client | Homepage + prepared load PASS; client calls=0 | PASS |

Additional observed browser boundary: two distinct Streamlit sessions on the same loopback server, real prepared PDF A and synthetic text B; B showed only its source canary, no A title or PDF page. PASS for this bounded smoke, not a hostile multi-tenant audit. See browser-results.json.

Excessive agency: all eight generation paths use a server-denied default factory, no model tool definitions, fixed instructions and declarative validation. A default-mode configured credential cannot initialize a paid client. Forbidden expression calls/attributes/indexing and forged reducer events are exercised offline. No shell/GitHub/network action is driven by source content. Actual model prompt-injection behavior remains PARTIAL.

Coverage: injection; expression/JSON/semantic attacks; XSS fixed text and escaped graph boundaries; file/resource envelopes; state/session isolation; excessive agency; failure/cost boundaries. Redacted synthetic failures cover nine client outcomes. Refer to test_day29.py for exact payloads and assertions.
