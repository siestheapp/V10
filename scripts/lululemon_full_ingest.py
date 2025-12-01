#!/usr/bin/env python3
"""
Brand-specific ingest for Lululemon PDPs.

This mirrors the shape of `scripts/jcrew_full_ingest.py`, but parses the
Lululemon `__NEXT_DATA__` payload that `lululemon_pdp_dump.py` extracts.

Workflow:
  1. Fetch the PDP (or read a saved JSON payload) to obtain the product blob.
  2. Normalize variants, sizes, and hero images per color.
  3. Upsert the product + variants into fs-core, keeping ops.ingest_runs in sync.
  4. Store marketing copy + care/fabric bullets in the spotlight tables so the
     rest of the platform can surface accurate metadata.

Example:
    source venv/bin/activate
    python scripts/lululemon_full_ingest.py \\
        --payload data/tmp/lululemon_prod6750191.json \\
        --url "https://shop.lululemon.com/p/mens-button-down-shirts/Commission-LS-Button-Down-Pockets/_/prod6750191"
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
import importlib
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

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
from lululemon_graphql_client import (  # noqa: E402
    response_to_ingest_payload,
)

DEFAULT_BRAND_NAME = "Lululemon"
DEFAULT_BRAND_SLUG = "lululemon"
BASE_HOST = "https://shop.lululemon.com"
DEFAULT_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

SIZE_ALIAS_MAP = {
    "X-SMALL": "XS",
    "XX-SMALL": "XXS",
    "SMALL": "S",
    "MEDIUM": "M",
    "MED": "M",
    "LARGE": "L",
    "X-LARGE": "XL",
    "XX-LARGE": "XXL",
    "2XL": "XXL",
    "3XL": "XXXL",
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
    color_code: str
    color_name: str
    style_id: str
    variant_url: str
    swatch_url: Optional[str]
    hero_images: List[str]
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


def canonicalize_url(path: str, fallback: str) -> str:
    if not path:
        path = fallback or ""
    if path.startswith("http"):
        return path
    if not path.startswith("/"):
        path = f"/{path}"
    return f"{BASE_HOST}{path}"


def with_query(url: str, **params: str) -> str:
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    for key, value in params.items():
        if value is None:
            query.pop(key, None)
        else:
            query[key] = value
    return urlunsplit(
        (
            parts.scheme or "https",
            parts.netloc or urlsplit(BASE_HOST).netloc,
            parts.path,
            urlencode(query, doseq=True),
            parts.fragment,
        )
    )


def normalize_size(label: Optional[str]) -> Optional[str]:
    if not label:
        return None
    cleaned = " ".join(label.strip().split()).upper()
    return SIZE_ALIAS_MAP.get(cleaned, cleaned.replace(" ", "-"))


def size_sort_key(label: str, fallback_index: int) -> int:
    return SIZE_ORDER.get(label, 200 + fallback_index * 5)


def load_payload(
    url: Optional[str],
    payload_path: Optional[Path],
    *,
    allow_playwright: bool,
    graphql_response_path: Optional[Path] = None,
    graphql_response: Optional[dict] = None,
) -> dict:
    if graphql_response_path or graphql_response:
        response = graphql_response or json.loads(
            graphql_response_path.read_text(encoding="utf-8")
        )
        return response_to_ingest_payload(response)
    if payload_path:
        return json.loads(payload_path.read_text(encoding="utf-8"))
    if not url:
        raise RuntimeError(
            "Provide --url/--payload or a GraphQL response when ingesting."
        )
    luludump = importlib.import_module("lululemon_pdp_dump")
    html = luludump.fetch_html(url, allow_playwright=allow_playwright)
    return luludump.extract_next_data(html)


def extract_current(payload: dict) -> dict:
    try:
        return payload["props"]["pageProps"]["initialStoreState"]["productDetailPage"]["current"]
    except KeyError as exc:  # noqa: BLE001
        raise RuntimeError("Payload missing productDetailPage.current block") from exc


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


def upsert_variant(cur, product_id: int, record: VariantRecord) -> int:
    cur.execute(
        """
        SELECT id FROM core.product_variants
         WHERE product_id = %s
           AND COALESCE(color_name, '') = %s
        """,
        (product_id, record.color_name),
    )
    row = cur.fetchone()
    variant_sku = record.style_id or f"{product_id}-{record.color_code.lower()}"
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
                None,
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


def replace_variant_images(
    cur,
    variant_id: int,
    swatch_url: Optional[str],
    hero_urls: Sequence[str],
    color_name: str,
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
                failure_id = row[0]
                cur.execute(
                    """
                    UPDATE ops.ingest_failures
                       SET last_status     = 'error',
                           last_error      = %s,
                           last_attempt_at = now(),
                           attempt_count   = attempt_count + 1,
                           product_id      = COALESCE(product_id, %s)
                     WHERE id = %s
                    """,
                    (error_message, product_id, failure_id),
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


def record_skipped_ingest(
    source: str,
    input_url: str,
    content_hash: str,
    product_code: str,
) -> bool:
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


def dedupe_strings(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if not value:
            continue
        normalized = " ".join(value.strip().split())
        if not normalized or normalized.lower() in seen:
            continue
        seen.add(normalized.lower())
        ordered.append(normalized)
    return ordered


def collect_care_statements(current: dict) -> List[str]:
    """
    Collect care instructions from both the legacy NEXT_DATA shape and the
    GraphQL shape.

    Primary source:
      current.productAttributes.productContentCare[].care[].careDescription

    Fallback (GraphQL / richer PDP blocks):
      current.colorAttributes[].careAndContent.sections[].attributes[].{text,list}
    """
    care: List[str] = []

    # Primary: productAttributes → productContentCare
    attrs = current.get("productAttributes") or {}
    for block in attrs.get("productContentCare") or []:
        for entry in block.get("care") or []:
            desc = (
                (entry or {}).get("careDescription")
                or (entry or {}).get("description")
                or ""
            )
            if desc:
                care.append(desc)

    # Fallback: colorAttributes → careAndContent.sections[].attributes[]
    color_attributes = current.get("colorAttributes") or []
    for attr in color_attributes:
        care_section = (attr or {}).get("careAndContent") or {}
        for section in care_section.get("sections") or []:
            for item in section.get("attributes") or []:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                if text:
                    care.append(text)
                # Handle list-style bullets which may be a dict with `items`
                # or a bare list.
                lst = item.get("list")
                if isinstance(lst, dict):
                    items = lst.get("items") or []
                elif isinstance(lst, list):
                    items = lst
                else:
                    items = []
                for entry in items:
                    if isinstance(entry, str) and entry:
                        care.append(entry)

    return dedupe_strings(care)


def collect_section_text(color_attributes: Sequence[dict], key: str) -> List[str]:
    bullets: List[str] = []
    for attr in color_attributes:
        section = (attr or {}).get(key)
        if not section:
            continue
        for block in section.get("sections") or []:
            for item in block.get("attributes") or []:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                if text:
                    bullets.append(text)

                # Also support list-based attributes (GraphQL often encodes
                # bullets under `list`).
                lst = item.get("list")
                if isinstance(lst, dict):
                    items = lst.get("items") or []
                elif isinstance(lst, list):
                    items = lst
                else:
                    items = []
                for entry in items:
                    if isinstance(entry, str) and entry:
                        bullets.append(entry)
    return dedupe_strings(bullets)


def collect_fit_notes(color_attributes: Sequence[dict]) -> List[str]:
    notes: List[str] = []
    for attr in color_attributes:
        section = (attr or {}).get("fitOrHowToUse")
        if not section:
            continue
        title = section.get("title")
        if title:
            notes.append(title)
        for block in section.get("sections") or []:
            for item in block.get("attributes") or []:
                if not isinstance(item, dict):
                    continue
                text = item.get("text")
                if text:
                    notes.append(text)

                lst = item.get("list")
                if isinstance(lst, dict):
                    items = lst.get("items") or []
                elif isinstance(lst, list):
                    items = lst
                else:
                    items = []
                for entry in items:
                    if isinstance(entry, str) and entry:
                        notes.append(entry)
    return dedupe_strings(notes)


def replace_specs(cur, product_id: int, spec_key: str, values: Sequence[str], source: str):
    cur.execute(
        "DELETE FROM core.product_specs WHERE product_id = %s AND spec_key = %s",
        (product_id, spec_key),
    )
    for order, value in enumerate(values, start=1):
        if not value:
            continue
        cur.execute(
            "SELECT core.upsert_product_spec(%s,%s,%s,%s,%s,%s);",
            (
                product_id,
                spec_key,
                value.strip(),
                order,
                source,
                Json({"source": source}),
            ),
        )


def replace_marketing_story(cur, product_id: int, story: str):
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
        (product_id, None, "marketing_story", story.strip(), None),
    )


def upsert_fit_guidance(cur, product_id: int, fit_statement: Optional[str], sample_size: Optional[int]):
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
            fit_statement,
            0,
            sample_size or 0,
            0,
            sample_size or 0,
            Json({}),
            Json({"fit_statement": fit_statement}),
        ),
    )


def ingest_product_content(cur, product_id: int, current: dict):
    color_attributes = current.get("colorAttributes") or []
    care = collect_care_statements(current)
    fabric = collect_section_text(color_attributes, "fabricOrBenefits")
    features = collect_section_text(color_attributes, "featuresOrIngredients")
    fit_notes = collect_fit_notes(color_attributes)

    replace_specs(cur, product_id, "care", care, source="lululemon-care")
    replace_specs(cur, product_id, "fabric", fabric, source="lululemon-fabric")
    replace_specs(cur, product_id, "features", features, source="lululemon-features")

    # Marketing story: prefer the summary-level field, but fall back to any
    # dedicated why-we-made-this content blocks when present (GraphQL).
    summary = current.get("productSummary") or {}
    story = summary.get("whyWeMadeThis") or ""

    if not story:
        attrs = current.get("productAttributes") or {}
        wwmt_attr = attrs.get("productContentWhyWeMadeThis")
        if isinstance(wwmt_attr, str):
            story = wwmt_attr
        elif isinstance(wwmt_attr, dict):
            story = (
                wwmt_attr.get("text")
                or wwmt_attr.get("description")
                or wwmt_attr.get("body")
                or story
            )
        elif isinstance(wwmt_attr, list):
            # Join any text-like entries into a single paragraph.
            parts: List[str] = []
            for item in wwmt_attr:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = (
                        item.get("text")
                        or item.get("description")
                        or item.get("body")
                        or ""
                    )
                    if text:
                        parts.append(text)
            if parts:
                story = " ".join(parts)

    if not story:
        # Final fallback: whyWeMadeThisAttributes[].text from GraphQL.
        wwmt_blocks = current.get("whyWeMadeThisAttributes") or []
        parts: List[str] = []
        for block in wwmt_blocks:
            if isinstance(block, dict):
                text = block.get("text")
                if text:
                    parts.append(text)
        if parts:
            story = " ".join(parts)

    replace_marketing_story(cur, product_id, story)

    fit_statement = fit_notes[0] if fit_notes else None
    upsert_fit_guidance(
        cur,
        product_id,
        fit_statement=fit_statement,
        sample_size=current.get("productSummary", {}).get("totalReviews"),
    )


def build_variant_records(current: dict, canonical_url: str) -> List[VariantRecord]:
    colors = {entry.get("code"): entry for entry in current.get("colors") or []}
    carousel = {
        entry.get("color", {}).get("code"): entry
        for entry in current.get("productCarousel") or []
    }
    size_map: Dict[str, List[str]] = {}
    style_map: Dict[str, str] = {}
    price_map: Dict[str, Dict[str, object]] = {}

    for sku in current.get("skus") or []:
        color_code = (sku.get("color") or {}).get("code")
        size = normalize_size(sku.get("size"))
        if not color_code or not size:
            continue
        style_map.setdefault(color_code, sku.get("styleId"))
        price_map[color_code] = sku.get("price") or {}
        size_list = size_map.setdefault(color_code, [])
        if size not in size_list:
            size_list.append(size)

    for entry in current.get("colorDriver") or []:
        color_code = entry.get("color")
        if not color_code:
            continue
        size_list = size_map.setdefault(color_code, [])
        for label in entry.get("sizes") or []:
            normalized = normalize_size(label)
            if normalized and normalized not in size_list:
                size_list.append(normalized)

    default_color = current.get("selectedColor")
    if not default_color:
        summary = current.get("productSummary") or {}
        default_color = (summary.get("topSellers") or summary.get("trendingColorsAll") or [None])[0]
    if not default_color:
        default_color = next(iter(colors.keys()), None)

    records: List[VariantRecord] = []
    for idx, (color_code, meta) in enumerate(colors.items()):
        if not color_code:
            continue
        size_labels = size_map.get(color_code, [])
        if not size_labels:
            size_labels = DEFAULT_SIZES
        size_labels = sorted(size_labels, key=lambda label: size_sort_key(label, 0))
        style_id = style_map.get(color_code) or meta.get("slug") or color_code
        variant_url = with_query(canonical_url, color=style_id)
        hero_images = carousel.get(color_code, {}).get("imageInfo") or []
        attrs = {
            "color_code": color_code,
            "style_id": style_id,
            "swatch_url": meta.get("swatchUrl"),
            "slug": meta.get("slug"),
            "price": price_map.get(color_code),
        }
        records.append(
            VariantRecord(
                color_code=color_code,
                color_name=meta.get("name") or color_code,
                style_id=style_id,
                variant_url=variant_url,
                swatch_url=meta.get("swatchUrl"),
                hero_images=hero_images or [meta.get("swatchUrl")] if meta.get("swatchUrl") else [],
                size_labels=size_labels,
                attrs=attrs,
                is_primary=bool(color_code == default_color or (idx == 0 and not default_color)),
            )
        )

    if records and not any(record.is_primary for record in records):
        records[0].is_primary = True
    return records


def ingest_catalog(
    url: Optional[str],
    payload_path: Optional[Path],
    *,
    allow_playwright: bool,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    graphql_response_path: Optional[Path] = None,
    graphql_response: Optional[dict] = None,
    run_checks: bool = True,
) -> None:
    payload = load_payload(
        url,
        payload_path,
        allow_playwright=allow_playwright,
        graphql_response_path=graphql_response_path,
        graphql_response=graphql_response,
    )
    current = extract_current(payload)
    product_summary = current.get("productSummary") or {}
    product_code = product_summary.get("productId") or product_summary.get("unifiedId")
    if not product_code:
        raise RuntimeError("Unable to determine product code from payload.")
    product_name_field = product_summary.get("productName")
    if isinstance(product_name_field, list):
        product_name_field = product_name_field[0]
    title = (
        product_summary.get("displayName")
        or product_name_field
        or "Untitled Product"
    ).strip()
    base_name = (product_name_field or title).strip()
    category = product_summary.get("parentCategoryDisplayName") or (
        (product_summary.get("productCategory") or ["uncategorized"])[0]
        if isinstance(product_summary.get("productCategory"), list)
        else product_summary.get("productCategory")
    )
    canonical_url = canonicalize_url(product_summary.get("pdpUrl"), url or "")

    content_hash = hashlib.sha256(json.dumps(current, sort_keys=True).encode("utf-8")).hexdigest()
    variant_records = build_variant_records(current, canonical_url)
    if not variant_records:
        raise RuntimeError("Unable to extract variants from payload.")

    if dry_run:
        print(
            json.dumps(
                {
                    "product_code": product_code,
                    "title": title,
                    "category": category,
                    "variant_count": len(variant_records),
                    "url": canonical_url,
                    "spotlight": spotlight_enabled,
                },
                indent=2,
            )
        )
        return

    if record_skipped_ingest(
        "lululemon_full_ingest",
        canonical_url,
        content_hash,
        product_code,
    ):
        print(f"⏭️  Skipped {product_code} ({title}) — payload unchanged.")
        return

    run_id = create_ingest_run(
        source="lululemon_full_ingest",
        input_url=canonical_url,
        content_hash=content_hash,
    )
    product_id: Optional[int] = None

    try:
        with connect() as conn:
            with conn.cursor() as cur:
                brand_id = ensure_brand(cur, brand_slug, brand_name)
                product_id = ensure_product(
                    cur,
                    brand_id,
                    product_code,
                    title,
                    base_name,
                    category,
                    current,
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
                    replace_variant_images(
                        cur,
                        variant_id,
                        record.swatch_url,
                        record.hero_images,
                        record.color_name,
                        record.is_primary,
                    )
                    upsert_product_url(
                        cur,
                        product_id,
                        record.variant_url,
                        variant_id=variant_id,
                    )

                ingest_product_content(cur, product_id, current)

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

        mark_ingest_run_success(
            run_id,
            product_id=product_id,
            rows_inserted=len(variant_records),
        )
        if run_checks:
            check_result = ingest_checker.run_checks(product_code)
            if check_result.issues:
                issues_text = "; ".join(check_result.issues)
                raise RuntimeError(
                    f"Ingest checker detected issues for {product_code}: {issues_text}"
                )
        print(
            f"✅ Ingested {product_code} ({title}) — {len(variant_records)} variants "
            f"({'spotlight' if spotlight_enabled else 'baseline'}) mode."
        )
    except Exception as exc:
        message = str(exc)
        mark_ingest_run_error(
            run_id,
            product_id=product_id,
            error_message=message,
        )
        record_ingest_failure(
            canonical_url,
            "lululemon_full_ingest",
            product_id=product_id,
            error_message=message,
        )
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a Lululemon PDP into fs-core.")
    parser.add_argument("--url", help="Lululemon PDP URL or local HTML path.")
    parser.add_argument(
        "--payload",
        type=Path,
        help="Optional path to a saved __NEXT_DATA__ JSON payload.",
    )
    parser.add_argument(
        "--graphql-response",
        type=Path,
        help="Optional path to a saved GraphQL response JSON file.",
    )
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Disable Playwright fallback when fetching remote URLs.",
    )
    parser.add_argument(
        "--no-spotlight",
        dest="spotlight",
        action="store_false",
        default=True,
        help="Disable spotlight metadata for this product.",
    )
    parser.add_argument(
        "--brand-name",
        default=DEFAULT_BRAND_NAME,
        help="Brand display name (defaults to Lululemon).",
    )
    parser.add_argument(
        "--brand-slug",
        default=DEFAULT_BRAND_SLUG,
        help="Brand slug used in core.brands.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print parsed payload details without touching the database.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    if not args.url and not args.payload and not args.graphql_response:
        raise SystemExit(
            "❌ Provide --url, --payload, or --graphql-response for ingestion."
        )
    ingest_catalog(
        args.url,
        args.payload,
        allow_playwright=not args.no_playwright,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        graphql_response_path=args.graphql_response,
        run_checks=True,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


