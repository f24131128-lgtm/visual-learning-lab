# Visual Learning Lab

A 2026 iThome Ironman project built with ChatGPT × Codex × Vibe Coding. It turns learning content into structured explanations and visual learning aids.

**Status:** Day 17 / 30 — Learning Scene Compiler v1.

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

## Learning Scene Compiler

Day 17 introduces a three-stage boundary: `scene/compiler.py` sends bounded existing analysis and extracted source context through one explicit request; `scene/validator.py` treats the declarative response as untrusted and normalizes it; `scene/runtime.py` and the whitelisted renderers project the resulting semantic state into coordinated views. The main analysis schema remains unchanged.

The v1 domain is deliberately narrow: `probability_sets`. A scene declares a finite sample space, weighted outcomes, event membership, optional staged paths, semantic relations, known view types, bindings, focus targets, and validated source pages. It cannot contain HTML, JavaScript, Python, arbitrary Plotly code, calls, indexing, or attribute access. `scene/expressions.py` implements only event IDs, `|`, `&`, `~`, `-`, and parentheses with length/depth limits.

Compilation is cached by material identity, stored analysis language, scene schema version, and domain. Local focus, selected outcomes, learning lens, Monte Carlo count, and deterministic seed are excluded from cache identity. The validator bounds outcomes, events, tree depth/nodes, bindings, labels, expressions, renderer types, and source pages. Malformed scenes fail inside the optional workspace without removing the analysis, lessons, lab, review, or simulation.

**API usage:** main analysis: one request; first uncached Learning Scene build: one optional request. Event/outcome selection, set operations, De Morgan and inclusion–exclusion lenses, probability-tree navigation, and 100/1,000/10,000-trial Monte Carlo runs: zero requests.

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

Timeline, Analogies, Image Breakdown, richer 3D experiences beyond trajectories, richer source verification, and arbitrary learner-selected text highlighting. Future Learning Scene domains may coordinate objects, vectors, graphs, equations, waveforms, or 3D views, but v1 does not claim support beyond finite probability and sets.

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

The offline suite covers finite-set expression security and algebra, De Morgan and inclusion–exclusion derivation, deterministic bounded Monte Carlo, scene/schema/reference/source validation, explicit scene request counts and local interactions, plus the earlier lab, simulation, canvas, source, review, and learning regressions. Test fixtures never become application defaults. A real PDF/model run is still needed to assess generated scene quality; validation ensures safe computation, not mathematical fidelity to every source.

In Community Cloud, add `OPENAI_API_KEY = "your-key-here"` to the app's **Advanced settings → Secrets** instead of uploading or committing the local secrets file. See [Streamlit's secrets management guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
