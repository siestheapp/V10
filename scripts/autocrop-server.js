#!/usr/bin/env node
import express from 'express';
import multer from 'multer';
import cors from 'cors';
import path from 'path';
import fs from 'fs';
import fse from 'fs-extra';
import sharp from 'sharp';
import smartcrop from 'smartcrop-sharp';
import crypto from 'crypto';
import { exec } from 'child_process';

const root = process.cwd();
const CONFIG_PATH = path.resolve(root, 'scripts/autocrop.config.json');

function loadConfig() {
  const raw = fs.readFileSync(CONFIG_PATH, 'utf8');
  return JSON.parse(raw);
}

function baseNameNoExt(file) {
  return path.basename(file, path.extname(file));
}

function mapStrategy(strategy) {
  if (strategy === 'attention') return sharp.strategy.attention;
  if (strategy === 'entropy') return sharp.strategy.entropy;
  return sharp.strategy.attention;
}

async function ensureDirs(cfg) {
  await fse.ensureDir(path.resolve(root, cfg.outputDir));
  await fse.ensureDir(path.resolve(root, cfg.archiveDir));
  await fse.ensureDir(path.resolve(root, cfg.originalsDir));
}

function sanitizeFilename(name) {
  return name.replace(/[^a-zA-Z0-9._-]/g, '_');
}

function timestampEST(){
  const d = new Date();
  const parts = new Intl.DateTimeFormat('en-US', {
    timeZone: 'America/New_York',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
  }).formatToParts(d).reduce((acc,p)=>{ acc[p.type] = p.value; return acc; }, {});
  return `${parts.year}${parts.month}${parts.day}_${parts.hour}${parts.minute}${parts.second}`;
}

async function processOne(inputAbs, cfg, outBaseName) {
  const strategy = mapStrategy(cfg.strategy);
  const outputs = [];
  for (const t of cfg.targets) {
    const ext = (cfg.outputFormat || 'png').toLowerCase();
    const outBase = path.resolve(root, cfg.outputDir, `${outBaseName}-${t.name}`);
    const outPath = `${outBase}.${ext}`;
    let pipeline;
    if (cfg.strategy === 'smartcrop') {
      try {
        const result = await smartcrop.crop(inputAbs, { width: t.width, height: t.height, ...(cfg.smartcrop||{}) });
        const c = result?.topCrop;
        if (c && c.width > 0 && c.height > 0) {
          const trimRatio = (cfg.headless && cfg.headless.enabled) ? (cfg.headless.trimTopRatio || 0) : 0;
          const shiftY = Math.round(trimRatio * c.height);
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
        // fallback to attention
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
      await pipeline.toFile(outPath);
    }

    outputs.push({
      target: t.name,
      width: t.width,
      height: t.height,
      url: `/out/${outBaseName}-${t.name}.${ext}`
    });
  }
  return outputs;
}

async function start() {
  const cfg = loadConfig();
  await ensureDirs(cfg);

  const app = express();
  app.use(cors());
  app.use(express.json());

  // Static
  app.use('/out', express.static(path.resolve(root, cfg.outputDir)));
  app.use('/originals', express.static(path.resolve(root, cfg.originalsDir)));
  app.use('/ui', express.static(path.resolve(root, 'scripts/webui')));

  // Upload handling
  const storage = multer.diskStorage({
    destination: function(_req, _file, cb) {
      cb(null, path.resolve(root, cfg.originalsDir));
    },
    filename: function(_req, file, cb) {
      const base = baseNameNoExt(file.originalname);
      const ext = path.extname(file.originalname).toLowerCase();
      const stamped = `${sanitizeFilename(base)}-${Date.now()}${ext}`;
      cb(null, stamped);
    }
  });
  const upload = multer({ storage });

  app.post('/upload', upload.array('files', 20), async (req, res) => {
    try {
      const files = req.files || [];
      const results = [];
      for (const f of files) {
        const inputAbs = f.path; // saved in originalsDir
        const base = baseNameNoExt(path.basename(inputAbs));
        const outputs = await processOne(inputAbs, cfg, base);
        results.push({
          original: `/originals/${path.basename(inputAbs)}`,
          outputs
        });
      }
      res.json({ ok: true, results });
    } catch (e) {
      console.error(e);
      res.status(500).json({ ok: false, error: 'PROCESSING_FAILED' });
    }
  });

  // Upload originals only (no processing)
  app.post('/upload-original', upload.array('files', 20), async (req, res) => {
    try{
      const files = req.files || [];
      const results = files.map(f => ({
        original: `/originals/${path.basename(f.path)}`,
        base: baseNameNoExt(path.basename(f.path))
      }));
      res.json({ ok:true, results });
    }catch(e){
      console.error(e);
      res.status(500).json({ ok:false, error:'UPLOAD_FAILED' });
    }
  });

  async function listAll() {
    const originalsAbs = path.resolve(root, cfg.originalsDir);
    const outAbs = path.resolve(root, cfg.outputDir);
    if (!fs.existsSync(originalsAbs)) return [];
    const files = await fse.readdir(originalsAbs);
    const imageFiles = files.filter(f => cfg.acceptableExtensions.includes(path.extname(f).toLowerCase()));
    const meta = await Promise.all(imageFiles.map(async f => {
      const fp = path.join(originalsAbs, f);
      const st = await fse.stat(fp);
      return { f, mtimeMs: st.mtimeMs };
    }));
    meta.sort((a,b) => b.mtimeMs - a.mtimeMs); // newest first
    const results = [];
    const allOutFiles = await fse.readdir(outAbs).catch(()=>[]);
    for (const { f } of meta) {
      const base = baseNameNoExt(f);
      const outputs = [];
      for (const t of cfg.targets) {
        const ext = (cfg.outputFormat || 'png').toLowerCase();
        const match = allOutFiles.find(fn => fn.startsWith(base) && fn.endsWith(`-${t.name}.${ext}`));
        if (match) outputs.push({ target: t.name, width: t.width, height: t.height, url: `/out/${match}` });
      }
      results.push({
        original: `/originals/${f}`,
        outputs
      });
    }
    return results;
  }

  app.get('/list', async (_req, res) => {
    try {
      const results = await listAll();
      res.json({ ok: true, results });
    } catch (e) {
      console.error(e);
      res.status(500).json({ ok: false, error: 'LIST_FAILED' });
    }
  });

  // Manual crop: { base, rect: { x,y,width,height } } in original pixel coords
  app.post('/crop', async (req, res) => {
    try{
      const { base, rect, meta } = req.body || {};
      if(!base || !rect) return res.status(400).json({ ok:false, error:'MISSING_PARAMS' });
      const originalsAbs = path.resolve(root, cfg.originalsDir);
      const extIn = (await fse.readdir(originalsAbs)).find(f => baseNameNoExt(f) === base);
      if(!extIn) return res.status(404).json({ ok:false, error:'ORIGINAL_NOT_FOUND' });
      const inputAbs = path.join(originalsAbs, extIn);

      const md = await sharp(inputAbs).metadata();
      const clamp = (v, min, max)=> Math.max(min, Math.min(max, v));
      const left   = clamp(Math.round(rect.x), 0, Math.max(0, (md.width||0)-1));
      const top    = clamp(Math.round(rect.y), 0, Math.max(0, (md.height||0)-1));
      const width  = clamp(Math.round(rect.width), 1, Math.max(1, (md.width||1)-left));
      const height = clamp(Math.round(rect.height), 1, Math.max(1, (md.height||1)-top));

      const cropped = await sharp(inputAbs).extract({ left, top, width, height }).toBuffer();

      const outAbs = path.resolve(root, cfg.outputDir);
      const extOut = (cfg.outputFormat || 'png').toLowerCase();
      const urls = [];
      const segs = [];
      if (meta) {
        const { user, brand, item, size } = meta;
        if (user) segs.push(sanitizeFilename(String(user)));
        if (brand) segs.push(sanitizeFilename(String(brand)));
        if (item) segs.push(sanitizeFilename(String(item)));
        if (size) segs.push(sanitizeFilename(String(size)));
      }
      const metaPart = segs.length ? `${segs.join('__')}` : '';
      const stamp = timestampEST();
      for (const t of (cfg.targets||[])) {
        const nameCore = metaPart || baseNameNoExt(inputAbs);
        const outPath = path.join(outAbs, `${nameCore}-${t.name}_${stamp}.${extOut}`);
        let p = sharp(cropped).resize(t.width, t.height);
        if (extOut === 'webp') p = p.toFormat('webp', { quality: cfg.webpQuality ?? 90 });
        else if (extOut === 'jpg' || extOut === 'jpeg') p = p.toFormat('jpeg', { quality: cfg.jpgQuality ?? 95, mozjpeg: true });
        else if (extOut === 'png') p = p.png({ compressionLevel: cfg.pngCompressionLevel ?? 9 });
        await p.toFile(outPath);
        const st = await fse.stat(outPath);
        urls.push(`/out/${path.basename(outPath)}?v=${st.mtimeMs}`);
      }
      res.json({ ok:true, urls, original:`/originals/${extIn}` });
    }catch(e){
      console.error(e);
      res.status(500).json({ ok:false, error:'CROP_FAILED' });
    }
  });

  // Delete by base name (without extension); removes original and all outputs
  app.delete('/delete/:base', async (req, res) => {
    try{
      const base = req.params.base;
      if(!base) return res.status(400).json({ ok:false, error:'MISSING_BASE' });
      const originalsAbs = path.resolve(root, cfg.originalsDir);
      const outAbs = path.resolve(root, cfg.outputDir);

      // Remove original(s) matching base.*
      const originals = (await fse.readdir(originalsAbs)).filter(f => baseNameNoExt(f) === base);
      await Promise.all(originals.map(f => fse.remove(path.join(originalsAbs, f))));

      // Remove outputs for each target
      const ext = (cfg.outputFormat || 'png').toLowerCase();
      await Promise.all((cfg.targets||[]).map(t => fse.remove(path.join(outAbs, `${base}-${t.name}.${ext}`))));

      res.json({ ok:true });
    }catch(e){
      console.error(e);
      res.status(500).json({ ok:false, error:'DELETE_FAILED' });
    }
  });

  app.get('/health', (_req, res) => {
    res.json({ ok: true });
  });

  app.get('/', (_req, res) => {
    res.redirect('/ui');
  });

  const port = Number(process.env.PORT || 5173);
  app.listen(port, () => {
    const url = `http://localhost:${port}`;
    console.log(`Autocrop web UI running at ${url}`);
    try{
      if (process.env.NO_AUTO_OPEN) return;
      if (process.platform === 'darwin') {
        exec(`open -a "Google Chrome" ${url}`, (err)=>{ if(err) exec(`open ${url}`); });
      } else if (process.platform === 'win32') {
        exec(`start ${url}`);
      } else {
        exec(`xdg-open ${url}`);
      }
    }catch(_e){ /* no-op */ }
  });
}

start().catch(err => {
  console.error(err);
  process.exit(1);
});


