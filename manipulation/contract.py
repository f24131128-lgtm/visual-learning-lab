"""Small analytic inverse contract derived from provable forward shapes.

No topic names, general equation solver, model programs, or browser expressions.
Unsupported/ambiguous shapes retain their existing controls. The normalized
contract is application data, not a new model-controlled event handler language.
"""
import ast
import copy
import math

from safe_math import CONSTANTS, FUNCTIONS, validate_expression

VERSION = "1.0"
MAX_TARGETS = 4
MAX_COORDINATE = 1e6
MAX_AST_NODES = 256


def tree(expression, names, quantities=None):
    def parse(value):
        syntax=ast.parse(value,mode="eval")
        refs={n.id for n in ast.walk(syntax) if isinstance(n,ast.Name)}-CONSTANTS.keys()-FUNCTIONS.keys()
        if not refs <= set(names)|set(quantities or {}): raise ValueError("Unknown forward reference")
        validate_expression(value,refs)
        return syntax.body
    root = parse(expression)
    budget = [MAX_AST_NODES]
    def expand(node, visiting=()):
        budget[0] -= 1
        if budget[0] < 0: raise ValueError("Expansion bound")
        if isinstance(node, ast.Name) and node.id in (quantities or {}):
            if node.id in visiting: raise ValueError("Cyclic expansion")
            return expand(parse(quantities[node.id]), visiting+(node.id,))
        result = copy.copy(node)
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST): setattr(result, field, expand(value, visiting))
            elif isinstance(value, list): setattr(result, field, [expand(x, visiting) if isinstance(x, ast.AST) else x for x in value])
        return result
    return expand(root)


def affine(node, names):
    """Exact affine proof (addition, constant multiplication/division only)."""
    if isinstance(node, ast.Constant) and type(node.value) in (int, float):
        return float(node.value), {}
    if isinstance(node, ast.Name):
        if node.id in CONSTANTS: return float(CONSTANTS[node.id]), {}
        if node.id in names: return 0., {node.id: 1.}
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        c, terms = affine(node.operand, names)
        sign = -1 if isinstance(node.op, ast.USub) else 1
        return c*sign, {k: v*sign for k,v in terms.items()}
    if isinstance(node, ast.BinOp):
        a, aa = affine(node.left, names); b, bb = affine(node.right, names)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            sign = -1 if isinstance(node.op, ast.Sub) else 1
            terms = dict(aa)
            for k,v in bb.items(): terms[k] = terms.get(k, 0.)+sign*v
            return a+sign*b, {k:v for k,v in terms.items() if v != 0}
        if isinstance(node.op, ast.Mult) and not (aa and bb):
            return a*b, {k:v*(b if aa else a) for k,v in (aa or bb).items()}
        if isinstance(node.op, ast.Div) and not bb and abs(b)>1e-12:
            return a/b, {k:v/b for k,v in aa.items()}
    raise ValueError("Not affine")


def trig_product(node, function, names):
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == function and len(node.args)==1:
        return (1., {}), affine(node.args[0], names)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        for radius, trig in ((node.left,node.right),(node.right,node.left)):
            if isinstance(trig,ast.Call) and isinstance(trig.func,ast.Name) and trig.func.id==function and len(trig.args)==1:
                return affine(radius,names), affine(trig.args[0],names)
    raise ValueError("Not polar")


def number(value):
    if type(value) not in (int,float) or abs(value)>MAX_COORDINATE or not math.isfinite(value):
        raise ValueError("Invalid coordinate")
    return float(value)


def angular_solution(angle, offset, scale, parameter, current):
    if not math.isfinite(scale) or abs(scale)<1e-9: raise ValueError("Degenerate inverse")
    candidates = [(angle-offset+2*math.pi*k)/scale for k in range(-128,129)]
    candidates = [v for v in candidates if parameter["min"]-1e-12<=v<=parameter["max"]+1e-12]
    if not candidates: raise ValueError("No legal angle")
    return min(parameter["max"],max(parameter["min"], min(candidates,key=lambda v:abs(v-current))))


def invert(target, parameters, current, x, y):
    """Finite coordinates -> <=2 legal parameters. No arbitrary patches."""
    x,y=number(x),number(y)
    if not target["bounds"][0]<=x<=target["bounds"][2] or not target["bounds"][1]<=y<=target["bounds"][3]:
        raise ValueError("Outside gesture envelope")
    model=target["inverse"]; result={}
    if model["kind"] in ("circular","polar"):
        dx,dy=x-model["origin"][0],y-model["origin"][1]
        if math.hypot(dx,dy)<1e-8: raise ValueError("Undefined direction")
        aid=model["angle_id"]
        result[aid]=angular_solution(math.atan2(dy,dx),model["offset"],model["angle_scale"],parameters[aid],current[aid])
        if model["kind"]=="polar":
            result[model["radius_id"]]=(math.hypot(dx,dy)-model["radius_offset"])/model["radius_scale"]
    elif model["kind"]=="affine":
        result[model["parameter_id"]]=(y-model["offset"])/model["scale"]
    else: raise ValueError("Unsupported inverse")
    for key,value in result.items():
        p=parameters[key]
        if p["min"]==p["max"] or not math.isfinite(value) or not p["min"]-1e-10<=value<=p["max"]+1e-10:
            raise ValueError("Outside legal parameter range")
        result[key]=min(p["max"],max(p["min"],value))
    return result


def valid_event(event, identity, revision, last_token, targets):
    if not isinstance(event,dict) or set(event)!={"scene","revision","token","kind","target","x","y","time"}: return None
    if event["scene"]!=identity or type(event["revision"]) is not int or event["revision"]!=revision or event["kind"]!="manipulate": return None
    token=event["token"]
    if not isinstance(token,str) or not 1<=len(token)<=80 or token==last_token: return None
    try:
        number(event["x"]);number(event["y"]);number(event["time"])
    except ValueError: return None
    return next((t for t in targets if t["id"]==event["target"]),None)


def focus_event(event,identity,revision,last_token,targets,clock):
    if not isinstance(event,dict) or set(event)!={"scene","revision","token","kind","target","time"}: return None
    if event["scene"]!=identity or type(event["revision"]) is not int or event["revision"]!=revision or event["kind"]!="manipulation_focus": return None
    if type(event["time"]) not in (int,float) or event["time"]!=clock: return None
    token=event["token"]
    if not isinstance(token,str) or not 1<=len(token)<=80 or token==last_token: return None
    return next((t for t in targets if t["id"]==event["target"]),None)
