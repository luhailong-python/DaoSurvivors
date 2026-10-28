// Art preview renderer and text/asset mapping exporter. This never runs a game or Unity.
const {chromium}=require(process.env.DAO_PLAYWRIGHT_MODULE||'playwright');
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const coveragePath=path.join(root,'docs/ui-suite/UI_COVERAGE.json');
const coverage=JSON.parse(fs.readFileSync(coveragePath,'utf8').replace(/^\uFEFF/,''));
const url=process.env.DAO_SUITE_URL||'http://127.0.0.1:4327/designs/ui-suite/preview/';
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
(async()=>{
 const edge=process.env.DAO_BROWSER||'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
 const browser=await chromium.launch({headless:true,...(fs.existsSync(edge)?{executablePath:edge}:{})});
 const page=await browser.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
 const failures=[],scriptErrors=[];page.on('pageerror',e=>scriptErrors.push(String(e)));
 await page.goto(url+'?capture=1',{waitUntil:'networkidle'});await page.evaluate(()=>window.suiteReady);await page.evaluate(()=>document.fonts.ready);
 const selected=process.env.DAO_SUITE_IDS?new Set(process.env.DAO_SUITE_IDS.split(',')):null;
 const rows=coverage.screens.filter(r=>!selected||selected.has(r.id));
 const records=[];
 for(const row of rows){
  await page.evaluate(id=>window.daoSuite.setView(id),row.id);
  await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode().catch(()=>null))));
  const mapping=await page.evaluate(()=>{
    const screen=document.getElementById('screen'),bounds=screen.getBoundingClientRect();
    const text=[];const walker=document.createTreeWalker(screen,NodeFilter.SHOW_TEXT);
    while(walker.nextNode()){
      const node=walker.currentNode,value=node.textContent.trim();if(!value)continue;
      const parent=node.parentElement,style=getComputedStyle(parent);if(style.display==='none'||style.visibility==='hidden')continue;
      const range=document.createRange();range.selectNodeContents(node);
      const rects=[...range.getClientRects()].filter(r=>r.width&&r.height).map(r=>({x:+(r.x-bounds.x).toFixed(2),y:+(r.y-bounds.y).toFixed(2),width:+r.width.toFixed(2),height:+r.height.toFixed(2)}));
      if(!rects.length)continue;
      text.push({text:value,tag:parent.tagName,font:style.fontFamily,fontSize:style.fontSize,fontWeight:style.fontWeight,color:style.color,alignment:style.textAlign,lineHeight:style.lineHeight,rects});
    }
    return {id:window.daoSuite.row.id,viewport:[innerWidth,innerHeight],designSize:[1920,1080],textRegions:text,
      imageLayers:[...screen.querySelectorAll('img')].map(im=>({asset:im.dataset.asset,naturalSize:[im.naturalWidth,im.naturalHeight],broken:!im.complete||!im.naturalWidth})),
      overflowText:text.flatMap(t=>t.rects.some(r=>r.x<-.6||r.y<-.6||r.x+r.width>1920.6||r.y+r.height>1080.6)?[t.text]:[])};
  });
  const broken=mapping.imageLayers.filter(i=>i.broken).map(i=>i.asset);
  if(broken.length||mapping.overflowText.length)failures.push({id:row.id,broken,overflowText:mapping.overflowText});
  const shot=path.join(root,row.screenPath),layout=path.join(root,row.layoutPath);
  fs.mkdirSync(path.dirname(shot),{recursive:true});fs.mkdirSync(path.dirname(layout),{recursive:true});
  await page.screenshot({path:shot});
  const cssAssets=['art/common/main_frame.png','art/common/title_plate.png','art/common/button_primary.png','art/common/button_secondary.png'];
  const assets=[...new Set([...mapping.imageLayers.map(i=>i.asset),...cssAssets])];
  fs.writeFileSync(layout,JSON.stringify({...mapping,renderOperation:'Browser DOM layout and compositing; not AI image generation or Unity runtime.',artSources:assets,screenSha256:hash(shot)},null,2));
  row.independentAssets=assets;row.productionStatus=broken.length?'asset_missing':'rendered';row.acceptanceStatus='awaiting_visual_review';
  records.push({id:row.id,file:row.screenPath,sha256:hash(shot),layout:row.layoutPath,brokenImages:broken.length,textOverflows:mapping.overflowText.length});
 }
 const responsive=[];
 if(!selected){
 for(const viewport of [{width:1280,height:720},{width:2560,height:1080}]){
  await page.setViewportSize(viewport);
  for(const row of rows){await page.evaluate(id=>window.daoSuite.setView(id),row.id);await page.evaluate(()=>Promise.all([...document.images].map(im=>im.decode().catch(()=>null))));
   const result=await page.evaluate(()=>{const b=document.querySelector('.viewport').getBoundingClientRect();return {id:window.daoSuite.row.id,viewport:[innerWidth,innerHeight],frame:[b.x,b.y,b.width,b.height],aspectRatio:b.width/b.height,missingImages:[...document.images].filter(i=>!i.naturalWidth).length,bodyScrollWidth:document.body.scrollWidth}});
   if(result.missingImages||result.bodyScrollWidth>viewport.width+1)failures.push({id:row.id,viewport,error:'responsive asset/overflow'});
   responsive.push(result);
  }
 }
 }
 const sourceFiles=['designs/ui-suite/preview/index.html','designs/ui-suite/preview/style.css','designs/ui-suite/preview/menu.css','designs/ui-suite/preview/suite.js','designs/ui-suite/preview/menu.js'];
 const report={verifiedAt:new Date().toISOString(),purpose:'Art/UI state rendering, not game logic or Unity verification',browser:await browser.version(),baseResolution:[1920,1080],records,responsive,sourceFiles:sourceFiles.map(f=>({file:f,sha256:hash(path.join(root,f))})),scriptErrors,failures,status:failures.length||scriptErrors.length?'failed':'passed'};
 if(!selected){fs.writeFileSync(coveragePath,JSON.stringify(coverage,null,2));}
 fs.writeFileSync(path.join(root,'docs/ui-suite/',selected?'render-debug.json':'render-verification.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify({status:report.status,frames:rows.length,responsive:responsive.length,scriptErrors,failures}));
 if(failures.length||scriptErrors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
