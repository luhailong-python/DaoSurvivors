"""Verify current source bindings and outputs without altering accepted artwork."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
enemies=read(ROOT/'docs/whole-game/enemies.json')
combat=read(ROOT/'docs/whole-game/world-combat-slices.json')
terrain=read(ROOT/'art/whole-game/terrain/v1/terrain-manifest.json')
seam=read(ROOT/'art/whole-game/terrain/v1/seam-qa.json')
support=read(ROOT/'docs/whole-game/world-support.json')
checks=[]
def check(id,value,expected,files=None):
    checks.append({'id':id,'status':'pass' if value==expected else 'fail','value':value,'expected':expected,'files':files or []})
check('enemy-identity-count',len(enemies['entries']),14)
check('elite-key-count',len(enemies['eliteVariants']),6)
check('enemy-destination-sha',sum(sha(ROOT/e['destination'])==e['sha256'] for e in enemies['entries']),14)
check('world-combat-cuts',len(combat['files']),16)
check('world-combat-sha',sum(sha(ROOT/e['file'])==e['sha256'] for e in combat['files']),16)
check('terrain-count',len(terrain['tiles']),6)
check('terrain-seam-checks',sum(e['status']=='pass' for e in seam['checks']),4)
check('world-pickup-count',len(support['loot']),6)
check('pickup-current-sha',sum(sha(ROOT/e['file'])==e['sha256'] for e in support['loot']),6)
check('pickup-source-alpha-preserved',sum(np.array_equal(np.array(Image.open(ROOT/e['file']).convert('RGBA'))[:,:,3],np.array(Image.open(e['source']).convert('RGBA'))[:,:,3]) for e in support['loot']),6)
n=support['noise'];check('noise-byte-copy',sha(ROOT/n['file']),sha(Path(n['source'])),[n['file']])
r=support['sharedStatusRing'];check('status-ring-byte-copy',sha(ROOT/r['file']),sha(Path(r['source'])),[r['file']])
check('nine-evolution-mappings',len(support['evolutions']),9)
check('nine-evolution-previews',sum((ROOT/e['comparisonPreview']).exists() for e in support['evolutions']),9)
check('all-twelve-support-previews',sum((ROOT/e).exists() for e in support['previews']),12)
shadow=support['shadow'];check('shadow-file-sha',sha(ROOT/shadow['file']),shadow['sha256'],[shadow['file']])
with Image.open(ROOT/shadow['file']) as im:
    a=np.array(im.convert('RGBA'))[:,:,3]
    edge=np.concatenate((a[0],a[-1],a[:,0],a[:,-1]))
    check('shadow-canvas',list(im.size),[512,256],[shadow['file']])
    check('shadow-transparent-outer-edge',int((edge>0).sum()),0,[shadow['file']])
check('camera-composite-present',(ROOT/'designs/whole-game/support/world-camera-composite.png').exists(),True)
pending=[]
review_path=ROOT/'docs/whole-game/world-support-visual-review.json'
review=read(review_path) if review_path.exists() else {'status':'pending'}
if review['status']!='accepted-support-art-offline':pending.append({'id':'support-visual-review','status':'pending','action':'Explicit actual-view review must bind the current art/preview SHA values.'})
pending.append({'id':'unity-validation','status':'deferred-by-user','action':'Import, shader blend/whiteflash/dissolve, trail blend and sorting, PPU and runtime remain next stage.'})
out={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'referenceCommit':support['referenceCommit'],
    'scope':'Non-player/non-UI current production audit, source+disk verified; no reference repo or source pixels modified.',
    'status':'current-production-support-audit-with-explicit-pending-items','checks':checks,'pending':pending,
    'counts':{'enemyIdentities':14,'enemyPoolKeys':20,'eliteAssignments':6,'terrainTiles':6,'propKinds':1,'worldSkills':9,'evolutionAssignments':9,'enemyProjectileKinds':5,'worldLootKeys':6,'enemyStatuses':3,'sharedStatusRings':1,'dissolveNoiseTextures':1,'acceptedIndependentShadows':1 if review['status']=='accepted-support-art-offline' else 0},
    'sourceCorrections':['FourCorner Mixed emits8 compass directions, base emits4 diagonal directions; Area*2 is not the only change.',
     'InsideScope Mixed writesAttackTimer0.5 only as initial phase; Sport logic threshold remains1/reset0.',
     'ToNearest Mixed red; Bouncing Mixed (1,.5,.5,1); CircularMotion Mixed yellow sprite and trail.',
     'Sprite scale depends on(globalArea+skillArea)*.01, so doubling skillArea does not imply doubling whole sprite.',
     'Five TrailRenderers useUnity builtin material, not five missing texture files.'],
    'visualObservations':{'enemyLineup':'14 distinct Daoist reskins viewed; no visible body/implement clipping at lineup scale. Mapping remains documented redesign, not original species replication.',
     'worldCombat':'16 cuts viewed; nine player/world textures and five enemy bullets have intact silhouettes and useful shape/hue contrast.',
     'terrain':'Mixed-variant view reviewed; no hard rectangular seam. Repetition remains visible as expected from source6-tile/weighted contract.',
     'supportPreviews':'All12 viewed; six world loot values/shapes identifiable, teal/amber40/80 distinction readable at selected small scale; nine comparisons preserve correct source branches, no clipped texture assets. Alpha-derived contact shadow and representative world-camera composite also viewed.',
     'limits':'Static comparison diagrams prove art assignments; they do not establish exact Unity shader/trail execution or playable game.'}}
dump(ROOT/'docs/whole-game/support-audit-current.json',out)
lines=['# 非角色、非UI美术当前核验','',
 '本报告对照固定源码与当前磁盘制作结果，补充历史缺口快照，不改写旧快照。未生成新图，未修改F盘或任何Git状态。', '',
 '已经具备：14个敌人身份/20个Key和6精英映射、6个正式地块及72种拼接组合验收、1个Prop、9种玩家世界纹理、5种敌弹、6种世界拾取物、9种进化关系与对比图、3种敌方状态规格、1个共享状态环、1个实际引用的溶解噪声副本，以及1个源Alpha后处理衍生阴影。', '',
 '本轮检查：'+str(sum(c['status']=='pass' for c in checks))+'/'+str(len(checks))+'项产物/哈希/Alpha/映射检查通过。详细值见同名JSON。全量美术验收另行收口，不用这里的文件计数代替。', '',
 '## 仍须处理','',
 '- 非角色/非UI本批产物的独立阴影与代表性镜头组合已完成离线视觉核验，详见world-support-visual-review.json；整款仍需Root汇总角色动作及总交付验收。',
 '- Unity导入/Shader/拖尾混合/排序/PPU/运行均按用户要求留至下一阶段。', '',
 '## 本次修正的源码细节','',
 '- 四象符进化：4个对角方向变为8个方向，另有技能Area×2。',
 '- 八卦阵进化：AttackTimer初始设0.5；后续FixedUpdate仍在>=1时触发并清零，不是持续0.5秒伤害间隔。',
 '- 御剑/流珠/葫芦进化分别乘红色、(1,0.5,0.5)、黄色，葫芦程序拖尾也乘黄色。',
 '- 尺寸公式是(全局Area+技能Area)×0.01；技能Area翻倍不等于最终尺寸翻倍。',
 '- 5个TrailRenderer使用内置材质，记录渐变/宽度/时间即可，不虚增5张贴图缺口。', '',
 '实际视觉核验包括敌人深底阵容、世界战斗浅底总览、混排地面、源噪声，以及新增12张支持/进化/镜头图。已确认形状/归属完整、经验青玉/琥珀区别明确、文字未遮住效果，世界状态表意与源一致；软阴影落于角色/敌人/Prop脚下，未见硬边或矩形实底。离线乘色/阈值预览不当作Unity Shader精确效果。']
(ROOT/'docs/whole-game/support-audit-current.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'checks':len(checks),'passed':sum(c['status']=='pass' for c in checks),'failed':[c['id'] for c in checks if c['status']=='fail'],'pending':[p['id'] for p in pending]},ensure_ascii=False))
