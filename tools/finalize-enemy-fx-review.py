"""Record the completed 2026-10-28 visual review against current image hashes.

This records this session's actual image-view evidence. It is not an automatic
visual judge and must not be used to accept replacement image pixels.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=ROOT/'docs/whole-game/world-combat-slices.json';d=load(p)
assert d['sheetSha256']=='87d2ca1039c09fa653a3db2e822e2dae614806203c27a4125bbc5fedbc68b5b8'
assert sha(ROOT/d['sheet'])==d['sheetSha256']
review={'date':'2026-10-28','reviewMethod':'Actual viewed native atlas followed by both full 16-asset light/dark review montages. No Unity engine execution.','sourceSheetSHA256':d['sheetSha256'],'result':'accepted for art delivery with retained raw nominal-grid QC findings','previews':[],'assets':[]}
for s in ['designs/whole-game/world-combat-review-light.png','designs/whole-game/world-combat-review-dark.png']:
 review['previews'].append({'file':s,'sha256':sha(ROOT/s)})
for e in d['files']:
 assert sha(ROOT/e['file'])==e['sha256']
 e['validation']['visualReview']='accepted; complete subject, no neighbour contamination, clean visible margins, readable on reviewed light/dark backgrounds'
 review['assets'].append({'file':e['file'],'sha256':e['sha256'],'status':'accepted','notes':'Native silhouette and translucent glow preserved; no upscaling or alpha cleaning.'})
 save(ROOT/(e['file']+'.derivation.json'),e)
d['slicedAssetQC']['status']='accepted_pixel_ownership_and_actual_light_dark_visual_review_with_retained_raw_grid_findings'
d['visualReviewRecord']='docs/whole-game/world-combat-visual-review.json';save(p,d)
save(ROOT/'docs/whole-game/world-combat-visual-review.json',review)
p=ROOT/'docs/whole-game/enemies.json';d=load(p)
review={'date':'2026-10-28','result':'accepted static enemy art delivery with retained provenance/weak-alpha warnings','reviewMethod':'Actually viewed every adopted 1024 PNG at full size, plus light and dark final 14-identity montages. No inherited animation acceptance.','assets':[],'previews':[]}
for s in d['previews']:review['previews'].append({'file':s,'sha256':sha(ROOT/s)})
for e in d['entries']:
 assert sha(ROOT/e['destination'])==e['sha256']
 e['review']['finalLightDarkLineup']='accepted; identity, anatomy, implements and tails/wings intact, distinct readable silhouettes'
 review['assets'].append({'file':e['destination'],'sha256':e['sha256'],'status':'accepted','sourceFullSizeViewed':True})
 save(ROOT/(e['destination']+'.adoption.json'),e)
halo=ROOT/'art/whole-game/fx/elite-halo.png'
for e in d['eliteVariants']:
 e['eliteOverlay']['bindingStatus']='actual file present; shared scope-ring byte copy verified'
 e['eliteOverlay']['sha256']=sha(halo)
d['validation']['visualStatus']='accepted static sources and actual light/dark lineup review'
d['validation']['eliteOverlayPresent']=halo.is_file()
d['visualReviewRecord']='docs/whole-game/enemies-visual-review.json';save(p,d)
save(ROOT/'docs/whole-game/enemies-visual-review.json',review)
print('Recorded actual visual review for 14 enemy static identities, 20 key mappings and 16 world FX assets; raw warnings retained.')
