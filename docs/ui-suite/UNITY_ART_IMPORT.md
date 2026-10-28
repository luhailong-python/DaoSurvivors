# Unity 美术资源导入建议

2026-10-28。此文档服务于本次**图片与 UI 美术交付**，不是 Unity 导入、Prefab、场景或运行验证回执。本阶段不新建 Unity 接入代码，不执行业务联调。既有 `Assets/`、`Packages/`、`ProjectSettings/` 是此前阶段的冻结样稿，**不在当前美术交付包内**；不能拿其中的示例规则替代本次功能参考。

## 三类仓库与本地目录

| 类型 | 位置／地址 | 用途与边界 |
| --- | --- | --- |
| 功能参考 | `.reference/survivors-roguelike-kit`；`https://github.com/Roo-Roo-Roo/survivors-roguelike-kit`；固定提交 `3f905381d73a34b516030528b8ef6743868b9e52` | 只研究系统、布局、配置与流程；不向其提交，不整体纳入成果包 |
| 美术参考 | `F:\work\image`；实际远端 `https://luyuacpp.visualstudio.com/image/_git/image` | 道家Q版风格和明确复用的素材来源；现已只读；关联记录集中于本项目 docs/image-reference-associations.md，不随成果提交 |
| 本次成果 | `E:\work\image\DaoSurvivors`；成果 GitHub 地址待用户提供 | 当前只本地制作、验收与交付，未绑定成果远端，不提交、推送或发布 |

同一对话继续使用当前目录。`道途幸存者`为临时名称，中文道法名为本次道家化设计；参考游戏的内部字段和数量关系保留在 `UI_COVERAGE.json`。

## 交付入口

- `art/common/`：通用窗框、标题牌、卡片、行框、按钮、关闭与圆头像框。
- `art/common/states/`：明确拆出的选中、禁用、普通等控件状态以及勾选和锁定标记。
- `art/common/controls/`：统一画布的普通、按下、选中、禁用与锁定控件组；与 `states/` 的来源切片分别追溯，不混用不同画布。
- `art/characters/`：人物、妖灵和展示用灵狐的独立透明PNG；静态图不当作完整动作动画。
- `art/icons/`：主动道法、永久成长/被动属性、货币、奖励及状态图标；所属字段与使用位置随最终资源映射交付。
- `art/illustrations/`：大厅与战斗场景等无动态文字底图。
- `art/fonts/`：Noto Sans SC 字体与随包 OFL 授权。
- `designs/ui-suite/screens/`、`designs/ui-suite/layouts/`：整屏效果与对应布局/文字区域记录；整屏PNG不切成一张整体可拉伸窗口。
- `docs/ui-suite/UI_COVERAGE.json`：完整界面/状态、来源、资源使用位置、制作验收状态的总账；制作中条目不能视为完成。
- `art/manifest.json`：本次正式资源清单与最终导入映射入口；文件中的尺寸、状态组、Border 和来源记录为后续接入依据，均须在Unity中验证。
- `docs/ASSET_SOURCES.json`、`docs/art-extension-sources.json`及每张新图的生成记录：历史复制、模型生成、裁切、缩放分别追溯。新 `art/` 资源的最终清单保留到原始记录的映射，不能仅因目录迁移重写实际模型字段。

## 分辨率、坐标与文字

参考画布为 **1920×1080横屏**。建议后续使用 Canvas Scaler 的 Scale With Screen Size，以相同参考分辨率布置；具体 Match/Expand 策略需接入阶段按页面截图验证，不在美术阶段声称已通过引擎适配。

1280×720按比例缩放；2560×1080的核心交互保持居中16:9安全区，背景可延展或等比cover。人物、圆徽章、法器、文字不得非等比拉伸。截图导出1920像素不表示底图获得同等原生细节；实际原生尺寸以图像记录为准。

布局记录的原点为左上角，单位为参考画布像素。后续转 RectTransform 时可使用顶部锚点与 `anchoredPosition=(x,-y)`，宽高按记录；若采用中心坐标须显式转换，不凭截图目测重排。重要操作留在安全区域，遮挡区和可滚动区分别映射。

动态标题、名称、数量、金币、关卡描述、等级与业务效果使用独立文本组件。字号、颜色、行高、对齐、换行和区域尺寸跟随每屏布局记录；Noto中文须在接入时检查字形、基线、两行长标题和低分辨率可读性。无需将文本随窗框九宫格缩放。美术预览文字渲染不构成 TMP 字体图集和引擎字形验证。

## 建议导入设置

以下是建议值，最终须在Unity中验证：

| 资源 | Texture Type／Sprite Mode | Alpha／sRGB | 建议 Pivot | Filter／Mip Maps | 拉伸规则 |
| --- | --- | --- | --- | --- | --- |
| 通用框板、按钮、页签 | Sprite (2D and UI)／Single | PNG真实Alpha；sRGB开启 | `(0.5,0.5)`；布局另定锚点 | Bilinear／关闭 | 有明确Border才用Sliced |
| 圆头像框、关闭钮、锁/勾 | Sprite (2D and UI)／Single | 真实Alpha；sRGB开启 | `(0.5,0.5)` | Bilinear／关闭 | Simple、等比，不九宫格 |
| 独立道法/属性/货币图标 | Sprite (2D and UI)／Single | 真实Alpha；sRGB开启 | `(0.5,0.5)` | Bilinear／关闭 | 同一逻辑槽用统一显示框，等比留白 |
| 人物与妖灵 | Sprite (2D and UI)／Single | 真实Alpha；sRGB开启 | UI展示建议`(0.5,0.5)`；脚底Pivot另需真实脚点映射 | Bilinear／关闭 | 保持整图比例，不重裁到脸导致身份丢失 |
| 大幅场景/大厅插画 | 按容器选Sprite Single或Default Texture；不混用同一路径配置 | RGB背景无需伪造透明；sRGB开启 | 居中 | Bilinear／常规UI关闭 | 等比Contain/Cover，避免宽高独立缩放 |

建议先用无压缩验证边缘，再按目标设备评估平台压缩。Max Size不得小于需保留的实际长边；本批常用不超过4096可先用4096，但以最终清单尺寸为准。不因方便打包强制NPOT转方图；建议 Non Power of 2=None。Pixels Per Unit可先统一100作为UI工程约定，不能将其当作物理世界比例证据。

角色/按钮边缘应由Alpha表示透明，不能出现画进去的棋盘格或用底色冒充透明。验证RGBA、Alpha最小值0与柔边；是否最大255依资产设计决定，半透明勾选底不应被强行改成全不透明。Alpha Is Transparency可开启以保护透明边缘颜色，是否预乘Alpha需与后续材质统一，不在导入时反复叠加去黑边处理。

## 九宫格与切片参数

当前交付的两项主控件已换用不含文字的属性面板来源。顺序固定 **Left / Bottom / Right / Top**；当前证据在 `docs/art-extension-sources.json` 的 `commonReplacements`，最终以 `art/manifest.json` 对应文件记录为入口。这些是美术切片参数及导入建议，尚未在Unity中验证。

| 当前文件 | 画布 | Left | Bottom | Right | Top | 使用规则 |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `art/common/main_frame.png` | 1546×743 | 97 | 74 | 97 | 99 | Sliced建议；保留卷云边角，接入时核验最小尺寸 |
| `art/common/title_plate.png` | 655×110 | 0 | 0 | 0 | 0 | Simple；仅整体等比缩放，不九宫格、不横向拉伸 |

上述来源为美术参考仓库 `designs/attribute-panels/v2-painted/unity-slices/png/`。旧组队窗框和旧标题牌仅用于来源追溯：1664×705、Border 76/79/76/79 的旧 `main_frame.png`，以及716×145、Border 142/29/142/35 的旧 `title_plate.png` **不是当前 `art/common/` 同名文件参数**。此前冻结的 `Assets/` 不在当前交付包内，不应从中覆盖当前资源。

以下控件仍沿用旧批准原稿的相同PNG字节；原始来源 `F:\work\image\designs\team-ui-v2\unity-slices\manifest.json`，本地复制追溯见 `docs/ASSET_SOURCES.json`。如后续另导出不同画布，必须重新记录，不能直接套用旧值。

| 文件 | 原画布 | Left | Bottom | Right | Top |
| --- | --- | ---: | ---: | ---: | ---: |
| `section_plate.png` | 433×72 | 76 | 16 | 72 | 21 |
| `member_row.png` | 851×97 | 24 | 19 | 24 | 19 |
| `application_card.png` | 631×198 | 27 | 24 | 27 | 24 |
| `button_primary.png` | 225×66 | 45 | 16 | 45 | 16 |
| `button_secondary.png` | 220×66 | 45 | 16 | 45 | 16 |

`close.png`为82×82、`portrait_frame.png`为91×91，两者Border为0，Simple等比。当前655×110标题牌的卷云轮廓应保持完整，随标题容器等比Contain，不为了铺满行宽切片。

状态导出的画布与旧原画不同：目前已核实普通/选中/禁用主按钮同为460×112，页签同为360×114，列表行同为360×96，勾选框两态同为98×98，锁/勾标记48×48。**这些新状态的Border不能未经测量沿用旧225×66按钮参数**；以最终状态资源映射所列值为准，未列Border时按Simple使用并标待接入验证。

## 控件状态合同

同一逻辑控件的 normal、pressed、selected、disabled、locked 必须有一致的画布尺寸、Pivot与内容安全区。锁定可由同画布底皮+独立锁图标组合；单独48×48锁标不是某个460×112按钮的替代状态画布。按下可用已记录的色调/亮度派生，但不得改变边角尺寸或标题定位；状态差异不能只靠微小色差，选中应有边框/勾，禁用应有文字原因，锁定应给条件或价格。

建议在下一阶段采用 Sprite Swap 或独立背景图切换，对文本保持同一Rect。若采用 Color Tint代替已交付状态PNG，须说明采用方式并避免二次乘色让边框发黑。普通与选中、已解锁与已选择属于不同语义，不能拿“购买成功”直接当“已选角色”。

最终 `art/manifest.json` 的状态组和制作总账共同作为验收依据；只把有实际文件、尺寸一致且映射完整的状态组记为交付。未列出的状态或组合保持待补，不能仅凭命名推断已完成。

## 功能数据到画面的使用约束

- 三名预设角色对应 Fighter/Assassin/Mage；第二、第三角色各500金币是源配置事实。展示价格独立文本，锁定层不能遮住起始道法与身份说明。
- 永久成长覆盖14字段，原上限分别为1/2/3/5阶，不能统一画五个等级点。内部字段、上限与原金币表见 `UI_COVERAGE.json`；原demo数值不是正式平衡验收。
- 局内同时预留6主动+6被动槽；被动资产14种不代表局内14槽。Curse现为局外成长项，当前运行被动池13项，二者作用域必须标清。
- 三选升级支持新主动、持有道法升级、属性升级及钱袋。满槽不代表所有技能满级，只有无可用升级时才按来源逻辑补金币。
- 宝箱展示1/3/5件奖励及金币，揭示约3秒时确认不可用，完成后一次确认全部。多次相同技能奖励应清楚表示阶数推进，不把重复图误标重复发奖异常。
- 进化条件满足只能显示“待宝箱触发”；不能在条件详情加“立即进化”按钮。进化结果归宝箱奖励流程。
- 设置有总音量、音乐、音效、分辨率、全屏、语言、伤害浮字七项；源locale只有English(en)，本次中文为美术本地化。

## 建议打包与下一阶段核验

可按common、icons、characters拆分Sprite Atlas；插画和字体分别保留。建议禁用旋转和紧密裁切以保持状态画布可比较，保留足够Padding/Extrude避免金边串色；具体数值和设备压缩需引擎测试，不声称本阶段已测。

下一阶段需逐项核验：Sprite与字体导入、九宫格最小尺寸、透明柔边、三种横屏视口、长中文与多语言、12槽填满、低血/伤害数字、三选暂停、宝箱揭示和进化、角色消费及成长不足/满阶、确认取消返回、单次结算与存档失败恢复。当前只通过设计图、状态图与说明表达这些要求。
