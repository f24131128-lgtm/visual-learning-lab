"""Single offline numeric renderer adapter for two existing formal runtimes."""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

from i18n import tr
from scene.state import fingerprint
from . import lab, world
from .preview import bake, lab_projection, world_projection

_component=components.declare_component("direct_semantic_manipulation",path=str(Path(__file__).parent/"frontend"))
LABELS=("Drag the highlighted endpoint", "Drag an anchor vertically", "Tentative preview · release to validate", "Current exploration value", "Compiled baseline value", "Exploration changes do not change the source.", "Release to apply", "That change is outside this validated model. The world was preserved.", "Local exploration", "Numeric preview unavailable; release still validates the change.")


def _cache(owner,key,build):
    cache=owner.setdefault("manipulation_numeric_cache",{})
    if key not in cache:
        try: cache[key]=build()
        except (ValueError,TypeError,KeyError,OverflowError): cache[key]=None
        while len(cache)>2: cache.pop(next(iter(cache)))
    return cache[key]


def _payload(identity,revision,targets,parameters,values,baseline,objects,curves,metrics,current,previews,clock,**extra):
    result=dict(version="1.0",identity=identity,revision=revision,targets=targets,parameters=parameters,values=values,
        baseline=baseline,objects=objects,curves=curves,metrics=metrics,current=current,previews=previews,time=clock,
        labels={k:tr(k) for k in LABELS},**extra)
    if len(json.dumps(result,ensure_ascii=False,allow_nan=False).encode())>1_500_000: raise ValueError("Manipulation payload bound")
    return result


def world_payload(scene,wrapper):
    state=wrapper["world"];ts=world.targets(scene,state)
    identity=fingerprint(["direct",wrapper["material_id"],scene])
    previews={}
    for target in ts:
        fixed={k:v for k,v in state["parameters"].items() if k not in target["parameter_ids"]}
        key=fingerprint([identity,target["parameter_ids"],fixed])
        previews[target["id"]]=_cache(wrapper,key,lambda t=target:bake(scene["parameters"],state["parameters"],t["parameter_ids"],lambda v:world_projection(scene,v)))
    from scene.world.policy import parameter_display
    from scene.world.engine import snapshot
    exact=snapshot(scene,state)
    return _payload(identity,state["revision"],ts,[p|{"display":parameter_display(p)} for p in scene["parameters"]],state["parameters"],
        {p["id"]:p["default"] for p in scene["parameters"]},scene["objects"],scene["series"],scene["metrics"],
        world_projection(scene,state["parameters"]),previews,state["time"],committed=dict(
            objects={o["id"]:exact["projections"][o["id"]] for o in scene["objects"]},
            metrics={m["id"]:exact["projections"][m["id"]][0] for m in scene["metrics"]}),
        focused_target_ids=[t["id"] for t in ts if t["semantic_id"]==state["focus"]])


def render_world(scene,wrapper):
    if not world.targets(scene,wrapper["world"]): return False
    try:
        data=world_payload(scene,wrapper)
        st.caption(tr("Drag the highlighted endpoint"))
        event=_component(payload=data,key="direct-world-"+data["identity"],default=None)
        if world.commit_focus(scene,wrapper["world"],data["identity"],event) or world.commit(scene,wrapper["world"],data["identity"],event): st.rerun()
        from scene.world.state import acknowledge_rejection
        if acknowledge_rejection(wrapper["world"],data["identity"],event):
            wrapper["world_control_error"]=tr("That change is outside this validated model. The world was preserved.")
            st.rerun()
        return True
    except (ValueError,TypeError,KeyError,OverflowError): return False


def lab_payload(demo,saved,material,semantic_id):
    ts=lab.targets(demo,saved["values"],semantic_id)
    identity=fingerprint(["direct",material,demo,semantic_id])
    previews={}
    for t in ts:
        fixed={k:v for k,v in saved["values"].items() if k not in t["parameter_ids"]}
        key=fingerprint([identity,t["parameter_ids"],fixed])
        previews[t["id"]]=_cache(saved,key,lambda t=t:bake(demo["parameters"],saved["values"],t["parameter_ids"],lambda v:lab_projection(demo,v)))
    return _payload(identity,lab.revision(saved),ts,demo["parameters"],saved["values"],{p["id"]:p["default"] for p in demo["parameters"]},
        [],demo["series"],demo["derived_metrics"],lab_projection(demo,saved["values"]),previews,0.,ack=saved.get("gesture_ack"))


def render_lab(demo,saved,material,path):
    from source_atlas.model import semantic_catalog
    from workspace.state import get_workspace_state,set_workspace_focus
    wrapper=st.session_state.get("learning_scene_state")
    if wrapper and wrapper.get("material_id")!=material: wrapper=None
    catalog=semantic_catalog((wrapper or {}).get("scene"),st.session_state.get("analysis",{}))
    semantic_id=lab.semantic_target(demo,path,catalog,st.session_state.get("analysis",{}))
    if not lab.targets(demo,saved["values"],semantic_id): return False
    try:
        data=lab_payload(demo,saved,material,semantic_id)
        from workspace.state import get_workspace_focus
        data["focused_target_ids"]=[t["id"] for t in data["targets"] if t["semantic_id"]==get_workspace_focus(get_workspace_state(material),wrapper)]
        st.caption(tr("Drag an anchor vertically"))
        event=_component(payload=data,key="direct-lab-"+data["identity"],default=None)
        focus=lambda i:set_workspace_focus(get_workspace_state(material),i,catalog,wrapper)
        if lab.commit_focus(demo,saved,data["identity"],event,semantic_id,focus) or lab.commit(demo,saved,data["identity"],event,semantic_id,focus): st.rerun()
        # An explicit acknowledgment stamp unlocks a rejected event without
        # changing formal values or accepting spoofed target/focus metadata.
        if isinstance(event,dict) and event.get("scene")==data["identity"] and type(event.get("revision")) is int and event["revision"]==data["revision"] and isinstance(event.get("token"),str) and 1<=len(event["token"])<=80 and event["token"]!=saved.get("gesture_ack"):
            saved["gesture_ack"]=event["token"];st.rerun()
        return True
    except (ValueError,TypeError,KeyError,OverflowError): return False
