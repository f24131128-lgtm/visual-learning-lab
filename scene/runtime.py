"""Coordinated multi-view Learning Scene workspace."""

import streamlit as st

from i18n import tr
from .renderers import (
    render_controls, render_formula, render_monte_carlo, render_sample_space,
    render_set_view, render_special_lens, render_tree,
)


def render_scene(scene, state, format_pages, source_context=None, allowed_pages=()):
    if scene["domain"] == "spatial_dynamics":
        from .world.runtime import render_world
        return render_world(scene, state, format_pages, source_context, allowed_pages)
    with st.container(border=True):
        st.markdown("### " + tr("Learning Scene"))
        st.markdown(f"#### {scene['title']}")
        st.caption(scene["learning_goal"])
        render_controls(scene, state)
        if state["lens"] == "explore":
            left, right = st.columns(2)
            with left:
                render_sample_space(scene, state)
            with right:
                render_set_view(scene, state)
            render_tree(scene, state)
            lower_left, lower_right = st.columns(2)
            with lower_left:
                render_formula(scene, state)
            with lower_right:
                render_monte_carlo(scene, state)
        else:
            render_special_lens(scene, state)
            left, right = st.columns(2)
            with left: render_set_view(scene, state)
            with right: render_formula(scene, state)
        st.caption(tr("This workspace uses one validated semantic scene. All controls run locally after compilation."))
