"""One explicit strict Responses request; cached unsuitable outcomes and isolated failures."""
import json
from i18n import output_language_instruction
from .schema import SCHEMA, INSTRUCTIONS, MAX_PAYLOAD
from .validator import normalize, shape
from .state import save
from .diagnostics import Rejection, record


def context(analysis,source,catalog,registry,focus,allowed_pages):
    if focus not in catalog: raise Rejection("missing_formal_focus","$.formal_focus")
    ids=[focus]+[i for i in catalog if i!=focus][:15]
    result=dict(analysis_language=analysis.get("analysis_language","zh-TW"),formal_focus=focus,
        catalog={i:catalog[i] for i in ids},parameter_registry={k:{field:value for field,value in v.items() if field!="demo_spec"} for k,v in registry.items() if set(v["semantic_ids"])&set(ids)},
        allowed_pages=list(allowed_pages)[:8],quick_summary=str(analysis.get("quick_summary",""))[:1500])
    if source.get("kind")=="pdf":
        result["source_context"]={str(p):str(source.get("page_texts",{}).get(p,source.get("page_texts",{}).get(str(p),"")))[:1200] for p in allowed_pages[:8]}
    else: result["source_context"]=str(source.get("text",source.get("source_text","")))[:6000]
    excerpts=result["source_context"].values() if isinstance(result["source_context"],dict) else [result["source_context"]]
    if not any(text.strip() for text in excerpts): raise Rejection("missing_source_context","$.source_context")
    # Only bounded catalog metadata, never PDF bytes or a second vision request.
    if len(json.dumps(result,ensure_ascii=False))>18000: raise Rejection("context_bound")
    return result


def request(client,model,data):
    language=data["analysis_language"]
    response=client.responses.create(model=model,instructions=INSTRUCTIONS+"\n"+output_language_instruction(language if language in ("en","zh-TW") else "zh-TW"),
        input=json.dumps(data,ensure_ascii=False),text={"format":dict(type="json_schema",name="analogy_world_v1",strict=True,schema=SCHEMA)})
    if getattr(response,"status",None)=="incomplete": raise Rejection("incomplete_response")
    for item in getattr(response,"output",[]) or []:
        for content in getattr(item,"content",[]) or []:
            if getattr(content,"type",None)=="refusal": raise Rejection("model_refusal")
    if not isinstance(response.output_text,str) or len(response.output_text.encode())>MAX_PAYLOAD: raise Rejection("response_bound")
    try: return json.loads(response.output_text)
    except json.JSONDecodeError as error: raise Rejection("invalid_json") from error


def build(store,key,client,model,data,catalog,registry,pages,force_new=False):
    if key in store["cache"]:
        store["active"]=key
        return store["cache"][key]
    raw=None; stage="request"; progress={}
    pending=store.setdefault("pending",{})
    try:
        if key in pending and not force_new:
            raw=pending[key]
        else:
            raw=request(client,model,data)
            stage="normalize"
            shape(raw,SCHEMA)
            # Generated declarations only, never compiler input/source/PDF/key.
            # Retain failed data in session for explicit zero-request revalidation.
            if isinstance(raw,dict) and len(json.dumps(raw,ensure_ascii=False).encode())<=MAX_PAYLOAD:
                pending[key]=raw
                while len(pending)>2: pending.pop(next(iter(pending)))
        stage="normalize"
        spec=normalize(raw,catalog,registry,pages,key[-1],progress)
        stage="cache"
        save(store,key,spec)
        pending.pop(key,None)
        record(store,key,"accepted" if spec["suitable"] else "unsuitable",raw=raw,normalized=spec)
        return spec
    except Exception as error:
        if isinstance(error,Rejection) and error.code in ("response_bound","invalid_json","incomplete_response","model_refusal"): stage="response"
        entry=record(store,key,stage,error,raw)
        entry.update(progress)
        return None
