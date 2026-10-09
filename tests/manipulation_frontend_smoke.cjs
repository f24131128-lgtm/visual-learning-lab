// Fixed application-code execution only, numeric payloads. Not live browser QA.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),path=require('node:path');
const root=path.join(__dirname,'../manipulation/frontend');
const payloads=JSON.parse(fs.readFileSync(0,'utf8'));
const boards=[];let frames=[];
class Point{
 constructor(type,parents,options){this.type=type;this.parents=parents;this.options=options;this.handlers={};this.coords={scrCoords:[1,0,0]};if(type==='point')this.xy=parents.slice();else if(type==='curve'){this.dataX=parents[0];this.dataY=parents[1]}}
 X(){return this.xy[0]}Y(){return this.xy[1]}setPosition(_,xy){this.xy=xy.slice()}
 on(key,fn){this.handlers[key]=fn}setAttribute(){}
}
const JXG={COORDS_BY_USER:1,JSXGraph:{initBoard(id,options){const b={id,options,items:[],origin:{scrCoords:[1,50,80]},unitX:10,unitY:10,create(type,parents,options){const item=new Point(type,parents,options);this.items.push(item);return item},suspendUpdate(){},unsuspendUpdate(){},setBoundingBox(box,equal){this.box=box;this.equal=equal}};boards.push(b);return b},freeBoard(){}}};
const ctx=vm.createContext({console,JXG,getComputedStyle:e=>e.style,requestAnimationFrame:fn=>{frames.push(fn);return frames.length},cancelAnimationFrame:()=>{}});
vm.runInContext(fs.readFileSync(path.join(root,'adapter.js'),'utf8'),ctx);
const D=ctx.DirectManipulation;
for(const p of payloads){
 const original=JSON.parse(JSON.stringify(p));
 const commits=[],previews=[];
 const host={id:'board',addEventListener(){},removeEventListener(){}};
 const c=D.mount(host,p,{commit:e=>commits.push(e),preview:(data,values)=>previews.push({data,values})});
 assert.equal(c.points.size,p.targets.length);
 const target=p.targets[0],handle=c.points.get(target.id);
 const params=Object.fromEntries(p.parameters.map(x=>[x.id,x]));
 handle.handlers.down();
 let expected;
 if(target.inverse.kind==='circular'){
  handle.xy=[target.inverse.origin[0],target.inverse.origin[1]+1];expected={phase:Math.PI/2};
 }else if(target.inverse.kind==='polar'){
  handle.xy=[30*Math.cos(Math.PI/3),30*Math.sin(Math.PI/3)];expected={speed:30,angle:Math.PI/3};
 }else{handle.xy=[target.position[0],2];expected={offset:2}}
 handle.handlers.drag();handle.handlers.drag();
 assert.equal(commits.length,0,'pointer movement must be local');
 for(const f of frames)f();frames=[];
 const inverse=D.inverse(target,params,p.values,...handle.xy);
 for(const [id,v] of Object.entries(expected))assert(Math.abs(inverse[id]-v)<1e-10);
 assert.equal(previews.at(-1).values[Object.keys(expected)[0]],inverse[Object.keys(expected)[0]]);
 const projected=D.interpolate(p.previews[target.id],inverse);assert(projected);
 assert.deepEqual(JSON.parse(JSON.stringify(D.interpolate(p.previews[target.id],p.values))),JSON.parse(JSON.stringify(D.interpolate(p.previews[target.id],p.values))));
 handle.handlers.up();handle.handlers.up();assert.equal(commits.length,1);
 assert.equal(commits[0].target,target.id);assert.equal(commits[0].kind,'manipulate');
 assert(!('semantic_id' in commits[0]));assert(!('patches' in commits[0]));
 // Rejected release: restore every canonical value without replacing the board.
 const mounted=c.board,created=boards.length;
 c.restore(original);
 assert.equal(c.board,mounted);assert.equal(boards.length,created);
 assert(Math.abs(handle.Y()-D.position(target,original.values)[1])<1e-10);
 // Cancel stays cancelled through further pointer motion until a new gesture.
 handle.handlers.down();handle.xy=[target.position[0],1];handle.handlers.drag();c.cancel();
 handle.xy=[target.position[0],2];handle.handlers.drag();handle.handlers.up();
 assert.equal(commits.length,1,'cancelled preview must never commit');
 c.restore(original);
 const accepted=JSON.parse(JSON.stringify(original));accepted.values=inverse;
 accepted.targets=accepted.targets.map(t=>({...t,position:D.position(t,inverse)}));
 c.restore(accepted);
 assert.equal(c.board,mounted);assert.equal(boards.length,created);
 assert(Math.abs(handle.Y()-D.position(target,inverse)[1])<1e-10);
 c.restore(original);
 c.destroy();
 // State -> visual: constructing from the authoritative new values updates it.
 const next=JSON.parse(JSON.stringify(p));next.values=inverse;next.targets[0].position=D.position(target,inverse);
 const d=D.mount(host,next,{commit(){}});
 assert(Math.abs(d.points.get(target.id).Y()-next.targets[0].position[1])<1e-10);d.destroy();
 // Live DOM coordinates include iframe reflow, border, equal-scale origin and
 // optional CSS transform. Fractional unscaled dimensions must stay exact.
 for(const scale of [1,2]){
  let left=21.25,top=74.5;const host2={...host,clientLeft:1,clientTop:1,style:{width:'525.109px',height:'365px',transform:scale===1?'none':'matrix(2,0,0,2,0,0)'},getBoundingClientRect(){return{left,top,width:scale===1?525.109375:1050.218,height:365*scale}}};
  const events=[],e=D.mount(host2,p,{commit:v=>events.push(v)}),q=e.points.get(target.id),desired=D.position(target,inverse);
  q.handlers.down();left+=30;top+=40;
  q.handlers.drag({clientX:left+scale*(1+50+desired[0]*10),clientY:top+scale*(1+80-desired[1]*10)});q.handlers.up();
  assert.equal(events.length,1);assert(Math.abs(events[0].x-desired[0])<1e-10);assert(Math.abs(events[0].y-desired[1])<1e-10);e.destroy();
 }
}
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
assert(!/\beval\s*\(|new Function|\.innerHTML\s*=/.test(fs.readFileSync(path.join(root,'adapter.js'),'utf8')+html));
assert(html.includes("event.source!==parent"));assert(html.includes('next.ack'));assert(html.includes('Tentative preview'));
console.log('Direct manipulation fixed-code smoke passed: 3 cases, local motion, release-only commit, inverse and state sync.');
