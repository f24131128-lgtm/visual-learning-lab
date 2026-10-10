"""Golden Path presentation, existing event contracts and failure isolation."""
import copy
import unittest
from unittest.mock import patch

import test_day25
from scene.world import runtime


class GoldenPathTests(unittest.TestCase):
    def test_source_page_subset_survives_widget_cleanup_and_focus_change(self):
        helper = test_day25.TwinProductTests()
        app = helper.app("phase")
        helper.choose(app, "source_object")
        state = app.session_state["source_atlas_state"]
        atlas = copy.deepcopy(state["atlas"])
        atlas["processed_pages"] = [1, 2]
        atlas["regions"] = [r for r in atlas["regions"] if r["page"] in (1, 2)]
        key = state["key"][:4] + ((1, 2),) + state["key"][5:]
        state.update(key=key, atlas=atlas)
        app.session_state["source_atlas_cache"][key] = atlas
        material = app.session_state["analysis_id"]
        with patch("openai.resources.responses.Responses.create", side_effect=AssertionError("unexpected request")) as request:
            app.radio(key="workspace-mode-"+material).set_value("explore").run()
            app.radio(key="workspace-mode-"+material).set_value("source").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["source_atlas_state"]["key"], key)
            self.assertEqual(app.session_state["source_atlas_state"]["atlas"], atlas)
            self.assertEqual(app.multiselect(key="atlas-widget-pages-"+material).value, [1, 2])
            self.assertEqual(app.session_state["source_atlas_state"]["region_hint"], "source_object")
            request.assert_not_called()

    def test_ambiguous_source_choice_is_visible_and_explicit(self):
        helper = test_day25.TwinProductTests()
        app = helper.app("phase")
        atlas = app.session_state["source_atlas_state"]["atlas"]
        region = next(r for r in atlas["regions"] if r["region_id"] == "source_object")
        region["semantic_ids"] = ["angle", "wave"]
        with patch("openai.resources.responses.Responses.create", side_effect=AssertionError("unexpected request")) as request:
            helper.choose(app, "source_object")
            choice = next(w for w in app.selectbox if w.label == "選擇此來源的概念")
            self.assertEqual(app.session_state["learning_scene_state"]["world"]["focus"], "angle")
            choice.set_value("wave").run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["learning_scene_state"]["world"]["focus"], "wave")
            request.assert_not_called()

    def test_production_explore_removes_engineering_controls_preserves_state(self):
        helper = test_day25.TwinProductTests()
        for kind in ("phase", "projectile"):
            with self.subTest(kind=kind):
                app = helper.app(kind)
                helper.choose(app, "source_object")
                app.button(key="workspace-twin-explore").click().run()
                before = copy.deepcopy(app.session_state["learning_scene_state"]["world"])
                app.run()
                self.assertFalse(app.exception)
                labels = [e.label for e in app.expander]
                for fragment in ("Keyboard", "Recording", "Replay", "備援", "記錄", "3D"):
                    self.assertFalse(any(fragment in label for label in labels), labels)
                self.assertFalse(any(w.key.startswith("world-widget-") for w in app.slider))
                self.assertEqual(app.session_state["learning_scene_state"]["world"], before)
                wrapper = app.session_state["learning_scene_state"]
                data = runtime.payload(wrapper["scene"], wrapper)
                self.assertTrue(data["learner_view"])
                self.assertIn("recording", data)  # Internal contract retained.
                app.button(key="workspace-twin-source").click().run()
                self.assertEqual(app.session_state["learning_scene_state"]["world"], before)

    def test_next_actions_are_local_and_keep_the_original_material(self):
        helper = test_day25.TwinProductTests()
        app = helper.app("phase")
        material = app.session_state["analysis_id"]
        original = copy.deepcopy(app.session_state["analysis"])
        with patch("openai.resources.responses.Responses.create", side_effect=AssertionError("unexpected request")) as request:
            app.radio(key="workspace-mode-"+material).set_value("learn").run()
            app.button(key="workspace-next-explore").click().run()
            self.assertEqual(app.session_state["learning_workspace"]["mode"], "explore")
            app.radio(key="workspace-mode-"+material).set_value("learn").run()
            app.button(key="workspace-next-source").click().run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["learning_workspace"]["mode"], "source")
            self.assertEqual(app.session_state["analysis"], original)
            request.assert_not_called()

    def test_view_failure_uses_planar_snapshot_without_changing_state(self):
        helper = test_day25.TwinProductTests()
        app = helper.app("phase")
        helper.choose(app, "source_object")
        app.button(key="workspace-twin-explore").click().run()
        before = copy.deepcopy(app.session_state["learning_scene_state"]["world"])
        with patch("manipulation.runtime.render_world", return_value=False), patch.object(runtime, "_component", side_effect=ValueError("unavailable")):
            app.run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state["learning_scene_state"]["world"], before)
        self.assertTrue(any("互動視圖暫時" in info.value for info in app.info))
        self.assertTrue(any(chart.type == "plotly_chart" for chart in app.get("plotly_chart")))

    def test_real_rejection_shapes_still_fail_closed(self):
        from world_fixtures import three_phase_world
        from scene.world.validator import normalize_world
        raw = three_phase_world()
        for step in (dict(op="set_time", target_id="", value=.01),
                     dict(op="set_parameter", target_id="amplitude", value=10000)):
            candidate = copy.deepcopy(raw)
            candidate["experiments"][0]["steps"] = [step]
            with self.subTest(step=step), self.assertRaises(ValueError):
                normalize_world(candidate, [1])


if __name__ == "__main__":
    unittest.main()
