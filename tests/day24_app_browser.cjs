// Real Streamlit integration, fresh headless profile, localhost only.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require('playwright');
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:1450,height:1050}}),page=await context.newPage();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));const results=[];
 const iframe=()=>page.locator('iframe[title="manipulation.runtime.direct_semantic_manipulation"]');
 async function getFrame(expected){
  for(let i=0;i<8;i++){
   await iframe().waitFor({timeout:45000});const f=await iframe().elementHandle().then(e=>e.contentFrame());
   try{await f.waitForFunction(key=>typeof controller!=='undefined'&&Boolean(controller?.points.size)&&(!key||P.values[key]!==undefined),expected,{timeout:10000});return f}
   catch(error){if(!/detached|Timeout/.test(error.message))throw error}
  }throw new Error('Expected material did not render');
 }
 async function drag(frame,target,desired){
  await iframe().scrollIntoViewIfNeeded();
  const xy=await frame.evaluate(({id,desired})=>{
   const rect=document.getElementById('board').getBoundingClientRect(),b=controller.board,pt=controller.points.get(id);
   const host=document.getElementById('board');return {start:[rect.left+host.clientLeft+pt.coords.scrCoords[1],rect.top+host.clientTop+pt.coords.scrCoords[2]],end:[rect.left+host.clientLeft+b.origin.scrCoords[1]+desired[0]*b.unitX,rect.top+host.clientTop+b.origin.scrCoords[2]-desired[1]*b.unitY],revision:P.revision};
  },{id:target,desired});
  const rect=await iframe().boundingBox();await page.mouse.move(rect.x+xy.start[0],rect.y+xy.start[1]);await page.mouse.down();
  await frame.waitForFunction(rev=>P.revision>rev&&!focusPending,xy.revision,{timeout:30000});
  if(target==='launch')await page.getByText('目前焦點：Launch vertical velocity',{exact:true}).waitFor();
  if(target==='relation_curve_anchor_offset')await page.getByText('目前焦點：仿射關係',{exact:true}).waitFor();
  await frame.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  await page.evaluate(async()=>{let previous='',stable=0;for(let i=0;i<60&&stable<6;i++){await new Promise(requestAnimationFrame);const r=document.querySelector('iframe[title="manipulation.runtime.direct_semantic_manipulation"]').getBoundingClientRect(),now=JSON.stringify([r.x,r.y,r.width,r.height]);stable=now===previous?stable+1:0;previous=now}});
  const end=await frame.evaluate(desired=>{const host=document.getElementById('board'),r=host.getBoundingClientRect(),b=controller.board;return [r.left+host.clientLeft+b.origin.scrCoords[1]+desired[0]*b.unitX,r.top+host.clientTop+b.origin.scrCoords[2]-desired[1]*b.unitY]},desired);
  const afterFocus=await iframe().boundingBox();
  await page.mouse.move(afterFocus.x+end[0],afterFocus.y+end[1],{steps:12});await page.mouse.up();
  await frame.waitForFunction(revision=>P.revision>=revision+2&&!pending&&!focusPending,xy.revision,{timeout:30000});
  const result=await frame.evaluate(()=>({values:P.values,revision:P.revision,targets:P.targets,committed:P.committed}));
  console.log(JSON.stringify({target,expected:desired,values:result.values}));return result;
 }
 async function roundtrip(kind,values){
  await page.getByText('來源',{exact:true}).click();
  await iframe().waitFor({state:'detached'});
  await page.getByText('探索',{exact:true}).click();
  const f=await getFrame(Object.keys(values)[0]);const current=await f.evaluate(()=>P.values);assert.deepEqual(current,values);return f;
 }
 try{
  await page.goto('http://127.0.0.1:8527');let frame=await getFrame('phase');
  const phase=await drag(frame,'pointer',[0,1]);assert(Math.abs(phase.values.phase-Math.PI/2)<1e-5,JSON.stringify(phase));assert(Math.abs(phase.committed.metrics.wave_value-1)<1e-10);
  await iframe().screenshot({path:path.resolve(__dirname,'../docs/day24/app-phase.png')});
  frame=await roundtrip('phase',phase.values);results.push({case:'phase',values:phase.values,source_roundtrip:true,exact_signal:phase.committed.metrics.wave_value});
  await page.getByRole('combobox',{name:'Day 24 離線驗收'}).click();await page.getByRole('option',{name:'B 發射向量與軌跡',exact:true}).click();
  frame=await getFrame('speed');
  const projectile=await drag(frame,'launch',[30*Math.cos(Math.PI/3),30*Math.sin(Math.PI/3)]);
  assert(Math.abs(projectile.values.speed-30)<1e-4);assert(Math.abs(projectile.values.angle-Math.PI/3)<1e-5);
  assert(Math.abs(projectile.committed.metrics.metric_vx-15)<1e-4);
  await iframe().screenshot({path:path.resolve(__dirname,'../docs/day24/app-projectile.png')});
  frame=await roundtrip('projectile',projectile.values);results.push({case:'projectile',values:projectile.values,source_roundtrip:true,exact_horizontal:projectile.committed.metrics.metric_vx});
  await page.getByRole('combobox',{name:'Day 24 離線驗收'}).click();await page.getByRole('option',{name:'C 仿射關係與錨點',exact:true}).click();
  frame=await getFrame('gain');
  const math=await drag(frame,'relation_curve_anchor_offset',[0,2]);assert(Math.abs(math.values.offset-2)<.01,JSON.stringify(math));
  const positions=await frame.evaluate(()=>Array.from(controller.points.values()).map(p=>[p.X(),p.Y()]));
  assert(Math.abs(positions[1][1]-(2*math.values.gain+math.values.offset))<1e-8,'the other anchor must follow the same parameters');
  await iframe().screenshot({path:path.resolve(__dirname,'../docs/day24/app-math.png')});
  await roundtrip('math',math.values);results.push({case:'math',values:math.values,source_roundtrip:true,positions});
  assert.deepEqual(errors,[]);fs.writeFileSync(path.resolve(__dirname,'../docs/day24/app-browser-results.json'),JSON.stringify({scope:'offline declarations in normal app; real pointer events and reducer reruns',results,page_errors:errors},null,2));
  console.log('Normal Streamlit app: 3 real pointer drags committed, exact formal metrics and all Source/Explore roundtrips passed.');
 }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
