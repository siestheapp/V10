#!/usr/bin/env python3
"""
Reliable downloader for Lululemon module-federation remoteEntry bundles.

The men's dress pants PDP payload exposed the `configs.rvmOverrides.subapps`
map, which lists every micro-frontend (pdp-app, cdp-app, size-guide-app, etc.)
and its current version. Each entry hosts a webpack remote at:

    https://shop.lululemon.com/static/uf/<subapp>/<version>/static/chunks/remoteEntry.js

Direct `curl`/`requests` calls routinely trip Akamai, so this helper mirrors the
`lululemon_pdp_dump` approach: try `requests` first, then fall back to a real
Chromium session (Playwright) that warms the homepage before requesting the
bundle. The JS is saved under `data/tmp/remotes/<subapp>-<version>.js` so we can
scan it for persisted GraphQL query hashes offline.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

REQUESTS_IMPORT_ERROR = None
try:
    import requests
except Exception as exc:  # noqa: N816
    REQUESTS_IMPORT_ERROR = exc
    requests = None  # type: ignore[assignment]

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "tmp" / "remotes"
REMOTE_URL_TEMPLATE = "https://shop.lululemon.com/static/uf/{subapp}/{version}/static/chunks/remoteEntry.js"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": "text/javascript,application/javascript;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Referer": "https://shop.lululemon.com/",
}


@dataclass(frozen=True)
class RemoteModule:
    """Small helper describing one module federation remote."""

    name: str
    version: str

    @property
    def url(self) -> str:
        return REMOTE_URL_TEMPLATE.format(subapp=self.name, version=self.version)

    @property
    def filename(self) -> str:
        safe_version = self.version.replace("/", "_")
        return f"{self.name}-{safe_version}.js"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Lululemon module-federation remoteEntry bundles with Playwright fallback."
    )
    parser.add_argument(
        "--payload",
        type=Path,
        help="Optional __NEXT_DATA__ JSON file to auto-discover subapps + versions.",
    )
    parser.add_argument(
        "--include",
        action="append",
        metavar="SUBAPP",
        help="Limit payload-derived modules to these subapp names (can be repeated).",
    )
    parser.add_argument(
        "--module",
        action="append",
        metavar="SUBAPP=VERSION",
        help="Explicit module(s) to fetch (e.g. --module pdp-app=2.3.57).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to store bundles (default: {DEFAULT_OUTPUT_DIR}).",
    )
    parser.add_argument(
        "--no-playwright",
        action="store_true",
        help="Disable Playwright fallback (fail fast if requests is blocked).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download bundles even if the destination file already exists.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print the resolved module list and exit without downloading.",
    )
    return parser.parse_args(argv)


def parse_module_arg(raw: str) -> RemoteModule:
    if "=" not in raw:
        raise argparse.ArgumentTypeError(f"Expected SUBAPP=VERSION, got: {raw}")
    name, version = [part.strip() for part in raw.split("=", 1)]
    if not name or not version:
        raise argparse.ArgumentTypeError(f"Invalid module specification: {raw}")
    return RemoteModule(name=name, version=version)


def modules_from_payload(payload_path: Path, include: Optional[Iterable[str]]) -> List[RemoteModule]:
    data = json.loads(payload_path.read_text(encoding="utf-8"))
    configs = data.get("props", {}).get("pageProps", {}).get("configs", {})
    overrides = configs.get("rvmOverrides", {})
    subapps = overrides.get("subapps") or {}
    if not subapps:
        raise RuntimeError("Payload missing configs.rvmOverrides.subapps; cannot derive modules.")
    include_set = {name.strip() for name in include or [] if name.strip()}
    modules: List[RemoteModule] = []
    for name, meta in subapps.items():
        if include_set and name not in include_set:
            continue
        version = (meta or {}).get("version")
        if not version:
            print(f"⚠️  Skipping {name!r}: missing version field.")
            continue
        modules.append(RemoteModule(name=name, version=str(version)))
    return modules


def dedupe(modules: Iterable[RemoteModule]) -> List[RemoteModule]:
    seen: set[Tuple[str, str]] = set()
    ordered: List[RemoteModule] = []
    for module in modules:
        key = (module.name, module.version)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(module)
    return ordered


def resolve_modules(args: argparse.Namespace) -> List[RemoteModule]:
    modules: List[RemoteModule] = []
    if args.module:
        modules.extend(parse_module_arg(raw) for raw in args.module)
    if args.payload:
        modules.extend(modules_from_payload(args.payload, args.include))
    if not modules:
        raise RuntimeError("No modules specified. Use --module and/or --payload.")
    return dedupe(modules)


def fetch_remote_entry(url: str, *, allow_playwright: bool) -> str:
    if requests is not None:
        session = requests.Session()
        session.headers.update(REQUEST_HEADERS)
        try:
            resp = session.get(url, timeout=45)
            if resp.status_code == 200 and resp.text.strip():
                return resp.text
            print(f"⚠️  requests got {resp.status_code} for {url}; falling back to Playwright…")
        except Exception as exc:  # noqa: BLE001
            print(f"⚠️  requests error for {url}: {exc}; falling back to Playwright…")
    elif REQUESTS_IMPORT_ERROR:
        print(
            "⚠️  requests unavailable "
            f"({REQUESTS_IMPORT_ERROR}); falling back to Playwright for all downloads."
        )

    if not allow_playwright:
        raise RuntimeError("Playwright fallback disabled and requests failed or unavailable.")

    return fetch_via_playwright(url)


def fetch_via_playwright(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-http2"])
        context = browser.new_context(
            user_agent=REQUEST_HEADERS["User-Agent"],
            locale="en-US",
            timezone_id="America/New_York",
        )
        page = context.new_page()
        try:
            page.goto(
                "https://shop.lululemon.com/",
                wait_until="domcontentloaded",
                timeout=60000,
            )
            page.wait_for_timeout(1500)
        except PlaywrightTimeoutError as exc:
            print(
                f"⚠️  Homepage warm-up timed out ({exc}); continuing directly to remote bundle."
            )
        response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
        if response is None:
            browser.close()
            raise RuntimeError(f"Playwright failed to receive a response for {url}")
        text = response.text()
        browser.close()
        if not text.strip():
            raise RuntimeError(f"Empty response body received for {url}")
        return text


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    try:
        modules = resolve_modules(args)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ {exc}")
        sys.exit(1)

    if args.list:
        print(f"📦 Resolved {len(modules)} module(s):")
        for module in modules:
            print(f" - {module.name}@{module.version} → {module.url}")
        return

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    allow_playwright = not args.no_playwright

    for module in modules:
        destination = output_dir / module.filename
        if destination.exists() and not args.force:
            print(f"⏭️  {module.name}@{module.version} already exists ({destination}); skipping. Use --force to overwrite.")
            continue

        print(f"⬇️  Fetching {module.name}@{module.version}…")
        content = fetch_remote_entry(module.url, allow_playwright=allow_playwright)
        destination.write_text(content, encoding="utf-8")
        rel_path = destination.relative_to(PROJECT_ROOT)
        print(f"   ↳ saved {len(content)} bytes to {rel_path}")


if __name__ == "__main__":
    main()

