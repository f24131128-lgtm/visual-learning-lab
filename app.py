"""Visual Learning Lab — Day 19 source-to-scene semantic atlas."""

import hashlib
import json
import textwrap

from graphviz import Digraph
from openai import OpenAI
from pypdf import PdfReader
import streamlit as st

from i18n import RESPONSE_LANGUAGES, current_language, output_language_instruction, tr
from interactive_lab import (
    INTERACTIVE_LAB_SCHEMA, LAB_INSTRUCTIONS, clean_interactive_lab,
    ensure_lab_state, render_interactive_lab, render_lab_links, reset_lab_state,
)
from presentation import render_header, render_footer
from dynamic_simulation import ensure_simulation_state, render_simulation_studio, reset_simulation_state
from scene.compiler import render_scene_builder, reset_scene_state, scene_candidate
from scene.schema import LEARNING_SCENE_CANDIDATE_SCHEMA

from learning_canvas import (
    VISUAL_REF_SCHEMA,
    clean_visual_refs,
    ensure_canvas_state,
    go_to_lesson,
    render_learning_canvas,
    reset_canvas_state,
)

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
MAX_EXPLANATION_SOURCE_CHARS = 6000

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
        "learning_path": {
            "type": "object",
            "properties": {
                "suitable": {"type": "boolean"},
                "title": {"type": "string"},
                "reason": {"type": "string"},
                "steps": {
                    "type": "array",
                    "maxItems": 6,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "learning_goal": {"type": "string"},
                            "explanation": {"type": "string"},
                            "source_pages": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 1},
                            },
                            "connection_to_previous": {"type": "string"},
                            "visual_refs": VISUAL_REF_SCHEMA,
                        },
                        "required": [
                            "id",
                            "title",
                            "learning_goal",
                            "explanation",
                            "source_pages",
                            "connection_to_previous",
                            "visual_refs",
                        ],
                        "additionalProperties": False,
                    },
                },
                "checkpoint_questions": {
                    "type": "array",
                    "maxItems": 3,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "question": {"type": "string"},
                            "options": {
                                "type": "array",
                                "minItems": 4,
                                "maxItems": 4,
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "text": {"type": "string"},
                                    },
                                    "required": ["id", "text"],
                                    "additionalProperties": False,
                                },
                            },
                            "correct_option_id": {"type": "string"},
                            "explanation": {"type": "string"},
                            "source_pages": {
                                "type": "array",
                                "items": {"type": "integer", "minimum": 1},
                            },
                            "related_step_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                            },
                        },
                        "required": [
                            "id",
                            "question",
                            "options",
                            "correct_option_id",
                            "explanation",
                            "source_pages",
                            "related_step_ids",
                        ],
                        "additionalProperties": False,
                    },
                },
            },
            "required": [
                "suitable",
                "title",
                "reason",
                "steps",
                "checkpoint_questions",
            ],
            "additionalProperties": False,
        },
        "interactive_lab": INTERACTIVE_LAB_SCHEMA,
        "learning_scene_candidate": LEARNING_SCENE_CANDIDATE_SCHEMA,
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
        "learning_path",
        "interactive_lab",
        "learning_scene_candidate",
        "primary_visualization",
        "suggested_visualizations",
    ],
    "additionalProperties": False,
}

EXPLANATION_SCHEMA = {
    "type": "object",
    "properties": {
        "plain_explanation": {"type": "string"},
        "why_it_matters": {"type": "string"},
        "intuition_or_example": {"type": "string"},
        "source_note": {"type": "string"},
    },
    "required": [
        "plain_explanation",
        "why_it_matters",
        "intuition_or_example",
        "source_note",
    ],
    "additionalProperties": False,
}

FOCUSED_REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "review_title": {"type": "string"},
        "review_summary": {"type": "string"},
        "source_note": {"type": "string"},
        "items": {
            "type": "array",
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "related_step_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "what_to_fix": {"type": "string"},
                    "focused_explanation": {"type": "string"},
                    "intuition_or_example": {"type": "string"},
                    "source_pages": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                },
                "required": [
                    "id",
                    "related_step_ids",
                    "what_to_fix",
                    "focused_explanation",
                    "intuition_or_example",
                    "source_pages",
                ],
                "additionalProperties": False,
            },
        },
        "retry_questions": {
            "type": "array",
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "question": {"type": "string"},
                    "options": {
                        "type": "array",
                        "minItems": 4,
                        "maxItems": 4,
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "text": {"type": "string"},
                            },
                            "required": ["id", "text"],
                            "additionalProperties": False,
                        },
                    },
                    "correct_option_id": {"type": "string"},
                    "explanation": {"type": "string"},
                    "related_step_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "source_pages": {
                        "type": "array",
                        "items": {"type": "integer", "minimum": 1},
                    },
                },
                "required": [
                    "id",
                    "question",
                    "options",
                    "correct_option_id",
                    "explanation",
                    "related_step_ids",
                    "source_pages",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "review_title",
        "review_summary",
        "source_note",
        "items",
        "retry_questions",
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
        "analyzed_page_texts": {
            page_number: page_text for page_number, page_text in analyzed_pages
        },
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


def build_analysis_id(source_kind, source_bytes, analysis_language="zh-TW"):
    """Create a stable identity for explanation caching within one source."""
    digest = hashlib.sha256()
    digest.update(source_kind.encode("utf-8"))
    digest.update(b"\0")
    digest.update(source_bytes)
    digest.update(b"\0")
    digest.update(analysis_language.encode("utf-8"))
    return digest.hexdigest()


def clean_explanation(raw_explanation):
    """Validate and normalize one contextual explanation response."""
    if not isinstance(raw_explanation, dict):
        return None

    cleaned = {}
    for field in EXPLANATION_SCHEMA["required"]:
        value = raw_explanation.get(field)
        if not isinstance(value, str):
            return None
        cleaned[field] = value.strip()

    if not all(
        cleaned[field]
        for field in ("plain_explanation", "why_it_matters", "source_note")
    ):
        return None
    return cleaned


def get_explanation_language(analysis):
    """Use stored language; retain the legacy heuristic only for old sessions."""
    stored_language = analysis.get("analysis_language")
    if stored_language in RESPONSE_LANGUAGES:
        return RESPONSE_LANGUAGES[stored_language]
    language_fragments = []
    quick_summary = analysis.get("quick_summary")
    if isinstance(quick_summary, str):
        language_fragments.append(quick_summary)

    field_groups = (
        ("key_concepts", ("concept", "explanation")),
        ("relationships", ("source", "relation", "target")),
        ("visual_evidence", ("description", "learning_value")),
    )
    for group_name, fields in field_groups:
        items = analysis.get(group_name, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            language_fragments.extend(
                item[field]
                for field in fields
                if isinstance(item.get(field), str)
            )

    combined_text = " ".join(language_fragments)
    chinese_count = sum(
        "\u3400" <= character <= "\u4dbf"
        or "\u4e00" <= character <= "\u9fff"
        or "\uf900" <= character <= "\ufaff"
        for character in combined_text
    )
    english_count = sum(
        character.isascii() and character.isalpha()
        for character in combined_text
    )
    if chinese_count >= 4 and chinese_count * 2 >= english_count:
        return "Traditional Chinese"
    return "English"


def build_visualization_explanation_target(
    target_type, target, visualization, allowed_pages
):
    """Build validated target and local context for one visualization element."""
    if not isinstance(target, dict) or not isinstance(visualization, dict):
        return None

    target_id = target.get("id")
    label = target.get("label")
    if not all(
        isinstance(value, str) and value.strip()
        for value in (target_id, label)
    ):
        return None
    target_id, label = target_id.strip(), label.strip()

    if target_type in {"concept_map_node", "visual_flow_node"}:
        nodes = visualization.get("nodes", [])
        edges = visualization.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            return None
        nodes_by_id = {
            node["id"]: node
            for node in nodes
            if isinstance(node, dict)
            and isinstance(node.get("id"), str)
            and isinstance(node.get("label"), str)
        }
        if target_id not in nodes_by_id:
            return None

        node = nodes_by_id[target_id]
        source_pages = valid_source_pages(
            node.get("source_pages", []), allowed_pages
        )
        connected_edges = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            source_id = edge.get("source")
            target_node_id = edge.get("target")
            if target_id not in {source_id, target_node_id}:
                continue
            if source_id not in nodes_by_id or target_node_id not in nodes_by_id:
                continue
            connected_edge = {
                "source": nodes_by_id[source_id]["label"],
                "relation": edge.get("label", ""),
                "target": nodes_by_id[target_node_id]["label"],
            }
            if target_type == "visual_flow_node":
                connected_edge["position"] = (
                    "previous step" if target_node_id == target_id else "next step"
                )
            connected_edges.append(connected_edge)

        selected_item = {
            "id": target_id,
            "label": label,
            "source_pages": source_pages,
        }
        if target_type == "concept_map_node":
            selected_item["role"] = node.get("role", "supporting")
        return selected_item, source_pages, {
            "connected_relationships": connected_edges
        }

    if target_type == "comparison_item":
        items = visualization.get("items", [])
        criteria = visualization.get("criteria", [])
        if not isinstance(items, list) or not isinstance(criteria, list):
            return None
        if not any(
            isinstance(item, dict) and item.get("id") == target_id
            for item in items
        ):
            return None

        comparison_values = []
        source_pages = set()
        for criterion in criteria:
            if not isinstance(criterion, dict):
                continue
            for value in criterion.get("values", []):
                if not isinstance(value, dict) or value.get("item_id") != target_id:
                    continue
                value_pages = valid_source_pages(
                    value.get("source_pages", []), allowed_pages
                )
                source_pages.update(value_pages)
                comparison_values.append(
                    {
                        "criterion": criterion.get("criterion", ""),
                        "value": value.get("value", ""),
                        "source_pages": value_pages,
                    }
                )
                break

        source_pages = sorted(source_pages)
        return (
            {
                "id": target_id,
                "label": label,
                "source_pages": source_pages,
            },
            source_pages,
            {
                "comparison_title": visualization.get("title", ""),
                "criteria_and_values": comparison_values,
                "takeaway": visualization.get("takeaway", ""),
            },
        )

    return None


def build_learning_step_explanation_target(target, learning_path, allowed_pages):
    """Build one validated lesson-step target with adjacent step context."""
    if not isinstance(target, dict) or not isinstance(learning_path, dict):
        return None

    target_id = target.get("id")
    steps = learning_path.get("steps", [])
    if not isinstance(target_id, str) or not isinstance(steps, list):
        return None

    step_index = next(
        (
            index
            for index, step in enumerate(steps)
            if isinstance(step, dict) and step.get("id") == target_id
        ),
        None,
    )
    if step_index is None:
        return None

    step = steps[step_index]
    source_pages = valid_source_pages(
        step.get("source_pages", []), allowed_pages
    )
    selected_item = {
        "id": target_id,
        "title": step.get("title", ""),
        "learning_goal": step.get("learning_goal", ""),
        "explanation": step.get("explanation", ""),
        "connection_to_previous": step.get("connection_to_previous", ""),
        "source_pages": source_pages,
    }

    nearby_steps = []
    for index in (step_index - 1, step_index + 1):
        if not 0 <= index < len(steps):
            continue
        nearby_step = steps[index]
        nearby_steps.append(
            {
                "position": "previous" if index < step_index else "next",
                "id": nearby_step["id"],
                "title": nearby_step["title"],
                "learning_goal": nearby_step["learning_goal"],
                "connection_to_previous": nearby_step["connection_to_previous"],
                "source_pages": valid_source_pages(
                    nearby_step.get("source_pages", []), allowed_pages
                ),
            }
        )

    return selected_item, source_pages, {"nearby_steps": nearby_steps}


def build_explanation_context(
    target_type,
    target,
    analysis,
    source_context,
    allowed_pages,
    visualization=None,
):
    """Build bounded, source-aware context for an explanation request."""
    source_context = source_context if isinstance(source_context, dict) else {}
    source_kind = source_context.get("kind", "text")

    visualization_context = {}
    learning_path_context = {}
    if target_type == "key_concept":
        target_pages = valid_source_pages(
            target.get("source_pages", []), allowed_pages
        )
        selected_item = {
            "concept": target.get("concept", ""),
            "explanation": target.get("explanation", ""),
            "source_pages": target_pages,
        }
    elif target_type == "visual_evidence":
        page = target.get("page")
        target_pages = [page] if page in allowed_pages else []
        selected_item = {
            "type": target.get("type", "other"),
            "description": target.get("description", ""),
            "learning_value": target.get("learning_value", ""),
            "page": page if target_pages else None,
        }
    elif target_type == "learning_path_step":
        learning_target = build_learning_step_explanation_target(
            target, visualization, allowed_pages
        )
        if learning_target is None:
            return None
        selected_item, target_pages, learning_path_context = learning_target
    else:
        visualization_target = build_visualization_explanation_target(
            target_type, target, visualization, allowed_pages
        )
        if visualization_target is None:
            return None
        selected_item, target_pages, visualization_context = visualization_target

    source_sections = []
    if source_kind == "pdf":
        page_texts = source_context.get("page_texts", {})
        if isinstance(page_texts, dict):
            for page in target_pages:
                page_text = page_texts.get(page, "")
                if isinstance(page_text, str) and page_text.strip():
                    source_sections.append(f"[Page {page}]\n{page_text.strip()}")
    else:
        pasted_text = source_context.get("source_text", "")
        if isinstance(pasted_text, str) and pasted_text.strip():
            source_sections.append(pasted_text.strip())
    relevant_source_text = "\n\n".join(source_sections)
    relevant_source_text = relevant_source_text[:MAX_EXPLANATION_SOURCE_CHARS]

    nearby_concepts = []
    raw_concepts = analysis.get("key_concepts", [])
    if isinstance(raw_concepts, list):
        for item in raw_concepts:
            if not isinstance(item, dict):
                continue
            concept = item.get("concept")
            explanation = item.get("explanation")
            pages = valid_source_pages(item.get("source_pages", []), allowed_pages)
            if not isinstance(concept, str) or not concept.strip():
                continue
            if target_pages and not set(pages).intersection(target_pages):
                continue
            nearby_concepts.append(
                {
                    "concept": concept.strip(),
                    "explanation": (
                        explanation.strip() if isinstance(explanation, str) else ""
                    ),
                    "source_pages": pages,
                }
            )
            if len(nearby_concepts) == 5:
                break

    target_terms = {
        value.strip().casefold()
        for value in (
            selected_item.get("concept", ""),
            selected_item.get("label", ""),
            selected_item.get("title", ""),
            *(item["concept"] for item in nearby_concepts),
        )
        if isinstance(value, str) and value.strip()
    }
    nearby_relationships = []
    raw_relationships = analysis.get("relationships", [])
    if isinstance(raw_relationships, list):
        for item in raw_relationships:
            if not isinstance(item, dict):
                continue
            source = item.get("source")
            relation = item.get("relation")
            relationship_target = item.get("target")
            if not all(
                isinstance(value, str) and value.strip()
                for value in (source, relation, relationship_target)
            ):
                continue
            pages = valid_source_pages(item.get("source_pages", []), allowed_pages)
            touches_target = (
                source.strip().casefold() in target_terms
                or relationship_target.strip().casefold() in target_terms
            )
            overlaps_pages = bool(
                target_pages and set(pages).intersection(target_pages)
            )
            if not touches_target and not overlaps_pages:
                continue
            nearby_relationships.append(
                {
                    "source": source.strip(),
                    "relation": relation.strip(),
                    "target": relationship_target.strip(),
                    "source_pages": pages,
                }
            )
            if len(nearby_relationships) == 5:
                break

    return {
        "source_kind": source_kind,
        "response_language": get_explanation_language(analysis),
        "selected_item_type": target_type,
        "selected_item": selected_item,
        "quick_summary": analysis.get("quick_summary", ""),
        "relevant_pages": target_pages,
        "relevant_extracted_source_text": relevant_source_text,
        "nearby_key_concepts": nearby_concepts,
        "nearby_relationships": nearby_relationships,
        "visualization_context": visualization_context,
        "learning_path_context": learning_path_context,
        "pdf_reinspection_status": (
            "The original PDF is not attached to this explanation request. "
            "Visual evidence and visualization data come from the prior analysis."
            if source_kind == "pdf"
            else "Not applicable to pasted text."
        ),
    }


def request_explanation(client, explanation_context):
    """Request one source-aware drill-down explanation from the Responses API."""
    instructions = """You explain one selected part of a learning analysis.

Return only data matching the supplied JSON Schema.
- plain_explanation: explain the selected item clearly in simpler language.
- why_it_matters: state its role in understanding the broader material.
- intuition_or_example: give a concise intuition or example when useful; otherwise
  return an empty string.
- source_note: write one short line. Identify the relevant PDF page or pages from
  relevant_pages, or identify the source as pasted text. State whether source
  material was used and whether general explanatory knowledge was added. Do not
  write a paragraph or repeat the explanation.

Use only page numbers present in relevant_pages. Never invent source pages. For any
PDF target, the original PDF is not attached to this request: rely on the extracted
text and structured results from the prior analysis, and do not claim that you
reinspected the PDF. For visualization targets, use visualization_context directly
instead of reconstructing graph connections, flow steps, or comparison values.
For a learning_path_step target, use learning_path_context for the adjacent steps
and explain the selected lesson step without replacing the guided lesson.
Keep the explanation concise and educational. Use the exact language specified by
response_language for every output field. That language hint comes from the full
active analysis, so do not switch languages based on the selected item alone. When
response_language is Traditional Chinese, use Traditional Chinese characters and
never Simplified Chinese. When it is English, use English.
Keep quoted source excerpts and mathematical variables in their original language.
Never present a translated passage as original source evidence.
"""
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=json.dumps(explanation_context, ensure_ascii=False),
        text={
            "format": {
                "type": "json_schema",
                "name": "visual_learning_explanation",
                "strict": True,
                "schema": EXPLANATION_SCHEMA,
            }
        },
    )
    explanation = clean_explanation(json.loads(response.output_text))
    if explanation is None:
        raise ValueError("The model returned an invalid explanation object.")
    return explanation


def build_focused_review_context(
    analysis,
    learning_path,
    incorrect_questions,
    answers,
    source_context,
    allowed_pages,
):
    """Build bounded context around the learner's checked wrong answers."""
    steps = learning_path["steps"]
    steps_by_id = {step["id"]: step for step in steps}
    relevant_step_ids = {
        step_id
        for question in incorrect_questions
        for step_id in question["related_step_ids"]
        if step_id in steps_by_id
    }
    relevant_steps = [
        step for step in steps if step["id"] in relevant_step_ids
    ]

    incorrect_context = []
    relevant_pages = set()
    for question in incorrect_questions:
        options_by_id = {
            option["id"]: option["text"] for option in question["options"]
        }
        selected_option_id = answers.get(question["id"])
        correct_option_id = question["correct_option_id"]
        question_pages = valid_source_pages(
            question.get("source_pages", []), allowed_pages
        )
        relevant_pages.update(question_pages)
        incorrect_context.append(
            {
                "id": question["id"],
                "question": question["question"],
                "learner_selected": {
                    "id": selected_option_id,
                    "text": options_by_id.get(selected_option_id, ""),
                },
                "correct_option": {
                    "id": correct_option_id,
                    "text": options_by_id[correct_option_id],
                },
                "checkpoint_explanation": question["explanation"],
                "related_step_ids": question["related_step_ids"],
                "source_pages": question_pages,
            }
        )

    step_context = []
    for step in relevant_steps:
        step_pages = valid_source_pages(
            step.get("source_pages", []), allowed_pages
        )
        relevant_pages.update(step_pages)
        step_context.append(
            {
                "id": step["id"],
                "title": step["title"],
                "learning_goal": step["learning_goal"],
                "explanation": step["explanation"],
                "connection_to_previous": step["connection_to_previous"],
                "source_pages": step_pages,
            }
        )

    relevant_pages = sorted(relevant_pages)
    source_context = source_context if isinstance(source_context, dict) else {}
    source_kind = source_context.get("kind", "text")
    source_sections = []
    if source_kind == "pdf":
        page_texts = source_context.get("page_texts", {})
        if isinstance(page_texts, dict):
            for page in relevant_pages:
                page_text = page_texts.get(page, "")
                if isinstance(page_text, str) and page_text.strip():
                    source_sections.append(f"[Page {page}]\n{page_text.strip()}")
    else:
        pasted_text = source_context.get("source_text", "")
        if isinstance(pasted_text, str) and pasted_text.strip():
            source_sections.append(pasted_text.strip())
    relevant_source_text = "\n\n".join(source_sections)
    relevant_source_text = relevant_source_text[:MAX_EXPLANATION_SOURCE_CHARS]

    key_concepts = []
    for item in analysis.get("key_concepts", []):
        if not isinstance(item, dict):
            continue
        pages = valid_source_pages(item.get("source_pages", []), allowed_pages)
        if relevant_pages and not set(pages).intersection(relevant_pages):
            continue
        key_concepts.append(
            {
                "concept": item.get("concept", ""),
                "explanation": item.get("explanation", ""),
                "source_pages": pages,
            }
        )
        if len(key_concepts) == 6:
            break

    relevant_terms = {
        value.strip().casefold()
        for value in (
            *(step["title"] for step in relevant_steps),
            *(item["concept"] for item in key_concepts),
        )
        if isinstance(value, str) and value.strip()
    }
    relationships = []
    for item in clean_relationships(
        analysis.get("relationships", []), allowed_pages
    ):
        page_overlap = bool(
            relevant_pages
            and set(item["source_pages"]).intersection(relevant_pages)
        )
        term_overlap = (
            item["source"].casefold() in relevant_terms
            or item["target"].casefold() in relevant_terms
        )
        if not page_overlap and not term_overlap:
            continue
        relationships.append(item)
        if len(relationships) == 6:
            break

    visual_evidence = [
        item
        for item in clean_visual_evidence(
            analysis.get("visual_evidence", []), allowed_pages
        )
        if item["page"] in relevant_pages
    ][:4]

    return {
        "source_kind": source_kind,
        "response_language": get_explanation_language(analysis),
        "quick_summary": analysis.get("quick_summary", ""),
        "incorrect_checkpoint_questions": incorrect_context,
        "related_learning_steps": step_context,
        "relevant_key_concepts": key_concepts,
        "relevant_relationships": relationships,
        "relevant_visual_evidence": visual_evidence,
        "relevant_pages": relevant_pages,
        "relevant_extracted_source_text": relevant_source_text,
        "pdf_reinspection_status": (
            "The original PDF is not attached to this focused-review request."
            if source_kind == "pdf"
            else "Not applicable to pasted text."
        ),
    }


def request_focused_review(
    client, review_context, allowed_pages, valid_step_ids
):
    """Generate and validate one explicitly requested targeted review."""
    instructions = """Create a small focused review for the learner's checked mistakes.

Return only data matching the supplied JSON Schema.
- Address the exact distinction behind each learner-selected wrong option. Do not
  produce a generic chapter summary and do not repeat original questions verbatim.
- Create 1–3 review items for distinct review areas when practical. Use only valid
  learning-step ids from related_learning_steps in related_step_ids.
- Create a small Retry Check, preferably 2 questions, aimed at the missed ideas.
  Each retry question must have exactly four plausible options with unique ids, and
  correct_option_id must match one option. Avoid trivia and trick questions.
- Use only page numbers present in relevant_pages. Never invent page numbers. The
  original PDF is not attached, so do not claim to have reinspected it.
- Keep source_note to one short line that distinguishes supplied source context
  from any general explanatory knowledge added for clarification.
- Discuss specific responses and concepts without labeling or diagnosing the
  learner's ability.

Use the exact language specified by response_language for every output field. When
it is Traditional Chinese, use Traditional Chinese characters and never Simplified
Chinese. When it is English, use English.
Keep quoted source excerpts and mathematical variables in their original language.
Never present a translated passage as original source evidence.
"""
    response = client.responses.create(
        model=MODEL,
        instructions=instructions,
        input=json.dumps(review_context, ensure_ascii=False),
        text={
            "format": {
                "type": "json_schema",
                "name": "visual_learning_focused_review",
                "strict": True,
                "schema": FOCUSED_REVIEW_SCHEMA,
            }
        },
    )
    raw_review = json.loads(response.output_text)
    focused_review = clean_focused_review(
        raw_review, allowed_pages, valid_step_ids
    )
    if focused_review is None:
        raise ValueError("The model returned an invalid focused review.")
    return focused_review


def render_explanation(explanation):
    """Render the currently active contextual explanation."""
    with st.container(border=True):
        st.markdown("##### " + tr("Explain This"))
        st.markdown("**" + tr("In simple terms") + "**")
        st.write(explanation["plain_explanation"])
        st.markdown("**" + tr("Why it matters") + "**")
        st.write(explanation["why_it_matters"])
        if explanation["intuition_or_example"]:
            st.markdown("**" + tr("Intuition or example") + "**")
            st.write(explanation["intuition_or_example"])
        st.caption(tr("Source context: {note}", note=explanation["source_note"]))


def render_explain_action(
    cache_key, explanation_context, button_label=None
):
    """Render one inline action and cache its explanation for this analysis."""
    cache = st.session_state.setdefault("explanation_cache", {})
    errors = st.session_state.setdefault("explanation_errors", {})

    if st.button(button_label or tr("Explain this"), key=f"explain-{cache_key}", type="tertiary"):
        st.session_state["active_explanation_key"] = cache_key
        if cache_key not in cache:
            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)
                with st.spinner(tr("Explaining this part…")):
                    cache[cache_key] = request_explanation(
                        client, explanation_context
                    )
                errors.pop(cache_key, None)
            except (KeyError, st.errors.StreamlitSecretNotFoundError):
                errors[cache_key] = (
                    tr("OpenAI API access is not configured for explanations yet.")
                )
            except (json.JSONDecodeError, ValueError):
                errors[cache_key] = (
                    tr("This explanation came back in an unexpected format. Please try again.")
                )
            except Exception:
                errors[cache_key] = (
                    tr("We couldn’t explain this item right now. Please try again.")
                )

    if st.session_state.get("active_explanation_key") == cache_key:
        if cache_key in cache:
            render_explanation(cache[cache_key])
        elif cache_key in errors:
            st.error(errors[cache_key])


def render_visualization_explorer(
    visualization_type,
    visualization,
    analysis,
    source_context,
    allowed_pages,
    analysis_id,
):
    """Render one compact selector that reuses the existing explanation system."""
    st.markdown("#### " + tr("Explore this visualization"))
    if not visualization or not visualization.get("suitable"):
        st.caption(tr("No visualization elements are available to explore."))
        return

    if visualization_type == "comparison_item":
        targets = visualization.get("items", [])
        select_label = tr("Choose an item")
    elif visualization_type == "visual_flow_node":
        targets = visualization.get("nodes", [])
        select_label = tr("Choose a step")
    else:
        targets = visualization.get("nodes", [])
        select_label = tr("Choose a concept")

    targets_by_id = {
        target["id"]: target
        for target in targets
        if isinstance(target, dict)
        and isinstance(target.get("id"), str)
        and target.get("id")
        and isinstance(target.get("label"), str)
        and target.get("label")
    }
    if not targets_by_id:
        st.caption(tr("No visualization elements are available to explore."))
        return

    selected_id = st.selectbox(
        select_label,
        options=list(targets_by_id),
        format_func=lambda target_id: targets_by_id[target_id]["label"],
        key=f"explore-select-{analysis_id}-{visualization_type}",
    )
    selected_target = targets_by_id.get(selected_id)
    if selected_target is None:
        st.warning(tr("That visualization element is no longer available."))
        return

    explanation_context = build_explanation_context(
        visualization_type,
        selected_target,
        analysis,
        source_context,
        allowed_pages,
        visualization=visualization,
    )
    if explanation_context is None:
        st.warning(tr("We couldn’t prepare that visualization element for explanation."))
        return

    render_explain_action(
        f"{analysis_id}:{visualization_type}:{selected_id}",
        explanation_context,
    )


def get_incorrect_questions(questions, answers, checked):
    """Return checked questions whose stored answer is incorrect."""
    return [
        question
        for question in questions
        if checked.get(question["id"])
        and answers.get(question["id"]) != question["correct_option_id"]
    ]


def build_review_queue(learning_path, incorrect_questions):
    """Map missed questions to deduplicated lesson steps in lesson order."""
    question_numbers = {
        question["id"]: index
        for index, question in enumerate(
            learning_path["checkpoint_questions"], start=1
        )
    }
    missed_by_step = {}
    for question in incorrect_questions:
        for step_id in question["related_step_ids"]:
            missed_by_step.setdefault(step_id, []).append(question["id"])

    return [
        {
            "step_id": step["id"],
            "title": step["title"],
            "source_pages": step["source_pages"],
            "question_ids": list(dict.fromkeys(missed_by_step[step["id"]])),
            "question_numbers": [
                question_numbers[question_id]
                for question_id in dict.fromkeys(missed_by_step[step["id"]])
                if question_id in question_numbers
            ],
        }
        for step in learning_path["steps"]
        if step["id"] in missed_by_step
    ]


def build_review_pattern_key(analysis_id, incorrect_questions, answers):
    """Identify one material-specific pattern of checked wrong answers."""
    pattern = sorted(
        (question["id"], answers.get(question["id"], ""))
        for question in incorrect_questions
    )
    digest = hashlib.sha256(
        json.dumps(pattern, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return f"{analysis_id}:{digest}"


def clear_adaptive_retry_widgets():
    """Remove retry radio state when the active mistake pattern changes."""
    for key in list(st.session_state):
        if isinstance(key, str) and key.startswith("adaptive-retry-option-"):
            st.session_state.pop(key, None)


def clear_active_adaptive_review():
    """Clear displayed review state while retaining reusable cached reviews."""
    state = st.session_state.get("adaptive_review_state")
    if isinstance(state, dict):
        state.update(
            {
                "pattern_key": None,
                "review_queue": [],
                "focused_review": None,
                "error": None,
                "retry_answers": {},
                "retry_checked": {},
            }
        )
    clear_adaptive_retry_widgets()


def reset_adaptive_review_state():
    """Clear all adaptive-review state and cache for a new material."""
    st.session_state.pop("adaptive_review_state", None)
    st.session_state.pop("focused_review_cache", None)
    clear_adaptive_retry_widgets()


def ensure_adaptive_review_state(analysis_id):
    """Return initialized adaptive-review state for the active material."""
    state = st.session_state.get("adaptive_review_state")
    if not isinstance(state, dict) or state.get("material_id") != analysis_id:
        reset_adaptive_review_state()
        state = {
            "material_id": analysis_id,
            "pattern_key": None,
            "review_queue": [],
            "focused_review": None,
            "error": None,
            "retry_answers": {},
            "retry_checked": {},
        }
        st.session_state["adaptive_review_state"] = state
        st.session_state["focused_review_cache"] = {}
    return state


def adaptive_review_copy():
    """Keep review chrome in the selected product language."""
    keys = (
        "complete", "review_areas", "related_questions", "review_step", "unmapped",
        "build", "building", "focused_review", "review", "what_to_fix",
        "focused_explanation", "intuition", "retry", "choose", "check",
        "choose_first", "correct", "not_quite", "no_retry", "original",
        "retry_result", "retry_complete", "correct_suffix", "source",
        "error", "key_error", "format_error",
    )
    return {key: tr(f"review.{key}") for key in keys}


def reset_guided_learning_state():
    """Clear lesson progress that belongs to a previous material."""
    for key in (
        "guided_learning_material_id",
        "guided_learning_started",
        "guided_learning_step_id",
        "guided_quiz_answers",
        "guided_quiz_checked",
    ):
        st.session_state.pop(key, None)
    for key in list(st.session_state):
        if isinstance(key, str) and key.startswith("guided-quiz-option-"):
            st.session_state.pop(key, None)
    reset_adaptive_review_state()


def ensure_guided_learning_state(analysis_id, learning_path):
    """Initialize and sanitize material-specific lesson and quiz state."""
    steps = learning_path["steps"]
    questions = learning_path["checkpoint_questions"]
    step_ids = {step["id"] for step in steps}
    questions_by_id = {question["id"]: question for question in questions}

    if st.session_state.get("guided_learning_material_id") != analysis_id:
        reset_guided_learning_state()
        st.session_state["guided_learning_material_id"] = analysis_id
        st.session_state["guided_learning_started"] = False
        st.session_state["guided_learning_step_id"] = steps[0]["id"]
        st.session_state["guided_quiz_answers"] = {}
        st.session_state["guided_quiz_checked"] = {}

    if st.session_state.get("guided_learning_step_id") not in step_ids:
        st.session_state["guided_learning_step_id"] = steps[0]["id"]

    answers = st.session_state.get("guided_quiz_answers", {})
    if not isinstance(answers, dict):
        answers = {}
    answers = {
        question_id: option_id
        for question_id, option_id in answers.items()
        if question_id in questions_by_id
        and option_id
        in {option["id"] for option in questions_by_id[question_id]["options"]}
    }
    st.session_state["guided_quiz_answers"] = answers

    checked = st.session_state.get("guided_quiz_checked", {})
    if not isinstance(checked, dict):
        checked = {}
    st.session_state["guided_quiz_checked"] = {
        question_id: True
        for question_id, is_checked in checked.items()
        if is_checked and question_id in answers and question_id in questions_by_id
    }


def calculate_quiz_result(questions, answers, checked):
    """Return a completed local quiz result, or None while answers are unchecked."""
    question_ids = {question["id"] for question in questions}
    if not question_ids or not question_ids.issubset(checked):
        return None
    correct_count = sum(
        answers.get(question["id"]) == question["correct_option_id"]
        for question in questions
    )
    return correct_count, len(questions)


def render_knowledge_check(questions, allowed_pages, analysis_id):
    """Render and grade the structured checkpoint quiz without API calls."""
    st.markdown("#### " + tr("Knowledge Check"))
    if not questions:
        st.caption(tr("No checkpoint questions are available for this lesson."))
        return None

    answers = st.session_state["guided_quiz_answers"]
    checked = st.session_state["guided_quiz_checked"]
    for index, question in enumerate(questions, start=1):
        question_id = question["id"]
        options_by_id = {
            option["id"]: option["text"] for option in question["options"]
        }
        st.markdown(f"**{index}. {question['question']}**")

        widget_key = f"guided-quiz-option-{analysis_id}-{question_id}"
        previous_answer = answers.get(question_id)
        if widget_key not in st.session_state and previous_answer in options_by_id:
            st.session_state[widget_key] = previous_answer
        selected_option = st.radio(
            tr("Choose an answer"),
            options=list(options_by_id),
            index=None,
            format_func=lambda option_id, labels=options_by_id: labels[option_id],
            key=widget_key,
            label_visibility="collapsed",
        )
        if selected_option != previous_answer:
            if selected_option is None:
                answers.pop(question_id, None)
            else:
                answers[question_id] = selected_option
            checked.pop(question_id, None)
            clear_active_adaptive_review()
            st.rerun()  # Refresh the canvas review emphasis above the quiz.

        if st.button(
            tr("Check answer"),
            key=f"guided-quiz-check-{analysis_id}-{question_id}",
        ):
            if selected_option is None:
                st.warning(tr("Choose an answer before checking."))
            else:
                checked[question_id] = True
                st.rerun()

        if checked.get(question_id):
            if answers.get(question_id) == question["correct_option_id"]:
                st.success(tr("Correct"))
            else:
                st.error(tr("Not quite"))
            st.write(question["explanation"])
            pages = valid_source_pages(
                question.get("source_pages", []), allowed_pages
            )
            if pages:
                st.caption(tr("Source: {pages}", pages=format_page_references(pages)))

    result = calculate_quiz_result(questions, answers, checked)
    if result is not None:
        correct_count, question_count = result
        st.info(tr("Knowledge Check: {correct} / {total} correct", correct=correct_count, total=question_count))
    return result


def render_retry_check(
    focused_review,
    original_result,
    adaptive_state,
    allowed_pages,
    pattern_key,
    copy,
):
    """Render and grade focused-review retry questions entirely locally."""
    st.markdown(f"#### {copy['retry']}")
    questions = focused_review["retry_questions"]
    if not questions:
        st.caption(copy["no_retry"])
        return

    answers = adaptive_state["retry_answers"]
    checked = adaptive_state["retry_checked"]
    pattern_digest = pattern_key.rsplit(":", 1)[-1]
    for index, question in enumerate(questions, start=1):
        question_id = question["id"]
        options_by_id = {
            option["id"]: option["text"] for option in question["options"]
        }
        st.markdown(f"**{index}. {question['question']}**")

        widget_key = (
            f"adaptive-retry-option-{pattern_digest}-{question_id}"
        )
        previous_answer = answers.get(question_id)
        if widget_key not in st.session_state and previous_answer in options_by_id:
            st.session_state[widget_key] = previous_answer
        selected_option = st.radio(
            copy["choose"],
            options=list(options_by_id),
            index=None,
            format_func=lambda option_id, labels=options_by_id: labels[option_id],
            key=widget_key,
            label_visibility="collapsed",
        )
        if selected_option != previous_answer:
            if selected_option is None:
                answers.pop(question_id, None)
            else:
                answers[question_id] = selected_option
            checked.pop(question_id, None)

        if st.button(
            copy["check"],
            key=f"adaptive-retry-check-{pattern_digest}-{question_id}",
        ):
            if selected_option is None:
                st.warning(copy["choose_first"])
            else:
                checked[question_id] = True

        if checked.get(question_id):
            if answers.get(question_id) == question["correct_option_id"]:
                st.success(copy["correct"])
            else:
                st.error(copy["not_quite"])
            st.write(question["explanation"])
            pages = valid_source_pages(
                question.get("source_pages", []), allowed_pages
            )
            if pages:
                st.caption(
                    f"{copy['source']}: {format_page_references(pages)}"
                )

    retry_result = calculate_quiz_result(questions, answers, checked)
    if retry_result is not None:
        original_correct, original_total = original_result
        retry_correct, retry_total = retry_result
        st.info(
            f"{copy['original']}: {original_correct} / {original_total} "
            f"{copy['correct_suffix']}\n\n"
            f"{copy['retry_result']}: {retry_correct} / {retry_total} "
            f"{copy['correct_suffix']}"
        )
        st.caption(copy["retry_complete"])


def render_adaptive_review(
    learning_path,
    analysis,
    source_context,
    allowed_pages,
    analysis_id,
    original_result,
    interactive_lab=None,
):
    """Render local review routing and an optional cached focused-review request."""
    questions = learning_path["checkpoint_questions"]
    answers = st.session_state["guided_quiz_answers"]
    checked = st.session_state["guided_quiz_checked"]
    copy = adaptive_review_copy()
    adaptive_state = ensure_adaptive_review_state(analysis_id)
    incorrect_questions = get_incorrect_questions(questions, answers, checked)

    if not incorrect_questions:
        clear_active_adaptive_review()
        st.success(copy["complete"])
        return

    review_queue = build_review_queue(learning_path, incorrect_questions)
    pattern_key = build_review_pattern_key(
        analysis_id, incorrect_questions, answers
    )
    if adaptive_state.get("pattern_key") != pattern_key:
        clear_adaptive_retry_widgets()
        focused_review_cache = st.session_state.setdefault(
            "focused_review_cache", {}
        )
        adaptive_state.update(
            {
                "pattern_key": pattern_key,
                "review_queue": review_queue,
                "focused_review": focused_review_cache.get(pattern_key),
                "error": None,
                "retry_answers": {},
                "retry_checked": {},
            }
        )

    st.markdown(f"#### {copy['review_areas']}")
    if review_queue:
        for index, queue_item in enumerate(review_queue, start=1):
            st.markdown(f"**{index}. {queue_item['title']}**")
            question_numbers = ", ".join(
                str(number) for number in queue_item["question_numbers"]
            )
            if question_numbers:
                st.caption(
                    f"{copy['related_questions']} {question_numbers}"
                )
            if queue_item["source_pages"]:
                st.caption(
                    f"{copy['source']}: "
                    f"{format_page_references(queue_item['source_pages'])}"
                )
            if st.button(
                copy["review_step"],
                key=(
                    f"adaptive-review-step-{pattern_key}-"
                    f"{queue_item['step_id']}"
                ),
            ):
                go_to_lesson(queue_item["step_id"], learning_path)
                st.rerun()
    else:
        st.caption(copy["unmapped"])

    render_lab_links(interactive_lab, [item["step_id"] for item in review_queue],
                     analysis_id, "review-queue", recommended=True)

    if adaptive_state.get("focused_review") is None:
        if st.button(
            copy["build"],
            key=f"adaptive-build-focused-{pattern_key}",
            type="primary",
        ):
            focused_review_cache = st.session_state.setdefault(
                "focused_review_cache", {}
            )
            cached_review = focused_review_cache.get(pattern_key)
            if cached_review is not None:
                adaptive_state["focused_review"] = cached_review
                adaptive_state["error"] = None
            else:
                try:
                    api_key = st.secrets["OPENAI_API_KEY"]
                    client = OpenAI(api_key=api_key)
                    review_context = build_focused_review_context(
                        analysis,
                        learning_path,
                        incorrect_questions,
                        answers,
                        source_context,
                        allowed_pages,
                    )
                    with st.spinner(copy["building"]):
                        focused_review = request_focused_review(
                            client,
                            review_context,
                            allowed_pages,
                            {step["id"] for step in learning_path["steps"]},
                        )
                    focused_review_cache[pattern_key] = focused_review
                    adaptive_state["focused_review"] = focused_review
                    adaptive_state["error"] = None
                    st.rerun()  # Reflect review-to-canvas links after the explicit request.
                except (KeyError, st.errors.StreamlitSecretNotFoundError):
                    adaptive_state["error"] = copy["key_error"]
                except (json.JSONDecodeError, ValueError):
                    adaptive_state["error"] = copy["format_error"]
                except Exception:
                    adaptive_state["error"] = copy["error"]

    if adaptive_state.get("error"):
        st.error(adaptive_state["error"])

    focused_review = adaptive_state.get("focused_review")
    if focused_review is None:
        return

    st.markdown(f"### {copy['focused_review']}")
    st.markdown(f"#### {focused_review['review_title']}")
    st.write(focused_review["review_summary"])
    for index, item in enumerate(focused_review["items"], start=1):
        st.markdown(f"##### {copy['review']} {index}")
        st.markdown(f"**{copy['what_to_fix']}**")
        st.write(item["what_to_fix"])
        st.markdown(f"**{copy['focused_explanation']}**")
        st.write(item["focused_explanation"])
        if item["intuition_or_example"]:
            st.markdown(f"**{copy['intuition']}**")
            st.write(item["intuition_or_example"])
        if item["source_pages"]:
            st.caption(
                f"{copy['source']}: "
                f"{format_page_references(item['source_pages'])}"
            )
    st.caption(focused_review["source_note"])
    render_lab_links(interactive_lab,
                     [step_id for item in focused_review["items"] for step_id in item["related_step_ids"]],
                     analysis_id, "focused-review", recommended=True)

    render_retry_check(
        focused_review,
        original_result,
        adaptive_state,
        allowed_pages,
        pattern_key,
        copy,
    )


def render_guided_learning(
    learning_path,
    analysis,
    primary_visualization,
    source_context,
    allowed_pages,
    analysis_id,
    interactive_lab=None,
):
    """Render one lesson step at a time with local navigation and quiz state."""
    st.markdown("### " + tr("Guided Learning"))
    if not learning_path or not learning_path.get("suitable"):
        reason = learning_path.get("reason", "") if learning_path else ""
        st.caption(reason or tr("A guided learning path is not available for this material."))
        return

    ensure_guided_learning_state(analysis_id, learning_path)
    steps = learning_path["steps"]
    st.markdown(f"#### {learning_path['title']}")

    if not st.session_state["guided_learning_started"]:
        st.write(tr("Learn this material in {count} steps.", count=len(steps)))
        if learning_path["reason"]:
            st.caption(learning_path["reason"])
        if st.button(
            tr("Start guided learning"),
            key=f"guided-start-{analysis_id}",
            type="primary",
        ):
            st.session_state["guided_learning_started"] = True
            st.session_state["guided_learning_step_id"] = steps[0]["id"]
            st.rerun()
        return

    step_ids = [step["id"] for step in steps]
    current_step_id = st.session_state["guided_learning_step_id"]
    current_index = step_ids.index(current_step_id)
    current_step = steps[current_index]

    st.caption(tr("Step {number} of {count}", number=current_index + 1, count=len(steps)))
    st.progress((current_index + 1) / len(steps))
    st.markdown(f"#### {current_step['title']}")
    st.markdown("**" + tr("Goal") + "**")
    st.write(current_step["learning_goal"])
    st.markdown("**" + tr("Explanation") + "**")
    st.write(current_step["explanation"])
    if current_step["connection_to_previous"]:
        st.markdown("**" + tr("Why this comes next") + "**")
        st.write(current_step["connection_to_previous"])
    if current_step["source_pages"]:
        st.caption(
            tr("Source: {pages}", pages=format_page_references(current_step["source_pages"]))
        )

    visualization_labels = {
        "flow": "Visual Flow",
        "concept_map": "Concept Map",
        "comparison": "Comparison",
    }
    related_visualization = visualization_labels.get(primary_visualization["type"])
    if related_visualization:
        st.caption(tr("Related visualization: {label}", label=tr(related_visualization)))

    render_lab_links(interactive_lab, [current_step_id], analysis_id, "guided")

    previous_column, next_column = st.columns(2)
    with previous_column:
        if st.button(
            tr("Previous"),
            key=f"guided-previous-{analysis_id}-{current_step_id}",
            disabled=current_index == 0,
            use_container_width=True,
        ):
            st.session_state["guided_learning_step_id"] = step_ids[
                current_index - 1
            ]
            st.rerun()
    with next_column:
        if st.button(
            tr("Next"),
            key=f"guided-next-{analysis_id}-{current_step_id}",
            disabled=current_index == len(steps) - 1,
            use_container_width=True,
        ):
            st.session_state["guided_learning_step_id"] = step_ids[
                current_index + 1
            ]
            st.rerun()

    explanation_context = build_explanation_context(
        "learning_path_step",
        current_step,
        analysis,
        source_context,
        allowed_pages,
        visualization=learning_path,
    )
    if explanation_context is not None:
        render_explain_action(
            f"{analysis_id}:learning_path_step:{current_step_id}",
            explanation_context,
            button_label=tr("Explain this step"),
        )

    if current_index == len(steps) - 1:
        original_result = render_knowledge_check(
            learning_path["checkpoint_questions"],
            allowed_pages,
            analysis_id,
        )
        if original_result is not None:
            render_adaptive_review(
                learning_path,
                analysis,
                source_context,
                allowed_pages,
                analysis_id,
                original_result,
                interactive_lab,
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
    return tr("p. {pages}", pages=", ".join(parts))


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


def clean_learning_path(raw_path, allowed_pages, visualization_type="none", visualization=None):
    """Validate lesson steps and keep only independently valid quiz questions."""
    if not isinstance(raw_path, dict):
        return None

    reason = raw_path.get("reason", "")
    reason = reason.strip() if isinstance(reason, str) else ""
    if raw_path.get("suitable") is not True:
        return {
            "suitable": False,
            "title": "",
            "reason": reason,
            "steps": [],
            "checkpoint_questions": [],
        }

    title = raw_path.get("title")
    raw_steps = raw_path.get("steps")
    if (
        not isinstance(title, str)
        or not title.strip()
        or not isinstance(raw_steps, list)
        or not 2 <= len(raw_steps) <= 6
    ):
        return None

    steps = []
    step_ids = set()
    for raw_step in raw_steps:
        if not isinstance(raw_step, dict):
            return None
        step_id = raw_step.get("id")
        step_title = raw_step.get("title")
        learning_goal = raw_step.get("learning_goal")
        explanation = raw_step.get("explanation")
        connection = raw_step.get("connection_to_previous")
        if not all(
            isinstance(value, str)
            for value in (
                step_id,
                step_title,
                learning_goal,
                explanation,
                connection,
            )
        ):
            return None
        step_id = step_id.strip()
        step_title = step_title.strip()
        learning_goal = learning_goal.strip()
        explanation = explanation.strip()
        connection = connection.strip()
        if (
            not step_id
            or step_id in step_ids
            or not step_title
            or not learning_goal
            or not explanation
        ):
            return None
        step_ids.add(step_id)
        steps.append(
            {
                "id": step_id,
                "title": step_title,
                "learning_goal": learning_goal,
                "explanation": explanation,
                "source_pages": valid_source_pages(
                    raw_step.get("source_pages", []), allowed_pages
                ),
                "connection_to_previous": connection,
                "visual_refs": clean_visual_refs(
                    raw_step.get("visual_refs", []), visualization_type, visualization
                ),
            }
        )

    checkpoint_questions = []
    question_ids = set()
    raw_questions = raw_path.get("checkpoint_questions", [])
    if not isinstance(raw_questions, list):
        raw_questions = []
    for raw_question in raw_questions[:3]:
        if not isinstance(raw_question, dict):
            continue
        question_id = raw_question.get("id")
        question = raw_question.get("question")
        explanation = raw_question.get("explanation")
        correct_option_id = raw_question.get("correct_option_id")
        raw_options = raw_question.get("options")
        if (
            not all(
                isinstance(value, str) and value.strip()
                for value in (
                    question_id,
                    question,
                    explanation,
                    correct_option_id,
                )
            )
            or question_id.strip() in question_ids
            or not isinstance(raw_options, list)
            or len(raw_options) != 4
        ):
            continue

        options = []
        option_ids = set()
        options_valid = True
        for raw_option in raw_options:
            if not isinstance(raw_option, dict):
                options_valid = False
                break
            option_id = raw_option.get("id")
            option_text = raw_option.get("text")
            if not all(
                isinstance(value, str) and value.strip()
                for value in (option_id, option_text)
            ):
                options_valid = False
                break
            option_id, option_text = option_id.strip(), option_text.strip()
            if option_id in option_ids:
                options_valid = False
                break
            option_ids.add(option_id)
            options.append({"id": option_id, "text": option_text})

        correct_option_id = correct_option_id.strip()
        if not options_valid or correct_option_id not in option_ids:
            continue

        raw_related_step_ids = raw_question.get("related_step_ids", [])
        if not isinstance(raw_related_step_ids, list):
            raw_related_step_ids = []
        related_step_ids = []
        for related_step_id in raw_related_step_ids:
            if (
                isinstance(related_step_id, str)
                and related_step_id in step_ids
                and related_step_id not in related_step_ids
            ):
                related_step_ids.append(related_step_id)

        question_id = question_id.strip()
        question_ids.add(question_id)
        checkpoint_questions.append(
            {
                "id": question_id,
                "question": question.strip(),
                "options": options,
                "correct_option_id": correct_option_id,
                "explanation": explanation.strip(),
                "source_pages": valid_source_pages(
                    raw_question.get("source_pages", []), allowed_pages
                ),
                "related_step_ids": related_step_ids,
            }
        )

    return {
        "suitable": True,
        "title": title.strip(),
        "reason": reason,
        "steps": steps,
        "checkpoint_questions": checkpoint_questions,
    }


def clean_focused_review(raw_review, allowed_pages, valid_step_ids):
    """Validate focused-review content while isolating malformed retry questions."""
    if not isinstance(raw_review, dict):
        return None

    review_title = raw_review.get("review_title")
    review_summary = raw_review.get("review_summary")
    source_note = raw_review.get("source_note")
    raw_items = raw_review.get("items")
    raw_retry_questions = raw_review.get("retry_questions", [])
    if (
        not all(
            isinstance(value, str) and value.strip()
            for value in (review_title, review_summary, source_note)
        )
        or not isinstance(raw_items, list)
        or not isinstance(raw_retry_questions, list)
    ):
        return None

    valid_step_ids = set(valid_step_ids)
    items = []
    item_ids = set()
    for raw_item in raw_items[:3]:
        if not isinstance(raw_item, dict):
            continue
        item_id = raw_item.get("id")
        what_to_fix = raw_item.get("what_to_fix")
        focused_explanation = raw_item.get("focused_explanation")
        intuition_or_example = raw_item.get("intuition_or_example")
        if (
            not all(
                isinstance(value, str)
                for value in (
                    item_id,
                    what_to_fix,
                    focused_explanation,
                    intuition_or_example,
                )
            )
            or not item_id.strip()
            or item_id.strip() in item_ids
            or not what_to_fix.strip()
            or not focused_explanation.strip()
        ):
            continue
        item_id = item_id.strip()
        item_ids.add(item_id)
        related_step_ids = []
        raw_related_step_ids = raw_item.get("related_step_ids", [])
        if isinstance(raw_related_step_ids, list):
            for step_id in raw_related_step_ids:
                if (
                    isinstance(step_id, str)
                    and step_id in valid_step_ids
                    and step_id not in related_step_ids
                ):
                    related_step_ids.append(step_id)
        items.append(
            {
                "id": item_id,
                "related_step_ids": related_step_ids,
                "what_to_fix": what_to_fix.strip(),
                "focused_explanation": focused_explanation.strip(),
                "intuition_or_example": intuition_or_example.strip(),
                "source_pages": valid_source_pages(
                    raw_item.get("source_pages", []), allowed_pages
                ),
            }
        )

    if not items:
        return None

    retry_questions = []
    retry_question_ids = set()
    for raw_question in raw_retry_questions[:2]:
        if not isinstance(raw_question, dict):
            continue
        question_id = raw_question.get("id")
        question = raw_question.get("question")
        explanation = raw_question.get("explanation")
        correct_option_id = raw_question.get("correct_option_id")
        raw_options = raw_question.get("options")
        if (
            not all(
                isinstance(value, str) and value.strip()
                for value in (
                    question_id,
                    question,
                    explanation,
                    correct_option_id,
                )
            )
            or question_id.strip() in retry_question_ids
            or not isinstance(raw_options, list)
            or len(raw_options) != 4
        ):
            continue

        options = []
        option_ids = set()
        options_valid = True
        for raw_option in raw_options:
            if not isinstance(raw_option, dict):
                options_valid = False
                break
            option_id = raw_option.get("id")
            option_text = raw_option.get("text")
            if not all(
                isinstance(value, str) and value.strip()
                for value in (option_id, option_text)
            ):
                options_valid = False
                break
            option_id, option_text = option_id.strip(), option_text.strip()
            if option_id in option_ids:
                options_valid = False
                break
            option_ids.add(option_id)
            options.append({"id": option_id, "text": option_text})

        correct_option_id = correct_option_id.strip()
        if not options_valid or correct_option_id not in option_ids:
            continue

        related_step_ids = []
        raw_related_step_ids = raw_question.get("related_step_ids", [])
        if isinstance(raw_related_step_ids, list):
            for step_id in raw_related_step_ids:
                if (
                    isinstance(step_id, str)
                    and step_id in valid_step_ids
                    and step_id not in related_step_ids
                ):
                    related_step_ids.append(step_id)

        question_id = question_id.strip()
        retry_question_ids.add(question_id)
        retry_questions.append(
            {
                "id": question_id,
                "question": question.strip(),
                "options": options,
                "correct_option_id": correct_option_id,
                "explanation": explanation.strip(),
                "related_step_ids": related_step_ids,
                "source_pages": valid_source_pages(
                    raw_question.get("source_pages", []), allowed_pages
                ),
            }
        )

    return {
        "review_title": review_title.strip(),
        "review_summary": review_summary.strip(),
        "source_note": source_note.strip(),
        "items": items,
        "retry_questions": retry_questions,
    }


def build_comparison_table(comparison):
    """Build rows for a static Streamlit comparison table."""
    if not comparison or not comparison["suitable"]:
        return []

    item_labels = {item["id"]: item["label"] for item in comparison["items"]}
    rows = []
    for criterion in comparison["criteria"]:
        row = {tr("Criterion"): criterion["criterion"]}
        for value in criterion["values"]:
            cell = value["value"]
            if value["source_pages"]:
                cell += "\n\n" + tr("Source: {pages}", pages=format_page_references(value["source_pages"]))
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
        fontname="Noto Sans TC, Microsoft JhengHei, sans-serif",
        fontsize="14",
        margin="0.18,0.12",
    )
    graph.attr(
        "edge",
        color="#8270DF",
        fontname="Noto Sans TC, Microsoft JhengHei, sans-serif",
        fontsize="12",
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
        fontname="Noto Sans TC, Microsoft JhengHei, sans-serif",
        fontsize="14",
        margin="0.18,0.12",
    )
    graph.attr(
        "edge",
        color="#8270DF",
        fontname="Noto Sans TC, Microsoft JhengHei, sans-serif",
        fontsize="12",
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

st.set_page_config(page_title="Visual Learning Lab", page_icon="✦", layout="wide")

render_header()

with st.container(border=True):
    st.subheader(tr("Start with what you’re learning"))
    st.caption(tr("Bring a page, a chapter, or an idea you want to understand."))
    uploaded_pdf = st.file_uploader(
        tr("Upload a PDF"),
        type=["pdf"], key="material-pdf",
        help=tr("PDFs are analyzed through both extracted text and visual pages."),
    )
    content = st.text_area(
        tr("Or paste your content"),
        height=200, key="material-text",
        placeholder=tr("Paste your notes, a tricky explanation, or a concept you want to explore…"),
    )
    st.caption(tr("Use one source at a time · PDF text and visual page content are analyzed together."))
    st.caption(tr("Original source excerpts stay in their original language."))
    if st.button(tr("Visualize"), key="analyze-material", type="primary", use_container_width=True):
        st.session_state.pop("analysis", None)
        st.session_state.pop("source_info", None)
        st.session_state.pop("allowed_source_pages", None)
        st.session_state.pop("source_context", None)
        st.session_state.pop("analysis_id", None)
        st.session_state["explanation_cache"] = {}
        st.session_state["explanation_errors"] = {}
        st.session_state.pop("active_explanation_key", None)
        reset_guided_learning_state()
        reset_canvas_state()
        reset_lab_state()
        reset_simulation_state()
        reset_scene_state()
        st.session_state.pop("analysis_language", None)

        has_pdf = uploaded_pdf is not None
        has_pasted_text = bool(content.strip())

        if not has_pdf and not has_pasted_text:
            st.warning(tr("Please upload a PDF or paste some learning content first."))
        elif has_pdf and has_pasted_text:
            st.warning(tr("Please use only one source at a time: upload a PDF or paste text."))
        else:
            source_text = content.strip()
            allowed_source_pages = []
            source_info = None
            source_kind = "text"
            source_bytes = source_text.encode("utf-8")
            page_texts = {}

            if has_pdf:
                try:
                    pdf_data = extract_pdf_text(uploaded_pdf)
                except Exception:
                    st.error(
                        tr("We couldn’t read this PDF. Please check that it is a valid PDF and try again.")
                    )
                    pdf_data = None

                if pdf_data is not None:
                    found_pages = pdf_data["extractable_page_numbers"]
                    analyzed_pages = pdf_data["analyzed_page_numbers"]
                    if not found_pages:
                        st.warning(
                            tr("No extractable text was found in this PDF. It may be scanned or image-based. Visual analysis still requires a readable PDF file.")
                        )
                    else:
                        source_text = pdf_data["text"]
                        allowed_source_pages = analyzed_pages
                        source_kind = "pdf"
                        source_bytes = uploaded_pdf.getvalue()
                        page_texts = pdf_data["analyzed_page_texts"]
                        source_info = {
                            "found_count": len(found_pages),
                            "total_count": pdf_data["total_pages"],
                            "analyzed_count": len(analyzed_pages),
                        }
                        st.info(
                            tr("Found extractable text on {found} of {total} PDF page(s); analyzing the first {analyzed} extractable page(s).", found=len(found_pages), total=pdf_data["total_pages"], analyzed=len(analyzed_pages))
                        )

            if has_pdf and not source_info:
                source_text = ""

            if not source_text:
                st.stop()

            st.session_state["source_info"] = source_info
            st.session_state["allowed_source_pages"] = allowed_source_pages
            st.session_state["source_context"] = {
                "kind": source_kind,
                "source_text": source_text if source_kind == "text" else "",
                "page_texts": page_texts,
            }
            st.session_state["analysis_id"] = build_analysis_id(
                source_kind, source_bytes, current_language()
            )
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
- learning_path: create a short guided lesson from the same understanding used for
  the rest of this analysis. When the material supports it, set suitable to true,
  create a concise title, and prefer 4–6 steps in a pedagogically meaningful order.
  Each step must teach one idea, use a unique canonical id, stay focused, and
  explain through connection_to_previous why it follows the prior step. Build the
  progression around the actual structure of the source: foundations and
  transformations for processes, central ideas and relationships for conceptual
  material, or items and important dimensions for comparisons. Do not merely copy
  Key Concepts in arbitrary order. Consider Quick Summary, Key Concepts,
  Relationships, Visual Flow, Concept Map, Comparison, Visual Evidence, and source
  structure together. Prefer 3 checkpoint questions that test understanding of the
  supplied material through concepts, relationships or processes, and application.
  Each question should have exactly 4 plausible options with unique ids, and
  correct_option_id must exactly match one option id. Avoid trivia and trick
  questions. Each question should use related_step_ids to identify one or more
  exact step ids that teach the knowledge it checks. Step and question source_pages
  may contain only [Page X] markers, or [] for pasted text or unclear support.
  Each step's visual_refs must link only relevant elements of the selected primary
  visualization using their exact canonical ids: type visual_flow_node for flow
  nodes, concept_map_node for concept map nodes, or comparison_item for comparison
  items. Do not infer ids from labels. Return [] when no direct link is supported
  or the primary visualization is none. Do not force supporting definitions into
  the visualization.
  Never invent pages. If a useful lesson cannot be formed, set suitable to false
  and return empty steps and questions.
- suggested_visualizations: choose zero or more types from the exact allowed list.
- learning_scene_candidate: decide whether the supplied material supports a finite,
  source-grounded probability/set Learning Scene. Set suitable true and domain
  probability_sets when the material defines or meaningfully connects a sample
  space or finite outcomes, events as sets, and probability/set operations such
  as union, intersection, complement, mutually exclusive events, De Morgan, or
  inclusion-exclusion. Do not require a staged experiment. Use suitable false and
  For source-supported quantitative physics/engineering with time evolution,
  vectors/positions/trajectories, and meaningful parameters/equations, set suitable
  true and domain spatial_dynamics. This may include rotating fields, harmonic
  motion, or projectile/orbital motion, not just one motor document. Prefer none
  for purely qualitative material with no defensible bounded numeric model.
  Use suitable false and domain none for unrelated material.
  The build remains a separate explicit action; this field only routes the UI.

The [Page X] markers are the only valid source of PDF page numbers.
Do not create rendered diagrams or 3D models in the response.
"""
            prompt += LAB_INSTRUCTIONS + "\n" + output_language_instruction(current_language())

            try:
                api_key = st.secrets["OPENAI_API_KEY"]
                client = OpenAI(api_key=api_key)
                try:
                    analysis_input = build_analysis_input(
                        client, source_text, uploaded_pdf if has_pdf else None
                    )
                except PdfVisualInputError:
                    st.error(
                        tr("We couldn’t send this PDF for visual analysis. Please try again with a valid PDF file.")
                    )
                    analysis_input = None

                if analysis_input is not None:
                    with st.spinner(tr("Analyzing your content…")):
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
                    analysis["analysis_language"] = current_language()
                    st.session_state["analysis_language"] = current_language()
                    st.session_state["analysis"] = analysis
                    ensure_canvas_state(
                        st.session_state["analysis_id"],
                        source_bytes if source_kind == "pdf" else None,
                    )
            except (KeyError, st.errors.StreamlitSecretNotFoundError):
                st.error(
                    tr("OpenAI API key is not configured yet. Add OPENAI_API_KEY to .streamlit/secrets.toml and try again.")
                )
            except json.JSONDecodeError:
                st.error(
                    tr("The analysis came back in an unexpected format. Please try again.")
                )
            except Exception:
                st.error(
                    tr("We couldn’t analyze that content right now. Check your API key and internet connection, then try again.")
                )

analysis = st.session_state.get("analysis")
if analysis:
    # Migrate a pre-Day-15 session once; subsequent UI switches cannot change it.
    if analysis.get("analysis_language") not in RESPONSE_LANGUAGES:
        analysis["analysis_language"] = (
            "zh-TW" if get_explanation_language(analysis) == "Traditional Chinese" else "en"
        )
    st.session_state["analysis_language"] = analysis["analysis_language"]
    if current_language() != analysis["analysis_language"]:
        st.info(tr("Generated content will use the selected language after your next analysis. Current explanations and reviews keep the active analysis language."))
    allowed_source_pages = st.session_state.get("allowed_source_pages", [])
    source_info = st.session_state.get("source_info")
    source_context = st.session_state.get("source_context", {})
    analysis_id = st.session_state.get("analysis_id", "current-analysis")
    relationships = clean_relationships(
        analysis.get("relationships", []), allowed_source_pages
    )
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
    selected_visualization = {
        "flow": visual_flow, "concept_map": concept_map, "comparison": comparison,
    }.get(primary_visualization["type"])
    learning_path = clean_learning_path(
        analysis.get("learning_path"), allowed_source_pages,
        primary_visualization["type"], selected_visualization,
    )
    if learning_path and learning_path["suitable"]:
        ensure_guided_learning_state(analysis_id, learning_path)
    interactive_lab = clean_interactive_lab(
        analysis.get("interactive_lab"), allowed_source_pages, learning_path, valid_source_pages,
    )
    ensure_lab_state(analysis_id, interactive_lab)
    try:
        ensure_simulation_state(analysis_id, interactive_lab, analysis, learning_path,
                                source_context, allowed_source_pages, valid_source_pages, MODEL)
    except Exception:
        reset_simulation_state()
        st.caption(tr("Dynamic simulations are unavailable for this context. Your experiment and lesson remain available."))
    from workspace.ui import render_navigation, render_focus, render_source_fallback
    from workspace.state import open_workspace
    from source_atlas.model import semantic_catalog
    from scene.compiler import ensure_scene_state, scene_domain
    workspace_state = render_navigation(analysis_id)
    mode = workspace_state["mode"]
    representation = "formal"
    wrapper = ensure_scene_state(analysis_id, analysis, scene_domain(analysis, source_context) or "probability_sets")
    catalog = semantic_catalog(wrapper.get("scene"), analysis)
    world_plan = None
    if mode == "explore":
        from learning_world.runtime import representation as render_representation
        representation, world_plan = render_representation(
            analysis, analysis_id, source_context, allowed_source_pages, MODEL,
            workspace_state, wrapper, interactive_lab)
    st.session_state["workspace_learning_path"] = learning_path
    def explain_source_region(region):
        target = dict(concept=region["label"], explanation=region["source_text_excerpt"][:1500],
                      source_pages=[region["page"]])
        context = build_explanation_context("key_concept", target, analysis, source_context, allowed_source_pages)
        from scene.state import fingerprint
        # An explicit Atlas rebuild may reuse region IDs for different content.
        identity = fingerprint(context)[:16]
        render_explain_action(f"{analysis_id}:source-region:{region['region_id']}:{identity}", context,
                              button_label=tr("Explain this source"))
    st.session_state["workspace_explain"] = explain_source_region
    # The slot updates after local render events, keeping focus metadata current.
    focus_slot = st.empty()
    source_bundle = None
    if mode == "source" or (mode == "explore" and representation == "formal"
                            and (not world_plan or world_plan["family"] not in ("static", "none"))):
        source_bundle = render_scene_builder(analysis, analysis_id, source_context, allowed_source_pages,
                                            MODEL, format_page_references, workspace_mode=mode)
    if mode == "source" and not source_bundle:
        render_source_fallback(analysis_id, source_context, allowed_source_pages, analysis)

    if mode == "learn":
        with st.container(border=True):
            st.markdown("### " + tr("Your learning snapshot"))
            if source_info:
                st.caption(
                    tr("PDF source: text found on {found} of {total} page(s); analyzed {analyzed} page(s).", found=source_info["found_count"], total=source_info["total_count"], analyzed=source_info["analyzed_count"])
                )

            st.markdown("#### " + tr("Quick Summary"))
            st.write(analysis.get("quick_summary", ""))

            st.markdown("#### " + tr("Key Concepts"))
            key_concepts = analysis.get("key_concepts", [])
            if not isinstance(key_concepts, list):
                key_concepts = []
            displayed_concept_count = 0
            for index, item in enumerate(key_concepts):
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
                st.markdown(f"- **{concept}**{description}")
                if pages:
                    st.caption(tr("Source: {pages}", pages=format_page_references(pages)))
                concept_target = {
                    "concept": concept,
                    "explanation": explanation,
                    "source_pages": pages,
                }
                explanation_context = build_explanation_context(
                    "key_concept",
                    concept_target,
                    analysis,
                    source_context,
                    allowed_source_pages,
                )
                render_explain_action(
                    f"{analysis_id}:key-concept:{index}", explanation_context
                )
                displayed_concept_count += 1

            if not displayed_concept_count:
                st.caption(tr("No key concepts were returned for this content."))

            with st.expander(tr("Visual Evidence"), expanded=False):
                st.markdown("#### " + tr("Visual Evidence"))
                visual_evidence = clean_visual_evidence(
                    analysis.get("visual_evidence", []), allowed_source_pages
                )
                if visual_evidence:
                    for index, item in enumerate(visual_evidence):
                        st.markdown(
                            tr("{kind} — Page {page}", kind=tr(item["type"]).capitalize(), page=item["page"])
                        )
                        st.write(item["description"])
                        st.markdown(tr("Learning value:"))
                        st.write(item["learning_value"])
                        explanation_context = build_explanation_context(
                            "visual_evidence",
                            item,
                            analysis,
                            source_context,
                            allowed_source_pages,
                        )
                        render_explain_action(
                            f"{analysis_id}:visual-evidence:{index}", explanation_context
                        )
                else:
                    st.caption(tr("No meaningful visual evidence was found in this content."))

            relationship_lines = []
            for item in relationships:
                relationship_lines.append(
                    f"- **{item['source']}** — *{item['relation']}* → **{item['target']}**"
                )
                if item["source_pages"]:
                    relationship_lines.append(
                        "  - " + tr("Source: {pages}", pages=format_page_references(item["source_pages"]))
                    )

            with st.expander(tr("Relationships"), expanded=False):
                if relationship_lines:
                    st.markdown("\n".join(relationship_lines))
                else:
                    st.caption(tr("No explicit relationships were found in this content."))
        st.button(tr("Continue with guided practice"), key="workspace-next-practice",
                  on_click=open_workspace, args=(workspace_state, "practice"))

    if mode == "explore" and representation == "process":
        from learning_world.runtime import render_process
        render_process(world_plan, analysis_id, workspace_state, wrapper, analysis, allowed_source_pages)

    if mode == "explore" and representation in ("analogy", "compare"):
        from analogy.runtime import render as render_analogy
        render_analogy(analysis, analysis_id, source_context, allowed_source_pages, MODEL,
                       workspace_state, wrapper, interactive_lab, learning_path,
                       st.session_state["interactive_lab_state"], compare=representation == "compare")

    if mode == "explore" and representation == "formal" and world_plan and world_plan["family"] == "none":
        st.write(analysis.get("quick_summary", ""))

    if mode == "explore" and representation == "formal" and (not world_plan or world_plan["family"] != "none"):
        with st.expander(tr("Suggested Visualization")):
            suggestions = analysis.get("suggested_visualizations", [])
            if isinstance(suggestions, list):
                st.caption(", ".join(tr(value) for value in suggestions if isinstance(value, str)))
        selection_reason = primary_visualization["reason"]

        if primary_visualization["type"] == "flow":
            st.markdown("### " + tr("Visual Flow"))
            if not visual_flow or not visual_flow["suitable"]:
                st.info(
                    tr("The selected Visual Flow could not be rendered because its structured data was incomplete.")
                )
            if selection_reason:
                st.caption(selection_reason)
        elif primary_visualization["type"] == "concept_map":
            st.markdown("### " + tr("Concept Map"))
            if not concept_map or not concept_map["suitable"]:
                st.info(
                    tr("The selected Concept Map could not be rendered because its structured data was incomplete.")
                )
            if selection_reason:
                st.caption(selection_reason)
        elif primary_visualization["type"] == "comparison":
            st.markdown("### " + tr("Comparison"))
            comparison_rows = build_comparison_table(comparison)
            if comparison_rows:
                st.markdown(f"#### {comparison['title']}")
                st.table(comparison_rows)
                st.markdown("**" + tr("Takeaway") + "**")
                st.write(comparison["takeaway"])
            else:
                st.info(
                    tr("The selected Comparison could not be rendered because its structured data was incomplete.")
                )
            if selection_reason:
                st.caption(selection_reason)
        else:
            st.markdown("### " + tr("Primary Visualization"))
            st.info(
                tr("No strong primary visualization was detected for this material.")
            )
            if selection_reason:
                st.caption(selection_reason)

        if primary_visualization["type"] != "none":
            render_learning_canvas(
                primary_visualization["type"], selected_visualization, learning_path,
                analysis, source_context, allowed_source_pages, analysis_id,
                build_flow_graph if primary_visualization["type"] == "flow" else build_concept_map_graph,
                build_explanation_context, render_explain_action, format_page_references,
                interactive_lab,
            )

        if not world_plan or world_plan["family"] not in ("static", "none"):
            render_interactive_lab(interactive_lab, analysis_id, learning_path, go_to_lesson, format_page_references)
            render_simulation_studio(interactive_lab, analysis_id, learning_path, go_to_lesson, format_page_references)

    if mode == "explore":
        from learning_world.runtime import render_diagnostics
        render_diagnostics(analysis_id)

    if mode == "practice":
        render_guided_learning(
            learning_path,
            analysis,
            primary_visualization,
            source_context,
            allowed_source_pages,
            analysis_id,
            interactive_lab,
        )
    with focus_slot.container():
        catalog = semantic_catalog(wrapper.get("scene"), analysis)
        render_focus(workspace_state, catalog, wrapper, allowed_source_pages)

render_footer()
