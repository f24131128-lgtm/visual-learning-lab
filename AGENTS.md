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
- User can paste text or upload a text-based PDF.
- GPT generates:
  - Quick Summary
  - Key Concepts
  - Relationships
  - Suggested Visualization
- Relationships are rendered as Visual Flow.
- PDF page labels are preserved for basic source tracing.

## Product direction
This is not meant to be another AI summarizer.
The core value is turning AI understanding into visual, interactive learning experiences.

Planned directions include:
- Concept maps
- Better flow diagrams
- Image / diagram understanding
- Formula understanding
- Source Check
- Analogies
- 3D / Motion

## Important rules
- Do not redesign the homepage unless explicitly asked.
- Do not remove existing working features when adding a new one.
- Keep pasted-text input working.
- Preserve OpenAI API integration and Structured Outputs.
- Never hard-code API keys.
- Never commit .streamlit/secrets.toml.
- Prefer small incremental changes over unnecessary architecture.
- When modifying a feature, preserve previous Day functionality unless explicitly told otherwise.
- Do not hard-code test examples.
- Generated visualizations must come from user input.
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
