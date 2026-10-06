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

Existing PyMuPDF remains AGPL/commercial: choosing a permissive native-text parser
does not erase the application's existing raster-library obligations. Resolve
the intended deployment/distribution license before public delivery. No AGPL,
GPL, custom-licensed competitor code or models were copied in this sprint.
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
