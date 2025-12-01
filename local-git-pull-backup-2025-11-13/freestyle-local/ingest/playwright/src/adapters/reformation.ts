import { Browser, Page } from 'playwright';
import { pickBestFromSrcset, collectGalleryUrls } from '../core/images';

function toAbsolute(url: string): string {
  if (url.startsWith('http')) return url;
  return new URL(url, 'https://www.thereformation.com').toString();
}

async function infiniteScroll(page: Page, maxScrolls = 30) {
  let lastHeight = await page.evaluate(() => document.body.scrollHeight);
  for (let i = 0; i < maxScrolls; i++) {
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(1000);
    const newHeight = await page.evaluate(() => document.body.scrollHeight);
    if (newHeight === lastHeight) break;
    lastHeight = newHeight;
  }
}

export async function collectCategoryPdpUrls(browser: Browser, categoryUrl: string, maxPages = 500): Promise<string[]> {
  const ctx = await browser.newContext();
  const page = await ctx.newPage();
  await page.goto(categoryUrl, { waitUntil: 'domcontentloaded' });
  await infiniteScroll(page, Math.min(maxPages, 100));

  const hrefs = await page.$$eval('a', nodes => nodes.map(n => (n as HTMLAnchorElement).href).filter(Boolean));
  const filtered = hrefs
    .filter(h => /\/products\//.test(h) || /\/products\//.test(new URL(h).pathname))
    .map(toAbsolute);
  await ctx.close();
  return Array.from(new Set(filtered));
}

async function extractJsonLd(page: Page): Promise<any | null> {
  const raw = await page.$$eval('script[type="application/ld+json"]', nodes => nodes.map(n => n.textContent || '').join('\n'));
  const blocks = raw
    .split(/\n(?=\{)/)
    .map(s => s.trim())
    .filter(Boolean);
  for (const blk of blocks) {
    try {
      const j = JSON.parse(blk);
      if (j['@type'] === 'Product') return j;
      if (Array.isArray(j)) {
        const p = j.find((x: any) => x['@type'] === 'Product');
        if (p) return p;
      }
    } catch {}
  }
  return null;
}

export type ParsedPdp = {
  brand: string;
  category: string;
  name: string;
  description?: string | null;
  price?: number | null;
  currency?: string | null;
  images: string[];
};

export async function parsePdp(page: Page, pdpUrl: string): Promise<ParsedPdp> {
  await page.goto(pdpUrl, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(500);

  const jsonLd = await extractJsonLd(page);
  let name: string | undefined;
  let description: string | undefined;
  let price: number | undefined;
  let currency: string | undefined;
  let images: string[] = [];

  if (jsonLd) {
    name = jsonLd.name;
    description = jsonLd.description;
    const offer = Array.isArray(jsonLd.offers) ? jsonLd.offers[0] : jsonLd.offers;
    if (offer) {
      const p = parseFloat(offer.price || offer.priceSpecification?.price);
      if (!isNaN(p)) price = p;
      currency = offer.priceCurrency || offer.priceSpecification?.priceCurrency || 'USD';
    }
    if (jsonLd.image) {
      images = Array.isArray(jsonLd.image) ? jsonLd.image : [jsonLd.image];
    }
  }

  if (!name) {
    name = await page.$eval('h1, [data-testid="pdp-name"], .ProductTitle', el => el.textContent?.trim() || '')
      .catch(() => '');
  }

  if (images.length === 0) {
    const gallery = await collectGalleryUrls(page);
    images = gallery.filter(u => /reformation|thereformation/.test(u));
  }

  return {
    brand: 'Reformation',
    category: 'Dresses',
    name: name || 'Unknown',
    description: description || null,
    price: price ?? null,
    currency: currency ?? null,
    images: images.map(toAbsolute)
  };
}

// New adapter object per plan: crawlCategory + extractPdp for one‑shot runner
export const ReformationAdapter = {
  brandName: 'Reformation',
  categoryName: 'dresses',

  crawlCategory: async (page: Page, categoryUrl: string): Promise<string[]> => {
    await page.goto(categoryUrl, { waitUntil: 'domcontentloaded' });
    // Dismiss cookie banners if present
    try {
      const btn = await page.$('#onetrust-accept-btn-handler');
      if (btn) { await btn.click(); await page.waitForTimeout(300); }
    } catch {}
    // Wait for any product anchors
    try { await page.waitForSelector('a[href*="/products/"]', { timeout: 10000 }); } catch {}
    // Robust infinite scroll: scroll until no new anchors
    let prevCount = 0;
    for (let i = 0; i < 60; i++) {
      const count = await page.$$eval('a[href*="/products/"]', els => els.length);
      if (count > prevCount) { prevCount = count; } else { break; }
      await page.evaluate(() => window.scrollBy(0, window.innerHeight * 2));
      await page.waitForTimeout(500);
    }
    const hrefs: string[] = await page.$$eval('a[href*="/products/"]', as =>
      Array.from(as).map(a => (a as HTMLAnchorElement).href)
    );
    // Filter out gift card and non-product links, force same-origin
    const filtered = hrefs
      .filter(h => h.startsWith('https://www.thereformation.com/'))
      .filter(h => /\/products\//.test(h))
      .filter(h => !/GIFT_CARD|onetrust|cookie/i.test(h));
    return Array.from(new Set(filtered));
  },

  extractPdp: async (page: Page, pdpUrl: string) => {
    await page.goto(pdpUrl, { waitUntil: 'networkidle' });
    await page.waitForTimeout(800);

    const brand = 'Reformation';
    const name = (await page.$eval('h1, .product-name, [data-testid="pdp-name"]', el => el.textContent?.trim() || '')).slice(0, 200);
    const priceText = await page
      .$eval('[data-testid="pdp-price"], .price, [itemprop=price]', el => el.textContent?.trim() || '')
      .catch(() => '');
    const list_price = parseFloat((priceText.match(/[\d,.]+/)?.[0] || '0').replace(/,/g, ''));

    const description = await page
      .$eval('.product-description, [data-testid="pdp-description"], [itemprop="description"]', el => el.textContent?.trim() || '')
      .catch(() => '');

    const gallery = await collectGalleryUrls(page);
    const images = Array.from(new Set(gallery));

    const size_scale = 'US-WOMENS-ALPHA';
    const color = await page.$eval('[data-testid="color-name"], .color-name', el => el.textContent?.trim() || '').catch(() => '');

    return {
      brand,
      category: 'dresses',
      name,
      description,
      list_price: isNaN(list_price) ? null : list_price,
      size_scale,
      color,
      product_url: pdpUrl,
      images
    };
  }
};


