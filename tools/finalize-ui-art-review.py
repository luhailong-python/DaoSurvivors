"""Finalize the inspected UI batch; no game/Unity execution or AI image editing."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, struct
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
def read(rel): return json.loads((ROOT/rel).read_text(encoding='utf-8-sig'))
def sha(rel): return hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
def write(rel,obj): (ROOT/rel).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat()
client_date='2026-10-29'
coverage=read('docs/ui-suite/UI_COVERAGE.json')
render=read('docs/ui-suite/render-verification.json')
assert render['status']=='passed' and len(render['records'])==52 and len(render['responsive'])==104
assert not render['failures'] and not render['scriptErrors']
independent=read('docs/ui-suite/brand-visual-independent-review.json')
assert independent['status']=='accepted_brand_ui_review' and not independent['issues']
assert len(independent['contactSheets'])==7
for evidence in independent['screens']+independent['contactSheets']:
    assert sha(evidence['file'])==evidence['sha256'], evidence['file']
layouts={r['id']:read(r['layoutPath']) for r in coverage['screens']}
texts={k:[t['text'] for t in v['textRegions']] for k,v in layouts.items()}
all_text=''.join(s for seq in texts.values() for s in seq)

# Read OpenType cmap using the standard library; no font dependency installation.
font=(ROOT/'art/fonts/NotoSansSC-Regular.otf').read_bytes()
u16=lambda p:struct.unpack_from('>H',font,p)[0]
u32=lambda p:struct.unpack_from('>I',font,p)[0]
tables={font[12+i*16:16+i*16]:u32(20+i*16) for i in range(u16(4))}
base=tables[b'cmap']; supported=set()
for i in range(u16(base+2)):
    sub=base+u32(base+8+i*8); fmt=u16(sub)
    if fmt==12:
        groups=[struct.unpack_from('>III',font,sub+16+j*12) for j in range(u32(sub+12))]
        for cp in set(map(ord,all_text)):
            if any(a<=cp<=b and g+cp-a!=0 for a,b,g in groups):supported.add(cp)
    elif fmt==4:
        n=u16(sub+6)//2; ends=sub+14; starts=ends+n*2+2; deltas=starts+n*2; offsets=deltas+n*2
        for cp in set(map(ord,all_text)):
            if cp>65535:continue
            for j in range(n):
                if u16(starts+j*2)<=cp<=u16(ends+j*2):
                    off=u16(offsets+j*2);delta=u16(deltas+j*2)
                    glyph=u16(offsets+j*2+off+2*(cp-u16(starts+j*2))) if off else cp
                    if glyph and (glyph+delta)&65535:supported.add(cp)
                    break
missing=sorted(set(ch for ch in all_text if not ch.isspace() and ord(ch) not in supported))
assert not missing, missing

semantic=[]
def check(key,condition,detail):
    assert condition, key
    semantic.append({'id':key,'status':'passed','detail':detail})
check('new-cards-match-background','养元' in texts['29-upgrade-new'] and '连星诀' in texts['29-upgrade-new'] and '四象符' in texts['29-upgrade-new'],'29 uses unheld Chain/FourCorner/HPMax; background holds ToNearest/BothSide/Bouncing and Might/Armor.')
check('owned-card-hud-level','Lv.4' in texts['30-upgrade-existing'],'30 first active slot is Lv.4 before the 4→5 reward.')
check('all-moneybag-maxed',all(texts[k].count('Lv.11')==6 and texts[k].count('Lv.5')==6 for k in ['31-upgrade-moneybag','36-treasure-moneybag']),'All-moneybag backgrounds show six max-level actives and six max-level passives.')
check('passives-not-evolved',texts['26-battle-build-full'].count('化境')==1 and all(t in {'Lv.1','Lv.2','Lv.3','Lv.4','Lv.5'} for t in texts['26-battle-build-full'][texts['26-battle-build-full'].index('诀')+1:texts['26-battle-build-full'].index('诀')+7]),'26 shows a single active evolved marker; passive badges range Lv.1–5 only.')
check('evolution-prerequisites','Lv.11' in texts['35-treasure-evolution'] and 'art/icons/attr-cooldown.png' in [i['asset'] for i in layouts['35-treasure-evolution']['imageLayers']],'35 pendingMix background includes active Lv11 and matching held Cooldown.')
check('treasure-gold-range',all('+ 950' in texts[k] for k in ['34-treasure-five','35-treasure-evolution','36-treasure-moneybag']),'Five-reward chest samples use950, within source900–1000 at baseGreed100.')
check('insufficient-wallet','180' in texts['09-unlock-insufficient'],'09 header and confirmation both show current180, required500, shortage320.')
check('formal-brand-on-all52',all('一炁当千' in texts[key] and not any('道途幸存者' in text for text in texts[key]) for key in texts),'All52 screens use the formal game name; old working title is absent from live screen text.')
check('brand-assets-on-all52',all(layout['brandAudit']['brandAssets'] and layout['brandAudit']['hasCurrentName'] and not layout['brandAudit']['hasPreviousWorkingTitle'] for layout in layouts.values()),'Every screen maps a formal emblem or wordmark resource; original actors/world art remains unchanged.')

full_views={'01-startup','02-loading','04-main-menu','05-character-select','25-battle-hud','40-victory','51-control-states','52-flow-map'}
notes={
 '01-startup':'Formal primary wordmark uses contain scaling inside the startup panel; tagline, entry and footer remain clear.',
 '02-loading':'Formal wordmark and title fit above the separate loading indicator; header emblem and text remain clear.',
 '04-main-menu':'Formal name/emblem in header and authorized tagline on paper backing; main actions remain unobscured.',
 '05-character-select':'Header uses formal emblem plus independent title text; character identities, prices and selection controls are unchanged.',
 '25-battle-hud':'Compact emblem/title in bottom strip leaves movement instructions and combat HUD unobscured.',
 '40-victory':'Result values/actions remain aligned; formal brand continues in the underlying battle footer.',
 '52-flow-map':'Formal emblem/title stay inside the header; flow grid, labels and returns remain readable.',
 '26-battle-build-full':'Six active and six passive slots; active evolution and passive Lv1–5 labels separated.',
 '29-upgrade-new':'Three new choices are unheld; buttons fit inside cards with consistent alignment.',
 '30-upgrade-existing':'Owned upgrade values match source; first HUD skill Lv4 matches card4→5.',
 '31-upgrade-moneybag':'Max-level full build supports all-moneybag fallback; still choose only one.',
 '34-treasure-five':'Five visible rewards and extra950; button and footer explicitly collect all.',
 '35-treasure-evolution':'Lv11 and held matching passive in background; evolved reward remains part of chest.',
 '36-treasure-moneybag':'All twelve background skills maxed; five moneybags all collected.',
 '47-evolution-locked':'Card footnotes now sit within each card; missing prerequisites remain explicit.',
 '48-evolution-ready':'Prerequisites checked; only continue and view options, no immediate evolution action.',
 '51-control-states':'Light normal/pressed tabs and list rows now use dark text; five state groups visible.'
}
records=[]
for i,row in enumerate(coverage['screens']):
    with Image.open(ROOT/row['screenPath']) as im: assert im.size==(1920,1080)
    assert sha(row['screenPath'])==layouts[row['id']]['screenSha256']
    for asset in row['independentAssets']:assert (ROOT/asset).is_file(),asset
    record={'id':row['id'],'file':row['screenPath'],'sha256':sha(row['screenPath']),'dimensions':[1920,1080],
            'reviewMethod':'contact sheet + original-resolution image' if row['id'] in full_views else 'contact sheet + exported text/asset regions',
            'contactSheet':f'designs/ui-suite/review/contact-{i//8*8+1:02d}-{min(i//8*8+8,52):02d}.jpg',
            'checks':{'style':True,'layout':True,'noMissingAsset':True,'chineseGlyphCoverage':True,'statePresentation':True,'safeArea':True},
            'note':notes.get(row['id'],'Consistent jade/ivory/gold hierarchy; labels, selection/disabled state, actions and spacing inspected in this batch.'),
            'status':'accepted_ui_art'}
    records.append(record)
    row.update(productionStatus='complete',acceptanceStatus='accepted_ui_art',acceptanceEvidence=['docs/ui-suite/final-visual-review.json','docs/ui-suite/render-verification.json'])
coverage['status']='ui_art_complete_unity_integration_pending'
coverage['uiAcceptedOn']=client_date
coverage['brandingStatus']='formal_brand_synchronized_all52'
coverage['wholeGameArtStatus']='UI subset accepted with formal brand refresh; full art acceptance is recorded separately in docs/whole-game/ACCEPTANCE.json.'
write('docs/ui-suite/UI_COVERAGE.json',coverage)
review={'schemaVersion':1,'reviewer':'ui_brand_refresh_with_independent_visual_qa','reviewedOnClientDate':client_date,'recordedAtUtc':now,
 'scope':'52 UI full-screen/state/flow images; not full non-UI game art or Unity integration',
 'method':'Independent reviewer viewed all7 contact sheets and original-resolution01/04/05/25/40/51/52. Implementing reviewer also viewed01/02/04/05/25/40/51/52. Checked exported text and asset mappings for all52. Authorized formal-brand rerender supersedes previous screen hashes; pre-brand evidence remains archived.',
 'gameName':'一炁当千','displayTagline':'一人成阵，万妖退散','independentReview':'docs/ui-suite/brand-visual-independent-review.json','preBrandEvidence':'docs/ui-suite/acceptance-history/pre-brand-20261029/snapshot-index.json',
 'sourceFiles':render['sourceFiles'],'summary':{'accepted':52,'needsRevision':0,'missingResources':0,'baseRenderChecks':52,'responsiveChecks':104},
 'font':{'file':'art/fonts/NotoSansSC-Regular.otf','method':'OpenType cmap formats4/12 read using standard-library struct','uniqueTextCharacters':len(set(all_text)),'missingGlyphs':missing},
 'semanticChecks':semantic,'screens':records,
 'limitations':['Browser compositing and state navigation are visual review only; no game logic or saves are exercised.','Unity import, nine-slice rendering, Prefabs, input and gameplay integration remain next phase.','Combat screen actor stills and the arena plate are layout art; this report does not claim full enemy/character animation or map replacement completion.']}
write('docs/ui-suite/final-visual-review.json',review)

original_receipt=read('docs/ui-suite/accepted-ui-resource-receipt.json')
manifest=read('art/manifest.json')
current_assets={item['file']:item for item in manifest['assets']}
for item in original_receipt['assets']:
    assert current_assets[item['file']]['sha256']==item['sha256']==sha(item['file'])
ui_paths={item['file'] for item in original_receipt['assets']}
ui_paths.update(item['file'] for item in manifest['assets'] if item.get('brandingStatus')=='formal_branding_resource')
receipt_assets=[current_assets[path] for path in sorted(ui_paths)]
write('docs/ui-suite/accepted-ui-branded-resource-receipt.json',{
    'schemaVersion':1,'scope':'Accepted UI resource subset: unchanged original88 resource files plus8 formal branding resources. Old unselected wordmark is production source only.',
    'gameName':'一炁当千','recordedAtUtc':now,'clientDate':client_date,
    'originalReceipt':'docs/ui-suite/accepted-ui-resource-receipt.json','originalReceiptSha256':sha('docs/ui-suite/accepted-ui-resource-receipt.json'),
    'sourceManifest':'art/manifest.json','sourceManifestSha256AtExtraction':sha('art/manifest.json'),
    'sourceTextSnapshots':manifest['sourceTextSnapshots'],'assets':receipt_assets,
    'counts':{'files':len(receipt_assets),'originalResources':len(original_receipt['assets']),'formalBrandResources':len(receipt_assets)-len(original_receipt['assets'])},
    'unityIntegration':'not-performed; import values remain advice only'})

functional=read('docs/ui-suite/functional-art-review.json')
functional.setdefault('originalResult',functional['result']);functional['result']='resolved_in_final_ui_art_review';functional['followupAtUtc']=now
functional['followupEvidence']=['docs/ui-suite/final-visual-review.json','docs/ui-suite/render-verification.json']
for finding in functional['findings']:
    finding.setdefault('originalStatus',finding['status']);finding['status']='resolved_in_final_ui_art'
    finding['resolution']={'F01':'Separate active/passive badges; passives maximum5.','F02':'BothSide2→3 now damage+10.','F03':'Moneybag full/maxed backgrounds and evolution-compatible pendingMix background.','F04':'New cards changed to Chain/FourCorner/HPMax; existing card HUD nowLv4.','F05':'Five-reward extra gold now950.'}[finding['id']]
for check_row in functional['checks']:
    if check_row['status']!='pass_art_content':
        check_row.setdefault('originalStatus',check_row['status']);check_row['status']='pass_art_content_after_correction'
functional['finalArtifactHashes']=render['sourceFiles']
write('docs/ui-suite/functional-art-review.json',functional)

md=['# 一炁当千 · UI 功能与资源总清单','',f'{client_date}，正式品牌已同步并验收：52 张整屏／状态／流程画面，52 份文字与图层映射。不是52种独立游戏系统；整款非UI素材与动作验收见另行总账。',
    '',f"功能参考固定版本 `{coverage['referenceGame']['commit']}`。已有功能、展示状态补齐与建议补充分别标明；Unity接入待下一阶段。",'','| ID | 系统 | 界面／状态 | 依据 | 制作／验收 | 整屏 |','| --- | --- | --- | --- | --- | --- |']
for row in coverage['screens']:
    md.append(f"| {row['id']} | {row['system']} | {row['interface']} · {row['state']} | {row['basis']} | 完成／UI美术通过 | [{row['id']}](../../{row['screenPath']}) |")
md.extend(['','existing=参考已有功能；supporting_state=已有功能的展示状态补齐；suggested=明确标注的美术建议。','','## 不适用／未发现的系统',''])
md.extend(f"- **{r['system']}**：{r['reason']}" for r in coverage['excludedSystems'])
md.extend(['','每屏独立资源与参考依据见同名JSON；字号、文案、颜色、文字区域与图层见 `designs/ui-suite/layouts/`。','',
 '[最终UI美术验收](ACCEPTANCE.md)、[视觉与语义记录](final-visual-review.json)、[156次视口检查](render-verification.json)、[Unity导入建议](UNITY_ART_IMPORT.md)。'])
(ROOT/'docs/ui-suite/UI_COVERAGE.md').write_text('\n'.join(md)+'\n',encoding='utf-8')

qc=[read(f'docs/icon-atlas{i}-slices.json') for i in [1,2]]
accept=['# 一炁当千 · UI 美术验收记录','',f'{client_date}。本记录验收正式品牌同步后的 UI 整屏、控件、图标与排版；整款游戏角色、敌人、场景和动画资源验收见另行总账。',
 '', '## 本批结果','',
 '- 52/52张1920×1080整屏／状态／流程画面及相应布局JSON已导出；0缺图、0脚本异常、0文字出画布。',
 '- 全52屏分别检查1280×720及2560×1080视口，共104次等比安全区检查；与52次基准合计156次。通过的是浏览器美术预览适配，不是Unity适配。',
 '- 查看全部7张汇总；本批另查看01、02、04、05、25、40、51、52原尺寸图。52屏正式名称和Logo资源映射一致，中文无缺字，页眉、启动卡片和战斗页脚未遮挡控件。独立视觉记录绑定当前哈希；旧屏哈希保存在pre-brand历史目录。',
 '- 原88项UI资源字节不变，另纳入8项正式品牌资源；旧未选用Logo仅保留为来源，不作为正式UI。当前UI资源回执为accepted-ui-branded-resource-receipt.json。',
 '- 15张控件状态PNG哈希、画布及Alpha核验通过；三类控件各普通/按下/选中/禁用/锁定画布与Pivot一致。',
 '- Noto字体OpenType cmap覆盖本批全部非空白字符，无缺字。动态文字单独排版，不烘焙在控件底图。',
 '- 源业务审查F01–F05已修复；新道法与已持有HUD不再重复，30御剑背景等级与4→5一致。被动上限5、主动11、宝箱全收与待宝箱进化条件保持准确。',
 '', '## 原图集QC的原始失败与警告（保留，不改写成通过）','',
 '模型原图不满足等分4×4切图合同，禁止直接按等格切片。最终采用逐行Alpha谷值定义的归属矩形，原生裁切后补透明画布；没有缩放、清边或AI修图。最终32张独立图标的所有源Alpha像素恰好归属一次，无跨归属主要连通块，明暗底检查通过。细微原生Alpha散点仍保留。',
 '', '| 原图 | 检查ID | 原始状态 | value（原值） | threshold（原值） |','| --- | --- | --- | --- | --- |']
for sheet in qc:
    for c in sheet['rawSheetQC']['reportedChecks']:
        accept.append(f"| `{sheet['sheet']}` | `{c['id']}` | **{c['status']}** | `{json.dumps(c['value'],ensure_ascii=False,separators=(',',':'))}` | `{json.dumps(c['threshold'])}` |")
accept.extend(['','完整原始结构、受影响路径与归属切片验收：', '', '```json',json.dumps([{'sheet':q['sheet'],'rawSheetQC':q['rawSheetQC'],'slicedAssetQC':q['slicedAssetQC']} for q in qc],ensure_ascii=False,indent=2),'```',
 '', '## 边界与下一阶段','',
 '本批屏幕是浏览器DOM/CSS、已有PNG与独立文本的合成设计图，不是模型新生成整屏，也不是Unity运行截图。图标512×512是原生裁切后补透明画布，不能当成新生成的512像素内容细节。生成模型/质量未由入口披露的字段仍为未确认。',
 '', 'Unity Sprite导入、九宫格、字体图集、Prefab、业务状态、存档、输入和设备显示尚未执行；Border/Pivot等均为有来源记录的接入建议。战斗中的静态人物及场景板不构成全部角色/敌人动作验收。',
 '', 'F盘美术库只读，关联记录已集中在本项目 `docs/image-reference-associations.md`。未进行Git提交、推送、发布或付费路线切换。',
 '', '[UI总清单](UI_COVERAGE.md) · [逐屏视觉记录](final-visual-review.json) · [渲染记录](render-verification.json) · [Unity导入建议](UNITY_ART_IMPORT.md)'])
(ROOT/'docs/ui-suite/ACCEPTANCE.md').write_text('\n'.join(accept)+'\n',encoding='utf-8')
print(json.dumps({'acceptedScreens':52,'responsive':104,'missingGlyphs':missing,'semanticChecks':len(semantic)},ensure_ascii=False))
