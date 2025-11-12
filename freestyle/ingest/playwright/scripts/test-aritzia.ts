import 'dotenv/config';
import { chromium } from 'playwright';
import { AritziaAdapter } from '../src/adapters/aritzia';

async function test() {
  const browser = await chromium.launch({ headless: false }); // Set to false to watch it work
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  const categoryUrl = 'https://www.aritzia.com/us/en/clothing/dresses';

  console.log('Testing Aritzia adapter...');
  console.log('Category:', categoryUrl);

  try {
    console.log('\n1. Crawling category page...');
    const pdpUrls = await AritziaAdapter.crawlCategory(page, categoryUrl);
    console.log(`Found ${pdpUrls.length} product URLs`);
    console.log('First 5 URLs:', pdpUrls.slice(0, 5));

    if (pdpUrls.length > 0) {
      console.log('\n2. Testing first product extraction...');
      const testUrl = pdpUrls[0];
      console.log('Extracting:', testUrl);

      const productData = await AritziaAdapter.extractPdp(page, testUrl);
      console.log('\nExtracted product data:');
      console.log(JSON.stringify(productData, null, 2));
    }
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
}

test();
