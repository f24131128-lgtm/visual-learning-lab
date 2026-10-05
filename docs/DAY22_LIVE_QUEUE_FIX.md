# Day 22 live Queue path — repair and acceptance

2026-10-05. Normal production `app.py`, port 8521. No commit or push.
This record supersedes the Queue live acceptance pending status in the original
Day22 checkpoint. It does not establish acceptance for other real materials.

## What is known about the original failure

The old compiler swallowed every exception into `build_failed` and discarded
the response. The original human's rejected planner declaration was unavailable
in the accessible browser/session and logs. Consequently, its exact rejected
field and original A–L failure category **cannot be recovered**. There is no
verbatim saved failing-model fixture, and no claim that the original rejection
was reproduced.

Code inspection established a real contract defect: `normalize_process` rejected
an otherwise valid local `id` when it also appeared in the canonical semantic
catalog. Its failing stage was process normalization, the core identity check
(`identity`), before caching or rendering. Formal identity and runtime declaration
identity are separate namespaces. A declaration can legitimately use
`id="enqueue", semantic_id="enqueue"`; rejecting that semantic shape needlessly
prevents compilation.

The deterministic manual fixture used `items_state`, `act_insert`, `act_remove`
as runtime IDs, with separate `collection`, `insert`, `remove` semantic IDs.
It never exercised the overlap. The new fixture deliberately uses canonical IDs
as declaration IDs, as well as empty optional display labels and an invalid
optional annotation. It is explicitly a **shape-derived regression**, not a
claimed capture of the lost rejected response.

| Declaration | Local / canonical ID relationship | Evidence |
|---|---|---|
| Original manual FIFO | `items_state` / `collection`, `act_insert` / `insert` | Deterministic fixture passes old check |
| New regression shape | `queue` / `queue`, `enqueue` / `enqueue` | Old core condition rejects; repaired normalizer accepts |
| Fresh real accepted candidate | Runtime `queue_items`, `enqueue_c`, `dequeue_front` | Browser diagnostic; no overlap rejection occurred |

The single fresh real candidate **already succeeded before this ID repair**.
Thus the repair closes a confirmed contract hole but is not proof of the original
failure's cause. New retained candidates and field diagnostics make a future
rejection inspectable without another paid request.

## Small contract and diagnostic changes

- Trusted normalization derives stable bounded `process_<hash>` IDs only when
  a local declaration ID overlaps the formal catalog, and rewrites typed
  transition target references. Canonical semantic IDs stay unchanged. Duplicate
  local IDs, derived collisions and unknown required semantic links still reject.
- Empty labels derive from the validated canonical catalog; empty explanation
  derives from that label. Invalid optional annotations drop independently.
  Unsafe operations, broken state/targets, excess capacity and markup remain
  fatal. The strict v1.0 envelope, five operations and generic reducer remain.
- Request context now advertises the existing `process` capability. This always
  available hint is excluded from cache fingerprinting to preserve valid old
  compiled plans. No topic/source word is used as a routing condition.
- At most two bounded 48KB failed declarations remain private in the active
  material's session store. Explicit local revalidation uses no client. A
  separate explicit regenerate action permits one new request when necessary.
  Accepted state and other learning features survive failures.
- Controlled traces include stage/code/path, preferred and compiled family,
  semantic feature flags, supplied and normalized IDs, runtime entry and legacy
  use. Planner reason remains bounded in the private candidate/accepted plan;
  exported diagnostics contain its length/fingerprint, not potentially quoted
  source text. SDK exception bodies/messages and raw declarations are not
  exported. Debug UI/download requires `?learning_world_debug=1`.
- Old cached plans are explicitly marked `cached_before_diagnostics`, rather
  than fabricating an original provider response or old request count.

No new renderer, dependency, topic-specific Queue branch, feature sprint or UI
redesign. Static Visual Flow remains accessible under Formal. The existing
Explore guards render the chosen process separately and do not render the legacy
flow at the same time. No legacy precedence bug was observed or introduced.

## Real production acceptance

Used the exact user-provided text, including the blank lines and arrows, through
the normal text box in the already-running `app.py:8521`. Clicked Start/開始理解
once, then Explore/探索 and Choose/選擇適合的學習表示 once. The normal analysis
selected a concept map in this fresh run (the earlier human had a Visual Flow).
The real planner selected process and the actual generic runtime appeared.

Observed browser sequence:

1. `A → B`, front=A, rear=B.
2. Enter C, press Enter to apply the normal Streamlit text input, enqueue:
   `A → B → C`, front=A, rear=C; shared focus=`enqueue(x)`.
3. Operation dequeue: `B → C`, front=B, rear=C, last removed=A;
   shared focus=`dequeue()`.
4. Source→Explore retains `B → C` and canonical focus.
5. Reset restores `A → B`, front=A, rear=B, clears local history.

Screenshots: [initial](day22-live-queue-initial.png),
[enqueue](day22-live-queue-enqueue.png),
[dequeue with shared focus](day22-live-queue-dequeue.png),
[reset](day22-live-queue-reset.png).
[Downloaded production diagnostic](day22-live-production-diagnostics.json)
reports `compiled_family=process`, `process_runtime_reached=true` and
`legacy_visual_flow_used=false`.

**Exact fresh Queue real-material HERO case: PASS.** This is browser evidence,
not a manual fixture or AppTest substituted for a real response. It is one
successful run, not a claim that every model output is suitable.

Paid debugging requests: **2 total**, one normal analysis and one representation
plan. No regeneration loop. The candidate was retained across code reruns and
all interactions reused it. The newly installed diagnostic's `request_count=0`
measures only subsequent observed local interaction, **not** those preceding two
requests. Root AppTest independently asserts exactly two mocked requests across
the complete path and zero added calls for enqueue/dequeue/navigation/reset.

## Automated verification

`tests/day22_live_fixtures.py` is test-only; production never imports it.
`tests/test_day22_live.py` adds eight tests: namespace adaptation/stability,
same-adapter LIFO, fatal security/core errors, retained-candidate local retry,
secret/source-safe diagnostics, cache compatibility, the full blank root input
path and root local retry without OpenAI client initialization.

Focused result: **35 passed in 17.246s** (`day22-live-focused.log`). The existing
Day22 tests also cover finite-state transitions, malicious payloads, bounds,
Graphviz failure, normal PDF paths, local requests and AST/topic-route checks.
Single full post-repair regression: **339 passed in 249.450s**
(`day22-live-regression.log`). `git diff --check` passes; only pre-existing CRLF
conversion notices remain. All automated API calls are mocked. AppTests run
outside the Windows sandbox because its asyncio
socketpair fails before Streamlit app execution.

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m unittest discover -s tests -p 'test_day22*.py' -q
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -X utf8 -B -m unittest discover -s tests -q
```

## Repair files and human retest

Production repair: `learning_world/diagnostics.py` (new), `compiler.py`,
`planner.py`, `runtime.py`, `schema.py` (prompt only); small integration changes
in `app.py` and `i18n.py`. New test files are above. Documentation, controlled
diagnostic and screenshots are included. `process.py`, requirements and third
party notices are unchanged by this repair. All earlier dirty Day21/22 work and
bytecode were preserved; no reset, commit or push.

Normal startup:

```powershell
& 'C:\Users\88690\AppData\Local\Python\pythoncore-3.14-64\python.exe' -B -m streamlit run app.py --server.port 8521
```

The existing server and verified browser session remain open. Reuse that session
to enter C→Enter→enqueue→dequeue→reset without generating again. For a fresh
human run, paste the exact text from the bug report, click 開始理解 once,
探索→選擇適合的學習表示 once, verify 互動流程 selected and perform the sequence
above. Fresh analysis/planning incur their normal API costs. If a new candidate
is rejected, open the debug query and download controlled diagnostics; after a
code correction choose 本地重驗已保留的學習表示 before any explicit regeneration.
