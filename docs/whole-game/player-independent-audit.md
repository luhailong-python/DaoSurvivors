# 角色动作独立复核

核验日期：2026-10-28。此报告只核验图片及功能要求；未执行 Unity 接入或运行。

## 当前源码要求

功能参考为 `.reference/survivors-roguelike-kit`，固定提交 `3f905381d73a34b516030528b8ef6743868b9e52`。

- `Player/Animator/PlayerAnim.cs` 的 `Update` 仅在 Rigidbody2D 速度是否为零之间切换 `Run`、`Idle`。
- `Player/Movement/PlayerMovement.cs` 根据横向输入的正负设置根节点 `localScale.x`。没有八方向身体状态要求。
- `Player/Hit/PlayerHit.cs` 对 `mSpriteRenderers` 逐一调用受击材质效果；死亡将材质 `_Alpha` 在 0.2 秒内降为零，并将独立阴影在 0.8 秒内淡出。不要求新的身体攻击、受击、死亡帧序列。
- Fighter、Mage、Assassin 的 Idle/Run 原始 `.anim` 均记录 `m_SampleRate: 30`、`m_StopTime: 1`、`m_LoopTime: 1`。新绘动作和复用剑修动作有各自美术时序，不能声称其时长与原片相同。

## 后续导入边界

参考角色的 PSB、SpriteSkin、骨骼和 LimbSolver2D IK 组成了原始骨骼表现。当前六部件合成导出的透明帧图属于独立美术交付，不能直接宣称可替换原 PSB 而保持原 `.anim` 绑定。后续 Unity 阶段需要选择重新绑定部件骨骼，或替换为序列帧渲染；两种方式均要重新核验碰撞高度、朝向、材质受击对象数组、阴影和动画状态。现在不实施该阶段。

切片使用统一画布和固定根点，不能按每帧 Alpha 最低像素重新贴地。部分旋转必须保持肩、髋覆盖；近远臂和腿要独立交替，且在明暗底和最终显示尺寸检查透明边缘。六个完整肢体部件不含单独肘、膝关节，不能称为复刻原游戏全部 IK 骨架。

## 剑修复核

已读取 `tools/export-sword-player-actions.py`、`art/whole-game/players/sword/animation.json`，以及已复制的来源证据。清单中的 18 单帧、2 条带共 20 文件的 SHA-256 与当前磁盘完全一致。查看 E/W 两张完整八帧条带，腿部前后交替、手臂独立摆动，身份与发髻、背剑、衣服和腰挂保持一致。

剑修 Run 使用来源 `walk` 的八帧美术，8×60ms；Idle 为独立静止图，1000ms 只是预览停留。不能将这套已有图片称为本次新生成，或以八帧数量推断实际 Unity 骨骼动画已经验收。

## 青云小道、清莲灵修

已查看以下四张完整 16 帧姿态表，覆盖两人的 Idle、Run，并查看原尺寸 `fighter/run/E/05.png`、`mage/idle/E/01.png`：

- `designs/whole-game/players/fighter-idle-poses.jpg`
- `designs/whole-game/players/fighter-run-poses.jpg`
- `designs/whole-game/players/mage-idle-poses.jpg`
- `designs/whole-game/players/mage-run-poses.jpg`

本阶段观察：青云小道的金色发带、短刺发、白绿金短袍、葫芦保持一致；清莲灵修的黑髻白莲簪、粉莲短袍、深绿短裤、裸小腿和白靴保持一致。v2 肩胸覆盖修正后，没有看到透明的颈、肩、髋缺口或浮在衣摆上的切口。两套 Run 均能逐相看到独立的两腿交换和手臂变化；Idle 有细微的头、躯干和袖部变化，使用六部件组合而非仅晃动一张完整立绘。

第一轮姿态表中支撑脚高度有变化，制作负责人随后修正。复看 06:20（执行主机时间）的接触修正版 Run 表与两人 E13 原尺寸图，发现把完整腿向下移动以固定脚底，造成新的髋部覆盖问题：青云小道 Run12—14 的近腿顶部开口落到躯干下方，E13 的裤腿切口明显可见；清莲灵修同阶段的近腿短裤顶部也更贴近衣摆下缘。该版不能通过最终视觉验收。已向负责人指出应保持髋关节藏在衣摆后，通过绕髋的腿长度校准或合适的形变解决脚底接触，不能只向下移动整条腿。

后续最终版已改用保持髋点的腿部 Y 长度解算和闭合的布料腿顶。重新查看上述四张完整姿态表（64 个 E 朝向姿势）及两人 Run/E/13 原尺寸图，之前露出的开放式裤腿髋口已消除，衣摆和髋部保持覆盖，没有看到新透明断口；独立手臂和腿的交替变化依然清楚。该版通过独立静态逐相美术复核。头部身份、服装和法器保持原方案；没有以另一角色的动作替换。

两份最终 `animation.json` 记录的全部 64 个 E 帧 SHA-256 与磁盘一致。Idle 两腿脚底均为 471px；Run 支撑脚为 471px，两人远腿第 02 相为 472px，最大采样误差 1px。末帧到首帧的实际播放、节奏和镜像正确性由主代理另行进行浏览器播放及帧检验；本报告不代替该部分，也不代表 Unity 运行验收。

最终证据和逐文件哈希已写入 `docs/whole-game/final-review-independent.json`，状态为 `accepted_still_visual_and_pose_review`。六个完整肢体部件的手脚保持刚性，不应宣称为肘、膝分段 IK 或 AI 视频动作。若后续像素或清单发生变化，应重新检查对应输出，不能沿用旧哈希的通过结论。
