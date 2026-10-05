"""Offline generic process demo through the production app, with zero AI requests.
Run: python -B -m streamlit run tests/manual_day22.py --server.port 8524
"""
import runpy
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/"tests")]
import streamlit as st
from day22_fixtures import discrete
from learning_world import compiler, planner

kind = st.sidebar.selectbox("Offline process acceptance", ["fifo", "lifo", "states"])
st.sidebar.caption("Synthetic declarations; generic local reducer; no model calls. Production never imports these fixtures.")
if st.session_state.get("day22_demo_kind") != kind:
    analysis, catalog, raw = discrete(kind)
    analysis["analysis_language"] = "zh-TW"
    material = "day22-offline-"+kind
    source = dict(kind="text", source_text=(ROOT/"tests"/"fixtures"/"day22_fifo.txt").read_text(encoding="utf-8") if kind == "fifo" else
                  "Synthetic test material: insert/remove at the last end." if kind == "lifo" else "A workflow starts idle, starts working, then finishes done.")
    caps = compiler.capabilities(analysis, {}, {})
    store = compiler.ensure({}, material)
    key = compiler.identity(material, "zh-TW", source, catalog, caps, None)
    raw["source_pages"] = []
    store["cache"][key] = planner.normalize(raw, catalog, [], caps)
    store["active"] = key
    st.session_state.update(analysis=analysis, analysis_id=material, allowed_source_pages=[], source_context=source,
        learning_world_plans=store, learning_workspace=dict(material_id=material, mode="explore", focus=None, representation="process"),
        day22_demo_kind=kind)
runpy.run_path(str(ROOT/"app.py"), run_name="__main__")
