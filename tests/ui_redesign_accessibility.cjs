// Real keyboard focus, reduced-motion and fixed-light appearance under a dark OS.
const {chromium}=require('playwright'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({channel:'msedge',headless:true}),context=await browser.newContext({viewport:{width:1440,height:1000},colorScheme:'dark',reducedMotion:'reduce'}),p=await context.newPage(),errors=[];
const out=path.resolve(__dirname,'../docs/ui-redesign');p.on('pageerror',e=>errors.push(e.message));
const ready=async()=>{await p.waitForFunction(()=>document.querySelector('[data-testid=stApp]')?.dataset.testScriptState==='notRunning'&&![...document.querySelectorAll('[data-stale]')].some(e=>e.dataset.stale==='true'));};
const frame=async title=>{const l=p.locator(`iframe[title="${title}"]`);await l.waitFor();return (await l.elementHandle()).contentFrame()};
try{
 await p.goto('http://127.0.0.1:8531');let s=await frame('source_atlas.runtime.source_atlas_viewer');await s.waitForFunction(()=>D?.image);await ready();
 const c=p.getByRole('combobox',{name:'來源頁面',exact:true});await c.focus();await c.press('ArrowDown');await p.getByRole('option',{name:'第 2 頁',exact:true}).click();
 await s.waitForFunction(()=>D?.page===2);await ready();
 const region=s.locator('rect.region[data-region-id=source_object]');await region.focus();await region.press('Enter');await s.waitForFunction(()=>D?.selected==='source_object');await ready();
 const sourceFocus=await s.evaluate(()=>document.activeElement?.getAttribute('data-region-id'));assert.equal(sourceFocus,'source_object');
 await p.getByRole('button',{name:'開啟互動分身',exact:true}).click();const d=await frame('manipulation.runtime.direct_semantic_manipulation');await d.waitForFunction(()=>controller?.points.size>0);await ready();
 const revision=await d.evaluate(()=>P.revision);const handle=d.locator('.vll-handle').first();await handle.focus();await handle.press('ArrowUp');
 await d.waitForFunction(r=>P.revision>r&&!pending,revision);await ready();
 const keyboard=await d.evaluate(()=>({phase:P.values.phase,focused:document.activeElement?.getAttribute('aria-label')}));assert(keyboard.phase>0);
 const reduced=await p.getByRole('button',{name:'回到支持此概念的來源',exact:true}).evaluate(e=>getComputedStyle(e).transitionDuration);assert.equal(reduced,'0s');
 await p.locator('[data-testid=stMain]').evaluate(e=>e.scrollTop=0);await ready();
 await p.screenshot({path:path.join(out,'final-explore-dark-os.png')});
 const appearance=await p.locator('[data-testid=stApp]').evaluate(e=>({background:getComputedStyle(e).backgroundColor,foreground:getComputedStyle(e).color}));
 fs.writeFileSync(path.join(out,'accessibility.json'),JSON.stringify({sourceKeyboardFocusPreserved:sourceFocus,keyboard,reducedMotion:reduced,appearance,pageErrors:errors},null,2));assert.deepEqual(errors,[]);
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
