"""Build the art-only manifest from real files and their provenance records.

Reads F: only to snapshot cited text evidence. Does not change images, Unity, or Git.
Unknown provenance stays explicit; rerun after adding new sidecars or screen layouts.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / 'art'
REFERENCE = Path('F:/work/image')


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def new_york_time():
    try:
        return datetime.now(ZoneInfo('America/New_York')).isoformat()
    except Exception:
        # Windows Python need not bundle tzdata; .NET has the OS timezone table.
        command = "[TimeZoneInfo]::ConvertTimeBySystemTimeZoneId([DateTimeOffset]::UtcNow,'Eastern Standard Time').ToString('o')"
        return subprocess.check_output(['powershell', '-NoProfile', '-Command', command], cwd=ROOT, text=True).strip()


def rel(path):
    return Path(path).relative_to(ROOT).as_posix()


def border(value):
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        return [value.get(k, 0) for k in ('left', 'bottom', 'right', 'top')]
    return [0, 0, 0, 0]


def collect_reference_evidence(value, output):
    if isinstance(value, dict):
        for key, sub in value.items():
            if key in ('sourceEvidence', 'originalEvidence') and isinstance(sub, list):
                output.update(s for s in sub if isinstance(s, str))
            collect_reference_evidence(sub, output)
    elif isinstance(value, list):
        for sub in value:
            collect_reference_evidence(sub, output)


def snapshot_evidence(records):
    cited = set()
    for record in records:
        collect_reference_evidence(record, cited)
    results = []
    for source in sorted(cited):
        source_path = Path(source)
        if not source_path.is_absolute():
            source_path = REFERENCE / source
        try:
            source_rel = source_path.resolve().relative_to(REFERENCE.resolve())
        except ValueError:
            continue
        if source_path.suffix.lower() not in ('.md', '.json', '.txt'):
            continue
        item = {'referenceRepositoryRelativePath': source_rel.as_posix()}
        if source_path.is_file():
            dest = ROOT / 'docs/provenance/art-reference' / source_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Deliberately byte-copy text evidence; all source files remain read-only.
            dest.write_bytes(source_path.read_bytes())
            item.update({'status': 'snapshot_available', 'snapshot': rel(dest), 'sha256': sha(dest)})
        else:
            item['status'] = 'missing_in_current_reference_checkout_not_restored'
        results.append(item)
    write(ROOT / 'docs/provenance/art-reference-index.json', results)
    return results


def portable_illustration_record(name):
    old = ROOT / f'Assets/DaoSurvivor/Resources/DaoArt/{name}.png.generation.json'
    new = ART / f'illustrations/{name}.png.generation.json'
    if new.exists():
        return read(new)
    if not old.is_file():
        return None
    record = read(old)
    original = copy.deepcopy(record)
    archive = ROOT / f'docs/provenance/original-records/{name}.png.generation.json'
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(old.read_bytes())
    target = ART / f'illustrations/{name}.png'
    if sha(target) != original['sha256']:
        raise ValueError(f'Illustration byte-copy mismatch: {name}')
    record['originalRecordedFile'] = original.get('projectRelativeOutput')
    record['originalGenerationRecordSnapshot'] = rel(archive)
    record['originalGenerationRecordSha256'] = sha(archive)
    record['projectRelativeOutput'] = rel(target)
    record['absoluteOutput'] = str(target)
    record['file'] = target.name
    record['actualRequestArgumentsReceipt'] = f'../../docs/production/{name}.receipt.json'
    record['artOnlyPortableCopy'] = {
        'operation': 'Byte-identical relocation of an existing native generated image; no new generation, AI edit, crop, or resampling.',
        'sourceRecordedFile': record['originalRecordedFile'],
        'sha256Unchanged': True,
        'generatedAtUnchanged': True,
        'originalRecordFieldsOtherwisePreserved': True,
    }
    write(new, record)
    return record


def source_record_index(base, extension, states):
    by_path = {}
    for record in base['assets']:
        name = Path(record['output']).name
        category = 'common' if record.get('role') == 'UI skin' else ('icons' if name.startswith('icon-') else 'characters')
        by_path[f'art/{category}/{name}'] = ('docs/ASSET_SOURCES.json', record)
    for record in extension['stateAssets'] + extension['commonReplacements']:
        by_path[record['output']] = ('docs/art-extension-sources.json', record)
    for record in states['assets']:
        by_path[record['output']] = ('docs/control-state-derivations.json', record)
    for record in base['fonts']['files']:
        by_path[f"art/fonts/{Path(record['output']).name}"] = ('docs/ASSET_SOURCES.json', record)
    return by_path


def player_source_index():
    """Index recorded existing sword files without reading the F: checkout."""
    by_path = {}
    animation_path = ART / 'whole-game/players/sword/animation.json'
    if not animation_path.is_file():
        return by_path
    animation = read(animation_path)
    clips_by_frame = {}
    for clip in animation.get('clips', []):
        for frame in clip.get('frames', []):
            clips_by_frame[frame] = clip
    for original in animation.get('files', []):
        record = copy.deepcopy(original)
        key = record['file']
        record['source'] = record.get('sourceRelativeToArtRepository')
        record['artSource'] = animation.get('artSource')
        record['sourceIdentity'] = animation.get('sourceIdentity')
        record['pivotNormalizedBottomLeft'] = animation.get('pivotNormalizedBottomLeft', [0.5, 41 / 512])
        record['sourceEvidence'] = [rel(animation_path), 'docs/whole-game/player-sword-source/manifest.json']
        if key in clips_by_frame:
            clip = clips_by_frame[key]
            record['animationClip'] = {field: clip.get(field) for field in (
                'name', 'action', 'facing', 'frameDurationMs', 'loop', 'totalDurationMs',
                'timingBasis', 'sourceActionLabel')}
        by_path[key] = (rel(animation_path), record)
    return by_path


def default_delivery_role(key, path):
    if key == 'art/branding/yiqi-dangqian-v1/logo-primary.png':
        return 'production_support_unselected_brand_source'
    if key.startswith('art/whole-game/players/'):
        if '/parts/' in key:
            return 'production_support_rig_part'
        if path.name == 'strip.png':
            return 'runtime_sprite_strip_multiple'
        if '/idle/' in key or '/run/' in key:
            return 'runtime_frame'
    if '/sheets/' in key:
        return 'review_only' if '-review-' in key else ('production_source_sheet_do_not_equal_grid_slice' if 'icons-v2' in key else 'production_source_sheet_follow_manifest')
    if '/native/' in key:
        return 'production_support_native_crop'
    if '/pre-adaptation/' in key:
        return 'production_support_pre_adaptation'
    if '/states/' in key:
        return 'source_support_for_formal_controls'
    if key.endswith('/dissolve-noise.png'):
        return 'runtime_shader_texture'
    if key.endswith('/contact-shadow.png'):
        return 'runtime_shadow_sprite'
    if path.suffix.lower() == '.txt':
        return 'license'
    return 'independent_art_resource'


def portable_source(value):
    if isinstance(value, str):
        path = Path(value)
        if path.is_absolute():
            try:
                return path.relative_to(ROOT).as_posix()
            except ValueError:
                pass
        return value
    return value


def apply_world_import_advice(item, record):
    """Keep part authoring pivots separate from fixed player frame roots."""
    key = item['file']
    advice = item['unityImportAdvice']
    if key.startswith('art/whole-game/players/'):
        if '/parts/' in key:
            advice.update({'textureType': 'Not imported into runtime by default', 'spriteMode': None})
            item['authoringPart'] = {field: record.get(field) for field in (
                'part', 'nativeSize', 'nativePivot', 'sourceCrop', 'displayScale', 'bindJoint', 'parent', 'mirrorAroundJoint')}
            if record.get('nativePivot'):
                x, y = record['nativePivot']
                width, height = item['dimensions']
                advice['pivotNormalizedBottomLeft'] = [x / width, (height - y) / height]
                advice['pivotBasis'] = 'Native part joint in top-left pixels, converted to normalized bottom-left; authoring support only.'
        elif item['dimensions'][1] == 512:
            advice['pivotNormalizedBottomLeft'] = [0.5, 41 / 512]
            advice['pivotBasis'] = 'Fixed 512x512 per-frame root [256,471]; never normalize across the full strip width.'
            advice['meshType'] = 'FullRect'
            item['animationRecord'] = '/'.join(key.split('/')[:4]) + '/animation.json'
            if item['deliveryRole'] == 'runtime_sprite_strip_multiple':
                count = item['dimensions'][0] // 512
                advice.update({
                    'textureType': 'Sprite (2D and UI) / Multiple',
                    'spriteMode': 'Multiple',
                    'imageType': 'Fixed 512x512 frame slices; do not display the whole strip as a Single sprite',
                    'sliceRectanglesXYWH': record.get('sliceRectanglesXYWH') or [[index * 512, 0, 512, 512] for index in range(count)],
                    'sliceCoordinateOrigin': 'bottom-left; every slice spans the single 512-pixel-high strip row',
                    'pivotAppliesTo': 'Every individual 512x512 slice',
                })
            else:
                advice.update({'textureType': 'Sprite (2D and UI) / Single', 'spriteMode': 'Single'})
    elif key.endswith('/dissolve-noise.png'):
        advice.update({
            'textureType': 'Default texture / shader sampler',
            'spriteMode': None,
            'imageType': None,
            'pivotNormalizedBottomLeft': None,
            'usage': 'Grayscale dissolve shader support; no visible sprite quad by default.',
            'sRGB': True,
            'wrapMode': 'Clamp',
            'mipMaps': False,
            'settingBasis': 'Preserve source dissolveTex.png.meta sRGBTexture=1, wrapU/V=1, enableMipMap=0 as initial advice; shader integration is unverified.',
        })
    elif key.endswith('/contact-shadow.png'):
        advice['usage'] = 'Flat contact shadow below characters; centre pivot on the ground plane, scale independently of character frame canvas.'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-reference-snapshots', action='store_true', help='Rebuild using local evidence only; never access F:')
    args = parser.parse_args()
    base = read(ROOT / 'docs/ASSET_SOURCES.json')
    extension = read(ROOT / 'docs/art-extension-sources.json')
    states = read(ROOT / 'docs/control-state-derivations.json')
    for name in ('lobby-v1', 'arena-v1'):
        portable_illustration_record(name)
    snapshots = read(ROOT / 'docs/provenance/art-reference-index.json') if args.no_reference_snapshots else snapshot_evidence([base, extension, states])
    source_index = source_record_index(base, extension, states)
    source_index.update(player_source_index())
    master = read(ROOT / 'docs/ui-suite/UI_COVERAGE.json')
    screen_uses = {}
    for screen in master['screens']:
        for resource in screen.get('independentAssets', []):
            screen_uses.setdefault(resource.replace('\\', '/'), []).append(screen['id'])
    assets = []
    warnings = []
    image_suffixes = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
    resource_suffixes = image_suffixes | {'.otf', '.ttf', '.txt', '.webm', '.mp4', '.svg'}
    for path in sorted(ART.rglob('*')):
        if not path.is_file() or path.suffix.lower() not in resource_suffixes:
            continue
        key = rel(path)
        item = {'file': key, 'bytes': path.stat().st_size, 'sha256': sha(path)}
        item['deliveryRole'] = default_delivery_role(key, path)
        item['usedByScreens'] = screen_uses.get(key, [])
        item['usageStatus'] = 'active_ui_suite' if item['usedByScreens'] else 'available_support_or_non_ui_resource'
        item['actualModel'] = None
        item['actualQuality'] = None
        item['modelQualityEvidenceStatus'] = 'Unconfirmed where not disclosed. Config/prompt/C2PA generic software labels are not actual model or quality proof.'
        record_file = None
        record = None
        for suffix in ('.derivation.json', '.generation.json', '.adoption.json'):
            sidecar = Path(str(path) + suffix)
            if sidecar.is_file():
                record_file, record = rel(sidecar), read(sidecar)
                break
        if record is None and key in source_index:
            record_file, record = source_index[key]
        if record:
            if record.get('deliveryRole'):
                item['deliveryRole'] = record['deliveryRole']
            item['provenanceRecord'] = record_file
            item['provenanceEntry'] = key
            expected = record.get('sha256')
            item['provenanceSha256Matches'] = expected == item['sha256'] if expected else None
            if expected and expected != item['sha256']:
                warnings.append({'file': key, 'problem': 'source_record_hash_mismatch', 'expected': expected, 'actual': item['sha256']})
            item['operation'] = record.get('operation') or record.get('adoptionType')
            item['relationship'] = record.get('relationship') or ('直接复用' if record.get('copyVerified') else None)
            item['source'] = portable_source(record.get('derivedFrom') or record.get('referenceRepositoryRelativePath') or record.get('sourceArtPath') or record.get('source') or record.get('sourceUrl') or record.get('evidence', {}).get('sourceArtifact'))
            item['sourceEvidence'] = record.get('sourceEvidence', [])
            item['generationInThisProject'] = record.get('tool') in ('image_gen__imagegen', 'image_gen.imagegen')
            for field in ('sourceKey', 'sourceIdentity', 'sourceArtRepository', 'sourceSHA256', 'sourceSha256', 'copyVerified', 'sourceRecords', 'selectedManifestSnapshot', 'artSource', 'animationClip'):
                if field in record:
                    item[field] = record[field]
            if 'originalRecordedFile' in record:
                item['originalRecordedFile'] = record['originalRecordedFile']
            if record.get('sourceManifestEntry'):
                item['historicalSourceProcessing'] = record['sourceManifestEntry'].get('processing') or record['sourceManifestEntry'].get('authoring')
            if record.get('configSnapshot'):
                item['configTarget'] = record['configSnapshot']
                item['submittedParameters'] = record.get('submittedParameters')
                item['generatedAt'] = record.get('generatedAt')
                item['receipt'] = record.get('evidence', {}).get('receipt')
                item['references'] = record.get('references')
            item['actualModel'] = record.get('actualModel')
            item['actualQuality'] = record.get('actualQuality')
        elif '-review-' in key:
            sheet = key.replace('-review-dark', '').replace('-review-light', '')
            item.update({'source': sheet, 'operation': 'Native sheet composite on light/dark review background; no AI generation or new painted detail.', 'provenanceRecord': 'docs/icon-atlas1-slices.json' if 'attribute' in key else 'docs/icon-atlas2-slices.json'})
        else:
            item['provenanceStatus'] = 'pending_sidecar_or_source_record'
            warnings.append({'file': key, 'problem': 'pending_provenance'})
        if path.suffix.lower() in image_suffixes:
            with Image.open(path) as image:
                image.load()
                item['dimensions'] = list(image.size)
                item['mode'] = image.mode
                alpha = image.getchannel('A') if 'A' in image.getbands() else None
                item['alphaExtrema'] = list(alpha.getextrema()) if alpha is not None else None
                item['hasRealTransparency'] = bool(alpha and alpha.getextrema()[0] < 255)
                item['alphaBoundsTopLeftExclusiveRightBottom'] = list(alpha.getbbox()) if alpha and alpha.getbbox() else None
            record = record or {}
            source_manifest = record.get('sourceManifestEntry', {})
            nineslice = record.get('nineSliceFromSourceManifest') or source_manifest.get('nine_slice') or record.get('nineSliceBordersLeftBottomRightTop') or record.get('borderLeftBottomRightTop')
            if nineslice is None:
                nineslice = record.get('borderLTRB', [0, 0, 0, 0])
                if 'borderLTRB' in record:
                    b = nineslice
                    nineslice = [b[0], b[3], b[2], b[1]]
            b = border(nineslice)
            slice_mode = 'Sliced' if any(b) else 'Simple / preserve aspect'
            if item['deliveryRole'].startswith(('production_source','production_support')) or item['deliveryRole'] == 'review_only':
                sprite_type = 'Not imported into runtime by default'
            else:
                sprite_type = 'Sprite (2D and UI) / Single'
            item['unityImportAdvice'] = {
                'validation': '建议；尚未在Unity导入或运行验证',
                'textureType': sprite_type,
                'spriteMode': 'Single' if sprite_type.startswith('Sprite') else None,
                'imageType': slice_mode,
                'pivotNormalizedBottomLeft': record.get('pivotNormalizedBottomLeft') or record.get('pivotBottomLeft') or record.get('pivot') or [0.5, 0.5],
                'borderLeftBottomRightTopPx': b,
                'borderBasis': 'Copied from cited source contract' if any(b) else 'Nonstretch artwork / zero border',
                'filterMode': 'Bilinear',
                'wrapMode': 'Clamp',
                'sRGB': True,
                'alphaIsTransparency': item['hasRealTransparency'],
                'mipMaps': False,
                'maxSizeAdvice': next((size for size in (32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384) if size >= max(item['dimensions'])), 16384),
                'compressionAdvice': '先用None核验；目标平台压缩在Unity阶段对照验收图决定',
            }
            if record.get('unityImportAdvice'):
                item['unityImportAdvice'].update(record['unityImportAdvice'])
            if record.get('meshType'):
                item['unityImportAdvice']['meshType'] = record['meshType']
            for field in ('filterMode', 'wrapMode'):
                if record.get(field):
                    item['unityImportAdvice'][field] = record[field]
            if 'mipmaps' in record:
                item['unityImportAdvice']['mipMaps'] = record['mipmaps']
            apply_world_import_advice(item, record)
            if source_manifest.get('minimum_size'):
                item['unityImportAdvice']['sourceMinimumSizePx'] = source_manifest['minimum_size']
            if source_manifest.get('resize_axes'):
                item['unityImportAdvice']['sourceResizeAxes'] = source_manifest['resize_axes']
            if source_manifest.get('content_insets'):
                item['contentInsetsPx'] = source_manifest['content_insets']
            if key == 'art/common/title_plate.png':
                item['unityImportAdvice']['imageType'] = 'Simple / whole proportional; do not nine-slice'
            if key.startswith('art/common/controls/'):
                item['controlFamily'] = record.get('family')
                item['controlState'] = record.get('state')
                item['containsDynamicText'] = False
                item['fixedGlyph'] = 'source lock glyph' if record.get('state') == 'locked' else ('source check glyph' if record.get('state') == 'selected' else None)
            if key.startswith('art/characters/'):
                item['animationCoverage'] = 'Static single image only; no animation inferred from a source frame filename.'
        elif path.suffix.lower() in ('.otf', '.ttf'):
            item['fontFamily'] = base['fonts']['family']
            item['license'] = base['fonts']['license']
            item['licenseFile'] = 'art/fonts/NotoSansSC-OFL.txt'
            item['unityImportAdvice'] = {'validation': '建议；尚未在Unity导入验证', 'type': 'Font; create TextMeshPro SDF in integration stage if used', 'chineseGlyphs': 'Keep Simplified Chinese coverage; fallback and dynamic atlas memory to validate later'}
        assets.append(item)
        if key.startswith('art/branding/'):
            item['brandingStatus'] = 'source_only_unselected' if item['deliveryRole'] == 'production_support_unselected_brand_source' else 'formal_branding_resource'
            item['brandSource'] = 'docs/branding/BRAND.json'
    manifest = {
        'schemaVersion': 1,
        'workingTitle': master['workingTitle'],
        'gameName': master.get('gameName', master['workingTitle']),
        'titleStatus': master.get('titleStatus'),
        'branding': {'record': 'docs/branding/BRAND.json', 'gameName': master.get('gameName', master['workingTitle']), 'displayTagline': master.get('displayTagline'), 'formalResources': sum(x.get('brandingStatus') == 'formal_branding_resource' for x in assets), 'sourceOnlyResources': sum(x.get('brandingStatus') == 'source_only_unselected' for x in assets)},
        'phase': 'art-only; Unity integration deferred',
        'generatedAtNewYork': new_york_time(),
        'projectDirectory': str(ROOT),
        'referenceGame': master['referenceGame'],
        'artReference': master['artReference'],
        'deliveryGithub': None,
        'deliveryGithubStatus': '待用户提供；没有执行提交、推送或发布',
        'scope': 'Current art/ files only. UI screen renders/layouts are indexed in docs/ui-suite/UI_COVERAGE.json. Frozen older Unity Assets/Packages/ProjectSettings and .reference clone are excluded.',
        'generationEvidenceRule': 'Configured targets, submitted fields and actual returned metadata remain separate. No returned model/quality is inferred from current configuration.',
        'sourceTextSnapshots': 'docs/provenance/art-reference-index.json',
        'sourceSnapshotCounts': dict(Counter(x['status'] for x in snapshots)),
        'unityValidation': 'All listed settings are import advice; no Unity editor import, shader, atlas packing or Play Mode validation performed in this art-only phase.',
        'counts': {'files': len(assets), 'byDeliveryRole': dict(Counter(x['deliveryRole'] for x in assets)), 'imageFiles': sum('dimensions' in x for x in assets), 'imagesWithRealTransparency': sum(x.get('hasRealTransparency', False) for x in assets), 'activeUiResourceFiles': sum(bool(x['usedByScreens']) for x in assets)},
        'warnings': warnings,
        'assets': assets,
    }
    write(ART / 'manifest.json', manifest)
    print(json.dumps({'manifest': 'art/manifest.json', 'counts': manifest['counts'], 'warnings': warnings, 'snapshots': manifest['sourceSnapshotCounts']}, ensure_ascii=False))


if __name__ == '__main__':
    main()
