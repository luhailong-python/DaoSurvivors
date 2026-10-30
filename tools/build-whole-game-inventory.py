"""Audit final art coverage against the pinned source scope and review evidence."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(s):return json.loads((ROOT/s).read_text(encoding='utf-8'))
def write(s,d):(ROOT/s).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def bound(s):return {'file':s,'sha256':sha(ROOT/s)}

def main():
    manifest=load('art/manifest.json');ui=load('docs/ui-suite/current-delivery-audit.json')
    players=load('docs/whole-game/player-actions-final-review.json')
    enemies=load('docs/whole-game/enemies.json');ev=load('docs/whole-game/enemies-visual-review.json')
    terrain=load('art/whole-game/terrain/v1/terrain-manifest.json');seams=load('art/whole-game/terrain/v1/seam-qa.json')
    fx=load('docs/whole-game/world-combat-slices.json');fv=load('docs/whole-game/world-combat-visual-review.json')
    sup=load('docs/whole-game/world-support.json');sv=load('docs/whole-game/world-support-visual-review.json')
    brand=load('docs/branding/BRAND.json');bv=load('docs/branding/visual-review.json')
    assert not manifest['warnings'],manifest['warnings']
    assert ui['status']=='accepted_ui_art_branded'
    assert load('docs/ui-suite/UI_COVERAGE.json')['workingTitle']=='一炁当千'
    assert brand['gameName']=='一炁当千' and brand['visualStatus']=='accepted_current_logo_and_emblem'
    assert bv['status']=='accepted' and len(brand['assets'])==8
    for e in brand['assets']:assert sha(ROOT/e['file'])==e['sha256'],e['file']
    assert players['status']=='accepted_player_art_only'
    assert len(enemies['entries'])==14 and len(enemies['eliteVariants'])==6
    assert len(ev['assets'])==14 and all(e['status']=='accepted' for e in ev['assets'])
    assert terrain['status']=='ground_art_accepted' and seams['status']=='ground_art_accepted_numeric_and_visual'
    assert len(terrain['tiles'])==6 and len(seams['pairs'])==72
    assert len(fx['files'])==16 and len(fv['assets'])==16
    assert sup['status']==sv['status']=='accepted-support-art-offline'
    assert len(sup['loot'])==6 and len(sup['evolutions'])==9 and len(sup['enemyWorldStatuses'])==3
    for e in manifest['assets']:assert sha(ROOT/e['file'])==e['sha256'],e['file']
    for e in players['files']+sv['files']:assert sha(ROOT/e['file'])==e['sha256'],e['file']
    for e in ev['assets']+fv['assets']:assert sha(ROOT/e['file'])==e['sha256'],e['file']
    for e in terrain['tiles']:assert sha(ROOT/e['file'])==e['sha256'],e['file']
    categories=[
      {'category':'Brand','required':'final game name and glyph-correct main logo, secondary emblem,8 formal sizes, allUI branding','delivered':8,'unit':'formal PNG exports','records':['docs/branding/BRAND.json','docs/branding/visual-review.json','docs/ui-suite/current-delivery-audit.json'],'status':'accepted'},
      {'category':'UI','required':'52 screens/states/flows + independent controls/icons/font/layout','delivered':52,'unit':'screens','records':['docs/ui-suite/UI_COVERAGE.json','docs/ui-suite/current-delivery-audit.json'],'status':'accepted'},
      {'category':'Players','required':'3 identities × Idle/Run, horizontal facing','delivered':6,'unit':'action families','records':['docs/whole-game/player-actions-final-review.json','docs/whole-game/final-review-independent.json'],'status':'accepted'},
      {'category':'Enemies','required':'14 identities mapped to20PoolKeys including6elites','delivered':20,'unit':'source keys','records':['docs/whole-game/enemies.json','docs/whole-game/enemies-visual-review.json'],'status':'accepted'},
      {'category':'Terrain','required':'6 interchangeable tiles for sharedMap1','delivered':6,'unit':'tiles;72adjacency pairs','records':['art/whole-game/terrain/v1/terrain-manifest.json','art/whole-game/terrain/v1/seam-qa.json'],'status':'accepted'},
      {'category':'Prop','required':'1 breakable prop visual','delivered':1,'unit':'sprite','records':['docs/whole-game/world-combat-slices.json'],'status':'accepted'},
      {'category':'World loot','required':'Exp40/Exp80/ReplyHP/Suck/Purse/Box','delivered':6,'unit':'keys','records':['docs/whole-game/world-support.json','docs/whole-game/world-support-visual-review.json'],'status':'accepted'},
      {'category':'Player world skills','required':'9 base textures +9 evolved renderer/cast relations','delivered':9,'unit':'base textures, each with evolved mapping','records':['docs/whole-game/world-combat-slices.json','docs/whole-game/world-support.json'],'status':'accepted'},
      {'category':'Enemy projectiles','required':'Blue/Pink/Red/Green/SnowMagic','delivered':5,'unit':'textures','records':['docs/whole-game/world-combat-visual-review.json'],'status':'accepted'},
      {'category':'World supports','required':'3status specs, sharedring, contactshadow, actualdissolve noise, whiteflash/deathfade specs','delivered':3,'unit':'status specs + support sprites/texture','records':['docs/whole-game/world-support.json','docs/whole-game/world-support-visual-review.json'],'status':'accepted'},
    ]
    reports=['docs/ui-suite/current-delivery-audit.json','docs/whole-game/player-actions-final-review.json',
        'docs/whole-game/final-review-independent.json','docs/whole-game/enemies-visual-review.json',
        'art/whole-game/terrain/v1/seam-qa.json','docs/whole-game/world-combat-visual-review.json',
        'docs/whole-game/world-support-visual-review.json','docs/whole-game/support-audit-current.json',
        'docs/branding/BRAND.json','docs/branding/visual-review.json','docs/branding/integration-review.json',
        'docs/whole-game/final-non-ui-recheck-20261029.json']
    inventory={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
        'project':'一炁当千','previousWorkingTitle':'道途幸存者','referenceCommit':'3f905381d73a34b516030528b8ef6743868b9e52',
        'scope':'complete art required by pinned survivors-roguelike-kit, no Unity implementation',
        'status':'complete_art_coverage_with_offline_visual_acceptance','missingRequiredArt':[],
        'categories':categories,'assetFileCount':len(manifest['assets']),
        'assetFileCountNote':'Includes runtime art, required source sheets/rig parts, licenses and production/review support.52UI screenshots/layouts are indexed separately.',
        'formalPlayerFrames':146,'playerStrips':10,'uiScreens':52,
        'brandFormalExports':8,'metricClarifications':{'playerMirrorPairs':64,'mirrorComparisonImages':128,'explanation':'Prior player report generatedWestExactMirrors=128 counted bothE/W images; actual mirror comparison is64pairs.'},
        'assetManifest':bound('art/manifest.json'),'hashBoundReviewRecords':[bound(s) for s in reports],
        'retainedFindings':['Original nominal-grid icon/FX sheet FAIL/WARN records retained; ownership crops replace the rejected equal-grid slicing method.',
            'Weak alpha specks/glow in inherited/source art retained as documented.',
            'Actual backend image model and quality are undisclosed; config targets are not claimed as actual results.'],
        'deferredByUser':['Unity import/Prefab/Animator/Shader/C# integration','runtime/platform/resolution/performance validation'],
        'gitSubmission':{'repository':manifest.get('deliveryGithub'),'authorization':'User explicitly authorized commit and push after final art verification. Actual result is recorded independently in Git and .local/release/receipt.json.'}}
    write('docs/whole-game/ART_COVERAGE.json',inventory)
    lines=['# 整款游戏美术覆盖与验收总账','',
        '2026-10-29。正式名《一炁当千》，已将新名字与Logo统一到52屏UI并合入整款交付。按固定源码范围完成本地美术制作及离线验收；没有进行Unity接入。历史缺口审计保留为当时快照，当前状态以本总账和哈希绑定验收为准。','',
        '|类别|当前覆盖|状态|','|---|---|---|']
    labels=[('品牌','正式名《一炁当千》，主Logo与葫芦徽记，共8正式尺寸，已统一UI'),('UI','52整屏/状态/流程及布局；15正式控件状态、图标、字体'),('角色','3人×Idle/Run；146正式E/W帧、10条带、12分层部件'),
        ('敌人','14身份、20PoolKey、6精英映射与共用光环'),('场景','6可混排正式地块、72种横纵接缝组合、1Prop'),
        ('掉落','6世界拾取key，经验40/80色彩和值各有映射'),('技能','9基本攻击纹理与9进化使用关系、对比预览'),
        ('敌弹与状态','5敌弹、3状态规格、共用状态环'),('支持图','软接触阴影、实际溶解噪声与许可、白闪/淡出规格')]
    lines += [f'|{a}|{b}|已完成离线美术验收|' for a,b in labels]
    lines+=['',f'资源清单有{len(manifest["assets"])}个文件，包含正式运行资源、生产来源、部件、检查支持和授权，并非全部为独立运行Sprite。来源记录缺口为0。52屏PNG和布局另列UI清单。','',
        '角色实际逐帧与循环、左右朝向和16→1环接已经查看；小道/灵修为原生生成部件的机械骨骼合成，剑修为身份匹配的既有动作字节复用。没有把整图晃动、程序绘画或视频说成本次动作原画。','',
        '镜像统计按64组E/W（涉及128张图）记数；旧角色报告的128字段是双向图片数，非128张W帧。此澄清不更改已验收像素。','',
        '原图集等格检测的失败/警告、原生弱Alpha散点和未披露的具体型号/质量仍保留。正式归属切片、关节覆盖、来源、规格与动作验收分别记录，不将原始检测改成通过。','',
        '后续事项为用户推迟的Unity接入与运行验证。成果仓库已核实，用户本轮已授权提交与Push，实际结果另以Git远端和本地发布回执确认。当前所需美术缺口：无。','',
        '机器总账：`ART_COVERAGE.json`；最终验收：`ACCEPTANCE.json`；导入建议：`UNITY_ART_IMPORT.md`。']
    (ROOT/'docs/whole-game/ART_COVERAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({'assetFiles':len(manifest['assets']),'categories':len(categories),'missingRequiredArt':[]}))
if __name__=='__main__':main()
