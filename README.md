# Visual Learning Lab

A 2026 iThome Ironman project built with ChatGPT × Codex × Vibe Coding. It turns learning content into structured explanations and visual learning aids.

**Status:** Day 20 / 30 — ecosystem research and optional native document geometry (human live acceptance pending).

## Day 20 — reuse before rebuilding

Live native-text integration fix: ordinary source `->` arrows/comparison operators are preserved as literal text without relaxing generated Atlas markup rules. See [exact PDF reproduction and regressions](docs/DAY20_NATIVE_TEXT_FIX.md).

[Landscape and architecture decisions](docs/OPEN_SOURCE_LANDSCAPE.md), [license/reuse ledger](docs/OPEN_SOURCE_REUSE_LEDGER.md), and [reproducible evidence](docs/DAY20_EVIDENCE.md) cover the research, rejected candidates, limits and Day 21–30 roadmap. Existing Day 1–19 paths remain in place.

An optional **本機解析文件結構 / Inspect document structure locally** action in Source Atlas uses pdfplumber to expose native text regions without an AI request, even before a semantic scene exists. It supplies bounded geometry hints to a later explicit Atlas build and refines only unique exact whole-line formula/label matches. It does not identify diagrams, infer semantic IDs, execute formulas, perform OCR, or upgrade semantic confidence.

Install the optional adapter with `python -m pip install -r requirements-documents.txt`; the base requirements are unchanged. Start with `python -m streamlit run app.py --server.port 8521`. Missing packages, unsupported page frames, dense pages or malformed PDFs leave the original Source Atlas/Source Lens and learning world usable. The local adapter accepts at most three analyzed pages, 20 MiB PDF input, 24 text regions/page and 64 total; it declines over-bound pages rather than silently sampling them. Existing PyMuPDF licensing obligations still require review; see [third-party notices](THIRD_PARTY_NOTICES.md).

Offline checks: `python -B -m unittest tests.test_day20 tests.test_day19 tests.test_day19_optional_scene -q`, then `python -B -m unittest discover -s tests -q`. Reproduce the synthetic benchmark with `python -B tests/benchmark_day20.py`. These are not real-user PDF accuracy or browser gesture acceptance results.

## What works

- **繁體中文 is the default product language**, with an English selector. The chosen language controls new generated analyses, lessons, quizzes, lab instructions, explanations, and reviews. Switching the UI language is local; existing generated content retains its stored analysis language until you analyze again. Original source excerpts and mathematical variables remain unchanged.
- A shared Chinese/English font stack, stronger text, comfortable line spacing, and clearer graph labels improve reading on laptops and smaller screens. No font downloads are required.
- Paste text or upload a text-based PDF. `pypdf` counts pages, extracts text from up to eight extractable pages, and keeps page labels for source tracing. Source page references are checked against those analyzed pages.
- For PDF input, the original file is also sent to the OpenAI Responses API alongside the extracted text. The model can inspect formulas, diagrams, graphs, waveforms, tables, and other visual content. Image-only PDFs without extractable text are not supported yet; there is no OCR.
- Strict Structured Outputs provide a Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, dedicated Flow, Concept Map, and Comparison data, a primary visualization decision, and a Guided Learning path.
- Relationships remain complete semantic text output. The app automatically chooses Visual Flow for an ordered process, Concept Map for conceptual structure, or a side-by-side Comparison table. Each visualization has its own validated representation.
- Every Key Concept and Visual Evidence item has **Explain this**. It provides a focused, source-aware clarification in place, using the active analysis and relevant extracted text so the learner does not have to paste the material again.
- The **Interactive Learning Canvas** supports direct node clicks, pan, and zoom for Flow and Concept Map, plus item buttons beneath Comparison. A shared **Learning Inspector** connects the selected item to its relationships, source pages, existing Explain This action, and related lessons. Graphs are read-only; stable IDs keep every interaction tied to the analysis.
- **Source Lens** previews actual, validated PDF pages on demand beside their extracted text and existing Visual Evidence. Only the active PDF is held in session memory. Page images are cached with a memory bound. Deterministic text matching can highlight a unique native PDF text location; ambiguous or missing matches show page context without a highlight. Pasted text gets a text-only source view. No OCR or extra AI request is involved.
- Guided Learning turns the analysis into a short step-by-step lesson followed by a local multiple-choice Knowledge Check. Step navigation and quiz grading do not call OpenAI. **Explain this step** reuses the existing cached, source-grounded explanation system.
- Checkpoint questions map back to lesson steps. Missed questions produce a local Review Queue, and learners can jump directly to the relevant existing step without another API request.
- **Build focused review** is an optional, explicitly triggered AI request based on the learner’s actual checked wrong answers. Its small Retry Check is graded locally and shows the original and retry results side by side.
- Guided Learning steps link to validated visualization IDs: lesson navigation highlights the related elements, and the inspector can jump back to a related lesson. Adaptive Review and Focused Review mark relevant elements as needing review. Selection takes visual priority over review, then the current lesson; selecting a node preserves learning and quiz progress.
- Graphviz remains the fallback if the interactive renderer fails. **Choose from list instead** provides keyboard selection and a manual Graphviz switch for browser component failures. Graph clicks, source viewing, lesson/review navigation, and quiz grading make no OpenAI requests.
- **Interactive Lab** turns supported mathematical relationships into one or two parameter experiments, generated within the main analysis request. Sliders update Plotly curves and derived values locally, with hover, fixed default curves for comparison, parameter reset, and short observation prompts. **Slider movement does not call OpenAI.**
- Lessons and the Learning Inspector can open related experiments. Checked mistakes and Focused Review recommend existing experiments through validated lesson IDs. Experiments also link back to lessons; navigation preserves quiz answers, review results, selection, and explanation caches.
- **Create dynamic simulation** is an optional, explicit request for a suitable existing lab. It uses bounded prior analysis, formulas, parameter definitions, validated lessons/pages, and extracted source text; it does not resend the PDF or expand the main analysis schema. Saved simulations reopen without another request.
- **Dynamic Simulation Studio** animates source-supported 2D points, vectors, segments, and curve markers, with optional 3D point trajectories and orbit controls. Play/Pause, playback speed, replay, a time scrubber, and synchronized frame metrics run in the browser. Trails show positions already traveled; a faint full path and static view are available.
- Simulations use the lab's **same parameter values and sliders**. Parameter changes recompute trajectories locally and restart playback; they never regenerate the AI scene. Related lessons and the inspector can explicitly build or open a simulation. Checked mistakes and Focused Review recommend existing simulations through validated lesson IDs, with no automatic request or claim of improved learning.
- Suitable finite probability/set material can explicitly **Build Learning Scene**. One targeted strict Structured Output compiles outcomes, events, stages, views, bindings, focus targets, and source references into a shared semantic world. Ordinary analysis does not pay for this second request.
- The probability workspace synchronizes a clickable sample space, data-driven set view, optional probability tree, formula/reasoning lens, and deterministic Monte Carlo simulation. Event or outcome focus is shared across every view. Union, intersection, complement, difference, De Morgan's laws, and inclusion–exclusion are computed locally from validated sets; changing controls makes no OpenAI request.

## Source Atlas — Day 19

PDF material with visual evidence or scene-linked source pages offers **建立來源互動圖譜 / Build Source Atlas** before the learning overview. Select up to **three analyzed pages**, ranked using Day 6 Visual Evidence, scene source pages and current focus. One explicit Responses request receives only those original page rasters, bounded extracted text/analysis and existing semantic IDs. No OCR, whole-PDF resend, executable renderer code or main-analysis schema change.

`source_atlas/` separates strict v1.0 schema/compiler, validator/evidence graph/formula trace, canonical-focus adapter/cache and fixed viewer. Boxes use each complete rotated/cropped page's top-left (0,0) to bottom-right (1,1), via existing Source Lens rasters; unequal page sizes are supported. Limits: 64 regions total, 24/page, eight links/region, 256 related edges, three pages, 8 MiB input raster bytes, 24,000 context characters and four cached atlases. Bad optional regions drop independently; duplicate IDs, wrong processed pages and global bounds reject only the atlas.

Original Source and Interactive Meaning share a desktop split workspace (stack on narrow screens). Click a source box or use the accessible source-object list to focus a scene quantity/event/outcome. World selection highlights the best anchor and switches pages. Source selection is a navigation hint, not a second semantic focus. **Pause world playback first**: external source navigation uses committed state, not an independent browser clock. Open as interactive scene focuses a valid cached scene without recompiling it.

Local controls: zoom/scroll, structure/labels/vectors/formulas/relationships layers, active-focus isolation, reset and high-confidence label hide/reveal. The PDF is never modified. Formula Trace follows the validated quantity DAG to parameters/equations/driven views; concept-source buttons navigate multi-page anchors. Overlays are **estimated grounding, not verified exact coordinates**. Medium confidence is dotted; low confidence never draws boxes. Excerpts are native-text-verified only when actually found in extracted text; other visual transcriptions are explicitly uncertain. Unmapped entities retain existing page-level Source Lens access.

Cache keys include material/PDF hash, stored language, atlas version, selected page set and scene/semantic fingerprint, excluding time, parameter values, selection, zoom and filters. A new scene requires an explicit new grounding build because IDs/bindings may change. Rejected output is not reused as valid; transient request failures allow an explicit retry. No local region/page/filter/label/focus action calls OpenAI. Pasted text gets no fake PDF boxes/CTA. Atlas failure preserves all previous analysis and learning features.

Offline acceptance (deterministic sources, not live AI grounding):

```powershell
python -B -m streamlit run tests/manual_day19.py --server.port 8521
```

Choose phasor or projectile sources. Check source arrow → world quantity and world selection → original source, page trace, Formula Trace, layers and labels. Production: `python -B -m streamlit run app.py`; build the scene first, then the atlas to ground current IDs. Human testing on real PDFs is required: schema validation cannot prove localization or source fidelity. See [Day 19 evidence](docs/DAY19_EVIDENCE.md).

## Learning Scene Compiler (Day 17–18 foundation)

The shared three-stage boundary remains: `scene/compiler.py` sends bounded existing analysis and extracted source context through one explicit request; `scene/validator.py` treats the declaration as untrusted; `scene/runtime.py` dispatches to the domain runtime. The main analysis includes a small strict suitability/domain field (`probability_sets`, `spatial_dynamics`, or `none`), not a complete generated world. Source-text heuristics also support older analyses.

The v1 domain is deliberately narrow: `probability_sets`. A scene declares a finite sample space, weighted outcomes, event membership, optional staged paths, semantic relations, known view types, bindings, focus targets, and validated source pages. It cannot contain HTML, JavaScript, Python, arbitrary Plotly code, calls, indexing, or attribute access. `scene/expressions.py` implements only event IDs, `|`, `&`, `~`, `-`, and parentheses with length/depth limits.

Compilation is cached by material identity, stored analysis language, scene schema version, and domain. Local focus, selected outcomes, learning lens, Monte Carlo count, and deterministic seed are excluded from cache identity. The validator bounds outcomes, events, tree depth/nodes, bindings, labels, expressions, renderer types, and source pages. Malformed scenes fail inside the optional workspace without removing the analysis, lessons, lab, review, or simulation.

**API usage:** main analysis: one request; first uncached Learning Scene build: one optional request. Event/outcome selection, set operations, De Morgan and inclusion–exclusion lenses, probability-tree navigation, and 100/1,000/10,000-trial Monte Carlo runs: zero requests.

## Spatial Learning World — Day 18

Suitable quantitative physics/engineering material exposes **建立空間學習場景 / Build Spatial Learning World** before the normal learning overview. This is a Learning Scene domain, not Dynamic Simulation. It compiles through the same explicit request/cache/validator/runtime boundary. The compiler uses the stored analysis language, bounded extracted source context and validated pages; it never resends the PDF. Invalid returned spatial specs are cached; transient API failures may be explicitly retried.

`scene/world/` extends the architecture with strict version 2.2 data, a safe quantity dependency graph, four forward binding types, three analytic/discrete inverse types, sampled invariants and one canonical physical state. Inverses, invariants and experiments are progressive capabilities, not prerequisites: the compiler emits empty arrays when unavailable. New optional policy declarations default conservatively to fixed time and preserved pedagogical ranges; missing base fields and malformed supplied policies still fail. Primitives are **point, vector, trajectory, and reference axis**. All use a planar x/y model today. The main workspace's **3D camera** uses the same contained clock, numeric projections and baseline ghosts (explicitly **z = 0**). It is not a volumetric 3D simulator. A separately labeled committed-state camera snapshot remains an accessible fallback.

The main workspace contains spatial, waveform, vector-plane and equation/state views. One contained offline SVG/Plotly runtime consumes only precomputed numbers; no model expression is executed in JavaScript. It plays a bounded frame sequence, pauses, resets, scrubs and changes speed without per-frame Streamlit reruns. Camera mode gates all participating views together at a bounded approximately 10 Hz, waiting for the camera render rather than allowing waveform time to run ahead. Camera rotation/zoom persists via `uirevision`; unavailable camera rendering falls back to synchronized 2D. Waveform clicks return time, vector-angle dragging returns a validated time/parameter patch, and trajectory clicks return the nearest sampled time. Gestures commit on release; Play commits on Pause/end. During playback the contained workspace owns the active local clock; the server retains the last committed state. Keyboard time selection is also available.

`policy.py` coordinates legal parameter ranges, semantic time and numeric viewports. Range priority is explicit source range, validated pedagogical range, then a declared semantic-type/baseline fallback. Angular controls may display degrees while storing radians. Time supports `fixed_duration`, parameter-only safe `derived_duration`, and `periodic_duration` (1–8 periods), capped at 10,000 time units. A same-height flight can declare `2*speed*sin(angle)/gravity`; all curves and paths end at that same locally recomputed time. There is no automatic guessing of a ground condition from labels, nor a new arbitrary termination solver. A shortened event atomically clamps existing time to its endpoint.

Validation derives a safety viewport from bounded defaults/corners/endpoints over their semantic durations; finite coordinate limits remain ±1,000,000. The displayed viewport fits the complete current trajectory plus any baseline, using equal physical scales and an 8% margin. Thus broad useful ranges do not make a normal flight microscopic. Reference-axis extents include both directions. The model's undersized but finite axes hint cannot force parameter-range shrinkage. Actual local states are rechecked before commit; deterministic sampling is not an analytic proof.

Focus links vector/curve/metric representations through canonical quantity IDs and their dependencies. Baselines produce faint spatial ghosts, baseline waveforms/cursors and numeric deltas. Source labels stay subtle, with existing Source Lens access for a selected quantity. Primary parameter, focus, baseline, experiment and recording controls live inside the coordinated runtime: each action commits the currently displayed time atomically with its semantic change. Keyboard fallback controls operate on the last committed state; pause playback before using them. All these actions are local. Recordings contain state patches only, not source text or secrets, and are session-only (not exported or persisted).

The consistency checker samples defaults, parameter corners/endpoints and legal times; each actual local state is checked again. It rejects cycles, contradictory/missing bindings, unsafe expressions, out-of-range coordinates, false declared invariants and inconsistent inverse mappings. This is bounded numerical evidence, **not a continuous mathematical proof or a guarantee that AI physics matches the source**.

Exploration Recording & Replay records semantic changes, not keyboard input. Replay has separate 0.5×/1×/2× pacing (3.6/1.8/0.9 seconds per meaningful state), quiet progress and parameter/time/focus summaries. Presentation skips identical states only; every raw recorded patch is validated and commit indices map back to the original sequence.

Compiler/validator diagnostics remain internal: rejection reasons with field paths are logged to the terminal and retained in active session diagnostics, never displayed as debug UI. `VLL_SCENE_DEBUG=1` enables a bounded declaration trace for this logger only; it excludes credentials and extracted source text. Version 2.2 invalidates incompatible earlier scenes/rejections; numeric caches also include scene identity. A valid replacement clears old rejection/runtime data without clearing unrelated caches. The exact public three-phase material and captured real Responses outputs are covered by the [compiler integration fix report](docs/DAY18_COMPILER_FIX.md); the latest pass is documented in [the consolidated fix report](docs/DAY18_CONSOLIDATED_FIX.md).

Limits: 12 objects, eight vectors, six waveform series, 24 quantities, four parameters, 20–180 frames, 32 forward and four inverse bindings, 12 invariants with 3–64 samples each, four recipes with eight steps each, and 80 recorded steps. Numeric caches keep four parameter states; transmitted workspace/replay data is limited to 2 MiB and deduplicates frame tables. No new production dependency, CDN, frontend build, or Node runtime is needed. The camera serves a local 4.85 MB MIT-licensed Plotly.js 3.7.0 asset copied from the existing Plotly installation; numeric payload limits are unchanged. Node is used only by an optional offline frontend smoke test.

Offline acceptance (no API, fixtures never become production defaults):

```powershell
python -B -m streamlit run tests/manual_day18.py
```

Choose the three-phase rotating field, complete projectile flight or circular motion. All use the same schema, binding engine and renderer. Check scrub → all views, 3D camera → continuous synchronized playback, waveform → world, baseline → parameter delta, experiment → existing state, paced recording/replay, and trajectory/launch-angle gestures. Projectile angle is 5°–85°, speed 5–100 m/s, gravity 1–20 m/s² in that fixture's declaration, not renderer constants. Then restart the production app, analyze a real physics PDF, build once and assess the generated model/source fidelity. Do not accept Day 18 solely from offline fixtures or automated tests. Detailed evidence is in [docs/DAY18_EVIDENCE.md](docs/DAY18_EVIDENCE.md).

## Dynamic Simulation Studio

The model returns a separate strict `dynamic_simulation` object: suitability/reason, title/goal, exact attached parameter IDs, canonical `time`, fixed 2D/3D axes, an optional linked 2D graph, whitelisted objects, static series, numeric metrics, observation prompts, and source/lesson references. There are no new model-defined sliders. Unsupported motion gets a cached explanation rather than a forced animation.

`simulation_spec.py` validates scene data. `simulation_plot.py` reuses the existing safe evaluator to precompute numeric arrays and creates one Plotly frame sequence for motion, a linked graph, and metrics above the axes. `dynamic_simulation.py` owns the explicit request, session caches, UI, and navigation. Plotly's installed JavaScript is bundled into an isolated Streamlit component: no CDN, generated code, frontend build, or request per frame. The existing lab chart remains unchanged.

The spec cache uses material identity, demo ID/specification, analysis language, and schema version; parameter values are excluded. A separate bounded numeric cache includes scene fingerprint and parameter values. UI language changes do not alter the generated scene's stored analysis language. New material clears stale simulation data. Animation options preserve lessons, quizzes, review, inspector selection, and explanation caches.

A parameter-dependent end time may use a safe arithmetic expression. An optional boundary condition compares one safe numeric expression with a finite threshold; local bisection ends motion on the valid side of its first sampled crossing. It adds no boolean syntax to the evaluator. Model assumptions and units still need source review: bounded sampling is not a general collision or physics engine.

**API usage:** main analysis: one request; first uncached simulation build: one optional request. Saved opens, lab sliders/reset, Play/Pause, speed, timeline, trail/path options, frame generation, and lesson/review navigation: zero requests. Explain This, Build focused review, and Build Learning Scene retain their own existing explicit request paths.

Limits: 20–300 frames (normally 90–150), eight objects, four moving objects, two trails, three static series, four metrics, and 32 plot traces. Trails retain at most 80 sampled history points including the current position. Figure JSON is limited to 6 MiB; the session numeric cache keeps at most six entries and 4 MiB. Failed requests or unusable scenes stay isolated. Animation errors show a static path and initial point; 3D falls back to an explicitly labeled x/y projection. Continuous looping is not included in v1.

## Safe mathematical experiments

The model produces data, never executable Python. `interactive_lab.py` validates stable IDs, finite ranges, defaults, source pages, lesson links, and demo limits. `safe_math.py` interprets a restricted AST recursively: real numbers, declared variables, `pi`, `e`, arithmetic `+ - * / **`, unary signs, and one-argument `sin`, `cos`, `tan`, `exp`, `log`, `sqrt`, `abs`. No model output is passed to `eval`, `exec`, a shell, or a code runner.

Experiments are bounded to two demos, four parameters, three curves, four metrics, and 1,000 points per curve. Expression length, tree size/depth, numeric results, and exponent magnitude are bounded too. Malformed demos are skipped individually; undefined slider combinations or chart failures stay inside the lab. Conceptual material does not get a forced experiment. Parameter state belongs to the active material, language, and exact demo specification.

## Planned

Timeline, Analogies, Image Breakdown, genuinely volumetric 3D learning worlds, richer source verification, and arbitrary learner-selected text highlighting. Current Learning Scene domains cover finite probability/sets and bounded planar spatial dynamics; arbitrary geometry, field meshes, generic inverse solvers and a general physics engine remain out of scope.

## Run locally

1. Install the Python dependencies with `pip install -r requirements.txt`.
2. Create `.streamlit/secrets.toml` with your key:

   ```toml
   OPENAI_API_KEY = "your-key-here"
   ```

3. Start the app from the repository root with `streamlit run app.py`.

Never commit `.streamlit/secrets.toml` or an actual API key.

## Deployment

Deploy `app.py` from the repository root on [Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app). The Python dependencies are declared in `requirements.txt`; no external Debian package is currently required.

The canvas uses `streamlit-flow-component==1.6.1` (bundled React Flow frontend); Source Lens uses `pymupdf==1.26.7` and Pillow for in-memory page rendering. Day 15 adds `plotly>=6.0,<7.0` and explicitly declares `numpy>=1.26,<3.0`, already a Streamlit dependency, for local numeric computation. No Node.js, font binaries, or frontend build is needed. Python 3.12 is the tested runtime; compatible dependencies can also resolve on Python 3.10+. The Graphviz/text fallbacks cover optional renderer failures; the lab works independently of the canvas component.

Day 16 adds **no dependencies**. Simulation data and bundled Plotly assets can add several MiB to browser transfers; frame/trail/cache limits bound this cost. 3D requires browser WebGL. Static x/y projections remain available when it fails. An optional simulation request adds latency and model usage only when explicitly built; generation quality still needs testing with real source material.

Day 17 also adds **no dependencies**. It reuses Streamlit, Graphviz, and Plotly already declared above. A live model run is still needed to judge whether real probability PDFs compile into pedagogically faithful scenes; automated tests validate safety, set arithmetic, synchronization state, request discipline, and graceful failure.

Browser canvas availability still depends on the third-party component and browser environment. If it falls back, the list selector and Graphviz remain usable. Default typography uses locally available fonts, so appearance can vary by device. The expanded main response may take longer and cost more tokens; ordinary local interactions add no API usage.

Run the local regression suite with `python -m unittest discover -s tests -v`.

The offline suite also covers the Day 18 quantity DAG, both physical fixtures, direct/inverse mappings, sampled mathematical invariants, malformed declarations, baseline/experiments/recordings, request discipline, the normal PDF result render path and fixed frontend smoke transitions. Test fixtures never become application defaults. A real PDF/model run is still needed to assess generated scene quality; validation ensures safe computation, not fidelity to every source.

In Community Cloud, add `OPENAI_API_KEY = "your-key-here"` to the app's **Advanced settings → Secrets** instead of uploading or committing the local secrets file. See [Streamlit's secrets management guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
