import 'dotenv/config';
import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

async function scrapeAritzia() {
  const browser = await chromium.launch({
    headless: false,
    slowMo: 100
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });

  const page = await context.newPage();

  console.log('Opening Aritzia dresses page...');
  console.log('If Cloudflare appears, you have 30 seconds to solve it.\n');

  await page.goto('https://www.aritzia.com/us/en/clothing/dresses', { timeout: 90000 });

  console.log('Waiting 30 seconds for Cloudflare / page load...\n');
  await page.waitForTimeout(30000);

  console.log('Attempting to find products...\n');

  // Now try to find products
  const productLinks = await page.$$eval('a[href*="/product/"]', as =>
    Array.from(as).map(a => (a as HTMLAnchorElement).href)
  ).catch(() => []);

  const uniqueUrls = Array.from(new Set(productLinks))
    .filter(h => h.startsWith('https://www.aritzia.com/'))
    .filter(h => /\/product\//.test(h));

  console.log(`Found ${uniqueUrls.length} product URLs\n`);

  if (uniqueUrls.length === 0) {
    console.error('No products found. Cloudflare may still be blocking or page did not load.');
    console.log('Taking screenshot for debugging...');
    await page.screenshot({ path: '/tmp/aritzia-category-fail.png' });
    console.log('Screenshot saved to /tmp/aritzia-category-fail.png');
    await browser.close();
    return;
  }

  // Save URLs
  const outputDir = path.join(__dirname, '../output');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  fs.writeFileSync(
    path.join(outputDir, 'product-urls.json'),
    JSON.stringify(uniqueUrls, null, 2)
  );
  console.log(`✓ Saved ${uniqueUrls.length} URLs\n`);

  // Extract first 5 products
  const limit = Math.min(5, uniqueUrls.length);
  console.log(`Extracting details for ${limit} products...\n`);

  const products = [];
  for (let i = 0; i < limit; i++) {
    const url = uniqueUrls[i];
    console.log(`[${i + 1}/${limit}] ${url}`);

    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });

      // Wait for potential Cloudflare + page load
      console.log('  Waiting 10s for page load...');
      await page.waitForTimeout(10000);

      // Try to find product name
      let name = '';
      const nameSelectors = [
        'h1.product-title',
        '[class*="ProductTitle"]',
        'h1[class*="Title"]',
        'h1'
      ];

      for (const sel of nameSelectors) {
        name = await page.$eval(sel, el => el.textContent?.trim() || '').catch(() => '');
        if (name && name !== 'www.aritzia.com' && name.length > 2) {
          console.log(`  Found name with: ${sel}`);
          break;
        }
      }

      // Try to find price
      let priceText = '';
      const priceSelectors = [
        '[class*="ProductPrice"]',
        '[class*="price"]',
        'span[class*="Price"]',
        '[data-auto="product-price"]'
      ];

      for (const sel of priceSelectors) {
        priceText = await page.$eval(sel, el => el.textContent?.trim() || '').catch(() => '');
        if (priceText && /\$?\d+/.test(priceText)) {
          console.log(`  Found price with: ${sel}`);
          break;
        }
      }

      const price = parseFloat((priceText.match(/[\d,.]+/)?.[0] || '0').replace(/,/g, ''));

      // Get images
      const images = await page.$$eval('img[src*="aritzia"], img[src*="product"]', imgs =>
        imgs.map(img => (img as HTMLImageElement).src).filter(src => src && src.includes('http'))
      ).catch(() => []);

      const product = {
        brand: 'Aritzia',
        name: name || 'Unknown',
        price: price || null,
        url,
        images: Array.from(new Set(images)).slice(0, 5)
      };

      products.push(product);
      console.log(`  ✓ ${product.name} - $${product.price}`);
      console.log(`  ✓ ${product.images.length} images\n`);

      // Wait between products
      if (i < limit - 1) {
        const delay = 3000 + Math.random() * 3000;
        console.log(`  Waiting ${Math.round(delay / 1000)}s...\n`);
        await page.waitForTimeout(delay);
      }
    } catch (error) {
      console.error(`  ✗ Error: ${error}\n`);
    }
  }

  // Save products
  const productsFile = path.join(outputDir, 'aritzia-products.json');
  fs.writeFileSync(productsFile, JSON.stringify(products, null, 2));

  console.log(`\n✓✓✓ SUCCESS! Saved ${products.length} products to ${productsFile}\n`);

  // Show summary
  console.log('Summary:');
  products.forEach((p, i) => {
    console.log(`${i + 1}. ${p.name} - $${p.price}`);
  });

  await browser.close();
}

scrapeAritzia().catch(console.error);
