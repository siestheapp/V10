#!/usr/bin/env node
import fs from 'fs';
import fse from 'fs-extra';
import path from 'path';
import chokidar from 'chokidar';
import sharp from 'sharp';
import smartcrop from 'smartcrop-sharp';
import crypto from 'crypto';

const root = process.cwd();
const CONFIG_PATH = path.resolve(root, 'scripts/autocrop.config.json');

function parseArgs(argv) {
  const flags = new Set();
  const kv = {};
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith('--')) {
      const [k, v] = a.replace(/^--/, '').split('=');
      if (v === undefined) flags.add(k);
      else kv[k] = v;
    }
  }
  return { flags, kv };
}

function loadConfig() {
  const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
  return JSON.parse(raw);
}

function mapStrategy(strategy) {
  if (strategy === 'attention') return sharp.strategy.attention;
  if (strategy === 'entropy') return sharp.strategy.entropy;
  return sharp.strategy.attention;
}

async function ensureDirs(cfg) {
  await fse.ensureDir(path.resolve(root, cfg.inputDir));
  await fse.ensureDir(path.resolve(root, cfg.outputDir));
  await fse.ensureDir(path.resolve(root, cfg.archiveDir));
}

function baseNameNoExt(file) {
  return path.basename(file, path.extname(file));
}

async function processOne(inputPath, cfg) {
  const inputAbs = path.resolve(root, inputPath);
  const origBase = baseNameNoExt(inputAbs);
  const hash = cfg.dedupeByHash ? crypto.createHash('sha1').update(fs.readFileSync(inputAbs)).digest('hex').slice(0,8) : '';
  const name = cfg.dedupeByHash ? `${origBase}-${hash}` : origBase;
  const strategy = mapStrategy(cfg.strategy);

  for (const t of cfg.targets) {
    const outBase = path.resolve(root, cfg.outputDir, `${name}-${t.name}`);
    const ext = (cfg.outputFormat || 'png').toLowerCase();
    const outPath = `${outBase}.${ext}`;
    if (cfg.dedupeByHash && fs.existsSync(outPath)) {
      continue; // skip duplicate target
    }
    let pipeline;
    if (cfg.strategy === 'smartcrop') {
      try {
        const result = await smartcrop.crop(inputAbs, { width: t.width, height: t.height, ...(cfg.smartcrop||{}) });
        const c = result?.topCrop;
        if (c && c.width > 0 && c.height > 0) {
          // Optionally shift crop down to trim head/face area
          const trimRatio = (cfg.headless && cfg.headless.enabled) ? (cfg.headless.trimTopRatio || 0) : 0;
          const shiftY = Math.round((trimRatio) * c.height);
          const crop = {
            left: Math.max(0, Math.round(c.x)),
            top: Math.max(0, Math.round(c.y + shiftY)),
            width: Math.max(1, Math.round(c.width)),
            height: Math.max(1, Math.round(c.height - shiftY))
          };
          pipeline = sharp(inputAbs)
            .extract(crop)
            .resize(t.width, t.height)
            .withMetadata();
        }
      } catch (e) {
        // fall through to attention
      }
    }
    if (!pipeline) {
      pipeline = sharp(inputAbs)
        .resize(t.width, t.height, { fit: t.fit || 'cover', position: strategy })
        .withMetadata();
    }

    if (ext === 'webp') {
      await pipeline.toFormat('webp', { quality: cfg.webpQuality ?? 90 }).toFile(outPath);
    } else if (ext === 'jpg' || ext === 'jpeg') {
      await pipeline.toFormat('jpeg', { quality: cfg.jpgQuality ?? 95, mozjpeg: true }).toFile(outPath);
    } else if (ext === 'png') {
      await pipeline.png({ compressionLevel: cfg.pngCompressionLevel ?? 9 }).toFile(outPath);
    } else {
      await pipeline.toFile(outPath); // default
    }
  }
}

async function archiveInput(inputPath, cfg) {
  const inputAbs = path.resolve(root, inputPath);
  const dest = path.resolve(root, cfg.archiveDir, path.basename(inputAbs));
  await fse.move(inputAbs, dest, { overwrite: true });
}

async function cleanArchive(cfg) {
  if (!cfg.cleanArchiveDays) return;
  const cutoff = Date.now() - cfg.cleanArchiveDays * 24 * 60 * 60 * 1000;
  const dir = path.resolve(root, cfg.archiveDir);
  if (!fs.existsSync(dir)) return;
  const files = await fse.readdir(dir);
  await Promise.all(files.map(async f => {
    const fp = path.join(dir, f);
    const stat = await fse.stat(fp);
    if (stat.mtimeMs < cutoff) await fse.remove(fp);
  }));
}

function isAcceptable(file, cfg) {
  const ext = path.extname(file).toLowerCase();
  return cfg.acceptableExtensions.includes(ext);
}

async function processExisting(cfg) {
  const inDir = path.resolve(root, cfg.inputDir);
  const files = (await fse.readdir(inDir))
    .filter(f => isAcceptable(f, cfg))
    .map(f => path.join(inDir, f));

  for (const f of files) {
    await processOne(f, cfg);
    await archiveInput(f, cfg);
  }
}

async function watchMode(cfg) {
  const inDir = path.resolve(root, cfg.inputDir);
  const watcher = chokidar.watch(inDir, { ignoreInitial: true });
  console.log(`Watching ${inDir} for new files... Drag images in to process.`);
  watcher.on('add', async file => {
    if (!isAcceptable(file, cfg)) return;
    try {
      await processOne(file, cfg);
      await archiveInput(file, cfg);
      console.log(`Processed: ${path.basename(file)}`);
    } catch (e) {
      console.error('Error processing', file, e);
    }
  });
}

async function main() {
  const { flags } = parseArgs(process.argv);
  const cfg = loadConfig();
  await ensureDirs(cfg);
  await cleanArchive(cfg);

  if (flags.has('clean')) {
    await fse.emptyDir(path.resolve(root, cfg.outputDir));
    console.log('Output directory cleaned');
    return;
  }

  if (flags.has('watch')) {
    await processExisting(cfg);
    await watchMode(cfg);
    return;
  }

  await processExisting(cfg);
  console.log('Done.');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});


