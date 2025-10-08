# Freestyle Design System (v3)

This design system captures tokens, components, and exact visual recipes used in the current Freestyle landing mock. It’s structured so you can hand it to a designer/dev or port it into Figma/Code.

---

## 1) Foundations

### 1.1 Color Tokens
- **Background** `--bg`: `#0b0c10`
- **Surface** `--surface`: `#0f1218`
- **Card** `--card`: `#11131a`
- **Text** `--text`: `#eef2f7`
- **Muted** `--muted`: `#a6b0bf`
- **Brand / Electric Violet** `--brand`: `#7c4dff`
- **Accent / Teal** `--brand-2`: `#2dd4bf`
- **Focus Ring** `--ring`: `rgba(124, 77, 255, .55)`

**UI Accent Colors**
- **Mac dots**: close `#ff5f57`, minimize `#febc2e`, zoom `#28c840`
- **Phone shell**: `#0b0e14`
- **Badge text**: `#ffffff`
- **Meta text**: `#cfd7e6`

### 1.2 Gradients & Overlays
- **Page background**:  
  `radial-gradient(1200px 600px at 80% -10%, rgba(124,77,255,.12), transparent),  
   radial-gradient(800px 500px at 10% 110%, rgba(45,212,191,.10), transparent),  
   #0b0c10`
- **Logo badge**:  
  `linear-gradient(135deg, #7c4dff, #9a7bff 55%, #bca8ff)`
- **Eyebrow pill**:  
  `linear-gradient(90deg, rgba(124,77,255,.18), rgba(45,212,191,.18))`
- **Mock frame surface**:  
  `linear-gradient(180deg, #161925, #0f1218)`
- **Mock frame bar**:  
  `linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02))`
- **Mock glow overlay** (`.mock::after`):  
  `radial-gradient(800px 300px at 80% -10%, rgba(124,77,255,.08), transparent)`
- **Primary button**:  
  `linear-gradient(180deg, #7c4dff, #6a3dff)`
- **Media darkening overlay** (`.media::after`):  
  inner shadow: `inset 0 -60px 90px rgba(0,0,0,.45)`

### 1.3 Elevation (Shadows)
- **Shadow 1** `--shadow-1`:  
  `0 8px 20px rgba(0,0,0,.35), 0 6px 12px rgba(0,0,0,.22)`
- **Shadow 2** `--shadow-2`:  
  `0 20px 50px rgba(0,0,0,.5)`
- **Phone shell**: `0 16px 40px rgba(0,0,0,.55)`
- **Logo badge**: `0 8px 18px rgba(124,77,255,.35)`

### 1.4 Radii
- **Global radius** `--radius`: `18px`
- **Buttons**: `12px`
- **Logo badge**: `10px`
- **Card**: `16px`
- **Phone bezel**: `28px`
- **Pills/badges**: `999px`

### 1.5 Typography
- **Font family**: Inter (system fallbacks)  
- **Scale**:  
  - `--step--1`: `clamp(13px, 1.6vw, 14px)`  
  - `--step-0`: `clamp(15px, 1.9vw, 18px)`  
  - `--step-1`: `clamp(18px, 2.4vw, 22px)`  
  - `--step-2`: `clamp(24px, 3.4vw, 28px)`  
  - `--step-3`: `clamp(32px, 4.4vw, 40px)`  
  - `--step-4`: `clamp(40px, 5.6vw, 56px)`
- **Headline (H1)**: `--step-4`, 1.05 line-height, `-0.4px` letter-spacing
- **Subtitle/body**: `--step-0`, color `--muted`
- **Eyebrow**: `--step--1`, bold 700, letter-spacing `.2px`
- **Meta** (card footer): `12px`

### 1.6 Spacing & Layout
- **Container max**: `--container: 1200px`, gutter: `min(92%, container)`
- **Grid breakpoints**: 780px, 900px, 1280px
- **Hero gaps**: 28px mobile → 64px desktop
- **Feature grid gaps**: 24px
- **Phone feed gap**: 14px

---

## 2) Components

### 2.1 Buttons
**Base**
- Inline-flex, min-height 44px, padding `10px 16px`, weight 800, radius `12px`, border `1px solid rgba(255,255,255,.12)`
- Focus: `outline: 3px solid var(--ring); outline-offset: 2px`

**Primary**
- Fill: `linear-gradient(180deg, #7c4dff, #6a3dff)`
- Text: `#fff`
- Shadow: `0 12px 26px rgba(124,77,255,.35)`
- Hover: `filter: brightness(1.05)`

**Ghost**
- Fill: `rgba(255,255,255,.02)`
- Text: `--text`

### 2.2 Eyebrow Pill
- Background: `linear-gradient(90deg, rgba(124,77,255,.18), rgba(45,212,191,.18))`
- Border: `1px solid rgba(255,255,255,.14)`
- Radius: `999px`
- Type: `--step--1` bold 700

### 2.3 Navigation Link
- Color `--text`; padding `8px 10px`; radius `10px`
- Hover: background `rgba(255,255,255,.06)`
- Focus-visible: outline `3px solid var(--ring)`

### 2.4 Feature Card
- Background `--card`; border `1px solid rgba(255,255,255,.08)`
- Radius `--radius`; padding `22px`; shadow `--shadow-1`
- Title: `--step-1`; Body: `--step-0` muted

### 2.5 **Mock Window + Phone + Feed Card** (exact visual recipe)

**Mock Window** (`.mock`)
- Background: `linear-gradient(180deg, #161925, #0f1218)`
- Border: `1px solid rgba(255,255,255,.08)`
- Radius: `18px`
- Shadow: `--shadow-2` → `0 20px 50px rgba(0,0,0,.5)`
- Overlay (`.mock::after`): `radial-gradient(800px 300px at 80% -10%, rgba(124,77,255,.08), transparent)`

**Frame Bar** (`.frame-bar`)
- Height: auto; padding `10px 12px`
- Divider: `1px solid rgba(255,255,255,.06)`
- Background: `linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02))`
- Dots: `#ff5f57`, `#febc2e`, `#28c840` with `inset 0 -1px 0 rgba(0,0,0,.25)`

**Phone Shell** (`.phone`)
- Size: `min(92%, 380px)`; aspect: `9/19`
- Bezel radius: `28px`
- Surface: `#0b0e14`
- Border: `1px solid rgba(255,255,255,.08)`
- Shadow: `0 16px 40px rgba(0,0,0,.55)`
- Top bar: border-bottom `1px solid rgba(255,255,255,.06)`; text `#c8d1e0` (`12px`)

**Feed Card** (`.card`)
- Surface: `#121622`
- Border: `1px solid rgba(255,255,255,.10)`
- Radius: `16px`
- Shadow: `--shadow-1` (see above)

**Media** (`.media`)
- Aspect: `4/5`; overflow hidden
- Image: `object-fit: cover; filter: saturate(1.05) contrast(1.05)`
- Overlay (`.media::after`): `inset 0 -60px 90px rgba(0,0,0,.45)` (simulates a soft gradient fade)

**Badge** (`.badge`)
- Position: absolute top/left `10px`
- Background: `rgba(0,0,0,.55)`
- Text: `#fff`; font `12px/700`
- Padding: `6px 10px`
- Border: `1px solid rgba(255,255,255,.18)`
- Radius: `999px`
- Backdrop blur: `blur(4px)`

**Meta Row** (`.meta`)
- Layout: space-between
- Padding: `10px 12px`
- Color: `#cfd7e6`
- Font size: `12px`

**Size Pill** (`.pill`)
- Padding: `4px 10px`
- Border: `1px solid rgba(255,255,255,.18)`
- Radius: `999px`
- Weight: 700

### 2.6 Testimonials Card
- Background: `rgba(0,0,0,.25)`
- Border: `1px solid rgba(255,255,255,.12)`
- Radius: `18px`
- Shadow: `--shadow-1`
- Avatar ring: `1px solid rgba(255,255,255,.14)`

### 2.7 Form (Waitlist)
- Input: min-height `48px`; radius `12px`; border `1px solid rgba(255,255,255,.16)`; bg `rgba(255,255,255,.03)`; text `--text`; placeholder `#b9c3d5`
- Button: use **Primary** specs
- Accessibility: `:focus-visible` ring as tokens

---

## 3) Layout & Responsiveness
- **Container**: `min(92%, 1200px)`
- **Hero grid**: 1-col → 2-col at `900px`
- **Feature grid**: 1-col → 3-col at `780px`
- **Fine-tune at 1280px**: increase `.subtitle` max-width; bump `.mock-body` padding

---

## 4) Code Snippets

### 4.1 CSS Tokens
```css
:root {
  --bg: #0b0c10;
  --surface: #0f1218;
  --card: #11131a;
  --muted: #a6b0bf;
  --text: #eef2f7;
  --brand: #7c4dff;
  --brand-2: #2dd4bf;
  --ring: rgba(124, 77, 255, .55);
  --shadow-1: 0 8px 20px rgba(0,0,0,.35), 0 6px 12px rgba(0,0,0,.22);
  --shadow-2: 0 20px 50px rgba(0,0,0,.5);
  --radius: 18px;
  --container: 1200px;
  --step--1: clamp(13px, 1.6vw, 14px);
  --step-0: clamp(15px, 1.9vw, 18px);
  --step-1: clamp(18px, 2.4vw, 22px);
  --step-2: clamp(24px, 3.4vw, 28px);
  --step-3: clamp(32px, 4.4vw, 40px);
  --step-4: clamp(40px, 5.6vw, 56px);
}
```

### 4.2 Primary Button
```css
.btn.primary {
  background: linear-gradient(180deg, #7c4dff, #6a3dff);
  color: #fff;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 12px;
  box-shadow: 0 12px 26px rgba(124,77,255,.35);
}
.btn.primary:hover { filter: brightness(1.05); }
.btn:focus-visible { outline: 3px solid var(--ring); outline-offset: 2px; }
```

### 4.3 Mock Window, Phone & Feed Card (as-is)
```css
.mock {
  position: relative;
  border-radius: 18px;
  background: linear-gradient(180deg, #161925, #0f1218);
  border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 20px 50px rgba(0,0,0,.5);
  overflow: hidden;
  isolation: isolate;
}
.mock::after {
  content: "";
  position: absolute; inset: 0; pointer-events: none;
  background: radial-gradient(800px 300px at 80% -10%, rgba(124,77,255,.08), transparent);
}
.frame-bar {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  border-bottom: 1px solid rgba(255,255,255,.06);
  background: linear-gradient(180deg, rgba(255,255,255,.04), rgba(255,255,255,.02));
}
.dot { width: 10px; height: 10px; border-radius: 50%; background: #ff5f57; box-shadow: inset 0 -1px 0 rgba(0,0,0,.25); }
.dot:nth-child(2) { background: #febc2e; }
.dot:nth-child(3) { background: #28c840; }
.mock-body { aspect-ratio: 16/10; display: grid; place-items: center; padding: 18px; }

.phone {
  width: min(92%, 380px); aspect-ratio: 9/19; border-radius: 28px;
  background: #0b0e14; border: 1px solid rgba(255,255,255,.08);
  box-shadow: 0 16px 40px rgba(0,0,0,.55);
  display: grid; grid-template-rows: 40px 1fr; overflow: hidden;
}
.phone .top { display: flex; align-items: center; justify-content: center; border-bottom: 1px solid rgba(255,255,255,.06); color: #c8d1e0; font-size: 12px; letter-spacing: .2px; }
.phone .feed { padding: 14px; display: grid; gap: 14px; }

.card { background: #121622; border: 1px solid rgba(255,255,255,.10); border-radius: 16px; overflow: hidden; box-shadow: 0 8px 20px rgba(0,0,0,.35), 0 6px 12px rgba(0,0,0,.22); }
.media { position: relative; display: block; aspect-ratio: 4/5; overflow: hidden; }
.media img { width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(1.05) contrast(1.05); }
.media::after { content: ""; position: absolute; inset: 0; box-shadow: inset 0 -60px 90px rgba(0,0,0,.45); }
.badge { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,.55); color: #fff; padding: 6px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; border: 1px solid rgba(255,255,255,.18); backdrop-filter: blur(4px); }
.meta { display: flex; justify-content: space-between; align-items: center; padding: 10px 12px; color: #cfd7e6; font-size: 12px; }
.pill { padding: 4px 10px; border: 1px solid rgba(255,255,255,.18); border-radius: 999px; font-weight: 700; }
```

---

## 5) Accessibility
- **Focus-visible** on links and buttons uses `--ring` for high visibility
- **Tap targets**: buttons ≥ 44×44px
- **Contrast**: text on card/phone surfaces uses light text on dark bg; badges use blurred black for legibility over media

---

## 6) Implementation Notes
- Replace placeholder images with real try‑on frames using `object-fit: cover` to avoid layout shift
- For video previews: place `<video>` inside `.media` (autoplay muted + poster). Keep the `.media::after` inner shadow to preserve text legibility on the meta row.
- Host color/typography tokens in a single CSS file so app screens and the landing page stay in sync.

---

**Last updated**: v3

