# 道途幸存者 · 美术与 UI 设计合同

2026-10-26。项目名为暂定名，当前交付目标是独立的 Unity 工程 `E:\work\image\DaoSurvivors`。本文件记录本轮设计要求与实际素材来源，运行是否通过以单独的验证报告为准。

## 项目与来源

- 用户给定玩法／项目来源：[Roo-Roo-Roo/survivors-roguelike-kit](https://github.com/Roo-Roo-Roo/survivors-roguelike-kit)。该链接不等于本地项目已绑定的 Git 远端。
- 美术参考仓库：`F:\work\image`，README 名称为“五行奇谈 · Q 版游戏美术”。核实远端为 `https://luyuacpp.visualstudio.com/image/_git/image`；当前 GitHub 地址待确认。
- 两个目录独立管理。新项目代码、正式资源、制作输出及[素材关联记录](image-reference-associations.md)保存在本工程中；此前写入 F 盘 README 的本项目关联已于 2026-10-26 迁回。

## 本轮界面与玩法

围绕三名可选角色、三处试炼和每局 90 秒的生存玩法制作完整 UI：选角、修行、图鉴、设置、战斗 HUD、升级选择和结算。角色内部标识为 `qingyun`、`jianxiu`、`lingxiu`；试炼内部标识为 `bamboo`、`ruins`、`moon`。正式中文名称和数值以本项目界面及代码为准。

大厅先突出当前角色、试炼选择与开始入口，辅助入口保持可辨认。战斗界面突出气血、灵气／升级进度、剩余时间和暂停。升级时清楚呈现可选收益；结算明确区分胜利与失败，并显示本局时间、击败数量、等级和所得资源。局内效果与局外修行的作用范围分别说明，避免把待选择效果显示成已生效。

## 已实际查看的首要风格图

| 参考仓库相对路径 | 实际文件 | 本轮用途 |
|---|---|---|
| `designs/mail-ui-v1/01-mail-event.png` | 1931×814，RGB PNG | 玉绿、象牙纸面、暖金卷云、道家 Q 版人物及完整手绘层级 |
| `designs/team-ui-v2/team-ui-v2.png` | 1931×814，RGB PNG | 圆润框板、标题牌、主次按钮、头像与清晰留白 |

两图均为已解码的真实图片，不是 Git LFS 指针；完整 SHA-256 见 [素材来源清单](ASSET_SOURCES.json)。两图作为风格输入，未将邮件或组队整屏图直接复制为本项目运行界面。

已实际阅读参考仓库的根规则、README 接手说明、`docs/WUXING_QITAN_HANDOFF.md`、`docs/QDAO_ART_DIRECTION.md`、`docs/IMAGE_MODEL_POLICY.md`、`config/image-generation.json`、`docs/AI_DESIGN_TOOLS_SETUP.md`、`designs/README.md`，以及对应素材目录的现存 README、邮件 `UI_SPEC.md` 和切片清单。

指定的 `qdao_ui_redesign_v5/UI_SPEC.md` 当前缺失，无法读取其第 2 节；没有从旧 Git 恢复。`designs/README.md` 中“邮件 PNG 缺失”和旧 D 盘路径已过时，本轮采用当前实际存在的两张指定原图。历史文档中的“五行奇谈”业务、演示数值、旧客户端路径和旧发布授权不作为本项目需求。

## 美术方向

以玉绿、青绿为主色，象牙米白和暖米色纸绢承担内容面板，暖金细边区分控件。形状圆润饱满，采用柔和云纹、如意卷角、适度金玉材质与细腻手绘明暗。朱砂、红穗和桃花粉只作少量点缀。

标题牌、主要操作和选中状态使用玉绿金边；正文、列表、次操作和说明卡以米白纸面承载。深底使用米白字、浅底使用深玉绿字。文字、数值、进度和状态由 Unity 原生 UI 显示，避免烘焙演示文案。正文优先保证阅读，装饰留在外围。

太极、葫芦、玉珠、流苏和云气依界面用途配置。人物保持大头短身与各自脸型、身份、服装和法器；不把不同角色换色成同一张脸。场景与人物保持同一美术方向，避免写实皮肤、塑料高光、粗糙拼贴、模糊拉伸和密集噪点。其他游戏只提供功能或玩法参考。

## 分辨率与适配

Unity 横屏设计坐标以 **1920×1080** 为基准，并检查 **1280×720** 与 **2560×1080**。

- 画面中的人物、圆徽标、文字和边角装饰保持等比；不按屏幕宽高分别拉伸。
- 1280×720 按相同比例缩放，主要操作和文字保持可见。
- 2560×1080 利用额外横向空间延展背景；核心信息保留在居中的 16:9 安全区域，操作入口不因宽屏漂移出可达范围。
- 框板与按钮仅在来源清单允许的范围使用九宫格；固定边距以原始 PNG 像素为准。页面内容超出时使用滚动或重新排布，不能压扁角色或文字。
- 战斗 HUD、升级选择、暂停和结算需在三种分辨率分别验证，不用大厅静态预览替代战斗适配验收。

## 本轮复用素材合同

18 张既有 PNG 位于 `Assets/DaoSurvivor/Resources/DaoArt/`，逐文件路径、来源 SHA、尺寸、真实 Alpha、九宫格和历史证据见 [ASSET_SOURCES.json](ASSET_SOURCES.json)。

| 素材组 | 输出文件 | 规格与使用方式 |
|---|---|---|
| 组队原稿控件 | `main_frame`、`title_plate`、`section_plate`、`member_row`、`application_card`、`button_primary`、`button_secondary`、`close`、`portrait_frame` | 同名 PNG，字节直接复制；九宫格沿用来源 manifest；圆框与关闭钮保持比例 |
| 静态人物 | `hero.png`、`sword.png`、`healer.png` | 1024×1024 透明全身图；保留金发带道童、束发剑修和莲花灵修各自外观 |
| 静态敌人与灵宠 | `enemy-tiger.png`、`enemy-lantern.png`、`fox.png` | 前两张为正式普攻起式中的单帧，1024×1024；九尾狐为1254×1254；不声明完整动画 |
| 法器图标 | `icon-sword.png`、`icon-boots.png`、`icon-taiji.png` | 前两张为600×600导出，太极为120×120；等比显示，无九宫格 |

上述 18 张复用素材只复制既有字节，没有新 AI 生成、裁切、缩放或原生细节提升。600 方图标来自共享母图的历史裁切和等比导出；1024 人物及动作帧的原生生成尺寸按历史证据分别记录。无法核实的原始尺寸、实际型号和质量保持未知，不按当前配置回填。

三名角色与两个敌人的当前载荷是静态图片。运行时位移、朝向或弹动效果如有实现，属于引擎表现，不能称为已交付独立手绘动作序列。

## 新生成的大厅主视觉

[大厅原图](../Assets/DaoSurvivor/Resources/DaoArt/lobby-v1.png)位于 `Assets/DaoSurvivor/Resources/DaoArt/lobby-v1.png`，Unity 资源键为 `DaoArt/lobby-v1`。实际原生输出 **1672×941、RGB PNG**，与宿主源字节一致，未裁切或缩放；提示词中的1920×1080只表示目标尺寸。

金发带道童与白狐位于左侧，玉绿仙山、瀑布云海与桃花承接两张主参考的画法；右侧保留清淡空间用于原生 UI。图中未烘焙界面标题、数字、按钮或框板。

完整证据见[逐图记录](../Assets/DaoSurvivor/Resources/DaoArt/lobby-v1.png.generation.json)、[工具回执](production/lobby-v1.receipt.json)和[实际提示词](production/lobby-v1.prompt.txt)。生成时实际附上两张 F 盘主参考。配置目标为 `gpt-image-2.5-sunburst / max`，2026-10-26 已重新核对[官方型号说明](https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst)及[质量参数](https://developers.openai.com/api/reference/resources/images/methods/generate)。内置调用没有型号或质量选择器，工具返回也未披露具体型号与画质，实际值均为未确认／`null`。

主记录时间为源文件保存时间 **2026-10-26 05:29:12.8440388（America/New_York，UTC−04:00）**，取自宿主原文件 `LastWriteTimeUtc` 并转换时区，不能冒充已核实的后端作业起止时间。PNG 的 Pillow 信息字典为空，但实际含有 C2PA `caBX` 声明块；可读到通用软件标签 `ChatGPT / gpt-image` 和创建声明时间，不能据此确定 Sunburst 分支、模型快照或质量。回执保存这些可读声明，未执行 C2PA 签名与信任链验证。

## 新生成的战斗 HUD 场景底图

[战斗底图](../Assets/DaoSurvivor/Resources/DaoArt/arena-v1.png)位于 `Assets/DaoSurvivor/Resources/DaoArt/arena-v1.png`，Unity 资源键为 `DaoArt/arena-v1`。实际原生 **1672×941、RGB PNG**，与宿主输出字节一致，没有裁切、放大或缩放导出。画面是日景竹林道场：中央浅灰石地保持开阔，低对比太极纹、外围玉竹、局部灯笼及角落荷池服务于独立角色和 HUD 的可读性。

这是 `baked_scene_mode` 的场景图层，用于战斗 HUD 排布，**不等同于可导航地图、碰撞资料或原主城分块交付**。角色、法术、HUD 与弹窗独立叠加；运行边界来自 Unity `RunModel`，不能从画面石缝或栏杆推定。具体参考视口、中心区域、角色比例与绘制层次见[场景合同](production/arena-v1.contract.json)。参考库 `docs/MAP_PARALLEL_SPLIT_20261013.json` 当前缺失；本图为新项目独立 UI 场景，没有占用原城市地图坐标，也没有恢复缺失清单或历史图块。

生成负责方已读取 `generate2dmap` 技能并核实 `host_image` 可用；本次按用户明确要求使用内置 `image_gen`，实际附上两张 F 盘主参考，透明背景参数为 `false`，没有发送型号或质量参数。配置目标仍为 Sunburst/max，实际型号和质量未披露，均记为 `null`。

[逐图记录](../Assets/DaoSurvivor/Resources/DaoArt/arena-v1.png.generation.json)、[回执](production/arena-v1.receipt.json)和[实际提示词](production/arena-v1.prompt.txt)分别保留配置快照、完整调用、引用 SHA、原生图身份及文件保存时间。保存取证时间为 **2026-10-26 05:49:43.7971852（America/New_York，UTC−04:00）**。PNG 含 C2PA 声明，通用软件标签为 `ChatGPT / gpt-image`；签名未验证，也不据此认定具体模型或质量。

## 字体与验收

使用官方 Noto Sans CJK SC Regular 静态字体，位于 `Assets/DaoSurvivor/Resources/Fonts/NotoSansSC-Regular.otf`，Unity 资源键为 `Fonts/NotoSansSC-Regular`。SIL OFL 1.1 原文随 `NotoSansSC-OFL.txt` 提供；官方来源与校验值见素材清单。该字体从官方 Noto 上游取得，不是参考仓库旧字体，也不是 AI 生成素材。

已完成复用 PNG 的解码、尺寸、真实 Alpha 和复制前后 SHA 核验，以及字体解析、授权载荷与目标中文字形覆盖核验。设计验收仍须检查风格、原生文案、选中／禁用／暂停／升级／胜败状态、三种分辨率和实际操作流程；Unity 导入、编译、运行、截图及构建结果由项目验证报告分别说明。
