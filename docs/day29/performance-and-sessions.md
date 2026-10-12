# Bounded local performance and session evidence

`clean-smoke-results.json` contains measured cold/warm AppTest homepage,
prepared load, first Source navigation, parameter update and process Working Set
in a fresh production-only Python 3.12 environment. These are local wall-clock
observations, not cloud SLA, browser novice time or Python-allocation estimates.
Only one final bounded measurement is summarized; earlier observations are kept.

The actual browser Golden Path changed A from 3 to 2.90, returned to the original
Source PDF and reopened controls with 2.90 still visible. Immutable source fact
remained 3. Source byte/text equality and API delta=0 are separately established
by AppTest mocks, not inferred solely from screenshots.

Two independent browser tabs maintained distinct Streamlit WebSocket sessions
on the **same 8550 test server**. A loaded the real prepared MIT PDF; B loaded a
clearly synthetic text material through `tests/manual_day29_session.py`.
Saved DOMs show A's SHM material and B's own source canary, no SHM or PDF page in B.
Pure logic tests additionally mutate A source/cache/focus and verify B is exactly
unchanged. The harness has no API generation, and never enters production.
This is bounded functional isolation evidence, not a security guarantee under
arbitrary malicious clients or multi-instance deployment.

Large-but-bounded rejection used a 10 MiB+5 byte buffer, 81 tiny blank pages and
a lowered object bound; no real resource exhaustion. PDFium raster/search work
is protected by one process-wide mutex. General session/resource admission limits
and hostile-PDF worker isolation remain unresolved infrastructure issues.

`bounds-performance.json` separately times rejection of already allocated
synthetic inputs: oversize bytes 0.000014 s; 81 blank pages 0.00836 s on local
Python 3.12. Input allocation is outside the timer. These are not decompression,
memory-exhaustion or production load measurements.

Narrow viewport **NOT TESTED**: the browser capability accepted a requested
390×844 override, but read-only DOM measurements and screenshots remained
1280×720. The override was reset. `05-viewport-override-unapplied.jpg` is explicitly
an unsuccessful override capture, not mobile evidence. No mobile certification,
high-volume test or high-concurrency claim is made.
