"""Zero-model browser acceptance fixtures; never used by the production app.

python -B -m streamlit run tests/manual_analogy.py --server.port 8523
"""
import runpy
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"tests")]
import streamlit as st
import pymupdf
from analogy_fixtures import formal,spec
from analogy.validator import normalize
from analogy.state import ensure,identity,save,parameter_registry
from scene.state import fingerprint,cache_key as scene_key
from source_atlas.model import semantic_fingerprint,semantic_catalog,normalize_atlas
from source_atlas.state import cache_key
from source_atlas.schema import VERSION
from source_lens import new_source_state
from atlas_fixtures import region,page_texts
from support import fixture,load_app_helpers

labels={"electricity":"電路與水流","phase":"相位與指針","queue":"佇列與排隊"}
kind=st.sidebar.selectbox("離線驗收案例",list(labels),format_func=lambda k:labels[k])
st.sidebar.caption("合成教材與已驗證譬喻；模型呼叫為零。正式產品不載入這些案例。")
if st.session_state.get("analogy_demo_kind")!=kind:
    scene,catalog=formal(kind);raw=spec(kind);analysis=fixture()
    material="offline-analogy-"+kind
    focus=scene["objects"][0]["semantic_id"] if scene else "fifo"
    raw["formal_focus"]=focus
    analysis.update(analysis_language="zh-TW",quick_summary="離線合成驗收教材："+labels[kind],
        learning_scene_candidate=dict(suitable=bool(scene),domain="spatial_dynamics" if scene else "none",reason="離線驗收模型"))
    if not scene:
        analysis["concept_map"]["nodes"]=[dict(id="fifo",label="先進先出佇列",source_pages=[1],role="primary")]
        analysis["concept_map"]["edges"]=[]
        analysis["visual_flow"]={"suitable":False,"reason":"","nodes":[],"edges":[]}
        catalog=semantic_catalog(None,analysis)
    h=load_app_helpers(); primary=h["clean_primary_visualization"](analysis["primary_visualization"])
    graph=h["clean_concept_map"](analysis["concept_map"],[1])
    path=h["clean_learning_path"](analysis["learning_path"],[1],primary["type"],graph)
    lab=h["clean_interactive_lab"](analysis.get("interactive_lab"),[1],path,h["valid_source_pages"])
    registry=parameter_registry(dict(scene=scene),lab,path,catalog)
    normalized=normalize(raw,catalog,registry,[1],focus)
    signature=fingerprint([semantic_fingerprint(scene,catalog),lab,path])
    store=ensure({},material,"zh-TW",signature)
    save(store,identity(material,"zh-TW",signature,focus),normalized)
    with pymupdf.open() as doc:
        page=doc.new_page(width=600,height=500)
        text={"electricity":["Ohm's law: V = I R","Voltage V","Resistance R","Current I = V / R"],"phase":["sin(t + phase)","Phase / angle","Sine signal"],"queue":["Queue: First in, first out","Arrivals are processed in arrival order"]}[kind]
        for i,line in enumerate(text): page.insert_text((50,60+i*70),line,fontsize=19)
        pdf=doc.tobytes()
    ids={"electricity":["voltage","resistance","current"],"phase":["angle","wave"],"queue":["fifo"]}[kind]
    regions=[region("anchor_"+i,1,(.06,(95+n*70)/500,.95,(145+n*70)/500),catalog[i]["label"],[i],"label","labels",excerpt=text[n+1]) for n,i in enumerate(ids)]
    atlas=normalize_atlas(dict(atlas_version=VERSION,processed_pages=[1],regions=regions),[1],catalog,page_texts(pdf))
    st.session_state.update(analysis=analysis,analysis_id=material,allowed_source_pages=[1],source_context=dict(kind="pdf",page_texts=page_texts(pdf)),product_language="zh-TW",
        learning_workspace=dict(material_id=material,mode="explore",focus=focus if not scene else None,representation="analogy"),analogy_world_state=store,
        learning_scene_cache={scene_key(material,"zh-TW","spatial_dynamics"):scene} if scene else {},
        source_atlas_cache={cache_key(material,pdf,"zh-TW",[1],scene,catalog):atlas},
        learning_canvas=dict(material_id=material,selected_id=None,kind=None,component=None,style_signature=None,last_event=-1,fallback=False,component_error=False,source=new_source_state(material,pdf)),
        analogy_demo_kind=kind)
runpy.run_path(str(ROOT/"app.py"),run_name="__main__")
