"""Phase C tests; initial failures recorded before contract implementation."""
import copy
import json
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from phase_c_fixtures import catalog, execution, equal_labels, fixed_world, malformed_shapes
from scene.validator import normalize_scene
from scene.world.validator import normalize_world


class FrozenRegressionShapes(unittest.TestCase):
    def test_duplicate_labels_preserve_formal_identity(self):
        scene = normalize_scene(equal_labels(), [1, 2])
        self.assertEqual({t["id"] for t in scene["focus_targets"]}, {"focus_e", "focus_union"})
        self.assertEqual([t["source_pages"] for t in scene["focus_targets"]], [[2], [1]])

    def test_zero_width_source_value_is_fixed_not_an_invented_range(self):
        scene = normalize_world(fixed_world(), [1])
        self.assertEqual(scene["parameters"][0]["parameter_kind"], "fixed")
        self.assertEqual((scene["parameters"][0]["min"], scene["parameters"][0]["max"]), (2, 2))

    def test_invalid_fixed_value_still_rejected(self):
        raw = fixed_world(); raw["parameters"][0]["default"] = 3
        with self.assertRaises(ValueError): normalize_world(raw, [1])

    def test_recursive_and_nonidentical_nested_call_return_contract(self):
        from learning_world import execution as engine
        for raw, expected in ((execution(), 6), (execution(True), 10)):
            spec = engine.normalize(raw, catalog(), list(catalog()))
            state = engine.initial(spec)
            for _ in range(24):
                if engine.enabled(spec, state, "call"): op = "call"
                elif engine.enabled(spec, state, "complete"): op = "complete"
                elif engine.enabled(spec, state, "return"): op = "return"
                else: break
                state, _ = engine.apply(spec, state, engine.event(spec, state, op))
            self.assertEqual(state["frames"][0]["result"], expected)
            self.assertEqual(state["frames"][0]["status"], "completed")
            self.assertTrue(engine.valid(spec, state))

    def test_early_return_wrong_caller_and_cycles_are_rejected(self):
        from learning_world import execution as engine
        spec = engine.normalize(execution(), catalog(), list(catalog()))
        state = engine.initial(spec)
        self.assertIsNone(engine.apply(spec, state, engine.event(spec, state, "return")))
        child, _ = engine.apply(spec, state, engine.event(spec, state, "call"))
        while engine.enabled(spec, child, "call"):
            child, _ = engine.apply(spec, child, engine.event(spec, child, "call"))
        child, _ = engine.apply(spec, child, engine.event(spec, child, "complete"))
        wrong = engine.event(spec, child, "return"); wrong["destination"] = "unrelated"
        self.assertIsNone(engine.apply(spec, child, wrong))
        with self.assertRaises(ValueError): engine.normalize(malformed_shapes()["cycle"], catalog(), list(catalog()))

    def test_unused_process_recovery_remains(self):
        from day23_benchmark import prepare_analysis
        from learning_world import planner, compiler
        from source_atlas.model import semantic_catalog
        root=Path(__file__).resolve().parents[1]/"docs/day23/phase_a/declarations/rc_charging"
        analysis, _, lab=prepare_analysis(json.loads((root/"analysis.json").read_text(encoding="utf-8"))["raw"])
        raw=json.loads((root/"planner.json").read_text(encoding="utf-8"))["raw"]
        plan=planner.normalize(raw, semantic_catalog(None,analysis), [], compiler.capabilities(analysis,{},lab))
        self.assertEqual(plan["family"], "dynamic")


class ContractSecurityTests(unittest.TestCase):
    def test_phase_c_frozen_gold_and_runner_execution_probe(self):
        from day23_phase_c_benchmark import manifest,probe_execution
        from learning_world import execution as engine
        self.assertEqual(len(manifest()["payload"]["materials"]),7)
        spec=engine.normalize(execution(True),catalog(),list(catalog()))
        self.assertEqual(probe_execution(spec,dict(root_result=10,call_count=2))["root_result"],10)
        with self.assertRaises(AssertionError):probe_execution(spec,dict(root_result=11,call_count=2))
    def test_depth_counts_cycles_unknown_references_and_executable_syntax(self):
        from learning_world import execution as engine
        cases=[]
        for expression in ("__import__('os')", "n.real", "n[0]", "lambda:1", "open(n)", "10**1000"):
            raw=execution(); raw["calls"][-1]["result_expression"]=expression; cases.append(raw)
        raw=execution(); raw["calls"][0]["semantic_id"]="unknown"; cases.append(raw)
        raw=execution(); raw["calls"][0]["arguments"][0]["value"]=True; cases.append(raw)
        raw=execution(); raw["calls"][0]["arguments"][0]["value"]=float("nan"); cases.append(raw)
        raw=execution(); raw["calls"][0]["children"][0]["call_id"]="missing"; cases.append(raw)
        raw=execution(); raw["calls"].append(copy.deepcopy(raw["calls"][0])); cases.append(raw)
        raw=execution(); raw["calls"]*=7; cases.append(raw)
        raw=execution(); raw["calls"]=[copy.deepcopy(raw["calls"][0]) for _ in range(9)]
        for i,c in enumerate(raw["calls"]):
            c["id"]=f"c{i}"; c["children"]=[dict(c["children"][0],call_id=f"c{i+1}")] if i<8 else []
            if i==8: c["result_expression"]="1"
        raw["root_id"]="c0"; cases.append(raw)
        for raw in cases:
            with self.subTest(raw=raw):
                with self.assertRaises((ValueError, TypeError)): engine.normalize(raw,catalog(),list(catalog()))

    def test_forged_state_stale_duplicate_events_and_reset(self):
        from learning_world import execution as engine
        spec=engine.normalize(execution(True),catalog(),list(catalog()))
        state=engine.initial(spec); event=engine.event(spec,state,"call")
        child,_=engine.apply(spec,state,event)
        self.assertIsNone(engine.apply(spec,child,event))
        forged=copy.deepcopy(child); forged["frames"][0]["status"]="active"
        self.assertFalse(engine.valid(spec,forged))
        forged=copy.deepcopy(child); forged["frames"][-1].update(status="completed",result=999)
        self.assertFalse(engine.valid(spec,forged))
        forged=copy.deepcopy(child); forged["frames"][-1]["caller"]="wrong"
        self.assertFalse(engine.valid(spec,forged))
        forged=copy.deepcopy(child); forged["frames"][-1]["result"]=True
        self.assertFalse(engine.valid(spec,forged))
        restored=engine.reset(spec,child)
        self.assertEqual(restored["frames"],state["frames"])
        self.assertGreater(restored["revision"],child["revision"])
        self.assertIsNone(engine.apply(spec,restored,event))
        event=engine.event(spec,restored,"call"); event["value"]="arbitrary"
        self.assertIsNone(engine.apply(spec,restored,event))

    def test_multiple_children_return_to_distinct_bindings(self):
        from learning_world import execution as engine
        raw=execution(True)
        second=copy.deepcopy(raw["calls"][1]); second["id"]="second"; second["arguments"][0]["value"]=5
        raw["calls"].append(second)
        raw["calls"][0]["children"].append(dict(raw["calls"][0]["children"][0],call_id="second",result_id="other"))
        raw["calls"][0]["result_expression"]="answer+other"
        spec=engine.normalize(raw,catalog(),list(catalog())); state=engine.initial(spec)
        for op in ("call","complete","return","call","complete","return","complete"):
            state,_=engine.apply(spec,state,engine.event(spec,state,op))
        self.assertEqual(state["frames"][0]["returned"],dict(answer=6,other=10))
        self.assertEqual(state["frames"][0]["result"],16)

    def test_optional_annotations_drop_but_bad_core_rejects(self):
        from learning_world import execution as engine
        raw=execution(); raw["annotations"]=[dict(semantic_id="unknown",text="<script>"),dict(semantic_id="base",text="A base call returns directly.")]
        self.assertEqual(len(engine.normalize(raw,catalog(),list(catalog()))["annotations"]),1)
        raw["calls"][0]["return_semantic_id"]="unknown"
        with self.assertRaises(ValueError): engine.normalize(raw,catalog(),list(catalog()))

    def test_fixed_domains_reject_fabricated_change_and_malformed_bounds(self):
        from semantic_contract import numeric_domain
        from scene.world.state import apply_patch,new_state
        from scene.world.policy import normalize_parameter
        for bad in (dict(min=2,max=1,default=2,step=0),dict(min=2,max=2,default=3,step=0),
                    dict(min=2,max=2,default=2,step=-1),dict(min=2,max=2,default=2,step=float("inf"))):
            with self.assertRaises(ValueError): numeric_domain(bad)
        world=normalize_world(fixed_world(),[1]); state=new_state(world)
        with self.assertRaises(ValueError): apply_patch(world,state,dict(op="set_parameter",target_id="scale",value=3))
        raw=fixed_world()["parameters"][0]; raw["range_source"]="semantic_default"
        normalize_parameter(raw); self.assertEqual((raw["min"],raw["max"]),(2,2))
        self.assertEqual(numeric_domain(dict(min=2.,max=2.+1e-10,default=2.,step=1e-11)),"adjustable")

    def test_same_expression_keeps_selected_source_identity(self):
        from scene.renderers import semantic_focus
        raw=equal_labels(); raw["focus_targets"][1]["expression"]="E"
        scene=normalize_scene(raw,[1,2])
        state=dict(selected_focus_id="focus_union",active_expression="E",selected_outcome_id=None)
        self.assertEqual(semantic_focus(scene,state)["source_pages"],[1])

    def test_no_topic_routing_and_unchanged_recorded_b_choices(self):
        import ast
        from day23_benchmark import read_manifest,prepare_analysis
        from learning_world import planner,compiler
        from source_atlas.model import semantic_catalog
        root=Path(__file__).resolve().parents[1]
        for file in ("learning_world/execution.py","learning_world/capabilities.py","semantic_contract.py"):
            tree=ast.parse((root/file).read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node,ast.If):
                    condition=ast.unparse(node.test).lower()
                    self.assertFalse(any(w in condition for w in ("factorial","recursion","damped","supply","mitosis")))
        for case in read_manifest()["payload"]["materials"]:
            directory=root/"docs/day23/phase_b/declarations"/case["material_id"]
            analysis,_,lab=prepare_analysis(json.loads((directory/"analysis.json").read_text(encoding="utf-8"))["raw"])
            plan=planner.normalize(json.loads((directory/"planner.json").read_text(encoding="utf-8"))["raw"],
                semantic_catalog(None,analysis),[],compiler.capabilities(analysis,{},lab))
            self.assertIn(plan["family"],case["acceptable_families"])

    def test_retained_real_candidates_revalidate_separately_from_history(self):
        root=Path(__file__).resolve().parents[1]/"docs/day23/phase_b/declarations"
        finite=json.loads((root/"finite_sampling/scene.json").read_text(encoding="utf-8"))["raw"]
        motion=json.loads((root/"damped_motion/scene.json").read_text(encoding="utf-8"))["raw"]
        # The unchanged recording has another independent required-field error.
        # Do not shorten source/model text or relax bounds to manufacture success.
        with self.assertRaisesRegex(ValueError, "learning goal"): normalize_scene(finite,[])
        with self.assertRaisesRegex(ValueError, "invalid set_time"): normalize_world(motion,[])


class ProductContractTests(unittest.TestCase):
    def test_three_recorded_phase_c_cases_in_production_ui_zero_requests(self):
        from streamlit.testing.v1 import AppTest
        from scene.world.engine import snapshot
        import math
        root=Path(__file__).resolve().parents[1]
        with patch("openai.resources.responses.responses.Responses.create",side_effect=AssertionError("unexpected API")) as api:
            for mid in ("nested_sum","scoped_labels","fixed_decay"):
                at=AppTest.from_file(str(root/"tests/manual_phase_c.py"),default_timeout=45)
                at.session_state["phase-c-review-selector"]=mid;at.run();self.assertFalse(at.exception)
                material="phase-c-review-"+mid
                if mid=="nested_sum":
                    for op in ["Call child"]*4+["Complete current call"]+["Return to caller","Complete current call"]*4:
                        next(b for b in at.button if b.label==op).click().run();self.assertFalse(at.exception)
                    self.assertTrue(any(t.value=="Result: 10" for t in at.text))
                elif mid=="scoped_labels":
                    key="canvas-list-"+material+"-concept_map"
                    for target in ("assembly_ready","inspection_ready"):
                        at.selectbox(key=key).select(target).run();self.assertFalse(at.exception)
                        self.assertEqual(at.session_state["learning_canvas"]["selected_id"],target)
                else:
                    at.slider(key="world-widget-"+material+"-time").set_value(4.).run();self.assertFalse(at.exception)
                    wrapper=at.session_state["learning_scene_state"]
                    self.assertAlmostEqual(snapshot(wrapper["scene"],wrapper["world"])["values"]["magnitude"],4/math.e)
                    self.assertFalse(any("amplitude" in s.key or "decay" in s.key for s in at.slider if not s.key.endswith("-time")))
                for mode in ("source","practice","explore"):
                    at.radio(key="workspace-mode-"+material).set_value(mode).run();self.assertFalse(at.exception)
            self.assertEqual(api.call_count,0)
    def test_fixed_world_frontend_uses_read_only_output(self):
        import subprocess,shutil
        from scene.world.runtime import payload
        from scene.world.state import new_state
        root=Path(__file__).resolve().parents[1]; world=normalize_world(fixed_world(),[1])
        data=payload(world,dict(world=new_state(world),material_id="fixed"))
        result=subprocess.run([shutil.which("node"),str(root/"tests/phase_c_frontend_smoke.cjs"),str(root/"scene/world/frontend/index.html")],input=json.dumps(data),capture_output=True,encoding="utf-8",timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
    def execution_app(self, cached=True):
        from test_day23 import ProductIntegrationTests
        from day22_fixtures import plan
        from learning_world import compiler,planner
        from source_atlas.model import semantic_catalog
        at,_,_=ProductIntegrationTests().app("recursive_calls",cached=False)
        analysis=at.session_state["analysis"]
        analysis["primary_visualization"]["type"]="concept_map"
        analysis["concept_map"]["nodes"]=[dict(id=i,label=v["label"],source_pages=[],role="central" if i=="call" else "primary") for i,v in catalog().items()]
        analysis["concept_map"]["edges"]=[]
        analysis["concept_map"].update(suitable=True,reason="Nested calls and return values.",edges=[dict(source="call",target="base",label="reaches"),dict(source="base",target="return_value",label="returns")])
        clean,_,lab=__import__("day23_benchmark").prepare_analysis(analysis)
        cat=semantic_catalog(None,clean)
        raw=plan("execution",list(cat),["structure","transitions","interaction_value"],pages=[])
        raw["execution"]=execution(True)
        store=compiler.ensure({},"m")
        key=compiler.identity("m","en",at.session_state["source_context"],cat,compiler.capabilities(clean,{},lab),None)
        if cached: store["cache"][key]=planner.normalize(raw,cat,[],compiler.capabilities(clean,{},lab)); store["active"]=key
        at.session_state["learning_world_plans"]=store
        at.session_state["learning_workspace"]["representation"]="execution" if cached else "formal"
        return at,raw

    def test_local_execution_navigation_focus_and_reset_preserve_learning(self):
        from unittest.mock import patch
        with patch("openai.resources.responses.responses.Responses.create",side_effect=AssertionError("unexpected request")) as api:
            at,_=self.execution_app(); at.run(); self.assertFalse(at.exception)
            before=copy.deepcopy(at.session_state["analysis"])
            def button(label): return next(b for b in at.button if b.label==label)
            self.assertTrue(button("Return to caller").disabled)
            self.assertTrue(button("Complete current call").disabled)
            button("Call child").click().run()
            self.assertEqual(at.session_state["learning_workspace"]["focus"],"call")
            button("Complete current call").click().run()
            button("Return to caller").click().run()
            self.assertEqual(at.session_state["learning_workspace"]["focus"],"return_value")
            store=at.session_state["learning_world_plans"]; saved=copy.deepcopy(store["states"][store["active"]])
            for mode in ("source","practice","learn","explore"):
                at.radio(key="workspace-mode-m").set_value(mode).run(); self.assertFalse(at.exception)
            store=at.session_state["learning_world_plans"]
            self.assertEqual(store["states"][store["active"]],saved)
            button("Complete current call").click().run()
            self.assertTrue(any(t.value=="Result: 10" for t in at.text))
            button("Reset execution").click().run()
            self.assertTrue(button("Complete current call").disabled)
            self.assertEqual(at.session_state["analysis"],before)
            self.assertEqual(api.call_count,0)

    def test_one_explicit_execution_compile_and_local_cached_rerun(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        at,raw=self.execution_app(cached=False)
        with patch("openai.resources.responses.responses.Responses.create",return_value=SimpleNamespace(output_text=json.dumps(raw))) as api:
            at.run(); self.assertEqual(api.call_count,0)
            at.button(key="world-plan-m").click().run(); self.assertFalse(at.exception)
            self.assertEqual(api.call_count,1)
            at.run(); self.assertEqual(api.call_count,1)

    def test_fixed_lab_has_read_only_value_no_slider(self):
        from streamlit.testing.v1 import AppTest
        code='''import streamlit as st
from interactive_lab import clean_interactive_lab,render_interactive_lab
from lab_fixtures import lab_fixture,learning_fixture
st.session_state["product_language"]="en"
raw=lab_fixture()
for demo in raw["demos"]:
    for p in demo["parameters"]: p.update(min=p["default"],max=p["default"],step=0)
path=learning_fixture()["learning_path"]
clean=clean_interactive_lab(raw,[1,2],path,lambda pages,allowed:[p for p in pages if p in allowed])
render_interactive_lab(clean,"fixed",path,lambda *args:None,str)
'''
        at=AppTest.from_string(code); at.run()
        self.assertFalse(at.exception); self.assertFalse(at.slider)
        self.assertTrue(any(c.value=="Fixed value" for c in at.caption))
        self.assertTrue(at.get("plotly_chart"))
        from semantic_contract import display_choices
        names=display_choices([dict(id="one",label="Same"),dict(id="two",label="Same")])
        self.assertNotEqual(names["one"],names["two"])


if __name__ == "__main__": unittest.main()
