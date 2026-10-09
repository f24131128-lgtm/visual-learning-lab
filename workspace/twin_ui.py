"""Compact source/current inspector within the existing Workspace."""
import streamlit as st
from html import escape

from i18n import tr
from manipulation import lab as direct_lab, world as direct_world
from source_atlas.compiler import source_for
from source_atlas.state import cache_key, sync_region, optional_scene
from .grounded_twin import comparison_rows, derive_links
from .state import get_workspace_focus, open_workspace

KINDS = {"native_geometry": "Native text geometry · meaning remains estimated",
         "estimated_region": "Estimated visual region", "page_only": "Page-level support only"}


def context(material, analysis, wrapper, catalog, lab, path, allowed):
    """Derive from current validated owners only; never read iframe targets."""
    atlas_state = st.session_state.get("source_atlas_state")
    source = source_for(material)
    if not atlas_state or not source or not atlas_state.get("atlas"): return None
    scene = optional_scene(wrapper)
    bounded_catalog = {i: v | {"pages": [p for p in v["pages"] if p in allowed]} for i, v in catalog.items()}
    key = cache_key(material, source["pdf_bytes"], analysis["analysis_language"],
                    atlas_state["atlas"]["processed_pages"], scene, bounded_catalog)
    targets, reps, owners = [], {}, {}
    if scene and scene["domain"] == "spatial_dynamics":
        from scene.world.state import new_state
        world = wrapper.setdefault("world", new_state(scene))
        targets = direct_world.targets(scene, world)
        for target in targets: owners[target["id"]] = (scene["parameters"], world["parameters"], None)
    else:
        saved = st.session_state.get("interactive_lab_state", {})
        if saved.get("material_id") == material:
            for demo in (lab or {}).get("demos", []):
                semantic = direct_lab.semantic_target(demo, path, catalog, analysis)
                values = saved["demos"][demo["id"]]["values"]
                ts = direct_lab.targets(demo, values, semantic)
                targets.extend(ts)
                if semantic:
                    reps.setdefault(semantic, []).extend(dict(id=r["id"]) for r in demo["series"] + demo["derived_metrics"])
                for target in ts: owners[target["id"]] = (demo["parameters"], values, demo["id"])
    links = derive_links(atlas_state, material, allowed, catalog, targets, reps,
                         atlas_state.get("document_model"), key)
    return dict(links=links, targets=targets, owners=owners, state=atlas_state)


def render_grounded_twin(workspace, analysis, wrapper, catalog, lab, path, allowed):
    try:
        data = context(workspace["material_id"], analysis, wrapper, catalog, lab, path, allowed)
        if not data or not data["links"]: return
        focus = get_workspace_focus(workspace, wrapper)
        selected = sync_region(data["state"], focus)
        link = data["links"].get(focus)
        if not link or selected and focus not in selected["semantic_ids"]: return
        with st.container():
            st.markdown('<div class="vll-twin-title">'+escape(tr("Source ↔ Live Twin" if link["manipulable"] else "Source ↔ formal representation"))+'</div>', unsafe_allow_html=True)
            st.text(catalog[focus]["label"])
            support = next((s for s in link["support"] if selected and s["region_id"] == selected["region_id"]), link["support"][0])
            st.caption(tr(KINDS[support["kind"]]) + " · " + tr("Page {page}", page=support["page"]))
            if link["manipulable"]:
                ids = link["manipulation_target_ids"]
                owned = [t for t in data["targets"] if t["id"] in ids]
                rows, seen = [], set()
                for target in owned:
                    parameters, values, _ = data["owners"][target["id"]]
                    for row in comparison_rows(parameters, values, target["parameter_ids"]):
                        if row["id"] not in seen: rows.append(row); seen.add(row["id"])
                # Fixed text values; no source excerpt is rewritten or interpreted.
                st.markdown(comparison_table(rows), unsafe_allow_html=True)
                st.caption(tr("Compiled defaults are model values; verify them against the unchanged original source."))
                if workspace["mode"] != "explore":
                    def explore():
                        demo_id = data["owners"][ids[0]][2]
                        if demo_id:
                            from interactive_lab import select_demo
                            select_demo(st.session_state["interactive_lab_state"], demo_id)
                        workspace["representation"] = "formal"
                        open_workspace(workspace, "explore", focus, catalog, wrapper)
                    st.button(tr("Open interactive twin"), key="workspace-twin-explore", type="primary", use_container_width=True, on_click=explore)
            else: st.caption(tr(link["reason_not_manipulable"]))
            if workspace["mode"] != "source":
                st.button(tr("Return to supporting source"), key="workspace-twin-source", on_click=open_workspace,
                          args=(workspace, "source", focus, catalog, wrapper))
            with st.expander(tr("Support details")):
                st.caption(tr("Source support is estimated. A safe handle is a model capability, not proof of source fidelity."))
                if link["manipulable"] and any(r["generated_range"] for r in rows):
                    st.caption(tr("Generated exploration range"))
    except (ValueError, TypeError, KeyError, OverflowError):
        # Optional evidence joins cannot invalidate a working formal engine.
        return


def comparison_table(rows):
    """Fixed markup only; source/model labels and units are always escaped."""
    headings = ("", tr("Compiled baseline"), tr("Current exploration"), tr("Delta"))
    head = "".join("<th scope='col'>"+escape(value)+"</th>" for value in headings)
    body = "".join("<tr><td>"+escape(row["label"])+"<br>"+escape(row["unit"])+"</td>"
                   + f"<td>{row['baseline']:.5g}</td><td>{row['current']:.5g}</td><td>{row['delta']:+.5g}</td></tr>"
                   for row in rows[:4])
    return '<table class="vll-readout"><thead><tr>'+head+'</tr></thead><tbody>'+body+'</tbody></table>'
