#!/usr/bin/env python3
"""
Quick-and-dirty Lululemon PDP fetcher.

Given any Lululemon PDP URL, this script:
  1. Loads the page (requests first, falls back to Playwright for Akamai-protected pages)
  2. Extracts the embedded Next.js `__NEXT_DATA__` payload
  3. Prints the top-level keys and optionally writes the payload to disk for inspection

Use this as the first step toward a full Lululemon ingest pipeline. Once we understand
the payload shape we can build `lululemon_full_ingest.py` mirroring the J.Crew scripts.

Example:
    source venv/bin/activate
    python scripts/lululemon_pdp_dump.py \\
        --url "https://shop.lululemon.com/p/mens-button-down-shirts/Commission-LS-Button-Down-Pockets/_/prod6750191?color=73732" \\
        --output data/tmp/lululemon_prod6750191.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dump Lululemon PDP __NEXT_DATA__ payload.")
    parser.add_argument("--url", required=True, help="Full Lululemon PDP URL.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the parsed JSON payload for later inspection.",
    )
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Disable Playwright fallback (useful if running on a box without browsers).",
    )
    return parser.parse_args(argv)


def fetch_html(url: str, *, allow_playwright: bool = True) -> str:
    """Fetch PDP HTML, falling back to Playwright when Akamai blocks requests."""
    parsed = urlparse(url)
    if parsed.scheme == "file":
        local_path = Path(unquote(parsed.path))
        if not local_path.exists():
            raise RuntimeError(f"Local file not found: {local_path}")
        return local_path.read_text(encoding="utf-8")
    if parsed.scheme in {"", "path"} and Path(url).exists():
        return Path(url).read_text(encoding="utf-8")

    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    try:
        resp = session.get(url, timeout=30)
        if resp.status_code == 200:
            return resp.text
        print(f"⚠️  requests returned {resp.status_code}; falling back to Playwright…", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001
        print(f"⚠️  requests error: {exc}; falling back to Playwright…", file=sys.stderr)

    if not allow_playwright:
        raise RuntimeError("Failed to fetch HTML via requests and Playwright fallback disabled.")

    return fetch_html_via_playwright(url)


def fetch_html_via_playwright(url: str) -> str:
    """Use headless Chromium via Playwright to load the PDP and return the HTML."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-http2"])
        context = browser.new_context(
            user_agent=DEFAULT_HEADERS["User-Agent"],
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = context.new_page()
        # Hit the homepage first to satisfy Akamai cookie challenges
        page.goto("https://shop.lululemon.com/", wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(1500)
        html = page.content()
        browser.close()
        return html


def extract_next_data(html: str) -> dict:
    """Parse the Next.js data blob."""
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        raise RuntimeError("Unable to locate __NEXT_DATA__ payload on page.")
    return json.loads(script.string)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    html = fetch_html(args.url, allow_playwright=not args.no_playwright)
    payload = extract_next_data(html)

    props = payload.get("props", {})
    page_props = props.get("pageProps", {})

    print("✅ Successfully extracted __NEXT_DATA__ payload.")
    print(f"Top-level keys: {list(payload.keys())}")
    print(f"pageProps keys: {list(page_props.keys())}")
    if "product" in page_props:
        product = page_props["product"]
        code = product.get("productId") or product.get("productCode")
        name = product.get("name") or product.get("productName")
        print(f"Parsed product: {code} – {name}")
    else:
        print("⚠️  pageProps missing 'product' key; inspect payload manually.")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"💾 Wrote payload to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - CLI diagnostics
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)

