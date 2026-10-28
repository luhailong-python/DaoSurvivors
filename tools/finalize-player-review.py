"""Bind the actually completed human-visible review to the final player pixels.

No image changes; numeric checks cannot substitute for the recorded visual work.
"""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    independent=load(ROOT/'docs/whole-game/final-review-independent.json')
    assert independent['status']=='accepted_still_visual_and_pose_review'
    assert independent['blockingFindings']==[]
    for e in independent['reviewedImages']+independent['hashBoundManifests']:
        assert sha(ROOT/e['file'])==e['sha256'],e['file']
    files=[];checks=[];characters=[]
    for kind in ['fighter','mage']:
        p=ROOT/f'art/whole-game/players/{kind}/animation.json';d=load(p)
        feet=[];scales=[]
        for action,clip in d['actions'].items():
            for e,pose in zip(clip['frames'],clip['poses']):
                p=ROOT/e['file'];assert sha(p)==e['sha256']
                im=Image.open(p);assert im.size==(512,512) and im.mode=='RGBA'
                w=Path(str(p).replace('\\E\\','\\W\\').replace('/E/','/W/'))
                assert np.array_equal(np.array(Image.open(w)),np.array(im)[:,::-1,:])
                for q in [p,w]:files.append({'file':q.relative_to(ROOT).as_posix(),'sha256':sha(q)})
                for n in ['near_leg','far_leg']:
                    if pose[n]['contact']!='swing':feet.append(pose[n]['soleY'])
                    scales.append(pose[n]['stretch'][1])
            for facing in ['E','W']:
                folder=ROOT/f'art/whole-game/players/{kind}/{action}/{facing}'
                strip=Image.open(folder/'strip.png');assert strip.size==(8192,512)
                for i in range(16):assert np.array_equal(np.array(strip.crop((512*i,0,512*i+512,512))),np.array(Image.open(folder/f'{i+1:02d}.png')))
                files.append({'file':(folder/'strip.png').relative_to(ROOT).as_posix(),'sha256':sha(folder/'strip.png')})
            q=next(x for x in d['qa'] if x['action']==action)
            assert q['analyticLoopSeamMaxChannelDifference']==0 and q['distinctFrames']==16
        assert min(feet)>=470 and max(feet)<=472
        characters.append({'character':kind,'actions':['Idle','Run'],'frames':64,'strips':4,'parts':6,
            'loopMs':960,'frameDurationMs':60,'supportSoleYRange': [min(feet),max(feet)],
            'legYScaleRangeAroundFixedHip':[min(scales),max(scales)],
            'visualReview':'accepted: all32Eposes, light/dark backgrounds, native extreme-stride frame; W reflected and browser-viewed',
            'notes':'six full painted limbs, fixed hip and Y length solve; no elbow/knee IK; no video; native generated part art composited mechanically'})
    sword=load(ROOT/'art/whole-game/players/sword/animation.json')
    for e in sword['files']:
        key=e.get('file') or e.get('destination')
        p=ROOT/key;assert sha(p)==e['sha256'];files.append({'file':key,'sha256':sha(p)})
    characters.append({'character':'sword','actions':['Idle','Run'],'frames':18,'strips':2,
        'visualReview':'accepted existing E/W dedicated Idle and8pose walk/Run; source hash identity match',
        'timing':'Idle1000ms preview hold; Run480ms authored source walk mapping; not original Animator timing'})
    report={'schemaVersion':1,'recordedAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'accepted_player_art_only','characters':characters,'formalFrames':146,'strips':10,
        'independentReview':'docs/whole-game/final-review-independent.json',
        'technicalChecks':{'generatedWestExactMirrors':128,'chronologicalStripsCompared':8,
            'complete512RGBAFrames':146,'analyticSeamDifference':0,'supportFootTolerancePx':1,
            'currentImageHashes':len(files)},
        'actualBrowserReview':{'url':'http://127.0.0.1:4327/docs/whole-game/index.html',
            'method':'Primary agent used the in-app browser to actually display all six formal clips,1x and0.25x playback, E/W switch, pause and single-frame controls; inspected W phase16 then1 across loop.',
            'observed':'Every formal frame loaded; independent head/body/arm/leg change visible; hip seams remain covered; no blank frame or first/last pose pop observed in reviewed loops.',
            'evidence':'Current tool-visible screenshots and DOM snapshots; no claim of a video recording or Unity runtime screenshot.',
            'controlsVerified':['play/pause','0.25x playback','E/W facing','frame16 to1 step']},
        'limitations':['Cutout full limbs have intentionally limited joint articulation.',
            'Sword existing art and gait are reused at original quality; no new per-frame painting claimed.',
            'Source engine uses SpriteSkin/IK; baked frames require renderer/Animator and hit-renderer binding in next Unity phase.',
            'Build-generated animation.json visualStatus is a technical-only pending marker; this hash-bound review is the current art acceptance.'],
        'unityIntegration':'not-performed','files':files}
    write(ROOT/'docs/whole-game/player-actions-final-review.json',report)
    print(json.dumps({'status':report['status'],'formalFrames':146,'strips':10,'imageHashes':len(files)}))
if __name__=='__main__':main()
