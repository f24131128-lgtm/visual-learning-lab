"""Fixed Explore view of the existing compiler/shared-focus bounded execution state."""
import streamlit as st
from i18n import tr
from source_atlas.model import semantic_catalog
from workspace.state import set_workspace_focus, get_workspace_focus
from semantic_contract import display_choices
from . import execution


def commit(store, key, spec, event, workspace, catalog, wrapper):
    result = execution.apply(spec, store["states"][key], event)
    if result is None: return False
    state, semantic = result
    if not set_workspace_focus(workspace, semantic, catalog, wrapper): return False
    store["states"][key] = state
    return True


def render_execution(plan, material, workspace, wrapper, analysis, pages):
    store = st.session_state.get("learning_world_plans", {})
    key = store.get("active")
    spec = (plan or {}).get("execution")
    if not spec or store.get("material") != material: return
    catalog = semantic_catalog(wrapper.get("scene"), analysis)
    state = store["states"].setdefault(key, execution.initial(spec))
    if not execution.valid(spec, state):
        st.info(tr("The execution state is unavailable. Existing learning remains available.")); return
    prefix = "world-execution-"+material+"-"+state["identity"][:12]
    calls = {c["id"]: c for c in spec["calls"]}
    top = state["frames"][-1]; call = calls[top["call_id"]]
    st.markdown("### "+tr("Interactive execution"))
    st.caption(tr("Generated bounded example · frames link to source concepts; they are not source facts."))
    st.text(tr("Current call: {label}", label=call["label"]))
    st.text(tr("Caller: {label}", label=calls[state["frames"][-2]["call_id"]]["label"] if len(state["frames"]) > 1 else tr("Root call")))
    st.markdown("#### "+tr("Call stack"))
    for f in state["frames"]:
        st.text(calls[f["call_id"]]["label"]+" · "+tr(f["status"].title()))
    for arg in call["arguments"]: st.text(arg["label"]+": "+f"{arg['value']:.5g}")
    for edge in call["children"]:
        if edge["result_id"] in top["returned"]: st.text(edge["result_label"]+": "+f"{top['returned'][edge['result_id']]:.5g}")
    if top["result"] is not None: st.text(tr("Result: {value}", value=f"{top['result']:.5g}"))
    for operation, label in (("call", "Call child"), ("complete", "Complete current call"), ("return", "Return to caller")):
        st.button(tr(label), key=prefix+"-"+operation, disabled=not execution.enabled(spec, state, operation),
            on_click=commit, args=(store, key, spec, execution.event(spec, state, operation), workspace, catalog, wrapper))
    def reset():
        result = execution.reset(spec, store["states"][key])
        if result and set_workspace_focus(workspace, calls[spec["root_id"]]["semantic_id"], catalog, wrapper): store["states"][key] = result
    st.button(tr("Reset execution"), key=prefix+"-reset", on_click=reset)
    choices = [dict(id=f["id"], label=calls[f["call_id"]]["label"]) for f in state["frames"]]
    labels = display_choices(choices, lambda item, n: tr("Call {number}", number=n))
    def select():
        frame = next(f for f in store["states"][key]["frames"] if f["id"] == st.session_state[prefix+"-frame"])
        set_workspace_focus(workspace, calls[frame["call_id"]]["semantic_id"], catalog, wrapper)
    st.selectbox(tr("Inspect a call"), [f["id"] for f in state["frames"]], format_func=labels.get,
                 key=prefix+"-frame", on_change=select)
    st.caption(tr("All execution steps run locally; no AI request is made."))
    for annotation in spec["annotations"]: st.text(annotation["text"])
    valid_pages=[p for p in plan["source_pages"] if p in pages]
    if valid_pages: st.caption(tr("Source pages: {pages}", pages=", ".join(map(str, valid_pages))))
