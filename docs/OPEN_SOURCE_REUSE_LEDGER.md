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


## Day 21 — workspace orchestration (2026-10-03)

Reuse the Day 20 primary-source inspections; no second landscape study or code/asset download.

| Alternative | Decision and concrete application | Cost / provenance / license boundary |
|---|---|---|
| H5P Interactive Book / Question | LEARN: one active activity; explicit checked feedback and retry; reuse existing quizzes | Existing Day 20 repository/semantics links; independent Python implementation, no H5P code/assets copied; prior component-specific license audit still applies |
| PhET Joist | LEARN: screen switching retains the system state; keep reset separate from navigation | Existing Joist/Projectile Motion sources in landscape; no dependency or assets added; Joist MIT is not a blanket simulation/assets permission |
| LearnHouse | LEARN / DEFER: activity navigation; defer LMS backend | Existing Day 20 maintenance/source evidence; do not copy AGPL platform code, no service deployment |
| Augmented Physics | LEARN: source selection is an entry into interaction; do not claim novelty | Existing primary source in landscape; no generated executable code or models adopted |
| Existing VLL scene reducer, Atlas, Lens, quizzes, Plotly | REUSE: route active views and existing stable IDs; small public internal contract | No package, renderer, parser, weights or notices added; existing PyMuPDF obligations remain unresolved |

AlgeBench semantic graph and ViviDoc State/Render/Transition/Constraint remain close prior art, not imported infrastructure. Formal/Analogy/Compare can become Explore activities later without changing top-level navigation. No renderer registry added without two production alternatives.

# Day 21 Ultra — targeted analogy decision (2026-10-03)

Eight systems/papers were inspected; no additional broad landscape scan. **REUSE** the existing safe_math AST evaluator, world reducer, semantic catalog, Streamlit component transport and installed Plotly public APIs (core [MIT license](https://github.com/plotly/plotly.js/blob/main/LICENSE)); no new dependency, upstream source, weights or artwork. **WRAP** a locally authored fixed SVG renderer receiving bounded numeric projections only. **LEARN** candidate assessment and explicit correspondences from [AnalogyMate](https://arxiv.org/abs/2401.17856), cross-domain metaphors from [Cao et al.](https://arxiv.org/abs/2308.10454), and the dynamic/static distinction from [Trey & Khan](https://www.sciencedirect.com/science/article/pii/S036013150700070X) (publisher abstract; full text unavailable). These studies do not establish this product's learning efficacy.

**LEARN** coordinated textbook interactions from [Augmented Physics](https://github.com/adigunturu/AugmentedPhysics), declarative decomposition from [ViviDoc](https://github.com/MisterBrookT/vividoc), and linked controls from [PhET Ohm's Law](https://phet.colorado.edu/en/simulations/ohms-law). No simulation assets/code are copied; framework licenses do not imply asset/model permission. **DEFER** [JSXGraph](https://github.com/jsxgraph/jsxgraph/blob/main/LICENSE.MIT): another frontend bundle adds deployment/maintenance cost without a needed capability for this bounded vocabulary. Existing PyMuPDF AGPL/commercial deployment obligations remain unresolved. The new renderer is independently written; existing notices remain applicable.

## Day 21 live mapping repair (2026-10-04)

REUSE the existing semantic catalog, canonical workspace reducer, fixed disc primitives and safe numeric projection. The repair extends correspondence cardinality and trusted normalization; it adds no parser, renderer dependency, assets, copied upstream code, weights or second graph subsystem. Earlier Day21 comparison/reuse decisions and license boundaries remain applicable. A bounded schematic is derived from validated model concepts, never a topic-specific physics fallback.

### Primitive-slot continuation (2026-10-04)

REUSE the existing fixed primitive vocabulary, safe AST interpreter, numeric projection and bounded material-specific cache for trusted empty-slot defaults and developer-only local candidate revalidation. This is normalization/diagnostics work: no parser, new renderer library, copied code, assets or executable model output; the previous Day21 upstream/license decisions remain applicable.

## Day 22 — focused representation/runtime comparison (2026-10-05)

Incremental review, not a repeat of the 30-project survey. Primary repositories,
docs, exact license files and available changelogs inspected before implementation.
No code, assets, weights or generated executables imported. Maintenance evidence
below means maintained repository/docs/changelog surfaces, not a service SLA.

| Candidate / exact license scope | Decision | Capability, deployment cost, provenance and maintenance evidence |
|---|---|---|
| [XState core LICENSE](https://github.com/statelyai/xstate/blob/main/LICENSE), MIT | LEARN | Pure synchronous [guards](https://stately.ai/docs/guards) and explicit [actions](https://stately.ai/docs/actions). Maintained v5 docs and core repo. JS actor/statechart bundle is unnecessary for bounded server-side single-step sequence mutations; callbacks still need a trusted adapter. Stately hosted services are not licensed by this file. |
| [transitions LICENSE](https://github.com/pytransitions/transitions/blob/master/LICENSE), MIT | LEARN / DEFER integration | Python FSM with optional graph/async extensions, [changelog](https://github.com/pytransitions/transitions/blob/master/Changelog.md). Lightweight alternative if hierarchical state machines become necessary. Today's operations are ordered data plus five fixed mutations; dynamic method/callback machinery adds no capability needed by acceptance. |
| [SimPy license](https://simpy.readthedocs.io/en/latest/about/license.html), MIT | DEFER | Maintained [official docs](https://simpy.readthedocs.io/en/latest/) describe Python generators and resource/event scheduling. Useful for interacting timed resources; discrete learner button operations require no scheduler. Generated generators are forbidden. No alternate GitHub fork imported. |
| [Penrose LICENSE](https://github.com/penrose/penrose/blob/main/LICENSE), MIT | LEARN / DEFER | [Core repository](https://github.com/penrose/penrose) separates domain/substance/style and constraint layout. Strong diagram grammar prior art, but a compiler/optimizer/browser stack and another DSL to bound. No copy of example diagrams or assets; those would require path-level review. |
| [bpmn-js LICENSE](https://github.com/bpmn-io/bpmn-js/blob/develop/LICENSE), bpmn.io custom MIT-like terms with mandatory watermark | IGNORE for this sprint | Maintained BPMN XML viewer/modeler [repository](https://github.com/bpmn-io/bpmn-js). Excellent business process diagrams, not ordered collection mutation. Additional browser/XML adapter and watermark obligation; do not call it unqualified MIT. |
| [JSXGraph LICENSE.MIT](https://github.com/jsxgraph/jsxgraph/blob/main/LICENSE.MIT), MIT option | DEFER | Established numeric direct manipulation. Existing world gestures already cover phase/projectile; it would not solve discrete transitions. No new offline bundle, external CDN, copied examples or assets. |
| [XYFlow LICENSE](https://github.com/xyflow/xyflow/blob/main/LICENSE), MIT core | REUSE existing wrapper | Existing pinned streamlit-flow-component already handles read-only semantic networks. Core license does not cover Pro assets. Do not add an editor or overwrite semantic data with layout events. |
| [Cytoscape.js LICENSE](https://github.com/cytoscape/cytoscape.js/blob/master/LICENSE), MIT core | DEFER | Maintained semantic graph/layout engine; no graph-scale blocker in <=16 items. Extension packages have their own licenses. No new bundle needed. |
| [Mermaid LICENSE](https://github.com/mermaid-js/mermaid/blob/develop/LICENSE), MIT | DEFER | Maintained declarative diagram syntax; another parser/security boundary and browser bundle for a small sequence. Existing graphviz Python public API quotes trusted local DOT construction and provides an accessible text fallback. No generated diagram code accepted. |
| [Plotly.js LICENSE](https://github.com/plotly/plotly.js/blob/main/LICENSE), MIT core | REUSE | Existing offline numeric projection/frame runtime, no additional download or integration. Existing world and analogy tests exercise it. Plotly commercial services are outside this license. |

Architecture: independently authored small semantic feature plan, capability adapter
and bounded process reducer. Trusted fixed operations are not a replacement for a
general FSM library: hierarchical/parallel/timed machines remain unsupported.
Reuse canonical workspace focus, Source Atlas formal IDs, existing Graphviz public
API (Python package MIT; renderer receives DOT through Streamlit), world quantity
DAG, probability engine, Analogy World and safe_math. Existing [Streamlit LICENSE](https://github.com/streamlit/streamlit/blob/develop/LICENSE)
is Apache-2.0 and [graphviz Python LICENSE.txt](https://github.com/xflr6/graphviz/blob/master/LICENSE.txt)
is MIT. Preserve installed distribution notices; the existing THIRD_PARTY_NOTICES.md
is a Day20 parser notice, not a full dependency audit. No new notice obligations
introduced. No dependency added. Existing PyMuPDF AGPL/commercial
deployment review remains unresolved; this decision does not remove it.

PhET, H5P, Augmented Physics and ViviDoc remain Day20/21 architectural references;
no simulation assets or executable-document model adopted. Docling/Docling Graph,
PageIndex, OpenSeadragon and RAGFlow stay deferred: none of the six required
generality cases needs another parser, retrieval service or viewport.

Day22 live Queue repair: WRAP the existing generic reducer and Graphviz adapter
with trusted semantic/runtime ID normalization; REUSE the existing explicit
compiler/cache and canonical Workspace focus. No additional parser, graph/FSM
package, external code, asset, model weight or dependency. This repair changes
the declaration boundary and diagnostics, not the prior license decisions.
Exact real production acceptance and its limits: [repair evidence](DAY22_LIVE_QUEUE_FIX.md).

## Day 23 — targeted investigation after frozen Phase A (client date 2026-10-05)

Measured trigger: three Comparison-only catalogs unavailable, two irrelevant
process payloads fatal, two malformed finite-state declarations, and one
parameterized numeric relationship incorrectly treated as needing time motion.
This is a four-candidate investigation, not another landscape survey.

| Candidate / exact license | Decision | Measured fit, costs, provenance and maintenance evidence |
|---|---|---|
| [Plotly.py public API/repository](https://github.com/plotly/plotly.py), [MIT code license](https://github.com/plotly/plotly.py/blob/main/LICENSE.txt); [Plotly.js core MIT](https://github.com/plotly/plotly.js/blob/main/LICENSE) | **REUSE** | Installed numeric-chart adapter already supports parameterized functions without time. No bundle/dependency/CDN needed. Repository exposes changelog/releases and existing VLL tests exercise local curves. Python docs prose has a separate CC license; commercial services are outside the core license. No upstream code or examples copied. |
| [JSXGraph repository](https://github.com/jsxgraph/jsxgraph), [exact MIT option](https://github.com/jsxgraph/jsxgraph/blob/main/LICENSE.MIT) | **LEARN FROM / DEFER integration** | Function plotting and interactive geometry confirm that parameter interaction need not mean animation. Another browser bundle, bounded numeric/gesture adapter and offline asset maintenance would not fix today's planner/catalog failures. Repo/license inspected; no independently measured installation or latency. No assets/examples imported. |
| [XState finite-state documentation](https://stately.ai/docs/finite-states), [core MIT](https://github.com/statelyai/xstate/blob/main/LICENSE), [release history](https://github.com/statelyai/xstate/releases) | **LEARN FROM** | Explicit distinction between one active state, legal state values and extended context informs neutral process prompt/contracts. Adding a JS actor runtime cannot repair invalid initial/from/to declarations and would add transport/state ownership complexity. Maintained documentation and releases visible; services and assets require separate audit. No code copied. |
| [Cytoscape.js element data/identity API](https://js.cytoscape.org/#notation/elements-json), [MIT core](https://github.com/cytoscape/cytoscape.js/blob/master/LICENSE), [release history](https://github.com/cytoscape/cytoscape.js/releases) | **LEARN FROM / DEFER integration** | Reuse existing stable element IDs independently of renderer choice. Another graph engine would still need the missing Comparison catalog adapter; current small graphs use existing Graphviz/flow wrapper. Extensions have independent licenses. No package/assets/code imported. |

No new renderer is written: existing safe_math, Plotly, Graphviz, canonical
semantic_catalog, process reducer and Workspace state are reused. Independently
written normalization/capability code only; requirements and notices unchanged.
The existing PyMuPDF AGPL/commercial deployment review remains unresolved.

Corpus provenance is separately bounded. Python documentation [license](https://docs.python.org/3/license.html)
was checked for three independent factual paraphrases (no copied code/assets).
OpenStax [damped-oscillation page](https://openstax.org/books/university-physics-volume-1/pages/15-5-damped-oscillations)
currently states restrictions on generative-AI ingestion and CC-BY-NC-SA content;
its prose/assets were excluded. Nine new excerpts are original problems, with
this substitution declared before evaluation. Do not call them retrieved PDFs
or a representative real-document corpus.

## Day 23 Phase C — semantic execution contract (2026-10-06)

Incremental investigation only; Phase A/B corpus/results remain frozen. Existing
XState/JSXGraph/Cytoscape decisions above are reused, not another broad survey.

| Candidate / exact license evidence | Decision and measured fit |
|---|---|
| [XState guards](https://stately.ai/docs/guards), [MIT core](https://github.com/statelyai/xstate/blob/main/LICENSE) | **LEARN FROM** pure enabling guards and explicit legal transitions. Existing Python reducer owns shared state; adding a JS actor service would duplicate ownership without validating numeric returns. Current official docs/license inspected. |
| [Python Tutor](https://pythontutor.com/) | **LEARN FROM UX ONLY / DEFER code** stack-frame/current-caller/value display. Repository/code/license retrieval failed; current exact reusable license unverified. No code, assets or arbitrary execution adopted. |
| [JSAV repository](https://github.com/vkaravir/JSAV), [MIT-license.txt](https://github.com/vkaravir/JSAV/blob/master/MIT-license.txt) | **LEARN FROM / DEFER integration** bounded stepping and algorithm-state presentation. Repository/changelog/tests inspected, not an independently measured deployment. Browser bundle/legacy build dependencies do not enforce source-grounded call/result contracts. OpenDSA content/extensions need separate audit. |
| [Penrose core MIT](https://github.com/penrose/penrose/blob/main/LICENSE) | **DEFER** declarative diagrams do not themselves guarantee caller-specific result routing. License inspected; detailed docs retrieval failed, so no claimed deep architecture review or asset reuse. |

**REUSE** existing safe_math AST interpreter, semantic_catalog, canonical workspace
focus, process/cache infrastructure, Plotly and Graphviz. Independently implement a
small resolved-call-tree reducer and parameter/label helpers. No new dependency,
upstream code, execution service, assets or model weights. Requirements/notices
unchanged; earlier PyMuPDF deployment obligations still apply. Same labels are a
selection contract problem, not a reason to replace the working graph renderer.
# Day 24 — direct manipulation implementation decision (2026-10-06)

Focused review, not a new Day20 landscape or benchmark. Existing Spatial World
quantity DAG/reducer/frame engine and Numeric Lab/safe_math remain the formal
engines. Analogy, probability, process, execution and Atlas remain intact.

| Candidate / exact scope | Decision | Real burden / integration / cost |
|---|---|---|
| [JSXGraph 1.13.3](https://github.com/jsxgraph/jsxgraph/releases/tag/v1.13.3), npm `jsxgraph@1.13.3/distrib/jsxgraphcore.js` + CSS | **ADAPT / WRAP NOW** | Public `initBoard`, numeric points/curves, coordinate transforms, point events, keyboard support. Removes hit-testing and board/point geometry machinery in the new adapter. One offline vanilla component, no React/npm runtime/CDN. Bundle measured locally below. Only fixed application callbacks and numeric arrays; never JessieCode, string function parents, readers, imported constructions or generated code. Canonical reducers remain Python-owned. |
| [Konva 10.0.12](https://github.com/konvajs/konva/blob/10.0.12/package.json), core browser renderer, [MIT](https://github.com/konvajs/konva/blob/10.0.12/LICENSE) | **LEARN FROM / DEFER** | Mature canvas dragstart/dragmove/dragend, transform and scene-graph support; easy vanilla iframe. Still needs mathematical constraints, axes and inverse semantics. Upstream size-limit is a build budget, not our measured deployed size. No canvas native/server package needed for browser use. No React bindings/examples/assets copied. |
| [PixiJS 8.14.3](https://github.com/pixijs/pixijs/tree/v8.14.3), browser core, [MIT](https://github.com/pixijs/pixijs/blob/v8.14.3/LICENSE) | **DEFER** | Federated events and WebGL/WebGPU suit large animated scenes; these few semantic handles do not justify GPU/canvas lifecycle, accessibility overlay or additional maths/constraint adapter. No extensions/assets installed; no package-size/performance claim measured. |
| Existing Plotly MIT browser bundle + Python API; [events](https://plotly.com/javascript/plotlyjs-events/), [editable shapes](https://plotly.com/javascript/shapes/) | **REUSE NOW** for linked charts/camera, **DEFER** drag shapes as inverse control | Already deployed. Relayout gives chart/layout updates rather than canonical formal parameter events. Shape edit does not remove our inverse, semantic focus, rejection/ack and constraints work. Keep Plotly and existing browser clock. |
| Current fixed Spatial World SVG frontend / reducers | **REUSE NOW / LEARN FROM** | Existing equal physical scale, letterboxing, release commits, revision/token rejection, frames, replay and fallbacks remain. New bounded JSXGraph component opts in only when analytic recognition proves an inverse. No universal canvas replacement. |

License choice explicitly **MIT**, per pinned [package declaration](https://raw.githubusercontent.com/jsxgraph/jsxgraph/v1.13.3/package.json)
and [LICENSE.MIT](https://raw.githubusercontent.com/jsxgraph/jsxgraph/v1.13.3/LICENSE.MIT).
Only published core JS and CSS are vendored, unchanged, with all embedded notices,
including Bjoern Hoehrmann's MIT UTF-8 decoder notice. Core JS includes the
upstream logo; not used by our boards (`showCopyright=false`, `showLogo=false`).
No examples, optional assets, readers/extensions, weights or copied handler code.
Runtime dependencies: no new Python package; one offline JS bundle 969,075 bytes,
CSS 4,767 bytes; hash manifest and notices retained beside the bundle.
Upstream releases show current maintenance and point/board APIs were inspected;
not proof of source fidelity, performance or universal formula coverage.
Existing PyMuPDF AGPL/commercial obligations remain unresolved deployment review.
