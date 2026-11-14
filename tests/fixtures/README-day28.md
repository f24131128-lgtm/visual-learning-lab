# Frozen regression input archive

`day28-frozen-inputs.zip` contains only the five otherwise untracked files needed
by the unmodified Day28 freeze/hash checks: two historical SHM response envelopes
and three exact regression reports. These are offline fixtures, not runtime
assets, human-study results, new model output or an API replay instruction.

The underlying MIT OCW / Peter Dourmashkin Chapter 23 source is already attributed
in `prepared/harmonic/manifest.json` (CC BY-NC-SA 4.0). Its identical PDF is reused
from there. Existing frozen manifests own the expected file hashes. The archive
itself has a pinned SHA-256 in `tools/prepare_regression_inputs.py`.

`python tools/prepare_regression_inputs.py` verifies every input before writing.
Existing changed content fails; only a newline representation whose exact hash
matches the frozen hash can be restored. No secrets, account email addresses or
connection strings were found in the five archive members during release review.
Response metadata is retained solely because it is part of the immutable hashes.
Production imports neither this archive nor its preparation tool.
