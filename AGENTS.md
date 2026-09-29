# Visual Learning Lab — Codex Instructions

## Project
2026 iThome Ironman project: Visual Learning Lab.

Goal:
Turn PDFs, text, and later images into AI-generated learning visualizations.

Current stack:
- Python
- Streamlit
- OpenAI Responses API
- Structured Outputs
- Graphviz
- pypdf
- streamlit-flow-component (interactive graphs)
- PyMuPDF and Pillow (Source Lens)
- NumPy and Plotly (local mathematical experiments)

## Current product behavior
- Day 17 accepts pasted text or a text-based PDF upload, one source at a time, and remains prepared for public deployment on Streamlit Community Cloud.
- `i18n.py` owns product translations; Traditional Chinese is the default, with an English selector. `presentation.py` owns shared typography and homepage framing. Source excerpts remain in their original language.
- The selected language is stored as `analysis_language` with the active analysis and included in its material hash. UI switching makes no request; Explain This and Focused Review retain the active analysis language until explicit reanalysis.
- `pypdf` counts pages and extracts up to eight text-bearing pages with page markers. Source page references are validated against those analyzed pages.
- For PDFs, the original file and extracted page-labeled text go to the OpenAI Responses API together. Visual analysis may inspect formulas, diagrams, graphs, waveforms, tables, and other visual learning content. There is no OCR.
- Strict Structured Outputs produce Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, Visual Flow, Concept Map, Comparison, a primary visualization decision, and a Guided Learning path.
- Relationships, Visual Flow, Concept Map, and Comparison are separate structured outputs. Relationships preserve semantic links as text. Visual Flow represents a coherent process, Concept Map represents a connected conceptual structure, and Comparison represents complete side-by-side distinctions.
- The app renders Flow and Concept Map through a read-only interactive canvas, with Graphviz as an automatic/manual fallback. Comparison keeps its table with direct item-selection buttons. A compact list selector remains available for keyboard/fallback use.
- Visual Evidence records meaningful PDF visuals with validated page numbers.
- Every Key Concept and Visual Evidence item offers Explain This. Its separate strict Structured Output request uses the selected item, Quick Summary, validated page context, relevant extracted text, and nearby analysis context. It does not resend or claim to reinspect the PDF.
- Main analysis and source context stay in `st.session_state`; explanation actions must not rerun the full analysis. Explanations are cached only for the active analyzed material and target.
- Direct node/item selection opens the Learning Inspector and reuses the existing Explain This targets and caches. Stable structured IDs provide identity; labels remain user-facing. Selection itself makes no AI request.
- Visualization explanations include validated node pages and connections, or existing comparison criteria and values. They reuse stored source context and never trigger the main analysis request.
- `learning_path` is generated within the main analysis request. Guided Learning reveals one validated lesson step at a time, and Explain this step reuses the existing explanation system.
- Guided Learning navigation and checkpoint grading are local. Material-specific session state stores the current step and quiz answers, and resets when new material is analyzed.
- Checkpoint questions map to validated learning steps through stable `related_step_ids`. Checked wrong answers create a local, deduplicated Review Queue in lesson order.
- Focused Review is generated only after the learner explicitly requests it. Its cache identity includes the material and exact checked wrong-answer pattern; failures do not clear the Review Queue or other analysis state.
- Retry Check selection, grading, and before/after results are local and make no OpenAI request.
- Lesson `visual_refs` are validated against the selected visualization's type and stable IDs; bad refs are dropped without discarding the lesson. Lessons and the inspector navigate in both directions. Review/focused-review links derive from existing step IDs.
- `learning_canvas.py` owns material-specific selection, component state, and highlighting. Priority is selected > review > current lesson > default. Navigation preserves quizzes, review, explanations, and component state.
- `source_lens.py` retains only the active PDF bytes and a bounded page/DPI image cache in session memory. Source Lens renders validated pages on demand, shows extracted text separately from prior visual evidence, and highlights only verified native-text matches. Failed/missing PDF rendering falls back to extracted text; pasted text has no fake pages.
- `interactive_lab` is a separate strict output within the main analysis request: up to two source-supported demos, one x variable, 1–4 parameters, 1–3 curves, up to four scalar metrics, observation prompts, validated pages and lesson IDs. Invalid demos are dropped independently; conceptual material need not have a lab.
- `safe_math.py` interprets bounded arithmetic ASTs without Python execution. `interactive_lab.py` validates specs, renders local Plotly charts/sliders/default comparisons, and keys state by active material, specification hash, and demo ID. Lessons, inspector, and actual review mistakes link to existing demos through stable step IDs.
- Dynamic Simulation Studio is optional: an explicit build makes one targeted strict Responses request using the attached lab and bounded existing source/analysis context, never the PDF again. The main analysis schema is unchanged. Unsuitable results are cached; API failures stay isolated.
- `simulation_spec.py` validates canonical `time`, exact lab parameter IDs, fixed 2D/3D axes, whitelisted points/vectors/segments/curve markers/reference lines/circles/trails, safe numeric metrics, and source/lesson links. Optional boundary stopping is a numeric comparator with local bisection, not a new boolean grammar.
- `simulation_plot.py` reuses `safe_math.py` for bounded local trajectory arrays and one Plotly frame clock for motion, linked graphs, trails and metrics. Bundled browser-side Plotly supplies Play/Pause/speed/replay/scrubbing; a static view and labeled 3D x/y projection provide fallbacks.
- `dynamic_simulation.py` owns explicit request/UI/session caches. Specs are keyed by material, demo/specification and stored analysis language, excluding parameter values. A separate bounded numeric cache includes scene fingerprint and values. The lab remains the canonical parameter store; lesson/inspector/review links reuse stable step IDs.
- `scene/` owns Learning Scene Compiler v1. `compiler.py` performs the explicit bounded request, `schema.py` defines the strict versioned declaration, `validator.py` normalizes untrusted data, `expressions.py` parses finite-set expressions, `probability.py` derives exact/local results, `state.py` owns material/language/version/domain cache identity, and `runtime.py`/`renderers.py` coordinate the workspace.
- Learning Scene v1 fully supports only `probability_sets`. Its shared outcome/event/focus IDs bind the sample space, set view, optional probability tree, formula lens, and Monte Carlo simulation. De Morgan and inclusion–exclusion results are computed from normalized sets, never copied as unverified display text.
- Learning Scene compilation is explicit and at most one targeted request per uncached material/language/schema/domain identity. Outcome/event selection, set operations, tree navigation, special lenses, and Monte Carlo sampling are local and must preserve all existing learning state.
- `app.py` is the repository-root Streamlit entrypoint. Python dependencies are declared in `requirements.txt`; current Graphviz rendering uses DOT source through `st.graphviz_chart` and does not require a system `packages.txt` file.

## Product direction
This is not meant to be another AI summarizer.
The core value is turning AI understanding into visual, interactive learning experiences.

Planned directions include Timeline, Analogies, Image Breakdown, richer Source Check, and richer 3D experiences beyond trajectories.

## Important rules
- Do not redesign the homepage unless explicitly asked.
- Do not remove existing working features when adding a new one.
- Keep pasted-text input working.
- Preserve OpenAI API integration and Structured Outputs.
- Never expose secrets.
- Never hard-code API keys.
- Never commit .streamlit/secrets.toml.
- Prefer small incremental changes over unnecessary architecture.
- When modifying a feature, preserve previous Day functionality unless explicitly told otherwise.
- Do not hard-code test examples.
- Generated visualizations must come from user input.
- Each visualization type should have its own structured representation rather than reusing semantic Relationships blindly.
- Source references must never invent page numbers.
- Explain This must stay grounded in the active source context and clearly distinguish source support from added general knowledge.
- Preserve structured node and item IDs when adding visualization interactions. Do not use display labels or array positions as the primary identity when an ID exists.
- Guided Learning step and quiz source pages must use the same analyzed-page validation as other outputs. Navigation and grading must never trigger an OpenAI request.
- Adaptive review must use actual checked answers. Focused Review calls must remain explicit, source-grounded, cached by mistake pattern, and isolated from existing features on failure.
- Canvas editing must stay disabled; component events never replace semantic analysis. Persist component state across reruns and reset canvas/source state for new material. Keep Graphviz and accessible selection usable on component failure.
- Graph clicks, pan/zoom, source/page viewing, lesson navigation, and review navigation must never make API calls. Reuse explicit Explain This and Build focused review actions.
- Source Lens must never fabricate evidence or highlight coordinates. Only render pages validated for the active PDF; keep source text distinct from general explanatory knowledge and cache rasterization.
- Preserve Streamlit Community Cloud compatibility: keep runtime paths portable, keep Python dependencies synchronized, and do not require local-only artifacts.
- AI generates data/specifications, never executable Python. Never pass model expressions to `eval`, `exec`, shell commands, or code runners. Preserve strict AST/function allowlists, numeric limits, and computation bounds.
- Lab IDs and related learning-step IDs must stay stable. Slider/reset/baseline actions are local and must preserve existing analysis, explanations, canvas selection, lesson progress, quiz answers and review caches. New material/specifications reset stale lab values.
- Interactive Lab failure must never break main analysis, Guided Learning, Adaptive Review, or Graphviz fallback. Validate source pages with the same analyzed-page whitelist as every other output.
- Keep UI translation in the localization layer. Generated content follows stored `analysis_language`, not a newly changed UI selector. Never present a translated source excerpt as original evidence.
- Simulation output is declarative data only. Reuse the safe evaluator and primitive allowlist; never execute model-generated Python or JavaScript. Reserve `time`; do not alias an existing lab parameter with that name.
- Build simulations only on explicit learner action. Parameter changes never invalidate the AI spec cache. Frame generation, playback, timeline, speed, reset, trail/path controls and navigation must make no API request; use browser animation, never a per-frame Streamlit rerun loop.
- Preserve stable simulation/demo/lesson IDs, validated source pages, shared lab values and all existing learning state. Reset stale simulation state for new material/specifications. Bound frames, trails, traces, payloads and caches; isolate simulation failures from other features.
- Learning Scene model output is declarative only. Never accept generated HTML, JavaScript, Python, Plotly code, calls, attribute access, or indexing. Keep compiler, validator, state, probability engine, renderers, and runtime separated; do not move the scene architecture into `app.py`.
- Preserve scene semantic IDs across every representation. A renderer consumes normalized shared state; it must not invent independent event membership or probability values. Local state must not enter the compiler cache key.
- Validate scene domain/version, global ID uniqueness, references, expressions, renderer types, labels, outcomes/events, tree depth/nodes, bindings, source pages, and Monte Carlo bounds. Malformed optional scenes must fail without affecting analysis, Guided Learning, review, lab, simulation, or Source Lens.
- Day 17 and later feature work must add meaningful automated tests for pure logic, malicious/malformed model output, bounds, source/reference integrity, request counts, local interaction, graceful isolation, and regressions in any extracted code. Run the focused tests, fix failures, then run the complete relevant suite once.

## Workflow
Before editing:
1. Inspect the existing code.
2. Preserve working behavior.
3. Make only the changes needed for the current task.

After editing:
1. Summarize files changed.
2. Mention any new dependency.
3. Give the exact command needed to run the app.
4. Do not give a long tutorial unless asked.
