// Isolated browser QA against production and the existing offline normal-app harness.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
const phase=process.argv[2]||'after',out=path.resolve(__dirname,'../docs/ui-redesign');
fs.mkdirSync(out,{recursive:true});
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000}}),page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 const idle=()=>page.waitForFunction(()=>document.querySelector('[data-testid=stApp]')?.dataset.testScriptState==='notRunning');
 const source=()=>page.locator('iframe[title="source_atlas.runtime.source_atlas_viewer"]');
 const direct=()=>page.locator('iframe[title="manipulation.runtime.direct_semantic_manipulation"]');
 const frame=async l=>{await l.waitFor();return (await l.elementHandle()).contentFrame()};
 const settle=()=>page.evaluate(async()=>{let last='',stable=0;for(let i=0;i<90&&stable<10;i++){await new Promise(requestAnimationFrame);const e=document.querySelector('[data-testid=stMain]'),r=e.getBoundingClientRect(),now=JSON.stringify([r.x,r.width,e.scrollHeight,...[...document.querySelectorAll('iframe')].map(f=>[f.clientWidth,f.clientHeight])]);stable=now===last?stable+1:0;last=now}});
 async function option(name,value){const c=page.getByRole('combobox',{name,exact:true});await idle();await c.scrollIntoViewIfNeeded();await c.focus();await c.press('ArrowDown');await page.getByRole('option',{name:value,exact:true}).click();await idle();}
 const shot=async name=>{await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTo(0,0));await page.screenshot({path:path.join(out,phase+'-'+name+'.png'),fullPage:true})};
 try{
  await page.goto('http://127.0.0.1:8530');await page.getByRole('button',{name:'開始理解',exact:true}).waitFor();await idle();await shot('home');
  await page.goto('http://127.0.0.1:8531');await source().waitFor();await idle();
  await option('來源頁面','第 2 頁');
  let s=await frame(source());await s.waitForFunction(()=>D?.regions.length>0);
  await s.locator('rect.region').filter({has:s.locator('title',{hasText:'Source diagram'})}).click();
  await page.getByRole('button',{name:'開啟互動分身',exact:true}).waitFor();await idle();
  s=await frame(source());await s.waitForFunction(()=>D?.selected==='source_object');const original=await s.evaluate(()=>({image:D.image,regions:D.regions,selected:D.selected,page:D.page}));
  await shot('source');await page.getByRole('button',{name:'開啟互動分身',exact:true}).click();
  const d=await frame(direct());await d.waitForFunction(()=>controller?.points.size>0);await idle();await shot('explore');
  await direct().scrollIntoViewIfNeeded();
  await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop=180);await settle();
  await page.evaluate(()=>{window.layoutShifts=[];window.layoutObserver=new PerformanceObserver(list=>{for(const e of list.getEntries())layoutShifts.push({value:e.value,recentInput:e.hadRecentInput})});layoutObserver.observe({type:'layout-shift',buffered:false})});
  await d.evaluate(()=>{window.qaBoard=controller.board;window.qaMounts=0;window.qaMessages=0;const original=DirectManipulation.mount;DirectManipulation.mount=(...args)=>{qaMounts++;return original(...args)};window.addEventListener('message',e=>{if(e.data.type==='streamlit:render')qaMessages++})});
  const start=await d.evaluate(()=>{const r=controller.points.get('pointer').rendNode.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2,rev:P.revision,bytes:JSON.stringify(P).length}});
  let b=await direct().boundingBox();await page.mouse.move(b.x+start.x,b.y+start.y);await page.mouse.down();
  await d.waitForFunction(r=>P.revision>r&&!focusPending,start.rev);
  const scrollBefore=await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop);
  const stageBefore=await direct().boundingBox();
  for(let i=0;i<3;i++){
   const xy=await d.evaluate(()=>{const r=document.getElementById('board').getBoundingClientRect(),b=controller.board;return [r.x+1+b.origin.scrCoords[1],r.y+1+b.origin.scrCoords[2]-b.unitY]});
   b=await direct().boundingBox();await page.mouse.move(b.x+xy[0],b.y+xy[1],{steps:10});
  }
  const preview=await d.evaluate(()=>({rev:P.revision,values:P.values}));await page.mouse.up();
  await d.waitForFunction(r=>P.revision>=r+2&&!pending&&!focusPending,start.rev);await idle();
  const result=await d.evaluate(()=>({values:P.values,metrics:P.committed.metrics,mounts:qaMounts,sameBoard:qaBoard===controller.board,messages:qaMessages,bytes:JSON.stringify(P).length}));
  const scrollAfter=await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop);
  const stageAfter=await direct().boundingBox(),layoutShifts=await page.evaluate(()=>{layoutObserver.disconnect();return layoutShifts});
  assert(Math.abs(result.values.phase-Math.PI/2)<.025);assert.equal(preview.rev,start.rev+1);
  await page.getByRole('button',{name:'回到支持此概念的來源',exact:true}).click();
  s=await frame(source());await s.waitForFunction(()=>D?.selected==='source_object');await idle();
  assert.deepEqual(await s.evaluate(()=>({image:D.image,regions:D.regions,selected:D.selected,page:D.page})),original);
  const responsive=[];
  for(const width of [1280,768,390,430]){
   await page.setViewportSize({width,height:900});await settle();await shot('source-'+width);
   const sourceBox=await source().boundingBox(),railBox=await page.locator('.st-key-context-rail').boundingBox();
   responsive.push({mode:'source',width,sourceBox,railBox,overflow:await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollWidth>e.clientWidth+1)});
  }
  await page.getByRole('button',{name:'開啟互動分身',exact:true}).click();
  const small=await frame(direct());await small.waitForFunction(()=>controller?.points.size>0);await idle();
  for(const width of [1280,768,390,430]){
   await page.setViewportSize({width,height:900});await settle();await shot('explore-'+width);
   responsive.push({mode:'explore',width,overflow:await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollWidth>e.clientWidth+1),componentOverflow:await small.evaluate(()=>document.body.scrollWidth>innerWidth+1)});
  }
  // Keyboard navigation uses the same native radio callbacks, not click-only tabs.
  await page.setViewportSize({width:1440,height:1000});
  await page.getByRole('button',{name:'回到支持此概念的來源',exact:true}).click();s=await frame(source());await s.waitForFunction(()=>D?.selected==='source_object');await idle();
  const sourceRadio=page.getByRole('radio',{name:'來源',exact:true});await sourceRadio.focus();await sourceRadio.press('ArrowRight');
  const keyboardFrame=await frame(direct());await keyboardFrame.waitForFunction(()=>P?.values);await idle();
  const keyboardMode=await page.getByRole('radio',{name:'探索',exact:true}).isChecked();assert(keyboardMode);
  await context.setOffline(false);await page.emulateMedia({reducedMotion:'reduce',colorScheme:'dark'});
  const reduced=await page.getByRole('button',{name:'回到支持此概念的來源',exact:true}).evaluate(e=>getComputedStyle(e).transitionDuration);
  assert.equal(reduced,'0s');await shot('explore-dark-os');
  fs.writeFileSync(path.join(out,phase+'-browser.json'),JSON.stringify({phase,result,payloadBefore:start.bytes,localPreviewNoCommit:true,sourceUnchanged:true,scrollBefore,scrollAfter,stageBefore,stageAfter,layoutShifts,responsive,keyboardMode,reducedMotion:reduced,pageErrors:errors},null,2));
  assert(responsive.every(r=>!r.overflow&&!r.componentOverflow));
  assert.deepEqual(errors,[]);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
