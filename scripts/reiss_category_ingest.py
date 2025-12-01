#!/usr/bin/env python3
"""
Category-level ingester for Reiss.

Loads a Reiss PLP (e.g. men's formal shirts) using Playwright so we can
discover every PDP URL, then pipes each PDP into reiss_full_ingest.
"""

from __future__ import annotations

import argparse
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from playwright.sync_api import sync_playwright  # type: ignore
except Exception:  # pragma: no cover - playwright optional at runtime
    sync_playwright = None

import reiss_full_ingest as full_ingest  # noqa: E402

DEFAULT_BRAND_NAME = "Reiss"
DEFAULT_BRAND_SLUG = "reiss"


@dataclass
class ProductCandidate:
    style_code: str
    product_code: str
    url: str


def build_page_urls(base_url: str, total_pages: int) -> List[str]:
    if total_pages <= 1:
        return [base_url]
    parsed = urlsplit(base_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    urls: List[str] = []
    for page_index in range(1, total_pages + 1):
        query["p"] = str(page_index)
        urls.append(
            urlunsplit(
                (
                    parsed.scheme or "https",
                    parsed.netloc,
                    parsed.path,
                    urlencode(query, doseq=True),
                    parsed.fragment,
                )
            )
        )
    return urls


def render_with_playwright(url: str, wait_ms: int) -> str:
    if not sync_playwright:
        raise RuntimeError(
            "Playwright is required but not available. "
            "Install it (`playwright install chromium`) or provide a pre-rendered HTML file."
        )
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
        # Hit homepage first so Akamai/challenge cookies are satisfied.
        page.goto("https://www.reiss.com/us/en", wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(1500)
        page.goto(url, wait_until="domcontentloaded", timeout=120000)
        page.wait_for_timeout(wait_ms)
        html = page.content()
        browser.close()
    return html


def extract_candidates_from_html(html: str, base_url: str) -> List[ProductCandidate]:
    soup = BeautifulSoup(html, "html.parser")
    anchors = soup.select("a[href*='/style/']")
    seen_styles: OrderedDict[str, ProductCandidate] = OrderedDict()
    for anchor in anchors:
        href = anchor.get("href")
        if not href or "/style/" not in href:
            continue
        candidate = parse_candidate_url(href, base_url)
        if not candidate:
            continue
        if candidate.style_code not in seen_styles:
            seen_styles[candidate.style_code] = candidate
    return list(seen_styles.values())


def parse_candidate_url(href: str, base_url: str) -> Optional[ProductCandidate]:
    parsed = urlsplit(href)
    if not parsed.netloc:
        base = urlsplit(base_url)
        parsed = parsed._replace(
            scheme=base.scheme or "https",
            netloc=base.netloc,
        )
    parts = [p for p in parsed.path.split("/") if p]
    try:
        style_index = parts.index("style")
    except ValueError:
        return None
    if len(parts) <= style_index + 2:
        return None
    style_code = parts[style_index + 1]
    product_code = parts[style_index + 2]
    clean_url = urlunsplit(
        (
            parsed.scheme,
            parsed.netloc,
            f"/{'/'.join(parts[: style_index + 3])}",
            "",
            "",
        )
    )
    return ProductCandidate(style_code=style_code, product_code=product_code, url=clean_url)


def ingest_candidates(
    candidates: Sequence[ProductCandidate],
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    max_variants: Optional[int],
    force: bool,
) -> None:
    total = len(candidates)
    if dry_run:
        for idx, candidate in enumerate(candidates, 1):
            print(
                f"[{idx}/{total}] {candidate.style_code} "
                f"(product_code={candidate.product_code}) {candidate.url}"
            )
        return

    successes = 0
    failures: List[str] = []
    for idx, candidate in enumerate(candidates, 1):
        label = f"[{idx}/{total}] {candidate.style_code}"
        print(f"{label} → ingesting {candidate.url}")
        try:
            full_ingest.ingest_catalog(
                candidate.url,
                html_path=None,
                spotlight_enabled=spotlight_enabled,
                brand_name=brand_name,
                brand_slug=brand_slug,
                dry_run=False,
                max_variants=max_variants,
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
    parser = argparse.ArgumentParser(description="Bulk-ingest a Reiss category page.")
    parser.add_argument(
        "--url",
        required=True,
        help="Reiss PLP/Category URL (e.g. https://www.reiss.com/.../use-formal?p=1)",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pagination pages to crawl (increments the 'p' query param).",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=3000,
        help="Extra wait after domcontentloaded for JS to hydrate (Playwright).",
    )
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Disable Playwright rendering (expects already-rendered HTML).",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Optional path to pre-rendered HTML (skips network fetch).",
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
        default=DEFAULT_BRAND_NAME,
        help="Brand display name (defaults to Reiss).",
    )
    parser.add_argument(
        "--brand-slug",
        default=DEFAULT_BRAND_SLUG,
        help="Brand slug in core.brands (defaults to 'reiss').",
    )
    parser.add_argument(
        "--max-variants",
        type=int,
        help="Optional cap on expanded variants per PDP (debugging).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force underlying PDP ingests even if the content hash matches a prior success.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    page_urls = build_page_urls(args.url, max(1, args.pages))
    candidates: OrderedDict[str, ProductCandidate] = OrderedDict()

    if args.html:
        html = args.html.read_text(encoding="utf-8")
        for candidate in extract_candidates_from_html(html, args.url):
            candidates.setdefault(candidate.style_code, candidate)
    else:
        if args.no_playwright:
            raise SystemExit("Playwright disabled but no --html provided.")
        for page_url in page_urls:
            print(f"Rendering {page_url}")
            html = render_with_playwright(page_url, wait_ms=args.wait_ms)
            for candidate in extract_candidates_from_html(html, page_url):
                candidates.setdefault(candidate.style_code, candidate)

    if not candidates:
        raise SystemExit("No PDP links discovered; ensure the URL is correct and Playwright rendered the content.")

    print(f"Discovered {len(candidates)} unique style codes.")
    ingest_candidates(
        list(candidates.values()),
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        max_variants=args.max_variants,
        force=args.force,
    )


if __name__ == "__main__":
    main()





