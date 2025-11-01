#!/usr/bin/env ts-node
import { promises as fs } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { chromium } from 'playwright'

const baseUrl =
  process.env.MOCKUP_URL ?? 'http://localhost:3000/mockups/preview?screen=size-twin'

const OUTPUTS: Array<{ scale: number; path: string }> = [
  { scale: 2, path: 'public/mockups/social-size-twin.png' },
  { scale: 3, path: 'public/mockups/social-size-twin@3x.png' },
]

const VIEWPORT = { width: 645, height: 1398 }

async function ensureDir(filePath: string) {
  await fs.mkdir(dirname(filePath), { recursive: true })
}

async function capture() {
  for (const output of OUTPUTS) {
    const browser = await chromium.launch()
    const context = await browser.newContext({
      viewport: VIEWPORT,
      deviceScaleFactor: output.scale,
      colorScheme: 'light',
    })
    const page = await context.newPage()
    await page.goto(baseUrl, { waitUntil: 'networkidle' })
    await page.setViewportSize(VIEWPORT)
    await page.waitForSelector('[data-testid="size-twin-screen"]', {
      state: 'visible',
      timeout: 15000,
    })
    const dest = resolve(output.path)
    await ensureDir(dest)
    await page.screenshot({
      path: dest,
      fullPage: true,
    })
    await browser.close()
    // eslint-disable-next-line no-console
    console.log(`Saved screenshot → ${dest}`)
  }
}

capture().catch((error) => {
  // eslint-disable-next-line no-console
  console.error(error)
  process.exit(1)
})
