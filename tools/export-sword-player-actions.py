"""Export only identity-matched existing locomotion art. No generation or Unity code."""
import hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('F:/work/image/qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin')
OUT=ROOT/'art/whole-game/players/sword'
DOC=ROOT/'docs/whole-game'
DOC.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source_manifest=json.loads((SOURCE/'manifest.json').read_text(encoding='utf-8-sig'))
legacy_files={r['path']:r for r in source_manifest['files']}
assert source_manifest['portrait_v11_sha256']==sha(ROOT/'art/characters/sword.png')
records=[];clips=[]
for facing in ['E','W']:
    for action,paths in [('idle',[f'idle/{facing}.png']),('run',[f'walk/{facing}/{i:02d}.png' for i in range(1,9)])]:
        frames=[]
        for i,rel in enumerate(paths):
            src=SOURCE/rel;dest_rel=rel.replace('walk/','run/');dst=OUT/dest_rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            current=sha(src)
            assert current==legacy_files[rel]['sha256'],rel
            if dst.exists():assert sha(dst)==current, 'Refuse overwriting another result: '+str(dst)
            else:shutil.copyfile(src,dst)
            with Image.open(dst) as im:
                assert im.size==(512,512) and im.mode=='RGBA'
                alpha=im.getchannel('A');assert alpha.getextrema()==(0,255)
                pixelinfo={'canvas':[512,512],'mode':'RGBA','alphaExtrema':alpha.getextrema(),'alphaBoundsXYXY':alpha.getbbox()}
            relative=dst.relative_to(ROOT).as_posix();frames.append(relative)
            records.append({'file':relative,'sha256':current,'sourceRelativeToArtRepository':'qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin/'+rel,'sourceAbsolute':str(src),'operation':'byte-for-byte copy; no scaling, crop, alignment, AI edit or new generation in this project','sourceManifestEntryHashMatches':True,'pixelInfo':pixelinfo,'rootPx':[256,471],'pivotNormalizedBottomLeft':[.5,41/512],'spriteTypeRecommendation':'Single','action':action,'facing':facing,'phase':i+1})
        if action=='run':assert len(set(sha(ROOT/f) for f in frames))==8
        clips.append({'name':action+'_'+facing,'action':action,'facing':facing,'frames':frames,'frameDurationMs':60 if action=='run' else 1000,'loop':True,'totalDurationMs':480 if action=='run' else 1000,'timingBasis':'Historical authored walk cycle8×60ms; suggested mapping to source Run state, not a verified source Animator clip duration.' if action=='run' else 'Static dedicated idle;1000ms is preview hold only.','sourceActionLabel':'walk' if action=='run' else 'idle'})
    src=SOURCE/f'walk/{facing}/strip.png';dst=OUT/f'run/{facing}/strip.png'
    if dst.exists():assert sha(dst)==sha(src)
    else:shutil.copyfile(src,dst)
    records.append({'file':dst.relative_to(ROOT).as_posix(),'sha256':sha(dst),'sourceRelativeToArtRepository':'qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin/walk/'+facing+'/strip.png','operation':'byte-for-byte copy of existing8×512strip','canvas':[4096,512],'spriteTypeRecommendation':'Multiple','sliceRectanglesXYWH':[[i*512,0,512,512] for i in range(8)],'isFrame':False})

evidence=DOC/'player-sword-source';evidence.mkdir(exist_ok=True)
for rel in ['manifest.json','visual-review.json','qc.json','validation.json','processing/portrait-source.json','processing/sources.json','processing/frame-transforms.json']:
    target=evidence/Path(rel).name
    shutil.copyfile(SOURCE/rel,target)
animation={'schemaVersion':1,'character':'sword','workingName':'逍遥剑修','sourceIdentity':'24_lu_dongbin','artSource':'existing','route':'read-only verified source copy','canvas':[512,512],'rootPx':[256,471],'rootBasis':'Source alignmentv3 fixed idle head ROI/top, not per-frame lowestalpha registration','pivotNormalizedBottomLeft':[.5,41/512],'clips':clips,'files':records,'unityExecuted':False,'limits':['Eight authored walk phases are supplied as locomotion mapped to source Run; movement-speed cadence must be calibrated at Unity integration.','No new attack/cast/hit/death body sequence is required by reference PlayerAnim: auto-skills, hit material flash and death fade are independent effects.','Existing fine saturated edge pixels were not changed; view over game backgrounds and validate platform compression later.','Historical model/quality labels are not actual returned version evidence; actual model and quality remain unconfirmed.']}
write(OUT/'animation.json',animation)

# Display-sized preview uses existing frames; source pixels are untouched.
preview=ROOT/'designs/whole-game/players';preview.mkdir(parents=True,exist_ok=True)
font=ImageFont.truetype(str(ROOT/'art/fonts/NotoSansSC-Regular.otf'),16)
sequence=[]
for phase in range(1,9):
    canvas=Image.new('RGB',(768,256),'#eee6ce');draw=ImageDraw.Draw(canvas)
    for col,(facing,bg) in enumerate([('E','#f6efd9'),('E','#183e32'),('W','#f6efd9'),('W','#183e32')]):
        x=col*192;draw.rectangle((x,0,x+191,255),fill=bg)
        im=Image.open(OUT/f'run/{facing}/{phase:02d}.png').convert('RGBA').resize((192,192),Image.Resampling.LANCZOS)
        canvas.paste(im,(x,10),im)
        draw.text((x+20,212),f'{facing} · {phase:02d}/08',font=font,fill='#355c40' if col%2==0 else '#eee6c9')
    sequence.append(canvas)
sequence[0].save(preview/'sword-run-review.gif',save_all=True,append_images=sequence[1:],duration=60,loop=0)
sequence[0].save(preview/'sword-run-review.png')
previewrecord={'file':'designs/whole-game/players/sword-run-review.gif','operation':'Display-size four-column light/dark composite of copiedE/W phases, quantizedGIF preview only','frames':8,'frameDurationMs':60,'sha256':sha(preview/'sword-run-review.gif')}
write(preview/'sword-run-review.json',previewrecord)

audit={'schemaVersion':1,'verifiedOn':'2026-10-28','recordedAtUtc':datetime.now(timezone.utc).isoformat(),'projectRoot':str(ROOT),'artReferenceReadOnly':True,'referenceGame':{'url':'https://github.com/Roo-Roo-Roo/survivors-roguelike-kit','commit':'3f905381d73a34b516030528b8ef6743868b9e52'},'sourceRequirements':{'bodyStates':['Idle','Run'],'facing':'PlayerMovement flipslocalScale.x whenhorizontalinput changes; eight directions are not required','hit':'PlayerHit invokes material flash; no bodyHit state required','death':'PlayerHit fades materialAlpha and shadow; no bodyDeath state required'},
 'referenceCode':['Assets/RGame/RoguelikeKit/Scripts/Game/Player/Animator/PlayerAnim.cs','Assets/RGame/RoguelikeKit/Scripts/Game/Player/Movement/PlayerMovement.cs','Assets/RGame/RoguelikeKit/Scripts/Game/Player/Hit/PlayerHit.cs'],
 'players':[{'id':'hero','uiMaster':'art/characters/hero.png','identity':'金发带、棕短刺发、玉绿金边白袍、白灯笼裤、青白靴、太极葫芦','matchedExistingActions':False,'status':'needs_new_same_identity_rig_art','evidence':['qdao_chibi_game_pack_v4/README.md explicitly describes static only','q_daoist_character_pack_4096/README.md explicitly describes static portraits','qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy contains manifestonly and0PNG'],'required':['Idle','Run'],'doNotUse':'Do not restore oldGit or treat4096resampledstill as animation.'},
 {'id':'sword','uiMaster':'art/characters/sword.png','identity':'24_lu_dongbin，黑髻白剑簪、青黑马甲白袍黑裤、背剑红穗与腰间葫芦','matchedExistingActions':True,'status':'exported_existing_locomotion','source':str(SOURCE),'identityEvidence':{'currentUiMasterSha256':sha(ROOT/'art/characters/sword.png'),'sourcePortraitBaselineV11Sha256':source_manifest['portrait_v11_sha256'],'matches':True,'visualReview':'Viewed UI master, source portrait, Eidle, all8E/Wwalk poses as strips; same identity and clothing, authored alternating legs/arms.'},'availableSource':'8direction×8walk+8idle+8strips+portrait=81PNG','selectedExport':'18frames E/W (idle1+run8 each) plus2compatibilitystrips','animation':'art/whole-game/players/sword/animation.json','frames':records},
 {'id':'healer','uiMaster':'art/characters/healer.png','identity':'29_he_xiangu，黑髻白莲簪玉穗、青绿粉莲短袍、深绿短裤、白靴、背后粉莲苞','matchedExistingActions':False,'status':'needs_new_same_identity_rig_art','rejectedCandidates':[{'path':'qdao_chibi_roster_v12/candidate-natural-body/29_he_xiangu','realPngCount':81,'reason':'Samehistoricalidentity but revisedplainmintlongcoat,longtrousers,andivoryshoes; conflicts with current shortpinklotusoutfit. SourceREADME explicitly describes this costume revision.'},{'path':'qdao_original_roster_v14_hd/action-remake-20261001/characters/03_lotus_healer_girl','realPngCount':144,'reason':'ActualE01 viewed:brownlonghair,goldcrown,longpinkdress,lanternandbottle; different character identity, not UIHeXiangu.'}],'required':['Idle','Run']}],
 'newProductionContract':{'artSource':'builtin image_gen for sixnativeRGBA bodyparts, then deterministic layered skeleton art compositing; no video generation','parts':['head','torso','near_arm','far_arm','near_leg','far_leg'],'canvas':[512,512],'rootPx':[256,470],'pivotPerPart':'Native pixel joint chosen manually after inspecting actual image','scalePerPart':'Calibrate actual native part sizes to one character proportion; not equal-size stretching','drawOrder':['far_leg','far_arm','torso','near_leg','near_arm','head'],'locomotion':'Independent opposite arm/leg phases, swing clearance and alternating support; no whole-still bob substitute','clips':{'Idle':{'frames':16,'frameMs':60},'Run':{'frames':16,'frameMs':60}},'timingNote':'960ms is a new art suggestion; no assertion about original source clip duration.'},
 'constraints':['Do not alter art/characters or UIreferences.','NoFwrites,oldGitrestore,Gitmutation,paidvideo,toolsinstallationorUnitycode.'],'evidenceCopiedTo':'docs/whole-game/player-sword-source/'}
write(DOC/'player-actions-audit.json',audit)
md='''# 三名角色动作美术核查

2026-10-28。F盘只读；未恢复旧Git、未调用付费视频、未安装工具、未编写Unity接入。

## 结论

| 当前人物 | 匹配动作 | 处理 |
| --- | --- | --- |
| 青云小道／金发带男 | 未发现 | 现存v4与4096包均为静态；v14的00动作目录现存0PNG。制作同母版六部件骨骼美术。 |
| 逍遥剑修／吕洞宾 | 有 | V12实存81PNG；取E/W独立Idle各1帧、真实步态各8帧，共18帧，以及2张兼容条带。 |
| 清莲灵修／粉莲短袍何仙姑 | 未发现匹配当前服装者 | V12何仙姑已改素绿长袍长裤，03莲花医者为棕长发冠、灯与瓶的另一人物，均不替换当前UI身份。制作同母版六部件骨骼美术。 |

实际读取v4、4096人物包、V12的README与CLIENT_CONTRACT；V12吕洞宾manifest、QC、visual-review、portrait-source、frame-transforms；03莲花医者MERGE_HANDOFF。实际查看当前三立绘、吕洞宾肖像/E站立/E与W全部8帧条带、V12何仙姑肖像/E站立/8帧条带、03莲花E01及4096金发带静态图。不能凭角色目录名认定匹配。

## 吕洞宾来源与导出

当前UI剑修SHA与V12 `processing/portrait-source.json`中的`baseline_v11_sha256`完全相同：`ea2228db505fbc057da4b4056d08e9bd00ddc0832921e1b37b148ac703b43989`。动作图保留黑髻剑簪、青黑白衣、背剑红穗、腰葫芦。E/W腿与臂有独立交替姿势，不是整图平移。

正式目录：`art/whole-game/players/sword/`。全部512×512RGBA单帧按字节复制，Alpha0–255，哈希与现存来源manifest一致；没有新缩放、重绘、裁切或生成。固定根点沿用源v3 `(256,471)`，Pivot建议`(0.5,0.080078125)`，不是每帧最低脚点重新贴地。

原动作名walk，以Run状态的locomotion美术映射供后续接入；8×60ms=480ms是来源美术时序，不宣称其为参考游戏原Animator实际时长。静止图为独立Idle，1000ms仅预览停留。细微原生饱和边缘不在本次改写，平台压缩与背景显示在Unity中验证。

`PlayerAnim.cs`只切Idle/Run；`PlayerMovement.cs`仅按横向输入翻转x朝向。`PlayerHit.cs`使用材质受击及死亡淡出，因此不虚增人物普攻/施法/受击/倒地序列为当前源码必需项。技能本体特效单独完成。

[逐帧/来源清单](player-actions-audit.json)、[动作资源参数](../../art/whole-game/players/sword/animation.json)、[明暗底循环预览](../../designs/whole-game/players/sword-run-review.gif)。历史来源记录已只读复制在`player-sword-source/`；旧E盘路径按历史证据保留，不表示本机原始生成母图仍存在。

## 另外两人的部件与动作合同

每人六张真正独立RGBA：head、torso、near_arm、far_arm、near_leg、far_leg。逐件记录native关节pivot、512画布的绑定关节、手工比例、层序、父骨骼和原生裁切来源。按实际部件大小校准，不能把六张图同宽拉伸。

512固定画布/脚底锚点，Idle/Run各16帧、每帧60ms；0.96秒是本次美术建议。Run须腿与手臂反相、两腿交替支持/抬离地面，躯干微前倾、头独立补偿；动作由真实部件分层旋转与合成，不能将完整立绘晃动当作跑步。保留曲线、帧坐标、关节覆盖、Alpha、环接及明暗底预览记录。不是AI视频，也不伪称新模型生成的每帧原画。
'''
(DOC/'player-actions-audit.md').write_text(md,encoding='utf-8')
print(json.dumps({'frames':18,'strips':2,'status':'exported_existing_identity_matched','missingPlayers':['hero','healer'],'preview':previewrecord},ensure_ascii=False))
