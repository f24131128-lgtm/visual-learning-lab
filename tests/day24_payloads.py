"""Reproducible offline renderer payload export, no model/source corpus changes."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from manipulation_fixtures import systems,math_demo
from scene.world.state import new_state
from manipulation.runtime import world_payload,lab_payload
from interactive_lab import default_values
target=ROOT/'docs/day24';target.mkdir(exist_ok=True)
payloads=[world_payload(s,dict(material_id='day24-'+str(n),world=new_state(s))) for n,s in enumerate(systems())]
payloads.append(lab_payload(math_demo(),dict(values=default_values(math_demo())),'day24-math','formal_relation'))
(target/'payloads.json').write_text(json.dumps(payloads,ensure_ascii=False),encoding='utf-8')
vendor=ROOT/'manipulation/frontend'
manifest=dict(version='1.13.3',license='MIT (selected dual-license option)',files=[])
for name,url in [('jsxgraphcore.js','https://cdn.jsdelivr.net/npm/jsxgraph@1.13.3/distrib/jsxgraphcore.js'),('jsxgraph.css','https://raw.githubusercontent.com/jsxgraph/jsxgraph/v1.13.3/distrib/jsxgraph.css'),('LICENSE.jsxgraph.txt','https://raw.githubusercontent.com/jsxgraph/jsxgraph/v1.13.3/LICENSE.MIT')]:
 data=(vendor/name).read_bytes();manifest['files'].append(dict(path=name,source=url,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
(vendor/'vendor-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps(dict(payload_bytes=[len(json.dumps(p).encode()) for p in payloads],preview_ready=[sum(v is not None for v in p['previews'].values()) for p in payloads])))
