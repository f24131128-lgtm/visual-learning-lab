"""Bounded token wrapping and exact geometry diagnostics; no paid requests.

The third live download proves geometry_bounds after semantic/blank-slot checks.
It does not retain expressions, wrap flags, time or numeric ranges. The moving
token inputs below are synthetic regressions, not the recovered live declaration.
"""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import numpy as np
from analogy import compiler, engine, state
from analogy.diagnostics import Rejection, record, summary
from analogy.validator import normalize
from analogy_fixtures import formal, spec


class GeometryTests(unittest.TestCase):
    def setUp(self):
        scene,self.catalog=formal("electricity")
        self.registry=state.parameter_registry({"scene":scene},{},None,self.catalog)
        self.raw=spec("electricity")
        self.raw["primitives"][2]["x"]="30*speed*time+index*.7"

    def normalize(self,raw=None):
        return normalize(raw or self.raw,self.catalog,self.registry,[1],"voltage")

    def test_raw_travel_beyond_viewport_wraps_into_the_unchanged_bounded_geometry(self):
        result=self.normalize()
        for level,tightness in ((5.,2.),(1.,10.),(10.,1.)):
            data=engine.project(result,{"level":level,"tightness":tightness})
            for obj in (o for o in data["objects"] if o["type"]=="tokens"):
                actual=np.array(obj["data"]["x"])
                expected=-1.+np.remainder(30*level/tightness*np.array(data["times"])+obj["index"]*.7+1.,6.)
                np.testing.assert_allclose(actual,expected)
                self.assertTrue(np.all(actual>=-1.)); self.assertTrue(np.all(actual<5.))
        self.assertGreater(30*10*result["time"]["duration"],100.)
        self.assertEqual(result["mappings"],self.raw["mappings"])

    def test_nonwrapped_oversized_position_is_still_fatal_with_exact_field_and_range(self):
        raw=copy.deepcopy(self.raw); raw["primitives"][2]["wrap_x"]=False
        with self.assertRaises(Rejection) as failure: self.normalize(raw)
        error=failure.exception
        self.assertEqual((error.code,error.path),("geometry_bounds","$.primitives[2].x"))
        self.assertFalse(error.detail["wrap_x"])
        self.assertEqual(error.detail["check_stage"],"rendered_geometry")
        self.assertGreater(error.detail["observed_max"],error.detail["limit_max"])

    def test_wrap_does_not_hide_unsafe_math_or_excessive_raw_arithmetic(self):
        for expression,code in (("2000*time","projection_bounds"),("__import__('os')","unsafe_expression"),("1/0","numeric_expression")):
            raw=copy.deepcopy(self.raw); raw["primitives"][2]["x"]=expression
            with self.subTest(expression=expression),self.assertRaises(Rejection) as failure: self.normalize(raw)
            self.assertEqual(failure.exception.code,code)
            self.assertEqual(failure.exception.path,"$.primitives[2].x")

    def test_other_geometry_and_wrap_interval_limits_are_not_relaxed(self):
        for field,value in (("y","101"),("x2","101"),("y2","-101"),("radius","21"),("radius","-1")):
            raw=copy.deepcopy(self.raw); raw["primitives"][2][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(Rejection) as failure: self.normalize(raw)
            self.assertEqual(failure.exception.code,"geometry_bounds")
            self.assertEqual(failure.exception.path,"$.primitives[2]."+field)
        for changes in (dict(wrap_max=101.),dict(wrap_min=2.,wrap_max=1.),dict(type="disc",count=1)):
            raw=copy.deepcopy(self.raw); raw["primitives"][2].update(changes)
            with self.subTest(changes=changes),self.assertRaises(Rejection): self.normalize(raw)

    def test_bounds_diagnostics_keep_numeric_evidence_without_expression_or_source(self):
        raw=copy.deepcopy(self.raw); raw["primitives"][2]["wrap_x"]=False
        try: self.normalize(raw)
        except Rejection as error:
            store=state.ensure({},"m","zh-TW","sig")
            with self.assertLogs("analogy.diagnostics",level="WARNING") as logs:
                trace=record(store,"key","normalize",error,raw)
        self.assertEqual(trace["detail"]["field"],"x")
        self.assertEqual(trace["detail"]["limit_max"],100.)
        self.assertGreater(trace["detail"]["observed_max"],100.)
        self.assertNotIn("30*speed*time",json.dumps(trace))
        self.assertNotIn("30*speed*time"," ".join(logs.output))
        self.assertTrue(any("wrap_x=False" in line for line in logs.output))
        self.assertEqual(summary(raw)["primitives"][2]["wrap_x"],False)
        self.assertEqual(summary(raw)["time"],raw["time"])

    def test_saved_failed_candidate_rechecks_locally_without_another_model_response(self):
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text=json.dumps(self.raw))
        store=state.ensure({},"m","zh-TW","sig"); key=state.identity("m","zh-TW","sig","voltage")
        with patch.object(compiler,"normalize",side_effect=Rejection("geometry_bounds","$.primitives")):
            self.assertIsNone(compiler.build(store,key,client,"offline",{"analysis_language":"zh-TW"},self.catalog,self.registry,[1]))
        result=compiler.build(store,key,None,"offline",None,self.catalog,self.registry,[1])
        self.assertTrue(result["suitable"]); self.assertFalse(store["pending"])
        self.assertEqual(client.responses.create.call_count,1)

    def test_captured_third_trace_passed_core_and_blank_radius_checks_only(self):
        trace=json.loads((Path(__file__).parent/"fixtures/day21_analogy_geometry_rejection.json").read_text(encoding="utf-8"))
        self.assertEqual((trace["stage"],trace["code"]),("normalize","geometry_bounds"))
        self.assertEqual(trace["generated"]["selected_candidate"],"water_channel")
        self.assertTrue(trace["normalized"]["suitable"])
        self.assertEqual(len(trace["normalized"]["mappings"]),8)
        self.assertTrue(any(r["path"]=="$.primitives[0].radius" and r["code"]=="unused_visual_default" for r in trace["recoveries"]))
        self.assertNotIn("wrap_x",trace["generated"]["primitives"][1])
        self.assertNotIn("detail",trace)


if __name__=="__main__": unittest.main()
