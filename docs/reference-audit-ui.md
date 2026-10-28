# Survivors Roguelike Kit：UI、流程与状态审计

核实日期：2026-10-26（America/New_York）。功能参考仓库为 `https://github.com/Roo-Roo-Roo/survivors-roguelike-kit`，实际克隆位置 `.reference/survivors-roguelike-kit`，实际 HEAD 为 `3f905381d73a34b516030528b8ef6743868b9e52`。它是功能参考，**不是成果提交远端**。本审计不运行 Unity、不修改参考代码、不提交或推送。

## 实际检查范围与证据等级

实际阅读 README、Media/README，以及 UI 主菜单、选角、选关、PowerUp、设置、加载、局内 HUD、升级、宝箱、结算的脚本；交叉读取相关 Prefab、GamePlay/PersistentManagers 场景、SaveGame/SaveSystem、CharacterSelectConfig、LevelConfig、两关和三角色配置。`Scripts/UI` 实际有 28 个 C# 文件，含布局、动画和交互辅助，不把 TMP 的 Examples 或 RSO 编辑器窗口当作游戏系统。

检索没有发现仓库内 AGENTS.md。仅有根 README 与 Media/README 两份 Markdown；后者仍写媒体占位说明，但实际六张游戏截图均存在、已解码并逐张查看，当前文件证据优先。`git lfs ls-files` 返回空，没有将 LFS 指针当成已取得图片。没有引擎运行验证，本审计是代码、序列化配置和静态画面的功能取证。

下列证据路径均相对功能参考仓库根目录。为缩短表格，`K/` 表示 `Assets/RGame/RoguelikeKit/`。`已证实`表示实际存在代码/配置/界面；`建议补齐`表示适合本类型的设计补充，不能冒称参考项目已经实现。

## 已证实的界面与操作

| 系统 | 实际入口、内容与流程 | 需要制作的状态 | 主要证据 |
| --- | --- | --- | --- |
| 主菜单 | New Game、Power Up、Settings、Exit 四入口 | 普通、悬停、按下、键盘焦点；退出确认属补齐 | `K/Scripts/UI/MainMenu/UIMainMenu.cs:12`；`K/Prefabs/UI/MainMenu/MainMenu_Panel.prefab:65,924,1673,2088` |
| 角色选择 | 主菜单新游戏打开角色列表；确认前往选关；返回关闭当前层 | 已解锁未选、已选、锁定附价格、购买成功、金币不足、取消、返回 | `K/Scripts/UI/MainMenu/UIMenuManager.cs:43–77`；`CharacterSelect/CharacterSelectPanel.cs:31–59,73–104` |
| 角色条目 | 名称、人物、初始技能图；三角色 Fighter、Assassin、Mage | 首角色可用；第二/第三位按存档锁定；两者售价均500 | `K/Scripts/UI/MainMenu/CharacterSelect/CharacterItem.cs:18–46`；`K/ScriptableObjects/DataSO/Level/SelectCharacter/{Fighter,Assassin,Mage}.asset:16–20` |
| 关卡选择 | 列表条目有预览图与描述；确认触发场景加载；返回关闭选关，露出角色层 | 普通、悬停、选中、确认、返回；无关卡/缺预览是建议异常补齐 | `K/Scripts/UI/MainMenu/LevelSelect/LevelSelectPanel.cs:25–69`；`LevelItem.cs:24–29`；`K/Prefabs/UI/MainMenu/LevelSelect_Panel .prefab:641–643` |
| 加载与淡入淡出 | 独立加载画面、旋转指示、场景过渡遮罩 | 加载中、进入完成；失败/重试是建议补齐 | `K/Scripts/UI/LoadingInterfaceController.cs:13–43`；`FadeController.cs:34–48`；`K/Scenes/Managers/PersistentManagers.unity:381,703,775,808` |
| 局外 PowerUp | 14属性网格；选中项显示名称、说明、下一阶金币；购买修改永久属性、扣币、保存与刷新货币 | 可购买、已选、升级成功、金币不足、满阶、返回；不足提示与满阶详情需设计补齐 | `K/Scripts/UI/MainMenu/PowerUp/PowerUpPanel.cs:19–27,38–40`；`PowerUpAttributeUpgrade.cs:84–98,116–120`；`PowerUpDescription.cs:15–27` |
| 设置 | 主音量、音乐音量、音效音量、分辨率、全屏、语言、伤害数字；使用左右调整 | 音量0/10/中间，布尔开/关，分辨率和语言选择，关闭返回；无可用选项/写入失败建议补齐 | `K/Scripts/UI/Setting/SettingPanel.cs:20–28,64–100,198–201`；`SettingItem.cs:53–90` |
| 局内主 HUD | 玩家出生后显示；HP当前/过渡条、经验条和等级、攻击与属性技能槽、当局金币和击败数 | 满血、受伤过渡、低血、零血；空槽/已填/满槽；经验积满与升级暂停；金币变化、伤害数字开/关 | `K/Scripts/UI/Game/MainPanel.cs:11–25`；`HealthUI.cs:12–24`；`LevelUI.cs:30–40`；`SkillIconPanel.cs:13–58`；`K/Scenes/Managers/GamePlay.unity:4621–4633` |
| 升级选择 | 三张卡，每张有图标、名称、等级、效果、选择按钮；选择后关闭并恢复 | 新激活攻击技能、攻击升级、属性升级、钱袋替代、鼠标/键盘焦点，暂停背景 | `K/Scripts/UI/Game/UpgradeSkillPanel.cs:25–68`；`UpgradeSkillItem.cs:19–77`；`K/Scenes/Managers/GamePlay.unity:8787–8790` |
| 宝箱 | 冻结战斗，展示一批技能/钱袋图标和获得金币；约3秒揭示后显示确认；确认应用全部奖励并继续 | 1/多奖励、揭示中确认不可用、可确认、含钱袋、升级/进化结果（技能取样条件由玩法审计补证） | `K/Scripts/UI/Game/TreasurePanel.cs:38–110`；`K/Scenes/Managers/GamePlay.unity:2048–2059` |
| 胜负结算 | 场景内有 GameWin 与 GameOver 两层；打开时冻结、清理对象/状态；退出时将当局金币加入存档并回主菜单 | 胜利、失败、最终金币/击败数、返回；重复领取防护/落盘失败应在后续接入验证 | `K/Scenes/Managers/GamePlay.unity:4290,5989`；`K/Scripts/UI/MainMenu/GameEndPanel.cs:30–52`；`CoinCountInGame.cs:14–16`；`KillCountInGame.cs:13–15` |
| 保存 | 自动保存设置、14属性阶数、金币、第二/第三角色解锁标记 | 首次本地档、读取失败、保存中/成功/失败是建议交互提示 | `K/Scripts/System/Save/SaveGame.cs:15–40`；`SaveSystemSO.cs:32–53` |

## 局外成长：14项配置与不同上限

实际 PowerUp_Panel.prefab 的 `mAttributeName`、`mMaxLevel`、`mRequireGold` 和 `mAttributeChangeValue` 已逐条读取；表内金币是原 demo 配置，**不是已完成平衡的本次正式经济**。新美术文案可转为道家用语，必须保留内部字段对应，不能缩成旧初稿的三个属性。

| 内部字段 | 建议中文功能名 | 原阶数上限 | 原每阶金币 | 配置说明 |
| --- | --- | ---: | --- | --- |
| Might | 法力 | 5 | 1/2/3/4/5 | 每阶伤害 +5% |
| Armor | 护身 | 3 | 1/2/3 | 每阶降低所受伤害10%（属性值为-10） |
| HPMax | 养元 | 3 | 1/2/3 | 每阶气血上限 +10% |
| Recovery | 回春 | 5 | 1/2/3/4/5 | 每阶每秒回复1气血 |
| Cooldown | 行法 | 2 | 1/2 | 每阶冷却 -10% |
| Area | 法域 | 2 | 1/2 | 每阶攻击范围 +10% |
| SkillSpeed | 御器 | 2 | 10/15 | 每阶投射物速度 +10% |
| Duration | 绵息 | 2 | 5/10 | 每阶效果持续 +15% |
| Amount | 分光 | 1 | 5 | 增加1投射物 |
| MoveSpeed | 身法 | 2 | 5/5 | 每阶移速 +10% |
| Magnet | 聚灵 | 2 | 25/25 | 每阶拾取范围 +25% |
| Growth | 悟性 | 5 | 5/10/15/20/25 | 每阶经验 +10% |
| Greed | 纳财 | 5 | 20/25/30/35/55 | 每阶金币 +10% |
| Curse | 劫数 | 5 | 100/200/300/400/500 | 提高敌人速度/气血/数量/频率，各阶说明10% |

证据见 `K/Prefabs/UI/MainMenu/PowerUp_Panel.prefab`：Might 2235–2242、Armor 2097–2104、HPMax 4095–4102、Recovery 11838–11845、Cooldown 5576–5583、Area 1433–1440、SkillSpeed 5677–5684、Duration 10538–10545、Amount 4516–4523、MoveSpeed 5150–5157、Magnet 7713–7720、Growth 641–648、Greed 5363–5370、Curse 10336–10344。机器可读表位于 `reference-ui-evidence.json`。

## 真实配置与旧九图的差别

1. 原参考是三角色、两关；旧初稿三关和90秒局是此前合理假设，不能继续标成来源事实。两关配置 `FirstLevel.asset`、`SecondLevel.asset` 当前引用相同 MapConfig 和 StageConfig；SecondLevel 的 Description 写更难，但显示用的 LevelDescription 仍与首关相同。设计可区分两个地点的美术/中文名称，须标为本次改写或补充，不能谎称源有独立三关内容。
2. 原第二/第三角色需要500金币解锁。旧初稿三人全可用，没有解锁购买、金币不足和锁定外观，应补图。
3. PowerUp 是14项且上限为1/2/3/5不同阶，旧三项成长不能代表完整系统。需要网格总览、选中详情、买得起/不足/满阶/成功状态与14项图标。
4. 原设置是7项，旧音效/特效两开关遗漏主音量、音乐、音效数值、分辨率、全屏、语言与伤害数字。资源目前只有 `Locales/English (en).asset`；本次中文是美术本地化，不称源已提供中英。
5. 原 HUD 为6攻击+6属性两组技能槽；旧两枚法术示意不完整。当局金币和击败数均有独立UI，不能只显示局外货币。
6. 原升级支持攻击激活/升级、属性收益、钱袋替代；旧单套三选图需增加语义状态。没有查到重抽、跳过、放逐入口，不应把这些画成已实现功能。
7. 原宝箱有5个潜在奖励槽、揭示中和全部领取流程。旧九图完全缺宝箱。
8. 原主菜单与选角、选关是分步；旧合并主界面可作为重设计选择，但必须额外交代分步返回关系，不丢掉原四入口。
9. 原加载/过渡、退出入口、首档/保存异常提示未被旧九图覆盖。暂停在原仓仅见输入事件，完整暂停菜单是建议补齐。
10. 原图鉴/灵宠展示不是已核实源 UI；旧图鉴可保留为明确建议补充，不能将其作为原有系统验收的替代。

## 建议补齐及不应机械叠加的内容

建议制作基础补充：启动/本地资源检查、加载失败与重试、选角购买确认与不足提示、PowerUp不足/满阶说明、暂停/继续/返回确认、键鼠操作帮助、技能与状态说明、保存失败说明、通用成功/警告/错误提示。这些均以“本次设计补充”列入总清单，点击/状态只通过美术图、预览与说明表达，本阶段不接业务。

未见完整用户系统、联网、更新服务、公告后台、服务器、角色创建、仓库背包、装备穿戴/强化、物品买卖、每日签到、活动、成就、排行、朋友、聊天、邮件、组队、公会、坐骑等代码或游戏UI证据。检索范围为 `K/Scripts`、`K/Prefabs/UI` 与 `K/Scenes`，排除第三方 TMP 示例和框架编辑器。`InputReader.cs:125–145` 有 Inventory 命名的遗留事件，**没有对应背包面板或订阅证据**，不足以认定背包系统存在。局外角色解锁与PowerUp花钱不等于独立商店。

没有检索到 `reroll/re-roll/banish/revive/skip/refund` 在游戏脚本或UI中形成相应功能。若以后加入，先列建议，不用模板式堆叠成当前必有系统。

## 需要在设计说明中保留的源状态边界

- `UIMenuManager.cs:108` 关闭PowerUp时解除的是 `CloseSettingsScreen`，与注册的 `ClosePowerUpScreen` 不符；不能拿静态源码当作重复打开完全可靠的运行证据。
- `UIMainMenu.ExitButtonAction` 有按钮与事件，但在 UIMenuManager 未找到订阅，在游戏脚本中未找到 Application.Quit；退出设计可以补齐，不能说源退出已经跑通。
- `CharacterItem.cs:46` 的 Button 回调无解锁判定，选角Panel另在指针事件里处理解锁；设计应清楚锁定与选中，避免照抄潜在越过锁定的行为。
- `TreasurePanel.Show` 用 List.Capacity 遍历而非 Count；需要后续接入以实际返回奖励数量为准。艺术资源可准备1–5槽，不把异常越界当正常流程。
- `GameEndPanel.Show` 把 timeScale设0，而 DelayInteractable 使用 WaitForSeconds；按钮可操作时机待真实运行验证。美术设计应明确“展示完毕可确认”，不复刻潜在卡住状态。
- 存档失败当前主要记日志，尚无用户错误面板；读写失败图属于本次建议补充。

以上是设计取证与待接入事项，不在本阶段修改参考代码。

## 已查看媒体与来源边界

已实际查看 `Media/CharacterSelect.png`、`LevelSelect.png`、`PowerUp.png`、`Setting.png`、`SkillUpgrede.png`、`Fight.png`。其黑红哥特边框、像素角色与英文文案只作为功能和布局资料；最终道家Q版画法必须使用F盘两张指定主参考，不能复制源游戏皮肤。原媒体尺寸和SHA见机器记录。本阶段没有对这六张截图做AI编辑或将其当成正式新美术。
