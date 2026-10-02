"""Offline source↔world fixture QA. No compiler/network/API calls."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import streamlit as st
from i18n import tr
from presentation import render_header
from source_lens import new_source_state
from source_atlas.model import normalize_atlas, semantic_catalog
from source_atlas.state import cache_key
from source_atlas.runtime import render_atlas
from scene.world.validator import normalize_world
from scene.world.state import new_state
from scene.runtime import render_scene
from tests.atlas_fixtures import source_pdf, atlas_fixture, page_texts
from tests.world_fixtures import three_phase_world, complete_projectile_world

st.set_page_config(page_title="Day 19 offline acceptance",layout="wide")
render_header()
st.caption("離線測試教材與定位 fixture，非真實模型生成結果；不使用 API。")
name=st.selectbox("測試教材",["三相波形與相量","拋體來源圖"])
if st.session_state.get("atlas_acceptance") != name:
    system="phasor" if name=="三相波形與相量" else "projectile"
    pdf=source_pdf(system)
    scene=normalize_world((three_phase_world if system=="phasor" else complete_projectile_world)(),[1,2])
    catalog=semantic_catalog(scene)
    key=cache_key("offline-atlas",pdf,"zh-TW",[1,2],scene,catalog)
    state=dict(key=key,atlas=normalize_atlas(atlas_fixture(system),[1,2],catalog,page_texts(pdf)),page=1,region_hint=None,seen_focus=None,last_token=None)
    wrapper=dict(material_id="offline-atlas",scene=scene,world=new_state(scene))
    st.session_state["atlas_acceptance_bundle"]=dict(state=state,catalog=catalog,source=new_source_state("offline-atlas",pdf),material_id="offline-atlas",
        source_context=dict(kind="pdf",page_texts=page_texts(pdf)),allowed=[1,2],wrapper=wrapper)
    st.session_state["atlas_acceptance"]=name
bundle=st.session_state["atlas_acceptance_bundle"]
left,right=st.columns([1,1.4])
with right:
    st.markdown("#### "+tr("Interactive Meaning"))
    render_scene(bundle["wrapper"]["scene"],bundle["wrapper"],lambda p:"",bundle["source_context"],[1,2])
with left:render_atlas(bundle)
