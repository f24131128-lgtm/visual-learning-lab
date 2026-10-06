"""Opt-in adapter over the existing quantity DAG, projections and reducer."""
import copy
import math

from .contract import MAX_TARGETS, affine, focus_event, invert, tree, trig_product, valid_event
from scene.world.engine import frames, snapshot
from scene.world.policy import time_domain


def targets(scene, state):
    """Recognize exact polar forward bindings; no inverse is guessed by labels.

    Parameter-linear angle with an affine, nonnegative radius is a supported
    analytic family. Time and other parameters remain frozen during a gesture.
    More complex expressions (including variable angular rate) use old controls.
    """
    result=[]; params={p["id"]:p for p in scene["parameters"]}
    names=set(params)|{"time"}; quantities={q["id"]:q["expression"] for q in scene["quantities"]}
    current=snapshot(scene,state)
    env=state["parameters"]|{"time":state["time"]}
    # Prefer the vector affordance when a point is the exact same formal handle.
    # Identity and focus remain the selected existing object's semantic ID.
    for obj in sorted(scene["objects"],key=lambda o:o["type"]!="vector"):
        if obj["type"] not in ("vector","point"): continue
        binding=next(b for b in scene["bindings"] if b["target_id"]==obj["id"])
        try:
            pair=[tree(quantities[q],names,quantities) for q in binding["quantity_ids"]]
            radius,angle=trig_product(pair[0],"cos",names)
            if trig_product(pair[1],"sin",names)!=(radius,angle): continue
            ac,aa=angle; rc,rr=radius
            adjustable=[k for k in aa if k in params and params[k]["min"]<params[k]["max"]]
            if len(adjustable)!=1: continue
            aid=adjustable[0]; scale=aa[aid]
            if abs(scale)<1e-9 or abs(scale)*(params[aid]["max"]-params[aid]["min"])>2*math.pi+1e-9: continue
            offset=ac+sum(v*env[k] for k,v in aa.items() if k!=aid)
            # Keep bounded branch enumeration and reject ambiguous cross coupling.
            if abs(offset)+max(abs(params[aid]["min"]*scale),abs(params[aid]["max"]*scale))>250*math.pi: continue
            rids=[k for k in rr if k in params and params[k]["min"]<params[k]["max"]]
            if len(rids)>1 or aid in rr or "time" in rr: continue
            rid=rids[0] if rids else None
            roffset=rc+sum(v*env[k] for k,v in rr.items() if k!=rid)
            low=roffset+(rr[rid]*params[rid]["min"] if rid else 0)
            high=roffset+(rr[rid]*params[rid]["max"] if rid else 0)
            if min(low,high)<=1e-8 or max(low,high)>1e6: continue
            nums=current["projections"][obj["id"]]
            origin=nums[:2] if obj["type"]=="vector" else [0.,0.]
            # A moving origin depending on manipulated parameters is ambiguous.
            if obj["origin_quantity_ids"]:
                for q in obj["origin_quantity_ids"]:
                    _,refs=affine(tree(quantities[q],names,quantities),names)
                    if aid in refs or (rid and rid in refs): raise ValueError("Moving control origin")
            maximum=max(low,high)
            model=dict(kind="polar" if rid else "circular",origin=origin,angle_id=aid,angle_scale=scale,offset=offset)
            if rid: model.update(radius_id=rid,radius_scale=rr[rid],radius_offset=roffset)
            if any(t["inverse"]==model for t in result):continue
            result.append(dict(id=obj["id"],object_id=obj["id"],semantic_id=obj["semantic_id"],label=obj["label"],
                gesture="drag_vector_endpoint" if rid else "drag_on_circle",coordinate_space="world",dimensions=2,
                parameter_ids=[aid]+([rid] if rid else []),inverse=model,
                bounds=[origin[0]-maximum,origin[1]-maximum,origin[0]+maximum,origin[1]+maximum],
                position=[origin[0]+nums[2],origin[1]+nums[3]] if obj["type"]=="vector" else nums,
                source_pages=obj["source_pages"]))
        except (ValueError,KeyError,TypeError,SyntaxError): continue
        if len(result)==MAX_TARGETS: break
    return result


def commit(scene,state,identity,event):
    """Commit one atomic semantic state, even when two parameters change.

    Sequential intermediate states can violate coupled invariants; validate the
    final values together through the same reducer used by gestures and replay.
    """
    from scene.world.state import apply_parameters
    target=valid_event(event,identity,state["revision"],state["last_token"],targets(scene,state))
    if target is None: return False
    try:
        trial=copy.deepcopy(state)
        domain=time_domain(scene,trial["parameters"])
        if not domain["min"]<=event["time"]<=domain["max"]: return False
        trial["time"]=event["time"]
        # Re-derive frozen offsets/origins at the displayed, validated clock time.
        target=next(t for t in targets(scene,trial) if t["id"]==target["id"])
        values=invert(target,{p["id"]:p for p in scene["parameters"]},trial["parameters"],event["x"],event["y"])
        apply_parameters(scene,trial,values,target["semantic_id"])
        trial["last_token"]=event["token"]
        state.update(trial)
        return True
    except (ValueError,TypeError,KeyError,StopIteration,OverflowError): return False


def commit_focus(scene,state,identity,event):
    from scene.world.state import apply_patch
    target=focus_event(event,identity,state["revision"],state["last_token"],targets(scene,state),state["time"])
    if target is None:return False
    trial=copy.deepcopy(state)
    try:
        apply_patch(scene,trial,dict(op="set_focus",target_id=target["semantic_id"],value=None))
        trial["last_token"]=event["token"];state.update(trial);return True
    except (ValueError,TypeError,KeyError,OverflowError):return False
