"""
Top-level package for ingestion and data scripts.

This file exists so that we can treat `scripts` as a proper Python package and
create brand-specific subpackages like `scripts.brands.lululemon`. Existing
CLI entrypoints (e.g. `python scripts/lululemon_full_ingest.py`) continue to
work as before.
"""



