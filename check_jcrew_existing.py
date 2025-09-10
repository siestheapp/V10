#!/usr/bin/env python3
"""Check existing J.Crew data in both new and legacy systems"""

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

print("=" * 60)
print("J.CREW DATA AUDIT")
print("=" * 60)

# J.Crew brand ID
jcrew_id = 4

print("\n1. NEW SYSTEM (measurement_sets):")
print("-" * 40)
cur.execute("""
    SELECT id, name, scope, category_id, garment_id, version, is_active, created_at
    FROM measurement_sets
    WHERE brand_id = %s
""", (jcrew_id,))
for row in cur.fetchall():
    print(f"ID: {row['id']}")
    print(f"  Name: {row['name']}")
    print(f"  Scope: {row['scope']}")
    print(f"  Active: {row['is_active']}")
    print(f"  Created: {row['created_at']}")
    
    # Check measurements for this set
    cur.execute("""
        SELECT COUNT(*) as count,
               COUNT(DISTINCT size_label) as sizes,
               COUNT(DISTINCT measurement_type) as types
        FROM measurements
        WHERE set_id = %s
    """, (row['id'],))
    meas = cur.fetchone()
    print(f"  Measurements: {meas['count']} total ({meas['sizes']} sizes × {meas['types']} types)")

print("\n2. LEGACY SYSTEM (garment_guides):")
print("-" * 40)
cur.execute("""
    SELECT id, guide_header, info_source, measurements_available, created_at
    FROM garment_guides
    WHERE brand_id = %s
""", (jcrew_id,))
for row in cur.fetchall():
    print(f"ID: {row['id']}")
    print(f"  Header: {row['guide_header']}")
    print(f"  Source: {row['info_source']}")
    print(f"  Available: {row['measurements_available']}")
    
    # Check entries
    cur.execute("""
        SELECT COUNT(*) as count,
               COUNT(DISTINCT size_label) as sizes,
               COUNT(DISTINCT measurement_type) as types
        FROM garment_guide_entries
        WHERE garment_guide_id = %s
    """, (row['id'],))
    entries = cur.fetchone()
    print(f"  Entries: {entries['count']} total ({entries['sizes']} sizes × {entries['types']} types)")

print("\n3. MEASUREMENT TYPES IN USE:")
print("-" * 40)
cur.execute("""
    SELECT DISTINCT mt.code, mt.display_name, mt.category
    FROM measurements m
    JOIN measurement_types mt ON m.measurement_type = mt.code
    WHERE m.set_id IN (SELECT id FROM measurement_sets WHERE brand_id = %s)
    ORDER BY mt.category, mt.code
""", (jcrew_id,))
types = cur.fetchall()
if types:
    for t in types:
        print(f"  {t['code']} ({t['display_name']}) - {t['category']}")
else:
    print("  No measurements found in new system")

print("\n4. AVAILABLE MEASUREMENT TYPES:")
print("-" * 40)
cur.execute("""
    SELECT code, display_name, category
    FROM measurement_types
    WHERE category = 'garment'
    ORDER BY sort_order
""")
for row in cur.fetchall():
    print(f"  {row['code']}: {row['display_name']}")

conn.close()

