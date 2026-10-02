"""Parser-neutral, bounded document envelope reusing the Source Atlas regions."""

import copy
import hashlib
import json
import logging
import re

from source_atlas.model import normalize_atlas
from source_atlas.schema import MAX_PAGES, MAX_PER_PAGE, MAX_REGIONS

VERSION = "1.1"
logger = logging.getLogger(__name__)
MAX_PDF_BYTES = 20 * 1024 * 1024
MAX_MODEL_BYTES = 256 * 1024


class DocumentError(ValueError):
    """Controlled field-level reason only; never a parser/source error body."""
    def __init__(self, reason, diagnostics=None):
        super().__init__(reason)
        self.diagnostics = diagnostics or {}


def failure_reason(error):
    return str(error)[:240] if isinstance(error, DocumentError) else type(error).__name__


def pdf_identity(pdf_bytes):
    if not isinstance(pdf_bytes, bytes) or not 0 < len(pdf_bytes) <= MAX_PDF_BYTES:
        raise DocumentError("document: input size")
    return hashlib.sha256(pdf_bytes).hexdigest()


def checked_pages(pages, allowed):
    if (not isinstance(pages, list) or not 1 <= len(pages) <= MAX_PAGES or
            any(type(p) is not int or p < 1 or p not in allowed for p in pages) or
            len(set(pages)) != len(pages)):
        raise DocumentError("document: selected pages")
    return sorted(pages)


def normalize_document(raw, pdf_bytes, pages, allowed):
    """External parser data never declares semantic links or executable formulas."""
    pages = checked_pages(pages, allowed)
    fields = {"version", "pdf_sha256", "parser", "parser_version", "atlas", "locators"}
    if not isinstance(raw, dict) or set(raw) != fields:
        raise DocumentError("document: envelope fields")
    if raw["version"] != VERSION or raw["pdf_sha256"] != pdf_identity(pdf_bytes):
        raise DocumentError("document: version or material identity")
    for key in ("parser", "parser_version"):
        if not isinstance(raw[key], str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", raw[key]):
            raise DocumentError("document: parser identity")
    try:
        size = len(json.dumps(raw, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    except (TypeError, ValueError, RecursionError) as error:
        raise DocumentError("document: non-JSON data") from error
    if size > MAX_MODEL_BYTES:
        raise DocumentError("document: payload bound")
    # A separate native plain-text policy preserves source comparisons, while
    # retaining the same geometry/envelope/bounds/markup checks. The semantic
    # compiler continues to use normalize_atlas's default generated-text policy.
    try:
        atlas = normalize_atlas(raw["atlas"], pages, {}, native_text=True)
    except ValueError as error:
        raise DocumentError(str(error)) from error
    logger.info("Local document normalization produced=%s accepted=%s reasons=%s",
                len(raw["atlas"]["regions"]), len(atlas["regions"]), atlas["diagnostics"])
    if atlas["diagnostics"]:
        raise DocumentError("document: invalid region fields: " + ",".join(atlas["diagnostics"][:8]),
                            dict(normalized_regions=len(atlas["regions"])))
    locators = raw["locators"]
    ids = {r["region_id"] for r in atlas["regions"]}
    if not isinstance(locators, dict) or len(locators) > MAX_REGIONS or set(locators) != ids:
        raise DocumentError("document: locator identity")
    seen = set()
    for identifier, item in locators.items():
        if not isinstance(item, dict) or set(item) != {"path", "reading_order", "method"}:
            raise DocumentError("document: locator fields")
        if (not isinstance(item["path"], str) or not re.fullmatch(r"page/[1-9][0-9]*/text_line/[0-9]+", item["path"]) or
                type(item["reading_order"]) is not int or not 0 <= item["reading_order"] < MAX_PER_PAGE or
                item["method"] != "native_text_geometry" or item["path"] in seen):
            raise DocumentError("document: locator value")
        region = next(r for r in atlas["regions"] if r["region_id"] == identifier)
        if item["path"] != f"page/{region['page']}/text_line/{item['reading_order']}":
            raise DocumentError("document: locator page/order")
        if region["type"] != "annotation" or region["semantic_ids"] or region["bbox"] is None:
            raise DocumentError("document: native text region")
        seen.add(item["path"])
        # This identifies parser-extracted text, not a second independent
        # verification of transcription/source support.
        region["excerpt_verified"] = False
    return {**copy.deepcopy(raw), "atlas": atlas}


def refine_atlas(atlas, document):
    """Unique exact whole-line match only; no inferred meaning or vector boxes."""
    result = copy.deepcopy(atlas)
    norm = lambda text: " ".join(text.split())
    for region in result["regions"]:
        if region["type"] not in ("formula", "label") or region["confidence"] == "low":
            continue
        excerpt = norm(region["source_text_excerpt"])
        if not excerpt:
            continue
        matches = [r for r in document["atlas"]["regions"] if r["page"] == region["page"]
                   and norm(r["source_text_excerpt"]) == excerpt]
        if len(matches) == 1:
            region["bbox"] = copy.deepcopy(matches[0]["bbox"])
            # Native geometry does NOT upgrade semantic confidence or enable
            # a low-confidence label to be masked.
            region["grounding_note"] = "Native PDF text geometry; semantic support remains estimated."
    return result


def compiler_context(document, budget=6000):
    """Bound geometry hints separately from the existing semantic catalog."""
    rows = []
    for region in document["atlas"]["regions"]:
        row = dict(locator=region["region_id"], page=region["page"], bbox=region["bbox"],
                   text=region["source_text_excerpt"])
        if len(json.dumps(rows + [row], ensure_ascii=False)) > budget:
            break
        rows.append(row)
    return rows
