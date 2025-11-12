import { Page } from 'playwright';
import { collectGalleryUrls } from '../core/images';

export const AritziaAdapter = {
  brandName: 'Aritzia',
  categoryName: 'dresses',

  crawlCategory: async (page: Page, categoryUrl: string): Promise<string[]> => {
    await page.goto(categoryUrl, { waitUntil: 'networkidle', timeout: 90000 });

    // Handle Cloudflare challenge - wait longer for it to complete
    console.log('Waiting for Cloudflare challenge...');
    await page.waitForTimeout(5000);

    // Check if we're past Cloudflare
    const title = await page.title();
    if (title.toLowerCase().includes('cloudflare') || title.toLowerCase().includes('just a moment')) {
      console.log('Still on Cloudflare, waiting longer...');
      await page.waitForTimeout(10000);
    }

    // Dismiss any cookie banners
    try {
      const cookieBtn = await page.$('button[data-testid="cookie-accept"], .cookie-accept, #onetrust-accept-btn-handler');
      if (cookieBtn) {
        await cookieBtn.click();
        await page.waitForTimeout(500);
      }
    } catch {}

    // Wait for product grid to load
    try {
      await page.waitForSelector('a[href*="/product/"]', { timeout: 15000 });
    } catch (e) {
      console.log('Warning: No products found initially, attempting scroll...');
    }

    // Infinite scroll to load all products
    let prevCount = 0;
    for (let i = 0; i < 50; i++) {
      const count = await page.$$eval('a[href*="/product/"]', els => els.length);
      console.log(`Scroll ${i + 1}: Found ${count} product links`);

      if (count > prevCount) {
        prevCount = count;
      } else if (i > 3) {
        // No new products after 3 attempts, we're done
        break;
      }

      await page.evaluate(() => window.scrollBy(0, window.innerHeight * 2));
      await page.waitForTimeout(1000);
    }

    // Collect all product URLs
    const hrefs: string[] = await page.$$eval('a[href*="/product/"]', as =>
      Array.from(as).map(a => (a as HTMLAnchorElement).href)
    );

    // Filter to valid Aritzia product URLs
    const filtered = hrefs
      .filter(h => h.startsWith('https://www.aritzia.com/'))
      .filter(h => /\/product\//.test(h))
      .filter(h => !/\/cart|\/checkout|\/account/.test(h));

    const uniqueUrls = Array.from(new Set(filtered));
    console.log(`Found ${uniqueUrls.length} unique product URLs`);

    return uniqueUrls;
  },

  extractPdp: async (page: Page, pdpUrl: string) => {
    // Navigate with longer timeout for Cloudflare
    await page.goto(pdpUrl, { waitUntil: 'networkidle', timeout: 90000 });

    // Wait longer for Cloudflare challenge to complete (it can take 5-10 seconds)
    console.log('  Waiting for Cloudflare...');
    await page.waitForTimeout(8000);

    // Check if we're stuck on Cloudflare
    const title = await page.title();
    if (title.toLowerCase().includes('cloudflare') || title.toLowerCase().includes('just a moment')) {
      console.log('  Still on Cloudflare page, waiting longer...');
      await page.waitForTimeout(10000);
    }

    // Try multiple selectors for product content
    const selectors = [
      'h1.product-title',
      '[class*="ProductTitle"]',
      '[class*="product-name"]',
      'h1[class*="title"]',
      'h1',
      '[data-auto="product-title"]'
    ];

    let productLoaded = false;
    for (const selector of selectors) {
      try {
        await page.waitForSelector(selector, { timeout: 5000 });
        productLoaded = true;
        console.log(`  Found product with selector: ${selector}`);
        break;
      } catch {}
    }

    if (!productLoaded) {
      console.error('  Could not find product content after waiting');
      // Take a screenshot for debugging
      const screenshotPath = `/tmp/aritzia-fail-${Date.now()}.png`;
      await page.screenshot({ path: screenshotPath });
      console.error(`  Screenshot saved to: ${screenshotPath}`);
    }

    const brand = 'Aritzia';

    // Try multiple selectors for product name
    let name = '';
    const nameSelectors = [
      'h1.product-title',
      '[class*="ProductTitle"]',
      '[class*="product-name"]',
      'h1[class*="title"]',
      '[data-auto="product-title"]',
      'h1'
    ];

    for (const sel of nameSelectors) {
      name = await page.$eval(sel, el => el.textContent?.trim() || '').catch(() => '');
      if (name && name !== 'www.aritzia.com' && name.length > 2) break;
    }

    // Try multiple selectors for price
    let priceText = '';
    const priceSelectors = [
      '[class*="price"]',
      '[data-auto="product-price"]',
      '[class*="ProductPrice"]',
      '[itemprop="price"]',
      '.price',
      'span[class*="Price"]'
    ];

    for (const sel of priceSelectors) {
      priceText = await page.$eval(sel, el => el.textContent?.trim() || '').catch(() => '');
      if (priceText && /\$?\d+/.test(priceText)) break;
    }

    const list_price = parseFloat((priceText.match(/[\d,.]+/)?.[0] || '0').replace(/,/g, ''));

    // Extract description
    const description = await page
      .$eval('[class*="description"], [class*="Description"], [itemprop="description"]', el => el.textContent?.trim() || '')
      .catch(() => '');

    // Extract color name
    const color = await page
      .$eval('[class*="color"], [class*="Color"], [data-auto="selected-color"]', el => el.textContent?.trim() || '')
      .catch(() => '');

    // Collect product images - look for img tags with product images
    const gallery = await collectGalleryUrls(page);

    // Also try to find images directly
    const directImages = await page.$$eval('img[src*="aritzia"], img[src*="product"]', imgs =>
      imgs.map(img => (img as HTMLImageElement).src).filter(src => src && src.includes('http'))
    ).catch(() => []);

    const images = Array.from(new Set([...gallery, ...directImages]));

    console.log(`Extracted: ${name} - ${color} - $${list_price} - ${images.length} images`);

    return {
      brand,
      category: 'dresses',
      name: name.slice(0, 200) || 'Unknown Product',
      description,
      list_price: isNaN(list_price) || list_price === 0 ? null : list_price,
      size_scale: 'US-WOMENS-ALPHA', // Aritzia uses XXS-XXL
      color,
      product_url: pdpUrl,
      images
    };
  }
};
