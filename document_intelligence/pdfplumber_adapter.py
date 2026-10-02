"""Public pdfplumber API wrapper, independently implemented; no vendored code."""

import io
import math
import logging
from importlib.metadata import version

from pypdf import PdfReader

from source_atlas.model import bbox_valid
from source_atlas.schema import MAX_PER_PAGE, MAX_REGIONS, VERSION as ATLAS_VERSION
from .model import VERSION, DocumentError, checked_pages, normalize_document, pdf_identity, failure_reason

MAX_CHARACTERS_PER_PAGE = 20000
logger = logging.getLogger(__name__)
ADAPTER_VERSION = "2"


def visible_bbox(pdf_page):
    """Rotate canonical PDF boxes into the parser's displayed media frame.

    Do not trust a crop-box axis swap alone: asymmetric 180/270 crops also
    need reflection. Unusual media origins are declined, not silently guessed.
    """
    media = [float(v) for v in pdf_page.mediabox]
    crop = [float(v) for v in pdf_page.cropbox]
    if any(not math.isfinite(v) for v in media+crop) or media[:2] != [0., 0.]:
        raise DocumentError("document: unsupported media origin")
    width, height = media[2:]
    left, bottom_pdf, right, top_pdf = crop
    if not 0 <= left < right <= width or not 0 <= bottom_pdf < top_pdf <= height:
        raise DocumentError("document: crop bounds")
    top, bottom = height-top_pdf, height-bottom_pdf
    rotation = pdf_page.rotation % 360
    if rotation == 0: return left, top, right, bottom
    if rotation == 90: return height-bottom, left, height-top, right
    if rotation == 180: return width-right, height-bottom, width-left, height-top
    if rotation == 270: return top, width-right, bottom, width-left
    raise DocumentError("document: unsupported rotation")


def available():
    try:
        import pdfplumber
        return True
    except (ImportError, OSError):
        return False


def parse(pdf_bytes, pages, allowed):
    diagnostics = dict(requested_pages=[], parsed_pages=[], chars={}, regions_produced=0, normalized_regions=0)
    try:
        return _parse(pdf_bytes, pages, allowed, diagnostics)
    except Exception as error:
        if isinstance(error, DocumentError):
            diagnostics.update(error.diagnostics)
            error.diagnostics = diagnostics
        # Even when INFO is disabled, a failure records boundary counts, not
        # source text, PDF bytes/path or an external library's error body.
        logger.warning("Local document adapter rejected counts=%s reason=%s", diagnostics, failure_reason(error))
        raise


def _parse(pdf_bytes, pages, allowed, diagnostics):
    identity = pdf_identity(pdf_bytes)
    pages = checked_pages(pages, allowed)
    diagnostics["requested_pages"] = pages
    logger.info("Local document adapter requested_pages=%s input_bytes=%s", pages, len(pdf_bytes))
    import pdfplumber  # Lazy, optional; never download models or call a service.
    reader = PdfReader(io.BytesIO(pdf_bytes))

    regions, locators = [], {}
    with pdfplumber.open(io.BytesIO(pdf_bytes), pages=pages) as document:
        diagnostics["parsed_pages"] = [p.page_number for p in document.pages]
        logger.info("Local document adapter parsed_pages=%s", [p.page_number for p in document.pages])
        if sorted(p.page_number for p in document.pages) != pages:
            raise DocumentError("document: page outside PDF")
        for page in document.pages:
            diagnostics["chars"][page.page_number] = len(page.chars)
            logger.info("Local document adapter page=%s chars=%s", page.page_number, len(page.chars))
            if len(page.chars) > MAX_CHARACTERS_PER_PAGE:
                raise DocumentError("document: page character bound")
            # pdfplumber coordinates already include page rotation; Source Lens
            # displays the crop box. Subtract its origin, not the media origin.
            visible = page.crop(visible_bbox(reader.pages[page.page_number-1]))
            x0, top, x1, bottom = visible.bbox
            width, height = x1-x0, bottom-top
            if width <= 0 or height <= 0:
                raise DocumentError("document: page dimensions")
            lines = visible.extract_text_lines(return_chars=False)
            diagnostics["regions_produced"] += len(lines)
            logger.info("Local document adapter page=%s regions_produced=%s", page.page_number, len(lines))
            if len(lines) > MAX_PER_PAGE or len(regions)+len(lines) > MAX_REGIONS:
                raise DocumentError("document: text line count bound")
            for order, line in enumerate(lines):
                text = line["text"]
                if not isinstance(text, str) or not text.strip() or len(text) > 600:
                    raise DocumentError("document: line text bound")
                box = dict(x0=(line["x0"]-x0)/width, y0=(line["top"]-top)/height,
                           x1=(line["x1"]-x0)/width, y1=(line["bottom"]-top)/height)
                if not bbox_valid(box):
                    raise DocumentError("document: native box")
                identifier = f"native_p{page.page_number}_line{order}"
                regions.append(dict(region_id=identifier, page=page.page_number, bbox=box,
                    type="annotation", label=text[:160], semantic_ids=[], source_text_excerpt=text,
                    parent_region_id=None, related_region_ids=[], layer="structure", confidence="medium",
                    grounding_note="Native PDF text geometry; not OCR or semantic classification."))
                locators[identifier] = dict(path=f"page/{page.page_number}/text_line/{order}",
                    reading_order=order, method="native_text_geometry")
            page.close()
    raw = dict(version=VERSION, pdf_sha256=identity, parser="pdfplumber", parser_version=version("pdfplumber"),
               atlas=dict(atlas_version=ATLAS_VERSION, processed_pages=pages, regions=regions), locators=locators)
    result = normalize_document(raw, pdf_bytes, pages, allowed)
    diagnostics["normalized_regions"] = len(result["atlas"]["regions"])
    logger.info("Local document adapter success normalized_regions=%s", len(result["atlas"]["regions"]))
    return result
