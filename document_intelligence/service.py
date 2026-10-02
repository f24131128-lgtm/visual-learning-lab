"""Active-PDF, bounded local parser cache; failures leave semantic state intact."""

from importlib.metadata import version
import logging
from . import pdfplumber_adapter
from .model import VERSION, DocumentError, checked_pages, pdf_identity
logger = logging.getLogger(__name__)


def get_document(source, pages, allowed):
    identity = pdf_identity(source.get("pdf_bytes"))
    pages = checked_pages(pages, allowed)
    key = (identity, VERSION, pdfplumber_adapter.ADAPTER_VERSION, "pdfplumber", version("pdfplumber"), tuple(pages))
    cache = source.setdefault("document_intelligence", {})
    logger.info("Local document cache hit=%s requested_pages=%s", key in cache, pages)
    if key not in cache:
        model = pdfplumber_adapter.parse(source["pdf_bytes"], pages, allowed)
        if not model["atlas"]["regions"]:
            raise DocumentError("document: no native text regions (no OCR)")
        cache[key] = model
        while len(cache) > 2:
            cache.pop(next(iter(cache)))
    return cache[key]
