# SCHEMA_EVOLUTION.md

This file tracks all schema and structural changes to the `tailor2` database, including migrations, optimizations, and manual changes. Update this file whenever you make a schema change (via migration, SQL, or GUI).

---

## [2025-06-28 17:04:21] Schema Check - No Changes

**Schema snapshot:** `SCHEMA_20250628_170421.sql`

No schema changes detected since last snapshot.

---
## [2025-06-28 01:53:14] Schema Check - No Changes

**Schema snapshot:** `SCHEMA_20250628_015314.sql`

No schema changes detected since last snapshot.

---
## [2025-06-28 00:19:20] Schema Check - No Changes

**Schema snapshot:** `SCHEMA_20250628_001920.sql`

No schema changes detected since last snapshot.

---
## [2024-06-28 01:35] Baseline Schema Snapshot

**Schema captured as baseline for future evolution tracking.**

- See `SCHEMA_BASELINE_20240628.sql` for the full schema at this point in time.

---

## How to Add a New Entry

1. Add a timestamped heading:
   ```
   ## [YYYY-MM-DD HH:MM] <Short Description>
   ```
2. Describe the change and why it was made.
3. Include the SQL or migration code if possible.
4. Optionally, link to a full schema snapshot if you took one.

---

## [Next Change]

(Add your next schema change here)

### [2025-06-28] Added center_back_length to size_guides_v2 and created size_guide_column_history

- Added column: center_back_length (DOUBLE PRECISION, nullable) to size_guides_v2.
  - Motivation: NN07 Clive 3323 Tee size guide includes back length as a key measurement. [Source](https://www.nn07.com/en/us/clive-3323-tee-black?srsltid=AfmBOoqauc-celIg7PQE6PR2zH_bWNoW4FrYoyYJm56VeHrQIRUSD0Yo)
  - Added by: SRD
- Added table: size_guide_column_history to track new columns, associated brands, reasons, and source URLs.
  - Columns: column_name, brand_id, brand_name, date_added, reason, added_by, source_url 