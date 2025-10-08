# Contributing

## Branch & PR workflow

1. Branch from the latest `main` for each task:
   - `git checkout main && git pull && git checkout -b feat/<task>`
2. Commit early/often; push to the same branch.
3. Open a Draft PR with screenshots + preview link; keep pushing updates.
4. When ready, mark “Ready for review”.
5. Merge via PR (Squash & merge). Delete the branch.

## PR requirements

- Screenshots: desktop and 375/390/414 widths
- Deploy preview link (Netlify/Vercel)
- Keep scope small enough to review in ≤10 minutes
- Mobile changes should not regress desktop unless stated

## Commit style

- Use concise, present‑tense messages, e.g.,
  - `Fix: hero mock centers on mobile`
  - `Feat: profile mock responsive polish`

## Local setup

This is a static site (`index.html`). No build step required. Open `index.html` in a browser or use any static server.


