# Third-party reuse notices — Day 20

New integration uses the public **pdfplumber 0.11.10** package API. No upstream
source file is copied or vendored. Repository: https://github.com/jsvine/pdfplumber.
Independent adapter: `document_intelligence/pdfplumber_adapter.py`.

## pdfplumber MIT notice

Copyright (c) 2015, Jeremy Singer-Vine

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Transitive distributions

This is a dependency notice, not a relicensing of those distributions. Keep
their complete `*.dist-info/licenses` trees when redistributing an environment.
The exact local resolved versions and license paths are in
`docs/day20-benchmark.json`; platform wheels and later versions may differ.

- pdfminer.six 20260107: MIT; native extraction engine used by pdfplumber.
- pypdfium2 5.13.0: BSD-3-Clause / Apache-2.0 and bundled dependency notices;
  distribution also includes CC-BY-4.0 data/documentation notice. Retain all
  `LICENSES` and `BUILD_LICENSES`, including PDFium's BSD notice and dependencies.
  No PDF JavaScript/V8 execution is enabled by this adapter.
- cryptography 50.0.2: Apache-2.0 / BSD notices; retain bundled licenses.
- cffi 2.1.1 and pycparser 3.0: retain their MIT-style license notices.
- Pillow/charset-normalizer already existed; their distribution notices remain
  required. This file does not replace an audit of all existing dependencies.

Historical Day20 deployment used PyMuPDF under AGPL/commercial terms. Day29
replaces production raster/search use with an independent public-API pypdfium2
5.13.0 adapter (`pdf_renderer.py`). No PyMuPDF import remains in production;
it is retained for offline fixtures/parity only in `requirements-test.txt`.
Do not deploy the test environment. Historical distributions are not cleared.

## Day29 production PDFium and prepared material

Retain pypdfium2's complete `LICENSES` and platform `data/*/BUILD_LICENSES`
trees, including BSD-3-Clause/Apache-2.0, PDFium and native dependencies.
Metadata also includes CC-BY-4.0 documentation/data notices; this does not
relicense every binary. No PDF JS, document actions or XFA are initialized.

Prepared source: MIT OpenCourseWare / Peter Dourmashkin, Chapter 23: Simple
Harmonic Motion, unchanged original physical PDF pages 3–10 excerpt.
https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs16_chapter23/
License: CC BY-NC-SA 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/.
Retain attribution, noncommercial use and applicable ShareAlike obligations.
Generated declarations/estimated overlays are product annotations, not MIT
endorsement or exact-location guarantees. `prepared/harmonic/manifest.json`
records hashes and provenance. No paid generation was used to package it.
# JSXGraph direct manipulation — Day 24

Vendored browser core **JSXGraph 1.13.3** and its CSS, chosen under the **MIT**
option of `(MIT OR LGPL-3.0-or-later)`; no npm/build dependency at deployment.
Source tag: https://github.com/jsxgraph/jsxgraph/tree/v1.13.3.
Distribution: https://cdn.jsdelivr.net/npm/jsxgraph@1.13.3/distrib/jsxgraphcore.js.
Files/notices: `manipulation/frontend/jsxgraphcore.js`, `jsxgraph.css`,
`LICENSE.jsxgraph.txt`, `vendor-manifest.json`. Preserve all embedded notices,
including the MIT UTF-8 decoder copyright of Bjoern Hoehrmann (2008–2009).
The complete JSXGraph MIT text is retained in `LICENSE.jsxgraph.txt`.
This does not relicense existing dependencies, optional upstream assets or models.

## MIT OCW teaching material — Day 26 evidence

The original source PDF is not included in this repository. Day26 screenshots
reproduce educational content from MIT OpenCourseWare, 8.01SC Classical
Mechanics, Chapter 5: Two Dimensional Kinematics (Peter Dourmashkin / MIT course
team), including Figure 5.3. Source:
https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter5/.
OCW terms: https://ocw.mit.edu/pages/privacy-and-terms-of-use/.
The reproduced educational content is under Creative Commons
Attribution-NonCommercial-ShareAlike 4.0:
https://creativecommons.org/licenses/by-nc-sa/4.0/.
UI grounding annotations and model exploration are additions; the original
source image remains unchanged. No MIT endorsement is implied. This notice
does not relicense application code or its software dependencies.

## MIT OCW Chapter 5 — Day30 prepared derivative

`prepared/projectile/source.pdf` now includes the **unchanged complete** Chapter 5
PDF (16 pages, SHA-256
`688a232388f914ed834e02b28ba343c10b3866e23c3cd94ff38f859957d0c5ec`). The earlier
Day26 statement above describes that historical stage, before this addition.
Peter Dourmashkin / MIT OpenCourseWare course team, 8.01SC Classical Mechanics,
Fall 2016, *Two Dimensional Kinematics*.
[Original resource](https://ocw.mit.edu/courses/8-01sc-classical-mechanics-fall-2016/resources/mit8_01scs22_chapter5/).
[OCW terms](https://ocw.mit.edu/pages/privacy-and-terms-of-use/),
[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/),
[complete legal code](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
Use this educational showcase noncommercially; retain attribution, the license
link, notices and applicable ShareAlike conditions. No endorsement is implied.
The archived-model derivative, provenance additions and screenshots are identified
in [PROVENANCE.md](prepared/projectile/PROVENANCE.md). Exploration annotations are
additions; PDF pixels, text and boxes never follow exploration values. These
source terms do not relicense software or clear historical distribution duties.

## Real teaching corpus and screenshots — Day 27

Original PDFs and extracted subsets are not committed. Exact URLs, original
physical pages, evaluation mappings, SHA-256 hashes and source-specific terms
are recorded in `docs/day27/corpus-manifest.json`. Educational portions of the
four screenshots retain their respective source licenses; model exploration
labels/curves and grounding annotations are additions, not original evidence.

- MIT OpenCourseWare, Peter Dourmashkin / MIT course team: 8.01SC Chapter 6
  (Circular Motion) and Chapter 23 (Simple Harmonic Motion); MIT 6.002 lecture 12
  (first-order circuits). CC BY-NC-SA 4.0 under
  https://ocw.mit.edu/pages/privacy-and-terms-of-use/.
  The original song-lyric page was excluded from the circular subset.
- Allen B. Downey, *Think DSP*: Chapter 1 signal material, CC BY-NC-SA 4.0,
  https://greenteapress.com/thinkdsp/thinkdsp.pdf.
- Allen B. Downey, *Think Python*, second edition: algorithm analysis/search
  and debugging excerpts, CC BY-NC 3.0,
  https://greenteapress.com/thinkpython2/thinkpython2.pdf.
- David M. Diez, Mine Cetinkaya-Rundel and Christopher D. Barr,
  *OpenIntro Statistics*, fourth edition: probability and regression excerpts,
  text under CC BY-SA 3.0. Original accessible PDF:
  https://www.openintro.org/go/?id=os4_for_screen_reader.
  License: https://github.com/OpenIntroStat/openintro-statistics/blob/master/LICENSE.md.
  Cover/branding permissions are separate; neither was included in the subsets.
- NASA, *Tour of the Electromagnetic Spectrum*, third edition: physical PDF
  page 35, unit-conversion table only, under NASA educational/informational
  reuse guidance: https://www.nasa.gov/nasa-brand-center/images-and-media/.
  Third-party photographs were excluded. No NASA or other publisher endorsement
  is implied.

Creative Commons license texts:
https://creativecommons.org/licenses/by-nc-sa/4.0/,
https://creativecommons.org/licenses/by-nc/3.0/,
https://creativecommons.org/licenses/by-sa/3.0/.
This attribution does not relicense application code or resolve existing
PyMuPDF AGPL/commercial deployment obligations.

## Limited public release — 2026-10-13

Streamlit authentication uses Authlib **1.8.0**, BSD-3-Clause; copyright 2017
Hsiaoming Yang. joserfc **1.7.5**, BSD-3-Clause; copyright 2023 Hsiaoming Yang.
Exact Authlib source notice: https://github.com/authlib/authlib/blob/v1.8.0/LICENSE.
These are installed public APIs, with independently authored quota adapters;
no provider tokens, model weights or upstream sample code are bundled.

psycopg and psycopg-binary **3.3.6** are **LGPL-3.0-only**, independently installed
driver distributions (not AGPL). Retain their full installed notices and source
availability/replacement obligations when redistributing; native libpq/OpenSSL
dependencies have their own notices. Exact driver source:
https://github.com/psycopg/psycopg/tree/3.3.6 and LICENSE.txt at that tag.
Installing a wheel is not a blanket license clearance for another platform's
bundled libraries. Linux native-wheel/license review remains a release gate.

New transitive distributions: cffi **2.1.1** (MIT-0), pycparser **3.11**
(BSD-3-Clause), cryptography **50.0.2** (Apache-2.0 OR BSD-3-Clause; choose its
BSD option, retain both distributed texts). Exact installed metadata, nine
copied license files and hashes are retained in
`docs/public-release/new-dependency-licenses.json` and its `licenses/` tree.
Existing PDFium license trees and JSXGraph notices remain unchanged. PyMuPDF
remains test-only; do not deploy `requirements-test.txt` or historical fixtures.

Public smoke source/screenshot: the unchanged first two pages of the existing
prepared MIT OCW Chapter 23 excerpt, with the attribution and CC BY-NC-SA 4.0
terms above. Replayed analysis is explicitly an offline test, not new paid AI
grounding evidence. These software notices do not alter source-material terms.
