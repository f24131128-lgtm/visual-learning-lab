"""Pure validation, evidence graph, ranking and formula trace."""

import copy
import hashlib
import math
import re
from collections import Counter

from scene.state import fingerprint
from .schema import ATLAS_SCHEMA, VERSION, MAX_PAGES, MAX_REGIONS, MAX_PER_PAGE, MAX_EDGES, TYPES, LAYERS


def semantic_catalog(scene=None, analysis=None):
    """Retain existing stable IDs. Representation IDs are links, not new focus."""
    result = {}
    if scene and scene.get("domain") == "spatial_dynamics":
        for item in scene["parameters"] + scene["quantities"]:
            result[item["id"]] = dict(label=item["label"], pages=item["source_pages"],
                kind="quantity" if "expression" in item else "parameter",
                equation=item.get("expression", ""), representations=[])
        result["time"] = dict(label="Time", pages=[], kind="time", equation="", representations=[])
        for group in ("objects", "series", "metrics"):
            for item in scene[group]:
                bind = next(b for b in scene["bindings"] if b["target_id"] == item["id"])
                refs = set(bind["quantity_ids"] + [item["semantic_id"]] + item.get("origin_quantity_ids", []))
                queue = list(refs)
                while queue:
                    current = queue.pop()
                    dependencies = set(re.findall(r"\b[A-Za-z][A-Za-z0-9_]*\b", result[current]["equation"])) & result.keys()
                    for dependency in dependencies-refs:
                        refs.add(dependency); queue.append(dependency)
                for identifier in refs:
                    result[identifier]["representations"].append(dict(id=item["id"], label=item["label"], kind=group))
    elif scene:
        for group in ("events", "outcomes", "focus_targets"):
            for item in scene.get(group, []):
                result[item["id"]] = dict(label=item["label"], pages=item["source_pages"], kind=group,
                    equation=item.get("expression", ""), representations=[dict(id=v["id"], label=v["title"], kind=v["type"]) for v in scene.get("views", []) if item["id"] in v["semantic_ids"]])
    else:
        for group in ("concept_map", "visual_flow"):
            graph = (analysis or {}).get(group)
            items = graph.get("nodes", []) if isinstance(graph, dict) else []
            if not isinstance(items, list): continue
            for item in items[:24]:
                if (isinstance(item, dict) and isinstance(item.get("id"), str)
                        and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", item["id"])
                        and _text(item.get("label"), 160, False) and item["id"] not in result):
                    pages = item.get("source_pages", [])
                    result[item["id"]] = dict(label=item["label"], pages=[p for p in pages[:8] if type(p) is int and p > 0] if isinstance(pages, list) else [], kind=group, equation="", representations=[])
        # Comparison items already have canonical IDs, just like graph nodes.
        # Their provenance belongs to their actual cells, not every PDF page.
        comparison = (analysis or {}).get("comparison")
        if isinstance(comparison, dict) and comparison.get("suitable") is True:
            items, criteria = comparison.get("items"), comparison.get("criteria")
            if isinstance(items, list) and isinstance(criteria, list):
                for item in items[:4]:
                    if (not isinstance(item, dict) or not isinstance(item.get("id"), str)
                            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", item["id"])
                            or not _text(item.get("label"), 160, False) or item["id"] in result):
                        continue
                    pages = []
                    for criterion in criteria[:8]:
                        cells = criterion.get("values") if isinstance(criterion, dict) else None
                        for cell in cells[:4] if isinstance(cells, list) else []:
                            if not isinstance(cell, dict) or cell.get("item_id") != item["id"]:
                                continue
                            refs = cell.get("source_pages")
                            if isinstance(refs, list):
                                pages.extend(p for p in refs[:8] if type(p) is int and p > 0)
                    result[item["id"]] = dict(label=item["label"], pages=list(dict.fromkeys(pages))[:8],
                        kind="comparison", equation="", representations=[])
        # Only when no structured identity exists, derive stable identities for
        # already analyzed concepts. Never replace graph/comparison IDs with labels
        # or positions. No fabricated pages or additional semantic interpretation.
        if not result:
            concepts = (analysis or {}).get("key_concepts")
            for item in concepts[:24] if isinstance(concepts, list) else []:
                if not isinstance(item, dict) or not _text(item.get("concept"), 160, False):
                    continue
                label = item["concept"]
                identifier = "concept_" + hashlib.sha256(label.encode("utf-8")).hexdigest()[:24]
                refs = item.get("source_pages")
                pages = [p for p in refs[:8] if type(p) is int and p > 0] if isinstance(refs, list) else []
                if identifier not in result:
                    result[identifier] = dict(label=label, pages=pages, kind="key_concept", equation="", representations=[])
    return result


def semantic_fingerprint(scene, catalog):
    # Includes binding/equation identity, never focus/time/parameter values.
    if scene and scene.get("domain") == "probability_sets":
        from scene.schema import LEARNING_SCENE_SCHEMA
        # Normalized probability scenes also hold derived finite-set/path
        # indexes, including tuple dict keys. Hash the declarative identity,
        # not those non-JSON runtime indexes; all are derived from these fields.
        scene = {k: scene[k] for k in LEARNING_SCENE_SCHEMA["properties"]}
    return fingerprint([scene, catalog])


def rank_pages(analysis, catalog, allowed, focus=None):
    scores = {p: 0 for p in allowed if type(p) is int and p > 0}
    def add(pages, score):
        for p in pages:
            if type(p) is int and p in scores: scores[p] += score
    for item in analysis.get("visual_evidence", [])[:32]:
        if isinstance(item, dict): add([item.get("page")], 10)
    for item in catalog.values(): add(item["pages"], 2)
    if focus in catalog: add(catalog[focus]["pages"], 12)
    for item in analysis.get("key_concepts", [])[:24]:
        if isinstance(item, dict) and isinstance(item.get("source_pages"), list): add(item["source_pages"], 1)
    return sorted(scores, key=lambda p: (-scores[p], p))


def bbox_valid(box):
    if not isinstance(box, dict) or set(box) != {"x0", "y0", "x1", "y1"}: return False
    if any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 1 for v in box.values()): return False
    w, h = box["x1"]-box["x0"], box["y1"]-box["y0"]
    return w >= .005 and h >= .005 and w*h >= .0001


def _text(value, bound, empty=True, native_text=False):
    # Data-only plain text. No generated markup enters Markdown/SVG/HTML.
    if not isinstance(value, str) or (not empty and not value.strip()) or len(value) > bound:
        return False
    if native_text:
        # Native PDF comparisons are literal data, rendered through st.text /
        # frontend textContent, not markup. Keep controls and tag-shaped input
        # forbidden; model-generated Atlas text keeps its stricter policy.
        return not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]|<[^>]*>", value)
    return not re.search(r"[<>\x00-\x08\x0b\x0c\x0e-\x1f]", value)


def extracted_page_text(page_texts, page):
    """Missing native extraction is not source text or verified evidence."""
    value = page_texts.get(page) if isinstance(page_texts, dict) else None
    return value if isinstance(value, str) else ""


def normalize_atlas(raw, pages, catalog, page_texts=None, *, native_text=False):
    """Reject invalid envelope; drop malformed optional regions independently."""
    if not isinstance(raw, dict) or set(raw) != set(ATLAS_SCHEMA["properties"]): raise ValueError("atlas: invalid fields")
    if raw["atlas_version"] != VERSION: raise ValueError("atlas_version: unsupported")
    requested = sorted(set(pages))
    actual = raw["processed_pages"]
    if (not isinstance(actual, list) or not 1 <= len(actual) <= MAX_PAGES or
            any(type(p) is not int for p in actual) or len(set(actual)) != len(actual) or sorted(actual) != requested):
        raise ValueError("processed_pages: must match validated selected pages")
    regions = raw["regions"]
    if not isinstance(regions, list) or len(regions) > MAX_REGIONS: raise ValueError("regions: count bound")
    counts = Counter(r.get("page") for r in regions if isinstance(r, dict) and type(r.get("page")) is int)
    if any(n > MAX_PER_PAGE for n in counts.values()): raise ValueError("regions: per-page count bound")
    ids = [r.get("region_id") for r in regions if isinstance(r, dict) and isinstance(r.get("region_id"), str)]
    if len(ids) != len(set(ids)): raise ValueError("region_id: duplicate identity")
    edge_count = sum(len(r.get("related_region_ids", [])) for r in regions if isinstance(r, dict) and isinstance(r.get("related_region_ids"), list))
    if edge_count > MAX_EDGES: raise ValueError("related_region_ids: total edge bound")
    good, diagnostics = [], []
    def reason(r):
        if not isinstance(r, dict) or set(r) != set(ATLAS_SCHEMA["properties"]["regions"]["items"]["properties"]): return "fields"
        if not isinstance(r["region_id"], str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", r["region_id"]): return "region_id"
        if type(r["page"]) is not int or r["page"] not in requested: return "page"
        if r["type"] not in TYPES or r["layer"] not in LAYERS or r["confidence"] not in ("high", "medium", "low"): return "enum"
        if not _text(r["label"], 160, False, native_text=native_text) or not _text(r["grounding_note"], 400, native_text=native_text) or not _text(r["source_text_excerpt"], 600, native_text=native_text): return "plain_text"
        if r["bbox"] is not None and not bbox_valid(r["bbox"]): return "bbox"
        for field, allowed in (("semantic_ids", set(catalog)), ("related_region_ids", set(ids))):
            values = r[field]
            if not isinstance(values, list) or len(values) > 8 or any(not isinstance(v, str) or v not in allowed for v in values) or len(values) != len(set(values)): return field
        parent = r["parent_region_id"]
        if parent is not None and (not isinstance(parent, str) or parent not in ids or parent == r["region_id"]): return "parent_region_id"
        if r["region_id"] in r["related_region_ids"]: return "self_relation"
        return None
    for index, original in enumerate(regions):
        error = reason(original)
        if error:
            diagnostics.append(f"regions[{index}].{error}"); continue
        r = copy.deepcopy(original)
        if r["confidence"] == "low": r["bbox"] = None  # Page-only, never draw a low-confidence precise box.
        excerpt = r["source_text_excerpt"]
        native = extracted_page_text(page_texts, r["page"])
        r["excerpt_verified"] = bool(excerpt.strip() and " ".join(excerpt.split()) in " ".join(native.split()))
        good.append(r)
    lookup = {r["region_id"]: r for r in good}
    cyclic = set()
    for r in good:
        chain, current = set(), r["region_id"]
        while current in lookup:
            if current in chain: cyclic.update(chain); break
            chain.add(current); current = lookup[current]["parent_region_id"]
    good = [r for r in good if r["region_id"] not in cyclic]
    if cyclic: diagnostics.append("parent_region_id: cyclic regions dropped")
    kept = {r["region_id"] for r in good}
    for r in good:
        if r["parent_region_id"] not in kept: r["parent_region_id"] = None
        r["related_region_ids"] = [i for i in r["related_region_ids"] if i in kept]
    return dict(atlas_version=VERSION, processed_pages=requested, regions=good, diagnostics=diagnostics)


def anchors(atlas, identifier):
    return sorted([r for r in atlas["regions"] if identifier in r["semantic_ids"]],
                  key=lambda r: (r["bbox"] is None, {"high": 0, "medium": 1, "low": 2}[r["confidence"]],
                                 {"vector": 0, "arrow": 0, "formula": 1, "diagram": 2, "graph_region": 2, "label": 5}.get(r["type"], 3),
                                 r["page"], r["region_id"]))


def evidence_graph(atlas, catalog):
    return [{"semantic_id": s, "region_id": r["region_id"], "page": r["page"],
             "representation_ids": [v["id"] for v in catalog[s]["representations"]]}
            for r in atlas["regions"] for s in r["semantic_ids"]]


def formula_trace(region, catalog):
    """Traverse a validated equation DAG, no parsing/executing source formula."""
    reached, queue = set(), list(region["semantic_ids"])
    while queue:
        identifier = queue.pop()
        if identifier in reached or identifier not in catalog: continue
        reached.add(identifier)
        queue.extend(set(re.findall(r"\b[A-Za-z][A-Za-z0-9_]*\b", catalog[identifier]["equation"])) & catalog.keys())
    labels = {i: catalog[i]["label"] for i in catalog}
    human = lambda e: re.sub(r"\b[A-Za-z][A-Za-z0-9_]*\b", lambda m: labels.get(m.group(), m.group()), e)
    views = {v["id"]: v for i in region["semantic_ids"] for v in catalog[i]["representations"]}
    return dict(source=region["source_text_excerpt"],
        equations=[catalog[i]["label"] + " = " + human(catalog[i]["equation"]) for i in sorted(reached) if catalog[i]["equation"]],
        parameters=[catalog[i]["label"] for i in sorted(reached) if catalog[i]["kind"] in ("parameter", "time")],
        quantities=[catalog[i]["label"] for i in sorted(reached) if catalog[i]["kind"] == "quantity"],
        representations=list(views.values()))
