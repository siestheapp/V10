#!/usr/bin/env python3
"""Complete analysis of J.Crew data with correct column names"""

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
print("J.CREW COMPLETE DATA ANALYSIS")
print("=" * 60)

# J.Crew brand ID
jcrew_id = 4

print("\n1. MEASUREMENT SETS (New System):")
print("-" * 40)

cur.execute("""
    SELECT id, scope, header, source, is_active, 
           unit, fit_type, gender, level
    FROM measurement_sets
    WHERE brand_id = %s
    ORDER BY id
""", (jcrew_id,))

sets = cur.fetchall()
print(f"Found {len(sets)} measurement set(s) for J.Crew")

for ms in sets:
    print(f"\n✓ Set ID {ms['id']}: {ms['header'] or 'No header'}")
    print(f"  Scope: {ms['scope']}")
    print(f"  Fit Type: {ms['fit_type']}")
    print(f"  Gender: {ms['gender']}")
    print(f"  Unit: {ms['unit']}")
    print(f"  Active: {ms['is_active']}")
    
    # Get measurements for this set
    cur.execute("""
        SELECT measurement_type, size_label, 
               min_value, max_value, exact_value, unit
        FROM measurements
        WHERE set_id = %s
        ORDER BY size_label, measurement_type
        LIMIT 15
    """, (ms['id'],))
    
    measurements = cur.fetchall()
    if measurements:
        print(f"  Measurements: {len(measurements)} samples shown")
        
        # Group by size for better display
        sizes = {}
        for m in measurements:
            size = m['size_label']
            if size not in sizes:
                sizes[size] = []
            if m['exact_value']:
                value = f"{m['exact_value']}{m['unit']}"
            elif m['min_value'] and m['max_value']:
                value = f"{m['min_value']}-{m['max_value']}{m['unit']}"
            else:
                value = "N/A"
            sizes[size].append(f"{m['measurement_type']}: {value}")
        
        for size, measures in list(sizes.items())[:3]:  # Show first 3 sizes
            print(f"    Size {size}: {', '.join(measures[:3])}")
    else:
        print(f"  ⚠ No measurements found for this set")

print("\n2. LEGACY GARMENT GUIDES:")
print("-" * 40)

cur.execute("""
    SELECT id, guide_header, info_source
    FROM garment_guides
    WHERE brand_id = %s
""", (jcrew_id,))

guides = cur.fetchall()
if guides:
    print(f"⚠ Found {len(guides)} legacy guide(s) - should be removed:")
    for guide in guides:
        print(f"  - Guide ID {guide['id']}: {guide['guide_header']}")
        
        # Count entries
        cur.execute("""
            SELECT COUNT(*) as count
            FROM garment_guide_entries
            WHERE garment_guide_id = %s
        """, (guide['id'],))
        count = cur.fetchone()['count']
        print(f"    Has {count} entries")
else:
    print("✓ No legacy guides found")

print("\n3. PRODUCT CACHE:")
print("-" * 40)

cur.execute("""
    SELECT product_name, category, product_url
    FROM jcrew_product_cache
    ORDER BY product_name
""")
products = cur.fetchall()

if products:
    print(f"✓ {len(products)} J.Crew products cached:")
    for p in products:
        print(f"  - {p['product_name'][:40]} ({p['category']})")
else:
    print("⚠ No products cached yet")

print("\n4. STATUS SUMMARY:")
print("-" * 40)

# Check if we have measurements in the new system
cur.execute("""
    SELECT COUNT(DISTINCT m.size_label) as sizes,
           COUNT(DISTINCT m.measurement_type) as types,
           COUNT(*) as total
    FROM measurements m
    JOIN measurement_sets ms ON m.set_id = ms.id
    WHERE ms.brand_id = %s
""", (jcrew_id,))

stats = cur.fetchone()
if stats and stats['total'] > 0:
    print(f"✓ NEW SYSTEM: {stats['total']} measurements ({stats['sizes']} sizes × {stats['types']} types)")
else:
    print("⚠ NEW SYSTEM: No measurements found")

# Check legacy system
cur.execute("""
    SELECT COUNT(*) as count
    FROM garment_guide_entries gge
    JOIN garment_guides gg ON gge.garment_guide_id = gg.id
    WHERE gg.brand_id = %s
""", (jcrew_id,))

legacy_count = cur.fetchone()['count']
if legacy_count > 0:
    print(f"⚠ LEGACY SYSTEM: {legacy_count} entries still exist")

print("\n5. RECOMMENDATIONS:")
print("-" * 40)

if stats and stats['total'] > 0:
    print("✓ J.Crew has data in the NEW measurement system")
else:
    print("⚠ Need to add J.Crew measurements to the NEW system")

if legacy_count > 0:
    print("⚠ Clean up legacy garment_guides entries")

if products:
    print("✓ Product cache is ready")
else:
    print("⚠ Add products to cache")

print("\n✅ The app should use measurement_sets (ID 7) for J.Crew")
print("✅ Backend image extraction will check jcrew_product_cache first")

conn.close()

