# 功能参考游戏：玩法与系统审计

核实日期：2026-10-26。功能参考为 [Survivors Roguelike Kit](https://github.com/Roo-Roo-Roo/survivors-roguelike-kit)，本地位置 `.reference/survivors-roguelike-kit/`，实际提交 **`3f905381d73a34b516030528b8ef6743868b9e52`**。该地址是功能参考，不是本次成果的提交远端。

本次阅读实际 C#、ScriptableObject YAML、场景序列化组件和相关图像，没有启动 Unity，也不将源码存在当作游戏已运行验证。逐项文件、行号、源码摘录与 SHA-256 位于 [reference-gameplay-evidence.json](reference-gameplay-evidence.json)。以下路径均相对功能参考仓库；公共前缀 `Assets/RGame/RoguelikeKit/` 简称 `Kit/`。

## 实际资料与入口

已读取根 README、Media/README，以及选角、选关、地图、波次、技能、升级、宝箱、玩家、敌人、掉落、属性、存档与战斗 UI 源文件。参考仓库内未找到 AGENTS.md，也没有除 README 和 Media/README 外的本地项目 Markdown 需求／交接／验收合同。Media/README 仍把截图称为占位文件，但实际八份截图／GIF 均已取得真实字节并可解码；`Fight.png` 和 `SkillUpgrede.png` 已实际查看。根目录没有 `.gitattributes`，`git lfs ls-files` 为空，本任务所需图像不是 LFS 指针。

这是**单人俯视自动攻击的幸存者肉鸽模板**。主流程为主菜单 → 选预设角色 → 选关 → 加载 → 移动御敌、拾取与升级 → 胜／败结算 → 金币入库并返回菜单。没有证据支持把它扩展解释为 MMORPG、在线社交或传统装备背包 RPG。

## 与此前九张初稿不同的关键事实

1. 源游戏有 **3 名预设角色、2 个关卡配置**。两关目前引用同一个 Map1、Stage1 和预览图，第二关描述虽称略难，但独立地图或难度差异没有在配置中得到证明。
2. Stage1 引用 **31 组刷怪配置**，最终 Fairy 在 **720 秒**开始出现。胜利条件为全部配置已启动且存活怪数归零，不能写成“90 秒到点胜利”，也不能写成“12:00 自动胜利”。
3. 有 **6 主动＋6 被动**技能槽；9 个主动技能资产、14 个被动属性资产。实际 GamePlay 场景随机池启用 9 主动＋13 被动，**未挂入 Curse**。
4. 有**宝箱一／三／五奖励、法宝进化和满级钱袋补位**；这些是原九张画面之外必须补齐的参考游戏核心 UI。
5. SaveGame 默认 GoldCount 为 **5000**。此前新原型的 120 初始货币、三关、90 秒和不同角色气血不是来源事实，应作为旧方案保留边界或由新方案明确覆盖。

证据：`Kit/Scripts/System/Skill/SkillManager.cs:193–347`；`Kit/Scenes/Managers/GamePlay.unity:5060` 的组件 `1373949327`；`Kit/ScriptableObjects/DataSO/Level/SelectLevel/{FirstLevel,SecondLevel}.asset:13–20`；`Kit/Scripts/System/Stage/StageManager.cs:170–178`；`Kit/Scripts/System/Save/SaveGame.cs:23–40`。

## 角色、关卡与战斗信息

| 原角色 | 已核实起始技能 | 直接证据 |
| --- | --- | --- |
| Fighter | ToNearestSkill | `Kit/Prefabs/Player/Fighter.prefab:538` |
| Assassin | BothSideSkill | `Kit/Prefabs/Player/Assassin.prefab:571` |
| Mage | BouncingSkill | `Kit/Prefabs/Player/Mage.prefab:610` |

三个角色配置有头像、起始技能图和角色 Prefab；Assassin、Mage 资产的 SellingPrice 为500。角色购买和永久强化菜单另由菜单审计补充。共同 PlayerStat 默认 HP=100，现有证据不能证明此前 120／100／150 的职业气血差异。

Map1 是100×100逻辑格和20个可破坏道具，地图代码按权重生成地块；它不是世界大地图或传送系统。两关卡的名称和缩略图可按道家风格重新设计，但必须注明同源配置，不能把美术差异说成源码已具备的独立玩法。

玩家移动读取输入系统，键盘无输入时可取摇杆；移动向量归一化。主动技能通过计时器循环自动施法。战斗 HUD 的必要信息为气血、经验和等级、12技能槽、本局金币及击败数。原截图与场景有这些 UI；时长、波次目标、Boss宽血条、危险箭头或目标详情可合理补充，但要标注为新设计。

## 技能、被动与进化

源技能名称主要为内部英文 Key，Description 为空；下面的中文是功能释义，正式道家名称属于本次美术文案。

| 主动 Key | 功能语义 | 配方被动 Key |
| --- | --- | --- |
| BothSideSkill | 双向挥击 | Armor |
| BouncingSkill | 弹跳投射 | HPMax |
| ChainSkill | 连锁寻敌 | MoveSpeed |
| CircularAttackSkill | 环形范围攻击 | Area |
| CircularMotionSkill | 环绕法器 | Duration |
| FourCornerSkill | 四向投射 | Might |
| InsideScopeSkill | 区域攻击 | SkillSpeed |
| RandomSkill | 随机投射 | Amount |
| ToNearestSkill | 自动追踪最近目标 | Cooldown |

这九个主动资产各有10条 UpgradeAttribute；当前最大等级规则为 `UpgradeAttribute.Count + 1`，所以本组为11级。14项被动为 Might、Armor、HPMax、Recovery、Cooldown、Area、SkillSpeed、Duration、Amount、MoveSpeed、Magnet、Growth、Greed、Curse，各有5个升级值。完整数值已从 Unity 十六进制整数数组解码到证据 JSON。

进化触发是：主动技能满级＋已持有兼容被动（代码不要求被动满级）→ `WaitMix` → 宝箱优先抽出 → 领取时调用 `MixSkill` → `Mixed`。须制作配方未齐、主动满级但缺被动、可进化、宝箱进化奖励、已进化等状态。原始 `CircularAttackSkillCast` 没有独立 MixSkill 覆盖，继承基类的状态改变；不应杜撰一个已经实现的特有进化攻击效果。

原升级卡某些英文伤害说明写百分号，但 DamageAdd 的实现是整数相加。后续中文展示应根据真实字段表达“伤害＋10”等，不直接照抄不一致描述。

## 升级与宝箱必须分开设计

升级从未满级且槽位允许的技能中无重复抽取，最多3项。已占满某类6槽时，仍可升级该类已持有技能，不能再得新技能。可选技能不足3个时，用每份50金币的钱袋补齐。界面打开后暂停，选择其一后继续。

宝箱由拾取触发，奖励数为1、3或5。先处理 `WaitMix`，再升级已持有技能，允许同一技能按剩余升级次数重复出现在一箱内；无可用技能时钱袋补位。金币受 Greed 影响。UI 揭晓动画约3秒，确认按钮之后启用，确认时**全部奖励一起生效**。不能把宝箱错误画成第二次三选一。

据此至少覆盖：普通三选、新技能卡、已有升级卡、钱袋补位、全满钱袋三选；宝箱拾取／揭晓禁用／一奖／三奖／五奖／进化混排／可领取／领取后返回。

## 妖灵、状态与掉落

有追踪近战、在射程内停步的远程、短时间锁定后持续冲锋的敌人类型；Boss状态节点包括 Rush、Teleport 及 Single／Burst／Circle／Spread／Spiral 射击。Boss出现预警、血条和详情是可补充的美术界面，并非已发现的现有 Boss UI。

BurnBuff、FreezingBuff、SlowBuff 作用于 BaseEnemy：烧伤按 Tick 伤害，冰冻令速度归零，减速按比例扣除速度。当前通过材质／附着效果反馈。为敌人补状态图标与时间标识合理，但不要称为原有玩家负面状态栏。

掉落物靠近后按 Magnet 范围吸向玩家；经验受 Growth 影响；Purse 默认50金币、ReplyHp 默认回复20HP、SuckExp吸取全场经验。可破坏物按权重生成掉落，敌人按 dropKeys 生成掉落。`Coin.cs` 目前只删除对象，没有加金币；`Pickup.cs` 是空壳，不能从类名推断完整背包或拾取系统。

## 胜败、存档与合理补充

HP耗尽会停止角色并淡出，发出GameOver。GamePlay场景中有GameWin和GameOver两套GameEndPanel；结算返回会把 CurrentGetGold 加入局外 GoldCount，保存并回主菜单。没有复活或广告复活源码。本局时间、最终等级、道法明细、伤害排行等结算内容如新增，要标为设计补充；已有“金币与击败数”可直接承接。

存档字段包含设置、14项局外成长、金币和二／三角色购买状态；没有本局中途继续字段。读取／保存异常当前仅输出日志，面向用户的安全提示、重试和返回属于必要的设计补充。不要设计成已上线的云存档或联网服务。

当前未找到在线登录、服务器、角色创建、背包仓库、装备穿戴交易、任务成就、签到活动、排行榜、好友聊天邮件、组队帮会、抽卡、宠物坐骑、打造、复活和自动更新服务。InputReader 虽残留 Inventory 事件，但无实现或界面证据。整套 UI 应围绕已核实的幸存者流程覆盖，不机械加入上述系统。技能说明／进化图鉴、局内属性汇总、帮助引导、退出确认、资源或存档异常提示可列为明确的合理补充。

## 本次审计边界

证据是静态源码、配置、序列化场景和已取得截图；不证明所有参考代码路径能正常运行。没有修改参考游戏代码、没有 Unity 接入、没有提交或推送；本文件只为“UI 功能与资源总清单”提供可追溯事实与假设边界。
