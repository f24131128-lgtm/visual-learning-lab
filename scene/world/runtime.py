"""A contained coordinated browser clock and automatic planar fallback.

The browser receives numeric projections and fixed product code, not expressions
to execute. Its messages return through the canonical semantic reducer.
"""

import json
from pathlib import Path
import re
import time

import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from i18n import tr
from presentation import TOKENS
from .engine import frames, references, snapshot
from .schema import MAX_PAYLOAD_BYTES
from .policy import parameter_display, time_domain, union_bounds
from .state import acknowledge_rejection, changes, consume_event, new_state, replay_states
from ..state import fingerprint

_component = components.declare_component("semantic_learning_world", path=str(Path(__file__).parent / "frontend"))

LABELS = ("Spatial Scene", "Signal / Waveform", "Vector / Phasor", "Equation / State Lens", "Time", "Play", "Pause", "Replay", "Reset time", "Playback speed", "Current", "Baseline", "Delta", "What changed?", "Drag a highlighted handle; click a waveform or trajectory to explore the same system.", "Click a waveform or select an object to explore the same system.", "Replay exploration", "Comparison", "Local exploration", "Planar model (z = 0)", "Replay complete", "Set baseline", "Reset to baseline", "Clear comparison", "Updating shared state…", "Try this", "Run experiment", "Exploration Recording & Replay", "Start recording", "Stop recording", "Clear recording", "Recording", "Recording stopped", "Recorded steps: {count}", "Replay speed", "Replay step {step} / {count}", "Initial state", "Focus", "3D camera", "2D interaction", "3D camera unavailable; synchronized 2D remains active.", "Synchronized planar camera (z = 0)", "Drag to rotate; scroll to zoom.")


def scene_identity(scene):
    return fingerprint({key: value for key, value in scene.items() if key not in ("validation_report", "quantity_order")})


def frame_data(scene, wrapper, parameters):
    cache = wrapper.setdefault("world_numeric_cache", {})
    key = fingerprint([scene_identity(scene), parameters])
    if key not in cache:
        cache[key] = frames(scene, parameters)
        while len(cache) > 4: cache.pop(next(iter(cache)))
    return cache[key]


def payload(scene, wrapper, replay=None):
    state = wrapper["world"]
    started = time.perf_counter()
    tables = {}
    def table(parameters):
        key = fingerprint(parameters)
        if key not in tables: tables[key] = frame_data(scene, wrapper, parameters)
        return key
    def dataset(local):
        current_key = table(local["parameters"])
        baseline_key = table(local["baseline"]["parameters"]) if local["baseline"] else None
        viewport = union_bounds([tables[current_key]["axes"]] + ([tables[baseline_key]["axes"]] if baseline_key else []))
        return {"frames_ref": current_key, "axes": viewport, "current": snapshot(scene, local),
                "baseline": snapshot(scene, local["baseline"]) if local["baseline"] else None,
                "baseline_frames_ref": baseline_key}
    quantities = {q["id"]: q for q in scene["quantities"]}
    labels = {q["id"]: q["label"] for q in scene["quantities"]} | {p["id"]: p["label"] for p in scene["parameters"]} | {"time": tr("Time")}
    def human(expression):
        return re.sub(r"\b[A-Za-z][A-Za-z0-9_]*\b", lambda match: labels.get(match.group(), match.group()), expression)
    def family(identifier):
        found, queue = {identifier}, [identifier]
        while queue:
            current = queue.pop()
            for ref in references(quantities[current]["expression"]) & quantities.keys():
                if ref not in found: found.add(ref); queue.append(ref)
        return sorted(found)
    result = {
        "identity": scene_identity(scene), "revision": state["revision"], "axes": scene["axes"], "theme_css": TOKENS,
        "learner_view": True,
        "time": time_domain(scene, {p["id"]: p["default"] for p in scene["parameters"]}),
        "objects": scene["objects"], "series": scene["series"], "metrics": scene["metrics"], "parameters": [p | {"display": parameter_display(p)} for p in scene["parameters"]],
        "quantities": [{"id": q["id"], "label": q["label"], "unit": q["unit"], "equation": human(q["expression"]), "family": family(q["id"])} for q in scene["quantities"]],
        "inverse": [{k: b[k] for k in ("id", "type", "object_id", "target_id")} for b in scene["inverse_bindings"]],
        "experiments": [{k: e[k] for k in ("id", "title", "learning_goal")} for e in scene["experiments"]],
        "recording": {"active": state["recording"], "count": len(state["recorded"])},
        "labels": {label: tr(label) for label in LABELS+("Fixed value", "Generated exploration range")}, "data": dataset(state), "replay": [], "tables": tables,
        "replay_generation": state["replay_generation"], "replay_indices": [], "replay_summaries": [],
    }
    if replay:
        # Presentation may skip semantic no-ops, never mutate or skip validation
        # of recorded actions. Commit indices refer to the original sequence.
        previous = None
        for index, local in enumerate(replay):
            if previous is not None and local == previous: continue
            rows = changes(scene, local | {"baseline": None, "previous": previous}) if previous else []
            summary = [f"{r['label']}: {r['before']:.4g} → {r['after']:.4g} {r['unit']}" for r in rows if r["label"] in {p["label"] for p in scene["parameters"]}]
            if previous and local["time"] != previous["time"]: summary.append(tr("Time") + f": {previous['time']:.4g} → {local['time']:.4g} " + scene["time"]["unit"])
            if previous and local["focus"] != previous["focus"]: summary.append(tr("Focus") + ": " + labels.get(local["focus"], tr("Choose a concept or source object")))
            if previous and local["baseline"] != previous["baseline"]: summary.append(tr("Comparison"))
            result["replay"].append(dataset(local)); result["replay_indices"].append(index)
            result["replay_summaries"].append(" · ".join(summary[:3]) or tr("Initial state"))
            previous = local
    encoded = json.dumps(result, allow_nan=False, ensure_ascii=False).encode()
    if len(encoded) > MAX_PAYLOAD_BYTES:
        raise ValueError("Coordinated view payload exceeds bound.")
    wrapper["world_timings"] = {"payload_seconds": time.perf_counter()-started, "payload_bytes": len(encoded)}
    return result


def plotly_fallback(scene, state):
    """Automatic planar snapshot when the coordinated view cannot render."""
    data = snapshot(scene, state)
    sampled = frames(scene, state["parameters"])
    fig = go.Figure()
    for obj in scene["objects"]:
        nums = data["projections"][obj["id"]]
        if obj["type"] == "trajectory":
            x, y = sampled["projections"][obj["id"]]
        elif obj["type"] in ("vector", "axis"):
            x, y = [nums[0]-(nums[2] if obj["type"] == "axis" else 0), nums[0]+nums[2]], [nums[1]-(nums[3] if obj["type"] == "axis" else 0), nums[1]+nums[3]]
        else:
            x, y = [nums[0]], [nums[1]]
        fig.add_trace(go.Scatter(x=x, y=y, mode="markers" if obj["type"] == "point" else "lines+markers", name=obj["label"], line={"width": 4 if obj["semantic_id"] == state["focus"] else 2}))
    fig.update_layout(height=380, margin=dict(l=0, r=0, t=0, b=0), xaxis_title=scene["axes"]["x_label"], yaxis_title=scene["axes"]["y_label"], yaxis=dict(scaleanchor="x", scaleratio=1), uirevision="world-snapshot")
    st.plotly_chart(fig, use_container_width=True, key="world-widget-snapshot-"+scene_identity(scene))


def render_world(scene, wrapper, format_pages, source_context=None, allowed_pages=()):
    state = wrapper.setdefault("world", new_state(scene))
    prefix = "world-widget-" + wrapper["material_id"] + "-"
    with st.container():
        st.caption(tr("Spatial Learning World"))
        st.markdown("#### " + scene["title"])
        st.caption(scene["learning_goal"])
        replay = wrapper.pop("world_pending_replay", None)
        if state.pop("replay_requested", False): replay = replay_states(scene, state)
        control_error = wrapper.pop("world_control_error", None)
        if control_error: st.info(control_error)
        # Headings are real Streamlit elements too: AppTest can verify the normal
        # PDF render path; browser-only SVG interaction needs browser/live QA.
        try:
            data = payload(scene, wrapper, replay)
            from manipulation.runtime import render_world as render_manipulation
            direct = render_manipulation(scene, wrapper)
            if direct:
                with st.expander(tr("Playback and comparison workspace")):
                    st.markdown("**"+tr("Spatial Scene")+" · "+tr("Signal / Waveform")+" · "+tr("Vector / Phasor")+" · "+tr("Equation / State Lens")+"**")
                    event = _component(payload=data, key=prefix+"coordinated", default=None)
            else:
                st.markdown("**"+tr("Spatial Scene")+" · "+tr("Signal / Waveform")+" · "+tr("Vector / Phasor")+" · "+tr("Equation / State Lens")+"**")
                event = _component(payload=data, key=prefix+"coordinated", default=None)
            if consume_event(scene, state, data["identity"], event):
                st.rerun()
            if acknowledge_rejection(state, data["identity"], event):
                wrapper["world_control_error"] = tr("That change is outside this validated model. The world was preserved.")
                st.rerun()
        except (ValueError, TypeError, KeyError):
            st.info(tr("The interactive view is unavailable. The current state is shown below; your learning is preserved."))
            plotly_fallback(scene, state)
        # Accessible state values also provide regression evidence after gestures.
        selected = next((q for q in scene["quantities"] if q["id"] == state["focus"]), None)
        if selected:
            selected_value = snapshot(scene, state)["values"][state["focus"]]
            st.caption(selected["label"]+f": {selected_value:.6g} "+selected["unit"])
        rows = changes(scene, state)
        if rows:
            st.caption(tr("What changed?"))
            st.caption(" · ".join(f"{r['label']}: {r['before']:.4g} → {r['after']:.4g} {r['unit']} (Δ {r['delta']:+.3g}"+(f", {r['percent']:+.1f}%" if r["percent"] is not None else "")+")" for r in rows[:6]))
        pages = selected["source_pages"] if selected else []
        if pages:
            st.caption(format_pages(pages))
            canvas = st.session_state.get("learning_canvas")
            if isinstance(canvas, dict) and canvas.get("material_id") == wrapper["material_id"] and source_context:
                from source_lens import render_source_lens
                render_source_lens(canvas["source"], wrapper["material_id"], "world-"+state["focus"], selected["label"], pages, source_context, allowed_pages)
        st.caption(tr("This workspace uses one validated semantic scene. All controls run locally after compilation."))
