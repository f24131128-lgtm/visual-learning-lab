"""Offline browser acceptance only: run with `streamlit run tests/manual_day18.py`."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from i18n import LANGUAGE_NAMES
from presentation import render_header
from scene.runtime import render_scene
from scene.world.state import new_state
from scene.world.validator import normalize_world
from tests.world_fixtures import circular_world, complete_projectile_world, three_phase_world

st.set_page_config(page_title="Day 18 offline acceptance", layout="wide")
render_header()
st.caption("Offline acceptance fixtures — not generated analysis or PDF evidence. No API access.")
name = st.selectbox("Acceptance system", ["Three-phase rotating field", "Projectile motion", "Circular motion"])
if st.session_state.get("acceptance_system") != name:
    for key in list(st.session_state):
        if str(key).startswith("world-widget-"): st.session_state.pop(key, None)
    factory = {"Three-phase rotating field": three_phase_world, "Projectile motion": complete_projectile_world, "Circular motion": circular_world}[name]
    scene = normalize_world(factory(), [])
    st.session_state["acceptance_wrapper"] = dict(material_id="offline-acceptance", scene=scene, world=new_state(scene))
    st.session_state["acceptance_system"] = name
wrapper = st.session_state["acceptance_wrapper"]
render_scene(wrapper["scene"], wrapper, lambda pages: "", {"kind": "text", "source_text": "", "page_texts": {}}, [])
