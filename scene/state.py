"""Material-scoped local state and bounded compiler cache."""

import hashlib
import json

import streamlit as st

from .schema import DOMAIN, SCENE_SCHEMA_VERSION

MAX_SCENE_CACHE_ENTRIES = 4


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, default=list).encode("utf-8")).hexdigest()


def cache_key(material_id, language):
    return (material_id, language, SCENE_SCHEMA_VERSION, DOMAIN)


def reset_scene_state(clear_cache=False):
    st.session_state.pop("learning_scene_state", None)
    if clear_cache:
        st.session_state.pop("learning_scene_cache", None)
    for key in list(st.session_state):
        if str(key).startswith("scene-widget-"):
            st.session_state.pop(key, None)


def ensure_state(material_id, language):
    key = cache_key(material_id, language)
    cache = st.session_state.setdefault("learning_scene_cache", {})
    state = st.session_state.get("learning_scene_state")
    if not isinstance(state, dict) or state.get("cache_key") != key:
        state = {
            "cache_key": key, "material_id": material_id, "language": language,
            "scene": cache.get(key), "selected_outcome_id": None,
            "selected_focus_id": None, "active_expression": None,
            "monte_carlo_samples": 1_000, "monte_carlo_seed": 17,
            "lens": "explore", "open": bool(cache.get(key)), "error": None,
        }
        st.session_state["learning_scene_state"] = state
    elif state.get("scene") is None and key in cache:
        state["scene"] = cache[key]
    return state


def save_scene(state, scene):
    cache = st.session_state.setdefault("learning_scene_cache", {})
    key = state["cache_key"]
    cache[key] = scene
    while len(cache) > MAX_SCENE_CACHE_ENTRIES:
        cache.pop(next(iter(cache)))
    state.update({"scene": scene, "selected_outcome_id": None,
                  "selected_focus_id": scene["focus_targets"][0]["id"],
                  "active_expression": scene["focus_targets"][0]["expression"],
                  "open": True, "error": None})
