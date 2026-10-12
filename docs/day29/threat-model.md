# Day29 code-grounded threat model

2026-10-12, Asia/Taipei. Scope: existing app, local adversarial tests and default
prepared mode. No external penetration test, paid model probe or deployment.

| Asset / attacker goal | Boundary and code control | Remaining limit / OWASP LLM mapping |
|---|---|---|
| Owner API key / theft, paid abuse | `production_safety.create_client` rejects default/public mode before SDK initialization; all six constructor modules use it. Keys are never compiler context. `.gitignore` excludes secrets. | Private mode is not authentication; no distributed budget/rate enforcement. LLM02 sensitive disclosure, LLM06 excessive agency, LLM10 unbounded consumption. |
| Uploaded PDF, text, images / resource exhaustion or path access | Streamlit → `checked_pdf`: 10 MiB, 80 pages, 20k xref objects, signature/name/MIME/encryption/finite dimensions. `extract_pdf_text`: 8 text-bearing pages and 48k selected characters. Uploaded names are not local paths; API filename is fixed `uploaded.pdf`. Public uploader disabled. | Decompression/native parsing is not process-isolated. Malicious documents remain private-only. LLM10. |
| Original source integrity / replace source facts | PDF bytes in `learning_canvas.source`, original text in `source_context`; `quantity_contract` separates fixed facts from hypothetical parameters. World/manipulation commit only canonical values. Prepared loader hashes immutable artifacts. | Grounding is estimated, mathematical checks do not prove semantic fidelity. LLM04 poisoning, LLM09 misinformation. |
| Semantic declarations / execute code or invent ownership | Source → fixed instructions plus untrusted input → strict Responses schema → `response_data` finite/depth/byte/duplicate checks → existing scene/planner/Atlas/ownership validators. Main required base validated independently of optional representations. | Offline captured-request tests cannot prove real model instruction obedience. LLM01 injection, LLM04, LLM05 improper output handling. |
| Browser renderer / XSS, URL/tool action | Fixed host code uses `textContent`; Flow content is HTML-escaped; numeric projections only; Plotly JSON escapes closing markup. No tools supplied in any of eight Responses sites. | Explicit Markdown links can still be learner-opened; this is not a browser isolation audit. LLM05, LLM06. |
| Runtime commits / bypass validation or alter another scene | `scene/world/state.consume_event` rejects wrong scene/revision/token; trial state validates atomically. `manipulation.state` checks material/revision/target ownership. Safe AST has no eval/exec/calls/attributes/indexes. | Browser gestures and arbitrary source fidelity need separate evidence. LLM06. |
| Session state / read another visitor's material | Material/language/spec identities and mutable caches remain in `st.session_state`. `prepared_demo.prepare` creates a fresh graph each load; PDFium's global mutex contains no source/cache. Two browser sessions use one test server with different materials. | Session state is not auth; bounded two-session evidence is not high-concurrency certification. LLM02. |
| Dependencies / supply-chain compromise, deployment exposure | Declared requirements, resolved pins, pip-audit advisories, JSXGraph hash/notice check; clean product-only source omits secrets/tests/ignored PDFs/bytecode. No commit/push/public deploy. | Native PDFium bundled-library advisories and unreachable Git objects are outside pip-audit/secret scan coverage. LLM03 supply chain. |

The external API is a separate disclosure boundary: live main analysis sends the
original PDF; targeted actions send bounded stored text and Atlas page rasters.
Ordinary local exploration never crosses it. Default mode does not initialize
the paid client even if a credential exists on the host. API failure retains the
previous valid source/analysis and displays a controlled translated error.

Reference: [OWASP LLM Top 10 2025](https://genai.owasp.org/llm-top-10/), retrieved
2026-10-12. Mappings identify applicable risks, not an OWASP certification.
