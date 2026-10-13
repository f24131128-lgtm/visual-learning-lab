"""Independent PDFium public-API adapter; original rendered crop/rotation frame.

PDFium calls are serialized process-wide. No document JS/actions are initialized.
"""
import ctypes
from contextlib import closing
import io
import math
import threading
import pypdfium2 as pdfium
from production_safety import checked_pdf

PDFIUM_LOCK = threading.RLock()


def render(data, number, dpi, side):
    from public_access import mode
    if mode()=='limited-public':
        from pdf_ingest import run_worker
        return run_worker('render',data,number=number,dpi=dpi,side=side)
    checked_pdf(data)
    with PDFIUM_LOCK, pdfium.PdfDocument(data) as document:
        if type(number) is not int or not 1 <= number <= len(document):
            raise ValueError("PDF page")
        with closing(document[number-1]) as page:
            width, height = page.get_size()
            if not all(math.isfinite(v) and 0 < v <= 20000 for v in (width, height)):
                raise ValueError("PDF dimensions")
            scale = min(dpi/72, side/max(width, height))
            with closing(page.render(scale=scale)) as bitmap:
                image = bitmap.to_pil().convert("RGB")
            result = io.BytesIO()
            image.save(result, format="PNG")
            return dict(png=result.getvalue(), width=image.width, height=image.height)


def anchors(data, number, phrase):
    from public_access import mode
    if mode()=='limited-public':
        from pdf_ingest import run_worker
        return run_worker('anchors',data,number=number,phrase=phrase)
    checked_pdf(data)
    if not isinstance(phrase, str) or not 0 < len(phrase) <= 500:
        return []
    with PDFIUM_LOCK, pdfium.PdfDocument(data) as document:
        if type(number) is not int or not 1 <= number <= len(document):
            raise ValueError("PDF page")
        with closing(document[number-1]) as page, closing(page.get_textpage()) as text:
            if text.count_chars() > 48000:
                return []
            with closing(text.search(phrase)) as search:
                match = search.get_next()
                if match is None or search.get_next() is not None:
                    return []  # Ambiguous native text never receives a highlight.
            count = text.count_rects(*match)
            if not 0 < count <= 4:
                return []
            boxes = [text.get_rect(i) for i in range(count)]
            # PageToDevice uses PDFium's actual crop and intrinsic rotation.
            w, h = [round(v*1000) for v in page.get_size()]
            rectangles = []
            for left, bottom, right, top in boxes:
                points = []
                for x, y in ((left,bottom),(left,top),(right,bottom),(right,top)):
                    dx, dy = ctypes.c_int(), ctypes.c_int()
                    if not pdfium.raw.FPDF_PageToDevice(page, 0, 0, w, h, 0, x, y, dx, dy):
                        return []
                    points.append((dx.value/w, dy.value/h))
                x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
                x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
                if not 0 <= x0 < x1 <= 1 or not 0 <= y0 < y1 <= 1:
                    return []
                rectangles.append((x0,y0,x1,y1))
            return rectangles
