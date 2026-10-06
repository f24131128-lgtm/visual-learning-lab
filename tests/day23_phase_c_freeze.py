"""New original Phase C holdout, distinct from deterministic fixtures and A/B gold.

Run only after deterministic contracts stabilize, BEFORE any holdout model calls.
Gold is an agent-authored pre-execution assessment; human approval is pending.
"""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/"tests")]
from day23_freeze import digest
CASES=[
 dict(material_id="scoped_labels",acceptable_families=["structural"],contract="identity",scene_domain="probability_sets",
 text="An original finite-outcome exercise: choose one of four equally likely tickets p, q, r, s. Two different departments print the same short event label 'Ready'. In the assembly department, Ready means tickets p or q. In the inspection department, Ready means tickets q or r. These are different events despite identical printed labels. Their intersection is q; their union is p, q, r. Each event has probability 1/2, the intersection 1/4, and the union 3/4. Keep both event identities selectable so their membership can be compared. The shared word Ready does not merge departments or events.",gold=dict(memberships=[["p","q"],["q","r"]],union=.75,intersection=.25)),
 dict(material_id="nested_sum",acceptable_families=["execution"],contract="execution",scene_domain=None,
 text="A resolved educational call example, not a request to run code. S(n) returns 0 when n=0; otherwise it calls S(n-1), waits for that child's returned numeric answer, then returns n plus the child's answer. Study the bounded invocation S(4). The stack enters S(4), S(3), S(2), S(1), S(0). The base invocation completes with 0. Unwinding returns 0 to S(1), then 1 to S(2), 3 to S(3), 6 to S(4), and the root completes with 10. Every child result belongs to its immediate caller; a waiting caller cannot complete early. Calls have separate frame identities even though they share one procedure. Observe legal call, completion and return operations locally.",gold=dict(root_result=10,call_count=5)),
 dict(material_id="nested_adjustment",acceptable_families=["execution"],contract="execution",scene_domain=None,
 text="Two different numeric procedures form one bounded teaching trace. The outer Adjust invocation has numeric argument offset=5. It invokes the inner Triple procedure with numeric argument input=4, waits for Triple's result, and then returns offset plus that result. Triple has no child; its result expression is 3 times input. Triple completes with 12, returns 12 to the waiting Adjust invocation, and Adjust completes with 17. The outer invocation cannot complete before receiving 12. Results cannot be routed to another frame. Show the active invocation, caller, arguments, returned binding and completed result; reset restores the initial outer invocation.",gold=dict(root_result=17,call_count=2)),
 dict(material_id="fixed_decay",acceptable_families=["dynamic","spatial"],contract="fixed",scene_domain="spatial_dynamics",
 text="An original mathematical teaching model uses y(t)=4*exp(-0.25*t) on 0<=t<=6 seconds. The source specifies amplitude exactly 4 units and decay rate exactly 0.25 per second. Both are fixed constants in this exercise, not uncertainty intervals and not learner-adjustable ranges. Time can move. The derived instantaneous magnitude is y(t); its rate is -0.25*y(t). At t=0, magnitude is 4 and rate -1; at t=4, magnitude is 4/e and rate -1/e. A planar point may have coordinates (t,y(t)); the same y(t) belongs to its waveform and magnitude metric. Fixed constants must be read-only. Do not invent slider spans or claim a generated range was supplied by the source.",gold=dict(fixed_values=[4,.25],at_time_4=1.4715177646857693)),
 dict(material_id="narrow_gain",acceptable_families=["dynamic","spatial"],contract="narrow",scene_domain=None,
 text="A calibration teaching model uses response(x)=gain*x for 0<=x<=2. The source explicitly allows gain from 2.0000 through 2.0002, default 2.0001, in increments 0.00001. This is a narrow positive-width interval, not a fixed parameter. Display it as adjustable without widening the specified bounds. The source also fixes a reference gain at exactly 2. A derived comparison metric is gain-2; it must not become an independent slider. At x=2 the default response is 4.0002, and the two legal endpoint responses are 4 and 4.0004. Parameter changes and reset are local; the reference remains fixed.",gold=dict(min=2,max=2.0002,default=2.0001,step=.00001,at_x_2=4.0002)),
 dict(material_id="guarded_workflow",acceptable_families=["process"],contract="legal",scene_domain=None,
 text="An original finite workflow has one status variable with values Draft, Reviewed, Released. Initially it is Draft. Review is legal only from Draft and changes status to Reviewed. Release is legal only from Reviewed and changes status to Released. Released is terminal: neither action is legal there. There is no action that jumps directly from Draft to Released. Reset restores Draft. Present the current status and legal actions, preserving the same formal source concept across Source and Explore. This is a finite state transition exercise without numeric sliders or collection input.",gold=dict(states=["Draft","Reviewed","Released"])),
 dict(material_id="term_only",acceptable_families=["static","none"],contract="static",scene_domain=None,
 text="In this short terminology note, a token is simply the local name used for a small named item. The note gives a definition, without prescribing order, state transitions, formulas, geometry, random outcomes, or a call execution example. An explanation or a simple conceptual representation is appropriate. Adding animated controls would not reveal a relationship specified in this source.",gold=dict(interaction_essential=False)),
]

def main():
 home=ROOT/"docs/day23/phase_c"; path=home/"manifest.json"
 if path.exists(): raise SystemExit("Already frozen; do not rewrite holdout/gold")
 payload=dict(scope="Day 23 Phase C only",provenance="7 original authored teaching excerpts; no downloaded/copyrighted corpus",gold_status="agent pre-execution gold; human review pending",materials=[])
 for case in CASES:
  case=dict(case,text_sha256=hashlib.sha256(case["text"].encode()).hexdigest())
  payload["materials"].append(case)
  material=home/"materials"/(case["material_id"]+".txt"); material.parent.mkdir(parents=True,exist_ok=True)
  material.write_text(case["text"]+"\n",encoding="utf-8")
 manifest=dict(frozen_at_utc=datetime.now(timezone.utc).isoformat(),corpus_sha256=digest(payload),payload=payload)
 path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:manifest[k] for k in ("frozen_at_utc","corpus_sha256")}))
if __name__=="__main__":main()
