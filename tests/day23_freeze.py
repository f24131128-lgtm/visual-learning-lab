"""One-time prospective corpus freeze. Never imported by production.

Public documentation cases are independently paraphrased, not copied code.
Other cases are original educational problems: no OpenStax text/assets are
ingested (its retrieved pages restrict use in generative AI offerings).
"""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "docs" / "day23"

# All judgments and interaction requirements are authored before model execution.
CASES = [
    ("damped_motion", "physics", ["continuous_numeric_state", "equation_governed", "time_dynamics", "spatial_relation"],
     "dynamic", ["spatial"], "Time-dependent displacement and a decay envelope should respond to damping, without inventing forces.",
     "Change a damping parameter and compare displacement curves; time changes position.",
     "Original problem: A damped oscillator has displacement x(t)=A*exp(-beta*t)*cos(omega*t). A is an initial scale, beta is a nonnegative decay rate, and omega is angular frequency. Study 0 to 8 seconds with A=1, beta=0.2 and omega=3. Hold omega fixed while comparing beta=0.1 and beta=0.5. The envelope is A*exp(-beta*t); its magnitude falls faster at larger beta. This simplified model treats beta and omega as independent teaching parameters and does not model critical damping."),
    ("vector_resultant", "physics", ["continuous_numeric_state", "spatial_relation", "direct_manipulation"],
     "spatial", ["dynamic"], "Two component vectors and their sum are spatial, parameter-governed but do not require physical time evolution.",
     "Change a component and see the resultant coordinates change with equal physical scales.",
     "Original problem: Two planar vectors are u=(a,0) and v=(0,b). Their resultant is r=(a,b), with length sqrt(a*a+b*b). Use a and b between 1 and 5. Starting at a=3,b=4 gives length 5. Draw both arrows from the same origin and the resultant from the origin. Changing a or b changes geometry; no time evolution or acceleration is asserted."),
    ("rc_charging", "electrical", ["equation_governed", "time_dynamics", "accumulation", "causal_flow"],
     "dynamic", [], "Exponential charging is quantitative and time-dependent; a diagram alone misses the time constant comparison.",
     "Increasing resistance stretches charging time; compare capacitor voltage against time.",
     "Original problem: An ideal resistor R and capacitor C in series are connected to a constant voltage Vs at time zero, with initially uncharged capacitor. Capacitor voltage Vc(t)=Vs*(1-exp(-t/(R*C))) and current I(t)=(Vs/R)*exp(-t/(R*C)). Use seconds, ohms and farads; R=2,C=1,Vs=5 initially. Compare R from 1 to 4 over 0 to 12 seconds while C and Vs stay fixed. At t=R*C, Vc is approximately 0.632*Vs. Larger R slows charging and lowers the initial current."),
    ("quadratic_shape", "mathematics", ["equation_governed", "continuous_numeric_state", "geometric_relation"],
     "dynamic", ["spatial"], "A parameterized function needs locally responsive plotting; time playback is optional and must not be a prerequisite.",
     "Change h and a; the vertex moves horizontally and opening/curvature changes.",
     "Original problem: Study y=a*(x-h)^2+k for x between -5 and 5. a is nonzero, h controls horizontal translation and k controls vertical translation. Start at a=1,h=0,k=0. Compare a=0.5 with a=2, and h=-2 with h=2. The vertex is (h,k), the symmetry line is x=h, and changing h does not change the minimum value when a is positive. x is an independent coordinate, not elapsed time."),
    ("finite_sampling", "mathematics", ["finite_outcomes", "set_relations", "probability", "branching"],
     "structural", [], "Explicit finite outcomes and overlapping events support exact set/probability operations and sampling.",
     "Select overlapping events, compute union/intersection, then sample locally.",
     "Original problem: A bag contains four equally likely labeled tokens r1,r2,b1,b2. One token is selected. Let R={r1,r2} mean red and N={r1,b1} mean label ending in 1. P(R)=1/2, P(N)=1/2, P(R intersection N)=1/4, and P(R union N)=3/4. Distinguish event union from adding probabilities without correcting overlap. Repeated sampling estimates probabilities but exact values come from the four outcomes."),
    ("undo_history", "programming", ["ordered_collection", "transition_system", "accumulation"],
     "process", [], "Last-end insertion/removal is a bounded discrete process with meaningful learner actions.",
     "Add a new action to the last end, undo removes that newest action, reset restores original history.",
     "An undo history can be represented as a bounded sequence. New actions are appended to the right; undo removes the rightmost action, so the most recent action is undone first. Start with actions Draw and Color, with room for six actions. Add Move to obtain Draw,Color,Move. Undo returns Move and leaves Draw,Color. Undo on an empty history is unavailable. A deque supports appending and popping at either end, but this teaching example uses only its right end."),
    ("future_lifecycle", "programming", ["transition_system", "branching", "causal_flow"],
     "process", ["static"], "Legal finite-state changes can be stepped; cancellation must not be represented as valid after running begins.",
     "Pending can start or cancel; running can finish; cancellation after start is disabled.",
     "A Future represents an asynchronous computation. For a simplified lifecycle, use pending, running, finished and cancelled. Starting changes pending to running. Successful completion changes running to finished. Cancellation may change pending to cancelled, but cannot cancel a computation already running or finished. finished and cancelled are terminal in this simplified model. This lesson models lifecycle states only, not thread scheduling, exception propagation or actual concurrent execution."),
    ("recursive_calls", "algorithms", ["branching", "ordered_collection", "transition_system", "hierarchy"],
     "process", ["static"], "Call nesting and return order are important; a source-supported static call diagram is honest if numeric execution cannot be represented.",
     "Inspect call/return order; if interactive, nesting must agree with the source rather than pretend arbitrary tokens execute recursion.",
     "Original problem: Define factorial for nonnegative integers by f(0)=1 and f(n)=n*f(n-1) when n is positive. For n=3 the calls descend 3,2,1,0; results unwind 1,1,2,6. Each suspended caller waits for the result of its child. A call stack stores pending frames in last-in-first-out order. The base case stops descent. Show why removing the base case prevents termination; do not run user-authored code."),
    ("feedback_response", "control", ["equation_governed", "feedback", "time_dynamics", "causal_flow"],
     "dynamic", [], "Closed-loop gain changes a quantitative response; topology alone misses the response comparison.",
     "Change proportional gain and compare steady state and response time.",
     "Original problem: A scalar plant obeys dy/dt=-y+u. A proportional feedback controller sets u=K*(r-y), with constant reference r=1 and y(0)=0. For K greater than zero the closed-loop response is y(t)=K/(1+K)*(1-exp(-(1+K)*t)). Use K from 0.5 to 4 and time from 0 to 6 seconds. Higher K speeds response and reduces steady-state error, but does not eliminate that error for finite K. No oscillation or overshoot occurs in this first-order ideal model."),
    ("market_equilibrium", "economics", ["continuous_numeric_state", "equation_governed", "causal_relation", "comparison"],
     "dynamic", ["static"], "Parameterized crossing curves communicate a comparative equilibrium; a supported static curve comparison is acceptable without fictitious time dynamics.",
     "Shift a demand intercept and inspect the intersection; do not invent a time-dependent market mechanism.",
     "Original problem: In a teaching market, quantity demanded is Qd=12-2*p and quantity supplied is Qs=2+p, with p between 0 and 6. Equilibrium requires Qd=Qs, giving p=10/3 and Q=16/3. Raising the demand intercept from 12 to 15 while holding both slopes and the supply intercept fixed gives p=13/3 and Q=19/3. These are comparative equilibria, not a claim about actual market data or adjustment over time."),
    ("cell_cycle", "biology", ["ordered_stages", "causal_flow", "transition_system"],
     "static", ["process"], "Qualitative ordered stages can use a fixed process diagram or honest finite-state navigation, without invented quantitative biology.",
     "Inspect stage order and the replication/division distinction; no invented rate sliders.",
     "Original lesson: A simplified eukaryotic cell cycle has G1, S, G2 and M phases. G1 includes cell growth; S replicates DNA; G2 prepares for division; M separates replicated chromosomes and divides the cell. The diagram returns to G1 after M. DNA replication and cell division are different events. This high-level account omits detailed checkpoints, quiescence and differences among cell types; it gives no phase durations or equations."),
    ("byte_definition", "conceptual", ["primarily_definitional"],
     "none", ["static"], "A short definition and example need no forced generated world or unrelated analogy.",
     "Read the definition; no additional world builder or fake PDF page is needed.",
     "Python bytes is an immutable sequence of integers in the range 0 through 255. An individual integer identifies one byte value; the sequence itself does not specify a text encoding. Decoding bytes as text requires choosing an encoding. This short lesson only distinguishes byte values from interpreted text; it supplies no evolving process or numeric experiment."),
]
DOCS = {
    "undo_history": "https://docs.python.org/3/library/collections.html#collections.deque",
    "future_lifecycle": "https://docs.python.org/3/library/concurrent.futures.html#future-objects",
    "byte_definition": "https://docs.python.org/3/library/stdtypes.html#bytes-objects",
}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def freeze():
    DEST.mkdir(parents=True, exist_ok=True)
    path = DEST / "phase_a_manifest.json"
    if path.exists():
        raise SystemExit("Manifest already frozen. No overwrite permitted.")
    materials = []
    for mid, domain, traits, primary, alternatives, reason, interaction, text in CASES:
        materials.append(dict(material_id=mid, domain=domain, semantic_traits=traits,
            primary_family=primary, acceptable_families=[primary, *alternatives], gold_reason=reason,
            expected_interaction=interaction, interaction_essential=mid not in
            ("recursive_calls", "market_equilibrium", "cell_cycle", "byte_definition"),
            text=text, text_sha256=hashlib.sha256(text.encode()).hexdigest(),
            provenance=dict(kind="public_documentation_paraphrase" if mid in DOCS else "independently_authored",
                url=DOCS.get(mid), retrieval_date="2026-10-05" if mid in DOCS else None,
                status="Original prose; documentation facts independently paraphrased; Python docs PSF License v2, no code/assets copied"
                if mid in DOCS else "Original educational problem; no external prose, assets or weights redistributed")))
        (DEST / "materials").mkdir(exist_ok=True)
        (DEST / "materials" / (mid + ".txt")).write_text(text + "\n", encoding="utf-8")
    payload = dict(benchmark_version="1.0", frozen_at_utc=datetime.now(timezone.utc).isoformat(),
        client_date="2026-10-05", base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        planner_schema="1.0", spatial_schema="2.2", probability_schema="1.1",
        gold_status="agent_authored_before_execution__human_review_pending",
        source_policy="3 documentation paraphrases and 9 original teaching excerpts. Restricted OpenStax pages were excluded; this is not a real-PDF corpus or a human-approved gold set.",
        correction_policy="Never overwrite gold. Any correction needs an append-only dated correction record and separately reported results.",
        materials=materials)
    manifest = dict(payload=payload, corpus_sha256=digest(payload))
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Frozen {len(materials)} materials: {manifest['corpus_sha256']}")


if __name__ == "__main__":
    freeze()
