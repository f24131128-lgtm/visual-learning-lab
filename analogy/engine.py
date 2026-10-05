"""One bounded numerical projection engine for every analogy domain."""
import itertools
import json
import math
import hashlib
import numpy as np
from scene.world.engine import calculate, check_expression, references
from .schema import MAX_PAYLOAD
from .diagnostics import Rejection

FIELDS = ("x", "y", "x2", "y2", "radius", "value", "visible")
# Geometry/value fields actually consumed by the fixed renderer. Other fields
# are transport/label auxiliaries, not mandatory model-authored mathematics.
REQUIRED_FIELDS = {
    "rectangle": {"x","y","x2","y2"}, "disc": {"x","y","radius"},
    "tokens": {"x","y","radius"}, "segment": {"x","y","x2","y2"},
    "curve": {"x","y"}, "meter": {"x","y","value"},
}


def expression_detail(expression, allowed, primitive_type="", field=""):
    """Controlled classification, never the expression or unknown symbol names."""
    problem="unsupported_math"
    if not expression.strip(): problem="empty"
    else:
        try:
            if references(expression)-set(allowed): problem="unknown_symbol"
        except (SyntaxError,ValueError,RecursionError): problem="syntax"
    return dict(primitive_type=primitive_type,field=field,length=len(expression),
                fingerprint=hashlib.sha256(expression.encode()).hexdigest()[:16],problem=problem,
                used_for_geometry=field in REQUIRED_FIELDS.get(primitive_type,set(FIELDS)))


def numeric_value(expression, values, path, primitive_type="", field=""):
    try: return calculate(expression,values)
    except (ValueError,KeyError,TypeError,OverflowError) as error:
        detail=expression_detail(expression,values,primitive_type,field)
        detail["problem"]="numeric"
        raise Rejection("numeric_expression",path,detail) from error


def bounded_array(a, low, high, primitive, n, field, index, times, values, code, stage):
    invalid=~np.isfinite(a)|(a<low)|(a>high)
    if not np.any(invalid): return
    detail=expression_detail(primitive[field],values,primitive["type"],field)
    detail.update(problem="bounds",limit_min=low,limit_max=high,
        observed_min=float(a.min()) if np.all(np.isfinite(a)) else None,
        observed_max=float(a.max()) if np.all(np.isfinite(a)) else None,
        token_index=index,time=float(times[np.flatnonzero(invalid)[0]]),
        wrap_x=primitive["wrap_x"],check_stage=stage)
    raise Rejection(code,f"$.primitives[{n}].{field}",detail)


def project(spec, parameters):
    if set(parameters) != {p["id"] for p in spec["parameters"]}: raise ValueError("parameter keys")
    for p in spec["parameters"]:
        v = parameters[p["id"]]
        if type(v) not in (int, float) or not math.isfinite(v) or not p["min"] <= v <= p["max"]: raise ValueError("parameter bounds")
    times = np.linspace(0., spec["time"]["duration"], spec["time"]["frames"])
    quantities = {q["id"]: q for q in spec["quantities"]}
    quantity_indices={q["id"]:n for n,q in enumerate(spec["quantities"])}
    outputs = []
    bounds = [-1., 1., -1., 1.]
    for n,primitive in enumerate(spec["primitives"]):
        for index in range(primitive["count"]):
            values = dict(parameters, time=times, index=float(index))
            for identifier in spec["quantity_order"]:
                values[identifier] = numeric_value(quantities[identifier]["expression"],values,f"$.quantities[{quantity_indices[identifier]}].expression",field="expression")
            data = {}
            for field in FIELDS:
                a = np.broadcast_to(numeric_value(primitive[field],values,f"$.primitives[{n}].{field}",primitive["type"],field), times.shape)
                bounded_array(a,-10000.,10000.,primitive,n,field,index,times,values,"projection_bounds","raw_numeric")
                data[field] = a.tolist()
            x, y, x2, y2, r = [np.array(data[k]) for k in ("x", "y", "x2", "y2", "radius")]
            if primitive["wrap_x"]:
                x=primitive["wrap_min"]+np.remainder(x-primitive["wrap_min"],primitive["wrap_max"]-primitive["wrap_min"])
                data["x"]=x.tolist()
            # Wrapped token travel is a bounded numeric phase, not its displayed
            # position. Check the actual renderer coordinates after wrapping;
            # raw arithmetic still obeys the unchanged 10,000 limit above.
            for field,a in (("x",x),("y",y),("x2",x2),("y2",y2)):
                bounded_array(a,-100.,100.,primitive,n,field,index,times,values,"geometry_bounds","rendered_geometry")
            bounded_array(r,0.,20.,primitive,n,"radius",index,times,values,"geometry_bounds","rendered_geometry")
            if primitive["type"] in ("disc", "tokens") and np.any(r<=0): raise ValueError("radius")
            if primitive["type"] == "rectangle":
                if np.any(x2<=0) or np.any(y2<=0): raise ValueError("dimensions")
                xmin,xmax,ymin,ymax = x-x2/2,x+x2/2,y-y2/2,y+y2/2
            elif primitive["type"] in ("segment", "curve"):
                xmin,xmax,ymin,ymax = np.minimum(x,x2) if primitive["type"]=="segment" else x, np.maximum(x,x2) if primitive["type"]=="segment" else x, np.minimum(y,y2) if primitive["type"]=="segment" else y, np.maximum(y,y2) if primitive["type"]=="segment" else y
            else: xmin,xmax,ymin,ymax=x-r,x+r,y-r,y+r
            bounds=[min(bounds[0],float(xmin.min())),max(bounds[1],float(xmax.max())),min(bounds[2],float(ymin.min())),max(bounds[3],float(ymax.max()))]
            outputs.append({k:primitive[k] for k in ("id","entity_id","type","label","color","control_parameter")} | dict(index=index, data=data))
    result=dict(times=times.tolist(), objects=outputs, bounds=bounds)
    if len(json.dumps(result, allow_nan=False).encode()) > MAX_PAYLOAD: raise ValueError("numeric payload")
    return result


def validate_math(spec):
    allowed={p["id"] for p in spec["parameters"]}|{"time", "index"}
    pending={q["id"]:q for q in spec["quantities"]}; order=[]
    all_ids=allowed|set(pending)
    for n,q in enumerate(pending.values()):
        try: check_expression(q["expression"], all_ids)
        except (ValueError,SyntaxError,RecursionError) as error: raise Rejection("unsafe_expression",f"$.quantities[{n}].expression",expression_detail(q["expression"],all_ids,field="expression")) from error
    while pending:
        ready=[i for i,q in pending.items() if references(q["expression"]) <= allowed]
        if not ready: raise Rejection("quantity_cycle","$.quantities")
        for i in ready: order.append(i); allowed.add(i); pending.pop(i)
    for n,p in enumerate(spec["primitives"]):
        for f in FIELDS:
            try: check_expression(p[f], allowed)
            except (ValueError,SyntaxError,RecursionError) as error: raise Rejection("unsafe_expression",f"$.primitives[{n}].{f}",expression_detail(p[f],allowed,p["type"],f)) from error
    spec["quantity_order"]=order
    # Bounded corners plus defaults; actual changes are independently rechecked.
    params=spec["parameters"]
    samples=[{p["id"]:p["default"] for p in params}]
    samples += [dict(zip([p["id"] for p in params], values)) for values in itertools.product(*[(p["min"],p["max"]) for p in params])]
    try: envelopes=[project(spec,v)["bounds"] for v in samples]
    except Rejection: raise
    except ValueError as error:
        reasons={"projection bounds":"projection_bounds","geometry bounds":"geometry_bounds","radius":"radius","dimensions":"dimensions","numeric payload":"numeric_payload"}
        raise Rejection(reasons.get(str(error),"numeric_projection"),"$.primitives") from error
    spec["bounds"]=[min(b[0] for b in envelopes),max(b[1] for b in envelopes),min(b[2] for b in envelopes),max(b[3] for b in envelopes)]
