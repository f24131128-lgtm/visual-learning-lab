"""Normal app, three original engineering PDFs; paid actions blocked."""
import runpy
import sys
import json
import copy
from pathlib import Path
from unittest.mock import patch
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import streamlit as st
from twin_fixtures import fixture
from source_lens import new_source_state
from scene.state import cache_key

labels = {"phase": "A 相位與波形", "projectile": "B 發射向量與軌跡", "math": "C 仿射關係與錨點"}
kind = st.sidebar.selectbox("Day 25 離線驗收", list(labels), format_func=lambda k: labels[k], key="day25-case")
st.sidebar.caption("原創三頁工程測試 PDF；非真實教材驗證。模型請求被阻擋，互動 API 差值 0。")
if st.session_state.get("day25_seed") != kind:
    from learning_canvas import reset_canvas_state
    from scene.state import reset_scene_state
    from interactive_lab import reset_lab_state
    reset_scene_state(); reset_lab_state(); reset_canvas_state()
    data = fixture(kind)
    material, scene = data["material"], data["scene"]
    st.session_state.update(analysis=data["analysis"], analysis_id=material, product_language="zh-TW",
        allowed_source_pages=[1,2,3], source_context=dict(kind="pdf", source_text="\n".join(data["texts"].values()), page_texts=data["texts"]),
        learning_scene_cache={cache_key(material,"zh-TW","spatial_dynamics"):scene} if scene else {},
        learning_canvas=dict(material_id=material, selected_id=None, kind=None, component=None, style_signature=None, last_event=-1,
                             fallback=False, component_error=False, source=new_source_state(material, data["pdf"])),
        learning_workspace=dict(material_id=material, mode="source", focus=None, representation="formal"),
        source_atlas_cache={data["atlas_state"]["key"]:data["atlas_state"]["atlas"]},
        source_atlas_state=data["atlas_state"], day25_seed=kind)
with patch("openai.resources.responses.Responses.create", side_effect=AssertionError("Paid actions are disabled in the offline acceptance app.")):
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")