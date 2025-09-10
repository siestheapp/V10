#!/usr/bin/env python3
"""Check valid measurement types"""

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
    WHERE conrelid = 'garment_guide_entries'::regclass 
    AND conname LIKE '%measurement_type%'
""")

print("Measurement type constraints:")
for row in cur.fetchall():
    print(row['pg_get_constraintdef'])

# Check existing measurement types
cur.execute("""
    SELECT DISTINCT measurement_type 
    FROM garment_guide_entries 
    ORDER BY measurement_type
""")

print("\nExisting measurement types in use:")
for row in cur.fetchall():
    print(f"  - {row['measurement_type']}")

conn.close()

