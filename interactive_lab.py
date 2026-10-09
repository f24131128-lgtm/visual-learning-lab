"""Validated declarative experiments, material-specific controls, and local charts."""

import hashlib
import html
import json
import math

import numpy as np
import streamlit as st

from i18n import FONT_STACK, tr
from semantic_contract import numeric_domain
from safe_math import MAX_POINTS, MathExpressionError, evaluate_expression, valid_identifier, valid_variable, validate_expression


def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _array(items, maximum, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


STRING = {"type": "string"}
NUMBER = {"type": "number", "minimum": -1e9, "maximum": 1e9}
INTERACTIVE_LAB_SCHEMA = _object({
    "suitable": {"type": "boolean"}, "reason": STRING,
    "demos": _array(_object({
        "id": STRING, "title": STRING, "learning_goal": STRING, "formula_display": STRING,
        "x": _object({"id": STRING, "label": STRING, "min": NUMBER, "max": NUMBER,
                      "points": {"type": "integer", "minimum": 50, "maximum": MAX_POINTS}}),
        "parameters": _array(_object({
            "id": STRING, "label": STRING, "min": NUMBER, "max": NUMBER,
            "default": NUMBER, "step": NUMBER, "unit": STRING,
        }), 4, 1),
        "series": _array(_object({"id": STRING, "label": STRING, "expression": STRING}), 3, 1),
        "derived_metrics": _array(_object({"id": STRING, "label": STRING, "expression": STRING, "unit": STRING}), 4),
        "try_this": _array(STRING, 3),
        "source_pages": _array({"type": "integer", "minimum": 1}, 8),
        "related_step_ids": _array(STRING, 6),
    }), 2),
})

LAB_INSTRUCTIONS = """
- interactive_lab: independently of the primary visualization, offer a safe 2D
  mathematical experiment only when an explicit relationship in the source would
  become clearer through parameter changes. Prefer ONE useful demo, at most TWO.
  Do not invent an equation for conceptual/non-numeric material: set suitable=false
  and demos=[] when no honest experiment is supported, and briefly explain why.
  Each demo has one independent x variable, 1–4 scalar parameters, 1–3 series,
  optionally 0–4 scalar derived_metrics, and up to 3 short actionable try_this prompts.
  Use stable unique ASCII identifiers starting with a letter (letters/digits/_ only,
  max 48 characters, no double underscores); display labels may use mathematical
  symbols. Each parameter must meaningfully change a curve. Formula display should
  be readable math/LaTeX matching the source, never Python code. Keep variable
  meanings and units consistent; disclose any unit conversion in the label/formula.
  Expressions are DATA in a restricted grammar: declared x/parameter identifiers,
  finite numeric constants, pi, e, + - * / **, unary +/-, parentheses, and exactly
  one-argument sin, cos, tan, exp, log (natural logarithm), sqrt, abs. Trigonometric
  functions take radians. No other syntax, functions, strings, attributes, arrays,
  code, imports, or assignments. Do not name variables after functions/pi/e.
  A metric may reference parameters and pi/e, but NOT x, series or other metrics.
  Limit each expression to 400 characters; keep it shallow and simple.
  Fixed source constants may use min=max=default and step=0; they render read-only.
  Do not invent source-supported variation. Other controls are generated exploration
  ranges unless the source explicitly supplies them. Derived metrics are not sliders.
  Choose finite readable adjustable ranges with min < max and defaults within range, positive
  steps no larger than the range, at most 10,000 slider increments; values must be
  within +/-1e9. Use 50–1000 x points, normally about 400. Choose parameter ranges
  and x domains that avoid singularities, invalid logs/roots and overflow. Defaults
  must produce valid finite curves and metrics. Avoid rapid oscillations that the
  selected x sampling cannot resolve. Do not introduce unsupported assumptions.
  source_pages uses only supplied [Page X] markers, or [] for pasted text/unclear
  support. related_step_ids must reference exact learning_path step IDs that teach
  this relationship. Invalid/missing mapping should be []. Try this should invite
  observations while changing one parameter at a time, without grading or claims
  that observations have already occurred.
"""


def _text(value, limit=500, empty=False):
    if not isinstance(value, str) or len(value) > limit or (not empty and not value.strip()):
        raise ValueError("Invalid text.")
    return value.strip()


def _finite(value):
    if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > 1e9:
        raise ValueError("Invalid numeric bound.")
    return float(value)


def _id(value, seen, variable=False):
    if not (valid_variable(value) if variable else valid_identifier(value)) or value in seen:
        raise ValueError("Invalid or duplicate identifier.")
    seen.add(value)
    return value


def default_values(demo):
    return {parameter["id"]: parameter["default"] for parameter in demo["parameters"]}


def compute_curves(demo, values):
    """No callbacks or external operations; bounded pure numeric computation."""
    if set(values) != {parameter["id"] for parameter in demo["parameters"]}:
        raise MathExpressionError("Missing parameters.")
    for parameter in demo["parameters"]:
        value = _finite(values[parameter["id"]])
        if not parameter["min"] <= value <= parameter["max"]:
            raise MathExpressionError("Parameter outside its validated range.")
    x = np.linspace(demo["x"]["min"], demo["x"]["max"], demo["x"]["points"])
    environment = {**values, demo["x"]["id"]: x}
    curves = {}
    for series in demo["series"]:
        result = evaluate_expression(series["expression"], environment)
        curves[series["id"]] = np.full_like(x, result) if np.isscalar(result) else result
    return x, curves


def _clean_demo(raw, allowed_pages, valid_steps, validate_pages):
    if not isinstance(raw, dict):
        raise ValueError("Invalid demo.")
    demo = {key: _text(raw.get(key)) for key in ("title", "learning_goal", "formula_display")}
    demo["id"] = _id(raw.get("id"), set())
    x = raw["x"]
    symbols = set()
    demo["x"] = {"id": _id(x.get("id"), symbols, True), "label": _text(x.get("label"), 100),
                 "min": _finite(x.get("min")), "max": _finite(x.get("max")), "points": x.get("points")}
    if demo["x"]["min"] >= demo["x"]["max"] or type(x.get("points")) is not int or not 50 <= x["points"] <= MAX_POINTS:
        raise ValueError("Invalid x range.")
    parameters = raw["parameters"]
    if not isinstance(parameters, list) or not 1 <= len(parameters) <= 4:
        raise ValueError("Invalid parameter count.")
    demo["parameters"] = []
    for raw_parameter in parameters:
        parameter = {"id": _id(raw_parameter.get("id"), symbols, True),
                     "label": _text(raw_parameter.get("label"), 100), "unit": _text(raw_parameter.get("unit"), 40, True)}
        parameter.update({field: _finite(raw_parameter.get(field)) for field in ("min", "max", "default", "step")})
        parameter["parameter_kind"] = numeric_domain(parameter)
        demo["parameters"].append(parameter)
    for field, minimum, maximum in (("series", 1, 3), ("derived_metrics", 0, 4)):
        entries = raw[field]
        if not isinstance(entries, list) or not minimum <= len(entries) <= maximum:
            raise ValueError("Invalid expression count.")
        seen = set()
        demo[field] = []
        names = symbols if field == "series" else symbols - {x["id"]}
        for item in entries:
            entry = {"id": _id(item.get("id"), seen), "label": _text(item.get("label"), 100),
                     "expression": validate_expression(_text(item.get("expression"), 400), names)}
            if field == "derived_metrics":
                entry["unit"] = _text(item.get("unit"), 40, True)
            demo[field].append(entry)
    prompts = raw.get("try_this")
    if not isinstance(prompts, list) or len(prompts) > 3:
        raise ValueError("Invalid observation prompts.")
    demo["try_this"] = [_text(prompt, 300) for prompt in prompts]
    demo["source_pages"] = validate_pages(raw.get("source_pages", []), allowed_pages)
    refs = raw.get("related_step_ids", [])
    demo["related_step_ids"] = list(dict.fromkeys(step for step in refs if isinstance(step, str) and step in valid_steps)) if isinstance(refs, list) else []
    values = default_values(demo)
    compute_curves(demo, values)  # Fail independently before creating any UI controls.
    for metric in demo["derived_metrics"]:
        evaluate_expression(metric["expression"], values)
    return demo


def clean_interactive_lab(raw, allowed_pages, learning_path, validate_pages):
    """Drop individual malformed demos; other analysis never depends on this result."""
    result = {"suitable": False, "reason": "", "demos": [], "rejected": 0}
    if not isinstance(raw, dict) or raw.get("suitable") is not True:
        return result
    result["reason"] = raw.get("reason", "") if isinstance(raw.get("reason"), str) else ""
    if not isinstance(raw.get("demos"), list):
        result["rejected"] = 1
        return result
    valid_steps = {step["id"] for step in (learning_path or {}).get("steps", [])}
    seen = set()
    result["rejected"] = max(0, len(raw["demos"]) - 2)
    for raw_demo in raw["demos"][:2]:
        try:
            demo = _clean_demo(raw_demo, allowed_pages, valid_steps, validate_pages)
            if demo["id"] in seen:
                raise ValueError("Duplicate demo ID.")
            seen.add(demo["id"])
            result["demos"].append(demo)
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError):
            result["rejected"] += 1
    result["suitable"] = bool(result["demos"])
    return result


def reset_lab_state():
    st.session_state.pop("interactive_lab_state", None)
    for key in list(st.session_state):
        if isinstance(key, str) and key.startswith("lab-widget-"):
            st.session_state.pop(key, None)


def ensure_lab_state(material_id, lab):
    state = st.session_state.get("interactive_lab_state")
    signature = hashlib.sha256(json.dumps(lab["demos"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    if not isinstance(state, dict) or state.get("material_id") != material_id or state.get("signature") != signature:
        reset_lab_state()
        state = {"material_id": material_id, "signature": signature,
                 "selected_id": lab["demos"][0]["id"] if lab["demos"] else None,
                 "demos": {demo["id"]: {"values": default_values(demo), "compare": True} for demo in lab["demos"]}}
        st.session_state["interactive_lab_state"] = state
    return state


def related_demos(lab, step_ids):
    return [demo for demo in (lab or {}).get("demos", []) if set(demo["related_step_ids"]).intersection(step_ids)]


def select_demo(state, demo_id):
    if demo_id in state["demos"]:
        state["selected_id"] = demo_id
        from workspace.state import open_workspace
        workspace = st.session_state.get("learning_workspace")
        if workspace:
            workspace["representation"] = "formal"
            open_workspace(workspace, "explore")


def render_lab_links(lab, step_ids, material_id, key_prefix, recommended=False):
    """One mapping serves lessons, review, and inspector; no duplicate charts."""
    demos = related_demos(lab, step_ids)
    if not demos:
        return
    state = ensure_lab_state(material_id, lab)
    st.markdown(f"**{tr('Recommended experiment' if recommended else 'Interactive experiment')}**")
    for demo in demos:
        if recommended:
            for prompt in demo["try_this"]:
                st.write(f"• {prompt}")
        if st.button(tr("Open lab: {title}", title=demo["title"]), key=f"lab-open-{key_prefix}-{material_id}-{demo['id']}", on_click=select_demo, args=(state, demo["id"])):
            st.caption(tr("Experiment selected below: {title}", title=demo["title"]))
        st.markdown(f"[{tr('Go to Interactive Lab')}](#interactive-lab)")
    # Reuse this existing mapping for inspector, lessons, and actual review mistakes.
    # Deferred import keeps the scene module separate from lab validation/state.
    from dynamic_simulation import render_simulation_links
    render_simulation_links(lab, step_ids, material_id, key_prefix, recommended)


def _save_parameter(state, demo_id, parameter_id, widget_key, generation=None):
    saved = state["demos"][demo_id]
    if generation is not None and generation != saved.get("control_generation", 0):
        return  # A retired pre-gesture widget cannot overwrite canonical values.
    saved["values"][parameter_id] = st.session_state[widget_key]


def _save_compare(state, demo_id, widget_key):
    state["demos"][demo_id]["compare"] = st.session_state[widget_key]


def _reset_parameters(state, demo, prefix):
    state["demos"][demo["id"]]["values"] = default_values(demo)
    if state["demos"][demo["id"]].get("control_generation"):
        state["demos"][demo["id"]]["control_generation"] += 1
    for parameter in demo["parameters"]:
        st.session_state[f"{prefix}-{parameter['id']}"] = parameter["default"]


def build_lab_chart(demo, values, compare):
    # Optional chart imports stay within the isolated rendering boundary.
    import plotly.graph_objects as go

    x, current = compute_curves(demo, values)
    baseline = compute_curves(demo, default_values(demo))[1] if compare else {}
    figure = go.Figure()
    colors = ["#6750C5", "#087E8B", "#B85B17"]
    for index, series in enumerate(demo["series"]):
        color = colors[index]
        label = html.escape(series["label"])
        if compare:
            figure.add_trace(go.Scatter(x=x, y=baseline[series["id"]], name=f"{label} · {tr('Default')}",
                                       mode="lines", line={"color": color, "width": 2, "dash": "dash"}, opacity=0.55))
        figure.add_trace(go.Scatter(x=x, y=current[series["id"]], name=f"{label} · {tr('Current')}" if compare else label,
                                   mode="lines", line={"color": color, "width": 3}))
    figure.update_layout(template="plotly_white", height=390, margin={"l": 12, "r": 12, "t": 20, "b": 12},
                         font={"family": FONT_STACK, "size": 15, "color": "#30264D"}, hovermode="x unified",
                         xaxis_title=html.escape(demo["x"]["label"]), yaxis_title=tr("Value"),
                         showlegend=compare or len(demo["series"]) > 1,
                         legend={"orientation": "h", "y": -0.22},
                         uirevision=demo["id"])
    figure.update_xaxes(showgrid=True, gridcolor="#EEEAF5", zerolinecolor="#B7ADCB")
    figure.update_yaxes(showgrid=True, gridcolor="#EEEAF5", zerolinecolor="#B7ADCB")
    return figure


def _render_demo(demo, state, learning_path, go_to_lesson, format_pages):
    prefix = f"lab-widget-{state['material_id']}-{state['signature']}-{demo['id']}"
    saved = state["demos"][demo["id"]]
    st.markdown(f"#### {demo['title']}")
    st.write(demo["learning_goal"])
    st.latex(demo["formula_display"])
    if demo["source_pages"]:
        st.caption(tr("Source: {pages}", pages=format_pages(demo["source_pages"])))
    controls, plot = st.columns([1, 2], gap="large")
    with controls:
        st.button(tr("Reset parameters"), key=f"{prefix}-reset", on_click=_reset_parameters, args=(state, demo, prefix))
        for parameter in demo["parameters"]:
            key = f"{prefix}-{parameter['id']}"
            generation = saved.get("control_generation", 0)
            if generation: key += f"-control-{generation}"
            st.session_state[key] = saved["values"][parameter["id"]]
            label = parameter["label"] + (f" ({parameter['unit']})" if parameter["unit"] else "")
            if parameter.get("parameter_kind") == "fixed":
                st.text(label+": "+f"{parameter['default']:.5g}")
                st.caption(tr("Fixed value"))
                continue
            st.caption(tr("Generated exploration range"))
            st.slider(label, min_value=parameter["min"], max_value=parameter["max"], step=parameter["step"],
                      key=key, on_change=_save_parameter, args=(state, demo["id"], parameter["id"], key, generation))
        compare_key = f"{prefix}-compare"
        st.session_state[compare_key] = saved["compare"]
        st.checkbox(tr("Compare with default"), key=compare_key, on_change=_save_compare, args=(state, demo["id"], compare_key))
    with plot:
        try:
            from manipulation.runtime import render_lab as render_manipulation
            render_manipulation(demo, saved, state["material_id"], learning_path)
            chart = build_lab_chart(demo, saved["values"], saved["compare"])
            st.plotly_chart(chart, use_container_width=True, key=f"{prefix}-chart", config={"displaylogo": False})
        except MathExpressionError:
            st.info(tr("This experiment is undefined for these values. Adjust the parameters or reset to defaults."))
        except Exception:
            st.info(tr("This experiment could not be displayed. Your lesson and review are still available."))
        for metric in demo["derived_metrics"]:
            try:
                value = evaluate_expression(metric["expression"], saved["values"])
                st.metric(metric["label"], f"{value:.5g} {metric['unit']}".strip())
            except MathExpressionError:
                st.caption(tr("Metric unavailable for these parameters: {label}", label=metric["label"]))
    if demo["try_this"]:
        st.markdown(f"**{tr('Try this')}**")
        for prompt in demo["try_this"]:
            st.write(f"• {prompt}")
    for number, step in enumerate((learning_path or {}).get("steps", []), 1):
        if step["id"] in demo["related_step_ids"]:
            st.caption(tr("Related lesson: Step {number} — {title}", number=number, title=step["title"]))
            if st.button(tr("Go to lesson step"), key=f"{prefix}-lesson-{step['id']}"):
                go_to_lesson(step["id"], learning_path)
                st.rerun()


def render_interactive_lab(lab, material_id, learning_path, go_to_lesson, format_pages):
    if lab["rejected"]:
        st.caption(tr("Some experiment data was invalid and was skipped. Other learning content is still available."))
    if not lab["suitable"]:
        return  # No empty panel for conceptual material or legacy analyses.
    # A single stable anchor survives both UI languages.
    st.subheader(tr("Interactive Lab"), anchor="interactive-lab")
    st.caption(tr("Move a slider to explore. Changes are computed locally; no AI request is made."))
    state = ensure_lab_state(material_id, lab)
    if len(lab["demos"]) > 1:
        columns = st.columns(len(lab["demos"]))
        for column, demo in zip(columns, lab["demos"]):
            column.button(demo["title"], key=f"lab-widget-select-{material_id}-{demo['id']}",
                          type="primary" if state["selected_id"] == demo["id"] else "secondary",
                          on_click=select_demo, args=(state, demo["id"]))
    demo = next(demo for demo in lab["demos"] if demo["id"] == state["selected_id"])
    with st.container(border=True):
        try:
            _render_demo(demo, state, learning_path, go_to_lesson, format_pages)
        except Exception:
            st.info(tr("This experiment could not be displayed. Your lesson and review are still available."))
