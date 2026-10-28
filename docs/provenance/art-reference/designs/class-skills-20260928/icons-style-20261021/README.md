# 四脉真诀 · 技能图标风格与功能重绘

本轮重绘四个职业的32个技能图标，技能名称、规则与数值以[技能目录](../catalog.json)为准。使用内置 `image_gen.imagegen` 逐张生成，统一承接[邮件UI](../../mail-ui-v1/01-mail-event.png)与[组队UI](../../team-ui-v2/team-ui-v2.png)的玉绿、象牙绢底、细暖金边、柔和云纹和圆润手绘质感。

图标按实际功能组织画面：单体攻击有明确攻击方向，群攻有多个分离落点，减速有冰霜或束足，治疗有恢复流，防御有挡击护环；被动则以稳定的护心镜、锋刃、生命珠、法力容器和轻履等表达对应属性。每职业前5项主动、后3项被动。

- [160px整套总览](qa/overview-160.png)
- [38px窄屏列表检查](qa/overview-38.png)
- [45px窄屏战斗图标检查](qa/overview-45.png)
- [50px列表检查](qa/overview-50.png)
- [60px战斗图标检查](qa/overview-60.png)
- [74px扩展尺寸检查](qa/overview-74.png)
- [288px细节检查](qa/overview-288.png)
- [32图与技能含义映射](manifest.json)
- [文件、哈希与来源检查](validation.json)
- [客户端安装清单与保留的GUID](installation.json)

## 来源与型号记录

每张正式原生图保存在 `icons/<ID>.png`，对应 `icons/<ID>.png.generation.json`；实际完整提示词见 `prompts/`，工具文字回执见 `records/`。生成记录中的 `prompt` 和 `evidence` 指向该图实际采用的调用；少数图为单独修正外圆角后的AI编辑版本，编辑前的哈希和文字记录保留。

配置目标为 GPT Image 2.5 Sunburst / max；工具未开放型号与质量选择器，也未返回可核实型号/质量，因此实际值记录为 `null`。配置目标及提示词不代表已锁定实际API分支。每图保留当次配置快照。

`style-anchor.png` 是本套共同实际附入的风格参考，与其独立来源记录一起保留。最终1101另经AI编辑修正外角。其他图记录中的 `submittedPath` 保留调用时的输入路径，`file` 指向仍可读取的同一原始锚点，SHA256可核对。

正式PNG原样复制到上级 `icons/` 和客户端 `Assets/Resources/UI/Skills/`，客户端 `.meta` 保持字节不变。旧图的生成记录、提示词和回执以文字保存在 `records/replaced-icons-source-records.json`，未另存旧图片。

## 检查与接入

2026-10-22追加按当前客户端几何复查：技能列表为50px、战斗图标为60px；1920宽屏相对2560设计宽缩放后约为38px和45px。复查仅发现1208「云篆护心」的浅色护心玉在小尺寸中不够清楚，已用内置AI编辑改为深玉绿色并加强护盾轮廓，保留浅绢底、细边框和挡击效果。其余31图的技能语义和缩小轮廓可区分。旧图的来源文字保存在 `records/1208-before-contrast-20261022.generation.json`，本次独立提示词和回执以 `1208-contrast-20261022` 命名。

`finalize.py --install --actual-sizes` 核验32个唯一原生正方形PNG、逐图SHA256、实际生成来源、提示词和回执，再复制到设计预览及客户端，并补齐38/45/50/60px实际尺寸检查图。检查图仅将正式PNG缩小排列，不回写正式图，不把缩放结果当作新生成素材。

客户端原生导入和预览入口为 `SkillIconStyleVerification.Capture`。2026-10-22已在Unity 6000.6.0f1验证：32张全部导入为Sprite，32个GUID及.meta字节保持，设计/客户端PNG哈希一致。四职业技能书与战斗选技在1920×1080、2560×1080下共导出10张有效截图，输出位于客户端 `Docs/VerificationEvidence/skill-icons-style-20261021/`，详见[原生回执](../../../../mmorpg-client/Docs/VerificationEvidence/skill-icons-style-20261021/native-import-capture.json)。预览使用编辑器样例，不表示在线服务端战斗验收。
