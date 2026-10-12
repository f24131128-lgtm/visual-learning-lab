# API cost and public abuse policy

Default **prepared mode** performs zero new paid generation and disables uploads
and all new-generation CTAs. `create_client` also denies the action server-side;
UI disabling is not the security boundary. The existing prepared source, identity,
Lab, Source Lens/Atlas and navigation work without a visitor key.

**Live AI is not ready for public owner-paid exposure.** `VLL_LIVE_AI=private`
is a deliberate private-operator setting, not identity or authentication. Streamlit
session counters/caches cannot establish trusted identity, distributed rate limits,
concurrency quotas or a hard cost ceiling. This project has no enforced external
gateway/auth/budget integration. Therefore public generation remains disabled;
no public paid endpoint was deployed. Missing platform documentation retrieval
does not justify assuming enforcement exists.

All eight paid Responses sites use GPT-6.1 Sol, reasoning medium, `store=False`,
zero SDK retries and a 90-second client timeout. Output cap is 16k tokens,
simulation 8k. `response_data` rejects incomplete/malformed/nonfinite/duplicate/
over-256-KiB/deep JSON before domain normalization. Explicit retries remain learner
actions. Browser disconnect is not API cancellation and may still incur cost.

| Action / site | Input envelope | Output, attempts, failure | Cache |
|---|---|---|---|
| Main analysis, app.py | 48k selected text characters; original PDF ≤10 MiB/80 pages/20k objects, up to 8 text-bearing citation pages; fixed prompt/schema additional | 16k tokens/256 KiB, one Responses attempt and one file-upload attempt; no auto retry; fail before replacing valid material | Active session material/language; main explicitly reanalyzes |
| Explain This, app.py | 6k relevant source chars plus selected target, summary, nearby validated context | 16k/256 KiB, one attempt; errors isolated | Material + exact target |
| Focused review, app.py | 6k source chars, up to 4 mistakes, existing lesson/question/context | 16k/256 KiB, one attempt; queue/checked answers retained | Material + exact wrong-answer pattern |
| World/probability compile, scene/compiler.py | Bounded context builder target 18k chars; source ≤10k chars, existing quantities/lesson refs; no original PDF | 16k/256 KiB, one attempt; rejected specs isolated/cached under existing policy | Material + stored language/version/domain |
| Source Atlas, source_atlas/compiler.py | ≤3 analyzed rasters, PNG total ≤8 MiB, semantic context ≤24k chars, no original PDF | 16k/150k response chars and generic 256 KiB; one explicit attempt; transient error explicit retry | PDF/material/language/pages/semantic fingerprint, no exploration values |
| Planner, learning_world/compiler.py | ≤24k encoded bytes, ≤16 entities, source ≤8k chars | 16k/256 KiB and existing planner payload bounds; one attempt; retained declaration locally rechecks without client | Material/language/catalog/capabilities/focus; 4 results, 2 pending |
| Analogy, analogy/compiler.py | ≤18k chars, ≤16 entities, bounded parameters/source; no PDF | 16k/256 KiB and domain payload bound; one attempt; local recheck/cached rejection | Existing material/language/catalog/registry/focus |
| Dynamic simulation, dynamic_simulation.py | ≤30k context chars, ≤6k source chars, canonical attached lab; no PDF | 8k/256 KiB; one explicit attempt; other state retained | Material/lab spec/stored language, parameters excluded |

The file-upload site is `build_analysis_input` in app.py. Filename is fixed and
source bytes remain server-side until explicit private analysis. Existing remote
file-retention/cleanup policy is an unresolved live-mode review item.

Official [model pricing](https://developers.openai.com/api/docs/models/gpt-6.1-sol),
retrieved **2026-10-12**: Standard per million tokens $2 input, $0.10 cached input,
$2.50 cache writes, $10 output. Reasoning output is included in output totals.
No Fast/Ultrafast/regional multiplier is assumed. Historical observed-token
estimates appear in `cost-estimates.json`; they are not invoices or today's spend.
The 16 historical POST_FIX requests total approximately $1.01405 at these rates:
main five requests $0.10287–$0.14108 each, Atlas five $0.05488–$0.07076,
planner five $0.00895–$0.01517, scene one $0.04253. These fixture observations are
not typical-user averages or guarantees; the other actions were not measured.
At the output caps alone, maximum output charges are $0.16 (16k) / $0.08 (8k),
excluding input, schema, image/PDF tokens and cache charges. Character/byte bounds
are not exact token budgets. Large original PDF input can dominate cost, so these
figures must never be advertised as per-action cost ceilings.

Private live release requires an owner-approved enforced identity boundary,
per-principal and global request/token/concurrency/spend budgets, real provider
usage accounting, retention review and failure policy. No session counter is
presented as protection for a publicly exposed owner key.
