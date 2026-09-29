"""Optional targeted scene requests, session caches, and learning navigation."""

import hashlib
import json

from openai import OpenAI
import streamlit as st
import streamlit.components.v1 as components

from i18n import DEFAULT_LANGUAGE, RESPONSE_LANGUAGES, output_language_instruction, tr
from interactive_lab import default_values, select_demo
from safe_math import MathExpressionError
from simulation_spec import DYNAMIC_SIMULATION_SCHEMA, SIMULATION_INSTRUCTIONS, clean_simulation, simulation_candidate
from simulation_plot import animation_html, build_simulation_figure, cached_scene, compute_scene, has_motion

MAX_CONTEXT_CHARS = 30000
MAX_SOURCE_CHARS = 6000
SCHEMA_VERSION = 1


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def build_simulation_context(analysis, demo, learning_path, source_context, allowed_pages, validate_pages):
    """Bound prior structured understanding and original excerpts; never attach a file."""
    language = analysis.get("analysis_language", DEFAULT_LANGUAGE)
    if language not in RESPONSE_LANGUAGES:
        language = DEFAULT_LANGUAGE
    steps = [step for step in (learning_path or {}).get("steps", []) if step["id"] in demo["related_step_ids"]]
    pages = validate_pages(demo["source_pages"] + [page for step in steps for page in step.get("source_pages", [])], allowed_pages)
    terms = [demo["title"], demo["learning_goal"], *(step["title"] for step in steps)]
    def clipped(value, limit=400):
        return value[:limit] if isinstance(value, str) else ""
    concepts = []
    for item in analysis.get("key_concepts", []):
        if not isinstance(item, dict):
            continue
        refs = validate_pages(item.get("source_pages", []), allowed_pages)
        if pages and not set(refs).intersection(pages):
            continue
        concepts.append({"concept": clipped(item.get("concept"), 150), "explanation": clipped(item.get("explanation")), "source_pages": refs})
        if len(concepts) == 6:
            break
    terms.extend(item["concept"] for item in concepts)
    relationships = []
    for item in analysis.get("relationships", []):
        if not isinstance(item, dict):
            continue
        refs = validate_pages(item.get("source_pages", []), allowed_pages)
        relevant = any(isinstance(item.get(key), str) and item[key].casefold() in text.casefold()
                       for key in ("source", "target") for text in terms)
        if not relevant and not (pages and set(refs).intersection(pages)):
            continue
        relationships.append({**{key: clipped(item.get(key), 150) for key in ("source", "relation", "target")}, "source_pages": refs})
        if len(relationships) == 6:
            break
    evidence = [{"page": item["page"], "type": clipped(item.get("type"), 30),
                 "description": clipped(item.get("description")), "learning_value": clipped(item.get("learning_value"))}
                for item in analysis.get("visual_evidence", []) if isinstance(item, dict)
                and type(item.get("page")) is int and item["page"] in pages][:4]
    kind = source_context.get("kind", "text")
    if kind == "pdf":
        remaining = MAX_SOURCE_CHARS
        sections = []
        for page in pages:
            text = source_context.get("page_texts", {}).get(page, "")
            if isinstance(text, str) and text and remaining > 0:
                section = (f"[Page {page}]\n" + text)[:remaining]
                sections.append(section)
                remaining -= len(section) + 2
        source_text = "\n\n".join(sections)
    else:
        source_text = clipped(source_context.get("source_text"), MAX_SOURCE_CHARS)
    context = {
        "analysis_language": language, "response_language": RESPONSE_LANGUAGES[language],
        "quick_summary": clipped(analysis.get("quick_summary"), 1200), "attached_lab_demo": demo,
        "source_kind": kind, "relevant_pages": pages, "relevant_extracted_source_text": source_text,
        "related_learning_steps": [{"id": step["id"], "title": clipped(step["title"], 150),
                                    "learning_goal": clipped(step["learning_goal"]), "explanation": clipped(step["explanation"]),
                                    "source_pages": validate_pages(step["source_pages"], allowed_pages)} for step in steps],
        "relevant_key_concepts": concepts, "relevant_relationships": relationships, "prior_visual_evidence": evidence,
        "pdf_reinspection_status": "No original PDF attached; visual evidence is from the existing analysis.",
    }
    # Preserve the attached equation/parameters; shorten supporting context first.
    for field in ("relevant_relationships", "prior_visual_evidence", "relevant_key_concepts", "related_learning_steps"):
        while context[field] and len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
            context[field].pop()
    if len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
        context["relevant_extracted_source_text"] = ""
    if len(json.dumps(context, ensure_ascii=False)) > MAX_CONTEXT_CHARS:
        raise ValueError("Targeted context exceeds its budget.")
    return context


def reset_simulation_state():
    st.session_state.pop("dynamic_simulation_state", None)
    for key in list(st.session_state):
        if isinstance(key, str) and key.startswith("sim-widget-"):
            st.session_state.pop(key, None)


def ensure_simulation_state(material_id, lab, analysis, learning_path, source_context, allowed_pages, validate_pages, model):
    language = analysis.get("analysis_language", DEFAULT_LANGUAGE)
    signature = fingerprint({"demos": lab["demos"], "language": language, "model": model, "version": SCHEMA_VERSION})
    state = st.session_state.get("dynamic_simulation_state")
    if not isinstance(state, dict) or state.get("material_id") != material_id or state.get("signature") != signature:
        reset_simulation_state()
        state = {"material_id": material_id, "signature": signature, "language": language, "model": model,
                 "active_id": None, "specs": {}, "errors": {}, "frames": {}, "options": {}, "contexts": {},
                 "allowed_pages": list(allowed_pages), "step_ids": [step["id"] for step in (learning_path or {}).get("steps", [])]}
        for demo in lab["demos"]:
            if simulation_candidate(demo):
                state["contexts"][demo["id"]] = build_simulation_context(analysis, demo, learning_path, source_context, allowed_pages, validate_pages)
                state["options"][demo["id"]] = {"trail": True, "full_path": True, "static": False, "open": True}
        st.session_state["dynamic_simulation_state"] = state
    return state


def spec_cache_key(state, demo):
    return (state["material_id"], demo["id"], state["language"], fingerprint(demo), SCHEMA_VERSION)


def request_simulation(client, model, context):
    """The only Day 16 API site: one strict, bounded targeted Responses request."""
    response = client.responses.create(
        model=model, instructions=SIMULATION_INSTRUCTIONS + "\n" + output_language_instruction(context["analysis_language"]),
        input=json.dumps(context, ensure_ascii=False), max_output_tokens=8000,
        text={"format": {"type": "json_schema", "name": "dynamic_simulation", "strict": True, "schema": DYNAMIC_SIMULATION_SCHEMA}},
    )
    return json.loads(response.output_text)


def build_or_open_simulation(state, demo):
    """Explicit button callback only. Cache identity deliberately excludes slider values."""
    lab_state = st.session_state.get("interactive_lab_state", {})
    if (state["material_id"] != st.session_state.get("analysis_id")
            or state["material_id"] != lab_state.get("material_id") or demo["id"] not in state["contexts"]):
        return
    select_demo(lab_state, demo["id"])
    state["active_id"] = demo["id"]
    state["options"][demo["id"]]["open"] = True
    key = spec_cache_key(state, demo)
    if key in state["specs"]:
        state["errors"].pop(demo["id"], None)
        return
    try:
        # No automatic SDK retries: a failed attempt can be retried explicitly.
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"], max_retries=0)
        with st.spinner(tr("Creating a dynamic simulation…")):
            raw = request_simulation(client, state["model"], state["contexts"][demo["id"]])
        def validate_pages(pages, allowed):
            return sorted({page for page in pages if type(page) is int and page in allowed}) if isinstance(pages, list) else []
        spec = clean_simulation(raw, demo, state["allowed_pages"],
                                {"steps": [{"id": step_id} for step_id in state["step_ids"]]}, validate_pages)
        if spec["suitable"]:
            data = compute_scene(spec, demo, default_values(demo))
            if not has_motion(spec, data):
                raise ValueError("The default scene contains no motion.")
            omitted = set(data["omitted"])
            for field in ("objects", "static_series", "metrics"):
                spec[field] = [item for item in spec[field] if item["id"] not in omitted
                               and not (item.get("type") == "trail" and item["object_id"] in omitted)]
            spec["rejected"] += len(omitted)
        state["specs"][key] = spec
        state["errors"].pop(demo["id"], None)
    except (KeyError, st.errors.StreamlitSecretNotFoundError):
        state["errors"][demo["id"]] = "Simulation API access is not configured yet."
    except (ValueError, TypeError, AttributeError, OverflowError, RecursionError):
        state["errors"][demo["id"]] = "The simulation data was incomplete or unsafe. Please try again."
    except Exception:
        state["errors"][demo["id"]] = "We couldn’t create this simulation right now. Please try again."


def render_simulation_links(lab, step_ids, material_id, key_prefix, recommended=False):
    """Use existing step mappings; links are explicit builds or cached local opens."""
    state = st.session_state.get("dynamic_simulation_state")
    if not isinstance(state, dict) or state["material_id"] != material_id:
        return
    matches = []
    for demo in (lab or {}).get("demos", []):
        if demo["id"] not in state["contexts"]:
            continue
        spec = state["specs"].get(spec_cache_key(state, demo))
        refs = spec.get("related_step_ids", []) if spec and spec["suitable"] else demo["related_step_ids"]
        if spec and not spec["suitable"]:
            continue
        if set(refs).intersection(step_ids):
            matches.append((demo, spec))
    if not matches:
        return
    st.markdown("**" + tr("Recommended simulation" if recommended else "Dynamic simulation") + "**")
    for demo, spec in matches:
        title = spec["title"] if spec else demo["title"]
        st.button(tr("Open simulation: {title}" if spec else "Create dynamic simulation: {title}", title=title),
                  key=f"sim-widget-link-{key_prefix}-{material_id}-{demo['id']}",
                  help=tr("Opens the saved simulation locally." if spec else "Optional: makes one AI request, then animation and controls are local."),
                  on_click=build_or_open_simulation, args=(state, demo))
        st.markdown(f"[{tr('Go to Dynamic Simulation Studio')}](#dynamic-simulation-studio)")


def render_simulation_studio(lab, material_id, learning_path, go_to_lesson, format_pages):
    """Near the lab. Only a built scene gets the larger, collapsible studio."""
    state = st.session_state.get("dynamic_simulation_state")
    lab_state = st.session_state.get("interactive_lab_state", {})
    if not isinstance(state, dict) or state["material_id"] != material_id:
        return
    demo = next((demo for demo in lab["demos"] if demo["id"] == lab_state.get("selected_id")), None)
    if not demo or demo["id"] not in state["contexts"]:
        return
    state["active_id"] = demo["id"]
    spec = state["specs"].get(spec_cache_key(state, demo))
    prefix = f"sim-widget-{material_id}-{state['signature']}-{demo['id']}"
    # The anchor is also available before generation for lesson / inspector links.
    st.markdown('<span id="dynamic-simulation-studio"></span>', unsafe_allow_html=True)
    st.button(tr("Open simulation" if spec else "Create dynamic simulation"), key=f"{prefix}-build",
              help=tr("Opens the saved simulation locally." if spec else "Optional: makes one AI request, then animation and controls are local."),
              on_click=build_or_open_simulation, args=(state, demo))
    if demo["id"] in state["errors"]:
        st.info(tr(state["errors"][demo["id"]]))
    if spec is None:
        st.caption(tr("Build once when motion would help. Playback and parameter changes make no AI requests."))
        return
    if not spec["suitable"]:
        st.caption(spec["reason"] or tr("Motion is not a useful fit for this experiment."))
        return
    st.subheader(tr("Dynamic Simulation Studio"))
    options = state["options"][demo["id"]]
    with st.expander(spec["title"], expanded=options["open"]):
        st.write(spec["learning_goal"])
        st.caption(tr("Uses the experiment parameters above. Changes restart playback and are computed locally."))
        if spec["source_pages"]:
            st.caption(tr("Source: {pages}", pages=format_pages(spec["source_pages"])))
        else:
            st.caption(tr("Source: pasted text") if state["contexts"][demo["id"]]["source_kind"] != "pdf"
                       else tr("Source: no validated page reference"))
        columns = st.columns(3)
        options["trail"] = columns[0].checkbox(tr("Show trail"), value=options["trail"], key=f"{prefix}-trail")
        options["full_path"] = columns[1].checkbox(tr("Full path"), value=options["full_path"], key=f"{prefix}-path")
        options["static"] = columns[2].checkbox(tr("Static view"), value=options["static"], key=f"{prefix}-static")
        if spec["rejected"]:
            st.caption(tr("Some simulation objects were invalid and were skipped."))
        try:
            data = cached_scene(state, spec, demo, lab_state["demos"][demo["id"]]["values"], fingerprint(spec))
            if data["omitted"]:
                st.caption(tr("Some simulation values are undefined for these parameters and were skipped."))
            if data["stopped"]:
                st.caption(tr("Motion stops at the declared model boundary."))
            fallback = build_simulation_figure(spec, data, full_path=True, static=True, projection=spec["scene"]["dimension"] == "3d")
            if options["static"]:
                if spec["scene"]["dimension"] == "3d":
                    st.caption(tr("Static view shows the x/y projection of this 3D trajectory."))
                st.plotly_chart(fallback, use_container_width=True, key=f"{prefix}-static-chart", config={"displaylogo": False})
            else:
                try:
                    figure = build_simulation_figure(spec, data, options["trail"], options["full_path"])
                    document = animation_html(figure, fallback, tr("Animation is unavailable. Showing a static trajectory at its initial time; 3D uses an x/y projection."))
                    if hasattr(st, "iframe"):
                        st.iframe(document, height=figure.layout.height + 35)
                    else:  # Portable to the earlier Streamlit versions in requirements.txt.
                        components.html(document, height=figure.layout.height + 35, scrolling=False)
                    st.caption(tr("Play, pause, speed, reset and the timeline run in your browser. Metrics follow the same clock."))
                except Exception:
                    st.caption(tr("Animation is unavailable. Showing a static trajectory at its initial time; 3D uses an x/y projection."))
                    st.plotly_chart(fallback, use_container_width=True, key=f"{prefix}-fallback", config={"displaylogo": False})
        except MathExpressionError:
            st.info(tr("This simulation is undefined for these values. Adjust the experiment parameters or reset them."))
        except Exception:
            st.info(tr("This simulation could not be displayed. Your experiment, lesson and review remain available."))
        st.markdown("**" + tr("Observe this") + "**")
        for prompt in spec["observation_prompts"]:
            st.write(f"• {prompt}")
        for number, step in enumerate((learning_path or {}).get("steps", []), 1):
            if step["id"] in spec["related_step_ids"]:
                st.caption(tr("Related lesson: Step {number} — {title}", number=number, title=step["title"]))
                if st.button(tr("Go to lesson step"), key=f"{prefix}-lesson-{step['id']}"):
                    go_to_lesson(step["id"], learning_path)
                    st.rerun()
