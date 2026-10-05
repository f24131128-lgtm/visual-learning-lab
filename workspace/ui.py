"""Conditional navigation and compact source actions; no compiler calls."""
import streamlit as st
from i18n import tr
from source_atlas.model import anchors
from source_atlas.state import sync_region
from .state import (MODES, actions, clear_workspace_focus, get_workspace_focus,
                    get_workspace_state, open_workspace)

LABELS = {"learn": "Learn", "source": "Source", "explore": "Explore", "practice": "Practice"}


def render_navigation(material_id):
    state = get_workspace_state(material_id)
    key = "workspace-mode-"+material_id
    st.session_state[key] = state["mode"]
    labels = {mode: tr(label) for mode, label in LABELS.items()}
    st.radio(tr("Learning Workspace"), MODES, key=key, horizontal=True,
             format_func=lambda m, names=labels: names[m],
             on_change=lambda: open_workspace(state, st.session_state[key]))
    return state


def render_focus(state, catalog, wrapper, allowed):
    focus = get_workspace_focus(state, wrapper)
    item = catalog.get(focus)
    left, right = st.columns([5, 1])
    with left:
        name = item["label"] if item else tr("Choose a concept or source object")
        details = []
        if item:
            pages = item["pages"]
            atlas_state = st.session_state.get("source_atlas_state", {})
            atlas = atlas_state.get("atlas")
            formula = None
            if atlas and atlas_state.get("key", [None])[0] == state["material_id"]:
                matches = anchors(atlas, focus)
                if matches: pages = list(dict.fromkeys(r["page"] for r in matches))
                label = next((r for r in matches if r["region_id"] == atlas_state.get("region_hint") and r["type"] == "label"), None)
                if label: name = label["label"]
                formula = next((r for r in matches if r["type"] == "formula" and r.get("source_text_excerpt") and r["excerpt_verified"]), None)
            details = [tr("Page {page}", page=p) for p in pages if p in allowed][:3]
            if formula: details.append(formula["source_text_excerpt"][:160])
        st.text(tr("Current focus: {name}", name=name))
        if details: st.caption(" · ".join(details))
    with right:
        if item: st.button(tr("Clear focus"), key="workspace-clear", on_click=clear_workspace_focus, args=(state, wrapper))


def render_source_actions(bundle):
    state = st.session_state.get("learning_workspace")
    if not state or state["material_id"] != bundle["material_id"]: return
    wrapper, catalog = bundle.get("wrapper"), bundle["catalog"]
    region = sync_region(bundle["state"], get_workspace_focus(state, wrapper))
    plans = st.session_state.get("learning_world_plans", {})
    plan = plans.get("cache", {}).get(plans.get("active")) if plans.get("material") == state["material_id"] else None
    process_ids = plan["focus_ids"] if plan and plan["family"] == "process" else []
    supported = actions(region, catalog, wrapper, st.session_state.get("workspace_learning_path"), process_ids)
    prefix = "workspace-action-"+bundle["material_id"]
    if "explore" in supported:
        chosen = get_workspace_focus(state, wrapper)
        if chosen not in supported["explore"]: chosen = supported["explore"][0]
        st.button(tr("Explore in interactive scene"), key=prefix+"-explore", on_click=open_workspace,
                  args=(state, "explore", chosen, catalog, wrapper))
    if "formula" in supported:
        def reveal_formula():
            matches = anchors(bundle["state"]["atlas"], get_workspace_focus(state, wrapper))
            formula = next((r for r in matches if r["type"] == "formula"), None)
            if formula:
                from source_atlas.state import select_region
                select_region(bundle["state"], formula["region_id"], catalog, wrapper)
            open_workspace(state, "source")
        if any(r["type"] == "formula" for r in anchors(bundle["state"]["atlas"], get_workspace_focus(state, wrapper))):
            st.button(tr("View related formula"), key=prefix+"-formula", on_click=reveal_formula)
    if "practice" in supported:
        def practice():
            from learning_canvas import go_to_lesson
            go_to_lesson(supported["practice"][0], st.session_state["workspace_learning_path"])
            open_workspace(state, "practice")
        st.button(tr("Practice this concept"), key=prefix+"-practice", on_click=practice)
    explain = st.session_state.get("workspace_explain")
    if "explain" in supported and explain: explain(region)


def render_source_fallback(material_id, source_context, allowed, analysis):
    from source_atlas.compiler import source_for
    from source_lens import render_source_lens
    if source_context.get("kind") != "pdf":
        st.text(source_context.get("source_text", "")[:18000] or tr("No source context is available."))
        return
    source = source_for(material_id)
    if source:
        if source["view"]["target"] != "workspace-source":
            source["view"].update(target="workspace-source", open=True, page=None)
        render_source_lens(source, material_id, "workspace-source", "", allowed,
                           source_context, allowed, analysis.get("visual_evidence", []))
    elif source_context.get("source_text"):
        st.text(source_context["source_text"][:18000])
    else:
        texts = source_context.get("page_texts")
        available = [(page, texts.get(page)) for page in allowed] if isinstance(texts, dict) else []
        shown = False
        for page, text in available[:8]:
            if isinstance(text, str) and text:
                st.caption(tr("Page {page}", page=page))
                st.text(text[:1800])
                shown = True
        if not shown: st.caption(tr("No source context is available."))
