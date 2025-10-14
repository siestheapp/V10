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

  async function listAll() {
    const originalsAbs = path.resolve(root, cfg.originalsDir);
    const outAbs = path.resolve(root, cfg.outputDir);
    if (!fs.existsSync(originalsAbs)) return [];
    const files = await fse.readdir(originalsAbs);
    const imageFiles = files.filter(f => cfg.acceptableExtensions.includes(path.extname(f).toLowerCase()));
    const results = [];
    for (const f of imageFiles) {
      const base = baseNameNoExt(f);
      const outputs = [];
      for (const t of cfg.targets) {
        const ext = (cfg.outputFormat || 'png').toLowerCase();
        const p = path.join(outAbs, `${base}-${t.name}.${ext}`);
        if (fs.existsSync(p)) {
          outputs.push({ target: t.name, width: t.width, height: t.height, url: `/out/${base}-${t.name}.${ext}` });
        }
      }
      results.push({
        original: `/originals/${f}`,
        outputs
      });
    }
    // Newest first
    results.sort((a, b) => (a.original < b.original ? 1 : -1));
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


