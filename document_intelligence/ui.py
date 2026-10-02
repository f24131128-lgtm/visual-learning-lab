"""Small explicit local action inside Atlas, not a new learning subsystem."""

import logging
import streamlit as st

from i18n import tr
from source_atlas.state import save_result
from .model import VERSION, failure_reason, refine_atlas
from .pdfplumber_adapter import available
from .service import get_document

logger = logging.getLogger(__name__)


def render_controls(state, source, pages, allowed):
    enabled = available()
    if state.get("parser_available") != enabled:
        logger.info("Local document UI parser_available=%s", enabled)
    state["parser_available"] = enabled
    # Retire only local parser state from an older contract; never semantic
    # Atlas/scene state. Failures were not cached and remain explicitly retryable.
    document = state.get("document_model")
    if document is not None and document.get("version") != VERSION:
        for key in ("document_model", "native_preview", "document_error", "document_diagnostic", "document_diagnostics"):
            state.pop(key, None)
    if st.button(tr("Inspect document structure locally"), type="secondary",
                 key="atlas-widget-native-"+source["material_id"],
                 disabled=not enabled or state.get("document_model") is not None):
        try:
            logger.info("Local document UI available=%s requested_pages=%s bytes_present=%s",
                        enabled, list(pages), isinstance(source.get("pdf_bytes"), bytes))
            with st.spinner(tr("Reading native PDF structure…")):
                document = get_document(source, list(pages), allowed)
            state["document_model"] = document
            state.pop("document_error", None)
            state.pop("document_diagnostic", None)
            state.pop("document_diagnostics", None)
            logger.info("Local document UI available=True normalized_regions=%s", len(document["atlas"]["regions"]))
            if state["atlas"] is not None:
                save_result(state, refine_atlas(state["atlas"], document))
        except Exception as error:
            # No source, PDF bytes or parser error body in logs/product UI.
            logger.warning("Local document UI structure_available=False parser_available=%s requested_pages=%s reason=%s",
                           enabled, list(pages), failure_reason(error))
            state["document_error"] = True
            state["document_diagnostic"] = failure_reason(error)
            state["document_diagnostics"] = getattr(error, "diagnostics", {})
    if not enabled:
        st.caption(tr("Optional local parser is not installed; Source Atlas still works."))
    elif state.get("document_error"):
        st.caption(tr("Local structure is unavailable for this PDF; original sources and AI grounding remain available."))
    document = state.get("document_model")
    state["document_available"] = bool(document and document["atlas"]["regions"])
    if document is not None:
        st.caption(tr("Native PDF structure: {count} text regions. No OCR or AI request.", count=len(document["atlas"]["regions"])))
    if document is not None and state["atlas"] is None:
        # Native navigation does not mark the semantic AI build as attempted.
        # A later semantic atlas supersedes this preview without a second focus.
        return state.setdefault("native_preview", dict(key=state["key"]+("native", document["parser_version"]),
            atlas=document["atlas"], page=pages[0], region_hint=None, seen_focus=None, last_token=None))
    return None
