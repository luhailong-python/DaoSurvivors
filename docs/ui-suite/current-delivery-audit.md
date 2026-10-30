# 一炁当千 · UI 当前交付核对

2026-10-29（America/New_York）。正式名称《一炁当千》与宣传短句“一人成阵，万妖退散”已同步至全部52屏。当前状态：**accepted_ui_art_branded**，新增问题0。

## 本次实际核对

- 52张1920×1080整屏、状态及流程图已按正式品牌重新导出，52份布局记录同步更新；52/52当前哈希与最新视觉验收及布局记录一致。
- 新52屏全部含正式名称及徽记／Logo映射，没有旧临时名称。启动页使用完整Logo，页眉和战斗页脚使用徽记加独立文字，图片保持等比Contain。
- 本批52次基准渲染、104次额外视口检查通过；脚本异常、缺图和文字出画布均为0。OpenType cmap核对全部中文等非空白字符，无缺字。
- 独立复核实际查看全部7张汇总，并以原尺寸查看01、04、05、25、40、51、52；制作复核另查看02加载页。未见品牌新增遮挡、控件挤压或中文问题。检查记录绑定当前52屏与7张汇总的哈希。
- 原88项UI资源、44份来源快照保持原字节，15张正式控件状态的画布、Pivot、Border及Alpha保持验收版本。新增8项正式品牌资源，当前UI子集回执为96文件，96/96哈希匹配。
- 当前全美术清单为330文件，含8项正式品牌与1项旧未采用Logo来源；旧Logo只作生产来源，不作为正式UI。

重跑核对：`python tools/audit-ui-delivery.py`。逐文件结果见 [current-delivery-audit.json](current-delivery-audit.json)。

## 验收版本与限制

当前画面使用新哈希验收。旧屏验收记录已保存到 [pre-brand历史索引](acceptance-history/pre-brand-20261029/snapshot-index.json)，不把授权重渲产生的哈希变化当作资源缺口。原88项来源回执继续保留；品牌后的96项回执单独记录。

原始两张图标图集的等格切片QC失败／警告仍保留在 [ACCEPTANCE.md](ACCEPTANCE.md)。正式图标使用已验收的Alpha归属切片，原生细微Alpha散点仍保留，512×512补透明画布不代表新增原生细节。未披露的实际图像型号与质量仍为未确认。

本次只修改UI合成排版、文字、资源引用和验收记录，没有重新生成或改动角色、怪物、世界等原图。浏览器状态预览不构成游戏逻辑或Unity运行；Unity导入、九宫格、字体图集、交互和设备渲染仍留待下一阶段。

## 交付索引

- [品牌后52屏图库](../../designs/ui-suite/gallery.html) · [状态预览](../../designs/ui-suite/preview/index.html) · [屏幕目录](../../designs/ui-suite/screens/) · [布局与文字区域](../../designs/ui-suite/layouts/)
- [UI覆盖](UI_COVERAGE.md) · [UI验收](ACCEPTANCE.md) · [最新逐屏记录](final-visual-review.json) · [独立品牌视觉核验](brand-visual-independent-review.json)
- [96项品牌后UI资源回执](accepted-ui-branded-resource-receipt.json) · [原88项资源回执](accepted-ui-resource-receipt.json) · [当前全美术清单](../../art/manifest.json)
- [品牌合同](../branding/BRAND.json) · [Unity导入建议](UNITY_ART_IMPORT.md) · [来源关联](../image-reference-associations.md)

本记录只验收UI子集；整款游戏美术与角色动作的统一结论见整款验收总账。
