"""Review-only homepage + prepared example; unchanged app.py owns all four views.

This entrypoint cannot collect participant data. No model/upload traffic is
allowed. The prepared-entry button is a disclosed study accommodation appended
to the real empty homepage, not a deployed onboarding feature.
"""
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import streamlit as st
from day28_prepared import install

def deny_request(*args, **kwargs):
    st.session_state["day28_blocked_requests"] = st.session_state.get("day28_blocked_requests", 0) + 1
    raise RuntimeError("Prepared example: new AI requests and uploads disabled")


with patch("openai.resources.responses.Responses.create", side_effect=deny_request), \
     patch("openai.resources.files.Files.create", side_effect=deny_request):
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")

st.caption("Day 28 準備示例 · 內容已預先生成；不是本次即時 AI 分析。")
st.caption("教材：MIT OpenCourseWare / Peter Dourmashkin，Chapter 23: Simple Harmonic Motion。原頁內容未改；僅摘選原 PDF 第 3–10 頁。CC BY-NC-SA 4.0。")
if not st.session_state.get("analysis"):
    st.button("試用準備好的示例 / Try a prepared example", key="day28-open-prepared",
              on_click=install, args=(st.session_state,))
st.caption("此預覽僅提供準備示例。自己的教材由正式入口執行真正 AI 分析，需等待且可能安全退化或拒絕。")

