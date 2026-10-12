"""AI-SIMULATED RED TEAM lane; frozen human entrypoint remains unchanged."""
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import streamlit as st
from streamlit.delta_generator import DeltaGenerator
from day28_prepared import install
from i18n import tr


def requires_ai(key):
    key = str(key or "")
    return (key == "analyze-material"
            or key.startswith(("explain-", "scene-widget-build-", "world-plan-", "world-plan-new-",
                               "atlas-widget-build-", "analogy-build-", "analogy-new-",
                               "adaptive-build-focused-", "sim-widget-link-"))
            or key.startswith("sim-widget-") and key.endswith("-build"))


def deny_request(*args, **kwargs):
    st.session_state["day28_blocked_requests"] = st.session_state.get("day28_blocked_requests", 0) + 1
    raise RuntimeError("Offline red team: AI requests and uploads disabled")


original_button = DeltaGenerator.button
original_st_button = st.button


def offline_button(self, label, *args, **kwargs):
    if requires_ai(kwargs.get("key")):
        kwargs.update(disabled=True, help=tr("Unavailable in this offline example; use the existing local controls."))
    return original_button(self, label, *args, **kwargs)


def offline_st_button(label, *args, **kwargs):
    if requires_ai(kwargs.get("key")):
        kwargs.update(disabled=True, help=tr("Unavailable in this offline example; use the existing local controls."))
    return original_st_button(label, *args, **kwargs)


st.info(tr("Prepared offline example · previously generated content, no new AI requests."))
st.caption(tr("Own PDF: local upload preview only here. New analysis requires the production app and an explicitly approved AI request."))
if not st.session_state.get("analysis"):
    st.button(tr("Try the prepared example"), key="red-team-open-prepared", on_click=install, args=(st.session_state,))
with patch.object(DeltaGenerator, "button", offline_button), patch.object(st, "button", offline_st_button), \
     patch("openai.resources.responses.Responses.create", side_effect=deny_request), \
     patch("openai.resources.files.Files.create", side_effect=deny_request):
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
st.caption("MIT OpenCourseWare / Peter Dourmashkin · Chapter 23: Simple Harmonic Motion · CC BY-NC-SA 4.0 · original PDF pages 3–10, unchanged.")
# Bounded evidence instrumentation: no source text, credentials or learner data.
st.caption("AI-SIMULATED RED TEAM · new AI/upload attempts: " + str(st.session_state.get("day28_blocked_requests", 0)))
