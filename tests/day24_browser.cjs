/* Isolated headless Edge, localhost only, fresh temp profile, no personal data.
 * Usage: NODE_PATH=<bundled modules> node tests/day24_browser.cjs payloads.json
 */
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'../manipulation/frontend'),payloads=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const html=`<!doctype html><body style="margin:0"><iframe id="component" src="/index.html" style="border:0;width:1100px;height:650px"></iframe><script>
window.received=[];window.send=p=>{window.current=p;document.querySelector('iframe').contentWindow.postMessage({type:'streamlit:render',args:{payload:p}},'*')};
window.addEventListener('message',e=>{if(e.data.type==='streamlit:setComponentValue'){window.received.push(e.data.value);if(e.data.value.kind==='manipulation_focus')send({...current,revision:current.revision+1,ack:e.data.value.token})}});
</script></body>`;
const server=http.createServer((req,res)=>{
 if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end(html);return}
 const name=path.basename(req.url.split('?')[0]);
 if(!['index.html','jsxgraphcore.js','jsxgraph.css','adapter.js'].includes(name)){res.writeHead(404);res.end();return}
 res.setHeader('Content-Type',name.endsWith('.js')?'application/javascript':name.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(path.join(root,name)));
});
(async()=>{
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1200,height:850}});const page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:'+server.address().port);const frame=await page.waitForSelector('iframe').then(e=>e.contentFrame());
  const results=[];
  for(let i=0;i<payloads.length;i++){
   const p=payloads[i];await page.evaluate(p=>{window.received=[];send(p)},p);
   await frame.waitForFunction(()=>typeof controller!=='undefined'&&controller?.points.size>0);
   const t=p.targets[0];
   const desired=t.inverse.kind==='circular'?[0,1]:t.inverse.kind==='polar'?[30*Math.cos(Math.PI/3),30*Math.sin(Math.PI/3)]:[t.position[0],2];
   const xy=await frame.evaluate(({id,desired})=>{
    const r=document.getElementById('board').getBoundingClientRect(),b=controller.board,pt=controller.points.get(id);
    const host=document.getElementById('board');return {start:[r.left+host.clientLeft+pt.coords.scrCoords[1],r.top+host.clientTop+pt.coords.scrCoords[2]],end:[r.left+host.clientLeft+b.origin.scrCoords[1]+desired[0]*b.unitX,r.top+host.clientTop+b.origin.scrCoords[2]-desired[1]*b.unitY],units:[b.unitX,b.unitY]};
   },{id:t.id,desired});
   assert(Math.abs(xy.units[0]-xy.units[1])<1e-8,'equal physical scale');
   const box=await page.locator('iframe').boundingBox();
   await page.mouse.move(box.x+xy.start[0],box.y+xy.start[1]);await page.mouse.down();
   const start=Date.now();await page.mouse.move(box.x+xy.end[0],box.y+xy.end[1],{steps:14});
   assert.equal((await page.evaluate(()=>received.filter(e=>e.kind==='manipulate'))).length,0,'no value commits on pointermove');
   await page.mouse.up();await page.waitForFunction(()=>received.filter(e=>e.kind==='manipulate').length===1);
   const events=await page.evaluate(()=>received),ev=events.find(e=>e.kind==='manipulate');
   assert.equal(events.filter(e=>e.kind==='manipulation_focus').length,1,'one canonical focus begin');
   assert.equal(ev.target,t.id);assert.equal(ev.kind,'manipulate');
   assert(Math.abs(ev.x-desired[0])<.2&&Math.abs(ev.y-desired[1])<.2,JSON.stringify(ev));
   await page.screenshot({path:path.resolve(__dirname,`../docs/day24/browser-case-${i+1}.png`),fullPage:true});
   // Backend rejection returns authoritative unchanged values and new revision.
   await page.evaluate(p=>send({...p,revision:p.revision+2,ack:'rejected'}),p);
   await frame.waitForFunction(rev=>P.revision===rev&&!pending,p.revision+2);
   const restored=await frame.evaluate(id=>{const q=controller.points.get(id);return [q.X(),q.Y()]},t.id);
   assert(Math.abs(restored[0]-t.position[0])<1e-8&&Math.abs(restored[1]-t.position[1])<1e-8);
   results.push({case:i+1,event:ev,drag_ms:Date.now()-start,value_commits:1,focus_commits:1,move_commits:0,rejection_restored:true});
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.resolve(__dirname,'../docs/day24/browser-results.json'),JSON.stringify({profile:'fresh isolated headless Edge',results,page_errors:errors},null,2));
  console.log('Actual JSXGraph browser pointer drags passed for three cases; no pointermove commits; rejection restores canonical positions.');
 }finally{await context.close();await browser.close();await new Promise(resolve=>server.close(resolve))}
})().catch(e=>{console.error(e);process.exitCode=1;server.close()});
