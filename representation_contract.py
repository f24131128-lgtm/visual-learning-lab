"""Explicit bounded Lab ownership over existing canonical semantic identities."""
import hashlib
import json

VERSION = "1.0"
REFS_SCHEMA = dict(type="array", items=dict(type="string"), maxItems=8)


def renderer_id(demo, group, local_id):
    return f"lab:{demo['id']}:{group}:{local_id}"


def signature(demo):
    data = {k: v for k, v in demo.items() if k != "ownership"}
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def validate_refs(refs, catalog, source_pages, allowed_pages):
    if not isinstance(refs, list) or len(refs) > 8 or len(set(refs)) != len(refs):
        raise ValueError("Invalid representation ownership refs")
    for identifier in refs:
        if not isinstance(identifier, str) or identifier not in catalog:
            raise ValueError("Unknown representation semantic ID")
        semantic_pages = set(catalog[identifier].get("pages", []))
        if allowed_pages and (not set(source_pages) & semantic_pages or not semantic_pages <= set(allowed_pages)):
            raise ValueError("Representation source provenance mismatch")
    return list(refs)


def bind(demo, catalog, material, allowed_pages):
    """A material/spec-bound envelope can be derived only from supplied exact refs."""
    rows = []
    for group in ("parameters", "series", "derived_metrics"):
        for item in demo[group]:
            pages = item.get("source_pages", demo["source_pages"])
            refs = validate_refs(item.get("semantic_refs", []), catalog, pages, allowed_pages)
            if refs and (not isinstance(material, str) or not material):
                raise ValueError("Missing representation material identity")
            for semantic in refs:
                rows.append(dict(semantic_id=semantic, id=renderer_id(demo, group, item["id"]), local_id=item["id"], label=item["label"], kind=group,
                                 source_pages=list(pages), demo_id=demo["id"]))
    return dict(version=VERSION, material_id=material, specification=signature(demo), rows=rows)


def registrations(demo, catalog, material, allowed_pages):
    try:
        ownership = demo.get("ownership")
        if (not isinstance(ownership, dict) or ownership.get("version") != VERSION
                or ownership.get("material_id") != material or ownership.get("specification") != signature(demo)):
            return {}
        expected = bind(demo, catalog, material, allowed_pages)
        if ownership != expected:
            return {}
    except (ValueError, TypeError, KeyError):
        return {}
    result = {}
    for row in ownership["rows"]:
        result.setdefault(row["semantic_id"], []).append(row)
    return result
