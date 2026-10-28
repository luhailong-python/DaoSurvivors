// Optional visual QA: npm install --no-save playwright, then node tools/capture-ui.cjs
const {chromium}=require(process.env.DAO_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs');
const path=require('node:path');
const crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const output=path.join(root,'designs/ui-v1/previews');
const url=process.env.DAO_PREVIEW_URL||'http://127.0.0.1:4327/docs/preview/';
const views=['home','cultivation','codex','battle','upgrade','pause','settings','result','defeat'];
(async()=>{
  fs.mkdirSync(output,{recursive:true});
  const edge=process.env.DAO_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  const browser=await chromium.launch({headless:true,...(fs.existsSync(edge)?{executablePath:edge}:{})});
  const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
  const errors=[];
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('response',r=>{if(r.status()>=400)errors.push(`${r.status()} ${r.url()}`)});
  await page.goto(url+'?capture=1',{waitUntil:'networkidle'});
  await page.evaluate(()=>document.fonts.ready);
  const records=[];
  for(let i=0;i<views.length;i++){
    const view=views[i];
    await page.evaluate(v=>window.daoPreview.show(v),view);
    await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode().catch(()=>null))));
    const broken=await page.evaluate(()=>[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>i.src));
    if(broken.length)errors.push(...broken.map(x=>'Missing image: '+x));
    const filename=`${String(i+1).padStart(2,'0')}-${view}-1920x1080.png`;
    await page.screenshot({path:path.join(output,filename)});
    records.push({view,file:'designs/ui-v1/previews/'+filename,width:1920,height:1080,
      sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(output,filename))).digest('hex'),
      operation:'DOM layout rendered by Chromium; composited existing PNGs and native font text. Not Unity runtime and not a new AI generation.'});
  }
  const responsive=[];
  for(const viewport of [{width:1280,height:720},{width:2560,height:1080},{width:390,height:844}]){
    await page.setViewportSize(viewport);
    for(const view of views){
    await page.evaluate(v=>window.daoPreview.show(v),view);
    await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode().catch(()=>null))));
    const result=await page.evaluate(()=>{const r=document.querySelector('.viewport').getBoundingClientRect();return {view:window.daoPreview.state.view,viewport:[innerWidth,innerHeight],frame:[r.x,r.y,r.width,r.height],bodyScrollWidth:document.body.scrollWidth,missingImages:[...document.images].filter(i=>!i.naturalWidth).length,frameAspect:r.width/r.height}});
    responsive.push(result);
    if(result.missingImages||result.bodyScrollWidth>viewport.width+1)errors.push('Responsive overflow/missing image '+JSON.stringify(viewport));
    }
  }
  await page.setViewportSize({width:1920,height:1080});
  await page.evaluate(()=>window.daoPreview.show('home'));
  await page.click('[data-hero="1"]'); await page.click('[data-stage="2"]');
  const selection=await page.evaluate(()=>({hero:window.daoPreview.state.hero,stage:window.daoPreview.state.stage}));
  if(selection.hero!==1||selection.stage!==2)errors.push('Selection interaction failed');
  await page.click('.bottom-nav [data-view="cultivation"]');
  await page.click('[data-action="train-0"]');
  const training=await page.evaluate(()=>({coins:window.daoPreview.state.coins,attack:window.daoPreview.state.perks[0]}));
  if(training.coins!==80||training.attack!==1)errors.push('Training interaction failed');
  await page.evaluate(()=>window.daoPreview.show('settings'));
  await page.click('[data-action="sound"]');
  if(await page.evaluate(()=>window.daoPreview.state.sound))errors.push('Settings toggle failed');
  const report={verifiedAt:new Date().toISOString(),kind:'UI design rendering, not Unity execution',browser:await browser.version(),records,responsive,interactions:{selection,training,soundToggle:true},errors,status:errors.length?'failed':'passed'};
  fs.mkdirSync(path.join(root,'docs/verification'),{recursive:true});
  fs.writeFileSync(path.join(root,'docs/verification/ui-preview.json'),JSON.stringify(report,null,2));
  await browser.close();
  console.log(JSON.stringify({status:report.status,previews:records.length,responsive:responsive.length,errors}));
  if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
