import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543'
)
cur = conn.cursor(cursor_factory=RealDictCursor)

# First, let's find the NN07 garment and its feedback
print('=== NN07 Garment Details ===')
cur.execute('''
    SELECT 
        ug.id,
        g.product_name,
        ug.size_label,
        ug.created_at,
        ugf.dimension,
        fc.feedback_text,
        ugf.created_at as feedback_date
    FROM user_garments ug
    LEFT JOIN garments g ON ug.garment_id = g.id
    LEFT JOIN user_garment_feedback ugf ON ugf.user_garment_id = ug.id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    WHERE g.product_name LIKE '%NN%' OR g.product_name LIKE '%Clive%'
    ORDER BY ugf.created_at
''')
nn07_feedback = cur.fetchall()
for row in nn07_feedback:
    if row['dimension']:
        print(f"{row['dimension']}: {row['feedback_text']} (added {row['feedback_date']})")

# Check current fit zones
print('\n=== Current Fit Zones for User 1 ===')
cur.execute('''
    SELECT 
        dimension,
        category,
        good_min,
        good_max,
        relaxed_min,
        relaxed_max,
        tight_min,
        tight_max,
        confidence_score,
        data_points_count,
        last_updated
    FROM user_fit_zones
    WHERE user_id = 1
    ORDER BY dimension
''')
zones = cur.fetchall()
for zone in zones:
    print(f"\n{zone['dimension']} ({zone['category']}):")
    if zone['tight_min'] and zone['tight_max']:
        print(f"  Tight: {zone['tight_min']}-{zone['tight_max']}")
    print(f"  Good: {zone['good_min']}-{zone['good_max']}")
    if zone['relaxed_min'] and zone['relaxed_max']:
        print(f"  Relaxed: {zone['relaxed_min']}-{zone['relaxed_max']}")
    print(f"  Confidence: {zone['confidence_score']}, Data points: {zone['data_points_count']}")
    print(f"  Last updated: {zone['last_updated']}")

# Check when fit zones were last calculated vs when NN07 was added
print('\n=== Fit Zone Update Analysis ===')
nn07_date = datetime(2025, 8, 13, 2, 16, 36)  # When NN07 feedback was added
for zone in zones:
    if zone['last_updated']:
        if zone['last_updated'] > nn07_date:
            print(f"✅ {zone['dimension']} fit zone WAS updated after NN07 feedback")
        else:
            print(f"❌ {zone['dimension']} fit zone was NOT updated after NN07 feedback")
            print(f"   Last updated: {zone['last_updated']}")
            print(f"   NN07 added: {nn07_date}")

# Check the garment measurements for NN07
print('\n=== NN07 Garment Measurements ===')
cur.execute('''
    SELECT 
        ug.id,
        ug.size_label,
        gge.measurement_type,
        gge.measurement_value_in as value
    FROM user_garments ug
    LEFT JOIN garments g ON ug.garment_id = g.id
    LEFT JOIN garment_guide_entries gge ON gge.garment_id = g.id AND gge.size_label = ug.size_label
    WHERE g.product_name LIKE '%NN%' OR g.product_name LIKE '%Clive%'
    ORDER BY gge.measurement_type
''')
measurements = cur.fetchall()
if measurements:
    for m in measurements:
        if m['measurement_type']:
            print(f"{m['measurement_type']}: {m['value']} inches")
else:
    print('No garment measurements found for NN07')

# Check all feedback history to see changes
print('\n=== All User Feedback History (chronological) ===')
cur.execute('''
    SELECT 
        b.name as brand,
        g.product_name,
        ug.size_label,
        ugf.dimension,
        fc.feedback_text,
        ugf.created_at,
        sge.chest_min, sge.chest_max,
        sge.sleeve_min, sge.sleeve_max
    FROM user_garment_feedback ugf
    JOIN user_garments ug ON ugf.user_garment_id = ug.id
    LEFT JOIN garments g ON ug.garment_id = g.id
    LEFT JOIN brands b ON g.brand_id = b.id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
    WHERE ug.user_id = 1
    ORDER BY ugf.created_at DESC
    LIMIT 20
''')
history = cur.fetchall()
for h in history:
    measurement_range = ''
    if h['dimension'] == 'chest' and h['chest_min']:
        measurement_range = f" ({h['chest_min']}-{h['chest_max']})"
    elif h['dimension'] == 'sleeve' and h['sleeve_min']:
        measurement_range = f" ({h['sleeve_min']}-{h['sleeve_max']})"
    
    print(f"{h['created_at'].strftime('%Y-%m-%d %H:%M')}: {h['brand']} {h['product_name']} Size {h['size_label']} - {h['dimension']}: {h['feedback_text']}{measurement_range}")

conn.close()
