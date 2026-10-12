"""Install an offline sitecustomize for the exact final unittest CLI.

Existing tests explicitly mock paid sites; a forgotten mock must fail closed.
"""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'.day29-local/offline-guard';folder.mkdir(parents=True,exist_ok=True)
(folder/'sitecustomize.py').write_text('''import atexit
import json
from pathlib import Path
from unittest.mock import patch
blocked = []
def deny(*args, **kwargs):
    blocked.append("unexpected provider request")
    raise AssertionError("Day29 offline regression prohibits real provider calls")
response_guard = patch("openai.resources.responses.Responses.create", side_effect=deny)
file_guard = patch("openai.resources.files.Files.create", side_effect=deny)
response_guard.start()
file_guard.start()
@atexit.register
def evidence():
    Path("docs/day29/final-request-guard.json").write_text(json.dumps({"unexpected_requests_blocked":len(blocked),"real_provider_calls":0}),encoding="utf-8")
''',encoding='utf-8')
