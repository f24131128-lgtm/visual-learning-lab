# Visual Learning Lab

Visual Learning Lab turns PDFs and text into **source-grounded interactive learning worlds**. Bring a chapter, select a formula or diagram, explore its model, and return to the unchanged original source.

**Status: Day 29 / 30 — production hardening, prepared-only release gate.** The default entrypoint disables paid generation and uploads, even when an owner key is present. Its labeled, previously generated noncommercial competition material works without a key. [Day 29 evidence](docs/DAY29_EVIDENCE.md) records the exact release restrictions and tests. Production model configuration remains GPT-6.1 Sol (`gpt-6.1-sol`, reasoning `medium`). Frozen Day27 benchmark and Day28 AI-simulated records remain unchanged; human learning-effectiveness evidence is still pending.

```text
PDF / Text → semantic analysis → source grounding → representation planning
           → validated learning-world specification → local interactive runtime
           → direct manipulation

source evidence ↔ stable semantic entity ↔ validated canonical state
                ↔ synchronized representations
```

Model output is untrusted declarative data. Strict Structured Outputs, reference checks, bounded validators and a restricted arithmetic interpreter admit supported specifications. The app never executes generated Python, JavaScript or HTML. Safety and mathematical consistency do not establish fidelity to every source.

After compilation, selection, dragging, playback, local controls and Source ↔ Explore navigation use existing state and make **zero model requests**. Analysis, representation planning, scene/Atlas builds, explanations and focused review remain separate explicit AI actions.

## Current capabilities

- **One material, four views:** Learn, Source, Explore and Practice share the active analysis and semantic focus. Traditional Chinese is the default; English is available. UI switching is local; generated content keeps its original analysis language.
- **PDF and pasted text:** original PDF plus page-labeled text support analysis. Up to eight text-bearing pages are extracted; citations are filtered to those pages. Pasted text keeps a text source view. No OCR.
- **Traceable source:** Source Lens renders actual pages; Source Atlas links estimated regions/formulas to existing semantic IDs. Page-only support stays page-only. Optional native geometry uses pdfplumber; native coordinates do not verify meaning.
- **Interactive representations:** read-only Flow/Concept Map, Comparison, finite probability/sets, bounded planar spatial dynamics, numeric experiments, declared processes and bounded resolved call trees. Optional Analogy World and Dynamic Simulation retain their explicit build paths.
- **Direct manipulation and Grounded Semantic Twin:** structurally recognized circular, polar and affine inverses commit to the existing World or Numeric Lab store. Linked paths, waveforms and values follow that state. Unsupported entities remain grounded and focusable without a fabricated handle. Source pixels, text and boxes never change with exploration.
- **Guided learning:** source-linked lessons, local quizzes, a review queue based on checked mistakes and optional cached focused review. Explain This uses stored source context.

Explore puts the interactive object first. Playback/comparison use a compact toolbar in their own disclosure. Keyboard fallback sections, engineering camera/static controls and recording/replay UI are absent from the learner view; safe internal reducer/replay contracts remain tested. Keyboard operation of direct handles and native controls remains available.

## The 90-second proof

Start with a compiled material: select its original formula/diagram in **Source** → **Open interactive twin** → drag the highlighted object → observe linked representations and committed values → **Return to supporting source**. The focus and exploration survive; the original evidence remains unchanged. Also select a supported source quantity without an inverse: it receives no drag handle.

The 90 seconds describe the demonstration, **not model generation time or a measured novice completion guarantee**. Exact observed results, request counts, limitations and four current screenshots are in [Day 26 evidence](docs/DAY26_EVIDENCE.md).

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Run from the repository root. The default prepared mode needs no key and sends no material to OpenAI. Use the prepared-example button, then Source → linked experiment controls → Source. The bundled MIT OCW excerpt and attribution use **CC BY-NC-SA 4.0**; keep this demo noncommercial and retain attribution/license notices.

Public owner-paid deployment is **awaiting approval and external setup**. Server mode `VLL_LIVE_AI=limited-public` requires a dedicated Project/key, verified OIDC and a persisted PostgreSQL admission ledger. Policy: USD 10 lifetime; 20 requests/UTC day; one concurrent request; 2 analyses + 6 extra generations per account; visitor PDFs <=2 MiB and 2 total pages. All existing paid paths share this policy; local operations and the prepared demo remain usable after exhaustion. Missing configuration denies paid access. See [public policy](docs/public-release/POLICY.md), [release gate](docs/public-release/DEPLOYMENT.md) and [secret template](docs/public-release/secrets.example.toml).

The owner has provisioned external resources and authorized the code update to
main, while paid activation remains pending live acceptance. Keep `VLL_LIVE_AI`
empty during verification. Valid Google auth can be checked in this paid-off
mode; a logged-in account may inspect an existing ledger without an AI request.
Use the [existing-site template](docs/public-release/cloud-secrets.example.toml)
and [update checkpoint](docs/public-release/PUSH_READINESS.md).

A deliberate server-side `VLL_LIVE_AI=private` enables the existing workflow only behind independently enforced private access. That setting is not authentication and must never be used for public hosting. A private operator configures `OPENAI_API_KEY` in `.streamlit/secrets.toml`; never commit it. See the historical [Day29 deployment instructions](docs/day29/deployment-smoke.md).

Optional native document geometry:

```powershell
python -m pip install -r requirements-documents.txt
```

No Node runtime, frontend build, CDN or system Graphviz package is required for production. Dependencies are declared in `requirements.txt`; missing optional renderers/parsers preserve existing learning and source fallbacks.

## Validation and deployment limits

```powershell
python -X utf8 -B -m unittest discover -s tests -q
```

Tests cover malicious declarations/events, source/reference bounds, atomic rejection, state synchronization, request discipline and regressions. Browser gestures and source fidelity require separate acceptance; automated fixtures do not prove arbitrary-PDF correctness or learning outcomes.

`app.py` is the Streamlit entrypoint. A fresh Python 3.12 environment with product-only source passed the prepared workflow without ignored PDFs, test imports, PyMuPDF or optional pdfplumber. This is local Windows evidence, not Linux/cloud/high-concurrency certification. `requirements-public-lock.txt` records the reviewed public runtime; `requirements-day29-lock.txt` preserves the prior closure. Public PDF ingestion/rasterization uses a bounded fixed-code process; Linux resource limits remain untested here, and this is not a filesystem/network sandbox. Arbitrary-document fidelity and real-device accessibility remain open limits.

Offline JSXGraph **1.13.3** uses its MIT option with pinned assets/notices; Plotly supplies existing numeric plots. Production Source Lens now uses **pypdfium2 5.13.0**, with PDFium operations serialized and crop/rotation coordinates checked against actual rasters. PyMuPDF is a test-only fixture dependency in `requirements-test.txt`; do not deploy that environment. Retain the complete PDFium wheel license trees. This is an engineering license decision, not legal approval of historical distributions. See [license decision](docs/day29/license-decision.md), [third-party notices](THIRD_PARTY_NOTICES.md) and the [reuse ledger](docs/OPEN_SOURCE_REUSE_LEDGER.md).

## Project evolution

| Stage | Result and deeper evidence |
|---|---|
| Days 1–20 | PDF/text analysis → dedicated visualizations → source-linked explanations/lessons/review → local labs/simulations → validated scenes and source geometry. [Ecosystem decisions](docs/OPEN_SOURCE_LANDSCAPE.md), [Day 20](docs/DAY20_EVIDENCE.md). |
| Day 21 | Shared Learn/Source/Explore/Practice workspace; optional Analogy World. [Checkpoint](docs/DAY21_CHECKPOINT.md). |
| Day 22 | Explicit representation planning across formal, numeric and process capabilities. [Evidence](docs/DAY22_EVIDENCE.md). |
| Day 23 | Semantic execution contracts, stable selectors, fixed quantities and bounded resolved call trees. [Checkpoint](docs/DAY23_CHECKPOINT.md). |
| Day 24 | Safe direct manipulation through existing formal engines. [Evidence](docs/DAY24_EVIDENCE.md). |
| Day 25 | Grounded Semantic Twin: source/representation/handle joins and source roundtrips. [Evidence](docs/DAY25_EVIDENCE.md). |
| Day 26 | Simplify Explore and make one production vertical slice reviewable. [Evidence](docs/DAY26_EVIDENCE.md), [checkpoint](docs/DAY26_CHECKPOINT.md). |
| Day 27 | Freeze ten real materials, preserve first attempts, examine five deep cases and four three-run stability cases; stop for human semantic review. [Evidence](docs/DAY27_EVIDENCE.md), [checkpoint](docs/DAY27_CHECKPOINT.md). |

The [product vision](PRODUCT_VISION.md) and [UI checkpoint](docs/UI_REDESIGN_CHECKPOINT.md) describe direction and prior design evidence. Historical checkpoints preserve what was measured at that time.
