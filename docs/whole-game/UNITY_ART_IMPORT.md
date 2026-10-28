# 全游戏美术的 Unity 导入建议

本阶段只交付美术；未在 Unity 中导入或运行。原目录中的早期 Unity 工程冻结，不纳入本次美术包。先看 `art/manifest.json` 的逐文件尺寸、Alpha、角色、Pivot、Border 与来源，再按实际平台调整压缩、PPU 和图集。

## 角色

三人当前身份与 UI 立绘相同。青云小道、清莲灵修各有独立六部件原画，以及 Idle/Run 各16帧、E/W两朝向的512×512 RGBA成品。每帧60ms、循环960ms为本次美术建议。头保留v1生成图，其余部件采用关闭空心关节的v2；部件表记录原生裁切、关节Pivot、比例和镜像。曲线保存在各自 `animation.json`。

逍遥剑修复用身份哈希匹配的既有E/W专用Idle各1帧、walk各8帧；walk映射当前Run状态。源美术8×60ms=480ms，Idle1000ms仅展示停留。参考游戏原骨骼Idle/Run为1秒、30fps采样；没有把这三种时序说成同一内容。

单帧Sprite(Single)，条带Sprite(Multiple)，按512×512等格切片。所有角色成品帧使用同一固定根点`(256,471)`，Unity归一化Pivot`(0.5,0.080078125)`。横条画布的中心不能当作每片的Pivot；10条带的chronological顺序已核验。E/W为朝向资源；接入时可选择仅导入E并水平镜像，避免双重翻转。保留完整画布，不能按每帧Alpha最下端重新贴地。

原游戏使用PSB SpriteSkin、骨骼和IK；本次序列帧不能直接替换其骨骼曲线。下阶段应选择重新绑定这些分层部件，或替换为SpriteRenderer切帧；相应更新PlayerHit的Renderer引用。六部件动作没有分节肘膝IK，不是AI视频。受击白闪与死亡淡出继续由材质控制，无需额外伪造身体攻击序列。

## 世界

正式混排地面为`art/whole-game/terrain/v1/ground-01.png`至`06.png`，均512×512；原生图集裁片与适配过程另存生产来源，不当作更多地图。Map1权重为200/3/3/1/1/3，两关共用。导入时遵循格边一致性并对照72种横纵组合接缝记录；不要对地块添加会改变边缘的透明裁边或独立缩放。

14个敌人静态身份映射全部20个PoolKey，6精英共享母版和独立共用光环。`enemies.json`有脚底Pivot与尺寸建议；敌人没有源码必需的身体逐帧动作，移动、镜像、顶点扰动、白闪、溶解和冲刺由下一阶段实现。Crow独立外观是本项目修订，原Crow.prefab实际误用Ghost图，来源事实保留。

9种技能世界PNG、5种敌弹、Prop与吸取物采用`world-combat-slices.json`的完整512画布、Pivot与原生归属；禁止对原图集等分硬切。9种进化并不要求9张新底图，按`world-support.json`的精确乘色、数量、方向、面积、CD与拖尾参数复用。里面记录了四角到八向、八卦阵初始计时与总面积公式，不能用概述替代。

6种世界掉落在`art/whole-game/support/`；Exp40青玉与Exp80琥珀分别映射40/80经验。影子`contact-shadow.png`源自已确认Slime的Alpha压缩/模糊，建议中心Pivot、Renderer Alpha0.35；状态环共用于冰冻/减速，灼烧由材质红色。`dissolve-noise.png`为MIT许可源码贴图的字节副本，作为Linear数据纹理，sRGB关闭；不能照搬普通彩色Sprite设置。

## UI 与阶段边界

52屏的布局、动态文字、字体、控件状态、九宫格参数见`docs/ui-suite/UNITY_ART_IMPORT.md`和`docs/art-resource-guide.md`。三类正式控件共15状态，各族画布/Pivot/Border一致。画面设计与离线状态预览已验收；Canvas Scaler、安全区、SDF字体、材质混合、拖尾、排序、性能、Collider、压缩和实际运行留待接入阶段。此文不是已执行导入的证明。
