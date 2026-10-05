"""Conditional workspace views, fixed numeric frontend and accessible local controls."""
from pathlib import Path
import json
import re
import streamlit as st
import streamlit.components.v1 as components
from i18n import tr
from scene.state import fingerprint
from source_atlas.model import semantic_fingerprint
from workspace.state import get_workspace_focus, set_workspace_focus, focusable
from . import compiler
from .state import ensure, identity, parameter_registry, values, set_parameter, highlighted, consume_event
from .engine import project
from .schema import MAX_PAYLOAD
from .diagnostics import record

_component=components.declare_component("analogy_world",path=str(Path(__file__).parent/"frontend"))
REPRESENTATIONS=("formal","analogy","compare")


def representation(workspace):
    current=workspace.setdefault("representation","formal")
    labels=dict(zip(REPRESENTATIONS,[tr("Formal model"),tr("Analogy World"),tr("Compare")]))
    key="workspace-representation-"+workspace["material_id"]
    st.session_state[key]=current
    st.radio(tr("Representation"),REPRESENTATIONS,horizontal=True,key=key,format_func=lambda i:labels[i],
        on_change=lambda: workspace.update(representation=st.session_state[key]))
    return workspace["representation"]


def reset_parameters(store,spec,registry,wrapper,lab_state):
    import copy
    # A multi-parameter reset is atomic, including formal invariants/recordings.
    trial_store,trial_wrapper,trial_lab=copy.deepcopy(store),copy.deepcopy(wrapper),copy.deepcopy(lab_state)
    for p in spec["parameters"]: set_parameter(trial_store,spec,p["id"],p["default"],registry,trial_wrapper,trial_lab)
    store.update(trial_store); wrapper.update(trial_wrapper); lab_state.update(trial_lab)


def render(analysis,material,source,pages,model,workspace,wrapper,lab,path,lab_state,compare=False):
    from source_atlas.model import semantic_catalog
    catalog=semantic_catalog(wrapper.get("scene"),analysis)
    focus=get_workspace_focus(workspace,wrapper)
    choices=[i for i in catalog if focusable(i,catalog,wrapper)]
    st.markdown("### "+tr("Analogy World"))
    st.caption(tr("Generated analogy · an explanatory aid, not source evidence or physical identity."))
    if not choices:
        st.info(tr("Choose a source-supported concept in the formal model before building an analogy.")); return
    if focus not in choices:
        labels={i:catalog[i]["label"] for i in choices}
        selected=st.selectbox(tr("Choose a concept"),[None]+choices,format_func=lambda i:labels.get(i,tr("Choose a concept")),key="analogy-initial-focus-"+material)
        if selected: set_workspace_focus(workspace,selected,catalog,wrapper); focus=get_workspace_focus(workspace,wrapper)
    registry=parameter_registry(wrapper,lab,path,catalog)
    signature=fingerprint([semantic_fingerprint(wrapper.get("scene"),catalog),lab,path])
    store=ensure(st.session_state.setdefault("analogy_world_state",{}),material,analysis.get("analysis_language","zh-TW"),signature)
    key=identity(material,analysis.get("analysis_language","zh-TW"),signature,focus)
    active_spec=store["cache"].get(store["active"])
    if key in store["cache"] and (active_spec is None or focus not in {e["id"] for e in active_spec["formal_entities"]}): store["active"]=key
    covered=bool(active_spec and active_spec["suitable"] and focus in {e["id"] for e in active_spec["formal_entities"]})
    retained=key in store.get("pending",{})
    build_clicked=st.button(tr("Recheck saved analogy locally") if retained else tr("Build Analogy World"),key="analogy-build-"+material,disabled=focus is None or key in store["cache"] or covered,type="primary")
    fresh_clicked=False
    if retained and key not in store["cache"] and not covered:
        st.caption(tr("The failed candidate is saved in this session. Rechecking makes no AI request; generating a new candidate makes one explicit request."))
        fresh_clicked=st.button(tr("Generate a new analogy candidate"),key="analogy-new-"+material)
    if build_clicked or fresh_clicked:
        stage="context"
        try:
            if retained and not fresh_clicked:
                compiler.build(store,key,None,model,None,catalog,registry,pages)
            else:
                from openai import OpenAI
                data=compiler.context(analysis,source,catalog,registry,focus,pages)
                stage="client"
                with st.spinner(tr("Building an analogy…")):
                    compiler.build(store,key,OpenAI(api_key=st.secrets["OPENAI_API_KEY"],max_retries=0),model,data,catalog,registry,pages,force_new=fresh_clicked)
        except Exception as error: record(store,key,stage,error)
    if key in store["errors"] and store.get("diagnostics",{}).get(key,{}).get("stage")!="renderer":
        st.info(tr("The analogy could not be built safely. Your formal learning remains available. You may retry explicitly."))
    spec=store["cache"].get(store["active"])
    if not spec:
        _render_diagnostics(store,key,material); return
    if not spec["suitable"]:
        st.info(spec["reason"]); _render_diagnostics(store,key,material); return
    if focus not in {e["id"] for e in spec["formal_entities"]}:
        st.caption(tr("This analogy covers the concepts listed below. Build explicitly to explore another concept."))
    st.markdown("#### "+spec["title"]); st.write(spec["learning_goal"]); st.write(spec["explanation"])
    if any(r["code"]!="derived_local_id" for r in spec.get("recoveries",[])):
        st.caption(tr("Some optional visuals or links were omitted. Correspondences remain available; independent teaching controls do not synchronize formal values."))
    if any(r["code"]=="correspondence_cards" for r in spec.get("recoveries",[])):
        st.caption(tr("Correspondence schematic · positions illustrate concepts, not physical motion."))
    # Always visible, outside expanders, in both analogy and compare.
    st.markdown("**"+tr("What it helps explain")+"**")
    for m in spec["mappings"]: st.write(m["explains"])
    st.markdown("**"+tr("Where the analogy breaks")+"**")
    for limit in spec["limitations"]:
        st.write(limit["breaks"]); st.caption(tr("Misconception to avoid: {text}",text=limit["misconception"]))
    try:
        _render_valid(spec,store,registry,wrapper,lab_state,workspace,catalog,compare)
        active=store["active"]
        if active in store["errors"] and store.get("diagnostics",{}).get(active,{}).get("stage")=="renderer":
            store["errors"].pop(active,None)
            record(store,active,"renderer",normalized=spec)
    except Exception as error:
        record(store,store["active"],"renderer",error,normalized=spec)
        st.info(tr("The analogy view is unavailable. Your formal learning remains available."))
    _render_diagnostics(store,key,material)


def _render_diagnostics(store,key,material):
    # Render after the attempt, including errors from a reused active build
    # whose canonical focus now points at another mapped concept.
    active=store["active"]
    error_key=key if key in store["errors"] else active if active in store["errors"] else None
    if error_key is None and st.query_params.get("analogy_debug")!="1": return
    traces=store.get("diagnostics",{})
    trace=traces.get(error_key if error_key is not None else key if key in traces else active)
    # Explicit developer opt-in, never prompts/source/expressions or SDK messages.
    with st.expander(tr("Analogy developer diagnostics")):
        if trace:
            st.json(trace)
            st.download_button(tr("Download sanitized diagnostics"),json.dumps(trace,ensure_ascii=False,indent=2),"analogy-diagnostics.json","application/json",key="analogy-diagnostics-"+material)
        else: st.caption(tr("No detailed trace was retained for this attempt. A new explicit build records one."))


def _render_valid(spec,store,registry,wrapper,lab_state,workspace,catalog,compare):
    prefix=fingerprint(store["active"])[:16]
    if st.button(tr("Reset analogy controls"),key="analogy-reset-"+prefix):
        reset_parameters(store,spec,registry,wrapper,lab_state)
    current=values(store,spec,registry,wrapper,lab_state)
    for p in spec["parameters"]:
        slider_key=f"analogy-param-{prefix}-{p['id']}"
        # Set before widget creation: formal-side changes own bound values.
        st.session_state[slider_key]=float(current[p["id"]])
        def update(parameter=p,key=slider_key):
            try: set_parameter(store,spec,parameter["id"],st.session_state[key],registry,wrapper,lab_state)
            except (ValueError,KeyError): store["errors"][store["active"]]="ParameterRejected"
        st.slider(p["label"]+(" ("+p["unit"]+")" if p["unit"] else ""),float(p["min"]),float(p["max"]),step=float(p["step"]),key=slider_key,on_change=update)
        st.caption(tr("Linked formal control") if p["formal_target"] else tr("Teaching control · qualitative correspondence"))
    current=values(store,spec,registry,wrapper,lab_state)
    canonical_stamp=fingerprint([current,get_workspace_focus(workspace,wrapper),wrapper.get("world",{}).get("revision")])
    if store.get("canonical_stamp")!=canonical_stamp:
        store["canonical_stamp"]=canonical_stamp
        store["revision"]+=1
    numeric_key=fingerprint([spec,current])
    if numeric_key not in store["numeric"]:
        data=project(spec,current); a,b=data["bounds"],spec["bounds"]
        data["bounds"]=[min(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),max(a[3],b[3])]
        store["numeric"][numeric_key]=data
        while len(store["numeric"])>4: store["numeric"].pop(next(iter(store["numeric"])))
    labels={k:tr(k) for k in ("Play","Pause","Replay","Time","Drag a control horizontally; select a shape to focus its formal concept.")}
    payload=dict(identity=fingerprint(store["active"]),numeric_identity=numeric_key,revision=store["revision"],data=store["numeric"][numeric_key],
        selected=highlighted(spec,workspace,wrapper),parameters=[{k:p[k] for k in ("id","label","min","max")} | dict(value=current[p["id"]]) for p in spec["parameters"]],labels=labels)
    if len(json.dumps(payload,allow_nan=False).encode())>MAX_PAYLOAD: raise ValueError("component payload bounds")
    st.caption(tr("Animation uses a local teaching clock; formal time keeps its committed state."))
    static=st.toggle(tr("Static view"),key="analogy-static-"+prefix)
    event=None
    if not static:
        try: event=_component(payload=payload,key="analogy-canvas-"+prefix,default=None)
        except Exception:
            static=True
            st.caption(tr("Animation is unavailable; use the static view and local controls."))
    if static: render_static(payload["data"],payload["selected"],prefix)
    if consume_event(store,spec,event,registry,wrapper,lab_state,workspace,catalog): st.rerun()
    st.caption(tr("Select a correspondence"))
    entities={e["id"]:e for e in spec["analogy_entities"]}
    active=get_workspace_focus(workspace,wrapper)
    if compare:
        left,right=st.columns(2)
        with left:
            st.markdown("**"+tr("Formal model · source-supported analysis")+"**")
            scene=wrapper.get("scene")
            if scene:
                from scene.runtime import render_scene
                render_scene(scene,wrapper,lambda ps:", ".join(str(p) for p in ps))
            else:
                from interactive_lab import build_lab_chart
                rendered=set()
                for p in spec["parameters"]:
                    target=registry.get(p["formal_target"],{})
                    if target.get("owner")=="lab" and target["demo_id"] not in rendered:
                        demo=target["demo_spec"]
                        st.plotly_chart(build_lab_chart(demo,lab_state["demos"][demo["id"]]["values"],False),use_container_width=True,key="analogy-formal-lab-"+prefix+"-"+demo["id"])
                        rendered.add(demo["id"])
            for e in spec["formal_entities"]:
                st.write(catalog[e["id"]]["label"])
                if catalog[e["id"]].get("equation"):
                    equation=re.sub(r"\b[A-Za-z][A-Za-z0-9_]*\b",lambda match:catalog.get(match.group(),{}).get("label",match.group()),catalog[e["id"]]["equation"])
                    st.code(equation,language=None)
                if e["source_pages"]: st.caption(tr("Source pages: {pages}",pages=", ".join(map(str,e["source_pages"]))))
        with right: st.markdown("**"+tr("Analogy · generated teaching model")+"**"); _mapping_buttons(spec,entities,catalog,workspace,wrapper,prefix,active)
    else: _mapping_buttons(spec,entities,catalog,workspace,wrapper,prefix,active)
    for annotation in spec["annotations"]: st.caption(entities[annotation["entity_id"]]["label"]+": "+annotation["text"])


def _mapping_buttons(spec,entities,catalog,workspace,wrapper,prefix,active):
    for m in spec["mappings"]:
        label=catalog[m["formal_id"]]["label"]+" ↔ "+entities[m["analogy_id"]]["label"]
        st.button(label,key="analogy-mapping-"+prefix+"-"+m["id"],type="primary" if active==m["formal_id"] else "secondary",
            on_click=set_workspace_focus,args=(workspace,m["formal_id"],catalog,wrapper))
        st.caption(m["relationship"])


def render_static(data,selected,key):
    """Fixed fallback consumes exactly the same numeric projection, no formulas."""
    import plotly.graph_objects as go
    figure=go.Figure()
    for o in data["objects"]:
        a={k:v[0] for k,v in o["data"].items()}
        if a["visible"]<.5: continue
        color="#de3f65" if o["entity_id"] in selected else o["color"]
        if o["type"]=="curve": x,y=o["data"]["x"],o["data"]["y"]
        elif o["type"]=="segment": x,y=[a["x"],a["x2"]],[a["y"],a["y2"]]
        elif o["type"]=="rectangle":
            x=[a["x"]-a["x2"]/2,a["x"]+a["x2"]/2,a["x"]+a["x2"]/2,a["x"]-a["x2"]/2,a["x"]-a["x2"]/2]
            y=[a["y"]-a["y2"]/2,a["y"]-a["y2"]/2,a["y"]+a["y2"]/2,a["y"]+a["y2"]/2,a["y"]-a["y2"]/2]
        else: x,y=[a["x"]],[a["y"]]
        label=o["label"]+(f": {a['value']:.3g}" if o["type"]=="meter" else "")
        figure.add_trace(go.Scatter(x=x,y=y,mode="lines" if len(x)>1 else "markers+text",name=label,text=[label] if len(x)==1 else None,textposition="top center",line=dict(color=color),marker=dict(color=color,size=16)))
    b=data["bounds"]
    figure.update_layout(height=380,xaxis=dict(range=[b[0]-.6,b[1]+.6]),yaxis=dict(range=[b[2]-.6,b[3]+.6],scaleanchor="x",scaleratio=1),showlegend=False)
    st.plotly_chart(figure,use_container_width=True,key="analogy-static-chart-"+key)
