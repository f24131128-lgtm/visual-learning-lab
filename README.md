# Visual Learning Lab

A 2026 iThome Ironman project built with ChatGPT × Codex × Vibe Coding. It turns learning content into structured explanations and visual learning aids.

**Status:** Day 7 / 30 — building in public.

## What works

- Paste text or upload a text-based PDF. `pypdf` counts pages, extracts text from up to eight extractable pages, and keeps page labels for source tracing. Source page references are checked against those analyzed pages.
- For PDF input, the original file is also sent to the OpenAI Responses API alongside the extracted text. The model can inspect formulas, diagrams, graphs, waveforms, tables, and other visual content. Image-only PDFs without extractable text are not supported yet; there is no OCR.
- Strict Structured Outputs provide a Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, dedicated Visual Flow and Concept Map data, and a primary visualization decision.
- Relationships remain complete semantic text output. The app automatically chooses a Graphviz Visual Flow for an ordered process or a Graphviz Concept Map for conceptual structure. Each visualization has its own validated nodes and edges.

## Planned

Timeline, Comparison, Analogies, Image Breakdown, 3D / Motion, and richer Source Check. Suggested visualization types may include these ideas, but only Visual Flow and Concept Map are rendered today.

Run the app with `streamlit run app.py` after configuring `OPENAI_API_KEY` in `.streamlit/secrets.toml`.
