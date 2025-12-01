### Operations: Connecting and Working with Supabase (tailor3)

This project uses a Supabase-hosted Postgres database referred to as "tailor3".

#### Connection

- Host: `aws-1-us-east-1.pooler.supabase.com`
- Port: `6543`
- Database: `postgres`
- User: `fs_core_rw`
- Password: stored in env var `DB_PASSWORD` (see `.env`)

Use `db_config.py` for consistent access in Python scripts and for `psql` shell env:

- File: `db_config.py`
- Exports `DB_CONFIG` (psycopg2/asyncpg dict) and `PSQL_ENV`
- Helper: `get_psql_command()` prints a ready-to-run `psql` command with env

Example `psql` session:

```bash
# from repo root
python3 -c 'import db_config; print(db_config.get_psql_command())' | bash
```

#### Environment Variables

- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- Loaded via `dotenv` in many scripts (see `db_config.py`, `scrapers/config/database.py`)

#### Python Clients

- `psycopg2` with `RealDictCursor` for row dicts (most scripts)
- `asyncpg` used by `src/ios_app/Backend/app.py` for pooled async operations

Typical sync usage:

```python
from db_config import DB_CONFIG
import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor(cursor_factory=RealDictCursor)
cur.execute("SELECT 1")
print(cur.fetchone())
```

Typical async usage (excerpt from backend):

```python
import asyncpg
from db_config import DB_CONFIG

pool = await asyncpg.create_pool(**DB_CONFIG)
async with pool.acquire() as conn:
    row = await conn.fetchrow("SELECT 1 as ok")
```

#### Tooling and Scripts

- Schema snapshots and evolution:
  - `scripts/database/schema_evolution.py` (diffs and writes markdown)
  - `scripts/development/get_complete_schema.sh` (table structures)
  - `scripts/database/db_snapshot.py` (JSON snapshot of counts/relations)
- Admin/data ops helpers (selected):
  - `scripts/database/normalize_existing_products.py`
  - `scripts/database/remove_length_feedback.py`
  - `scripts/database/simple_user_cleanup.py`
  - `scripts/safe_db_update.py` (UPSERTs for cache)
  - `scripts/python_tools/quick_sql.py` and `easy_sql.py`

#### Notes

- The legacy local `tailor2` database is deprecated. Always use tailor3 (Supabase).
- Some older docs mention `size_guides`; current system prefers `measurement_sets` + `measurements`.



