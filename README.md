# Visual Learning Lab

A 2026 iThome Ironman project built with ChatGPT × Codex × Vibe Coding. It turns learning content into structured explanations and visual learning aids.

**Status:** Day 8 / 30 — building in public.

## What works

- Paste text or upload a text-based PDF. `pypdf` counts pages, extracts text from up to eight extractable pages, and keeps page labels for source tracing. Source page references are checked against those analyzed pages.
- For PDF input, the original file is also sent to the OpenAI Responses API alongside the extracted text. The model can inspect formulas, diagrams, graphs, waveforms, tables, and other visual content. Image-only PDFs without extractable text are not supported yet; there is no OCR.
- Strict Structured Outputs provide a Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, dedicated Flow, Concept Map, and Comparison data, and a primary visualization decision.
- Relationships remain complete semantic text output. The app automatically chooses a Graphviz Visual Flow for an ordered process, a Graphviz Concept Map for conceptual structure, or a side-by-side Comparison table for meaningful parallel distinctions. Each visualization has its own validated representation.

## Planned

Timeline, Analogies, Image Breakdown, 3D / Motion, and richer Source Check. Suggested visualization types may include these ideas, but only Visual Flow, Concept Map, and Comparison are rendered today.

Run the app with `streamlit run app.py` after configuring `OPENAI_API_KEY` in `.streamlit/secrets.toml`.
