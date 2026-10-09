const {chromium}=require('playwright');
(async()=>{const b=await chromium.launch({channel:'msedge',headless:true}),p=await b.newPage({viewport:{width:1440,height:1000}});
try{await p.goto('http://127.0.0.1:8531');await p.locator('iframe[title="source_atlas.runtime.source_atlas_viewer"]').waitFor();
console.log(JSON.stringify(await p.evaluate(()=>({scrollables:[...document.querySelectorAll('*')].filter(e=>e.clientHeight&&e.scrollHeight>e.clientHeight+2&&['auto','scroll'].includes(getComputedStyle(e).overflowY)).map(e=>({testid:e.dataset.testid,tag:e.tagName,cls:e.className,top:e.scrollTop,height:e.clientHeight,scrollHeight:e.scrollHeight})),radio:document.querySelector('.st-key-workspace-nav label')?.outerHTML,stage:document.querySelector('.st-key-learning-stage')?.outerHTML.slice(0,1500)})),null,2));
}finally{await b.close()}})().catch(e=>{console.error(e);process.exitCode=1});
