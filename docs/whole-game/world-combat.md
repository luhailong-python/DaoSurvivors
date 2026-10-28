# 世界攻击、敌弹、拾取物与破坏物资源

2026-10-28。root新生成的 `art/whole-game/sheets/world-combat-v1.png` 已按实际Alpha归属完成16件切片，另复用1份精英光环。切片未调用模型、未AI编辑、未抠图或修改Alpha，未缩放或去除小组件。正式文件均512×512 RGBA，这个尺寸来自透明补画布，**不是把原生细节放大到512**。

原生图集1536×1024，SHA-256 `87d2ca1039c09fa653a3db2e822e2dae614806203c27a4125bbc5fedbc68b5b8`。生成记录由root保存于图片旁 `.generation.json`，实际参数/工具回执指向 `docs/production/world-combat-v1.*`。入口没有披露实际型号/质量，逐片沿用null，不用配置目标当作返回证明。

## 16件正式资源映射

下表文件均相对本项目根目录，目录为 `art/whole-game/fx/`。线性弹体默认向右（+X），旋转/移动由后续Unity逻辑处理，图片中无动态文案。

| 源Key | 文件 | 世界用途 |
| --- | --- | --- |
| ToNearestSkill | skill-nearest.png | 玉金飞剑，近敌投射 |
| BothSideSkill | skill-bothside.png | 成对弧月斩纹理；单一装饰纹理，不新增玩法投射次数 |
| BouncingSkill | skill-bouncing.png | 青玉珠，反弹弹体 |
| ChainSkill | skill-chain.png | 金白彗星，连锁寻敌 |
| CircularAttackSkill | skill-circle.png | 太极波弹；基本/进化发射数量按源Cast |
| CircularMotionSkill | skill-orbit.png | 绕身葫芦法器 |
| FourCornerSkill | skill-fourcorner.png | 朱砂符，四角投射 |
| InsideScopeSkill | skill-scope.png | 八卦范围环，中心透明 |
| RandomSkill | skill-random.png | 桃瓣命中印记，目标处淡出 |
| BlueMagic | enemy-blue.png | 深青蓝旋流敌弹 |
| PinkMagic | enemy-pink.png | 桃粉莲形敌弹 |
| RedMagic | enemy-red.png | 朱红火焰敌弹 |
| GreenMagic | enemy-green.png | 深青藤叶敌弹 |
| SnowMagic | enemy-snow.png | 霜雪六角敌弹 |
| Suck | pickup-suck.png | 吸取全场经验的玉环拾取物 |
| Prop | prop-urn.png | 可破灵瓮，地图20个实例可共用 |

精英共用 `art/whole-game/fx/elite-halo.png`，与skill-scope.png逐字节相同，单独记录复用关系；建议Unity材质金色状态 `#E7BA54`，此颜色未烘焙进PNG。文件存在与SHA已绑定 `docs/whole-game/enemies.json` 的六精英key。

## 切片方法和像素保证

原名义4×4格为384×256，但飞剑尖已穿过x384名义线，范围环和末行纹理也超出名义格。没有直接按4×4硬切。

实际归属行边为 `[0,256,520,758,1024]`；每行独立列边：

1. `[0,438,803,1150,1536]`
2. `[0,416,786,1150,1536]`
3. `[0,383,764,1150,1536]`
4. `[0,415,792,1174,1536]`

这些边从实际透明Alpha谷与完整轮廓选定。16个矩形覆盖原生画布且互不重叠；整张原图的非零Alpha像素逐个只归属一次，没有“只取最大组件”、漏掉粒子或裁断尾迹。8连通组件按Alpha>8且面积≥64检查，跨归属组件为0。每个原生矩形仅平移到512透明画布，所有RGBA像素逐字节复核相同。

源Alpha数值总和 **81,406,827**，16输出数值总和 **81,406,827**，非零像素数量同样相等。16件在各自512画布最外沿Alpha>8像素均为0。原生Alpha范围0–254，保留模型原有近不透明主体/透明辉光；没有将254重写成255或把有色透明像素当作实底。

精确cropXYXY、原生裁片尺寸、placementXY、可见BBox、Pivot、哈希和来源见 `docs/whole-game/world-combat-slices.json` 及每图 `.png.derivation.json`。

## 原始图集检查的FAIL/WARN

`docs/production/world-combat-v1-qc/sheet-qc.json`是按名义均分格检测的原始报告，status仍为fail，没有被删改或写成通过。全部非pass项原样列出；files均为 `art/whole-game/sheets/world-combat-v1.png`。

| id | status | value | threshold | files |
| --- | --- | --- | --- | --- |
| cross_cell_components | fail | 4 | 0 | art/whole-game/sheets/world-combat-v1.png |
| cross_cell_visible | fail | 5 | 0 | art/whole-game/sheets/world-combat-v1.png |
| boundary_band | warn | 815 | 0 | art/whole-game/sheets/world-combat-v1.png |
| safe_frame | warn | 15 | 0 | art/whole-game/sheets/world-combat-v1.png |
| faint_specks | warn | {"floor_px":344286,"detached_components":18} | 0 | art/whole-game/sheets/world-combat-v1.png |

解决方式是采用上列归属矩形，而非均分格。原始弱Alpha光晕与零散粒子保持，仍作为来源品质备注；不声称用无损切片消除了原图的弱Alpha噪声。正式切片的0跨界、0可见触边和像素守恒是另一次有明确方法的检查。

## 实际视觉验收与Unity建议

已实际查看原生图集和全部16件的深浅底总览，确认飞剑剑尖完整、各粒子/光尾归属正确，无相邻素材混入；葫芦、符、玉珠和破坏物轮廓清楚，范围环/命中印记中心留透。五敌弹保留明显形状和色相区别。低Alpha外光在两种底色下保持柔和，未见矩形背景块。记录与当前图片SHA绑定于 `docs/whole-game/world-combat-visual-review.json`。

查看：`designs/whole-game/world-combat-review-light.png` 与 `world-combat-review-dark.png`。总览仅对已有PNG缩小排版，没有生成新美术，也不是Unity运行截图。

导入建议：Sprite(Single)、FullRect、sRGB、Bilinear、Clamp、MipMaps关闭，Border全0；透明裁片使用完整512画布。普通FX/Pickup Pivot `[0.5,0.5]`，Prop按可见底部计算为 `[0.5,0.314453]`。实际PPU、碰撞体、弹道角度、SpriteRenderer排序、范围环大小/透明度及材质色需下一阶段在Unity验证。

九进化技能可复用这九份攻击纹理，按 `docs/whole-game-art-audit.md` 核实的CD/速度/数量/面积变化展示。切片本身不新增攻击逻辑，也未实现Shader/C#。所有状态时序和效果叠层的实机验证仍属于下一阶段。
