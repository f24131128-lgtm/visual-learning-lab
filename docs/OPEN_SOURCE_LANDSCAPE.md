# Day 20: open-source leverage, not another isolated feature

Checked 2026-10-02. Read alongside [reuse/license ledger](OPEN_SOURCE_REUSE_LEDGER.md).
This is a repository/documentation study, not a claim that every candidate was
installed or independently accuracy-tested. Local experiments are reported
separately in `DAY20_EVIDENCE.md`. No paid model requests are needed.

## Architecture inspected before integration

The dirty Day 18/19 worktree is retained. Existing pipeline:
`pypdf + original PDF → analysis → explicit validated scene → canonical state
→ coordinated runtime`. Source Lens owns PDF bytes/rasters; Source Atlas adds
estimated semantic boxes, a bounded source graph, formula trace and focus bridge.

| Subsystem | Commodity infrastructure already reused | Custom work to retain or reconsider |
|---|---|---|
| Input | pypdf, PyMuPDF, Pillow | Page whitelist, active-material identity; native document structure absent |
| Understanding | Responses Structured Outputs | Separate semantic declarations and validators, never generated executable code |
| Graphs | React Flow through streamlit-flow, Graphviz | Stable IDs, read-only selection, lessons/review linking; do not build another graph engine |
| Mathematics | NumPy, Plotly | Bounded safe expressions, canonical quantity DAG, validated inverses/invariants |
| Playback | Bundled Plotly | One contained clock and validated reducer commits; direct SVG gestures are maintenance debt |
| Sources | Existing PDF raster library | Atlas box estimates and hand-built overlays; deterministic native geometry is an immediate gap |
| Learning | Streamlit widgets | Lessons, checked mistakes and provenance; separate prompt/activity/feedback rather than accumulating vertical dumps |

## Document intelligence comparison — decision before implementation

| Candidate | Layout/formulas/figures/order | Coordinates/provenance | Deployment and risk | Decision |
|---|---|---|---|---|
| Current pipeline | Model sees visual pages; pypdf supplies native text; no OCR | Estimated semantic boxes; validated pages, native text anchors in Source Lens | Already working; no new models; grounding not exact | Retain semantics and raster fallback; augment geometry |
| [Docling](https://github.com/docling-project/docling) | Layout, table structure, reading order, formulas, OCR; JSON document model | DoclingDocument item provenance | Local execution possible; inference/model dependencies; Python minimum alone does not prove every 3.14 wheel works | Best structured/offline next candidate, not mandatory runtime today |
| [MinerU](https://github.com/opendatalab/MinerU) | Broad structured document/OCR/ formula capabilities | JSON and block/page locators | Current custom Apache-based license and model/backend requirements | Study/isolated benchmark later; no source copying or main dependency |
| [pdfplumber](https://github.com/jsvine/pdfplumber) | Native characters, text-line geometry and tables; not OCR or semantic formula recognition | Native PDF coordinates, object properties | MIT, CPU, official 3.14 tests; lightweight relative to neural parsers | Wrap now for explicit local source structure and conservative exact-text anchors |
| [Marker](https://github.com/datalab-to/marker) | Markdown/JSON, equations/tables, image extraction | Structured document output | Current code Apache-2.0, separately restricted model weights; CPU/GPU/MPS supported does not mean Cloud latency is acceptable | Offline comparison, not automatic runtime install |
| [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) | OCR and document structure; multilingual | OCR boxes/structured output | Apache-2.0 code; additional inference binaries/models to review individually | Candidate for scanned materials, not a silent change to current text-PDF acceptance |

Sources are feature claims, not our measured accuracy. Real 7-page probability
notes, user lecture slides and handwritten PDFs are **not present in tracked or
untracked repo PDF inventory**; do not pretend to benchmark them. Use existing
Day 19 phasor/projectile source generators and a small inspectable fixture for
probability, formulas and image-only/messy marks. Report missing user corpus.

The selected integration must add an explicit local mode inside the existing
Atlas area, not an app.py section. It reuses Atlas's region schema/validator and
Source Lens raster, supplies no independent semantic focus, and preserves the
explicit semantic compiler. Native boxes can refine a semantic formula/label
only on a unique exact whole-line source match. No guessing based on lexical
similarity, no moving vectors to a nearby label, no fabricated formula semantics.

Coordinate risk is concrete, not hypothetical: pdfplumber distinguishes media
and crop boxes; [crop issue #245](https://github.com/jsvine/pdfplumber/issues/245)
illustrates why offsets cannot be ignored. Match complete rotated/cropped raster
coordinates with tests, otherwise preserve the prior estimate. Release
[v0.11.10](https://github.com/jsvine/pdfplumber/releases/tag/v0.11.10) updates
dependencies following [issue #1374](https://github.com/jsvine/pdfplumber/issues/1374).

## Knowledge/document systems

| Project | Useful leverage | Why not replace VLL with it |
|---|---|---|
| [RAGFlow](https://github.com/infiniflow/ragflow) | Document parsing/retrieval and generated knowledge artifacts | Recommended Docker baseline 4 cores/16 GB/50 GB, not a Streamlit library; current README already lists mind maps/timelines/graphs/PageIndex: those pitches are commodity |
| [SurfSense](https://github.com/MODSetter/SurfSense) | Source connectors, notebook-oriented information workspace | Apache core plus BSL proprietary directory; larger web/backend stack, path-specific license audit required |
| [Open Notebook](https://github.com/lfnovo/open-notebook) | Notebook/source organization, multi-provider document interactions | MIT but an application/service stack, not a semantic simulation validator |
| [PageIndex](https://github.com/VectifyAI/PageIndex) | Hierarchical document navigation and reasoning-based retrieval | Retrieval/index building is distinct from local system manipulation; do not add per-interaction model calls |
| [LlamaIndex](https://github.com/run-llama/llama_index) | Document/Node abstractions and loader ecosystem | Adapter/component reuse rather than replacing our state or claiming generic RAG is unique |
| [Docling Graph](https://github.com/docling-project/docling-graph) | Document-to-graph provenance bookkeeping | Important close prior art for region↔entity links; generated knowledge graph is not the same as validated numerical execution |

Docling Graph's [provenance guide](https://github.com/docling-project/docling-graph/blob/main/docs/fundamentals/graph-management/provenance.md)
describes chunk/item geometry and per-node lineage. Source provenance alone is
not a moat. Borrow the distinction between evidence location and entity meaning;
never treat a parser's geometry as proof of semantic correctness.

## Renderer selection: avoid rebuilding solved engines

| Capability | Recommended building block | Decision for current runtime |
|---|---|---|
| Numeric curves, frames, basic 3D | [Plotly](https://github.com/plotly/plotly.js), already installed | Reuse now; retain contained shared clock |
| Direct 2D mathematical construction | [JSXGraph](https://github.com/jsxgraph/jsxgraph), choose MIT dual-license option | Wrap later: numerical projections and gesture events only, never model scripts |
| General semantic networks | [Cytoscape.js](https://github.com/cytoscape/cytoscape.js) | Prototype only when graph size/layout warrants replacing current flow wrapper |
| Read-only process graphs | [XYFlow](https://github.com/xyflow/xyflow), already indirectly used | Keep existing working canvas; editable mode remains disabled |
| Simple outline export | [Markmap](https://github.com/markmap/markmap) | Ignore for now: hierarchy is not our graph model or shared-state runtime |
| Static process diagrams | [Mermaid](https://github.com/mermaid-js/mermaid) | Optional export later; strict security mode and adapter-generated syntax required |
| Presentation-quality mathematical WebGL | [MathBox](https://github.com/unconed/mathbox) | Learn from; larger renderer integration and context-loss risk, no demonstrated current replacement benefit |
| Compact analytic SVG charts | [Observable Plot](https://github.com/observablehq/plot) | Good future JS option, but duplicating Plotly today adds no measured value |
| High-resolution source pan/zoom/hotspots | [OpenSeadragon](https://github.com/openseadragon/openseadragon) | Strong later replacement for bespoke viewer mechanics, not semantic focus/state |

A renderer registry is **not implemented today**: existing fixed domains do not
yet have two production renderer alternatives. Adding a registry now would be
abstraction without demonstrated leverage. Define capability contracts first.

## Mature learning UX — concrete findings and independent recommendations

- H5P Interactive Book declares chapters, default table of contents, page progress,
  summary and restart separately in [semantics.json](https://raw.githubusercontent.com/h5p/h5p-interactive-book/master/semantics.json).
  Recommendation: one active activity panel plus source/meaning context;
  completion is checked task state, not merely scrolling past a visualization.
- [H5P Question](https://github.com/h5p/h5p-question) and
  [Question Set](https://h5p.org/question-set) separate exercise/feedback/retry
  behavior. Recommendation: submit, checked feedback, retry and solution reveal
  should have explicit state transitions. Do not change quiz generation today.
- [LearnHouse](https://github.com/learnhouse/learnhouse) organizes courses and
  activities in a dedicated learning platform. Study its navigation, not its AGPL
  code. VLL needs a learning-object navigation model, not the entire LMS backend.
- [PhET Joist](https://github.com/phetsims/joist) owns home screens and screen
  switching; [Projectile Motion](https://github.com/phetsims/projectile-motion)
  is a concrete mature experiment example. Recommendation: distinct experiment
  goals, reset and parameter panel; keep observer controls separate from system
  controls. Accessibility needs labels/keyboard/feedback, not just clickable SVG.
  Joist's MIT license does not grant permission to redistribute every simulation,
  artwork, branding or asset; check the exact simulation license.

These are documented principles, not claims that we usability-tested those apps
or that VLL learning outcomes improved. Keep existing keyboard/list fallbacks.

## Uncomfortable prior art: overlap is real

| Project | Overlap / stronger aspect | Difference supported by our inspected code | Borrow / stop claiming |
|---|---|---|---|
| [Augmented Physics](https://github.com/adigunturu/AugmentedPhysics) | Static textbook diagrams → embedded simulations; bidirectional parameters and source-page augmentation, UIST 2024 research | Our bounded declarative quantity DAG, shared cross-view reducer and rejection tests are an explicit implementation emphasis; this is not proof of uniqueness | Borrow source-first experiment presentation; stop claiming source-linked interactive physics was invented here |
| [AlgeBench](https://github.com/ibenian/algebench) | Interactive 3D math, AI tutor, semantic graph-based visualization, richer 3D scope | Our product currently emphasizes original PDF evidence, validated source IDs and local bounded specs | Study renderer/lesson architecture; do not assume competitor lacks shared state or safety without full audit |
| [ViviDoc](https://github.com/MisterBrookT/vividoc) | AI-authored explorable documents, equations, State/Render/Transition/Constraint design | It emits standalone executable HTML; VLL forbids generated executable code and uses fixed renderers | Borrow interaction state decomposition; do not integrate its execution model |
| Docling Graph | Grounded graph nodes and geometry-ledger provenance | Our sources connect into local probability/physics reducers and learning interactions | Stop pitching region↔graph linkage alone as new |
| RAGFlow / notebook systems | Document intelligence, source chat, maps and knowledge artifacts | Numerical worlds, inverses and local exploration are our focus | Stop building a competing generic document chat platform |

Finding these projects is not a novelty/patent search or exhaustive competitor
audit. None of their code is copied in this sprint.

## Leverage scorecard / architecture decision

**REUSE NOW:** pdfplumber native geometry via a small optional adapter; existing
Plotly/pypdf/flow libraries. Narrow, measurable capability and manageable CPU use.

**ADAPT / WRAP:** Docling offline structured output (next comparison); JSXGraph
numeric gesture adapter; OpenSeadragon source viewport; Cytoscape only if needed.

**LEARN FROM:** PhET learning screens, H5P interaction states, LearnHouse navigation,
Augmented Physics source-first UX, Docling Graph provenance ledger.

**IGNORE FOR NOW:** another RAG server, mind-map engine, general WebGL replacement,
automatic large model install, generated HTML runtime. These are not bad projects;
they solve different problems or impose unjustified cost today.

Stop building PDF geometry/layout inference, graph-layout engines, generic RAG,
document chat, standalone flashcard systems and pan/zoom mechanics from scratch.
Double down on the **verified connection contract**: evidence locators with honest
uncertainty → stable semantic entities → validated state transitions → several
synchronized representations → actual learner actions/mistakes. Treat this as a
testable architectural focus, not a proven exclusive moat. Future persistent
mastery state is still work: today's recordings/state are session-local.

## Day 21–30 leverage roadmap (recommendations, not commitments)

| Day | Evidence-driven next step | Gate |
|---|---|---|
| 21 | Benchmark Docling offline on the actual user corpus | Ground truth and wheel/model/license manifest; no mandatory heavyweight runtime |
| 22 | Region/provenance uncertainty review workflow | Distinguish native geometry, OCR estimate and semantic support |
| 23 | OpenSeadragon viewport prototype | Offline bundle, accessible selection, same Atlas event contract |
| 24 | JSXGraph direct-manipulation adapter | Same reducer/projections, bounded inverses, no generated code |
| 25 | Learning-object workspace navigation inspired by H5P/PhET | Preserve all current state, explicit lesson/activity/check/review modes |
| 26 | Interaction state primitives for retry/hints/reveal | Accessibility and local transitions; no parallel quiz engine |
| 27 | Persist validated learner state | Privacy, schema migrations, restore identity and quotas |
| 28 | Optional document retrieval adapter | Only if multi-document learning requires it; use existing ecosystem |
| 29 | Cross-parser/renderer security and dependency audit | Bad external data, supply-chain notices, deployment resource budgets |
| 30 | User acceptance and measured product demonstration | Actual PDFs, real gestures, honest failure cases, no invented accuracy |
