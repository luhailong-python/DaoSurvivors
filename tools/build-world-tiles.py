"""Crop generated ground art, quilt shared edges, inspect every join, emit map data.

This is pixel reuse/downsizing, never a painting or image-generation route.
Does not execute a production build without an explicit --atlas. Never overwrites.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = [200, 3, 3, 1, 1, 3]
LABELS = ['plain-stone', 'moss-stone', 'bamboo-leaves', 'wildflower', 'lichen', 'stone-cluster']


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def project_path(value):
    value = Path(value)
    if not value.is_absolute():
        value = ROOT / value
    value = value.resolve()
    value.relative_to(ROOT)
    return value


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def crop_boxes(size, columns, rows, explicit=None):
    if explicit is not None:
        boxes = explicit['boxes'] if isinstance(explicit, dict) else explicit
        if len(boxes) != 6:
            raise ValueError('Exactly six crop boxes are required.')
    else:
        width, height = size
        if abs((width / columns) / (height / rows) - 1) > .03:
            raise ValueError('Atlas aspect does not match square cells. Supply six explicit square --boxes; do not stretch.')
        xx = [round(i * width / columns) for i in range(columns + 1)]
        yy = [round(i * height / rows) for i in range(rows + 1)]
        side = min(min(b-a for a,b in zip(xx,xx[1:])), min(b-a for a,b in zip(yy,yy[1:])))
        boxes = []
        for y in range(rows):
            for x in range(columns):
                left = xx[x] + (xx[x+1]-xx[x]-side)//2
                top = yy[y] + (yy[y+1]-yy[y]-side)//2
                boxes.append([left, top, left+side, top+side])
    sides = set()
    for box in boxes:
        left, top, right, bottom = box
        if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
            raise ValueError(f'Crop outside source: {box}')
        if right-left != bottom-top:
            raise ValueError(f'Non-square crop: {box}')
        sides.add(right-left)
    if len(sides) != 1:
        raise ValueError('Native crop sizes must match; no silent per-tile scale correction.')
    return boxes


def min_cut(cost, guard):
    """Left-to-right strip cut, ±1 pixel row movement, stable leftmost ties."""
    height, width = cost.shape
    valid = cost[:, guard:].astype(np.float64)
    costs = valid[0].copy()
    history = np.zeros(valid.shape, dtype=np.int8)
    for row in range(1, height):
        candidates = np.stack((np.r_[np.inf, costs[:-1]], costs, np.r_[costs[1:], np.inf]))
        chosen = np.argmin(candidates, axis=0)
        costs = valid[row] + candidates[chosen, np.arange(valid.shape[1])]
        history[row] = chosen - 1
    seam = np.zeros(height, dtype=np.int32)
    col = int(np.argmin(costs))
    seam[-1] = col + guard
    for row in range(height-1, 0, -1):
        col += int(history[row, col])
        seam[row-1] = col + guard
    return seam


def orient(array, side):
    if side == 'left': return array
    if side == 'right': return array[:, ::-1]
    if side == 'top': return array.transpose(1,0,2)
    if side == 'bottom': return array[::-1].transpose(1,0,2)
    raise ValueError(side)


def unorient(array, side):
    if side == 'left': return array
    if side == 'right': return array[:, ::-1]
    if side == 'top': return array.transpose(1,0,2)
    if side == 'bottom': return array.transpose(1,0,2)[::-1]
    raise ValueError(side)


def adapt_edges(original, canonical, guard, reach):
    result = original.copy()
    records = []
    for side in ('left', 'right', 'top', 'bottom'):
        view = orient(result, side).copy()
        reference = orient(canonical, side)
        cost = np.abs(view[:, :reach].astype(np.float32)-reference[:, :reach].astype(np.float32)).mean(axis=2)
        seam = min_cut(cost, guard)
        mask = np.arange(view.shape[1])[None,:] <= seam[:,None]
        view[mask] = reference[mask]
        result = unorient(view, side).copy()
        records.append({'side': side, 'cutPxPerRow': seam.tolist(), 'cutMinPx': int(seam.min()), 'cutMaxPx': int(seam.max()), 'cutMeanRGBError': float(cost[np.arange(len(seam)),seam].mean())})
    return result, records


def seam_metrics(first, second, axis):
    a = first.astype(np.float32)
    b = second.astype(np.float32)
    if axis == 'horizontal':
        step = np.abs(a[:,-1]-b[:,0])
        nearby = np.concatenate((np.abs(a[:,-17:-1]-a[:,-16:]), np.abs(b[:,:16]-b[:,1:17])),axis=1)
    else:
        step = np.abs(a[-1]-b[0])
        nearby = np.concatenate((np.abs(a[-17:-1]-a[-16:]), np.abs(b[:16]-b[1:17])),axis=0)
    mean = float(step.mean())
    context = float(nearby.mean())
    return {'joinMeanAbsoluteRGBStep': mean, 'joinMaxAbsoluteRGBStep': float(step.max()), 'nearbyMeanAbsoluteRGBStep': context, 'joinToNearbyRatio': mean/max(context, .001)}


def grid_image(tiles, grid, side):
    grid = np.asarray(grid)
    image = Image.new('RGB', (grid.shape[1]*side, grid.shape[0]*side))
    thumbs = [Image.fromarray(tile).resize((side,side), Image.Resampling.LANCZOS) for tile in tiles]
    for y, row in enumerate(grid):
        for x, tile in enumerate(row):
            image.paste(thumbs[int(tile)], (x*side,y*side))
    return image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--atlas', required=True, help='Project-local generated opaque six-cell ground atlas')
    parser.add_argument('--generation-record', help='Project-local original generation JSON; required before production acceptance')
    parser.add_argument('--grid', choices=['3x2','2x3'], default='3x2', help='Columns x rows, left-to-right, top-to-bottom')
    parser.add_argument('--boxes', help='JSON containing six equal square [left,top,right,bottom] rectangles, overrides grid')
    parser.add_argument('--size', type=int, choices=[512,1024], default=512)
    parser.add_argument('--guard', type=int, default=16, help='Mandatory shared edge guard pixels at final size')
    parser.add_argument('--reach', type=int, default=48, help='Maximum edge quilting extent at final size')
    parser.add_argument('--collar-source-index', type=int, choices=range(6), default=0)
    parser.add_argument('--seed', type=int, default=20261028)
    parser.add_argument('--output-dir', default='art/whole-game/terrain/v1')
    parser.add_argument('--preview-dir', default='designs/whole-game/scenes/v1')
    args = parser.parse_args()
    atlas_path = project_path(args.atlas)
    out = project_path(args.output_dir)
    preview = project_path(args.preview_dir)
    if out.exists() or preview.exists():
        raise ValueError('Output/preview directory already exists. Choose a new version; nothing is overwritten.')
    if not 1 <= args.guard < args.reach < args.size//3:
        raise ValueError('Require 1 <= guard < reach < size/3.')
    generation = project_path(args.generation_record) if args.generation_record else None
    if generation and not generation.is_file():
        raise ValueError('Generation record missing.')
    columns, rows = map(int,args.grid.split('x'))
    boxes = json.loads(project_path(args.boxes).read_text('utf-8-sig')) if args.boxes else None
    with Image.open(atlas_path) as image:
        image.load()
        native_mode = image.mode
        native_size = image.size
        if 'A' in image.getbands() and image.getchannel('A').getextrema() != (255,255):
            raise ValueError('Ground atlas has nonopaque pixels. Supply an opaque ground source; do not silently matte transparency.')
        boxes = crop_boxes(image.size, columns, rows, boxes)
        crops = [image.crop(box).convert('RGB') for box in boxes]
    native_side = crops[0].width
    if native_side < args.size:
        raise ValueError(f'Native cell {native_side}px is below requested {args.size}px. Upscaling is forbidden.')
    resized = [crop if crop.width == args.size else crop.resize((args.size,args.size),Image.Resampling.LANCZOS) for crop in crops]
    raw = [np.asarray(tile).copy() for tile in resized]
    source = raw[args.collar_source_index]
    # Toroidal half-offset uses real source pixels. Opposite output edges are
    # adjacent source pixels across its centre, rather than duplicated boundary rows.
    canonical = np.roll(source, shift=(-(args.size//2),-(args.size//2)), axis=(0,1))
    adapted, stitch_records = [], []
    for tile in raw:
        stitched, record = adapt_edges(tile,canonical,args.guard,args.reach)
        adapted.append(stitched)
        stitch_records.append(record)
    pair_results = []
    checks = []
    files = [f'{relative(out)}/ground-{i+1:02d}.png' for i in range(6)]
    for axis in ('horizontal','vertical'):
        reference_metrics = seam_metrics(canonical,canonical,axis)
        for first in range(6):
            for second in range(6):
                a,b = adapted[first],adapted[second]
                observed = np.stack((a[:,-1],b[:,0])) if axis=='horizontal' else np.stack((a[-1],b[0]))
                expected = np.stack((canonical[:,-1],canonical[:,0])) if axis=='horizontal' else np.stack((canonical[-1],canonical[0]))
                mismatches = int(np.count_nonzero(observed != expected))
                metrics = seam_metrics(a,b,axis)
                pair_results.append({'axis':axis,'firstTile':first+1,'secondTile':second+1,'files':[files[first],files[second]],'sourceRawJoin':seam_metrics(raw[first],raw[second],axis),'adaptedJoin':metrics,'referenceNaturalJoin':reference_metrics,'sharedCollarReferenceChannelMismatches':mismatches})
    mismatch_total = sum(x['sharedCollarReferenceChannelMismatches'] for x in pair_results)
    checks.append({'id':'all_6x6_horizontal_and_vertical_edge_reference_mismatches','status':'pass' if mismatch_total==0 else 'fail','value':mismatch_total,'threshold':0,'files':files})
    for axis in ('horizontal','vertical'):
        ratio = max(x['adaptedJoin']['joinToNearbyRatio'] for x in pair_results if x['axis']==axis)
        checks.append({'id':f'{axis}_join_to_nearby_ratio','status':'pass' if ratio<=1.5 else 'warn','value':ratio,'threshold':1.5,'files':files})
    cut_error = max(x['cutMeanRGBError'] for rows in stitch_records for x in rows)
    checks.append({'id':'maximum_inner_collar_cut_mean_RGB_error','status':'pass' if cut_error<=25 else 'warn','value':cut_error,'threshold':25,'files':files})
    if not generation:
        checks.append({'id':'original_generation_record_missing','status':'warn','value':1,'threshold':0,'files':[relative(atlas_path)]})
    if mismatch_total:
        raise ValueError('Shared collar invariant failed; no production files were written.')
    # Only begin publishing after all invariant computations finish.
    out.mkdir(parents=True)
    preview.mkdir(parents=True)
    (out/'native').mkdir()
    (out/'pre-adaptation').mkdir()
    entries=[]
    for i,(crop,raw_tile,tile) in enumerate(zip(crops,raw,adapted)):
        native_path=out/'native'/f'ground-{i+1:02d}.png'
        before_path=out/'pre-adaptation'/f'ground-{i+1:02d}.png'
        final_path=out/f'ground-{i+1:02d}.png'
        crop.save(native_path)
        Image.fromarray(raw_tile).save(before_path)
        Image.fromarray(tile).save(final_path)
        for support_path, role, source_path, operation in [
            (native_path,'production_support_native_crop',atlas_path,{'kind':'native crop','cropRectXYXY':boxes[i],'resampled':False,'generatedByAi':False,'newPaintedDetailCreated':False}),
            (before_path,'production_support_pre_adaptation',native_path,{'kind':'byte-equivalent pixels on new PNG encoding' if native_side==args.size else 'Lanczos downscale','from':[native_side,native_side],'to':[args.size,args.size],'resampled':native_side!=args.size,'generatedByAi':False,'newPaintedDetailCreated':False}),
        ]:
            write(Path(str(support_path)+'.derivation.json'),{'file':relative(support_path),'sha256':digest(support_path),'deliveryRole':role,'derivedFrom':{'file':relative(source_path),'sha256':digest(source_path),'generationRecord':relative(generation) if generation else None},'operation':operation,'actualModel':None,'actualQuality':None,'pivot':[.5,.5],'borderLTRB':[0,0,0,0]})
        item={'file':relative(final_path),'sha256':digest(final_path),'key':f'Map_{i+1}','label':LABELS[i],'weight':WEIGHTS[i],'dimensions':[args.size,args.size],'mode':'RGB','nativeCropFile':relative(native_path),'nativeCropSize':[native_side,native_side],'sourceCropRectXYXY':boxes[i],'preAdaptationFile':relative(before_path),'derivedFrom':{'file':relative(atlas_path),'sha256':digest(atlas_path),'generationRecord':relative(generation) if generation else None},'operation':{'kind':'native crop, optional downscale, lossless pixel-reuse common edge quilting','resampled':native_side!=args.size,'resize':{'from':[native_side,native_side],'to':[args.size,args.size],'filter':'Lanczos downscale only'} if native_side!=args.size else None,'generatedByAi':False,'newPaintedDetailCreated':False,'blurOrBlend':False,'collarReferenceIndex':args.collar_source_index,'collarReferenceOperation':'toroidal half-offset of source tile; copies actual source pixels','mandatoryGuardPx':args.guard,'maximumQuiltingExtentPx':args.reach,'changedPixelCountAgainstPreAdaptation':int(np.any(tile!=raw_tile,axis=2).sum()),'cutPaths':stitch_records[i]},'pivot':[.5,.5],'borderLTRB':[0,0,0,0],'actualModel':None,'actualQuality':None,'unityImportAdvice':{'status':'suggested_not_verified_in_Unity','spriteMode':'Single','pixelsPerUnit':args.size,'worldSize':[1,1],'filterMode':'Bilinear','wrapMode':'Clamp','mipMaps':False,'brightnessMultiplier':1,'sourceMaterialBrightnessWarning':'Source Map.mat multiplies RGB by 3; do not inherit blindly.'}}
        write(Path(str(final_path)+'.derivation.json'),item)
        entries.append(item)
    rng=random.Random(args.seed)
    map_rows=[[rng.choices(range(6),WEIGHTS,k=1)[0] for _ in range(100)] for _ in range(100)]
    props=[]
    for y in range(5):
        for x in range(4):
            props.append({'id':f'Prop-{len(props)+1:02d}','key':'Prop','positionWorld':[-50+(x+1)*20,-50+(y+1)*(100/6)],'artResource':None,'artResourceStatus':'bind separately to verified transparent destructible prop','blocksNavigation':False,'collisionNote':'Source Prop prefab has no Collider2D; do not invent a map blocker.'})
    assembly={'schemaVersion':1,'status':'art_assembly_data_not_Unity_runtime','mapKey':'Map1','sourceCommit':'3f905381d73a34b516030528b8ef6743868b9e52','tileWorldSize':[1,1],'width':100,'height':100,'tileCenterOriginWorld':[-50,-50],'tileIndexToWorld':'(-50+x,-50+y), source MapManager coordinate formula','occupiedBoundsWorld':[-50.5,-50.5,49.5,49.5],'gridOrigin':'bottom-left','rowsOrder':'bottom to top, Unity +Y up','tileIndices':'0-based; same order as tiles','tiles':[{'index':i,'file':entries[i]['file'],'key':entries[i]['key'],'weight':WEIGHTS[i]} for i in range(6)],'tileRows':map_rows,'randomSeedForReproducibleArtReview':args.seed,'sourceRandomSequenceReproduced':False,'propInstances':props,'camera':{'projection':'orthographic','sourceSize':8.5,'visibleWorldHeight':17,'viewportReference':[1920,1080],'tileDisplayPxAtReference':1080/17,'sourceClampMarginWorld':5},'walkability':'Open ground; no painted obstacles or portals. This art-only data is not a Unity collision/navigation acceptance.','navigationValidation':'Not a playable-map claim; Unity movement/collision deferred.'}
    write(out/'map1-assembly.json',assembly)
    # Image arrays use top-down rows; reverse the source bottom-up layout for review.
    grid_image(adapted,list(reversed(map_rows)),16).save(preview/'map1-overview.png')
    grid_image(adapted,[[y*3+x for x in range(3)] for y in range(2)],256).save(preview/'six-tiles.png')
    all_h=[[tile for second in range(6) for tile in (first,second)] for first in range(6)]
    # vertical pair atlas: column=first, row pairs=(first,second).
    all_v=[]
    for second in range(6):
        all_v.extend([list(range(6)),[second]*6])
    grid_image(adapted,all_h,128).save(preview/'horizontal-all-36-pairs.png')
    grid_image(adapted,all_v,128).save(preview/'vertical-all-36-pairs.png')
    mixed=[[((y*7+x*5+x//3)%6) for x in range(12)] for y in range(8)]
    grid_image(adapted,mixed,128).save(preview/'mixed-variants.png')
    grid_image(raw,mixed,128).save(preview/'mixed-before-adaptation.png')
    central=[map_rows[50+y][34:66] for y in reversed(range(-9,9))]
    camera_px_per_unit=1080/17
    camera=grid_image(adapted,central,64).resize((round(32*camera_px_per_unit),round(18*camera_px_per_unit)),Image.Resampling.LANCZOS)
    camera.crop(((camera.width-1920)//2,(camera.height-1080)//2,(camera.width-1920)//2+1920,(camera.height-1080)//2+1080)).save(preview/'camera-scale-ground.png')
    qa={'schemaVersion':1,'status':'numeric_edge_proof_complete_needs_visual_review','scope':'36 horizontal + 36 vertical combinations; reference-adjacency proof, not a claim of zero RGB step or source atlas tileability','checks':checks,'pairs':pair_results,'visualReview':{'status':'pending','required':['six native/final tiles','mixed-variants.png','mixed-before-adaptation.png','horizontal-all-36-pairs.png','vertical-all-36-pairs.png','map1-overview.png','camera-scale-ground.png']},'warningPolicy':'Report each WARN/FAIL with its exact id/value/threshold/files; never flatten a warning to all checks passed.'}
    write(out/'seam-qa.json',qa)
    write(out/'terrain-manifest.json',{'schemaVersion':1,'art_source':'host_image','operationRoute':'Existing generated raster crop/downscale/pixel-reuse quilting; no model called by this tool','atlas':relative(atlas_path),'atlasSha256':digest(atlas_path),'atlasNativeSize':list(native_size),'atlasMode':native_mode,'generationRecord':relative(generation) if generation else None,'sourceStyle':'Daoist chibi hand-painted floor; generated artwork remains the only painted source','status':'needs_visual_review','tiles':entries,'assembly':'map1-assembly.json','seamQA':'seam-qa.json','previewDirectory':relative(preview)})
    preview_rel=relative(out)
    html='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>清竹道场·地块美术验收</title><style>body{margin:24px;background:#ede5cf;color:#245c50;font:18px sans-serif}img{max-width:100%;height:auto;border:1px solid #bba675}figure{margin:24px 0}figcaption{margin:10px 0}h1{font-size:28px}a{color:#245c50}</style><h1>清竹道场地块美术验收</h1><p>六种同一地面变体；下列为生成美术裁切、缩小及共有外缘像素拼接预览，未接入Unity。</p>'''
    for filename,caption in [('six-tiles.png','六种正式地块（缩小审图）'),('mixed-variants.png','等量混排，检查变体与共同外缘'),('mixed-before-adaptation.png','边缘适配前，同一混排对照'),('horizontal-all-36-pairs.png','横向全部36种组合'),('vertical-all-36-pairs.png','纵向全部36种组合'),('map1-overview.png','100×100源权重地图，种子固定，仅缩小总览'),('camera-scale-ground.png','源正交镜头尺度的地面细节，未叠加人物')]:
        html+=f'<figure><figcaption>{caption}</figcaption><a href="{filename}"><img src="{filename}" alt="{caption}"></a></figure>'
    (preview/'index.html').write_text(html+'</html>',encoding='utf-8')
    print(json.dumps({'output':relative(out),'preview':relative(preview),'status':qa['status'],'checks':checks},ensure_ascii=False))


if __name__=='__main__':
    main()
