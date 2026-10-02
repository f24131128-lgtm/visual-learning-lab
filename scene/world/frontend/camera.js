"use strict";
// Fixed renderer code; Plotly is bundled locally, never generated or CDN-loaded.
// The current DSL is planar. Camera rotation does not invent a z coordinate.
globalThis.WorldCamera = (() => {
  let installed = false, busy = false, failed = false, pending = null;
  const escape = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  function render(element, P, D, S, family, color, table, onFocus, onFailure) {
    if (failed) {onFailure();return}
    if (busy) {pending=[element,P,D,S,family,color,table,onFocus,onFailure];return}
    if (!globalThis.Plotly) { failed = true; onFailure(); return; }
    const traces = [];
    function add(obj, data, sampled, ghost) {
      const n = data.projections[obj.id];
      let x, y;
      if (obj.type === "trajectory") [x, y] = sampled.projections[obj.id];
      else if (obj.type === "vector" || obj.type === "axis") {
        const extent = obj.type === "axis" ? 1 : 0;
        x = [n[0]-extent*n[2], n[0]+n[2]]; y = [n[1]-extent*n[3], n[1]+n[3]];
      } else { x = [n[0]]; y = [n[1]]; }
      const co = ghost ? "#8792a7" : color(obj.semantic_id);
      traces.push({type:"scatter3d",uid:obj.id+(ghost?"-baseline":""),x,y,z:x.map(()=>0),
        name:escape(obj.label),mode:obj.type==="point"?"markers":"lines+markers",
        line:{color:co,width:family.has(obj.semantic_id)?7:3},marker:{color:co,size:obj.type==="trajectory"?0:4},
        opacity:ghost?.25:1,showlegend:false,customdata:x.map(()=>ghost?null:obj.semantic_id),
        hovertemplate:escape(obj.label)+"<br>x=%{x:.4g}<br>y=%{y:.4g}<extra></extra>"});
      if (obj.type === "trajectory") traces.push({type:"scatter3d",uid:obj.id+"-cursor"+(ghost?"-baseline":""),
        x:[n[0]],y:[n[1]],z:[0],mode:"markers",marker:{size:6,color:co},opacity:ghost?.25:1,
        customdata:[ghost?null:obj.semantic_id],name:escape(obj.label),showlegend:false,hovertemplate:escape(obj.label)+"<extra></extra>"});
    }
    for (const obj of P.objects) {
      if (D.baseline) add(obj, D.baseline, P.tables[D.baseline_frames_ref], true);
      add(obj, S, table(D), false);
    }
    const a=D.axes, extent=Math.max(a.x_max-a.x_min,a.y_max-a.y_min);
    const layout={height:300,margin:{l:0,r:0,t:0,b:0},uirevision:P.identity,
      scene:{uirevision:P.identity,aspectmode:"data",dragmode:"orbit",
        xaxis:{range:[a.x_min,a.x_max],title:{text:escape(a.x_label)}},
        yaxis:{range:[a.y_min,a.y_max],title:{text:escape(a.y_label)}},
        zaxis:{range:[-extent*.2,extent*.2],title:{text:"z = 0"}}}};
    busy=true;
    const timeout=setTimeout(()=>{if(busy){busy=false;failed=true;pending=null;onFailure()}},3000);
    try {
      Promise.resolve(Plotly.react(element,traces,layout,{responsive:true,displayModeBar:false,displaylogo:false,scrollZoom:true})).then(()=>{
        clearTimeout(timeout);
        if(failed)return;
        busy=false;
        const canvas=element.querySelector?.("canvas");
        if(canvas&&!installed)canvas.addEventListener("webglcontextlost",()=>{failed=true;pending=null;onFailure()});
        if (!installed && element.on) { installed=true; element.on("plotly_click",event=>{
          const id=event.points?.[0]?.customdata;
          if (id) onFocus(id);
        }); }
        if(pending){const latest=pending;pending=null;render(...latest)}
      }).catch(()=>{clearTimeout(timeout);busy=false;failed=true;pending=null;onFailure()});
    } catch (_) {clearTimeout(timeout);busy=false;failed=true;pending=null;onFailure()}
  }
  return {render,isBusy:()=>busy,reset:()=>{failed=false}};
})();
