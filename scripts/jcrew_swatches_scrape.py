#!/usr/bin/env python3
"""
Extract color swatch names and image URLs from a J.Crew PDP.

Usage:
  python scripts/jcrew_swatches_scrape.py --url "<pdp_url>" [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

import requests
from bs4 import BeautifulSoup


@dataclass
class Swatch:
    color: str
    swatch_url: str


def fetch_html(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text


def extract_url_from_style(style_val: str) -> Optional[str]:
    # background-image:url("...") or url(...)
    if not style_val:
        return None
    m = re.search(r'url\\([\'"]?([^\\)\'"]+)[\'"]?\\)', style_val, re.IGNORECASE)
    return m.group(1) if m else None


def normalize_color_name(txt: str) -> str:
    return re.sub(r"\\s+", " ", txt or "").strip()


def parse_swatches(html: str) -> List[Swatch]:
    soup = BeautifulSoup(html, "html.parser")
    results: List[Swatch] = []
    seen: set[Tuple[str, str]] = set()

    # Heuristics:
    # - swatch chips often contain img elements with 'swatch' in src
    # - or buttons/divs with aria-label/color name and background-image style
    # Try multiple strategies; keep first valid url per color.

    # Strategy 1: <img> tags with 'swatch' in src
    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if not src:
            continue
        if "swatch" not in src.lower():
            continue
        alt = normalize_color_name(img.get("alt") or img.get("aria-label") or img.get("title") or "")
        # Parent may carry color text
        if not alt:
            parent_title = img.find_parent(attrs={"aria-label": True})
            if parent_title:
                alt = normalize_color_name(parent_title.get("aria-label", ""))
        if not alt:
            continue
        key = (alt.lower(), src)
        if key in seen:
            continue
        seen.add(key)
        results.append(Swatch(color=alt, swatch_url=src))

    # Strategy 2: elements with background-image and aria-label/title
    candidates = soup.select("[style*='background-image'], [style*='background-image'] *")
    for el in candidates:
        style_val = el.get("style") or ""
        url = extract_url_from_style(style_val)
        if not url:
            continue
        label = normalize_color_name(el.get("aria-label") or el.get("title") or "")
        if not label:
            # try parent
            p = el.find_parent(attrs={"aria-label": True})
            if p:
                label = normalize_color_name(p.get("aria-label", ""))
        if not label:
            # look for sibling text
            txt = el.get_text(" ", strip=True)
            if txt:
                label = normalize_color_name(txt)
        if not label:
            continue
        key = (label.lower(), url)
        if key in seen:
            continue
        seen.add(key)
        results.append(Swatch(color=label, swatch_url=url))

    # Deduplicate by color (keep first URL)
    dedup: dict[str, Swatch] = {}
    for s in results:
        k = s.color.lower()
        if k not in dedup:
            dedup[k] = s
    return list(dedup.values())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--json", action="store_true", help="Output JSON to stdout")
    args = ap.parse_args()

    html = fetch_html(args.url)
    swatches = parse_swatches(html)
    if args.json:
        print(json.dumps([asdict(s) for s in swatches], indent=2))
    else:
        for s in swatches:
            print(f"{s.color}\\t{s.swatch_url}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)



