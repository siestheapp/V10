#!/usr/bin/env python3
"""
End-to-end J.Crew PDP ingestion.

Given a PDP URL, this script:
  1. Normalizes the URL (handles /m/ mobile paths & colorProductCode)
  2. Ensures the brand + product records exist in fs-core
  3. Creates/updates product variants, URLs, swatches, size ladders, and hero images
  4. Sets spotlight mode (ops.ingestion_targets)
  5. Reuses the spotlight ingest logic to capture specs, badges, fit guidance, and review data

Usage:
    source venv/bin/activate
    python scripts/jcrew_full_ingest.py --url "<J.Crew PDP>" [--no-spotlight] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import urlencode

import psycopg2
from psycopg2.extras import Json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from db_config import DB_CONFIG  # noqa: E402
import ingest_checker  # noqa: E402
import jcrew_spotlight_ingest as spotlight  # noqa: E402

DEFAULT_BRAND_NAME = "J.Crew"
DEFAULT_BRAND_SLUG = "jcrew"
DEFAULT_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]
DEFAULT_HERO_TEMPLATE = (
    "https://www.jcrew.com/s7-img-facade/{product_code}_{color_code}?$pdp_enlarge$"
)
SIZE_ALIAS_MAP = {
    "XX-SMALL": "XXS",
    "X-SMALL": "XS",
    "SMALL": "S",
    "MEDIUM": "M",
    "MED": "M",
    "LARGE": "L",
    "X-LARGE": "XL",
    "XX-LARGE": "XXL",
    "TALL SIZE MEDIUM": "M-T",
    "TALL MEDIUM": "M-T",
    "TALL LARGE": "L-T",
    "TALL SIZE LARGE": "L-T",
    "X LARGE-TALL": "XL-T",
    "TALL X-LARGE": "XL-T",
    "XX-LARGE-TALL": "XXL-T",
    "TALL XX-LARGE": "XXL-T",
}
SIZE_ORDER = {
    "XXS": 5,
    "XS": 10,
    "S": 20,
    "M": 30,
    "L": 40,
    "XL": 50,
    "XXL": 60,
    "XXXL": 70,
    "XS-T": 80,
    "S-T": 90,
    "M-T": 100,
    "L-T": 110,
    "XL-T": 120,
    "XXL-T": 130,
}


@dataclass
class VariantRecord:
    color_name: str
    color_code: str
    color_product_code: str
    fit_label: Optional[str]
    variant_url: str
    swatch_url: str
    hero_url: Optional[str]
    size_labels: List[str]
    attrs: Dict[str, object]
    is_primary: bool = False


def ensure_brand(cur, slug: str, name: str) -> int:
    cur.execute("SELECT id FROM core.brands WHERE slug = %s", (slug,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute(
        "INSERT INTO core.brands (name, slug, aliases) VALUES (%s,%s,%s) RETURNING id",
        (name, slug, []),
    )
    return cur.fetchone()[0]


def ensure_product(
    cur,
    brand_id: int,
    product_code: str,
    title: str,
    category: str,
    raw_payload: Dict[str, object],
    gender: str,
) -> int:
    cur.execute(
        "SELECT id FROM core.products WHERE product_code = %s",
        (product_code,),
    )
    row = cur.fetchone()
    if row:
        product_id = row[0]
        cur.execute(
            """
            UPDATE core.products
               SET brand_id = %s,
                   title = %s,
                   category = %s,
                   raw = %s,
                   gender = %s
             WHERE id = %s
            """,
            (brand_id, title, category, Json(raw_payload), gender, product_id),
        )
        return product_id

    cur.execute(
        """
        INSERT INTO core.products (brand_id, product_code, title, category, raw, gender)
        VALUES (%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (brand_id, product_code, title, category, Json(raw_payload), gender),
    )
    return cur.fetchone()[0]


def assign_canonical_category(
    cur,
    product_id: int,
    brand_id: int,
    source_category: Optional[str],
) -> None:
    if not source_category:
        return
    cur.execute(
        """
        SELECT category_id, subcategory_id
          FROM core.brand_category_map
         WHERE brand_id = %s
           AND LOWER(source_category) = LOWER(%s)
        """,
        (brand_id, source_category),
    )
    row = cur.fetchone()
    if not row:
        return
    category_id, subcategory_id = row
    cur.execute(
        """
        INSERT INTO core.product_categories (product_id, category_id, subcategory_id)
        VALUES (%s,%s,%s)
        ON CONFLICT (product_id, category_id) DO NOTHING
        """,
        (product_id, category_id, subcategory_id),
    )
    if subcategory_id:
        cur.execute(
            """
            UPDATE core.product_categories
               SET subcategory_id = %s
             WHERE product_id = %s
               AND category_id = %s
            """,
            (subcategory_id, product_id, category_id),
        )


def upsert_product_url(
    cur,
    product_id: int,
    url: str,
    region: str = "US",
    variant_id: Optional[int] = None,
) -> None:
    cur.execute(
        """
        SELECT id, variant_id
          FROM core.product_urls
         WHERE product_id = %s
           AND url = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (product_id, url),
    )
    row = cur.fetchone()
    if row:
        existing_id, existing_variant = row
        if variant_id and not existing_variant:
            cur.execute(
                """
                UPDATE core.product_urls
                   SET variant_id = %s,
                       region = %s,
                       is_current = true
                 WHERE id = %s
                """,
                (variant_id, region, existing_id),
            )
        else:
            cur.execute(
                "UPDATE core.product_urls SET is_current = true WHERE id = %s",
                (existing_id,),
            )
        return
    cur.execute(
        """
        INSERT INTO core.product_urls (product_id, variant_id, region, url, is_current)
        VALUES (%s, %s, %s, %s, true)
        """,
        (product_id, variant_id, region, url),
    )


def upsert_ingestion_target(cur, product_id: int, spotlight_enabled: bool, note: str) -> None:
    cur.execute(
        """
        INSERT INTO ops.ingestion_targets (product_id, spotlight, notes)
        VALUES (%s,%s,%s)
        ON CONFLICT (product_id)
        DO UPDATE SET spotlight = EXCLUDED.spotlight,
                      notes = EXCLUDED.notes,
                      updated_at = now()
        """,
        (product_id, spotlight_enabled, note),
    )


def normalize_text(value: str) -> str:
    return " ".join(value.strip().split())


def prettify_color_name(value: str) -> str:
    cleaned = normalize_text(value)
    if not cleaned:
        return cleaned
    return cleaned.title()


def size_label_from_entry(entry: str) -> str:
    upper = normalize_text(entry).upper()
    return SIZE_ALIAS_MAP.get(upper, upper.replace(" ", "-"))


def size_sort_key(label: str, fallback_index: int) -> int:
    return SIZE_ORDER.get(label, 200 + fallback_index * 5)


def build_variant_records(
    product: Dict[str, object],
    canonical_url: str,
) -> List[VariantRecord]:
    colors = OrderedDict()
    for group in product.get("colorsList", []):
        for color in group.get("colors", []):
            code = color.get("code")
            if not code:
                continue
            if code in colors:
                continue
            colors[code] = {
                "name": prettify_color_name(color.get("name", "")),
                "product_code": color.get("productCode") or product.get("productCode"),
                "model_height": color.get("modelHeight"),
                "model_size": color.get("modelSize"),
            }
    if not colors:
        for code in product.get("colorsMap", {}):
            colors[code] = {
                "name": code,
                "product_code": product.get("productCode"),
                "model_height": None,
                "model_size": None,
            }

    fits = [
        normalize_text(variant["label"])
        for variant in product.get("variations", [])
        if variant.get("label")
    ]
    if not fits:
        fits = ["Classic"]

    color_sizes_map = product.get("colorSizesMap") or {}
    default_sizes = [
        size_label_from_entry(label)
        for label in product.get("sizesList") or DEFAULT_SIZES
    ]
    if not default_sizes:
        default_sizes = DEFAULT_SIZES

    default_color_code = product.get("defaultColorCode") or next(iter(colors.keys()), None)

    variant_records: List[VariantRecord] = []
    for color_index, (color_code, color_meta) in enumerate(colors.items()):
        size_entries = color_sizes_map.get(color_code) or default_sizes
        size_labels = []
        for idx, entry in enumerate(size_entries):
            label = size_label_from_entry(entry)
            if label not in size_labels:
                size_labels.append(label)
        if not size_labels:
            size_labels = default_sizes

        swatch_url = f"https://www.jcrew.com/s7-img-facade/{color_meta['product_code']}_{color_code}_sw?$pdp_sw20$"
        hero_url = DEFAULT_HERO_TEMPLATE.format(
            product_code=color_meta["product_code"],
            color_code=color_code,
        )

        for fit_index, fit_label in enumerate(fits):
            fit_value = fit_label if fit_label.lower() != "default" else None
            query_params = {
                "color_code": color_code,
                "color_name": spotlight.slugify(color_meta["name"]),
            }
            if fit_value:
                query_params["fit"] = spotlight.slugify(fit_value)
            delimiter = "&" if "?" in canonical_url else "?"
            variant_url = f"{canonical_url}{delimiter}{urlencode(query_params)}"
            attrs = {
                "color_code": color_code,
                "color_name": color_meta["name"],
                "fit_name": fit_value,
                "swatch_url": swatch_url,
                "model_height": color_meta.get("model_height"),
                "model_size": color_meta.get("model_size"),
            }
            variant_records.append(
                VariantRecord(
                    color_name=color_meta["name"],
                    color_code=color_code,
                    color_product_code=color_meta["product_code"],
                    fit_label=fit_value,
                    variant_url=variant_url,
                    swatch_url=swatch_url,
                    hero_url=hero_url,
                    size_labels=size_labels,
                    attrs=attrs,
                    is_primary=bool(
                        color_code == default_color_code and fit_index == 0 and color_index == 0
                    ),
                )
            )
    if variant_records and not any(rec.is_primary for rec in variant_records):
        variant_records[0].is_primary = True
    return variant_records


def upsert_variant(
    cur,
    product_id: int,
    record: VariantRecord,
) -> int:
    cur.execute(
        """
        SELECT id FROM core.product_variants
         WHERE product_id = %s
           AND COALESCE(color_name, '') = %s
           AND COALESCE(fit_name, '') = %s
        """,
        (product_id, record.color_name, record.fit_label or ""),
    )
    row = cur.fetchone()
    variant_sku = f"{record.color_product_code.lower()}-{spotlight.slugify(record.color_name)}-{spotlight.slugify(record.fit_label or 'default')}"
    if row:
        variant_id = row[0]
        cur.execute(
            """
            UPDATE core.product_variants
               SET variant_url = %s,
                   variant_sku = %s,
                   attrs = %s
             WHERE id = %s
            """,
            (record.variant_url, variant_sku, Json(record.attrs), variant_id),
        )
    else:
        cur.execute(
            """
            INSERT INTO core.product_variants
                (product_id, color_name, fit_name, variant_url, variant_sku, attrs)
            VALUES (%s,%s,%s,%s,%s,%s)
            RETURNING id
            """,
            (
                product_id,
                record.color_name,
                record.fit_label,
                record.variant_url,
                variant_sku,
                Json(record.attrs),
            ),
        )
        variant_id = cur.fetchone()[0]
    return variant_id


def replace_variant_sizes(cur, variant_id: int, labels: Sequence[str]) -> None:
    cur.execute("DELETE FROM core.variant_sizes WHERE variant_id = %s", (variant_id,))
    for idx, label in enumerate(labels):
        cur.execute(
            """
            INSERT INTO core.variant_sizes (variant_id, size_label, sort_key)
            VALUES (%s,%s,%s)
            """,
            (variant_id, label, size_sort_key(label, idx)),
        )


def upsert_variant_images(
    cur,
    variant_id: int,
    swatch_url: str,
    hero_url: Optional[str],
    color_name: str,
    set_primary: bool,
) -> None:
    cur.execute(
        """
        DELETE FROM core.product_images
         WHERE variant_id = %s
           AND (metadata->>'kind') = 'swatch'
        """,
        (variant_id,),
    )
    cur.execute(
        """
        INSERT INTO core.product_images (variant_id, url, position, is_primary, metadata)
        VALUES (%s,%s,NULL,false,%s)
        """,
        (variant_id, swatch_url, Json({"kind": "swatch", "color": color_name})),
    )
    if hero_url:
        if set_primary:
            cur.execute(
                """
                DELETE FROM core.product_images
                 WHERE variant_id = %s
                   AND is_primary = true
                """,
                (variant_id,),
            )
        cur.execute(
            """
            INSERT INTO core.product_images (variant_id, url, position, is_primary, metadata)
            VALUES (%s,%s,NULL,%s,%s)
            """,
            (
                variant_id,
                hero_url,
                set_primary,
                Json({"kind": "hero", "color": color_name}),
            ),
        )


def create_ingest_run(
    source: str,
    input_url: str,
    content_hash: str,
) -> int:
    """
    Record the start of an ingest run in ops.ingest_runs and return the run id.
    """
    with spotlight.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ops.ingest_runs (source, input_url, content_hash, status)
                VALUES (%s, %s, %s, 'pending')
                RETURNING id
                """,
                (source, input_url, content_hash),
            )
            run_id = cur.fetchone()[0]
        conn.commit()
    return run_id


def mark_ingest_run_success(
    run_id: Optional[int],
    *,
    product_id: Optional[int],
    rows_inserted: Optional[int] = None,
    rows_updated: Optional[int] = None,
) -> None:
    if not run_id:
        return
    with spotlight.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ops.ingest_runs
                   SET status = 'success',
                       finished_at = now(),
                       product_id = COALESCE(product_id, %s),
                       rows_inserted = COALESCE(rows_inserted, %s),
                       rows_updated = COALESCE(rows_updated, %s)
                 WHERE id = %s
                """,
                (product_id, rows_inserted, rows_updated, run_id),
            )
        conn.commit()


def mark_ingest_run_error(
    run_id: Optional[int],
    *,
    product_id: Optional[int],
    error_message: str,
) -> None:
    if not run_id:
        return
    with spotlight.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ops.ingest_runs
                   SET status = 'error',
                       finished_at = now(),
                       product_id = COALESCE(product_id, %s),
                       error_message = %s
                 WHERE id = %s
                """,
                (product_id, error_message, run_id),
            )
        conn.commit()


def record_ingest_failure(
    url: str,
    source: str,
    *,
    product_id: Optional[int],
    variant_id: Optional[int],
    error_message: str,
) -> None:
    """
    Record or update a failure row for this URL/source in ops.ingest_failures.
    """
    with spotlight.connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id
                  FROM ops.ingest_failures
                 WHERE url = %s
                   AND source = %s
                   AND resolved = false
                """,
                (url, source),
            )
            row = cur.fetchone()
            if row:
                failure_id = row[0]
                cur.execute(
                    """
                    UPDATE ops.ingest_failures
                       SET last_status     = 'error',
                           last_error      = %s,
                           last_attempt_at = now(),
                           attempt_count   = attempt_count + 1,
                           product_id      = COALESCE(product_id, %s),
                           variant_id      = COALESCE(variant_id, %s)
                     WHERE id = %s
                    """,
                    (error_message, product_id, variant_id, failure_id),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO ops.ingest_failures (
                        url,
                        source,
                        product_id,
                        variant_id,
                        last_status,
                        last_error,
                        last_attempt_at,
                        attempt_count
                    )
                    VALUES (%s, %s, %s, %s, 'error', %s, now(), 1)
                    """,
                    (url, source, product_id, variant_id, error_message),
                )
        conn.commit()


def record_skipped_ingest(
    source: str,
    input_url: str,
    content_hash: str,
    product_code: str,
) -> bool:
    """
    If we already have a successful ingest_run with this content_hash for the
    given URL, record a new 'skipped' run and return True.

    Returns False if no prior successful run exists (caller should proceed
    with a full ingest).
    """
    with spotlight.connect() as conn:
        with conn.cursor() as cur:
            # Check for an existing successful run with the same hash
            cur.execute(
                """
                SELECT 1
                  FROM ops.ingest_runs
                 WHERE source = %s
                   AND input_url = %s
                   AND content_hash = %s
                   AND status = 'success'
                 LIMIT 1
                """,
                (source, input_url, content_hash),
            )
            if not cur.fetchone():
                return False

            # Best-effort lookup of product_id for nicer audit trails
            cur.execute(
                "SELECT id FROM core.products WHERE product_code = %s LIMIT 1",
                (product_code,),
            )
            row = cur.fetchone()
            product_id = row[0] if row else None

            cur.execute(
                """
                INSERT INTO ops.ingest_runs (source, input_url, content_hash, status, product_id)
                VALUES (%s, %s, %s, 'skipped', %s)
                """,
                (source, input_url, content_hash, product_id),
            )
        conn.commit()
    return True


def ingest_catalog(
    url: str,
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool = False,
) -> None:
    canonical_url = spotlight.canonicalize_url(url)
    soup, next_data = spotlight.load_pdp_payload(canonical_url)
    initial_state = next_data["props"]["initialState"]
    product_map = initial_state["products"]["productsByProductCode"]
    product_code = next_data.get("query", {}).get("productCode") or next(iter(product_map.keys()))
    product = product_map[product_code]
    title = product.get("productName") or "Untitled Product"
    category_path = product.get("categoryAndProductPath") or ""
    category = category_path.split("/")[-2] if "/" in category_path else category_path or "unspecified"
    category = category.replace("-", " ").title()

    # Use the raw product payload as a deterministic content hash so we can detect no-op ingests.
    content_hash = hashlib.sha256(
        json.dumps(product, sort_keys=True).encode("utf-8")
    ).hexdigest()

    variant_records = build_variant_records(product, canonical_url)
    if not variant_records:
        raise RuntimeError("Unable to extract variants from PDP payload")

    if dry_run:
        print(
            json.dumps(
                {
                    "product_code": product_code,
                    "title": title,
                    "category": category,
                    "variant_count": len(variant_records),
                    "spotlight": spotlight_enabled,
                    "url": canonical_url,
                },
                indent=2,
            )
        )
        return

    # If this exact PDP payload has already been successfully ingested, record
    # a 'skipped' run and return without touching catalog/content tables.
    if record_skipped_ingest(
        "jcrew_full_ingest",
        canonical_url,
        content_hash,
        product_code,
    ):
        print(
            f"⏭️ Skipped {product_code} ({title}) — content unchanged since last successful ingest."
        )
        return

    run_id: Optional[int] = create_ingest_run(
        source="jcrew_full_ingest",
        input_url=canonical_url,
        content_hash=content_hash,
    )
    product_id: Optional[int] = None

    try:
        with spotlight.connect() as conn:
            with conn.cursor() as cur:
                brand_id = ensure_brand(cur, brand_slug, brand_name)
                product_id = ensure_product(
                    cur,
                    brand_id,
                    product_code,
                    title,
                    category,
                    product,
                    gender="male",
                )
                assign_canonical_category(cur, product_id, brand_id, category)
                upsert_ingestion_target(
                    cur,
                    product_id,
                    spotlight_enabled,
                    "Auto spotlight ingest" if spotlight_enabled else "Baseline ingest",
                )

                variant_ids: List[int] = []
                for record in variant_records:
                    variant_id = upsert_variant(cur, product_id, record)
                    variant_ids.append(variant_id)
                    replace_variant_sizes(cur, variant_id, record.size_labels)
                    upsert_variant_images(
                        cur,
                        variant_id,
                        record.swatch_url,
                        record.hero_url,
                        record.color_name,
                        record.is_primary,
                    )
                    upsert_product_url(
                        cur,
                        product_id,
                        record.variant_url,
                        variant_id=variant_id,
                    )
                primary_variant_id = None
                for record, variant_id in zip(variant_records, variant_ids):
                    if record.is_primary:
                        primary_variant_id = variant_id
                        break
                if primary_variant_id is None and variant_ids:
                    primary_variant_id = variant_ids[0]
                upsert_product_url(
                    cur,
                    product_id,
                    canonical_url,
                    variant_id=primary_variant_id,
                )
                conn.commit()

        content = spotlight.parse_product_content(canonical_url, soup=soup, next_data=next_data)
        spotlight.ingest(content)

        mark_ingest_run_success(
            run_id,
            product_id=product_id,
            rows_inserted=len(variant_records),
            rows_updated=None,
        )
        check_result = ingest_checker.run_checks(product_code)
        if check_result.issues:
            issues_text = "; ".join(check_result.issues)
            raise RuntimeError(
                f"Ingest checker detected issues for {product_code}: {issues_text}"
            )
        print(
            f"✅ Fully ingested {product_code} ({title}) — {len(variant_records)} variants, "
            f"{'spotlight' if spotlight_enabled else 'baseline'} mode."
        )
    except Exception as exc:
        error_message = str(exc)
        mark_ingest_run_error(
            run_id,
            product_id=product_id,
            error_message=error_message,
        )
        record_ingest_failure(
            canonical_url,
            "jcrew_full_ingest",
            product_id=product_id,
            variant_id=None,
            error_message=error_message,
        )
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add a J.Crew PDP to fs-core (catalog + spotlight).")
    parser.add_argument("--url", required=True, help="J.Crew PDP URL")
    parser.add_argument(
        "--no-spotlight",
        dest="spotlight",
        action="store_false",
        default=True,
        help="Disable spotlight content for this product",
    )
    parser.add_argument(
        "--brand-name",
        default=DEFAULT_BRAND_NAME,
        help="Brand display name (defaults to J.Crew)",
    )
    parser.add_argument(
        "--brand-slug",
        default=DEFAULT_BRAND_SLUG,
        help="Brand slug (defaults to 'jcrew')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed payload without writing to the database",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    missing = [k for k, v in DB_CONFIG.items() if not v]
    if missing:
        raise SystemExit(
            f"❌ Missing database configuration for: {', '.join(missing)}. "
            "Set DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT in .env."
        )
    ingest_catalog(
        args.url,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)

