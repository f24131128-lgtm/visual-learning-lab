"""Offline compiler stage evidence; no credentials, source bodies or paid calls."""
import copy
import json
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from analogy import compiler, state
from analogy.diagnostics import summary
from analogy_fixtures import formal, spec


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        scene, self.catalog = formal("electricity")
        self.registry = state.parameter_registry({"scene": scene}, {}, None, self.catalog)
        self.store = state.ensure({}, "material", "zh-TW", "signature")
        self.key = state.identity("material", "zh-TW", "signature", "voltage")
        self.raw = spec("electricity")
        self.client = MagicMock()

    def build(self):
        self.client.responses.create.return_value = SimpleNamespace(output_text=json.dumps(self.raw))
        return compiler.build(self.store,self.key,self.client,"offline",{"analysis_language":"zh-TW"},self.catalog,self.registry,[1])

    def test_shape_path_and_structural_candidate_preserved(self):
        self.raw["parameters"][0]["step"] = True
        self.assertIsNone(self.build())
        trace = self.store["diagnostics"][self.key]
        self.assertEqual((trace["stage"],trace["code"],trace["path"]),("normalize","numeric_bounds","$.parameters[0].step"))
        self.assertEqual(trace["generated"]["selected_candidate"],"candidate_one")
        self.assertEqual(trace["generated"]["mappings"][0]["formal_id"],"voltage")
        self.assertNotIn("expression",json.dumps(trace))

    def test_sdk_messages_never_retained(self):
        self.client.responses.create.side_effect = RuntimeError("sk-secret raw private source")
        self.assertIsNone(self.build())
        trace=self.store["diagnostics"][self.key]
        self.assertEqual(trace["stage"],"request")
        self.assertNotIn("secret",repr(self.store))

    def test_accepted_trace_and_bounded_records(self):
        self.assertIsNotNone(self.build())
        self.assertEqual(self.store["diagnostics"][self.key]["code"],"accepted")
        from analogy.diagnostics import record, Rejection
        for n in range(10): record(self.store,str(n),"normalize",Rejection("mapping"),self.raw)
        self.assertEqual(len(self.store["diagnostics"]),4)

    def test_sanitizer_no_source_code_credentials_or_unbounded_objects(self):
        raw=copy.deepcopy(self.raw)
        raw.update(source_context="private",explanation="private",reason="sk-secret\n<script>bad</script>")
        raw["candidates"]=raw["candidates"]*100
        result=summary(raw)
        self.assertLessEqual(len(result["candidates"]),24)
        self.assertNotIn("private",json.dumps(result)); self.assertNotIn("sk-secret",json.dumps(result))

    def test_refusal_incomplete_and_decode_identified_without_provider_text(self):
        cases=[(SimpleNamespace(output_text="",status="incomplete"),"incomplete_response"),
            (SimpleNamespace(output_text="",output=[SimpleNamespace(content=[SimpleNamespace(type="refusal",refusal="private")])]),"model_refusal"),
            (SimpleNamespace(output_text="private invalid json"),"invalid_json")]
        for response,code in cases:
            self.client.responses.create.return_value=response
            self.assertIsNone(compiler.build(self.store,self.key,self.client,"offline",{"analysis_language":"zh-TW"},self.catalog,self.registry,[1]))
            entry=self.store["diagnostics"][self.key]
            self.assertEqual((entry["stage"],entry["code"]),("response",code))
            self.assertNotIn("private",repr(entry))

    def test_schema_provider_classification_is_allowlisted(self):
        from analogy.diagnostics import record
        error=RuntimeError("private source and credentials")
        error.status_code=400; error.body={"error":{"code":"invalid_json_schema","message":"private","param":"private"}}
        entry=record(self.store,self.key,"request",error)
        self.assertEqual(entry["provider_code"],"invalid_json_schema")
        self.assertEqual(entry["http_status"],400); self.assertNotIn("private",repr(entry))


class RendererDiagnosticTests(unittest.TestCase):
    def test_first_renderer_failure_is_downloadable_and_recovers_without_a_request(self):
        from test_analogy import AnalogyAppTests
        from analogy import runtime
        at,raw=AnalogyAppTests().app()
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None):
            at.run()
            with patch.object(runtime,"_render_valid",side_effect=RuntimeError("private renderer detail")):
                at.button(key="analogy-build-a").click().run()
            store=at.session_state["analogy_world_state"]
            self.assertTrue(store["cache"]); self.assertTrue(store["errors"])
            self.assertFalse(at.exception)
            self.assertTrue(any(e.label=="譬喻開發診斷" for e in at.expander))
            self.assertIn("renderer",at.json[0].value)
            self.assertNotIn("private renderer detail",at.json[0].value)
            at.run()
            self.assertFalse(store["errors"]); self.assertFalse(at.exception)
            self.assertEqual(client.responses.create.call_count,1)

    def test_reused_build_renderer_failure_is_visible_under_a_different_mapped_focus(self):
        from test_analogy import AnalogyAppTests
        from analogy import runtime
        at,raw=AnalogyAppTests().app()
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(raw))
        with patch("openai.OpenAI",return_value=client),patch.object(runtime,"_component",return_value=None):
            at.run(); at.button(key="analogy-build-a").click().run()
            store=at.session_state["analogy_world_state"]; build_key=store["active"]
            with patch.object(runtime,"_render_valid",side_effect=RuntimeError("controlled failure")):
                next(b for b in at.button if b.label=="電阻 ↔ 管道限制").click().run()
            self.assertEqual(at.session_state["learning_scene_state"]["world"]["focus"],"resistance")
            self.assertEqual(store["active"],build_key)
            self.assertEqual(store["diagnostics"][build_key]["stage"],"renderer")
            self.assertFalse(at.exception)
            self.assertTrue(any(e.label=="譬喻開發診斷" for e in at.expander))
            self.assertIn("renderer",at.json[0].value)
            self.assertEqual(client.responses.create.call_count,1)


if __name__=="__main__": unittest.main()
