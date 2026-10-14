"""Observe the real production prepared UI; block every provider boundary.

No fixtures, fake declarations or private source injection. Evidence contains
only prepared material IDs, numerical state, hashes, and provider attempt counts.
Run: python -m streamlit run tests/manual_day30.py --server.port 8530
"""
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["VLL_LIVE_AI"] = ""
os.environ.pop("OPENAI_API_KEY", None)
import streamlit as st

def deny(*args, **kwargs):
    st.session_state["day30_blocked"] = st.session_state.get("day30_blocked", 0)+1
    raise AssertionError("Day30 offline acceptance forbids provider requests")

with patch("openai.resources.responses.Responses.create", side_effect=deny), patch("openai.resources.files.Files.create", side_effect=deny):
    runpy.run_path(str(ROOT/"app.py"), run_name="__main__")
if st.session_state.get("prepared_demo"):
    scene = st.session_state.get("learning_scene_state", {})
    source = st.session_state.get("learning_canvas", {}).get("source", {})
    lab = st.session_state.get("interactive_lab_state", {})
    report = dict(example=st.session_state["prepared_demo"], material=st.session_state["analysis_id"],
                  world=scene.get("world"), mode=st.session_state["learning_workspace"]["mode"],
                  lab_values={k:v["values"] for k,v in lab.get("demos", {}).items()},
                  blocked_provider_attempts=st.session_state.get("day30_blocked",0), real_provider_calls=0)
    # Source Lens retains bytes under pdf_bytes; expose hashes only.
    report["source_hashes"] = {k:hashlib.sha256(v).hexdigest() for k,v in source.items() if isinstance(v,bytes)}
    (ROOT/"docs/day30/browser-state.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n",encoding="utf8")
