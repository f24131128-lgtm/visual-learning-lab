"""Source Atlas must render before an optional semantic scene is compiled."""

import json
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from streamlit.testing.v1 import AppTest

import learning_canvas as canvas
from scene.state import cache_key as scene_key
from scene.validator import normalize_scene
from scene.world.state import new_state
from scene.world.validator import normalize_world
from source_lens import new_source_state
from source_atlas import compiler, runtime, state
from source_atlas.model import normalize_atlas, semantic_catalog

try:
    from atlas_fixtures import atlas_fixture, page_texts, source_pdf
    from scene_fixtures import two_toss_scene
    from support import fixture
    import test_day19 as day19
    from world_fixtures import three_phase_world
except ModuleNotFoundError:
    from .atlas_fixtures import atlas_fixture, page_texts, source_pdf
    from .scene_fixtures import two_toss_scene
    from .support import fixture
    from . import test_day19 as day19
    from .world_fixtures import three_phase_world


class OptionalSceneRenderTests(unittest.TestCase):
    def bundle(self, wrapper, semantic_id="input"):
        pdf = source_pdf()
        scene = wrapper.get("scene") if isinstance(wrapper, dict) else None
        catalog = semantic_catalog(scene, fixture())
        raw = atlas_fixture()
        for r in raw["regions"]:
            r["semantic_ids"] = [semantic_id]
        atlas = normalize_atlas(raw, [1, 2], catalog, page_texts(pdf))
        key = state.cache_key("optional19", pdf, "zh-TW", [1, 2], scene, catalog)
        return dict(state=dict(key=key, atlas=atlas, page=1, region_hint="formula_a",
                              seen_focus=None, last_token=None),
                    catalog=catalog, wrapper=wrapper, material_id="optional19",
                    source=new_source_state("optional19", pdf), allowed=[1, 2])

    def app(self, bundle):
        at = AppTest.from_string("""
import streamlit as st
from source_atlas.runtime import render_atlas
render_atlas(st.session_state['bundle'])
""", default_timeout=30)
        at.session_state["bundle"] = bundle
        return at

    def assert_source_only(self, wrapper, omit_wrapper=False):
        bundle = self.bundle(wrapper)
        if omit_wrapper:
            bundle.pop("wrapper")
        with patch.object(runtime, "_component", return_value=None) as viewer:
            at = self.app(bundle).run()
            self.assertFalse(at.exception)
            self.assertTrue(any("原始來源" in e.value for e in at.markdown))
            self.assertTrue(any("公式追溯" in e.value for e in at.markdown))
            self.assertTrue(any("Ia" in e.value for e in at.text))
            self.assertFalse(any(e.label == "轉成互動場景" for e in at.button))
            payload = viewer.call_args.kwargs["payload"]
            self.assertTrue(payload["image"].startswith("data:image/png;base64,"))
            self.assertEqual(len(payload["regions"]), 4)
            self.assertIsNone(state.current_focus(wrapper))
            self.assertFalse(state.set_focus(wrapper, "input", bundle["catalog"]))
            next(e for e in at.selectbox if e.label == "來源頁面").set_value(2).run()
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("formula_b").run()
            self.assertFalse(at.exception)
            self.assertEqual(viewer.call_args.kwargs["payload"]["page"], 2)
            self.assertEqual(viewer.call_args.kwargs["payload"]["selected"], "formula_b")
        return at

    def test_wrapper_scene_none_renders_source_and_formula_without_linking(self):
        self.assert_source_only(dict(material_id="optional19", scene=None))

    def test_scene_key_absent_renders_source_without_linking(self):
        self.assert_source_only(dict(material_id="optional19"))

    def test_no_wrapper_renders_source_without_linking(self):
        self.assert_source_only(None)

    def test_bundle_wrapper_key_absent_renders_source_without_linking(self):
        self.assert_source_only(None, omit_wrapper=True)

    def test_probability_scene_renders_and_keeps_bidirectional_focus(self):
        scene = normalize_scene(two_toss_scene(), [1, 2])
        wrapper = dict(material_id="optional19", scene=scene, active_expression="E",
                       selected_focus_id="focus_e", selected_outcome_id=None)
        bundle = self.bundle(wrapper, "E")
        bundle["state"]["atlas"]["regions"][2]["semantic_ids"] = ["F"]
        with patch.object(runtime, "_component", return_value=None) as viewer:
            at = self.app(bundle).run()
            self.assertFalse(at.exception)
            self.assertTrue(any(e.label == "轉成互動場景" for e in at.button))
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("vector_b").run()
            self.assertFalse(at.exception)
            active = at.session_state["bundle"]["wrapper"]
            self.assertEqual(state.current_focus(active), "F")
            active["active_expression"] = "E"
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(viewer.call_args.kwargs["payload"]["selected"], "formula_a")

    def test_spatial_scene_renders_and_keeps_bidirectional_focus(self):
        scene = normalize_world(three_phase_world(), [1, 2])
        wrapper = dict(material_id="optional19", scene=scene, world=new_state(scene))
        bundle = self.bundle(wrapper, "ia")
        bundle["state"]["atlas"]["regions"][2]["semantic_ids"] = ["ib"]
        with patch.object(runtime, "_component", return_value=None) as viewer:
            at = self.app(bundle).run()
            self.assertFalse(at.exception)
            self.assertTrue(any(e.label == "轉成互動場景" for e in at.button))
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("vector_b").run()
            self.assertFalse(at.exception)
            active = at.session_state["bundle"]["wrapper"]
            self.assertEqual(state.current_focus(active), "ib")
            active["world"]["focus"] = "ia"
            at.run()
            self.assertFalse(at.exception)
            self.assertEqual(viewer.call_args.kwargs["payload"]["selected"], "formula_a")


class NormalPDFOptionalSceneTests(unittest.TestCase):
    def test_real_pdf_path_builds_atlas_before_world_then_enables_links(self):
        raw = atlas_fixture()
        for r in raw["regions"]:
            r["semantic_ids"] = []  # PDF regions do not need a scene mapping.
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(raw))
        with patch.object(compiler, "OpenAI", return_value=client), \
                patch.object(canvas, "streamlit_flow", side_effect=lambda key, state, **kw: state), \
                patch.object(runtime, "_component", return_value=None) as viewer:
            at = day19.NormalPDFTests().app()
            at.session_state["learning_scene_cache"] = {}
            at.run()
            self.assertIsNone(at.session_state["learning_scene_state"]["scene"])
            self.assertFalse(at.exception)
            at.button(key="atlas-widget-build-pdf19").click().run()
            self.assertFalse(at.exception)
            self.assertIsNone(at.session_state["learning_scene_state"]["scene"])
            self.assertTrue(any("原始來源" in e.value for e in at.markdown))
            self.assertTrue(viewer.called)
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("formula_a").run()
            self.assertFalse(at.exception)
            self.assertTrue(any("公式追溯" in e.value for e in at.markdown))
            self.assertFalse(any(e.label == "轉成互動場景" for e in at.button))
            next(e for e in at.selectbox if e.label == "來源頁面").set_value(2).run()
            self.assertFalse(at.exception)
            self.assertEqual(client.responses.create.call_count, 1)
            at.radio(key="workspace-mode-pdf19").set_value("explore").run()
            self.assertFalse(at.button(key="scene-widget-build-pdf19").disabled)
            at.radio(key="workspace-mode-pdf19").set_value("source").run()

            # A later validated scene changes semantic identity. Explicitly
            # rebuild grounding with that catalog, retaining the existing bridge.
            scene = normalize_world(three_phase_world(), [1, 2])
            at.session_state["learning_scene_cache"] = {scene_key("pdf19", "zh-TW", "spatial_dynamics"): scene}
            client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(atlas_fixture()))
            at.run()
            at.button(key="atlas-widget-build-pdf19").click().run()
            self.assertFalse(at.exception)
            next(e for e in at.selectbox if e.label == "選取來源物件").set_value("vector_b").run()
            self.assertFalse(at.exception)
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"], "ib")
            at.radio(key="workspace-mode-pdf19").set_value("explore").run()
            at.selectbox(key="world-widget-pdf19-focus").set_value("ia").run()
            at.radio(key="workspace-mode-pdf19").set_value("source").run()
            self.assertFalse(at.exception)
            self.assertEqual(at.session_state["source_atlas_state"]["region_hint"], "formula_a")
            self.assertEqual(client.responses.create.call_count, 2)


class OptionalExtractedTextTests(unittest.TestCase):
    def test_null_or_absent_page_texts_do_not_break_grounding_request(self):
        pdf = source_pdf()
        client = MagicMock()
        client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(atlas_fixture()))
        for context in ({}, {"page_texts": None}, {"page_texts": {1: None}}):
            with self.subTest(context=context):
                compiler.request_atlas(client, "offline", {}, context, new_source_state("m", pdf),
                                       "m", [1], [1, 2], {})
                content = client.responses.create.call_args.kwargs["input"][0]["content"]
                self.assertEqual(json.loads(content[0]["text"])["extracted_text"], {"1": ""})
                self.assertEqual(len([c for c in content if c["type"] == "input_image"]), 1)
        self.assertEqual(client.responses.create.call_count, 3)

    def test_null_page_text_does_not_claim_excerpt_verified(self):
        scene = normalize_world(three_phase_world(), [1, 2])
        for texts in (None, {}, {1: None, 2: None}):
            with self.subTest(texts=texts):
                atlas = normalize_atlas(atlas_fixture(), [1, 2], semantic_catalog(scene), texts)
                self.assertEqual(len(atlas["regions"]), 6)
                self.assertFalse(any(r["excerpt_verified"] for r in atlas["regions"]))


if __name__ == "__main__":
    unittest.main()
