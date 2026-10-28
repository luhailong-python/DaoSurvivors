"""Package only this conversation's accepted art; never includes reference clone/Unity."""
from pathlib import Path
import hashlib,json,zipfile
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
DIRS=['art','designs/ui-suite','designs/whole-game','docs/ui-suite','docs/whole-game','docs/provenance','docs/production']
FILES=['README.md','docs/ART_DIRECTION.md','docs/art-reference-extension.md','docs/image-reference-associations.md','docs/art-resource-guide.md','docs/ASSET_SOURCES.json','docs/art-extension-sources.json','docs/control-state-derivations.json','docs/icon-atlas1-slices.json','docs/icon-atlas2-slices.json','docs/reference-audit-gameplay.md','docs/reference-gameplay-evidence.json','docs/reference-audit-ui.md','docs/reference-ui-evidence.json','docs/whole-game-art-audit.md','docs/whole-game-art-audit.json']
TOOLS=['build-art-manifest.py','build-world-tiles.py','build-player-rig.py','build-whole-game-inventory.py','render-suite.cjs','slice-suite-icons.py','slice-world-combat.py','export-sword-player-actions.py','build-world-support.py','audit-ui-delivery.py','audit-world-support.py','finalize-player-review.py','record-final-art-acceptance.py','record-builtin-art.py','package-art-delivery.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    accepted=ROOT/'docs/whole-game/ACCEPTANCE.json'
    status=json.loads(accepted.read_text(encoding='utf-8'))
    if status.get('status')!='accepted_art_only':raise SystemExit('No final whole-game art acceptance; package withheld.')
    inventory=json.loads((ROOT/'docs/whole-game/ART_COVERAGE.json').read_text(encoding='utf-8'))
    if inventory.get('missingRequiredArt'):raise SystemExit('Required art gaps remain.')
    for e in status['evidence']:
        if sha(ROOT/e['file'])!=e['sha256']:raise SystemExit(f'Changed acceptance evidence: {e["file"]}')
    manifest=json.loads((ROOT/'art/manifest.json').read_text(encoding='utf-8'))
    for e in manifest['assets']:
        if sha(ROOT/e['file'])!=e['sha256']:raise SystemExit(f'Changed art asset: {e["file"]}')
    paths=set()
    for name in DIRS:
        for p in (ROOT/name).rglob('*'):
            if p.is_file():paths.add(p)
    paths.update(ROOT/n for n in FILES)
    paths.update(ROOT/'tools'/n for n in TOOLS if (ROOT/'tools'/n).exists())
    files=[]
    for p in sorted(paths):
        if not p.is_file():raise SystemExit(f'Missing declared delivery file: {p}')
        p.resolve().relative_to(ROOT)
        rel=p.relative_to(ROOT).as_posix()
        if rel.split('/')[0] in {'.git','.reference','Assets','Packages','ProjectSettings','.local'}:raise SystemExit(f'Excluded tree: {rel}')
        if '.git' in p.parts or p.suffix.lower() in {'.cs','.dll','.exe','.psb'}:raise SystemExit(f'Non-art payload: {rel}')
        files.append({'file':rel,'bytes':p.stat().st_size,'sha256':sha(p)})
    out=ROOT/'.local/delivery';out.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S')
    dest=out/f'DaoSurvivors-Art-{stamp}.zip'
    if dest.exists():raise SystemExit('Refusing overwrite')
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for d in files:z.write(ROOT/d['file'],d['file'])
        z.writestr('DELIVERY_FILE_INDEX.json',json.dumps({'files':files,'unityIncluded':False,'referenceCloneIncluded':False},ensure_ascii=False,indent=2))
    with zipfile.ZipFile(dest) as z:
        bad=z.testzip()
        if bad:raise SystemExit(f'ZIP CRC mismatch: {bad}')
    receipt={'file':str(dest),'bytes':dest.stat().st_size,'sha256':sha(dest),'payloadFiles':len(files),'crcVerified':True,'excludes':['reference clone','frozen Unity project','other conversation content','Git data'],'status':'local-art-delivery-only'}
    (out/'LATEST.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False))
if __name__=='__main__':main()
