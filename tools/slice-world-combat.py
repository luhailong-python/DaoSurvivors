"""Lossless ownership slicing of the reviewed native world-combat atlas.

No AI call, cleanup, recolour, resampling or component filtering occurs.
"""
from pathlib import Path
import json,hashlib,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy import ndimage

ROOT=Path(__file__).resolve().parents[1]
SHEET=ROOT/'art/whole-game/sheets/world-combat-v1.png'
OUT=ROOT/'art/whole-game/fx';OUT.mkdir(parents=True,exist_ok=True)
DOC=ROOT/'docs/whole-game';DOC.mkdir(parents=True,exist_ok=True)
ROW_EDGES=[0,256,520,758,1024]
COL_EDGES=[[0,438,803,1150,1536],[0,416,786,1150,1536],[0,383,764,1150,1536],[0,415,792,1174,1536]]
KEYS=['ToNearestSkill','BothSideSkill','BouncingSkill','ChainSkill','CircularAttackSkill','CircularMotionSkill','FourCornerSkill','InsideScopeSkill','RandomSkill','BlueMagic','PinkMagic','RedMagic','GreenMagic','SnowMagic','Suck','Prop']
NAMES=['skill-nearest','skill-bothside','skill-bouncing','skill-chain','skill-circle','skill-orbit','skill-fourcorner','skill-scope','skill-random','enemy-blue','enemy-pink','enemy-red','enemy-green','enemy-snow','pickup-suck','prop-urn']
LABELS=['追星御剑','两仪斩','流珠引','连星诀','太极震','葫芦巡天','四象符','八卦阵','落花令','青蓝敌弹','桃粉敌弹','朱红敌弹','青藤敌弹','霜雪敌弹','吸灵玉环','可破灵瓮']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return p.relative_to(ROOT).as_posix()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
im=Image.open(SHEET);assert im.mode=='RGBA' and im.size==(1536,1024)
pixels=np.asarray(im);a=pixels[:,:,3];owners=np.full(a.shape,-1,np.int16);rects=[]
for row in range(4):
 for col in range(4):
  r=(COL_EDGES[row][col],ROW_EDGES[row],COL_EDGES[row][col+1],ROW_EDGES[row+1]);rects.append(r);owners[r[1]:r[3],r[0]:r[2]]=row*4+col
assert (owners>=0).all()
componentLabels,n=ndimage.label(a>8,structure=np.ones((3,3)));sizes=np.bincount(componentLabels.ravel());cross=[]
for i in range(1,n+1):
 if sizes[i]<64:continue
 use=np.unique(owners[componentLabels==i])
 if len(use)>1:cross.append({'component':i,'area':int(sizes[i]),'owners':use.tolist()})
if cross:raise SystemExit('Visible components cross ownership boundaries: '+json.dumps(cross))
entries=[];sumAlpha=0;sourcePixelCount=0
for index,(key,name,label,r) in enumerate(zip(KEYS,NAMES,LABELS,rects)):
 crop=im.crop(r);ca=np.asarray(crop.getchannel('A'));box=Image.fromarray((ca>8).astype('uint8')*255).getbbox();assert box
 px=round(256-(box[0]+box[2])/2);py=round(256-(box[1]+box[3])/2)
 if px<0 or py<0 or px+crop.width>512 or py+crop.height>512:raise SystemExit('Crop cannot fit without trimming: '+key)
 output=Image.new('RGBA',(512,512),(0,0,0,0));output.paste(crop,(px,py));target=OUT/(name+'.png');output.save(target)
 pa=np.asarray(Image.open(target));assert np.array_equal(pa[py:py+crop.height,px:px+crop.width],np.asarray(crop))
 bbox=Image.fromarray((pa[:,:,3]>8).astype('uint8')*255).getbbox()
 edge8=int((pa[0,:,3]>8).sum()+(pa[-1,:,3]>8).sum()+(pa[:,0,3]>8).sum()+(pa[:,-1,3]>8).sum())
 sumAlpha+=int(pa[:,:,3].sum(dtype=np.uint64));sourcePixelCount+=int((ca>0).sum())
 pivot=[0.5,round((512-bbox[3])/512,6)] if key=='Prop' else [0.5,0.5]
 entry={'file':rel(target),'key':key,'label':label,'sha256':sha(target),'canvas':[512,512],'mode':'RGBA','alphaExtrema':list(output.getchannel('A').getextrema()),'alphaPixels':{'zero':int((pa[:,:,3]==0).sum()),'nonzero':int((pa[:,:,3]>0).sum()),'visibleGreaterThan8':int((pa[:,:,3]>8).sum())},'derivedFrom':{'file':rel(SHEET),'sha256':sha(SHEET),'generationRecord':rel(SHEET)+'.generation.json'},'operation':{'kind':'native ownership crop + transparent padding','cropRectXYXY':list(r),'placementXY':[px,py],'nativeCropSize':list(crop.size),'visibleAlphaGreaterThan8BBoxInCrop':list(box),'resampled':False,'alphaModified':False,'sourcePixelsPreserved':True,'componentFiltering':'none; all source alpha pixels retained including faint native halo/specks'},'pivotBottomLeft':pivot,'spriteType':'Single','meshType':'FullRect','filterMode':'Bilinear','wrapMode':'Clamp','mipmaps':False,'colourSpace':'sRGB','borderLTRB':[0,0,0,0],'defaultDirection':'+X (right)' if key not in ['BouncingSkill','InsideScopeSkill','RandomSkill','Suck','Prop'] else 'radial/standing; see asset role','actualModel':None,'actualQuality':None,'modelEvidence':'Follow native atlas generation record; this slicing did not call an image model.','validation':{'pixelCopyMatchesSource':True,'ownershipComponentCrossings':0,'canvasEdgePixelsWithAlphaGreaterThan8':edge8,'visibleBBox':list(bbox),'visualReview':'awaiting light/dark whole-set review','Unity':'not-tested'}}
 save(target.with_suffix('.png.derivation.json'),entry);entries.append(entry)
assert sumAlpha==int(a.sum(dtype=np.uint64));assert sourcePixelCount==int((a>0).sum())
rawPath=ROOT/'docs/production/world-combat-v1-qc/sheet-qc.json';raw=json.loads(rawPath.read_text(encoding='utf-8'))
reported=[{'id':x['id'],'status':x['status'],'value':x['value'],'threshold':x['threshold'],'files':[rel(SHEET)]} for x in raw['checks'] if x['status'] in ['warn','fail']]
halo=OUT/'elite-halo.png';shutil.copyfile(OUT/'skill-scope.png',halo)
haloRecord={'file':rel(halo),'sha256':sha(halo),'derivedFrom':{'file':rel(OUT/'skill-scope.png'),'sha256':sha(OUT/'skill-scope.png'),'derivationRecord':rel(OUT/'skill-scope.png')+'.derivation.json'},'operation':'byte-for-byte reuse; no image generation, recolouring, resampling or alpha change','canvas':[512,512],'mode':'RGBA','pivotBottomLeft':[0.5,0.5],'borderLTRB':[0,0,0,0],'spriteType':'Single','suggestedMaterialTint':'#E7BA54','tintStatus':'Unity material suggestion only; not baked into PNG and not engine-validated','actualModel':None,'actualQuality':None};save(halo.with_suffix('.png.derivation.json'),haloRecord)
manifest={'schemaVersion':1,'sheet':rel(SHEET),'sheetSha256':sha(SHEET),'nativeSize':list(im.size),'art_source':'host_image','route':'builtin image_gen; slicing is native deterministic crop/padding only','nominalGrid':[4,4],'nominalCellSize':[384,256],'ownership':{'rowEdges':ROW_EDGES,'columnEdgesByRow':COL_EDGES,'method':'Inspected transparent-alpha valleys; row-specific rectangles tile the full native canvas exactly once. Sword tip belongs to row0col0 through x437, not nominal x383.','alphaThresholdForComponentQC':8,'minComponentAreaForCrossingQC':64},'rawSheetQC':{'status':raw['status'],'record':rel(rawPath),'reportedChecks':reported,'note':'Nominal grid failed. It was not used for adopted cuts; keep original failures as source-layout evidence.'},'slicedAssetQC':{'status':'passed_pixel_and_ownership_checks_pending_visual_review','componentCrossings':cross,'allSourceAlphaPixelsAssignedExactlyOnce':True,'sumAlphaSource':int(a.sum(dtype=np.uint64)),'sumAlphaOutputs':sumAlpha,'sourceNonzeroAlphaPixels':int((a>0).sum()),'outputNonzeroAlphaPixels':sourcePixelCount,'all16PNG512RGBA':True,'allVisibleCanvasEdgesClear':all(x['validation']['canvasEdgePixelsWithAlphaGreaterThan8']==0 for x in entries),'resampling':'none','matteCleaning':'none; faint native alpha is retained','engineValidation':'not-performed'},'files':entries,'sharedEliteHalo':haloRecord,'notes':['512x512 is a padded delivery canvas; native visible details are not upscaled.','The two crescents are one paired BothSideSkill texture by deliberate prompt, not two separately controllable images.','Texture previews are not Unity gameplay screenshots.']}
save(DOC/'world-combat-slices.json',manifest)
font=ImageFont.truetype(str(ROOT/'art/fonts/NotoSansSC-Regular.otf'),21)
previewDir=ROOT/'designs/whole-game';previewDir.mkdir(parents=True,exist_ok=True)
for label,bg,fg in [('light',(245,238,213,255),(32,70,58,255)),('dark',(22,48,42,255),(238,224,181,255))]:
 board=Image.new('RGBA',(1280,1376),bg);draw=ImageDraw.Draw(board)
 for i,e in enumerate(entries):
  with Image.open(ROOT/e['file']) as icon:
   thumb=icon.resize((320,320),Image.Resampling.LANCZOS);board.alpha_composite(thumb,(i%4*320,i//4*344))
  draw.text((i%4*320+160,i//4*344+314),e['label'],font=font,fill=fg,anchor='mt')
 board.convert('RGB').save(previewDir/f'world-combat-review-{label}.png')
print(json.dumps({'files':len(entries),'componentCrossings':cross,'alphaConservation':sumAlpha,'allEdgesClear':manifest['slicedAssetQC']['allVisibleCanvasEdgesClear'],'sharedEliteHalo':rel(halo)},ensure_ascii=False))
