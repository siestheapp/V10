#!/usr/bin/env python3
import re, json, sys, time, socket
import urllib.parse, urllib.request

# --- Settings ---------------------------------------------------------------
INDEXES = [
    "https://www.jcrew.com/sitemap/sitemap-index.xml",
    "https://www.jcrew.com/buy/sitemap.xml",
]
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/124.0.0.0 Safari/537.36")

socket.setdefaulttimeout(20)
MAX_RETRIES = 3
BASE_BACKOFF = 0.5
REQUEST_TIMEOUT = 10
ONLY_CATEGORY_MAPS = True  # skip huge product maps

# --- Proxy helper (avoids Akamai 403) ---------------------------------------
def via_proxy(url: str) -> str:
    u = urllib.parse.urlparse(url)
    inner = f"http://{u.netloc}{u.path}"
    if u.query:
        inner += f"?{u.query}"
    return f"https://r.jina.ai/{inner}"

def fetch_text(url: str, retry=MAX_RETRIES, backoff=BASE_BACKOFF) -> str:
    last = None
    proxied = via_proxy(url)
    for i in range(retry):
        try:
            req = urllib.request.Request(proxied, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as r:
                return r.read().decode("utf-8", errors="replace")
        except Exception as e:
            last = e
            time.sleep(backoff * (1.6 ** i))
    raise RuntimeError(f"Failed to fetch {url}: {last}")

# --- URL extraction ----------------------------------------------------------
RE_URL = re.compile(r"https?://[^\s\"'<>()]+", re.I)

def urls_from_index_text(txt: str):
    urls = [u for u in RE_URL.findall(txt)
            if u.startswith("https://www.jcrew.com/") and (u.endswith(".xml") or u.endswith(".xml.gz"))]
    if ONLY_CATEGORY_MAPS:
        urls = [u for u in urls if "-category.xml" in u]
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u); out.append(u)
    return out

def urls_from_child_sitemap_text(txt: str):
    urls = [u for u in RE_URL.findall(txt) if u.startswith("https://www.jcrew.com/")]
    seen, out = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u); out.append(u)
    return out

# --- Category path extraction (robust to /m/ and /plp/) ----------------------
def extract_paths_after_categories(all_urls):
    """
    Return:
      mens_paths: set of 'a/b/c...' (segments after 'categories/')
      womens_paths: same
    We detect gender by looking for 'mens' or 'womens' anywhere BEFORE 'categories' in the path.
    """
    mens_paths, womens_paths = set(), set()

    for url in all_urls:
        p = urllib.parse.urlparse(url).path  # ignore query; categories are path-based
        # split into segments and find 'categories'
        segs = [s for s in p.strip("/").split("/") if s]
        if "categories" not in segs:
            continue
        cat_idx = segs.index("categories")
        after = segs[cat_idx+1:]
        if not after:
            continue
        # find gender anywhere before categories
        prior = set(segs[:cat_idx])
        gender = "mens" if "mens" in prior else ("womens" if "womens" in prior else None)
        if not gender:
            continue  # skip if we didn't find gender
        path = "/".join(after)
        if not path:
            continue
        if gender == "mens":
            mens_paths.add(path)
        else:
            womens_paths.add(path)

    return mens_paths, womens_paths

def write_txt(path, items):
    with open(path, "w", encoding="utf-8") as f:
        for x in sorted(items):
            f.write(x + "\n")

def write_levels(prefix, paths):
    """
    Given a set of 'a/b/c/...' strings, write level1/2/3 unique slug lists.
    """
    lvl1, lvl2, lvl3 = set(), set(), set()
    for p in paths:
        segs = p.split("/")
        if len(segs) >= 1: lvl1.add(segs[0])
        if len(segs) >= 2: lvl2.add(segs[1])
        if len(segs) >= 3: lvl3.add(segs[2])
    write_txt(f"{prefix}_level1.txt", lvl1)
    write_txt(f"{prefix}_level2.txt", lvl2)
    write_txt(f"{prefix}_level3.txt", lvl3)

def main():
    # 1) Find the category sitemap(s)
    child_maps = []
    for idx in INDEXES:
        try:
            txt = fetch_text(idx)
            maps = urls_from_index_text(txt)
            child_maps.extend(maps)
        except Exception as e:
            print(f"warn index fetch {idx}: {e}", file=sys.stderr)

    if not child_maps:
        print("No category sitemaps found (proxy blocked?).", file=sys.stderr)
        sys.exit(1)

    # 2) Gather URLs from category sitemaps (small, fast)
    all_urls = []
    for sm in dict.fromkeys(child_maps):  # dedup preserve order
        try:
            txt = fetch_text(sm)
            locs = urls_from_child_sitemap_text(txt)
            all_urls.extend(locs)
        except Exception as e:
            print(f"warn child map {sm}: {e}", file=sys.stderr)

    # 3) Extract men/women category paths, robust to /plp/, /m/
    mens_paths, womens_paths = extract_paths_after_categories(all_urls)

    # 4) Write outputs
    write_txt("mens_paths.txt", mens_paths)
    write_txt("womens_paths.txt", womens_paths)
    write_levels("mens", mens_paths)
    write_levels("womens", womens_paths)

    print("Done.")
    print(f"Mens paths:   {len(mens_paths)} → mens_paths.txt (and mens_level1/2/3.txt)")
    print(f"Womens paths: {len(womens_paths)} → womens_paths.txt (and womens_level1/2/3.txt)")

if __name__ == "__main__":
    main()
