#!/usr/bin/env python3
"""
Scrape J.Crew PDP swatch colors and swatch image URLs using Playwright.

Usage:
  python scripts/jcrew_swatches_playwright.py --url "<PDP_URL>" --json
Requires:
  pip install playwright bs4
  playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


@dataclass
class Swatch:
    color: str
    swatch_url: str


def extract_url_from_style(style_val: str) -> Optional[str]:
    if not style_val:
        return None
    m = re.search(r'url\\([\'"]?([^\\)\'"]+)[\'"]?\\)', style_val, re.IGNORECASE)
    return m.group(1) if m else None


def normalize(txt: str) -> str:
    return re.sub(r"\\s+", " ", txt or "").strip()


def parse_swatches_from_html(html: str) -> List[Swatch]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[Swatch] = []
    seen: set[Tuple[str, str]] = set()

    # Strategy 0 (targeted): J.Crew PDP swatch list under section#c-product__price-colors
    for el in soup.select("section#c-product__price-colors [data-qaid^='pdpProductPriceColorsGroupListItem-']"):
        color = normalize(el.get("data-name") or el.get("aria-label") or "")
        img = el.find("img")
        src = normalize(img.get("src")) if img and img.get("src") else ""
        if not color or not src:
            continue
        key = (color.lower(), src)
        if key in seen:
            continue
        seen.add(key)
        results.append(Swatch(color=color, swatch_url=src))

    # Strategy 1: <img> with "swatch" in src
    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if not src or "swatch" not in src.lower():
            continue
        color = normalize(img.get("alt") or img.get("aria-label") or img.get("title") or "")
        if not color:
            parent = img.find_parent(attrs={"aria-label": True})
            if parent:
                color = normalize(parent.get("aria-label", ""))
        if not color:
            continue
        key = (color.lower(), src)
        if key in seen:
            continue
        seen.add(key)
        results.append(Swatch(color=color, swatch_url=src))

    # Strategy 2: elements with background-image style + label
    for el in soup.select("[style*='background-image']"):
        style_val = el.get("style") or ""
        url = extract_url_from_style(style_val)
        if not url:
            continue
        color = normalize(el.get("aria-label") or el.get("title") or "")
        if not color:
            parent = el.find_parent(attrs={"aria-label": True})
            if parent:
                color = normalize(parent.get("aria-label", ""))
        if not color:
            text = normalize(el.get_text(" ", strip=True))
            color = text or color
        if not color:
            continue
        key = (color.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        results.append(Swatch(color=color, swatch_url=url))

    # Dedup by color (first URL wins)
    dedup: dict[str, Swatch] = {}
    for s in results:
        k = s.color.lower()
        if k not in dedup:
            dedup[k] = s
    return list(dedup.values())


def fetch_rendered_html(url: str, timeout_ms: int = 60000) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/123.0.0.0 Safari/537.36"
            ))
            page.set_default_timeout(timeout_ms)
            # Reduce long-lived connections that prevent networkidle
            def _route(route, req):
                if req.resource_type in {"websocket", "eventsource", "media", "font"}:
                    return route.abort()
                return route.continue_()
            page.route("**/*", _route)

            page.goto(url, wait_until="domcontentloaded")
            # Dismiss cookie banners if present (best-effort)
            for sel in [
                'button:has-text("Accept")',
                'button:has-text("I Accept")',
                'button:has-text("Agree")',
            ]:
                try:
                    page.locator(sel).first.click(timeout=1500)
                except Exception:
                    pass
            # Wait specifically for the swatch container
            page.wait_for_selector("section#c-product__price-colors", timeout=timeout_ms)
            # Nudge rendering
            page.evaluate("window.scrollTo(0, document.body.scrollHeight/3);")
            page.wait_for_timeout(800)
            return page.content()
        finally:
            browser.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    html = fetch_rendered_html(args.url)
    swatches = parse_swatches_from_html(html)
    if args.json:
        print(json.dumps([asdict(s) for s in swatches], indent=2))
    else:
        for s in swatches:
            print(f"{s.color}\\t{s.swatch_url}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


