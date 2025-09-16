#!/usr/bin/env python3
"""
Polite J.Crew crawler to prewarm cache for men's tops.
 - Scans selected category listing pages for product links
 - Calls JCrewProductFetcher.fetch_product(url) to store colors (with swatch URLs/hex) in jcrew_product_cache
 - Designed to be safe to run repeatedly; uses the fetcher's normalized cache key to avoid duplicates

Usage:
  python scripts/crawl_jcrew_mens_tops.py --limit 200 --max-pages 3 --delay 0.7
"""

from __future__ import annotations

import argparse
import re
import time
from typing import Iterable, Set, List

import requests
from bs4 import BeautifulSoup

# Flexible import so the script runs from repo root
try:  # Attempt package-style import
    from src.ios_app.Backend.jcrew_fetcher import JCrewProductFetcher  # type: ignore
except Exception:
    import os
    import sys
    repo_root = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(repo_root, os.pardir))  # project root
    backend_dir = os.path.join(repo_root, "src", "ios_app", "Backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    from jcrew_fetcher import JCrewProductFetcher  # type: ignore


DEFAULT_CATEGORIES: List[str] = [
    # Shirts
    "https://www.jcrew.com/m/mens_category/shirts/casual",
    "https://www.jcrew.com/m/mens_category/shirts/dressshirts",
    "https://www.jcrew.com/m/mens_category/shirts/denim",
    # T-shirts & Polos
    "https://www.jcrew.com/m/mens_category/tshirts_and_polos/tshirts",
    "https://www.jcrew.com/m/mens_category/tshirts_and_polos/polos",
    # Sweaters & Sweatshirts
    "https://www.jcrew.com/m/mens_category/sweaters",
    "https://www.jcrew.com/m/mens_category/sweatshirts_and_hoodies",
    # Outerwear & Blazers
    "https://www.jcrew.com/m/mens_category/outerwear",
    "https://www.jcrew.com/m/mens_category/sportcoatsandblazers",
]


PRODUCT_URL_PATTERN = re.compile(r"/p/mens/[^\s\"]*/([A-Z0-9]{4,6})(?:\?|$|/)")


def extract_product_urls(html: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: Set[str] = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/p/mens/" in href and PRODUCT_URL_PATTERN.search(href):
            if href.startswith("/"):
                href = f"https://www.jcrew.com{href}"
            # Normalize by removing tracking query parameters; keep as-is otherwise
            urls.add(href.split("?", 1)[0])
    return urls


def crawl_categories(categories: Iterable[str], max_pages: int, delay: float, limit: int | None) -> List[str]:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    })

    discovered: Set[str] = set()
    for base_url in categories:
        for page in range(1, max_pages + 1):
            url = base_url if page == 1 else f"{base_url}?page={page}"
            try:
                resp = session.get(url, timeout=10)
                resp.raise_for_status()
            except Exception as e:
                print(f"⚠️  Skipping {url}: {e}")
                break

            new_urls = extract_product_urls(resp.text)
            if not new_urls:
                # Stop paginating this category if no products found
                break

            before = len(discovered)
            discovered.update(new_urls)
            after = len(discovered)
            print(f"🔎 {url} → +{after - before} (total {after})")

            if limit and len(discovered) >= limit:
                return list(discovered)[:limit]

            time.sleep(delay)

    return list(discovered)


def prewarm_cache(product_urls: Iterable[str], delay: float, limit: int | None) -> None:
    fetcher = JCrewProductFetcher()
    count = 0
    for url in product_urls:
        try:
            product = fetcher.fetch_product(url)
            if product:
                colors = product.get("colors_available", [])
                print(f"✅ Cached {product.get('product_code','?')} | {product.get('product_name','')} | {len(colors)} colors")
            else:
                print(f"❌ Failed to fetch {url}")
        except Exception as e:
            print(f"❌ Error caching {url}: {e}")
        count += 1
        if limit and count >= limit:
            break
        time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prewarm J.Crew men's tops cache")
    parser.add_argument("--limit", type=int, default=None, help="Max number of products to cache")
    parser.add_argument("--max-pages", type=int, default=3, help="Pages per category")
    parser.add_argument("--delay", type=float, default=0.7, help="Delay between requests in seconds")
    parser.add_argument("--category", action="append", help="Add/override category URL(s)")
    args = parser.parse_args()

    categories = args.category if args.category else DEFAULT_CATEGORIES
    print(f"📚 Crawling {len(categories)} categories, up to {args.max_pages} pages each…")
    urls = crawl_categories(categories, args.max_pages, args.delay, args.limit)
    print(f"🧭 Discovered {len(urls)} product URLs. Prewarming cache…")
    prewarm_cache(urls, args.delay, args.limit)
    print("🎉 Done.")


if __name__ == "__main__":
    main()


