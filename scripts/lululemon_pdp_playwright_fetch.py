#!/usr/bin/env python3
"""
Lululemon PDP JSON fetcher using a *real* browser context.

This is designed to be run **locally on your Mac**, not inside a sandbox.
It uses Playwright in headed mode with a persistent user profile so it
looks like a normal browser session and is much less likely to be blocked.

What it does:
  - Takes one or more Lululemon PDP URLs (or a text file containing URLs)
  - Opens them in Chromium (visible window, with your cookies/profile)
  - Grabs the embedded Next.js `__NEXT_DATA__` JSON
  - Writes each payload to a JSON file under `data/tmp/`

These JSON files can then be fed into `scripts/lululemon_full_ingest.py`
using its `--payload-path` option, or adapted by `lululemon_graphql_client`
if you decide to pivot to GraphQL payloads later.

Example:
    source venv/bin/activate
    pip install playwright
    playwright install chromium

    python scripts/lululemon_pdp_playwright_fetch.py \\
        --urls-file data/tmp/lululemon_pdp_urls.txt

    # Then, for a given product JSON:
    python scripts/lululemon_full_ingest.py \\
        --payload-path data/tmp/lululemon_prod11500068.json \\
        --brand-name "Lululemon" --brand-slug "lululemon"
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Brand-scoped temp directories so Lululemon artifacts live under
# data/tmp/lululemon/... instead of a shared flat tmp folder.
LULU_TMP_DIR = PROJECT_ROOT / "data" / "tmp" / "lululemon"
PDP_TMP_DIR = LULU_TMP_DIR / "pdp"
USER_DATA_DIR = PROJECT_ROOT / "data" / "playwright_user_data"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Lululemon PDP __NEXT_DATA__ payloads using Playwright in headed mode."
    )
    parser.add_argument(
        "--url",
        action="append",
        dest="urls",
        help="Single PDP URL. Can be specified multiple times.",
    )
    parser.add_argument(
        "--urls-file",
        type=Path,
        help="Path to a text file containing one PDP URL per line.",
    )
    parser.add_argument(
        "--max",
        type=int,
        default=None,
        help="Optional limit on number of URLs to process (for testing).",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=4000,
        help="Extra time in milliseconds to wait after load for client-side JS.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=PDP_TMP_DIR,
        help="Directory to write JSON payloads into (default: data/tmp/lululemon/pdp).",
    )
    return parser.parse_args(argv)


def load_urls(args: argparse.Namespace) -> List[str]:
    urls: List[str] = []
    if args.urls:
        urls.extend(args.urls)
    if args.urls_file:
        if not args.urls_file.exists():
            raise SystemExit(f"URLs file not found: {args.urls_file}")
        for line in args.urls_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    urls = [u for u in urls if u]
    if args.max is not None:
        urls = urls[: args.max]
    if not urls:
        raise SystemExit("No URLs provided. Use --url and/or --urls-file.")
    return urls


def extract_next_data_json(page) -> dict:
    """
    Execute JS in the page to retrieve the Next.js data blob.
    We read from the `__NEXT_DATA__` script tag or the global variable.
    """
    # Try direct global first
    value = page.evaluate(
        """
        () => {
          if (typeof window !== 'undefined' && window.__NEXT_DATA__) {
            return window.__NEXT_DATA__;
          }
          const el = document.querySelector('script#__NEXT_DATA__');
          if (el && el.textContent) {
            try { return JSON.parse(el.textContent); } catch (e) {}
          }
          return null;
        }
        """
    )
    if not value:
        raise RuntimeError("Unable to locate __NEXT_DATA__ on page.")
    return value


def guess_product_code(payload: dict, url: str) -> str:
    """
    Best-effort extraction of a stable product code for naming the output file.
    Falls back to parsing from the URL if the payload is oddly shaped.
    """
    # Common Next.js structure: props.pageProps.initialData / pageProps.product
    props = payload.get("props") or {}
    page_props = props.get("pageProps") or {}

    # Newer shapes might embed under pageProps.product
    product = page_props.get("product") or {}
    code = product.get("productId") or product.get("productCode")
    if isinstance(code, str) and code:
        return code

    # Fall back to a slug or ID from the URL path (e.g. prod11500068)
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    for part in reversed(parts):
        if part.startswith("prod") and any(ch.isdigit() for ch in part):
            return part
    # Last-resort: sanitised last path segment
    if parts:
        return parts[-1].replace("-", "_")
    return "lululemon_pdp"


def iter_with_progress(items: Iterable[str]) -> Iterable[str]:
    for idx, item in enumerate(items, start=1):
        print(f"\n[{idx}] Processing {item}")
        yield item


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    urls = load_urls(args)

    # Ensure brand-scoped directories exist
    out_dir: Path = args.out_dir
    LULU_TMP_DIR.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    USER_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Will write JSON payloads to: {out_dir}")
    print(f"Using persistent Playwright profile at: {USER_DATA_DIR}")
    print("A visible Chromium window will open; you can interact if a challenge appears.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            USER_DATA_DIR,
            headless=False,  # critical: look like a real browser
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-http2",
            ],
        )
        page = browser.new_page()

        # Hit homepage once to satisfy cookies / region challenges
        try:
            print("Priming session on Lululemon homepage…")
            page.goto("https://shop.lululemon.com/", wait_until="domcontentloaded", timeout=120_000)
            page.wait_for_timeout(3000)
        except PlaywrightTimeoutError:
            print("⚠️ Homepage load timed out; continuing anyway.", file=sys.stderr)

        try:
            for url in iter_with_progress(urls):
                try:
                    print(f"  → Navigating to {url}")
                    # `networkidle` is fragile on tracking-heavy sites, so prefer domcontentloaded.
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=120_000)
                    except PlaywrightTimeoutError:
                        print("  ⚠️ domcontentloaded timeout; trying again without wait condition.", file=sys.stderr)
                        page.goto(url, timeout=120_000)

                    page.wait_for_timeout(args.wait_ms)

                    payload = extract_next_data_json(page)
                    product_code = guess_product_code(payload, url)
                    out_path = out_dir / f"lululemon_{product_code}.json"

                    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
                    print(f"  ✅ Saved __NEXT_DATA__ for {product_code} → {out_path}")
                except Exception as exc:  # noqa: BLE001
                    print(f"  ❌ Failed for {url}: {exc}", file=sys.stderr)
        finally:
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:  # pragma: no cover - CLI diagnostics
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


