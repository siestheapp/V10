**Sies** **Brand** **Style** **Guide** **—** **v1**

*Audience:* Women 24–40 shopping premium fashion (wedding‑guest dresses,
eventwear).

*Brand* *essence:***Chic** **clarity** — luxury taste, zero confusion.

*One‑liner:Know* *your* *size* *before* *you* *buy.*

**1)** **Brand** **pillars**

> • **Assured** — confident, not shouty.
>
> • **Editorial** — fashion‑forward, magazine polish.
>
> • **Helpful** — practical, transparent, never gatekeepy.

**Voice** **&** **tone** - Warm, succinct, and precise (Net‑a‑Porter
energy). - Prefer *verbs* *over* *adjectives*, *nouns* *over*
*jargon*. - Use **en** **dash** **with** **a** **space** for ranges
(e.g., *32.0–* *33.0"*).

**2)** **Core** **identity**

**Name** **styling**: lowercase **sies** in text; wordmark may be set in
Title Case for logo lockup if needed.

**Logo/wordmark** - Typeface: *Playfair* *Display* (Semibold). -
Tracking: **0.02em**; optical kerning on. - Primary lockup: wordmark
only. No symbol for v1. - Clearspace: height of the **s** around all
sides. - Misuse: no outlines, no drop shadows, no gradients inside
letters.

**3)** **Typography**

**Display** **(H1/H2):** Playfair Display - H1 desktop 56 / 1.02; mobile
40 / 1.05 - H2 desktop 36 / 1.08; mobile 28 / 1.10

**UI** **&** **body:** Inter - Body 16 / 1.6; Small 14 / 1.5 - Buttons
16 / 1.1 / 600 - Overline / meta 12 / 700 / 0.12em

**Numerals:** Lining numerals (default). Prefer **.0** precision for
inch values when shown with pins or bars.

**4)** **Color**

**Core** **palette** - **Ink** \#1F1F1F — primary text - **Off‑white**
\#FAF8F6 — page background - **Lavender** \#8F6AAE — brand accent -
**Soft** **gold** \#C9B27D — secondary accent - **Muted** **gray**
\#6F6F74 —

secondary text - **Card** \#FFFFFF — surfaces

> 1

**Functional** **tints** - Success \#10B981 - Track gray \#ECECEC

**Fit** **Zones** **(bars)** - Tight \#EED9A3 - Good \#BFE5CE - Relaxed
\#CFE0F6

**5)** **Spacing,** **radius,** **elevation**

> • **Spacing** **scale:** 4, 8, 12, 16, 20, 24, 32, 44
>
> • **Radius:** 12 (cards), 18 (large cards), **9999** (pills/buttons)
>
> • **Shadows:** 0 10px 30px rgba(0,0,0,.06) for cards; 0 20px 40px
> rgba(0,0,0,.22) for device frames

**6)** **Design** **tokens** **(CSS)**

> :root{
>
> --bg:#FAF8F6;--ink:#1F1F1F;--muted:#6F6F74;--accent:#8F6AAE;--accent-2:#C9B27D;--card:#FFFFFF;
>
> --success:#10B981;--track:#ECECEC;--shadow:0 10px 30px
> rgba(0,0,0,.06);--radius:18px;
>
> --fit-tight:#EED9A3;--fit-good:#BFE5CE;--fit-relax:#CFE0F6;
>
> --font-display:"Playfair
> Display",serif;--font-ui:Inter,system-ui,-apple-system,Segoe
> UI,Roboto,Helvetica,Arial;
>
> }

**Tailwind** **theme** **snippet** **(optional)**

> // tailwind.config.js export default {
>
> theme:{ extend:{
>
> colors:{ bg:'#FAF8F6', ink:'#1F1F1F', muted:'#6F6F74',
> accent:'#8F6AAE', gold:'#C9B27D', card:'#FFFFFF', track:'#ECECEC',
> success:'#10B981',
>
> fit:{ tight:'#EED9A3', good:'#BFE5CE', relax:'#CFE0F6' } },
> borderRadius:{ xl:'18px', pill:'9999px' },
>
> boxShadow:{ card:'0 10px 30px rgba(0,0,0,.06)', device:'0 20px 40px
> rgba(0,0,0,.22)' },
>
> fontFamily:{ display:\['Playfair Display','serif'\],
> ui:\['Inter','system-ui'\] }
>
> }} }
>
> 2

**7)** **Components**

**Buttons** - Primary: ink background, white label, pill radius; hover
↑2% lightness. - Secondary: white background, 1px \#E8E4DE border, ink
text. - Focus: 3px lavender outline at 25% opacity.

**Pills** **&** **badges** - Match pill: white at 20% opacity over
gradient, bold 12px.

**Cards** - White background, 1px \#EEE6 border, radius 18px, shadow
card.

**Forms** - Email input: 14–16px, pill, 14px vertical padding, 1px
\#E8E4DE border; placeholder muted gray.

**FitZonesbar**-Singletrack(12px)withthreecontiguousfills(tight/good/relax).-Pins:8pxlavenderdot,1px
hairline tick, label pill (white, 1px \#EEE). - Labels stagger to avoid
collision.

**Device** **frames** - Prefer **photoreal** **iPhone** **15** **Pro**
renders (transparent PNG) or CSS devices. - Angle: −3° to −6°; add
shadow drop-shadow(0 20px 40px rgba(0,0,0,.22)) .

**8)** **Imagery** **&** **motion**

> • Product photography: bright, soft shadows, neutral backdrops. •
> Illustration: avoid silhouettes for v1; favor real garment shots. •
> Motion (web): 200–250ms ease‑out; hover scale ≤1.02.
>
> • Video loops: 4–6s, 30 fps, under 8–10 MB.

**9)** **Copy** **patterns**

**Hero**: *Know* *your* *size* *before* *you* *buy.*

**Sub**: *Sies* *predicts* *your* *perfect* *fit* *across* *brands*
*using* *the* *pieces* *you* *already* *love.* **CTA**: *Join* *the*
*waitlist* / *Get* *early* *access*

**Trust** **microcopy**: *Private* *by* *design* *—* *no* *body*
*photos* *required.*

**Fit** **Passport** **labels** - *Tailored* *Fit* — for fitted pieces -
*Everyday* *Fit* — for work & casual

\- *Relaxed* *Fit* — for flowy & layering

**10)** **Accessibility**

> • Min body size 16px; small 14px only for meta.
>
> • Contrast: text on off‑white ≥ 7:1 for body, ≥ 4.5:1 for secondary. •
> Focus visible on all interactive elements.
>
> • Never communicate fit state by color alone; always include a label.
>
> 3

**11)** **Page** **modules** **(landing)**

> 1\. **Hero**: headline, sub, primary CTA, 1–2 device renders.
>
> 2\. **Proof** **trio**: Personal to you / Cross‑brand match /
> Privacy‑first.
>
> 3\. **How** **it** **works** **(3** **steps)**: Add a few pieces →
> Build Fit Passport → Shop with confidence. 4. **Waitlist**: email
> field + CTA; legal microcopy.
>
> 5\. **Footer**: wordmark, copyright, privacy.

**12)** **Do** **/** **Don’t**

**Do** - Keep copy short; one idea per line. - Use consistent ranges
with en dash (e.g., *32.0–* *33.0"*). - Limit accent gold to micro
details (icons, dividers).

**Don’t** - Mix more than two typefaces. - Overuse gradients; avoid
rainbow UI. - Add drop shadows to the wordmark.

**13)** **Starter** **assets** **you** **likely** **need** **next**

> • Wordmark SVG (dark + light). • Favicon + app icon.
>
> • Two photoreal iPhone 15 Pro PNGs (angled + straight). • Social share
> image (1200×630) with hero + device.

**Ready‑to‑ship** **micro‑kit** **(copy/paste)** **Primary** **CTA**
**button**

> \<a class="btn" href="#waitlist"\>Get early access →\</a\>
>
> .btn{display:inline-flex;align-items:center;gap:10px;padding:14px
> 22px;border-radius:9999px;background:var(--ink);color:#fff;text-decoration:none;font-weight:
> 600;box-shadow:var(--shadow)}
>
> .btn:focus{outline:3px solid color-mix(in oklab,var(--accent)
> 25%,transparent);outline-offset:3px}

**Email** **input**

> 4
>
> \<form class="wl" action="#"\>
>
> \<input type="email" placeholder="you@example.com" required\> \<button
> class="btn"\>Join the waitlist\</button\>
>
> \</form\>
>
> .wl{display:flex;gap:10px;flex-wrap:wrap}
>
> .wl input{flex:1;min-width:220px;padding:14px
> 16px;border-radius:9999px;border: 1px solid
> \#E8E4DE;background:#fff;color:var(--ink)}
>
> .wl input::placeholder{color:var(--muted)}

— End v1 —

> 5
