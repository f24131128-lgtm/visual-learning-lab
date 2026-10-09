"""Source selection is a navigation hint, never a second semantic focus."""

import hashlib

import streamlit as st

from scene.state import fingerprint
from .model import anchors, semantic_fingerprint
from .schema import VERSION


def cache_key(material_id, pdf_bytes, language, pages, scene, catalog):
    return (material_id, hashlib.sha256(pdf_bytes).hexdigest(), language, VERSION,
            tuple(sorted(pages)), semantic_fingerprint(scene, catalog))


def ensure_state(key):
    current = st.session_state.get("source_atlas_state")
    cache = st.session_state.setdefault("source_atlas_cache", {})
    if not isinstance(current, dict) or current.get("key") != key:
        current = dict(key=key, atlas=cache.get(key), attempted=key in cache, error=None,
                       page=key[4][0], region_hint=None, seen_focus=None, last_token=None)
        st.session_state["source_atlas_state"] = current
    return current


def save_result(state, atlas):
    cache = st.session_state.setdefault("source_atlas_cache", {})
    cache[state["key"]] = atlas  # None is a rejection, not a valid object.
    while len(cache) > 4: cache.pop(next(iter(cache)))
    state.update(atlas=atlas, attempted=True, error=None if atlas is not None else "invalid")


def optional_scene(wrapper):
    """An absent/unbuilt scene is normal; this does not validate scene data."""
    scene = wrapper.get("scene") if isinstance(wrapper, dict) else None
    return scene if isinstance(scene, dict) and scene else None


def current_focus(wrapper):
    scene = optional_scene(wrapper)
    if scene is None:
        workspace = st.session_state.get("learning_workspace")
        if workspace and isinstance(wrapper, dict) and wrapper.get("material_id") == workspace["material_id"]:
            return workspace["focus"]
        return None
    if scene["domain"] == "spatial_dynamics":
        from scene.world.state import new_state
        return wrapper.setdefault("world", new_state(scene))["focus"]
    if wrapper.get("selected_outcome_id"): return wrapper["selected_outcome_id"]
    # Dynamic probability operations may have no declared focus ID.
    expr = wrapper.get("active_expression")
    if expr in {e["id"] for e in scene["events"]}: return expr
    match = next((f for f in scene["focus_targets"] if f["expression"] == expr), None)
    return match["id"] if match else None


def set_focus(wrapper, identifier, catalog):
    """Use existing reducers and selectors; never modify source physics/state."""
    scene = optional_scene(wrapper)
    if identifier not in catalog: return False
    if scene is None:
        workspace = st.session_state.get("learning_workspace")
        if workspace and isinstance(wrapper, dict) and wrapper.get("material_id") == workspace["material_id"]:
            from workspace.state import set_workspace_focus
            return set_workspace_focus(workspace, identifier, catalog)
        return False
    if scene["domain"] == "spatial_dynamics":
        from scene.world.state import apply_patch, new_state
        quantity_ids = {q["id"] for q in scene["quantities"]}
        if identifier not in quantity_ids: return False  # Parameters are trace links, not focus aliases.
        state = wrapper.setdefault("world", new_state(scene))
        if state["focus"] != identifier:
            apply_patch(scene, state, dict(op="set_focus", target_id=identifier, value=None))
    elif catalog[identifier]["kind"] == "outcomes":
        wrapper["selected_outcome_id"] = identifier
    else:
        target = next((t for t in scene["focus_targets"] if t["id"] == identifier or t["expression"] == identifier), None)
        if target:
            wrapper.update(selected_focus_id=target["id"], active_expression=target["expression"], selected_outcome_id=None, lens="explore")
            # Existing selector would otherwise overwrite external canonical focus.
            st.session_state.pop("scene-widget-focus-"+wrapper["material_id"], None)
        elif catalog[identifier]["kind"] == "events":
            # Select a generated runtime event control on the following render.
            from scene.renderers import _event_pair
            left, right = _event_pair(scene)
            wrapper.update(active_expression=identifier, selected_outcome_id=None, lens="explore")
            wrapper["selected_focus_id"] = "runtime_0" if left and identifier == left["id"] else "runtime_1" if right and identifier == right["id"] else "source_event_"+identifier
            st.session_state.pop("scene-widget-focus-"+wrapper["material_id"], None)
        else: return False
    wrapper["open"] = True
    return True


def select_region(atlas_state, region_id, catalog, wrapper=None):
    if isinstance(wrapper, dict) and atlas_state.get("key") and atlas_state["key"][0] != wrapper.get("material_id"): return False
    atlas = atlas_state["atlas"]
    region = next((r for r in atlas["regions"] if r["region_id"] == region_id), None)
    if region is None: return False
    if any(i not in catalog for i in region["semantic_ids"]): return False
    from workspace.state import focusable
    candidates = [i for i in region["semantic_ids"] if focusable(i, catalog, wrapper)]
    if wrapper:
        # Multiple meanings need a deliberate learner choice, not array order.
        identifier = current_focus(wrapper)
        if len(candidates) == 1: identifier = candidates[0]
        if identifier in candidates: set_focus(wrapper, identifier, catalog)
    atlas_state.update(region_hint=region_id, seen_focus=current_focus(wrapper), page=region["page"])
    return True


def sync_region(atlas_state, focus):
    """World selection wins; keep same-focus source-region disambiguation only."""
    matches = anchors(atlas_state["atlas"], focus) if focus else []
    changed = focus != atlas_state["seen_focus"]
    hinted = next((r for r in matches if r["region_id"] == atlas_state["region_hint"]), None)
    # Unmapped source regions may be inspected, without claiming a semantic link.
    if not hinted and not changed:
        hinted = next((r for r in atlas_state["atlas"]["regions"] if r["region_id"] == atlas_state["region_hint"]), None)
    selected = hinted if not changed and hinted else matches[0] if matches else None
    if changed:
        atlas_state.update(seen_focus=focus, region_hint=selected["region_id"] if selected else None)
        if selected: atlas_state["page"] = selected["page"]
    return selected


def consume_event(atlas_state, event, catalog, wrapper=None):
    if not isinstance(event, dict) or set(event) != {"atlas", "token", "region_id", "focus_stamp"}: return False
    if event["atlas"] != fingerprint(atlas_state["key"]): return False
    token = event["token"]
    if not isinstance(token, str) or not 1 <= len(token) <= 80 or token == atlas_state["last_token"]: return False
    if event["focus_stamp"] != fingerprint(current_focus(wrapper)): return False
    from workspace.grounded_twin import supported_regions
    if event["region_id"] not in {r["region_id"] for r in supported_regions(atlas_state, atlas_state["key"][0], atlas_state["key"][4], catalog)}: return False
    if not select_region(atlas_state, event["region_id"], catalog, wrapper): return False
    atlas_state["last_token"] = token
    return True
