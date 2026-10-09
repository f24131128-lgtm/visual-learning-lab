"""Trusted, ephemeral joins over existing identities; no focus or value store.

Only exact target semantic IDs confer an affordance. Dependency representations
are informative links, never an inferred inverse or a source-fidelity proof.
"""
from collections import Counter
import re

from source_atlas.model import bbox_valid, _text
from source_atlas.schema import MAX_PAGES, MAX_REGIONS, MAX_PER_PAGE


def _bounded_box(box):
    try: return bbox_valid(box)
    except (ValueError, TypeError, OverflowError): return False


def supported_regions(state, material, pages, catalog, expected_key=None):
    key = state.get("key") if isinstance(state, dict) else None
    atlas = state.get("atlas") if isinstance(state, dict) else None
    if (not isinstance(key, tuple) or len(key) < 6 or key[0] != material
            or expected_key is not None and key != expected_key
            or not isinstance(atlas, dict)):
        return []
    processed = atlas.get("processed_pages")
    regions = atlas.get("regions")
    if (not isinstance(processed, list) or not 1 <= len(processed) <= MAX_PAGES
            or any(type(p) is not int or p not in pages for p in processed)
            or len(set(processed)) != len(processed) or tuple(sorted(processed)) != key[4]
            or not isinstance(regions, list) or len(regions) > MAX_REGIONS):
        return []
    ids = [r.get("region_id") for r in regions if isinstance(r, dict)]
    if any(not isinstance(i, str) for i in ids) or len(set(ids)) != len(ids):
        return []
    counts = Counter(r.get("page") for r in regions if isinstance(r, dict) and type(r.get("page")) is int)
    if any(n > MAX_PER_PAGE for n in counts.values()):
        return []
    good = []
    for r in regions:
        if not isinstance(r, dict): continue
        links = r.get("semantic_ids")
        box = r.get("bbox")
        if (not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", r["region_id"])
                or type(r.get("page")) is not int or r["page"] not in processed
                or not _text(r.get("label"), 160, False, native_text=len(key)>6 and not links and r.get("type")=="annotation")
                or not isinstance(links, list) or len(links) > 8
                or any(not isinstance(i, str) or i not in catalog for i in links)
                or len(set(links)) != len(links)
                or r.get("confidence") not in ("high", "medium", "low")
                or box is not None and (not _bounded_box(box) or r["confidence"] == "low")):
            continue
        good.append(r)
    return good


def grounding_kind(region, document=None):
    """Prove native geometry from the existing normalized parser, not a note."""
    if region["bbox"] is None: return "page_only"
    if isinstance(document, dict):
        text = " ".join(region.get("source_text_excerpt", "").split())
        matches = [r for r in document.get("atlas", {}).get("regions", [])
                   if r["page"] == region["page"] and text
                   and " ".join(r["source_text_excerpt"].split()) == text]
        if (len(matches) == 1 and matches[0]["bbox"] == region["bbox"]
                and document.get("locators", {}).get(matches[0]["region_id"], {}).get("method") == "native_text_geometry"):
            return "native_geometry"
    return "estimated_region"


def derive_links(state, material, pages, catalog, targets=(), representations=None,
                 document=None, expected_key=None):
    """Many sources/representations/targets per semantic ID, within old bounds.

    Targets and representations must come from the existing normalized engines,
    never an iframe or Source Atlas declaration. Malformed optional joins isolate.
    """
    regions = supported_regions(state, material, pages, catalog, expected_key)
    if not isinstance(document, dict) or document.get("pdf_sha256") != state.get("key", (None, None))[1]: document = None
    if not isinstance(targets, (list, tuple)) or len(targets) > 8: targets = ()
    counts = Counter(t.get("id") for t in targets if isinstance(t, dict) and isinstance(t.get("id"), str))
    # Renderer-scoped IDs colliding across demos cannot silently choose an owner.
    targets = [t for t in targets if isinstance(t, dict) and isinstance(t.get("id"), str) and counts[t["id"]] == 1]
    by_semantic = {}
    for region in regions:
        for identifier in region["semantic_ids"]:
            link = by_semantic.setdefault(identifier, dict(semantic_id=identifier,
                source_region_ids=[], source_pages=[], support=[], representation_ids=[],
                manipulation_target_ids=[], formal_parameter_ids=[], manipulable=False,
                reason_not_manipulable="No validated direct manipulation is available; use the formal view and existing controls."))
            link["source_region_ids"].append(region["region_id"])
            if region["page"] not in link["source_pages"]: link["source_pages"].append(region["page"])
            link["support"].append(dict(region_id=region["region_id"], page=region["page"],
                kind=grounding_kind(region, document), confidence=region["confidence"]))
    for identifier, link in by_semantic.items():
        reps = catalog[identifier].get("representations", []) + (representations or {}).get(identifier, [])
        link["representation_ids"] = list(dict.fromkeys(r["id"] for r in reps))
        owned = [t for t in targets if t.get("semantic_id") == identifier
                 and t.get("object_id") in link["representation_ids"]
                 and t.get("source_pages") and set(t["source_pages"]) & set(link["source_pages"])]
        link["manipulation_target_ids"] = list(dict.fromkeys(t["id"] for t in owned))
        link["formal_parameter_ids"] = list(dict.fromkeys(p for t in owned for p in t["parameter_ids"]))
        link["manipulable"] = bool(owned)
        if owned: link["reason_not_manipulable"] = ""
        elif catalog[identifier]["kind"] == "quantity":
            link["reason_not_manipulable"] = "This quantity is derived from the current state; no validated direct manipulation is available."
        elif catalog[identifier]["kind"] in ("parameter", "time"):
            link["reason_not_manipulable"] = "This source value has no direct handle. Existing validated controls remain available."
    return by_semantic


def comparison_rows(parameters, current, identifiers):
    """Compiled defaults are a model baseline, never verified source numbers."""
    from scene.world.policy import parameter_display
    rows = []
    for p in parameters:
        if p["id"] not in identifiers: continue
        display = parameter_display(p) if "display_unit" in p else dict(factor=1., unit=p["unit"])
        factor = display["factor"]
        initial, value = p["default"] * factor, current[p["id"]] * factor
        rows.append(dict(id=p["id"], label=p["label"], unit=display["unit"], baseline=initial,
                         current=value, delta=value-initial,
                         generated_range=p.get("range_source") != "source"))
    return rows
