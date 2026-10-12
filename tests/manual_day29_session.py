"""Test-only two-browser material isolation probe, zero AI requests.

B is a clearly synthetic text fixture; it is not a prepared product example.
"""
import runpy
import sys
from pathlib import Path
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from support import fixture,load_app_helpers
from prepared_demo import install_prepared

def install_b():
    st.session_state.clear()
    analysis=fixture();analysis['quick_summary']='SESSION B SYNTHETIC SOURCE — independent material'
    analysis['analysis_language']='en'
    st.session_state.update(analysis=analysis,analysis_id='day29-session-B',analysis_language='en',
        allowed_source_pages=[],source_context=dict(kind='text',source_text='SESSION B SOURCE CANARY. Incoming material is transformed into resulting material.',page_texts={}),
        learning_workspace=dict(material_id='day29-session-B',mode='source',focus=None,representation='formal'),product_language='en')

st.caption('DAY29 TEST ONLY · A=real prepared PDF, B=synthetic text · separate browser sessions')
if not st.session_state.get('analysis'):
    st.button('Load session A PDF',on_click=install_prepared,args=(st.session_state,load_app_helpers()))
    st.button('Load session B text',on_click=install_b)
runpy.run_path(str(ROOT/'app.py'),run_name='__main__')
st.caption('TEST MATERIAL '+str(st.session_state.get('analysis_id','empty'))+' · paid generation server-disabled')
