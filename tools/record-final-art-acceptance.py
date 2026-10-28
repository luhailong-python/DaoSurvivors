"""Record final art-only acceptance after completed visual review; no images edited."""
from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    inv=json.loads((ROOT/'docs/whole-game/ART_COVERAGE.json').read_text(encoding='utf-8'))
    assert inv['missingRequiredArt']==[]
    evidence=[inv['assetManifest'],*inv['hashBoundReviewRecords']]
    evidence += [{'file':s,'sha256':sha(ROOT/s)} for s in ['docs/whole-game/ART_COVERAGE.json',
        'docs/whole-game/ART_COVERAGE.md','docs/whole-game/ACCEPTANCE.md','docs/whole-game/UNITY_ART_IMPORT.md',
        'docs/whole-game/index.html','README.md']]
    for e in evidence:assert sha(ROOT/e['file'])==e['sha256']
    d={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
        'clientDate':'2026-10-28','clientTimezone':'America/New_York',
        'status':'accepted_art_only','scope':'Complete actual-source-required local game art; offline visual/action/technical acceptance only',
        'missingRequiredArt':[],'evidence':evidence,
        'summary':{'uiScreens':52,'players':3,'actions':6,'formalPlayerFrames':146,'playerStrips':10,
            'enemyIdentities':14,'enemyPoolKeys':20,'eliteVariants':6,'terrainTiles':6,'breakableProp':1,
            'worldLootKeys':6,'playerSkillTextures':9,'evolvedRelations':9,'enemyProjectiles':5,'debuffs':3,
            'artManifestFiles':inv['assetFileCount']},
        'retainedSourceFindings':inv['retainedFindings'],
        'sourceFindingsNotSuppressed':True,'unityIntegration':'not-performed; deferred by explicit user scope',
        'submittedToGit':False,'published':False,'artReferenceWritesInThisContinuation':False,
        'deliveryArchiveReceipt':'.local/delivery/LATEST.json'}
    (ROOT/'docs/whole-game/ACCEPTANCE.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':d['status'],'evidenceFiles':len(evidence),'missingRequiredArt':[]}))
if __name__=='__main__':main()
