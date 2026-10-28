"""Slice existing generated part kits and animate the six painted parts.

This is mechanical cutout animation, not newly drawn frame art or AI video.
Native atlases and approved portraits are never modified.
"""
from pathlib import Path
import math, json, hashlib
from datetime import datetime, timezone
import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'art/whole-game/players'
REVIEW = ROOT / 'designs/whole-game/players'
NAMES = ['head', 'torso', 'far_arm', 'near_arm', 'far_leg', 'near_leg']
SIZE = 512
SPECS = {
    'fighter': {
        'name': '青云小道', 'portrait': 'art/characters/hero.png',
        'parts': {
            'head': ((278, 504), .43, (256, 244)),
            'torso': ((849, 126), .33, (256, 240)),
            'far_arm': ((1246, 165), .29, (224, 258)),
            'near_arm': ((226, 612), .285, (287, 258)),
            'far_leg': ((774, 579), .29, (240, 364)),
            'near_leg': ((1264, 582), .29, (278, 366)),
        }
    },
    'mage': {
        'name': '清莲灵修', 'portrait': 'art/characters/healer.png',
        'parts': {
            'head': ((315, 489), .38, (256, 247)),
            'torso': ((841, 153), .34, (256, 242)),
            'far_arm': ((1253, 215), .31, (228, 266)),
            'near_arm': ((370, 639), .31, (285, 265)),
            'far_leg': ((792, 625), .30, (242, 370)),
            'near_leg': ((1252, 620), .30, (276, 370)),
        }
    }
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return p.relative_to(ROOT).as_posix()
def write(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def font(sz=17):
    for p in [ROOT/'Assets/DaoSurvivor/Resources/Fonts/NotoSansSC-Regular.ttf', Path('C:/Windows/Fonts/msyh.ttc')]:
        if p.exists(): return ImageFont.truetype(str(p), sz)
    return ImageFont.load_default()

def rotate_point(pt, pivot, angle):
    a=math.radians(angle); x,y=pt[0]-pivot[0],pt[1]-pivot[1]
    return (pivot[0]+math.cos(a)*x-math.sin(a)*y,
            pivot[1]+math.sin(a)*x+math.cos(a)*y)

def slice_parts(kind, spec):
    sources={}
    for version in [1,2]:
        src=ROOT/f'art/whole-game/sheets/player-{kind}-rig-v{version}.png'
        sources[version]=(src,np.array(Image.open(src).convert('RGBA')))
    parts={}; meta=[]
    for version,(src,arr) in sources.items():
        parts0,meta0=slice_atlas(kind,spec,src,arr,version)
        parts.update(parts0);meta.extend(meta0)
    return parts,meta

def slice_atlas(kind,spec,src,arr,version):
    labs,n=ndimage.label(arr[:,:,3]>16)
    objs=ndimage.find_objects(labs)
    components=[]
    for i,s in enumerate(objs):
        if s is not None and (labs==i+1).sum()>1000:
            components.append((i+1, [s[1].start,s[0].start,s[1].stop,s[0].stop]))
    if len(components)!=6: raise ValueError(f'{kind}: expected6 real components, got{len(components)}')
    # Ownership by actual component centroid, never equal-cell slicing.
    components.sort(key=lambda z: (0 if (z[1][1]+z[1][3])/2<535 else 1,(z[1][0]+z[1][2])/2))
    parts={}; meta=[]
    for name,(lab,bbox) in zip(NAMES,components):
        if (version==1)!=(name=='head'):continue
        mask=ndimage.binary_dilation(labs==lab, iterations=3)
        mask &= ((labs==0)|(labs==lab))
        aa=arr.copy(); aa[~mask]=0
        b=Image.fromarray(aa).getbbox()
        part=Image.fromarray(aa).crop(b)
        pivot,scale,bind=spec['parts'][name]
        pv=(pivot[0]-b[0],pivot[1]-b[1])
        dest=OUT/kind/'parts'/f'{name}.png'; dest.parent.mkdir(parents=True,exist_ok=True)
        part.save(dest)
        mirror=(name=='far_arm') or (kind=='mage' and name=='near_arm')
        parts[name]={'im':part,'pivot':pv,'scale':scale,'bind':bind,'mirror':mirror}
        meta.append({'part':name,'file':rel(dest),'sha256':sha(dest),'nativeSize':list(part.size),
            'sourceCrop':list(b),'nativePivot':list(pv),'pivotAtlas':list(pivot),'displayScale':scale,
            'bindJoint':list(bind),'mirrorAroundJoint':mirror,'parent':'torso' if name!='torso' else 'root',
            'derivedFrom':{'file':rel(src),'sha256':sha(src),'generationRecord':rel(src)+'.generation.json'},
            'operation':'component-ownership crop; native RGBA retained; alpha hygiene removes disconnected <=16 haze outside3px contour',
            'removedAlphaPixels':int(((arr[:,:,3]>0)&~mask).sum()),
            'actualModel':None,'actualQuality':None})
        write(dest.with_suffix('.png.derivation.json'),meta[-1])
    return parts,meta

def place(part, joint, angle=0, stretch=(1,1)):
    """Affine-sample existing painted pixels with premultiplied alpha."""
    s=part['scale']; sx=s*stretch[0]*(-1 if part.get('mirror') else 1); sy=s*stretch[1]
    a=math.radians(angle); c=math.cos(a); sn=math.sin(a)
    # Input->output: joint + R(angle)*(scaled*(p-nativePivot)).
    # Pillow requires inverse output->input.
    px,py=part['pivot']; jx,jy=joint
    coeff=(c/sx,sn/sx,px-(c*jx+sn*jy)/sx,
           -sn/sy,c/sy,py-(-sn*jx+c*jy)/sy)
    return part['im'].convert('RGBa').transform((SIZE,SIZE),Image.Transform.AFFINE,
        coeff,Image.Resampling.BICUBIC).convert('RGBA')

def pose(parts,action,t):
    s=math.sin(t); c=math.cos(t)
    isrun=action=='run'; bob=(-3-3*math.cos(2*t)) if isrun else 1.5*s
    lean=-5+1.5*math.sin(2*t) if isrun else 1.2*s
    root=(256,355)
    poses={}; layers={}
    for name,p in parts.items():
        bind=p['bind']; joint=rotate_point((bind[0],bind[1]+bob),root,lean)
        angle=lean; stretch=(1,1)
        if name=='head': angle=lean*.25+(1.5*math.sin(t-.4) if isrun else .8*math.sin(t-.5))
        elif name=='torso': stretch=(1,1+(0.006*math.sin(2*t) if isrun else .012*s))
        elif name in ('near_arm','far_arm'):
            phase=0 if name=='near_arm' else math.pi
            angle+=(-23*math.sin(t+phase) if isrun else 2*math.sin(t+phase-.4))
        elif name in ('near_leg','far_leg'):
            phase=0 if name=='near_leg' else math.pi
            v=math.sin(t+phase)
            angle+=(23*v if isrun else .5*s)
            if isrun:
                # Swing leg rises; support leg sole is explicitly registered.
                joint=(joint[0],joint[1]-max(0,math.cos(t+phase))*11)
        layer=place(p,joint,angle,stretch)
        contact=None
        if name in ('near_leg','far_leg'):
            phase=0 if name=='near_leg' else math.pi
            if isrun:
                swing=max(0,math.cos(t+phase))
                target_bottom=471-round(26*swing)
                contact='support' if math.cos(t+phase)<=0 else 'swing'
            else:
                target_bottom=471
                contact='standing'
            # Keep the hip covered by the hem. Solve painted leg Y length
            # about the fixed hip, never translate its open end out of clothes.
            for _ in range(3):
                current=layer.getbbox()[3]-joint[1]
                sy=stretch[1]*(target_bottom-joint[1])/current
                stretch=(1,sy)
                layer=place(p,joint,angle,stretch)
        poses[name]={'joint':[round(v,3) for v in joint],'angle':round(angle,3),'stretch':list(stretch)}
        if contact:poses[name].update({'contact':contact,'soleY':layer.getbbox()[3]})
        layers[name]=layer
    # Hide painted limb socket caps beneath the finished torso overlap.
    canvas=Image.new('RGBA',(SIZE,SIZE))
    for name in ['far_arm','far_leg','near_leg','torso','near_arm','head']:
        canvas.alpha_composite(layers[name])
    return canvas,poses,layers

def make_review(kind,action,frames):
    # Review labels/backgrounds are diagnostic; the sprites are unpainted.
    sheet=Image.new('RGB',(1024,4*292),(237,232,214)); d=ImageDraw.Draw(sheet)
    for i,im in enumerate(frames):
        x=(i%4)*256; y=(i//4)*292
        tile=Image.new('RGBA',(256,256),(31,48,53,255) if i%2 else (245,240,225,255))
        tile.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS))
        sheet.paste(tile.convert('RGB'),(x,y+30)); d.text((x+8,y+5),f'{kind} {action} {i+1:02d}',font=font(16),fill=(30,47,44))
    dest=REVIEW/f'{kind}-{action}-poses.jpg';sheet.save(dest,quality=94)
    playback=[]
    for im in frames:
        bg=Image.new('RGBA',(1024,512),(242,237,219,255))
        bg.paste(Image.new('RGBA',(512,512),(25,42,48,255)),(512,0))
        bg.alpha_composite(im,(0,0));bg.alpha_composite(im,(512,0))
        playback.append(bg.convert('RGB'))
    gif=REVIEW/f'{kind}-{action}-review.gif'
    playback[0].save(gif,save_all=True,append_images=playback[1:],duration=60,loop=0,disposal=2)
    return [rel(dest),rel(gif)]

def main():
    REVIEW.mkdir(parents=True,exist_ok=True)
    reports=[]
    for kind,spec in SPECS.items():
        parts,meta=slice_parts(kind,spec)
        actions={}; checks=[]
        for action in ['idle','run']:
            frames=[]; poses=[]; info=[]
            for i in range(16):
                im,pp,layers=pose(parts,action,2*math.pi*i/16)
                dest=OUT/kind/action/'E'/f'{i+1:02d}.png';dest.parent.mkdir(parents=True,exist_ok=True)
                im.save(dest); frames.append(im);poses.append(pp)
                wb=im.getbbox(); a=np.array(im.getchannel('A'))
                if min(wb)<4 or max(wb)>508: raise ValueError(f'clipped:{kind}/{action}/{i}:{wb}')
                info.append({'file':rel(dest),'sha256':sha(dest),'bbox':list(wb),'durationMs':60,
                    'alphaExtrema':list(im.getchannel('A').getextrema())})
                write(dest.with_suffix('.png.derivation.json'),dict(info[-1],
                    derivedFrom=[{'file':p['file'],'sha256':p['sha256']} for p in meta],
                    operation='premultiplied-alpha affine cutout composite of6 existing painted parts',
                    pose=pp,root=[256,471],actualModel=None,actualQuality=None))
            strip=Image.new('RGBA',(SIZE*16,SIZE))
            for i,im in enumerate(frames):strip.paste(im,(i*SIZE,0))
            stripfile=dest.parent/'strip.png';strip.save(stripfile)
            write(stripfile.with_suffix('.png.derivation.json'),{'file':rel(stripfile),'sha256':sha(stripfile),
                'derivedFrom':[{'file':p['file'],'sha256':p['sha256']} for p in info],
                'operation':'horizontal chronological concatenation;16 cells512x512; no resampling'})
            # West uses exactly the source game's horizontal renderer flip.
            wdir=OUT/kind/action/'W';wdir.mkdir(parents=True,exist_ok=True)
            for i,im in enumerate(frames):
                wfile=wdir/f'{i+1:02d}.png';im.transpose(Image.Transpose.FLIP_LEFT_RIGHT).save(wfile)
                write(wfile.with_suffix('.png.derivation.json'),{'file':rel(wfile),'sha256':sha(wfile),
                    'derivedFrom':{'file':info[i]['file'],'sha256':info[i]['sha256']},
                    'operation':'exact horizontal reflection; fixed512x512 canvas; chronological frame retained'})
            # Keep the strip in chronological order, each cell mirrored.
            ws=Image.new('RGBA',strip.size)
            for i,im in enumerate(frames):ws.paste(im.transpose(Image.Transpose.FLIP_LEFT_RIGHT),(i*SIZE,0))
            ws.save(wdir/'strip.png')
            write((wdir/'strip.png.derivation.json'),{'file':rel(wdir/'strip.png'),'sha256':sha(wdir/'strip.png'),
                'derivedFrom':{'file':rel(stripfile),'sha256':sha(stripfile)},
                'operation':'each of16 chronological cells reflected horizontally; frame order unchanged'})
            cycle0=pose(parts,action,0)[0]; cycle2pi=pose(parts,action,2*math.pi)[0]
            seam=int(np.abs(np.array(cycle0,dtype=int)-np.array(cycle2pi,dtype=int)).max())
            firstlast=float(np.abs(np.array(frames[0],dtype=float)-np.array(frames[-1],dtype=float)).mean())
            checks.append({'action':action,'analyticLoopSeamMaxChannelDifference':seam,
                'adjacentLastFirstMeanChannelDifference':round(firstlast,4),
                'distinctFrames':len({hashlib.sha256(np.array(im).tobytes()).hexdigest() for im in frames}),
                'artAcceptance':'pending visual and playback review'})
            actions[action]={'frames':info,'poses':poses,'strip':rel(stripfile),'west':'mirror each frame horizontally',
                'review':make_review(kind,action,frames),'fps':16.6666667,'cycleMs':960,'loop':True}
        report={'schemaVersion':1,'character':kind,'name':spec['name'],
            'portrait':{'file':spec['portrait'],'sha256':sha(ROOT/spec['portrait'])},
            'artSource':'existing native-image-generated sixpart kit; mechanical cutout animation',
            'notNewPerFrameGeneration':True,'canvas':[512,512],'root':[256,471],
            'unitySuggestedPivot':[.5,41/512],'actions':actions,'parts':meta,
            'layerOrder':['far_arm','far_leg','near_leg','torso','near_arm','head'],
            'timingNote':'960ms art proposal; not a measured copy of source Animator duration',
            'unityIntegration':'not-performed','qa':checks,'visualStatus':'pending'}
        write(OUT/kind/'animation.json',report);reports.append(report)
    write(ROOT/'docs/whole-game/player-rig-technical-qa.json',{'characters':[
        {'character':r['character'],'qa':r['qa']} for r in reports], 'generatedAt':datetime.now(timezone.utc).isoformat(),
        'status':'technical-only; visual approval required'})
    print(json.dumps({'characters':[r['character'] for r in reports],'frames':128,'status':'awaiting visual review'}))

if __name__=='__main__':main()
