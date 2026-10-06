"""Three Phase C real-model recordings in production UI; paid API disabled.
Run from repository root: python -B -m streamlit run tests/manual_phase_c.py --server.port 8526
"""
import json,runpy,sys
from pathlib import Path
from unittest.mock import patch
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/"tests")]
import streamlit as st
import day23_benchmark as bench
from day23_phase_c_benchmark import manifest,HOME
from learning_world import compiler,planner
from source_atlas.model import semantic_catalog
CASES=("nested_sum","scoped_labels","fixed_decay")
choice=st.sidebar.selectbox("Day23 Phase C recorded review",CASES,key="phase-c-review-selector")
st.sidebar.caption("Frozen Phase C model recordings; production runtime; live API blocked. Identity scene rejected independently; its retained formal graph remains available.")
if st.session_state.get("phase_c_review_case")!=choice:
 case=next(c for c in manifest()["payload"]["materials"] if c["material_id"]==choice)
 directory=HOME/"declarations"/choice
 raw=json.loads((directory/"analysis.json").read_text(encoding="utf-8"))["raw"]
 analysis,path,lab=bench.prepare_analysis(raw);material="phase-c-review-"+choice
 source=dict(kind="text",source_text=case["text"],page_texts={});cat=semantic_catalog(None,analysis)
 caps=compiler.capabilities(analysis,{},lab);store=compiler.ensure({},material)
 key=compiler.identity(material,"en",source,cat,caps,None)
 declaration=json.loads((directory/"planner.json").read_text(encoding="utf-8"))["raw"]
 plan=planner.normalize(declaration,cat,[],caps);store["cache"][key]=plan;store["active"]=key
 # Material switches reset recorded review's scene only, as normal new analysis does.
 for name in ("learning_scene_state","learning_scene_cache","source_atlas_state","source_info"):
  st.session_state.pop(name,None)
 st.session_state.update(analysis=raw,analysis_id=material,product_language="en",allowed_source_pages=[],source_context=source,
  learning_world_plans=store,learning_workspace=dict(material_id=material,mode="explore",focus=None,
  representation="execution" if plan["family"]=="execution" else "formal"),phase_c_review_case=choice)
 raw["analysis_language"]="en"
 if choice=="fixed_decay":
  from scene.state import cache_key,ensure_state,save_scene
  scene=bench.normalize_scene(json.loads((directory/"scene.json").read_text(encoding="utf-8"))["raw"],[])
  wrapper=ensure_state(material,"en","spatial_dynamics");save_scene(wrapper,scene)
with patch("openai.resources.responses.responses.Responses.create",side_effect=RuntimeError("Recorded Phase C review has no live API access")):
 runpy.run_path(str(ROOT/"app.py"),run_name="__main__")
