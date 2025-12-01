# Freestyle Design System — Unified

Single source of truth for Freestyle’s Ink + Iridescent Petrol brand. This consolidates:
- Tokens from `freestyle-tokens.css` / `freestyle-tokens.json`
- Guidance from `design-system/chatgotconversation.md`
- Visual references from `design-system/remixed-86a2b3c6.html`

## 1) Tokens (authoritative)
Use `freestyle-tokens.css` as the import; JSON is the machine-readable mirror.

```css
/* import once */
<link rel="stylesheet" href="/design-system/freestyle-tokens.css">
```

Colors
- ink-900: #0B0F14
- ink-700: #121A22
- ink-500: #2A3642
- ink-300: #6A7683
- canvas-0: #F7F9FB
- canvas-50: #EFF3F6
- canvas-100: #E9EEF1
- petrol-600: #009090
- petrol-500: #00A3A3
- petrol-400: #16B5B5
- petrol-100: #E0F7F7
- mint-400: #A6FFCB
- ice-300: #7FE1FF
- coral-500: #FF6B5A
- brand-sheen: linear-gradient(135deg,#00A3A3 0%,#7FE1FF 50%,#A6FFCB 100%)

Radii
- card: 16px; btn: 12px; pill: 999px

Spacing
- 4, 8, 12, 16, 24, 32

Shadows
- elev-0: 0 1px 2px rgba(0,0,0,.06)
- elev-1: 0 8px 24px rgba(11,15,20,.08)
- elev-2: 0 20px 60px rgba(0,0,0,.18)

Typography
- Inter (400, 500, 600, 700, 800)
- Display 44/110/700/-0.02; H2 28/120/600/-0.01; H3 18/130/600; Body 16/150/400; Caption 12/140/400

## 2) Roles (landing default)
- Background: canvas-0
- Card surfaces: #fff, border rgba(11,15,20,.08)
- Primary CTA: petrol-500; hover petrol-400; active petrol-600; text #fff
- Section dividers: canvas-100
- Meta/captions: ink-300; Subheads: ink-500; Body: ink-900
- Links/focus: underline or focus ring using ice-300
- Brand sheen: hero accent only (headline mask or one accent), not full blocks

## 3) Components (starter CSS)
```css
.button-primary{background:var(--petrol-500);color:#fff;border:0;border-radius:var(--radius-btn);padding:var(--space-12) var(--space-16);font-weight:600}
.button-primary:hover{background:var(--petrol-400)}
.button-primary:active{background:var(--petrol-600);transform:translateY(1px)}

.pill{display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border-radius:var(--radius-pill);border:1px solid rgba(11,15,20,.12)}
.pill.good{background:var(--petrol-100);border-color:rgba(0,163,163,.35);color:var(--ink-900)}
.pill.tight{color:var(--coral-500);border-color:var(--coral-500)}
.pill.relaxed{color:var(--ice-300);border-color:var(--ice-300)}

.card{background:#fff;border:1px solid rgba(11,15,20,.08);border-radius:var(--radius-card);box-shadow:var(--elev-0)}
.header{background:rgba(247,249,251,.85);backdrop-filter:blur(.5em)}
.logo{font-weight:600;letter-spacing:-.01em;background:var(--brand-sheen);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
```

## 4) Do / Don’t
- Do: let product photos dominate; use petrol to guide (CTAs, key chips)
- Do: keep gradients to one accent per view
- Do: keep copy dark on light backgrounds
- Don’t: mix Sies lavender with petrol on the same page
- Don’t: fill large panels with petrol; reserve for accents

## 5) Accessibility
- Buttons ≥ 44px; focus-visible ring using ice-300
- Contrast: body on white uses ink-900; petrol over white passes at medium weights

## 6) Dark Mode (future)
- BG ink-900; cards ink-700; text white; keep petrol-500 for CTAs (hover petrol-400)

## 7) Migration Notes
- Landing page currently Sies-styled (freestyle-october). Import tokens and override CTA, logo, dividers first; then map SCSS variables to tokens.
- Treat `freestyle_design_system_v_3.md` as an alternate violet/teal exploration (do not mix with active tokens).

## 8) References
- Tokens: `design-system/freestyle-tokens.css` and `.json`
- Guidance: `design-system/chatgotconversation.md`
- Gallery: `design-system/remixed-86a2b3c6.html`
