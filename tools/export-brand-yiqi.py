"""Mechanical size exports and review layouts of native generated logo art."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,zipfile
import numpy as np
from PIL import Image,ImageDraw,ImageFont

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'art/branding/yiqi-dangqian-v1'
DOC=ROOT/'docs/branding';PREVIEW=ROOT/'designs/branding/yiqi-dangqian-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    PREVIEW.mkdir(parents=True,exist_ok=True);DOC.mkdir(parents=True,exist_ok=True)
    assets=[]
    for basename,widths in [('logo-primary-v2',[1536,768,384]),('logo-emblem',[512,256,128])]:
        src=ART/(basename+'.png');im=Image.open(src).convert('RGBA')
        outputs=[src]
        for w in widths:
            h=round(im.height*w/im.width);p=ART/f'{basename}-{w}.png'
            # Pure downsample, not painted or newly generated details.
            out=im.convert('RGBa').resize((w,h),Image.Resampling.LANCZOS).convert('RGBA');out.save(p)
            write(p.with_suffix('.png.derivation.json'),{'file':rel(p),'sha256':sha(p),
                'derivedFrom':{'file':rel(src),'sha256':sha(src),'generationRecord':rel(src)+'.generation.json'},
                'operation':'premultiplied-alpha LANCZOS downscale only; no new art generation or painted edits',
                'dimensions':[w,h],'pivotNormalizedBottomLeft':[.5,.5],'borderLeftBottomRightTopPx':[0,0,0,0]})
            outputs.append(p)
        for p in outputs:
            a=Image.open(p);ar=np.array(a.getchannel('A'));ys,xs=np.where(ar>16)
            bounds=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)]
            assert ar.min()==0 and ar.max()>240
            assert bounds[0]>0 and bounds[1]>0 and bounds[2]<a.width and bounds[3]<a.height
            assets.append({'file':rel(p),'sha256':sha(p),'dimensions':list(a.size),'format':'RGBA PNG',
                'role':'main wordmark' if 'primary' in basename else 'standalone secondary emblem',
                'alphaExtrema':list(a.getchannel('A').getextrema()),'visibleBoundsAlphaAbove16':bounds,
                'hasRealTransparency':True,'sourceType':'native builtin generation' if p==src else 'downscaled derivative',
                'record':rel(p)+('.generation.json' if p==src else '.derivation.json'),
                'unityImportAdvice':{'textureType':'Sprite(2D and UI)','spriteMode':'Single','pivot':[.5,.5],
                    'border':[0,0,0,0],'preserveAspect':True,'filterMode':'Bilinear','wrapMode':'Clamp',
                    'alphaIsTransparency':True,'mipMaps':False,'compression':'None initially; test platform choice later',
                    'validatedInUnity':False}})
    # Native source pixels remain unchanged. These plates only place assets.
    plate=Image.new('RGB',(1600,1000),'#f2ebd8')
    for x,y,w,h,bg in [(0,0,1600,470,'#f3eddb'),(0,470,1000,270,'#16463c'),(0,740,1000,260,'#f3eddb')]:
        tile=Image.new('RGBA',(w,h),bg);im=Image.open(ART/'logo-primary-v2.png')
        iw=w-100;im=im.convert('RGBa').resize((iw,round(iw/3)),Image.Resampling.LANCZOS).convert('RGBA')
        tile.alpha_composite(im,((w-im.width)//2,(h-im.height)//2));plate.paste(tile.convert('RGB'),(x,y))
    emblem=Image.open(ART/'logo-emblem-512.png');tile=Image.new('RGBA',(600,530),'#dedec5');tile.alpha_composite(emblem,(44,9));plate.paste(tile.convert('RGB'),(1000,470))
    plate.save(PREVIEW/'brand-review.jpg',quality=96)
    # Explicit game-size readability review, using delivered downscales.
    small=Image.new('RGB',(1000,460),'#f3eddb')
    for y,bg in [(0,'#f3eddb'),(230,'#16463c')]:
        tile=Image.new('RGBA',(1000,230),bg)
        for w,x in [(768,10),(384,600)]:
            im=Image.open(ART/f'logo-primary-v2-{384 if w==768 else w}.png')
            tile.alpha_composite(im,(x,30 if w==768 else 100))
        icon=Image.open(ART/'logo-emblem-128.png');tile.alpha_composite(icon,(420,45));small.paste(tile.convert('RGB'),(0,y))
    small.save(PREVIEW/'small-size-review.jpg',quality=96)
    manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'gameName':'一炁当千',
        'pronunciation':'yī qì dāng qiān','previousWorkingTitle':'道途幸存者','displayTagline':'一人成阵，万妖退散',
        'phase':'name and logo addition; no Unity implementation',
        'generationRoute':'native image_gen.imagegen','actualModel':None,'actualQuality':None,
        'unverifiedReason':'Host tool does not expose model/quality parameters or reliable result identifiers.',
        'nativeImages':2,'downscaledExports':6,'assets':assets,
        'promptFiles':['docs/production/yiqi-dangqian-logo-v2.prompt.txt','docs/production/yiqi-dangqian-emblem-v1.prompt.txt'],
        'sourceReferenceOnly':'art/branding/yiqi-dangqian-v1/logo-primary.png is earlier unselected glyph repair source; use logo-primary-v2.png as the finished wordmark.',
        'preview':'designs/branding/yiqi-dangqian-v1/index.html',
        'originalGameArtAcceptance':'docs/whole-game/ACCEPTANCE.json',
        'relationshipToPreviousDelivery':'Separate brand addition; earlier accepted game art and its archive remain byte-unchanged.',
        'visualStatus':'pending actual light/dark, Chinese glyph and integration review'}
    write(DOC/'BRAND.json',manifest)
    print(json.dumps({'nativeImages':2,'exports':6,'realAlpha':True,'visibleClipping':False,'manifest':rel(DOC/'BRAND.json')}))

if __name__=='__main__':main()
