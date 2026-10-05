"""Offline workspace contracts and real app active-view navigation."""
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

import streamlit as st
from streamlit.testing.v1 import AppTest
from workspace import state as ws
from scene.state import cache_key as scene_key
from scene.world.state import new_state, apply_patch, validate_semantic, start_recording, replay_states
from scene.world.validator import normalize_world
from source_atlas import compiler as atlas_compiler, runtime as atlas_runtime
from source_atlas.model import normalize_atlas, semantic_catalog
from source_atlas.state import cache_key, select_region, sync_region, current_focus
from source_lens import new_source_state
from support import ROOT, fixture
from atlas_fixtures import atlas_fixture, source_pdf, page_texts, region
from world_fixtures import complete_projectile_world


def hero_data():
    import pymupdf
    scene = normalize_world(complete_projectile_world(), [1, 2])
    catalog = semantic_catalog(scene)
    with pymupdf.open(stream=source_pdf("projectile"), filetype="pdf") as doc:
        doc[1].insert_text((64, 120), "Gravity g", fontsize=18)
        doc[1].insert_text((64, 170), "ay = -g", fontsize=18)
        pdf = doc.tobytes()
    raw = atlas_fixture("projectile")
    raw["regions"].extend([
        region("gravity_label", 2, (.07, .20, .30, .26), "Gravity g", ["gravity"], "label", "labels", excerpt="Gravity g"),
        region("gravity_formula", 2, (.07, .30, .30, .36), "ay = -g", ["gravity"], "formula", "formulas", excerpt="ay = -g"),
    ])
    atlas = normalize_atlas(raw, [1, 2], catalog, page_texts(pdf))
    return scene, catalog, pdf, atlas


class WorkspaceStateTests(unittest.TestCase):
    def setUp(self):
        self.session = patch.object(st, "session_state", {})
        self.session.start()
        self.addCleanup(self.session.stop)
        self.scene, self.catalog, self.pdf, self.atlas = hero_data()
        self.wrapper = dict(material_id="hero", scene=self.scene, world=new_state(self.scene))
        self.workspace = ws.get_workspace_state("hero")
        self.source = dict(atlas=self.atlas, region_hint=None, seen_focus=None, page=1)

    def test_navigation_is_local_and_preserves_focus_and_numeric_state(self):
        select_region(self.source, "gravity_label", self.catalog, self.wrapper)
        original = copy.deepcopy(self.wrapper["world"])
        for mode in ws.MODES:
            self.assertTrue(ws.open_workspace(self.workspace, mode))
            self.assertEqual(ws.get_workspace_focus(self.workspace, self.wrapper), "gravity")
        self.assertEqual(self.wrapper["world"], original)

    def test_source_explore_source_retains_disambiguated_anchor(self):
        select_region(self.source, "gravity_label", self.catalog, self.wrapper)
        ws.open_workspace(self.workspace, "explore", "gravity", self.catalog, self.wrapper)
        ws.open_workspace(self.workspace, "source")
        self.assertEqual(sync_region(self.source, ws.get_workspace_focus(self.workspace, self.wrapper))["region_id"], "gravity_label")

    def test_reverse_world_selection_changes_source_anchor(self):
        apply_patch(self.scene, self.wrapper["world"], dict(op="set_focus", target_id="vx", value=None))
        self.assertEqual(ws.get_workspace_focus(self.workspace, self.wrapper), "vx")
        self.assertIn("vx", sync_region(self.source, "vx")["semantic_ids"])

    def test_actions_require_actual_capabilities(self):
        selected = self.atlas["regions"][-2]
        available = ws.actions(selected, self.catalog, self.wrapper)
        self.assertEqual(set(available), {"explore", "explain", "formula"})
        self.assertNotIn("practice", available)

    def test_native_unlinked_region_has_only_literal_explanation(self):
        selected = dict(semantic_ids=[], source_text_excerpt="Literal native line")
        self.assertEqual(ws.actions(selected, {}, None), {"explain": True})

    def test_unmapped_empty_region_hides_all_actions(self):
        self.assertEqual(ws.actions(dict(semantic_ids=[], source_text_excerpt=""), {}), {})

    def test_parameter_is_not_fake_scene_focus(self):
        self.assertFalse(ws.open_workspace(self.workspace, "explore", "grav", self.catalog, self.wrapper))
        self.assertEqual(self.workspace["mode"], "learn")

    def test_malicious_or_unknown_focus_and_mode_rejected(self):
        for value in ("unknown", "<script>", None, [], {}):
            self.assertFalse(ws.set_workspace_focus(self.workspace, value, self.catalog, self.wrapper))
        self.assertFalse(ws.open_workspace(self.workspace, "other"))

    def test_material_identity_resets_navigation_only(self):
        st.session_state["quiz_answers"] = {"q": "a"}
        self.workspace.update(mode="explore", focus="gravity")
        self.assertEqual(ws.get_workspace_state("new")["mode"], "learn")
        self.assertEqual(st.session_state["quiz_answers"], {"q": "a"})

    def test_analysis_only_focus_uses_stable_graph_id(self):
        catalog = semantic_catalog(None, fixture())
        self.assertTrue(ws.set_workspace_focus(self.workspace, "input", catalog))
        self.assertEqual(ws.get_workspace_focus(self.workspace), "input")
        ws.clear_workspace_focus(self.workspace)
        self.assertIsNone(ws.get_workspace_focus(self.workspace))

    def test_clear_focus_preserves_physics_and_valid_recording_origin(self):
        world = self.wrapper["world"]
        original = copy.deepcopy(world)
        ws.clear_workspace_focus(self.workspace, self.wrapper)
        self.assertIsNone(current_focus(self.wrapper))
        for key in ("time", "parameters", "baseline", "recorded"):
            self.assertEqual(world[key], original[key])
        start_recording(world)
        apply_patch(self.scene, world, dict(op="set_focus", target_id="gravity", value=None))
        validate_semantic(self.scene, world["recording_origin"])
        self.assertEqual(replay_states(self.scene, world)[-1]["focus"], "gravity")

    def test_practice_requires_exact_validated_visual_ref(self):
        region = dict(semantic_ids=["input"], source_text_excerpt="")
        catalog = semantic_catalog(None, fixture())
        self.assertEqual(ws.actions(region, catalog, None, fixture()["learning_path"])["practice"], ["s1"])

    def test_foreign_material_cannot_change_focus_or_navigation(self):
        foreign = dict(self.wrapper, material_id="other")
        self.assertFalse(ws.open_workspace(self.workspace, "explore", "gravity", self.catalog, foreign))
        self.assertEqual(self.workspace["mode"], "learn")

    def test_clear_focus_is_recorded_and_replayed_locally(self):
        world = self.wrapper["world"]
        start_recording(world)
        ws.clear_workspace_focus(self.workspace, self.wrapper)
        self.assertEqual(world["recorded"], [{"kind": "clear_focus"}])
        self.assertIsNone(replay_states(self.scene, world)[-1]["focus"])

    def test_probability_clear_uses_valid_empty_set_then_selection(self):
        from scene.validator import normalize_scene
        from scene_fixtures import two_toss_scene
        from scene.renderers import semantic_focus
        scene = normalize_scene(two_toss_scene(), [1, 2])
        wrapper = dict(material_id="hero", scene=scene, active_expression="E", selected_focus_id="focus_e")
        ws.clear_workspace_focus(self.workspace, wrapper)
        self.assertEqual(semantic_focus(scene, wrapper)["outcome_ids"], frozenset())
        self.assertTrue(ws.set_workspace_focus(self.workspace, "F", semantic_catalog(scene), wrapper))
        self.assertEqual(current_focus(wrapper), "F")


class WorkspaceAppTests(unittest.TestCase):
    def app(self, hero=False):
        at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=40)
        analysis = fixture()
        analysis["analysis_language"] = "en"
        at.session_state["analysis"] = analysis
        at.session_state["analysis_id"] = "hero"
        at.session_state["product_language"] = "en"
        at.session_state["source_context"] = dict(kind="text", source_text="Original study material", page_texts={})
        at.session_state["allowed_source_pages"] = []
        if hero:
            scene, catalog, pdf, atlas = hero_data()
            analysis["learning_scene_candidate"] = dict(suitable=True, domain="spatial_dynamics", reason="Supported motion")
            at.session_state["allowed_source_pages"] = [1, 2]
            at.session_state["source_context"] = dict(kind="pdf", page_texts=page_texts(pdf))
            at.session_state["learning_scene_cache"] = {scene_key("hero", "en", "spatial_dynamics"): scene}
            at.session_state["learning_canvas"] = dict(material_id="hero", selected_id=None, kind=None, component=None,
                style_signature=None, last_event=-1, fallback=False, component_error=False, source=new_source_state("hero", pdf))
            key = cache_key("hero", pdf, "en", [1, 2], scene, catalog)
            at.session_state["source_atlas_cache"] = {key: atlas}
        return at

    def switch(self, at, mode):
        at.radio(key="workspace-mode-hero").set_value(mode).run()
        self.assertFalse(at.exception)
        return at

    def test_only_active_major_renderer_runs(self):
        with patch("interactive_lab.render_interactive_lab") as lab:
            with patch("dynamic_simulation.render_simulation_studio") as simulation:
                at = self.app().run()
                self.assertFalse(at.exception)
                self.assertFalse(lab.called)
                self.assertFalse(simulation.called)
                self.switch(at, "source")
                self.assertFalse(lab.called)
                self.switch(at, "explore")
                self.assertEqual(lab.call_count, 1)
                self.assertEqual(simulation.call_count, 1)
                self.switch(at, "practice")
                self.assertEqual(lab.call_count, 1)

    def test_analysis_only_all_modes_and_no_dead_source_actions(self):
        at = self.app().run()
        for mode in ws.MODES: self.switch(at, mode)
        self.switch(at, "source")
        self.assertTrue(any("Original study material" in e.value for e in at.text))
        self.assertFalse(any("workspace-action" in str(e.key) for e in at.button))

    def test_source_graph_focus_and_practice_share_existing_stable_ids(self):
        import learning_canvas
        with patch.object(atlas_runtime, "_component", return_value=None), patch.object(learning_canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app()
            analysis = at.session_state["analysis"]
            pdf = source_pdf()
            catalog = semantic_catalog(None, analysis)
            raw = atlas_fixture()
            for item in raw["regions"]: item["semantic_ids"] = ["input"]
            atlas = normalize_atlas(raw, [1, 2], catalog, page_texts(pdf))
            at.session_state["source_context"] = dict(kind="pdf", page_texts=page_texts(pdf))
            at.session_state["allowed_source_pages"] = [1, 2]
            at.session_state["learning_canvas"] = dict(material_id="hero", selected_id=None, kind=None, component=None,
                style_signature=None, last_event=-1, fallback=False, component_error=False, source=new_source_state("hero", pdf))
            at.session_state["source_atlas_cache"] = {cache_key("hero", pdf, "en", [1, 2], None, catalog): atlas}
            at.run()
            self.switch(at, "source")
            next(e for e in at.selectbox if e.label == "Choose a source object").set_value("formula_a").run()
            self.assertEqual(at.session_state["learning_workspace"]["focus"], "input")
            self.switch(at, "explore")
            self.assertEqual(at.session_state["learning_canvas"]["selected_id"], "input")
            self.switch(at, "source")
            at.button(key="workspace-action-hero-practice").click().run()
            self.assertEqual(at.session_state["guided_learning_step_id"], "s1")
            self.assertEqual(at.session_state["learning_workspace"]["mode"], "practice")

    def test_canonical_clear_removes_canvas_emphasis_and_keeps_quiz_state(self):
        import learning_canvas
        with patch.object(learning_canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state):
            at = self.app().run()
            self.switch(at, "explore")
            at.selectbox(key="canvas-list-hero-concept_map").set_value("input").run()
            at.session_state["guided_quiz_answers"] = {"q1": "b"}
            at.button(key="workspace-clear").click().run()
            self.assertIsNone(at.session_state["learning_canvas"]["selected_id"])
            self.assertEqual(at.session_state["guided_quiz_answers"], {"q1": "b"})

    def test_no_quiz_practice_has_supported_empty_state(self):
        at = self.app()
        at.session_state["analysis"]["learning_path"] = dict(suitable=False, steps=[], checkpoint_questions=[], title="", reason="")
        at.run()
        self.switch(at, "practice")
        self.assertFalse(any("quiz" in str(e.key) for e in at.button))

    def test_pdf_bytes_absent_still_shows_only_validated_extracted_pages(self):
        at = self.app()
        at.session_state["allowed_source_pages"] = [1]
        at.session_state["source_context"] = dict(kind="pdf", page_texts={1: "Available original text", 99: "Unanalyzed page"})
        at.run()
        self.switch(at, "source")
        self.assertTrue(any("Available original text" in e.value for e in at.text))
        self.assertFalse(any("Unanalyzed page" in e.value for e in at.text))

    def test_projectile_hero_zero_api_parser_calls_and_state_retained(self):
        with patch.object(atlas_runtime, "_component", return_value=None), \
             patch("scene.world.runtime._component", return_value=None), \
             patch("scene.compiler.request_scene") as compile_scene, \
             patch.object(atlas_compiler, "request_atlas") as compile_atlas, \
             patch("document_intelligence.pdfplumber_adapter.parse") as parser:
            at = self.app(hero=True).run()
            self.assertFalse(at.exception)
            self.switch(at, "source")
            next(e for e in at.selectbox if e.label in ("Source page", "來源頁面")).set_value(2).run()
            source_select = next(e for e in at.selectbox if e.label in ("Choose a source object", "選取來源物件"))
            source_select.set_value("gravity_label").run()
            self.assertFalse(at.exception)
            self.assertTrue(any(e.value == "Current focus: Gravity g" for e in at.text))
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"], "gravity")
            at.button(key="workspace-action-hero-explore").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(at.session_state["learning_workspace"]["mode"], "explore")
            self.assertEqual(at.selectbox(key="world-widget-hero-focus").value, "gravity")
            at.slider(key="world-widget-hero-time").set_value(.5).run()
            world = copy.deepcopy(at.session_state["learning_scene_state"]["world"])
            self.switch(at, "source")
            self.assertEqual(at.session_state["source_atlas_state"]["region_hint"], "gravity_label")
            self.assertEqual(at.session_state["learning_scene_state"]["world"], world)
            at.button(key="workspace-action-hero-formula").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(at.session_state["source_atlas_state"]["region_hint"], "gravity_formula")
            for mocked in (compile_scene, compile_atlas, parser): mocked.assert_not_called()

    def test_reverse_selection_and_clear_do_not_break_world(self):
        with patch.object(atlas_runtime, "_component", return_value=None), patch("scene.world.runtime._component", return_value=None):
            at = self.app(hero=True).run()
            self.switch(at, "explore")
            at.selectbox(key="world-widget-hero-focus").set_value("vx").run()
            self.switch(at, "source")
            self.assertIn("vx", next(r for r in at.session_state["source_atlas_state"]["atlas"]["regions"] if r["region_id"] == at.session_state["source_atlas_state"]["region_hint"])["semantic_ids"])
            at.button(key="workspace-clear").click().run()
            self.switch(at, "explore")
            self.assertIsNone(at.session_state["learning_scene_state"]["world"]["focus"])

    def test_source_explanation_is_explicit_grounded_and_cached_across_navigation(self):
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(dict(
            plain_explanation="Gravity changes vertical velocity.", why_it_matters="Connect force and motion.",
            intuition_or_example="", source_note="Based on the supplied context.")))
        with patch("openai.OpenAI", return_value=client), patch.object(atlas_runtime, "_component", return_value=None), patch("scene.world.runtime._component", return_value=None):
            at = self.app(hero=True)
            at.secrets["OPENAI_API_KEY"] = "offline-placeholder"
            at.run()
            self.switch(at, "source")
            next(e for e in at.selectbox if e.label == "Source page").set_value(2).run()
            next(e for e in at.selectbox if e.label == "Choose a source object").set_value("gravity_label").run()
            client.responses.create.assert_not_called()
            button = next(e for e in at.button if str(e.key).startswith("explain-hero:source-region:gravity_label:"))
            button.click().run()
            self.assertFalse(at.exception)
            context = json.loads(client.responses.create.call_args.kwargs["input"])
            self.assertEqual(context["relevant_pages"], [2])
            self.assertEqual(context["response_language"], "English")
            client.files.create.assert_not_called()
            self.switch(at, "explore")
            self.switch(at, "source")
            next(e for e in at.button if str(e.key).startswith("explain-hero:source-region:gravity_label:")).click().run()
            self.assertEqual(client.responses.create.call_count, 1)

    def test_missing_atlas_and_native_package_preserve_scene(self):
        with patch.object(atlas_runtime, "_component", return_value=None), patch("scene.world.runtime._component", return_value=None), patch("document_intelligence.ui.available", return_value=False):
            at = self.app(hero=True)
            at.session_state["source_atlas_cache"] = {}
            at.run()
            self.switch(at, "source")
            self.assertTrue(any(e.key == "atlas-widget-build-hero" for e in at.button))
            self.switch(at, "explore")
            self.assertEqual(at.selectbox(key="world-widget-hero-focus").value, "px")

    def test_image_only_native_fallback_keeps_ai_atlas_and_world_available(self):
        from day20_fixtures import corpus
        with patch("scene.world.runtime._component", return_value=None), patch("document_intelligence.ui.available", return_value=True), patch("scene.compiler.request_scene") as scene_call, patch.object(atlas_compiler, "request_atlas") as atlas_call:
            at = self.app(hero=True)
            at.session_state["learning_canvas"]["source"]["pdf_bytes"] = corpus()["image_only"]
            at.session_state["allowed_source_pages"] = [1]
            at.session_state["source_context"] = dict(kind="pdf", page_texts={1: ""})
            at.run()
            self.switch(at, "source")
            at.button(key="atlas-widget-native-hero").click().run()
            self.assertFalse(at.exception)
            self.assertFalse(at.session_state["source_atlas_state"]["document_available"])
            self.assertFalse(at.button(key="atlas-widget-build-hero").disabled)
            self.switch(at, "explore")
            self.assertTrue(at.session_state["learning_scene_state"]["scene"])
            scene_call.assert_not_called()
            atlas_call.assert_not_called()


if __name__ == "__main__": unittest.main()
