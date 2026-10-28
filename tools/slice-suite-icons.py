"""Slice the adopted 16-icon native-alpha atlas by verified ownership rectangles.

This is deterministic crop + transparent padding, not AI editing or upscaling.
Dependencies: Pillow, numpy, scipy (available in the configured Forge runtime).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import struct
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["Might", "Armor", "HPMax", "Recovery", "Cooldown", "Area", "SkillSpeed", "Duration",
        "Amount", "MoveSpeed", "Magnet", "Growth", "Greed", "Curse", "Gold", "Exp"]
LABELS = ["道法", "护甲", "气血上限", "回复", "冷却", "范围", "弹速", "持续",
          "数量", "身法", "拾取范围", "经验增益", "金币增益", "诅咒", "金币", "经验"]
ROW_EDGES = [0, 319, 632, 928, 1254]
COLUMN_EDGES = [[0, 339, 658, 949, 1254], [0, 324, 653, 970, 1254],
                [0, 327, 645, 964, 1254], [0, 354, 659, 961, 1254]]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def file_times(source: Path):
    utc = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc)
    try:
        return {"lastWriteTimeUtc": utc.isoformat(), "lastWriteTimeNewYork": utc.astimezone(ZoneInfo("America/New_York")).isoformat(),
                "method": "stat mtime + IANA America/New_York conversion"}
    except ZoneInfoNotFoundError:
        if os.name != "nt":
            raise
        literal = str(source).replace("'", "''")
        command = ("$f=Get-Item -LiteralPath '"+literal+"'; $z=[TimeZoneInfo]::FindSystemTimeZoneById('Eastern Standard Time'); "
                   "[pscustomobject]@{lastWriteTimeUtc=$f.LastWriteTimeUtc.ToString('o'); "
                   "lastWriteTimeNewYork=[TimeZoneInfo]::ConvertTime([DateTimeOffset]$f.LastWriteTimeUtc,$z).ToString('o'); "
                   "creationTimeUtc=$f.CreationTimeUtc.ToString('o'); method='PowerShell filesystem UTC timestamps + Windows Eastern Standard Time alias for America/New_York, including DST'} | ConvertTo-Json -Compress")
        return json.loads(subprocess.check_output(["powershell.exe", "-NoProfile", "-Command", command], text=True, encoding="utf-8-sig").strip())


def png_chunks(path: Path):
    data = path.read_bytes()
    cursor = 8
    chunks = []
    while cursor < len(data):
        size = int.from_bytes(data[cursor:cursor+4], "big")
        kind = data[cursor+4:cursor+8].decode("ascii")
        body = data[cursor+8:cursor+8+size]
        chunks.append((kind, body))
        cursor += size + 12
    return chunks


def read_cbor(data: bytes, position=0):
    """Small read-only decoder for extracting unsigned C2PA assertions, not trust verification."""
    initial = data[position]
    position += 1
    major, ai = initial >> 5, initial & 31
    if ai < 24:
        value = ai
    elif ai in (24, 25, 26, 27):
        count = {24: 1, 25: 2, 26: 4, 27: 8}[ai]
        value = int.from_bytes(data[position:position+count], "big")
        position += count
    else:
        raise ValueError("Indefinite or unsupported CBOR value")
    if major == 0:
        return value, position
    if major == 1:
        return -1-value, position
    if major in (2, 3):
        raw = data[position:position+value]
        return (raw if major == 2 else raw.decode("utf-8")), position+value
    if major == 4:
        result = []
        for _ in range(value):
            item, position = read_cbor(data, position)
            result.append(item)
        return result, position
    if major == 5:
        result = {}
        for _ in range(value):
            key, position = read_cbor(data, position)
            item, position = read_cbor(data, position)
            result[key] = item
        return result, position
    if major == 6:
        item, position = read_cbor(data, position)
        return item, position
    if major == 7:
        if ai == 20:
            return False, position
        if ai == 21:
            return True, position
        if ai == 22:
            return None, position
        if ai in (26, 27):
            return struct.unpack(">f" if ai == 26 else ">d", value.to_bytes(4 if ai == 26 else 8, "big"))[0], position
        return value, position
    raise ValueError("Unsupported CBOR major type")


def c2pa_summary(path: Path):
    records = []
    for kind, body in png_chunks(path):
        if kind != "caBX":
            continue
        parsed = []

        def boxes(payload):
            cursor = 0
            while cursor+8 <= len(payload):
                length = int.from_bytes(payload[cursor:cursor+4], "big")
                box_kind = payload[cursor+4:cursor+8]
                if length < 8 or cursor+length > len(payload):
                    break
                content = payload[cursor+8:cursor+length]
                if box_kind == b"jumb":
                    boxes(content)
                elif box_kind == b"cbor":
                    try:
                        obj, _ = read_cbor(content)
                        if isinstance(obj, dict) and "actions" in obj:
                            parsed.extend(obj["actions"])
                    except (ValueError, IndexError, UnicodeDecodeError, TypeError):
                        pass
                cursor += length
        boxes(body)
        records.append({"container": "PNG caBX/JUMBF", "bytes": len(body),
                        "sha256": hashlib.sha256(body).hexdigest(), "actions": parsed,
                        "cryptographicSignatureValidated": False,
                        "note": "Read embedded assertion fields only; generic gpt-image does not identify a backend snapshot or quality."})
    return {"present": bool(records), "manifests": records, "backendModelDisclosed": False,
            "qualityDisclosed": False, "signatureValidationStatus": "未执行签名及信任链验证"}


def main(source: Path, atlas="attribute"):
    if atlas == "combat":
        slug = "combat-icons-v2"
        manifest_name = "icon-atlas2-slices.json"
        keys = ["BothSideSkill", "BouncingSkill", "ChainSkill", "CircularAttackSkill", "CircularMotionSkill", "FourCornerSkill", "InsideScopeSkill", "RandomSkill", "ToNearestSkill", "TreasureClosed", "TreasureOpen", "MoneyBag", "Healing", "Burn", "Freeze", "Slow"]
        names = ["skill-bothside", "skill-bouncing", "skill-chain", "skill-circle", "skill-orbit", "skill-fourcorner", "skill-scope", "skill-random", "skill-nearest", "treasure-closed", "treasure-open", "moneybag", "healing", "buff-burn", "buff-freeze", "buff-slow"]
        labels = ["双向道法", "弹跳道法", "连锁道法", "环形攻击", "环绕法器", "四向符法", "区域法阵", "随机投射", "追踪飞剑", "未开宝箱", "已开宝箱", "钱袋", "回复物", "灼烧", "冰冻", "减速"]
        row_edges = [0, 323, 616, 914, 1254]
        column_edges = [[0, 326, 634, 915, 1254], [0, 334, 622, 940, 1254], [0, 320, 627, 933, 1254], [0, 322, 618, 929, 1254]]
    else:
        slug, manifest_name, keys, labels = "attribute-icons-v2", "icon-atlas1-slices.json", KEYS, LABELS
        names = [("attr-"+key.lower()) if key not in ("Gold", "Exp") else key.lower() for key in keys]
        row_edges, column_edges = ROW_EDGES, COLUMN_EDGES
    sheet_path = ROOT / ("art/sheets/"+slug+".png")
    icon_dir = ROOT / "art/icons"
    icon_dir.mkdir(parents=True, exist_ok=True)
    sheet_path.parent.mkdir(parents=True, exist_ok=True)
    if sheet_path.exists() and sha(sheet_path) != sha(source):
        raise SystemExit("Refusing to replace a different adopted sheet")
    shutil.copy2(source, sheet_path)
    image = Image.open(sheet_path)
    if image.size != (1254, 1254) or image.mode != "RGBA":
        raise SystemExit("This adopted ownership map is valid only for the inspected 1254x1254 RGBA sheet")
    alpha = np.asarray(image.getchannel("A"))
    visible = alpha > 8
    component_labels, component_count = ndimage.label(visible, structure=np.ones((3, 3)))
    owner_map = np.full(alpha.shape, -1, dtype=np.int16)
    rectangles = []
    for row in range(4):
        for column in range(4):
            rect = (column_edges[row][column], row_edges[row], column_edges[row][column+1], row_edges[row+1])
            rectangles.append(rect)
            owner_map[rect[1]:rect[3], rect[0]:rect[2]] = row*4+column
    crossing = []
    sizes = np.bincount(component_labels.ravel())
    for number in range(1, component_count+1):
        if sizes[number] < 64:
            continue
        owners = np.unique(owner_map[component_labels == number])
        if len(owners) != 1:
            crossing.append({"label": number, "area": int(sizes[number]), "owners": owners.tolist()})
    if crossing:
        raise SystemExit("Ownership map crosses visible icon components: " + json.dumps(crossing))
    files = []
    alpha_total = 0
    for index, (key, rect) in enumerate(zip(keys, rectangles)):
        crop = image.crop(rect)
        crop_alpha = np.asarray(crop.getchannel("A"))
        ys, xs = np.nonzero(crop_alpha > 8)
        box = (int(xs.min()), int(ys.min()), int(xs.max()+1), int(ys.max()+1))
        offset = (round(256-(box[0]+box[2])/2), round(256-(box[1]+box[3])/2))
        if offset[0] < 0 or offset[1] < 0 or offset[0]+crop.width > 512 or offset[1]+crop.height > 512:
            raise SystemExit("Native ownership crop does not fit the declared 512 canvas: " + key)
        output = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        output.paste(crop, offset)  # Direct byte placement, no mask/compositing or alpha modification.
        target = icon_dir / names[index]
        target = target.with_suffix(".png")
        output.save(target)
        check = np.asarray(Image.open(target))
        if not np.array_equal(check[offset[1]:offset[1]+crop.height, offset[0]:offset[0]+crop.width], np.asarray(crop)):
            raise SystemExit("Pixel preservation check failed: " + key)
        alpha_total += int(check[:, :, 3].sum(dtype=np.uint64))
        record = {"file": relative(target), "key": key, "label": labels[index], "sha256": sha(target),
                  "canvas": [512, 512], "mode": "RGBA", "alphaExtrema": list(output.getchannel("A").getextrema()),
                  "derivedFrom": {"file": relative(sheet_path), "sha256": sha(sheet_path),
                                  "generationRecord": relative(sheet_path)+".generation.json"},
                  "operation": {"kind": "native crop + transparent padding", "cropRectXYXY": list(rect),
                                "placementXY": list(offset), "nativeCropSize": list(crop.size),
                                "visibleAlphaGreaterThan8BBoxInCrop": list(box), "resampled": False,
                                "alphaModified": False, "sourcePixelsPreserved": True,
                                "componentFiltering": "none; all source alpha pixels retained"},
                  "pivot": [0.5, 0.5], "spriteTypeRecommendation": "Single", "borderLTRB": [0, 0, 0, 0],
                  "actualModel": None, "actualQuality": None,
                  "modelEvidence": "Follow source atlas generation record; this derivative did not call an image model.",
                  "validation": {"canvasEdgePixelsWithAlphaGreaterThan8": int(np.count_nonzero(check[0,:,3]>8)+np.count_nonzero(check[-1,:,3]>8)+np.count_nonzero(check[:,0,3]>8)+np.count_nonzero(check[:,-1,3]>8)),
                                 "pixelCopyMatchesSource": True, "ownershipComponentCrossings": 0}}
        save_json(target.with_name(target.name+".derivation.json"), record)
        files.append(record)
    if alpha_total != int(alpha.sum(dtype=np.uint64)):
        raise SystemExit("Atlas alpha conservation failed")
    raw_qc_path = ROOT / ("docs/production/"+slug+"-qc/sheet-qc.json")
    raw_qc = json.loads(raw_qc_path.read_text(encoding="utf-8"))
    reported = [{"id": c["id"], "status": c["status"], "value": c["value"], "threshold": c["threshold"],
                 "files": [relative(sheet_path)]} for c in raw_qc["checks"] if c["status"] in ("warn", "fail")]
    manifest = {"schemaVersion": 1, "sheet": relative(sheet_path), "sheetSha256": sha(sheet_path),
                "nativeSize": list(image.size), "art_source": "host_image", "route": "builtin image_gen",
                "gridRounding": "Generated icons overflow nominal 4x4; row-specific ownership rectangles used instead of equal-grid cuts.",
                "rawSheetQC": {"status": raw_qc["status"], "record": relative(raw_qc_path), "reportedChecks": reported},
                "slicedAssetQC": {"status": "passed_pixel_and_ownership_checks", "componentAlphaThreshold": 8,
                                  "componentMinArea": 64, "componentCrossings": crossing,
                                  "allSourceAlphaPixelsAssignedExactlyOnce": True, "sumAlphaSource": int(alpha.sum(dtype=np.uint64)),
                                  "sumAlphaOutputs": alpha_total, "resampling": "none", "matteCleaning": "none; faint native alpha is preserved",
                                  "remainingLimit": "Numeric isolation does not establish visual identity. Review on light/dark backgrounds is required."},
                "files": files}
    save_json(ROOT / ("docs/"+manifest_name), manifest)
    font_path = ROOT / "Assets/DaoSurvivor/Resources/Fonts/NotoSansSC-Regular.otf"
    font = ImageFont.truetype(str(font_path), 18)
    for label, bg in (("light", (245, 238, 213, 255)), ("dark", (22, 48, 42, 255))):
        board = Image.new("RGBA", (1024, 1120), bg)
        draw = ImageDraw.Draw(board)
        for i, entry in enumerate(files):
            tile = Image.open(ROOT / entry["file"]).resize((256, 256), Image.Resampling.LANCZOS)
            x, y = i % 4*256, i // 4*280
            board.alpha_composite(tile, (x, y))
            draw.text((x+128, y+246), entry["label"], fill=(39, 78, 55, 255) if label == "light" else (238, 224, 181, 255), font=font, anchor="mt")
        board.convert("RGB").save(ROOT / ("art/sheets/"+slug+"-review-"+label+".png"))
    times = file_times(source)
    prompt_path = ROOT / ("docs/production/"+slug+".prompt.txt")
    config_path = Path(r"F:\work\image\config\image-generation.json")
    refs = [Path(r"F:\work\image\designs\mail-ui-v1\01-mail-event.png"), Path(r"F:\work\image\designs\team-ui-v2\team-ui-v2.png")]
    if atlas == "combat":
        refs.append(Path(r"C:\Users\luyua\.codex\generated_images\01a17784-7bd6-7ee0-b3b0-353fcf2e1606\exec-cdcbf1d9-d1db-47a9-a704-76f9b7795cb7.png"))
    output_hint = (f"Generated images are saved to {source.parent} as {source} by default.\n"
                   "If you need to use a generated image at another path, copy it and leave the original in place unless the user explicitly asks you to delete it.\n"
                   "The generated image is already displayed to the user. There is no need to render it in the final response as a Markdown image or file link.")
    receipt_path = ROOT / ("docs/production/"+slug+".receipt.json")
    receipt = {"tool": "image_gen__imagegen", "submittedArguments": {"prompt": prompt_path.read_bytes().decode("utf-8-sig"),
               "referenced_image_paths": [str(p) for p in refs], "transparent_background": True},
               "returnedFields": ["image_url", "output_hint"], "output_hint": output_hint,
               "image_url": "Data URL omitted; adopted native output is preserved byte-for-byte in art/sheets.",
               "actualModel": None, "actualQuality": None, "sourceArtifact": str(source),
               "sourceArtifactFileTimes": times, "c2pa": c2pa_summary(source)}
    save_json(receipt_path, receipt)
    generation = {"schemaVersion": 1, "file": sheet_path.name, "projectRelativeOutput": relative(sheet_path),
                  "absoluteOutput": str(sheet_path), "sha256": sha(sheet_path), "bytes": sheet_path.stat().st_size,
                  "generatedAt": times["lastWriteTimeNewYork"], "generatedAtUtc": times["lastWriteTimeUtc"],
                  "generatedAtBasis": "Original host output LastWriteTimeUtc converted to America/New_York; file persistence evidence, not verified backend job duration.",
                  "width": image.width, "height": image.height, "format": "PNG", "mode": "RGBA",
                  "alphaExtrema": list(image.getchannel("A").getextrema()), "transparent": True,
                  "tool": "image_gen__imagegen", "route": "builtin", "art_source": "host_image",
                  "configSnapshot": json.loads(config_path.read_text(encoding="utf-8-sig")),
                  "configSnapshotEvidence": {"file": str(config_path), "sha256": sha(config_path)},
                  "submittedParameters": {"model": None, "quality": None, "transparent_background": True,
                                          "referenced_image_paths": [str(p) for p in refs], "promptFile": relative(prompt_path)},
                  "actualModel": None, "actualQuality": None,
                  "unverifiedReason": "宿主管理，工具未披露具体型号与质量；通用C2PA gpt-image标签不能证明Sunburst分支或max。",
                  "prompt": relative(prompt_path), "promptSha256": sha(prompt_path),
                  "references": [{"file": str(p), "sha256": sha(p), "purpose": "道家Q版高清手绘风格参考"} for p in refs],
                  "evidence": {"receipt": relative(receipt_path), "receiptSha256": sha(receipt_path),
                               "sourceArtifact": str(source), "sourceArtifactSha256": sha(source),
                               "toolReturnFields": ["image_url", "output_hint"], "c2pa": receipt["c2pa"]},
                  "officialVerification": {"verifiedOn": "2026-10-26", "performedBy": "parent/root before generation",
                                           "modelTarget": "gpt-image-2.5-sunburst", "qualityTarget": "max",
                                           "sources": ["https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst",
                                                       "https://developers.openai.com/api/reference/resources/images/methods/generate"],
                                           "scope": "Configuration capability only, not this call's actual model/quality evidence"},
                  "operation": {"kind": "byte-for-byte adoption", "sourceBytesEqualOutput": sha(source) == sha(sheet_path),
                                "crop": None, "resize": None, "nativeOutputPreserved": True},
                  "qc": {"rawNominalGrid": "failed; do not cut equal 4x4 cells", "rawQCRecord": relative(raw_qc_path),
                         "adoptedSlicing": "row-specific native ownership rectangles; all source pixels conserved", "sliceManifest": "docs/"+manifest_name}}
    save_json(sheet_path.with_name(sheet_path.name+".generation.json"), generation)
    print(json.dumps({"files": len(files), "sheetNativeSize": list(image.size), "sheetSha256": sha(sheet_path),
                      "allSourceAlphaPixelsAssignedExactlyOnce": True, "rawSheetStatus": raw_qc["status"],
                      "sliceStatus": "passed_pixel_and_ownership_checks", "c2paActions": sum(len(m["actions"]) for m in receipt["c2pa"]["manifests"])}, ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--atlas", choices=("attribute", "combat"), default="attribute")
    args = parser.parse_args()
    main(args.source.resolve(), args.atlas)
