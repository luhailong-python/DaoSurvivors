# 一炁当千

制作目录：`E:\work\image\DaoSurvivors`。2026-10-29，按参考游戏实际范围完成整款游戏美术的本地制作与离线验收；当前阶段不做 Unity 接入。

正式名《一炁当千》，旧工作名“道途幸存者”。新名字和Logo已统一到本次UI美术交付。

## 查看与交付

- [整套美术总览与三角色动作播放](docs/whole-game/index.html)
- [名字与Logo展示](designs/branding/yiqi-dangqian-v1/index.html)
- [52 屏 UI 图库](designs/ui-suite/gallery.html)
- [完整覆盖与验收总账](docs/whole-game/ART_COVERAGE.md)
- [最终验收及保留事项](docs/whole-game/ACCEPTANCE.md)
- [逐文件资源清单](art/manifest.json)
- [Unity 美术导入建议](docs/whole-game/UNITY_ART_IMPORT.md)

本机可查看 [美术总览](http://127.0.0.1:4327/docs/whole-game/index.html)。离线解压后可直接打开上述 HTML；需本地服务时，在本目录运行 `python -m http.server 4327 --bind 127.0.0.1`。完整美术 ZIP 的路径、SHA 和 CRC 核验回执保存在 `.local/delivery/LATEST.json`；成包不包括功能参考克隆、Git 或早期 Unity 工程。

## 当前覆盖

|类别|成果|
|---|---|
|品牌|正式名字、主Logo与葫芦徽记，8正式PNG尺寸，已统一UI|
|UI|52 张1920×1080整屏/状态/流程图和对应布局，独立面板、控件、图标、字体；三类正式控件共15状态|
|角色|既定3人×Idle/Run，146正式E/W帧、10条带、12分层部件|
|敌人|14身份映射20个PoolKey，含6精英映射和共用光环|
|场景|6可混排正式地块，72种横纵组合检查；1可破坏Prop|
|世界掉落|6种，Exp40青玉与Exp80琥珀各有数值映射|
|技能和敌弹|9基本技能纹理及9进化使用关系/对比，5敌弹|
|支持|3状态规格、共用状态环、接触阴影、实际溶解噪声和许可、受击/淡出规格|

全量美术文件包含正式资源、图集/分层来源、生产/检查支持和授权，不全部视为独立运行Sprite；52张整屏PNG及布局另列UI清单。当前所需美术缺口为0。源没有的社交/经营系统和逐怪跑攻死身体序列没有虚增为必需项。

小道和灵修采用内置生图制作的六部件原画，通过真实肢体分层变换完成动作；肩髋接缝已返修。剑修保留身份匹配的来源Idle及walk动作，walk用于Run状态，原始像素和480ms步态未改写。新两人960ms为美术建议；不冒称与参考项目1秒骨骼动画相同。逐帧、明暗底、关节、实际浏览器播放与16→1环接的证据见 [角色动作验收](docs/whole-game/player-actions-final-review.json)。

## 来源与边界

功能参考：[Roo-Roo-Roo/survivors-roguelike-kit](https://github.com/Roo-Roo-Roo/survivors-roguelike-kit)，固定提交 `3f905381d73a34b516030528b8ef6743868b9e52`，只在 `.reference/survivors-roguelike-kit` 读取。它不是成果提交仓库。

美术参考：`F:\work\image`，远端为 [Azure DevOps image](https://luyuacpp.visualstudio.com/image/_git/image)。两张指定主参考为 `designs/mail-ui-v1/01-mail-event.png` 和 `designs/team-ui-v2/team-ui-v2.png`。本接续阶段F盘只读，不操作共享Git；来源合同快照保存在 `docs/provenance/`，实际关系见 [项目关联](docs/image-reference-associations.md)、[基础来源](docs/ASSET_SOURCES.json) 与各图旁侧录。

新增/编辑图逐图保存配置目标、实交参数、回执、时间、参考图片和SHA。实际后端型号/质量未披露的保持null；配置目标不冒充返回证明。原始图集等格检测的FAIL/WARN和弱Alpha散点保留，正式切片改用像素归属边界。完整数值在UI和世界战斗验收文档中，没有被改写为通过。

Unity导入、Prefab/Renderer/Animator/材质/拖尾接入、平台压缩及实机验证留至下一阶段；早期Unity目录冻结。成果仓库已核实为[luhailong-python/DaoSurvivors](https://github.com/luhailong-python/DaoSurvivors)，用户本轮已授权提交和Push。实际提交SHA与远端确认结果见Git及`.local/release/receipt.json`；[Git交付说明](docs/GIT_DELIVERY.md)记录提交范围。Noto字体OFL和复用溶解贴图的MIT许可随美术包保留。
