#!/usr/bin/env python3
"""
Quick integrity checker for recently ingested products.

Usage examples:

    python scripts/ingest_checker.py --product-code SU538118
    python scripts/ingest_checker.py --latest-runs 5 --brand reiss

The checker verifies that:
  * The product exists and belongs to the expected brand.
  * Variants exist and each has size rows, hero imagery, and URLs.
  * Product-level marketing/spec content is present.
  * An ops.ingest_runs record exists for the most recent ingest.

It surfaces any gaps so we can immediately fix the ingest before handing
off data downstream.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Sequence

import sys
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DB_CONFIG  # noqa: E402


@dataclass
class ProductSummary:
    product_id: int
    product_code: str
    brand_slug: str
    title: str
    category: Optional[str]
    base_name: Optional[str]
    raw_present: bool


@dataclass
class CheckResult:
    product: ProductSummary
    variants: List[Dict]
    content: Dict[str, int]
    specs: Dict[str, int]
    ingest_run: Optional[Dict]
    issues: List[str]


def ensure_db_config() -> None:
    missing = [k for k, v in DB_CONFIG.items() if not v]
    if missing:
        raise SystemExit(
            f"Missing database configuration for: {', '.join(missing)}. "
            "Set DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT in .env"
        )


def connect():
    ensure_db_config()
    return psycopg2.connect(
        dbname=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )


def fetch_product(cur, product_code: str) -> ProductSummary:
    cur.execute(
        """
        SELECT p.id,
               p.product_code,
               b.slug AS brand_slug,
               p.title,
               p.category,
               p.base_name,
               p.raw IS NOT NULL AS has_raw
          FROM core.products p
          JOIN core.brands b ON p.brand_id = b.id
         WHERE p.product_code = %s
        """,
        (product_code,),
    )
    row = cur.fetchone()
    if not row:
        raise SystemExit(f"❌ No product found with code {product_code}.")

    return ProductSummary(
        product_id=row[0],
        product_code=row[1],
        brand_slug=row[2],
        title=row[3],
        category=row[4],
        base_name=row[5],
        raw_present=row[6],
    )


def fetch_variants(cur, product_id: int) -> List[Dict]:
    cur.execute(
        """
        SELECT pv.id,
               pv.color_name,
               pv.fit_name,
               pv.variant_url,
               pv.attrs,
               COALESCE(vs.size_count, 0) AS size_count,
               COALESCE(pi.hero_count, 0) AS hero_count,
               COALESCE(pu.url_count, 0) AS url_count
          FROM core.product_variants pv
          LEFT JOIN (
                SELECT variant_id, COUNT(*) AS size_count
                  FROM core.variant_sizes
                 GROUP BY variant_id
          ) vs ON vs.variant_id = pv.id
          LEFT JOIN (
                SELECT variant_id, COUNT(*) AS hero_count
                  FROM core.product_images
                 WHERE metadata->>'kind' = 'hero'
                 GROUP BY variant_id
          ) pi ON pi.variant_id = pv.id
          LEFT JOIN (
                SELECT variant_id, COUNT(*) AS url_count
                  FROM core.product_urls
                 GROUP BY variant_id
          ) pu ON pu.variant_id = pv.id
         WHERE pv.product_id = %s
         ORDER BY pv.id
        """,
        (product_id,),
    )
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def fetch_product_content(cur, product_id: int) -> Dict[str, int]:
    cur.execute(
        """
        SELECT content_type, COUNT(*)
          FROM core.product_content
         WHERE product_id = %s
         GROUP BY content_type
        """,
        (product_id,),
    )
    return {row[0]: row[1] for row in cur.fetchall()}


def fetch_specs(cur, product_id: int) -> Dict[str, int]:
    cur.execute(
        """
        SELECT spec_key, COUNT(*)
          FROM core.product_specs
         WHERE product_id = %s
         GROUP BY spec_key
        """,
        (product_id,),
    )
    return {row[0]: row[1] for row in cur.fetchall()}


def fetch_latest_ingest_run(cur, product_id: int, product_code: str) -> Optional[Dict]:
    cur.execute(
        """
        SELECT id, source, status, rows_inserted, finished_at
          FROM ops.ingest_runs
         WHERE product_id = %s OR input_url ILIKE %s
         ORDER BY finished_at DESC NULLS LAST, id DESC
         LIMIT 1
        """,
        (product_id, f"%{product_code}%"),
    )
    row = cur.fetchone()
    if not row:
        return None
    if isinstance(row, dict):
        finished = row.get("finished_at")
        return {
            "id": row.get("id"),
            "source": row.get("source"),
            "status": row.get("status"),
            "rows_inserted": row.get("rows_inserted"),
            "finished_at": finished.isoformat() if isinstance(finished, datetime) else finished,
        }
    finished = row[4]
    return {
        "id": row[0],
        "source": row[1],
        "status": row[2],
        "rows_inserted": row[3],
        "finished_at": finished.isoformat() if isinstance(finished, datetime) else finished,
    }


def fetch_recent_product_codes(
    conn,
    limit: int,
    brand_slug: Optional[str],
) -> List[str]:
    if limit <= 0:
        return []
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.product_code
              FROM ops.ingest_runs r
              JOIN core.products p ON p.id = r.product_id
              JOIN core.brands b ON b.id = p.brand_id
             WHERE r.status = 'success'
               AND (%s IS NULL OR b.slug = %s)
             ORDER BY COALESCE(r.finished_at, r.created_at) DESC,
                      r.id DESC
             LIMIT %s
            """,
            (brand_slug, brand_slug, limit),
        )
        seen = set()
        product_codes: List[str] = []
        for (code,) in cur.fetchall():
            if code and code not in seen:
                seen.add(code)
                product_codes.append(code)
        return product_codes


def evaluate(
    product: ProductSummary,
    variants: List[Dict],
    content: Dict[str, int],
    specs: Dict[str, int],
    ingest_run: Optional[Dict],
) -> List[str]:
    issues: List[str] = []

    if not product.raw_present:
        issues.append("Product.raw payload missing.")
    if not product.base_name:
        issues.append("base_name is NULL; preferred for storefront naming.")
    if not variants:
        issues.append("No product_variants rows found.")

    for variant in variants:
        label = f"Variant {variant['id']} ({variant['color_name'] or 'unknown color'})"
        if variant["size_count"] == 0:
            issues.append(f"{label} has 0 size entries.")
        if variant["hero_count"] == 0:
            issues.append(f"{label} has no hero images.")
        if variant["url_count"] == 0:
            issues.append(f"{label} missing product_urls entries.")
        attrs = variant.get("attrs") or {}
        if not isinstance(attrs, dict):
            try:
                attrs = json.loads(attrs)
            except Exception:  # noqa: BLE001
                attrs = {}
        if not attrs.get("item_number") and not attrs.get("style_id"):
            issues.append(f"{label} attrs missing item/style identifiers.")

    required_specs = {
        "care": "care instructions",
        "fabric": "fabric composition",
        "features": "features/benefits",
    }
    for key, desc in required_specs.items():
        if specs.get(key, 0) == 0:
            issues.append(f"No product_specs rows for '{key}' ({desc}).")

    if content.get("marketing_story", 0) == 0:
        issues.append("No marketing_story content row found.")

    if not ingest_run:
        issues.append("No ops.ingest_runs entry located for this product.")
    elif ingest_run["status"] != "success":
        issues.append(
            f"Latest ingest_run ({ingest_run['id']}) not successful (status={ingest_run['status']})."
        )

    return issues


def pretty_print(result: CheckResult) -> None:
    product = result.product
    variants = result.variants
    content = result.content
    specs = result.specs
    ingest_run = result.ingest_run
    issues = result.issues
    summary = {
        "product_id": product.product_id,
        "product_code": product.product_code,
        "brand": product.brand_slug,
        "title": product.title,
        "category": product.category,
        "base_name": product.base_name,
        "variant_count": len(variants),
    }
    print(json.dumps(summary, indent=2))

    print("\nVariant overview:")
    for variant in variants:
        print(
            f"  • #{variant['id']} color={variant['color_name'] or '-'} fit={variant['fit_name'] or '-'} "
            f"sizes={variant['size_count']} hero_imgs={variant['hero_count']} urls={variant['url_count']}"
        )

    print("\nSpecs summary:")
    for key, count in specs.items():
        print(f"  - {key}: {count} rows")

    print("\nContent summary:")
    for key, count in content.items():
        print(f"  - {key}: {count} rows")

    print("\nLatest ingest run:")
    if ingest_run:
        print(json.dumps(ingest_run, indent=2))
    else:
        print("  (none)")

    if issues:
        print("\n⚠️  Issues detected:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n✅ No issues detected.")


def run_checks_for_product(conn, product_code: str) -> CheckResult:
    with conn.cursor() as cur:
        product = fetch_product(cur, product_code)
        variants = fetch_variants(cur, product.product_id)
        specs = fetch_specs(cur, product.product_id)
        content = fetch_product_content(cur, product.product_id)
    with conn.cursor(cursor_factory=RealDictCursor) as cur2:
        ingest_run = fetch_latest_ingest_run(cur2, product.product_id, product.product_code)
    issues = evaluate(product, variants, content, specs, ingest_run)
    return CheckResult(
        product=product,
        variants=variants,
        content=content,
        specs=specs,
        ingest_run=ingest_run,
        issues=issues,
    )


def run_checks(product_code: str) -> CheckResult:
    with connect() as conn:
        return run_checks_for_product(conn, product_code)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify ingest completeness for products.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--product-code",
        help="Product code (e.g. SU538118, prod6750191, etc.)",
    )
    group.add_argument(
        "--latest-runs",
        type=int,
        help="Validate the last N successful ingest runs (optionally filtered by brand).",
    )
    parser.add_argument(
        "--brand",
        help="Brand slug filter to pair with --latest-runs.",
    )
    args = parser.parse_args(argv)
    if args.brand and not args.latest_runs:
        parser.error("--brand can only be used together with --latest-runs")
    return args


def resolve_product_codes(conn, args: argparse.Namespace) -> List[str]:
    if args.latest_runs:
        return fetch_recent_product_codes(conn, args.latest_runs, args.brand)
    return [args.product_code]


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    with connect() as conn:
        product_codes = resolve_product_codes(conn, args)
        if not product_codes:
            print("No ingest runs matched the provided filters.")
            return
        multi = len(product_codes) > 1
        any_issues = False
        for idx, code in enumerate(product_codes, 1):
            if multi:
                print(f"\n=== [{idx}/{len(product_codes)}] Validating {code} ===")
            result = run_checks_for_product(conn, code)
            pretty_print(result)
            if result.issues:
                any_issues = True
        if any_issues:
            sys.exit(1)


if __name__ == "__main__":
    main()

