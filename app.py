"""Visual Learning Lab — Day 5 PDF analysis prototype."""

import json
import textwrap

from graphviz import Digraph
from openai import OpenAI
from pypdf import PdfReader
import streamlit as st

MODEL = "gpt-5.6-luna"
MAX_ANALYZED_PDF_PAGES = 8
VISUALIZATION_TYPES = [
    "Concept Map",
    "Flow",
    "Timeline",
    "Comparison",
    "Analogy",
    "Image / Diagram",
    "3D / Motion",
]

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "quick_summary": {"type": "string"},
        "key_concepts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "concept": {"type": "string"},
                    "explanation": {"type": "string"},
                    "source_pages": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                },
                "required": ["concept", "explanation", "source_pages"],
                "additionalProperties": False,
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "relation": {"type": "string"},
                    "target": {"type": "string"},
                    "source_pages": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                },
                "required": [
                    "source",
                    "relation",
                    "target",
                    "source_pages",
                ],
                "additionalProperties": False,
            },
        },
        "suggested_visualizations": {
            "type": "array",
            "items": {"type": "string", "enum": VISUALIZATION_TYPES},
        },
    },
    "required": [
        "quick_summary",
        "key_concepts",
        "relationships",
        "suggested_visualizations",
    ],
    "additionalProperties": False,
}


def extract_pdf_text(uploaded_pdf):
    """Extract up to eight text-bearing PDF pages with explicit page markers."""
    uploaded_pdf.seek(0)
    reader = PdfReader(uploaded_pdf)
    text_pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = (page.extract_text() or "").strip()
        if page_text:
            text_pages.append((page_number, page_text))

    analyzed_pages = text_pages[:MAX_ANALYZED_PDF_PAGES]
    labeled_text = "\n\n".join(
        f"[Page {page_number}]\n{page_text}"
        for page_number, page_text in analyzed_pages
    )
    return {
        "text": labeled_text,
        "total_pages": len(reader.pages),
        "extractable_page_numbers": [page_number for page_number, _ in text_pages],
        "analyzed_page_numbers": [page_number for page_number, _ in analyzed_pages],
    }


def valid_source_pages(raw_pages, allowed_pages):
    """Keep only integer page numbers explicitly present in the input markers."""
    if not allowed_pages or not isinstance(raw_pages, list):
        return []
    return sorted(
        {
            page
            for page in raw_pages
            if isinstance(page, int)
            and not isinstance(page, bool)
            and page in allowed_pages
        }
    )


def format_page_references(page_numbers):
    """Format page numbers as compact references such as p. 2–3, 5."""
    if not page_numbers:
        return ""

    page_numbers = sorted(set(page_numbers))
    ranges = []
    start = previous = page_numbers[0]
    for page in page_numbers[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append((start, previous))
        start = previous = page
    ranges.append((start, previous))

    parts = [
        str(start) if start == end else f"{start}–{end}"
        for start, end in ranges
    ]
    return "p. " + ", ".join(parts)


def clean_relationships(relationships, allowed_pages):
    """Normalize relationships and discard invalid or unverified page references."""
    if not isinstance(relationships, list):
        return []

    cleaned = []
    for relationship in relationships:
        if not isinstance(relationship, dict):
            continue
        source = relationship.get("source")
        relation = relationship.get("relation")
        target = relationship.get("target")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (source, relation, target)
        ):
            continue
        cleaned.append(
            {
                "source": source.strip(),
                "relation": relation.strip(),
                "target": target.strip(),
                "source_pages": valid_source_pages(
                    relationship.get("source_pages", []), allowed_pages
                ),
            }
        )
    return cleaned


def _wrap_graph_label(value, width):
    return "\n".join(textwrap.wrap(value, width=width))


def build_flow_graph(relationships):
    """Build a directed top-to-bottom graph from model-produced relationships."""
    graph = Digraph("visual_flow")
    graph.attr(
        "graph",
        rankdir="TB",
        bgcolor="transparent",
        pad="0.25",
        nodesep="0.55",
        ranksep="0.75",
    )
    graph.attr(
        "node",
        shape="box",
        style="rounded,filled",
        color="#6750C5",
        fillcolor="#F7F4FF",
        fontname="Arial",
        fontsize="11",
        margin="0.18,0.12",
    )
    graph.attr(
        "edge",
        color="#8270DF",
        fontname="Arial",
        fontsize="10",
        arrowsize="0.7",
    )

    node_ids = {}
    valid_relationships = 0

    for relationship in relationships or []:
        if not isinstance(relationship, dict):
            continue

        source = relationship.get("source")
        relation = relationship.get("relation")
        target = relationship.get("target")
        if not all(
            isinstance(value, str) and value.strip()
            for value in (source, relation, target)
        ):
            continue
        source = source.strip()
        relation = relation.strip()
        target = target.strip()

        for concept in (source, target):
            if concept not in node_ids:
                node_id = f"concept_{len(node_ids)}"
                node_ids[concept] = node_id
                graph.node(node_id, label=_wrap_graph_label(concept, 28))

        graph.edge(
            node_ids[source],
            node_ids[target],
            label=_wrap_graph_label(relation, 18),
        )
        valid_relationships += 1

    return graph if valid_relationships else None

st.set_page_config(page_title="Visual Learning Lab", page_icon="✦", layout="centered")

# Static presentation styles only; content inputs are never inserted into HTML.
st.markdown("""
<style>
.block-container { max-width: 980px; padding-top: 3rem; padding-bottom: 3rem; }
.hero { padding: 2rem 0 1.5rem; }
.eyebrow { color: #8270df; font-size: .76rem; font-weight: 700;
           letter-spacing: .15em; text-transform: uppercase; }
.hero h1 { font-size: clamp(2.3rem, 6vw, 3.7rem); line-height: 1.12;
           letter-spacing: -.055em; padding: .7rem 0; }
.subtitle { font-size: 1.15rem; opacity: .75; line-height: 1.65; }
.pill { display: inline-block; border: 1px solid #8270df66; border-radius: 99px;
        padding: .3rem .7rem; font-size: .75rem; margin-top: .8rem; }
[data-testid="stFileUploaderDropzone"] { border: 1px dashed #8270df88;
                                         border-radius: 12px; }
div.stButton > button[kind="primary"] { background: #6750c5; color: white;
    border: 1px solid #6750c5; border-radius: 10px; min-height: 3rem;
    font-weight: 650; }
div.stButton > button[kind="primary"]:hover { background: #5540ae;
                                            border-color: #5540ae; }
.capabilities { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 12px; margin: .8rem 0 1.2rem; }
.capability { border: 1px solid #8270df33; border-radius: 14px;
              padding: 1.1rem; background: #8270df08; }
.capability h3 { font-size: 1rem; padding: .5rem 0; }
.capability p { font-size: .86rem; line-height: 1.55; opacity: .75; margin: 0; }
.symbol { color: #8270df; font-size: 1.35rem; }
.source { border-color: #8270df88; background: #8270df12; }
.source-note { border-left: 3px solid #8270df; padding: .5rem 1rem;
               font-size: .9rem; line-height: 1.6; margin: 1rem 0; }
@media (max-width: 640px) {
    .capabilities { grid-template-columns: 1fr; }
    .block-container { padding-top: 1.5rem; }
}
</style>
<div class="hero">
    <div class="eyebrow">See the idea. Find the connection.</div>
    <h1>Visual Learning Lab</h1>
    <div class="subtitle">Turn complex ideas into something you can actually see.</div>
    <span class="pill">2026 iThome Ironman · Day 5 PDF prototype</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Start with what you’re learning")
    st.caption("Bring a page, a chapter, or an idea you want to understand.")
    uploaded_pdf = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="Day 5 preview: text-based PDFs can now be analyzed.",
    )
    content = st.text_area(
        "Or paste your content",
        height=200,
        placeholder="Paste your notes, a tricky explanation, or a concept you want to explore…",
    )
    st.caption("Use one source at a time · scanned/image PDFs need OCR support planned for later.")
    if st.button("Visualize", type="primary", use_container_width=True):
        st.session_state.pop("analysis", None)
        st.session_state.pop("source_info", None)
        st.session_state.pop("allowed_source_pages", None)

        has_pdf = uploaded_pdf is not None
        has_pasted_text = bool(content.strip())

        if not has_pdf and not has_pasted_text:
            st.warning("Please upload a PDF or paste some learning content first.")
        elif has_pdf and has_pasted_text:
            st.warning("Please use only one source at a time: upload a PDF or paste text.")
        else:
            source_text = content.strip()
            allowed_source_pages = []
            source_info = None

            if has_pdf:
                try:
                    pdf_data = extract_pdf_text(uploaded_pdf)
                except Exception:
                    st.error(
                        "We couldn’t read this PDF. Please check that it is a valid PDF "
                        "and try again."
                    )
                    pdf_data = None

                if pdf_data is not None:
                    found_pages = pdf_data["extractable_page_numbers"]
                    analyzed_pages = pdf_data["analyzed_page_numbers"]
                    if not found_pages:
                        st.warning(
                            "No extractable text was found in this PDF. It may be scanned "
                            "or image-based. OCR / image PDF support is planned for a later version."
                        )
                    else:
                        source_text = pdf_data["text"]
                        allowed_source_pages = analyzed_pages
                        source_info = {
                            "found_count": len(found_pages),
                            "total_count": pdf_data["total_pages"],
                            "analyzed_count": len(analyzed_pages),
                        }
                        st.info(
                            f"Found extractable text on {len(found_pages)} of "
                            f"{pdf_data['total_pages']} PDF page(s); analyzing the first "
                            f"{len(analyzed_pages)} extractable page(s)."
                        )

            if has_pdf and not source_info:
                source_text = ""

            if not source_text:
                st.stop()

            st.session_state["source_info"] = source_info
            st.session_state["allowed_source_pages"] = allowed_source_pages
            prompt = """You are the learning-content analyst for Visual Learning Lab.

Analyze the user's pasted learning content faithfully and make it easier to study.
Return only data that matches the supplied JSON Schema.

- quick_summary: a concise explanation of the main idea.
- key_concepts: objects with concept, explanation, and source_pages. source_pages
  must contain only page numbers explicitly shown in [Page X] markers. Use [] for
  pasted text or when no supporting page is clear.
- relationships: explicit relationships between concepts. Each item must contain
  source, relation, target, and source_pages. source_pages must contain only page
  numbers explicitly shown in [Page X] markers. Use [] for pasted text or when no
  supporting page is clear. Use an empty array when no usable relationship is
  supported by the content. Do not invent relationships.
- suggested_visualizations: choose zero or more types from the exact allowed list.

Use the same language as the user's content. Keep relationships clear enough to
draw as labeled arrows in a top-to-bottom flow diagram. The [Page X] markers are
the only valid source of PDF page numbers; never invent a page number. Do not
create diagrams or 3D models in the response.
"""

            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)
                with st.spinner("Analyzing your content…"):
                    response = client.responses.create(
                        model=MODEL,
                        instructions=prompt,
                        input=source_text,
                        text={
                            "format": {
                                "type": "json_schema",
                                "name": "visual_learning_analysis",
                                "strict": True,
                                "schema": ANALYSIS_SCHEMA,
                            }
                        },
                    )
                analysis = json.loads(response.output_text)
                if not isinstance(analysis, dict):
                    raise ValueError("The model returned an invalid analysis object.")
                st.session_state["analysis"] = analysis
            except (KeyError, st.errors.StreamlitSecretNotFoundError):
                st.error(
                    "OpenAI API key is not configured yet. Add OPENAI_API_KEY to "
                    ".streamlit/secrets.toml and try again."
                )
            except json.JSONDecodeError:
                st.error(
                    "The analysis came back in an unexpected format. Please try again."
                )
            except Exception:
                st.error(
                    "We couldn’t analyze that content right now. Check your API key "
                    "and internet connection, then try again."
                )

analysis = st.session_state.get("analysis")
if analysis:
    allowed_source_pages = st.session_state.get("allowed_source_pages", [])
    source_info = st.session_state.get("source_info")
    relationships = clean_relationships(
        analysis.get("relationships", []), allowed_source_pages
    )

    with st.container(border=True):
        st.markdown("### Your learning snapshot")
        if source_info:
            st.caption(
                f"PDF source: text found on {source_info['found_count']} of "
                f"{source_info['total_count']} page(s); analyzed "
                f"{source_info['analyzed_count']} page(s)."
            )

        st.markdown("#### Quick Summary")
        st.write(analysis.get("quick_summary", ""))

        st.markdown("#### Key Concepts")
        key_concepts = analysis.get("key_concepts", [])
        if not isinstance(key_concepts, list):
            key_concepts = []
        concept_lines = []
        for item in key_concepts:
            if isinstance(item, dict):
                concept = item.get("concept", "")
                explanation = item.get("explanation", "")
                pages = valid_source_pages(
                    item.get("source_pages", []), allowed_source_pages
                )
            elif isinstance(item, str):
                concept = item
                explanation = ""
                pages = []
            else:
                continue

            if not isinstance(concept, str) or not concept.strip():
                continue
            concept = concept.strip()
            explanation = explanation.strip() if isinstance(explanation, str) else ""
            description = f" — {explanation}" if explanation else ""
            concept_lines.append(f"- **{concept}**{description}")
            if pages:
                concept_lines.append(f"  - Source: {format_page_references(pages)}")

        if concept_lines:
            st.markdown("\n".join(concept_lines))
        else:
            st.caption("No key concepts were returned for this content.")

        st.markdown("#### Relationships")
        if relationships:
            relationship_lines = []
            for item in relationships:
                relationship_lines.append(
                    f"- **{item['source']}** — *{item['relation']}* → **{item['target']}**"
                )
                if item["source_pages"]:
                    relationship_lines.append(
                        f"  - Source: {format_page_references(item['source_pages'])}"
                    )
            st.markdown(
                "\n".join(relationship_lines)
            )
        else:
            st.caption("No explicit relationships were found in this content.")

        st.markdown("#### Suggested Visualization")
        suggested_visualizations = analysis.get("suggested_visualizations", [])
        if not isinstance(suggested_visualizations, list):
            suggested_visualizations = []
        if suggested_visualizations:
            st.markdown(", ".join(suggested_visualizations))
        else:
            st.caption("No visualization type was suggested for this content.")

    st.markdown("### Visual Flow")
    flow_graph = build_flow_graph(relationships)
    if flow_graph:
        st.graphviz_chart(flow_graph.source, use_container_width=True)
    else:
        st.info("A flow visualization could not be generated from this content.")

st.markdown("### One idea. More ways to understand it.")
st.caption("Planned capabilities · coming in future versions")

capabilities = [
    ("◎", "Concept Map", "Connect key ideas and see how they relate."),
    ("→", "Flow", "Follow a process, one clear step at a time."),
    ("≈", "Analogies", "Make unfamiliar ideas click with familiar examples."),
    ("▧", "Image Breakdown", "Explore the parts of a diagram and what they mean."),
    ("◇", "3D / Motion", "Explore spatial ideas and how systems change."),
    ("↗", "Source Check", "Trace explanations back to the original PDF or source material."),
]

cards = "".join(
    f'<article class="capability {"source" if title == "Source Check" else ""}">'
    f'<span class="symbol" aria-hidden="true">{symbol}</span>'
    f'<h3>{title}</h3><p>{description}</p></article>'
    for symbol, title, description in capabilities
)
st.markdown(f'<div class="capabilities">{cards}</div>', unsafe_allow_html=True)
st.markdown("""
<div class="source-note"><strong>Understanding should come with evidence.</strong><br>
Planned Source Check will link generated explanations to their supporting source passages,
so you can inspect the original context and spot oversimplifications.</div>
""", unsafe_allow_html=True)
st.divider()
st.caption("Visual Learning Lab · Built in public, one day at a time.")
