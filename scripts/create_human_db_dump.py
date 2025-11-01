#!/usr/bin/env python3
"""
Create a human-readable, full database dump of the Freestyle database

Outputs a dated text file at repo root: tailor3_dump_<YYYY-MM-DD>.txt
"""

import json
from datetime import datetime
from typing import List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

from db_config import DB_CONFIG


def format_value(value):
    if value is None:
        return "null"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def get_public_tables(cursor) -> List[str]:
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        ORDER BY table_name
        """
    )
    rows = cursor.fetchall()
    return [r["table_name"] for r in rows]


def get_columns(cursor, table: str) -> List[str]:
    cursor.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema='public' AND table_name=%s
        ORDER BY ordinal_position
        """,
        (table,),
    )
    return [r["column_name"] for r in cursor.fetchall()]


def get_primary_key(cursor, table: str) -> Optional[str]:
    cursor.execute(
        """
        SELECT a.attname AS col
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary
        """,
        (f"public.{table}",),
    )
    row = cursor.fetchone()
    return row["col"] if row else None


def dump_table(cursor, f, table: str):
    # Header with count
    cursor.execute(f"SELECT COUNT(*) AS c FROM public.{table}")
    total = cursor.fetchone()["c"]

    f.write(f"\n{'-'*80}\n")
    f.write(f"TABLE: {table}  (rows: {total})\n")
    f.write(f"{'-'*80}\n\n")

    if total == 0:
        return

    # Column ordering and sort preference
    columns = get_columns(cursor, table)
    pk = get_primary_key(cursor, table)
    order_col = pk or ("id" if "id" in columns else columns[0])

    # Stream rows
    cursor.execute(f"SELECT * FROM public.{table} ORDER BY {order_col}")
    rows = cursor.fetchall()

    for idx, row in enumerate(rows, 1):
        f.write(f"[{idx}]\n")
        for col in columns:
            val = format_value(row.get(col))
            if "\n" in val:
                f.write(f"  {col}:\n")
                for line in val.splitlines():
                    f.write(f"    {line}\n")
            else:
                f.write(f"  {col}: {val}\n")
        f.write("\n")


def create_dump() -> str:
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    cur = conn.cursor()

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"tailor3_dump_{today}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            # Header
            f.write("=" * 80 + "\n")
            f.write("TAILOR3 — HUMAN-READABLE DATABASE DUMP\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")

            # Overview: counts per table
            f.write("OVERVIEW\n")
            f.write("-" * 80 + "\n")
            tables = get_public_tables(cur)
            for t in tables:
                cur.execute(f"SELECT COUNT(*) AS c FROM public.{t}")
                c = cur.fetchone()["c"]
                f.write(f"  {t:.<40} {c:>8} rows\n")
            f.write("\n\n")

            # Full data per table
            for t in tables:
                dump_table(cur, f, t)

            # Footer
            f.write("\n" + "=" * 80 + "\n")
            f.write("END OF DUMP\n")
            f.write("=" * 80 + "\n")

        return filename
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    print("Creating FreestyleDB dump...")
    out = create_dump()
    print(f"✅ Created: {out}")


