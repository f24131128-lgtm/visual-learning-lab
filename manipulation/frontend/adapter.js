/* Independent fixed public-API adapter. Numeric parents only; no model programs. */
(function(global){
"use strict";
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const angle=(v,offset,scale,p,current)=>{
 const solutions=[];
 for(let k=-128;k<=128;k++){const n=(v-offset+2*Math.PI*k)/scale;if(n>=p.min-1e-12&&n<=p.max+1e-12)solutions.push(clamp(n,p.min,p.max))}
 if(!solutions.length)return null;
 return solutions.reduce((best,n)=>Math.abs(n-current)<Math.abs(best-current)?n:best,solutions[0]);
};
function inverse(target,parameters,values,x,y){
 const m=target.inverse,out={...values};
 if(!Number.isFinite(x)||!Number.isFinite(y))return null;
 if(m.kind==='affine'){
  out[m.parameter_id]=clamp((y-m.offset)/m.scale,parameters[m.parameter_id].min,parameters[m.parameter_id].max);
 }else{
  const dx=x-m.origin[0],dy=y-m.origin[1];if(Math.hypot(dx,dy)<1e-8)return null;
  const a=angle(Math.atan2(dy,dx),m.offset,m.angle_scale,parameters[m.angle_id],values[m.angle_id]);
  if(a===null)return null;out[m.angle_id]=a;
  if(m.kind==='polar')out[m.radius_id]=clamp((Math.hypot(dx,dy)-m.radius_offset)/m.radius_scale,parameters[m.radius_id].min,parameters[m.radius_id].max);
 }
 return out;
}
function position(target,values){
 const m=target.inverse;
 if(m.kind==='affine')return [m.x,m.constant+Object.entries(m.coefficients).reduce((sum,[id,k])=>sum+k*values[id],0)];
 const a=m.angle_scale*values[m.angle_id]+m.offset;
 const r=m.kind==='polar'?m.radius_scale*values[m.radius_id]+m.radius_offset:Math.hypot(target.position[0]-m.origin[0],target.position[1]-m.origin[1]);
 return [m.origin[0]+r*Math.cos(a),m.origin[1]+r*Math.sin(a)];
}
function interpolate(mesh,values){
 if(!mesh)return null;
 const corners=[{index:0,weight:1}];
 for(let axis=0;axis<mesh.axes.length;axis++){
  const xs=mesh.axes[axis],v=clamp(values[mesh.parameter_ids[axis]],xs[0],xs.at(-1));
  const u=(v-xs[0])/(xs.at(-1)-xs[0])*(xs.length-1),lo=Math.min(xs.length-2,Math.floor(u)),w=u-lo;
  const next=[];for(const corner of corners)for(const [i,k] of [[lo,1-w],[lo+1,w]])next.push({index:corner.index*xs.length+i,weight:corner.weight*k});
  corners.splice(0,corners.length,...next);
 }
 function blend(nodes){
  if(Array.isArray(nodes[0]))return nodes[0].map((_,i)=>blend(nodes.map(n=>n[i])));
  if(typeof nodes[0]==='object')return Object.fromEntries(Object.keys(nodes[0]).map(k=>[k,blend(nodes.map(n=>n[k]))]));
  return nodes.reduce((sum,n,i)=>sum+n*corners[i].weight,0);
 }
 return blend(corners.map(c=>mesh.rows[c.index]));
}
function sample(series,times,time){
 if(series.length===1)return series[0];
 const v=clamp(time,times[0],times.at(-1)),i=Math.min(times.length-2,Math.max(0,Math.floor((v-times[0])/(times.at(-1)-times[0])*(times.length-1))));
 const w=(v-times[i])/(times[i+1]-times[i]);return series[i]*(1-w)+series[i+1]*w;
}
function bounds(data,targets){
 const points=targets.flatMap(t=>[[t.bounds[0],t.bounds[1]],[t.bounds[2],t.bounds[3]]]);
 for(const rows of Object.values(data.objects)){
  for(let i=0;i<rows[0].length;i++){
   points.push([rows[0][i],rows[1][i]]);
   if(rows.length===4)points.push([rows[0][i]+rows[2][i],rows[1][i]+rows[3][i]]);
  }
 }
 for(const curve of Object.values(data.curves))if(!Array.isArray(curve))for(let i=0;i<curve.x.length;i++)points.push([curve.x[i],curve.y[i]]);
 const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]);
 let x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 const xp=Math.max((x1-x0)*.1,.25),yp=Math.max((y1-y0)*.1,.25);
 return [x0-xp,y1+yp,x1+xp,y0-yp];
}
function makeBoard(element,box,equal){
 return global.JXG.JSXGraph.initBoard(element.id,{boundingbox:box,keepaspectratio:equal,axis:true,
  showCopyright:false,showLogo:false,showNavigation:false,pan:{enabled:false},zoom:{enabled:false},
  keyboard:{enabled:true,dx:8,dy:8},resize:{enabled:true},renderer:'svg',
  defaultAxes:{x:{ticks:{drawLabels:true,majorHeight:8,minorTicks:0}},y:{ticks:{drawLabels:true,majorHeight:8,minorTicks:0}}}});
}
function mount(element,payload,hooks){
 const p=payload,parameters=Object.fromEntries(p.parameters.map(v=>[v.id,v])),points=new Map(),curves=new Map(),objects=new Map(),labels=new Map();
 let values={...p.values},data=p.current,active=null,frame=0,blocked=false;
 const colors=['#6750c5','#087e8b','#b85b17','#4262ad'];
 const visibleObjects=p.objects.filter(o=>p.targets.some(t=>t.object_id===o.id));
 const viewData={...data,objects:Object.fromEntries(visibleObjects.map(o=>[o.id,data.objects[o.id]])),curves:p.objects.length?{}:data.curves};
 const fitTargets=p.objects.length?p.targets:p.targets.map(t=>({...t,bounds:[...t.position,...t.position]}));
 const board=makeBoard(element,bounds(viewData,fitTargets),true);
 const numericPoint=xy=>board.create('point',xy,{fixed:true,visible:false,withLabel:false,name:''});
 for(const [n,obj] of visibleObjects.entries()){
  const rows=data.objects[obj.id],col=colors[n%colors.length];
  if(obj.type==='trajectory')objects.set(obj.id,board.create('curve',[rows[0],rows[1]],{strokeColor:col,strokeWidth:2.5,highlight:false,withLabel:false}));
  else if(obj.type==='vector'||obj.type==='axis'){
   const a=numericPoint([rows[0][0],rows[1][0]]),b=numericPoint([rows[0][0]+rows[2][0],rows[1][0]+rows[3][0]]);
   const line=board.create(obj.type==='vector'?'arrow':'segment',[a,b],{strokeColor:col,strokeWidth:3,highlight:false});
   objects.set(obj.id,{a,b,line,axis:obj.type==='axis'});
  }else objects.set(obj.id,board.create('point',[rows[0][0],rows[1][0]],{size:4,fixed:true,withLabel:false,fillColor:col,strokeColor:col,name:''}));
 }
 for(const [n,curve] of p.curves.entries()){
  const row=data.curves[curve.id];if(Array.isArray(row))continue;
  curves.set(curve.id,board.create('curve',[row.x,row.y],{strokeColor:colors[n%colors.length],strokeWidth:3,highlight:false,withLabel:false}));
 }
 function update(){
  board.suspendUpdate();
  for(const obj of visibleObjects){
   const rows=data.objects[obj.id],render=objects.get(obj.id),nums=!active&&p.committed?p.committed.objects[obj.id]:rows.map(row=>sample(row,data.times,p.time));
   if(obj.type==='trajectory'){render.dataX=rows[0];render.dataY=rows[1]}
   else if(render.a){render.a.setPosition(global.JXG.COORDS_BY_USER,nums.slice(0,2));render.b.setPosition(global.JXG.COORDS_BY_USER,[nums[0]+nums[2],nums[1]+nums[3]])}
   else render.setPosition(global.JXG.COORDS_BY_USER,nums.slice(0,2));
  }
  for(const curve of p.curves){const row=data.curves[curve.id],render=curves.get(curve.id);if(render){render.dataX=row.x;render.dataY=row.y}}
  for(const target of p.targets){const point=points.get(target.id);if(target.id!==active?.id)point.setPosition(global.JXG.COORDS_BY_USER,position(target,values))}
  board.unsuspendUpdate();hooks.preview?.(data,values,Boolean(active));
  for(const [id,label] of labels){const q=points.get(id);label.style.left=(q.coords.scrCoords[1]+12)+'px';label.style.top=(q.coords.scrCoords[2]-22)+'px'}
 }
 function finish(){
  if(!active||blocked)return;
  const target=active,xy=position(target,values);active=null;blocked=true;
  for(const point of points.values())point.setAttribute({fixed:true});
  cancelAnimationFrame(frame);frame=0;
  // Send only one bounded semantic gesture on release, not arbitrary patches.
  hooks.commit({kind:'manipulate',target:target.id,x:xy[0],y:xy[1],time:p.time});
 }
 for(const target of p.targets){
  const point=board.create('point',target.position,{name:'',withLabel:false,size:8,face:'o',fixed:false,
   fillColor:'#6750c5',strokeColor:'white',strokeWidth:3,highlightFillColor:'#b59aff',highlightStrokeColor:'#6750c5',highlightSize:11,
   snapToGrid:false,showInfobox:false,ariaLabel:target.label});
  points.set(target.id,point);
  if((p.focused_target_ids||[]).includes(target.id))point.setAttribute({fillColor:'#087e8b',strokeColor:'#ffd166',strokeWidth:4});
  // Plain DOM text bypasses the library's text/JessieCode/markup facilities.
  if(global.document){const label=global.document.createElement('span');label.textContent=target.label;label.style.cssText='position:absolute;pointer-events:none;font:13px system-ui;color:#6750c5';element.append(label);labels.set(target.id,label)}
  point.rendNode?.setAttribute('aria-label',target.label);
  point.on('down',()=>{if(blocked)return;active=target;hooks.begin?.(target)});
  function move(event){
   if(blocked)return;if(!active)active=target;
   let x=point.X(),y=point.Y();
   if(event&&Number.isFinite(event.clientX)&&Number.isFinite(event.clientY)){
    // Streamlit can move the iframe while acknowledging focus. Use the live
    // DOM transform rather than the library's pointer-down offset cache.
    // origin/unit account for equal-scale board letterboxing; CSS borders and
    // scale are removed before converting to physical coordinates.
    const rect=element.getBoundingClientRect(),style=global.getComputedStyle(element);
    const sx=style.transform==='none'?1:rect.width/parseFloat(style.width),sy=style.transform==='none'?1:rect.height/parseFloat(style.height);
    const px=(event.clientX-rect.left)/sx-element.clientLeft,py=(event.clientY-rect.top)/sy-element.clientTop;
    x=(px-board.origin.scrCoords[1])/board.unitX;y=(board.origin.scrCoords[2]-py)/board.unitY;
   }
   const next=inverse(target,parameters,p.values,x,y);
   if(!next){point.setPosition(global.JXG.COORDS_BY_USER,position(target,values));return}
   values=next;point.setPosition(global.JXG.COORDS_BY_USER,position(target,values));
   const projected=interpolate(p.previews[target.id],values);if(projected)data=projected;
   // Stable gesture viewport; the separate linked view fits complete paths.
   if(!frame)frame=requestAnimationFrame(()=>{frame=0;update()});
  }
  point.on('drag',move);point.on('up',finish);
  point.on('keydrag',()=>{active=target;move();finish()});
 }
 const cancel=()=>{if(blocked)return;active=null;values={...p.values};data=p.current;update()};
 const setFocus=ids=>{for(const [id,point]of points)point.setAttribute(ids.includes(id)?{fillColor:'#087e8b',strokeColor:'#ffd166',strokeWidth:4}:{fillColor:'#6750c5',strokeColor:'white',strokeWidth:3})};
 element.addEventListener('pointercancel',cancel);
 const escape=e=>{if(e.key==='Escape')cancel()};
 element.addEventListener('keydown',escape);
 update();
 return {board,points,update,finish,cancel,setFocus,destroy(){cancelAnimationFrame(frame);element.removeEventListener('pointercancel',cancel);element.removeEventListener('keydown',escape);for(const label of labels.values())label.remove();global.JXG.JSXGraph.freeBoard(board)}};
}
global.DirectManipulation={mount,inverse,position,interpolate,sample,bounds};
})(globalThis);
