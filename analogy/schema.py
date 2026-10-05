"""Strict compiler contract and application-controlled primitive vocabulary."""
VERSION = "1.1"
MAX_PAYLOAD = 450_000
MAX_FRAMES = 120
MAX_TOKENS = 16
PRIMITIVES = ("rectangle", "disc", "segment", "tokens", "curve", "meter")


def obj(fields):
    return dict(type="object", properties=fields, required=list(fields), additionalProperties=False)


def arr(item, maximum, minimum=0):
    return dict(type="array", items=item, minItems=minimum, maxItems=maximum)


def txt(limit=600):
    return dict(type="string", maxLength=limit)


def num(low=-10000, high=10000):
    return dict(type="number", minimum=low, maximum=high)


ID = txt(64)
SCORE = num(0, 1)
SCHEMA = obj(dict(
    version=dict(type="string", enum=[VERSION]), suitable=dict(type="boolean"), reason=txt(),
    title=txt(160), learning_goal=txt(), formal_focus=ID, analogy_domain=txt(160), explanation=txt(1000),
    candidates=arr(obj(dict(id=ID, title=txt(160), clarity=SCORE, visualizability=SCORE,
        interaction=SCORE, fidelity=SCORE, misconception_risk=SCORE)), 3), selected_candidate=ID,
    formal_entities=arr(obj(dict(id=ID, source_pages=arr(dict(type="integer"), 8))), 16),
    analogy_entities=arr(obj(dict(id=ID, label=txt(160))), 16),
    mappings=arr(obj(dict(id=ID, formal_id=ID, analogy_id=ID, relationship=txt(), explains=txt(),
        fidelity=SCORE, mode=dict(type="string", enum=["quantitative", "qualitative"]))), 16),
    limitations=arr(obj(dict(breaks=txt(), misconception=txt())), 6),
    parameters=arr(obj(dict(id=ID, label=txt(160), unit=txt(32), min=num(), max=num(), default=num(), step=num(0.000001, 10000),
        mapping_id=ID, formal_target=txt(160), scale=num(), offset=num())), 4),
    quantities=arr(obj(dict(id=ID, expression=txt(400))), 24),
    time=obj(dict(duration=num(0.1, 30), frames=dict(type="integer", minimum=2, maximum=MAX_FRAMES))),
    primitives=arr(obj(dict(id=ID, entity_id=ID, type=dict(type="string", enum=list(PRIMITIVES)), label=txt(160),
        x=txt(400), y=txt(400), x2=txt(400), y2=txt(400), radius=txt(400), value=txt(400), visible=txt(400),
        count=dict(type="integer", minimum=1, maximum=MAX_TOKENS),
        wrap_x=dict(type="boolean"), wrap_min=num(-100,100), wrap_max=num(-100,100),
        color=dict(type="string", enum=["blue", "orange", "green", "purple", "gray"]), control_parameter=ID)), 24),
    annotations=arr(obj(dict(entity_id=ID, text=txt())), 8),
))

INSTRUCTIONS = """Compile a source-grounded teaching analogy, never executable code or markup.
Use only supplied formal semantic IDs and source pages. Do not invent source facts, geometry or provenance.
Analogy entities and their visuals are generated explanatory aids, not source evidence or physical identities.
In ONE response assess 1-3 candidates and select one with fidelity >= .65 and misconception_risk <= .45.
If none is defensible emit suitable=false with reason and empty scene arrays (time still required).
Every analogy entity needs at least one mapping to an exact supplied formal entity; each mapping needs relationship, explains and fidelity >= .65.
One analogy entity may explain several formal concepts through distinct mappings. Never duplicate a formal_id/analogy_id pair. Map the requested formal_focus explicitly.
Use unique local IDs within each group; application code can namespace renderer IDs. Never alter supplied formal IDs.
Mandatory limitations describe where the analogy breaks AND a misconception to avoid.
Use parameters (max 4), acyclic scalar quantities (max 24), safe arithmetic/sin/cos/sqrt/abs; no booleans, indexing, attributes or calls beyond safe_math.
Reserved time runs 0..duration, index identifies a repeated token 0..count-1. Primitive expressions use time/index/parameters/quantities.
rectangle: x,y center, x2,y2 positive width/height; disc/tokens: x,y center,radius; segment: x,y to x2,y2; curve: x,y path over time; meter: x,y with value. Numeric visible>=.5 shows a primitive.
All expression slots remain required schema keys. Unused fields may be empty strings: radius/value for rectangle or segment; x2/y2/value for disc/tokens; x2/y2/radius/value for curve; x2/y2/radius for meter. Application code supplies safe numeric auxiliaries. Use visible="1" by default. Never put prose, null, placeholders such as N/A, or code in expression slots.
All positions/dimensions <=100 absolute, radius <=20, expression results <=10000. Tokens count <=16, total repeated objects <=64, frames<=120.
For repeated tokens only, wrap_x=true wraps the computed x coordinate into [wrap_min,wrap_max) using fixed numeric projection. Use this for continuous unidirectional streams rather than misleading back-and-forth oscillation. Its raw travel stays within the 10000 numeric limit; the wrapped displayed x and other geometry stay within 100. Otherwise wrap_x=false, with x itself within 100.
Motion is defined through time expressions; do not output transition scripts. Labels and annotations are plain text.
control_parameter optionally names a declared parameter for a horizontal drag control; empty disables drag.
formal_target optionally names an EXACT supplied parameter registry key. Only quantitative mappings may bind.
Binding is formal_value=scale*analogy_value+offset, finite nonzero scale; endpoints MUST match the full formal range and defaults MUST match.
An empty formal_target means an independent teaching control, never claim quantitative formal synchronization.
Only bind a parameter whose supplied semantic_ids contains the mapping's formal_id. No guessed label matching.
If its mapping is qualitative, formal_target MUST be empty. Prefer an independent teaching control over an uncertain quantitative binding.
Runtime details are optional: use empty parameters/quantities/primitives/annotations arrays if you cannot provide a safe coherent visualization. The application can show a correspondence schematic from the validated concepts; never invent physics to fill required runtime fields.
Give intuitive controls and visible effects; maintain source-supported mathematical relationships. Never imply a new physical law from an analogy.
"""
