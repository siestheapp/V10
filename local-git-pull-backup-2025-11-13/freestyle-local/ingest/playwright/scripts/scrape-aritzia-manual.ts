import 'dotenv/config';
import { chromium } from 'playwright';
import { AritziaAdapter } from '../src/adapters/aritzia';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function askQuestion(query: string): Promise<string> {
  return new Promise(resolve => rl.question(query, resolve));
}

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

  console.log('Step 1: Navigating to Aritzia dresses...\n');
  await page.goto('https://www.aritzia.com/us/en/clothing/dresses', { timeout: 90000 });

  console.log('\n⚠️  MANUAL STEP REQUIRED ⚠️');
  console.log('If you see a Cloudflare challenge in the browser:');
  console.log('1. Solve the CAPTCHA');
  console.log('2. Wait for the dresses page to fully load');
  console.log('3. Come back here and press ENTER\n');

  await askQuestion('Press ENTER when the page has loaded...');

  console.log('\n✓ Continuing with scrape...\n');

  // Now try to find products
  const productLinks = await page.$$eval('a[href*="/product/"]', as =>
    Array.from(as).map(a => (a as HTMLAnchorElement).href)
  );

  const uniqueUrls = Array.from(new Set(productLinks))
    .filter(h => h.startsWith('https://www.aritzia.com/'))
    .filter(h => /\/product\//.test(h));

  console.log(`Found ${uniqueUrls.length} product URLs\n`);

  if (uniqueUrls.length === 0) {
    console.error('No products found. The page may not have loaded correctly.');
    await browser.close();
    rl.close();
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

  // Extract first 5 products
  const limit = Math.min(5, uniqueUrls.length);
  console.log(`Extracting ${limit} products...\n`);

  const products = [];
  for (let i = 0; i < limit; i++) {
    const url = uniqueUrls[i];
    console.log(`[${i + 1}/${limit}] ${url}`);

    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 90000 });
      await page.waitForTimeout(3000);

      // Check for Cloudflare again
      const title = await page.title();
      if (title.toLowerCase().includes('cloudflare') || title.toLowerCase().includes('just a moment')) {
        console.log('  ⚠️  Cloudflare detected, please solve and press ENTER');
        await askQuestion('  Press ENTER when ready...');
      }

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
        if (name && name !== 'www.aritzia.com' && name.length > 2) break;
      }

      // Try to find price
      let priceText = '';
      const priceSelectors = [
        '[class*="price"]',
        '[class*="Price"]',
        'span[class*="Price"]'
      ];

      for (const sel of priceSelectors) {
        priceText = await page.$eval(sel, el => el.textContent?.trim() || '').catch(() => '');
        if (priceText && /\$?\d+/.test(priceText)) break;
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
      console.log(`  Images: ${product.images.length}\n`);

      // Wait between products
      if (i < limit - 1) {
        const delay = 2000 + Math.random() * 3000;
        await page.waitForTimeout(delay);
      }
    } catch (error) {
      console.error(`  ✗ Error: ${error}\n`);
    }
  }

  // Save products
  fs.writeFileSync(
    path.join(outputDir, 'products-manual.json'),
    JSON.stringify(products, null, 2)
  );

  console.log(`\n✓ Saved ${products.length} products to output/products-manual.json`);

  await browser.close();
  rl.close();
}

scrapeAritzia();
