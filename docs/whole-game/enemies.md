# 全部敌人美术交付

日期：2026-10-28。14种独立道家Q版形象已按字节复用导出，覆盖功能参考游戏当前全部20个敌人PoolKey（14基础身份＋6精英）。本轮新增生成/AI修图次数为0。实际逐张查看所采用的14份原图，并复核浅色/深色阵容图；未修改既有UI图或其引用。

正式资源：`art/whole-game/enemies/`。每张1024×1024 RGBA、有真实Alpha，均与来源及原manifest的SHA-256一致；14个文件的SHA各不相同。精确SHA、逐张Alpha统计、源Prefab、原生/缩放来源、证据快照位于 `docs/whole-game/enemies.json` 和每图 `.png.adoption.json`。

这是一套**道家试炼幻身外观替换**。内部战斗key和行为继续对应参考游戏，展示名可用“原形象名＋幻身”。没有把仙鹤说成蝙蝠、把符虎说成眼球，也不把既有宠物图片冒称本次新生成怪物。原外观/法器/物种特征保持不变，功能外观对应属于本次明确记录的改造。

## 基础身份映射

每条F来源目录均相对 `F:/work/image/`：`designs/creature-combat-20261005/pets/<目录>/runtime/attack/E/01.png`。只取已确认动作中的一张预备静帧，用于参考游戏原有的静态Sprite敌人合同，不继承整套68帧的动画完成结论。

| 游戏Key | 道家幻身身份 | F来源目录 | E正式资源 |
| --- | --- | --- | --- |
| Bat | 云啾啾 | legacy-yun-jiu-jiu | `art/whole-game/enemies/Bat.png` |
| BoyFairy | 芽铃童 | 13-yalingtong | `art/whole-game/enemies/BoyFairy.png` |
| EyeBall | 符小虎 | legacy-fu-xiao-hu | `art/whole-game/enemies/EyeBall.png` |
| FlySkull | 桂灯童 | 04-guideng | `art/whole-game/enemies/FlySkull.png` |
| ForestGuardianFairy | 苍嶂麟 | 07-cangzhanglin | `art/whole-game/enemies/ForestGuardianFairy.png` |
| Gear | 玄潮龟 | 10-xuanchaogui | `art/whole-game/enemies/Gear.png` |
| Ghost | 霜团貂 | 03-shuangtuan | `art/whole-game/enemies/Ghost.png` |
| Slime | 葫团团 | legacy-hu-tuan-tuan | `art/whole-game/enemies/Slime.png` |
| Crow | 烛翎 | 01-zhuling | `art/whole-game/enemies/Crow.png` |
| CrystalHealerFairy | 露华灵 | 16-luhualing | `art/whole-game/enemies/CrystalHealerFairy.png` |
| Fairy | 岚铎仙 | 15-landuoxian | `art/whole-game/enemies/Fairy.png` |
| FlameDancerFairy | 赤砂魁 | 09-chishakui | `art/whole-game/enemies/FlameDancerFairy.png` |
| FrostCrystalFairy | 月弦师 | 12-yuexianshi | `art/whole-game/enemies/FrostCrystalFairy.png` |
| PinkFairy | 绛铃 | 02-jiangling | `art/whole-game/enemies/PinkFairy.png` |

EyeBall/符小虎、FlySkull/桂灯童沿用本项目此前已采用的试敌身份。源Crow.prefab实际引用Ghost.png，现改为独立灵鸦是本次有记录的外观修订。

六精英key：Bat1、EyeBall1、FlySkull1、ForestGuardianFairy1、Gear1、Slime1。各复用对应去掉后缀1的基础PNG，同时映射共享 `art/whole-game/fx/elite-halo.png`。此环取世界scope环原样复制，建议Unity材质金色状态 `#E7BA54`，放在脚底/身后；颜色是导入和效果建议，未烘焙新图，尚未Unity验证。最终环的像素来源见worldFX切片清单。

## 世界表现与导入合同

| 状态 | 正式美术与表现规格 |
| --- | --- |
| 移动 | 一张完整透明Sprite，按源脚本位移/左右镜像、轻微材质正弦扰动；源无敌人Animator/逐帧移动动画 |
| 受击 | 全身短暂白闪；源约0.1秒进入＋0.1秒恢复；不另外伪造hit动作帧 |
| 死亡 | 全身噪声溶解约0.3秒，阴影淡出；不宣称有倒地序列 |
| 冲撞 | Ghost保持原方向锁定冲撞；Crow沿状态机位移/缩放；不以坐标变化冒充新姿态 |
| 灼烧 | 敌人材质染红，玩法伤害值仍由代码配置；不画在玩家负面状态HUD |
| 冰冻/减速 | 身体时间停顿/变慢与共用脚底环，冷色和时长按原Buff；见worldFX状态说明 |
| Boss | 建议1080p可见高度170px（普通约110px），结合既有Boss HUD；最终尺寸/排序须Unity联调 |
| 精英 | 复用基础图＋共享环，始终保留独立key和精英名；不新增六个假物种 |

PNG按Sprite(Single)、FullRect、sRGB、Bilinear、Clamp、禁用MipMaps建议导入，Border均为0，不作九宫格。沿源合同保留左下Pivot `[0.5,0.08]`，左上像素虚拟锚 `[512,942]`；悬浮图是虚拟锚，不声称每只脚都贴住该点。像素高度须按alpha主体而非整个1024画布确定；PPU/Collider/SortingLayer/Scale及材质行为留待下一阶段验证。

## 验收与原文警告

已核验14/14可解码PNG、1024方画布、真实Alpha、来源/输出SHA一致、源manifest SHA一致、14种独立图、全部20 key映射。14份alpha≥16主体在画布最外沿的像素总数为0。已实际查看每份源图及两张最终阵容图，手足/法器/尾翼完整，浅深底下轮廓与身份可区分。未运行Unity，不继承原项目的引擎验收。

以下本轮QA的WARN原样保留，不用“全部检查通过”覆盖：

| id | value | threshold | files |
| --- | --- | --- | --- |
| actual-generation-model-quality-unconfirmed | 14 | actual source evidence required to confirm | 本包全部14个PNG，完整路径见JSON |
| faint-alpha-on-outer-edge | 12 | 0 | `art/whole-game/enemies/Gear.png` |
| faint-alpha-on-outer-edge | 15 | 0 | `art/whole-game/enemies/Ghost.png` |
| faint-alpha-on-outer-edge | 7 | 0 | `art/whole-game/enemies/FlameDancerFairy.png` |
| faint-alpha-on-outer-edge | 4 | 0 | `art/whole-game/enemies/PinkFairy.png` |

弱Alpha外沿残点来自原图并保持原字节，alpha≥16边缘统计全部为0；没有新抠图、去散点、补边或裁切。模型/质量实际证据未披露，继续为null，历史目标Sunburst/max不作为实际返回证明。

另保留选中源帧的历史字符串警告：ForestGuardianFairy为 `actual-model-or-quality-undisclosed-null-preserved`；Ghost为 `visible-alpha-touches-canvas-edge-review-crop`；PinkFairy为 `reference_outside_audit_scope:reference:3`。它们不是本轮新生成失败：本轮直接测量透明边界并实看，Ghost主体无可见裁切，PinkFairy历史额外参考属于宿主生成缓存、未冒称已重新取得。原README中的全动画连播限制完整保留，但本次只使用一张静态帧，不宣称这些历史连播已补验。

## 来源、证据与预览

- `docs/whole-game/enemy-source-evidence/<来源目录>/` 保存原README、交接、姿态说明、选中manifest记录、原逐图记录及必要文字依赖快照；D盘旧路径/已删除原生文件仍作为历史证据，不自动恢复。
- `docs/whole-game/enemies.json` 包含每个快照原路径及SHA、导出链和所有源游戏Prefab映射。
- `designs/whole-game/enemy-lineup-light.png`、`enemy-lineup-dark.png`为14身份静态阵容验收图，只做缩小排版合成，不是AI生图或游戏运行截图。
- `tools/package-enemy-art.py`完成字节复制、透明度/哈希检查和预览排版，不创作新动作。

F盘本次完全只读；关联统一由本项目 `docs/image-reference-associations.md`维护，不操作任何Git状态。功能参考GitHub与美术参考Azure远端分别记录，成果GitHub仍待用户提供。
