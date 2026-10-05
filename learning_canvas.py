"""Read-only learning canvas. All navigation here is local; explanation is explicit."""

import html
import time

import streamlit as st

from i18n import FONT_STACK, tr
from interactive_lab import render_lab_links

from source_lens import new_source_state, render_source_lens

try:
    from streamlit_flow import streamlit_flow
    from streamlit_flow.elements import StreamlitFlowEdge, StreamlitFlowNode
    from streamlit_flow.layouts import LayeredLayout
    from streamlit_flow.state import StreamlitFlowState
except Exception:
    # Import/asset failures must not take away the existing Graphviz experience.
    streamlit_flow = None

VISUAL_TARGETS = {
    "flow": "visual_flow_node",
    "concept_map": "concept_map_node",
    "comparison": "comparison_item",
}
VISUAL_REF_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "type": {"type": "string", "enum": list(VISUAL_TARGETS.values())},
            "id": {"type": "string"},
        },
        "required": ["type", "id"],
        "additionalProperties": False,
    },
}


def visual_targets(visualization):
    if not visualization or not visualization.get("suitable"):
        return {}
    return {item["id"]: item for item in visualization.get("items", visualization.get("nodes", []))}


def clean_visual_refs(raw_refs, visualization_type, visualization):
    """Bad links are discarded independently of the lesson that contains them."""
    expected_type = VISUAL_TARGETS.get(visualization_type)
    ids = visual_targets(visualization)
    cleaned = []
    seen = set()
    if isinstance(raw_refs, list):
        for ref in raw_refs:
            if not isinstance(ref, dict):
                continue
            ref_id = ref.get("id")
            if (expected_type and ref.get("type") == expected_type
                    and isinstance(ref_id, str) and ref_id in ids and ref_id not in seen):
                cleaned.append({"type": expected_type, "id": ref_id})
                seen.add(ref_id)
    return cleaned


def reset_canvas_state():
    st.session_state.pop("learning_canvas", None)
    for key in list(st.session_state):
        if isinstance(key, str) and key.startswith(("canvas-widget-", "canvas-list-")):
            st.session_state.pop(key, None)


def ensure_canvas_state(material_id, pdf_bytes=None):
    state = st.session_state.get("learning_canvas")
    if not isinstance(state, dict) or state.get("material_id") != material_id:
        reset_canvas_state()
        state = {
            "material_id": material_id,
            "selected_id": None,
            "kind": None,
            "component": None,
            "style_signature": None,
            "last_event": -1,
            "fallback": False,
            "component_error": False,
            "source": new_source_state(material_id, pdf_bytes),
        }
        st.session_state["learning_canvas"] = state
    return state


def select_target(state, target_id, visualization):
    """Accept only stable IDs from the canonical analysis; preserve all lesson state."""
    if not isinstance(target_id, str) or target_id not in visual_targets(visualization):
        return False
    if target_id == state["selected_id"]:
        return False
    state["selected_id"] = target_id
    workspace = st.session_state.get("learning_workspace")
    wrapper = st.session_state.get("learning_scene_state")
    if workspace and workspace["material_id"] == state["material_id"]:
        from workspace.state import set_workspace_focus
        from source_atlas.model import semantic_catalog
        catalog = semantic_catalog((wrapper or {}).get("scene"), st.session_state.get("analysis"))
        set_workspace_focus(workspace, target_id, catalog, wrapper)
    state["source"]["view"].update(target=None, open=False, page=None)
    return True


def related_lessons(learning_path, target_type, target_id):
    return [(number, step) for number, step in enumerate((learning_path or {}).get("steps", []), 1)
            if {"type": target_type, "id": target_id} in step.get("visual_refs", [])]


def go_to_lesson(step_id, learning_path):
    if any(step["id"] == step_id for step in (learning_path or {}).get("steps", [])):
        from workspace.state import open_workspace
        workspace = st.session_state.get("learning_workspace")
        if workspace: open_workspace(workspace, "practice")
        st.session_state["guided_learning_started"] = True
        st.session_state["guided_learning_step_id"] = step_id
        return True
    return False


def canvas_highlights(learning_path, material_id):
    """Derive emphasis from actual checked answers and the current focused review."""
    lesson_ids, review_ids = set(), set()
    if st.session_state.get("guided_learning_material_id") != material_id:
        return lesson_ids, review_ids
    path = learning_path or {}
    steps = path.get("steps", [])
    if st.session_state.get("guided_learning_started"):
        active_step = st.session_state.get("guided_learning_step_id")
        lesson_ids = {ref["id"] for step in steps if step["id"] == active_step for ref in step.get("visual_refs", [])}
    answers = st.session_state.get("guided_quiz_answers", {})
    checked = st.session_state.get("guided_quiz_checked", {})
    wrong_questions = [q for q in path.get("checkpoint_questions", [])
                       if checked.get(q["id"]) and q["id"] in answers and answers[q["id"]] != q["correct_option_id"]]
    review_steps = {step_id for question in wrong_questions for step_id in question["related_step_ids"]}
    adaptive = st.session_state.get("adaptive_review_state", {})
    if wrong_questions and adaptive.get("material_id") == material_id:
        for item in (adaptive.get("focused_review") or {}).get("items", []):
            review_steps.update(item.get("related_step_ids", []))
    review_ids = {ref["id"] for step in steps if step["id"] in review_steps for ref in step.get("visual_refs", [])}
    return lesson_ids, review_ids


def node_visual_state(node_id, selected_id, lesson_ids, review_ids):
    """Priority: manual selection > needs review > current lesson > default.

    Other applicable states remain visible as text badges in the inspector.
    Lesson/review navigation never overwrites a manual selection.
    """
    if node_id == selected_id:
        return "selected"
    if node_id in review_ids:
        return "review"
    if node_id in lesson_ids:
        return "lesson"
    return "default"


def node_style(role, visual_state):
    style = {
        "width": 200, "padding": "10px 14px", "borderRadius": "12px",
        "fontSize": "16px", "fontFamily": FONT_STACK, "fontWeight": "500", "lineHeight": "1.55", "color": "#30264D",
        "whiteSpace": "normal", "overflowWrap": "anywhere",
        "background": "#FFFFFF", "border": "1px solid #B7ACEE",
    }
    if role == "central":
        style.update(background="#EEE8FF", fontWeight="700", border="2px solid #8270DF")
    elif role == "primary":
        style.update(background="#F7F4FF", fontWeight="600")
    if visual_state == "selected":
        style.update(background="#6750C5", color="#FFFFFF", border="3px solid #493397", boxShadow="0 0 0 3px #E5DCFF")
    elif visual_state == "review":
        style.update(background="#FFF8EB", border="2px dashed #987135")
    elif visual_state == "lesson":
        style.update(background="#EEE8FF", border="2px solid #8270DF")
    return style


def build_component_state(kind, visualization):
    """Convert canonical data once. UI state never becomes analysis data."""
    vertical = kind == "flow"
    nodes = [StreamlitFlowNode(
        id=node["id"], pos=(0, 0),
        # Component supports raw HTML: escape every model-provided label.
        data={"content": f'<div>{html.escape(node["label"])}</div>'},
        source_position="bottom" if vertical else "right",
        target_position="top" if vertical else "left",
        draggable=False, connectable=False, deletable=False, selectable=True,
        style=node_style(node.get("role"), "default"),
    ) for node in visualization["nodes"]]
    edges = [StreamlitFlowEdge(
        id=f"edge-{index}", source=edge["source"], target=edge["target"],
        label=edge["label"], edge_type="smoothstep" if vertical else "default",
        marker_end={"type": "arrowclosed", "color": "#8270DF"} if vertical else {},
        animated=False, deletable=False, focusable=False,
        label_show_bg=True, label_bg_style={"fill": "#FFFFFF"},
        label_style={"fontSize": 14, "fontFamily": FONT_STACK, "fontWeight": 500, "fill": "#392E58"}, style={"stroke": "#8270DF"},
    ) for index, edge in enumerate(visualization["edges"])]
    return StreamlitFlowState(nodes, edges)


def sync_component_styles(state, visualization, lesson_ids, review_ids):
    """Only advance the component revision for a real presentation change."""
    signature = tuple((node["id"], node_visual_state(node["id"], state["selected_id"], lesson_ids, review_ids)) for node in visualization["nodes"])
    if signature == state["style_signature"]:
        return
    canonical = visual_targets(visualization)
    component = state["component"]
    for node, (_, visual_state) in zip(component.nodes, signature):
        node.style = node_style(canonical[node.id].get("role"), visual_state)
        node.selected = node.id == state["selected_id"]
    state["style_signature"] = signature
    component.timestamp = max(component.timestamp + 1, int(time.time() * 1000))


def accept_component_event(state, returned, visualization):
    """Reject semantic mutations and stale replies; retain frontend layout state."""
    current = state["component"]
    if returned.timestamp < current.timestamp:
        return False
    expected_nodes = [node.id for node in current.nodes]
    expected_edges = [(edge.id, edge.source, edge.target, edge.label) for edge in current.edges]
    if ([node.id for node in returned.nodes] != expected_nodes or
            [(edge.id, edge.source, edge.target, edge.label) for edge in returned.edges] != expected_edges):
        raise ValueError("The component returned an edited graph.")
    # Even unexpected frontend label/flag edits cannot become semantic data.
    for node, original in zip(returned.nodes, current.nodes):
        node.data = original.data
        node.draggable = node.connectable = node.deletable = False
    for edge in returned.edges:
        edge.deletable = False
    state["component"] = returned
    if returned.timestamp <= state["last_event"]:
        return False
    state["last_event"] = returned.timestamp
    # The component sends null for layout acknowledgements and pane clicks.
    # Neither should clear the learner's selection.
    return select_target(state, returned.selected_id, visualization)


def render_graph(kind, visualization, state, lesson_ids, review_ids, graph_builder):
    """Interactive renderer with automatic server fallback and a manual escape hatch."""
    if not state["fallback"] and streamlit_flow is not None:
        st.caption(tr("Click a node to explore · Pan and zoom to navigate"))
        try:
            if state["component"] is None:
                state["component"] = build_component_state(kind, visualization)
            sync_component_styles(state, visualization, lesson_ids, review_ids)
            returned = streamlit_flow(
                f"canvas-widget-{state['material_id']}-{kind}", state["component"],
                height=520, layout=LayeredLayout("down" if kind == "flow" else "right", node_node_spacing=35, node_layer_spacing=80),
                fit_view=True, show_controls=True, show_minimap=False,
                get_node_on_click=True, get_edge_on_click=False,
                allow_new_edges=False, animate_new_edges=False,
                pan_on_drag=True, allow_zoom=True, min_zoom=0.15,
                enable_pane_menu=False, enable_node_menu=False, enable_edge_menu=False,
                style={"backgroundColor": "#FCFAFF", "borderRadius": "12px", "border": "1px solid #E5DFF4"},
            )
            changed = accept_component_event(state, returned, visualization)
        except Exception:
            state["fallback"] = True
            state["component_error"] = True
        else:
            if changed:
                # One local rerun applies selection styling. Stable acknowledgements
                # do not rerun again; never recreate StreamlitFlowState here.
                st.rerun()
            return
    else:
        state["fallback"] = True
    if state["component_error"] or streamlit_flow is None:
        st.caption(tr("The interactive canvas is unavailable. Showing the Graphviz view."))
    graph = graph_builder(visualization)
    if graph:
        st.graphviz_chart(graph.source, use_container_width=True)


def select_from_list(state, visualization, widget_key):
    select_target(state, st.session_state.get(widget_key), visualization)


def render_selection_controls(kind, visualization, state, lesson_ids, review_ids):
    targets = visual_targets(visualization)
    if kind == "comparison":
        columns = st.columns(len(targets))
        for column, (target_id, target) in zip(columns, targets.items()):
            status = node_visual_state(target_id, state["selected_id"], lesson_ids, review_ids)
            with column:
                if st.button(target["label"], key=f"canvas-item-{state['material_id']}-{target_id}", type="primary" if status == "selected" else "secondary", use_container_width=True):
                    select_target(state, target_id, visualization)
                    st.rerun()
                if target_id in review_ids:
                    st.caption(tr("Needs review"))
                if target_id in lesson_ids:
                    st.caption(tr("Current lesson"))
    with st.expander(tr("Explore this visualization · Choose from list instead"), expanded=state["fallback"]):
        list_key = f"canvas-list-{state['material_id']}-{kind}"
        # Sync before widget creation, so graph clicks and keyboard selection agree.
        st.session_state[list_key] = state["selected_id"]
        st.selectbox(tr("Choose a learning item"), options=list(targets), index=None, format_func=lambda item_id: targets[item_id]["label"], key=list_key,
                     on_change=select_from_list, args=(state, visualization, list_key))
        if kind != "comparison":
            if st.button(tr("Use Graphviz view") if not state["fallback"] else tr("Try interactive view"), key=f"canvas-renderer-{state['material_id']}"):
                state["fallback"] = not state["fallback"]
                state["component_error"] = False
                st.rerun()
        if state["selected_id"] is not None and st.button(tr("Clear selection"), key=f"canvas-clear-{state['material_id']}"):
            workspace = st.session_state.get("learning_workspace")
            if workspace and workspace["material_id"] == state["material_id"]:
                from workspace.state import clear_workspace_focus
                clear_workspace_focus(workspace, st.session_state.get("learning_scene_state"))
            state["selected_id"] = None
            state["source"]["view"].update(target=None, open=False, page=None)
            st.rerun()


def render_learning_inspector(kind, visualization, state, learning_path, analysis, source_context, allowed_pages, build_context, explain_action, format_pages, interactive_lab=None):
    target = visual_targets(visualization).get(state["selected_id"])
    st.markdown("### " + tr("Learning Inspector"))
    if target is None:
        st.caption(tr("Select a concept, step, or comparison item to explore its context and source."))
        return
    target_type = VISUAL_TARGETS[kind]
    context = build_context(target_type, target, analysis, source_context, allowed_pages, visualization=visualization)
    if context is None:
        st.caption(tr("This learning item is no longer available."))
        return
    pages = context["relevant_pages"]
    nearby = context["visualization_context"]
    with st.container(border=True):
        st.markdown(f"#### {target['label']}")
        lesson_ids, review_ids = canvas_highlights(learning_path, state["material_id"])
        badges = []
        if target["id"] in review_ids:
            badges.append(tr("Needs review"))
        if target["id"] in lesson_ids:
            badges.append(tr("Current lesson"))
        if kind == "concept_map":
            badges.append(tr("Role: {role}", role=tr(target["role"])))
        if badges:
            st.caption(" · ".join(badges))
        st.markdown("**" + tr("Context") + "**")
        if kind == "comparison":
            for value in nearby["criteria_and_values"]:
                st.write(f"{value['criterion']}: {value['value']}")
            st.caption(tr("Takeaway: {text}", text=nearby["takeaway"]))
        else:
            st.caption(tr("Connected steps") if kind == "flow" else tr("Connected to"))
            for edge in nearby["connected_relationships"]:
                prefix = f"{tr(edge['position']).capitalize()} · " if "position" in edge else ""
                st.write(f"{prefix}{edge['source']} — {edge['relation']} → {edge['target']}")
        st.caption(tr("Source: {pages}", pages=format_pages(pages)) if pages else tr("Source: pasted text") if source_context.get("kind") != "pdf" else tr("Source: no validated page reference"))
        lessons = related_lessons(learning_path, target_type, target["id"])
        for number, step in lessons:
            st.markdown("**" + tr("Related lesson: Step {number} — {title}", number=number, title=step["title"]) + "**")
            st.write(step["learning_goal"])
            if st.button(tr("Go to lesson step"), key=f"canvas-lesson-{state['material_id']}-{target['id']}-{step['id']}"):
                go_to_lesson(step["id"], learning_path)
                st.rerun()
        if not lessons:
            st.caption(tr("No lesson step is linked to this item."))
        render_lab_links(interactive_lab, [step["id"] for _, step in lessons], state["material_id"], f"inspector-{target['id']}")
        explain_action(f"{state['material_id']}:{target_type}:{target['id']}", context)
        render_source_lens(state["source"], state["material_id"], f"{target_type}:{target['id']}", target["label"], pages, source_context, allowed_pages, analysis.get("visual_evidence", []))


def render_learning_canvas(kind, visualization, learning_path, analysis, source_context, allowed_pages, analysis_id, graph_builder, build_context, explain_action, format_pages, interactive_lab=None):
    """Render the current primary visualization and a single shared inspector."""
    if not visual_targets(visualization):
        st.caption(tr("No visualization elements are available to explore."))
        return
    state = ensure_canvas_state(analysis_id)
    if state["kind"] != kind:
        state.update(kind=kind, selected_id=None, component=None, style_signature=None, last_event=-1)
    workspace = st.session_state.get("learning_workspace")
    if workspace and workspace["material_id"] == analysis_id:
        from workspace.state import get_workspace_focus
        focus = get_workspace_focus(workspace, st.session_state.get("learning_scene_state"))
        if focus in visual_targets(visualization): state["selected_id"] = focus
    if state["selected_id"] not in visual_targets(visualization):
        state["selected_id"] = None
    lesson_ids, review_ids = canvas_highlights(learning_path, analysis_id)
    if kind != "comparison":
        render_graph(kind, visualization, state, lesson_ids, review_ids, graph_builder)
        if state["fallback"]:
            st.caption(tr("Choose an item from the list below to explore this view."))
        else:
            st.caption(tr("Solid purple: selected · Dashed amber: needs review · Light purple: current lesson"))
    render_selection_controls(kind, visualization, state, lesson_ids, review_ids)
    render_learning_inspector(kind, visualization, state, learning_path, analysis, source_context, allowed_pages, build_context, explain_action, format_pages, interactive_lab)
