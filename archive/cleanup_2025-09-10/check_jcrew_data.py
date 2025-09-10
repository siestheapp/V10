#!/usr/bin/env python3
"""Check if J.Crew brand and size guides exist in the database"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database connection using Supabase pooler
conn = psycopg2.connect(
    database='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543',
    cursor_factory=RealDictCursor
)

cur = conn.cursor()

# Check for J.Crew brand
cur.execute("SELECT * FROM brands WHERE name ILIKE '%j%crew%'")
jcrew_brand = cur.fetchone()
print("J.Crew brand:", jcrew_brand)

if jcrew_brand:
    brand_id = jcrew_brand["id"]
    
    # Check for garment guides
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM garment_guides 
        WHERE brand_id = %s
    """, (brand_id,))
    guides_count = cur.fetchone()
    print(f"J.Crew garment guides count: {guides_count['count']}")
    
    # Check garment_guides table structure
    cur.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'garment_guides'
        ORDER BY ordinal_position
    """)
    columns = cur.fetchall()
    print("\ngarment_guides columns:")
    for col in columns:
        print(f"  - {col['column_name']}: {col['data_type']}")
    
    # Check for any garment guides
    cur.execute("""
        SELECT garment_type, garment_subcategory, COUNT(*) as count
        FROM garment_guides
        WHERE brand_id = %s
        GROUP BY garment_type, garment_subcategory
    """, (brand_id,))
    categories = cur.fetchall()
    if categories:
        print("\nJ.Crew categories:")
        for cat in categories:
            print(f"  - {cat['garment_type']} / {cat['garment_subcategory']}: {cat['count']} items")
    
    # Check for size data
    cur.execute("""
        SELECT DISTINCT size_label
        FROM garment_guide_entries
        WHERE garment_guide_id IN (
            SELECT id FROM garment_guides WHERE brand_id = %s
        )
        ORDER BY size_label
    """, (brand_id,))
    sizes = cur.fetchall()
    if sizes:
        print(f"\nAvailable sizes: {[s['size_label'] for s in sizes]}")
    else:
        print("\nNo size data found for J.Crew")
else:
    print("J.Crew brand not found in database")

conn.close()