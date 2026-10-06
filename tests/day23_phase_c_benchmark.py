"""Explicit Phase C evaluation. Reuses Day23 request facade; never changes A/B.

--live makes at most 18 paid attempts across resumes. No API retry or polishing.
Raw declarations are saved before validation. Gold is never sent to the planner.
"""
import argparse,copy,hashlib,json,logging,math,os,sys,tomllib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/"tests")]
import day23_benchmark as base
from day23_freeze import digest
from learning_world import compiler,execution,process
from source_atlas.model import semantic_catalog
from workspace.state import focusable,set_workspace_focus,open_workspace
from interactive_lab import default_values,compute_curves
from scene.world.state import new_state
HOME=ROOT/"docs/day23/phase_c"

def manifest():
 m=json.loads((HOME/"manifest.json").read_text(encoding="utf-8"))
 assert digest(m["payload"])==m["corpus_sha256"]
 for c in m["payload"]["materials"]:
  assert hashlib.sha256(c["text"].encode()).hexdigest()==c["text_sha256"]
  assert (HOME/"materials"/(c["material_id"]+".txt")).read_text(encoding="utf-8").rstrip("\n")==c["text"]
 return m

def probe_execution(spec,gold):
 state=execution.initial(spec);steps=[]
 assert execution.apply(spec,state,execution.event(spec,state,"return")) is None
 for _ in range(80):
  op=next((o for o in ("call","complete","return") if execution.enabled(spec,state,o)),None)
  if op is None:break
  ev=execution.event(spec,state,op)
  if op=="return":
   wrong=dict(ev,destination="wrong_caller");assert execution.apply(spec,state,wrong) is None
  state,semantic=execution.apply(spec,state,ev)
  assert execution.valid(spec,state)
  assert execution.apply(spec,state,ev) is None
  steps.append(dict(operation=op,semantic_id=semantic,depth=len(state["frames"])))
 assert len(state["frames"])==1 and state["frames"][0]["status"]=="completed"
 assert math.isclose(state["frames"][0]["result"],gold["root_result"],abs_tol=1e-12)
 assert len(spec["calls"])==gold["call_count"]
 restored=execution.reset(spec,state);assert restored["frames"]==execution.initial(spec)["frames"]
 return dict(root_result=state["frames"][0]["result"],steps=steps,wrong_caller_early_return_stale_rejected=True,reset=True)

def numeric_probe(lab,case):
 assert lab["demos"],"numeric artifact missing"
 demo=lab["demos"][0];values=default_values(demo);x,curves=compute_curves(demo,values)
 params=demo["parameters"]
 if case["contract"]=="fixed":
  assert all(p["parameter_kind"]=="fixed" for p in params),"source constants became sliders"
  assert all(p["default"] in case["gold"]["fixed_values"] for p in params)
  assert any(all(math.isclose(float(y),4*math.exp(-.25*float(t)),rel_tol=1e-8,abs_tol=1e-9) for t,y in zip(x,v)) for v in curves.values()),"source magnitude mismatch"
 else:
  gold=case["gold"]
  gain=next(p for p in params if p["parameter_kind"]=="adjustable")
  for key in ("min","max","default","step"):assert math.isclose(gain[key],gold[key],rel_tol=0,abs_tol=1e-12),"narrow source range changed"
  assert any(all(math.isclose(float(y),gold["default"]*float(t),rel_tol=1e-9,abs_tol=1e-9) for t,y in zip(x,v)) for v in curves.values()),"source response mismatch"
  assert not any(p["default"]==gold["default"]-2 for p in params),"derived value became control"
 return dict(parameter_domains=[{k:p[k] for k in ("id","min","max","default","step","parameter_kind")} for p in params],source_curve_samples_checked=len(x))

def evaluate(case,client):
 row=dict(material_id=case["material_id"],contract=case["contract"],proposal_family=None,selected_family=None,
  selection_pass=None,compilation_pass=None,semantic_pass=None,reference_pass=None,post_compile_api_calls=None,
  analysis_retained=False,failure=None,human_grounding="pending")
 try:
  h=base.HELPERS or base.load_app_helpers();client.stage="analysis"
  response=client.create(model=client.model,instructions=base.analysis_prompt(),input=case["text"],text={"format":dict(type="json_schema",name="visual_learning_analysis",strict=True,schema=h["ANALYSIS_SCHEMA"])})
  analysis,path,lab=base.prepare_analysis(json.loads(response.output_text));row["analysis_retained"]=bool(analysis.get("quick_summary"))
  source=dict(kind="text",source_text=case["text"],page_texts={});catalog=semantic_catalog(None,analysis)
  catalog={i:v for i,v in catalog.items() if focusable(i,catalog,{})}
  caps=compiler.capabilities(analysis,{},lab);store=compiler.ensure({},case["material_id"])
  key=compiler.identity(case["material_id"],"en",source,catalog,caps,None);client.stage="planner"
  plan=compiler.build(store,key,client,client.model,compiler.context(analysis,source,catalog,[],caps,None),catalog,[],caps)
  row["diagnostic"]=store["diagnostics"].get(key,{})
  raw=json.loads((client.directory/"planner.json").read_text(encoding="utf-8"))
  row["proposal_family"]=raw.get("raw",{}).get("preferred")
  if plan is None:row.update(compilation_pass=False,failure="planner_rejected");return row
  row.update(selected_family=plan["family"],selection_pass=plan["family"] in case["acceptable_families"],reference_pass=set(plan["focus_ids"])<=set(catalog) and plan["source_pages"]==[])
  scene=None
  if case["scene_domain"]:
   client.stage="scene"
   declaration=base.request_scene(client,client.model,base.build_scene_context(analysis,source,[],case["scene_domain"]))
   try:scene=base.normalize_scene(declaration,[])
   except ValueError as error:
    row["optional_scene_rejection"]=str(error)[:250]
    if case["contract"]=="identity":row.update(compilation_pass=False,failure="scene_rejected");return row
  row["compilation_pass"]=bool(plan["family"] in ("execution","process","static","none") or scene or lab["demos"])
  client.local_start=client.calls
  if case["contract"]=="execution":
   assert plan["family"]=="execution","resolved execution was replaced by generic operations"
   row["interaction"]=probe_execution(plan["execution"],case["gold"])
  elif case["contract"]=="identity":
   assert plan["family"]=="structural" and scene and scene["domain"]=="probability_sets"
   label={o["id"]:o["label"] for o in scene["outcomes"]}
   memberships=[sorted(label[i] for i in e["outcome_ids"]) for e in scene["events"]]
   assert all(m in memberships for m in case["gold"]["memberships"]),"scoped events were merged/changed"
   assert len({e["id"] for e in scene["events"]})>=2
   row["interaction"]=dict(event_ids=[e["id"] for e in scene["events"]],memberships=memberships,**base.probe_scene(scene))
  elif case["contract"] in ("fixed","narrow"):
   row["interaction"]=numeric_probe(lab,case)
   if scene:row["spatial_interaction"]=base.probe_scene(scene)
  elif case["contract"]=="legal":
   assert plan["family"]=="process"
   spec=plan["process"];assert len(spec["states"])==1
   variable=spec["states"][0];assert variable["initial"]=="Draft" and set(variable["values"])==set(case["gold"]["states"])
   pairs={(t["from_state"],t["to_state"]) for t in spec["transitions"]}
   required={("Draft","Reviewed"),("Reviewed","Released")}
   assert required<=pairs and pairs<=required|{("Reviewed","Draft"),("Released","Draft")},"illegal workflow edge"
   row["interaction"]=base.probe_process(spec)
   state=process.initial(spec)
   for desired in ("Reviewed","Released"):
    t=next(t for t in spec["transitions"] if t["to_state"]==desired)
    state,_=process.apply(spec,state,dict(identity=state["identity"],revision=state["revision"],transition_id=t["id"],value=""))
   assert not any(process.enabled(spec,state,t["id"]) for t in spec["transitions"] if t["to_state"]!="Draft"),"terminal review/release remained legal"
  else:assert plan["family"] in ("static","none") and plan["process"] is None and plan["execution"] is None
  # Canonical mode/focus round trip is separate from browser acceptance.
  ws=dict(material_id=case["material_id"],mode="explore",focus=None);focus=plan["focus_ids"][0]
  assert set_workspace_focus(ws,focus,catalog),"canonical focus rejected"
  for mode in ("source","practice","explore"):open_workspace(ws,mode);assert ws["focus"]==focus
  row["semantic_pass"]=True
 except Exception as error:
  row.update(semantic_pass=False if client.local_start is not None else None,failure=base.safe_error(error))
  if isinstance(error,AssertionError):row["failure"]["contract_reason"]=str(error)[:180]
 finally:
  if client.local_start is not None:row["post_compile_api_calls"]=client.calls-client.local_start
 return row

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--live",action="store_true");parser.add_argument("--audit",action="store_true");parser.add_argument("--audit-v2",action="store_true");parser.add_argument("--final-replay",action="store_true");args=parser.parse_args()
 if (args.audit or args.audit_v2 or args.final_replay) and args.live:parser.error("Audit is recorded replay only")
 m=manifest();file=HOME/("final_replay_results.json" if args.final_replay else "audit_v2_results.json" if args.audit_v2 else "audit_results.json" if args.audit else "results.json");fp=base.production_fingerprint()
 result=json.loads(file.read_text(encoding="utf-8")) if file.exists() else dict(scope="Day23 Phase C prospective validation only",started_at_utc=datetime.now(timezone.utc).isoformat(),corpus_sha256=m["corpus_sha256"],production_sha256=fp,model="gpt-5.6-luna",rows=[])
 assert result["production_sha256"]==fp and result["corpus_sha256"]==m["corpus_sha256"],"Frozen run identity changed"
 client=None
 if args.live:
  from openai import OpenAI
  secret=os.environ.get("OPENAI_API_KEY") or tomllib.loads((ROOT/".streamlit/secrets.toml").read_text(encoding="utf-8"))["OPENAI_API_KEY"]
  client=OpenAI(api_key=secret,max_retries=0,timeout=120)
 attempts=lambda:sum(json.loads(p.read_text(encoding="utf-8")).get("paid_this_run") is True for p in HOME.glob("declarations/*/*.json"))
 budget=dict(remaining=max(0,18-attempts()));initial_budget=budget["remaining"];logging.getLogger("streamlit").setLevel(logging.ERROR)
 for case in m["payload"]["materials"]:
  if case["material_id"] in {r["material_id"] for r in result["rows"]}:continue
  facade=base.Responses(HOME/"declarations"/case["material_id"],"live" if args.live else "replay",result["model"],budget,live_client=client)
  row=evaluate(case,facade);result["rows"].append(row)
  records=[json.loads(p.read_text(encoding="utf-8")) for p in HOME.glob("declarations/*/*.json")]
  result["paid_request_attempts"]=attempts();result["tokens"]={k:sum(r.get("usage",{}).get(k) or 0 for r in records) for k in ("input_tokens","output_tokens","total_tokens")}
  result["summary"]={k:{"pass":sum(r.get(k) is True for r in result["rows"]),"fail":sum(r.get(k) is False for r in result["rows"]),"not_evaluated":sum(r.get(k) is None for r in result["rows"])} for k in ("selection_pass","compilation_pass","semantic_pass","reference_pass")}
  result["execution"]="live" if args.live else "recorded_replay"
  result["paid_attempts_this_execution"]=initial_budget-budget["remaining"]
  result["updated_at_utc"]=datetime.now(timezone.utc).isoformat();base.save(file,result);print(json.dumps(row),flush=True)
 print(json.dumps({k:result[k] for k in ("summary","paid_request_attempts","tokens")},indent=2))
if __name__=="__main__":main()
