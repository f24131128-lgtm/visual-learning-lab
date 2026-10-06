"""Small reproducible synthetic local benchmark; not real-corpus throughput."""
import gzip,json,statistics,sys,time,tracemalloc
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from manipulation_fixtures import systems,math_demo
from manipulation import runtime,world,lab
from scene.world.state import new_state
from interactive_lab import default_values

rows=[]
for name,scene in zip(('phase','projectile'),systems()):
    wrapper=dict(material_id='benchmark-'+name,world=new_state(scene));tracemalloc.start()
    start=time.perf_counter();payload=runtime.world_payload(scene,wrapper);cold=(time.perf_counter()-start)*1000
    peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();hot=[];commits=[]
    for i in range(7):
        start=time.perf_counter();runtime.world_payload(scene,wrapper);hot.append((time.perf_counter()-start)*1000)
        state=wrapper['world'];target=world.targets(scene,state)[0]
        event=dict(scene=payload['identity'],revision=state['revision'],token='bench'+str(i),kind='manipulate',target=target['id'],x=target['position'][0],y=target['position'][1],time=state['time'])
        start=time.perf_counter();assert world.commit(scene,state,payload['identity'],event);commits.append((time.perf_counter()-start)*1000)
    rows.append(dict(case=name,cold_payload_ms=cold,hot_payload_median_ms=statistics.median(hot),exact_commit_median_ms=statistics.median(commits),python_allocation_peak_bytes=peak,payload_bytes=len(json.dumps(payload,ensure_ascii=False).encode())))
demo=math_demo();saved=dict(values=default_values(demo));tracemalloc.start();start=time.perf_counter()
payload=runtime.lab_payload(demo,saved,'benchmark-math','formal_relation');cold=(time.perf_counter()-start)*1000
peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop();hot=[];commits=[]
for i in range(7):
    start=time.perf_counter();runtime.lab_payload(demo,saved,'benchmark-math','formal_relation');hot.append((time.perf_counter()-start)*1000)
    target=lab.targets(demo,saved['values'],'formal_relation')[0]
    event=dict(scene=payload['identity'],revision=lab.revision(saved),token='bench'+str(i),kind='manipulate',target=target['id'],x=target['position'][0],y=target['position'][1],time=0.)
    start=time.perf_counter();assert lab.commit(demo,saved,payload['identity'],event,'formal_relation',lambda _:True);commits.append((time.perf_counter()-start)*1000)
rows.append(dict(case='math',cold_payload_ms=cold,hot_payload_median_ms=statistics.median(hot),exact_commit_median_ms=statistics.median(commits),python_allocation_peak_bytes=peak,payload_bytes=len(json.dumps(payload,ensure_ascii=False).encode())))
vendor=(ROOT/'manipulation/frontend/jsxgraphcore.js').read_bytes()
result=dict(scope='three synthetic declarations; cold timings include tracemalloc overhead; Python allocation is not process RSS; seven hot repetitions',rows=rows,vendor_bytes=len(vendor),vendor_gzip_bytes=len(gzip.compress(vendor)),model_calls=0)
(ROOT/'docs/day24/performance.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
