"""One navigation contract; scene reducers remain the semantic authority."""
import streamlit as st
from source_atlas.state import current_focus, optional_scene, set_focus

MODES = ("learn", "source", "explore", "practice")


def get_workspace_state(material_id):
    state = st.session_state.get("learning_workspace")
    if not isinstance(state, dict) or state.get("material_id") != material_id:
        state = dict(material_id=material_id, mode="learn", focus=None)
        st.session_state["learning_workspace"] = state
    return state


def get_workspace_focus(state, wrapper=None):
    # Never mirror scene focus: replay, world and source use the same reducer.
    if optional_scene(wrapper):
        return current_focus(wrapper)
    return state["focus"]


def set_workspace_focus(state, identifier, catalog, wrapper=None):
    if not isinstance(identifier, str) or identifier not in catalog: return False
    if isinstance(wrapper, dict) and wrapper.get("material_id") != state["material_id"]: return False
    if optional_scene(wrapper):
        if not set_focus(wrapper, identifier, catalog): return False
    else:
        state["focus"] = identifier
    return True


def clear_workspace_focus(state, wrapper=None):
    canvas = st.session_state.get("learning_canvas")
    if isinstance(canvas, dict) and canvas.get("material_id") == state["material_id"]:
        canvas["selected_id"] = None
    scene = optional_scene(wrapper)
    if scene and scene["domain"] == "spatial_dynamics":
        from scene.world.state import clear_focus, new_state
        clear_focus(wrapper.setdefault("world", new_state(scene)))
    elif scene:
        event = scene["events"][0]["id"]
        wrapper.update(selected_outcome_id=None, active_expression=f"{event} - {event}", selected_focus_id="workspace_empty", lens="explore")
        st.session_state.pop("scene-widget-focus-"+wrapper["material_id"], None)
    state["focus"] = None


def open_workspace(state, mode, semantic_focus=None, catalog=None, wrapper=None):
    if mode not in MODES: return False
    if semantic_focus is not None and not set_workspace_focus(state, semantic_focus, catalog or {}, wrapper): return False
    state["mode"] = mode
    return True


def focusable(identifier, catalog, wrapper=None):
    if identifier not in catalog: return False
    scene = optional_scene(wrapper)
    if scene and scene["domain"] == "spatial_dynamics":
        return identifier in {q["id"] for q in scene["quantities"]}
    return catalog[identifier]["kind"] not in ("parameter", "time")


def actions(region, catalog, wrapper=None, learning_path=None, process_ids=None):
    if not region: return {}
    links = [i for i in region["semantic_ids"] if focusable(i, catalog, wrapper)]
    result = {}
    exploration = links if optional_scene(wrapper) else [i for i in links if i in (process_ids or ())]
    if exploration: result["explore"] = exploration
    if region.get("source_text_excerpt") or links: result["explain"] = True
    if any(catalog[i].get("equation") for i in links): result["formula"] = links
    # Whole-scene lesson links are not individual concept targeting.
    steps = [s["id"] for s in (learning_path or {}).get("steps", [])
             if any(r.get("id") in links for r in s.get("visual_refs", []))]
    if steps: result["practice"] = steps
    return result
