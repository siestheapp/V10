## Design Archive

This archive documents multiple design systems used in this repo. Each section captures tokens, rules, components, and behaviors so we can maintain and, when ready, migrate between systems.

### SECTION 1 — Sies (Marketing/Landing)

Scope: The system implemented in `index.html`. This section is the source of truth for the landing experience: hero, how-it-works, profile spotlight, demo mockups, FAQ, and CTAs.

#### Design Principles

- **Clarity first**: high-contrast ink on warm paper background; few colors; generous white space.
- **Feel modern, soft, trustworthy**: rounded radii, subtle depth, soft gradients.
- **Mobile-considerate**: safe-area insets, touch targets ≥ 44px, iOS zoom prevention, reduced-motion support.
- **Composable primitives**: tokens + small class utilities that repeat across sections.

Brand & Voice (from old.md v1):

- Brand pillars: Assured, Editorial, Helpful.
- Voice: warm, succinct, precise; prefer verbs over adjectives; avoid jargon.
- Typographic punctuation: use en dash with spaces for ranges (e.g., 32.0 – 33.0").

#### Tokens (CSS Variables)

Defined in `:root` of `index.html`. Treat these as the canonical tokens for this system.

```css
:root{
  /* Color */
  --bg:#FAF8F6;        /* app background (warm paper) */
  --ink:#1F1F1F;       /* primary text */
  --muted:#6F6F74;     /* secondary text */
  --accent:#8F6AAE;    /* subtle accent (not the primary gradient) */
  --card:#FFFFFF;      /* card surfaces */
  --track:#ECECEC;     /* tracks/dividers */
  --shadow:0 10px 30px rgba(0,0,0,.06); /* default elevation */

  /* Brand gradient (primary) */
  --g1:#667eea;        /* indigo */
  --g2:#764ba2;        /* purple */

  /* Radii */
  --radius:16px;
  --radius-lg:22px;
  --radius-xl:28px;
  --radius-2xl:36px;

  /* Spacing & layout */
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;

  /* Safe areas (iOS) */
  --safe-top: env(safe-area-inset-top);
  --safe-bottom: env(safe-area-inset-bottom);
}
```

Usage rules:

- **Text on white**: use `--ink` for body; `--muted` for helper copy.
- **Gradients**: brand actions and badges use the `--g1 → --g2` diagonal.
- **Shadows**: prefer the provided soft shadow; increase only for focus states or hero mock frames.
- **Radii**: prefer `--radius-lg` for interactive controls; `--radius-2xl` for large device frames.

Additional palette items from the Sies Original (Part 3) showcase that are visible in `index.html` or useful for parity:

- Wordmark gradient for `.logo` text: `linear-gradient(180deg, #F1DCE3, #8B7F83)`.
- Legacy purple accent family (rarely used on the landing page): `#7C4DFF` (base), `#693ACC` (hover), `#5B2FD6` (pressed).
- Status colors (not used on landing, available for messages): Success `#2ECC71`, Warning `#F39C12`, Error `#E74C3C`.

You can expose these as optional tokens during migration if needed.

Extended/legacy tokens (from old.md v1) you may want for parity:

- `--accent-2:#C9B27D` (soft gold, secondary accent).
- `--success:#10B981` (functional success).
- Fit zone colors: `--fit-tight:#EED9A3`, `--fit-good:#BFE5CE`, `--fit-relax:#CFE0F6`.

#### Typography

- **Font family**: Inter (`400, 500, 600, 700, 800`).
- **Base style**: `body { font-family: Inter, system-ui, ...; color: var(--ink) }`.
- **Headings**:
  - H1: `clamp(32px, 5vw, 54px)`, line-height ≈ 1.04, tight letter-spacing −2%.
  - Section H2: `clamp(26px, 3.4vw, 36px)`.
  - Step title: 22px, weight ≈ 650.
  - Eyebrow: 12px, uppercase, 700, letter-spacing 0.1em.
- **Body**: 16–17px; `.sub` up to 20px on large screens; microcopy 12–15px.
- **Do**: Keep headings to one or two lines; constrain width with `max-width` or `ch` units.

Legacy display typeface (v1 brand guidance): Playfair Display (Semibold) for wordmark/brand titles. Landing currently uses Inter for UI and headings.

#### Layout & Spacing

- **Container**: `.container { max-width: var(--maxw); margin: 0 auto; padding: 0 20px }`.
- **Sections**: `.section { padding: 64px 0 }` with responsive tightening at ≤430px.
- **Sticky header**: translucent surface, backdrop blur, 1px divider.
- **Anchor scrolling**: `html { scroll-behavior: smooth; scroll-padding-top: 64px }`.
- **Grids**:
  - `hero-wrap`: two columns (1.2fr / 1fr), stacks at ≤1200px.
  - `#how .how-grid`: 1.35fr / 1fr; stacks at ≤960px.
  - `.three-mockups`: 3 fixed columns (272px); stacks to 1 col at ≤960px.

Breakpoints used in code:

- ≤1200px: hero stacks.
- ≤960px: how-grid stacks; hero mock mobile overrides apply.
- ≤430px: iPhone tuning (no overflow, wider tap targets, prevent zoom).

#### Color & Elevation

- Background is warm (`--bg`), with white cards and soft separator lines `rgba(0,0,0,.06)`.
- Elevation is subtle; keep z-layers minimal. Stronger elevation appears only for overlays and mock frames.

#### Components

Each component lists structure (HTML), style notes, and behaviors when present.

1) Header / Nav

- Sticky header with logo gradient wordmark and inline links.
- Use `header`, `.nav`, `.logo`, and simple `<a>` links. Keep the surface translucent and blurred.

2) Hero

- Left: H1, benefits list, waitlist form, micro note.
- Right: device mock showing a video. On mobile, the mock becomes a rounded rectangle with contained video and no extra padding/shadow.
- Class references: `.hero`, `.hero-wrap`, `.benefits`, `.benefit`, `.mock`, `.mock-inner`.

3) Waitlist Form

- Structure: `.cta` wraps `.input` and `.btn`.
- Styles:
  - `.input`: white surface, 1px border `#E8E4DE`, `--radius-lg`, subtle purple shadow.
  - `.btn`: gradient from `--g1` to `--g2`, bold 18px, `--radius-lg`, same shadow.
- Netlify form attributes present; JavaScript progressively enhances to async submit with a success message fallback.

4) Section Heading Stack (shared)

- Eyebrow + H2 + optional `.lede` paragraph. Maintain tight vertical rhythm (8–14px gaps).

5) How It Works — Step List

- `.how-list` is a vertical stack with CSS counters.
- `.step::before` renders a numbered circular gradient badge.
- Titles `.step-title` and copy `.step-text` sit in column 2 of a two-column grid.

6) Mock Containers (iframes/videos)

- Base pattern: `.mock > .mock-inner` wraps the media.
- Variants:
  - Hero/video: frameless on mobile; rounded 40px corners.
  - How section: fixed 430×1000 iframe scaled to 0.7 with matching wrapper `aspect-ratio` and border-radius.
  - Demo gallery (`#demo .three-mockups`): frameless, precise scale; uses `.click-overlay` to capture clicks without impacting layout.
  - Visual guidance (from brand v1): prefer photoreal iPhone 15 Pro renders or clean CSS frames; slight angle −3° to −6° acceptable in marketing compositions; device shadow around `drop-shadow(0 20px 40px rgba(0,0,0,.22))` when using cutouts.

7) Profile Spotlight

- Centered phone mock with radial background vignette and thin section dividers.
- `.profile-grid` centers the header stack and phone.

8) Demo Mockups (Three-up)

- `.three-mockups` grid of three devices with labels `.mockup-label` above each phone.
- On small screens, stack vertically with consistent gaps and internal scaling to fit.

9) FAQ Accordion

- Native `<details>/<summary>` with custom chevron and gradient dot. Rounded 14px containers with 1px border `#E8E4DE`.

10) Footer

- Simple single-line copyright with muted color.

#### Interaction & Behavior

- **Smooth scroll** to anchors with `scroll-padding-top` to clear the sticky header.
- **Analytics**: click tracking for mockups via an overlay and `postMessage` inside iframes.
  - Events:
    - `mock_click` with `{ key }` for overlays and marked mocks (`data-track`).
    - `mock_button_click` forwarded from embedded iframes via `postMessage`.
- **Forms**: enhanced Netlify submission intercepts `submit`, encodes as `application/x-www-form-urlencoded`, replaces form DOM with inline success; fallback redirect to `/thanks` on error.
- **Reduced motion**: hides `.mock video` and swaps to a static `mock-cover.jpg` when `prefers-reduced-motion: reduce`.

#### Fit Zones (for product education and future states)

- Zones and colors (legacy): Tight `#EED9A3`, Good `#BFE5CE`, Relaxed `#CFE0F6`.
- Guidance: never communicate fit by color alone; pair with a text label (e.g., Tailored Fit / Everyday Fit / Relaxed Fit).

#### Elevation Catalog (from code + Part 3 parity)

- Base/elements: `var(--shadow)` → `0 10px 30px rgba(0,0,0,.06)`.
- Buttons/CTAs (hero form and badges): `0 10px 24px rgba(118,75,162,.25)`.
- Device frames (large mocks): `0 30px 80px rgba(0,0,0,.25)`.
- FAQ indicators: lighter `0 4px 12px rgba(118,75,162,.25)` on the dot.

#### Accessibility & Usability

- **Touch targets**: form controls and primary buttons ≥ 48px high on mobile; set `input, select, textarea { font-size: 16px }` to prevent iOS zoom.
- **Safe areas**: header/footer pad with `env(safe-area-inset-*)`.
- **Contrast**: dark ink on white; ensure gradients over text have enough contrast (avoid text directly over gradient backgrounds unless solid backdrop).
- **Keyboard**: native controls; maintain visible focus outlines (system default acceptable for now).

Expanded rules (from old.md v1):

- Minimum body text 16px; 14px only for metadata.
- Contrast: body text on off‑white ≥ 7:1; secondary ≥ 4.5:1.
- Provide focus-visible outlines on all interactive elements.
- Do not rely on color alone for fit or status; include labels or icons.

#### Do / Don’t

- **Do**
  - Use tokenized colors and radii; adjust only via tokens.
  - Keep gradients for primary actions and badges; use solid `--accent` sparingly.
  - Maintain tight header stacks and consistent section rhythm.
  - Use the mock container patterns for any new media.

- **Don’t**
  - Introduce new elevations or radii outside token set.
  - Place text directly on busy videos without a solid or gradient-opaque backdrop.
  - Override mobile mock rules that ensure containment and safe-area padding.

#### Gradients Catalog

- Wordmark text (header logo): `linear-gradient(180deg, #F1DCE3, #8B7F83)` applied via background-clip text.
- Primary CTA/background accents: `linear-gradient(135deg, var(--g1), var(--g2))` where `--g1:#667eea`, `--g2:#764ba2`.
- Profile spotlight section background: `radial-gradient(1200px 420px at 50% -120px, rgba(255,255,255,.9), rgba(255,255,255,0))`.

#### Wordmark Logo (as in `feed-gallery.html`)

- Text: lowercase `sies`.
- Style: gradient text fill using brand warm-metal gradient.
- CSS:

```css
.logo{
  font-weight:600;
  font-size:32px;
  letter-spacing:-.01em;
  background: linear-gradient(180deg,#F1DCE3 0%, #8B7F83 100%);
  -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent;
}
```

- Notes: keep gradient direction vertical (180deg). Use lowercase wordmark in UI headers; Playfair Display may be used for standalone brand assets per v1 brand guidance.

#### Copy Patterns (from old.md v1)

- Hero headline: “Know your size before you buy.”
- Subheadline: “Sies predicts your perfect fit across brands using the pieces you already love.”
- CTA labels: “Join the waitlist”, “Get early access”.
- Trust microcopy: “Private by design — no body photos required.”

#### Code References (non-exhaustive)

- Tokens and globals: see `index.html` `<style>` `:root`, `body`, `.container`, `.section`.
- Hero and form: `.hero`, `.cta`, `.input`, `.btn`.
- Steps: `.how-list`, `.step`, `.step::before`, `.step-title`, `.step-text`.
- Mock patterns: `.mock`, `.mock-inner` variants under `#how`, `#demo`, and hero mobile overrides.
- FAQ: `#faq details`, `#faq summary`, and associated pseudo-elements.

#### Landing Modules Checklist

- Hero: headline, sub, primary CTA, 1–2 device renders.
- Proof trio: Personal to you / Cross‑brand match / Privacy‑first.
- How it works (3 steps): Add a few pieces → Build Fit Profile → Shop with confidence.
- Waitlist: email field + CTA; legal microcopy.
- Footer: wordmark, copyright, privacy links.

#### Imagery & Motion Guidance

- Product photography: bright, soft shadows, neutral backdrops.
- Motion: 200–250ms ease‑out; hover scale ≤ 1.02.
- Video loops: 4–6s, 30fps, under 8–10 MB.

#### Scales (for parity with Sies Original showcase)

- Spacing reference: 4, 8, 12, 16, 24, 32 (landing also uses `--space: clamp(12px, 2vw, 20px)`).
- Radius reference (legacy small components): 8, 10, 12, 16, 20. Landing favors larger radii via tokens (`16, 22, 28, 36`).
- Typography reference: Display/H1/H2/H3/Body/Caption as in Part 3. Landing actually uses: H1 `clamp(32px, 5vw, 54px)`, H2 `clamp(26px, 3.4vw, 36px)`, Step title 22px, body 16–17px, eyebrow 12px uppercase.

#### Starter Assets (recommended next)

- Wordmark SVG (dark + light), favicon + app icon.
- Two photoreal iPhone 15 Pro PNGs (angled + straight) or CSS devices.
- Social share image (1200×630) with hero + device.

#### Migration Notes (toward next system)

- Extract tokens to `tokens.css` (global) to reduce duplication across pages.
- Move shared component styles (e.g., `.btn`, `.input`, `.mock`, `.section-head`, `.eyebrow`) to a `components.css` import.
- Keep analytics API consistent (`mock_click`, `mock_button_click`) so UI migration doesn’t break basic click funnels.

#### Open Questions

- Do we want a light/dark token pair for future theming?
- Should `.btn` have explicit focus-visible style for AA compliance beyond system default?

---

Placeholder for future sections:

- SECTION 2 — Social (Peer Size Matches) [separate system; not covered here]


