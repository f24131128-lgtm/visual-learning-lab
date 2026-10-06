// Fixed production frontend smoke: singleton parameter is an output, never a range.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
class Element {
 constructor(tag=''){this.tag=tag;this.children=[];this.style={};this.events={};this.viewBox={baseVal:{width:520,height:300}};}
 append(...items){this.children.push(...items)} replaceChildren(...items){this.children=items}
 setAttribute(){} addEventListener(k,v){this.events[k]=v}
 getBoundingClientRect(){return {left:0,top:0,width:520,height:300}}
}
const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id)};
node('speed').value='1';node('replaySpeed').value='1';
const handlers={},messages=[],parent={postMessage:m=>messages.push(m)};
const ctx=vm.createContext({document:{getElementById:node,createElementNS:(_,t)=>new Element(t),createElement:t=>new Element(t),body:{scrollHeight:650}},
 parent,window:{addEventListener:(k,v)=>handlers[k]=v},ResizeObserver:class {observe(){}},
 requestAnimationFrame:()=>1,cancelAnimationFrame(){},setTimeout:()=>1,clearTimeout(){},performance:{now:()=>0},console});
const html=fs.readFileSync(process.argv[2],'utf8');vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],ctx);
const payload=JSON.parse(fs.readFileSync(0,'utf8'));
handlers.message({source:parent,data:{type:'streamlit:render',args:{payload}}});
const controls=node('parameters').children;
assert.equal(controls.length,1);assert.equal(controls[0].children[1].tag,'output');
assert.equal(Object.keys(controls[0].children[1].events).length,0);
assert(messages.some(m=>m.type==='streamlit:componentReady'));
console.log('Phase C fixed parameter frontend smoke passed');
