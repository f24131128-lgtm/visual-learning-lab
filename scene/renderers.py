"""Whitelisted renderers for normalized probability Learning Scenes."""

from graphviz import Digraph
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from .expressions import display_expression, evaluate_expression
from .probability import (
    MONTE_CARLO_COUNTS, de_morgan, format_probability, inclusion_exclusion,
    monte_carlo, probability,
)


def _event_pair(scene):
    return (scene["events"][0], scene["events"][1]) if len(scene["events"]) >= 2 else (None, None)


def active_set(scene, state):
    if state.get("selected_outcome_id"):
        return frozenset([state["selected_outcome_id"]])
    expression = state.get("active_expression") or scene["focus_targets"][0]["expression"]
    return evaluate_expression(expression, scene["event_sets"], [item["id"] for item in scene["outcomes"]])


def source_caption(pages, format_pages):
    if pages:
        st.caption(tr("Source: {pages}", pages=format_pages(pages)))


def render_controls(scene, state):
    targets = list(scene["focus_targets"])
    left, right = _event_pair(scene)
    if left and right:
        generated = [
            (f"{left['id']} | {right['id']}", f"{left['label']} ∪ {right['label']}"),
            (f"{left['id']} & {right['id']}", f"{left['label']} ∩ {right['label']}"),
            (f"~{left['id']}", f"{left['label']}ᶜ"), (f"~{right['id']}", f"{right['label']}ᶜ"),
            (f"{left['id']} - {right['id']}", f"{left['label']} − {right['label']}"),
            (f"{right['id']} - {left['id']}", f"{right['label']} − {left['label']}"),
        ]
        existing = {item["expression"] for item in targets}
        targets += [{"id": f"runtime_{i}", "label": label, "expression": expression, "source_pages": []}
                    for i, (expression, label) in enumerate(generated) if expression not in existing]
    options = [item["id"] for item in targets]
    labels = {item["id"]: item["label"] for item in targets}
    current = state.get("selected_focus_id")
    index = options.index(current) if current in options else 0
    label_options = [labels[value] for value in options]
    selected_label = st.selectbox(tr("Event / operation"), label_options, index=index,
                                  key=f"scene-widget-focus-{state['material_id']}")
    selected = options[label_options.index(selected_label)]
    target = next(item for item in targets if item["id"] == selected)
    if selected != state.get("selected_focus_id"):
        state.update(selected_focus_id=selected, active_expression=target["expression"], selected_outcome_id=None)
    if not state.get("active_expression"):
        state["active_expression"] = target["expression"]
    lens_options = ["explore", "de_morgan", "inclusion_exclusion"]
    lens_labels = [tr("Explore"), tr("De Morgan"), tr("Inclusion–Exclusion")]
    lens = st.radio(tr("Learning lens"), lens_labels,
                    index=lens_options.index(state.get("lens", "explore")), horizontal=True,
                    key=f"scene-widget-lens-{state['material_id']}")
    state["lens"] = lens_options[lens_labels.index(lens)] if lens in lens_labels else "explore"


def render_sample_space(scene, state):
    st.markdown("#### " + tr("Sample Space"))
    selected = active_set(scene, state)
    columns = st.columns(min(4, max(1, len(scene["outcomes"]))))
    for index, outcome in enumerate(scene["outcomes"]):
        is_selected = outcome["id"] == state.get("selected_outcome_id")
        in_focus = outcome["id"] in selected
        label = ("● " if is_selected else "✓ " if in_focus else "") + outcome["label"]
        if columns[index % len(columns)].button(label, key=f"scene-widget-outcome-{state['material_id']}-{outcome['id']}",
                                                type="primary" if in_focus else "secondary", use_container_width=True):
            state["selected_outcome_id"] = None if is_selected else outcome["id"]
    st.caption(tr("Click an outcome to focus it across every representation."))


def render_set_view(scene, state):
    st.markdown("#### " + tr("Set View"))
    left, right = _event_pair(scene)
    if not left or not right:
        st.info(tr("This scene needs two events for the set view.")); return
    left_set, right_set, focus = scene["event_sets"][left["id"]], scene["event_sets"][right["id"]], active_set(scene, state)
    zones = {"outside": [], "left": [], "both": [], "right": []}
    for item in scene["outcomes"]:
        identifier = item["id"]
        zone = "both" if identifier in left_set and identifier in right_set else "left" if identifier in left_set else "right" if identifier in right_set else "outside"
        zones[zone].append(item)
    exclusive = not (left_set & right_set)
    anchors = {"outside": (0.5, .08), "left": (.27 if exclusive else .34, .5),
               "both": (.5, .5), "right": (.73 if exclusive else .66, .5)}
    figure = go.Figure()
    figure.add_shape(type="rect", x0=.02, y0=.02, x1=.98, y1=.96, line={"color": "#8277a8"}, fillcolor="#fbfaff")
    left_box = (.12, .42) if exclusive else (.18, .58)
    right_box = (.58, .88) if exclusive else (.42, .82)
    figure.add_shape(type="circle", x0=left_box[0], y0=.2, x1=left_box[1], y1=.82, line={"color": "#6c5ce7", "width": 3}, fillcolor="rgba(108,92,231,.08)")
    figure.add_shape(type="circle", x0=right_box[0], y0=.2, x1=right_box[1], y1=.82, line={"color": "#00a896", "width": 3}, fillcolor="rgba(0,168,150,.08)")
    for zone, items in zones.items():
        x, y = anchors[zone]
        for offset, item in enumerate(items):
            figure.add_trace(go.Scatter(x=[x], y=[y - offset * .075], mode="markers+text",
                marker={"size": 18 if item["id"] in focus else 10, "color": "#f59e0b" if item["id"] in focus else "#6b7280"},
                text=[item["label"]], textposition="middle right", hovertemplate="%{text}<extra></extra>", showlegend=False))
    figure.add_annotation(x=.27, y=.88, text=left["label"], showarrow=False)
    figure.add_annotation(x=.73, y=.88, text=right["label"], showarrow=False)
    figure.update_xaxes(visible=False, range=[0, 1]); figure.update_yaxes(visible=False, range=[0, 1])
    figure.update_layout(height=320, margin=dict(l=4, r=4, t=4, b=4), plot_bgcolor="white")
    st.plotly_chart(figure, use_container_width=True, key=f"scene-set-{state['material_id']}")
    st.caption(tr("Highlighted outcomes are computed from the active expression: {expression}", expression=display_expression(state["active_expression"])))


def render_tree(scene, state):
    if not scene["experiment"]["staged"]: return
    st.markdown("#### " + tr("Probability Tree"))
    graph = Digraph(graph_attr={"rankdir": "LR", "bgcolor": "transparent"})
    graph.node("root", tr("Start"), shape="circle")
    focus = active_set(scene, state)
    nodes = {(): "root"}
    for outcome in scene["outcomes"]:
        prefix = ()
        for depth, value in enumerate(outcome["path"]):
            next_prefix = prefix + (value,)
            if next_prefix not in nodes:
                node_id = "path_" + str(len(nodes)); nodes[next_prefix] = node_id
                graph.node(node_id, outcome["label"] if depth == len(outcome["path"]) - 1 else value,
                           style="filled", fillcolor="#fde68a" if outcome["id"] in focus else "#f4f1ff")
                graph.edge(nodes[prefix], node_id, label=value)
            prefix = next_prefix
    st.graphviz_chart(graph, use_container_width=True)
    leaves = st.columns(min(4, len(scene["outcomes"])))
    for index, outcome in enumerate(scene["outcomes"]):
        if leaves[index % len(leaves)].button(outcome["label"], key=f"scene-widget-leaf-{state['material_id']}-{outcome['id']}", use_container_width=True):
            state["selected_outcome_id"] = outcome["id"]


def render_formula(scene, state):
    st.markdown("#### " + tr("Formula / Reasoning Lens"))
    focus = active_set(scene, state)
    if state.get("selected_outcome_id"):
        outcome = next(item for item in scene["outcomes"] if item["id"] == state["selected_outcome_id"])
        memberships = [f"{outcome['label']} {'∈' if outcome['id'] in scene['event_sets'][event['id']] else '∉'} {event['label']}"
                       for event in scene["events"]]
        st.write(" · ".join(memberships) if memberships else f"**{outcome['label']}** · " + tr("outside the declared events"))
    else:
        p = probability(scene, focus)
        expression = display_expression(state["active_expression"])
        if scene["equally_likely"]:
            st.latex(rf"P({expression}) = \frac{{|{expression}|}}{{|S|}} = \frac{{{len(focus)}}}{{{len(scene['outcomes'])}}}")
        st.metric(f"P({expression})", format_probability(p))
    source_caption(scene["source_pages"], lambda pages: ", ".join(f"p. {p}" for p in pages))


def render_special_lens(scene, state):
    left, right = _event_pair(scene)
    if not left or not right:
        st.info(tr("This lens needs two events.")); return
    if state["lens"] == "de_morgan":
        st.markdown("#### " + tr("De Morgan Lens"))
        result = de_morgan(scene, left["id"], right["id"])
        rows = [
            (f"({left['label']} ∪ {right['label']})ᶜ", f"{left['label']}ᶜ ∩ {right['label']}ᶜ", result["union_complement"]),
            (f"({left['label']} ∩ {right['label']})ᶜ", f"{left['label']}ᶜ ∪ {right['label']}ᶜ", result["intersection_complement"]),
        ]
        for a_label, b_label, (a, b, equal) in rows:
            columns = st.columns(2); columns[0].markdown(f"**{a_label}**  \n{', '.join(sorted(a)) or '∅'}")
            columns[1].markdown(f"**{b_label}**  \n{', '.join(sorted(b)) or '∅'}")
            st.success(tr("Computed sets are identical.")) if equal else st.error(tr("Computed sets differ."))
    elif state["lens"] == "inclusion_exclusion":
        st.markdown("#### " + tr("Inclusion–Exclusion Lens"))
        data = inclusion_exclusion(scene, left["id"], right["id"])
        st.latex(r"P(E \cup F)=P(E)+P(F)-P(E \cap F)")
        st.write(f"{format_probability(data['left'])} + {format_probability(data['right'])} − {format_probability(data['intersection'])} = **{format_probability(data['union'])}**")
        st.caption(tr("The overlap is subtracted once because it was counted in both events."))


def render_monte_carlo(scene, state):
    st.markdown("#### " + tr("Monte Carlo Simulation"))
    samples = st.select_slider(tr("Trials"), options=list(MONTE_CARLO_COUNTS), value=state.get("monte_carlo_samples", 1_000),
                               key=f"scene-widget-samples-{state['material_id']}")
    state["monte_carlo_samples"] = samples
    if st.button(tr("Run again"), key=f"scene-widget-rerun-{state['material_id']}"):
        state["monte_carlo_seed"] = int(state.get("monte_carlo_seed", 17)) + 1
    result = monte_carlo(scene, active_set(scene, state), samples, state.get("monte_carlo_seed", 17))
    columns = st.columns(3)
    columns[0].metric(tr("Theoretical"), f"{result['theoretical']:.4f}")
    columns[1].metric(tr("Empirical"), f"{result['empirical']:.4f}")
    columns[2].metric(tr("Difference"), f"{result['difference']:.4f}")
    x, y = zip(*result["checkpoints"])
    figure = go.Figure(go.Scatter(x=x, y=y, mode="lines", name=tr("Empirical")))
    figure.add_hline(y=result["theoretical"], line_dash="dash", annotation_text=tr("Theoretical"))
    figure.update_layout(height=230, margin=dict(l=8, r=8, t=12, b=8), xaxis_title=tr("Trials"), yaxis_range=[0, 1])
    st.plotly_chart(figure, use_container_width=True, key=f"scene-monte-{state['material_id']}-{state['monte_carlo_seed']}")
