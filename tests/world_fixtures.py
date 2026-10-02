"""Two deterministic acceptance systems, never imported by production routing."""

from scene.world.schema import VERSION

try:
    from support import fixture
except ModuleNotFoundError:
    from .support import fixture


def base(title, parameters, quantities):
    def param(identifier, label, unit, low, high, default, step):
        return dict(id=identifier, label=label, unit=unit, min=low, max=high, default=default, step=step, source_pages=[1], quantity_kind="scalar", range_source="pedagogical", display_unit="native")
    return {"scene_version": VERSION, "domain": "spatial_dynamics", "scene_id": "world_scene", "title": title,
            "learning_goal": "Explore one physical state through multiple views.", "assumptions": ["Ideal planar model; no losses."], "source_pages": [1],
            "time": {"min": 0., "max": .05, "frames": 120, "unit": "s", "strategy": "fixed_duration", "duration_expression": None, "periods": 1},
            "axes": dict(x_min=-4., x_max=4., y_min=-4., y_max=4., x_label="x", y_label="y"),
            "parameters": [param(*p) for p in parameters],
            "quantities": [dict(id=i, label=l, unit=u, expression=e, source_pages=[1]) for i, l, u, e in quantities],
            "objects": [], "series": [], "metrics": [], "bindings": [], "inverse_bindings": [], "invariants": [], "experiments": []}


def representation(scene, group, identifier, label, semantic, refs, kind=None, origin_refs=()):
    item = dict(id=identifier, label=label, semantic_id=semantic, source_pages=[1])
    if group == "objects": item.update(type=kind, origin=[0., 0.], origin_quantity_ids=list(origin_refs))
    if group == "metrics": item["unit"] = next(q["unit"] for q in scene["quantities"] if q["id"] == semantic)
    scene[group].append(item)
    btype = "vector_components" if kind in ("vector", "axis") else "point_position" if group == "objects" else "curve_value" if group == "series" else "metric_value"
    scene["bindings"].append(dict(id="bind_"+identifier, type=btype, target_id=identifier, quantity_ids=refs))


def invariant(identifier, label, left, right="0", kind="approx_equal", low=0., high=0.):
    return dict(id=identifier, label=label, type=kind, left_expression=left, right_expression=right, lower=low, upper=high, tolerance=1e-7, samples=48)


def three_phase_world():
    scene = base("Three-phase rotating field", [("amplitude", "Amplitude", "A", .5, 2., 1., .1), ("frequency", "Frequency", "Hz", 40., 60., 50., 1.)], [
        ("theta", "Electrical angle", "rad", "2*pi*frequency*time"),
        ("theta_b", "Phase B angle", "rad", "theta-2*pi/3"), ("theta_c", "Phase C angle", "rad", "theta-4*pi/3"),
        ("ia", "Phase A current", "A", "amplitude*cos(theta)"), ("ib", "Phase B current", "A", "amplitude*cos(theta_b)"), ("ic", "Phase C current", "A", "amplitude*cos(theta_c)"),
        ("ax", "Phase A horizontal", "A", "ia"), ("ay", "Phase A vertical", "A", "0"),
        ("bx", "Phase B horizontal", "A", "ib*cos(2*pi/3)"), ("by", "Phase B vertical", "A", "ib*sin(2*pi/3)"),
        ("cx", "Phase C horizontal", "A", "ic*cos(4*pi/3)"), ("cy", "Phase C vertical", "A", "ic*sin(4*pi/3)"),
        ("rx", "Resultant horizontal", "A", "ax+bx+cx"), ("ry", "Resultant vertical", "A", "ay+by+cy"),
        ("magnitude", "Resultant magnitude", "A", "sqrt(rx**2+ry**2)"), ("period", "Period", "s", "1/frequency"),
        ("axis_ax", "Phase A axis horizontal", "", "2.5"), ("axis_ay", "Phase A axis vertical", "", "0"),
        ("axis_bx", "Phase B axis horizontal", "", "2.5*cos(2*pi/3)"), ("axis_by", "Phase B axis vertical", "", "2.5*sin(2*pi/3)"),
        ("axis_cx", "Phase C axis horizontal", "", "2.5*cos(4*pi/3)"), ("axis_cy", "Phase C axis vertical", "", "2.5*sin(4*pi/3)"),
    ])
    for phase in ("a", "b", "c"):
        representation(scene, "objects", "axis_"+phase, "Phase "+phase.upper()+" axis", "i"+phase, ["axis_"+phase+"x", "axis_"+phase+"y"], "axis")
        representation(scene, "objects", "vector_"+phase, "Phase "+phase.upper(), "i"+phase, [phase+"x", phase+"y"], "vector")
        representation(scene, "series", "wave_"+phase, "Phase "+phase.upper(), "i"+phase, ["i"+phase])
        representation(scene, "metrics", "metric_"+phase, "Phase "+phase.upper()+" current", "i"+phase, ["i"+phase])
    representation(scene, "objects", "resultant", "Resultant field", "magnitude", ["rx", "ry"], "vector")
    for identifier in ("magnitude", "period", "theta"):
        representation(scene, "metrics", "metric_"+identifier, next(q["label"] for q in scene["quantities"] if q["id"] == identifier), identifier, [identifier])
    scene["inverse_bindings"] = [dict(id="rotate_resultant", type="angle_to_time", object_id="resultant", target_id="time", rate_expression="2*pi*frequency", offset_expression="0", scale=1.)]
    scene["invariants"] = [
        invariant("sum_currents", "Balanced current sum", "ia+ib+ic", kind="sum_relation"),
        invariant("phase_ab", "120 degree phase separation", "theta", "theta_b", "phase_difference", 2*3.141592653589793/3, 2*3.141592653589793/3),
        invariant("phase_bc", "120 degree phase separation", "theta_b", "theta_c", "phase_difference", 2*3.141592653589793/3, 2*3.141592653589793/3),
        invariant("constant_resultant", "Constant field magnitude", "magnitude", kind="constant_over_time"),
        invariant("correct_magnitude", "Resultant equals 1.5 times amplitude", "magnitude", "1.5*amplitude"),
        invariant("vector_sum_x", "Horizontal vector sum", "rx", "ax+bx+cx", "vector_relation"),
        invariant("vector_sum_y", "Vertical vector sum", "ry", "ay+by+cy", "vector_relation"),
    ]
    scene["experiments"] = [dict(id="higher_frequency", title="Increase frequency", learning_goal="Compare period and field rotation.",
        steps=[dict(op="set_parameter", target_id="frequency", value=60.), dict(op="set_focus", target_id="period", value=None)], observation_targets=["period", "theta"], source_pages=[1])]
    return scene


def projectile_world():
    scene = base("Projectile motion", [("speed", "Launch speed", "m/s", 15., 20., 18., .5), ("angle", "Launch angle", "rad", .7, 1.1, .9, .05)], [
        ("px", "Horizontal position", "m", "speed*cos(angle)*time"), ("py", "Vertical position", "m", "speed*sin(angle)*time-4.905*time**2"),
        ("vx", "Horizontal velocity", "m/s", "speed*cos(angle)"), ("vy", "Vertical velocity", "m/s", "speed*sin(angle)-9.81*time"),
        ("launch_y", "Launch vertical velocity", "m/s", "speed*sin(angle)"), ("gravity", "Gravity", "m/s²", "-9.81"), ("zero", "Zero", "", "0"),
        ("energy", "Specific mechanical energy", "m²/s²", "(vx**2+vy**2)/2+9.81*py"),
    ])
    scene["time"]["max"] = 1.8
    scene["axes"].update(x_min=-2., x_max=44., y_min=-12., y_max=35.)
    representation(scene, "objects", "body", "Moving body", "px", ["px", "py"], "point")
    representation(scene, "objects", "path", "Flight trajectory", "px", ["px", "py"], "trajectory")
    representation(scene, "objects", "velocity", "Velocity vector", "vx", ["vx", "vy"], "vector", ["px", "py"])
    representation(scene, "objects", "launch", "Launch direction", "launch_y", ["vx", "launch_y"], "vector")
    representation(scene, "objects", "acceleration", "Gravity vector", "gravity", ["zero", "gravity"], "vector", ["px", "py"])
    for q in ("px", "py", "vx", "vy", "energy"):
        label = next(qty["label"] for qty in scene["quantities"] if qty["id"] == q)
        representation(scene, "metrics", "metric_"+q, label, q, [q])
    for q in ("px", "py"):
        representation(scene, "series", "curve_"+q, next(qty["label"] for qty in scene["quantities"] if qty["id"] == q), q, [q])
    scene["inverse_bindings"] = [dict(id="path_time", type="nearest_path_time", object_id="path", target_id="time", rate_expression=None, offset_expression=None, scale=1.),
        dict(id="launch_angle", type="angle_to_parameter", object_id="launch", target_id="angle", rate_expression=None, offset_expression="0", scale=1.)]
    scene["invariants"] = [invariant("conserve_energy", "Constant ideal mechanical energy", "energy", kind="constant_over_time"),
        invariant("above_ground", "Above ground flight interval", "py", kind="bounded", low=0., high=20.)]
    return scene


def spatial_analysis():
    analysis = fixture()
    analysis.update(analysis_language="en", quick_summary="Three-phase time-dependent currents create a rotating vector field. Frequency and amplitude set the waveforms.",
                    learning_scene_candidate=dict(suitable=True, domain="spatial_dynamics", reason="Quantitative rotating field model."))
    return analysis


def complete_projectile_world():
    """Same renderer; source-supported derived event and meaningful ranges."""
    import math
    scene = projectile_world()
    scene["parameters"][0].update(min=5., max=100., default=20., step=.5, quantity_kind="speed")
    scene["parameters"][1].update(min=math.radians(5), max=math.radians(85), default=math.pi/4,
                                   step=math.radians(.5), quantity_kind="inclination_angle", display_unit="degrees")
    scene["parameters"].append(dict(id="grav", label="Gravity", unit="m/s²", min=1., max=20., default=9.8,
                                     step=.1, source_pages=[1], quantity_kind="acceleration", range_source="pedagogical", display_unit="native"))
    expressions = dict(py="speed*sin(angle)*time-0.5*grav*time**2", vy="speed*sin(angle)-grav*time",
                       gravity="-grav", energy="(vx**2+vy**2)/2+grav*py")
    for q in scene["quantities"]:
        if q["id"] in expressions: q["expression"] = expressions[q["id"]]
    scene["time"].update(strategy="derived_duration", duration_expression="2*speed*sin(angle)/grav", max=4.)
    scene["axes"].update(x_min=-1., x_max=10., y_min=-1., y_max=10.)  # Deliberately undersized live-style hint.
    scene["invariants"][1].update(upper=10_000.)
    return scene


def circular_world():
    """A third domain reuses existing primitives; no circular renderer branch."""
    scene = base("Uniform circular motion", [("radius", "Radius", "m", 1., 10., 2., .1),
                 ("omega", "Angular frequency", "rad/s", 1., 5., 2., .1)], [
        ("cx", "Horizontal position", "m", "radius*cos(omega*time)"),
        ("cy", "Vertical position", "m", "radius*sin(omega*time)"),
        ("hx", "Horizontal axis extent", "m", "radius"), ("hy", "Axis zero", "m", "0")])
    scene["time"].update(strategy="periodic_duration", duration_expression="2*pi/omega", periods=2, max=7.)
    scene["axes"].update(x_min=-2., x_max=2., y_min=-2., y_max=2.)
    representation(scene, "objects", "horizontal_axis", "Horizontal reference", "hx", ["hx", "hy"], "axis")
    representation(scene, "objects", "orbit", "Orbit", "cx", ["cx", "cy"], "trajectory")
    representation(scene, "objects", "position", "Position", "cx", ["cx", "cy"], "point")
    representation(scene, "objects", "radius_vector", "Radius vector", "cx", ["cx", "cy"], "vector")
    representation(scene, "series", "position_curve", "Horizontal position", "cx", ["cx"])
    representation(scene, "metrics", "position_metric", "Horizontal position", "cx", ["cx"])
    return scene
