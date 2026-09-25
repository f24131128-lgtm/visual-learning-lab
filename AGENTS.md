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

## Current product behavior
- Day 12 accepts pasted text or a text-based PDF upload, one source at a time, and remains prepared for public deployment on Streamlit Community Cloud.
- `pypdf` counts pages and extracts up to eight text-bearing pages with page markers. Source page references are validated against those analyzed pages.
- For PDFs, the original file and extracted page-labeled text go to the OpenAI Responses API together. Visual analysis may inspect formulas, diagrams, graphs, waveforms, tables, and other visual learning content. There is no OCR.
- Strict Structured Outputs produce Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, Visual Flow, Concept Map, Comparison, a primary visualization decision, and a Guided Learning path.
- Relationships, Visual Flow, Concept Map, and Comparison are separate structured outputs. Relationships preserve semantic links as text. Visual Flow represents a coherent process, Concept Map represents a connected conceptual structure, and Comparison represents complete side-by-side distinctions.
- The app renders the selected Flow or Concept Map with Graphviz and renders Comparison as a static Streamlit table.
- Visual Evidence records meaningful PDF visuals with validated page numbers.
- Every Key Concept and Visual Evidence item offers Explain This. Its separate strict Structured Output request uses the selected item, Quick Summary, validated page context, relevant extracted text, and nearby analysis context. It does not resend or claim to reinspect the PDF.
- Main analysis and source context stay in `st.session_state`; explanation actions must not rerun the full analysis. Explanations are cached only for the active analyzed material and target.
- Flow nodes, Concept Map nodes, and Comparison items can be selected below the primary visualization and explained through the existing Explain This system. Their stable structured IDs provide cache identity; labels remain user-facing.
- Visualization explanations include validated node pages and connections, or existing comparison criteria and values. They reuse stored source context and never trigger the main analysis request.
- `learning_path` is generated within the main analysis request. Guided Learning reveals one validated lesson step at a time, and Explain this step reuses the existing explanation system.
- Guided Learning navigation and checkpoint grading are local. Material-specific session state stores the current step and quiz answers, and resets when new material is analyzed.
- `app.py` is the repository-root Streamlit entrypoint. Python dependencies are declared in `requirements.txt`; current Graphviz rendering uses DOT source through `st.graphviz_chart` and does not require a system `packages.txt` file.

## Product direction
This is not meant to be another AI summarizer.
The core value is turning AI understanding into visual, interactive learning experiences.

Planned directions include Timeline, Analogies, Image Breakdown, richer Source Check, and 3D / Motion.

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
- Preserve Streamlit Community Cloud compatibility: keep runtime paths portable, keep Python dependencies synchronized, and do not require local-only artifacts.

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
