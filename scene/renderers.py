"""Whitelisted renderers for normalized probability Learning Scenes."""

import math

from graphviz import Digraph
import plotly.graph_objects as go
import streamlit as st

from i18n import tr
from .expressions import display_expression, evaluate_expression, expression_event_ids
from .probability import MONTE_CARLO_COUNTS, de_morgan, inclusion_exclusion, monte_carlo, probability


def _event_pair(scene):
    """Return two genuine events; the validator excludes the universe."""
    return (scene["events"][0], scene["events"][1]) if len(scene["events"]) >= 2 else (None, None)


def _event_labels(scene):
    return scene.get("event_labels") or {event["id"]: event["label"] for event in scene["events"]}


def semantic_focus(scene, state):
    """The one canonical local focus consumed by every coordinated view."""
    outcome_map = {outcome["id"]: outcome for outcome in scene["outcomes"]}
    selected_id = state.get("selected_outcome_id")
    if selected_id in outcome_map:
        outcome = outcome_map[selected_id]
        return {
            "outcome_ids": frozenset({selected_id}),
            "selected_outcome_id": selected_id,
            "expression": None,
            "display_label": outcome["label"],
            "source_pages": list(outcome["source_pages"]),
        }

    expression = state.get("active_expression") or scene["focus_targets"][0]["expression"]
    outcome_ids = evaluate_expression(
        expression, scene["event_sets"], [item["id"] for item in scene["outcomes"]]
    )
    target = next(
        (item for item in scene["focus_targets"] if item["expression"] == expression), None
    )
    pages = list(target["source_pages"]) if target else []
    if not pages:
        by_id = {event["id"]: event for event in scene["events"]}
        pages = list(dict.fromkeys(
            page
            for identifier in expression_event_ids(expression)
            for page in by_id[identifier]["source_pages"]
        ))
    return {
        "outcome_ids": frozenset(outcome_ids),
        "selected_outcome_id": None,
        "expression": expression,
        "display_label": display_expression(expression, _event_labels(scene)),
        "source_pages": pages,
    }


def active_set(scene, state):
    return semantic_focus(scene, state)["outcome_ids"]


def source_caption(pages, format_pages):
    if pages:
        st.caption(tr("Source: {pages}", pages=format_pages(pages)))


def _select_outcome(state, outcome_id):
    state["selected_outcome_id"] = (
        None if state.get("selected_outcome_id") == outcome_id else outcome_id
    )


def render_controls(scene, state):
    targets = list(scene["focus_targets"])
    left, right = _event_pair(scene)
    if left and right:
        generated = [
            (left["id"], left["label"]),
            (right["id"], right["label"]),
            (f"{left['id']} | {right['id']}", f"{left['label']} ∪ {right['label']}"),
            (f"{left['id']} & {right['id']}", f"{left['label']} ∩ {right['label']}"),
            (f"~{left['id']}", f"{left['label']}ᶜ"),
            (f"~{right['id']}", f"{right['label']}ᶜ"),
            (f"{left['id']} - {right['id']}", f"{left['label']} − {right['label']}"),
            (f"{right['id']} - {left['id']}", f"{right['label']} − {left['label']}"),
        ]
        existing = {item["expression"] for item in targets}
        targets += [
            {"id": f"runtime_{index}", "label": label, "expression": expression, "source_pages": []}
            for index, (expression, label) in enumerate(generated)
            if expression not in existing
        ]
    # Source Atlas can focus any declared event, not only the first pair used
    # by the special set-operation lenses. Keep expressions canonical.
    existing = {item["expression"] for item in targets}
    targets += [{"id": "source_event_"+event["id"], "label": event["label"], "expression": event["id"], "source_pages": event["source_pages"]}
                for event in scene["events"] if event["id"] not in existing]
    options = [item["id"] for item in targets]
    labels = {item["id"]: item["label"] for item in targets}
    current = state.get("selected_focus_id")
    index = options.index(current) if current in options else 0
    label_options = [labels[value] for value in options]
    selected_label = st.selectbox(
        tr("Event / operation"), label_options, index=index,
        key=f"scene-widget-focus-{state['material_id']}",
    )
    selected = options[label_options.index(selected_label)]
    target = next(item for item in targets if item["id"] == selected)
    if selected != state.get("selected_focus_id"):
        state.update(
            selected_focus_id=selected,
            active_expression=target["expression"],
            selected_outcome_id=None,
        )
    if not state.get("active_expression"):
        state["active_expression"] = target["expression"]

    lens_options = ["explore"]
    lens_labels = [tr("Explore")]
    if left and right:
        lens_options += ["de_morgan", "inclusion_exclusion"]
        lens_labels += [tr("De Morgan"), tr("Inclusion–Exclusion")]
    current_lens = state.get("lens", "explore")
    if current_lens not in lens_options:
        current_lens = "explore"
    lens = st.radio(
        tr("Learning lens"), lens_labels,
        index=lens_options.index(current_lens), horizontal=True,
        key=f"scene-widget-lens-{state['material_id']}",
    )
    state["lens"] = lens_options[lens_labels.index(lens)] if lens in lens_labels else "explore"


def render_sample_space(scene, state):
    st.markdown("#### " + tr("Sample Space"))
    focus = semantic_focus(scene, state)
    columns = st.columns(min(4, max(1, len(scene["outcomes"]))))
    for index, outcome in enumerate(scene["outcomes"]):
        is_selected = outcome["id"] == focus["selected_outcome_id"]
        in_focus = outcome["id"] in focus["outcome_ids"]
        label = ("● " if is_selected else "✓ " if in_focus else "") + outcome["label"]
        columns[index % len(columns)].button(
            label,
            key=f"scene-widget-outcome-{state['material_id']}-{outcome['id']}",
            type="primary" if in_focus else "secondary",
            use_container_width=True,
            on_click=_select_outcome,
            args=(state, outcome["id"]),
        )
    st.caption(tr("Click an outcome to focus it across every representation."))


def set_view_data(scene, state):
    left, right = _event_pair(scene)
    if not left or not right:
        return None
    left_set, right_set = scene["event_sets"][left["id"]], scene["event_sets"][right["id"]]
    focus = semantic_focus(scene, state)
    zones = {"outside": [], "left": [], "both": [], "right": []}
    for outcome in scene["outcomes"]:
        identifier = outcome["id"]
        zone = (
            "both" if identifier in left_set and identifier in right_set
            else "left" if identifier in left_set
            else "right" if identifier in right_set
            else "outside"
        )
        zones[zone].append(outcome)
    status = {}
    for zone, outcomes in zones.items():
        ids = {outcome["id"] for outcome in outcomes}
        overlap = ids & set(focus["outcome_ids"])
        status[zone] = "active" if ids and overlap == ids else "partial" if overlap else "inactive"
    selected_zone = next(
        (zone for zone, outcomes in zones.items()
         if focus["selected_outcome_id"] in {outcome["id"] for outcome in outcomes}), None
    )
    return {
        "left": left, "right": right, "left_set": left_set, "right_set": right_set,
        "zones": zones, "zone_status": status, "selected_zone": selected_zone,
        "focus": focus,
    }


def _arc(cx, cy, radius, start, end, steps=48):
    return [
        (cx + radius * math.cos(start + (end - start) * index / steps),
         cy + radius * math.sin(start + (end - start) * index / steps))
        for index in range(steps + 1)
    ]


def _full_circle(cx, cy, radius):
    return _arc(cx, cy, radius, 0, 2 * math.pi)


def _region_trace(points, fillcolor, name):
    if not points:
        return None
    x, y = zip(*(points + [points[0]]))
    return go.Scatter(
        x=x, y=y, mode="lines", fill="toself", fillcolor=fillcolor,
        line={"width": 0}, hoverinfo="skip", showlegend=False, name=name,
    )


def _zone_fill(status, base):
    if status == "active":
        return "rgba(245,158,11,.42)"
    if status == "partial":
        return "rgba(245,158,11,.22)"
    return base


def build_set_figure(scene, state):
    """Build a membership-faithful two-event Euler/Venn figure inside universe S."""
    data = set_view_data(scene, state)
    if data is None:
        return None
    left_set, right_set = data["left_set"], data["right_set"]
    status = data["zone_status"]
    figure = go.Figure()
    figure.add_shape(
        type="rect", x0=.02, y0=.02, x1=.98, y1=.96,
        line={"color": "#625a7d", "width": 2},
        fillcolor=_zone_fill(status["outside"], "#fbfaff"), layer="below",
    )

    polygons = {}
    circle_specs = []
    anchors = {"outside": (.5, .09), "left": (.29, .52), "both": (.5, .52), "right": (.71, .52)}
    if not (left_set & right_set):
        circle_specs = [(.30, .53, .23), (.70, .53, .23)]
        polygons["left"] = _full_circle(*circle_specs[0])
        polygons["right"] = _full_circle(*circle_specs[1])
        polygons["both"] = []
        anchors.update(left=(.30, .53), right=(.70, .53))
    elif left_set <= right_set or right_set <= left_set:
        outer_is_left = right_set <= left_set
        outer = (.5, .53, .34)
        inner = (.5, .53, .19)
        circle_specs = [outer, inner] if outer_is_left else [inner, outer]
        polygons["both"] = _full_circle(*inner)
        polygons["left" if outer_is_left else "right"] = _full_circle(*outer)
        polygons["right" if outer_is_left else "left"] = []
        anchors.update(both=(.5, .53), left=(.28, .53), right=(.72, .53))
    else:
        left_center, right_center, center_y, radius = .38, .62, .53, .29
        theta = math.acos((right_center - left_center) / (2 * radius))
        left_only = (
            _arc(left_center, center_y, radius, theta, 2 * math.pi - theta)
            + _arc(right_center, center_y, radius, math.pi + theta, math.pi - theta)
        )
        intersection = (
            _arc(left_center, center_y, radius, -theta, theta)
            + _arc(right_center, center_y, radius, math.pi - theta, math.pi + theta)
        )
        right_only = [(1 - x, y) for x, y in left_only]
        polygons.update(left=left_only, both=intersection, right=right_only)
        circle_specs = [(left_center, center_y, radius), (right_center, center_y, radius)]

    base_colors = {
        "left": "rgba(108,92,231,.10)",
        "both": "rgba(99,102,241,.14)",
        "right": "rgba(0,168,150,.10)",
    }
    for zone in ("left", "right", "both"):
        trace = _region_trace(
            polygons.get(zone, []), _zone_fill(status[zone], base_colors[zone]), zone
        )
        if trace is not None:
            figure.add_trace(trace)

    for cx, cy, radius in circle_specs:
        figure.add_shape(
            type="circle", x0=cx - radius, y0=cy - radius, x1=cx + radius, y1=cy + radius,
            line={"color": "#5b5374", "width": 2}, fillcolor="rgba(0,0,0,0)",
        )

    for zone, outcomes in data["zones"].items():
        x, y = anchors[zone]
        for offset, outcome in enumerate(outcomes):
            selected = outcome["id"] == data["focus"]["selected_outcome_id"]
            focused = outcome["id"] in data["focus"]["outcome_ids"]
            figure.add_trace(go.Scatter(
                x=[x], y=[y - offset * .075], mode="markers+text",
                marker={
                    "size": 20 if selected else 15 if focused else 10,
                    "color": "#111827" if selected else "#f59e0b" if focused else "#6b7280",
                    "symbol": "diamond" if selected else "circle",
                    "line": {"color": "white", "width": 2 if selected else 1},
                },
                text=[outcome["label"]], textposition="middle right",
                hovertemplate="%{text}<extra></extra>", showlegend=False,
            ))
    figure.add_annotation(x=.055, y=.91, text="S", showarrow=False, font={"size": 16, "color": "#3f3854"})
    figure.add_annotation(x=.25, y=.88, text=data["left"]["label"], showarrow=False)
    figure.add_annotation(x=.75, y=.88, text=data["right"]["label"], showarrow=False)
    figure.update_xaxes(visible=False, range=[0, 1])
    figure.update_yaxes(visible=False, range=[0, 1])
    figure.update_layout(
        height=340, margin=dict(l=4, r=4, t=4, b=4), plot_bgcolor="white",
        meta={
            "focus_outcome_ids": sorted(data["focus"]["outcome_ids"]),
            "selected_outcome_id": data["focus"]["selected_outcome_id"],
            "zone_status": status,
            "universe": "S",
            "event_ids": [data["left"]["id"], data["right"]["id"]],
        },
    )
    return figure


def render_set_view(scene, state):
    st.markdown("#### " + tr("Set View"))
    figure = build_set_figure(scene, state)
    if figure is None:
        st.info(tr("This scene needs two events for the set view."))
        return
    focus = semantic_focus(scene, state)
    st.plotly_chart(figure, use_container_width=True, key=f"scene-set-{state['material_id']}")
    st.caption(tr(
        "Highlighted outcomes are computed from the active expression: {expression}",
        expression=focus["display_label"],
    ))


def tree_view_data(scene, state):
    focus = semantic_focus(scene, state)
    descendants = {(): set()}
    leaves = {}
    for outcome in scene["outcomes"]:
        path = tuple(outcome["path"])
        if not path:
            continue
        leaves[path] = outcome["id"]
        for depth in range(len(path) + 1):
            descendants.setdefault(path[:depth], set()).add(outcome["id"])
    return {"focus": focus, "descendants": descendants, "leaves": leaves}


def build_tree_graph(scene, state):
    data = tree_view_data(scene, state)
    focus = set(data["focus"]["outcome_ids"])
    graph = Digraph(graph_attr={"rankdir": "LR", "bgcolor": "transparent"})
    root_active = bool(data["descendants"].get((), set()) & focus)
    graph.node(
        "root", tr("Start"), shape="circle", style="filled",
        fillcolor="#fde68a" if root_active else "#f4f1ff",
    )
    node_ids = {(): "root"}
    outcome_map = {outcome["id"]: outcome for outcome in scene["outcomes"]}
    ordered_prefixes = sorted(
        (prefix for prefix in data["descendants"] if prefix),
        key=lambda prefix: (len(prefix), tuple(str(value) for value in prefix)),
    )
    for index, prefix in enumerate(ordered_prefixes, 1):
        node_id = f"tree_{index}"
        node_ids[prefix] = node_id
        outcome_id = data["leaves"].get(prefix)
        label = outcome_map[outcome_id]["label"] if outcome_id else prefix[-1]
        active = bool(data["descendants"][prefix] & focus)
        selected = outcome_id == data["focus"]["selected_outcome_id"]
        graph.node(
            node_id, label, shape="box" if outcome_id else "circle", style="filled",
            fillcolor="#f59e0b" if selected else "#fde68a" if active else "#f4f1ff",
            color="#111827" if selected else "#6d5f9b",
            penwidth="3" if selected else "2" if active else "1",
        )
        parent = prefix[:-1]
        graph.edge(
            node_ids[parent], node_id, label=str(prefix[-1]),
            color="#d97706" if active else "#9ca3af",
            penwidth="3" if active else "1",
        )
    return graph


def render_tree(scene, state):
    if not scene["experiment"]["staged"]:
        return
    st.markdown("#### " + tr("Probability Tree"))
    st.graphviz_chart(build_tree_graph(scene, state), use_container_width=True)
    leaves = st.columns(min(4, len(scene["outcomes"])))
    for index, outcome in enumerate(scene["outcomes"]):
        leaves[index % len(leaves)].button(
            outcome["label"],
            key=f"scene-widget-leaf-{state['material_id']}-{outcome['id']}",
            use_container_width=True,
            on_click=_select_outcome,
            args=(state, outcome["id"]),
        )


def probability_decomposition(scene, outcome_ids):
    value = float(probability(scene, outcome_ids))
    if scene["equally_likely"]:
        return f"{len(set(outcome_ids))}/{len(scene['outcomes'])} = {value:.2f}"
    return f"{value:.2f}"


def render_formula(scene, state):
    st.markdown("#### " + tr("Formula / Reasoning Lens"))
    focus = semantic_focus(scene, state)
    if focus["selected_outcome_id"]:
        outcome = next(
            item for item in scene["outcomes"] if item["id"] == focus["selected_outcome_id"]
        )
        for event in scene["events"]:
            symbol = "∈" if outcome["id"] in scene["event_sets"][event["id"]] else "∉"
            st.write(f"{outcome['label']} {symbol} {event['label']}")
    else:
        st.write(f"P({focus['display_label']}) = {probability_decomposition(scene, focus['outcome_ids'])}")
        st.metric(f"P({focus['display_label']})", f"{float(probability(scene, focus['outcome_ids'])):.2f}")
    source_caption(focus["source_pages"], lambda pages: ", ".join(f"p. {page}" for page in pages))


def _outcome_labels(scene, outcome_ids):
    labels = {outcome["id"]: outcome["label"] for outcome in scene["outcomes"]}
    return ", ".join(labels[identifier] for identifier in labels if identifier in outcome_ids) or "∅"


def inclusion_exclusion_lines(scene, left, right):
    data = inclusion_exclusion(scene, left["id"], right["id"])
    left_label, right_label = left["label"], right["label"]
    return [
        f"P({left_label}) = {probability_decomposition(scene, scene['event_sets'][left['id']])}",
        f"P({right_label}) = {probability_decomposition(scene, scene['event_sets'][right['id']])}",
        f"P({left_label} ∩ {right_label}) = {probability_decomposition(scene, scene['event_sets'][left['id']] & scene['event_sets'][right['id']])}",
        f"P({left_label} ∪ {right_label})",
        f"= P({left_label}) + P({right_label}) − P({left_label} ∩ {right_label})",
        f"= {float(data['left']):.2f} + {float(data['right']):.2f} − {float(data['intersection']):.2f}",
        f"= {float(data['union']):.2f}",
    ]


def render_special_lens(scene, state):
    left, right = _event_pair(scene)
    if not left or not right:
        st.info(tr("This lens needs two events."))
        return
    if state["lens"] == "de_morgan":
        st.markdown("#### " + tr("De Morgan Lens"))
        result = de_morgan(scene, left["id"], right["id"])
        rows = [
            (f"({left['label']} ∪ {right['label']})ᶜ", f"{left['label']}ᶜ ∩ {right['label']}ᶜ", result["union_complement"]),
            (f"({left['label']} ∩ {right['label']})ᶜ", f"{left['label']}ᶜ ∪ {right['label']}ᶜ", result["intersection_complement"]),
        ]
        for left_formula, right_formula, (left_set, right_set, equal) in rows:
            columns = st.columns(2)
            columns[0].markdown(f"**{left_formula}**  \n{_outcome_labels(scene, left_set)}")
            columns[1].markdown(f"**{right_formula}**  \n{_outcome_labels(scene, right_set)}")
            st.success(tr("Computed sets are identical.")) if equal else st.error(tr("Computed sets differ."))
    elif state["lens"] == "inclusion_exclusion":
        st.markdown("#### " + tr("Inclusion–Exclusion Lens"))
        for line in inclusion_exclusion_lines(scene, left, right):
            st.write(line)
        st.caption(tr("The overlap is subtracted once because it was counted in both events."))


def render_monte_carlo(scene, state):
    st.markdown("#### " + tr("Monte Carlo Simulation"))
    focus = semantic_focus(scene, state)
    st.caption(f"P({focus['display_label']})")
    samples = st.select_slider(
        tr("Trials"), options=list(MONTE_CARLO_COUNTS),
        value=state.get("monte_carlo_samples", 1_000),
        key=f"scene-widget-samples-{state['material_id']}",
    )
    state["monte_carlo_samples"] = samples
    if st.button(tr("Run again"), key=f"scene-widget-rerun-{state['material_id']}"):
        state["monte_carlo_seed"] = int(state.get("monte_carlo_seed", 17)) + 1
    result = monte_carlo(
        scene, focus["outcome_ids"], samples, state.get("monte_carlo_seed", 17)
    )
    columns = st.columns(3)
    columns[0].metric(tr("Theoretical"), f"{result['theoretical']:.4f}")
    columns[1].metric(tr("Empirical"), f"{result['empirical']:.4f}")
    columns[2].metric(tr("Difference"), f"{result['difference']:.4f}")
    x, y = zip(*result["checkpoints"])
    figure = go.Figure(go.Scatter(x=x, y=y, mode="lines", name=tr("Empirical")))
    figure.add_hline(y=result["theoretical"], line_dash="dash", annotation_text=tr("Theoretical"))
    figure.update_layout(
        height=230, margin=dict(l=8, r=8, t=12, b=8),
        xaxis_title=tr("Trials"), yaxis_range=[0, 1],
        meta={"focus_outcome_ids": sorted(focus["outcome_ids"]), "target": focus["display_label"]},
    )
    st.plotly_chart(
        figure, use_container_width=True,
        key=f"scene-monte-{state['material_id']}-{state['monte_carlo_seed']}",
    )
