# Contributing

Read [README](README.md) and [the user guide](docs/USER_GUIDE.md) first.
Use Python 3.12 and a virtual environment. Install `requirements-test.txt` for
local tests; deploy only `requirements.txt`. Never commit secrets or personal PDFs.

Before proposing a change, describe the learner problem and preserve source IDs,
source references, cached analysis and existing fallbacks. Model output remains
untrusted declarative data; never execute it. Add meaningful tests for changed
state, bounds, failure isolation and request counts.

Run `python -X utf8 -B tools/day30_verify.py focused`, then `full` when relevant.
For the local launcher run `python -m unittest discover -s tests -p test_local_launch.py`.
The offline runner blocks provider calls and restores historical reports.
Browser dragging needs separate browser evidence; AppTest alone does not prove it.

PRs should explain the learner-facing change, validation, limitations and any new
licenses/dependencies. Preserve existing notices. This repository has no root
software license grant; do not assume it is MIT-licensed. See THIRD_PARTY_NOTICES.md.
