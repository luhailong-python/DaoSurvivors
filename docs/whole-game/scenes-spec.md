# 清竹道场场景美术合同

核实日期：2026-10-28，America/New_York。临时游戏名“道途幸存者”，临时场景名“清竹道场”。本说明对应机器合同 [`scenes-spec.json`](scenes-spec.json)，只做美术与地图拼装数据，不搭建 Unity 场景、不修改 C#、Prefab、材质或 Shader。

## 实际来源与范围

功能参考 `Roo-Roo-Roo/survivors-roguelike-kit`，固定提交 `3f905381d73a34b516030528b8ef6743868b9e52`。实际阅读了 `Map1.asset`、`MapManager.cs`、`MapConfigSO.cs`、`Game.unity`、`CameraFollow.cs`、`Map.shader`、`Map.mat` 和 `Prop.prefab`；准确仓库相对路径及各文件 SHA 见 JSON。

- 只有一套 Map1。First、Second 两份关卡共用此地图及 Stage1；不增造两套世界地图。
- Map1 为 100×100 逻辑格，每格 1×1 世界单位。六种纹理权重依次为 **200 / 3 / 3 / 1 / 1 / 3**，总权重 211。
- 唯一一种可破坏 Prop 实例化 20 次，按源码公式排为五行四列。不是20种道具，也不是障碍迷宫。
- 游戏镜头为正交，`orthographic size = 8.5`，可见世界高度17；在1920×1080参考分辨率下，每地块约63.53显示像素。
- 源纹理每张2048×2048是源项目现存事实。本轮正式地块采用512×512，不把缩小或拼接称为新增原生细节。

地图中心坐标公式为 `(-50+x, -50+y)`，x、y取0…99。首末地块中心为-50与49，实际覆盖边界为 `[-50.5, -50.5, 49.5, 49.5]`。这与笼统写成-50至50不同，拼装数据保存了源码公式。

## 已制作地块与输入合同

已取得真实母图 [`world-terrain-v1.png`](../../art/whole-game/sheets/world-terrain-v1.png)：原生1536×1024、RGB、严格3列×2行，每格512×512。本图由协调者使用内置 image_gen 生成；实际配置目标、提交参数、返回信息、时间和两张风格参考在同名 `.generation.json` 及 `docs/production/world-terrain-v1.*`，本工具没有调用模型。

| 源顺序 | 正式资源 | 内容 | 权重 |
|---|---|---|---:|
| 1 | `art/whole-game/terrain/v1/ground-01.png` | 安静浅灰绿碎石底 | 200 |
| 2 | `art/whole-game/terrain/v1/ground-02.png` | 苔痕与中央小石 | 3 |
| 3 | `art/whole-game/terrain/v1/ground-03.png` | 竹叶点缀 | 3 |
| 4 | `art/whole-game/terrain/v1/ground-04.png` | 小花点缀 | 1 |
| 5 | `art/whole-game/terrain/v1/ground-05.png` | 地衣点缀 | 1 |
| 6 | `art/whole-game/terrain/v1/ground-06.png` | 小石堆点缀 | 3 |

新母图遵循同样合同：完全俯视、同材质地面、方形格、无文字、无格间留白、无角色建筑和界面框、完全不透明，中心放变体，外缘保持安静。工具支持3×2或2×3和显式六个裁切矩形。只在不超过一像素的网格取整差中居中裁成共同方形；严重长宽比错误直接拒绝。每格小于正式尺寸时拒绝放大。更大母图可明确缩小到512或1024，并记录原生裁切尺寸、裁切框、Lanczos缩小与最终尺寸。

## 共有外缘与接缝处理

本批每格原生就是512，因此没有缩放。先原生裁切，再以第一张纹理的真实像素建立共有外缘：将第一张做半幅循环偏移，使输出左右、上下边的像素来自原图中央自然相邻像素。所有变体复制同一外缘，强制保护16像素外圈，在最大48像素范围中用确定性的动态规划选择逐行±1像素的最小误差拼接线，内部保留各变体原像素。

这是**来源像素重排及拼接**，没有程序画地面、混色、模糊、生成新纹理或增加细节。两侧边界并非强行复制为同一像素行：自然相邻像素允许真实纹理梯度，证明比较的是每对拼接与同一自然相邻引用的逐通道一致性。不要把“引用不匹配为0”说成“自然RGB步进为0”。

每张 `.derivation.json` 保留原图 SHA、原生裁切框、原生尺寸、无缩放事实、共同外缘来源、所有拼接线、修改像素数量和最终 SHA。`native/` 与 `pre-adaptation/` 是有明示用途的来源/对照文件，不属于另外12种游戏地面；本批两者像素相同。正式使用目录直属的六张 `ground-*.png`。

## 已完成的核验

数值结果见 [`seam-qa.json`](../../art/whole-game/terrain/v1/seam-qa.json)：

| 检查 | 结果 | 阈值 |
|---|---:|---:|
| 横向36对＋纵向36对共有外缘引用通道不匹配 | 0 | 0 |
| 横向边界梯度／邻近自然梯度 | 0.9943420076212431 | ≤1.5 |
| 纵向边界梯度／邻近自然梯度 | 0.9974060712552862 | ≤1.5 |
| 内侧拼接线平均RGB误差最大值 | 4.706380367279053 | ≤25 |

实际查看了六图排版、变体等量混排、处理前混排、全部横向36对、全部纵向36对、100×100源权重总览和源镜头尺度图。未见直线明暗接缝、被切断的中心点缀或画入地面的角色/界面。源权重使安静地块占约94.79%；整图总览有同类石纹重复，属于源码权重下的贴图效果，没有把它说成新绘100×100整幅地图。

预览入口为 [`designs/whole-game/scenes/v1/index.html`](../../designs/whole-game/scenes/v1/index.html)。该页各图均由正式地块拼排后缩小显示，明确不是新增的模型原生整图。

## 拼装数据与尚待组合

[`map1-assembly.json`](../../art/whole-game/terrain/v1/map1-assembly.json) 给出100×100地图、六种权重、明确索引/坐标原点、20个Prop坐标、镜头尺度和可复核固定种子。它复现权重与布局规则，不声称复现 Unity 随机数序列。Prop位置为：

- x：-30、-10、10、30。
- y：-33⅓、-16⅔、0、16⅔、33⅓。

源码Prop没有 Collider2D；不额外发明地图阻挡或门户。目前地面美术已通过本批数值和视觉核验。**Prop透明图、独立阴影及代表性角色合成仍待协调者的新世界资源绑定**，本场景合同因此没有冒称整套场景组合已完成。

这是美术拼装交接，不宣称可玩地图或碰撞/导航验收；没有用全开放数据的连通性代替实际 Unity 运行。下一阶段才验证物理、镜头边缘、排序、导入采样与实际帧率。

## Unity 导入建议

六张正式地块建议 Sprite (2D and UI)、Single、中心Pivot `(0.5,0.5)`、PPU512、1×1世界单位、Bilinear、Clamp、关闭MipMaps，先无压缩对照。此建议未在Unity导入验证。角色和Prop用脚底锚点，与地面中心Pivot分别管理。

已核实源 `Map.mat` 的 `_Brightness = 3`，而 `Map.shader` 直接将采样RGB乘以该值。本次浅色地面按原图1倍亮度验收，接入时先以1倍对照再决定效果；盲用3倍会过曝。本阶段没有修改材质或Shader。

## 工具与环境记录

工具为 [`build-world-tiles.py`](../../tools/build-world-tiles.py)，生产必须显式指定本项目内的母图，输出与预览目标必须尚不存在，不覆盖旧成果。本批执行：

```powershell
Set-Location -LiteralPath 'E:\work\image\DaoSurvivors'
& 'C:\Users\luyua\.codex\runtimes\agent-sprite-forge\Scripts\python.exe' 'tools\build-world-tiles.py' --atlas 'art/whole-game/sheets/world-terrain-v1.png' --generation-record 'art/whole-game/sheets/world-terrain-v1.png.generation.json' --grid 3x2 --size 512
```

已实际读取 `generate2dmap/SKILL.md`、地图策略与预设资料，采用生成位图作为地面来源、数据作为拼装规则。能力检查保存在 [`scene-doctor.json`](scene-doctor.json)，内置 `host_image` 可用；没有调用API、CLI模型、付费路线或生成新图。环境报告唯一WARN原文如下，报告未提供value、threshold或files字段，不补造这些字段：

```json
{
  "id": "python.path",
  "status": "WARN",
  "detail": "other python.exe on PATH: C:/Python314/python.exe; ~/AppData/Local/Programs/Python/Python313/python.exe; ~/AppData/Local/Microsoft/WindowsApps/python.exe",
  "remedy": "PowerShell, cmd and Git Bash may resolve different interpreters; run Forge with the one shown in python.version"
}
```

因此实际生产显式使用上面专用Python。未配置的API和缺少Grok属于可选路线信息，不影响本次使用已取得的内置生成母图。F盘全程只读，未进行Git操作。
