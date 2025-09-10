#!/usr/bin/env python3
"""Clean up legacy J.Crew data from garment_guides"""

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
print("CLEANING UP LEGACY J.CREW DATA")
print("=" * 60)

try:
    # First, show what we're about to delete
    print("\n1. Legacy data to be removed:")
    print("-" * 40)
    
    cur.execute("""
        SELECT id, guide_header 
        FROM garment_guides 
        WHERE brand_id = 4
    """)
    guides = cur.fetchall()
    
    for guide in guides:
        cur.execute("""
            SELECT COUNT(*) as count 
            FROM garment_guide_entries 
            WHERE garment_guide_id = %s
        """, (guide['id'],))
        count = cur.fetchone()['count']
        print(f"Guide ID {guide['id']}: {guide['guide_header']} ({count} entries)")
    
    if guides:
        # Delete entries first (due to foreign key)
        print("\n2. Deleting garment_guide_entries...")
        cur.execute("""
            DELETE FROM garment_guide_entries 
            WHERE garment_guide_id IN (
                SELECT id FROM garment_guides WHERE brand_id = 4
            )
        """)
        entries_deleted = cur.rowcount
        print(f"   Deleted {entries_deleted} entries")
        
        # Delete guides
        print("\n3. Deleting garment_guides...")
        cur.execute("""
            DELETE FROM garment_guides 
            WHERE brand_id = 4
        """)
        guides_deleted = cur.rowcount
        print(f"   Deleted {guides_deleted} guides")
        
        # Commit the changes
        conn.commit()
        print("\n✅ Legacy data cleaned up successfully!")
    else:
        print("\n✅ No legacy data found to clean up")
    
    # Verify cleanup
    print("\n4. Verification:")
    print("-" * 40)
    
    # Check new system
    cur.execute("""
        SELECT COUNT(*) as sets 
        FROM measurement_sets 
        WHERE brand_id = 4
    """)
    new_sets = cur.fetchone()['sets']
    
    cur.execute("""
        SELECT COUNT(*) as measurements
        FROM measurements m
        JOIN measurement_sets ms ON m.set_id = ms.id
        WHERE ms.brand_id = 4
    """)
    new_measurements = cur.fetchone()['measurements']
    
    print(f"✓ NEW system: {new_sets} measurement set(s), {new_measurements} measurements")
    
    # Check legacy system
    cur.execute("""
        SELECT COUNT(*) as guides 
        FROM garment_guides 
        WHERE brand_id = 4
    """)
    legacy_guides = cur.fetchone()['guides']
    
    print(f"✓ LEGACY system: {legacy_guides} guides (should be 0)")
    
    # Check product cache
    cur.execute("""
        SELECT COUNT(*) as products 
        FROM jcrew_product_cache
    """)
    products = cur.fetchone()['products']
    
    print(f"✓ Product cache: {products} products")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()

