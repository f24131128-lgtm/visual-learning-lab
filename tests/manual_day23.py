"""Recorded real-model Day23 outputs in the production app. No new API calls.
Run: python -B -m streamlit run tests/manual_day23.py --server.port 8526
"""
import json
import runpy
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
import streamlit as st
import day23_benchmark as bench
from learning_world import compiler, planner
from source_atlas.model import semantic_catalog

CASES = ("rc_charging", "future_lifecycle", "byte_definition")
choice = st.sidebar.selectbox("Day23 recorded real-model review", CASES, key="day23-recorded-selector")
st.sidebar.caption("Recorded prospective model outputs, reused main analysis, production runtime. This replay makes no API request.")
if st.session_state.get("day23_recorded_case") != choice:
    case = next(c for c in bench.read_manifest()["payload"]["materials"] if c["material_id"] == choice)
    directory = bench.HOME / "phase_b" / "declarations" / choice
    analysis = json.loads((directory / "analysis.json").read_text(encoding="utf-8"))["raw"]
    clean, path, lab = bench.prepare_analysis(analysis)
    material = "day23-recorded-" + choice
    source = dict(kind="text", source_text=case["text"], page_texts={})
    catalog = semantic_catalog(None, clean)
    caps = compiler.capabilities(clean, {}, lab)
    store = compiler.ensure({}, material)
    key = compiler.identity(material, "en", source, catalog, caps, None)
    declaration = json.loads((directory / "planner.json").read_text(encoding="utf-8"))["raw"]
    plan = planner.normalize(declaration, catalog, [], caps)
    store["cache"][key] = plan
    store["active"] = key
    analysis["analysis_language"] = "en"
    st.session_state.update(analysis=analysis, analysis_id=material, product_language="en",
        allowed_source_pages=[], source_context=source, learning_world_plans=store,
        learning_workspace=dict(material_id=material, mode="explore", focus=None,
            representation="process" if plan["family"] == "process" else "formal"), day23_recorded_case=choice)
    st.session_state.pop("source_info", None)
with patch("openai.resources.responses.responses.Responses.create", side_effect=RuntimeError("Recorded review has no live API access")):
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")
