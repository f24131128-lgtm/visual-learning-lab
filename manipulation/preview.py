"""Bounded numeric-only tentative previews; committed engines stay authoritative."""
import itertools
import json

import numpy as np

MAX_PREVIEW_VALUES = 100_000
MAX_PREVIEW_BYTES = 900_000
PREVIEW_FRAMES = 40


def bake(parameters, current, identifiers, project):
    """1D or 2D parameter lattice, no source/model expressions sent to browser.

    Every preview is produced by the existing safe projection engine. Linear
    interpolation is intentionally approximate, visibly marked as tentative.
    Release recomputes/validates exact state; a failed preview never hides the
    normal controls. Numeric cache owners bound entries independently.
    """
    if not 1<=len(identifiers)<=2: raise ValueError("Preview dimensions")
    params={p["id"]:p for p in parameters}
    size=33 if len(identifiers)==1 else 9
    axes=[np.linspace(params[k]["min"],params[k]["max"],size).tolist() for k in identifiers]
    rows=[]; count=0
    def plain(value):
        nonlocal count
        if isinstance(value,dict): return {k:plain(v) for k,v in value.items()}
        if isinstance(value,(list,tuple)): return [plain(v) for v in value]
        if type(value) in (int,float) or isinstance(value,np.floating):
            count+=1
            if count>MAX_PREVIEW_VALUES or not np.isfinite(value): raise ValueError("Preview bound")
            # Preview transport precision only; canonical engines retain floats.
            return float(f"{float(value):.6g}")
        raise ValueError("Non-numeric preview")
    for values in itertools.product(*axes):
        params_now=current|dict(zip(identifiers,values))
        rows.append(plain(project(params_now)))
    result=dict(parameter_ids=identifiers,axes=axes,rows=rows)
    if len(json.dumps(result,allow_nan=False).encode())>MAX_PREVIEW_BYTES: raise ValueError("Preview bytes")
    return result


def world_projection(scene,parameters):
    from scene.world.engine import frames
    data=frames(scene|{"time":scene["time"]|{"frames":PREVIEW_FRAMES}},parameters)
    return dict(domain=[data["domain"]["min"],data["domain"]["max"]],times=data["times"],
        objects={o["id"]:data["projections"][o["id"]] for o in scene["objects"]},
        curves={s["id"]:data["projections"][s["id"]][0] for s in scene["series"]},
        metrics={m["id"]:data["projections"][m["id"]][0] for m in scene["metrics"]})


def lab_projection(demo,values):
    from safe_math import evaluate_expression
    x=np.linspace(demo["x"]["min"],demo["x"]["max"],PREVIEW_FRAMES)
    return dict(domain=[0.,1.],times=[0.,1.],objects={},
        curves={s["id"]:dict(x=x.tolist(),y=np.broadcast_to(evaluate_expression(s["expression"],values|{demo["x"]["id"]:x}),x.shape).tolist()) for s in demo["series"]},
        metrics={m["id"]:[float(evaluate_expression(m["expression"],values))]*2 for m in demo["derived_metrics"]})
