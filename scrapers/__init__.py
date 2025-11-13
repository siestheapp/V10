import importlib
import sys

# Legacy import shim for the scrapers package.
# Routes old 'scrapers.*' imports to 'scripts.scrapers_pkg.*'.
_base_pkg = "scripts.scrapers_pkg"
_legacy_submodules = [
    "config",
    "models",
    "utils",
    "web_interface",
    "scripts",
    "scrapers",
    "base_scraper",  # legacy: scrapers.base_scraper
    "banana_republic",  # legacy: scrapers.banana_republic
    "jcrew",  # legacy: scrapers.jcrew
    "scrapers.banana_republic",
    "scrapers.jcrew",
    "scrapers.base_scraper",
]

for name in _legacy_submodules:
    try:
        # Resolve to scripts.scrapers_pkg.<name> or scripts.scrapers_pkg.scrapers.<name>
        try:
            mod = importlib.import_module(f"{_base_pkg}.{name}")
        except ModuleNotFoundError:
            mod = importlib.import_module(f"{_base_pkg}.scrapers.{name}")
        sys.modules[f"scrapers.{name}"] = mod
    except Exception:
        # Leave unresolved if the submodule is missing; consumers may not need it.
        pass


