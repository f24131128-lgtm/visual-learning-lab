// Execute fixed source viewer code against a DOM spy, not model code.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2],'utf8'),script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
class E{constructor(){this.children=[];this.attrs={};this.style={};this.value='';this.checked=false;}
 setAttribute(k,v){this.attrs[k]=v}appendChild(e){this.children.push(e)}replaceChildren(){this.children=[]}scrollTo(){} }
const nodes=new Map(),el=id=>{if(!nodes.has(id))nodes.set(id,new E());return nodes.get(id)};
el('zoom').value='1';const messages=[],parent={postMessage:m=>messages.push(m)},handlers={};
const context=vm.createContext({document:{getElementById:el,createElementNS:()=>new E(),createElement:()=>new E(),querySelector:()=>new E()},parent,window:{addEventListener:(k,f)=>handlers[k]=f},Date,Math});
vm.runInContext(script,context);const payload=JSON.parse(fs.readFileSync(0,'utf8'));
const render=()=>handlers.message({source:parent,data:{type:'streamlit:render',args:{payload}}});render();
assert(messages.some(m=>m.type==='streamlit:componentReady'));
assert(el('overlays').children.length===payload.regions.length);
assert(el('original').attrs.href.startsWith('data:image/png;base64,'));
const rect=el('overlays').children[0],box=payload.regions[0].bbox;
assert.equal(rect.attrs.x,box.x0*payload.width);assert.equal(rect.attrs.y,box.y0*payload.height);
el('zoom').value='2';el('zoom').oninput();assert.equal(el('page').style.width,'200%');
let count=messages.length;el('layer').value='vectors';el('layer').oninput();assert(messages.length===count);
assert(el('overlays').children.every(e=>e.attrs['aria-label'].includes('phasor')));
el('hideLabels').checked=true;el('hideLabels').oninput();
const mask=el('overlays').children.find(e=>e.attrs.class.includes('mask'));assert(mask);
mask.onclick();assert.equal(messages.length,count);assert(!el('overlays').children.some(e=>e.attrs.class.includes('mask')));
el('reset').onclick();assert.equal(el('zoom').value,'1');assert.equal(el('hideLabels').checked,false);
el('overlays').children[0].onkeydown({key:'Enter',preventDefault(){}});
const event=messages.at(-1).value;assert.equal(event.region_id,payload.regions[0].region_id);assert.equal(event.atlas,payload.identity);assert.equal(event.focus_stamp,payload.focus_stamp);
count=messages.length;el('overlays').children[1].onclick();assert.equal(messages.length,count); // Pending/duplicate gate.
render();assert.equal(el('zoom').value,'1');
console.log('Source viewer coordinate/layer/zoom/mask/keyboard/protocol smoke passed');
