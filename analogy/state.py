"""Bounded session caches; canonical formal focus/parameters remain authoritative."""
import copy
import math
from scene.state import fingerprint
from scene.world.engine import references
from workspace.state import get_workspace_focus, set_workspace_focus, focusable
from .schema import VERSION
from .engine import project


def parameter_registry(wrapper, lab, path, catalog):
    registry={}
    scene=wrapper.get("scene")
    if scene and scene["domain"]=="spatial_dynamics":
        for p in scene["parameters"]:
            linked=[]
            for identifier,entry in catalog.items():
                if not focusable(identifier,catalog,wrapper): continue
                todo=[identifier]; seen=set()
                while todo:
                    i=todo.pop()
                    if i in seen: continue
                    seen.add(i)
                    todo.extend(references(catalog[i]["equation"])&catalog.keys() if catalog[i].get("equation") else [])
                if p["id"] in seen: linked.append(identifier)
            registry["world:"+p["id"]]={k:p[k] for k in ("label","min","max","default")} | dict(owner="world", parameter_id=p["id"], semantic_ids=linked)
    else:
        for demo in (lab or {}).get("demos",[]):
            linked={r["id"] for s in (path or {}).get("steps",[]) if s["id"] in demo["related_step_ids"] for r in s.get("visual_refs",[]) if r["id"] in catalog}
            for p in demo["parameters"]:
                registry[f"lab:{demo['id']}:{p['id']}"]={k:p[k] for k in ("label","min","max","default")} | dict(owner="lab",demo_id=demo["id"],parameter_id=p["id"],semantic_ids=sorted(linked),demo_spec=demo)
    return registry


def identity(material,language,model_signature,focus):
    return (material,language,VERSION,model_signature,focus)


def ensure(store, material, language, signature):
    key=(material,language,VERSION,signature)
    if store.get("identity")!=key: store.clear(); store.update(identity=key,cache={},active=None,local={},numeric={},revision=0,last_token=None,errors={})
    store.setdefault("pending",{})
    return store


def save(store,key,spec):
    store["cache"][key]=spec
    while len(store["cache"])>4:
        old=next(iter(store["cache"])); store["cache"].pop(old); store["local"].pop(old,None); store["numeric"].clear()
    store["active"]=key
    store["errors"].pop(key,None)
    store["revision"]+=1


def values(store,spec,registry,wrapper,lab_state):
    local=store["local"].setdefault(store["active"],{})
    result={}
    for p in spec["parameters"]:
        if p["formal_target"]:
            target=registry[p["formal_target"]]
            if target["owner"]=="world":
                from scene.world.state import new_state
                actual=wrapper.setdefault("world",new_state(wrapper["scene"]))["parameters"][target["parameter_id"]]
            else: actual=lab_state["demos"][target["demo_id"]]["values"][target["parameter_id"]]
            result[p["id"]]=(actual-p["offset"])/p["scale"]
            if math.isclose(result[p["id"]],p["min"],abs_tol=1e-9): result[p["id"]]=p["min"]
            if math.isclose(result[p["id"]],p["max"],abs_tol=1e-9): result[p["id"]]=p["max"]
        else: result[p["id"]]=local.get(p["id"],p["default"])
    return result


def set_parameter(store,spec,identifier,value,registry,wrapper,lab_state):
    p=next((p for p in spec["parameters"] if p["id"]==identifier),None)
    if p is None or type(value) not in (int,float) or not math.isfinite(value) or not p["min"]<=value<=p["max"]: raise ValueError("parameter event")
    trial=values(store,spec,registry,wrapper,lab_state); trial[identifier]=value
    project(spec,trial)  # actual-state recheck before changing either model
    if p["formal_target"]:
        target=registry[p["formal_target"]]; formal=p["scale"]*value+p["offset"]
        if target["owner"]=="world":
            from scene.world.state import apply_patch, new_state
            state=wrapper.setdefault("world",new_state(wrapper["scene"]))
            apply_patch(wrapper["scene"],state,dict(op="set_parameter",target_id=target["parameter_id"],value=formal))
        else:
            if not target["min"]<=formal<=target["max"]: raise ValueError("formal range")
            if "demo_spec" in target:
                from interactive_lab import compute_curves
                candidate=dict(lab_state["demos"][target["demo_id"]]["values"])
                candidate[target["parameter_id"]]=formal
                compute_curves(target["demo_spec"],candidate)
            lab_state["demos"][target["demo_id"]]["values"][target["parameter_id"]]=formal
    else: store["local"].setdefault(store["active"],{})[identifier]=value
    store["revision"]+=1


def select_entity(spec,entity,workspace,catalog,wrapper):
    related=[m for m in spec["mappings"] if m["analogy_id"]==entity]
    current=get_workspace_focus(workspace,wrapper)
    # Preserve a related canonical focus; otherwise prefer the build focus and
    # stable mapping ID. Array ordering never chooses semantic identity.
    mapping=min(related,key=lambda m:(m["formal_id"]!=current,m["formal_id"]!=spec["formal_focus"],m["id"])) if related else None
    return bool(mapping and set_workspace_focus(workspace,mapping["formal_id"],catalog,wrapper))


def highlighted(spec,workspace,wrapper):
    focus=get_workspace_focus(workspace,wrapper)
    return [m["analogy_id"] for m in spec["mappings"] if m["formal_id"]==focus]


def consume_event(store,spec,event,registry,wrapper,lab_state,workspace,catalog):
    if not isinstance(event,dict) or event.get("identity")!=fingerprint(store["active"]) or type(event.get("revision")) is not int or event["revision"]!=store["revision"] or not isinstance(event.get("token"),str) or not 1<=len(event["token"])<=80 or event["token"]==store["last_token"]: return False
    common={"identity","revision","token","kind"}
    try:
        if event.get("kind")=="focus" and set(event)==common|{"entity"}:
            if not select_entity(spec,event["entity"],workspace,catalog,wrapper): return False
            store["revision"]+=1
        elif event.get("kind")=="parameter" and set(event)==common|{"parameter","value"}:
            if event["parameter"] not in {p["control_parameter"] for p in spec["primitives"] if p["control_parameter"]}: return False
            set_parameter(store,spec,event["parameter"],event["value"],registry,wrapper,lab_state)
        else: return False
    except (ValueError,KeyError,TypeError): return False
    store["last_token"]=event["token"]
    return True
