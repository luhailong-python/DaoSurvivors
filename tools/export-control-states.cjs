'use strict';

const fs = require('node:fs/promises');
const path = require('node:path');
const crypto = require('node:crypto');

const root = path.resolve(__dirname, '..');
const sourceDirectory = path.join(root, 'art', 'common', 'states');
const outputDirectory = path.join(root, 'art', 'common', 'controls');
const recordFile = path.join(root, 'docs', 'control-state-derivations.json');
const sourceRecordFile = path.join(root, 'docs', 'art-extension-sources.json');
const defaultPlaywright = 'C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright';
const defaultBrowser = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
const families = {
  primary_button: [460, 112],
  tab: [360, 114],
  list_row: [360, 96],
};
const states = ['normal', 'pressed', 'selected', 'disabled', 'locked'];
const styles = {
  normal: { source: 'normal', filter: 'none', opacity: '1', kind: 'source-copy' },
  pressed: { source: 'normal', filter: 'brightness(0.82) saturate(0.95)', opacity: '1', kind: 'native-ui-state-composite' },
  selected: { source: 'selected', filter: 'none', opacity: '1', kind: 'source-copy' },
  disabled: { source: 'normal', filter: 'grayscale(0.7)', opacity: '0.48', kind: 'native-ui-state-composite' },
  locked: { source: 'disabled', filter: 'none', opacity: '1', kind: 'source-copy-semantic-reuse' },
};
const sha = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const relative = file => path.relative(root, file).replaceAll(path.sep, '/');
const argValue = (flag, fallback) => {
  const index = process.argv.indexOf(flag);
  return index === -1 ? fallback : process.argv[index + 1];
};

function dimensions(bytes) {
  if (bytes.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') throw new Error('Expected PNG bytes.');
  return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
}

async function exists(file) {
  try { await fs.access(file); return true; } catch { return false; }
}

async function inspectPng(page, bytes) {
  // The data URL is an internal browser input. It is never printed or saved in metadata.
  return page.evaluate(async dataUrl => {
    const image = new Image();
    image.src = dataUrl;
    await image.decode();
    const canvas = document.createElement('canvas');
    canvas.width = image.naturalWidth;
    canvas.height = image.naturalHeight;
    const context = canvas.getContext('2d', { willReadFrequently: true });
    context.drawImage(image, 0, 0);
    const rgba = context.getImageData(0, 0, canvas.width, canvas.height).data;
    let min = 255, max = 0, transparent = 0, nonzero = 0;
    let left = canvas.width, top = canvas.height, right = -1, bottom = -1;
    const boundary = { top: 0, right: 0, bottom: 0, left: 0 };
    for (let y = 0; y < canvas.height; y++) {
      for (let x = 0; x < canvas.width; x++) {
        const alpha = rgba[(y * canvas.width + x) * 4 + 3];
        min = Math.min(min, alpha); max = Math.max(max, alpha);
        if (alpha === 0) transparent++;
        if (alpha > 0) {
          nonzero++;
          left = Math.min(left, x); top = Math.min(top, y);
          right = Math.max(right, x); bottom = Math.max(bottom, y);
        }
        if (y === 0) boundary.top = Math.max(boundary.top, alpha);
        if (x === canvas.width - 1) boundary.right = Math.max(boundary.right, alpha);
        if (y === canvas.height - 1) boundary.bottom = Math.max(boundary.bottom, alpha);
        if (x === 0) boundary.left = Math.max(boundary.left, alpha);
      }
    }
    return {
      dimensions: [canvas.width, canvas.height],
      alphaExtrema: [min, max], transparentPixels: transparent, nonzeroAlphaPixels: nonzero,
      alphaBoundsTopLeftExclusiveRightBottom: right < 0 ? null : [left, top, right + 1, bottom + 1],
      outermostEdgeMaximumAlpha: boundary,
      hasRealTransparency: min === 0 && max > 0 && transparent > 0,
    };
  }, `data:image/png;base64,${bytes.toString('base64')}`);
}

async function verifyExisting() {
  const record = JSON.parse(await fs.readFile(recordFile, 'utf8'));
  if (record.assets.length !== 15) throw new Error('Expected fifteen recorded controls.');
  for (const asset of record.assets) {
    const output = await fs.readFile(path.join(root, asset.output));
    const source = await fs.readFile(path.join(root, asset.source));
    if (sha(output) !== asset.sha256 || sha(source) !== asset.sourceSha256) throw new Error(`Hash changed: ${asset.output}`);
    if (dimensions(output).join(',') !== asset.dimensions.join(',')) throw new Error(`Canvas changed: ${asset.output}`);
  }
  process.stdout.write(`${JSON.stringify({ verified: 15, hashAndCanvasChecks: 'passed', overwrittenPngs: 0 })}\n`);
}

async function exportStates() {
  // Refuse any existing PNG, including a partial previous export. Never overwrite user art.
  for (const family of Object.keys(families)) {
    for (const state of states) {
      const destination = path.join(outputDirectory, `${family}_${state}.png`);
      if (await exists(destination)) throw new Error(`Output already exists: ${relative(destination)}. Use --verify to check the saved export.`);
    }
  }
  const sourceRecord = JSON.parse(await fs.readFile(sourceRecordFile, 'utf8'));
  const playwrightPath = argValue('--playwright-module', defaultPlaywright);
  const browserExecutable = argValue('--browser-executable', defaultBrowser);
  const { chromium } = require(playwrightPath);
  const playwrightVersion = require(path.join(playwrightPath, 'package.json')).version;
  const browser = await chromium.launch({ executablePath: browserExecutable, headless: true, args: ['--force-color-profile=srgb'] });
  const prepared = [];
  const browserVersion = browser.version();
  try {
    for (const [family, [width, height]] of Object.entries(families)) {
      const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1, colorScheme: 'light' });
      const page = await context.newPage();
      for (const state of states) {
        const style = styles[state];
        const sourceFile = path.join(sourceDirectory, `${family}_${style.source}.png`);
        const sourceBytes = await fs.readFile(sourceFile);
        const approved = sourceRecord.stateAssets.find(asset => asset.output === relative(sourceFile));
        if (!approved || sha(sourceBytes) !== approved.sha256) throw new Error(`Unverified source: ${relative(sourceFile)}`);
        if (dimensions(sourceBytes).join(',') !== `${width},${height}`) throw new Error(`Source canvas mismatch: ${family}`);
        const css = `display:block;width:${width}px;height:${height}px;filter:${style.filter};opacity:${style.opacity};transform:none;image-rendering:auto;`;
        let outputBytes = sourceBytes;
        let layoutEvidence = null;
        if (style.kind === 'native-ui-state-composite') {
          const dataUrl = `data:image/png;base64,${sourceBytes.toString('base64')}`;
          await page.setContent(`<!doctype html><html><head><style>html,body{margin:0;padding:0;width:${width}px;height:${height}px;background:transparent;overflow:hidden;}body{zoom:1;}</style></head><body><img id="control" alt="" draggable="false" src="${dataUrl}" style="${css}"></body></html>`);
          await page.locator('#control').evaluate(image => image.decode());
          layoutEvidence = await page.locator('#control').evaluate(image => {
            const box = image.getBoundingClientRect(), computed = getComputedStyle(image);
            return { naturalWidth: image.naturalWidth, naturalHeight: image.naturalHeight,
              x: box.x, y: box.y, width: box.width, height: box.height,
              devicePixelRatio: devicePixelRatio, filter: computed.filter, opacity: computed.opacity,
              dynamicText: document.body.textContent.trim() };
          });
          if (layoutEvidence.x !== 0 || layoutEvidence.y !== 0 || layoutEvidence.width !== width || layoutEvidence.height !== height || layoutEvidence.devicePixelRatio !== 1 || layoutEvidence.dynamicText !== '') throw new Error('Unexpected browser scaling, offset or text.');
          outputBytes = await page.screenshot({ omitBackground: true, animations: 'disabled', scale: 'css' });
        }
        const pixelInspection = await inspectPng(page, outputBytes);
        if (!pixelInspection.hasRealTransparency || pixelInspection.dimensions.join(',') !== `${width},${height}`) throw new Error(`Invalid PNG alpha or dimensions: ${family}_${state}`);
        if (state === 'disabled' && pixelInspection.alphaExtrema[1] > 123) throw new Error('Disabled opacity did not render as specified.');
        const destination = path.join(outputDirectory, `${family}_${state}.png`);
        prepared.push({ bytes: outputBytes, destination, metadata: {
          family, state, output: relative(destination), sha256: sha(outputBytes), source: relative(sourceFile), sourceSha256: sha(sourceBytes),
          dimensions: [width, height], pivotNormalizedBottomLeft: [0.5, 0.5], canvasAnchorTopLeftPx: [width / 2, height / 2],
          pixelInspection, operation: { type: style.kind, tool: style.kind === 'native-ui-state-composite' ? 'Playwright / Microsoft Edge DOM-CSS screenshot' : 'filesystem byte copy',
            exactImageCss: css, stylesheet: `html,body{margin:0;padding:0;width:${width}px;height:${height}px;background:transparent;overflow:hidden;}body{zoom:1;}`,
            filter: style.filter, opacity: Number(style.opacity), deviceScaleFactor: 1, outputScale: 'css', omitBackground: true,
            crop: null, resize: null, translation: [0, 0], generatedByAi: false, increasedNativeDetail: false },
          layoutEvidence,
          semanticReuse: state === 'locked' ? 'Existing source disabled artwork includes a lock. Reused byte-for-byte specifically as locked; no new locked painting or separate AI edit is claimed.' : state === 'disabled' ? 'Normal source rendered with opacity 0.48 and grayscale 0.7; this generic disabled state has no baked lock.' : null,
          sourceEvidence: { record: 'docs/art-extension-sources.json', sourceEntryOutput: approved.output, referenceRepositorySource: approved.source, originalEvidence: approved.sourceEvidence },
          qualityProvenance: { actualModel: approved.actualModel, actualQuality: approved.actualQuality, note: 'Quality and model trace to the existing source artwork. Browser/native UI state composition does not call an image model or create new painted detail.' },
          containsDynamicText: false, nineSliceFromSourceManifest: approved.sourceManifestEntry?.nine_slice ?? null,
        } });
      }
      await context.close();
    }
  } finally { await browser.close(); }

  await fs.mkdir(outputDirectory, { recursive: true });
  for (const asset of prepared) await fs.writeFile(asset.destination, asset.bytes, { flag: 'wx' });
  const record = {
    schemaVersion: 1, exportedAtUtc: new Date().toISOString(), projectDirectory: root,
    purpose: 'Transparent native UI control-state export for the art-only phase',
    exporter: { script: 'tools/export-control-states.cjs', scriptSha256: sha(await fs.readFile(__filename)), nodeVersion: process.version, playwrightVersion, browserExecutable, browserVersion },
    outputDirectory: 'art/common/controls', sameCanvasAndPivotWithinEveryFamily: true,
    sourceRecordsPreserved: true, sourcePngsModified: false, overwrittenExistingPngs: 0,
    notes: ['normal/selected are exact source-byte copies.', 'locked is an exact copy of existing disabled art with a baked lock; semantic reuse is declared.', 'pressed/disabled are native DOM/CSS state composites, not AI generation or new painting.', 'All rendered images use the native source canvas, deviceScaleFactor 1, no transform and no resampling size change.', 'No dynamic text or base64 media payload is stored in this record.'],
    assets: prepared.map(asset => asset.metadata),
    validation: { pngCount: prepared.length, realAlpha: 'passed', nativeCanvas: 'passed', samePivot: 'passed', noDynamicText: 'passed', copiedStateBytesPreserved: 'passed', renderedStateCount: prepared.filter(asset => asset.metadata.operation.type === 'native-ui-state-composite').length },
  };
  await fs.writeFile(recordFile, `${JSON.stringify(record, null, 2)}\n`, { flag: 'wx' });
  process.stdout.write(`${JSON.stringify({ exported: prepared.length, browserComposites: record.validation.renderedStateCount, pngDirectory: record.outputDirectory, record: relative(recordFile), dimensionsAndAlpha: 'passed', existingPngsOverwritten: 0 })}\n`);
}

(process.argv.includes('--verify') ? verifyExisting() : exportStates()).catch(error => {
  process.stderr.write(`${error.stack || error}\n`);
  process.exitCode = 1;
});
