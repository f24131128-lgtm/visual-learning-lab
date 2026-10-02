"""Strict data declarations; expressions never become browser code."""

VERSION = "2.2"
DOMAIN = "spatial_dynamics"
OPTIONAL_CAPABILITIES = ("inverse_bindings", "invariants", "experiments")
MAX_OBJECTS = 12
MAX_VECTORS = 8
MAX_SERIES = 6
MAX_QUANTITIES = 24
MAX_FRAMES = 180
MAX_BINDINGS = 32
MAX_INVERSE_BINDINGS = 4
MAX_INVARIANTS = 12
MAX_INVARIANT_SAMPLES = 64
MAX_EXPERIMENTS = 4
MAX_EXPERIMENT_STEPS = 8
MAX_RECORDING_STEPS = 80
MAX_PAYLOAD_BYTES = 2 * 1024 * 1024


def obj(properties):
    return {"type": "object", "properties": properties,
            "required": list(properties), "additionalProperties": False}


def arr(items, limit, minimum=0):
    return {"type": "array", "items": items, "minItems": minimum, "maxItems": limit}


TEXT = {"type": "string"}
NUMBER = {"type": "number"}
NULL_TEXT = {"type": ["string", "null"]}
PAGES = arr({"type": "integer", "minimum": 1}, 8)
PATCH_SCHEMA = obj({
    "op": {"type": "string", "enum": ["set_parameter", "set_time", "set_focus", "restore_baseline"]},
    "target_id": dict(TEXT, description="set_focus: a canonical quantity ID, not an object/series/metric ID. set_parameter: exact parameter ID. set_time: time. restore_baseline: empty string."), "value": {"type": ["number", "null"]},
})
WORLD_SCHEMA = obj({
    "scene_version": {"type": "string", "enum": [VERSION]},
    "domain": {"type": "string", "enum": [DOMAIN]},
    "scene_id": TEXT, "title": TEXT, "learning_goal": TEXT,
    "assumptions": arr(TEXT, 4), "source_pages": PAGES,
    "time": obj({"min": NUMBER, "max": NUMBER, "frames": {"type": "integer", "minimum": 20, "maximum": MAX_FRAMES}, "unit": TEXT,
                 "strategy": {"type": "string", "enum": ["fixed_duration", "derived_duration", "periodic_duration"]},
                 "duration_expression": dict(NULL_TEXT, description="Parameter-only safe expression. Derived: complete event duration. Periodic: one period; multiplied by periods. Fixed: null."),
                 "periods": {"type": "integer", "minimum": 1, "maximum": 8}}),
    "axes": obj({"x_min": NUMBER, "x_max": NUMBER, "y_min": NUMBER, "y_max": NUMBER, "x_label": TEXT, "y_label": TEXT}),
    "parameters": arr(obj({"id": TEXT, "label": TEXT, "unit": TEXT, "min": NUMBER, "max": NUMBER, "default": NUMBER, "step": NUMBER, "source_pages": PAGES,
                           "quantity_kind": {"type": "string", "enum": ["scalar", "length", "speed", "acceleration", "frequency", "angle", "inclination_angle"]},
                           "range_source": {"type": "string", "enum": ["source", "pedagogical", "semantic_default"]},
                           "display_unit": {"type": "string", "enum": ["native", "degrees"]}}), 4, 1),
    "quantities": arr(obj({"id": TEXT, "label": TEXT, "unit": TEXT, "expression": dict(TEXT, description="Safe arithmetic using declared parameter/quantity IDs and the canonical variable time. Never use an undeclared t or Unicode symbol."), "source_pages": PAGES}), MAX_QUANTITIES, 1),
    "objects": arr(obj({"id": TEXT, "label": TEXT, "type": {"type": "string", "enum": ["point", "vector", "trajectory", "axis"]}, "semantic_id": TEXT, "origin": arr(NUMBER, 2, 2), "origin_quantity_ids": arr(TEXT, 2), "source_pages": PAGES}), MAX_OBJECTS, 1),
    "series": arr(obj({"id": TEXT, "label": TEXT, "semantic_id": TEXT, "source_pages": PAGES}), MAX_SERIES, 1),
    "metrics": arr(obj({"id": TEXT, "label": TEXT, "semantic_id": TEXT, "unit": TEXT, "source_pages": PAGES}), 8, 1),
    "bindings": arr(obj({"id": TEXT, "type": {"type": "string", "enum": ["point_position", "vector_components", "curve_value", "metric_value"]}, "target_id": TEXT, "quantity_ids": arr(TEXT, 2, 1)}), MAX_BINDINGS, 1),
    "inverse_bindings": arr(obj({"id": TEXT, "type": {"type": "string", "enum": ["angle_to_time", "angle_to_parameter", "nearest_path_time"]}, "object_id": TEXT, "target_id": TEXT, "rate_expression": dict(NULL_TEXT, description="Parameter IDs and constants ONLY, not time or derived quantity IDs. Inline a derived rate's arithmetic, or omit the optional inverse."), "offset_expression": dict(NULL_TEXT, description="Parameter IDs and constants ONLY; never a derived quantity ID."), "scale": NUMBER}), MAX_INVERSE_BINDINGS),
    "invariants": arr(obj({"id": TEXT, "label": TEXT, "type": {"type": "string", "enum": ["approx_equal", "bounded", "constant_over_time", "vector_relation", "phase_difference", "sum_relation"]}, "left_expression": TEXT, "right_expression": TEXT, "lower": NUMBER, "upper": NUMBER, "tolerance": NUMBER, "samples": {"type": "integer", "minimum": 3, "maximum": MAX_INVARIANT_SAMPLES}}), MAX_INVARIANTS),
    "experiments": arr(obj({"id": TEXT, "title": TEXT, "learning_goal": TEXT, "steps": arr(PATCH_SCHEMA, MAX_EXPERIMENT_STEPS, 1), "observation_targets": arr(TEXT, 8, 1), "source_pages": PAGES}), MAX_EXPERIMENTS),
})

INSTRUCTIONS = """Compile the source into a generic spatial_dynamics Learning World 2.2.
Return only strict declarative data. Do not emit code, HTML, JavaScript, URLs or renderer instructions.
Only compile a source-supported quantitative physical system. Parameters have finite, meaningful legal ranges.
Use canonical time (seconds unless source says otherwise), <=4 parameters, <=24 derived scalar quantities.
The expression variable is exactly time, NOT t. A source formula using t must be written with time.
Expressions use only declared ASCII IDs, never source notation such as ω or implicit multiplication.
All IDs are globally unique across every group; time is reserved and is not a declared parameter.
Quantity expressions may depend on time, parameters and other quantities in an acyclic graph.
Reuse the SAME canonical quantities through forward bindings for spatial points/vectors/trajectories,
waveforms and live state metrics. Do not duplicate unrelated formulas across representations.
Safe arithmetic only: + - * / **, unary signs, pi, e, sin/cos/tan/exp/log/sqrt/abs(one argument).
Angles are radians internally; use display_unit degrees for natural educational angular controls.
Parameter range priority: source explicit valid range (range_source source), then useful source-supported
pedagogical ranges (pedagogical), then semantic_default derived locally from quantity_kind and baseline.
Do not invent a source range. Scalar/length/speed/acceleration/frequency/angle/inclination_angle are safe
quantity kinds, not renderer modes. Inclination means a strictly positive angle below pi/2.
For an ideal same-height flight, useful pedagogical ranges can be speed 5..100 m/s,
inclination 5..85 degrees (store radians), gravity 1..20 m/s², if consistent with the source model.
Stable ASCII ids; concise human labels.
Vector origin is fixed data or origin_quantity_ids [x,y] from canonical quantities;
vector_components bind dx/dy quantities; point_position binds x/y. Empty origin_quantity_ids uses fixed origin.
axis uses vector_components as a bidirectional reference axis, not an animated arrow.
trajectory is a sampled point_position over canonical time. curve_value and metric_value each bind one quantity.
All objects, series and metrics have semantic_id referring to a canonical quantity for selection/linking.
Objects <=12, vectors <=8, series <=6, frames 20..180, bindings <=32, inverse bindings <=4.
Every object, curve and metric has exactly one forward binding. For a curve/metric, semantic_id
must equal its one bound quantity_id. A focus target is always a quantity ID, never an object ID.
Axes are finite bounded hints, not a reason to shrink useful parameter ranges. The validator derives
safe viewport bounds from legal parameters and semantic time, including origins and both axis endpoints.
Declare meaningful time: fixed_duration uses min/max and null duration_expression; derived_duration
uses a PARAMETER-ONLY safe positive duration_expression, e.g. 2*speed*sin(angle)/gravity for complete
same-height flight; periodic_duration uses a one-period expression (e.g. 2*pi/omega) and periods 1..8.
Always supply periods (1 for non-periodic) and a valid finite min/max hint. Derived time ends at
min + duration, periodic at min + periods*period. No time/quantity references in duration_expression.
Event trajectories must stop at their physical endpoint, not while airborne or after impact.
Use a short time window resolving the fastest declared oscillation with the bounded frame count,
normally no more than three periods at maximum frequency. Do not invent unsupported controls.
inverse_bindings, invariants and experiments are OPTIONAL capabilities: return [] when unsupported
or uncertain. They must not be fabricated to fill a minimum count. All base views remain usable without them.
Inverse mapping whitelist only: angle_to_time (vector angle=rate(parameters)*time+offset(parameters)),
angle_to_parameter (vector angle=scale*parameter+offset(parameters); parameter range <=one turn),
nearest_path_time (trajectory selection maps to nearest sampled time). Never emit arbitrary inverse code.
Only declare an inverse when its exact formula agrees with the forward vector at all legal states.
Inverse rate_expression/offset_expression may reference ONLY parameter IDs, constants and safe functions;
NOT time or derived quantities. Inline derived arithmetic (e.g. 2*pi*frequency rather than omega).
Use null for unused rate/offset,
target_id time or an exact parameter id. Do not invent inverse mappings.
Declare source-supported numeric invariants: approx_equal/vector_relation compare expressions;
sum_relation compares a sum to its right expression; bounded checks lower<=left<=upper;
constant_over_time checks left stays constant at each parameter state; phase_difference checks
wrapped angular difference(left-right) equals lower radians. Tolerance 1e-10..1e-4, samples 3..64.
For balanced three-phase cosines, declare current-sum zero, 120 degree phase separation,
and constant resultant magnitude ONLY if your exact component model implies it.
Keep projectile time interval and parameter ranges physically valid (no below-ground flight); express
position, velocity and graphs with this same generic model. Do not insert a motor/projectile renderer.
Experiments <=4 with <=8 whitelisted steps: set_parameter/set_time numeric values; set_focus exact
quantity id and value null; restore_baseline target_id empty, value null. Observation targets exact quantities.
No fabricated physics. List simplifications as assumptions. Source pages only supplied allowed pages,
smallest direct support per item, [] when unclear or pasted text. Never claim assumptions as source evidence.
If a reliable finite numeric model cannot be grounded, do not invent one; the app will safely reject it.
"""
