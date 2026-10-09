// Isolated Edge, fixed original viewer, numeric fixtures; no model requests.
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const baseline=process.argv.includes('--baseline'),out=path.resolve(__dirname,'../docs/day25');fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1000,height:850}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const html=fs.readFileSync(path.resolve(__dirname,'../source_atlas/frontend/index.html'),'utf8');
 await page.setContent(html);
 const rows=[];
 for(const count of [20,24,60]){
  const payload={identity:'fixture',focus_stamp:'focus',page:1,width:1800,height:2400,
   image:'data:image/svg+xml;base64,'+Buffer.from('<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="2400"><rect width="1800" height="2400" fill="white"/></svg>').toString('base64'),
   selected:null,relevant:[],labels:{},regions:Array.from({length:count},(_,i)=>({region_id:'r'+i,label:'Source '+i,bbox:{x0:.1+(i%4)*.2,x1:.24+(i%4)*.2,y0:.1+Math.floor(i/4)*.035,y1:.125+Math.floor(i/4)*.035},confidence:i%2?'medium':'high',layer:'formulas',type:'formula',related_region_ids:[]}))};
  const render=await page.evaluate(p=>{const start=performance.now();window.dispatchEvent(new MessageEvent('message',{source:parent,data:{type:'streamlit:render',args:{payload:p}}}));return performance.now()-start},payload);
  assert.equal(await page.locator('rect.region').count(),count);
  const result={count,render_ms:render,overlay_bytes:Buffer.byteLength(JSON.stringify(payload.regions)),production_bound:count<=24};
  const selected={...payload,selected:'r'+(count-1)};
  await page.evaluate(p=>window.dispatchEvent(new MessageEvent('message',{source:parent,data:{type:'streamlit:render',args:{payload:p}}})),selected);
  result.programmatic_zoom=Number(await page.locator('#zoom').inputValue());
  await page.locator('rect.active').press('Enter');
  if(!baseline){
   assert(result.programmatic_zoom>1);
   const geometry=await page.evaluate(()=>{const v=document.querySelector('.viewport').getBoundingClientRect(),r=document.querySelector('rect.active').getBoundingClientRect();return {inside:r.top>=v.top-1&&r.bottom<=v.bottom+1&&r.left>=v.left-1&&r.right<=v.right+1}});assert(geometry.inside,'focused bbox inside viewport');
   await page.locator('#zoom').fill('1.5');await page.locator('#zoom').dispatchEvent('input');
   await page.evaluate(p=>window.dispatchEvent(new MessageEvent('message',{source:parent,data:{type:'streamlit:render',args:{payload:p}}})),selected);
   assert.equal(Number(await page.locator('#zoom').inputValue()),1.5,'same render retains user zoom');
   await page.setViewportSize({width:620,height:850});
   await page.locator('#focusRegion').click();
   const bbox=await page.evaluate(()=>{const r=document.querySelector('rect.active'),s=document.getElementById('page').getBoundingClientRect();return [Number(r.getAttribute('x'))/1800, r.getBoundingClientRect().width/s.width]});
   assert(Math.abs(bbox[0]-selected.regions.at(-1).bbox.x0)<1e-12);assert(Math.abs(bbox[1]-(selected.regions.at(-1).bbox.x1-selected.regions.at(-1).bbox.x0))<1e-6);
   await page.evaluate(p=>window.dispatchEvent(new MessageEvent('message',{source:parent,data:{type:'streamlit:render',args:{payload:{...p,page:2,selected:null,regions:[]}}}})),payload);
   assert.equal(await page.locator('rect.region').count(),0);assert.equal(Number(await page.locator('#zoom').inputValue()),1,'page-only opens whole page');
   await page.setViewportSize({width:1000,height:850});
  }
  rows.push(result);
 }
 assert.deepEqual(errors,[]);
 fs.writeFileSync(path.join(out,baseline?'viewer-before.json':'viewer-after.json'),JSON.stringify({scope:'single fixed viewer isolated browser; 60 overlays stress exceeds per-page production bound',rows,errors},null,2));
 console.log(JSON.stringify(rows));await context.close();await browser.close();
})().catch(e=>{console.error(e);process.exitCode=1});
