#!/usr/bin/env python3
"""Check structure of garment_guide_entries table"""

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

# Check table structure
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'garment_guide_entries'
    ORDER BY ordinal_position
""")

print("garment_guide_entries columns:")
for row in cur.fetchall():
    print(f"  - {row['column_name']}: {row['data_type']}")

# Check a sample entry
cur.execute("""
    SELECT * FROM garment_guide_entries LIMIT 1
""")

sample = cur.fetchone()
if sample:
    print("\nSample entry:")
    for key, value in sample.items():
        print(f"  {key}: {value}")

conn.close()

