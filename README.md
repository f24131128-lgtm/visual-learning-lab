# Visual Learning Lab

A 2026 iThome Ironman project built with ChatGPT × Codex × Vibe Coding. It turns learning content into structured explanations and visual learning aids.

**Status:** Day 10 / 30 — v0.1, the first public deployment milestone.

## What works

- Paste text or upload a text-based PDF. `pypdf` counts pages, extracts text from up to eight extractable pages, and keeps page labels for source tracing. Source page references are checked against those analyzed pages.
- For PDF input, the original file is also sent to the OpenAI Responses API alongside the extracted text. The model can inspect formulas, diagrams, graphs, waveforms, tables, and other visual content. Image-only PDFs without extractable text are not supported yet; there is no OCR.
- Strict Structured Outputs provide a Quick Summary, Key Concepts, Relationships, Suggested Visualization, Visual Evidence, dedicated Flow, Concept Map, and Comparison data, and a primary visualization decision.
- Relationships remain complete semantic text output. The app automatically chooses a Graphviz Visual Flow for an ordered process, a Graphviz Concept Map for conceptual structure, or a side-by-side Comparison table for meaningful parallel distinctions. Each visualization has its own validated representation.
- Every Key Concept and Visual Evidence item has **Explain this**. It provides a focused, source-aware clarification in place, using the active analysis and relevant extracted text so the learner does not have to paste the material again.

## Planned

Timeline, Analogies, Image Breakdown, 3D / Motion, richer Source Check, arbitrary text highlighting, and explanations from visualization nodes. Suggested visualization types may include some of these ideas, but only Visual Flow, Concept Map, and Comparison are rendered today.

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

In Community Cloud, add `OPENAI_API_KEY = "your-key-here"` to the app's **Advanced settings → Secrets** instead of uploading or committing the local secrets file. See [Streamlit's secrets management guide](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management).
