import 'dotenv/config';
import { chromium } from 'playwright';
import { ReformationAdapter } from '../src/adapters/reformation';

(async () => {
  const category = process.argv[2] || 'https://www.thereformation.com/collections/dresses';
  const browser = await chromium.launch({ headless: true });
  try {
    const ctx = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116 Safari/537.36'
    });
    const page = await ctx.newPage();
    const urls = await ReformationAdapter.crawlCategory(page as any, category);
    await ctx.close();
    console.log('Found PDP URLs:', urls.length);
    console.log((urls || []).slice(0, 20).join('\n'));
  } finally {
    await browser.close();
  }
})();


