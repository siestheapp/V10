#!/usr/bin/env python3
"""
Scrape a J.Crew PDP and populate fs-core spotlight tables.

Baseline data written for every run:
  - product specs (tech bullets, style descriptors, item code)
  - sustainability badges
  - fit guidance summary + true-to-size metadata
  - review aggregates (average rating, histogram)

When the target product is marked as spotlight in ops.ingestion_targets,
also persists long-form marketing copy and the AI-powered review summary.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

import psycopg2
from psycopg2.extras import Json
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from db_config import DB_CONFIG

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/129.0.0.0 Safari/537.36"
)

REQUEST_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}


@dataclass
class ProductContent:
    product_code: str
    title: str
    marketing_story: str
    tech_bullets: List[str]
    fit_notes: List[str]
    item_code: str
    style_descriptors: List[str]
    sustainability_badges: List[Dict[str, str]]
    fit_statement: Optional[str]
    fit_sample_size: Optional[int]
    review_stats: Dict[str, object]
    review_summary: Optional[str]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def ensure_db_config():
    missing = [k for k, v in DB_CONFIG.items() if not v]
    if missing:
        raise SystemExit(
            f"❌ Missing database configuration for: {', '.join(missing)}. "
            "Set DB_NAME/DB_USER/DB_PASSWORD/DB_HOST/DB_PORT in .env."
        )


def fetch_html_via_playwright(url: str) -> str:
    url = canonicalize_url(url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=USER_AGENT,
            extra_http_headers={
                k: v for k, v in REQUEST_HEADERS.items() if k.lower() != "user-agent"
            },
        )
        page = context.new_page()
        page.goto("https://www.jcrew.com", wait_until="domcontentloaded", timeout=40000)
        # Some PDPs (especially tuxedo styles) take longer to satisfy Akamai/BotMan checks.
        page.goto(url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_selector("script#__NEXT_DATA__", timeout=90000, state="attached")
        html = page.content()
        browser.close()
        return html


def canonicalize_url(url: str) -> str:
    """
    J.Crew mobile PDPs use /m/... paths that sometimes omit structured data.
    Strip the /m prefix so we always hit the desktop PDP which includes
    marketing copy, specs, and complete review payloads.
    """
    parts = urlsplit(url)
    path = parts.path
    query_params = parse_qs(parts.query, keep_blank_values=True)
    color_product_code = (query_params.get("colorProductCode") or [None])[0]
    segments = [seg for seg in path.split("/") if seg]
    if segments and segments[0] == "m":
        segments[0] = "p"
        if color_product_code:
            segments[-1] = color_product_code
            query_params.pop("colorProductCode", None)
        path = "/" + "/".join(segments)
    new_query = urlencode(query_params, doseq=True)
    return urlunsplit((parts.scheme or "https", parts.netloc, path, new_query, parts.fragment))


def fetch_html(url: str) -> str:
    url = canonicalize_url(url)
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    # Prime Akamai/BotMan cookies by hitting the homepage first.
    session.get("https://www.jcrew.com", timeout=30)
    session.headers["Referer"] = "https://www.jcrew.com/"
    resp = session.get(url, timeout=30)
    if resp.status_code == 403:
        print("⚠️  Received 403 from J.Crew, retrying via Playwright…")
        return fetch_html_via_playwright(url)
    resp.raise_for_status()
    return resp.text


def extract_next_data(soup: BeautifulSoup) -> dict:
    script = soup.find("script", id="__NEXT_DATA__")
    if not script:
        raise RuntimeError("Unable to locate __NEXT_DATA__ payload on page")
    return json.loads(script.string)


def extract_style_descriptors(soup: BeautifulSoup) -> List[str]:
    container = soup.select_one("div[class*='ProductSeoLilyKeywords']")
    if not container:
        return []
    descriptors: List[str] = []
    for node in container.find_all(["button", "span", "div"]):
        text = node.get_text(strip=True)
        if not text:
            continue
        if "how we'd describe this style" in text.lower():
            continue
        if len(text) > 50:
            continue
        if text not in descriptors:
            descriptors.append(text)
    return descriptors


def extract_badges(soup: BeautifulSoup, eco_labels: Sequence[str]) -> List[Dict[str, str]]:
    badges: List[Dict[str, str]] = []
    for node in soup.select("div[class*='sustainability-badges']"):
        text_chunks = [chunk.strip() for chunk in node.stripped_strings]
        if not text_chunks:
            continue
        label = text_chunks[0]
        description = " ".join(text_chunks[1:]) if len(text_chunks) > 1 else ""
        badges.append(
            {
                "label": label,
                "description": description,
            }
        )

    # Ensure eco labels from JSON are present even if badge markup missing
    existing_labels = {badge["label"] for badge in badges}
    for label in eco_labels:
        if label not in existing_labels:
            badges.append({"label": label, "description": ""})
    return badges


def extract_fit_statement(soup: BeautifulSoup) -> tuple[Optional[str], Optional[int]]:
    header = soup.find(string=re.compile(r"Size\s*&\s*Fit", re.I))
    if not header:
        return None, None
    section = header.find_parent("section") or header.find_parent("div")
    if not section:
        return None, None
    text = " ".join(section.stripped_strings)
    match = re.search(
        r"Fits\s+([^.]+?)\s+based on\s+(\d+)\s+customer reviews", text, re.I
    )
    if not match:
        return None, None
    phrase = match.group(1).strip()
    try:
        votes = int(match.group(2))
    except ValueError:
        votes = None
    return phrase, votes


def load_pdp_payload(url: str) -> Tuple[BeautifulSoup, dict]:
    html = fetch_html(url)
    soup = BeautifulSoup(html, "html.parser")
    next_data = extract_next_data(soup)
    return soup, next_data


def parse_product_content(
    url: str,
    *,
    soup: Optional[BeautifulSoup] = None,
    next_data: Optional[dict] = None,
) -> ProductContent:
    if soup is None or next_data is None:
        soup, next_data = load_pdp_payload(url)
    initial_state = next_data["props"]["initialState"]
    product_map = initial_state["products"]["productsByProductCode"]

    product_code = next_data.get("query", {}).get("productCode")
    if not product_code and product_map:
        product_code = next(iter(product_map.keys()))
    if not product_code or product_code not in product_map:
        raise RuntimeError("Unable to determine product code from PDP payload")

    product = product_map[product_code]
    title = product.get("productName") or soup.find("h1").get_text(strip=True)

    marketing_story = (product.get("productDescriptionRomance") or "").strip()
    tech_bullets = product.get("productDescriptionTech") or []
    fit_notes = product.get("productDescriptionFit") or []
    if product.get("productDescriptionFitAdditionalText"):
        fit_notes.extend(product["productDescriptionFitAdditionalText"])

    style_descriptors = extract_style_descriptors(soup)
    badges = extract_badges(soup, product.get("c_styleEco") or [])

    fit_statement, sample_size = extract_fit_statement(soup)

    reviews_state = initial_state["reviews"]["products"].get(product_code, {})
    review_summary = initial_state["reviews"].get("reviewsSummary", {}).get(product_code)
    ratings_distribution = {
        int(star): count for star, count in (reviews_state.get("ratingsDistribution") or {}).items()
    }
    review_stats = {
        "average_rating": reviews_state.get("averageRating"),
        "total_reviews": reviews_state.get("totalReviews"),
        "ratings_distribution": ratings_distribution,
    }

    item_code = product_code
    return ProductContent(
        product_code=product_code,
        title=title,
        marketing_story=marketing_story,
        tech_bullets=tech_bullets,
        fit_notes=fit_notes,
        item_code=item_code,
        style_descriptors=style_descriptors,
        sustainability_badges=badges,
        fit_statement=fit_statement,
        fit_sample_size=sample_size,
        review_stats=review_stats,
        review_summary=review_summary,
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


def fetch_product_metadata(cur, product_code: str) -> tuple[int, bool]:
    cur.execute(
        "SELECT id FROM core.products WHERE product_code = %s",
        (product_code,),
    )
    row = cur.fetchone()
    if not row:
        raise RuntimeError(f"Product {product_code} not found in core.products")
    product_id = row[0]

    cur.execute(
        "SELECT spotlight FROM ops.ingestion_targets WHERE product_id = %s",
        (product_id,),
    )
    spotlight_row = cur.fetchone()
    spotlight = bool(spotlight_row and spotlight_row[0])
    return product_id, spotlight


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


def replace_badges(cur, product_id: int, badges: Sequence[Dict[str, str]]):
    cur.execute("DELETE FROM core.product_badges WHERE product_id = %s", (product_id,))
    for badge in badges:
        label = badge.get("label")
        if not label:
            continue
        code = slugify(label)
        cur.execute(
            "SELECT core.upsert_product_badge(%s,%s,%s,%s);",
            (
                product_id,
                code,
                Json({"label": label, "description": badge.get("description", "")}),
                "pdp",
            ),
        )


def upsert_fit_guidance(
    cur,
    product_id: int,
    fit_label: Optional[str],
    fit_statement: Optional[str],
    sample_size: Optional[int],
):
    # Ensure only one variant-agnostic record exists (NULL variant skips ON CONFLICT)
    cur.execute(
        "DELETE FROM core.product_fit_guidance WHERE product_id = %s AND variant_id IS NULL",
        (product_id,),
    )
    cur.execute(
        "SELECT core.upsert_product_fit_guidance(%s,%s,%s,%s,%s,%s,%s,%s,%s);",
        (
            product_id,
            None,  # variant agnostic
            fit_label.strip() if fit_label else None,
            0,
            sample_size or 0,
            0,
            sample_size or 0,
            Json({}),
            Json(
                {
                    "fit_statement": fit_statement,
                }
            ),
        ),
    )


def upsert_review_stats(cur, product_id: int, stats: Dict[str, object]):
    cur.execute(
        "SELECT core.upsert_product_review_stats(%s,%s,%s,%s);",
        (
            product_id,
            stats.get("average_rating"),
            stats.get("total_reviews"),
            Json(stats.get("ratings_distribution") or {}),
        ),
    )


def replace_review_summary(cur, product_id: int, summary: str):
    if not summary:
        return
    cur.execute(
        """
        DELETE FROM core.product_review_summaries
        WHERE product_id = %s AND summary_type = %s
        """,
        (product_id, "ai_summary"),
    )
    cur.execute(
        "SELECT core.upsert_product_review_summary(%s,%s,%s,%s);",
        (product_id, "ai_summary", summary.strip(), None),
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


def ingest(content: ProductContent, *, dry_run: bool = False):
    if dry_run:
        print(json.dumps(content.__dict__, indent=2))
        return

    with connect() as conn:
        with conn.cursor() as cur:
            product_id, spotlight = fetch_product_metadata(cur, content.product_code)

            replace_specs(
                cur,
                product_id,
                "tech",
                content.tech_bullets,
                source="pdp-tech",
            )
            replace_specs(
                cur,
                product_id,
                "style_descriptor",
                content.style_descriptors,
                source="pdp-style-descriptor",
            )
            replace_specs(
                cur,
                product_id,
                "item_code",
                [content.item_code],
                source="pdp-meta",
            )

            replace_badges(cur, product_id, content.sustainability_badges)
            upsert_fit_guidance(
                cur,
                product_id,
                content.fit_notes[0] if content.fit_notes else None,
                content.fit_statement,
                content.fit_sample_size or content.review_stats.get("total_reviews"),
            )
            upsert_review_stats(cur, product_id, content.review_stats)

            if spotlight:
                replace_review_summary(cur, product_id, content.review_summary or "")
                replace_marketing_story(cur, product_id, content.marketing_story)

            conn.commit()
            print(
                f"✅ Ingested PDP content for {content.product_code} "
                f"({'spotlight' if spotlight else 'baseline'})"
            )


def main():
    parser = argparse.ArgumentParser(
        description="Scrape J.Crew PDP content and ingest spotlight metadata."
    )
    parser.add_argument(
        "--url",
        required=True,
        help="Product detail page URL (J.Crew PDP)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print extracted payload without writing to the database",
    )
    args = parser.parse_args()

    content = parse_product_content(args.url)
    ingest(content, dry_run=args.dry_run)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover
        print(f"❌ {exc}", file=sys.stderr)
        sys.exit(1)


