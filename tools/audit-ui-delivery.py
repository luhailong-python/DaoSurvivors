"""Read-only verification of the accepted UI batch; writes audit records only."""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/ui-suite/current-delivery-audit.json"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest = read("docs/ui-suite/accepted-ui-resource-receipt.json")
    current_manifest = read("art/manifest.json")
    review = read("docs/ui-suite/final-visual-review.json")
    coverage = read("docs/ui-suite/UI_COVERAGE.json")
    issues = []
    files = []
    screens = []
    controls = defaultdict(list)
    assets = {item["file"]: item for item in manifest["assets"]}
    current_assets = {item["file"]: item for item in current_manifest["assets"]}
    for item in manifest["assets"]:
        path = ROOT / item["file"]
        result = {"file": item["file"], "exists": path.is_file()}
        if not path.is_file():
            issues.append({"id": "missing_manifest_asset", "file": item["file"]})
        else:
            result["sha256"] = sha(path)
            result["matchesAcceptedManifest"] = result["sha256"] == item.get("sha256")
            if not result["matchesAcceptedManifest"]:
                issues.append({"id": "manifest_hash_mismatch", "file": item["file"]})
            result["representedInCurrentManifest"] = item["file"] in current_assets
            result["currentManifestHashMatchesReceipt"] = current_assets.get(item["file"], {}).get("sha256") == item["sha256"]
            if not result["representedInCurrentManifest"] or not result["currentManifestHashMatchesReceipt"]:
                issues.append({"id": "current_manifest_ui_subset_changed", "file": item["file"]})
            if "dimensions" in item:
                with Image.open(path) as image:
                    result["dimensions"] = list(image.size)
                    result["mode"] = image.mode
                    if result["dimensions"] != item["dimensions"]:
                        issues.append({"id": "asset_dimensions_changed", "file": item["file"]})
                    if "alphaExtrema" in item:
                        result["alphaExtrema"] = list(image.getchannel("A").getextrema()) if "A" in image.getbands() else None
                        if result["alphaExtrema"] != item["alphaExtrema"]:
                            issues.append({"id": "asset_alpha_changed", "file": item["file"]})
            provenance = item.get("provenanceRecord")
            result["provenanceRecord"] = provenance
            result["provenanceRecordExists"] = bool(provenance and (ROOT / provenance).is_file())
            if not result["provenanceRecordExists"]:
                issues.append({"id": "missing_provenance_record", "file": item["file"], "record": provenance})
            if item.get("controlFamily"):
                controls[item["controlFamily"]].append({
                    "file": item["file"],
                    "state": item["controlState"],
                    "dimensions": result.get("dimensions"),
                    "pivot": item["unityImportAdvice"]["pivotNormalizedBottomLeft"],
                    "border": item["unityImportAdvice"]["borderLeftBottomRightTopPx"],
                })
        files.append(result)
    reviews = {item["id"]: item for item in review["screens"]}
    for item in coverage["screens"]:
        path = ROOT / item["screenPath"]
        layout_path = ROOT / item["layoutPath"]
        result = {"id": item["id"], "screen": item["screenPath"], "layout": item["layoutPath"]}
        accepted = reviews.get(item["id"])
        if not path.is_file() or not layout_path.is_file() or not accepted:
            issues.append({"id": "missing_screen_layout_or_review", "screen": item["id"]})
            screens.append(result)
            continue
        layout = read(item["layoutPath"])
        with Image.open(path) as image:
            result["dimensions"] = list(image.size)
        result["sha256"] = sha(path)
        result["matchesAcceptedReview"] = result["sha256"] == accepted["sha256"]
        result["matchesLayoutHash"] = result["sha256"] == layout["screenSha256"]
        result["missingAssets"] = [p for p in item["independentAssets"] if not (ROOT / p).is_file()]
        result["assetsOutsideUiManifest"] = [p for p in item["independentAssets"] if p not in assets]
        result["mappedAssetsEqualLayout"] = set(item["independentAssets"]) == set(layout["artSources"])
        result["brokenLayers"] = [x for x in layout["imageLayers"] if x.get("broken")]
        result["overflowText"] = layout["overflowText"]
        result["acceptanceStatus"] = item["acceptanceStatus"]
        for key in ("matchesAcceptedReview", "matchesLayoutHash", "mappedAssetsEqualLayout"):
            if not result[key]:
                issues.append({"id": key, "screen": item["id"], "value": False})
        for key in ("missingAssets", "assetsOutsideUiManifest", "brokenLayers", "overflowText"):
            if result[key]:
                issues.append({"id": key, "screen": item["id"], "value": result[key]})
        if result["dimensions"] != [1920, 1080]:
            issues.append({"id": "screen_dimensions", "screen": item["id"], "value": result["dimensions"]})
        screens.append(result)
    source_files = []
    for item in review["sourceFiles"]:
        path = ROOT / item["file"]
        result = {"file": item["file"], "exists": path.is_file(), "matchesAcceptedReview": path.is_file() and sha(path) == item["sha256"]}
        if not result["matchesAcceptedReview"]:
            issues.append({"id": "ui_preview_source_changed", "file": item["file"]})
        source_files.append(result)
    snapshots = []
    for item in read(manifest["sourceTextSnapshots"]):
        path = ROOT / item["snapshot"]
        result = {"file": item["snapshot"], "matchesAcceptedManifest": path.is_file() and sha(path) == item["sha256"]}
        if not result["matchesAcceptedManifest"]:
            issues.append({"id": "provenance_snapshot_changed_or_missing", "file": item["snapshot"]})
        snapshots.append(result)
    for family, states in controls.items():
        if {x["state"] for x in states} != {"normal", "pressed", "selected", "disabled", "locked"}:
            issues.append({"id": "control_states_incomplete", "family": family})
        for field in ("dimensions", "pivot", "border"):
            if len({tuple(x[field]) for x in states}) != 1:
                issues.append({"id": "control_state_geometry", "family": family, "field": field})
    contacts = sorted({item["contactSheet"] for item in review["screens"]})
    result = {
        "schemaVersion": 1,
        "recordedAtUtc": datetime.now(timezone.utc).isoformat(),
        "clientDate": "2026-10-28",
        "scope": "Accepted UI-only subset from docs/ui-suite/accepted-ui-resource-receipt.json, checked against disk and current art/manifest.json. Does not certify non-UI art, player animation or Unity execution.",
        "status": "accepted_ui_art_unchanged" if not issues else "requires_review",
        "summary": {
            "screens": len(screens), "layoutFiles": len(screens),
            "acceptedScreenHashesMatched": sum(x.get("matchesAcceptedReview", False) for x in screens),
            "manifestFiles": len(files),
            "uiSubsetReceipt": "docs/ui-suite/accepted-ui-resource-receipt.json",
            "currentWholeArtManifestFileCount": len(current_assets),
            "manifestHashesMatched": sum(x.get("matchesAcceptedManifest", False) for x in files),
            "deliveryRoles": dict(Counter(x["deliveryRole"] for x in manifest["assets"])),
            "stateFamilies": len(controls), "stateFiles": sum(map(len, controls.values())),
            "provenanceSnapshots": len(snapshots),
            "provenanceSnapshotHashesMatched": sum(x["matchesAcceptedManifest"] for x in snapshots),
            "missingFilesOrTechnicalIssues": len(issues),
        },
        "visualReview": {
            "method": "Viewed all seven existing contact sheets in this continuation; retained approved screen originals.",
            "contactSheets": contacts,
            "finding": "Consistent jade/ivory/gold frames, readable state hierarchy and aligned controls; no new layout defect observed at contact-sheet scale. Existing original-resolution reviews remain applicable because all accepted screen and preview-source hashes match.",
            "notRepeated": "No rerendering, no new responsive or Unity execution tests, no per-screen original-resolution re-review in this continuation.",
        },
        "limitations": [
            "Raw icon sheets retain recorded fail/warn results; approved ownership slicing is the formal resource route. Do not equal-grid slice originals.",
            "Native faint alpha specks remain; no cleaning or claimed new 512-pixel detail.",
            "Model and quality remain unconfirmed wherever the native image endpoint did not disclose them.",
            "UI acceptance uses an immutable 88-file resource receipt; the current art/manifest.json may also contain non-UI whole-game resources that this audit does not certify.",
            "Unity import, font atlases, nine-slice rendering, actual interactions and device execution are deferred by user instruction.",
        ],
        "recommendedDeliveryLinks": [
            "designs/ui-suite/preview/index.html", "designs/ui-suite/screens/", "designs/ui-suite/layouts/",
            "docs/ui-suite/UI_COVERAGE.md", "docs/ui-suite/ACCEPTANCE.md",
            "docs/ui-suite/UNITY_ART_IMPORT.md", "art/manifest.json", "docs/image-reference-associations.md",
        ],
        "issues": issues, "controlFamilies": dict(controls), "sourceFiles": source_files,
        "provenanceSnapshots": snapshots,
        "files": files, "screens": screens,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(OUT), "status": result["status"], "summary": result["summary"], "issues": issues}, ensure_ascii=False))


if __name__ == "__main__":
    main()
