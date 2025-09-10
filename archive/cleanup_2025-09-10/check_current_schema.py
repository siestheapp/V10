#!/usr/bin/env python3
"""Check current database schema to understand what's being used"""

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
print("CURRENT DATABASE SCHEMA CHECK")
print("=" * 60)

# Check if we have the new unified tables
print("\n1. NEW UNIFIED TABLES (Post-Migration):")
print("-" * 40)

# Check measurement_sets
cur.execute("""
    SELECT COUNT(*) as count, 
           COUNT(CASE WHEN scope = 'size_guide' THEN 1 END) as size_guides,
           COUNT(CASE WHEN scope = 'garment_spec' THEN 1 END) as garment_specs
    FROM measurement_sets
""")
result = cur.fetchone()
print(f"✓ measurement_sets: {result['count']} total ({result['size_guides']} size guides, {result['garment_specs']} garment specs)")

# Check measurements table structure
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'measurements'
    AND column_name IN ('set_id', 'garment_id', 'size_label', 'measurement_type')
""")
cols = [row['column_name'] for row in cur.fetchall()]
print(f"✓ measurements table has: {', '.join(cols)}")

# Check measurement_types
cur.execute("SELECT COUNT(*) as count FROM measurement_types")
result = cur.fetchone()
print(f"✓ measurement_types: {result['count']} defined types")

print("\n2. LEGACY TABLES (Pre-Migration):")
print("-" * 40)

# Check if garment_guides still exists
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'garment_guides'
    ) as exists
""")
if cur.fetchone()['exists']:
    cur.execute("SELECT COUNT(*) as count FROM garment_guides")
    print(f"⚠ garment_guides: {cur.fetchone()['count']} records (LEGACY - use measurement_sets instead)")

# Check if garment_guide_entries still exists  
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'garment_guide_entries'
    ) as exists
""")
if cur.fetchone()['exists']:
    cur.execute("SELECT COUNT(*) as count FROM garment_guide_entries")
    print(f"⚠ garment_guide_entries: {cur.fetchone()['count']} records (LEGACY - use measurements instead)")

print("\n3. BACKWARD COMPATIBILITY VIEWS:")
print("-" * 40)

# Check for views
views = ['garment_guides_view', 'garment_guide_entries_view', 'size_guides_view', 'size_guide_entries_view']
for view in views:
    cur.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.views 
            WHERE table_name = %s
        ) as exists
    """, (view,))
    if cur.fetchone()['exists']:
        print(f"✓ {view} exists (for backward compatibility)")

print("\n4. J.CREW SPECIFIC:")
print("-" * 40)

# Check J.Crew brand
cur.execute("SELECT id, name FROM brands WHERE name ILIKE '%j%crew%'")
jcrew = cur.fetchone()
if jcrew:
    print(f"✓ J.Crew brand exists (ID: {jcrew['id']})")
    
    # Check J.Crew in new structure
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM measurement_sets 
        WHERE brand_id = %s
    """, (jcrew['id'],))
    result = cur.fetchone()
    print(f"  - measurement_sets for J.Crew: {result['count']}")
    
    # Check J.Crew in legacy structure
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM garment_guides 
        WHERE brand_id = %s
    """, (jcrew['id'],))
    result = cur.fetchone()
    print(f"  - garment_guides for J.Crew: {result['count']} (legacy)")

# Check our product cache
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'jcrew_product_cache'
    ) as exists
""")
if cur.fetchone()['exists']:
    cur.execute("SELECT COUNT(*) as count FROM jcrew_product_cache")
    print(f"✓ jcrew_product_cache: {cur.fetchone()['count']} products cached")

print("\n5. RECOMMENDATION:")
print("-" * 40)
print("Based on the migration:")
print("• Use 'measurement_sets' and 'measurements' tables (NEW)")
print("• Avoid 'garment_guides' and 'garment_guide_entries' (LEGACY)")
print("• The views provide backward compatibility if needed")
print("• J.Crew data should be added to the new unified structure")

conn.close()

