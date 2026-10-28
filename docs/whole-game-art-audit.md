# 整款游戏美术：源码范围与缺口审计

核实日期：2026-10-28（America/New_York）。功能参考为 `https://github.com/Roo-Roo-Roo/survivors-roguelike-kit`，固定提交 `3f905381d73a34b516030528b8ef6743868b9e52`；本地为 `E:\work\image\DaoSurvivors\.reference\survivors-roguelike-kit`。本报告为实际源码/序列化资源审计，未运行 Unity，不等于最终美术验收。并列的 `whole-game-art-audit.json` 给出逐项实际路径、Prefab SHA-256、Sprite/脚本/控制器引用及31组刷怪来源。

当前要求已扩大为这款单人俯视幸存者游戏的全部视觉美术。52项 UI 状态仅是其中一类；不能以52张界面图代替人物动作、地图地块、敌人、世界掉落物和技能弹体。本次仍只做美术，Unity 工程接入、Prefab、Shader/C#与运行联调留到下一阶段。

## 实际读取与计数方法

实际阅读根 README、已有玩法/UI审计，并直接检查 `Assets/RGame/RoguelikeKit/` 下的 Runtime Pool、Stage1及31组SpawnSet、两份关卡、三角色Prefab与六份AnimationClip、Map1、MapManager、敌人Prefab、敌人移动/受击/死亡、五种Magic、DropOut、九技能Prefab和Cast/Sport逻辑、Burn/Freezing/Slow以及相关Shader。全仓 `.meta` GUID 建表后解析资源引用，精英没有按名称猜成新怪种。参考克隆无 AGENTS.md，制作目录及适用上级未发现 AGENTS.md；F侧本次保持只读。此前已核实 LFS 清单为空；三份PSB实际约14–15MB，有真实字节，非LFS指针。

下文 `K/` 表示功能参考仓库相对路径 `Assets/RGame/RoguelikeKit/`。这些路径只用于取证，不是成果 GitHub 地址。成果远端仍待用户提供。

| 类别 | 直接确认的数量与范围 |
| --- | --- |
| 玩家 | 3身份，6动作：每人Idle/Run；横向镜像，无八方向合同 |
| 敌人 | 20个活跃PoolKey = 14基础身份 + 6精英key；实际13独立Sprite文件 |
| 刷怪 | Stage1有31组配置；不等于31种外观 |
| 世界地图 | 1套Map1，6种权重随机地块，100×100逻辑格，两关共用 |
| 可破坏道具 | 1种Prop，每地图20个实例，不是20种图 |
| 世界掉落 | 6个key：Exp40/Exp80/ReplyHP/Suck/Purse/Box |
| 主动技能 | 9种基本攻击纹理及9种进化后的视觉使用关系；源不要求18套独立纹理 |
| 敌方弹体 | 5种Blue/Pink/Red/Green/SnowMagic |
| 敌方状态 | Burn/Freezing/Slow共3状态；后两种共用SlowBuff环 |
| 通用世界支持 | 阴影、溶解噪声及受击/淡出状态规格 |

## 玩家身份与动作

| 源身份 | 当前静态美术 | 必须交付的动作 | 源资源 |
| --- | --- | --- | --- |
| Fighter | `art/characters/hero.png` | Idle、Run | `K/Prefabs/Player/Fighter.prefab`、`K/Art/Sprites/Player/Fighter.psb` |
| Assassin | `art/characters/sword.png` | Idle、Run | `K/Prefabs/Player/Assassin.prefab`、`K/Art/Sprites/Player/Assassin.psb` |
| Mage | `art/characters/healer.png` | Idle、Run | `K/Prefabs/Player/Mage.prefab`、`K/Art/Sprites/Player/Mage.psb` |

每人的 `K/Art/Animation/<身份>/{Idle,Run}.anim` 都是1秒、30采样/秒、循环。检查曲线没有 `m_Sprite`切帧，实际为PSB骨骼的旋转/位移/缩放。`PlayerAnim.cs`只按速度是否为0切换Idle/Run；`PlayerMovement.cs`按x方向镜像。源不要求玩家挥刀、施法、受伤、倒地、八方向动画；自动攻击由独立技能对象表现。`PlayerHit.cs`受击白闪、死亡材质Alpha约0.2秒淡出，影子约0.8秒后触发失败。

后续美术交付可选择统一画布的真实角色逐帧动作包，或可活动的分层身体/骨骼美术与明确Idle/Run动作设计。必须实际展示四肢/衣饰动作、脚底注册、时长和循环质量；不能只把整张立绘上下晃动或缩放就称为角色跑步完成。当前三张独立静态立绘可作为角色母版，尚不能据此验收六套动作。

## 敌人身份与20个PoolKey

直接来源：`K/ScriptableObjects/RuntimeDataSO/Pool/Pool.asset`，Stage1/SpawnSet，以及下列Prefab。除Crow异常外，精英与对应基础key确实引用同一PNG。

| 基础身份 | 关联精英key | 实际引用PNG文件名 | 行为/弹体 |
| --- | --- | --- | --- |
| Bat | Bat1 | Bat.png | 远程；BlueMagic |
| BoyFairy | — | BoyFairy.png | 远程；GreenMagic |
| EyeBall | EyeBall1 | Eyeball.png | 近战 |
| FlySkull | FlySkull1 | FlySkull.png | 近战 |
| ForestGuardianFairy | ForestGuardianFairy1 | ForestGuardianFairy.png | 远程；GreenMagic |
| Gear | Gear1 | Gear.png | 近战 |
| Ghost | — | Ghost.png | 直线冲撞 |
| Slime | Slime1 | Slime.png | 近战 |
| Crow | — | **Ghost.png** | 近战与状态机；Boss |
| CrystalHealerFairy | — | CrystalHealerFairy.png | 远程；SnowMagic；Boss |
| Fairy | — | Fairy.png | 远程；RedMagic；最终Boss |
| FlameDancerFairy | — | FlameDancerFairy.png | 远程；RedMagic；Boss |
| FrostCrystalFairy | — | FrostCrystalFairy.png | 远程；SnowMagic；Boss |
| PinkFairy | — | PinkFairy.png | 远程；PinkMagic；Boss |

PNG位于 `K/Art/Sprites/Monster/NewMonster/`。Prefab位于 `K/Prefabs/Enemy/NewMonster/`，有的在对应身份子文件夹；JSON列出完整准确路径。

**Crow异常：**源码有Crow.png，但Crow.prefab实际写入Ghost.png GUID；不能凭PoolKey说原画就是乌鸦。新美术为14个身份分别设计道家外观是合理改造，须注明Crow独立外观属于本次修订；严格复现则只需13种基础Sprite。六精英允许复用基础画面并用材质/共用精英标记区分，不能谎称源已有六套不同PNG。

这些敌人没有Animator或.anim序列。Sprite通过材质正弦顶点扰动、脚本移动和左右镜像产生动态；受击由HitAnimationSO白闪，死亡由DissolveAnimationSO噪声溶解约0.3秒。`ChargeEnemy`在初段跟踪后定向冲撞；Crow状态机含冲刺/缩放等。美术完整最低要求为：14身份母版、20 key逐个映射、普通/精英/Boss区别、可辨识世界缩放及脚底Pivot、白闪/溶解/冲刺状态设计。逐怪跑攻死序列不是原项目必需，可作为额外质量提升而非缺口假增。

现有 `enemy-tiger.png`、`enemy-lantern.png`是两个试用敌人，尚无覆盖14身份的完整证据，不可直接用两张图片替代全部敌人。

## 地图与可破坏物

`K/ScriptableObjects/DataSO/Level/Map/Map1.asset`的6条Sprite：

| 源纹理 | 原生尺寸 | 权重 |
| --- | ---: | ---: |
| `K/Art/Sprites/Map/Map_1.PNG` | 2048×2048 | 200 |
| `K/Art/Sprites/Map/Map_2.PNG` | 2048×2048 | 3 |
| `K/Art/Sprites/Map/Map_3.PNG` | 2048×2048 | 3 |
| `K/Art/Sprites/Map/Map_4.PNG` | 2048×2048 | 1 |
| `K/Art/Sprites/Map/Map_5.PNG` | 2048×2048 | 1 |
| `K/Art/Sprites/Map/Map_6.PNG` | 2048×2048 | 3 |

MapManager把每张随机纹理缩放到1×1世界单位格，拼成100×100；因此新图必须六种外边缘兼容，验收混排接缝和大面积重复效果。不能把一张有建筑、镜头和角色的整幅插画当作已完成六张可循环地块。当前 `art/illustrations/arena-v1.png`是UI背景插画，不满足此合同。源2048尺寸是已存素材事实，新制作可在共同清晰度合同中选择一致尺寸；不得把缩放称原生生成细节。

`K/Prefabs/DropOut/Prop.prefab`是唯一可破坏物，源码以规则网格实例化20次。接触Skill后溶解，随机落物；不是移动障碍地图设计。新美术要单独提供完整透明Prop及落地阴影；碎裂序列非源必需。两关引用同一个Map1/Stage1，不增加第三关，也不凭美术两种缩略图声称源码已有两张不同地图。

## 世界掉落与拾取

| PoolKey | 源Prefab | 视觉交付与现状 |
| --- | --- | --- |
| Exp40 | `K/Prefabs/DropOut/Exp40.prefab` | 当前UI有exp.png；需世界小尺寸验收和40点形态/颜色映射 |
| Exp80 | `K/Prefabs/DropOut/Exp80.prefab` | 源与Exp40同Sprite，蓝/橙颜色不同；需清楚区别而非改成同一值 |
| ReplyHP | `K/Prefabs/DropOut/ReplyHp.prefab` | 可从healing.png承接世界拾取图，但须缩小检查；回复20HP |
| Suck | `K/Prefabs/DropOut/Suck.prefab` | 全场经验吸取物；缺独立可识别世界图，源本体旋转 |
| Purse | `K/Prefabs/DropOut/Purse.prefab` | 可从moneybag.png承接世界图；源加50金币 |
| Box | `K/Prefabs/DropOut/TreasureBox.prefab` | 可从treasure-closed.png承接世界图；开启/奖励见UI状态清单 |

Exp40/Exp80及Shadow引用GUID `a86470a33a6bf42c4b3595704624658b`未在仓库.meta找到，不能宣称已解码原始Sprite；颜色和值由Prefab直接核实。此缺失不阻止新绘拾取物与阴影。源没有独立运行金币Coin池入口，也不把空Pickup壳当作背包系统。

## 九技能世界美术和进化

来源：`K/Prefabs/Skill/<Key>.prefab`、`K/Scripts/System/Skill/SkillCast/<Key>Cast.cs`及`Skill/Sport/<Key>.cs`。源技能均无Animator，世界Sprite与UI图标是不同用途。现有九张`art/icons/skill-*.png`仅证明图标完成，世界弹体/范围环的透明留白、朝向和Pivot要另行验收。基本纹理可在进化后继续复用，参数变化需在预览/清单表达。

| Key / 本轮临时名 | 世界形态 | 源进化变化 |
| --- | --- | --- |
| ToNearestSkill / 追星御剑 | 朝近敌方向的飞剑弹体 | CD=0.15；Damage=5 |
| BothSideSkill / 两仪斩 | 左右双向斩/投射 | CD×0.3，Area×2 |
| BouncingSkill / 流珠引 | 屏幕边缘反弹的珠 | Velocity×1.5，Amount+3 |
| ChainSkill / 连星诀 | 寻敌连锁弹体 | CD×0.3 |
| CircularAttackSkill / 太极震 | 向周围放射的弹体 | Mixed分支固定16方向、间隔22.5°，额外缩放×2 |
| CircularMotionSkill / 葫芦巡天 | 绕玩家旋转的法器 | Velocity+1，Amount+3 |
| FourCornerSkill / 四象符 | 四角投射物 | Area×2 |
| InsideScopeSkill / 八卦阵 | 跟随玩家的范围环 | Area×2 |
| RandomSkill / 落花令 | 目标处命中/淡出印记 | CD×0.3 |

不要从美术名称推出源码没有的穿透、召唤或额外状态。进化条件/宝箱收取流程以UI清单和玩法审计为准。源有火/冰/慢Debuff的技能配置及世界材质表现；这不代表玩家也有三条负面状态。

## 五敌方弹体、三状态和通用支持

五弹体分别位于 `K/Prefabs/Enemy/Magic/{BlueMagic,PinkMagic,RedMagic,GreenMagic,SnowMagic}.prefab`，对应 `K/Art/Sprites/Monster/NewMonster/Magic/*.png`。由EnemyMagic脚本直线移动、命中回收、超时5秒回池；不要求五份逐帧动画。新图需在玉绿/纸色世界中仍有危险对比，五种身份有明确纹理或颜色映射，不能只用UI Buff图标代替。

Burn在敌人材质上染红并持续伤害；Freezing停速且停材质时间；Slow减速且降低材质时间，后两者共用 `K/Prefabs/Buff/SlowBuff.prefab` / SlowBuff.png的脚底环。三张Buff UI图标已存在，世界状态需要单独可看预览/参数说明，可复用同一环而不重复伪增图数。

通用独立美术还应覆盖：椭圆落地影/可投影Alpha、溶解灰度噪声（Enemy/Prop材质 `_NoiseTex`）、受击白闪/死亡淡出/精英状态的视觉规格。源dissolveTex/Ramp文件存在不等于都被使用；按材质实际引用建立替代关系，不机械复制全部技术贴图。Shader重写留到Unity接入阶段，本阶段可交付PNG与效果预览、不得标为Unity运行通过。

## 当前缺口及最低完整交付矩阵

本节是2026-10-28审计时点的缺口快照；后续制作验收另行更新生产清单，不改写历史快照说素材早已完成。

| 类别 | 当前已取得 | 达到整款美术完成还需 |
| --- | --- | --- |
| UI | 52屏/状态、控件/图标已制作 | 全屏视觉及文案验收、正式资源manifest和导入参数 |
| 玩家 | 3张静态立绘 | 3人×Idle/Run、画布/脚底Pivot/动作预览验收 |
| 敌人 | 2个初步试用敌人 | 14基础身份成图、20 key映射、6精英状态、Boss辨识 |
| 地图 | 1张道场UI插画 | 6边缘兼容地块与混排接缝预览、1透明Prop |
| 掉落 | 经验/治疗/钱袋/宝箱UI图标 | 6世界拾取物映射，补Suck，区分Exp40/80，世界缩小检查 |
| 玩家技能 | 9个UI图标 | 9世界FX与9进化使用关系/状态对照 |
| 敌人技能 | 未建立独立美术映射 | 5世界弹体、三Debuff表现 |
| 通用世界支持 | 未建立独立美术映射 | 阴影、溶解遮罩、白闪/消散/精英视觉规格 |
| 来源交付 | 已有原图/切片证据 | 新增逐图证据、哈希、统一清单和Unity导入建议；仍不接入Unity |

不适用系统：在线账号/服务器/角色创建、MMORPG背包装备仓库/世界传送/组队帮会宠物坐骑、社交好友邮件聊天、卡牌抽取、任务签到活动排行榜。源未启用的旧Enemy1木头/钟表/文具等样例、TMP/插件示例、调试图、编辑器图标不计入当前可玩流程的全部美术要求。无需把31刷怪配置当31怪种，也无需生造三张不同世界地图。声音/音乐不在本次“图片及UI美术”审计中。

## 可复核文件

- `docs/whole-game-art-audit.json`：全部20敌人/3玩家/9技能/6掉落/5弹体/6地块的精确源路径、控制器、Sprite和脚本引用。
- `tools/audit-whole-game-art.py`：只读参考源码并输出上述JSON的扫描器，未修改参考库或任何Git状态。
- `docs/reference-audit-gameplay.md`与`docs/reference-audit-ui.md`：玩法/52 UI工作依据。
- `docs/ui-suite/UI_COVERAGE.json`：UI制作清单；不能单独作为本次扩大后整款美术的覆盖证明。

所有新增成果继续位于 `E:\work\image\DaoSurvivors`。F盘只读，项目关联保存在本项目 `docs/image-reference-associations.md`；当前不提交、不推送、不发布。
