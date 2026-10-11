// Real Edge/Chromium acceptance: empty app, public file upload, actual response
// replay, ordinary widgets and pointer gestures. No seeded analysis or judge.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..'),home=path.join(root,'.day27-local/browser');
fs.mkdirSync(home,{recursive:true});
const corpus=JSON.parse(fs.readFileSync(path.join(root,'docs/day27/corpus-manifest.json'),'utf8'));
const cid=process.argv[2],capture=process.argv[3]||'',narrow=process.argv.includes('--narrow');
const c=corpus.materials.find(c=>c.material_id===cid);
if(!c)throw Error('Unknown frozen case');
const load=p=>JSON.parse(fs.readFileSync(p,'utf8'));
const bundle=load(path.join(root,'.day27-local/cases',cid+'.json'));
const session=()=>load(path.join(home,cid+'-session.json'));
(async()=>{
 const browser=await chromium.launch({channel:'msedge',headless:true});
 const context=await browser.newContext({viewport:{width:narrow?880:1440,height:1000}}),page=await context.newPage(),errors=[],consoleErrors=[];
 const result={case:cid,viewport:narrow?'880x1000':'1440x1000',scope:'Actual first-attempt declarations through unchanged production app; no new network generations',steps:[],page_errors:errors,console_errors:consoleErrors};
 page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')consoleErrors.push(m.text())});
 page.setDefaultTimeout(20000);
 const idle=async()=>{await page.waitForFunction(()=>document.querySelector('[data-testid=stApp]')?.dataset.testScriptState==='notRunning');};
 async function settle(){await idle();await page.evaluate(async()=>{let old='',stable=0;for(let i=0;i<100&&stable<8;i++){await new Promise(requestAnimationFrame);let next=JSON.stringify([...document.querySelectorAll('iframe')].map(f=>[f.clientWidth,f.clientHeight]));stable=old===next?stable+1:0;old=next}});}
 let hasAnalysis=false;
 async function rerunAction(action){
  const snapshotFile=path.join(home,cid+'-session.json'),before=fs.existsSync(snapshotFile)?fs.statSync(snapshotFile).mtimeMs:0;
  await action();
  if(!hasAnalysis){await page.evaluate(()=>new Promise(r=>setTimeout(r,750)));await settle();return;}
  await page.waitForFunction(()=>document.querySelector('[data-testid=stApp]')!==null);
  for(let i=0;i<100;i++){
   if(fs.existsSync(snapshotFile)&&fs.statSync(snapshotFile).mtimeMs>before){await settle();return;}
   await new Promise(r=>setTimeout(r,100));
  }
  throw Error('Automation did not observe completion of the production rerun');
 }
 async function option(name,value){
  result.last_operation={kind:'select',name,value};
  if(hasAnalysis&&name==='Source page'&&session().page===Number(value.replace('Page ','')))return;
  const combo=page.getByRole('combobox',{name,exact:true});await combo.scrollIntoViewIfNeeded();
  const current=await combo.evaluate(e=>(e.closest('[data-testid=stSelectbox]')?.innerText||e.value||'').split('\n').map(s=>s.trim()));
  if(current.includes(value))return;
  await combo.focus();await combo.press('ArrowDown');await rerunAction(()=>page.getByRole('option',{name:value,exact:true}).click());
 }
 const nav=async name=>{await rerunAction(()=>page.getByText(name,{exact:true}).first().click());};
 async function expander(name){
  const summary=page.locator('summary').filter({hasText:name}).first();
  if(!await summary.count())return;
  await summary.scrollIntoViewIfNeeded();
  for(let i=0;i<3;i++){
   if(!await summary.evaluate(e=>e.closest('details')?.open))await summary.click();
   await settle();
   if(await summary.evaluate(e=>e.closest('details')?.open))return;
  }
 }
 const source=()=>page.locator('iframe[title="source_atlas.runtime.source_atlas_viewer"]');
 const direct=()=>page.locator('iframe[title="manipulation.runtime.direct_semantic_manipulation"]');
 async function moveSlider(slider){
  const value=Number(await slider.getAttribute('aria-valuenow')),max=Number(await slider.getAttribute('aria-valuemax'));
  const key=value>=max?'ArrowLeft':'ArrowRight';result.slider_key=key;
  await rerunAction(async()=>{await slider.press(key);await slider.press('Tab');});
 }
 const frameOf=async l=>{await l.waitFor();return (await l.elementHandle()).contentFrame()};
 let sourceOriginal=null,focusOriginal=null,interactionsStart=0;
 try{
  await page.goto('http://127.0.0.1:8540');await page.getByRole('button',{name:'開始理解',exact:true}).waitFor();await settle();
  await option('語言 / Language','English');
  await page.locator('input[type=file]').setInputFiles(path.join(root,c.subset_path));await settle();
  await page.getByRole('button',{name:'Visualize',exact:true}).click();await page.getByText('Learn',{exact:true}).waitFor();await settle();
  hasAnalysis=true;
  result.steps.push('Real PDF upload and actual recorded main analysis');
  await nav('Explore');await page.getByText('Concept Map',{exact:true}).first().waitFor().catch(()=>{});await expander('Representation');
  await rerunAction(()=>page.getByRole('button',{name:'Choose a learning representation',exact:true}).click());
  result.steps.push('Original first planner declaration accepted/rejected by production');
  await nav('Source');
  if(bundle.raw_scene){
   const label=bundle.scene_data.domain==='spatial_dynamics'?'Build Spatial Learning World':'Build Learning Scene';
   const button=page.getByRole('button',{name:label,exact:true});
   if(await button.count()){await button.click();await settle();result.steps.push('Original first scene declaration revalidated');}
  }
  const deepFile=path.join(root,'.day27-local/deep',cid+'.json');
  if(fs.existsSync(deepFile)){
   const detail=load(deepFile);await expander('Source preparation');
   const build=page.getByRole('button',{name:'Build Source Atlas',exact:true});
   if(await build.count()&&await build.isEnabled()){
    await rerunAction(()=>build.click());
    result.atlas_build_observation={accepted:!!session().atlas};
    if(!session().atlas)throw Error('Atlas absent after production build action');
    result.steps.push('Actual recorded deep Atlas declaration');
    await source().waitFor();
   }
   if(await source().count()&&detail.result.selected_region){
    const region=detail.atlas.regions.find(r=>r.region_id===detail.result.selected_region);
    await option('Source page','Page '+region.page);
    await option('Choose a source object',region.label);
    const sf=await frameOf(source());await sf.waitForFunction(()=>D?.image);
    sourceOriginal=await sf.evaluate(()=>({image:D.image,regions:D.regions,page:D.page,selected:D.selected,zoom:document.getElementById('zoom').value}));
    focusOriginal=session().focus;result.source_selected={region_id:region.region_id,focus:focusOriginal};
   }else result.source_selection_absence='No rendered Source Atlas or no unambiguous focusable region';
  }
  interactionsStart=fs.existsSync(path.join(home,'events.jsonl'))?fs.readFileSync(path.join(home,'events.jsonl'),'utf8').trim().split('\n').length:0;
  await nav('Explore');
  const before=session();result.before={focus:before.focus,lab:before.lab,world:before.world};
  const chartFingerprint=async()=>JSON.stringify(await page.locator('.js-plotly-plot').evaluateAll(es=>es.map(e=>(e.data||[]).map(t=>({name:t.name,x:t.x,y:t.y})))));
  const chartsBefore=await chartFingerprint();
  const scrollBeforeInteraction=await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop);
  const dragTargets=bundle.result.direct_manipulation_affordances||[];
  if(await direct().count()){
   const df=await frameOf(direct());await df.waitForFunction(()=>controller?.points.size>0);
   await direct().scrollIntoViewIfNeeded();await settle();
   const info=await df.evaluate(()=>{const t=P.targets.find(t=>P.focused_target_ids.includes(t.id))||P.targets[0],p=controller.points.get(t.id),r=p.rendNode.getBoundingClientRect();return {target:t,xy:[r.x+r.width/2,r.y+r.height/2],revision:P.revision,values:P.values}});
   result.actual_targets=await df.evaluate(()=>P.targets);
   if(info.target){
    let host=await direct().boundingBox();await page.mouse.move(host.x+info.xy[0],host.y+info.xy[1]);await page.mouse.down();
    await df.waitForFunction(r=>P.revision>r&&!focusPending,info.revision);
    const scrollBefore=await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop);
    let dest=[...info.target.position];const inv=info.target.inverse;
    if(inv.kind==='affine')dest[1]+=.12*(info.target.bounds[3]-info.target.bounds[1]);
    else{const ox=inv.origin[0],oy=inv.origin[1],dx=dest[0]-ox,dy=dest[1]-oy,a=.1;dest=[ox+dx*Math.cos(a)-dy*Math.sin(a),oy+dx*Math.sin(a)+dy*Math.cos(a)]}
    for(let i=0;i<3;i++){
     const xy=await df.evaluate(v=>{const h=document.getElementById('board'),r=h.getBoundingClientRect(),b=controller.board;return [r.left+h.clientLeft+b.origin.scrCoords[1]+v[0]*b.unitX,r.top+h.clientTop+b.origin.scrCoords[2]-v[1]*b.unitY]},dest);
     host=await direct().boundingBox();await page.mouse.move(host.x+xy[0],host.y+xy[1],{steps:10});
     await df.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    }
    await page.mouse.up();await df.waitForFunction(r=>P.revision>=r+2&&!pending&&!focusPending,info.revision);await settle();
    result.pointer_drag={before:info.values,after:await df.evaluate(()=>P.values),scroll_before:scrollBefore,scroll_after:await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop)};
   }
  }else if(await page.getByRole('slider').count()){
   await expander('Parameters and comparison');const slider=page.getByRole('slider').first();
   await slider.scrollIntoViewIfNeeded();await slider.focus();await moveSlider(slider);
   result.slider_interaction={name:await slider.getAttribute('aria-label'),before:before.lab,after:session().lab};
  }else{
   await expander('Parameters and comparison');
   if(await page.getByRole('slider').count()){
    const slider=page.getByRole('slider').first();await slider.scrollIntoViewIfNeeded();await slider.focus();await moveSlider(slider);
    result.slider_interaction={before:before.lab,after:session().lab};
   }else result.interaction_absence='No numeric drag/slider; formal or discrete controls retained, not an automatic failure';
  }
  result.after=session();
  if(result.slider_interaction){
   result.canonical_value_changed=JSON.stringify(before.lab?.demos)!==JSON.stringify(result.after.lab?.demos);
   result.linked_chart_changed=chartsBefore!==await chartFingerprint();
   result.slider_scroll_observation={before:scrollBeforeInteraction,after:await page.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop)};
  }
  result.context_observation={mode_before:before.mode||'explore',mode_after:result.after.mode,focus_before:before.focus,focus_after:result.after.focus};
  if(capture&&!process.argv.includes('--capture-source')){
   if(cid==='circular')await expander('Representation');
   const heading=cid==='harmonic'||cid==='probability'||cid==='signals'?page.getByText('Interactive Lab',{exact:true}).first():cid==='circular'?page.locator('summary').filter({hasText:'Representation'}).first():page.getByText('Concept Map',{exact:true}).first();
   if(await heading.count())await heading.evaluate(e=>e.scrollIntoView({block:'start'}));await settle();
   await page.screenshot({path:path.join(root,'docs/day27',capture),fullPage:false});result.screenshot=capture;
  }
  const returnButton=page.getByRole('button',{name:'Return to supporting source',exact:true});
  if(await returnButton.count())await rerunAction(()=>returnButton.click());else await nav('Source');await settle();
  const returned=session();result.focus_preserved=returned.focus===result.after.focus;
  result.source_pdf_immutable=returned.source_pdf_sha256===c.subset_sha256;
  if(sourceOriginal&&await source().count()){
   const sf=await frameOf(source());await sf.waitForFunction(()=>D?.image);
   const src=await sf.evaluate(()=>({image:D.image,regions:D.regions,page:D.page,selected:D.selected,zoom:document.getElementById('zoom').value}));
   result.source_view_unchanged=JSON.stringify(sourceOriginal)===JSON.stringify(src);
  }
  result.roundtrip_mode=returned.mode;
  if(capture&&process.argv.includes('--capture-source')){
   await source().scrollIntoViewIfNeeded();await settle();
   await page.screenshot({path:path.join(root,'docs/day27',capture),fullPage:false});result.screenshot=capture;
  }
  const events=fs.readFileSync(path.join(home,'events.jsonl'),'utf8').trim().split('\n').slice(interactionsStart).map(JSON.parse);
  result.post_compilation_response_attempts=events.filter(e=>e.kind.includes('response')).length;
  result.post_compilation_network_delta=events.reduce((n,e)=>n+(e.new_network_requests||0),0);
  result.success=true;
 }catch(e){result.success=false;result.error=e.message;result.expander_observation=await page.locator('summary').evaluateAll(es=>es.map(e=>({text:e.innerText,parent:e.parentElement.tagName,details:e.closest('details')?.open})));
  console.log(JSON.stringify({case:cid,error:e.message,expanders:result.expander_observation,body:(await page.locator('body').innerText()).slice(-1500)}));
  if(capture&&!fs.existsSync(path.join(root,'docs/day27',capture)))await page.screenshot({path:path.join(root,'docs/day27',capture),fullPage:false});
 }finally{
  const data=JSON.stringify(result,null,2),stamp=Date.now();
  fs.writeFileSync(path.join(home,cid+(narrow?'-narrow':'-desktop')+'-'+stamp+'-results.json'),data,{flag:'wx'});
  fs.writeFileSync(path.join(home,cid+(narrow?'-narrow':'-desktop')+'-results.json'),data);
  console.log(JSON.stringify({case:cid,success:result.success,errors:errors.length,roundtrip:result.roundtrip_mode,network_delta:result.post_compilation_network_delta}));
  await context.close();await browser.close();
 }
})().catch(e=>{console.error(e.message);process.exitCode=1});
