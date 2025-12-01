#!/usr/bin/env python3
"""Check constraints on garment_guides table"""

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    database='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543',
    cursor_factory=RealDictCursor
)
cur = conn.cursor()

# Check constraints
cur.execute("""
    SELECT conname, pg_get_constraintdef(oid) 
    FROM pg_constraint 
    WHERE conrelid = 'garment_guides'::regclass 
    AND contype = 'c'
""")

print("Check constraints on garment_guides:")
for row in cur.fetchall():
    print(f"  {row['conname']}: {row['pg_get_constraintdef']}")

# Check existing info_source values
cur.execute("""
    SELECT DISTINCT info_source 
    FROM garment_guides 
    ORDER BY info_source
""")

print("\nExisting info_source values:")
for row in cur.fetchall():
    print(f"  - {row['info_source']}")

conn.close()

