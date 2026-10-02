"""Reproducible bounded local timing evidence, without an API or browser."""

import json
import statistics
import time
from unittest.mock import patch

from scene.world.engine import frames
from scene.world.runtime import payload
from scene.world.state import new_state
from scene.world.validator import normalize_world
from .world_fixtures import projectile_world, three_phase_world


def main():
    results = []
    for factory in (three_phase_world, projectile_world):
        scene = normalize_world(factory(), [1])
        state = new_state(scene)
        timings = []
        for _ in range(5):
            start = time.perf_counter()
            frames(scene, state["parameters"])
            timings.append(time.perf_counter()-start)
        wrapper = dict(world=state, material_id="offline-metrics")
        with patch("scene.world.runtime.tr", side_effect=lambda key: key): payload(scene, wrapper)
        results.append(dict(title=scene["title"], frames=scene["time"]["frames"], objects=len(scene["objects"]),
                            forward_bindings=len(scene["bindings"]), inverse_bindings=len(scene["inverse_bindings"]),
                            validation=scene["validation_report"], frame_median_ms=1000*statistics.median(timings),
                            payload=wrapper["world_timings"]))
    print(json.dumps(results, indent=2))


if __name__ == "__main__": main()
