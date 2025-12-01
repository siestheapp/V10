"""
Lululemon brand module.

This subpackage exposes a stable API around the existing
`scripts/lululemon_full_ingest.py` implementation so that other code can
import Lululemon ingest helpers without depending on CLI script layout.

Over time, brand-specific orchestration (PDP/category entrypoints, Playwright
helpers, etc.) can move in here, while the legacy CLI scripts remain as thin
wrappers for backwards compatibility.
"""

from __future__ import annotations

from typing import Optional, Sequence
from pathlib import Path

from scripts import lululemon_full_ingest as _impl

# Re-export core constants so callers can treat this as the canonical module.
DEFAULT_BRAND_NAME = _impl.DEFAULT_BRAND_NAME
DEFAULT_BRAND_SLUG = _impl.DEFAULT_BRAND_SLUG
BASE_HOST = _impl.BASE_HOST


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
    """
    Thin wrapper around `lululemon_full_ingest.ingest_catalog`.

    This keeps the public API stable even if we later refactor the underlying
    implementation or move it into this package.
    """
    return _impl.ingest_catalog(
        url,
        payload_path,
        allow_playwright=allow_playwright,
        spotlight_enabled=spotlight_enabled,
        brand_name=brand_name,
        brand_slug=brand_slug,
        dry_run=dry_run,
        graphql_response_path=graphql_response_path,
        graphql_response=graphql_response,
        run_checks=run_checks,
    )


__all__ = [
    "DEFAULT_BRAND_NAME",
    "DEFAULT_BRAND_SLUG",
    "BASE_HOST",
    "ingest_catalog",
]



