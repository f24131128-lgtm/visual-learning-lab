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
- Day 7 accepts pasted text or a text-based PDF upload, one source at a time.
- `pypdf` counts pages and extracts up to eight text-bearing pages with page markers. Source page references are validated against those analyzed pages.
- For PDFs, the original file and extracted page-labeled text go to the OpenAI Responses API together. Visual analysis may inspect formulas, diagrams, graphs, waveforms, tables, and other visual learning content. There is no OCR.
- Strict Structured Outputs produce Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, Visual Flow, Concept Map, and a primary visualization decision.
- Relationships, Visual Flow, and Concept Map are separate structured outputs. Relationships preserve semantic links as text. Visual Flow represents a coherent process; Concept Map represents a connected conceptual structure. The app renders the selected primary visualization with Graphviz.
- Visual Evidence records meaningful PDF visuals with validated page numbers.

## Product direction
This is not meant to be another AI summarizer.
The core value is turning AI understanding into visual, interactive learning experiences.

Planned directions include Timeline, Comparison, Analogies, Image Breakdown, richer Source Check, and 3D / Motion.

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
