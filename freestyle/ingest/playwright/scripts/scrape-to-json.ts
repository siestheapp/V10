import 'dotenv/config';
import { chromium } from 'playwright';
import { AritziaAdapter } from '../src/adapters/aritzia';
import * as fs from 'fs';
import * as path from 'path';

async function scrapeToJson(categoryUrl: string, outputDir: string) {
  const browser = await chromium.launch({
    headless: false, // Run visible to see what's happening
    slowMo: 100 // Slow down actions to be more human-like
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 },
    locale: 'en-US',
    timezoneId: 'America/New_York',
    permissions: [],
    // Add realistic browser headers
    extraHTTPHeaders: {
      'Accept-Language': 'en-US,en;q=0.9',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Encoding': 'gzip, deflate, br',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'none',
      'Cache-Control': 'max-age=0'
    }
  });

  const page = await context.newPage();

  // Add random mouse movements to look more human
  await page.addInitScript(() => {
    // Override the navigator.webdriver property
    Object.defineProperty(navigator, 'webdriver', {
      get: () => undefined
    });
  });

  console.log(`Scraping: ${categoryUrl}`);
  console.log(`Output: ${outputDir}\n`);

  // Ensure output directory exists
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }

  try {
    // Crawl category
    console.log('1. Crawling category page...');
    const pdpUrls = await AritziaAdapter.crawlCategory(page, categoryUrl);
    console.log(`Found ${pdpUrls.length} products\n`);

    // Save product URLs
    const urlsFile = path.join(outputDir, 'product-urls.json');
    fs.writeFileSync(urlsFile, JSON.stringify(pdpUrls, null, 2));
    console.log(`✓ Saved URLs to ${urlsFile}\n`);

    // Extract first 10 products (or all if less)
    const limit = Math.min(10, pdpUrls.length);
    console.log(`2. Extracting details for ${limit} products...\n`);

    const products = [];
    for (let i = 0; i < limit; i++) {
      const url = pdpUrls[i];
      console.log(`[${i + 1}/${limit}] ${url}`);

      try {
        const productData = await AritziaAdapter.extractPdp(page, url);
        products.push(productData);
        console.log(`  ✓ ${productData.name} - $${productData.list_price}\n`);

        // Random delay between 3-7 seconds to avoid rate limiting
        if (i < limit - 1) {
          const delay = 3000 + Math.random() * 4000;
          console.log(`  Waiting ${Math.round(delay / 1000)}s before next product...\n`);
          await page.waitForTimeout(delay);
        }
      } catch (error) {
        console.error(`  ✗ Error: ${error}\n`);
      }
    }

    // Save extracted products
    const productsFile = path.join(outputDir, 'products.json');
    fs.writeFileSync(productsFile, JSON.stringify(products, null, 2));
    console.log(`\n✓ Saved ${products.length} products to ${productsFile}`);

    // Create a summary
    const summary = {
      scrapedAt: new Date().toISOString(),
      categoryUrl,
      totalUrlsFound: pdpUrls.length,
      productsExtracted: products.length,
      brands: [...new Set(products.map(p => p.brand))],
      priceRange: {
        min: Math.min(...products.map(p => p.list_price || 0).filter(p => p > 0)),
        max: Math.max(...products.map(p => p.list_price || 0))
      }
    };

    const summaryFile = path.join(outputDir, 'summary.json');
    fs.writeFileSync(summaryFile, JSON.stringify(summary, null, 2));
    console.log(`✓ Saved summary to ${summaryFile}`);

  } catch (error) {
    console.error('Scraping error:', error);
  } finally {
    await browser.close();
  }
}

// Parse command line args
const categoryUrl = process.argv[2] || 'https://www.aritzia.com/us/en/clothing/dresses';
const outputDir = process.argv[3] || path.join(__dirname, '../output');

scrapeToJson(categoryUrl, outputDir);
