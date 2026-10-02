"""Strict declarative schema for Learning Scene v1."""

SCENE_SCHEMA_VERSION = "1.1"
DOMAIN = "probability_sets"
VIEW_TYPES = ["sample_space", "set", "probability_tree", "formula", "monte_carlo"]
RELATION_TYPES = ["subset", "mutually_exclusive", "equivalent", "complement", "related"]

LEARNING_SCENE_CANDIDATE_SCHEMA = {
    "type": "object",
    "properties": {
        "suitable": {"type": "boolean"},
        "domain": {"type": "string", "enum": [DOMAIN, "spatial_dynamics", "none"]},
        "reason": {"type": "string"},
    },
    "required": ["suitable", "domain", "reason"],
    "additionalProperties": False,
}

SOURCE_PAGES = {"type": "array", "items": {"type": "integer", "minimum": 1}}

LEARNING_SCENE_SCHEMA = {
    "type": "object",
    "properties": {
        "scene_version": {"type": "string", "enum": [SCENE_SCHEMA_VERSION]},
        "scene_id": {"type": "string"},
        "title": {"type": "string"},
        "domain": {"type": "string", "enum": [DOMAIN]},
        "learning_goal": {"type": "string"},
        "source_pages": SOURCE_PAGES,
        "equally_likely": {"type": "boolean"},
        "outcomes": {
            "type": "array", "minItems": 1, "maxItems": 64,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "label": {"type": "string"},
                    "path": {"type": "array", "items": {"type": "string"}, "maxItems": 4},
                    "weight": {"type": "number", "exclusiveMinimum": 0},
                    "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "label", "path", "weight", "source_pages"],
                "additionalProperties": False,
            },
        },
        "events": {
            "type": "array", "minItems": 1, "maxItems": 12,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "label": {"type": "string"},
                    "outcome_ids": {"type": "array", "items": {"type": "string"}, "maxItems": 64},
                    "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "label", "outcome_ids", "source_pages"],
                "additionalProperties": False,
            },
        },
        "parameters": {
            "type": "array", "maxItems": 8,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "label": {"type": "string"},
                    "kind": {"type": "string", "enum": ["integer", "choice"]},
                    "default_value": {"type": "string"},
                    "allowed_values": {"type": "array", "items": {"type": "string"}, "maxItems": 12},
                    "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "label", "kind", "default_value", "allowed_values", "source_pages"],
                "additionalProperties": False,
            },
        },
        "states": {
            "type": "array", "maxItems": 12,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "label": {"type": "string"},
                    "kind": {"type": "string", "enum": ["focus", "selection", "event_expression"]},
                    "semantic_ids": {"type": "array", "items": {"type": "string"}, "maxItems": 12},
                },
                "required": ["id", "label", "kind", "semantic_ids"],
                "additionalProperties": False,
            },
        },
        "relations": {
            "type": "array", "maxItems": 24,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "type": {"type": "string", "enum": RELATION_TYPES},
                    "source_event_id": {"type": "string"}, "target_event_id": {"type": "string"},
                    "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "type", "source_event_id", "target_event_id", "source_pages"],
                "additionalProperties": False,
            },
        },
        "experiment": {
            "type": "object",
            "properties": {
                "staged": {"type": "boolean"},
                "stages": {
                    "type": "array", "maxItems": 4,
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"}, "label": {"type": "string"},
                            "branch_values": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 12},
                            "source_pages": SOURCE_PAGES,
                        },
                        "required": ["id", "label", "branch_values", "source_pages"],
                        "additionalProperties": False,
                    },
                },
            },
            "required": ["staged", "stages"], "additionalProperties": False,
        },
        "views": {
            "type": "array", "minItems": 1, "maxItems": 5,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "type": {"type": "string", "enum": VIEW_TYPES},
                    "title": {"type": "string"},
                    "semantic_ids": {"type": "array", "items": {"type": "string"}, "maxItems": 64},
                },
                "required": ["id", "type", "title", "semantic_ids"],
                "additionalProperties": False,
            },
        },
        "bindings": {
            "type": "array", "maxItems": 64,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "semantic_id": {"type": "string"},
                    "view_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 5},
                },
                "required": ["id", "semantic_id", "view_ids"],
                "additionalProperties": False,
            },
        },
        "focus_targets": {
            "type": "array", "minItems": 1, "maxItems": 16,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "label": {"type": "string"},
                    "expression": {"type": "string"}, "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "label", "expression", "source_pages"],
                "additionalProperties": False,
            },
        },
        "source_refs": {
            "type": "array", "maxItems": 64,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"}, "semantic_id": {"type": "string"}, "source_pages": SOURCE_PAGES,
                },
                "required": ["id", "semantic_id", "source_pages"],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "scene_version", "scene_id", "title", "domain", "learning_goal", "source_pages",
        "equally_likely", "outcomes", "events", "parameters", "states", "relations",
        "experiment", "views", "bindings", "focus_targets", "source_refs",
    ],
    "additionalProperties": False,
}

SCENE_INSTRUCTIONS = """You compile supplied learning material into a safe declarative Learning Scene.
Return only the strict JSON schema. The only supported v1 domain is probability_sets.
If the source does not support a finite probability/set model, return a conservative scene is not possible is not an option in this schema: only call this compiler for candidate material.
Use stable ASCII ids and concise human-facing labels. Outcomes, taken together, are the complete finite sample space S. Never emit S, sample_space, universe, omega, Ω, or an event containing every outcome as an ordinary event. Events contain exact outcome ids and must be proper subsets of S.
Use positive outcome weights; set equally_likely only when supported. For staged experiments, each outcome path has exactly one branch value per stage and every value is declared by that stage. When complete outcome labels such as (H,H), (H,T), (T,H), (T,T) clearly encode repeated ordered stages, set staged true, declare those stages, preserve the ordered paths, and include probability_tree. Do not add branch probabilities unless the source supports them. Otherwise staged is false, stages and paths are empty.
Views use only the whitelisted types. Include sample_space, set, formula and monte_carlo; add probability_tree only for a real staged experiment. semantic_ids reference declared outcomes/events/focus targets.
Focus target expressions use only event ids, | union, & intersection, ~ complement, - difference, and parentheses. Never emit code, HTML, JavaScript, Python, URLs, Plotly specifications, prose formulas, calls, indexing, or attribute access.
De Morgan and inclusion-exclusion operands must be two genuine non-universe events. Bindings connect the same semantic outcome/event/focus target to all views that represent it. Use the smallest source-page set that directly supports each item; pages must be drawn only from the supplied allowed pages, and use [] when uncertain. Do not invent outcomes, event membership, probabilities, stages, or pages."""
