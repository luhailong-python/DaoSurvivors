# 世界拾取物、进化与通用支持图

本批仅复用已确认图片与源码贴图；没有生图或AI修图。6种世界掉落已独立提供，经验80使用源经验晶机械HSV琥珀改色，其余为字节复制。透明度不变。逐图来源、SHA、尺寸、显示高度、源值/颜色语义见 `world-support.json` 及每图 `.derivation.json`。

溶解噪声是功能参考提交中实际 `_NoiseTex` 的 `Art/Teture/dissolveTex.png` 原字节副本；原MIT许可保存在 `art/whole-game/support/SOURCE_GAME_MIT_LICENSE.txt`。建议作为Linear数据贴图导入。没有将 `dissolveRamp` 或未使用贴图虚增为必需美术。

冰冻和减速共用 `status-ring.png`，取本项目已生成八卦环原样复制，属于有记录的道家外观替换。灼烧由材质红色实现，无须新增火焰序列；冰冻2秒停速/停材质时间，减速3秒降速50%，两者共用同一个脚下环。效果叠层由下一阶段实现。

独立接触阴影 `contact-shadow.png` 来自已确认葫团团/Slime的Alpha：取非零BBox、压成256×64，置于512×256透明画布，再GaussianBlur10软化，RGB为黑色；不绘制新轮廓、不生图。Pivot中心，建议SpriteRenderer白色乘Alpha0.35；玩家/普通敌人/Boss/Prop可见宽度分别95/80/130/65px。它替换未能解码的原Shadow GUID，不冒称已找到原贴图。本文件和脚本没有把全套美术标为通过。

## 九种进化的真实关系

|Key|进化变化|比较图|
|---|---|---|
|ToNearestSkill|CD设为0.15秒；Damage设为5；弹体乘红色。|`designs/whole-game/support/evolution-ToNearestSkill.png`|
|BothSideSkill|CD×0.3；技能Area×2；仍然左右各投射一次。|`designs/whole-game/support/evolution-BothSideSkill.png`|
|BouncingSkill|Velocity×1.5；Amount+3；弹体乘(1,0.5,0.5)。|`designs/whole-game/support/evolution-BouncingSkill.png`|
|ChainSkill|CD×0.3；仍用同一寻敌连锁纹理。|`designs/whole-game/support/evolution-ChainSkill.png`|
|CircularAttackSkill|改为16方向、间隔22.5°；额外尺寸×2。|`designs/whole-game/support/evolution-CircularAttackSkill.png`|
|CircularMotionSkill|Velocity+1；Amount+3；弹体及程序拖尾乘黄色。|`designs/whole-game/support/evolution-CircularMotionSkill.png`|
|FourCornerSkill|四对角方向变为八方向；技能Area×2。|`designs/whole-game/support/evolution-FourCornerSkill.png`|
|InsideScopeSkill|技能Area×2；生成时AttackTimer设0.5，后续仍按阈值1触发。|`designs/whole-game/support/evolution-InsideScopeSkill.png`|
|RandomSkill|CD×0.3；目标印记保持0.5秒淡出。|`designs/whole-game/support/evolution-RandomSkill.png`|

对比使用源技能满级（逐条应用UpgradeAttribute）前后数据、归一化全局Area100/Amount0/SkillSpeed100；用同一纹理缩放、旋转和乘色，CD变化只通过数值说明，未捏造同时发射更多弹体。真实尺寸为 `(全局Area+技能Area)×0.01`；技能Area翻倍并非总尺寸翻倍。太极震进化另外乘2。四象符有四角到八向变化。八卦阵的AttackTimer设0.5只调整生成后的计时起点，不能声称其后持续每0.5秒攻击。

五种技能的TrailRenderer使用Unity内置材质，无额外外部拖尾贴图缺口；准确源持续时间/渐变Key保存在JSON，环绕法器进化时身体和拖尾均乘黄色。最终宽度、混合、排序及采样须Unity阶段复核。

## 预览与验收状态

`designs/whole-game/support/world-pickups-scale.png`检查6种拾取物及小尺寸；`world-status-dissolve.png`显示三个状态、白闪和五阶段噪声阈值；`world-camera-composite.png`为1920×1080已有地块、角色、敌人、Prop、六拾取物、共享环与衍生阴影的代表性镜头摆放。预览是已有美术的离线合成，非新原画、非Unity截图，状态颜色为离线近似。

本脚本只记录产出与技术检查，实际视觉检查单独补记。Unity导入和运行未执行。

实际视觉核验已完成，逐图SHA绑定于 `world-support-visual-review.json`：12张预览均已查看；阴影软边透明、角色/敌人/Prop落点清楚，拾取物小尺寸及9种进化关系通过本批离线美术核验。Unity验证仍未执行。
