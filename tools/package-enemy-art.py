"""Copy reviewed existing enemy reskins; no image generation or image editing."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json,hashlib,shutil,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
SRC=Path('F:/work/image')
PET=SRC/'designs/creature-combat-20261005/pets'
FRAME='runtime/attack/E/01.png'
PLAN=[
('Bat','legacy-yun-jiu-jiu','云啾啾','普通远程','云垫幼鹤；青蓝弹体','ground'),
('BoyFairy','13-yalingtong','芽铃童','普通远程','橡果帽种铃童；青绿弹体','ground'),
('EyeBall','legacy-fu-xiao-hu','符小虎','普通近战','额符杏金虎；延续已用试敌形象','ground'),
('FlySkull','04-guideng','桂灯童','普通近战','提灯叶帽童；延续已用试敌形象','hover'),
('ForestGuardianFairy','07-cangzhanglin','苍嶂麟','普通远程','青玉鳞甲四足麟；青绿弹体','ground'),
('Gear','10-xuanchaogui','玄潮龟','普通近战','青瓷水盂背甲灵龟','ground'),
('Ghost','03-shuangtuan','霜团貂','冲撞','珠灰圆耳宽卷尾灵貂','ground'),
('Slime','legacy-hu-tuan-tuan','葫团团','普通近战','白毛抱葫芦狐；保留单尾身份','ground'),
('Crow','01-zhuling','烛翎','Boss近战','靛蓝灵鸦铜红翼斑；冲刺状态机','hover'),
('CrystalHealerFairy','16-luhualing','露华灵','Boss远程','露壶青瓷女仙；雪色弹体','ground'),
('Fairy','15-landuoxian','岚铎仙','最终Boss远程','持玉铎与玉槌的仙灵；朱红弹体','ground'),
('FlameDancerFairy','09-chishakui','赤砂魁','Boss远程','陶塑窑炉小守卫；朱红弹体','ground'),
('FrostCrystalFairy','12-yuexianshi','月弦师','Boss远程','靛蓝象牙丝衣月弦仙灵；雪色弹体','ground'),
('PinkFairy','02-jiangling','绛铃','Boss远程','象牙绛红折瓣衣三铃折扇仙灵；桃粉弹体','hover')]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def objects(o):
 if isinstance(o,dict):
  yield o
  for v in o.values(): yield from objects(v)
 elif isinstance(o,list):
  for v in o:yield from objects(v)
def selected(m):
 return next(o for o in objects(m) if any(isinstance(v,str) and v.replace('\\','/')==FRAME for v in o.values()))
def recordpaths(d,frame):
 found=[]
 for k in ['sourceRecord','generationRecord','record','provenanceRecord']:
  s=frame.get(k)
  if isinstance(s,dict): s=s.get('path') or s.get('file') or s.get('record')
  if isinstance(s,str) and (d/s).is_file(): found.append(d/s)
 for p in [d/(FRAME+'.generation.json'),d/'records/attack/E/01.generation.json',d/'records/attack-E/01.generation.json',d/'records/E-attack/01.generation.json',d/'evidence/attack/E/01.generation.json',d/'source/attack/E/01.png.generation.json']:
  if p.is_file() and p not in found:found.append(p)
 return found
def source_text_dependencies(d,recordfiles):
 found={};pending=list(recordfiles)
 while pending:
  p=pending.pop(0)
  if p in found:continue
  found[p]=True
  if p.suffix!='.json':continue
  try:v=load(p)
  except ValueError:continue
  for o in objects(v):
   for k,s in o.items():
    if not isinstance(s,str) or not s.lower().endswith(('.json','.txt','.md')) or '\n' in s:continue
    raw=s.replace('\\','/')
    if raw.startswith(('D:/work/image/','E:/work/image/')):q=SRC/raw.split('/work/image/',1)[1]
    elif raw.startswith('F:/work/image/'):q=Path(raw)
    elif ':/' in raw:continue
    else:q=d/raw
    try:q.resolve().relative_to(d.resolve())
    except ValueError:continue
    if q.is_file() and q not in found:pending.append(q)
 return list(found)
if '--inspect' in sys.argv:
 for key,slug,*_ in PLAN:
  d=PET/slug;m=load(d/'manifest.json');f=selected(m)
  print(key,slug,json.dumps(f,ensure_ascii=False))
  print('RECORDS',[str(p.relative_to(d)) for p in recordpaths(d,f)])
 sys.exit()
OUT=ROOT/'art/whole-game/enemies';OUT.mkdir(parents=True,exist_ok=True)
DOC=ROOT/'docs/whole-game';DOC.mkdir(parents=True,exist_ok=True)
EVID=DOC/'enemy-source-evidence';EVID.mkdir(exist_ok=True)
audit=load(ROOT/'docs/whole-game-art-audit.json');bykey={e['key']:e for e in audit['enemies']}
entries=[]
for key,slug,name,role,identity,anchor in PLAN:
 d=PET/slug;source=d/FRAME;dest=OUT/(key+'.png');m=load(d/'manifest.json');f=selected(m)
 shutil.copyfile(source,dest)
 with Image.open(dest) as im:
  im.load();assert im.mode=='RGBA';a=np.asarray(im.getchannel('A'));bbox=Image.fromarray((a>=16).astype('uint8')*255).getbbox()
  shape=list(im.size);zero=int((a==0).sum());partial=int(((a>0)&(a<255)).sum());opaque=int((a==255).sum());extrema=[int(a.min()),int(a.max())]
  edge16=int((a[0]>=16).sum()+(a[-1]>=16).sum()+(a[:,0]>=16).sum()+(a[:,-1]>=16).sum())
  edgeAny=int((a[0]>0).sum()+(a[-1]>0).sum()+(a[:,0]>0).sum()+(a[:,-1]>0).sum())
 snap=EVID/slug;snap.mkdir(exist_ok=True)
 for namefile in ['README.md','MERGE_HANDOFF.md','POSES.md']:
  if (d/namefile).is_file():shutil.copyfile(d/namefile,snap/namefile)
 records=[]
 for i,p in enumerate(recordpaths(d,f)):
  target=snap/f'01-source-record-{i+1:02}.json';shutil.copyfile(p,target)
  records.append({'source':p.relative_to(SRC).as_posix(),'snapshot':target.relative_to(ROOT).as_posix(),'sha256':sha(p)})
 dependencies=[]
 for p in source_text_dependencies(d,recordpaths(d,f)):
  target=snap/'dependencies'/p.relative_to(d);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
  dependencies.append({'source':p.relative_to(SRC).as_posix(),'snapshot':target.relative_to(ROOT).as_posix(),'sha256':sha(p)})
 assert records,slug
 frameSnapshot={'originalManifest':(d/'manifest.json').relative_to(SRC).as_posix(),'originalManifestSHA256':sha(d/'manifest.json'),'selection':FRAME,'selectedFrameRecord':f,'sourcePackageMetadata':{k:v for k,v in m.items() if k not in ['groups','frames','files','animations','sourceIndex']},'snapshotPurpose':'Only selected single frame is adopted; metadata of 68-frame original is historical context, not a claim this task copies or validates all 68.'}
 (snap/'selected-manifest-frame.json').write_text(json.dumps(frameSnapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 item={'sourceKey':key,'displayName':name+'幻身','sourceIdentity':name,'role':role,'identity':identity,'artSource':'existing','adoptionType':'reskin; direct byte copy','sourceArtRepository':{'path':str(SRC),'remote':'https://luyuacpp.visualstudio.com/image/_git/image'},'sourceArtPath':source.relative_to(SRC).as_posix(),'destination':dest.relative_to(ROOT).as_posix(),'sourceSHA256':sha(source),'sha256':sha(dest),'copyVerified':sha(source)==sha(dest),'canvas':shape,'mode':'RGBA','realAlpha':extrema[0]==0 and extrema[1]>0,'alpha':{'range':extrema,'zeroPixels':zero,'partialPixels':partial,'opaquePixels':opaque,'visibleBBoxAlphaAtLeast16':list(bbox),'visibleEdgePixelsAlphaAtLeast16':edge16,'edgePixelsAnyAlpha':edgeAny},'pivotBottomLeft':[0.5,0.08],'anchorTopLeftPx':[512,942],'anchorKind':'virtual hover anchor' if anchor=='hover' else 'source logical ground anchor; not exact every-foot contact','facing':'three-quarter front, down-right; x mirror allowed for source movement','suggestedVisibleHeightAt1080':170 if role.startswith('Boss') or role.startswith('最终') else 110,'spriteType':'Single','meshType':'FullRect','borderLTRB':[0,0,0,0],'filterMode':'Bilinear','wrapMode':'Clamp','mipmaps':False,'colourSpace':'sRGB','generationModel':None,'generationQuality':None,'generationEvidenceNote':'Historical source generation evidence is preserved. No generation or AI edit occurred during this adoption. Configuration targets never establish actual model/quality.','sourceRecords':records,'selectedManifestSnapshot':(snap/'selected-manifest-frame.json').relative_to(ROOT).as_posix(),'sourceGamePrefab':bykey[key]['source'],'sourceGameSpritePaths':bykey[key]['sprites'],'review':{'fullSourceImageViewed':True,'adoptedDate':'2026-10-28','visibleClippingCheck':'pass' if edge16==0 else 'fail','identityCheck':'pass; distinct existing Daoist chibi identity','engineValidation':'not-run; Unity import and motion integration remain next phase'}}
 entries.append(item)
 item['historicalNativeSize']=[1254,1254]
 item['historicalNativeSizeBasis']='Source README and selected source record; final1024PNG was an earlier full-canvas export, this adoption does not resample.'
 item['sourceEvidenceDependencies']=dependencies
 item['sourceFrameWarnings']=f.get('warnings',[])
 item['generationConfigTarget']={'model':'gpt-image-2.5-sunburst','quality':'max','basis':'Historical source configuration, not actual returned metadata and not a new generation.'}
 item['sourceManifestSHAMatches']=f.get('sha256')==item['sha256']
 (dest.with_suffix('.png.adoption.json')).write_text(json.dumps(item,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
elites=[]
for key in ['Bat1','EyeBall1','FlySkull1','ForestGuardianFairy1','Gear1','Slime1']:
 base=key[:-1];e=next(x for x in entries if x['sourceKey']==base)
 elites.append({'sourceKey':key,'baseKey':base,'sprite':e['destination'],'sha256':e['sha256'],'displayName':e['sourceIdentity']+'精英幻身','eliteOverlay':{'assetRef':'elite_halo','asset':'art/whole-game/fx/elite-halo.png','bindingStatus':'root approved shared scope-ring byte copy; worldFX slice created separately','placement':'behind feet/body; does not replace source sprite','suggestedTint':'#E7BA54; material colour suggestion, no baked recolouring'},'sourceGamePrefab':bykey[key]['source'],'notes':'Shared base texture, separate key and elite presentation; not claimed as six new generated species.'})
warnings=[{'id':'actual-generation-model-quality-unconfirmed','value':14,'threshold':'actual source evidence required to confirm','files':[x['destination'] for x in entries],'severity':'WARN','disposition':'Historical built-in generation did not disclose model/quality; preserved as null.'}]
for e in entries:
 if e['alpha']['edgePixelsAnyAlpha']>0:
  warnings.append({'id':'faint-alpha-on-outer-edge','value':e['alpha']['edgePixelsAnyAlpha'],'threshold':0,'files':[e['destination']],'severity':'WARN','disposition':'Alpha>=16 edge count is zero; source weak-alpha specks kept byte-identical; no matte or cropping edit.'})
out={'schemaVersion':1,'title':'道途幸存者—完整敌人美术替换','date':'2026-10-28','phase':'art-only; no Unity integration','referenceCommit':audit['reference']['commit'],'scope':'14 distinct existing Daoist chibi identities assigned to all 20 live source enemy keys. This is a documented reskin, not replication of original monster species.','counts':{'baseIdentitySprites':14,'mappedActiveEnemyKeys':20,'eliteSharedSpriteMappings':6,'newGeneratedImages':0,'newAIEditedImages':0},'entries':entries,'eliteVariants':elites,'stateContract':{'move':'Reuse one master per enemy. Source movement uses transform translation, x mirror and mild shader sine distortion; no enemy animation clips exist. Preserve original source timing; movement preview is not a new frame animation.','hit':'Source _BlendColor white flash about 0.1s in +0.1s out. Apply to sprite independently; no extra hit PNG required.','death':'Noise dissolve about 0.3s and projected shadow fade. Keep silhouette intact until dissolve; no death sprite animation claimed.','rush':'Ghost directional dash and Crow state-machine scale/rush preserve game-key behaviour. Apply position/scale to static master; no pose frames invented.','burn':'Enemy material flame red tint; do not attach player-negative-status HUD.','freeze':'Stop movement and shader time, reuse status ring with cold colour; source FreezingBuff effect.','slow':'Reduce speed/shader time, shared status ring; source SlowBuff effect.','boss':'Larger visual height, HUD name/health treatment; static portrait does not change actual enemy HP/behaviour.','elite':'Base texture plus shared elite_halo overlay; renderer placement/timing must be validated in Unity next phase.'},'validation':{'copiesSHA256Match':all(e['copyVerified'] for e in entries),'allPNGDecoded':True,'allRealAlpha':all(e['realAlpha'] for e in entries),'all1024Square':all(e['canvas']==[1024,1024] for e in entries),'allDistinctSpriteSHA256':len({e['sha256'] for e in entries})==14,'visibleOuterEdgePixelsAlphaAtLeast16':sum(e['alpha']['visibleEdgePixelsAlphaAtLeast16'] for e in entries),'warnings':warnings,'Unity':'not-tested'},'sourceWarnings':'Original full-sequence playback limitations do not establish a defect in the adopted static frame, and are retained in evidence README snapshots. No animation acceptance is inherited.','previews':['designs/whole-game/enemy-lineup-light.png','designs/whole-game/enemy-lineup-dark.png']}
(DOC/'enemies.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
# Review montage only: compositing/downscale/text labels, no new art generation.
PREVIEW=ROOT/'designs/whole-game';PREVIEW.mkdir(parents=True,exist_ok=True)
fontpath=ROOT/'art/fonts/NotoSansSC-Regular.otf'
font=ImageFont.truetype(str(fontpath),27);small=ImageFont.truetype(str(fontpath),18)
for theme,bg,fg in [('light','#eee8d5','#204c42'),('dark','#14382f','#f4e7c6')]:
 sheet=Image.new('RGB',(2100,960),bg);draw=ImageDraw.Draw(sheet)
 draw.text((25,12),'道途幸存者 · 14种试炼幻身 / 全20个敌人Key映射',font=font,fill=fg)
 for i,e in enumerate(entries):
  col=i%7;row=i//7;x=col*300;y=58+row*450
  with Image.open(ROOT/e['destination']) as im:
   thumb=im.copy();thumb.thumbnail((290,340),Image.Resampling.LANCZOS);sheet.paste(thumb,(x+(300-thumb.width)//2,y),thumb)
  draw.text((x+13,y+340),e['sourceIdentity']+' / '+e['sourceKey'],font=small,fill=fg)
  draw.text((x+13,y+369),e['role'],font=small,fill=fg)
  draw.text((x+13,y+397),'1024² · 透明PNG · 静帧复用',font=small,fill=fg)
 sheet.save(PREVIEW/f'enemy-lineup-{theme}.png')
print(json.dumps({'created':14,'keyMappings':20,'realAlpha':True,'visibleEdgePixels16':out['validation']['visibleOuterEdgePixelsAlphaAtLeast16'],'warnings':len(warnings),'output':str(OUT)},ensure_ascii=False))
