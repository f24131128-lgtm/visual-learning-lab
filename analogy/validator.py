"""Reject unsafe declarations before any renderer or state mutation."""
import copy
import json
import math
import re
import hashlib
from safe_math import valid_variable
from .schema import SCHEMA, MAX_PAYLOAD, PRIMITIVES
from .engine import validate_math, FIELDS, REQUIRED_FIELDS
from .diagnostics import Rejection, summary


def shape(value, schema, path="$"):
    kind=schema["type"]
    if kind=="object":
        if not isinstance(value,dict) or set(value)!=set(schema["properties"]): raise Rejection("envelope_fields",path)
        for k,s in schema["properties"].items(): shape(value[k],s,path+"."+k)
    elif kind=="array":
        if not isinstance(value,list) or not schema["minItems"]<=len(value)<=schema["maxItems"]: raise Rejection("array_bounds",path)
        for i,v in enumerate(value): shape(v,schema["items"],f"{path}[{i}]")
    elif kind=="string":
        if not isinstance(value,str) or len(value)>schema.get("maxLength",64) or re.search(r"[\x00-\x08\x0b-\x1f\x7f]|<[^>]*>",value): raise Rejection("text",path)
    elif kind=="boolean":
        if type(value) is not bool: raise Rejection("boolean",path)
    else:
        if type(value) not in ((int,) if kind=="integer" else (int,float)) or not math.isfinite(value) or not schema.get("minimum",-math.inf)<=value<=schema.get("maximum",math.inf): raise Rejection("numeric_bounds",path)
    if "enum" in schema and value not in schema["enum"] and not re.fullmatch(r"\$\.primitives\[\d+\]\.type",path): raise Rejection("enum",path)


def local_ids(spec, catalog):
    """Namespace renderer IDs by reference type; preserve formal and math identity."""
    seen=set(catalog)|{"time","index"}
    for group in ("parameters","quantities"):
        for n,item in enumerate(spec[group]):
            i=item["id"]
            if not valid_variable(i) or i in seen: raise Rejection("numeric_ids",f"$.{group}[{n}].id")
            seen.add(i)
    aliases={}
    for group in ("candidates","analogy_entities","mappings","primitives"):
        aliases[group]={}
        for n,item in enumerate(spec[group]):
            old=item["id"]
            if not old.strip() or old in aliases[group]: raise Rejection("duplicate_local_id",f"$.{group}[{n}].id")
            i=old
            if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,47}",i) or i in seen:
                i="aw_"+group[:3]+"_"+hashlib.sha256((group+":"+old).encode()).hexdigest()[:16]
                if i in seen: raise Rejection("derived_id_collision",f"$.{group}[{n}].id")
                spec["recoveries"].append(dict(code="derived_local_id",path=f"$.{group}[{n}].id"))
            aliases[group][old]=i; item["id"]=i; seen.add(i)
    def alias(group,value): return aliases[group].get(value,value)
    spec["selected_candidate"]=alias("candidates",spec["selected_candidate"])
    for m in spec["mappings"]: m["analogy_id"]=alias("analogy_entities",m["analogy_id"])
    for p in spec["parameters"]: p["mapping_id"]=alias("mappings",p["mapping_id"])
    for p in spec["primitives"]: p["entity_id"]=alias("analogy_entities",p["entity_id"])
    for a in spec["annotations"]: a["entity_id"]=alias("analogy_entities",a["entity_id"])


def correspondence_cards(spec, missing, catalog):
    """A fixed schematic for validated generated concepts, never invented physics."""
    used=set(catalog)|{item["id"] for group in ("candidates","analogy_entities","mappings","parameters","quantities","primitives") for item in spec[group]}
    for n,e in enumerate(spec["analogy_entities"]):
        if e["id"] not in missing: continue
        identifier="aw_card_"+hashlib.sha256(e["id"].encode()).hexdigest()[:16]
        if identifier in used: raise Rejection("derived_id_collision","$.primitives")
        used.add(identifier)
        spec["primitives"].append(dict(id=identifier,entity_id=e["id"],type="disc",label=e["label"],x=str((n%4)*3),y=str(-(n//4)*2),x2="1",y2="1",radius="0.35",value="0",visible="1",count=1,color="gray",control_parameter="",wrap_x=False,wrap_min=0.,wrap_max=1.))
    if missing: spec["recoveries"].append(dict(code="correspondence_cards",path="$.primitives"))
    if len(spec["primitives"])>24 or sum(p["count"] for p in spec["primitives"])>64: raise Rejection("primitive_work","$.primitives")


def visual_defaults(spec):
    """Treat blank unused slots as absent; never replace nonempty unsafe input."""
    incomplete=set()
    for n,p in enumerate(spec["primitives"]):
        required=REQUIRED_FIELDS.get(p["type"],set(FIELDS)-{"visible"})
        for field in FIELDS:
            p[field]=p[field].strip()
            if p[field]: continue
            if field in required: incomplete.add(p["id"])
            # Missing geometry is a placeholder for safety checks ONLY; the
            # entire incomplete visual is omitted before it reaches a renderer.
            p[field]="1" if field=="visible" or (p["type"]=="rectangle" and field in ("x2","y2")) else "0.15" if field=="radius" and p["type"] in ("disc","tokens") else "0"
            spec["recoveries"].append(dict(code="missing_visual_field" if field in required else "unused_visual_default",path=f"$.primitives[{n}].{field}"))
    return incomplete


def normalize(raw, catalog, registry, allowed_pages, focus, progress=None):
    shape(raw,SCHEMA)
    if len(json.dumps(raw,allow_nan=False).encode())>MAX_PAYLOAD: raise Rejection("declaration_size")
    spec=copy.deepcopy(raw)
    try: return _normalize(spec,catalog,registry,allowed_pages,focus)
    finally:
        if progress is not None:
            progress["normalized"]=summary(spec)
            progress["recoveries"]=spec.get("recoveries",[])[:32]


def _normalize(spec, catalog, registry, allowed_pages, focus):
    if not spec["reason"].strip(): raise Rejection("reason")
    if not spec["suitable"]:
        if any(spec[k] for k in ("formal_entities","analogy_entities","mappings","parameters","quantities","primitives","annotations")): raise Rejection("unsuitable_scene")
        return spec
    for k in ("title","learning_goal","analogy_domain","explanation"):
        if not spec[k].strip(): raise Rejection("required_teaching_text")
    if spec["formal_focus"]!=focus or focus not in catalog: raise Rejection("formal_focus")
    entities={e["id"] for e in spec["formal_entities"]}
    if not entities or focus not in entities or len(entities)!=len(spec["formal_entities"]): raise Rejection("formal_entity_ids")
    for n,e in enumerate(spec["formal_entities"]):
        if e["id"] not in catalog or catalog[e["id"]]["kind"] in ("parameter","time") or not set(e["source_pages"])<=set(allowed_pages)&set(catalog[e["id"]]["pages"]) or len(set(e["source_pages"]))!=len(e["source_pages"]): raise Rejection("provenance",f"$.formal_entities[{n}].source_pages")
        # Retain the validated catalog pages, not a model-authored source quote.
        e["source_pages"]=[p for p in catalog[e["id"]]["pages"] if p in allowed_pages]
    spec["recoveries"]=[]
    local_ids(spec,catalog)
    candidate=next((c for c in spec["candidates"] if c["id"]==spec["selected_candidate"]),None)
    if not candidate or candidate["fidelity"]<.65 or candidate["misconception_risk"]>.45 or min(candidate[k] for k in ("clarity","visualizability"))<.4: raise Rejection("unsuitable_fidelity","$.candidates")
    analogies={e["id"] for e in spec["analogy_entities"]}
    mappings={m["id"]:m for m in spec["mappings"]}
    pairs={(m["formal_id"],m["analogy_id"]) for m in mappings.values()}
    if not analogies or {m["analogy_id"] for m in mappings.values()}!=analogies or len(pairs)!=len(mappings): raise Rejection("ambiguous_mappings","$.mappings")
    for n,m in enumerate(mappings.values()):
        if m["formal_id"] not in entities or m["fidelity"]<.65 or not m["relationship"].strip() or not m["explains"].strip(): raise Rejection("mapping",f"$.mappings[{n}]")
    if focus not in {m["formal_id"] for m in mappings.values()}: raise Rejection("unmapped_focus","$.mappings")
    if not spec["limitations"] or any(not l["breaks"].strip() or not l["misconception"].strip() for l in spec["limitations"]): raise Rejection("limitations")
    targets=set()
    for n,p in enumerate(spec["parameters"]):
        if not valid_variable(p["id"]) or not p["min"]<p["max"] or not p["min"]<=p["default"]<=p["max"] or p["step"]>p["max"]-p["min"] or (p["max"]-p["min"])/p["step"]>10000 or p["min"]+p["step"]==p["min"] or p["mapping_id"] not in mappings: raise Rejection("parameter",f"$.parameters[{n}]")
        if p["formal_target"]:
            target=registry.get(p["formal_target"]); mapping=mappings[p["mapping_id"]]
            if mapping["mode"]!="quantitative":
                p["formal_target"]=""; p["scale"]=1.; p["offset"]=0.
                spec["recoveries"].append(dict(code="qualitative_binding_omitted",path=f"$.parameters[{n}].formal_target"))
                continue
            if not target or mapping["formal_id"] not in target["semantic_ids"]: raise Rejection("formal_binding",f"$.parameters[{n}].formal_target")
            limits=sorted(p["scale"]*p[v]+p["offset"] for v in ("min","max"))
            if p["scale"]==0 or not all(math.isclose(a,b,rel_tol=1e-9,abs_tol=1e-9) for a,b in zip(limits,[target["min"],target["max"]])) or not math.isclose(p["scale"]*p["default"]+p["offset"],target["default"],rel_tol=1e-9,abs_tol=1e-9):
                p["formal_target"]=""; p["scale"]=1.; p["offset"]=0.
                spec["recoveries"].append(dict(code="binding_omitted",path=f"$.parameters[{n}].formal_target"))
            else:
                # Only surviving links reserve canonical controls. An omitted
                # optional link cannot block another valid link to that target.
                if p["formal_target"] in targets: raise Rejection("formal_binding",f"$.parameters[{n}].formal_target")
                targets.add(p["formal_target"])
    if any(not valid_variable(q["id"]) for q in spec["quantities"]): raise Rejection("quantity_name")
    parameters={p["id"] for p in spec["parameters"]}
    if sum(p["count"] for p in spec["primitives"])>64: raise Rejection("primitive_work","$.primitives")
    rendered=set()
    for n,p in enumerate(spec["primitives"]):
        if p["entity_id"] not in analogies or (p["type"]!="tokens" and p["count"]!=1): raise Rejection("primitive_reference",f"$.primitives[{n}]")
        if p["wrap_x"] and (p["type"]!="tokens" or p["wrap_min"]>=p["wrap_max"]): raise Rejection("wrap_domain")
        if p["type"] in PRIMITIVES: rendered.add(p["entity_id"])
        if p["control_parameter"]:
            param=next((v for v in spec["parameters"] if v["id"]==p["control_parameter"]),None)
            if not param or mappings[param["mapping_id"]]["analogy_id"]!=p["entity_id"]:
                p["control_parameter"]=""
                spec["recoveries"].append(dict(code="drag_omitted",path=f"$.primitives[{n}].control_parameter"))
    if any(a["entity_id"] not in analogies or not a["text"].strip() for a in spec["annotations"]): raise Rejection("annotation_reference","$.annotations")
    incomplete=visual_defaults(spec)
    # Even discarded visuals must pass AST, numeric and workload safety first.
    validate_math(spec)
    unsupported=[n for n,p in enumerate(spec["primitives"]) if p["type"] not in PRIMITIVES]
    for n in unsupported: spec["recoveries"].append(dict(code="unsupported_visual_omitted",path=f"$.primitives[{n}].type"))
    for n,p in enumerate(spec["primitives"]):
        if p["id"] in incomplete: spec["recoveries"].append(dict(code="incomplete_visual_omitted",path=f"$.primitives[{n}]"))
    spec["primitives"]=[p for p in spec["primitives"] if p["type"] in PRIMITIVES and p["id"] not in incomplete]
    rendered={p["entity_id"] for p in spec["primitives"]}
    correspondence_cards(spec,analogies-rendered,catalog)
    if unsupported or incomplete or analogies-rendered: validate_math(spec)
    return spec
