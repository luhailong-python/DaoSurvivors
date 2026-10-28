# 正式美术资源与 Unity 导入建议

本说明覆盖当前 `art/` 下的独立资源。整款游戏的角色动画、敌人、场景和技能特效范围另按全游戏美术审计持续补齐；本清单不把六张静态人物图称为完整角色动画。本阶段只交付美术，以下 Unity 设置尚未在编辑器中实际验证。

机器清单为 [`art/manifest.json`](../art/manifest.json)。每项包含文件尺寸、文件字节数、SHA-256、真实 Alpha、来源记录、操作类型、界面使用位置、Pivot 和 Border。界面布局及文字使用 [`UI_COVERAGE.json`](ui-suite/UI_COVERAGE.json) 和各屏 `designs/ui-suite/layouts/*.json`。

## 当前目录

| 目录 | 用途 | 使用规则 |
|---|---|---|
| `art/common/` | 9 张共用窗框、标题牌、卡片、按钮和头像框 | 按下方各自尺寸及 Border 使用 |
| `art/common/controls/` | 三族控件，各有普通、按下、选中、禁用、锁定五状态，共 15 张 | 后续 Unity 正式状态资源优先采用此目录 |
| `art/common/states/` | 13 张来源控件与勾选、锁、复选框 | 保留为控件制作依据；其中名称为 disabled 的旧控件带锁，不作为无锁禁用状态 |
| `art/characters/` | 3 个角色展示静态图、2 个敌人静态单帧、1 个九尾狐静态图 | UI 展示图；没有据此声称跑步、攻击或死亡动画完成 |
| `art/icons/` | 32 个本轮图集切出的图标及 3 个既有独立图标 | 独立透明 PNG，整张按比例显示 |
| `art/illustrations/` | 大厅主视觉与战斗 HUD 场景底图 | 原生 1672×941，RGB；不是可碰撞地图或无缝地形合同 |
| `art/sheets/` | 两张原生模型图集、浅色及深色审图合成图 | 生产来源与检查用；运行时直接使用 `art/icons/` 独立切片 |
| `art/fonts/` | Noto Sans CJK SC Regular 与 OFL 授权 | 字体未改字形；保留授权文本 |

当前初始快照共 88 个资源文件：86 张图片、1 个 OTF、1 份授权；其中 80 张图片有真实透明像素。该数字对应清单生成时点，之后扩展资源以机器清单重建结果为准。JSON 侧车和清单不是美术图片，不计入这 88 项。

## 九宫格与固定图形

以下顺序严格采用 Unity Border 的 **Left、Bottom、Right、Top**，单位为当前 PNG 像素。不能把源文档的 Left、Top、Right、Bottom 直接照抄到 Unity 输入顺序。

| 资源 | 画布 | Border L/B/R/T | 建议 |
|---|---:|---:|---|
| `common/main_frame.png` | 1546×743 | 97 / 74 / 97 / 99 | Sliced，来自干净的 Attribute V10 窗框 |
| `common/title_plate.png` | 655×110 | 0 / 0 / 0 / 0 | Simple，整张等比，禁止九宫格拉伸 |
| `common/section_plate.png` | 433×72 | 76 / 16 / 72 / 21 | Sliced |
| `common/member_row.png` | 851×97 | 24 / 19 / 24 / 19 | Sliced |
| `common/application_card.png` | 631×198 | 27 / 24 / 27 / 24 | Sliced |
| `common/button_primary.png` | 225×66 | 45 / 16 / 45 / 16 | 既有小尺寸 Sliced；不能把本参数用于 460×112 五状态按钮 |
| `common/button_secondary.png` | 220×66 | 45 / 16 / 45 / 16 | Sliced |
| `common/close.png` | 82×82 | 全 0 | Simple，圆形整张等比 |
| `common/portrait_frame.png` | 91×91 | 全 0 | Simple，圆环整张等比 |
| `controls/primary_button_*.png` | 460×112 | 82 / 34 / 82 / 30 | 横向拉伸；源合同最小 204×112 |
| `controls/tab_*.png` | 360×114 | 82 / 34 / 82 / 30 | 横向拉伸；源合同最小 204×114 |
| `controls/list_row_*.png` | 360×96 | 82 / 31 / 82 / 27 | 横向拉伸；源合同最小 204×96 |

正式三族控件各状态画布相同，中心 Pivot 均为 `(0.5, 0.5)`，没有位移或状态间缩放。普通与选中为原文件字节复制，锁定从带固定锁图形的来源状态明确改作锁定使用。按下由浏览器原生控件状态导出：`brightness(.82) saturate(.95)`；无锁禁用采用 `opacity:.48; grayscale(.7)`，Alpha 最大值为 122。这六张状态不是 AI 修图，也没有新增手绘细节。完整操作及校验见 [`control-state-derivations.json`](control-state-derivations.json)。

动态按钮文字、玩家名、标题、数量和业务文案均使用独立文字层。锁定状态中的锁、选中状态中的勾选为明确保留的固定图形。布局 JSON 记录文字内容、矩形、字体、字号、颜色及对齐；不得将整屏设计 PNG 当作最终可交互控件。

## 图标切片

两张模型图集原生均为 1254×1254。32 个正式图标均为 **原生局部裁切后加入透明留白的 512×512 PNG**，没有重采样、放大、Alpha 过滤或新的模型调用。512×512 是交付画布，不能视为模型逐图原生生成了 512×512 的细节。

原图没有严格服从 4×4 格线，整齐等分会截断或混入邻近图标。因此以逐行 Alpha 低谷确定互不重叠的归属矩形，保存所有来源 Alpha 像素各一次；逐图 `.derivation.json` 记录 `cropRectXYXY`、原生裁切大小、画布放置坐标和像素一致性。正式使用独立图标，不对原图执行等分切图。原图的格线 FAIL/WARN 没有被改写成通过，见两份切片记录及 UI 验收报告：

- [`icon-atlas1-slices.json`](icon-atlas1-slices.json)：14 项属性、灵石、经验。
- [`icon-atlas2-slices.json`](icon-atlas2-slices.json)：9 项主动技能、宝匣开合、钱袋、回复及 3 项敌人状态。

图标统一建议 Simple、Border 全 0、中心 Pivot；实际可见边界可从每项清单中的 Alpha Bounds 获取。原生裁切的细小半透明笔触保留，没有以程序重画或清除来冒充模型质量提升。

## 导入初始建议

独立 UI PNG 建议 `Texture Type = Sprite (2D and UI)`、`Sprite Mode = Single`、`Filter Mode = Bilinear`、`Wrap Mode = Clamp`、`sRGB = On`、`Generate Mip Maps = Off`。需要透明的资源启用 `Alpha Is Transparency`；两张 RGB 插画无需伪造透明。先用 `Compression = None` 对照成品核验，再在下一阶段按目标平台决定压缩。单图 Max Size 至少不小于原始长边，清单给出了对应的 2 次幂初始值，避免导入时自动降采样。

UI 参考分辨率为 1920×1080。Canvas Scaler、屏幕安全区、异形屏、SDF 字体图集大小、Sprite Atlas 打包、内存和目标平台压缩都属于后续 Unity 接入验证；网页设计预览的分辨率适配不代表这些设置已通过 Unity 验证。人物 UI 立绘目前使用中心 Pivot 的建议；运行时角色脚底注册和动画帧需按全游戏动画合同另行设置，不能从展示立绘推断。

Noto 字体初始可供 TextMeshPro 创建 SDF；中文动态字集和回退链、清晰度、Atlas 内存须在接入阶段验证。不得以本地商用系统字体替换已交付字体而不更新来源和许可记录。

## 来源与生成证据

功能参考、风格参考和成果远端分别管理。功能参考为 Survivors Roguelike Kit，固定提交在总清单记录；美术参考为 `F:\work\image`，已核实远端为 Azure DevOps image，不能称为本项目成果 GitHub。成果提交仓库仍待用户提供。

既有素材的原生生成、历史裁切和历史重构信息保留在 [`ASSET_SOURCES.json`](ASSET_SOURCES.json) 与 [`art-extension-sources.json`](art-extension-sources.json)。本项目的字节复制不被描述成新模型生成。引用的 44 份源合同/来源文字以原字节快照保存于 `docs/provenance/art-reference/`，其原路径与 SHA 位于 [`art-reference-index.json`](provenance/art-reference-index.json)；F 盘保持只读。

大厅与场景的逐图生成记录已复制到 `art/illustrations/*.png.generation.json`。记录保留最初生成时间、配置目标、实际参数、返回信息和图片 SHA；`originalRecordedFile` 标明旧工程记录的位置，原记录字节快照另存 `docs/provenance/original-records/`。这次移动没有重新生成图片。新图集记录位于 `art/sheets/*.png.generation.json`，原始请求回执和提示词在 `docs/production/`，不依赖被冻结的旧 Unity 工程。

内置入口未暴露具体模型及质量选择器，也未返回可确认的具体后端型号与质量；这些字段保持 `null`。`gpt-image-2.5-sunburst / max` 为配置目标，C2PA 中通用 `ChatGPT / gpt-image` 为读取到的标签，二者均不能充当实际型号或质量证明。

## 重建与扩展清单

在本项目明确工作目录执行：

```powershell
Set-Location -LiteralPath 'E:\work\image\DaoSurvivors'
python tools/build-art-manifest.py --no-reference-snapshots
```

该命令只重建本项目的 `art/manifest.json`，按当前图片实测尺寸、Alpha 与 SHA，读取逐图侧车和当前 UI 使用映射。初次保存源合同快照时可去掉 `--no-reference-snapshots`，以只读方式访问 F 并将其引用文字复制到本项目；不修改参考库、图片、Unity 文件或 Git 状态。

后续新增资源应同时写同名 `.generation.json` 或 `.derivation.json`，准确提供 `sha256`、来源和操作。没有证据的新增文件会列入 `warnings` 的 `pending_provenance`，不自动猜测生成方法。重建后检查 `warnings`，并以全游戏美术清单核对资源覆盖；单有文件数量不能证明整款美术已完成。
