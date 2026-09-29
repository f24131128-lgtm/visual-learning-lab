"""Bounded local numeric trajectories and one browser-side Plotly frame clock."""

import html
import json
from functools import lru_cache

import numpy as np

from i18n import FONT_STACK, tr
from interactive_lab import _finite
from safe_math import MathExpressionError, evaluate_expression
from simulation_spec import MOVING_TYPES, TIME_SYMBOL

MAX_TRAIL_POINTS = 80
MAX_TRACES = 32
MAX_FIGURE_BYTES = 6 * 1024 * 1024
MAX_FRAME_CACHE_ENTRIES = 6
MAX_FRAME_CACHE_BYTES = 4 * 1024 * 1024
COLORS = ("#6750C5", "#087E8B", "#B85B17", "#BE4773")


def _vector(expression, values, times):
    value = evaluate_expression(expression, {**values, TIME_SYMBOL: times})
    array = np.full(times.shape, value, dtype=float) if np.isscalar(value) else value
    if array.shape != times.shape or not np.all(np.isfinite(array)) or np.any(np.abs(array) > 1e9):
        raise MathExpressionError("Invalid coordinates or metric values.")
    return array


def _time_samples(spec, values):
    clock = spec["time"]
    end = clock["max"]
    if clock["max_expression"] is not None:
        end = _finite(evaluate_expression(clock["max_expression"], values))
    if not clock["min"] < end <= clock["max"]:
        raise MathExpressionError("End time is outside its safe bounds.")
    times = np.linspace(clock["min"], end, clock["frames"])
    stop = spec["stop_when"]
    if stop is None:
        return times, False
    sign = 1 if stop["comparison"] == "below" else -1
    distances = sign * (_vector(stop["expression"], values, times) - stop["threshold"])
    if distances[0] < 0:
        raise MathExpressionError("Initial state is outside the declared boundary.")
    crossings = np.flatnonzero(distances[1:] < 0)
    if not crossings.size:
        return times, False
    index = int(crossings[0]) + 1
    low, high = float(times[index - 1]), float(times[index])
    # Numeric bisection of ONE whitelisted expression, never boolean code. Keep
    # the final sample on the valid side so a trajectory does not pass its boundary.
    for _ in range(40):
        middle = (low + high) / 2
        distance = sign * (evaluate_expression(stop["expression"], {**values, TIME_SYMBOL: middle}) - stop["threshold"])
        if distance >= 0:
            low = middle
        else:
            high = middle
    if low <= clock["min"]:
        raise MathExpressionError("No valid motion interval remains.")
    return np.linspace(clock["min"], low, clock["frames"]), True


def compute_scene(spec, demo, values):
    """Evaluate vectors once, independently dropping unusable auxiliary objects."""
    if set(values) != set(spec["parameter_ids"]):
        raise MathExpressionError("Parameters no longer match the simulation.")
    for parameter in demo["parameters"]:
        value = _finite(values[parameter["id"]])
        if not parameter["min"] <= value <= parameter["max"]:
            raise MathExpressionError("Parameter outside the lab range.")
    times, stopped = _time_samples(spec, values)
    data = {"time": times, "objects": {}, "static_series": {}, "metrics": {}, "omitted": [], "stopped": stopped}
    curves = {series["id"]: series for series in demo["series"]}

    def coords(item, endpoint=""):
        return {axis: _vector(item[f"{axis}{endpoint}_expression"], values, times)
                for axis in "xyz" if item.get(f"{axis}{endpoint}_expression") is not None}

    for obj in spec["objects"]:
        kind = obj["type"]
        try:
            if kind in ("vector", "line_segment"):
                entry = {"start": coords(obj, "0"), "end": coords(obj, "1")}
            elif kind == "moving_marker_on_curve" and obj["curve_id"] is not None:
                x = _vector(obj["x_expression"], values, times)
                if np.min(x) < demo["x"]["min"] or np.max(x) > demo["x"]["max"]:
                    raise MathExpressionError("Curve marker is outside the lab domain.")
                value = evaluate_expression(curves[obj["curve_id"]]["expression"], {**values, demo["x"]["id"]: x})
                y = np.full_like(x, value) if np.isscalar(value) else value
                if y.shape != times.shape or np.any(np.abs(y) > 1e9):
                    raise MathExpressionError("Invalid linked curve.")
                entry = {"position": {"x": x, "y": y}}
            elif kind in MOVING_TYPES:
                entry = {"position": coords(obj)}
            elif kind == "reference_line":
                entry = {"value": _finite(evaluate_expression(obj["value_expression"], values))}
            elif kind == "circle":
                entry = {key: _finite(evaluate_expression(obj[f"{key}_expression"], values)) for key in ("x", "y", "radius")}
                if entry["radius"] <= 0:
                    raise MathExpressionError("Circle radius must be positive.")
            else:
                continue  # Trails only reference successfully evaluated moving objects.
            data["objects"][obj["id"]] = entry
        except (ValueError, KeyError, TypeError, OverflowError):
            data["omitted"].append(obj["id"])
    for field in ("static_series", "metrics"):
        for item in spec[field]:
            try:
                data[field][item["id"]] = coords(item) if field == "static_series" else _vector(item["expression"], values, times)
            except (ValueError, KeyError, TypeError, OverflowError):
                data["omitted"].append(item["id"])
    if not any(obj["type"] in MOVING_TYPES and obj["id"] in data["objects"] for obj in spec["objects"]):
        raise MathExpressionError("No valid moving object remains.")
    return data


def has_motion(spec, data):
    return any(np.any(np.diff(array) != 0)
               for obj in spec["objects"] if obj["type"] in MOVING_TYPES and obj["id"] in data["objects"]
               for group in ("position", "start", "end")
               for array in data["objects"][obj["id"]].get(group, {}).values())


def numeric_size(value):
    if isinstance(value, np.ndarray):
        return value.nbytes
    if isinstance(value, dict):
        return sum(numeric_size(item) for item in value.values())
    if isinstance(value, list):
        return sum(numeric_size(item) for item in value)
    return 0


def cached_scene(state, spec, demo, values, fingerprint):
    key = (state["material_id"], demo["id"], fingerprint, tuple(sorted(values.items())))
    cache = state["frames"]
    if key in cache:
        result = cache.pop(key)
        cache[key] = result
        return result
    result = compute_scene(spec, demo, values)
    size = numeric_size(result)
    while cache and (len(cache) >= MAX_FRAME_CACHE_ENTRIES
                     or sum(numeric_size(item) for item in cache.values()) + size > MAX_FRAME_CACHE_BYTES):
        cache.pop(next(iter(cache)))
    if size <= MAX_FRAME_CACHE_BYTES:
        cache[key] = result
    return result


def build_simulation_figure(spec, data, show_trail=True, full_path=True, static=False, projection=False):
    """Fixed trace identities, fixed axes, metrics outside axes, and ONE frame list."""
    import plotly.graph_objects as go

    figure = go.Figure()
    dynamic = []
    scene_3d = spec["scene"]["dimension"] == "3d" and not projection
    colors = {obj["id"]: COLORS[i % len(COLORS)] for i, obj in enumerate(spec["objects"])}

    def trace(coordinates, panel, label, color, mode="lines", opacity=1, vector=False):
        is_3d = scene_3d and panel == "scene"
        coords = {axis: np.asarray(coordinates[axis]).tolist() for axis in ("xyz" if is_3d else "xy")}
        common = {**coords, "name": html.escape(label), "mode": mode, "opacity": opacity,
                  "line": {"color": color, "width": 3}, "marker": {"color": color, "size": 10},
                  "showlegend": False}
        if is_3d:
            return go.Scatter3d(**common, scene="scene")
        if vector:
            common["marker"].update(symbol=["circle", "arrow"], size=[5, 13], angleref="previous")
        return go.Scatter(**common, xaxis="x2" if panel == "graph" else "x", yaxis="y2" if panel == "graph" else "y")

    def add_dynamic(builder):
        index = len(figure.data)
        figure.add_trace(builder(0))
        dynamic.append((index, builder))

    for obj in spec["objects"]:
        kind, object_id, panel = obj["type"], obj["id"], obj["panel"]
        color = colors[object_id]
        entry = data["objects"].get(object_id)
        if kind == "trail":
            target = data["objects"].get(obj["object_id"])
            if not target or not show_trail or static:
                continue
            position = target.get("position", target.get("end"))
            def trail_at(i, pos=position, item=obj, ink=colors[obj["object_id"]]):
                indices = np.linspace(0, i, min(i + 1, MAX_TRAIL_POINTS), dtype=int)
                return trace({axis: values[indices] for axis, values in pos.items()}, item["panel"], item["label"], ink)
            add_dynamic(trail_at)
            continue
        if entry is None:
            continue
        if kind in MOVING_TYPES:
            position = entry.get("position", entry.get("end"))
            # A linked function graph stays visible even when the reference path is off.
            if full_path or static or (kind == "moving_marker_on_curve" and obj["curve_id"] is not None):
                figure.add_trace(trace(position, panel, obj["label"], color, opacity=.3))
            if "position" in entry:
                def point_at(i, pos=position, item=obj, ink=color):
                    return trace({axis: [values[i]] for axis, values in pos.items()}, item["panel"], item["label"], ink, "markers")
                add_dynamic(point_at)
            else:
                def segment_at(i, ends=entry, item=obj, ink=color):
                    coords = {axis: [ends["start"][axis][i], ends["end"][axis][i]] for axis in ends["end"]}
                    return trace(coords, item["panel"], item["label"], ink, "lines+markers", vector=item["type"] == "vector")
                add_dynamic(segment_at)
        elif kind == "reference_line":
            axes = spec["graph"] if panel == "graph" else spec["scene"]
            coords = {axis: [entry["value"], entry["value"]] if axis == obj["axis"] else [axes[f"{axis}_min"], axes[f"{axis}_max"]] for axis in "xy"}
            figure.add_trace(trace(coords, panel, obj["label"], "#A59BBB", opacity=.65))
        elif kind == "circle":
            angles = np.linspace(0, 2 * np.pi, 100)
            coords = {"x": entry["x"] + entry["radius"] * np.cos(angles), "y": entry["y"] + entry["radius"] * np.sin(angles)}
            figure.add_trace(trace(coords, panel, obj["label"], "#A59BBB", opacity=.6))
    for series in spec["static_series"]:
        coords = data["static_series"].get(series["id"])
        if coords is not None:
            figure.add_trace(trace(coords, series["panel"], series["label"], "#8F82AD", opacity=.5))
    if len(figure.data) > MAX_TRACES:
        raise ValueError("Too many plot traces.")
    split = spec["graph"] is not None
    main_domain = [0.46, 1] if split else [0, 1]
    axis_style = {"autorange": False, "gridcolor": "#EEEAF5", "zerolinecolor": "#B7ADCB", "automargin": True}
    if scene_3d:
        figure.update_layout(scene={**{f"{axis}axis": {"title": html.escape(spec["scene"][f"{axis}_label"]),
                                                       "range": [spec["scene"][f"{axis}_min"], spec["scene"][f"{axis}_max"]], "autorange": False} for axis in "xyz"},
                                    "domain": {"x": [0, 1], "y": main_domain}, "aspectmode": "data"})
    else:
        for axis in "xy":
            figure.update_layout(**{f"{axis}axis": {**axis_style, "title": html.escape(spec["scene"][f"{axis}_label"]),
                                                   "range": [spec["scene"][f"{axis}_min"], spec["scene"][f"{axis}_max"]],
                                                   "domain": main_domain if axis == "y" else [0, 1]}})
        # Equal coordinate units preserve physical geometry / vector angles.
        figure.update_layout(yaxis={"scaleanchor": "x", "scaleratio": 1, "constrain": "domain"})
    if split:
        for axis in "xy":
            figure.update_layout(**{f"{axis}axis2": {**axis_style, "title": html.escape(spec["graph"][f"{axis}_label"]),
                                                    "range": [spec["graph"][f"{axis}_min"], spec["graph"][f"{axis}_max"]],
                                                    "anchor": "y2" if axis == "x" else "x2",
                                                    "domain": [0, .31] if axis == "y" else [0, 1]}})

    metrics = [metric for metric in spec["metrics"] if metric["id"] in data["metrics"]]
    def metric_text(metric, i):
        value = data["metrics"][metric["id"]][i]
        # Display negligible roundoff as zero without changing numeric trajectories.
        return f"{0 if abs(value) < 1e-10 else value:.4g}"
    def annotations(i):
        result = [{"text": f"{html.escape(metric['label'])}<br><b>{metric_text(metric, i)} {html.escape(metric['unit'])}</b>",
                   "xref": "paper", "yref": "paper", "x": (j + .5) / max(1, len(metrics)), "y": 1.17,
                   "showarrow": False, "xanchor": "center", "font": {"size": 14}}
                  for j, metric in enumerate(metrics)]
        if not static:
            result.append({"text": tr("Playback speed"), "xref": "paper", "yref": "paper", "x": .68, "y": -.04,
                           "xanchor": "right", "showarrow": False, "font": {"size": 13}})
        return result

    figure.update_layout(template="plotly_white", height=800 if split else 680,
                         margin={"l": 46, "r": 20, "t": 100, "b": 230 if not static else 50},
                         font={"family": FONT_STACK, "size": 14, "color": "#30264D"},
                         annotations=annotations(0), uirevision=spec["title"], hovermode="closest")
    if not static:
        def animate_options(duration, resume=False):
            return {"mode": "immediate", "fromcurrent": resume, "transition": {"duration": 0},
                    "frame": {"duration": duration, "redraw": True}}
        play_args = [None, animate_options(75, True)]
        figure.frames = [go.Frame(name=str(i), traces=[index for index, _ in dynamic],
                                  data=[builder(i) for _, builder in dynamic], layout={"annotations": annotations(i)})
                         for i in range(len(data["time"]))]
        figure.update_layout(updatemenus=[
            {"type": "buttons", "direction": "left", "showactive": False, "x": 0, "y": -.04, "xanchor": "left",
             "buttons": [{"label": "▶ " + tr("Play"), "method": "animate", "args": play_args},
                         {"label": "⏸ " + tr("Pause"), "method": "animate", "args": [[None], animate_options(0)]},
                         {"label": "↺ " + tr("Reset"), "method": "animate", "args": [["0"], animate_options(0)]}]},
            {"type": "dropdown", "active": 1, "x": .7, "y": -.04, "xanchor": "left",
             "buttons": [{"label": f"{speed:g}×", "method": "relayout",
                          "args": [{"updatemenus[0].buttons[0].args": [None, animate_options(round(75 / speed), True)]}]}
                         for speed in (.5, 1, 2)]}],
            sliders=[{"active": 0, "x": 0, "len": 1, "y": -.21, "tickcolor": "#8270DF", "minorticklen": 0,
                      "currentvalue": {"prefix": tr("Current time") + ": ", "suffix": " " + spec["time"]["unit"], "font": {"size": 14}},
                      "steps": [{"method": "animate", "args": [[str(i)], animate_options(0)], "label": f"{time:.3g}"}
                                for i, time in enumerate(data["time"])]}])
    if len(figure.to_json().encode()) > MAX_FIGURE_BYTES:
        raise ValueError("Animation exceeds the payload budget.")
    return figure


@lru_cache(maxsize=1)
def _plotly_bundle():
    from plotly.offline import get_plotlyjs
    return get_plotlyjs()


def animation_html(figure, fallback, fallback_message):
    """Trusted fixed host, bundled JS (no CDN), and escaped numeric Plotly JSON.

    Using a component also carries frames on older supported Streamlit releases.
    Model expressions never enter script text: only precomputed arrays and labels.
    """
    payload = json.dumps({"figure": json.loads(figure.to_json()), "fallback": json.loads(fallback.to_json()),
                          "message": fallback_message}, ensure_ascii=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    body {{ margin:0; font-family:{FONT_STACK}; color:#30264D; background:white; }}
    #notice {{ font-size:14px; line-height:1.6; padding:8px; display:none; }}
    #scene {{ width:100%; }}
    </style></head><body><div id="notice" role="status"></div><div id="scene"></div>
    <script type="application/json" id="scene-data">{payload}</script>
    <script>{_plotly_bundle()}</script><script>
    (() => {{
      const payload = JSON.parse(document.getElementById('scene-data').textContent);
      const config = {{responsive:true, displaylogo:false, displayModeBar:false}};
      let failed = false;
      const fallback = () => {{
        if (failed) return;
        failed = true;
        const notice = document.getElementById('notice');
        notice.textContent = payload.message; notice.style.display = 'block';
        Plotly.purge('scene');
        Plotly.newPlot('scene', payload.fallback.data, payload.fallback.layout, config)
          .catch(() => {{ document.getElementById('scene').textContent = payload.message; }});
      }};
      // Plotly rejects interrupted animation queues with no reason when Pause,
      // replay or scrubbing cancels playback. This is expected, not a render error.
      window.addEventListener('unhandledrejection', event => {{
        if (event.reason == null) {{ event.preventDefault(); return; }}
        if (event.reason instanceof Error) fallback();
      }});
      Plotly.newPlot('scene', payload.figure.data, payload.figure.layout, config)
        .then(() => Plotly.addFrames('scene', payload.figure.frames)).catch(fallback);
    }})();
    </script></body></html>"""
