"""Read-only reference-source art audit. Only writes the local audit JSON."""
from pathlib import Path
import re,json,hashlib
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'.reference/survivors-roguelike-kit'
BASE='Assets/RGame/RoguelikeKit/'
guid={}
for p in (REF/'Assets').rglob('*.meta'):
    s=p.read_text(encoding='utf-8-sig',errors='replace')
    m=re.search(r'^guid: (\w+)',s,re.M)
    if m: guid[m[1]]=p.with_suffix('').relative_to(REF).as_posix()
def txt(path): return (REF/path).read_text(encoding='utf-8-sig',errors='replace')
def refs(path,field):
    return list(dict.fromkeys(guid.get(g,g) for g in re.findall(r'^\s*'+re.escape(field)+r': \{fileID: [^,}]+, guid: (\w+)',txt(path),re.M)))
def describe(path):
    s=txt(path)
    out={'source':path,'sha256':hashlib.sha256((REF/path).read_bytes()).hexdigest()}
    for field,key in [('m_Sprite','sprites'),('m_Script','scripts'),('m_Materials','materials')]:
        out[key]=refs(path,field)
    out['controllers']=refs(path,'m_Controller')
    out['magicKeys']=re.findall(r'^\s*_magicKey: (\S+)',s,re.M)
    out['sprites']=list(dict.fromkeys(out['sprites']))
    out['dropKeys']=re.findall(r'^\s*_dropKeys:\n((?:    - \w+\n)*)',s,re.M)
    out['dropKeys']=[x.strip() for b in out['dropKeys'] for x in b.split('-') if x.strip()]
    out['sourcePrefabs']=refs(path,'m_SourcePrefab')
    out['spriteOverrides']=[guid.get(g,g) for g in re.findall(r'propertyPath: m_Sprite\n\s+value:.*\n\s+objectReference: \{fileID: [^,]+, guid: (\w+)',s)]
    return out
pool=BASE+'ScriptableObjects/RuntimeDataSO/Pool/Pool.asset'
defs=re.findall(r'- _key: (\S+)\n\s+_pool:\n\s+_prefab: \{fileID: [^,]+, guid: (\w+)',txt(pool))
pool_map={k:guid[g] for k,g in defs}
stage=BASE+'ScriptableObjects/DataSO/Level/Stages/Stage1.asset'
stagefiles=[guid[g] for g in re.findall(r'guid: (\w+)',txt(stage)) if g in guid and '/StageSet/' in guid[g]]
stagekeys=[]
for p in stagefiles: stagekeys.extend(re.findall(r'PoolKey: (\w+)',txt(p)))
enemykeys=list(dict.fromkeys(stagekeys))
enemies=[]
for k in enemykeys:
    o=describe(pool_map[k]);o['key']=k;o['stageSpawnConfigs']=[p for p in stagefiles if f'PoolKey: {k}\n' in txt(p)];enemies.append(o)
players=[]
for k in ['Fighter','Assassin','Mage']:
    o=describe(BASE+f'Prefabs/Player/{k}.prefab');o['key']=k;o['animations']=[]
    for p in sorted((REF/(BASE+f'Art/Animation/{k}')).glob('*.anim')):
        s=p.read_text(encoding='utf-8-sig');o['animations'].append({'source':p.relative_to(REF).as_posix(),'name':p.stem,'sampleRate':float(re.search(r'm_SampleRate: (\S+)',s)[1]),'duration':float(re.search(r'm_StopTime: (\S+)',s)[1]),'loop':bool(int(re.search(r'm_LoopTime: (\S+)',s)[1])),'spriteCurveCount':s.count('attribute: m_Sprite'),'transformPathCount':len(set(re.findall(r'^\s+path: (.+)',s,re.M)))})
    players.append(o)
skills=[]
for p in sorted((REF/(BASE+'Prefabs/Skill')).glob('*.prefab')):
    o=describe(p.relative_to(REF).as_posix());o['key']=p.stem
    caster=BASE+f'Scripts/System/Skill/SkillCast/{p.stem}Cast.cs'
    s=txt(caster);mix=re.search(r'public override void MixSkill\(\)\s*\{(.*?)\n        \}',s,re.S)
    o['evolutionCode']=mix[1].strip() if mix else ('Mixed branch in Cast' if 'SkillCurrentState.Mixed' in s else 'Inherited base state only')
    o['castSource']=caster;o['sportSource']=BASE+f'Scripts/System/Skill/Skill/Sport/{p.stem}.cs'
    skills.append(o)
map1=BASE+'ScriptableObjects/DataSO/Level/Map/Map1.asset'
tiles=[{'source':guid[g],'weight':int(w)} for g,w in re.findall(r'sprite: \{fileID: [^,]+, guid: (\w+), type: 3\}\n\s+weight: (\d+)',txt(map1))]
for row in tiles:
    with Image.open(REF/row['source']) as im:row['size']=list(im.size)
lootkeys=['Exp40','Exp80','ReplyHP','Suck','Purse','Box']
loot=[dict(describe(pool_map[k]),key=k) for k in lootkeys]
magic=[dict(describe(pool_map[k]),key=k) for k in ['BlueMagic','PinkMagic','RedMagic','GreenMagic','SnowMagic']]
out={'reference':{'url':'https://github.com/Roo-Roo-Roo/survivors-roguelike-kit','commit':'3f905381d73a34b516030528b8ef6743868b9e52','localPath':str(REF)},'auditDate':'2026-10-28','auditStatus':'source audit complete; art production acceptance separate','counts':{'players':len(players),'playerAnimationClips':sum(len(p['animations']) for p in players),'activeEnemyPoolKeys':len(enemies),'baseEnemyIdentities':14,'eliteVariants':6,'actualDistinctEnemySpriteFiles':len(set(x for e in enemies for x in e['sprites'])),'stageSpawnConfigs':len(stagefiles),'skills':len(skills),'mapTileVariants':len(tiles),'breakablePropKinds':1,'propInstancesPerMap':20,'lootPoolKeys':len(loot),'enemyProjectileKinds':len(magic)},'players':players,'enemies':enemies,'skills':skills,'map':{'config':map1,'width':100,'height':100,'tiles':tiles,'prop':describe(BASE+'Prefabs/DropOut/Prop.prefab')},'loot':loot,'enemyProjectiles':magic,'allPoolMapping':pool_map,'sourceEvidence':{'playerAnimationLogic':BASE+'Scripts/Game/Player/Animator/PlayerAnim.cs','mapGeneration':BASE+'Scripts/System/Map/MapManager.cs','enemyBase':BASE+'Scripts/Game/Enemy/BaseEnemy.cs','enemyHit':BASE+'Scripts/Game/Enemy/Hit/EnemyHit.cs'}}
out['sourceAnomalies']=[{'id':'crow-ghost-sprite','fact':'Crow prefab actually references Ghost.png; Crow.png exists but is not the referenced Sprite.','requiredTreatment':'Give Crow a separate new crow identity only as a documented art redesign, never claim it is the original visible Sprite.'},{'id':'levels-share-map','fact':'FirstLevel and SecondLevel reference the same Map1 and Stage1.','requiredTreatment':'One world tile family covers both; new distinct map gameplay is outside current source scope.'},{'id':'unknown-unity-sprite-guid','fact':'Exp40/Exp80/Shadow use GUID a86470a33a6bf42c4b3595704624658b, unresolved by repository .meta scan.','requiredTreatment':'Replace with new pickup/shadow PNG and record it as new art. Do not claim original Sprite decoded.'}]
out['animationContract']={'players':{'requiredActions':['Idle','Run'],'sourceScheme':'PSB skeletal transform animation; 1 second, 30 samples/sec, loop; no m_Sprite curves.','directionScheme':'Horizontal transform.localScale mirror; no eight-direction requirement in source.','acceptedArtDeliverable':'Either validated layered rig art with Idle/Run motion spec, or real authored animated sprites with constant canvas, foot registration, frame timing and preview. A whole-character bob/squash export alone is not equivalent to articulated Run.','hitAndDeath':'Source white-flash and material alpha fade; no separate attack/hurt/death sprite clip is required by source.'},'enemies':{'sourceScheme':'Static SpriteRenderer, procedural movement plus vertex sine distortion, x mirror, hit flash, noise dissolve; no enemy Animator or .anim clip.','acceptedArtDeliverable':'14 identity PNG masters and mapping for all 20 keys, with source-compatible motion/hit/death state art guidance; elite marker/variant may share base master.','optionalBeyondSource':['walk/run strips','attack strips','dead-body frames']},'skills':{'sourceScheme':'Static transparent sprite/projectile transformed by casts/movement, no sprite Animator.','acceptedArtDeliverable':'9 distinct world FX textures plus 9 evolved-state assignments/previews. Evolution may reuse the same texture and change spawn count/speed/scale per source.'}}
out['minimumArtDeliveryMatrix']=[
 {'category':'UI screens and controls','sourceCount':'52 current designed states; full UIs in separate UI_COVERAGE.json','currentArt':'art/common/, art/icons/, designs/ui-suite/','gapAtAudit':'Requires final visual/source acceptance and export manifest, tracked separately.'},
 {'category':'Player identities','sourceCount':3,'currentArt':['art/characters/hero.png','art/characters/sword.png','art/characters/healer.png'],'gapAtAudit':'Static masters exist; need world-facing foot Pivot/size acceptance and all six Idle/Run motion deliveries.'},
 {'category':'Player motion','sourceCount':6,'currentArt':[],'gapAtAudit':'Three Idle and three Run; no authored motion package found in current art/.'},
 {'category':'Enemy identity masters','sourceCount':14,'currentArt':['art/characters/enemy-tiger.png','art/characters/enemy-lantern.png'],'gapAtAudit':'Two existing sample enemies have no confirmed complete mapping to the 14 actual identities; need a full source-key mapping.'},
 {'category':'Elite assignments','sourceCount':6,'currentArt':[],'gapAtAudit':'Base master reuse allowed; explicitly map six *1 keys and optional common elite marker. No invented extra six species required.'},
 {'category':'Map tiles','sourceCount':6,'currentArt':[],'gapAtAudit':'arena-v1 is a UI plate, not the six independent loopable gameplay tiles. Need same compatible outer edges, six source-weight mappings, tile seam preview.'},
 {'category':'Breakable prop','sourceCount':1,'currentArt':[],'gapAtAudit':'One independent prop, reused 20 times per generated map; optional impact/dissolve state art guidance.'},
 {'category':'World loot','sourceCount':6,'currentArt':['art/icons/exp.png','art/icons/healing.png','art/icons/moneybag.png','art/icons/treasure-closed.png'],'gapAtAudit':'Reuse is possible after world readability/size validation; Exp40 vs Exp80 need distinct value/appearance assignments; Suck attractor independent art missing.'},
 {'category':'World skill FX','sourceCount':9,'currentArt':'Nine skill-* UI icons exist','gapAtAudit':'UI icon crops do not establish world FX production. Need nine clear transparent attack/projectile textures and effect orientation/Pivot.'},
 {'category':'Evolved skill assignment','sourceCount':9,'currentArt':[],'gapAtAudit':'No extra texture is mandatory: source changes cast parameters. Deliver 9 parameter-faithful visual comparisons and mapped shared textures.'},
 {'category':'Enemy projectile FX','sourceCount':5,'currentArt':[],'gapAtAudit':'BlueMagic/PinkMagic/RedMagic/GreenMagic/SnowMagic must each have an unambiguous world texture assignment.'},
 {'category':'Enemy status FX','sourceCount':3,'currentArt':['art/icons/buff-burn.png','art/icons/buff-freeze.png','art/icons/buff-slow.png'],'gapAtAudit':'Icons complete, but world Burn tint/Freezing/Slow shared source ring needs readable art/state guidance. Shared ring allowed with different time/colour.'},
 {'category':'Common world material support','sourceCount':'1 shadow + 1 dissolve mask minimum','currentArt':[],'gapAtAudit':'Source uses projected/material shadows and dissolve noise. Supply compatible independent support PNG/mask or document complete reuse with legal source evidence; shaders/C# remain next phase.'},
 {'category':'Lobby and loading illustrations','sourceCount':2,'currentArt':['art/illustrations/lobby-v1.png','art/illustrations/arena-v1.png'],'gapAtAudit':'Illustrations exist; keep separate from loopable gameplay map claim.'}
]
out['notApplicable']=['Online login, account, server selection, character creation','MMORPG world/teleport/social/friends/chat/mail/guild/party','Traditional inventory, warehouse, equipment, crafting, mounts, pets','Quests, dailies, events, sign-in, ranks, gacha','Source-required eight-direction character art','Separate enemy attack/walk/death frame strips','Three unique gameplay maps','New sound or music production (outside this visual art audit)']
out['currentArtInspection']={'snapshotDate':'2026-10-28','artPngCount':len(list((ROOT/'art').rglob('*.png'))),'characterMotionPackageFound':False,'worldTilePackageFound':False,'fullEnemySourceMappingFound':False,'note':'This audit is a point-in-time gap audit, not final production acceptance. New production may resolve these gaps; do not overwrite this snapshot to imply the art existed at audit time.'}
imagefiles=sorted(set(x for section in ('players','enemies','skills','loot','enemyProjectiles') for row in out[section] for x in row['sprites'] if x.startswith('Assets/') and x.lower().endswith('.png')) | {t['source'] for t in out['map']['tiles']})
out['decodedReferencedImages']=[]
for s in imagefiles:
    with Image.open(REF/s) as im:
        im.load()
        out['decodedReferencedImages'].append({'source':s,'size':list(im.size),'format':im.format})
out['sourceEvidenceSha256']={s:hashlib.sha256((REF/s).read_bytes()).hexdigest() for s in out['sourceEvidence'].values()}
(ROOT/'docs/whole-game-art-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out['counts'],ensure_ascii=False));print('enemyKeys',enemykeys)
