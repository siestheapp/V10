export function pickBestFromSrcset(srcset: string): string | undefined {
  const parts = srcset.split(',').map(p => p.trim());
  const parsed = parts
    .map(p => {
      const [url, size] = p.split(' ');
      const val = parseInt(size) || 0;
      return { url, val };
    })
    .sort((a, b) => b.val - a.val);
  return parsed[0]?.url;
}

export async function collectGalleryUrls(page: any): Promise<string[]> {
  return await page.evaluate(() => {
    const urls = new Set<string>();
    document.querySelectorAll('img').forEach(img => {
      const src = img.getAttribute('src') || img.getAttribute('data-src');
      if (src && src.includes('http')) urls.add(src);
      const srcset = img.getAttribute('srcset');
      if (srcset)
        srcset.split(',').forEach(s => {
          const url = s.trim().split(' ')[0];
          if (url && url.startsWith('http')) urls.add(url);
        });
    });
    document.querySelectorAll('picture source').forEach(source => {
      const srcset = source.getAttribute('srcset');
      if (srcset)
        srcset.split(',').forEach(s => {
          const url = s.trim().split(' ')[0];
          if (url && url.startsWith('http')) urls.add(url);
        });
    });
    document.querySelectorAll('[style*="background-image"]').forEach(el => {
      const bg = getComputedStyle(el as Element).backgroundImage;
      const m = /url\(["']?(.*?)["']?\)/.exec(bg);
      if (m && m[1] && m[1].startsWith('http')) urls.add(m[1]);
    });
    return Array.from(urls);
  });
}


