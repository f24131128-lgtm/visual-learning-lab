"""Original page viewer + compact trace; consumes validated atlas data only."""

import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from i18n import tr
from presentation import TOKENS
from scene.state import fingerprint
from source_lens import get_page_render
from .model import anchors, formula_trace
from .state import consume_event, current_focus, optional_scene, select_region, sync_region

_component = components.declare_component("source_atlas_viewer", path=str(Path(__file__).parent/"frontend"))
LABELS = ("Zoom", "Reset view", "Diagram Breakdown", "All layers", "Structure", "Labels", "Vectors", "Formulas", "Relationships",
          "Active focus only", "Hide labels", "Reveal label", "Estimated region — verify on the original page.", "Source Viewer", "Focus source region", "More source controls")


def viewer_payload(bundle, selected, render):
    state, catalog = bundle["state"], bundle["catalog"]
    focus = current_focus(bundle.get("wrapper"))
    return dict(identity=fingerprint(state["key"]), focus_stamp=fingerprint(focus), page=state["page"],
        image="data:image/png;base64,"+base64.b64encode(render["png"]).decode(),
        width=render["width"], height=render["height"],
        regions=[{k: r[k] for k in ("region_id", "bbox", "label", "type", "layer", "confidence", "related_region_ids")}
                 for r in state["atlas"]["regions"] if r["page"] == state["page"] and r["bbox"] is not None],
        selected=selected["region_id"] if selected else None,
        relevant=[r["region_id"] for r in anchors(state["atlas"], focus)] if focus else [],
        labels={k: tr(k) for k in LABELS}, theme_css=TOKENS)


def render_atlas(bundle, context_panel=None):
    state, catalog, wrapper = bundle["state"], bundle["catalog"], bundle.get("wrapper")
    scene = optional_scene(wrapper) or {}
    atlas = state["atlas"]
    selected = sync_region(state, current_focus(wrapper))
    prefix = "atlas-widget-"+bundle["material_id"]+"-"+fingerprint(state["key"])[:12]+"-"
    st.markdown("#### "+tr("Original Source"))
    st.caption(tr("Native text locations only; figures and semantic links still require grounding." if bundle.get("native_only") else
                  "Estimated visual grounding; the original PDF remains the source of truth."))
    page_key = prefix+"page"
    st.session_state[page_key] = state["page"]
    page_labels = {p: tr("Page {page}", page=p) for p in atlas["processed_pages"]}
    page_control, object_control = st.columns([1, 2])
    page_control.selectbox(tr("Source page"), atlas["processed_pages"], format_func=lambda p, labels=page_labels: labels[p],
        key=page_key, on_change=lambda: state.update(page=st.session_state[page_key]))
    available = [r for r in atlas["regions"] if r["page"] == state["page"]]
    ids = [r["region_id"] for r in available]
    if ids:
        key = prefix+"region"
        st.session_state[key] = selected["region_id"] if selected and selected["region_id"] in ids else None
        object_control.selectbox(tr("Choose a source object"), ids, index=None,
            format_func=lambda i: next(r["label"] for r in available if r["region_id"] == i), key=key,
            on_change=lambda: select_region(state, st.session_state[key], catalog, wrapper))
    try:
        render = get_page_render(bundle["source"], bundle["material_id"], state["page"], bundle["allowed"])
        event = _component(payload=viewer_payload(bundle, selected, render), key=prefix+"viewer", default=None)
        if consume_event(state, event, catalog, wrapper): st.rerun()
    except Exception as error:
        # Viewer/PDF failure cannot take down the cached scene; local list remains.
        if isinstance(error, st.errors.StreamlitAPIException): raise
        st.info(tr("The interactive source image is unavailable. Use the source list or existing Source Lens."))
        if "render" in locals(): st.image(render["png"], output_format="PNG")
    with context_panel if context_panel is not None else st.container():
        if selected:
            st.text(selected["label"])
            st.caption(tr("Grounding quality: {quality}", quality=tr("Grounding "+selected["confidence"])))
            if selected["bbox"] is None: st.caption(tr("Page-level anchor only; no reliable visual box is available."))
            if selected["grounding_note"]: st.caption(tr(selected["grounding_note"]))
            if bundle.get("native_only") and selected["source_text_excerpt"]:
                st.caption(tr("Native PDF text"))
                st.text(selected["source_text_excerpt"])
            links = selected["semantic_ids"]
            if links:
                st.caption(tr("Linked meaning")+": "+" · ".join(catalog[i]["label"] for i in links))
                from workspace.ui import render_source_meaning
                render_source_meaning(bundle)
                focusable = [i for i in links if catalog[i]["kind"] not in ("parameter", "time")]
                if scene and focusable and not st.session_state.get("learning_workspace"):
                    from .state import set_focus
                    chosen = st.selectbox(tr("Explore linked meaning"), focusable, format_func=lambda i: catalog[i]["label"], key=prefix+"meaning")
                    st.button(tr("Open as interactive scene"), key=prefix+"open", on_click=set_focus, args=(wrapper, chosen, catalog))
            if selected["type"] == "formula":
                st.markdown("##### "+tr("Formula Trace"))
                trace = formula_trace(selected, catalog)
                if trace["source"]:
                    st.caption(tr("Verified extracted excerpt" if selected["excerpt_verified"] else "Estimated visual transcription — verify on the original page."))
                    st.text(trace["source"])
                for eq in trace["equations"][:6]: st.text(eq.replace("Time", tr("Time")))
                if trace["parameters"]: st.caption(tr("Parameters")+": "+" · ".join(tr("Time") if p == "Time" else p for p in trace["parameters"]))
                if trace["quantities"]: st.caption(tr("Quantities")+": "+" · ".join(trace["quantities"][:8]))
                if trace["representations"]:
                    names = {"objects": "Spatial Scene", "series": "Signal / Waveform", "metrics": "Equation / State Lens",
                             "sample_space": "Sample Space", "set": "Set View", "formula": "Formula Lens", "probability_tree": "Probability Tree", "monte_carlo": "Monte Carlo"}
                    views = list(dict.fromkeys(tr(names.get(v["kind"], v["kind"])) for v in trace["representations"]))
                    st.caption(tr("Driven representations")+": "+" · ".join(views))
        from workspace.ui import render_source_actions
        with st.expander(tr("Related learning")):
            render_source_actions(bundle)
        focus = current_focus(wrapper)
        matches = anchors(atlas, focus) if focus else []
        if matches:
            st.caption(tr("Concept source trace"))
            for region in matches[:8]:
                st.button(tr("Page {page}", page=region["page"])+" · "+region["label"], key=prefix+"trace-"+region["region_id"],
                    on_click=select_region, args=(state, region["region_id"], catalog, wrapper))
        elif wrapper and focus:
            st.caption(tr("No visual anchor for this focus. Existing page-level source links remain available."))
        if not atlas["regions"]: st.caption(tr("No reliable regions were grounded; page context is retained."))
