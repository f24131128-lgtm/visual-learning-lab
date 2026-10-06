"""The same inverse contract over existing Numeric Lab state and evaluator."""
import ast
import copy
import math

from .contract import focus_event, invert, tree, valid_event


def polynomial(node, names):
    """Bounded exact polynomial proof; never numerical differentiation."""
    from safe_math import CONSTANTS
    if isinstance(node,ast.Constant) and type(node.value) in (int,float): return {():float(node.value)}
    if isinstance(node,ast.Name):
        if node.id in CONSTANTS: return {():float(CONSTANTS[node.id])}
        if node.id in names: return {(node.id,):1.}
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,(ast.USub,ast.UAdd)):
        sign=-1 if isinstance(node.op,ast.USub) else 1
        return {k:v*sign for k,v in polynomial(node.operand,names).items()}
    if isinstance(node,ast.BinOp):
        a=polynomial(node.left,names);b=polynomial(node.right,names)
        if isinstance(node.op,(ast.Add,ast.Sub)):
            result=dict(a);sign=-1 if isinstance(node.op,ast.Sub) else 1
            for k,v in b.items(): result[k]=result.get(k,0.)+v*sign
        elif isinstance(node.op,ast.Mult):
            result={}
            for ka,va in a.items():
                for kb,vb in b.items():
                    k=tuple(sorted(ka+kb))
                    if len(k)>2: raise ValueError("Polynomial bound")
                    result[k]=result.get(k,0.)+va*vb
        elif isinstance(node.op,ast.Div) and set(b)=={()} and abs(b[()])>1e-12:
            result={k:v/b[()] for k,v in a.items()}
        else: raise ValueError("Unsupported polynomial")
        if len(result)>16: raise ValueError("Polynomial bound")
        return {k:v for k,v in result.items() if v!=0}
    raise ValueError("Unsupported polynomial")


def targets(demo, values, semantic_id):
    if not semantic_id or len(demo["series"])!=1: return []
    try:
        xid=demo["x"]["id"];params={p["id"]:p for p in demo["parameters"]}
        poly=polynomial(tree(demo["series"][0]["expression"],set(params)|{xid}),set(params)|{xid})
        adjustable={k for k,p in params.items() if p["min"]<p["max"]}
        # Exactly one coefficient parameter and one constant parameter, no
        # products/powers between parameters, and no extra independent terms.
        pairs=[k for k in poly if len(k)==2 and xid in k and len(set(k))==2]
        if len(pairs)!=1: return []
        slope=next(k for k in pairs[0] if k!=xid)
        intercepts=[k[0] for k in poly if len(k)==1 and k[0]!=xid]
        if len(intercepts)!=1 or not {slope,intercepts[0]}<=adjustable: return []
        intercept=intercepts[0]
        if not set(poly)<={(),(xid,),(intercept,),tuple(sorted((slope,xid)))}: return []
        if not demo["x"]["min"]<=0<=demo["x"]["max"]: return []
        xs=[0., demo["x"]["max"] if abs(demo["x"]["max"])>=abs(demo["x"]["min"]) else demo["x"]["min"]]
        if abs(xs[1])<1e-8: return []
        a=poly[pairs[0]];b=poly[(intercept,)];c=poly.get((),0.);d=poly.get((xid,),0.)
        result=[]
        for n,(x,pid) in enumerate(zip(xs,[intercept,slope])):
            scale=b if pid==intercept else a*x
            offset=(a*values[slope]*x if pid==intercept else b*values[intercept])+c+d*x
            if abs(scale)<1e-8: return []
            ys=[a*params[slope][u]*x+b*params[intercept][v]+c+d*x for u in ("min","max") for v in ("min","max")]
            if max(map(abs,ys))>1e6: return []
            result.append(dict(id=demo["series"][0]["id"]+"_anchor_"+pid,object_id=demo["series"][0]["id"],
                semantic_id=semantic_id,label=params[pid]["label"],gesture="drag_along_axis",coordinate_space="world",dimensions=1,
                parameter_ids=[pid],position=[x,scale*values[pid]+offset],bounds=[x,min(ys),x,max(ys)],
                inverse=dict(kind="affine",parameter_id=pid,scale=scale,offset=offset,x=x,
                    constant=c+d*x,coefficients={slope:a*x,intercept:b}),source_pages=demo["source_pages"]))
        return result
    except (ValueError,TypeError,KeyError,SyntaxError,OverflowError): return []


def semantic_target(demo, path, catalog, analysis=None):
    """Use an unambiguous existing lesson-to-formal reference, never a new ID."""
    ids=set()
    for step in (path or {}).get("steps",[]):
        if step["id"] in demo["related_step_ids"]:
            for ref in step.get("visual_refs",[]):
                identifier=ref.get("id")
                if identifier in catalog: ids.add(identifier)
    if len(ids)==1:return next(iter(ids))
    # A model-declared central relation can explicitly own several mapped
    # parameter/anchor concepts. Require direct graph links to EVERY related
    # lesson reference; labels and equation/topic words play no role.
    graph=(analysis or {}).get("concept_map")
    if not ids or (analysis or {}).get("primary_visualization",{}).get("type")!="concept_map" or not isinstance(graph,dict) or graph.get("suitable") is not True:return None
    nodes=graph.get("nodes",[]);edges=graph.get("edges",[])
    if not isinstance(nodes,list) or not 2<=len(nodes)<=24 or not isinstance(edges,list) or len(edges)>48:return None
    known={n.get("id") for n in nodes if isinstance(n,dict) and isinstance(n.get("id"),str)}
    if len(known)!=len(nodes) or not known<=catalog.keys():return None
    centers=[n["id"] for n in nodes if n.get("role")=="central"]
    if len(centers)!=1:return None
    root=centers[0];children={root}
    for edge in edges:
        if not isinstance(edge,dict) or edge.get("source") not in known or edge.get("target") not in known:return None
        if edge["source"]==root:children.add(edge["target"])
    return root if ids<=children else None


def revision(saved):
    """Other existing controls invalidate gestures without owning a second state."""
    from scene.state import fingerprint
    signature=fingerprint(saved["values"])
    if saved.get("manipulation_signature")!=signature:
        saved["manipulation_signature"]=signature
        saved["manipulation_revision"]=saved.get("manipulation_revision",-1)+1
    return saved["manipulation_revision"]


def commit(demo,saved,identity,event,semantic_id,focus):
    target=valid_event(event,identity,revision(saved),saved.get("gesture_token"),targets(demo,saved["values"],semantic_id))
    if target is None or event["time"]!=0: return False
    from interactive_lab import compute_curves
    from safe_math import evaluate_expression
    try:
        values=saved["values"]|invert(target,{p["id"]:p for p in demo["parameters"]},saved["values"],event["x"],event["y"])
        compute_curves(demo,values)
        for metric in demo["derived_metrics"]: evaluate_expression(metric["expression"],values)
        if not focus(target["semantic_id"]): return False
        saved.update(values=values,gesture_token=event["token"],gesture_ack=event["token"])
        saved["manipulation_signature"]=None
        revision(saved)
        return True
    except (ValueError,TypeError,KeyError,OverflowError): return False


def commit_focus(demo,saved,identity,event,semantic_id,focus):
    target=focus_event(event,identity,revision(saved),saved.get("gesture_token"),targets(demo,saved["values"],semantic_id),0.)
    if target is None or not focus(target["semantic_id"]):return False
    saved.update(gesture_token=event["token"],gesture_ack=event["token"],manipulation_revision=saved["manipulation_revision"]+1)
    return True
