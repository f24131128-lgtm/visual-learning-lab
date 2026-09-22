"""Visual Learning Lab — Day 8 comparison visualization prototype."""

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
VISUAL_EVIDENCE_TYPES = [
    "formula",
    "diagram",
    "graph",
    "waveform",
    "table",
    "image",
    "other",
]
PRIMARY_VISUALIZATION_TYPES = ["flow", "concept_map", "comparison", "none"]
CONCEPT_MAP_ROLES = ["central", "primary", "supporting"]

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
        "visual_evidence": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "page": {"type": "integer", "minimum": 1},
                    "type": {"type": "string", "enum": VISUAL_EVIDENCE_TYPES},
                    "description": {"type": "string"},
                    "learning_value": {"type": "string"},
                },
                "required": ["page", "type", "description", "learning_value"],
                "additionalProperties": False,
            },
        },
        "visual_flow": {
            "type": "object",
            "properties": {
                "suitable": {"type": "boolean"},
                "reason": {"type": "string"},
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "source_pages": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 1},
                            },
                        },
                        "required": ["id", "label", "source_pages"],
                        "additionalProperties": False,
                    },
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "label": {"type": "string"},
                        },
                        "required": ["source", "target", "label"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["suitable", "reason", "nodes", "edges"],
            "additionalProperties": False,
        },
        "concept_map": {
            "type": "object",
            "properties": {
                "suitable": {"type": "boolean"},
                "reason": {"type": "string"},
                "nodes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                            "role": {"type": "string", "enum": CONCEPT_MAP_ROLES},
                            "source_pages": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 1},
                            },
                        },
                        "required": ["id", "label", "role", "source_pages"],
                        "additionalProperties": False,
                    },
                },
                "edges": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "source": {"type": "string"},
                            "target": {"type": "string"},
                            "label": {"type": "string"},
                        },
                        "required": ["source", "target", "label"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["suitable", "reason", "nodes", "edges"],
            "additionalProperties": False,
        },
        "comparison": {
            "type": "object",
            "properties": {
                "suitable": {"type": "boolean"},
                "reason": {"type": "string"},
                "title": {"type": "string"},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "label": {"type": "string"},
                        },
                        "required": ["id", "label"],
                        "additionalProperties": False,
                    },
                },
                "criteria": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "criterion": {"type": "string"},
                            "values": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "item_id": {"type": "string"},
                                        "value": {"type": "string"},
                                        "source_pages": {
                                            "type": "array",
                                            "items": {
                                                "type": "integer",
                                                "minimum": 1,
                                            },
                                        },
                                    },
                                    "required": [
                                        "item_id",
                                        "value",
                                        "source_pages",
                                    ],
                                    "additionalProperties": False,
                                },
                            },
                        },
                        "required": ["criterion", "values"],
                        "additionalProperties": False,
                    },
                },
                "takeaway": {"type": "string"},
            },
            "required": [
                "suitable",
                "reason",
                "title",
                "items",
                "criteria",
                "takeaway",
            ],
            "additionalProperties": False,
        },
        "primary_visualization": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": PRIMARY_VISUALIZATION_TYPES},
                "reason": {"type": "string"},
            },
            "required": ["type", "reason"],
            "additionalProperties": False,
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
        "visual_evidence",
        "visual_flow",
        "concept_map",
        "comparison",
        "primary_visualization",
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


def clean_visual_evidence(visual_evidence, allowed_pages):
    """Keep only complete visual evidence items tied to analyzed PDF pages."""
    if not allowed_pages or not isinstance(visual_evidence, list):
        return []

    cleaned = []
    for item in visual_evidence:
        if not isinstance(item, dict):
            continue

        page = item.get("page")
        evidence_type = item.get("type")
        description = item.get("description")
        learning_value = item.get("learning_value")
        if (
            not isinstance(page, int)
            or isinstance(page, bool)
            or page not in allowed_pages
            or evidence_type not in VISUAL_EVIDENCE_TYPES
            or not isinstance(description, str)
            or not description.strip()
            or not isinstance(learning_value, str)
            or not learning_value.strip()
        ):
            continue

        cleaned.append(
            {
                "page": page,
                "type": evidence_type,
                "description": description.strip(),
                "learning_value": learning_value.strip(),
            }
        )
    return cleaned


class PdfVisualInputError(Exception):
    """Raised when the original PDF cannot be attached for visual analysis."""


def build_analysis_input(client, source_text, uploaded_pdf):
    """Build text-only or combined text-plus-PDF input for the Responses API."""
    if uploaded_pdf is None:
        return source_text

    pdf_name = getattr(uploaded_pdf, "name", None) or "uploaded.pdf"
    try:
        uploaded_file = client.files.create(
            file=(pdf_name, uploaded_pdf.getvalue(), "application/pdf"),
            purpose="user_data",
        )
    except Exception as error:
        raise PdfVisualInputError from error

    return [
        {
            "role": "user",
            "content": [
                {"type": "input_text", "text": source_text},
                {"type": "input_file", "file_id": uploaded_file.id},
            ],
        }
    ]


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


def clean_visual_flow(raw_flow, allowed_pages):
    """Validate one connected flow and its PDF page references."""
    if not isinstance(raw_flow, dict):
        return None

    reason = raw_flow.get("reason", "")
    reason = reason.strip() if isinstance(reason, str) else ""
    if raw_flow.get("suitable") is not True:
        return {"suitable": False, "reason": reason, "nodes": [], "edges": []}

    raw_nodes = raw_flow.get("nodes")
    raw_edges = raw_flow.get("edges")
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        return None

    nodes = []
    node_ids = set()
    for node in raw_nodes:
        if not isinstance(node, dict):
            return None
        node_id = node.get("id")
        label = node.get("label")
        if not isinstance(node_id, str) or not isinstance(label, str):
            return None
        node_id, label = node_id.strip(), label.strip()
        if not node_id or not label or node_id in node_ids:
            return None
        node_ids.add(node_id)
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "source_pages": valid_source_pages(
                    node.get("source_pages", []), allowed_pages
                ),
            }
        )

    if len(nodes) < 2 or not raw_edges:
        return None

    edges = []
    neighbors = {node_id: set() for node_id in node_ids}
    for edge in raw_edges:
        if not isinstance(edge, dict):
            return None
        source, target, label = (
            edge.get("source"), edge.get("target"), edge.get("label")
        )
        if not all(isinstance(value, str) for value in (source, target, label)):
            return None
        source, target, label = source.strip(), target.strip(), label.strip()
        if source not in node_ids or target not in node_ids or source == target:
            return None
        edges.append({"source": source, "target": target, "label": label})
        neighbors[source].add(target)
        neighbors[target].add(source)

    seen = set()
    pending = [nodes[0]["id"]]
    while pending:
        node_id = pending.pop()
        if node_id not in seen:
            seen.add(node_id)
            pending.extend(neighbors[node_id] - seen)
    if seen != node_ids:
        return None

    return {"suitable": True, "reason": reason, "nodes": nodes, "edges": edges}


def clean_primary_visualization(raw_decision):
    """Normalize the model's primary visualization decision."""
    if not isinstance(raw_decision, dict):
        return {"type": "none", "reason": ""}

    visualization_type = raw_decision.get("type")
    reason = raw_decision.get("reason", "")
    reason = reason.strip() if isinstance(reason, str) else ""
    if visualization_type not in PRIMARY_VISUALIZATION_TYPES:
        visualization_type = "none"
    return {"type": visualization_type, "reason": reason}


def clean_concept_map(raw_map, allowed_pages):
    """Validate one connected concept map and its PDF page references."""
    if not isinstance(raw_map, dict):
        return None

    reason = raw_map.get("reason", "")
    reason = reason.strip() if isinstance(reason, str) else ""
    if raw_map.get("suitable") is not True:
        return {"suitable": False, "reason": reason, "nodes": [], "edges": []}

    raw_nodes = raw_map.get("nodes")
    raw_edges = raw_map.get("edges")
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        return None

    nodes = []
    node_ids = set()
    central_nodes = 0
    for node in raw_nodes:
        if not isinstance(node, dict):
            return None
        node_id = node.get("id")
        label = node.get("label")
        role = node.get("role")
        if not isinstance(node_id, str) or not isinstance(label, str):
            return None
        node_id, label = node_id.strip(), label.strip()
        if (
            not node_id
            or not label
            or node_id in node_ids
            or role not in CONCEPT_MAP_ROLES
        ):
            return None
        node_ids.add(node_id)
        central_nodes += role == "central"
        nodes.append(
            {
                "id": node_id,
                "label": label,
                "role": role,
                "source_pages": valid_source_pages(
                    node.get("source_pages", []), allowed_pages
                ),
            }
        )

    if len(nodes) < 2 or central_nodes != 1 or not raw_edges:
        return None

    edges = []
    neighbors = {node_id: set() for node_id in node_ids}
    for edge in raw_edges:
        if not isinstance(edge, dict):
            return None
        source, target, label = (
            edge.get("source"), edge.get("target"), edge.get("label")
        )
        if not all(
            isinstance(value, str) and value.strip()
            for value in (source, target, label)
        ):
            return None
        source, target, label = source.strip(), target.strip(), label.strip()
        if source not in node_ids or target not in node_ids or source == target:
            return None
        edges.append({"source": source, "target": target, "label": label})
        neighbors[source].add(target)
        neighbors[target].add(source)

    seen = set()
    pending = [nodes[0]["id"]]
    while pending:
        node_id = pending.pop()
        if node_id not in seen:
            seen.add(node_id)
            pending.extend(neighbors[node_id] - seen)
    if seen != node_ids:
        return None

    return {"suitable": True, "reason": reason, "nodes": nodes, "edges": edges}


def clean_comparison(raw_comparison, allowed_pages):
    """Validate a complete comparison matrix and its PDF page references."""
    if not isinstance(raw_comparison, dict):
        return None

    reason = raw_comparison.get("reason", "")
    reason = reason.strip() if isinstance(reason, str) else ""
    if raw_comparison.get("suitable") is not True:
        return {
            "suitable": False,
            "reason": reason,
            "title": "",
            "items": [],
            "criteria": [],
            "takeaway": "",
        }

    title = raw_comparison.get("title")
    takeaway = raw_comparison.get("takeaway")
    raw_items = raw_comparison.get("items")
    raw_criteria = raw_comparison.get("criteria")
    if (
        not isinstance(title, str)
        or not title.strip()
        or not isinstance(takeaway, str)
        or not takeaway.strip()
        or not isinstance(raw_items, list)
        or not 2 <= len(raw_items) <= 4
        or not isinstance(raw_criteria, list)
        or not 1 <= len(raw_criteria) <= 6
    ):
        return None

    items = []
    item_ids = set()
    item_labels = set()
    for item in raw_items:
        if not isinstance(item, dict):
            return None
        item_id = item.get("id")
        label = item.get("label")
        if not isinstance(item_id, str) or not isinstance(label, str):
            return None
        item_id, label = item_id.strip(), label.strip()
        normalized_label = label.casefold()
        if (
            not item_id
            or not label
            or item_id in item_ids
            or normalized_label in item_labels
        ):
            return None
        item_ids.add(item_id)
        item_labels.add(normalized_label)
        items.append({"id": item_id, "label": label})

    criteria = []
    criterion_names = set()
    for criterion_item in raw_criteria:
        if not isinstance(criterion_item, dict):
            return None
        criterion = criterion_item.get("criterion")
        raw_values = criterion_item.get("values")
        if (
            not isinstance(criterion, str)
            or not criterion.strip()
            or not isinstance(raw_values, list)
            or len(raw_values) != len(items)
        ):
            return None
        criterion = criterion.strip()
        normalized_criterion = criterion.casefold()
        if normalized_criterion in criterion_names:
            return None
        criterion_names.add(normalized_criterion)

        values_by_id = {}
        for raw_value in raw_values:
            if not isinstance(raw_value, dict):
                return None
            item_id = raw_value.get("item_id")
            value = raw_value.get("value")
            if (
                not isinstance(item_id, str)
                or item_id not in item_ids
                or item_id in values_by_id
                or not isinstance(value, str)
                or not value.strip()
            ):
                return None
            values_by_id[item_id] = {
                "item_id": item_id,
                "value": value.strip(),
                "source_pages": valid_source_pages(
                    raw_value.get("source_pages", []), allowed_pages
                ),
            }

        if set(values_by_id) != item_ids:
            return None
        criteria.append(
            {
                "criterion": criterion,
                "values": [values_by_id[item["id"]] for item in items],
            }
        )

    return {
        "suitable": True,
        "reason": reason,
        "title": title.strip(),
        "items": items,
        "criteria": criteria,
        "takeaway": takeaway.strip(),
    }


def build_comparison_table(comparison):
    """Build rows for a static Streamlit comparison table."""
    if not comparison or not comparison["suitable"]:
        return []

    item_labels = {item["id"]: item["label"] for item in comparison["items"]}
    rows = []
    for criterion in comparison["criteria"]:
        row = {"Criterion": criterion["criterion"]}
        for value in criterion["values"]:
            cell = value["value"]
            if value["source_pages"]:
                cell += f"\n\nSource: {format_page_references(value['source_pages'])}"
            row[item_labels[value["item_id"]]] = cell
        rows.append(row)
    return rows


def _wrap_graph_label(value, width):
    return "\n".join(textwrap.wrap(value, width=width))


def build_flow_graph(visual_flow):
    """Build a directed top-to-bottom graph from the validated visual flow."""
    if not visual_flow or not visual_flow["suitable"]:
        return None

    graph = Digraph("visual_flow")
    graph.attr(
        "graph",
        rankdir="TB",
        bgcolor="transparent",
        pad="0.12",
        nodesep="0.32",
        ranksep="0.45",
        margin="0.02",
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

    for node in visual_flow["nodes"]:
        graph.node(
            node["id"],
            label=_wrap_graph_label(node["label"], 28),
            tooltip=format_page_references(node["source_pages"]),
        )

    for edge in visual_flow["edges"]:
        graph.edge(
            edge["source"],
            edge["target"],
            label=_wrap_graph_label(edge["label"], 18),
        )

    return graph


def build_concept_map_graph(concept_map):
    """Build a compact concept network with role-based visual emphasis."""
    if not concept_map or not concept_map["suitable"]:
        return None

    graph = Digraph("concept_map")
    graph.attr(
        "graph",
        rankdir="LR",
        bgcolor="transparent",
        pad="0.12",
        nodesep="0.3",
        ranksep="0.55",
        margin="0.02",
        splines="spline",
    )
    graph.attr(
        "node",
        fontname="Arial",
        fontsize="11",
        margin="0.18,0.12",
    )
    graph.attr(
        "edge",
        color="#8270DF",
        fontname="Arial",
        fontsize="10",
        fontcolor="#4F467A",
        dir="none",
    )

    node_styles = {
        "central": {
            "shape": "ellipse",
            "style": "filled",
            "color": "#5540AE",
            "fillcolor": "#6750C5",
            "fontcolor": "white",
            "penwidth": "2",
        },
        "primary": {
            "shape": "box",
            "style": "rounded,filled",
            "color": "#8270DF",
            "fillcolor": "#EEE9FF",
            "fontcolor": "#2F2850",
            "penwidth": "1.5",
        },
        "supporting": {
            "shape": "box",
            "style": "rounded,filled",
            "color": "#B7ACEE",
            "fillcolor": "#FBFAFF",
            "fontcolor": "#3F385D",
        },
    }

    for node in concept_map["nodes"]:
        graph.node(
            node["id"],
            label=_wrap_graph_label(node["label"], 26),
            tooltip=format_page_references(node["source_pages"]),
            **node_styles[node["role"]],
        )

    for edge in concept_map["edges"]:
        graph.edge(
            edge["source"],
            edge["target"],
            label=_wrap_graph_label(edge["label"], 18),
        )

    return graph

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
    <span class="pill">2026 iThome Ironman · Day 8 comparison visualization</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader("Start with what you’re learning")
    st.caption("Bring a page, a chapter, or an idea you want to understand.")
    uploaded_pdf = st.file_uploader(
        "Upload a PDF",
        type=["pdf"],
        help="PDFs are analyzed through both extracted text and visual pages.",
    )
    content = st.text_area(
        "Or paste your content",
        height=200,
        placeholder="Paste your notes, a tricky explanation, or a concept you want to explore…",
    )
    st.caption("Use one source at a time · PDF text and visual page content are analyzed together.")
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
                            "or image-based. Visual analysis still requires a readable PDF file."
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

Analyze the user's learning content faithfully and make it easier to study.
Return only data that matches the supplied JSON Schema.

- quick_summary: a concise explanation of the main idea.
- key_concepts: objects with concept, explanation, and source_pages. source_pages
  must contain only page numbers explicitly shown in [Page X] markers. Use [] for
  pasted text or when no supporting page is clear.
- relationships: explicit relationships between concepts. Each item must contain
  source, relation, target, and source_pages. source_pages must contain only page
  numbers explicitly shown in [Page X] markers. Use [] for pasted text or when no
  supporting page is clear. Use an empty array when no usable relationship is
  supported by the content. Do not invent relationships. Include all supported
  semantic relationships, including definitions and properties; this list is
  displayed as text and does not define the Visual Flow.
- visual_evidence: objects with page, type, description, and learning_value.
  For PDFs, inspect the original PDF visually as well as the extracted [Page X]
  text. Look for meaningful formulas, diagrams, graphs, waveforms, tables, labels,
  and other visual learning content. page must be a page number explicitly shown
  in a [Page X] marker; never invent a page number. Use only the allowed type
  values. Do not invent visual evidence. Return [] when no meaningful visual
  content is visible. For pasted text, return [].
- primary_visualization: choose the single visualization that would most help a
  learner understand the core structure of the actual material. Do not decide from
  keywords or from the number of concepts or relationships. First detect whether
  the material contains an explicit, coherent, pedagogically important process
  with roughly three or more meaningful stages: for example, a problem, input,
  state, or cause progressing through transformations or intermediate effects to
  a result, output, new state, or outcome. If that process is central to what the
  learner needs to understand, choose flow even when the material also contains
  definitions, notation, formulas, or supporting conceptual relationships. Choose
  concept_map when no strong ordered process dominates and understanding mainly
  depends on relationships among concepts, properties, categories, components, or
  formulas where ordering is not essential. Choose comparison when useful
  side-by-side similarities, differences, alternatives, tradeoffs, or parallel
  properties are the dominant learning structure. Do not choose comparison merely
  because two concepts appear. Choose none only when none of these views would
  meaningfully improve understanding. Briefly explain why.
- visual_flow: use this only for the main coherent process. If
  primary_visualization.type is flow, suitable should normally be true. Show one
  connected, directed flow with concise stages that follow the source. Do not add
  unrelated supporting concepts to fill it. Give each stage one canonical id;
  every edge must reference exact node ids and have a short readable label. Node
  source_pages must use only [Page X] markers, or [] for pasted text or unclear
  support. Never invent page numbers or process steps. If visual_flow contains a
  coherent connected process of three or more meaningful nodes and that process is
  central to the material, primary_visualization should normally be flow. Do not
  force flow when the sequence is artificial or merely a possible study order.
  When flow is not selected, set suitable to false and return empty nodes and edges.
- concept_map: use this for the main conceptual structure. If
  primary_visualization.type is concept_map, suitable should normally be true.
  Prefer one central topic and roughly 5–10 useful nodes, without including every
  possible fact. Use canonical, unique node ids and avoid duplicate concepts with
  slightly different names. Give exactly one node the central role; use primary
  and supporting roles for the others. Every edge must reference exact node ids
  and describe a meaningful conceptual link. Keep the map connected. Node
  source_pages must use only [Page X] markers, or [] for pasted text or unclear
  support. Never invent page numbers or concepts. When Concept Map is not
  selected, set suitable to false and return empty nodes and edges.
- comparison: use this only when primary_visualization.type is comparison. Compare
  2–4 distinct items using preferably 3–6 meaningful, specific criteria. Avoid
  vague criteria. Every criterion must contain exactly one value for every item,
  and every item_id must exactly match a canonical id from items. Keep cell values
  concise and include only supported distinctions. Value source_pages must use
  only [Page X] markers, or [] for pasted text or unclear support. Never invent
  page numbers. The takeaway should state the most useful learning distinction,
  not declare a winner. When Comparison is not selected, set suitable to false
  and return an empty title, items, criteria, and takeaway.
- suggested_visualizations: choose zero or more types from the exact allowed list.

Use the same language as the user's content. If the source is primarily Traditional
Chinese, respond in Traditional Chinese. If it is English, English output is fine.
Do not unexpectedly switch to Simplified Chinese. The [Page X] markers are the
only valid source of PDF page numbers. Do not create rendered diagrams or 3D
models in the response.
"""

            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)
                try:
                    analysis_input = build_analysis_input(
                        client, source_text, uploaded_pdf if has_pdf else None
                    )
                except PdfVisualInputError:
                    st.error(
                        "We couldn’t send this PDF for visual analysis. Please try "
                        "again with a valid PDF file."
                    )
                    analysis_input = None

                if analysis_input is not None:
                    with st.spinner("Analyzing your content…"):
                        response = client.responses.create(
                            model=MODEL,
                            instructions=prompt,
                            input=analysis_input,
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

        st.markdown("#### Visual Evidence")
        visual_evidence = clean_visual_evidence(
            analysis.get("visual_evidence", []), allowed_source_pages
        )
        if visual_evidence:
            for item in visual_evidence:
                st.markdown(
                    f"**{item['type'].capitalize()}** — Page {item['page']}"
                )
                st.write(item["description"])
                st.markdown("Learning value:")
                st.write(item["learning_value"])
        else:
            st.caption("No meaningful visual evidence was found in this content.")

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

    primary_visualization = clean_primary_visualization(
        analysis.get("primary_visualization")
    )
    visual_flow = clean_visual_flow(
        analysis.get("visual_flow"), allowed_source_pages
    )
    concept_map = clean_concept_map(
        analysis.get("concept_map"), allowed_source_pages
    )
    comparison = clean_comparison(
        analysis.get("comparison"), allowed_source_pages
    )
    selection_reason = primary_visualization["reason"]

    if primary_visualization["type"] == "flow":
        st.markdown("### Visual Flow")
        flow_graph = build_flow_graph(visual_flow)
        if flow_graph:
            st.graphviz_chart(flow_graph.source, use_container_width=True)
        else:
            st.info(
                "The selected Visual Flow could not be rendered because its "
                "structured data was incomplete."
            )
        if selection_reason:
            st.caption(selection_reason)
    elif primary_visualization["type"] == "concept_map":
        st.markdown("### Concept Map")
        concept_graph = build_concept_map_graph(concept_map)
        if concept_graph:
            st.graphviz_chart(concept_graph.source, use_container_width=True)
        else:
            st.info(
                "The selected Concept Map could not be rendered because its "
                "structured data was incomplete."
            )
        if selection_reason:
            st.caption(selection_reason)
    elif primary_visualization["type"] == "comparison":
        st.markdown("### Comparison")
        comparison_rows = build_comparison_table(comparison)
        if comparison_rows:
            st.markdown(f"#### {comparison['title']}")
            st.table(comparison_rows)
            st.markdown("**Takeaway**")
            st.write(comparison["takeaway"])
        else:
            st.info(
                "The selected Comparison could not be rendered because its "
                "structured data was incomplete."
            )
        if selection_reason:
            st.caption(selection_reason)
    else:
        st.markdown("### Primary Visualization")
        st.info(
            "No strong primary visualization was detected for this material."
        )
        if selection_reason:
            st.caption(selection_reason)

st.markdown("### One idea. More ways to understand it.")
st.caption("Planned capabilities · coming in future versions")

capabilities = [
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
