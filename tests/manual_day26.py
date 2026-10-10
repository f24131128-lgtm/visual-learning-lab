"""Transparent evidence wrapper around unchanged production entrypoint.

Starts empty: real file upload and explicit build buttons are required. No seed,
fixture, prompt override or learner-facing instrumentation. Private source and
declarations stay in ignored .day26-local. Maximum seven explicit SDK attempts,
SDK retries disabled. All later interactions must use existing local owners.
"""
import json
import importlib
import runpy
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import streamlit as st
from openai.resources.responses import Responses

PRIVATE = ROOT / ".day26-local"
PRIVATE.mkdir(exist_ok=True)
record_path = PRIVATE / "requests.json"
# Streamlit reruns can overlap. Keep one SDK method rather than wrapping a
# previous run's observer (which would duplicate/overwrite request records).
original_create = getattr(Responses, "_day26_original_create", Responses.create)
seen = set()
while getattr(original_create, "__name__", "") == "observed_create":
    if id(original_create) in seen:
        raise RuntimeError("Recursive evidence observer")
    seen.add(id(original_create))
    original_create = original_create.__globals__["original_create"]
Responses._day26_original_create = original_create


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


def observed_create(client, **kwargs):
    records = json.loads(record_path.read_text(encoding="utf-8")) if record_path.exists() else []
    if len(records) >= 7:
        denied = PRIVATE / "blocked-requests.json"
        entries = json.loads(denied.read_text(encoding="utf-8")) if denied.exists() else []
        entries.append(dict(stage=kwargs.get("text", {}).get("format", {}).get("name", "unknown")))
        save(denied, entries[-20:])
        raise AssertionError("Day26 acceptance request ceiling reached; local interaction must not request AI.")
    stage = kwargs.get("text", {}).get("format", {}).get("name", "unknown")
    record = dict(attempt=len(records)+1, stage=stage, model=kwargs.get("model"),
                  sdk_retries=0, status="started", seconds=None)
    records.append(record)
    save(record_path, records)  # Record failed attempts too; never retry implicitly.
    client._client.max_retries = 0
    started = time.perf_counter()
    try:
        response = original_create(client, **kwargs)
        raw = json.loads(response.output_text)
        save(PRIVATE / f"response-{record['attempt']}.json", raw)
        record.update(status="returned", seconds=time.perf_counter()-started,
                      usage={key: getattr(response.usage, key, None) for key in
                             ("input_tokens", "output_tokens", "total_tokens")})
        return response
    except Exception as error:
        record.update(status="failed", failure_type=type(error).__name__, seconds=time.perf_counter()-started)
        raise
    finally:
        save(record_path, records)


Responses.create = observed_create
# runpy's entrypoint is outside Streamlit's import watcher. Refresh the two
# edited presentation modules once for this live acceptance session.
if getattr(Responses, "_day26_presentation_revision", None) != 2:
    for name in ("workspace.ui", "source_atlas.runtime", "source_atlas.compiler"):
        if name in sys.modules: importlib.reload(sys.modules[name])
    Responses._day26_presentation_revision = 2
runpy.run_path(str(ROOT / "app.py"), run_name="__main__")

# Inspect existing owners after each completed rerun. No new runtime state.
wrapper = st.session_state.get("learning_scene_state") or {}
atlas = st.session_state.get("source_atlas_state") or {}
world = wrapper.get("world") or {}
workspace = st.session_state.get("learning_workspace") or {}
plans = st.session_state.get("learning_world_plans") or {}
report = dict(material=st.session_state.get("analysis_id"), mode=workspace.get("mode"),
              focus=world.get("focus", workspace.get("focus")), world=world,
              scene=wrapper.get("scene"), scene_error=wrapper.get("validation_reason"),
              atlas=atlas.get("atlas"), selected_region=atlas.get("region_hint"), page=atlas.get("page"),
              analysis=st.session_state.get("analysis"), allowed_pages=st.session_state.get("allowed_source_pages"),
              payload_measurement=wrapper.get("world_timings"),
              planner=plans.get("cache", {}).get(plans.get("active")),
              lab=st.session_state.get("interactive_lab_state"))
save(PRIVATE / "session.json", report)
