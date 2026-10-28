"""Record rendered UI provenance and verify the current deliverable bytes. No AI call."""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from PIL import Image

root = Path(__file__).resolve().parents[1]
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sources = json.loads((root / "docs/ASSET_SOURCES.json").read_text(encoding="utf-8-sig"))
report = json.loads((root / "docs/verification/ui-preview.json").read_text(encoding="utf-8-sig"))
runtime_art = root / "Assets/DaoSurvivor/Resources/DaoArt"
art = []
errors = []
for path in sorted(runtime_art.glob("*.png")):
    with Image.open(path) as im:
        im.verify()
    with Image.open(path) as im:
        art.append({"file": path.relative_to(root).as_posix(), "sha256": digest(path),
                    "size": list(im.size), "mode": im.mode,
                    "alphaExtrema": list(im.getextrema()[-1]) if im.mode == "RGBA" else None,
                    "generationRecord": path.name + ".generation.json" if path.with_name(path.name + ".generation.json").exists() else "docs/ASSET_SOURCES.json"})
for record in sources["assets"] + sources.get("generatedAssets", []):
    path = root / record["output"]
    if not path.exists() or digest(path) != record["sha256"]:
        errors.append("Source mapping mismatch: " + record["output"])
renderer = []
for name in ("docs/preview/index.html", "docs/preview/style.css", "docs/preview/preview.js", "tools/capture-ui.cjs"):
    path = root / name
    renderer.append({"file": name, "sha256": digest(path)})
frames = []
for record in report["records"]:
    path = root / record["file"]
    with Image.open(path) as im:
        if im.size != (1920, 1080):
            errors.append("Unexpected preview dimensions: " + record["file"])
    if digest(path) != record["sha256"]:
        errors.append("Stale render hash: " + record["file"])
    frames.append({**record, "derivedFrom": "runtimeArtwork entries and rendererSources in this manifest",
                   "nativeGeneration": False, "actualModel": None, "actualQuality": None,
                   "modelEvidence": "UI composition is not an AI call. Follow each artwork's original generation/source record.",
                   "text": "Native DOM text rendered using bundled Noto Sans SC; not baked model-generated copy",
                   "sourcePixelPolicy": "Illustrations are uniformly fitted to the UI viewport; preview pixels do not add native image detail."})
result = {"recordedAt": datetime.now().astimezone().isoformat(), "projectRoot": str(root),
          "scope": "Images and UI design deliverable; not Unity runtime acceptance", "runtimeArtwork": art,
          "rendererSources": renderer, "renderedFrames": frames, "sourceManifest": "docs/ASSET_SOURCES.json",
          "browserVerification": "docs/verification/ui-preview.json", "errors": errors,
          "status": "passed" if not errors else "failed"}
(root / "designs/ui-v1/delivery-manifest.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"status": result["status"], "runtimePngCount": len(art), "uiFrames": len(frames), "errors": errors}, ensure_ascii=False))
raise SystemExit(bool(errors))
