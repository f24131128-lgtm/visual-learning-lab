// Fixed frontend code smoke tests, not a replacement for browser/live acceptance.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync(process.argv[2], 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
// Browser globals include unforgeable names that a standalone syntax parse misses.
assert(!/function\s+(location|window|document|top|parent)\b/.test(script));
class Element {
  constructor(name='') { this.name=name; this.children=[]; this.attrs={}; this.style={}; this.events={}; this.textContent=''; this.viewBox={baseVal:{width:520,height:name==='waves'?260:300}}; }
  append(...items){this.children.push(...items)}
  replaceChildren(...items){this.children=items}
  setAttribute(key,value){this.attrs[key]=String(value)}
  addEventListener(key,value){this.events[key]=value}
  setPointerCapture(){} releasePointerCapture(){}
  getBoundingClientRect(){return {left:0,top:0,width:520,height:this.viewBox.baseVal.height}}
}
const nodes = new Map();
const node = id => {if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id)};
node('speed').value='1';
node('replaySpeed').value='1';
const cameraCalls=[];
const messages=[],handlers={};
const parent={postMessage:message=>messages.push(message)};
const context=vm.createContext({document:{getElementById:node,createElementNS:(_,tag)=>new Element(tag),createElement:tag=>new Element(tag),body:{scrollHeight:650}},parent,
  window:{addEventListener:(type,callback)=>handlers[type]=callback}, ResizeObserver:class {observe(){}},
  requestAnimationFrame:()=>1,cancelAnimationFrame:()=>{},setTimeout:()=>1,clearTimeout:()=>{},performance:{now:()=>0},console,
  Plotly:{react:(element,traces,layout)=>{cameraCalls.push({traces,layout});return null}},
  Promise:{resolve:()=>({then:fn=>{fn();return {catch(){}}}})}});
vm.runInContext(fs.readFileSync(require('node:path').join(require('node:path').dirname(process.argv[2]),'camera.js'),'utf8'),context);
vm.runInContext(script,context);
assert(messages.some(message=>message.type==='streamlit:componentReady'));
const inputs=JSON.parse(fs.readFileSync(0,'utf8'));
const inspect=source=>vm.runInContext(source,context);
assert(inspect('(()=>{const c=coords({x_min:-4,x_max:4,y_min:-4,y_max:4});return Math.abs((c.x(2)-c.x(0))-(c.y(0)-c.y(2)))<1e-10})()'));
let renderRevision=0;
const render=payload=>handlers.message({source:parent,data:{type:'streamlit:render',args:{payload:{...payload,revision:++renderRevision}}}});
for(const input of inputs){
  const payload=input.normal;
  render(payload);
  assert.equal(node('recordPanel').hidden,true);
  assert.equal(node('cameraControls').hidden,true);
  assert(node('space').children.length>10);
  assert(node('waves').children.length>10);
  assert(node('vectors').children.length>5);
  assert(node('metrics').children.length===payload.parameters.length+payload.metrics.length);
  assert.equal(inspect('speed(99)'),1);assert.equal(inspect('speed(".5")'),.5);
  assert.equal(inspect('replayDwell(".5")'),3600);assert.equal(inspect('replayDwell("2")'),900);
  node('play').onclick();inspect('tick(64);tick(128);tick(192)');
  assert(inspect('S.time')>0);
  const runningTime=inspect('S.time');
  handlers.message({source:parent,data:{type:'streamlit:render',args:{payload:{...payload,revision:renderRevision}}}});
  assert.equal(inspect('S.time'),runningTime);assert(inspect('playing'));
  // Accessible recording callbacks may change metadata without a physical
  // patch; these must not be mistaken for identical iframe layout messages.
  handlers.message({source:parent,data:{type:'streamlit:render',args:{payload:{...payload,revision:renderRevision,recording:{active:true,count:0}}}}});
  assert(inspect('P.recording.active'));
  handlers.message({source:parent,data:{type:'streamlit:render',args:{payload:{...payload,revision:renderRevision}}}});
  node('play').onclick();inspect('tick(64);tick(128);tick(192)');
  const current=inspect('JSON.stringify(S)');
  const state=JSON.parse(current);
  const timeIndex=payload.tables[payload.data.frames_ref].times.indexOf(state.time);
  for(const series of payload.series) assert.equal(state.projections[series.id][0],payload.tables[payload.data.frames_ref].projections[series.id][0][timeIndex]);
  node('pause').onclick();assert.equal(messages.at(-1).value.kind,'patch');assert.equal(messages.at(-1).dataType,'json');
  render(payload);node('cameraToggle').onclick();
  node('play').onclick();inspect('tick(100);tick(200);tick(300)');
  const cameraState=JSON.parse(inspect('JSON.stringify(S)'));
  const vector=payload.objects.find(o=>o.type==='vector');
  if(vector){const trace=cameraCalls.at(-1).traces.find(trace=>trace.uid===vector.id);assert.equal(trace.x[1],cameraState.projections[vector.id][0]+cameraState.projections[vector.id][2]);}
  assert.equal(node('timeline').value,cameraState.time);
  assert.equal(node('timeline').max,cameraState.domain.max);
  node('pause').onclick();node('cameraToggle').onclick();
  render(payload);node('play').onclick();inspect('tick(64);tick(128);tick(192)');
  const displayedTime=inspect('S.time');
  node('baselineSet').onclick();assert.equal(messages.at(-1).value.time,displayedTime);assert.equal(messages.at(-1).value.kind,'baseline');
  render(payload);node('play').onclick();inspect('tick(64);tick(128);tick(192)');
  node('legend').children[0].onclick();assert.equal(messages.at(-1).value.kind,'focus');assert(messages.at(-1).value.time>0);
  render(payload);
  const inputControl=node('parameters').children[0].children[1];inputControl.value=payload.parameters[0].display.max;inputControl.onchange();
  assert.equal(messages.at(-1).value.kind,'batch');assert.equal(messages.at(-1).value.patches[1].target_id,payload.parameters[0].id);
  render(payload);node('recordStart').onclick();assert.equal(messages.at(-1).value.kind,'record');assert.equal(messages.at(-1).value.action,'start');
  if(payload.experiments.length){render(payload);node('experimentChoice').value=payload.experiments[0].id;node('experimentRun').onclick();assert.equal(messages.at(-1).value.kind,'experiment');}
  render(payload);
  node('waves').onclick({clientX:260,clientY:100,stopPropagation(){}});
  assert(messages.at(-1).value.patch.value>payload.time.min);
  render(payload);
  const inv=payload.inverse.find(binding=>binding.type==='angle_to_time');
  if(inv){
    const object=payload.objects.find(object=>object.id===inv.object_id);
    const handle=node('space').children.find(child=>child.attrs['aria-label']===object.label);
    handle.events.pointerdown({pointerId:1,preventDefault(){},stopPropagation(){}});
    node('space').onpointermove({pointerId:1,clientX:260,clientY:80});
    node('space').onpointerup({pointerId:1});
    assert.equal(messages.at(-1).value.kind,'inverse');
    assert(Math.abs(messages.at(-1).value.value-Math.PI/2)<1e-8);
  }
  const cleared=structuredClone(payload);
  cleared.revision+=1;
  cleared.data.current.focus=null;
  render(cleared);
  assert.equal(node('equations').children.length,0);
  render(input.replay);
  inspect('tick(1000)');assert.equal(inspect('replayIndex'),0);
  inspect('tick(1900)');
  assert.equal(inspect('S.time'),input.replay.replay[1].current.time);
  assert(node('status').textContent.includes('2'));
  inspect('tick(3800)');
  assert.equal(messages.at(-1).value.kind,'replay');
  assert.equal(messages.at(-1).value.index,input.replay.replay_indices.at(-1));
}
console.log('Frontend smoke: numeric systems, synchronized camera/clock, waveform, inverse gesture and paced replay passed.');
