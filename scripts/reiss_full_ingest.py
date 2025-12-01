#!/usr/bin/env python3
"""
Brand-specific ingest pipeline for Reiss PDPs.

Similar to the Lululemon/J.Crew ingesters, this script:
  1. Loads the Reiss PDP (or a saved HTML export) and parses the hydrated
     React Query payload that contains product data.
  2. Expands all available colourways/fits by fetching each itemNumber so we
     capture every variant under the same styleNumber.
  3. Normalizes variants (color, fit, sizes, hero imagery) and upserts them into
     fs-core, keeping ops.ingest_runs/ingest_failures in sync.
  4. Stores tone-of-voice/fabric/care content inside spotlight tables so the
     rest of the stack can surface it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import urlsplit, urlunsplit

import psycopg2
from psycopg2.extras import Json
import requests
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DB_CONFIG  # noqa: E402
import ingest_checker  # noqa: E402

DEFAULT_BRAND_NAME = "Reiss"
DEFAULT_BRAND_SLUG = "reiss"
BASE_HOST = "https://www.reiss.com"
CDN_HOST = "https://cdn.platform.next"
DEFAULT_SIZES = ["XS", "S", "M", "L", "XL", "XXL"]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
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
    "XXXXL": 80,
}


@dataclass
class VariantRecord:
    item_number: str
    color_name: str
    fit_name: Optional[str]
    variant_url: str
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


def dedupe_strings(values: Iterable[str]) -> List[str]:
    seen = set()
    ordered: List[str] = []
    for value in values:
        if not value:
            continue
        normalized = " ".join(value.strip().split())
        lowered = normalized.lower()
        if not normalized or lowered in seen:
            continue
        seen.add(lowered)
        ordered.append(normalized)
    return ordered


def slugify(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    return cleaned.strip("-") or "ungrouped"


def fetch_html(url: str, session: requests.Session) -> str:
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    return resp.text


def load_html(
    url: Optional[str],
    html_path: Optional[Path],
    session: requests.Session,
) -> Tuple[str, str]:
    if html_path:
        html = html_path.read_text(encoding="utf-8")
        resolved_url = url or extract_canonical_url(html)
        if not resolved_url:
            raise RuntimeError("Unable to determine canonical URL from HTML payload.")
        return html, resolved_url
    if not url:
        raise RuntimeError("Either --url or --html must be provided.")
    html = fetch_html(url, session)
    return html, url


def extract_canonical_url(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("link", rel="canonical")
    return link["href"].strip() if link and link.get("href") else None


def extract_payload(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", {"type": "application/json"}):
        content = script.string or ""
        if "dehydratedState" in content:
            return json.loads(content)
    raise RuntimeError("Unable to locate dehydrated React Query payload.")


def extract_product_block(payload: dict) -> dict:
    try:
        queries = payload["props"]["pageProps"]["dehydratedState"]["queries"]
    except KeyError as exc:  # noqa: BLE001
        raise RuntimeError("Payload missing dehydratedState queries.") from exc

    for entry in queries:
        key = entry.get("queryKey")
        if isinstance(key, list) and key and key[0] == "product":
            data = entry.get("state", {}).get("data")
            if data:
                return data
    raise RuntimeError("Product query block not found in payload.")


def normalize_color_name(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.strip().split()).title()


def normalize_size_label(label: str) -> str:
    cleaned = " ".join(label.strip().split())
    upper = cleaned.upper()
    alias = {
        "EXTRA SMALL": "XS",
        "SMALL": "S",
        "MEDIUM": "M",
        "LARGE": "L",
        "EXTRA LARGE": "XL",
        "XX LARGE": "XXL",
    }
    return alias.get(upper, cleaned)


def size_sort_key(label: str, idx: int) -> int:
    normalized = label.strip().upper().replace(" ", "")
    return SIZE_ORDER.get(normalized, 200 + idx * 5)


def swap_item_in_url(base_url: str, new_item_code: str) -> str:
    parsed = urlsplit(base_url)
    segments = [part for part in parsed.path.split("/") if part]
    if "style" in segments:
        style_idx = segments.index("style")
        if len(segments) > style_idx + 2:
            segments[style_idx + 2] = new_item_code.lower()
        elif len(segments) == style_idx + 2:
            segments.append(new_item_code.lower())
    else:
        segments.append("style")
        segments.append(new_item_code.lower())
    new_path = "/" + "/".join(segments)
    return urlunsplit((parsed.scheme or "https", parsed.netloc or urlsplit(BASE_HOST).netloc, new_path, "", ""))


def absolute_media_url(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if path.startswith("//"):
        return f"https:{path}"
    if path.startswith("/common/"):
        return f"{CDN_HOST}{path}"
    return f"{BASE_HOST}{path if path.startswith('/') else '/' + path}"


def gather_variant_payloads(
    base_url: str,
    base_product: dict,
    session: requests.Session,
    max_variants: Optional[int],
) -> Dict[str, dict]:
    item_map = base_product.get("fitsAndColourwaysItemNumberMap") or {}
    base_item = (base_product.get("itemNumber") or "").upper()
    variants = {base_item: base_product} if base_item else {}

    ordered_items: List[str] = []
    colourways = (
        base_product.get("fitsAndColourways", {})
        .get("colourways", {})
        .get("colourways", [])
    )
    for entry in colourways:
        code = (entry.get("itemNumber") or "").upper()
        if code and code not in ordered_items:
            ordered_items.append(code)
    for code in item_map.keys():
        upper = code.upper()
        if upper not in ordered_items:
            ordered_items.append(upper)

    for item_number in ordered_items:
        if not item_number:
            continue
        if item_number in variants:
            continue
        if max_variants and len(variants) >= max_variants:
            break
        target_url = swap_item_in_url(base_url, item_number)
        try:
            html = fetch_html(target_url, session)
            payload = extract_payload(html)
            product = extract_product_block(payload)
            variants[item_number] = product
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  Failed to expand {item_number} ({target_url}): {exc}")
            continue
    return variants


def build_base_name(title: str, color_names: Sequence[str]) -> str:
    lowered = title.lower()
    for color in color_names:
        token = f" in {color.lower()}"
        if lowered.endswith(token):
            return title[: -len(token)]
    return title


def build_variant_records(
    base_url: str,
    variant_payloads: Dict[str, dict],
    item_map: Dict[str, dict],
    base_item_number: Optional[str],
) -> List[VariantRecord]:
    records: List[VariantRecord] = []
    base_item_upper = (base_item_number or "").upper()

    for item_number, meta in item_map.items():
        key = item_number.upper()
        payload = variant_payloads.get(key)
        if not payload:
            continue
        color_name = meta.get("colour") or payload.get("colour") or payload.get("title")
        fit_name = meta.get("fit") or payload.get("fitLabel") or payload.get("fit")
        variant_url = swap_item_in_url(base_url, payload.get("itemNumber") or key)
        images = [
            absolute_media_url(entry.get("imageUrl"))
            for entry in payload.get("itemMedia") or []
        ]
        hero_images = [img for img in images if img]
        size_entries = (payload.get("options") or {}).get("options") or []
        size_labels = [
            normalize_size_label(entry.get("name", ""))
            for entry in size_entries
            if entry.get("name")
        ]
        if not size_labels:
            size_labels = DEFAULT_SIZES

        attrs = {
            "style_number": payload.get("styleNumber"),
            "item_number": payload.get("itemNumber"),
            "product_code": payload.get("productCode"),
            "colour": color_name,
            "fit": fit_name,
            "price": payload.get("price"),
            "price_data": payload.get("priceData"),
            "was_price": payload.get("wasPrice"),
            "stock_status": {
                entry.get("name"): entry.get("stockStatus")
                for entry in size_entries
                if entry.get("name")
            },
        }

        records.append(
            VariantRecord(
                item_number=key,
                color_name=normalize_color_name(color_name),
                fit_name=fit_name.strip() if isinstance(fit_name, str) else fit_name,
                variant_url=variant_url,
                hero_images=hero_images,
                size_labels=size_labels,
                attrs=attrs,
                is_primary=key == base_item_upper,
            )
        )

    if records and not any(record.is_primary for record in records):
        records[0].is_primary = True
    return records


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
        VALUES (%s,%s,%s,%s,true)
        """,
        (product_id, variant_id, region, url),
    )


def ensure_product_group(
    cur,
    brand_id: int,
    slug: str,
    display_name: str,
) -> int:
    cur.execute(
        """
        SELECT id
          FROM core.product_groups
         WHERE brand_id = %s
           AND slug = %s
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
           AND COALESCE(fit_name,'') = COALESCE(%s,'')
        """,
        (product_id, record.color_name, record.fit_name),
    )
    row = cur.fetchone()
    variant_sku = record.item_number
    if row:
        variant_id = row[0]
        cur.execute(
            """
            UPDATE core.product_variants
               SET variant_url = %s,
                   variant_sku = %s,
                   fit_name = %s,
                   attrs = %s
             WHERE id = %s
            """,
            (
                record.variant_url,
                variant_sku,
                record.fit_name,
                Json(record.attrs),
                variant_id,
            ),
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
            record.fit_name,
            record.variant_url,
            variant_sku,
            Json(record.attrs),
        ),
    )
    return cur.fetchone()[0]


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
    hero_urls: Sequence[str],
    color_name: str,
    set_primary: bool,
) -> None:
    cur.execute(
        """
        DELETE FROM core.product_images
         WHERE variant_id = %s
           AND (metadata->>'kind') = 'hero'
        """,
        (variant_id,),
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
    rows_inserted: Optional[int],
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
                       SET last_status     = 'error',
                           last_error      = %s,
                           last_attempt_at = now(),
                           attempt_count   = attempt_count + 1,
                           product_id      = COALESCE(product_id, %s)
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


def html_to_text(value: Optional[str]) -> str:
    if not value:
        return ""
    soup = BeautifulSoup(value, "html.parser")
    return soup.get_text(" ", strip=True)


def extract_feature_bullets(html_value: Optional[str]) -> List[str]:
    if not html_value:
        return []
    soup = BeautifulSoup(html_value, "html.parser")
    bullets = [li.get_text(" ", strip=True) for li in soup.find_all("li")]
    if bullets:
        return dedupe_strings(bullets)
    paragraphs = [
        node.get_text(" ", strip=True)
        for node in soup.find_all(["p", "span"])
        if node.get_text(strip=True)
    ]
    if paragraphs:
        return dedupe_strings(paragraphs)
    text_content = soup.get_text(" ", strip=True)
    if text_content:
        return dedupe_strings([text_content])
    return []


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
            fit_statement,
            0,
            0,
            0,
            0,
            Json({}),
            Json({"fit_statement": fit_statement}),
        ),
    )


def ingest_product_content(cur, product_id: int, product_data: dict):
    description = product_data.get("itemDescription") or {}
    care = dedupe_strings([description.get("washingInstructions")])
    fabric = dedupe_strings([description.get("composition")])
    features = extract_feature_bullets(description.get("toneOfVoice"))
    story = (
        description.get("toneOfVoiceSanitised")
        or description.get("toneOfVoiceUnformatted")
        or html_to_text(description.get("toneOfVoice"))
    )
    replace_specs(cur, product_id, "care", care, source="reiss-care")
    replace_specs(cur, product_id, "fabric", fabric, source="reiss-fabric")
    replace_specs(cur, product_id, "features", features, source="reiss-tone-of-voice")
    if story:
        replace_marketing_story(cur, product_id, story)
    fit_statement = product_data.get("fitLabel") or product_data.get("fit")
    if isinstance(fit_statement, str):
        upsert_fit_guidance(cur, product_id, fit_statement.strip())


def ingest_catalog(
    url: Optional[str],
    html_path: Optional[Path],
    *,
    spotlight_enabled: bool,
    brand_name: str,
    brand_slug: str,
    dry_run: bool,
    max_variants: Optional[int],
    force: bool,
) -> None:
    session = requests.Session()
    session.headers.update(DEFAULT_HEADERS)
    html, canonical_url = load_html(url, html_path, session)
    payload = extract_payload(html)
    base_product = extract_product_block(payload)

    style_number = (base_product.get("styleNumber") or "").upper()
    if not style_number:
        raise RuntimeError("Missing styleNumber in payload.")
    base_item_number = (base_product.get("itemNumber") or "").upper()
    item_map = base_product.get("fitsAndColourwaysItemNumberMap") or {}
    if not item_map and base_item_number:
        item_map = {
            base_item_number: {
                "colour": base_product.get("colour"),
                "fit": base_product.get("fit"),
            }
        }

    variant_payloads = gather_variant_payloads(
        canonical_url,
        base_product,
        session,
        max_variants,
    )
    variant_records = build_variant_records(
        canonical_url,
        variant_payloads,
        item_map,
        base_item_number,
    )
    if not variant_records:
        raise RuntimeError("Unable to extract variants from PDP payload.")

    color_names = [meta.get("colour") for meta in item_map.values() if meta.get("colour")]
    title = base_product.get("title") or base_product.get("productName") or "Untitled Reiss Product"
    base_name = build_base_name(title, [name for name in color_names if name])
    category = base_product.get("category") or "Uncategorized"

    hash_source = {
        "styleNumber": style_number,
        "variants": {code: variant_payloads.get(code) for code in sorted(variant_payloads.keys())},
    }
    content_hash = hashlib.sha256(
        json.dumps(hash_source, sort_keys=True).encode("utf-8")
    ).hexdigest()

    if dry_run:
        print(
            json.dumps(
                {
                    "style_number": style_number,
                    "title": title,
                    "base_name": base_name,
                    "category": category,
                    "variant_count": len(variant_records),
                    "url": canonical_url,
                },
                indent=2,
            )
        )
        return

    product_code = style_number
    if not force and record_skipped_ingest(
        "reiss_full_ingest",
        canonical_url,
        content_hash,
        product_code,
    ):
        print(f"⏭️  Skipped {style_number} — payload unchanged.")
        return

    run_id = create_ingest_run(
        source="reiss_full_ingest",
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
                    {"base": base_product, "variants": variant_payloads},
                    gender="male",
                )
                assign_canonical_category(cur, product_id, brand_id, category)
                group_slug = slugify(base_name or title)
                group_id = ensure_product_group(cur, brand_id, group_slug, base_name or title)
                ensure_group_membership(cur, group_id, product_id)
                upsert_ingestion_target(
                    cur,
                    product_id,
                    spotlight_enabled,
                    note="reiss_full_ingest",
                )
                ingest_product_content(cur, product_id, base_product)

                variant_ids: List[int] = []
                for record in variant_records:
                    variant_id = upsert_variant(cur, product_id, record)
                    variant_ids.append(variant_id)
                    replace_variant_sizes(cur, variant_id, record.size_labels)
                    replace_variant_images(
                        cur,
                        variant_id,
                        record.hero_images,
                        record.color_name,
                        set_primary=record.is_primary,
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
        mark_ingest_run_success(
            run_id,
            product_id=product_id,
            rows_inserted=len(variant_records),
        )
        check_result = ingest_checker.run_checks(product_code)
        if check_result.issues:
            issues_text = "; ".join(check_result.issues)
            raise RuntimeError(
                f"Ingest checker detected issues for {product_code}: {issues_text}"
            )
        print(f"✅ Ingested Reiss {style_number} with {len(variant_records)} variants.")
        print("   ↳ ingest_checker passed with no issues.")
    except Exception as exc:  # noqa: BLE001
        message = str(exc)
        mark_ingest_run_error(run_id, product_id=product_id, error_message=message)
        record_ingest_failure(
            canonical_url,
            "reiss_full_ingest",
            product_id=product_id,
            error_message=message,
        )
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest a Reiss PDP into fs-core.")
    parser.add_argument(
        "--url",
        help="Full Reiss PDP URL (e.g. https://www.reiss.com/us/en/style/su538118/f18163)",
    )
    parser.add_argument(
        "--html",
        type=Path,
        help="Optional path to a saved HTML document for offline parsing.",
    )
    parser.add_argument(
        "--spotlight",
        action="store_true",
        help="Mark this product as spotlight-enabled in ops.ingestion_targets.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and print metadata without touching the database.",
    )
    parser.add_argument(
        "--brand-name",
        default=DEFAULT_BRAND_NAME,
        help="Override the brand name (defaults to Reiss).",
    )
    parser.add_argument(
        "--brand-slug",
        default=DEFAULT_BRAND_SLUG,
        help="Override the brand slug (defaults to reiss).",
    )
    parser.add_argument(
        "--max-variants",
        type=int,
        help="Optional limit on the number of colourway fetches (useful for testing).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force ingest even if content hash matches a previous success.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    ingest_catalog(
        args.url,
        args.html,
        spotlight_enabled=args.spotlight,
        brand_name=args.brand_name,
        brand_slug=args.brand_slug,
        dry_run=args.dry_run,
        max_variants=args.max_variants,
        force=args.force,
    )


if __name__ == "__main__":
    main()

