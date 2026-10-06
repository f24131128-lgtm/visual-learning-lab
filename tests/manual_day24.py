"""Exactly three offline materials in the normal app. No production fixture routing.

python -B -m streamlit run tests/manual_day24.py --server.port 8527
"""
import runpy
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
import pymupdf
import streamlit as st
from manipulation_fixtures import analysis,systems,SOURCES
from scene.state import cache_key
from source_lens import new_source_state
from learning_world.compiler import capabilities

labels={'phase':'A 相位與波形','projectile':'B 發射向量與軌跡','math':'C 仿射關係與錨點'}
kind=st.sidebar.selectbox('Day 24 離線驗收',list(labels),format_func=lambda k:labels[k],key='day24-case')
st.sidebar.caption('三份合成教材；使用正式 app 與既有引擎，模型呼叫為零。')
if st.session_state.get('day24_seed')!=kind:
 from learning_canvas import reset_canvas_state
 from scene.state import reset_scene_state
 from interactive_lab import reset_lab_state
 reset_scene_state();reset_lab_state();reset_canvas_state()
 material='day24-'+kind
 scene=systems()[0 if kind=='phase' else 1] if kind!='math' else None
 with pymupdf.open() as pdf:
  page=pdf.new_page(width=600,height=760)
  page.insert_textbox((45,50,555,700),SOURCES[kind],fontsize=17)
  binary=pdf.tobytes()
 st.session_state.update(analysis=analysis(kind),analysis_id=material,product_language='zh-TW',
  allowed_source_pages=[1],source_context=dict(kind='pdf',source_text=SOURCES[kind],page_texts={1:SOURCES[kind]}),
  learning_scene_cache={cache_key(material,'zh-TW','spatial_dynamics'):scene} if scene else {},
  learning_canvas=dict(material_id=material,selected_id=None,kind=None,component=None,style_signature=None,last_event=-1,fallback=False,component_error=False,source=new_source_state(material,binary)),
  learning_workspace=dict(material_id=material,mode='explore',focus=None,representation='formal'),
  day24_seed=kind)
runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
