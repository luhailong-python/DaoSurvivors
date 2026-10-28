"""Build the art-production checklist from the inspected, pinned reference. No game code."""
import json
import re
import struct
from pathlib import Path

root=Path(__file__).resolve().parents[1]
ref=root/'.reference/survivors-roguelike-kit'
prefix='Assets/RGame/RoguelikeKit/'
ui=prefix+'Scripts/UI/'
perk_source=prefix+'Prefabs/UI/MainMenu/PowerUp_Panel.prefab'
text=(ref/perk_source).read_text(encoding='utf-8-sig')
labels={
 'Might':('剑意','每阶伤害 +5%'), 'Armor':('护体','每阶承伤降低 10%'),
 'HPMax':('养元','每阶气血上限 +10%'), 'Recovery':('回春','每阶每秒回复 1 气血'),
 'Cooldown':('凝神','每阶施法间隔 -10%'), 'Area':('法域','每阶法术范围 +10%'),
 'SkillSpeed':('疾符','每阶投射速度 +10%'), 'Duration':('绵长','每阶法术持续 +15%'),
 'Amount':('分光','额外发射 1 枚投射物'), 'MoveSpeed':('御风','每阶移速 +10%'),
 'Magnet':('聚灵','每阶拾取范围 +25%'), 'Growth':('悟性','每阶经验收益 +10%'),
 'Greed':('纳财','每阶金币收益 +10%'), 'Curse':('劫缘','每阶妖灵速度、气血、数量与频率 +10%')}
perks=[]
for key,(name,desc) in labels.items():
    m=re.search(r'  mAttributeName: '+key+r'\n(?P<body>.*?)(?=\n---|\Z)',text,re.S)
    block=m.group('body')
    n=int(re.search(r'mMaxLevel: (\d+)',block)[1])
    gold=re.search(r'mRequireGold: ([0-9a-f]+)',block)[1]
    costs=list(struct.unpack('<'+'i'*(len(gold)//8),bytes.fromhex(gold)))
    perks.append({'key':key,'name':name,'description':desc,'maxLevel':n,'costs':costs,
      'icon':f'art/icons/attr-{key.lower()}.png','evidence':perk_source,'evidenceLine':text[:m.start()].count('\n')+1,
      'numericPolicy':'Costs and caps are reference demo config, not a proposed live balance table.'})
skills=[
 ('ToNearestSkill','追星御剑','自动锁定近处妖灵','Cooldown','skill-nearest'),
 ('BothSideSkill','两仪斩','向两侧释放法刃','Armor','skill-bothside'),
 ('BouncingSkill','流珠引','灵珠弹跳攻击','HPMax','skill-bouncing'),
 ('ChainSkill','连星诀','法力在妖灵之间连锁','MoveSpeed','skill-chain'),
 ('CircularAttackSkill','太极震','围绕自身释放范围法术','Area','skill-circle'),
 ('CircularMotionSkill','葫芦巡天','法器环绕自身运转','Duration','skill-orbit'),
 ('FourCornerSkill','四象符','向四角释放投射物','Might','skill-fourcorner'),
 ('InsideScopeSkill','八卦阵','在区域内生成法术攻击','SkillSpeed','skill-scope'),
 ('RandomSkill','落花令','随机方向释放投射物','Amount','skill-random')]
skill_data=[{'key':k,'name':n,'description':d,'evolutionRequires':p,'icon':'art/icons/'+i+'.png',
  'evolvedDisplayName':n+' · 化境','nameSource':'本次道家化临时中文名，源资产Description为空',
  'maxReferenceLevel':11,'source':prefix+'ScriptableObjects/DataSO/Skill/AttackSkill/'+k+'.asset'} for k,n,d,p,i in skills]
rows=[]
def add(id,system,name,state,kind,basis,evidence,variant='',notes=''):
    rows.append({'id':id,'system':system,'interface':name,'state':state,'kind':kind,'variant':variant or state,
      'basis':basis,'referenceEvidence':evidence,'assumptionOrNote':notes,
      'screenPath':f'designs/ui-suite/screens/{id}.png','layoutPath':f'designs/ui-suite/layouts/{id}.json',
      'independentAssets':[], 'productionStatus':'planned','acceptanceStatus':'pending','unityStatus':'待下一阶段接入验证'})
add('01-startup','启动与加载','启动画面','初次进入','startup','supporting_state',[prefix+'Scenes/Initialization.unity'],'start','启动标识为基础美术补齐；没有制作在线登录。')
add('02-loading','启动与加载','进入秘境','加载中','loading','existing',[ui+'LoadingInterfaceController.cs'],'loading','源无百分比进度契约，使用不定进度提示。')
add('03-loading-error','启动与加载','加载异常','读取失败','message','suggested',[ui+'LoadingInterfaceController.cs'],'load-error','本地资源异常的可恢复反馈设计。')
add('04-main-menu','山门与导航','山门主界面','默认','main','existing',[ui+'MainMenu/UIMainMenu.cs'],'home')
add('05-character-select','角色选择与解锁','选择道友','首名可用／两名未解锁','characters','existing',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'locked')
add('06-character-owned','角色选择与解锁','选择道友','全角色已解锁／选中剑修','characters','existing',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'owned')
add('07-character-detail','角色选择与解锁','道友详情','起始道法与说明','character-detail','suggested',[ui+'MainMenu/CharacterSelect/CharacterItem.cs'],'detail','整页详情是对已有角色与起始技能数据的美术补充。')
add('08-unlock-confirm','角色选择与解锁','结缘道友','500 金币确认','message','suggested',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'unlock-confirm','源点击直接购买；增加明确消费确认。')
add('09-unlock-insufficient','角色选择与解锁','结缘道友','金币不足','message','supporting_state',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'unlock-insufficient')
add('10-unlock-success','角色选择与解锁','结缘道友','已解锁','message','supporting_state',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'unlock-success')
add('11-character-empty','角色选择与解锁','选择道友','配置为空','empty','suggested',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'character-empty')
add('12-level-select','秘境选择','选择秘境','两关列表／第一关已选','levels','existing',[ui+'MainMenu/LevelSelect/LevelSelectPanel.cs'],'select')
add('13-level-detail','秘境选择','秘境详情','第二关说明','levels','supporting_state',[ui+'MainMenu/LevelSelect/LevelItem.cs'],'detail','两个配置实际共享Map1/Stage1；不伪称已有独立第二张地图。')
add('14-level-unselected','秘境选择','选择秘境','尚未选择','levels','suggested',[ui+'MainMenu/LevelSelect/LevelSelectPanel.cs'],'unselected','确认前置校验属于UI补齐。')
add('15-level-empty','秘境选择','选择秘境','无关卡配置','empty','suggested',[ui+'MainMenu/LevelSelect/LevelSelectPanel.cs'],'level-empty')
for id,state,variant in [('16-powerup-overview','14项属性总览','overview'),('17-powerup-detail','已选属性／可购买','detail'),('18-powerup-insufficient','金币不足','insufficient'),('19-powerup-maxed','已达各自最高阶','maxed'),('20-powerup-success','已购买／阶数更新','success')]:
    add(id,'永久成长','温养根基',state,'growth','existing',[ui+'MainMenu/PowerUp/PowerUpAttributeUpgrade.cs',perk_source],variant)
for id,state,variant in [('21-settings-audio','总音量／音乐／音效','audio'),('22-settings-display','分辨率／全屏／伤害浮字','display'),('23-settings-language','语言选择','language')]:
    add(id,'设置','清心小筑',state,'settings','existing',[ui+'Setting/SettingPanel.cs'],variant,'源仅配置English；中文为本次美术本地化，不宣称源已支持中文。' if variant=='language' else '')
add('24-display-confirm','设置','画面设置确认','保留或还原','message','suggested',[ui+'Setting/SettingPanel.cs'],'display-confirm','分辨率变更的安全还原设计。')
for id,state,variant in [('25-battle-hud','常规战斗／空技能槽','normal'),('26-battle-build-full','6主动＋6被动满槽','full'),('27-battle-buffs','燃烧／冰冻／减速状态','buffs'),('28-boss-arrival','末波首领预警','boss')]:
    add(id,'核心战斗','战斗 HUD',state,'battle','suggested' if variant=='boss' else 'existing',[ui+'Game/SkillIconPanel.cs',prefix+'Scenes/Managers/GamePlay.unity'],variant,'首领存在；明显预警条为美术补齐。' if variant=='boss' else '数值为状态排版样例，非游戏运行截图。')
for id,state,variant in [('29-upgrade-new','新主动／新被动三选一','new'),('30-upgrade-existing','持有道法升级','existing'),('31-upgrade-moneybag','技能满级后金币补位','moneybag')]:
    add(id,'局内升级','灵光乍现',state,'upgrade','existing',[ui+'Game/UpgradeSkillPanel.cs',ui+'Game/UpgradeSkillItem.cs'],variant)
for id,state,variant in [('32-treasure-one','单件奖励／揭晓中','one'),('33-treasure-three','三件奖励／揭晓中','three'),('34-treasure-five','五件奖励／可领取','five'),('35-treasure-evolution','满足条件／法器进化','evolution'),('36-treasure-moneybag','无可升级技能／金币替代','moneybag')]:
    add(id,'宝箱与进化','机缘宝匣',state,'treasure','existing',[ui+'Game/TreasurePanel.cs',prefix+'Scripts/System/Skill/SkillManager.cs'],variant,'宝箱揭晓约3秒后才可确认，奖励全部领取而非三选一。')
add('37-pause','暂停与退出','稍作调息','暂停','pause','suggested',[prefix+'Scripts/Input/InputReader.cs'],'pause','源有暂停事件但未见完整暂停窗口，按类型基础功能补齐。')
add('38-abandon-confirm','暂停与退出','结束历练确认','取消／返回山门','message','suggested',[ui+'MainMenu/GameEndPanel.cs'],'abandon')
add('39-exit-confirm','暂停与退出','离开游戏确认','确认／取消','message','suggested',[ui+'MainMenu/UIMainMenu.cs'],'quit','源有退出按钮但未接通回调；美术提供确认状态，后续接入。')
add('40-victory','历练结算','此境已平','所有波次清空／胜利','result','existing',[ui+'MainMenu/GameEndPanel.cs',prefix+'Scenes/Managers/GamePlay.unity'],'victory','不沿用旧稿90秒胜利；样例时长12:35。')
add('41-defeat','历练结算','道途未尽','气血耗尽／失败','result','existing',[ui+'MainMenu/GameEndPanel.cs'],'defeat')
add('42-save-pending','本地存档与反馈','本地保存提示','保存中／避免重复领取','message','suggested',[ui+'MainMenu/GameEndPanel.cs'],'saving','原有保存系统；明确等待反馈为设计补齐。')
add('43-save-error','本地存档与反馈','本地保存异常','重试／保留当前界面','message','suggested',[ui+'MainMenu/GameEndPanel.cs'],'save-error')
add('44-guide-controls','帮助与引导','入山指引','移动与自动施法','guide','suggested',[prefix+'Scripts/Input/InputReader.cs'],'controls')
add('45-guide-growth','帮助与引导','悟道指引','升级／满槽／宝箱','guide','suggested',[ui+'Game/UpgradeSkillPanel.cs',ui+'Game/TreasurePanel.cs'],'growth')
add('46-skill-codex','道法资料','道法总览','九主动／属性说明','codex','suggested',[prefix+'ScriptableObjects/DataSO/Skill/AttackSkill'], 'codex','资料面板为新增帮助UI；技能与配方来自源数据。')
add('47-evolution-locked','道法资料','法器化境','条件未满足','evolution','suggested',[prefix+'Scripts/System/Skill/SkillManager.cs'],'locked','进化资料页为美术补齐，进化逻辑来自源系统。')
add('48-evolution-ready','道法资料','法器化境','条件已满足／待宝箱触发','evolution','suggested',[prefix+'Scripts/System/Skill/SkillManager.cs'],'ready','不提供绕过宝箱的立即进化按钮。')
add('49-character-stats','道法资料','道友属性','局内与永久成长分区','stats','suggested',[prefix+'ScriptableObjects/RuntimeDataSO/PowerUp/PowerUpStat.asset'],'stats','资料页为美术补齐；不虚构装备穿戴系统。')
add('50-notice-states','通用控件','消息反馈','成功／不足／异常／空态','notice','supporting_state',[ui+'MainMenu/PowerUp/PowerUpAttributeUpgrade.cs'],'notices')
add('51-control-states','通用控件','统一控件','普通／按下／选中／禁用／锁定','components','supporting_state',[ui+'MainMenu/CharacterSelect/CharacterSelectPanel.cs'],'components')
add('52-flow-map','流程说明','整套界面关系','入口与返回路径','flow','supporting_state',[ui+'MainMenu/UIMenuManager.cs'],'flow')
excluded=[
 {'system':'更新器／在线公告／登录／选服／创建账号角色','reason':'单机模板，未发现在线账号、补丁或区服系统；启动与3名预设角色选择已覆盖。'},
 {'system':'背包／仓库／物品整理／使用数量','reason':'源为即时拾取和道法槽，未发现持有物品库存；以拾取和宝箱语义表达。'},
 {'system':'装备穿戴／强化／打造／交易','reason':'Armor是被动属性，不是穿戴装备；永久成长与道法进化已覆盖。'},
 {'system':'任务／活动／签到／成就／排行榜','reason':'未发现对应数据或业务入口；波次进度及胜败目标已覆盖，不机械增设运营功能。'},
 {'system':'好友／聊天／邮件／组队／帮会／宠物／坐骑','reason':'未见游戏内对应业务，F风格图不能作为功能需求；狐图只作美术展示。'},
 {'system':'一般物品商店／出售／兑换／抽卡','reason':'经济入口仅角色解锁与PowerUp购买；未见其他商城逻辑。'},
 {'system':'重抽／跳过／禁用道法／复活','reason':'未发现reroll/skip/banish/revive实现，不画成已支持操作。'}]
document={'schemaVersion':2,'workingTitle':'道途幸存者','titleStatus':'临时名称',
 'phase':'art-only','referenceGame':{'url':'https://github.com/Roo-Roo-Roo/survivors-roguelike-kit','commit':'3f905381d73a34b516030528b8ef6743868b9e52','localPath':str(ref)},
 'artReference':{'path':'F:/work/image','remote':'https://luyuacpp.visualstudio.com/image/_git/image'},
 'outputRoot':str(root),'deliveryGithub':None,'deliveryGithubStatus':'待用户提供，不提交、不推送、不发布',
 'designResolution':[1920,1080],'screens':rows,'permanentAttributes':perks,'activeSkills':skill_data,
 'sourceFacts':{'defaultSaveGold':5000,'baseCharacterHp':100,'characterCount':3,'lockedCharacterPrices':[500,500],'levelConfigCount':2,'activeSlotCount':6,'passiveSlotCount':6,'upgradeChoices':3,'treasureRewardCounts':[1,3,5],'treasureRevealSeconds':3,'lastSpawnSeconds':720,'victory':'全部波次已启动且存活敌人归零','passiveSkillAssets':14,'runtimePassivePool':13,'notInCurrentRuntimePool':['Curse']},
 'excludedSystems':excluded,'status':'inventory_established_production_in_progress'}
out=root/'docs/ui-suite/UI_COVERAGE.json';out.write_text(json.dumps(document,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# UI 功能与资源总清单','',f'功能参考固定版本 `{document["referenceGame"]["commit"]}`。共 {len(rows)} 张整屏／状态／流程画面；不是52种独立游戏系统。制作和验收状态见同名JSON，当前开始制作。','',
 '| ID | 系统 | 界面／状态 | 依据 | 制作 | 验收 |','| --- | --- | --- | --- | --- | --- |']
for r in rows:lines.append(f'| {r["id"]} | {r["system"]} | {r["interface"]} · {r["state"]} | {r["basis"]} | planned | pending |')
lines+=['','existing=参考已有功能；supporting_state=已有功能的展示状态补齐；suggested=明确标注的新增美术建议。','', '## 不适用／未发现的系统','']
for r in excluded:lines.append('- **'+r['system']+'**：'+r['reason'])
(root/'docs/ui-suite/UI_COVERAGE.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'screens':len(rows),'attributes':len(perks),'activeSkills':len(skill_data),'status':'inventory_established'},ensure_ascii=False))

