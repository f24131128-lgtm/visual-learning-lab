# PDF/license decision

Decision **A: replace production PyMuPDF**, using an independently written
public-API PDFium adapter. Actual production uses were solely in `source_lens.py`:
page rasterization and unique native-text search/highlight coordinates. Overlays
already used Pillow; native geometry already used optional pdfplumber/pypdf.
There was no other production fitz/PyMuPDF fallback to retain.

`pdf_renderer.py` wraps pypdfium2 5.13.0, serializes every PDFium operation, closes
native handles, bounds dimensions and converts native text boxes using PDFium's
crop/rotation-aware PageToDevice function. No upstream implementation was copied.
PDFium JS/actions/XFA are never initialized. Source Lens keeps its session-local
8-page / 24 MiB raster cache, text fallback, unique-match rule and original PDF.

Alternatives reviewed in the reuse ledger: pypdf lacks equivalent bitmap
rasterization; pdfplumber's image path also uses PDFium and adds dependencies;
PyMuPDF requires AGPL or commercial terms. Direct PDFium wrapping covers actual
uses with fewer mandatory layers. [Official PDFium API](https://pypdfium2.readthedocs.io/en/stable/python_api.html)
and [licenses/builds](https://pypdfium2.readthedocs.io/en/stable/readme.html), retrieved
2026-10-12; exact installed wheel license paths are in dependency metadata.

Tests compare unequal multipage PDFs, all 0/90/180/270 crop rotations, native
formula ink under mapped boxes, raster dimension/antialiasing tolerance, second
page navigation, equation-image pages, bounded zoom frame and corrupt rejection.
Source Atlas actual PDF overlays and Source roundtrip were checked in a browser.
Equivalent dimensions/frame are required; pixel-for-pixel antialiasing identity
is not asserted. No OCR/guessed highlight replaced native search.

Production requirements/imports no longer use PyMuPDF. The clean install confirms
it is unavailable while Source works. Tests retain it for fixture creation and
independent comparison; do not deploy `requirements-test.txt`. Existing historical
AGPL/commercial distribution obligations are not retroactively resolved.

Retain PDFium's complete LICENSES/BUILD_LICENSES trees, not just the binding's
headline license. This is a concrete engineering decision, **not legal approval**.
Prepared MIT OCW material is CC BY-NC-SA 4.0: retain attribution and applicable
ShareAlike conditions, restrict the demonstration to noncommercial use. Commercial
reuse, past distributions and any future binary redistribution require review.
