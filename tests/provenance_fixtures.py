"""Explicit new-contract educational fixtures, never production migrations."""
import copy


def declared_parameter(p):
    p = copy.deepcopy(p)
    p.update(provenance="source_variable", expose_control=True, source_baseline_ref=None,
             source_evidence="This test source defines this variable.", source_pages=p.get("source_pages", [1]))
    return p


def declared_demo(raw, *, runtime_time=False, refs=()):
    raw = copy.deepcopy(raw)
    raw["source_facts"] = []
    raw["x"].update(semantic_role="runtime_time" if runtime_time else "independent_variable",
                    provenance=None if runtime_time else "source_variable")
    raw["parameters"] = [declared_parameter(p) | {"semantic_refs": list(refs)} for p in raw["parameters"]]
    for p in raw["parameters"]: p["source_pages"] = list(raw["source_pages"])
    for group in ("series", "derived_metrics"):
        for item in raw[group]: item.update(provenance="derived", semantic_refs=list(refs))
    return raw


def declared_world(raw):
    from scene.world.schema import VERSION
    raw = copy.deepcopy(raw)
    raw.update(scene_version=VERSION, source_facts=[])
    raw["parameters"] = [declared_parameter(p) for p in raw["parameters"]]
    for q in raw["quantities"]: q["provenance"] = "derived"
    return raw


def declared_analysis(raw):
    """Explicit synthetic declaration of captured mathematical shapes, test-only.

    This is never an automatic legacy migration or a new model output. Captured
    bytes are untouched; the production policy for those bytes stays read-only.
    """
    raw=copy.deepcopy(raw)
    lab=raw.get("interactive_lab")
    if isinstance(lab,dict):
        lab["version"]="2.0"
        lab["demos"]=[declared_demo(d) for d in lab.get("demos",[])]
    return raw
