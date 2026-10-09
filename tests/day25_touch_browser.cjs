// Bounded touch emulation; not a real-device ergonomics or canonical-Python test.
const fs=require('node:fs'),path=require('node:path'),http=require('node:http'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),payload=JSON.parse(fs.readFileSync(path.join(root,'docs/day24/payloads.json'),'utf8'))[0];
const html=`<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1"><body style="margin:0"><iframe src="/source/index.html" id="source" style="width:100%;height:660px;border:0"></iframe><iframe src="/direct/index.html" id="direct" style="width:100%;height:800px;border:0"></iframe><div style="height:300px">Outside component scroll</div><script>window.events=[];window.current=null;window.post=p=>{current=p;document.getElementById('direct').contentWindow.postMessage({type:'streamlit:render',args:{payload:p}},'*')};window.addEventListener('message',e=>{if(e.data.type==='streamlit:setComponentValue'){events.push(e.data.value);if(e.data.value.kind==='manipulation_focus')post({...current,revision:current.revision+1})}})</script>`;
const server=http.createServer((req,res)=>{
 if(req.url==='/'){res.setHeader('Content-Type','text/html');res.end(html);return}
 const match=req.url.match(/^\/(source|direct)\/(index.html|adapter.js|jsxgraphcore.js|jsxgraph.css)$/);
 if(!match){res.writeHead(404);res.end();return}
 res.setHeader('Content-Type',match[2].endsWith('.js')?'application/javascript':match[2].endsWith('.css')?'text/css':'text/html');
 res.end(fs.readFileSync(path.join(root,match[1]==='source'?'source_atlas/frontend':'manipulation/frontend',match[2])));
});
(async()=>{
 await new Promise(r=>server.listen(0,'127.0.0.1',r));const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto('http://127.0.0.1:'+server.address().port);
  const sf=await page.locator('#source').elementHandle().then(e=>e.contentFrame());
  await sf.waitForFunction(()=>typeof draw==='function');
  await page.evaluate(()=>document.getElementById('source').contentWindow.postMessage({type:'streamlit:render',args:{payload:{identity:'touch-source',focus_stamp:'focus',page:1,width:600,height:760,image:'data:image/svg+xml;base64,'+btoa('<svg xmlns="http://www.w3.org/2000/svg" width="600" height="760"><rect width="600" height="760" fill="white"/></svg>'),selected:null,relevant:[],labels:{},regions:[{region_id:'source',label:'Original source',type:'formula',layer:'formulas',confidence:'high',bbox:{x0:.1,y0:.15,x1:.8,y1:.35},related_region_ids:[]}]}}},'*'));
  await sf.locator('rect.region').tap();await page.waitForFunction(()=>events.some(e=>e.region_id==='source'));assert.equal((await page.evaluate(()=>events)).find(e=>e.region_id==='source').region_id,'source');
  const df=await page.locator('#direct').elementHandle().then(e=>e.contentFrame());await df.waitForFunction(()=>typeof DirectManipulation!=='undefined');
  await page.evaluate(p=>post(p),payload);await df.waitForFunction(()=>controller?.points.size>0);
  await page.locator('#direct').scrollIntoViewIfNeeded();
  await df.evaluate(()=>new Promise(resolve=>{let n=0;const settled=()=>++n===8?resolve():requestAnimationFrame(settled);requestAnimationFrame(settled)}));
  const coordinates=await df.evaluate(()=>{const h=document.getElementById('board'),rect=controller.points.get(P.targets[0].id).rendNode.getBoundingClientRect(),r=h.getBoundingClientRect(),b=controller.board;return {start:[rect.left+rect.width/2,rect.top+rect.height/2],end:[r.left+h.clientLeft+b.origin.scrCoords[1],r.top+h.clientTop+b.origin.scrCoords[2]-b.unitY],hit_width:rect.width}});
  const box=await page.locator('#direct').boundingBox(),cdp=await context.newCDPSession(page);
  const point=xy=>({x:box.x+xy[0],y:box.y+xy[1],radiusX:5,radiusY:5,force:1,id:1});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[point(coordinates.start)]});
  await df.waitForFunction(()=>P.revision===1&&!focusPending);
  for(let i=1;i<=8;i++)await cdp.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[point(coordinates.start.map((v,j)=>v+(coordinates.end[j]-v)*i/8))]});
  await cdp.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
  await page.waitForFunction(()=>events.some(e=>e.kind==='manipulate'));
  const ev=(await page.evaluate(()=>events)).find(e=>e.kind==='manipulate');assert(Math.abs(ev.x)<.01&&Math.abs(ev.y-1)<.01,'touch release at upper endpoint');
  const scroll=await page.evaluate(()=>{window.scrollTo(0,document.body.scrollHeight);return window.scrollY});assert(scroll>0);
  assert.deepEqual(errors,[]);
  const result={scope:'isolated 390px mobile/touch emulation, fixed source and existing Day24 numeric payload; no Python reducer claim',source_tap:true,touch_release:ev,handle_hit_width_css_px:coordinates.hit_width,outer_scroll_available:true,page_errors:errors};
  fs.writeFileSync(path.join(root,'docs/day25/touch-results.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
 }finally{await context.close();await browser.close();server.close()}
})().catch(e=>{console.error(e);server.close();process.exitCode=1});
