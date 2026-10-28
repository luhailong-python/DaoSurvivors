# UI 功能与资源总清单

2026-10-28，UI 子集已完成美术验收：52 张整屏／状态／流程画面，52 份文字与图层映射。不是52种独立游戏系统，也不代表整款游戏非UI素材已全部完成。

功能参考固定版本 `3f905381d73a34b516030528b8ef6743868b9e52`。已有功能、展示状态补齐与建议补充分别标明；Unity接入待下一阶段。

| ID | 系统 | 界面／状态 | 依据 | 制作／验收 | 整屏 |
| --- | --- | --- | --- | --- | --- |
| 01-startup | 启动与加载 | 启动画面 · 初次进入 | supporting_state | 完成／UI美术通过 | [01-startup](../../designs/ui-suite/screens/01-startup.png) |
| 02-loading | 启动与加载 | 进入秘境 · 加载中 | existing | 完成／UI美术通过 | [02-loading](../../designs/ui-suite/screens/02-loading.png) |
| 03-loading-error | 启动与加载 | 加载异常 · 读取失败 | suggested | 完成／UI美术通过 | [03-loading-error](../../designs/ui-suite/screens/03-loading-error.png) |
| 04-main-menu | 山门与导航 | 山门主界面 · 默认 | existing | 完成／UI美术通过 | [04-main-menu](../../designs/ui-suite/screens/04-main-menu.png) |
| 05-character-select | 角色选择与解锁 | 选择道友 · 首名可用／两名未解锁 | existing | 完成／UI美术通过 | [05-character-select](../../designs/ui-suite/screens/05-character-select.png) |
| 06-character-owned | 角色选择与解锁 | 选择道友 · 全角色已解锁／选中剑修 | existing | 完成／UI美术通过 | [06-character-owned](../../designs/ui-suite/screens/06-character-owned.png) |
| 07-character-detail | 角色选择与解锁 | 道友详情 · 起始道法与说明 | suggested | 完成／UI美术通过 | [07-character-detail](../../designs/ui-suite/screens/07-character-detail.png) |
| 08-unlock-confirm | 角色选择与解锁 | 结缘道友 · 500 金币确认 | suggested | 完成／UI美术通过 | [08-unlock-confirm](../../designs/ui-suite/screens/08-unlock-confirm.png) |
| 09-unlock-insufficient | 角色选择与解锁 | 结缘道友 · 金币不足 | supporting_state | 完成／UI美术通过 | [09-unlock-insufficient](../../designs/ui-suite/screens/09-unlock-insufficient.png) |
| 10-unlock-success | 角色选择与解锁 | 结缘道友 · 已解锁 | supporting_state | 完成／UI美术通过 | [10-unlock-success](../../designs/ui-suite/screens/10-unlock-success.png) |
| 11-character-empty | 角色选择与解锁 | 选择道友 · 配置为空 | suggested | 完成／UI美术通过 | [11-character-empty](../../designs/ui-suite/screens/11-character-empty.png) |
| 12-level-select | 秘境选择 | 选择秘境 · 两关列表／第一关已选 | existing | 完成／UI美术通过 | [12-level-select](../../designs/ui-suite/screens/12-level-select.png) |
| 13-level-detail | 秘境选择 | 秘境详情 · 第二关说明 | supporting_state | 完成／UI美术通过 | [13-level-detail](../../designs/ui-suite/screens/13-level-detail.png) |
| 14-level-unselected | 秘境选择 | 选择秘境 · 尚未选择 | suggested | 完成／UI美术通过 | [14-level-unselected](../../designs/ui-suite/screens/14-level-unselected.png) |
| 15-level-empty | 秘境选择 | 选择秘境 · 无关卡配置 | suggested | 完成／UI美术通过 | [15-level-empty](../../designs/ui-suite/screens/15-level-empty.png) |
| 16-powerup-overview | 永久成长 | 温养根基 · 14项属性总览 | existing | 完成／UI美术通过 | [16-powerup-overview](../../designs/ui-suite/screens/16-powerup-overview.png) |
| 17-powerup-detail | 永久成长 | 温养根基 · 已选属性／可购买 | existing | 完成／UI美术通过 | [17-powerup-detail](../../designs/ui-suite/screens/17-powerup-detail.png) |
| 18-powerup-insufficient | 永久成长 | 温养根基 · 金币不足 | existing | 完成／UI美术通过 | [18-powerup-insufficient](../../designs/ui-suite/screens/18-powerup-insufficient.png) |
| 19-powerup-maxed | 永久成长 | 温养根基 · 已达各自最高阶 | existing | 完成／UI美术通过 | [19-powerup-maxed](../../designs/ui-suite/screens/19-powerup-maxed.png) |
| 20-powerup-success | 永久成长 | 温养根基 · 已购买／阶数更新 | existing | 完成／UI美术通过 | [20-powerup-success](../../designs/ui-suite/screens/20-powerup-success.png) |
| 21-settings-audio | 设置 | 清心小筑 · 总音量／音乐／音效 | existing | 完成／UI美术通过 | [21-settings-audio](../../designs/ui-suite/screens/21-settings-audio.png) |
| 22-settings-display | 设置 | 清心小筑 · 分辨率／全屏／伤害浮字 | existing | 完成／UI美术通过 | [22-settings-display](../../designs/ui-suite/screens/22-settings-display.png) |
| 23-settings-language | 设置 | 清心小筑 · 语言选择 | existing | 完成／UI美术通过 | [23-settings-language](../../designs/ui-suite/screens/23-settings-language.png) |
| 24-display-confirm | 设置 | 画面设置确认 · 保留或还原 | suggested | 完成／UI美术通过 | [24-display-confirm](../../designs/ui-suite/screens/24-display-confirm.png) |
| 25-battle-hud | 核心战斗 | 战斗 HUD · 常规战斗／空技能槽 | existing | 完成／UI美术通过 | [25-battle-hud](../../designs/ui-suite/screens/25-battle-hud.png) |
| 26-battle-build-full | 核心战斗 | 战斗 HUD · 6主动＋6被动满槽 | existing | 完成／UI美术通过 | [26-battle-build-full](../../designs/ui-suite/screens/26-battle-build-full.png) |
| 27-battle-buffs | 核心战斗 | 战斗 HUD · 燃烧／冰冻／减速状态 | existing | 完成／UI美术通过 | [27-battle-buffs](../../designs/ui-suite/screens/27-battle-buffs.png) |
| 28-boss-arrival | 核心战斗 | 战斗 HUD · 末波首领预警 | suggested | 完成／UI美术通过 | [28-boss-arrival](../../designs/ui-suite/screens/28-boss-arrival.png) |
| 29-upgrade-new | 局内升级 | 灵光乍现 · 新主动／新被动三选一 | existing | 完成／UI美术通过 | [29-upgrade-new](../../designs/ui-suite/screens/29-upgrade-new.png) |
| 30-upgrade-existing | 局内升级 | 灵光乍现 · 持有道法升级 | existing | 完成／UI美术通过 | [30-upgrade-existing](../../designs/ui-suite/screens/30-upgrade-existing.png) |
| 31-upgrade-moneybag | 局内升级 | 灵光乍现 · 技能满级后金币补位 | existing | 完成／UI美术通过 | [31-upgrade-moneybag](../../designs/ui-suite/screens/31-upgrade-moneybag.png) |
| 32-treasure-one | 宝箱与进化 | 机缘宝匣 · 单件奖励／揭晓中 | existing | 完成／UI美术通过 | [32-treasure-one](../../designs/ui-suite/screens/32-treasure-one.png) |
| 33-treasure-three | 宝箱与进化 | 机缘宝匣 · 三件奖励／揭晓中 | existing | 完成／UI美术通过 | [33-treasure-three](../../designs/ui-suite/screens/33-treasure-three.png) |
| 34-treasure-five | 宝箱与进化 | 机缘宝匣 · 五件奖励／可领取 | existing | 完成／UI美术通过 | [34-treasure-five](../../designs/ui-suite/screens/34-treasure-five.png) |
| 35-treasure-evolution | 宝箱与进化 | 机缘宝匣 · 满足条件／法器进化 | existing | 完成／UI美术通过 | [35-treasure-evolution](../../designs/ui-suite/screens/35-treasure-evolution.png) |
| 36-treasure-moneybag | 宝箱与进化 | 机缘宝匣 · 无可升级技能／金币替代 | existing | 完成／UI美术通过 | [36-treasure-moneybag](../../designs/ui-suite/screens/36-treasure-moneybag.png) |
| 37-pause | 暂停与退出 | 稍作调息 · 暂停 | suggested | 完成／UI美术通过 | [37-pause](../../designs/ui-suite/screens/37-pause.png) |
| 38-abandon-confirm | 暂停与退出 | 结束历练确认 · 取消／返回山门 | suggested | 完成／UI美术通过 | [38-abandon-confirm](../../designs/ui-suite/screens/38-abandon-confirm.png) |
| 39-exit-confirm | 暂停与退出 | 离开游戏确认 · 确认／取消 | suggested | 完成／UI美术通过 | [39-exit-confirm](../../designs/ui-suite/screens/39-exit-confirm.png) |
| 40-victory | 历练结算 | 此境已平 · 所有波次清空／胜利 | existing | 完成／UI美术通过 | [40-victory](../../designs/ui-suite/screens/40-victory.png) |
| 41-defeat | 历练结算 | 道途未尽 · 气血耗尽／失败 | existing | 完成／UI美术通过 | [41-defeat](../../designs/ui-suite/screens/41-defeat.png) |
| 42-save-pending | 本地存档与反馈 | 本地保存提示 · 保存中／避免重复领取 | suggested | 完成／UI美术通过 | [42-save-pending](../../designs/ui-suite/screens/42-save-pending.png) |
| 43-save-error | 本地存档与反馈 | 本地保存异常 · 重试／保留当前界面 | suggested | 完成／UI美术通过 | [43-save-error](../../designs/ui-suite/screens/43-save-error.png) |
| 44-guide-controls | 帮助与引导 | 入山指引 · 移动与自动施法 | suggested | 完成／UI美术通过 | [44-guide-controls](../../designs/ui-suite/screens/44-guide-controls.png) |
| 45-guide-growth | 帮助与引导 | 悟道指引 · 升级／满槽／宝箱 | suggested | 完成／UI美术通过 | [45-guide-growth](../../designs/ui-suite/screens/45-guide-growth.png) |
| 46-skill-codex | 道法资料 | 道法总览 · 九主动／属性说明 | suggested | 完成／UI美术通过 | [46-skill-codex](../../designs/ui-suite/screens/46-skill-codex.png) |
| 47-evolution-locked | 道法资料 | 法器化境 · 条件未满足 | suggested | 完成／UI美术通过 | [47-evolution-locked](../../designs/ui-suite/screens/47-evolution-locked.png) |
| 48-evolution-ready | 道法资料 | 法器化境 · 条件已满足／待宝箱触发 | suggested | 完成／UI美术通过 | [48-evolution-ready](../../designs/ui-suite/screens/48-evolution-ready.png) |
| 49-character-stats | 道法资料 | 道友属性 · 局内与永久成长分区 | suggested | 完成／UI美术通过 | [49-character-stats](../../designs/ui-suite/screens/49-character-stats.png) |
| 50-notice-states | 通用控件 | 消息反馈 · 成功／不足／异常／空态 | supporting_state | 完成／UI美术通过 | [50-notice-states](../../designs/ui-suite/screens/50-notice-states.png) |
| 51-control-states | 通用控件 | 统一控件 · 普通／按下／选中／禁用／锁定 | supporting_state | 完成／UI美术通过 | [51-control-states](../../designs/ui-suite/screens/51-control-states.png) |
| 52-flow-map | 流程说明 | 整套界面关系 · 入口与返回路径 | supporting_state | 完成／UI美术通过 | [52-flow-map](../../designs/ui-suite/screens/52-flow-map.png) |

existing=参考已有功能；supporting_state=已有功能的展示状态补齐；suggested=明确标注的美术建议。

## 不适用／未发现的系统

- **更新器／在线公告／登录／选服／创建账号角色**：单机模板，未发现在线账号、补丁或区服系统；启动与3名预设角色选择已覆盖。
- **背包／仓库／物品整理／使用数量**：源为即时拾取和道法槽，未发现持有物品库存；以拾取和宝箱语义表达。
- **装备穿戴／强化／打造／交易**：Armor是被动属性，不是穿戴装备；永久成长与道法进化已覆盖。
- **任务／活动／签到／成就／排行榜**：未发现对应数据或业务入口；波次进度及胜败目标已覆盖，不机械增设运营功能。
- **好友／聊天／邮件／组队／帮会／宠物／坐骑**：未见游戏内对应业务，F风格图不能作为功能需求；狐图只作美术展示。
- **一般物品商店／出售／兑换／抽卡**：经济入口仅角色解锁与PowerUp购买；未见其他商城逻辑。
- **重抽／跳过／禁用道法／复活**：未发现reroll/skip/banish/revive实现，不画成已支持操作。

每屏独立资源与参考依据见同名JSON；字号、文案、颜色、文字区域与图层见 `designs/ui-suite/layouts/`。

[最终UI美术验收](ACCEPTANCE.md)、[视觉与语义记录](final-visual-review.json)、[156次视口检查](render-verification.json)、[Unity导入建议](UNITY_ART_IMPORT.md)。
