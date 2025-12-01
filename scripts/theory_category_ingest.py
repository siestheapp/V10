#!/usr/bin/env python3
"""
Theory category ingester.

Uses Playwright to render the men's shirts PLP, extracts PDP URLs via
data-product-details blocks, then calls theory_full_ingest for each.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence
from urllib.parse import urlsplit, urlunsplit

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from playwright.sync_api import sync_playwright  # type: ignore
except Exception:  # pragma: no cover
    sync_playwright = None

import theory_full_ingest as full_ingest  # noqa: E402


@dataclass
class ProductCandidate:
    product_code: str
    variant_id: str
    url: str


def render_with_playwright(url: str, wait_ms: int) -> str:
    if not sync_playwright:
        raise RuntimeError("Playwright is required to render Theory PLPs.")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-http2"])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = context.new_page()
        page.goto("https://www.theory.com/men/", wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(1000)
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


def canonicalize_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme or "https", parsed.netloc, parsed.path, "", ""))


def extract_candidates(html: str) -> List[ProductCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: OrderedDict[str, ProductCandidate] = OrderedDict()
    for element in soup.select("[data-product-details]"):
        raw = element.get("data-product-details")
        if not raw:
            continue
        try:
            payload = json.loads(
                raw.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">")
            )
        except json.JSONDecodeError:
            continue
        variant = payload.get("variant")
        listing_url = payload.get("url") or payload.get("productLink")
        if not variant:
            continue
        product_code = (
            element.get("data-master-pid")
            or variant.split("_")[0]
        )
        variant_id = element.get("data-pid") or variant
        if listing_url:
            clean_url = canonicalize_url(listing_url)
        else:
            link = element.select_one("a.link")
            href = link.get("href") if link else None
            if not href:
                image_link = element.select_one(".image-container a")
                href = image_link.get("href") if image_link else None
            if not href:
                continue
            clean_url = canonicalize_url(f"https://www.theory.com{href}")
        key = (product_code, clean_url)
        if key not in candidates:
            candidates[key] = ProductCandidate(
                product_code=product_code,
                variant_id=variant_id,
                url=clean_url,
            )
    return list(candidates.values())


def ingest_candidates(
    candidates: Sequence[ProductCandidate],
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    force: bool,
) -> None:
    total = len(candidates)
    if dry_run:
        for idx, candidate in enumerate(candidates, 1):
            print(f"[{idx}/{total}] {candidate.product_code} {candidate.url}")
        return
    successes = 0
    failures: List[str] = []
    for idx, candidate in enumerate(candidates, 1):
        label = f"[{idx}/{total}] {candidate.product_code}"
        print(f"{label} → ingesting {candidate.url}")
        try:
            full_ingest.ingest_catalog(
                candidate.url,
                pid=candidate.product_code,
                color=None,
                spotlight_enabled=spotlight_enabled,
                brand_name=brand_name,
                brand_slug=brand_slug,
                dry_run=False,
                force=force,
            )
            successes += 1
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{candidate.url} :: {exc}")
            print(f"❌ {label} failed: {exc}")
    print(f"\nSummary: {successes} succeeded / {total} attempted.")
    if failures:
        print("Failures:")
        for row in failures:
            print(f"  - {row}")
        raise SystemExit(1)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bulk-ingest Theory PLP (mens shirts).")
    parser.add_argument(
        "--url",
        default="https://www.theory.com/men/shirts/",
        help="Theory PLP URL to render.",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=3000,
        help="Extra wait after domcontentloaded for JS hydration.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List discovered PDPs without ingesting.",
    )
    parser.add_argument(
        "--spotlight",
        action="store_true",
        help="Mark resulting products as spotlight-enabled.",
    )
    parser.add_argument(
        "--brand-name",
        default="Theory",
        help="Override brand display name.",
    )
    parser.add_argument(
        "--brand-slug",
        default="theory",
        help="Override brand slug.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force underlying PDP ingests even when unchanged.",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Optional path to a pre-rendered PLP HTML file.",
    )
    return parser.parse_args(argv)


def load_plp_html(url: str, wait_ms: int, html_path: Optional[Path]) -> str:
    if html_path:
        return html_path.read_text(encoding="utf-8")
    cached = Path("data/tmp/theory_plp_cache.html")
    if cached.exists():
        return cached.read_text(encoding="utf-8")
    html = render_with_playwright(url, wait_ms)
    cached.parent.mkdir(parents=True, exist_ok=True)
    cached.write_text(html, encoding="utf-8")
    return html


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    plp_html = load_plp_html(args.url, args.wait_ms, args.html)
    html = plp_html
    candidates = extract_candidates(html)
    if not candidates:
        raise SystemExit("No products discovered on the PLP; check if JavaScript rendering succeeded.")
    print(f"Discovered {len(candidates)} unique Theory PDPs.")
    ingest_candidates(
        candidates,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        force=args.force,
    )


if __name__ == "__main__":
    main()

