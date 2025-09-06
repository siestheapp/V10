## Design Tokens (CSS Variables)

This document consolidates the CSS variable tokens defined in `:root` across the HTML files in this repository. Tokens are grouped by file, with a brief consolidated set at the top.

### Consolidated tokens (common across pages)

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

Notes:
- Some pages add additional tokens such as `--border`, `--stroke`, `--r`/`--r-lg`/`--r-xl`, and feature-specific tokens.
- The profile pages also define `--accent-light`, `--good`, `--personal`, and `--shimmer`.

---

### index.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

### closet-screen.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#fff; --border:#E8E4DE; --shadow:0 12px 30px rgba(0,0,0,.08);
  --g1:#667eea; --g2:#764ba2;
  --r:16px; --r-lg:22px; --r-xl:28px;
}
```

### closet-gallery.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#fff; --border:#E8E4DE; --shadow:0 12px 30px rgba(0,0,0,.08);
  --g1:#667eea; --g2:#764ba2;
  --r:16px; --r-lg:22px; --r-xl:28px;
}
```

### feed-gallery.html

```css
::root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
}
```

### profile-screen.html

```css
::root{
  --bg:#FAF8F6;
  --ink:#1A1A1A;
  --muted:#8A8A8F;
  --accent:#9B7AAD;
  --accent-light:#E8DFF1;
  --stroke:#F0EDE9;
  --card:#FFFFFF;
  --good:#22C55E;
  --personal:#D4A574;
  --shimmer: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.4) 50%, transparent 70%);
}
```

### profile-gallery.html

```css
::root{
  --bg:#FAF8F6;
  --ink:#1A1A1A;
  --muted:#8A8A8F;
  --accent:#9B7AAD;
  --accent-light:#E8DFF1;
  --stroke:#F0EDE9;
  --card:#FFFFFF;
  --good:#22C55E;
  --personal:#D4A574;
  --shimmer: linear-gradient(120deg, transparent 30%, rgba(255,255,255,0.4) 50%, transparent 70%);
}
```

### archive/index3.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

### archive/index3_clean.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

### archive/index3_simplified.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

### archive/friends-screen.html

```css
:root{
  /* Match feed-screen color system */
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
}
```

### archive/treemap-demo.html

```css
:root{
  /* Design system tokens you can swap */
  --color-bg:#FAF8F6;
  --color-ink:#2B2031;
  --color-accent:#8F6AAE; /* used to derive category tints */
}
```

### archive/feed-screen.html

```css
::root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
}
```

### archive/index-interactive.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```

### archive/indexwithvideo.html

```css
:root{
  --bg:#FAF8F6; --ink:#1F1F1F; --muted:#6F6F74; --accent:#8F6AAE;
  --card:#FFFFFF; --track:#ECECEC; --shadow:0 10px 30px rgba(0,0,0,.06);
  --g1:#667eea; --g2:#764ba2;
  --radius:16px; --radius-lg:22px; --radius-xl:28px; --radius-2xl:36px;
  --space: clamp(12px, 2vw, 20px);
  --maxw: 1120px;
}
```


