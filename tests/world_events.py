"""AppTest events through the production boundary, replacing retired widgets."""
from unittest.mock import patch
from scene.world import runtime


def world_event(app, kind, **data):
    wrapper = app.session_state["learning_scene_state"]
    state = wrapper["world"]
    event = dict(scene=runtime.scene_identity(wrapper["scene"]),
                 revision=state["revision"], token="test-local-"+str(state["revision"]),
                 kind=kind, **data)
    with patch.object(runtime, "_component", return_value=event): app.run()
    if app.exception: raise AssertionError(str(app.exception))


def world_patch(app, op, target, value):
    world_event(app, "patch", patch=dict(op=op, target_id=target, value=value))
