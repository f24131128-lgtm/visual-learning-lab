"""Local navigation to existing controls, using exact representation ownership."""
from representation_contract import registrations
from quantity_contract import can_commit


def linked_control_demo(lab, catalog, material, allowed, focus):
    if not isinstance(focus, str) or focus not in catalog:
        return None
    matches = [demo for demo in (lab or {}).get("demos", [])
               if registrations(demo, catalog, material, allowed).get(focus)
               and any(can_commit(p) for p in demo["parameters"])]
    # Ambiguous owners need a choice; do not pick an arbitrary first demo.
    return matches[0] if len(matches) == 1 else None


def active_control_demo(workspace, lab, catalog, allowed, focus):
    demo = linked_control_demo(lab, catalog, workspace["material_id"], allowed, focus)
    if (demo and workspace.get("control_focus_id") == focus
            and workspace.get("control_demo_id") == demo["id"]):
        return demo
    return None


def open_controls(workspace, lab, catalog, allowed, focus, wrapper=None):
    from .state import open_workspace
    demo = linked_control_demo(lab, catalog, workspace["material_id"], allowed, focus)
    if not demo or not open_workspace(workspace, "explore", focus, catalog, wrapper):
        return False
    workspace.update(representation="formal", control_demo_id=demo["id"], control_focus_id=focus)
    return True
