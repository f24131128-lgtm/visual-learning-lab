"""Explore adapter: planning is explicit; selection and discrete actions are local."""
import streamlit as st
from graphviz import Digraph
from i18n import tr
from workspace.state import get_workspace_focus, set_workspace_focus, focusable
from source_atlas.model import semantic_catalog
from . import compiler, process
from .diagnostics import record


def ready_analogy(material):
    store = st.session_state.get("analogy_world_state", {})
    if store.get("identity", [None])[0] != material: return False
    spec = store.get("cache", {}).get(store.get("active"))
    return bool(spec and spec.get("suitable"))


def representation(analysis, material, source, pages, model, workspace, wrapper, lab):
    catalog = semantic_catalog(wrapper.get("scene"), analysis)
    catalog = {i: v for i, v in catalog.items() if focusable(i, catalog, wrapper)}
    caps = compiler.capabilities(analysis, wrapper, lab)
    language = analysis.get("analysis_language", "zh-TW")
    store = compiler.ensure(st.session_state.setdefault("learning_world_plans", {}), material)
    focus = get_workspace_focus(workspace, wrapper)
    key = compiler.identity(material, language, source, catalog, caps, focus)
    pending = key in store["pending"]
    recheck = st.button(tr("Recheck saved representation locally") if pending else tr("Choose a learning representation"), key="world-plan-"+material, disabled=not catalog or key in store["cache"])
    regenerate = False
    if pending and key not in store["cache"]:
        st.caption(tr("The candidate is retained. Local recheck makes no AI request; a new candidate makes one explicit request."))
        regenerate = st.button(tr("Generate a new representation candidate"), key="world-plan-new-"+material)
    if recheck or regenerate:
        try:
            data = compiler.context(analysis, source, catalog, pages, caps, focus)
            with st.spinner(tr("Choosing a learning representation…")):
                if pending and not regenerate:
                    result = compiler.build(store, key, None, model, data, catalog, pages, caps)
                else:
                    from openai import OpenAI
                    result = compiler.build(store, key, OpenAI(api_key=st.secrets["OPENAI_API_KEY"], max_retries=0), model, data, catalog, pages, caps, force_new=regenerate)
            if result:
                workspace["representation"] = "process" if result["family"] == "process" else "analogy" if result["family"] == "analogy" else "formal"
        except Exception as error:
            record(store, key, "context", error)
    if key in store["errors"]: st.info(tr("The representation could not be built safely. Existing learning remains available; retry explicitly."))
    plan = store["cache"].get(store["active"])
    # A semantic catalog/compiler change cannot publish stale links; local focus/values do not change specs.
    if store["active"] and store["active"][:4] != key[:4]: plan = None
    if plan:
        if store["active"] not in store["diagnostics"]:
            record(store, store["active"], "cached_before_diagnostics", normalized=plan)
        st.caption(plan["reason"])
        if plan["adapted"]: st.caption(tr("A simpler supported representation is used."))
    options = ["formal"]
    if plan and plan["family"] == "process": options.append("process")
    if catalog and (not plan or plan["family"] == "analogy" or ready_analogy(material)): options.append("analogy")
    if ready_analogy(material): options.append("compare")
    current = workspace.setdefault("representation", "formal")
    if current not in options: workspace["representation"] = "formal"
    labels = {"formal": tr("Formal model"), "process": tr("Interactive process"), "analogy": tr("Analogy World"), "compare": tr("Compare")}
    widget = "workspace-representation-"+material
    st.session_state[widget] = workspace["representation"]
    st.radio(tr("Representation"), options, horizontal=True, key=widget, format_func=lambda i: labels[i],
             on_change=lambda: workspace.update(representation=st.session_state[widget]))
    diagnostic_key = key if key in store["diagnostics"] else store["active"]
    if diagnostic_key in store["diagnostics"]:
        store["diagnostics"][diagnostic_key]["legacy_visual_flow_used"] = workspace["representation"] == "formal" and analysis.get("primary_visualization", {}).get("type") == "flow"
    return workspace["representation"], plan


def render_diagnostics(material):
    if st.query_params.get("learning_world_debug") != "1": return
    import json
    store = st.session_state.get("learning_world_plans", {})
    if store.get("material") != material: return
    key = store.get("diagnostic_active") or store.get("active")
    trace = store.get("diagnostics", {}).get(key)
    if not trace: return
    trace["request_count"] = store.get("request_count", 0)
    with st.expander(tr("Learning representation diagnostics")):
        st.json(trace)
        st.download_button(tr("Download representation diagnostics"), json.dumps(trace, ensure_ascii=False, indent=2),
            file_name="learning-world-diagnostics.json", mime="application/json", key="world-diagnostic-"+material)


def commit(store, key, spec, event, workspace, catalog, wrapper):
    state = store["states"].get(key)
    if state is None: return False
    result = process.apply(spec, state, event)
    if not result: return False
    trial, semantic = result
    if not set_workspace_focus(workspace, semantic, catalog, wrapper): return False
    store["states"][key] = trial
    return True


def render_process(plan, material, workspace, wrapper, analysis, pages):
    store = st.session_state.get("learning_world_plans", {})
    key = store.get("active")
    spec = plan["process"] if plan else None
    if not spec or store.get("material") != material: return
    catalog = semantic_catalog(wrapper.get("scene"), analysis)
    state = store["states"].setdefault(key, process.initial(spec))
    if not process.valid(spec, state):
        st.info(tr("The process state is unavailable. Existing learning remains available.")); return
    trace = store.get("diagnostics", {}).get(key)
    if trace:
        trace.update(process_runtime_reached=True, legacy_visual_flow_used=False)
    st.markdown("### " + tr("Interactive process"))
    st.caption(tr("Generated learning model · formal concepts retain their original source links."))
    focus = get_workspace_focus(workspace, wrapper)
    prefix = "world-process-"+material+"-"+state["identity"][:12]
    for collection in spec["collections"]:
        st.text(collection["label"])
        items = state["collections"][collection["id"]]
        if not items: st.caption(tr("Empty collection"))
        else:
            graph = Digraph()
            graph.attr(rankdir="LR")
            for n, item in enumerate(items):
                roles = [collection["first_label"]] if n == 0 else []
                if n == len(items)-1: roles.append(collection["last_label"])
                graph.node(item["id"], label=item["text"] + ("\n" + " / ".join(r for r in roles if r) if roles else ""),
                           shape="box", color="#2563eb" if focus == collection["semantic_id"] else "#64748b")
                if n: graph.edge(items[n-1]["id"], item["id"])
            try: st.graphviz_chart(graph.source)
            except Exception: pass
            # Always-accessible ordered view and endpoint roles also survive renderer failure.
            st.text(" → ".join(item["text"] for item in items))
            st.caption(f"{collection['first_label']}: {items[0]['text']} · {collection['last_label']}: {items[-1]['text']}")
    for variable in spec["states"]: st.text(variable["label"] + ": " + state["states"][variable["id"]])
    value = st.text_input(tr("New item"), max_chars=64, key=prefix+"-input") if any(t["operation"] in ("append", "prepend") for t in spec["transitions"]) else ""
    for t in spec["transitions"]:
        allowed = process.enabled(spec, state, t["id"]) and (bool(value.strip()) if t["operation"] in ("append", "prepend") else True)
        event = dict(identity=state["identity"], revision=state["revision"], transition_id=t["id"], value=value)
        st.button(t["label"], key=prefix+"-"+t["id"], disabled=not allowed,
                  on_click=commit, args=(store, key, spec, event, workspace, catalog, wrapper))
        st.caption(t["explanation"])
    def reset():
        result = process.reset(spec, store["states"][key])
        if result: store["states"][key] = result
    st.button(tr("Reset process"), key=prefix+"-reset", on_click=reset)
    if state["last_removed"]: st.text(tr("Last removed: {item}", item=state["last_removed"]))
    labels = {t["id"]: t["label"] for t in spec["transitions"]}
    if state["history"]:
        st.caption(tr("Local transition history"))
        st.text(" → ".join(labels[h["transition_id"]] for h in state["history"][-8:]))
    for a in spec["annotations"]: st.text(a["text"])
    for identifier in plan["focus_ids"]:
        if st.button(catalog[identifier]["label"], key=prefix+"-focus-"+identifier):
            set_workspace_focus(workspace, identifier, catalog, wrapper)
    valid_pages = [p for p in plan["source_pages"] if p in pages]
    if valid_pages: st.caption(tr("Source pages: {pages}", pages=", ".join(map(str, valid_pages))))
