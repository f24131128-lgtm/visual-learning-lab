"""Day 17 probability fixtures; test data never enters application defaults."""


def two_toss_scene():
    outcomes = [
        {"id": "o_hh", "label": "(H,H)", "path": ["H", "H"], "weight": 1, "source_pages": [2]},
        {"id": "o_ht", "label": "(H,T)", "path": ["H", "T"], "weight": 1, "source_pages": [2]},
        {"id": "o_th", "label": "(T,H)", "path": ["T", "H"], "weight": 1, "source_pages": [2]},
        {"id": "o_tt", "label": "(T,T)", "path": ["T", "T"], "weight": 1, "source_pages": [2]},
    ]
    event_ids = ["E", "F"]
    semantic_ids = [item["id"] for item in outcomes] + event_ids + ["focus_e", "focus_union"]
    view_types = ["sample_space", "set", "probability_tree", "formula", "monte_carlo"]
    views = [{"id": f"view_{kind}", "type": kind, "title": kind.replace("_", " ").title(),
              "semantic_ids": semantic_ids} for kind in view_types]
    return {
        "scene_version": "1.0", "scene_id": "coin_toss_scene", "title": "Two coin tosses",
        "domain": "probability_sets", "learning_goal": "Connect outcomes, events, formulas, and repeated trials.",
        "source_pages": [2], "equally_likely": True, "outcomes": outcomes,
        "events": [
            {"id": "E", "label": "First toss is H", "outcome_ids": ["o_hh", "o_ht"], "source_pages": [2]},
            {"id": "F", "label": "Exactly one H", "outcome_ids": ["o_ht", "o_th"], "source_pages": [2]},
        ],
        "parameters": [],
        "states": [{"id": "shared_focus", "label": "Shared focus", "kind": "focus", "semantic_ids": ["E", "F"]}],
        "relations": [],
        "experiment": {"staged": True, "stages": [
            {"id": "stage_1", "label": "First toss", "branch_values": ["H", "T"], "source_pages": [2]},
            {"id": "stage_2", "label": "Second toss", "branch_values": ["H", "T"], "source_pages": [2]},
        ]},
        "views": views,
        "bindings": [{"id": f"binding_{semantic}", "semantic_id": semantic,
                      "view_ids": [view["id"] for view in views]} for semantic in semantic_ids],
        "focus_targets": [
            {"id": "focus_e", "label": "Event E", "expression": "E", "source_pages": [2]},
            {"id": "focus_union", "label": "E union F", "expression": "E | F", "source_pages": [2]},
        ],
        "source_refs": [{"id": "source_e", "semantic_id": "E", "source_pages": [2]}],
    }


def probability_analysis():
    from support import fixture
    analysis = fixture()
    analysis["quick_summary"] = "A finite probability sample space contains outcomes, and events are sets of outcomes."
    analysis["key_concepts"] = [
        {"concept": "Sample space", "explanation": "Four equally likely coin-toss outcomes.", "source_pages": [2]},
        {"concept": "Event", "explanation": "A subset of the sample space.", "source_pages": [2]},
    ]
    analysis["relationships"] = [{"source": "Event E", "relation": "is a subset of", "target": "Sample space S", "source_pages": [2]}]
    analysis["analysis_language"] = "en"
    return analysis
