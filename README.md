# Freestyle

Landing page and mockups.

## Autocrop pipeline (Proxi hero images)

Drag-and-drop workflow to convert photos into hero-ready crops for the first card in `freestyle-october/assets/iframe/feed-unified.html` (2:3 portrait; 354×520 CSS px with 1x/2x/3x outputs).

- Input folder: `./_autocrop/in`
- Output folder: `./_autocrop/out`
- Archive: `./_autocrop/archive`

Config: `scripts/autocrop.config.json`

```json
{
  "targets": [
    { "name": "proxy-hero@1x", "width": 354, "height": 520 },
    { "name": "proxy-hero@2x", "width": 708, "height": 1040 },
    { "name": "proxy-hero@3x", "width": 1062, "height": 1560 }
  ],
  "strategy": "attention"
}
```

Usage:

```bash
npm i
npm run autocrop:watch   # keep running; drag files into _autocrop/in
# or process existing once:
npm run autocrop
```

Notes:
- Uses Sharp with `fit: cover` and attention-based crop to center people/outfits.
- Outputs `.webp` and `.jpg` by default; adjust in config (`formats`).
- Processed originals are moved to `archive`.
- Clean outputs: `npm run autocrop:clean`.

### Web UI (drag-and-drop in the browser)

Start the local server and open the web UI:

```bash
npm run autocrop:web
# then open http://localhost:5173
```

- Drag images into the page; originals are saved to `./_autocrop/originals` and cropped outputs to `./_autocrop/out`.
- Download links are shown for each generated size and format.

### Smart centering (SmartCrop)

The pipeline can center the person/dress automatically. The default strategy is `smartcrop` (via `smartcrop-sharp`). Adjust weights in `scripts/autocrop.config.json` under `smartcrop`:

```json
{
  "strategy": "smartcrop",
  "smartcrop": {
    "facePriority": true,
    "skinBias": 0.65,
    "yBias": 0.15,
    "ruleOfThirds": true
  }
}
```

Fallback: if SmartCrop fails to find a crop, it falls back to Sharp’s attention-based cover.
