# Open-source reuse and prior-art ledger

Date checked: **2026-10-02**. Repository links are official source/README evidence;
official product sites are linked in the landscape when different. Licenses can
change between revisions: recheck the exact artifact and all transitive/model
licenses before future integration. This is an engineering audit, not legal advice.
“Available” means the repository/doc page was accessible; it is not evidence of
recent commits or production reliability. No blanket permission across ecosystems.

| Capability / project (official repo) | License observed | Stack / deployment weight | Apparent maintenance evidence | Reuse decision / expected value / risk |
|---|---|---|---|---|
| Native PDF geometry — [pdfplumber](https://github.com/jsvine/pdfplumber) | [MIT](https://raw.githubusercontent.com/jsvine/pdfplumber/stable/LICENSE.txt) | Python/pdfminer; PDFium + cryptography transitives; CPU, no model | Releases: v0.11.10; README tests Python 3.14 | **REUSE NOW**, optional pinned package; accurate native text positions, no OCR; crop/rotation and parser resource risk |
| Structured documents — [Docling](https://github.com/docling-project/docling) | MIT code, models separate | Python + inference/OCR models, local CPU options | Release page and current docs available | **ADAPT/WRAP** offline next; rich JSON/provenance; don't infer 3.14 compatibility of all transitives |
| Document parsing — [MinerU](https://github.com/opendatalab/MinerU) | [Custom Apache-based](https://raw.githubusercontent.com/opendatalab/MinerU/master/LICENSE.md), additional commercial thresholds/online attribution | Python, model/backend-specific CPU/GPU tiers | Current migration/tier docs and releases | **LEARN FROM**, no source copied; not plain Apache; substantial model/backend deployment risk |
| PDF→JSON — [Marker](https://github.com/datalab-to/marker) | Apache-2.0 code; modified AI Pubs Open Rail-M weights | Python/Torch/models, CPU/GPU/MPS | Current README and release navigation | **ADAPT/WRAP** offline only after weight terms; not blanket permissive model use |
| OCR/layout — [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | Apache-2.0 code; models individually review | Python/Paddle/inference downloads | Current OCR/VL documentation | **ADAPT/WRAP** future scanned-PDF service; handwriting quality unmeasured here |
| PDF rasters — [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/about.html) | AGPL/commercial | Existing C/Python dependency | Installed 1.26.7 | Existing **legal/deployment debt**; preserve working sources, do not copy new code; resolve intended deployment obligations before public distribution |
| PDF input — [pypdf](https://github.com/py-pdf/pypdf) | BSD-3-Clause (existing package) | Pure Python | Installed 6.19.0 | **REUSE NOW** existing extraction/page whitelist; no OCR/layout classifier |
| Document RAG — [RAGFlow](https://github.com/infiniflow/ragflow) | Apache-2.0 | Docker services; recommended 16 GB RAM/50 GB disk | README 1.0.0-rc1 2026-09-29 | **LEARN FROM**, not embed entire application in Streamlit; commodity graph/map features already extensive |
| Notebook/connectors — [SurfSense](https://github.com/MODSetter/SurfSense) | [Apache outside proprietary path, BSL 1.1 within it](https://raw.githubusercontent.com/MODSetter/SurfSense/main/LICENSE) | Web frontend/backend/database | Current repo/docs available; exact release date not resolved | **LEARN FROM**, path-specific audit; no blanket copying |
| Document notebooks — [Open Notebook](https://github.com/lfnovo/open-notebook) | MIT | Python/web app/database/provider services | Current repo/deployment docs available | **LEARN FROM** source organization; do not import an entire service into VLL |
| Hierarchical retrieval — [PageIndex](https://github.com/VectifyAI/PageIndex) | MIT as repository license display | Python/model-assisted indexing | Current repo/docs available | **ADAPT/WRAP** only for future retrieval; not source geometry or a physics runtime |
| Loaders/nodes — [LlamaIndex](https://github.com/run-llama/llama_index) | MIT core, plugins separately audit | Python modular ecosystem | Current node documentation available | **ADAPT/WRAP** individual loader if needed; dependency surface/call cost risk |
| Grounded graphs — [Docling Graph](https://github.com/docling-project/docling-graph) | MIT | Python/Docling + extraction dependencies | Current provenance docs/exports available | **LEARN FROM** source-ledger architecture; strong overlap, not a validated numerical world |
| Interactive book — [H5P Interactive Book](https://github.com/h5p/h5p-interactive-book) | MIT for this component | JS/H5P host/content libraries | Schema and repo available; release recency not resolved | **LEARN FROM** chapters/progress/restart; audit each H5P component/host, not universal H5P license |
| Question state — [H5P Question](https://github.com/h5p/h5p-question) | MIT repository component | JS/H5P dependency system | Current repo/examples available | **LEARN FROM** discrete feedback/retry states; not replacing quizzes today |
| LMS — [LearnHouse](https://github.com/learnhouse/learnhouse) | [AGPL-3.0](https://raw.githubusercontent.com/learnhouse/learnhouse/main/LICENSE) | Next.js/Python services/database | Current repo available; exact release date not resolved | **LEARN FROM** navigation only, independently implemented; do not copy code |
| Simulation shell — [PhET Joist](https://github.com/phetsims/joist) | MIT framework; individual simulations/assets differ | JS/TS framework + many sibling repositories | Development guide and framework available | **LEARN FROM** screen organization/accessibility; framework license is not simulation license |
| Educational simulation — [PhET Projectile Motion](https://github.com/phetsims/projectile-motion) | Simulation-specific multi-part LICENSE; not classified as blanket permissive | JS simulation + framework dependencies | Current repo/LICENSE available | **LEARN FROM** behavior; copy nothing, audit exact code/assets separately before reuse |
| Direct math manipulation — [JSXGraph](https://github.com/jsxgraph/jsxgraph) | Dual LGPL/MIT; MIT option available | Browser JS, local bundling possible | Current README/docs, dual-license files | **ADAPT/WRAP** later; constrain primitives/events and preserve reducer |
| Network renderer — [Cytoscape.js](https://github.com/cytoscape/cytoscape.js) | MIT | Browser/Node JS | README documents regular release policy; repo available | **ADAPT/WRAP** when current graph layout limits demonstrated; no independent semantic truth |
| Node UI — [XYFlow](https://github.com/xyflow/xyflow) | MIT core, Pro extras separate | React/Svelte JS | Current maintained-library documentation | **REUSE NOW** existing indirect flow use; do not replace working wrapper without evidence |
| Outline maps — [Markmap](https://github.com/markmap/markmap) | MIT | JS/Markdown pipeline | Current docs available, release recency not resolved | **IGNORE NOW**, duplicates simpler outline presentation, loses semantic graph distinction |
| Static diagrams — [Mermaid](https://github.com/mermaid-js/mermaid) | MIT | JS renderer | Current repo/security docs available | **ADAPT/WRAP** future exports; generated syntax/HTML must be sanitized |
| WebGL math — [MathBox](https://github.com/unconed/mathbox) | MIT | JS/WebGL/Three ecosystem | Repository available; no latest-maintenance date established | **IGNORE NOW / LEARN FROM**, more integration work than current demonstrated need |
| Analytic graphics — [Observable Plot](https://github.com/observablehq/plot) | ISC | JS/D3 SVG | Current documentation/repo available | **IGNORE NOW**, overlaps installed Plotly; reusable later in a JS-only view |
| Numeric charts — [Plotly.js](https://github.com/plotly/plotly.js) | MIT | Bundled browser JS/Python package | Current repo/release documentation | **REUSE NOW**, already powering local runtime; preserve bundled notices |
| Source viewport — [OpenSeadragon](https://github.com/openseadragon/openseadragon) | BSD-3-Clause | Browser JS, offline bundling possible | Current stable-build docs/course | **ADAPT/WRAP** later, replace pan/zoom mechanics not source identity |
| Textbook→simulation — [Augmented Physics](https://github.com/adigunturu/AugmentedPhysics) | MIT repo, separate research artifacts audit | Research web prototype, source demo assets | UIST 2024; repo has small commit history, no production maturity established | **LEARN FROM** close prior art; source-first UX, don't claim novel idea or copy a whole prototype |
| Semantic 3D tutor — [AlgeBench](https://github.com/ibenian/algebench) | MIT | Python/TypeScript/Three/MathBox | Current README development instructions | **LEARN FROM** close semantic/3D architecture; learning/safety claims not independently validated |
| Generated explainers — [ViviDoc](https://github.com/MisterBrookT/vividoc) | MIT | Generated standalone HTML/Canvas/KaTeX | ACL 2026 demo and current README | **LEARN FROM** State/Render/Transition/Constraint; reject generated-code execution model |

## Actual reuse and attribution (not hypothetical permissions)

Only the **pdfplumber public package API** is newly selected; no upstream source
is copied/adapted into our own modules. Pin 0.11.10 in a separate optional
requirements file, preserve distribution metadata/licenses, and ship the MIT
notice in `THIRD_PARTY_NOTICES.md`. Integration code is independently authored.
Its PDF extraction uses pdfminer.six; native rendering support in the package
depends on pypdfium2/PDFium, although VLL retains its existing raster path.
Cryptography/cffi/pycparser are transitive dependencies, not learning features.
Capture the resolved local versions and bundled license paths in evidence.
Do not remove wheel license metadata when redistributing an environment.

No MinerU, Marker, LearnHouse, SurfSense, PhET or competitor source/assets/models
are copied. No assumption that merely wrapping a copyleft library avoids its
obligations. Existing PyMuPDF needs a deliberate deployment-license decision;
this sprint does not silently solve it by adding a permissive parser.

## Prior-art lookup workflow

Search this table by capability before a substantial feature. Follow the source
link, inspect exact file/package/model licenses, assess portability and measured
benefit, and record why custom implementation remains necessary. Unknown dates,
licenses or accuracy are unknown, not favorable evidence. Recheck this ledger
when integrating a newer artifact. See landscape scorecard and Day 21–30 roadmap.
