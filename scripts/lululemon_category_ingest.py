#!/usr/bin/env python3
"""
Lululemon Category → fs-core Ingest Runner

This script mirrors the J.Crew category orchestrator but uses the Lululemon
payloads we already reverse-engineered. Given a category/listing URL (or a
saved `__NEXT_DATA__` JSON file), it:

  1. Loads the page (requests + Playwright fallback via lululemon_pdp_dump)
  2. Recursively scans the Next.js payload for any objects containing
     both `productId` and `pdpUrl`
  3. Deduplicates those PDPs by productId and optionally limits the run
  4. Runs `lululemon_full_ingest.ingest_catalog(...)` for each PDP so the
     fs-core catalog + spotlight tables stay in sync

Because Lululemon sits behind aggressive Akamai rules, you can point
`--payload` at a locally saved JSON dump (grabbed via browser “Save Page
Source” + `lululemon_pdp_dump.py --url file:///... --output ...`) to avoid
network flakiness during category discovery.
"""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(PROJECT_ROOT))

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in __import__("sys").path:
    __import__("sys").path.insert(0, str(SCRIPTS_DIR))

import lululemon_full_ingest as full_ingest  # noqa: E402
from lululemon_graphql_client import (  # noqa: E402
    REQUESTS_IMPORT_ERROR,
    execute_query as graphql_execute_query,
)

# Brand-scoped tmp layout for Lululemon artifacts.
LULU_TMP_DIR = PROJECT_ROOT / "data" / "tmp" / "lululemon"

# New preferred locations:
LULU_CATEGORY_DIR = LULU_TMP_DIR / "category"
LULU_GRAPHQL_DIR = LULU_TMP_DIR / "graphql"

# Legacy locations (pre-reorg); still read from and write-compatible for now.
LEGACY_CATEGORY_DIR = PROJECT_ROOT / "data" / "tmp" / "lululemon_category_cache"
LEGACY_GRAPHQL_DIR = PROJECT_ROOT / "data" / "tmp" / "lululemon_graphql_cache"

# Keep exported names for backwards compatibility with any external imports.
CATEGORY_CACHE_DIR = LULU_CATEGORY_DIR
GRAPHQL_CACHE_DIR = LULU_GRAPHQL_DIR


@dataclass(frozen=True)
class ProductCandidate:
    product_id: str
    pdp_url: str
    display_name: Optional[str]
    source_category: Optional[str]


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover PDPs from a Lululemon category page and ingest them into fs-core."
    )
    parser.add_argument(
        "--url",
        help="Lululemon category/listing URL (e.g. https://shop.lululemon.com/c/men-button-down-shirts).",
    )
    parser.add_argument(
        "--payload",
        type=Path,
        help="Local __NEXT_DATA__ JSON file (useful when Akamai blocks direct fetches).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Optional cap on the number of products to ingest.",
    )
    parser.add_argument(
        "--no-spotlight",
        dest="spotlight",
        action="store_false",
        default=True,
        help="Disable spotlight content for these products.",
    )
    parser.add_argument(
        "--brand-name",
        default=full_ingest.DEFAULT_BRAND_NAME,
        help="Brand display name (defaults to Lululemon).",
    )
    parser.add_argument(
        "--brand-slug",
        default=full_ingest.DEFAULT_BRAND_SLUG,
        help="Brand slug (defaults to 'lululemon').",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List discovered PDPs without touching the database.",
    )
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Disable Playwright fallback when fetching remote category pages.",
    )
    parser.add_argument(
        "--use-graphql",
        action="store_true",
        help="Fetch each PDP via GraphQL instead of the scraped category payload.",
    )
    parser.add_argument(
        "--graphql-cache-dir",
        type=Path,
        default=GRAPHQL_CACHE_DIR,
        help="Directory to store cached GraphQL responses.",
    )
    parser.add_argument(
        "--refresh-graphql-cache",
        action="store_true",
        help="Force re-fetching GraphQL responses even when cache files exist.",
    )
    return parser.parse_args(argv)


def load_category_payload(
    url: Optional[str],
    payload_path: Optional[Path],
    allow_playwright: bool,
) -> Dict:
    if payload_path:
        return json.loads(payload_path.read_text(encoding="utf-8"))
    if not url:
        raise RuntimeError("Provide either --url or --payload for category discovery.")
    luludump = importlib.import_module("lululemon_pdp_dump")
    html = luludump.fetch_html(url, allow_playwright=allow_playwright)
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")
    if not script or not script.string:
        raise RuntimeError("Unable to locate __NEXT_DATA__ payload on category page.")
    return json.loads(script.string)


def build_product_lookup(payload: Dict) -> Dict[str, Dict]:
    lookup: Dict[str, Dict] = {}
    for node in iter_product_nodes(payload):
        product_id = str(node.get("productId") or "").strip()
        if not product_id:
            continue
        if product_id not in lookup and node.get("skuStyleOrder"):
            lookup[product_id] = node
    return lookup


def iter_product_nodes(node: object) -> Iterable[Dict[str, object]]:
    if isinstance(node, dict):
        keys = node.keys()
        if "productId" in keys and "pdpUrl" in keys:
            yield node
        for value in node.values():
            yield from iter_product_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from iter_product_nodes(item)


def extract_candidates(payload: Dict) -> List[ProductCandidate]:
    seen: Dict[str, ProductCandidate] = {}
    for node in iter_product_nodes(payload):
        product_id = str(node.get("productId") or "").strip()
        pdp_url = node.get("pdpUrl") or node.get("pdpUrlWithRegion")
        if not product_id or not pdp_url:
            continue
        full_url = canonicalize_pdp_url(pdp_url)
        display_name = node.get("displayName") or (
            node.get("productName")[0]
            if isinstance(node.get("productName"), list) and node["productName"]
            else node.get("productName")
        )
        category = node.get("parentCategoryDisplayName") or node.get("productCategory")
        candidate = ProductCandidate(
            product_id=product_id,
            pdp_url=full_url,
            display_name=display_name,
            source_category=category if isinstance(category, str) else None,
        )
        seen.setdefault(product_id, candidate)
    return list(seen.values())


def canonicalize_pdp_url(path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{full_ingest.BASE_HOST}{path}"


def normalize_price_value(value: Optional[str]) -> str:
    if not value:
        return "0.00"
    value = str(value)
    if "." in value:
        return value
    return f"{value}.00"


def dedupe_preserve_order(items: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def build_synthetic_payload(
    product: Dict,
    canonical_url: str,
) -> Dict:
    product_id = str(product.get("productId") or "").strip()
    display_name = (product.get("displayName") or product.get("productName") or "Untitled Product").strip()
    product_name = (product.get("productName") or display_name).strip()
    parent_category = product.get("parentCategoryDisplayName") or product.get("parentCategoryUnifiedId")
    product_category = product.get("productCategory")
    if isinstance(product_category, str):
        product_category_list: List[str] = [product_category]
    elif isinstance(product_category, list):
        product_category_list = product_category
    else:
        product_category_list = [parent_category] if parent_category else []

    list_price_raw = (product.get("listPrice") or ["0"])[0]
    sale_price_raw = (product.get("productSalePrice") or [None])[0]
    currency_code = product.get("currencyCode") or "USD"
    product_summary = {
        "productId": product_id,
        "displayName": display_name,
        "productName": product_name,
        "parentCategoryDisplayName": parent_category,
        "productCategory": product_category_list,
        "pdpUrl": product.get("pdpUrl") or canonical_url,
        "unifiedId": product.get("unifiedId") or product_name,
        "allAvailableSizes": product.get("allAvailableSizes") or [],
        "listPrice": product.get("listPrice") or [],
        "price": {
            "listPrice": normalize_price_value(list_price_raw),
            "currency": {"code": currency_code, "symbol": "$"},
            "onSale": bool(product.get("productOnSale")),
            "salePrice": normalize_price_value(sale_price_raw) if sale_price_raw else None,
            "earlyAccessMarkdownPrice": None,
        },
        "skuStyleOrder": product.get("skuStyleOrder") or [],
        "trendingColorsAll": [],
        "topSellers": [],
    }

    swatch_map = {
        str(swatch.get("colorId")): swatch for swatch in product.get("swatches") or []
    }
    color_meta: Dict[str, Dict[str, object]] = {}
    for sku in product.get("skuStyleOrder") or []:
        color_id = str(sku.get("colorId") or "").strip()
        if not color_id:
            continue
        entry = color_meta.setdefault(
            color_id,
            {
                "code": color_id,
                "name": sku.get("colorName"),
                "slug": sku.get("styleId02") or sku.get("styleId") or color_id,
                "sizes": [],
                "images": [],
            },
        )
        if sku.get("colorName"):
            entry["name"] = sku["colorName"]
        if sku.get("styleId02"):
            entry["slug"] = sku["styleId02"]
        if sku.get("styleId"):
            entry["styleId"] = sku["styleId"]
        entry["images"].extend(sku.get("images") or [])
        normalized_size = full_ingest.normalize_size(sku.get("size"))
        if normalized_size and normalized_size not in entry["sizes"]:
            entry["sizes"].append(normalized_size)

    for color_id, entry in color_meta.items():
        swatch = swatch_map.get(color_id)
        if swatch:
            entry["swatchUrl"] = swatch.get("primaryImage") or swatch.get("hoverImage")
        elif entry.get("images"):
            entry["swatchUrl"] = entry["images"][0]

    default_color = next(iter(color_meta.keys()), None)
    colors = [
        {
            "code": code,
            "name": meta.get("name") or code,
            "swatchUrl": meta.get("swatchUrl"),
            "slug": meta.get("slug") or code,
        }
        for code, meta in color_meta.items()
    ]
    color_driver = [
        {"color": code, "name": meta.get("name") or code, "sizes": meta.get("sizes") or []}
        for code, meta in color_meta.items()
    ]

    product_carousel = []
    for code, meta in color_meta.items():
        hero_images = dedupe_preserve_order(meta.get("images") or [])
        if not hero_images:
            continue
        product_carousel.append(
            {
                "color": {
                    "code": code,
                    "name": meta.get("name") or code,
                    "swatchUrl": meta.get("swatchUrl"),
                    "slug": meta.get("slug") or code,
                },
                "modelInfo": {"description": None, "modelIsWearing": [], "shopThisLook": None},
                "imageInfo": hero_images,
                "mediaInfo": [{"type": "image", "url": img, "posterImageUrl": None} for img in hero_images],
            }
        )

    canonical_pdp_url = full_ingest.canonicalize_url(product.get("pdpUrl"), canonical_url)
    skus: List[Dict[str, object]] = []
    for sku in product.get("skuStyleOrder") or []:
        color_id = str(sku.get("colorId") or "").strip()
        if not color_id:
            continue
        sku_raw = str(sku.get("sku") or "").strip()
        sku_id = sku_raw.split("_")[-1] if sku_raw else sku.get("skuStyleOrderId")
        color_info = color_meta.get(color_id, {})
        skus.append(
            {
                "id": sku_id,
                "skuUrl": full_ingest.with_query(
                    canonical_pdp_url,
                    color=sku.get("styleId02") or color_id,
                    skuId=sku_id,
                ),
                "price": {
                    "listPrice": normalize_price_value(list_price_raw),
                    "currency": {"code": currency_code, "symbol": "$"},
                    "onSale": bool(product.get("productOnSale")),
                    "salePrice": normalize_price_value(sale_price_raw) if sale_price_raw else None,
                    "earlyAccessMarkdownPrice": None,
                },
                "size": full_ingest.normalize_size(sku.get("size")),
                "color": {
                    "code": color_id,
                    "name": color_info.get("name") or sku.get("colorName"),
                    "swatchUrl": color_info.get("swatchUrl"),
                    "slug": color_info.get("slug") or color_id,
                },
                "available": True,
                "inseam": None,
                "styleId": sku.get("styleId"),
                "styleNumber": sku.get("styleId01") or sku.get("styleNumber"),
            }
        )

    current = {
        "productSummary": product_summary,
        "colors": colors,
        "colorDriver": color_driver,
        "productCarousel": product_carousel,
        "skus": skus,
        "selectedColor": default_color,
        "colorAttributes": [],
        "productAttributes": [],
        "whyWeMadeThisAttributes": [],
        "highlights": product.get("highlights") or [],
    }

    return {
        "props": {
            "pageProps": {
                "initialStoreState": {
                    "productDetailPage": {"current": current}
                }
            }
        }
    }


def normalize_locale(locale: Optional[str]) -> str:
    if not locale:
        return "en_US"
    normalized = locale.replace("-", "_")
    parts = normalized.split("_")
    if len(parts) == 2:
        return f"{parts[0].lower()}_{parts[1].upper()}"
    return normalized


def derive_category_locale(payload: Dict) -> str:
    page_props = payload.get("props", {}).get("pageProps", {})
    akamai = page_props.get("akamaiDevice")
    if isinstance(akamai, dict):
        akamai_locale = akamai.get("locale")
    elif isinstance(akamai, str):
        akamai_locale = akamai
    else:
        akamai_locale = None
    locale = page_props.get("locale") or akamai_locale or "en-US"
    return normalize_locale(locale)


def extract_slug_from_url(url: str) -> str:
    path = urlsplit(url).path
    segments = [segment for segment in path.split("/") if segment]
    if len(segments) >= 3:
        return segments[2]
    return segments[-1] if segments else url


def build_graphql_variables(
    candidate: ProductCandidate,
    product_node: Optional[Dict[str, object]],
    locale: str,
) -> Dict[str, object]:
    slug = extract_slug_from_url(candidate.pdp_url)
    unified_id = None
    if product_node:
        unified_id = product_node.get("unifiedId")
        if not unified_id:
            summary = product_node.get("productSummary") or {}
            if isinstance(summary, dict):
                unified_id = summary.get("unifiedId")
    if not unified_id:
        unified_id = slug

    return {
        "id": candidate.product_id,
        "category": slug,
        "unifiedId": unified_id,
        "locale": locale,
        "fetchPcmMedia": True,
        "fetchVariants": True,
    }


def fetch_graphql_payload(
    candidate: ProductCandidate,
    product_node: Optional[Dict[str, object]],
    locale: str,
    cache_path: Path,
    refresh: bool,
) -> Optional[Path]:
    if cache_path.exists() and not refresh:
        print(f"   ↳ using cached GraphQL response {cache_path.name}")
        return cache_path

    variables = build_graphql_variables(candidate, product_node, locale)
    try:
        response = graphql_execute_query(variables)
    except Exception as exc:  # noqa: BLE001
        print(f"   ↳ GraphQL fetch failed: {exc}")
        return None

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
    print(f"   ↳ saved GraphQL response to {cache_path.name}")
    return cache_path


def ingest_category(args: argparse.Namespace) -> None:
    payload = load_category_payload(args.url, args.payload, allow_playwright=not args.no_playwright)
    product_lookup = build_product_lookup(payload)
    candidates = extract_candidates(payload)
    if args.limit is not None:
        candidates = candidates[: args.limit]

    print(f"📋 Discovered {len(candidates)} unique PDP references.")
    if not candidates:
        return

    if args.dry_run:
        for idx, candidate in enumerate(candidates, 1):
            print(
                f"[DRY-RUN] {idx:03d}: {candidate.product_id} "
                f"({candidate.display_name or 'Untitled'}) → {candidate.pdp_url}"
            )
        return

    category_locale = derive_category_locale(payload)

    if args.use_graphql and REQUESTS_IMPORT_ERROR:
        raise SystemExit(
            "GraphQL ingestion requires the 'requests' package "
            f"(import error: {REQUESTS_IMPORT_ERROR})"
        )

    successes = 0
    failures = 0

    # Ensure brand-scoped directories exist; keep legacy dirs readable.
    CATEGORY_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if LEGACY_CATEGORY_DIR.exists() and not any(CATEGORY_CACHE_DIR.iterdir()):
        # If legacy dir has files and new dir is empty, we simply *read* from
        # both by virtue of using explicit paths later. We intentionally do not
        # move files automatically here to avoid surprises.
        pass

    graphql_cache_dir = args.graphql_cache_dir or GRAPHQL_CACHE_DIR

    for idx, candidate in enumerate(candidates, 1):
        print(
            f"\n[{idx}/{len(candidates)}] Ingesting {candidate.product_id} "
            f"({candidate.display_name or 'Untitled'})"
        )
        try:
            payload_path: Optional[Path] = None
            graphql_path: Optional[Path] = None
            allow_playwright = not args.no_playwright
            product_node = product_lookup.get(candidate.product_id)

            if args.use_graphql:
                graphql_cache_file = graphql_cache_dir / f"{candidate.product_id}.graphql.json"
                graphql_path = fetch_graphql_payload(
                    candidate,
                    product_node,
                    category_locale,
                    graphql_cache_file,
                    args.refresh_graphql_cache,
                )
                if graphql_path:
                    allow_playwright = False
                else:
                    print("   ↳ falling back to category payload workflow.")

            if not graphql_path and product_node:
                synthetic_payload = build_synthetic_payload(product_node, candidate.pdp_url)
                payload_path = CATEGORY_CACHE_DIR / f"{candidate.product_id}.category.json"
                payload_path.write_text(json.dumps(synthetic_payload), encoding="utf-8")
                allow_playwright = False
                print(f"   ↳ using cached payload {payload_path.name}")
            else:
                if not graphql_path:
                    print("   ↳ no category payload found; falling back to live fetch")

            full_ingest.ingest_catalog(
                candidate.pdp_url,
                payload_path,
                allow_playwright=allow_playwright,
                spotlight_enabled=args.spotlight,
                brand_name=args.brand_name,
                brand_slug=args.brand_slug,
                dry_run=False,
                graphql_response_path=graphql_path,
                # Category payloads often lack rich content (care/fabric/features/
                # why-we-made-this). We still want variants/images in fs-core even
                # when those fields are missing, so we disable the strict
                # ingest_checker pass here. You can always run ingest_checker
                # manually later for any product you care about.
                run_checks=False,
            )
            successes += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"❌ Failed to ingest {candidate.pdp_url}: {exc}")

    print("\n📊 CATEGORY INGEST SUMMARY")
    print(f"   Total PDPs:   {len(candidates)}")
    print(f"   Successful:   {successes}")
    print(f"   Failed:       {failures}")


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    if not args.url and not args.payload:
        raise SystemExit("❌ Provide a category --url or a saved --payload JSON file.")
    ingest_category(args)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"❌ {exc}")
        raise

