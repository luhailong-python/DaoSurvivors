# 三名角色动作美术核查

2026-10-28。F盘只读；未恢复旧Git、未调用付费视频、未安装工具、未编写Unity接入。

## 结论

| 当前人物 | 匹配动作 | 处理 |
| --- | --- | --- |
| 青云小道／金发带男 | 未发现 | 现存v4与4096包均为静态；v14的00动作目录现存0PNG。制作同母版六部件骨骼美术。 |
| 逍遥剑修／吕洞宾 | 有 | V12实存81PNG；取E/W独立Idle各1帧、真实步态各8帧，共18帧，以及2张兼容条带。 |
| 清莲灵修／粉莲短袍何仙姑 | 未发现匹配当前服装者 | V12何仙姑已改素绿长袍长裤，03莲花医者为棕长发冠、灯与瓶的另一人物，均不替换当前UI身份。制作同母版六部件骨骼美术。 |

实际读取v4、4096人物包、V12的README与CLIENT_CONTRACT；V12吕洞宾manifest、QC、visual-review、portrait-source、frame-transforms；03莲花医者MERGE_HANDOFF。实际查看当前三立绘、吕洞宾肖像/E站立/E与W全部8帧条带、V12何仙姑肖像/E站立/8帧条带、03莲花E01及4096金发带静态图。不能凭角色目录名认定匹配。

## 吕洞宾来源与导出

当前UI剑修SHA与V12 `processing/portrait-source.json`中的`baseline_v11_sha256`完全相同：`ea2228db505fbc057da4b4056d08e9bd00ddc0832921e1b37b148ac703b43989`。动作图保留黑髻剑簪、青黑白衣、背剑红穗、腰葫芦。E/W腿与臂有独立交替姿势，不是整图平移。

正式目录：`art/whole-game/players/sword/`。全部512×512RGBA单帧按字节复制，Alpha0–255，哈希与现存来源manifest一致；没有新缩放、重绘、裁切或生成。固定根点沿用源v3 `(256,471)`，Pivot建议`(0.5,0.080078125)`，不是每帧最低脚点重新贴地。

原动作名walk，以Run状态的locomotion美术映射供后续接入；8×60ms=480ms是来源美术时序，不宣称其为参考游戏原Animator实际时长。静止图为独立Idle，1000ms仅预览停留。细微原生饱和边缘不在本次改写，平台压缩与背景显示在Unity中验证。

`PlayerAnim.cs`只切Idle/Run；`PlayerMovement.cs`仅按横向输入翻转x朝向。`PlayerHit.cs`使用材质受击及死亡淡出，因此不虚增人物普攻/施法/受击/倒地序列为当前源码必需项。技能本体特效单独完成。

[逐帧/来源清单](player-actions-audit.json)、[动作资源参数](../../art/whole-game/players/sword/animation.json)、[明暗底循环预览](../../designs/whole-game/players/sword-run-review.gif)。历史来源记录已只读复制在`player-sword-source/`；旧E盘路径按历史证据保留，不表示本机原始生成母图仍存在。

## 另外两人的部件与动作合同

每人六张真正独立RGBA：head、torso、near_arm、far_arm、near_leg、far_leg。逐件记录native关节pivot、512画布的绑定关节、手工比例、层序、父骨骼和原生裁切来源。按实际部件大小校准，不能把六张图同宽拉伸。

512固定画布/脚底锚点，Idle/Run各16帧、每帧60ms；0.96秒是本次美术建议。Run须腿与手臂反相、两腿交替支持/抬离地面，躯干微前倾、头独立补偿；动作由真实部件分层旋转与合成，不能将完整立绘晃动当作跑步。保留曲线、帧坐标、关节覆盖、Alpha、环接及明暗底预览记录。不是AI视频，也不伪称新模型生成的每帧原画。
