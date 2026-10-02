"""Inspectable synthetic PDFs, never imported by production code."""
import pymupdf
try:
    from atlas_fixtures import source_pdf
except ModuleNotFoundError:
    from .atlas_fixtures import source_pdf


def text_pdf(lines):
    with pymupdf.open() as doc:
        page = doc.new_page(width=600, height=700)
        for index, line in enumerate(lines):
            page.insert_text((48, 70+index*32), line, fontsize=16)
        return doc.tobytes()


def cropped_rotated(rotation):
    with pymupdf.open(stream=source_pdf(), filetype="pdf") as doc:
        doc[0].set_cropbox(pymupdf.Rect(20, 30, 570, 650))
        doc[0].set_rotation(rotation)
        doc[1].set_cropbox(pymupdf.Rect(30, 30, 760, 460))
        return doc.tobytes()


def corpus():
    pdf = source_pdf()
    with pymupdf.open(stream=pdf, filetype="pdf") as source, pymupdf.open() as target:
        page = target.new_page(width=600, height=700)
        page.insert_image(page.rect, stream=source[0].get_pixmap().tobytes("png"))
        scan = target.tobytes()
    return {
        "lecture_phasor": pdf,
        "projectile": source_pdf("projectile"),
        "probability": text_pdf(["Sample space S = {HH, HT, TH, TT}", "Event E = {HH, HT}",
                                  "P(E) = 1/2", "P(E union F) = P(E) + P(F) - P(E intersection F)"]),
        "formula_heavy": text_pdf([f"q{i}(t) = A cos(2 pi f t - {i} pi/3)" for i in range(12)]),
        "image_only": scan,
        "messy_marks_page": pdf,  # Page 2 includes ambiguous marks; parser finds only native formula.
        "crop_rotate_90": cropped_rotated(90),
    }
