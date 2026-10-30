# 一炁当千 · UI 美术验收记录

2026-10-29。本记录验收正式品牌同步后的 UI 整屏、控件、图标与排版；整款游戏角色、敌人、场景和动画资源验收见另行总账。

## 本批结果

- 52/52张1920×1080整屏／状态／流程画面及相应布局JSON已导出；0缺图、0脚本异常、0文字出画布。
- 全52屏分别检查1280×720及2560×1080视口，共104次等比安全区检查；与52次基准合计156次。通过的是浏览器美术预览适配，不是Unity适配。
- 查看全部7张汇总；本批另查看01、02、04、05、25、40、51、52原尺寸图。52屏正式名称和Logo资源映射一致，中文无缺字，页眉、启动卡片和战斗页脚未遮挡控件。独立视觉记录绑定当前哈希；旧屏哈希保存在pre-brand历史目录。
- 原88项UI资源字节不变，另纳入8项正式品牌资源；旧未选用Logo仅保留为来源，不作为正式UI。当前UI资源回执为accepted-ui-branded-resource-receipt.json。
- 15张控件状态PNG哈希、画布及Alpha核验通过；三类控件各普通/按下/选中/禁用/锁定画布与Pivot一致。
- Noto字体OpenType cmap覆盖本批全部非空白字符，无缺字。动态文字单独排版，不烘焙在控件底图。
- 源业务审查F01–F05已修复；新道法与已持有HUD不再重复，30御剑背景等级与4→5一致。被动上限5、主动11、宝箱全收与待宝箱进化条件保持准确。

## 原图集QC的原始失败与警告（保留，不改写成通过）

模型原图不满足等分4×4切图合同，禁止直接按等格切片。最终采用逐行Alpha谷值定义的归属矩形，原生裁切后补透明画布；没有缩放、清边或AI修图。最终32张独立图标的所有源Alpha像素恰好归属一次，无跨归属主要连通块，明暗底检查通过。细微原生Alpha散点仍保留。

| 原图 | 检查ID | 原始状态 | value（原值） | threshold（原值） |
| --- | --- | --- | --- | --- |
| `art/sheets/attribute-icons-v2.png` | `cross_cell_components` | **fail** | `10` | `0` |
| `art/sheets/attribute-icons-v2.png` | `cross_cell_visible` | **fail** | `11` | `0` |
| `art/sheets/attribute-icons-v2.png` | `boundary_band` | **warn** | `2929` | `0` |
| `art/sheets/attribute-icons-v2.png` | `safe_frame` | **warn** | `16` | `0` |
| `art/sheets/attribute-icons-v2.png` | `faint_specks` | **warn** | `{"floor_px":138655,"detached_components":40}` | `0` |
| `art/sheets/combat-icons-v2.png` | `cross_cell_components` | **fail** | `5` | `0` |
| `art/sheets/combat-icons-v2.png` | `cross_cell_visible` | **fail** | `5` | `0` |
| `art/sheets/combat-icons-v2.png` | `boundary_band` | **warn** | `567` | `0` |
| `art/sheets/combat-icons-v2.png` | `safe_frame` | **warn** | `16` | `0` |
| `art/sheets/combat-icons-v2.png` | `faint_specks` | **warn** | `{"floor_px":200309,"detached_components":40}` | `0` |

完整原始结构、受影响路径与归属切片验收：

```json
[
  {
    "sheet": "art/sheets/attribute-icons-v2.png",
    "rawSheetQC": {
      "status": "fail",
      "record": "docs/production/attribute-icons-v2-qc/sheet-qc.json",
      "reportedChecks": [
        {
          "id": "cross_cell_components",
          "status": "fail",
          "value": 10,
          "threshold": 0,
          "files": [
            "art/sheets/attribute-icons-v2.png"
          ]
        },
        {
          "id": "cross_cell_visible",
          "status": "fail",
          "value": 11,
          "threshold": 0,
          "files": [
            "art/sheets/attribute-icons-v2.png"
          ]
        },
        {
          "id": "boundary_band",
          "status": "warn",
          "value": 2929,
          "threshold": 0,
          "files": [
            "art/sheets/attribute-icons-v2.png"
          ]
        },
        {
          "id": "safe_frame",
          "status": "warn",
          "value": 16,
          "threshold": 0,
          "files": [
            "art/sheets/attribute-icons-v2.png"
          ]
        },
        {
          "id": "faint_specks",
          "status": "warn",
          "value": {
            "floor_px": 138655,
            "detached_components": 40
          },
          "threshold": 0,
          "files": [
            "art/sheets/attribute-icons-v2.png"
          ]
        }
      ]
    },
    "slicedAssetQC": {
      "status": "passed_pixel_ownership_and_visual_review",
      "componentAlphaThreshold": 8,
      "componentMinArea": 64,
      "componentCrossings": [],
      "allSourceAlphaPixelsAssignedExactlyOnce": true,
      "sumAlphaSource": 158550184,
      "sumAlphaOutputs": 158550184,
      "resampling": "none",
      "matteCleaning": "none; faint native alpha is preserved",
      "remainingLimit": "Unity import/device rendering remains unverified; native faint alpha specks are intentionally retained."
    }
  },
  {
    "sheet": "art/sheets/combat-icons-v2.png",
    "rawSheetQC": {
      "status": "fail",
      "record": "docs/production/combat-icons-v2-qc/sheet-qc.json",
      "reportedChecks": [
        {
          "id": "cross_cell_components",
          "status": "fail",
          "value": 5,
          "threshold": 0,
          "files": [
            "art/sheets/combat-icons-v2.png"
          ]
        },
        {
          "id": "cross_cell_visible",
          "status": "fail",
          "value": 5,
          "threshold": 0,
          "files": [
            "art/sheets/combat-icons-v2.png"
          ]
        },
        {
          "id": "boundary_band",
          "status": "warn",
          "value": 567,
          "threshold": 0,
          "files": [
            "art/sheets/combat-icons-v2.png"
          ]
        },
        {
          "id": "safe_frame",
          "status": "warn",
          "value": 16,
          "threshold": 0,
          "files": [
            "art/sheets/combat-icons-v2.png"
          ]
        },
        {
          "id": "faint_specks",
          "status": "warn",
          "value": {
            "floor_px": 200309,
            "detached_components": 40
          },
          "threshold": 0,
          "files": [
            "art/sheets/combat-icons-v2.png"
          ]
        }
      ]
    },
    "slicedAssetQC": {
      "status": "passed_pixel_ownership_and_visual_review",
      "componentAlphaThreshold": 8,
      "componentMinArea": 64,
      "componentCrossings": [],
      "allSourceAlphaPixelsAssignedExactlyOnce": true,
      "sumAlphaSource": 148193277,
      "sumAlphaOutputs": 148193277,
      "resampling": "none",
      "matteCleaning": "none; faint native alpha is preserved",
      "remainingLimit": "Native faint haze/specks preserved; Unity runtime import and display validation are pending the next phase. A 512x512 canvas is padded native content, not newly generated 512x512 detail."
    }
  }
]
```

## 边界与下一阶段

本批屏幕是浏览器DOM/CSS、已有PNG与独立文本的合成设计图，不是模型新生成整屏，也不是Unity运行截图。图标512×512是原生裁切后补透明画布，不能当成新生成的512像素内容细节。生成模型/质量未由入口披露的字段仍为未确认。

Unity Sprite导入、九宫格、字体图集、Prefab、业务状态、存档、输入和设备显示尚未执行；Border/Pivot等均为有来源记录的接入建议。战斗中的静态人物及场景板不构成全部角色/敌人动作验收。

F盘美术库只读，关联记录已集中在本项目 `docs/image-reference-associations.md`。未进行Git提交、推送、发布或付费路线切换。

[UI总清单](UI_COVERAGE.md) · [逐屏视觉记录](final-visual-review.json) · [渲染记录](render-verification.json) · [Unity导入建议](UNITY_ART_IMPORT.md)
