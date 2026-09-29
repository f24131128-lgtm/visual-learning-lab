"""Offline fixtures and helpers; never part of the running application."""

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_app_helpers():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8-sig"))
    body = []
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "set_page_config":
            break
        body.append(node)
    namespace = {"__name__": "app_helpers", "__file__": str(ROOT / "app.py")}
    exec(compile(ast.Module(body=body, type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


def fixture(kind="concept_map"):
    target_type = {"concept_map": "concept_map_node", "flow": "visual_flow_node", "comparison": "comparison_item"}[kind]
    nodes = [
        {"id": "input", "label": "Incoming material", "source_pages": [1], "role": "central"},
        {"id": "transform", "label": "Material transformation", "source_pages": [1, 2], "role": "primary"},
        {"id": "output", "label": "Resulting material", "source_pages": [2], "role": "supporting"},
    ]
    edges = [
        {"source": "input", "target": "transform", "label": "processed by"},
        {"source": "transform", "target": "output", "label": "produces"},
    ]
    graph = {"suitable": True, "reason": "Study the main structure.", "nodes": nodes, "edges": edges}
    comparison = {
        "suitable": True, "reason": "Compare the alternatives.", "title": "Material choices",
        "items": [{"id": n["id"], "label": n["label"]} for n in nodes],
        "criteria": [{"criterion": "Role", "values": [
            {"item_id": n["id"], "value": n["label"], "source_pages": n["source_pages"]} for n in nodes]}],
        "takeaway": "Different items have different roles.",
    }
    questions = [{
        "id": f"q{i}", "question": f"Which description fits stage {i}?",
        "options": [{"id": letter, "text": f"Choice {letter}"} for letter in "abcd"],
        "correct_option_id": "a", "explanation": "Choice a follows the source.",
        "source_pages": [1 if i < 3 else 2], "related_step_ids": [f"s{i}"],
    } for i in range(1, 4)]
    path = {
        "suitable": True, "title": "Follow the material", "reason": "Three useful stages.",
        "steps": [{
            "id": f"s{i}", "title": n["label"], "learning_goal": "Understand this stage.",
            "explanation": "This stage has a distinct role in the process.",
            "source_pages": n["source_pages"], "connection_to_previous": "Build on the previous stage.",
            "visual_refs": [{"type": target_type, "id": n["id"]}],
        } for i, n in enumerate(nodes, 1)], "checkpoint_questions": questions,
    }
    return {
        "quick_summary": "Material is transformed into a useful result.",
        "key_concepts": [{"concept": n["label"], "explanation": "A source-grounded concept.", "source_pages": n["source_pages"]} for n in nodes],
        "relationships": [{"source": "Incoming material", "relation": "undergoes", "target": "Material transformation", "source_pages": [1]}],
        "visual_evidence": [{"page": 1, "type": "diagram", "description": "A material process diagram.", "learning_value": "Shows the transformation."}],
        "primary_visualization": {"type": kind, "reason": "This view fits the learning structure."},
        "visual_flow": graph if kind == "flow" else {"suitable": False, "reason": "", "nodes": [], "edges": []},
        "concept_map": graph if kind == "concept_map" else {"suitable": False, "reason": "", "nodes": [], "edges": []},
        "comparison": comparison if kind == "comparison" else {"suitable": False, "reason": "", "title": "", "items": [], "criteria": [], "takeaway": ""},
        "learning_path": path, "suggested_visualizations": ["Concept Map" if kind == "concept_map" else "Flow" if kind == "flow" else "Comparison"],
        "interactive_lab": {"suitable": False, "reason": "No mathematical experiment is supported.", "demos": []},
    }


def focused_fixture():
    return {
        "review_title": "Revisit the transformation", "review_summary": "Distinguish input from output.",
        "source_note": "PDF p.1 · Based on supplied context.",
        "items": [{"id": "review1", "related_step_ids": ["s2"], "what_to_fix": "The role of the transformation.",
                   "focused_explanation": "Input passes through this stage.", "intuition_or_example": "", "source_pages": [1]}],
        "retry_questions": [{"id": "retry1", "question": "Which step transforms the input?",
                             "options": [{"id": letter, "text": f"Option {letter}"} for letter in "abcd"],
                             "correct_option_id": "b", "explanation": "The middle stage transforms input.", "related_step_ids": ["s2"], "source_pages": [1]}],
    }


def sample_pdf():
    import pymupdf
    with pymupdf.open() as doc:
        page = doc.new_page()
        page.insert_text((60, 80), "Incoming material enters the process.")
        page.insert_text((60, 110), "Material transformation creates a useful result.")
        page.draw_rect(pymupdf.Rect(60, 145, 240, 200), color=(0.4, 0.3, 0.8))
        page = doc.new_page()
        page.insert_text((60, 80), "Resulting material is the output.")
        page = doc.new_page()  # A sparse analyzed page for Source Lens unit tests.
        page.draw_circle((120, 120), 40)
        return doc.tobytes()


def source_fixture():
    return {"kind": "pdf", "source_text": "", "page_texts": {
        1: "Incoming material enters the process.\nMaterial transformation creates a useful result.",
        2: "Resulting material is the output.",
    }}
