#!/usr/bin/env python3
"""Check structure of measurement_sets table"""

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

print("measurement_sets table structure:")
print("-" * 40)

cur.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'measurement_sets'
    ORDER BY ordinal_position
""")

for row in cur.fetchall():
    nullable = "" if row['is_nullable'] == 'NO' else " (nullable)"
    print(f"  {row['column_name']}: {row['data_type']}{nullable}")

print("\nSample J.Crew measurement_set:")
print("-" * 40)

cur.execute("""
    SELECT * FROM measurement_sets
    WHERE brand_id = 4
    LIMIT 1
""")

sample = cur.fetchone()
if sample:
    for key, value in sample.items():
        print(f"  {key}: {value}")
else:
    print("  No J.Crew measurement sets found")

conn.close()

