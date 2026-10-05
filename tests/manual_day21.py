"""Offline Day 21 hero demo; fixtures never enter the production entrypoint.

Run: python -m streamlit run tests/manual_day21.py --server.port 8522
"""
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
import streamlit as st
from test_day21 import hero_data
from support import fixture
from scene.state import cache_key as scene_key
from source_atlas.state import cache_key
from source_lens import new_source_state
from atlas_fixtures import page_texts

if "day21_demo_seeded" not in st.session_state:
    scene, catalog, pdf, atlas = hero_data()
    analysis = fixture()
    analysis.update(analysis_language="zh-TW", learning_scene_candidate=dict(
        suitable=True, domain="spatial_dynamics", reason="Offline validated projectile fixture"))
    material = "day21-offline-projectile"
    st.session_state.update(analysis=analysis, analysis_id=material,
        allowed_source_pages=[1, 2], source_context=dict(kind="pdf", page_texts=page_texts(pdf)),
        product_language="zh-TW", learning_scene_cache={scene_key(material, "zh-TW", "spatial_dynamics"): scene},
        source_atlas_cache={cache_key(material, pdf, "zh-TW", [1, 2], scene, catalog): atlas},
        learning_canvas=dict(material_id=material, selected_id=None, kind=None, component=None,
            style_signature=None, last_event=-1, fallback=False, component_error=False, source=new_source_state(material, pdf)),
        learning_workspace=dict(material_id=material, mode="source", focus=None), day21_demo_seeded=True)
runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
