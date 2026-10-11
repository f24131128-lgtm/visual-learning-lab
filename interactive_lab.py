"""Validated declarative experiments, material-specific controls, and local charts."""

import hashlib
import html
import json
import math

import numpy as np
import streamlit as st

from i18n import FONT_STACK, tr
from semantic_contract import numeric_domain
from quantity_contract import (FACTS_SCHEMA, PROVENANCE_FIELDS, ROLE_SCHEMA, can_commit,
    check_commit, check_values, normalize_facts, source_values, validate_parameter,
    evaluate_quantity, validate_quantity_expression)
from representation_contract import REFS_SCHEMA, bind as bind_ownership
from safe_math import MAX_POINTS, MathExpressionError, evaluate_expression, valid_identifier, valid_variable, validate_expression


def _object(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def _array(items, maximum, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": maximum}


STRING = {"type": "string"}
NUMBER = {"type": "number", "minimum": -1e9, "maximum": 1e9}
LAB_VERSION = "2.0"
INTERACTIVE_LAB_SCHEMA = _object({
    "version": {"type": "string", "enum": [LAB_VERSION]},
    "suitable": {"type": "boolean"}, "reason": STRING,
    "demos": _array(_object({
        "id": STRING, "title": STRING, "learning_goal": STRING, "formula_display": STRING,
        "source_facts": FACTS_SCHEMA,
        "x": _object({"id": STRING, "label": STRING, "min": NUMBER, "max": NUMBER,
                      "points": {"type": "integer", "minimum": 50, "maximum": MAX_POINTS},
                      "semantic_role": {"type": "string", "enum": ["runtime_time", "independent_variable"]},
                      "provenance": {"type": ["string", "null"], "enum": [None, "source_variable", "hypothetical_exploration"]}}),
        "parameters": _array(_object({
            "id": STRING, "label": STRING, "min": NUMBER, "max": NUMBER,
            "default": NUMBER, "step": NUMBER, "unit": STRING,
            "source_pages": FACTS_SCHEMA["items"]["properties"]["source_pages"],
            **PROVENANCE_FIELDS, "semantic_refs": REFS_SCHEMA,
        }), 4),
        "series": _array(_object({"id": STRING, "label": STRING, "expression": STRING,
            "provenance": {"type": "string", "enum": ["derived"]}, "semantic_refs": REFS_SCHEMA}), 3, 1),
        "derived_metrics": _array(_object({"id": STRING, "label": STRING, "expression": STRING, "unit": STRING,
            "provenance": {"type": "string", "enum": ["derived"]}, "semantic_refs": REFS_SCHEMA}), 4),
        "try_this": _array(STRING, 3),
        "source_pages": _array({"type": "integer", "minimum": 1}, 8),
        "related_step_ids": _array(STRING, 6),
    }), 2),
})

LAB_INSTRUCTIONS = """
- interactive_lab version is 2.0. Every parameter explicitly declares provenance:
  source_fixed, source_variable, or hypothetical_exploration. Derived quantities
  belong in series/derived_metrics with provenance derived, never controls.
  Keep reported measurements, statistics, coefficients, event probabilities and
  example conditions immutable as source_facts or singleton source_fixed parameters.
  Preserve their exact stated values, validated pages and a short evidence paraphrase.
  If a what-if varies a source fact, use a DIFFERENT parameter ID with provenance
  hypothetical_exploration and source_baseline_ref pointing to that immutable fact.
  A model default is an initial exploration value, not automatically a source value.
  source_variable requires source evidence that it is a variable. expose_control
  explicitly opts a legal variable/hypothetical parameter into learner adjustment;
  a variable need not have a slider. source_fixed has expose_control false and step 0.
  Use source_baseline_ref null when there is no specific immutable baseline.
  Runtime time is separate: x.semantic_role runtime_time, x.provenance null.
  Other independent axes use independent_variable with explicit source_variable or
  hypothetical_exploration provenance. Do not classify elapsed time as a parameter.
  Source facts may be referenced as constants in safe expressions.
  Each series, metric and control supplies semantic_refs: exact existing formal
  graph-node/comparison-item IDs that it actually represents. Multiple exact refs
  are allowed only when justified by that representation, never merely a related
  lesson, matching label or topic. Use [] if ownership is uncertain. Refer to IDs
  emitted in this same main analysis; do not invent an owner or a drag affordance.
- interactive_lab: independently of the primary visualization, offer a safe 2D
  mathematical experiment only when an explicit relationship in the source would
  become clearer through parameter changes. Prefer ONE useful demo, at most TWO.
  Do not invent an equation for conceptual/non-numeric material: set suitable=false
  and demos=[] when no honest experiment is supported, and briefly explain why.
  Each demo has one independent x variable, 0–4 scalar parameters, 1–3 series,
  optionally 0–4 scalar derived_metrics, and up to 3 short actionable try_this prompts.
  Use stable unique ASCII identifiers starting with a letter (letters/digits/_ only,
  max 48 characters, no double underscores); display labels may use mathematical
  symbols. IDs must be distinct across facts, x, parameters, series and metrics.
  Each exposed control must meaningfully change a curve. Formula display should
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
    try:
        check_values(demo["parameters"], values)
    except ValueError as error:
        raise MathExpressionError(str(error)) from error
    for parameter in demo["parameters"]:
        value = _finite(values[parameter["id"]])
        if not parameter["min"] <= value <= parameter["max"]:
            raise MathExpressionError("Parameter outside its validated range.")
    x = np.linspace(demo["x"]["min"], demo["x"]["max"], demo["x"]["points"])
    environment = {**source_values(demo), **values, demo["x"]["id"]: x}
    curves = {}
    for series in demo["series"]:
        result = evaluate_quantity(series["expression"], environment)
        curves[series["id"]] = np.full_like(x, result) if np.isscalar(result) else result
    return x, curves


def _clean_demo(raw, allowed_pages, valid_steps, validate_pages, *, version=None, catalog=None, material=None):
    if not isinstance(raw, dict):
        raise ValueError("Invalid demo.")
    demo = {key: _text(raw.get(key)) for key in ("title", "learning_goal", "formula_display")}
    demo["id"] = _id(raw.get("id"), set())
    modern = version == LAB_VERSION
    demo["contract_version"] = LAB_VERSION if modern else "legacy_read_only"
    x = raw["x"]
    symbols = set()
    demo["x"] = {"id": _id(x.get("id"), symbols, True), "label": _text(x.get("label"), 100),
                 "min": _finite(x.get("min")), "max": _finite(x.get("max")), "points": x.get("points")}
    if demo["x"]["min"] >= demo["x"]["max"] or type(x.get("points")) is not int or not 50 <= x["points"] <= MAX_POINTS:
        raise ValueError("Invalid x range.")
    if modern:
        role, provenance = x.get("semantic_role"), x.get("provenance")
        if not ((role == "runtime_time" and provenance is None) or (role == "independent_variable" and provenance in ("source_variable", "hypothetical_exploration"))):
            raise ValueError("Invalid independent axis semantic role")
        demo["x"].update(semantic_role=role, provenance=provenance)
    demo["source_facts"] = normalize_facts(raw["source_facts"], allowed_pages, symbols) if modern else []
    symbols.update(f["id"] for f in demo["source_facts"])
    facts = {f["id"]: f for f in demo["source_facts"]}
    parameters = raw["parameters"]
    if not isinstance(parameters, list) or not 0 <= len(parameters) <= 4:
        raise ValueError("Invalid parameter count.")
    demo["parameters"] = []
    for raw_parameter in parameters:
        parameter = {"id": _id(raw_parameter.get("id"), symbols, True),
                     "label": _text(raw_parameter.get("label"), 100), "unit": _text(raw_parameter.get("unit"), 40, True)}
        parameter.update({field: _finite(raw_parameter.get(field)) for field in ("min", "max", "default", "step")})
        parameter["parameter_kind"] = numeric_domain(parameter)
        if modern:
            for key in PROVENANCE_FIELDS: parameter[key] = raw_parameter.get(key)
            parameter["source_pages"] = validate_pages(raw_parameter.get("source_pages", []), allowed_pages)
            parameter["semantic_refs"] = raw_parameter.get("semantic_refs")
            validate_parameter(parameter, facts, allowed_pages)
        demo["parameters"].append(parameter)
    representation_ids = set(symbols) | {demo["id"]}
    for field, minimum, maximum in (("series", 1, 3), ("derived_metrics", 0, 4)):
        entries = raw[field]
        if not isinstance(entries, list) or not minimum <= len(entries) <= maximum:
            raise ValueError("Invalid expression count.")
        seen = representation_ids
        demo[field] = []
        names = symbols if field == "series" else symbols - {x["id"]}
        for item in entries:
            entry = {"id": _id(item.get("id"), seen), "label": _text(item.get("label"), 100),
                     "expression": validate_quantity_expression(_text(item.get("expression"), 400), names)}
            if field == "derived_metrics":
                entry["unit"] = _text(item.get("unit"), 40, True)
            if modern:
                if item.get("provenance") != "derived": raise ValueError("Expression quantity must be derived")
                entry.update(provenance="derived", semantic_refs=item.get("semantic_refs"))
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
        evaluate_quantity(metric["expression"], source_values(demo) | values)
    if modern:
        demo["ownership"] = bind_ownership(demo, catalog or {}, material, allowed_pages)
    return demo


def clean_interactive_lab(raw, allowed_pages, learning_path, validate_pages, *, catalog=None, material=None):
    """Drop individual malformed demos; other analysis never depends on this result."""
    result = {"suitable": False, "reason": "", "demos": [], "rejected": 0}
    if not isinstance(raw, dict) or raw.get("suitable") is not True:
        return result
    if raw.get("version") not in (None, LAB_VERSION):
        result["rejected"] = 1
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
            demo = _clean_demo(raw_demo, allowed_pages, valid_steps, validate_pages,
                version=raw.get("version"), catalog=catalog, material=material)
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
    signature = hashlib.sha256(json.dumps([LAB_VERSION, lab["demos"]], sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:16]
    if not isinstance(state, dict) or state.get("material_id") != material_id or state.get("signature") != signature:
        reset_lab_state()
        state = {"material_id": material_id, "signature": signature,
                 "selected_id": lab["demos"][0]["id"] if lab["demos"] else None,
                  "demos": {demo["id"]: {"values": default_values(demo), "compare": True, "specification": demo, "control_generation": 0} for demo in lab["demos"]}}
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
    try:
        commit_lab_values(saved["specification"], saved, {parameter_id: st.session_state[widget_key]})
    except MathExpressionError:
        st.session_state[widget_key+"-numeric-rejected"] = True
    except (ValueError, KeyError):
        return


def commit_lab_values(demo, saved, changes):
    """One atomic value boundary for sliders, inverses and analogy bindings."""
    if saved.get("specification") != demo or not isinstance(changes, dict) or not 1 <= len(changes) <= 4:
        raise ValueError("Stale or unbound Lab declaration")
    parameters = {p["id"]: p for p in demo["parameters"]}
    candidate = dict(saved["values"])
    for identifier, value in changes.items():
        if identifier not in parameters: raise ValueError("Unknown Lab control")
        candidate[identifier] = check_commit(parameters[identifier], value)
    compute_curves(demo, candidate)
    for metric in demo["derived_metrics"]:
        evaluate_quantity(metric["expression"], source_values(demo) | candidate)
    saved["values"] = candidate


def _save_compare(state, demo_id, widget_key):
    state["demos"][demo_id]["compare"] = st.session_state[widget_key]


def _reset_parameters(state, demo, prefix):
    state["demos"][demo["id"]]["values"] = default_values(demo)
    saved = state["demos"][demo["id"]]
    saved["control_generation"] = saved.get("control_generation", 0) + 1
    for parameter in demo["parameters"]:
        st.session_state[f"{prefix}-{parameter['id']}"] = parameter["default"]


def build_lab_chart(demo, values, compare):
    # Optional chart imports stay within the isolated rendering boundary.
    import plotly.graph_objects as go
    from presentation import PLOT_STYLE

    x, current = compute_curves(demo, values)
    baseline = compute_curves(demo, default_values(demo))[1] if compare else {}
    figure = go.Figure()
    colors = ["#6750C5", "#087E8B", "#B85B17"]
    for index, series in enumerate(demo["series"]):
        color = colors[index]
        label = html.escape(series["label"])
        if compare:
            figure.add_trace(go.Scatter(x=x, y=baseline[series["id"]], name=f"{label} · {tr('Initial exploration')}",
                                       mode="lines", line={"color": color, "width": 2, "dash": "dash"}, opacity=0.55))
        figure.add_trace(go.Scatter(x=x, y=current[series["id"]], name=f"{label} · {tr('Current exploration')}" if compare else label,
                                   mode="lines", line={"color": color, "width": 3}))
    figure.update_layout(template="plotly_white", height=390, margin={"l": 12, "r": 12, "t": 20, "b": 12},
                         font={"family": FONT_STACK, "size": 14, "color": PLOT_STYLE["foreground"]}, hovermode="x unified",
                         paper_bgcolor="rgba(0,0,0,0)",
                         xaxis_title=html.escape(demo["x"]["label"]), yaxis_title=tr("Value"),
                         showlegend=compare or len(demo["series"]) > 1,
                         legend={"orientation": "h", "y": -0.22},
                         uirevision=demo["id"])
    figure.update_xaxes(showgrid=True, gridcolor=PLOT_STYLE["grid"], zerolinecolor=PLOT_STYLE["axis"])
    figure.update_yaxes(showgrid=True, gridcolor=PLOT_STYLE["grid"], zerolinecolor=PLOT_STYLE["axis"])
    return figure


def _render_demo(demo, state, learning_path, go_to_lesson, format_pages):
    prefix = f"lab-widget-{state['material_id']}-{state['signature']}-{demo['id']}"
    saved = state["demos"][demo["id"]]
    st.markdown(f"#### {demo['title']}")
    st.write(demo["learning_goal"])
    if demo.get("contract_version") == "legacy_read_only":
        st.caption(tr("Earlier experiment · values are read-only until provenance is declared."))
    st.latex(demo["formula_display"])
    if demo["source_pages"]:
        st.caption(tr("Source: {pages}", pages=format_pages(demo["source_pages"])))
    plot = st.container()
    controls = st.expander(tr("Parameters and comparison"))
    with controls:
        if demo.get("source_facts"):
            st.markdown("**" + tr("Source values") + "**")
            for fact in demo["source_facts"]:
                st.text(f"{fact['label']}: {fact['value']:.6g} {fact['unit']}")
                st.caption(fact["source_evidence"])
                if fact["source_pages"]: st.caption(tr("Source: {pages}", pages=format_pages(fact["source_pages"])))
        st.button(tr("Reset parameters"), key=f"{prefix}-reset", on_click=_reset_parameters, args=(state, demo, prefix))
        for parameter in demo["parameters"]:
            key = f"{prefix}-{parameter['id']}"
            generation = saved.get("control_generation", 0)
            if generation: key += f"-control-{generation}"
            st.session_state[key] = saved["values"][parameter["id"]]
            label = parameter["label"] + (f" ({parameter['unit']})" if parameter["unit"] else "")
            if not can_commit(parameter):
                st.text(label+": "+f"{parameter['default']:.5g}")
                st.caption(tr("Source value" if parameter.get("provenance") == "source_fixed" else "Read-only value"))
                continue
            st.caption(tr("Generated exploration range"))
            if parameter.get("provenance") == "hypothetical_exploration": st.caption(tr("Hypothetical control · the source stays unchanged."))
            st.caption(tr("Initial exploration: {value}", value=f"{parameter['default']:.6g}"))
            st.slider(label, min_value=parameter["min"], max_value=parameter["max"], step=parameter["step"],
                      key=key, on_change=_save_parameter, args=(state, demo["id"], parameter["id"], key, generation))
            if st.session_state.pop(key+"-numeric-rejected", False):
                st.info(tr("This experiment is undefined for these values. Adjust the parameters or reset to defaults."))
        compare_key = f"{prefix}-compare"
        st.session_state[compare_key] = saved["compare"]
        st.checkbox(tr("Compare with default"), key=compare_key, on_change=_save_compare, args=(state, demo["id"], compare_key))
    with plot:
        try:
            from manipulation.runtime import render_lab as render_manipulation
            direct = render_manipulation(demo, saved, state["material_id"], learning_path)
            chart = build_lab_chart(demo, saved["values"], saved["compare"])
            with st.expander(tr("Curve and default comparison"), expanded=saved["compare"]) if direct else st.container():
                st.plotly_chart(chart, use_container_width=True, key=f"{prefix}-chart", config={"displaylogo": False})
        except MathExpressionError:
            st.info(tr("This experiment is undefined for these values. Adjust the parameters or reset to defaults."))
        except Exception:
            st.info(tr("This experiment could not be displayed. Your lesson and review are still available."))
        for metric in demo["derived_metrics"]:
            try:
                value = evaluate_quantity(metric["expression"], source_values(demo) | saved["values"])
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
    st.caption(tr("Explore the model. Changes are computed locally."))
    state = ensure_lab_state(material_id, lab)
    if len(lab["demos"]) > 1:
        columns = st.columns(len(lab["demos"]))
        for column, demo in zip(columns, lab["demos"]):
            column.button(demo["title"], key=f"lab-widget-select-{material_id}-{demo['id']}",
                          type="primary" if state["selected_id"] == demo["id"] else "secondary",
                          on_click=select_demo, args=(state, demo["id"]))
    demo = next(demo for demo in lab["demos"] if demo["id"] == state["selected_id"])
    with st.container():
        try:
            _render_demo(demo, state, learning_path, go_to_lesson, format_pages)
        except Exception:
            st.info(tr("This experiment could not be displayed. Your lesson and review are still available."))
