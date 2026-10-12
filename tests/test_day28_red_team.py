"""AI-SIMULATED RED TEAM engineering tests; no human scores or API calls."""
import copy
import hashlib
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest
from day28_prepared import ROOT, prepare
from interactive_lab import clean_interactive_lab
from source_atlas.model import semantic_catalog
from support import load_app_helpers
from workspace.control_navigation import active_control_demo, linked_control_demo, open_controls


class RedTeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = prepare()
        cls.catalog = semantic_catalog(None, cls.data["analysis"])
        cls.lab = clean_interactive_lab(cls.data["analysis"]["interactive_lab"], cls.data["allowed_source_pages"],
            cls.data["analysis"]["learning_path"], load_app_helpers()["valid_source_pages"],
            catalog=cls.catalog, material=cls.data["analysis_id"])

    def test_exact_owner_not_label_or_page_inference(self):
        d = self.data
        self.assertIsNotNone(linked_control_demo(self.lab, self.catalog, d["analysis_id"], d["allowed_source_pages"], "amplitude_phase"))
        for focus in (None, "p1_sine_formula", "spring_model", "Amplitude", "__import__('os')"):
            self.assertIsNone(linked_control_demo(self.lab, self.catalog, d["analysis_id"], d["allowed_source_pages"], focus))

    def test_stale_modified_or_ambiguous_ownership_rejected(self):
        d = self.data
        resolve = lambda lab, material=d["analysis_id"], pages=d["allowed_source_pages"]: linked_control_demo(lab, self.catalog, material, pages, "amplitude_phase")
        self.assertIsNone(resolve(self.lab, "other-material"))
        self.assertIsNone(resolve(self.lab, pages=[1]))
        changed = copy.deepcopy(self.lab)
        changed["demos"][0]["parameters"][0]["label"] += " altered"
        self.assertIsNone(resolve(changed))
        ambiguous = copy.deepcopy(self.lab)
        ambiguous["demos"].append(copy.deepcopy(ambiguous["demos"][0]))
        self.assertIsNone(resolve(ambiguous))

    def test_controls_require_adjustable_parameter_and_current_focus(self):
        from representation_contract import bind
        lab = copy.deepcopy(self.lab)
        demo = lab["demos"][0]
        for p in demo["parameters"]:
            p.update(provenance="source_fixed", expose_control=False)
        demo["ownership"] = bind(demo, self.catalog, self.data["analysis_id"], self.data["allowed_source_pages"])
        self.assertIsNone(linked_control_demo(lab, self.catalog, self.data["analysis_id"], self.data["allowed_source_pages"], "amplitude_phase"))
        state = copy.deepcopy(self.data["learning_workspace"])
        self.assertTrue(open_controls(state, self.lab, self.catalog, self.data["allowed_source_pages"], "amplitude_phase"))
        self.assertIsNotNone(active_control_demo(state, self.lab, self.catalog, self.data["allowed_source_pages"], "amplitude_phase"))
        self.assertIsNone(active_control_demo(state, self.lab, self.catalog, self.data["allowed_source_pages"], "spring_model"))

    def test_invalid_navigation_preserves_learning_state(self):
        state = copy.deepcopy(self.data["learning_workspace"])
        before = copy.deepcopy(state)
        self.assertFalse(open_controls(state, self.lab, self.catalog, self.data["allowed_source_pages"], "unknown"))
        self.assertEqual(state, before)

    def test_frozen_human_files_and_original_browser_evidence_unchanged(self):
        manifest = json.loads((ROOT / "docs/day28/freeze-manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["files_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)
        seal = json.loads((ROOT / "docs/day28-ai-red-team/baseline-integrity.json").read_text(encoding="utf-8-sig"))
        for name, expected in seal["files_sha256"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)

    def test_source_controls_round_trip_zero_requests_and_unchanged_source(self):
        with patch("openai.resources.responses.Responses.create") as api, patch("openai.resources.files.Files.create") as uploads:
            app = AppTest.from_file(str(ROOT / "tests/manual_day28_red_team.py"), default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertTrue(next(b for b in app.button if b.key == "analyze-material").disabled)
            self.assertTrue(app.get("file_uploader"))
            next(b for b in app.button if b.key == "red-team-open-prepared").click().run()
            material = app.session_state["analysis_id"]
            nav = "workspace-mode-" + material
            source = copy.deepcopy(app.session_state["source_context"])
            pdf = app.session_state["learning_canvas"]["source"]["pdf_bytes"]
            analysis = copy.deepcopy(app.session_state["analysis"])
            app.session_state["red_team_preservation_sentinel"] = {"quiz": "keep", "explanations": "keep", "review": "keep"}
            next(r for r in app.radio if r.key == nav).set_value("source").run()
            next(s for s in app.selectbox if s.key == "workspace-control-concept-"+material).set_value("amplitude_phase").run()
            next(b for b in app.button if b.key == "workspace-source-controls").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["learning_workspace"]["mode"], "explore")
            self.assertTrue(next(e for e in app.expander if e.label == "參數與對照").proto.expanded)
            amplitude = next(s for s in app.slider if "trial_amplitude" in s.key)
            amplitude.set_value(2.9).run()
            self.assertFalse(app.exception)
            next(b for b in app.button if b.key == "workspace-controls-source").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["learning_workspace"]["mode"], "source")
            self.assertEqual(app.session_state["source_context"], source)
            self.assertEqual(app.session_state["learning_canvas"]["source"]["pdf_bytes"], pdf)
            self.assertEqual(app.session_state["analysis"], analysis)
            self.assertEqual(app.session_state["red_team_preservation_sentinel"]["quiz"], "keep")
            saved = next(iter(app.session_state["interactive_lab_state"]["demos"].values()))
            self.assertEqual(saved["values"]["trial_amplitude"], 2.9)
            self.assertEqual(app.session_state["day28_blocked_requests"] if "day28_blocked_requests" in app.session_state else 0, 0)
            api.assert_not_called(); uploads.assert_not_called()

    def test_offline_generation_entries_disabled_local_controls_live(self):
        app = AppTest.from_file(str(ROOT / "tests/manual_day28_red_team.py"), default_timeout=30).run()
        next(b for b in app.button if b.key == "red-team-open-prepared").click().run()
        material = app.session_state["analysis_id"]
        nav = "workspace-mode-"+material
        for mode in ("learn", "source", "explore", "practice"):
            next(r for r in app.radio if r.key == nav).set_value(mode).run()
            self.assertFalse(app.exception)
            for b in app.button:
                if b.key and (b.key.startswith(("explain-", "scene-widget-build-", "world-plan-", "atlas-widget-build-", "sim-widget-link-")) or b.key.startswith("sim-widget-") and b.key.endswith("-build")):
                    self.assertTrue(b.disabled, b.key)
            if mode == "explore": self.assertTrue(app.slider)
        self.assertEqual(app.session_state["day28_blocked_requests"] if "day28_blocked_requests" in app.session_state else 0, 0)


if __name__ == "__main__":
    unittest.main()
