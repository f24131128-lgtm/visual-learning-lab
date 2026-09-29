"""Local, in-memory source evidence for the active learning material."""

import io
import re

import streamlit as st

from i18n import tr
from PIL import Image, ImageDraw

try:
    import pymupdf
except (ImportError, OSError):
    pymupdf = None

RENDER_DPI = 144
MAX_PAGE_SIDE = 1800
MAX_CACHE_BYTES = 24 * 1024 * 1024
MAX_TEXT_CONTEXT = 6000


def new_source_state(material_id, pdf_bytes=None):
    """Own only the active PDF, with a bounded, session-local raster cache."""
    return {
        "material_id": material_id,
        "pdf_bytes": pdf_bytes,
        "pages": {},
        "anchors": {},
        "view": {"target": None, "open": False, "page": None},
    }


def validated_pages(pages, allowed_pages):
    return sorted({p for p in pages if type(p) is int and p in allowed_pages})


def _terms(text):
    stop = {"the", "and", "for", "from", "with", "this", "that", "into", "are", "of", "to", "in", "is", "a"}
    english = {word for word in re.findall(r"[a-z0-9]+", text.casefold()) if len(word) > 2 and word not in stop}
    chinese = set()
    for run in re.findall(r"[\u3400-\u9fff]+", text):
        chinese.update(run[i:i + 2] for i in range(len(run) - 1))
    return english | chinese


def find_text_anchor(label, page_text):
    """Return an actual extracted excerpt and conservative search phrase, or None.

    Lexical overlap is a navigation aid, never a proof of support. Prefer an exact
    distinctive label; otherwise require multiple terms and a clear best chunk.
    All returned text is sliced from the supplied source, never generated.
    """
    if not label or not page_text:
        return None
    terms = _terms(label)
    if not terms:
        return None
    chunks = [m.group().strip() for m in re.finditer(r"[^\n。！？!?]+[。！？!?]?", page_text)]
    candidates = []
    label_pattern = re.compile(re.escape(label.strip()).replace(r"\ ", r"\s+"), re.IGNORECASE)
    for chunk in chunks:
        if not chunk or len(chunk) > 500:
            continue
        exact = label_pattern.search(chunk)
        # A short, generic token is not precise enough to highlight.
        distinctive = len(label.strip()) >= 6 or len(re.findall(r"[\u3400-\u9fff]", label)) >= 4
        if exact and distinctive:
            return {"excerpt": chunk, "phrase": exact.group(), "method": "exact label"}
        overlap = terms & _terms(chunk)
        score = len(overlap) / len(terms)
        if len(overlap) >= 2 and score >= 0.6:
            candidates.append((score, chunk))
    candidates.sort(key=lambda item: item[0], reverse=True)
    if candidates and (len(candidates) == 1 or candidates[0][0] - candidates[1][0] >= 0.15):
        chunk = candidates[0][1]
        return {"excerpt": chunk, "phrase": chunk, "method": "lexical match"}
    return None


def get_page_render(state, material_id, page_number, allowed_pages):
    """Rasterize once per active material/page/DPI; never accept unvalidated pages."""
    if state.get("material_id") != material_id:
        raise ValueError("Source material has changed.")
    if type(page_number) is not int or page_number not in allowed_pages:
        raise ValueError("The source page is not among the analyzed pages.")
    if not state.get("pdf_bytes"):
        raise ValueError("The active PDF is unavailable.")
    key = (material_id, page_number, RENDER_DPI)
    cache = state["pages"]
    if key in cache:
        result = cache.pop(key)
        cache[key] = result
        return result
    if pymupdf is None:
        raise RuntimeError("PDF rendering is unavailable.")
    with pymupdf.open(stream=state["pdf_bytes"], filetype="pdf") as document:
        if not 1 <= page_number <= len(document):
            raise ValueError("The source page is outside this PDF.")
        page = document[page_number - 1]
        scale = min(RENDER_DPI / 72, MAX_PAGE_SIDE / max(page.rect.width, page.rect.height))
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        result = {"png": pixmap.tobytes("png"), "width": pixmap.width, "height": pixmap.height}
    while cache and (len(cache) >= 8 or sum(len(item["png"]) for item in cache.values()) + len(result["png"]) > MAX_CACHE_BYTES):
        cache.pop(next(iter(cache)))
    if len(result["png"]) <= MAX_CACHE_BYTES:
        cache[key] = result
    return result


def locate_anchor(state, page_number, phrase):
    """Locate a unique native-text phrase. No OCR and no guessed coordinates."""
    key = (page_number, phrase)
    if key in state["anchors"]:
        return state["anchors"][key]
    rectangles = []
    if pymupdf is not None and phrase:
        with pymupdf.open(stream=state["pdf_bytes"], filetype="pdf") as document:
            page = document[page_number - 1]
            normalized = " ".join(page.get_text().split()).casefold()
            needle = " ".join(phrase.split()).casefold()
            # Repeated phrases are ambiguous. An exact native PDF match is required.
            if normalized.count(needle) == 1:
                matches = page.search_for(phrase)
                if 0 < len(matches) <= 4:
                    for match in matches:
                        rect = match * page.rotation_matrix
                        if not rect.is_empty and page.rect.contains(rect):
                            rectangles.append(tuple((value / dimension) for value, dimension in zip(
                                (rect.x0, rect.y0, rect.x1, rect.y1),
                                (page.rect.width, page.rect.height, page.rect.width, page.rect.height),
                            )))
    if len(state["anchors"]) >= 64:
        state["anchors"].pop(next(iter(state["anchors"])))
    state["anchors"][key] = rectangles
    return rectangles


def highlighted_image(render, rectangles):
    """Overlay verified rectangles on a cached raster without rerasterizing the PDF."""
    if not rectangles:
        return render["png"]
    with Image.open(io.BytesIO(render["png"])) as image:
        image = image.convert("RGBA")
    overlay = Image.new("RGBA", image.size)
    draw = ImageDraw.Draw(overlay)
    for rect in rectangles:
        coords = [value * dimension for value, dimension in zip(rect, (image.width, image.height, image.width, image.height))]
        draw.rectangle(coords, fill=(160, 131, 235, 55), outline=(103, 80, 197, 140), width=2)
    output = io.BytesIO()
    Image.alpha_composite(image, overlay).convert("RGB").save(output, format="PNG")
    return output.getvalue()


def toggle_source_view(view):
    view["open"] = not view["open"]


def render_source_lens(state, material_id, target_key, label, pages, source_context, allowed_pages, visual_evidence=()):
    """An explicit source toggle; every operation in this panel is local."""
    if state.get("material_id") != material_id:
        st.caption(tr("Source context is no longer available for this material."))
        return
    view = state["view"]
    if view["target"] != target_key:
        view.update(target=target_key, open=False, page=None)
    st.button(tr("Hide source") if view["open"] else tr("View source"), key=f"lens-toggle-{material_id}-{target_key}",
              on_click=toggle_source_view, args=(view,))
    if not view["open"]:
        return
    st.markdown("##### " + tr("Source Lens"))
    if source_context.get("kind") != "pdf":
        text = source_context.get("source_text", "")
        anchor = find_text_anchor(label, text)
        st.caption(tr("Supplied pasted-text context"))
        st.text(anchor["excerpt"] if anchor else text[:MAX_TEXT_CONTEXT])
        if not text:
            st.caption(tr("No supplied text context is available."))
        return
    pages = validated_pages(pages, allowed_pages)
    if not pages:
        st.caption(tr("No validated source page is linked to this item."))
        return
    if view["page"] not in pages:
        view["page"] = pages[0]
    if len(pages) > 1:
        columns = st.columns(len(pages))
        for column, number in zip(columns, pages):
            if column.button(tr("p. {pages}", pages=number), key=f"lens-page-{material_id}-{target_key}-{number}", type="primary" if view["page"] == number else "secondary"):
                view["page"] = number
                st.rerun()
    page_number = view["page"]
    page_text = source_context.get("page_texts", {}).get(page_number, "")
    anchor = find_text_anchor(label, page_text)
    try:
        render = get_page_render(state, material_id, page_number, allowed_pages)
        rectangles = []
        if anchor:
            try:
                rectangles = locate_anchor(state, page_number, anchor["phrase"])
            except Exception:
                pass  # A failed text lookup must not hide a successfully rendered page.
        # Default image sizing fits the column on Streamlit 1.39 and newer.
        st.image(highlighted_image(render, rectangles), caption=tr("Original PDF · Page {page}", page=page_number), output_format="PNG")
        if rectangles:
            st.caption(tr("Text match highlighted for navigation; verify its meaning in context."))
        else:
            st.caption(tr("Showing source page context; an exact text location was not found."))
    except Exception:
        st.info(tr("We couldn’t preview this PDF page. The available extracted text is shown below."))
    if anchor:
        st.caption(tr("Matching extracted excerpt"))
        st.text(anchor["excerpt"])
    evidence = [item for item in visual_evidence if isinstance(item, dict)
                and type(item.get("page")) is int and item["page"] == page_number]
    if evidence:
        st.caption(tr("Visual evidence observed on original PDF page · from the existing analysis"))
        for item in evidence:
            st.write(item["description"])
    st.markdown("**" + tr("Extracted text context") + "**")
    st.caption(tr("Extracted text from the same page; this is not an exact transcription of diagrams or formulas."))
    st.text(page_text[:MAX_TEXT_CONTEXT] if page_text else tr("No extracted text is available for this analyzed page."))
    if len(page_text) > MAX_TEXT_CONTEXT:
        st.caption(tr("Text context is shortened for display."))
