import { chromium, Browser, Page } from 'playwright';

export async function withBrowser<T>(fn: (browser: Browser) => Promise<T>) {
  const browser = await chromium.launch({ headless: true });
  try {
    return await fn(browser);
  } finally {
    await browser.close();
  }
}

export async function newPage(browser: Browser): Promise<Page> {
  const ctx = await browser.newContext({
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116 Safari/537.36'
  });
  const page = await ctx.newPage();
  return page;
}


