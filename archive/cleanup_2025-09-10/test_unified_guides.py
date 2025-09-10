#!/usr/bin/env python3
"""
Demonstrate how the unified measurement_guides table simplifies queries
"""

import psycopg2
from psycopg2.extras import RealDictCursor

conn = psycopg2.connect(
    dbname='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

print("=== BEFORE: Complex Conditional Queries ===\n")
print("To get all guides for a brand, you needed:")
print("""
-- Two separate queries or a UNION:
SELECT 'body' as type, size_guide_header as name, measurements_available
FROM size_guides WHERE brand_id = 1
UNION ALL  
SELECT 'garment' as type, guide_header as name, measurements_available
FROM garment_guides WHERE brand_id = 1;
""")

print("\n=== AFTER: Simple Unified Query ===\n")
print("Now you can just do:")
print("""
SELECT guide_type, name, measurements_available
FROM measurement_guides  
WHERE brand_id = 1;
""")

# Show real example
print("\n=== Real Example: All Guides for Lululemon ===")
cur.execute("""
    SELECT 
        guide_type,
        name,
        measurements_available,
        CASE 
            WHEN category_id IS NOT NULL THEN 'Category: ' || category_id::text
            WHEN garment_id IS NOT NULL THEN 'Garment: ' || garment_id::text
            ELSE 'Not linked'
        END as applies_to
    FROM measurement_guides
    WHERE brand_id = 1
    ORDER BY guide_type, name;
""")

for row in cur.fetchall():
    print(f"\n{row['guide_type'].upper()}: {row['name']}")
    print(f"  Applies to: {row['applies_to']}")
    print(f"  Measurements: {', '.join(row['measurements_available'] or [])}")

# Show how measurements table can be simplified
print("\n\n=== Simplifying the Measurements Table ===")
print("\nCurrent structure uses source_type and source_id:")
cur.execute("""
    SELECT 
        source_type,
        COUNT(*) as count
    FROM measurements
    GROUP BY source_type;
""")
for row in cur.fetchall():
    print(f"  {row['source_type']}: {row['count']} measurements")

print("\nWith unified guides, we can add a single guide_id column:")
print("  ALTER TABLE measurements ADD COLUMN guide_id INTEGER REFERENCES measurement_guides(id);")
print("\nThen populate it:")
print("""
  UPDATE measurements m
  SET guide_id = mg.id
  FROM measurement_guides mg
  WHERE 
    (m.source_type = 'size_guide' AND mg.original_table = 'size_guides' AND mg.original_id = m.source_id) OR
    (m.source_type = 'garment_spec' AND mg.original_table = 'garment_guides' AND mg.original_id = m.source_id);
""")

# Show benefit for queries
print("\n=== Query Benefits ===")
print("\nBEFORE - Getting guide info for a measurement:")
print("""
SELECT m.*, 
  CASE 
    WHEN m.source_type = 'size_guide' THEN sg.size_guide_header
    WHEN m.source_type = 'garment_spec' THEN gg.guide_header
  END as guide_name
FROM measurements m
LEFT JOIN size_guides sg ON m.source_type = 'size_guide' AND m.source_id = sg.id
LEFT JOIN garment_guides gg ON m.source_type = 'garment_spec' AND m.source_id = gg.id;
""")

print("\nAFTER - Much simpler:")
print("""
SELECT m.*, mg.name as guide_name
FROM measurements m
JOIN measurement_guides mg ON m.guide_id = mg.id;
""")

cur.close()
conn.close()

print("\n✅ The unified table is ready to use!")
print("✅ No existing tables were modified")
print("\nYou can start using measurement_guides for new features while")
print("keeping the old tables until you're ready to fully migrate.")
