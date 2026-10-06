"""Small trusted adapter contract; no topic/source routing or generated code."""

POLICY_REVISION = "day23.phase_c.1"


def contracts(caps):
    """Model request hints distinguish an existing artifact from a build candidate."""
    return {
        "direct_manipulation": dict(available=True, advertised_by_model=False,
            requires=["validated_forward_binding", "proved_analytic_inverse", "canonical_semantic_id"],
            supports=["circular_parameter", "polar_endpoint", "affine_anchor"],
            negotiation="runtime_only", commit="canonical_reducer", model_code=False),
        "numeric_lab": dict(ready=bool(caps.get("lab")), time_required=False,
            supports=["continuous_parameter_comparison", "function_curves"],
            requires=["equations", "continuous_parameters"]),
        "spatial": dict(candidate=bool(caps.get("spatial")), explicit_build=True,
            supports=["planar_numeric_projection", "time_playback", "parameter_changes"]),
        "structural": dict(candidate=bool(caps.get("structural")), explicit_build=True,
            supports=["finite_membership", "set_operations", "local_sampling"]),
        "process": dict(available=True, requires_valid_declaration=True,
            supports=["bounded_ordered_collection", "finite_state_variable"],
            unsupported=["arbitrary_arithmetic_updates", "automatic_recursion", "timed_scheduling"]),
        "execution": dict(available=True, requires_valid_declaration=True,
            supports=["bounded_resolved_call_tree", "nested_call_return", "fixed_numeric_arguments", "safe_numeric_results"],
            maximum_calls=24, maximum_depth=8,
            unsupported=["arbitrary_program_execution", "unbounded_recursion", "conditional_code"]),
        "static": dict(ready=bool(caps.get("graph")), supports=["structured_diagram", "comparison"]),
        "analogy": dict(candidate=bool(caps.get("analogy")), explicit_build=True,
            supports=["source_supported_correspondence"]),
    }


def eligible(features, caps, process):
    families = []
    if features["transitions"] and process and (features["ordered_collection"] or process["states"]):
        families.append("process")
    if features["equations"] and (features["continuous_parameters"] or features["time_dynamics"]):
        if features["spatial_relations"] and caps.get("spatial"):
            families.append("spatial")
        # A numeric independent variable can be a coordinate, frequency or time.
        # Existing validated lab curves already implement all three locally.
        if caps.get("lab") or (features["time_dynamics"] and caps.get("spatial")):
            families.append("dynamic")
    if features["finite_outcomes"] and features["set_relations"] and caps.get("structural"):
        families.append("structural")
    if features["analogy_suitable"] and caps.get("analogy"):
        families.append("analogy")
    if features["structure"] and caps.get("graph"):
        families.append("static")
    return families
