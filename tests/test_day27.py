"""Domain safety and production request ownership, entirely offline."""
import ast
import copy
import math
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from model_config import MODEL, response_options
from scene.world.policy import declaration_defaults, normalize_parameter
from scene.world.schema import VERSION, WORLD_SCHEMA
from scene.world.state import apply_parameters, new_state
from scene.world.validator import normalize_world
from scene.world.engine import evaluate
from scene.state import cache_key
from world_fixtures import complete_projectile_world


def parameter(domain="positive", **changes):
    return dict(id="arbitrary", label="Unrelated label", quantity_kind="length",
                domain_constraint=domain, min=1., max=10., default=2., step=.1,
                range_source="pedagogical", display_unit="native", unit="m",
                source_pages=[], **changes)


class DomainTests(unittest.TestCase):
    def test_zero_nonnegative_height(self):
        p=parameter("non_negative"); p.update(min=0., default=0.)
        self.assertEqual(normalize_parameter(p)["default"], 0.)

    def test_zero_positive_radius_and_wavelength(self):
        for identifier in ("radius", "wavelength", "unrelated"):
            for field in ("min", "max", "default"):
                p=parameter(); p.update(id=identifier); p[field]=0.
                with self.assertRaises(ValueError): normalize_parameter(p)

    def test_signed_negative_displacement(self):
        p=parameter("signed"); p.update(min=-10., default=-2.)
        self.assertEqual(normalize_parameter(p)["default"], -2.)

    def test_negative_nonnegative_length(self):
        for source in ("source", "pedagogical", "semantic_default"):
            p=parameter("non_negative"); p.update(min=-1., range_source=source)
            with self.assertRaises(ValueError): normalize_parameter(p)

    def test_positive_speed_frequency_still_strict(self):
        for kind in ("speed", "frequency", "acceleration"):
            for domain in ("positive", "non_negative", "signed"):
                p=parameter(domain); p.update(quantity_kind=kind, min=0.)
                with self.assertRaises(ValueError): normalize_parameter(p)

    def test_nonfinite_and_malformed_ranges(self):
        for changes in (dict(min=float("nan")), dict(max=float("inf")),
                        dict(default=float("-inf")), dict(min=11.), dict(step=0.),
                        dict(default=11.), dict(domain_constraint="anything")):
            p=parameter(); p.update(changes)
            with self.assertRaises(ValueError): normalize_parameter(p)

    def test_runtime_domain_violation_atomic_even_if_bounds_tampered(self):
        scene=normalize_world(complete_projectile_world(), [1]); state=new_state(scene)
        p=scene["parameters"][0]; p.update(domain_constraint="positive", min=0.)
        before=copy.deepcopy(state)
        with self.assertRaises(ValueError):
            apply_parameters(scene, state, {p["id"]: 0.}, state["focus"])
        self.assertEqual(state, before)
        values=dict(state["parameters"]); values[p["id"]]=0.
        with self.assertRaises(ValueError): evaluate(scene, values, 0.)

    def test_semantic_fallback_domains(self):
        for domain, baseline in (("positive", 2.), ("non_negative", 0.), ("signed", -2.)):
            p=parameter(domain); p.update(range_source="semantic_default", min=-10. if domain=="signed" else 0. if domain=="non_negative" else 1., default=baseline)
            normalize_parameter(p)
            self.assertLess(p["min"], p["max"])
            if domain=="positive": self.assertGreater(p["min"], 0.)
            if domain=="non_negative": self.assertGreaterEqual(p["min"], 0.)
            self.assertLessEqual(p["min"], baseline)
            self.assertGreaterEqual(p["max"], baseline)

    def test_legacy_defaults_conservative_and_strict_version_invalidates_cache(self):
        raw=complete_projectile_world()
        p=raw["parameters"][0]; p.pop("domain_constraint", None); p.update(quantity_kind="length", min=0.)
        self.assertEqual(declaration_defaults(raw)["parameters"][0]["domain_constraint"], "positive")
        with self.assertRaises(ValueError): normalize_world(raw, [1])
        raw=complete_projectile_world(); raw["scene_version"]="2.2"
        with self.assertRaises(ValueError): normalize_world(raw, [1])
        self.assertEqual(cache_key("m", "en", "spatial_dynamics")[2], VERSION)
        self.assertEqual(WORLD_SCHEMA["properties"]["parameters"]["items"]["properties"]["domain_constraint"]["enum"], ["positive", "non_negative", "signed"])


class ProductionModelTests(unittest.TestCase):
    def test_all_eight_request_sites_use_owned_configuration(self):
        root=Path(__file__).resolve().parents[1]; sites=[]
        for name in ("app.py", "scene/compiler.py", "source_atlas/compiler.py", "learning_world/compiler.py", "analogy/compiler.py", "dynamic_simulation.py"):
            tree=ast.parse((root/name).read_text(encoding="utf-8-sig"))
            for call in ast.walk(tree):
                if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute) and call.func.attr=="create" and isinstance(call.func.value, ast.Attribute) and call.func.value.attr=="responses":
                    options=[kw.value for kw in call.keywords if kw.arg is None]
                    self.assertTrue(any(isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id=="response_options" for v in options), name)
                    self.assertFalse(any(kw.arg in ("model", "reasoning") for kw in call.keywords), name)
                    sites.append(name)
        self.assertEqual(len(sites), 8)
        self.assertEqual(response_options(), {"model":"gpt-6.1-sol", "reasoning":{"effort":"medium"}})
        opts=response_options(); opts["reasoning"]["effort"]="none"
        self.assertEqual(response_options()["reasoning"]["effort"], "medium")

    def test_scene_and_simulation_ignore_obsolete_caller_model(self):
        from scene.compiler import request_scene
        from dynamic_simulation import request_simulation
        from analogy.compiler import request
        client=MagicMock(); client.responses.create.return_value=SimpleNamespace(output_text="{}", status="completed", output=[])
        for function, data in ((request_scene, {"domain":"spatial_dynamics", "analysis_language":"en"}),
                               (request_simulation, {"analysis_language":"en"}), (request, {"analysis_language":"en"})):
            function(client, "obsolete-model", data)
            options=client.responses.create.call_args.kwargs
            self.assertEqual(options["model"], MODEL)
            self.assertEqual(options["reasoning"], {"effort":"medium"})
            self.assertTrue(options["text"]["format"]["strict"])


if __name__=="__main__": unittest.main()
