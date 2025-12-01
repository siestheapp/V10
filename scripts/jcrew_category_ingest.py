#!/usr/bin/env python3
"""
J.Crew Category → fs-core Ingest Runner

Given a J.Crew category/listing URL (e.g. men's linen casual shirts), this script:
  1. Uses the existing Selenium-based JCrewCategoryScraper to discover PDP URLs
  2. For each unique product URL, calls jcrew_full_ingest.ingest_catalog(...)
     so that:
       - core.products / core.product_variants / core.product_images are populated
       - ops.ingestion_targets is updated
       - spotlight content ingestion is triggered via jcrew_spotlight_ingest
       - ops.ingest_runs and ops.ingest_failures capture per-PDP ingest status

USAGE:
    source venv/bin/activate
    python scripts/jcrew_category_ingest.py \\
        --url "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen" \\
        [--limit 10] [--no-spotlight] [--dry-run]
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Sequence

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from jcrew_category_scraper import JCrewCategoryScraper  # noqa: E402
import jcrew_full_ingest as full_ingest  # noqa: E402


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover all PDPs from a J.Crew category page and ingest them into fs-core."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="J.Crew category/listing URL (e.g. men's shirts / linen subcategory).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on number of products to ingest (for testing).",
    )
    parser.add_argument(
        "--no-spotlight",
        dest="spotlight",
        action="store_false",
        default=True,
        help="Disable spotlight content for these products (baseline-only ingest).",
    )
    parser.add_argument(
        "--brand-name",
        default=full_ingest.DEFAULT_BRAND_NAME,
        help="Brand display name (defaults to J.Crew).",
    )
    parser.add_argument(
        "--brand-slug",
        default=full_ingest.DEFAULT_BRAND_SLUG,
        help="Brand slug (defaults to 'jcrew').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print discovered PDP URLs and per-product ingest payloads; no DB writes.",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the category browser in headless mode (no visible Chrome window).",
    )
    return parser.parse_args(argv)


def discover_products(category_url: str, *, headless: bool, limit: Optional[int]) -> list[dict]:
    """
    Use JCrewCategoryScraper to discover PDP URLs from the category page.
    """
    scraper = JCrewCategoryScraper(headless=headless)
    try:
        scraper.driver = scraper.setup_driver()
        product_links = scraper.extract_product_links(category_url)
    finally:
        if scraper.driver:
            scraper.driver.quit()

    if limit is not None:
        product_links = product_links[:limit]

    return product_links


def ingest_category(
    category_url: str,
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    headless: bool,
    limit: Optional[int],
) -> None:
    print(f"🚀 J.Crew Category Ingest")
    print(f"📍 Category URL: {category_url}")
    print(f"📅 Started: {datetime.utcnow().isoformat()}Z")

    products = discover_products(category_url, headless=headless, limit=limit)
    total = len(products)
    print(f"📋 Discovered {total} unique PDPs from category page.")

    if dry_run:
        for idx, info in enumerate(products, 1):
            print(f"[DRY-RUN] {idx:03d}/{total:03d} {info.get('product_code')} → {info.get('url')}")
        return

    successes = 0
    failures = 0

    for idx, info in enumerate(products, 1):
        url = info.get("url")
        product_code = info.get("product_code")
        print(f"\n[{idx}/{total}] Ingesting {product_code} → {url}")
        try:
            full_ingest.ingest_catalog(
                url,
                spotlight_enabled=spotlight_enabled,
                brand_name=brand_name,
                brand_slug=brand_slug,
                dry_run=False,
            )
            successes += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"❌ Failed to ingest {product_code} from {url}: {exc}")
            # Per-PDP details and error are already recorded via ops.ingest_runs/ops.ingest_failures

    print("\n📊 CATEGORY INGEST SUMMARY")
    print(f"   Total PDPs:   {total}")
    print(f"   Successful:   {successes}")
    print(f"   Failed:       {failures}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    if "jcrew.com" not in args.url:
        raise SystemExit("❌ URL must be from jcrew.com")

    ingest_category(
        args.url,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        headless=args.headless,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()







