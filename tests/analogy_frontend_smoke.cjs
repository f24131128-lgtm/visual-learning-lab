// Fixed-code smoke, separate evidence from a real browser and live AI grounding.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
assert(!/eval\s*\(|new Function|innerHTML/.test(script));
class Element{
 constructor(){this.attrs={};this.style={};this.events={};this.children=[];this.textContent='';}
 setAttribute(k,v){this.attrs[k]=String(v)} appendChild(c){this.children.push(c)} replaceChildren(){this.children=[]}
 addEventListener(k,v){this.events[k]=v} setPointerCapture(){}
 createSVGPoint(){return {x:0,y:0,matrixTransform(m){return m.transform(this)}}}
 getScreenCTM(){return {inverse(){return {transform:p=>({x:(p.x-100)/50-4,y:p.y/50})}}}}
}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id)},messages=[],handlers={};
const parent={postMessage:m=>messages.push(m)};
const context=vm.createContext({document:{getElementById:node,createElementNS:()=>new Element()},parent,window:{addEventListener:(k,v)=>handlers[k]=v},requestAnimationFrame:()=>1,performance:{now:()=>0},console});
vm.runInContext(script,context);const inspect=s=>vm.runInContext(s,context);
assert(messages.some(m=>m.type==='streamlit:componentReady'));
const cases=JSON.parse(fs.readFileSync(0,'utf8'));
for(const p of cases){
 const render=next=>handlers.message({source:parent,data:{type:'streamlit:render',args:{payload:next}}});render(p);
 assert(node('stage').children.length>=p.data.objects.filter(o=>o.data.visible[0]>=.5).length);
 assert(node('stage').children.some(n=>n.attrs.role==='button'));
 node('play').onclick();inspect('tick(1500)');const frame=inspect('frame');assert(frame>0);
 render(p);assert.equal(inspect('frame'),frame);assert(inspect('playing'));
 node('play').onclick();assert(!inspect('playing'));
 node('replay').onclick();assert.equal(inspect('frame'),0);
 node('scrub').oninput({target:{value:'10'}});assert.equal(inspect('frame'),10);assert(!inspect('playing'));
 const shape=node('stage').children.find(n=>n.attrs.role==='button');shape.events.keydown({key:'Enter',preventDefault(){}});
 assert.equal(messages.at(-1).value.kind,'focus');assert.equal(messages.at(-1).dataType,'json');
 render(p);const control=p.data.objects.find(o=>o.control_parameter&&o.data.visible[0]>=.5);
 if(control){const handle=node('stage').children.find(n=>n.attrs['aria-label']===control.label&&n.attrs.role==='button');handle.events.pointerdown({clientX:200,clientY:100,pointerId:1});node('stage').events.pointerup({clientX:400,clientY:100});assert.equal(messages.at(-1).value.kind,'parameter');const param=p.parameters.find(a=>a.id===control.control_parameter);assert(messages.at(-1).value.value>=param.min&&messages.at(-1).value.value<=param.max);}
 const old=inspect('payload.identity');handlers.message({source:{},data:{type:'streamlit:render',args:{payload:{...p,identity:'hostile'}}}});assert.equal(inspect('payload.identity'),old);
 render({...p,numeric_identity:p.numeric_identity+'-changed'});assert.equal(inspect('frame'),0);assert(!inspect('playing'));
}
console.log('Analogy frontend smoke passed: three domains, numeric geometry, clock, layout, selection, gestures, transport.');
