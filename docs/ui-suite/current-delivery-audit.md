# UI 已验收批次的当前磁盘核对

2026-10-28（America/New_York）。沿用当前项目 `E:\work\image\DaoSurvivors`；本次不改原图、不重新生图、不操作 Git。

当前结论：**UI 批次保留验收，未发现需要返修的新增问题。** 本记录不代表整款非 UI 美术、角色动作或 Unity 接入验收。

## 本次实际核对

- 52 张整屏 PNG 全部存在，均为 1920×1080；52/52 SHA-256 与 `final-visual-review.json` 及对应布局记录一致。
- 52 份布局与覆盖清单中的独立资源集合一致；没有缺图、清单外资源、已记录的破损图层或文字出画布。
- [UI 原批次资源回执](accepted-ui-resource-receipt.json) 所列 88 文件全部存在、哈希一致；其中 68 个独立资源、13 个控件来源支持、1 个授权文件、4 张审查底图、2 张生产源图集。此回执从扩充整款清单前的 `art/manifest.json` 提取，保存原清单哈希；当前 `art/manifest.json` 可继续收录非 UI 资源。此处仅验收 UI 子集。
- 15 张正式控件状态 PNG 覆盖主按钮、页签、列表行各五态；各组画布、Pivot 与 Border 一致。原画尺寸与 Alpha 和已验收清单一致。
- 每项资源指定的来源记录均存在；44 份本地美术来源文本快照哈希一致。Noto 字体及 OFL 授权文件存在且哈希一致。
- 五个浏览器预览源文件哈希与已验收记录一致。本次查看全部七张现有汇总图，确认框板风格、状态层级与控件排布没有新增可见问题。未重新导出画面，也未重复原尺寸逐屏与响应式运行测试。

可复现命令：`python tools/audit-ui-delivery.py`。逐文件结果见 [current-delivery-audit.json](current-delivery-audit.json)。

## 必须保留的交付说明

原始两张图标图集的等格切片 QC 失败／警告仍然有效，具体值保留在 [ACCEPTANCE.md](ACCEPTANCE.md)。正式图标使用已验收的 Alpha 归属切片；不得把原图改称等格切片通过。原生细微 Alpha 散点仍保留，512×512 为补透明画布，不是新增原生细节。

内置生图入口未披露的实际型号和质量继续标为未确认。现有整屏是浏览器 DOM/CSS、PNG 与独立文字的设计合成图。Unity 导入、九宫格、字体图集、业务交互、设备渲染均留待下一阶段；没有以此批次的静态战斗人物推断动作验收。

## 交付索引

- [52 张整屏](../../designs/ui-suite/screens/) · [对应布局与文字区域](../../designs/ui-suite/layouts/) · [预览入口](../../designs/ui-suite/preview/index.html)
- [UI 功能覆盖](UI_COVERAGE.md) · [原批次验收及限制](ACCEPTANCE.md) · [逐屏视觉验收](final-visual-review.json)
- [当前全美术清单](../../art/manifest.json) · [UI 原批次资源回执](accepted-ui-resource-receipt.json) · [Unity 导入建议](UNITY_ART_IMPORT.md) · [来源关联](../image-reference-associations.md)

全套交付应另附最新非 UI 生产清单及角色实际动作验收；冻结的早期 `Assets/` 样稿不属于本批正式美术。
