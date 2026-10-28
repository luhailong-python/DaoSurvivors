# 全游戏 UI 美术参考扩充核查

核实日期：2026-10-26。当前制作目录为 `E:\work\image\DaoSurvivors`，美术参考仓库为 `F:\work\image`。本阶段仅交付图片、UI设计与美术资源；不编写C#、Prefab或场景，不做Git提交。原 `Assets/` 中的早期实现与旧图冻结，不作为本轮全游戏美术验收。

[Roo-Roo-Roo/survivors-roguelike-kit](https://github.com/Roo-Roo-Roo/survivors-roguelike-kit) 是功能与流程参考，现存只读副本位于 `.reference/survivors-roguelike-kit/`；它不是成果保存远端。成果GitHub待用户补充。F参考仓库当前核实远端为 `https://luyuacpp.visualstudio.com/image/_git/image`，GitHub地址待确认。

## 实读文档与当前采用依据

已重新读取F根README的接手说明、`docs/WUXING_QITAN_HANDOFF.md`、`docs/QDAO_ART_DIRECTION.md`及工具/图像策略相关说明；按根规则使用邮件与组队两张实际主参考。`qdao_ui_redesign_v5/UI_SPEC.md`仍缺失，未从旧Git恢复。

- `designs/gameplay-ui/README.md`确认背包、任务、活动、帮会四张1931×814静态稿；`fidelity-20261016/README.md`、`exact-20261017/HANDOFF.md`、`exact-20261021/README.md`、`exact-20261022/README.md`区分原稿、切片、状态和在制/验收边界。后两轮主要修标题、圆勾和活跃空槽，不代表宝箱/货币已成为高清透明单件。
- `designs/equipment-ui-20261008/README.md`、逐图来源与sprite清单确认600方灵剑/靴子是母图裁切缩放导出；`equipment-ui-20261009/README.md`、`exact-20261021/install-manifest.json`及`connected-validation/summary.json`说明后续详情卡和字段更新。旧项目离线编译/许可状态不作为本项目接入证据。
- `designs/class-skills-20260928/DESIGN.md`、`icons-style-20261021/README.md`和manifest确认32枚技能图已按两张主参考重绘；1208于10月22日提高护心玉对比。**32张当前正式图全部是1254×1254 RGB**，不能冒称透明独立图标。README引用的`qa/overview-160.png`当前缺失，本次改为实际逐图查看选用候选，未恢复旧总览。
- `designs/attribute-panels/README.md`、`v2-painted/unity-slices/README.md`和manifest确认无字v10框板及边距；`exact-identity-20261022/README.md`只是后期身份文本接线说明，不改本次图像风格合同。
- `designs/battle-patrol-jewelry-ui-20261021/README.md`与`designs/ui-completion-20261021/README.md`确认战斗与商城已批准静态稿。图中的姓名、价格、次数、属性值和“五行奇谈”业务均不移植。

实际查看了战斗信息、人物属性、技能三栏布局、背包、商城和活动宝箱六类成图；路径、尺寸及SHA见[扩充来源清单](art-extension-sources.json)。技能布局截图为历史排布依据，当前图标画法以逐张1254新版PNG为准。

## 候选图标16项：透明与整张卡图分开

下表路径均相对F参考仓库；逐项SHA、真实Alpha、源记录和选择状态保存在`art-extension-sources.json`。本轮没有为了凑数量复制不合用图。

| 编号 | 当前真实源路径 | 实测尺寸／透明度 | 可承担的美术语义 | 结论 |
|---|---|---|---|---|
| C01 | `designs/equipment-ui-20261008/sprites/icon_sword.png` | 600×600 / 真Alpha [0, 255] | Might伤害、法器/自动追踪剑的造型参考 | 已有干净art副本 |
| C02 | `designs/equipment-ui-20261008/sprites/icon_boots.png` | 600×600 / 真Alpha [0, 255] | MoveSpeed移动速度 | 已有干净art副本 |
| C03 | `designs/guild-ui-v2/assets/icon-pill.png` | 600×600 / 真Alpha [0, 255] | 仅供吸灵葫芦/恢复容器造型参考；不能称为已画好的丹药 | 边缘待修，不采用 |
| C04 | `designs/guild-ui-v2/assets/icon-scroll.png` | 600×600 / 真Alpha [0, 255] | Growth经验/悟道造型参考 | 边缘待修，不采用 |
| C05 | `designs/guild-ui-v2/assets/icon-talisman.png` | 600×600 / 真Alpha [0, 255] | 道符主动法器造型参考 | 边缘待修，不采用 |
| C06 | `designs/class-skills-20260928/icons/1102.png` | 1254×1254 / RGB，无Alpha | 横扫攻击图面；不冒充9种主动全部共享此图 | 候选，未复制 |
| C07 | `designs/class-skills-20260928/icons/1106.png` | 1254×1254 / RGB，无Alpha | Armor护甲 | 候选，未复制 |
| C08 | `designs/class-skills-20260928/icons/1107.png` | 1254×1254 / RGB，无Alpha | Might伤害 | 候选，未复制 |
| C09 | `designs/class-skills-20260928/icons/1108.png` | 1254×1254 / RGB，无Alpha | HPMax气血上限 | 候选，未复制 |
| C10 | `designs/class-skills-20260928/icons/1202.png` | 1254×1254 / RGB，无Alpha | Area范围/雷系群攻图面 | 候选，未复制 |
| C11 | `designs/class-skills-20260928/icons/1203.png` | 1254×1254 / RGB，无Alpha | Freezing冻结状态 | 候选，未复制 |
| C12 | `designs/class-skills-20260928/icons/1205.png` | 1254×1254 / RGB，无Alpha | Amount数量/范围进化的多目标图面，不能当作四向精确示意 | 候选，未复制 |
| C13 | `designs/class-skills-20260928/icons/1401.png` | 1254×1254 / RGB，无Alpha | SkillSpeed弹速/追踪剑图面 | 候选，未复制 |
| C14 | `designs/class-skills-20260928/icons/1404.png` | 1254×1254 / RGB，无Alpha | Slow减速状态 | 候选，未复制 |
| C15 | `qdao_ui_redesign_v5/components/png/round_badge_flame.png` | 120×120 / 真Alpha [0, 255] | Burn灼烧小状态标记 | 仅小状态尺寸 |
| C16 | `qdao_ui_redesign_v5/components/png/round_badge_taiji.png` | 120×120 / 真Alpha [0, 255] | 进化/归一通用标识，不能代表9种具体进化技能 | 已有干净art副本 |

C03虽名为`icon-pill`，画面实际为金色葫芦，不能写成丹药。C03–C05存在少量洋红残边，且其历史源目录与旧124图标合同已缺失；当前副本仍可解码，但本轮不把它们算作最终干净成品。C15/C16只有120方，只适合小标记。RGB技能图可以整张放入浅绢卡片，不能把RGB转换为RGBA后声称获得真透明。

已排除的误用：`designs/guild-ui-v2/assets/icon-chest.png`实际是120方亭阁徽章；邮件`mail_reward_coin.png`/`mail_reward_crystal.png`为116×98且Alpha全255；活动宝箱切片只有73×66且Alpha全255。它们不构成高清透明宝箱、金币或经验晶石资源。原生徽标提取目录`qdao_ui_style_recut_v10/artwork/`只余index，没有可直接用的原生符号PNG。

## 必须完整覆盖的20项属性／状态／掉落词汇

Roo的`SkillDataSO.cs`实读确认14种永久属性。以下是美术语义映射，不复制F旧技能的回合、数值或职业业务；属性缩写应与功能参考对应。缺专用透明图的条目由本轮新图补齐，最终采用以新图自身记录为准。

| 功能词汇 | 建议图形 | 现存来源核查 |
|---|---|---|
| Might 伤害 | 锋刃／飞剑 | C01干净600透明；C08的1254整牌也能表达锋刃 |
| Armor 护甲 | 玉质护心镜／圆盾 | C07为清晰1254 RGB整牌；暂无同品质透明独立盾 |
| HPMax 气血上限 | 生命心玉 | C09为1254 RGB整牌 |
| Recovery 回复 | 玉露丹／恢复葫芦 | C03只是葫芦徽章且边缘待修，不能当作已完成丹药 |
| Cooldown 冷却 | 沙漏／回转刻度 | 没有合格专用透明单件，不能借移动加速图冒充 |
| Area 范围 | 扩张法阵与边界 | C10雷阵整牌可参考，专用透明范围图需新制 |
| SkillSpeed 弹速 | 飞剑与流线 | C13整牌可参考 |
| Duration 持续 | 长明灯配时间环 | 没有合格专用透明单件 |
| Amount 数量 | 多枚分离飞剑／星符 | C12为五星图面；不要把五点画面标成四向 |
| MoveSpeed 移速 | 踏云靴 | C02干净600透明 |
| Magnet 拾取范围 | 聚灵葫芦与吸引粒子 | 现存葫芦没有吸引语义且边缘待修，需专用图 |
| Growth 经验增益 | 悟道经卷／灵芽 | C04可作造型参考，透明边缘待修 |
| Greed 金币增益 | 聚财铜钱与上升金光 | 现存货币切片小且不透明，需新制 |
| Curse 诅咒 | 紫黑咒印／封煞符 | 无合格专用透明图，不能借护盾或冰晶冒充 |
| Burn 灼烧 | 朱金火焰 | C15仅120小徽，高清状态图需新制 |
| Freezing 冻结 | 冰晶与冷雾 | C11为1254 RGB整牌 |
| Slow 减速 | 束足风环 | C14为1254 RGB整牌 |
| 金币／钱袋 | 铜钱、50金币兜底钱袋 | 现存透明高质版本缺失 |
| 经验晶石 | 蓝绿灵晶 | 现存邮件切片116×98且不透明 |
| 宝箱／进化奖励 | 真宝箱，普通/稀有/进化可区分 | 现存“icon-chest”是亭阁占位，需专门宝箱图 |

Roo实际为6主动+6被动槽、三选升级和钱袋兜底、1/3/5宝箱与进化流程。技能库有9种主动形态，不能因为槽位为6就只画6种全库图标；双向、弹跳、连锁、环形、环绕、四向、区域、随机、追踪应保持图形辨识。新透明图集负责补齐，不复制上述旧回合制技能的规则。

## 已复制的控件状态与边距

13件真实现存状态资源已复制至`art/common/states/`，均与批准源SHA一致；九宫格、画布、Alpha及来源见清单。

| 组 | 画布 | 已有状态／文件 | 原始边距 |
|---|---|---|---|
| primary_button | 460×112 | normal / selected / disabled | L/T/R/B = 82/30/82/34，仅按合同横向伸缩 |
| tab | 360×114 | normal / selected / disabled | L/T/R/B = 82/30/82/34 |
| list_row | 360×96 | normal / selected / disabled | L/T/R/B = 82/27/82/31 |
| checkbox | 98×98 | checkbox_off / checkbox_on | 整体等比，无九宫格 |
| 状态叠层 | 48×48 | check / lock | 整体等比，不是整按钮状态 |

selected已含勾，disabled已含锁；没有独立pressed、hover、focus或同画布locked原图。本轮不把selected改名pressed，也不把48锁放大冒充完整锁定按钮。

## 已替换的干净主框与标题

全尺寸复查发现早期Team主框有矩形纸面拼接边，标题牌有拉伸填块及残留队伍数；经root批准，仅替换新艺术目录的两件，旧`Assets/`不动。

- `art/common/main_frame.png`：来自`designs/attribute-panels/v2-painted/unity-slices/png/window_frame.png`，1546×743真实透明，无字；**L/B/R/T = 97/74/97/99**。
- `art/common/title_plate.png`：来自同目录`title_plate.png`，655×110真实透明，无字；**L/B/R/T = 0/0/0/0，整牌等比，不做九宫格**。

替换前后SHA和原manifest完整条目见`commonReplacements`。这次是现存批准资源复制，不是新AI生成或原生细节提升。本阶段目录按`art/common`、`art/characters`、`art/icons`、`art/illustrations`、`art/fonts`组织；所有导出、参考和源记录留在本项目。2026-10-26 按用户要求，将此前误写在 F 盘 README 中的8段关联迁回[本项目素材关联记录](image-reference-associations.md)，F 盘原有素材说明保留。
