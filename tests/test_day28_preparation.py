"""Offline study preparation checks; automation is never human evidence."""
import copy
import csv
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from day28_prepared import ROOT, PUBLIC, install, prepare


class PreparationTests(unittest.TestCase):
    def test_changed_input_fails_before_session_mutation(self):
        state = {"existing_learning": {"quiz": "keep"}}
        before = copy.deepcopy(state)
        with patch("day28_prepared.sha", return_value="changed"):
            with self.assertRaises(ValueError):
                install(state)
        self.assertEqual(state, before)

    def test_source_provenance_local_changes_and_immutable_source(self):
        from interactive_lab import clean_interactive_lab, default_values, compute_curves, commit_lab_values
        from quantity_contract import source_values
        from support import load_app_helpers
        from source_atlas.model import semantic_catalog
        data = prepare()
        helpers = load_app_helpers()
        analysis = data["analysis"]
        lab = clean_interactive_lab(analysis["interactive_lab"], data["allowed_source_pages"],
                                   analysis["learning_path"], helpers["valid_source_pages"],
                                   catalog=semantic_catalog(None, analysis), material=data["analysis_id"])
        demo = lab["demos"][0]
        values = default_values(demo)
        saved = dict(specification=demo, values=values, compare=False)
        source = copy.deepcopy(data["learning_canvas"]["source"])
        facts = source_values(demo)
        original = compute_curves(demo, values)[1]["shifted_displacement"].copy()
        commit_lab_values(demo, saved, {"trial_amplitude": 1.5})
        current = compute_curves(demo, saved["values"])[1]["shifted_displacement"]
        self.assertTrue((abs(current-original/2) < 1e-10).all())
        self.assertEqual(source_values(demo), facts)
        self.assertEqual(data["learning_canvas"]["source"], source)
        self.assertEqual(data["learning_workspace"]["mode"], "learn")
        self.assertIsNone(data["learning_workspace"]["focus"])
        self.assertEqual(data["allowed_source_pages"], list(range(1, 9)))
        self.assertNotIn("learning_scene_cache", data)
        self.assertNotIn("learning_world_plans", data)

    def test_blank_templates_and_counterbalanced_assignments(self):
        template = json.loads((PUBLIC / "participant-template.json").read_text(encoding="utf-8"))
        self.assertIsNone(template["participant_code"])
        self.assertTrue(all(t["human_score_0_1_2"] is None for t in template["study_b"]["tasks"]))
        with (PUBLIC / "HUMAN_DATA_TEMPLATE.csv").open(encoding="utf-8", newline="") as file:
            self.assertEqual(list(csv.DictReader(file)), [])
        assignments = json.loads((PUBLIC / "TASK_ORDER_ASSIGNMENTS.json").read_text(encoding="utf-8"))
        rows = assignments["participants"]
        self.assertEqual([r["participant_code"] for r in rows], [f"P{i:02}" for i in range(1, 6)])
        for row in rows:
            self.assertEqual([t["task_id"] for t in row["sequence"]], ["A", "B"])
            self.assertEqual({t["condition"] for t in row["sequence"]}, {"PDF", "VLL"})
        self.assertEqual([r["sequence"][0]["condition"] for r in rows], ["PDF", "VLL", "PDF", "VLL", "PDF"])

    def test_homepage_to_four_production_views_zero_requests(self):
        with patch("openai.resources.responses.Responses.create") as api, \
             patch("openai.resources.files.Files.create") as uploads:
            app = AppTest.from_file(str(ROOT / "tests/manual_day28.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertNotIn("analysis", app.session_state)
            self.assertTrue(app.get("file_uploader"))
            next(b for b in app.button if b.key == "day28-open-prepared").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["learning_workspace"]["mode"], "learn")
            material = app.session_state["analysis_id"]
            pdf_before = app.session_state["learning_canvas"]["source"]["pdf_bytes"]
            nav = "workspace-mode-"+material
            for mode in ("source", "explore", "practice", "source"):
                next(r for r in app.radio if r.key == nav).set_value(mode).run()
                self.assertFalse(app.exception, mode)
                self.assertEqual(app.session_state["learning_workspace"]["mode"], mode)
                self.assertEqual(app.session_state["learning_canvas"]["source"]["pdf_bytes"], pdf_before)
                if mode == "explore":
                    sliders = list(app.slider)
                    self.assertGreaterEqual(len(sliders), 3)
                    amplitude = next(s for s in sliders if "trial_amplitude" in s.key)
                    amplitude.set_value(1.5).run()
                    self.assertFalse(app.exception)
                if mode == "practice":
                    self.assertTrue(app.session_state["workspace_learning_path"]["steps"])
            demo = next(iter(app.session_state["interactive_lab_state"]["demos"].values()))
            self.assertTrue(math.isclose(demo["values"]["trial_amplitude"], 1.5))
            attempts = app.session_state["day28_blocked_requests"] if "day28_blocked_requests" in app.session_state else 0
            self.assertEqual(attempts, 0)
            api.assert_not_called()
            uploads.assert_not_called()


if __name__ == "__main__":
    unittest.main()
