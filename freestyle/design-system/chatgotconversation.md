Love that you pulled everything together. If this were my startup, I’d lock in Freestyle’s “Ink +
Iridescent Petrol” system today and ship with it. It hits the exact vibe you need: modern, gender-
neutral, social (alive on feed content) but still utility-serious for sizing. It also pairs beautifully with
Reformation’s photography (lots of natural light, neutral backdrops), so your CTAs pop without clashing.
Here’s the decisive call + a tight spec you can hand to a designer/dev right now.
Printed using ChatGPT to PDF, powered by PDFCrowd HTML to PDF API. 16/76
The call (use this)
Primary concept: Ink + Iridescent Petrol
Why: Distinct from Sies’ lavender/gold (editorial/luxury) and better for a social app. Petrol reads
fresh/techy without feeling cold; it flatters UGC and product photography; it’s accessible (great
contrast on light surfaces); and it scales to dark mode cleanly.
Brand personality: Confident, helpful, a little playful. Not glossy-luxury; more approachable “smart
friend.
”
Palette (ship these exact tokens)
Neutrals
ink-900 #0B0F14 (primary text/dark bg)
ink-700 #121A22 (dark surfaces, nav)
ink-500 #2A3642 (subheads)
ink-300 #6A7683 (meta/captions)
canvas-0 #F7F9FB (app bg)
canvas-50 #EFF3F6 (cards/sections)
canvas-100 #E9EEF1 (borders)
Brand & accents
petrol-500 #00A3A3 (primary CTA)
petrol-600 #009090 (pressed/active)
petrol-400 #16B5B5 (hover/highlight)
petrol-100 #E0F7F7 (pills/soft bg)
mint-400 #A6FFCB (success/sub-accent)
ice-300 #7FE1FF (selection/focus)
coral-500 #FF6B5A (alerts/“too tight”)
Brand sheen (hero only)
brand-sheen: linear-gradient(135deg,#00A3A3 0%,#7FE1FF 50%,#A6FFCB 100%)
These match your freestyle-tokens.css/json—keep them as the single source of truth.
Typography (fast + cohesive)
Family: Inter for everything (weights 400/500/600/700). It’s gorgeous at small sizes, renders crisply
on mobile, and keeps dev simple.
Printed using ChatGPT to PDF, powered by PDFCrowd HTML to PDF API. 17/76
Scale (mobile first):
H1: 40/44, 700, letter-spacing −0.02em
H2: 28/32, 600, −0.01em
H3: 18/24, 600
Body: 16/24, 400
Caption: 12/16, 400
Numerals: lining; avoid faux small caps.
Spacing, radius, elevation
Spacing: 4, 8, 12, 16, 24, 32 (don’t invent new steps)
Radius: card 16px, button 12px, pills 999px
Shadows:
elev-0: 0 1px 2px rgba(0,0,0,.06)
elev-1: 0 8px 24px rgba(11,15,20,.08) (cards)
elev-2: 0 20px 60px rgba(0,0,0,.18) (modals/hero)
Color roles & usage rules
CTA buttons: petrol-500 → hover petrol-400 → active petrol-600. Text always white.
Hero treatment: Use brand-sheen sparingly (one element: headline text mask or CTA underline or
device edge glow). Never fill large panels with it.
Badges/pills:
“Good fit”/consensus → petrol-100 pill with petrol border/text
“Too tight”
→ coral outline text
“Relaxed”
→ ice outline text
Dividers/borders: canvas-100
Links/focus: ice-300 underline on focus for visible a11y.
Accessibility: petrol on white > 4.5:1 at 500+ weights; all body text on white uses ink-900. Run WCAG
checks on any text over petrol-100 backgrounds.
Dark mode (optional, future-proof)
BG: ink-900
Cards: ink-700 with elev-0
Text: white at 90% for body, 100% for headings
Printed using ChatGPT to PDF, powered by PDFCrowd HTML to PDF API. 18/76
CTA: keep petrol-500; lighten hover to petrol-400
This palette flips cleanly; no additional brand colors needed.
Component starter kit (keep it tight)
Button / Primary
bg petrol-500; text #fff; radius 12; padding 12–16; shadow elev-1 on hero only
Chip / Pill
default: white bg, 1px rgba(11,15,20,.12) border
variants: .good (petrol-100), .tight (coral outline), .relaxed (ice outline)
Card
white bg, 1px rgba(11,15,20,.08) border, radius 16, elev-0; never stack more than 2 shadows
Nav
sticky; bg rgba(247,249,251,.85) with backdrop-filter blur; active link uses small petrol
underline
Device mock
black frame with subtle elev-2; don’t gradient-fill the phone—let the screen content carry the
color
Do / Don’t (guardrails)
Do let product photos dominate; use petrol to guide the eye (CTAs, key chips).
Do keep gradient use to one accent element per view (headline mask, CTA sheen, or device edge
—not all three).
Do keep copy dark on light backgrounds for conversion pages.
Don’t wash large sections in petrol; reserve blocks of color for interstitials or empty states.
Don’t mix Sies lavender with petrol on the same page; if you must reference Sies later, isolate it by
context.
Handoﬀ snippets
CSS tokens (drop-in)
You already have freestyle-tokens.css; import once at the top of the LP and in your component lib.
Example roles:
css
.button-primary{
background: var(--petrol-500);
color:#fff; border:0; border-radius: var(--radius-btn);
padding: var(--space-12) var(--space-16); font-weight:600;
}
Printed using ChatGPT to PDF, powered by PDFCrowd HTML to PDF API. 19/76
.button-primary:hover{ background: var(--petrol-400); }
.button-primary:active{ background: var(--petrol-600); transform: translateY(1px); }
.pill{ display:inline-flex; align-items:center; gap:6px;
padding:6px 10px; border-radius: var(--radius-pill);
border:1px solid rgba(11,15,20,.12);
}
.pill.good{ background: var(--petrol-100); border-color: rgba(0,163,163,.35); color: var(--ink-
900); }
.pill.tight{ color: var(--coral-500); border-color: var(--coral-500); }
.pill.relaxed{ color: var(--ice-300); border-color: var(--ice-300); }
.card{ background:#fff; border:1px solid rgba(11,15,20,.08);
border-radius: var(--radius-card); box-shadow: var(--elev-0); }
Figma styles (tell your designer)
Color styles: import the exact token hexes above; name as Ink/900, Petrol/500, etc.
Text styles: H1 40/44 700, H2 28/32 600, Body 16/24 400, Caption 12/16.
Eﬀects: Elev/0, Elev/1, Elev/2 with the same blur/spread values as tokens.
Why not Sies (lavender/gold) for Freestyle?
Sies’ palette is perfect for an editorial, luxury fit-advisor brand. Freestyle’s wedge is social + community
data. Petrol gives you a fresher, more inclusive signal (works for all genders, all categories), reads as
“tech-enabled help,
” and makes UGC feel contemporary rather than catalog. It also photographs better
against the mixed lighting in creator content.
Bottom line
Ship Freestyle with Ink + Iridescent Petrol.
Keep gradient as one special eﬀect (hero only).
Use petrol for CTAs, selections, and positive state; coral for errors/“too tight.
”
Stick to Inter and a tight spacing/radius system so dev can move fast and everything feels cohesive
on mobile.
If you want, I can convert these tokens into a Tailwind theme or drop them into your current landing
page as a ready CSS file and wire one section so your Upwork dev has a perfect reference.