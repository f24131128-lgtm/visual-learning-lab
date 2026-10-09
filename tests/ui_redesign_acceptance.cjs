// Real Source + JSXGraph iframes, normal app, isolated browser profile.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1450,height:1080}}),page=await context.newPage(),errors=[],rows=[];
 const out=path.resolve(__dirname,'../docs/ui-redesign');fs.mkdirSync(out,{recursive:true});
 page.on('pageerror',e=>errors.push(e.message));
 const source=()=>page.locator('iframe[title="source_atlas.runtime.source_atlas_viewer"]');
 const direct=()=>page.locator('iframe[title="manipulation.runtime.direct_semantic_manipulation"]');
 const idle=()=>page.waitForFunction(()=>document.querySelector('[data-testid=stApp]')?.dataset.testScriptState==='notRunning');
 async function option(name,value){
  const combo=page.getByRole('combobox',{name,exact:true});await combo.waitFor();await idle();
  for(let i=0;i<3;i++){
   await combo.scrollIntoViewIfNeeded();await combo.focus();
   await combo.press('ArrowDown');
   try{await page.getByRole('option',{name:value,exact:true}).waitFor({timeout:2500});break}
   catch(e){if(i===2){await page.screenshot({path:path.join(out,'selector-failure.png')});throw e}}
  }
  await page.getByRole('option',{name:value,exact:true}).click();
 }
 const frameOf=async locator=>{await locator.waitFor({timeout:40000});return (await locator.elementHandle()).contentFrame()};
 async function choosePage(n){await option('來源頁面','第 '+n+' 頁');await idle();}
 async function selectSource(id){
  const f=await frameOf(source());await f.waitForFunction(id=>D?.regions.some(r=>r.region_id===id),id);
  await source().scrollIntoViewIfNeeded();await f.locator('rect.region').filter({has:f.locator('title',{hasText:id==='source_object'?'Source diagram':''})}).count();
  const r=f.locator('rect.region').filter({has:f.locator('title',{hasText:'Source diagram'})});
  if(id==='source_object')await r.click();else await f.locator('rect.region').first().click();
  await f.waitForFunction(id=>D?.selected===id,id);
  return f;
 }
 async function drag(id,desired){
  const f=await frameOf(direct());await f.waitForFunction(()=>controller?.points.size>0);
  await idle();await direct().scrollIntoViewIfNeeded();
  await page.evaluate(async()=>{let previous='',stable=0;for(let i=0;i<90&&stable<8;i++){await new Promise(requestAnimationFrame);const r=document.querySelector('iframe[title="manipulation.runtime.direct_semantic_manipulation"]').getBoundingClientRect(),now=JSON.stringify([r.x,r.y,r.width,r.height]);stable=now===previous?stable+1:0;previous=now}});
  const start=await f.evaluate(id=>{const p=controller.points.get(id),r=p.rendNode.getBoundingClientRect();return {xy:[r.left+r.width/2,r.top+r.height/2],revision:P.revision,focus:P.focused_target_ids}},id);
  assert(start.focus.includes(id),'source focus highlights exact target');
  let host=await direct().boundingBox();await page.mouse.move(host.x+start.xy[0],host.y+start.xy[1]);await page.mouse.down();
  try{await f.waitForFunction(r=>P.revision>r&&!focusPending,start.revision,{timeout:15000})}
  catch(e){console.log(JSON.stringify({stage:'focus_timeout',id,start,diagnostic:await f.evaluate(()=>({revision:P.revision,focusPending,pending,time:P.time}))}));await direct().screenshot({path:path.join(out,'drag-start-failure.png')});throw e}
  await page.evaluate(async()=>{let previous='',stable=0;for(let i=0;i<90&&stable<8;i++){await new Promise(requestAnimationFrame);const r=document.querySelector('iframe[title="manipulation.runtime.direct_semantic_manipulation"]').getBoundingClientRect(),now=JSON.stringify([r.x,r.y,r.width,r.height]);stable=now===previous?stable+1:0;previous=now}});
  const end=await f.evaluate(xy=>{const h=document.getElementById('board'),r=h.getBoundingClientRect(),b=controller.board;return [r.left+h.clientLeft+b.origin.scrCoords[1]+xy[0]*b.unitX,r.top+h.clientTop+b.origin.scrCoords[2]-xy[1]*b.unitY]},desired);
  host=await direct().boundingBox();await page.mouse.move(host.x+end[0],host.y+end[1],{steps:14});
  // The normal app may scroll/resize the iframe during tentative preview.
  // Finish at a live DOM coordinate, rather than a stale scripted screen point.
  for(let i=0;i<3;i++){
   await f.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
   const live=await f.evaluate(xy=>{const h=document.getElementById('board'),r=h.getBoundingClientRect(),b=controller.board;return [r.left+h.clientLeft+b.origin.scrCoords[1]+xy[0]*b.unitX,r.top+h.clientTop+b.origin.scrCoords[2]-xy[1]*b.unitY]},desired);
   host=await direct().boundingBox();await page.mouse.move(host.x+live[0],host.y+live[1]);
  }
  await page.mouse.up();
  await f.waitForFunction(r=>P.revision>=r+2&&!pending&&!focusPending,start.revision,{timeout:30000});
  await idle();
  return {frame:f,result:await f.evaluate(()=>({values:P.values,metrics:P.committed?.metrics,focus:P.focused_target_ids,targets:P.targets}))};
 }
 try{
  await page.goto('http://127.0.0.1:8531');
  for(const [kind,label,target,desired]of [['phase','A 相位與波形','pointer',[0,1]],['projectile','B 發射向量與軌跡','launch',[15,15*Math.sqrt(3)]],['math','C 仿射關係與錨點','relation_curve_anchor_offset',[0,2]]].filter(x=>(!process.argv.includes('--math-only')||x[0]==='math')&&(!process.argv.includes('--phase-only')||x[0]==='phase'))){
   if(kind!=='phase')await option('Day 25 離線驗收',label);
   await source().waitFor();await choosePage(2);const sourceFrame=await selectSource('source_object');
   const original=await sourceFrame.evaluate(()=>({image:D.image,regions:D.regions,selected:D.selected,page:D.page,zoom:document.getElementById('zoom').value}));
   await page.getByRole('button',{name:'開啟互動分身',exact:true}).click();
   const {frame,result}=await drag(target,desired);
   console.log(JSON.stringify({case:kind,desired,result}));
   await direct().screenshot({path:path.join(out,kind+'-explore.png')});
   if(kind==='phase'){assert(Math.abs(result.values.phase-Math.PI/2)<1e-5);assert(Math.abs(result.metrics.wave_value-1)<1e-10);}
   if(kind==='projectile'){assert(Math.abs(result.values.speed-30)<1e-4);assert(Math.abs(result.values.angle-Math.PI/3)<1e-5);assert(Math.abs(result.metrics.metric_vx-15)<1e-4);}
   if(kind==='math')assert(Math.abs(result.values.offset-2)<.01);
   await idle();await page.getByRole('button',{name:'回到支持此概念的來源',exact:true}).click();
   const returned=await frameOf(source());await returned.waitForFunction(()=>D?.selected==='source_object');
   const unchanged=await returned.evaluate(()=>({image:D.image,regions:D.regions,selected:D.selected,page:D.page,zoom:document.getElementById('zoom').value}));
   assert.deepEqual(unchanged,original,'source raster/boxes/selection/viewport remain original');
   await source().screenshot({path:path.join(out,kind+'-source.png')});
   if(process.argv.includes('--capture')){
    await page.getByRole('button',{name:'開啟互動分身',exact:true}).scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(out,kind+'-workspace.png')});
   }
   await page.getByRole('button',{name:'開啟互動分身',exact:true}).click();
   const again=await frameOf(direct());await again.waitForFunction(()=>controller?.points.size>0);
   assert.deepEqual(await again.evaluate(()=>P.values),result.values,'exploration values survive source navigation');
   // A forged release must restore canonical coordinates and focus, with no API.
   const values=await again.evaluate(()=>P.values);
   const revision=await again.evaluate(()=>P.revision),ack=await again.evaluate(()=>P.ack);
   await again.evaluate(()=>send({kind:'manipulate',target:'spoofed_target',x:1,y:1,time:P.time}));
   let restored=again;
   try{await restored.waitForFunction(({revision,ack})=>(P.revision>revision||P.ack!==ack)&&!pending&&!focusPending,{revision,ack})}
   catch(e){if(!/detached/.test(e.message))throw e;restored=await frameOf(direct());await restored.waitForFunction(()=>P?.values);}
   assert.deepEqual(await restored.evaluate(()=>P.values),values);
   rows.push({case:kind,values:result.values,metrics:result.metrics,source_roundtrip:true,source_unchanged:true,exact_target_highlight:true,interaction_api_delta:0});
  }
  // Non-manipulable source-backed derived entity, page-only, no invented box.
  await option('Day 25 離線驗收','A 相位與波形');
  await page.getByRole('combobox',{name:'Day 25 離線驗收',exact:true}).waitFor();
  await page.locator('.st-key-workspace-nav').getByText('來源',{exact:true}).click();
  await idle();
  if(!await source().count())await page.getByRole('button',{name:'回到支持此概念的來源',exact:true}).click();
  await source().waitFor();await choosePage(3);
  await option('選取來源物件','Derived source quantity');
  await page.getByText('來源 ↔ 正式表示',{exact:true}).waitFor();
  await page.getByRole('button',{name:'開啟互動分身',exact:true}).waitFor({state:'detached'});
  const unsupported=await frameOf(source());await unsupported.waitForFunction(()=>D?.selected==='derived_source');assert.equal(await unsupported.locator('rect.region').count(),0);assert.equal(await unsupported.locator('#zoom').inputValue(),'1');
  await source().screenshot({path:path.join(out,'non-manipulable.png')});
  await page.getByText('探索',{exact:true}).click();
  const derivedFrame=await frameOf(direct());await derivedFrame.waitForFunction(()=>P?.values);
  assert.deepEqual(await derivedFrame.evaluate(()=>P.focused_target_ids),[],'no handle assigned to derived entity');
  rows.push({case:'non_manipulable',page_only:true,fake_handle:false,interaction_api_delta:0});
  assert.deepEqual(errors,[]);
  fs.writeFileSync(path.join(out,process.argv.includes('--phase-only')?'phase-capture-results.json':process.argv.includes('--math-only')?'math-browser-results.json':'app-browser-results.json'),JSON.stringify({scope:'original synthetic 3-page PDFs in normal app, real pointer drags and source iframe clicks; paid SDK blocked',rows,page_errors:errors},null,2));
  console.log(JSON.stringify(rows));
 }finally{await context.close();await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1});
