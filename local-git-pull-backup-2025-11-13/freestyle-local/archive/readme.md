
# Sies  

Sies is a mobile app that helps users find the perfect clothing size across brands by learning from the garments they already own. Instead of relying on generic size charts, Sies builds a **personalized fit profile** using brand-specific size guides, garment measurements, and user feedback.  

---

## 🚀 Features
- **TagMatch**: Scan or upload a photo of a clothing tag, and Sies finds the exact product online along with its measurements.  
- **Closet-Based Fit Profile**: Add a few favorite garments to your digital closet. Sies uses their measurements to predict your size across brands.  
- **Fit Zones**: Personalized “Tight / Perfect / Relaxed” fit preferences that adapt dynamically based on user feedback.  
- **Interactive Prototype**: Explore how Sies compares garment fits visually with recommendations powered by brand size guides.  
- **Landing Page Preview**: A marketing site designed to showcase how Sies works and validate user interest.  

---

## 📱 Vision
Sies aims to remove the uncertainty from online clothing shopping. By creating a **universal fit layer** across brands, it saves users from returns, improves confidence in purchases, and creates a new way for retailers to engage with customers.  

---

## 🛠 Tech Stack
- **Frontend:** SwiftUI (iOS)  
- **Backend:** Supabase / PostgreSQL for size guide data and user fit profiles  
- **AI & Automation:** Python + OCR for tag recognition and size guide parsing  
- **Design:** Figma for app mockups and interactive prototypes  
- **Landing Page:** HTML/CSS with ongoing Figma design migration  

---

## 📂 Repo Structure
- `/landing` → Landing page mockups and HTML source  
- `/app` → iOS SwiftUI app code (WIP)  
- `/db` → SQL schemas for size guide ingestion and fit zone logic  
- `/design` → Figma exports, design system, and prototypes  

---

## 📖 How to Use
1. Clone the repo:  
   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git


# Sies — Waitlist Landing (Static)

**Copyright © 2025 Sean Davey. All rights reserved.**

This is a single-file static site (`index.html`). You can deploy it *as-is* anywhere that serves static files.

## Project Ownership

This project is owned and developed by **Sean Davey**. All code, design, and intellectual property contained within this repository are proprietary and protected by copyright law.

## Easiest ways to deploy

### Option 1 — Netlify Drop (no account required)
1. Go to https://app.netlify.com/drop
2. Drag the folder or ZIP from this bundle. Netlify will host it instantly.
3. Click **Site settings → Domain** to set a custom domain (or connect your domain).

### Option 2 — Vercel (CLI)
```bash
npm i -g vercel
vercel deploy --prod
```
(Answer the prompts; it will choose `index.html` as the entry.)

### Option 3 — GitHub Pages
1. Create a new repo and upload `index.html`.
2. In repo settings → Pages → Deploy from Branch (main), root `/`.

### Hook up the waitlist form
- Replace `FORM_ENDPOINT` in `index.html` with a Formspree/Fillout/ConvertKit endpoint.
- For Google Sheets:
  - Create an Apps Script Web App that writes incoming POSTs to a sheet.
  - Paste the Web App URL into `FORM_ENDPOINT`.

### Swap in your app screenshot
Replace the `<img>` in the `.mock-inner` with your latest mockup image.

