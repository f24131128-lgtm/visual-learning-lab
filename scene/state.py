"""Material-scoped local state and bounded compiler cache."""

import hashlib
import json

import streamlit as st

from .schema import DOMAIN, SCENE_SCHEMA_VERSION

MAX_SCENE_CACHE_ENTRIES = 4


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=list).encode("utf-8")).hexdigest()


def cache_key(material_id, language, domain=DOMAIN):
    from .world.schema import DOMAIN as WORLD_DOMAIN, VERSION
    return (material_id, language, VERSION if domain == WORLD_DOMAIN else SCENE_SCHEMA_VERSION, domain)


def reset_scene_state(clear_cache=False):
    st.session_state.pop("learning_scene_state", None)
    if clear_cache:
        st.session_state.pop("learning_scene_cache", None)
    for key in list(st.session_state):
        if str(key).startswith(("scene-widget-", "world-widget-")):
            st.session_state.pop(key, None)


def ensure_state(material_id, language, domain=DOMAIN):
    key = cache_key(material_id, language, domain)
    cache = st.session_state.setdefault("learning_scene_cache", {})
    def compatible(scene):
        return isinstance(scene, dict) and scene.get("scene_version") == key[2] and scene.get("domain") == domain
    if key in cache and cache[key] is not None and not compatible(cache[key]):
        # A mismatched cached declaration is not a current-version rejection.
        # Discard just this entry, not unrelated material/probability caches.
        cache.pop(key)
    state = st.session_state.get("learning_scene_state")
    if not isinstance(state, dict) or state.get("cache_key") != key or (state.get("scene") is not None and not compatible(state["scene"])):
        state = {
            "cache_key": key, "material_id": material_id, "language": language,
            "scene": cache.get(key), "selected_outcome_id": None,
            "selected_focus_id": None, "active_expression": None,
            "monte_carlo_samples": 1_000, "monte_carlo_seed": 17,
            "lens": "explore", "open": bool(cache.get(key)), "error": "invalid" if domain == "spatial_dynamics" and key in cache and cache[key] is None else None,
            "attempted": key in cache,
        }
        st.session_state["learning_scene_state"] = state
    elif state.get("scene") is None and key in cache:
        state["scene"] = cache[key]
        if state["scene"]:
            state.update(open=True, error=None, attempted=True)
            state.pop("validation_reason", None)
    return state


def save_scene(state, scene):
    cache = st.session_state.setdefault("learning_scene_cache", {})
    key = state["cache_key"]
    cache[key] = scene
    while len(cache) > MAX_SCENE_CACHE_ENTRIES:
        cache.pop(next(iter(cache)))
    if scene["domain"] == "spatial_dynamics":
        from .world.state import new_state
        state.update(scene=scene, world=new_state(scene), open=True, error=None, attempted=True)
        for name in ("world_numeric_cache", "world_pending_replay", "world_control_error"):
            state.pop(name, None)
        state.pop("validation_reason", None)
        return
    state.update({"scene": scene, "selected_outcome_id": None,
                  "selected_focus_id": scene["focus_targets"][0]["id"],
                  "active_expression": scene["focus_targets"][0]["expression"],
                  "open": True, "error": None})


def save_rejection(state):
    """Cache an invalid spatial compiler response, not a transient API failure."""
    cache = st.session_state.setdefault("learning_scene_cache", {})
    cache[state["cache_key"]] = None
    while len(cache) > MAX_SCENE_CACHE_ENTRIES: cache.pop(next(iter(cache)))
    state.update(scene=None, attempted=True, error="invalid")
    for name in ("world", "world_numeric_cache", "world_pending_replay"):
        state.pop(name, None)
