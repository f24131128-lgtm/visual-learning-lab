# Dependency audit

Fresh production Python 3.12 installation resolved 54 distributions. `pip check`
passed. `requirements-day29-lock.txt` captures that closure, excluding pip-audit's
own tooling. The audit used trusted PyPI advisory data via pip-audit with exact
pins and no resolver:

```text
python -m pip_audit --disable-pip --no-deps -r requirements-day29-lock.txt -f json -o docs/day29/dependency-advisories.json --timeout 30
```

`dependency-advisories.json` contains all 54 packages and zero returned known
advisories; `dependency-advisories-final.log` records successful completion.
The first attempt used an invalid flag combination; a second ran before a pin
file existed because of an audit script UTF-8 error. Those failures remain in
logs; neither was treated as a successful audit. This is not a zero-vulnerability
guarantee. Native libraries within wheels, unknown vulnerabilities, JS transitive
dependencies and other platform wheel builds are not comprehensively scanned.

`dependency-metadata.json` records exact installed versions/license paths and
checks all three vendored JSXGraph 1.13.3 manifest hashes: PASS. MIT is the chosen
dual-license option; embedded notices and `LICENSE.jsxgraph.txt` are retained.
No blanket dependency upgrade was performed. A fresh resolver selected current
compatible versions inside existing constraints; lock pins document them.
Only the production raster dependency changed: PyMuPDF → pypdfium2 5.13.0.
jsonschema is now declared directly because main base validation uses it.
PyMuPDF and pdfplumber remain in the separate offline test requirements.
