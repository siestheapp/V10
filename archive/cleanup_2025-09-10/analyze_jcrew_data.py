#!/usr/bin/env python3
"""Analyze all J.Crew data across new and legacy systems"""

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
print("J.CREW DATA ANALYSIS")
print("=" * 60)

# J.Crew brand ID
jcrew_id = 4

print("\n1. NEW SYSTEM (measurement_sets + measurements):")
print("-" * 40)

# Get J.Crew measurement sets
cur.execute("""
    SELECT id, scope, header, source, is_active, created_at
    FROM measurement_sets
    WHERE brand_id = %s
    ORDER BY id
""", (jcrew_id,))

sets = cur.fetchall()
for ms in sets:
    print(f"\nSet ID {ms['id']}: {ms['header'] or 'No header'}")
    print(f"  Scope: {ms['scope']}")
    print(f"  Source: {ms['source']}")
    print(f"  Active: {ms['is_active']}")
    
    # Get measurements for this set
    cur.execute("""
        SELECT measurement_type, size_label, 
               value_in, value_cm
        FROM measurements
        WHERE set_id = %s
        ORDER BY size_label, measurement_type
        LIMIT 10
    """, (ms['id'],))
    
    measurements = cur.fetchall()
    if measurements:
        print(f"  Sample measurements:")
        for m in measurements:
            print(f"    {m['size_label']}/{m['measurement_type']}: {m['value_in']}in")
    else:
        print(f"  No measurements found")

print("\n2. LEGACY SYSTEM (garment_guides + entries):")
print("-" * 40)

cur.execute("""
    SELECT id, guide_header, info_source, created_at
    FROM garment_guides
    WHERE brand_id = %s
    ORDER BY id
""", (jcrew_id,))

guides = cur.fetchall()
for guide in guides:
    print(f"\nGuide ID {guide['id']}: {guide['guide_header'] or 'No header'}")
    print(f"  Source: {guide['info_source']}")
    print(f"  Created: {guide['created_at']}")
    
    # Get entries
    cur.execute("""
        SELECT COUNT(*) as count,
               COUNT(DISTINCT size_label) as sizes,
               COUNT(DISTINCT measurement_type) as types,
               array_agg(DISTINCT measurement_type) as type_list
        FROM garment_guide_entries
        WHERE garment_guide_id = %s
    """, (guide['id'],))
    
    entry_stats = cur.fetchone()
    if entry_stats['count'] > 0:
        print(f"  Entries: {entry_stats['count']} total")
        print(f"  Sizes: {entry_stats['sizes']}")
        print(f"  Types: {entry_stats['type_list']}")

print("\n3. PRODUCT CACHE:")
print("-" * 40)

cur.execute("""
    SELECT COUNT(*) as count FROM jcrew_product_cache
""")
cache_count = cur.fetchone()['count']
print(f"J.Crew products cached: {cache_count}")

if cache_count > 0:
    cur.execute("""
        SELECT product_name, category, subcategory 
        FROM jcrew_product_cache 
        LIMIT 5
    """)
    print("Sample products:")
    for p in cur.fetchall():
        print(f"  - {p['product_name']} ({p['category']}/{p['subcategory']})")

print("\n4. RECOMMENDATIONS:")
print("-" * 40)
print("✓ J.Crew already has measurement_set ID 7 with size guide data")
print("✓ Product cache table has been created with sample products")
print("⚠ Legacy garment_guides entries should be removed (IDs: 5, 6)")
print("⚠ Legacy garment_guide_entries should be cleaned up")
print("\nNext steps:")
print("1. Remove legacy J.Crew data from garment_guides")
print("2. Ensure backend uses measurement_sets (ID 7) for fit analysis")
print("3. Test with actual J.Crew product URLs")

conn.close()

