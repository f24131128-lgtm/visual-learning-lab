"""Prospective evidence/tooling contracts. No paid API calls in tests."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import day23_benchmark as bench
from day23_freeze import digest
from day22_fixtures import discrete
from learning_world import planner
from learning_world import compiler
from learning_world.capabilities import contracts
from source_atlas.model import semantic_catalog
from workspace.state import set_workspace_focus


class CorpusTests(unittest.TestCase):
    def test_frozen_hash_provenance_gold_and_diversity(self):
        manifest = bench.read_manifest()
        payload = manifest["payload"]
        materials = payload["materials"]
        self.assertEqual(len(materials), 12)
        self.assertEqual(len({c["material_id"] for c in materials}), 12)
        self.assertGreaterEqual(len({c["domain"] for c in materials}), 8)
        self.assertIn("human_review_pending", payload["gold_status"])
        for case in materials:
            self.assertIn(case["primary_family"], case["acceptable_families"])
            self.assertTrue(case["gold_reason"] and case["semantic_traits"] and case["provenance"]["status"])
            self.assertLess(len(case["text"]), 1800)

    def test_tamper_refuses_execution(self):
        raw = bench.read_manifest()
        raw["payload"]["materials"][0]["acceptable_families"] = ["none"]
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            path = Path(folder) / "manifest.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "digest"):
                bench.read_manifest(path)

    def test_canonical_hash_ignores_dict_insertion_order(self):
        self.assertEqual(digest(dict(a=1, b=2)), digest(dict(b=2, a=1)))

    def test_real_production_prompt_without_gold(self):
        prompt = bench.analysis_prompt()
        self.assertIn("learning-content analyst", prompt)
        self.assertNotIn("acceptable_families", prompt)
        self.assertNotIn("primary_family", prompt)


class RunnerTests(unittest.TestCase):
    def client(self, directory, mode="replay", source=None, live=None, remaining=1):
        result = bench.Responses(directory, mode, "offline", dict(remaining=remaining), source, live)
        result.stage = "planner"
        return result

    def test_replay_resume_no_network_and_no_overwrite(self):
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            root = Path(folder)
            source, dest = root / "a", root / "b"
            bench.save(source / "planner.json", dict(raw={"preferred": "none"}, status="completed", paid_this_run=True))
            client = self.client(dest, source=source, live=MagicMock())
            self.assertEqual(json.loads(client.create().output_text), {"preferred": "none"})
            client.live_client.responses.create.assert_not_called()
            self.assertFalse(json.loads((dest / "planner.json").read_text())["paid_this_run"])
            snapshot = (dest / "planner.json").read_bytes()
            client.create()
            self.assertEqual((dest / "planner.json").read_bytes(), snapshot)

    def test_paid_budget_and_raw_persist_before_normalization(self):
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            client = self.client(Path(folder), mode="live", live=MagicMock())
            client.live_client.responses.create.return_value = SimpleNamespace(
                id="fake", status="completed", output_text='{"malformed":true}', usage=None)
            client.create()
            self.assertEqual(json.loads((Path(folder) / "planner.json").read_text())["raw"], {"malformed": True})
            client.stage = "scene"
            with self.assertRaisesRegex(RuntimeError, "budget"):
                client.create()
            self.assertEqual(client.calls, 1)

    def test_local_interaction_guard(self):
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            client = self.client(Path(folder), live=MagicMock())
            client.local_start = 0
            with self.assertRaisesRegex(AssertionError, "local interaction"):
                client.create()
            client.live_client.responses.create.assert_not_called()

    def test_sdk_failure_never_dumps_secret_or_source(self):
        error = ValueError("sk-secret EXAMPLE SOURCE HEADER AUTHORIZATION")
        self.assertEqual(bench.safe_error(error), dict(type="ValueError"))
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            client = self.client(Path(folder), mode="live", live=MagicMock())
            client.live_client.responses.create.side_effect = error
            with self.assertRaises(ValueError):
                client.create()
            saved = (Path(folder) / "planner.json").read_text()
            self.assertNotIn("sk-secret", saved)
            self.assertNotIn("EXAMPLE SOURCE", saved)
            self.assertIn('"paid_this_run": true', saved)

    def test_missing_replay_is_unmeasured_not_synthetic_success(self):
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            with self.assertRaises(FileNotFoundError):
                self.client(Path(folder)).create()

    def test_summary_separates_missing_fail_and_local_observation(self):
        totals = bench.summarize([dict(selection_pass=True, failure_category=None, post_compile_api_calls=0),
            dict(selection_pass=False, failure_category="P1", post_compile_api_calls=None),
            dict(selection_pass=None, failure_category="P3", post_compile_api_calls=None)])
        self.assertEqual(totals["selection_pass"], {"pass": 1, "fail": 1, "not_evaluated": 1})
        self.assertEqual(totals["local_api_observed_cases"], 1)
        self.assertEqual(totals["post_compile_api_calls"], 0)

    def test_process_probe_uses_actual_reducer(self):
        _, catalog, raw = discrete()
        spec = planner.normalize(raw, catalog, [1], {})
        observed = bench.probe_process(spec["process"])
        self.assertTrue(observed["reset"] and observed["stale_event_rejected"])
        self.assertEqual({r["operation"] for r in observed["operations"]}, {"append", "remove_first"})


def recorded(mid, stage="planner"):
    return json.loads((bench.HOME / "phase_a" / "declarations" / mid / (stage + ".json")).read_text(encoding="utf-8"))["raw"]


class GeneralBoundaryTests(unittest.TestCase):
    def test_comparison_ids_pages_and_reordering(self):
        analysis = dict(comparison=dict(suitable=True, items=[dict(id="choice_a", label="Choice A"), dict(id="choice_b", label="Choice B")],
            criteria=[dict(values=[dict(item_id="choice_a", source_pages=[1, True, -1]), dict(item_id="choice_b", source_pages=[2])])]))
        catalog = semantic_catalog(None, analysis)
        self.assertEqual(set(catalog), {"choice_a", "choice_b"})
        self.assertEqual(catalog["choice_a"]["pages"], [1])
        self.assertEqual(catalog["choice_b"]["pages"], [2])
        analysis["comparison"]["items"].reverse()
        self.assertEqual(catalog, semantic_catalog(None, analysis))
        analysis["comparison"]["items"][0]["label"] = "<script>"
        self.assertNotIn("choice_b", semantic_catalog(None, analysis))

    def test_actual_comparison_only_analysis_now_has_canonical_catalog(self):
        for mid in ("damped_motion", "quadratic_shape", "market_equilibrium"):
            analysis, _, _ = bench.prepare_analysis(recorded(mid, "analysis"))
            catalog = semantic_catalog(None, analysis)
            self.assertEqual(set(catalog), {i["id"] for i in analysis["comparison"]["items"]})
            self.assertTrue(all(v["pages"] == [] for v in catalog.values()))

    def test_concept_fallback_is_stable_only_when_no_structured_ids(self):
        analysis = dict(key_concepts=[dict(concept="One", source_pages=[1]), dict(concept="Two", source_pages=[]),
                                     dict(concept="<img>", source_pages=[99])])
        catalog = semantic_catalog(None, analysis)
        analysis["key_concepts"].reverse()
        self.assertEqual(catalog, semantic_catalog(None, analysis))
        self.assertEqual(len(catalog), 2)
        analysis["comparison"] = dict(suitable=True, items=[dict(id="existing", label="Existing")], criteria=[])
        self.assertEqual(set(semantic_catalog(None, analysis)), {"existing"})

    def test_parameterized_numeric_interaction_needs_no_time(self):
        analysis, _, lab = bench.prepare_analysis(recorded("vector_resultant", "analysis"))
        catalog = semantic_catalog(None, analysis)
        caps = compiler.capabilities(analysis, {}, lab)
        raw = recorded("vector_resultant")
        self.assertFalse(raw["features"]["time_dynamics"])
        spec = planner.normalize(raw, catalog, [], caps)
        self.assertEqual(spec["family"], "dynamic")
        self.assertTrue(spec["adapted"])
        self.assertFalse(spec["degraded"])
        self.assertTrue(bench.probe_lab(lab)["numeric_comparison"])
        raw["features"]["interaction_value"] = False
        self.assertEqual(planner.normalize(raw, catalog, [], caps)["family"], "static")

    def test_numeric_capability_absence_cannot_promise_interaction(self):
        analysis, _, _ = bench.prepare_analysis(recorded("vector_resultant", "analysis"))
        raw = recorded("vector_resultant")
        self.assertEqual(planner.normalize(raw, semantic_catalog(None, analysis), [], dict(graph=True))["family"], "static")
        self.assertFalse(contracts({})["numeric_lab"]["ready"])
        self.assertFalse(contracts({})["numeric_lab"]["time_required"])

    def test_unused_process_fault_isolation_uses_captured_responses(self):
        for mid, family in (("rc_charging", "dynamic"), ("finite_sampling", "static")):
            analysis, _, lab = bench.prepare_analysis(recorded(mid, "analysis"))
            catalog = semantic_catalog(None, analysis)
            spec = planner.normalize(recorded(mid), catalog, [], compiler.capabilities(analysis, {}, lab))
            self.assertEqual(spec["family"], family)
            self.assertIsNone(spec["process"])
            self.assertEqual(spec["recovery_codes"], ["unused_process_omitted"])

    def test_required_invalid_process_semantics_stay_rejected(self):
        for mid in ("future_lifecycle", "recursive_calls"):
            analysis, _, lab = bench.prepare_analysis(recorded(mid, "analysis"))
            with self.assertRaises(ValueError):
                planner.normalize(recorded(mid), semantic_catalog(None, analysis), [], compiler.capabilities(analysis, {}, lab))

    def test_unused_process_cannot_hide_security_or_workload_violations(self):
        analysis, _, lab = bench.prepare_analysis(recorded("rc_charging", "analysis"))
        raw = recorded("rc_charging")
        catalog = semantic_catalog(None, analysis)
        caps = compiler.capabilities(analysis, {}, lab)
        mutations = [lambda r: r["process"]["transitions"][0].update(operation="eval"),
            lambda r: r["process"]["states"][0].update(label="<script>"),
            lambda r: r["process"]["states"][0].update(initial="x" * 65),
            lambda r: r["process"].update(states=r["process"]["states"] * 3),
            lambda r: r["process"]["states"][0].update(callback="execute"),
            lambda r: r.update(focus_ids=["unknown"]), lambda r: r.update(source_pages=[1])]
        for mutation in mutations:
            candidate = copy.deepcopy(raw)
            mutation(candidate)
            with self.assertRaises(ValueError):
                planner.normalize(candidate, catalog, [], caps)

    def test_capability_contracts_cache_revision_and_language(self):
        analysis, _, lab = bench.prepare_analysis(recorded("vector_resultant", "analysis"))
        analysis["analysis_language"] = "zh-TW"
        catalog = semantic_catalog(None, analysis)
        caps = compiler.capabilities(analysis, {}, lab)
        source = dict(kind="text", source_text="Original source")
        data = compiler.context(analysis, source, catalog, [], caps, None)
        self.assertTrue(data["runtime_contracts"]["numeric_lab"]["ready"])
        self.assertFalse(data["runtime_contracts"]["numeric_lab"]["time_required"])
        self.assertEqual(data["analysis_language"], "zh-TW")
        before = compiler.identity("m", "zh-TW", source, catalog, caps, None)
        with patch("learning_world.compiler.POLICY_REVISION", "new-policy"):
            self.assertNotEqual(before, compiler.identity("m", "zh-TW", source, catalog, caps, None))

    def test_labels_are_not_routes_and_no_topic_conditions(self):
        import ast
        raw = recorded("vector_resultant")
        analysis, _, lab = bench.prepare_analysis(recorded("vector_resultant", "analysis"))
        catalog = semantic_catalog(None, analysis)
        caps = compiler.capabilities(analysis, {}, lab)
        before = planner.normalize(raw, catalog, [], caps)["family"]
        for item in catalog.values():
            item["label"] = "mitosis supply recursion feedback ohm queue projectile"
        self.assertEqual(planner.normalize(raw, catalog, [], caps)["family"], before)
        topics = {"queue", "ohm", "projectile", "phase", "probability", "recursion", "supply", "mitosis", "feedback"}
        for file in (bench.ROOT / "learning_world").glob("*.py"):
            tree = ast.parse(file.read_text(encoding="utf-8"))
            for condition in [n.test for n in ast.walk(tree) if isinstance(n, (ast.If, ast.IfExp, ast.While))]:
                self.assertFalse({n.value.lower() for n in ast.walk(condition) if isinstance(n, ast.Constant) and isinstance(n.value, str)} & topics)


class ProductIntegrationTests(unittest.TestCase):
    def app(self, mid, source=None, pages=None, pdf=None, cached=True):
        from streamlit.testing.v1 import AppTest
        from day22_fixtures import plan
        from source_lens import new_source_state
        case = next(c for c in bench.read_manifest()["payload"]["materials"] if c["material_id"] == mid)
        raw_analysis = recorded(mid, "analysis")
        pages = pages or []
        if pages:
            def assign_refs(value):
                if isinstance(value, dict):
                    for k, v in value.items():
                        if k == "source_pages":
                            value[k] = list(pages)
                        else:
                            assign_refs(v)
                elif isinstance(value, list):
                    for item in value:
                        assign_refs(item)
            assign_refs(raw_analysis)
        raw_analysis["analysis_language"] = "en"
        if pages:
            h = bench.HELPERS or bench.load_app_helpers()
            analysis = copy.deepcopy(raw_analysis)
            for group in ("concept_map", "visual_flow", "comparison"):
                analysis[group] = h["clean_" + group](raw_analysis.get(group), pages)
            path = h["clean_learning_path"](raw_analysis["learning_path"], pages, "comparison", analysis["comparison"])
            lab = bench.clean_interactive_lab(raw_analysis.get("interactive_lab"), pages, path, h["valid_source_pages"])
        else:
            analysis, path, lab = bench.prepare_analysis(raw_analysis)
        source = source or dict(kind="text", source_text=case["text"], page_texts={})
        catalog = semantic_catalog(None, analysis)
        caps = compiler.capabilities(analysis, {}, lab)
        store = compiler.ensure({}, "m")
        key = compiler.identity("m", "en", source, catalog, caps, None)
        if mid in ("damped_motion", "quadratic_shape", "market_equilibrium"):
            raw = plan("dynamic", list(catalog), ["equations", "continuous_parameters", "structure", "interaction_value"], pages=pages)
        else:
            raw = recorded(mid)
            raw["source_pages"] = list(pages)
        if cached:
            store["cache"][key] = planner.normalize(raw, catalog, pages, caps)
            store["active"] = key
        at = AppTest.from_file(str(bench.ROOT / "app.py"), default_timeout=40)
        at.secrets["OPENAI_API_KEY"] = "offline"
        data = dict(analysis=raw_analysis, analysis_id="m", source_context=source, allowed_source_pages=pages,
                    product_language="en", learning_world_plans=store,
                    learning_workspace=dict(material_id="m", mode="explore", focus=None, representation="formal"))
        if pdf:
            data["learning_canvas"] = dict(material_id="m", selected_id=None, kind=None, component=None,
                style_signature=None, last_event=-1, fallback=False, component_error=False, source=new_source_state("m", pdf))
        for k, v in data.items():
            at.session_state[k] = v
        return at, raw, catalog

    def test_comparison_numeric_controls_round_trip_zero_requests(self):
        with patch("openai.resources.responses.responses.Responses.create", side_effect=AssertionError("unexpected paid request")) as api:
            at, _, catalog = self.app("quadratic_shape")
            at.run()
            self.assertFalse(at.exception)
            self.assertTrue(at.slider)
            slider = at.slider[0]
            slider.set_value(slider.max if slider.value != slider.max else slider.min).run()
            before = copy.deepcopy(at.session_state["interactive_lab_state"])
            focus = next(iter(catalog))
            at.session_state["learning_workspace"]["focus"] = focus
            for mode in ("source", "practice", "learn", "explore"):
                at.radio(key="workspace-mode-m").set_value(mode).run()
                self.assertFalse(at.exception)
            self.assertEqual(at.session_state["interactive_lab_state"], before)
            self.assertEqual(at.session_state["learning_workspace"]["focus"], focus)
            self.assertEqual(api.call_count, 0)

    def test_explicit_comparison_plan_has_catalog_and_one_request(self):
        at, raw, catalog = self.app("damped_motion", cached=False)
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run()
            self.assertFalse(at.button(key="world-plan-m").disabled)
            self.assertEqual(api.call_count, 0)
            at.button(key="world-plan-m").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)
            request_context = json.loads(api.call_args.kwargs["input"])
            self.assertEqual(set(request_context["catalog"]), set(catalog))
            self.assertTrue(request_context["runtime_contracts"]["numeric_lab"]["ready"])
            at.run()
            self.assertEqual(api.call_count, 1)

    def test_normal_pdf_comparison_cta_source_and_page_whitelist(self):
        import io
        import textwrap
        import fitz
        text = next(c["text"] for c in bench.read_manifest()["payload"]["materials"] if c["material_id"] == "damped_motion")
        document = fitz.open()
        page = document.new_page()
        page.insert_text((36, 36), "\n".join(textwrap.wrap(text, 85)), fontsize=9)
        pdf = document.tobytes()
        document.close()
        extracted = (bench.HELPERS or bench.load_app_helpers())["extract_pdf_text"](io.BytesIO(pdf))
        source = dict(kind="pdf", source_text="", page_texts=extracted["analyzed_page_texts"])
        at, raw, catalog = self.app("damped_motion", source, [1], pdf, cached=False)
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run()
            self.assertFalse(at.exception)
            at.button(key="world-plan-m").click().run()
            self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)
            context = json.loads(api.call_args.kwargs["input"])
            self.assertEqual(context["allowed_pages"], [1])
            self.assertTrue(all(v["pages"] == [1] for v in context["catalog"].values()))
            at.radio(key="workspace-mode-m").set_value("source").run()
            self.assertFalse(at.exception)
            at.radio(key="workspace-mode-m").set_value("explore").run()
            self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)

    def test_required_process_failure_preserves_product_learning(self):
        at, raw, _ = self.app("future_lifecycle", cached=False)
        with patch("openai.resources.responses.responses.Responses.create", return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run()
            at.button(key="world-plan-m").click().run()
            self.assertFalse(at.exception)
            self.assertIn("pending", str(at.session_state["source_context"]).lower())
            self.assertTrue(at.session_state["analysis"]["quick_summary"])
            self.assertTrue(at.session_state["learning_world_plans"]["pending"])
            for mode in ("learn", "source", "practice", "explore"):
                at.radio(key="workspace-mode-m").set_value(mode).run()
                self.assertFalse(at.exception)
            self.assertEqual(api.call_count, 1)


class SemanticReviewTests(unittest.TestCase):
    def test_source_equations_and_actual_operations(self):
        import day23_review
        self.assertEqual(len(day23_review.numeric_checks()), 6)
        self.assertEqual(len(day23_review.process_checks()), 3)

    def test_misleading_recursion_is_not_promoted_to_meaningful_success(self):
        import day23_review
        example = day23_review.recursion_counterexample()
        self.assertTrue(example["mechanical_runtime_pass"])
        self.assertFalse(example["meaningful_runtime_pass"])
        self.assertEqual(example["failure_category"], "R3")

    def test_ready_numeric_lab_does_not_require_optional_spatial_request(self):
        with tempfile.TemporaryDirectory(dir=bench.ROOT) as folder:
            mid = "damped_motion"
            case = next(c for c in bench.read_manifest()["payload"]["materials"] if c["material_id"] == mid)
            source = bench.HOME / "phase_b" / "declarations" / mid
            client = bench.Responses(Path(folder), "replay", "offline", dict(remaining=0), source, MagicMock())
            result = bench.evaluate(case, client)
            self.assertTrue(result["compilation_pass"] and result["runtime_pass"])
            self.assertFalse((Path(folder) / "scene.json").exists())
            client.live_client.responses.create.assert_not_called()

    def test_recorded_product_three_cases_run_with_no_requests(self):
        from streamlit.testing.v1 import AppTest
        with patch("openai.resources.responses.responses.Responses.create", side_effect=AssertionError("unexpected API")) as api:
            for mid in ("rc_charging", "future_lifecycle", "byte_definition"):
                at = AppTest.from_file(str(bench.ROOT / "tests/manual_day23.py"), default_timeout=40)
                # Fresh sessions avoid AppTest's stale widget-tree serialization
                # across scripts that replace the active material in the sidebar.
                at.session_state["day23-recorded-selector"] = mid
                at.run()
                self.assertFalse(at.exception)
                if mid == "future_lifecycle":
                    next(b for b in at.button if b.label == "Start").click().run()
                    self.assertTrue(next(b for b in at.button if b.label == "Cancel").disabled)
                elif mid == "rc_charging":
                    self.assertTrue(at.slider)
                else:
                    self.assertFalse(at.slider)
            self.assertEqual(api.call_count, 0)


if __name__ == "__main__":
    unittest.main()
