#!/usr/bin/env python3
"""
Brand-specific ingest pipeline for Theory PDPs.

Uses the Demandware Product-Variation endpoint to pull structured JSON for
all colorways and sizes, then normalizes the data into core.products,
core.product_variants, product_urls, and the shared product group table.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence
from urllib.parse import parse_qs, urlsplit, urlunsplit

import psycopg2
import requests
from bs4 import BeautifulSoup
from psycopg2.extras import Json

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DB_CONFIG  # noqa: E402
import ingest_checker  # noqa: E402

VARIATION_ENDPOINT = (
    "https://www.theory.com/on/demandware.store/"
    "Sites-theory2_US-Site/default/Product-Variation"
)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
}

SIZE_ORDER = {
    "XXXS": 0,
    "XXS": 5,
    "XS": 10,
    "S": 20,
    "M": 30,
    "L": 40,
    "XL": 50,
    "XXL": 60,
    "XXXL": 70,
}


@dataclass
class VariantRecord:
    color_id: str
    color_name: str
    variant_url: str
    var_group_id: str
    hero_images: List[str]
    swatch_url: Optional[str]
    size_labels: List[str]
    attrs: Dict[str, object]
    is_primary: bool = False


def ensure_db_config() -> None:
    missing = [k for k, v in DB_CONFIG.items() if not v]
    if missing:
        raise SystemExit(
            f"❌ Missing database configuration for: {', '.join(missing)}. "
            "Set DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT in .env."
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


def slugify(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    return cleaned.strip("-") or "ungrouped"


def canonicalize_url(url: str) -> str:
    if not url:
        return url
    parsed = urlsplit(url)
    return urlunsplit((parsed.scheme or "https", parsed.netloc, parsed.path, "", ""))


def parse_pid_and_color(url: Optional[str], explicit_pid: Optional[str], explicit_color: Optional[str]) -> tuple[str, Optional[str]]:
    if explicit_pid:
        return explicit_pid, explicit_color
    if not url:
        raise SystemExit("Either --url or --pid must be provided.")
    parsed = urlsplit(url)
    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        raise SystemExit("Unable to parse Theory product ID from URL.")
    slug = path_parts[-1]
    if slug.endswith(".html"):
        slug = slug[:-5]
    pid = slug.split("_")[0]
    query = parse_qs(parsed.query)
    color_key = f"dwvar_{pid}_color"
    color = explicit_color or query.get(color_key, [None])[0]
    if "_" in slug and not color:
        color = slug.split("_", 1)[1]
    return pid, color


def fetch_variation(session: requests.Session, pid: str, color: Optional[str]) -> dict:
    params = {"pid": pid}
    if color:
        params[f"dwvar_{pid}_color"] = color
    resp = session.get(VARIATION_ENDPOINT, params=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def extract_color_values(payload: dict) -> List[dict]:
    product = payload.get("product") or {}
    for attribute in product.get("variationAttributes") or []:
        if attribute.get("attributeId") == "color":
            return attribute.get("values") or []
    return []


def build_variant_records(
    session: requests.Session,
    pid: str,
    color_values: Sequence[dict],
    primary_color: Optional[str],
) -> List[VariantRecord]:
    records: List[VariantRecord] = []
    for idx, color_meta in enumerate(color_values):
        color_id = color_meta.get("id")
        if not color_id:
            continue
        color_payload = fetch_variation(session, pid, color_id)
        product = color_payload.get("product") or {}
        images = product.get("images", {}).get("large", []) or []
        hero_images = [
            entry.get("absURL") or entry.get("url")
            for entry in images
            if entry.get("type") != "video" and (entry.get("absURL") or entry.get("url"))
        ]
        if not hero_images:
            hero_images = [
                entry.get("absURL") or entry.get("url")
                for entry in images
                if entry.get("absURL") or entry.get("url")
            ]
        size_values = (product.get("sizeVariationAttributes") or {}).get("values")
        if not size_values:
            for attr in product.get("variationAttributes") or []:
                if attr.get("attributeId") == "size":
                    size_values = attr.get("values")
                    break
        size_labels = []
        for value in size_values or []:
            label = value.get("displayValue") or value.get("id")
            if label:
                label_clean = " ".join(label.strip().split())
                if label_clean and label_clean not in size_labels:
                    size_labels.append(label_clean)
        color_name = color_meta.get("displayValue") or color_id
        swatch_url = None
        swatches = (color_meta.get("images") or {}).get("swatch") or []
        if swatches:
            swatch_url = swatches[0].get("absURL") or swatches[0].get("url")
        attrs = {
            "var_group_id": color_meta.get("varGroupId"),
            "item_number": color_meta.get("varGroupId"),
            "style_id": pid,
            "color_code": color_id,
            "unavailable": not color_meta.get("selectable", True),
            "ats": color_meta.get("ats"),
            "price": product.get("price"),
            "promotions": product.get("promotions"),
            "material": product.get("material"),
            "care": product.get("care"),
            "model_size": product.get("modelSize"),
            "highlight": product.get("highlightTileAttr"),
        }
        variant_url = canonicalize_url(color_meta.get("productLink") or product.get("selectedProductUrl") or "")
        records.append(
            VariantRecord(
                color_id=color_id,
                color_name=color_name,
                variant_url=variant_url,
                var_group_id=color_meta.get("varGroupId") or f"{pid}_{color_id}",
                hero_images=[img for img in hero_images if img],
                swatch_url=swatch_url,
                size_labels=size_labels,
                attrs=attrs,
                is_primary=bool(color_id == primary_color or (primary_color is None and idx == 0)),
            )
        )
    if records and not any(record.is_primary for record in records):
        records[0].is_primary = True
    return records


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
    base_name: str,
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
                   base_name = %s,
                   category = %s,
                   raw = %s,
                   gender = %s
             WHERE id = %s
            """,
            (brand_id, title, base_name, category, Json(raw_payload), gender, product_id),
        )
        return product_id
    cur.execute(
        """
        INSERT INTO core.products (brand_id, product_code, title, base_name, category, raw, gender)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (brand_id, product_code, title, base_name, category, Json(raw_payload), gender),
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
    if not url:
        return
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
        VALUES (%s,%s,%s,%s,true)
        """,
        (product_id, variant_id, region, url),
    )


def ensure_product_group(cur, brand_id: int, slug: str, display_name: str) -> int:
    cur.execute(
        """
        SELECT id FROM core.product_groups
         WHERE brand_id = %s AND slug = %s
        """,
        (brand_id, slug),
    )
    row = cur.fetchone()
    if row:
        group_id = row[0]
        cur.execute(
            """
            UPDATE core.product_groups
               SET display_name = %s,
                   updated_at = now()
             WHERE id = %s
            """,
            (display_name, group_id),
        )
        return group_id
    cur.execute(
        """
        INSERT INTO core.product_groups (brand_id, slug, display_name)
        VALUES (%s,%s,%s)
        RETURNING id
        """,
        (brand_id, slug, display_name),
    )
    return cur.fetchone()[0]


def ensure_group_membership(cur, group_id: int, product_id: int) -> None:
    cur.execute(
        """
        INSERT INTO core.product_group_members (group_id, product_id)
        VALUES (%s,%s)
        ON CONFLICT DO NOTHING
        """,
        (group_id, product_id),
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


def upsert_variant(cur, product_id: int, record: VariantRecord) -> int:
    cur.execute(
        """
        SELECT id FROM core.product_variants
         WHERE product_id = %s
           AND COALESCE(color_name,'') = %s
        """,
        (product_id, record.color_name),
    )
    row = cur.fetchone()
    variant_sku = record.var_group_id.lower()
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
        return variant_id
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
            None,
            record.variant_url,
            variant_sku,
            Json(record.attrs),
        ),
    )
    return cur.fetchone()[0]


def replace_variant_sizes(cur, variant_id: int, labels: Sequence[str]) -> None:
    cur.execute("DELETE FROM core.variant_sizes WHERE variant_id = %s", (variant_id,))
    for idx, label in enumerate(labels):
        normalized = " ".join(label.strip().split())
        if not normalized:
            continue
        cur.execute(
            """
            INSERT INTO core.variant_sizes (variant_id, size_label, sort_key)
            VALUES (%s,%s,%s)
            """,
            (variant_id, normalized, SIZE_ORDER.get(normalized.upper(), 200 + idx * 5)),
        )


def replace_variant_images(
    cur,
    variant_id: int,
    hero_urls: Sequence[str],
    color_name: str,
    swatch_url: Optional[str],
    set_primary: bool,
) -> None:
    cur.execute(
        """
        DELETE FROM core.product_images
         WHERE variant_id = %s
           AND (metadata->>'kind') IN ('swatch','hero')
        """,
        (variant_id,),
    )
    if swatch_url:
        cur.execute(
            """
            INSERT INTO core.product_images (variant_id, url, position, is_primary, metadata)
            VALUES (%s,%s,NULL,false,%s)
            """,
            (variant_id, swatch_url, Json({"kind": "swatch", "color": color_name})),
        )
    for idx, hero in enumerate(hero_urls):
        cur.execute(
            """
            INSERT INTO core.product_images (variant_id, url, position, is_primary, metadata)
            VALUES (%s,%s,%s,%s,%s)
            """,
            (
                variant_id,
                hero,
                idx + 1,
                set_primary and idx == 0,
                Json({"kind": "hero", "color": color_name}),
            ),
        )


def create_ingest_run(source: str, input_url: str, content_hash: str) -> int:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ops.ingest_runs (source, input_url, content_hash, status)
                VALUES (%s,%s,%s,'pending')
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
) -> None:
    if not run_id:
        return
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE ops.ingest_runs
                   SET status = 'success',
                       finished_at = now(),
                       product_id = COALESCE(product_id, %s),
                       rows_inserted = COALESCE(rows_inserted, %s)
                 WHERE id = %s
                """,
                (product_id, rows_inserted, run_id),
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
    with connect() as conn:
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
    error_message: str,
) -> None:
    with connect() as conn:
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
                cur.execute(
                    """
                    UPDATE ops.ingest_failures
                       SET last_status = 'error',
                           last_error = %s,
                           last_attempt_at = now(),
                           attempt_count = attempt_count + 1,
                           product_id = COALESCE(product_id, %s)
                     WHERE id = %s
                    """,
                    (error_message, product_id, row[0]),
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
                    VALUES (%s,%s,%s,NULL,'error',%s,now(),1)
                    """,
                    (url, source, product_id, error_message),
                )
        conn.commit()


def record_skipped_ingest(source: str, input_url: str, content_hash: str, product_code: str) -> bool:
    with connect() as conn:
        with conn.cursor() as cur:
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
            cur.execute(
                "SELECT id FROM core.products WHERE product_code = %s LIMIT 1",
                (product_code,),
            )
            row = cur.fetchone()
            product_id = row[0] if row else None
            cur.execute(
                """
                INSERT INTO ops.ingest_runs (source, input_url, content_hash, status, product_id)
                VALUES (%s,%s,%s,'skipped',%s)
                """,
                (source, input_url, content_hash, product_id),
            )
        conn.commit()
    return True


def html_to_lines(value: Optional[str]) -> List[str]:
    if not value:
        return []
    soup = BeautifulSoup(value, "html.parser")
    return [line.strip() for line in soup.get_text("\n").splitlines() if line.strip()]


def replace_specs(cur, product_id: int, spec_key: str, values: Sequence[str], source: str):
    cur.execute(
        "DELETE FROM core.product_specs WHERE product_id = %s AND spec_key = %s",
        (product_id, spec_key),
    )
    for order, entry in enumerate(values, start=1):
        if not entry:
            continue
        cur.execute(
            "SELECT core.upsert_product_spec(%s,%s,%s,%s,%s,%s);",
            (
                product_id,
                spec_key,
                entry.strip(),
                order,
                source,
                Json({"source": source}),
            ),
        )


def replace_marketing_story(cur, product_id: int, story: Optional[str]):
    if not story:
        return
    cur.execute(
        """
        DELETE FROM core.product_content
         WHERE product_id = %s AND content_type = %s
        """,
        (product_id, "marketing_story"),
    )
    cur.execute(
        "SELECT core.insert_product_content(%s,%s,%s,%s,%s);",
        (product_id, None, "marketing_story", story.strip(), Json({"source": "theory"})),
    )


def upsert_fit_guidance(cur, product_id: int, fit_statement: Optional[str]):
    if not fit_statement:
        return
    cur.execute(
        "DELETE FROM core.product_fit_guidance WHERE product_id = %s AND variant_id IS NULL",
        (product_id,),
    )
    cur.execute(
        "SELECT core.upsert_product_fit_guidance(%s,%s,%s,%s,%s,%s,%s,%s,%s);",
        (
            product_id,
            None,
            fit_statement.strip(),
            0,
            0,
            0,
            0,
            Json({}),
            Json({"fit_statement": fit_statement.strip()}),
        ),
    )


def ingest_product_content(cur, product_id: int, product: dict):
    material = product.get("material")
    care = product.get("care")
    description = product.get("shortDescription")
    model_info = html_to_lines(product.get("modelSize"))
    replace_specs(cur, product_id, "fabric", [material] if material else [], source="theory-material")
    replace_specs(cur, product_id, "care", [care] if care else [], source="theory-care")
    replace_specs(cur, product_id, "features", [description] if description else [], source="theory-description")
    replace_specs(cur, product_id, "model_info", model_info, source="theory-model")
    replace_marketing_story(cur, product_id, description)
    fit_statement = model_info[0] if model_info else None
    upsert_fit_guidance(cur, product_id, fit_statement)


def ingest_catalog(
    url: Optional[str],
    pid: Optional[str],
    color: Optional[str],
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    force: bool,
) -> None:
    pid, initial_color = parse_pid_and_color(url, pid, color)
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    base_payload = fetch_variation(session, pid, initial_color)
    product = base_payload.get("product") or {}
    color_values = extract_color_values(base_payload)
    if not color_values:
        raise RuntimeError("Unable to discover color variation attributes.")
    primary_color = initial_color or next((value.get("id") for value in color_values if value.get("selectable")), None)
    variant_records = build_variant_records(session, pid, color_values, primary_color)
    if not variant_records:
        raise RuntimeError("No Theory variants could be extracted.")
    title = product.get("productName") or "Untitled Theory Product"
    base_name = title
    category = product.get("masterClassCategory") or "mens-shirts"
    canonical_url = canonicalize_url(f"https://www.theory.com{product.get('selectedProductUrl') or urlsplit(url or '').path}")
    content_hash = hashlib.sha256(json.dumps(base_payload, sort_keys=True).encode("utf-8")).hexdigest()
    if not force and record_skipped_ingest(
        "theory_full_ingest",
        canonical_url,
        content_hash,
        pid,
    ):
        print(f"⏭️  Skipped {pid} ({title}) — payload unchanged.")
        return
    if dry_run:
        print(
            json.dumps(
                {
                    "product_code": pid,
                    "title": title,
                    "category": category,
                    "variants": len(variant_records),
                    "url": canonical_url,
                },
                indent=2,
            )
        )
        return
    run_id = create_ingest_run("theory_full_ingest", canonical_url, content_hash)
    product_id: Optional[int] = None
    committed_product_id: Optional[int] = None
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                brand_id = ensure_brand(cur, brand_slug, brand_name)
                product_id = ensure_product(
                    cur,
                    brand_id,
                    pid,
                    title,
                    base_name,
                    category,
                    {"master": base_payload},
                    gender="male",
                )
                assign_canonical_category(cur, product_id, brand_id, category)
                group_slug = slugify(base_name)
                group_id = ensure_product_group(cur, brand_id, group_slug, base_name)
                ensure_group_membership(cur, group_id, product_id)
                upsert_product_url(cur, product_id, canonical_url)
                upsert_ingestion_target(
                    cur,
                    product_id,
                    spotlight_enabled,
                    note="theory_full_ingest",
                )
                ingest_product_content(cur, product_id, product)
                for record in variant_records:
                    variant_id = upsert_variant(cur, product_id, record)
                    replace_variant_sizes(cur, variant_id, record.size_labels)
                    replace_variant_images(
                        cur,
                        variant_id,
                        record.hero_images,
                        record.color_name,
                        record.swatch_url,
                        set_primary=record.is_primary,
                    )
                    upsert_product_url(cur, product_id, record.variant_url, variant_id=variant_id)
            conn.commit()
        committed_product_id = product_id
        mark_ingest_run_success(
            run_id,
            product_id=committed_product_id,
            rows_inserted=len(variant_records),
        )
        check_result = ingest_checker.run_checks(pid)
        if check_result.issues:
            issues_text = "; ".join(check_result.issues)
            raise RuntimeError(f"Ingest checker detected issues for {pid}: {issues_text}")
        print(f"✅ Ingested Theory {pid} with {len(variant_records)} variants.")
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        mark_ingest_run_error(run_id, product_id=committed_product_id, error_message=message)
        record_ingest_failure(
            canonical_url,
            "theory_full_ingest",
            product_id=committed_product_id,
            error_message=message,
        )
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a Theory PDP into fs-core.")
    parser.add_argument("--url", help="Theory PDP URL (e.g. https://www.theory.com/...J0794505.html)")
    parser.add_argument("--pid", help="Explicit Theory product ID (e.g. J0794505)")
    parser.add_argument("--color", help="Optional color code to seed the initial variation call (e.g. YJY)")
    parser.add_argument(
        "--spotlight",
        action="store_true",
        help="Mark this product as spotlight-enabled in ops.ingestion_targets.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and print metadata without touching the database.")
    parser.add_argument(
        "--brand-name",
        default="Theory",
        help="Override the brand display name.",
    )
    parser.add_argument(
        "--brand-slug",
        default="theory",
        help="Override the brand slug.",
    )
    parser.add_argument("--force", action="store_true", help="Force ingestion even if no content changes detected.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    ingest_catalog(
        args.url,
        args.pid,
        args.color,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        force=args.force,
    )


if __name__ == "__main__":
    main()

