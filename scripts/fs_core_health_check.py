#!/usr/bin/env python3
"""
Broad fs-core health check / data quality auditor.

This is meant to act as a lightweight DBA / data engineer for you:
it runs a battery of checks across the core tables and surfaces
rows that look suspicious or incomplete.

It focuses on:
  - Referential integrity across core.* tables (orphan rows, missing links)
  - Products without variants / sizes / images / URLs
  - Duplicated identifiers
  - Missing specs / marketing content at scale
  - ingest_runs that don't line up cleanly with products

Usage examples:

    # Global snapshot (all brands)
    python scripts/fs_core_health_check.py

    # Focus on one brand
    python scripts/fs_core_health_check.py --brand-slug lululemon

    # JSON output (for machines / logging)
    python scripts/fs_core_health_check.py --brand-slug lululemon --output-json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Sequence

from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DB_CONFIG  # noqa: E402


@dataclass
class CheckReport:
    name: str
    description: str
    issue_count: int
    sample_rows: List[Dict[str, Any]]


@dataclass
class HealthSummary:
    brand_slug: Optional[str]
    checks: List[CheckReport]


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


def make_where_brand_clause(brand_slug: Optional[str]) -> str:
    if brand_slug:
        return "WHERE b.slug = %(brand_slug)s"
    return ""


def run_check(
    cur,
    name: str,
    description: str,
    sql: str,
    params: Dict[str, Any],
    sample_limit: int = 50,
) -> CheckReport:
    """
    Execute a check query that returns rows representing problems.
    The total issue_count is computed separately to avoid LIMIT bias.
    """
    # Count total
    count_sql = f"SELECT COUNT(*) AS cnt FROM ({sql}) AS sub"
    cur.execute(count_sql, params)
    row = cur.fetchone()
    issue_count = int(row["cnt"]) if isinstance(row, dict) else int(row[0])

    # Fetch sample rows
    sample_sql = f"{sql} LIMIT {sample_limit}"
    cur.execute(sample_sql, params)
    columns = [desc[0] for desc in cur.description]
    sample_rows = [dict(zip(columns, r)) for r in cur.fetchall()]

    return CheckReport(
        name=name,
        description=description,
        issue_count=issue_count,
        sample_rows=sample_rows,
    )


def collect_checks(conn, brand_slug: Optional[str]) -> HealthSummary:
    params: Dict[str, Any] = {}
    if brand_slug:
        params["brand_slug"] = brand_slug

    checks: List[CheckReport] = []

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # 1) Duplicate product_codes
        where_brand = make_where_brand_clause(brand_slug)
        sql = f"""
            SELECT p.product_code,
                   COUNT(*) AS dup_count
              FROM core.products p
              JOIN core.brands b ON b.id = p.brand_id
              {where_brand}
             GROUP BY p.product_code
            HAVING COUNT(*) > 1
             ORDER BY dup_count DESC, p.product_code
        """
        checks.append(
            run_check(
                cur,
                name="duplicate_product_codes",
                description="Products sharing the same product_code (should generally be unique).",
                sql=sql,
                params=params,
            )
        )

        # 2) Products without variants
        sql = f"""
            SELECT p.id, p.product_code, p.title
              FROM core.products p
              JOIN core.brands b ON b.id = p.brand_id
         LEFT JOIN core.product_variants v ON v.product_id = p.id
             {where_brand}
             AND v.id IS NULL
             ORDER BY p.id
        """
        checks.append(
            run_check(
                cur,
                name="products_without_variants",
                description="Products that have no product_variants rows linked.",
                sql=sql,
                params=params,
            )
        )

        # 3) Orphan variants (product_id not in products)
        sql = """
            SELECT v.id, v.product_id
              FROM core.product_variants v
         LEFT JOIN core.products p ON p.id = v.product_id
             WHERE p.id IS NULL
             ORDER BY v.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_variants",
                description="product_variants rows whose product_id does not point to a core.products row.",
                sql=sql,
                params=params,
            )
        )

        # 4) Variants without sizes / hero images / URLs (similar to ingest_checker, but across many products)
        sql = f"""
            SELECT pv.id,
                   pv.product_id,
                   pv.color_name,
                   COALESCE(vs.size_count, 0) AS size_count,
                   COALESCE(pi.hero_count, 0) AS hero_count,
                   COALESCE(pu.url_count, 0) AS url_count
              FROM core.product_variants pv
              JOIN core.products p ON p.id = pv.product_id
              JOIN core.brands b ON b.id = p.brand_id
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
             {where_brand}
             AND (
                 COALESCE(vs.size_count, 0) = 0
                 OR COALESCE(pi.hero_count, 0) = 0
                 OR COALESCE(pu.url_count, 0) = 0
             )
             ORDER BY pv.product_id, pv.id
        """
        checks.append(
            run_check(
                cur,
                name="variants_missing_sizes_images_or_urls",
                description="Variants that lack sizes, hero images, or product_urls.",
                sql=sql,
                params=params,
            )
        )

        # 5) Orphan size rows
        sql = """
            SELECT vs.id, vs.variant_id
              FROM core.variant_sizes vs
         LEFT JOIN core.product_variants v ON v.id = vs.variant_id
             WHERE v.id IS NULL
             ORDER BY vs.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_variant_sizes",
                description="variant_sizes rows whose variant_id does not point to a product_variants row.",
                sql=sql,
                params=params,
            )
        )

        # 6) Orphan product_images
        sql = """
            SELECT i.id, i.variant_id, i.url
              FROM core.product_images i
         LEFT JOIN core.product_variants v ON v.id = i.variant_id
             WHERE v.id IS NULL
             ORDER BY i.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_product_images",
                description="product_images rows whose variant_id does not point to a product_variants row.",
                sql=sql,
                params=params,
            )
        )

        # 7) Orphan product_urls
        sql = """
            SELECT u.id, u.variant_id, u.url
              FROM core.product_urls u
         LEFT JOIN core.product_variants v ON v.id = u.variant_id
             WHERE v.id IS NULL
             ORDER BY u.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_product_urls",
                description="product_urls rows whose variant_id does not point to a product_variants row.",
                sql=sql,
                params=params,
            )
        )

        # 8) Orphan specs / content (product_id not in products)
        sql = """
            SELECT s.id, s.product_id, s.spec_key
              FROM core.product_specs s
         LEFT JOIN core.products p ON p.id = s.product_id
             WHERE p.id IS NULL
             ORDER BY s.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_product_specs",
                description="product_specs rows whose product_id does not point to a core.products row.",
                sql=sql,
                params=params,
            )
        )

        sql = """
            SELECT c.id, c.product_id, c.content_type
              FROM core.product_content c
         LEFT JOIN core.products p ON p.id = c.product_id
             WHERE p.id IS NULL
             ORDER BY c.id
        """
        checks.append(
            run_check(
                cur,
                name="orphan_product_content",
                description="product_content rows whose product_id does not point to a core.products row.",
                sql=sql,
                params=params,
            )
        )

        # 9) Products missing key specs / marketing_story (for brand or globally)
        sql = f"""
            SELECT p.id,
                   p.product_code,
                   p.title,
                   COALESCE(sp.care_specs, 0) AS care_specs,
                   COALESCE(sp.fabric_specs, 0) AS fabric_specs,
                   COALESCE(sp.feature_specs, 0) AS feature_specs,
                   COALESCE(ct.marketing_stories, 0) AS marketing_stories
              FROM core.products p
              JOIN core.brands b ON b.id = p.brand_id
         LEFT JOIN (
                   SELECT product_id,
                          COUNT(*) FILTER (WHERE spec_key = 'care') AS care_specs,
                          COUNT(*) FILTER (WHERE spec_key = 'fabric') AS fabric_specs,
                          COUNT(*) FILTER (WHERE spec_key = 'features') AS feature_specs
                     FROM core.product_specs
                    GROUP BY product_id
          ) sp ON sp.product_id = p.id
         LEFT JOIN (
                   SELECT product_id,
                          COUNT(*) FILTER (WHERE content_type = 'marketing_story') AS marketing_stories
                     FROM core.product_content
                    GROUP BY product_id
          ) ct ON ct.product_id = p.id
             {where_brand}
             AND (
                 COALESCE(sp.care_specs, 0) = 0
                 OR COALESCE(sp.fabric_specs, 0) = 0
                 OR COALESCE(sp.feature_specs, 0) = 0
                 OR COALESCE(ct.marketing_stories, 0) = 0
             )
             ORDER BY p.id
        """
        checks.append(
            run_check(
                cur,
                name="products_missing_specs_or_marketing_story",
                description="Products missing one or more of care/fabric/features specs or a marketing_story.",
                sql=sql,
                params=params,
            )
        )

        # 10) ingest_runs without a matching product or with non-success status
        sql = """
            SELECT r.id,
                   r.product_id,
                   r.source,
                   r.status,
                   r.input_url
              FROM ops.ingest_runs r
         LEFT JOIN core.products p ON p.id = r.product_id
             WHERE p.id IS NULL
                OR r.status <> 'success'
             ORDER BY r.id DESC
        """
        checks.append(
            run_check(
                cur,
                name="problematic_ingest_runs",
                description="ingest_runs rows with no matching product_id or non-success status.",
                sql=sql,
                params=params,
            )
        )

    return HealthSummary(brand_slug=brand_slug, checks=checks)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run broad fs-core health checks across core tables."
    )
    parser.add_argument(
        "--brand-slug",
        help="Optional brand slug (e.g. 'lululemon') to scope checks.",
    )
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Emit JSON instead of human-readable text.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    with connect() as conn:
        summary = collect_checks(conn, args.brand_slug)

    if args.output_json:
        print(
            json.dumps(
                {
                    "brand_slug": summary.brand_slug,
                    "checks": [
                        {
                            "name": c.name,
                            "description": c.description,
                            "issue_count": c.issue_count,
                            "sample_rows": c.sample_rows,
                        }
                        for c in summary.checks
                    ],
                },
                indent=2,
            )
        )
        return

    scope = summary.brand_slug or "(all brands)"
    print(f"fs-core health check for {scope}")
    print("=" * 60)
    for check in summary.checks:
        print(f"\n[{check.name}]")
        print(f"  {check.description}")
        print(f"  Issues found: {check.issue_count}")
        if not check.sample_rows:
            continue
        print("  Sample rows:")
        for row in check.sample_rows[:10]:
            print(f"    - {json.dumps(row, default=str)}")


if __name__ == "__main__":
    main()



