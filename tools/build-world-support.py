"""Reuse source pixels for world-support delivery; no raster artwork is drawn here.

Writes only this project's support assets, comparative contact sheets and records.
Tint/transform/threshold previews are offline compositing, never Unity screenshots.
"""
from pathlib import Path
from datetime import datetime, timezone
import colorsys, hashlib, json, math, re, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'.reference/survivors-roguelike-kit'
BASE='Assets/RGame/RoguelikeKit/'
OUT=ROOT/'art/whole-game/support'
REV=ROOT/'designs/whole-game/support'
DOC=ROOT/'docs/whole-game'
for p in (OUT,REV,DOC):p.mkdir(parents=True,exist_ok=True)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return p.read_text(encoding='utf-8-sig')
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(ROOT).as_posix()
def stats(p):
    with Image.open(p) as im:
        a=np.array(im.convert('RGBA'))[:,:,3]
        return {'canvas':list(im.size),'mode':im.mode,'alphaRange':[int(a.min()),int(a.max())],
                'zeroAlphaPixels':int((a==0).sum()),'sha256':sha(p)}
def derive(src,name,kind='byte-copy',process=None):
    dst=OUT/name
    if process:process(Image.open(src).convert('RGBA')).save(dst)
    else:shutil.copyfile(src,dst)
    row={'file':rel(dst),'source':str(src),'sourceSha256':sha(src),'operation':kind,
         'newGeneration':False,'newAIEdit':False,**stats(dst)}
    dump(dst.with_suffix(dst.suffix+'.derivation.json'),row)
    return row
def multiply(im,color):
    a=np.array(im.convert('RGBA')).astype(np.float32)
    a[:,:,:3]*=np.array(color[:3])[None,None,:]
    if len(color)>3:a[:,:,3]*=color[3]
    return Image.fromarray(np.round(a).clip(0,255).astype('uint8'))
def amber(im):
    a=np.array(im);rgb=a[:,:,:3].astype(np.float32)/255
    mx=rgb.max(2);mn=rgb.min(2);sat=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-8),0)
    # One consistent warm hue while keeping source value/saturation and every Alpha byte.
    sat=sat*.90
    flat=[colorsys.hsv_to_rgb(30/360,float(s),float(v)) for s,v in zip(sat.flat,mx.flat)]
    a[:,:,:3]=np.round(np.array(flat).reshape(rgb.shape)*255).astype('uint8')
    return Image.fromarray(a)

font=ROOT/'art/fonts/NotoSansSC-Regular.otf'
def f(n):return ImageFont.truetype(str(font),n)
INK='#173e35';MUTED='#567268'
def fit(im,w,h):
    im=im.copy();im.thumbnail((w,h),Image.Resampling.LANCZOS);return im
def paste(canvas,im,cx,cy,w,h,angle=0,tint=None):
    if tint:im=multiply(im,tint)
    im=fit(im,w,h)
    if angle:im=im.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    canvas.alpha_composite(im,(round(cx-im.width/2),round(cy-im.height/2)))
def sprite(path):
    im=Image.open(ROOT/path).convert('RGBA')
    return im.crop(im.getbbox())
def panel(title,w=1440,h=660):
    im=Image.new('RGBA',(w,h),'#f5f0dd');d=ImageDraw.Draw(im)
    d.text((28,16),title,font=f(28),fill=INK)
    return im,d

loot=[]
rows=[('Exp40','exp-40.png','art/icons/exp.png','青玉经验晶','经验40，按Growth乘算',40,24),
      ('Exp80','exp-80.png','art/icons/exp.png','琥珀经验晶','经验80，按Growth乘算',80,28),
      ('ReplyHP','pickup-heal.png','art/icons/healing.png','灵果汤','回复20HP',20,34),
      ('Suck','pickup-suck.png','art/whole-game/fx/pickup-suck.png','吸灵玉环','全场经验吸取',None,40),
      ('Purse','pickup-purse.png','art/icons/moneybag.png','灵石钱袋','当前金币+50',50,34),
      ('Box','pickup-box.png','art/icons/treasure-closed.png','试炼宝箱','进入宝箱奖励流程',None,48)]
audit=json.loads(read(ROOT/'docs/whole-game-art-audit.json'))
for key,name,source,label,effect,value,height in rows:
    row=derive(ROOT/source,name,'HSV hue recolour to amber; original Alpha/value preserved' if key=='Exp80' else 'byte-copy',amber if key=='Exp80' else None)
    row.update({'key':key,'label':label,'effect':effect,'baseValue':value,'suggestedVisibleHeight1080':height,
        'pivotBottomLeft':[.5,.5],'spriteMode':'Single','filterMode':'Bilinear','wrapMode':'Clamp',
        'sourceGamePrefab':next(r['source'] for r in audit['loot'] if r['key']==key),
        'tintForNewArt':[1,1,1,1],'sourcePrefabTint':{'Exp40':[0,.82521486,1,1],'Exp80':[1,.33965534,0,1]}.get(key,[1,1,1,1]),
        'tintNote':'Source blue/orange meaning preserved with a teal/amber art redesign; do not reapply source tint to already coloured PNG.' if key.startswith('Exp') else 'New art already coloured; source behaviour remains unchanged.'})
    loot.append(row)

noise=derive(REF/(BASE+'Art/Teture/dissolveTex.png'),'dissolve-noise.png')
noise.update({'usage':'Enemy/Prop _NoiseTex','colourSpace':'Linear (sRGB off)','textureType':'Default','wrapMode':'Repeat','filterMode':'Bilinear','mipmaps':False,'channel':'red/greyscale; source RGB equal',
              'sourceMaterialGuid':'6e75b6128bb492846857bf4a52a2d076','licenseFile':'art/whole-game/support/SOURCE_GAME_MIT_LICENSE.txt'})
shutil.copyfile(REF/'LICENSE',OUT/'SOURCE_GAME_MIT_LICENSE.txt')
ring=derive(ROOT/'art/whole-game/fx/skill-scope.png','status-ring.png')
ring.update({'usage':'shared SlowBuff/FreezingBuff world ring; documented Daoist reskin','pivotBottomLeft':[.5,.5],
             'sourceGamePrefab':BASE+'Prefabs/Buff/SlowBuff.prefab','tint':[1,1,1,1],
             'sourceMatch':'Source both requests SlowBuff and positions at owner+Vector3.down*0.5; proposed new ring retains shared identity.'})

def contact_shadow(im):
    a=im.getchannel('A');box=a.getbbox();a=a.crop(box)
    a=a.resize((256,64),Image.Resampling.LANCZOS)
    canvas=Image.new('L',(512,256),0);canvas.paste(a,(128,96))
    canvas=canvas.filter(ImageFilter.GaussianBlur(10))
    out=Image.new('RGBA',canvas.size,(0,0,0,0));out.putalpha(canvas)
    return out
shadow=derive(ROOT/'art/whole-game/enemies/Slime.png','contact-shadow.png',
              'approved Slime Alpha bbox -> resize256x64 -> centre512x256 -> GaussianBlur10; RGB black; no painted pixels or generation',contact_shadow)
shadow.update({'status':'produced-awaiting-visual-review','usage':'contact shadow; new-game derived mask replacing unresolved source GUID a86470a33a6bf42c4b3595704624658b',
 'sourceAlphaOnly':True,'pivotBottomLeft':[.5,.5],'recommendedRendererColour':[1,1,1,.35],
 'suggestedVisibleWidth1080':{'player':95,'ordinaryEnemy':80,'boss':130,'prop':65},
 'filterMode':'Bilinear','wrapMode':'Clamp','colourSpace':'sRGB','spriteMode':'Single','mipmaps':False,
 'note':'Source GUID was not decoded; this is a documented mask derivative, not a copied source shadow and not a new original painting.'})

names={'ToNearestSkill':('追星御剑','nearest'),'BothSideSkill':('两仪斩','bothside'),'BouncingSkill':('流珠引','bouncing'),
       'ChainSkill':('连星诀','chain'),'CircularAttackSkill':('太极震','circle'),'CircularMotionSkill':('葫芦巡天','orbit'),
       'FourCornerSkill':('四象符','fourcorner'),'InsideScopeSkill':('八卦阵','scope'),'RandomSkill':('落花令','random')}
descriptions={
 'ToNearestSkill':'CD设为0.15秒；Damage设为5；弹体乘红色。',
 'BothSideSkill':'CD×0.3；技能Area×2；仍然左右各投射一次。',
 'BouncingSkill':'Velocity×1.5；Amount+3；弹体乘(1,0.5,0.5)。',
 'ChainSkill':'CD×0.3；仍用同一寻敌连锁纹理。',
 'CircularAttackSkill':'改为16方向、间隔22.5°；额外尺寸×2。',
 'CircularMotionSkill':'Velocity+1；Amount+3；弹体及程序拖尾乘黄色。',
 'FourCornerSkill':'四对角方向变为八方向；技能Area×2。',
 'InsideScopeSkill':'技能Area×2；生成时AttackTimer设0.5，后续仍按阈值1触发。',
 'RandomSkill':'CD×0.3；目标印记保持0.5秒淡出。'}
skills=[]
for key,(cn,short) in names.items():
    data=BASE+f'ScriptableObjects/DataSO/Skill/AttackSkill/{key}.asset'
    s=read(REF/data);fields={k:float(re.search(r'^  '+k+r': ([\d.]+)',s,re.M)[1]) for k in ['Velocity','Duration','CD','Damage','Amount','Area']}
    mods=re.findall(r'skillAttributeType: (\d+)\n\s+IntValue: (-?\d+)',s)
    for typ,v in mods:
        v=int(v);typ=int(typ)
        if typ==0:fields['Damage']+=v
        elif typ==1:fields['CD']*=1-v/100
        elif typ==2:fields['Amount']+=v
        elif typ==3:fields['Velocity']*=1+v/100
        elif typ==4:fields['Area']+=v
    mixed=dict(fields);tint=None
    if key=='ToNearestSkill':mixed.update(CD=.15,Damage=5);tint=[1,0,0,1]
    elif key=='BothSideSkill':mixed['CD']*=.3;mixed['Area']*=2
    elif key=='BouncingSkill':mixed['Velocity']*=1.5;mixed['Amount']+=3;tint=[1,.5,.5,1]
    elif key in ('ChainSkill','RandomSkill'):mixed['CD']*=.3
    elif key=='CircularMotionSkill':mixed['Velocity']+=1;mixed['Amount']+=3;tint=[1,1,0,1]
    elif key in ('FourCornerSkill','InsideScopeSkill'):mixed['Area']*=2
    caster=BASE+f'Scripts/System/Skill/SkillCast/{key}Cast.cs'
    prefab=BASE+f'Prefabs/Skill/{key}.prefab'
    ps=read(REF/prefab);trail=None
    if 'TrailRenderer:' in ps:
        tr=ps.split('TrailRenderer:',1)[1]
        trail={'source':'Unity built-in TrailRenderer geometry; no additional artwork texture',
            'durationSeconds':float(re.search(r'  m_Time: ([\d.]+)',tr)[1]),
            'material':'Unity builtin, fileID10308, GUID0000000000000000f000000000000000',
            'gradientKeys':re.findall(r'key[01]: \{([^}]+)\}',tr),
            'evolvedTint':[1,1,0,1] if key=='CircularMotionSkill' else None,
            'nextPhase':'Use source widthCurve/colourGradient and existing builtin material; actual trail sorting/blend remains Unity validation.'}
    r={'key':key,'name':cn,'texture':f'art/whole-game/fx/skill-{short}.png','sameTextureAfterEvolution':True,
       'maxLevelBeforeMix':len(mods)+1,'beforeMixedAtMaxLevel':fields,'afterMixedAtMaxLevel':mixed,
       'MixAttributeSkillKey':re.search(r'MixAttributeSkillKey: (\w+)',s)[1],
       'sourceData':data,'sourceDataSha256':sha(REF/data),'sourceCast':caster,'sourceCastSha256':sha(REF/caster),
       'sourcePrefab':prefab,'description':descriptions[key],'evolvedSpriteMultiply':tint,'trail':trail,
       'previewNormalization':{'globalArea':100,'globalAmount':0,'globalSkillSpeed':100,'scope':'Comparison isolates skill evolution; not an integrated player build or game screenshot.'}}
    r['beforeRendererScaleFactor']=(100+fields['Area'])/100
    r['afterRendererScaleFactor']=(100+mixed['Area'])/100*(2 if key=='CircularAttackSkill' else 1)
    if key=='FourCornerSkill':r.update(beforeCastAngles=[45,135,225,315],afterCastAngles=list(range(0,360,45)))
    if key=='CircularAttackSkill':r.update(beforeAngleStepDegrees=45,afterCastCount=16,afterAngleStepDegrees=22.5)
    if key=='InsideScopeSkill':r['timerSemantics']='Mixed Cast writes AttackTimer=0.5. FixedUpdate tests >=1 and resets to0, so do not describe a sustained0.5s interval.'
    skills.append(r)

def pose_effect(c,key,mixed,cx,cy,width,height,progress=.5):
    r=next(x for x in skills if x['key']==key);p=r['afterMixedAtMaxLevel' if mixed else 'beforeMixedAtMaxLevel'];im=sprite(r['texture'])
    ti=r['evolvedSpriteMultiply'] if mixed else None
    ratio=r['afterRendererScaleFactor']/r['beforeRendererScaleFactor'] if mixed else 1
    if key in ('CircularAttackSkill','FourCornerSkill'):
        n=(16 if mixed else int(p['Amount'])) if key=='CircularAttackSkill' else (8 if mixed else 4)
        n=max(1,min(16,n));rad=min(width,height)*.34
        for i in range(n):
            a=(i*360/n if key=='FourCornerSkill' or mixed else i*45)+(45 if key=='FourCornerSkill' and not mixed else 0)
            ang=math.radians(a)
            paste(c,im,cx+rad*math.cos(ang),cy-rad*math.sin(ang),min(78*ratio,130),min(78*ratio,130),a,ti)
    elif key=='CircularMotionSkill':
        n=int(p['Amount']);rad=min(width,height)*.32
        for i in range(n):
            a=math.radians(i*360/n);paste(c,im,cx+rad*math.cos(a),cy-rad*math.sin(a),66,66,tint=ti)
    elif key=='InsideScopeSkill':paste(c,im,cx,cy,220*ratio,220*ratio,tint=ti)
    elif key=='BothSideSkill':
        for sign in (-1,1):paste(c,im,cx+sign*145,cy,130*ratio,130*ratio,180 if sign<0 else 0,ti)
    elif key=='BouncingSkill':
        n=int(p['Amount']);
        for i in range(n):paste(c,im,cx+(i-(n-1)/2)*90,cy+35*(i%2),80,80,tint=ti)
    elif key=='RandomSkill':
        for i in range(int(p['Amount'])):paste(c,im,cx+(i-(p['Amount']-1)/2)*100,cy,100,100,tint=ti)
    else:
        # CD changes are indicated by true numeric labels, not invented simultaneous volleys.
        paste(c,im,cx,cy,270,165,tint=ti)

previews=[]
for r in skills:
    key=r['key'];im,d=panel(r['name']+' · 基础满级 / 进化对照')
    d.text((48,72),'满级、进化前',font=f(22),fill=INK);d.text((764,72),'进化后 · 复用同一纹理',font=f(22),fill=INK)
    pose_effect(im,key,False,360,290,640,320);pose_effect(im,key,True,1080,290,640,320)
    for i,mixed in enumerate((False,True)):
        v=r['afterMixedAtMaxLevel' if mixed else 'beforeMixedAtMaxLevel'];x=40+i*720
        text=f"CD {v['CD']:.3f}s  |  Velocity {v['Velocity']:.2f}  |  Amount {v['Amount']:.0f}"
        d.text((x,463),text,font=f(19),fill=INK)
        d.text((x,495),f"技能Area {v['Area']:.0f}  |  归一化尺寸系数 {r['afterRendererScaleFactor' if mixed else 'beforeRendererScaleFactor']:.2f}",font=f(18),fill=MUTED)
    # Split long semantic notes rather than squeeze fixed-size glyphs.
    desc=r['description'];pieces=[desc[i:i+45] for i in range(0,len(desc),45)]
    for j,line in enumerate(pieces):d.text((28,550+j*27),line,font=f(20),fill=INK)
    d.text((28,625),'已有像素的缩放/旋转/材质乘色示意；无新绘；非Unity运行截图；忽略碰撞与玩家全局加成。',font=f(16),fill=MUTED)
    path=REV/f'evolution-{key}.png';im.convert('RGB').save(path);r['comparisonPreview']=rel(path);previews.append(rel(path))

im,d=panel('6种世界掉落 · 正式图与1080p建议显示尺度',1800,700)
for i,r in enumerate(loot):
    x=150+300*i;asset=sprite(r['file']);paste(im,asset,x,220,230,230)
    paste(im,asset,x,440,240,r['suggestedVisibleHeight1080'])
    d.text((x-130,500),r['key']+' / '+r['label'],font=f(18),fill=INK)
    d.text((x-130,535),r['effect'],font=f(16),fill=MUTED)
    d.text((x-130,565),str(r['suggestedVisibleHeight1080'])+'px 可见高度',font=f(17),fill=MUTED)
d.text((25,650),'经验40/80复用形状、青玉/琥珀区分；80为机械HSV改色。所有正式PNG保留透明Alpha。',font=f(19),fill=INK)
path=REV/'world-pickups-scale.png';im.convert('RGB').save(path);previews.append(rel(path))

enemy=sprite('art/whole-game/enemies/EyeBall.png');sr=sprite(ring['file'])
im,d=panel('世界状态 · 既有敌人及共享环的材质表现示意',1800,800)
for i,(label,ti,hasring) in enumerate([('普通',None,False),('灼烧',[1,.35,.25,1],False),('冰冻',None,True),('减速',None,True),('受击白闪',None,False)]):
    x=180+360*i
    if hasring:paste(im,sr,x,295,250,110)
    use=enemy
    if label=='受击白闪':
        a=np.array(enemy);a[:,:,:3]=255;use=Image.fromarray(a)
    paste(im,use,x,210,240,260,tint=ti)
    d.text((x-100,380),label,font=f(24),fill=INK)
    note={'普通':'正常速度 / 材质时间','灼烧':'3.1秒；每秒3点伤害','冰冻':'2秒；速度和材质时间归零','减速':'3秒；速度减50%','受击白闪':'约0.1秒进入+0.1秒恢复'}[label]
    d.text((x-160,425),note,font=f(17),fill=MUTED)
noiseim=Image.open(OUT/'dissolve-noise.png').convert('L').resize(enemy.size)
na=np.array(noiseim)/255
for i,threshold in enumerate([0,.25,.5,.75,1]):
    a=np.array(enemy);a[:,:,3]=np.where(na>=threshold,a[:,:,3],0) if threshold<1 else 0
    paste(im,Image.fromarray(a),180+360*i,590,190,200)
    d.text((70+360*i,710),f'溶解阈值 {threshold:.2f}',font=f(20),fill=INK)
d.text((25,760),'灰度阈值遮罩、白闪和乘色仅是离线合成预览；非Shader精确复现。阴影见镜头组合图。',font=f(19),fill=INK)
path=REV/'world-status-dissolve.png';im.convert('RGB').save(path);previews.append(rel(path))

# Source-sized camera assembly uses existing tile pixels and accepted sprites only.
# Ground tile world height17 maps to1080px; output rounded64px tiles is an art preview.
import random
rng=random.Random(20261028)
scene=Image.new('RGBA',(1920,1080))
tiles=[Image.open(ROOT/f'art/whole-game/terrain/v1/ground-{i:02d}.png').convert('RGBA').resize((64,64),Image.Resampling.LANCZOS) for i in range(1,7)]
for y in range(17):
    for x in range(30):scene.alpha_composite(tiles[rng.choices(range(6),weights=[200,3,3,1,1,3])[0]],(x*64,y*64))
shadowim=sprite(shadow['file'])
def placed(path,x,ground,height,shadowwidth,ringbehind=False):
    if ringbehind:paste(scene,sprite(ring['file']),x,ground,150,60)
    paste(scene,multiply(shadowim,[1,1,1,.35]),x,ground+2,shadowwidth,shadowwidth*.30)
    sp=Image.open(ROOT/path).convert('RGBA')
    visible=sp.getchannel('A').point(lambda v:255 if v>=16 else 0).getbbox()
    scale=height/(visible[3]-visible[1])
    sp=sp.resize((round(sp.width*scale),round(sp.height*scale)),Image.Resampling.LANCZOS)
    scene.alpha_composite(sp,(round(x-(visible[0]+visible[2])/2*scale),round(ground-visible[3]*scale)))
placed('art/characters/hero.png',960,590,145,95)
placed('art/whole-game/enemies/Slime.png',610,440,110,80)
placed('art/whole-game/enemies/EyeBall.png',1250,470,110,80,True)
placed('art/whole-game/enemies/Bat.png',720,765,110,80)
placed('art/whole-game/enemies/Ghost.png',1280,770,110,80)
placed('art/whole-game/enemies/Fairy.png',1550,330,170,130)
placed('art/whole-game/fx/prop-urn.png',385,750,90,65)
for i,r in enumerate(loot):paste(scene,sprite(r['file']),650+i*125,955,120,r['suggestedVisibleHeight1080'])
paste(scene,sprite('art/whole-game/fx/skill-nearest.png'),1100,545,130,70)
paste(scene,sprite('art/whole-game/fx/enemy-blue.png'),830,435,55,55)
sd=ImageDraw.Draw(scene);sd.text((35,25),'美术摆放预览 · 参考镜头尺度约63.53px/格',font=f(29),fill=INK)
sd.text((35,70),'已确认地块/静态角色/敌人/破坏物/六掉落/状态环/Alpha衍生阴影；非Unity运行截图。',font=f(21),fill=INK)
for i,r in enumerate(loot):sd.text((620+i*125,1000),r['key'],font=f(17),fill=INK)
path=REV/'world-camera-composite.png';scene.convert('RGB').save(path);previews.append(rel(path))

statuses=[{'key':'Burn','source':BASE+'Scripts/System/Buff/BurnBuff.cs','durationSeconds':3.1,'tickSeconds':1,'damagePerTick':3,'rendererProperty':'_FlameRedBlend','sourceValue':'Color.red','ring':None,'artPreviewTintApproximation':[1,.35,.25,1]},
 {'key':'Freezing','source':BASE+'Scripts/System/Buff/FreezingBuff.cs','durationSeconds':2,'speed':'zero','shaderTimeSpeed':0,'ring':ring['file'],'ringTint':[1,1,1,1],'ringOwnerOffsetWorld':[0,-.5,0]},
 {'key':'Slow','source':BASE+'Scripts/System/Buff/SlowBuff.cs','durationSeconds':3,'speedReductionPercent':50,'shaderTimeSpeed':'original*0.5','ring':ring['file'],'ringTint':[1,1,1,1],'ringOwnerOffsetWorld':[0,-.5,0]}]

evidence=[BASE+'Scripts/System/Skill/SkillManager.cs',BASE+'Scripts/SOData/Skill/Enum/UpgradeSkillAttributeType.cs',BASE+'Art/Matrials/Prop.mat',BASE+'Art/Matrials/Enemy/WoodMonster.mat',BASE+'Scripts/System/Skill/Skill/Sport/InsideScopeSkill.cs',BASE+'Scripts/Game/DropOut/Exp/Exp.cs',BASE+'Scripts/Game/DropOut/Reply/ReplyHp.cs',BASE+'Scripts/Game/DropOut/Purse/Purse.cs']
evidence += [BASE+f'ScriptableObjects/DataSO/Buff/{n}Buff.asset' for n in ('Burn','Freezing','Slow')]
out={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'support-produced-visual-review-pending',
 'referenceCommit':audit['reference']['commit'],'artGenerationCount':0,'aiEditCount':0,'operations':'byte copies; one HSV recolour; preview-only resize/rotate/multiply/alpha threshold and typography',
 'loot':loot,'noise':noise,'sharedStatusRing':ring,'shadow':shadow,
 'evolutions':skills,'enemyWorldStatuses':statuses,'previews':previews,'sourceEvidence':[{'file':p,'sha256':sha(REF/p)} for p in evidence],
 'visualReview':{'status':'pending','note':'Do not infer visual acceptance from this script completing.'},'unityValidation':'not-run; import, shader, scale, trail blend, collision and exact runtime remain next phase'}
dump(DOC/'world-support.json',out)
lines=['# 世界拾取物、进化与通用支持图','',
 '本批仅复用已确认图片与源码贴图；没有生图或AI修图。6种世界掉落已独立提供，经验80使用源经验晶机械HSV琥珀改色，其余为字节复制。透明度不变。逐图来源、SHA、尺寸、显示高度、源值/颜色语义见 `world-support.json` 及每图 `.derivation.json`。','',
 '溶解噪声是功能参考提交中实际 `_NoiseTex` 的 `Art/Teture/dissolveTex.png` 原字节副本；原MIT许可保存在 `art/whole-game/support/SOURCE_GAME_MIT_LICENSE.txt`。建议作为Linear数据贴图导入。没有将 `dissolveRamp` 或未使用贴图虚增为必需美术。','',
 '冰冻和减速共用 `status-ring.png`，取本项目已生成八卦环原样复制，属于有记录的道家外观替换。灼烧由材质红色实现，无须新增火焰序列；冰冻2秒停速/停材质时间，减速3秒降速50%，两者共用同一个脚下环。效果叠层由下一阶段实现。','',
 '独立接触阴影 `contact-shadow.png` 来自已确认葫团团/Slime的Alpha：取非零BBox、压成256×64，置于512×256透明画布，再GaussianBlur10软化，RGB为黑色；不绘制新轮廓、不生图。Pivot中心，建议SpriteRenderer白色乘Alpha0.35；玩家/普通敌人/Boss/Prop可见宽度分别95/80/130/65px。它替换未能解码的原Shadow GUID，不冒称已找到原贴图。本文件和脚本没有把全套美术标为通过。','',
 '## 九种进化的真实关系','',
 '|Key|进化变化|比较图|','|---|---|---|']
for r in skills:lines.append(f"|{r['key']}|{r['description']}|`{r['comparisonPreview']}`|")
lines += ['', '对比使用源技能满级（逐条应用UpgradeAttribute）前后数据、归一化全局Area100/Amount0/SkillSpeed100；用同一纹理缩放、旋转和乘色，CD变化只通过数值说明，未捏造同时发射更多弹体。真实尺寸为 `(全局Area+技能Area)×0.01`；技能Area翻倍并非总尺寸翻倍。太极震进化另外乘2。四象符有四角到八向变化。八卦阵的AttackTimer设0.5只调整生成后的计时起点，不能声称其后持续每0.5秒攻击。', '',
 '五种技能的TrailRenderer使用Unity内置材质，无额外外部拖尾贴图缺口；准确源持续时间/渐变Key保存在JSON，环绕法器进化时身体和拖尾均乘黄色。最终宽度、混合、排序及采样须Unity阶段复核。', '',
 '## 预览与验收状态','',
 '`designs/whole-game/support/world-pickups-scale.png`检查6种拾取物及小尺寸；`world-status-dissolve.png`显示三个状态、白闪和五阶段噪声阈值；`world-camera-composite.png`为1920×1080已有地块、角色、敌人、Prop、六拾取物、共享环与衍生阴影的代表性镜头摆放。预览是已有美术的离线合成，非新原画、非Unity截图，状态颜色为离线近似。', '',
 '本脚本只记录产出与技术检查，实际视觉检查单独补记。Unity导入和运行未执行。']
(DOC/'world-support.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'loot':len(loot),'evolutions':len(skills),'previews':len(previews),'noiseCopyVerified':sha(OUT/'dissolve-noise.png')==sha(REF/(BASE+'Art/Teture/dissolveTex.png')),'shadow':'alpha-derived-mask'},ensure_ascii=False))
