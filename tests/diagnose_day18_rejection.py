"""Offline audit of the captured public-text response; never repairs app data."""

import copy
import json
from pathlib import Path
import re

from scene.validator import normalize_scene
from scene.world.schema import VERSION


def main():
    raw = json.loads((Path(__file__).parent/"fixtures/day18_three_phase_rejected.json").read_text(encoding="utf-8"))["raw"]
    raw = copy.deepcopy(raw)
    # Preserve the captured file verbatim; audit its semantics under the current
    # contract after the cache/schema revision, rather than stopping at version.
    raw["scene_version"] = VERSION
    def check(stage):
        try:
            normalize_scene(raw, [])
            print(stage + ": accepted")
        except ValueError as error:
            print(stage + ": " + str(error))
    check("original")
    for q in raw["quantities"]:
        q["expression"] = re.sub(r"\bt\b", "time", q["expression"])
    check("canonical time corrected in audit only")
    raw["inverse_bindings"][0]["rate_expression"] = "2*pi*f"
    check("inverse parameter-only rate corrected in audit only")
    for experiment in raw["experiments"]:
        for step in experiment["steps"]:
            if step["op"] == "set_focus" and step["target_id"] == "resultant_field": step["target_id"] = "bmag"
    check("recipe quantity focus corrected in audit only")
    raw["axes"].update(x_min=-16, x_max=16, y_min=-16, y_max=16)
    check("axes cover maximum legal amplitude in audit only")


if __name__ == "__main__": main()
