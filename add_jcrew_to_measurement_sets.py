#!/usr/bin/env python3
"""
Add J.Crew size guide to the NEW measurement_sets system
Based on the screenshot showing the official J.Crew MEN > TOPS guide
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    database='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543',
    cursor_factory=RealDictCursor
)
cur = conn.cursor()

def add_jcrew_measurement_set():
    """Add J.Crew Men's Tops to measurement_sets"""
    
    print("📊 Adding J.Crew Men's Tops to NEW measurement_sets system...")
    
    # First check if it already exists
    cur.execute("""
        SELECT id FROM measurement_sets 
        WHERE brand_id = 4 
        AND scope = 'size_guide'
        AND gender = 'male'
    """)
    existing = cur.fetchone()
    
    if existing:
        print(f"⚠️  J.Crew measurement set already exists (ID: {existing['id']})")
        print("   Deleting old measurements to replace with correct data...")
        
        # Delete old measurements
        cur.execute("""
            DELETE FROM measurements 
            WHERE set_id = %s
        """, (existing['id'],))
        
        set_id = existing['id']
    else:
        # Create new measurement set
        cur.execute("""
            INSERT INTO measurement_sets (
                scope, 
                brand_id, 
                category_id,
                gender,
                fit_type,
                source_url,
                unit,
                notes,
                created_at
            ) VALUES (
                'size_guide',
                4,  -- J.Crew brand ID
                1,  -- Tops category ID
                'male',
                'regular',
                'https://www.jcrew.com/size-charts',
                'in',  -- Must be 'in' or 'cm'
                'J.Crew Men''s Tops Size Guide - covers shirts, t-shirts, sweaters, and outerwear',
                NOW()
            )
            RETURNING id
        """)
        set_id = cur.fetchone()['id']
        print(f"✅ Created measurement set ID: {set_id}")
    
    return set_id

def add_jcrew_measurements(set_id):
    """Add the actual measurements from the screenshot"""
    
    print(f"\n📏 Adding measurements to set {set_id}...")
    
    # Data from the J.Crew screenshot
    # Format: size -> {chest, neck, waist, arm_length}
    size_data = {
        'XS': {
            'chest': [32, 34],
            'neck': [13, 13.5],
            'waist': [26, 28],
            'arm_length': [31, 32]
        },
        'S': {
            'chest': [35, 37],
            'neck': [14, 14.5],
            'waist': [29, 31],
            'arm_length': [32, 33]
        },
        'M': {
            'chest': [38, 40],
            'neck': [15, 15.5],
            'waist': [32, 34],
            'arm_length': [33, 34]
        },
        'L': {
            'chest': [41, 43],
            'neck': [16, 16.5],
            'waist': [35, 37],
            'arm_length': [34, 35]
        },
        'XL': {
            'chest': [44, 46],
            'neck': [17, 17.5],
            'waist': [38, 40],
            'arm_length': [35, 36]
        },
        'XXL': {
            'chest': [47, 49],
            'neck': [18, 18.5],
            'waist': [41, 43],
            'arm_length': [36, 37]
        },
        'XXXL': {
            'chest': [50, 52],
            'neck': [18, 18.5],  # Same as XXL
            'waist': [44, 45],
            'arm_length': [36, 37]  # Same as XXL
        }
    }
    
    # Measurement type mapping
    measurement_types = {
        'chest': 'body_chest',
        'neck': 'body_neck',
        'waist': 'body_waist',
        'arm_length': 'body_sleeve'  # Using existing body_sleeve type (screenshot says "Arm Length")
    }
    
    for size_label, measurements in size_data.items():
        for measure_name, values in measurements.items():
            measurement_type = measurement_types[measure_name]
            min_value = values[0]
            max_value = values[1]
            
            # Check if measurement exists
            cur.execute("""
                SELECT id FROM measurements 
                WHERE set_id = %s 
                AND size_label = %s 
                AND measurement_type = %s
            """, (set_id, size_label, measurement_type))
            
            existing = cur.fetchone()
            
            if existing:
                # Update existing
                cur.execute("""
                    UPDATE measurements SET
                        min_value = %s,
                        max_value = %s,
                        updated_at = NOW()
                    WHERE id = %s
                """, (min_value, max_value, existing['id']))
            else:
                # Insert new
                cur.execute("""
                    INSERT INTO measurements (
                        set_id,
                        source_type,
                        brand_id,
                        size_label,
                        measurement_type,
                        min_value,
                        max_value,
                        unit,
                        created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                    )
                """, (
                    set_id,
                    'size_guide',
                    4,  # J.Crew brand ID
                    size_label,
                    measurement_type,
                    min_value,
                    max_value,
                    'in'  # Must be 'in' or 'cm'
                ))
        
        print(f"  ✅ Added {size_label}: chest={measurements['chest']}, neck={measurements['neck']}, waist={measurements['waist']}, arm={measurements['arm_length']}")
    
    conn.commit()
    print(f"\n✅ Added {len(size_data)} sizes with 4 measurements each")

def verify_data():
    """Verify the data was added correctly"""
    
    print("\n🔍 Verifying data...")
    
    # Check measurement_sets
    cur.execute("""
        SELECT id, scope, gender, notes 
        FROM measurement_sets 
        WHERE brand_id = 4
    """)
    sets = cur.fetchall()
    print(f"\nMeasurement sets for J.Crew: {len(sets)}")
    for s in sets:
        print(f"  - ID {s['id']}: {s['scope']} ({s['gender']})")
        print(f"    Notes: {s['notes'][:50]}...")
    
    # Check measurements
    cur.execute("""
        SELECT 
            size_label,
            measurement_type,
            min_value,
            max_value
        FROM measurements
        WHERE brand_id = 4
        AND size_label = 'M'
        ORDER BY measurement_type
    """)
    measurements = cur.fetchall()
    print(f"\nSample measurements for size M:")
    for m in measurements:
        print(f"  - {m['measurement_type']}: {m['min_value']}-{m['max_value']} inches")
    
    # Count total
    cur.execute("""
        SELECT COUNT(*) as count 
        FROM measurements 
        WHERE brand_id = 4
    """)
    count = cur.fetchone()['count']
    print(f"\nTotal J.Crew measurements in new system: {count}")

def main():
    try:
        print("=" * 60)
        print("🎯 J.Crew Size Guide Migration to NEW System")
        print("=" * 60)
        
        # Add to measurement_sets
        set_id = add_jcrew_measurement_set()
        
        # Add measurements
        add_jcrew_measurements(set_id)
        
        # Verify
        verify_data()
        
        print("\n" + "=" * 60)
        print("✅ SUCCESS! J.Crew data added to NEW measurement_sets system")
        print("=" * 60)
        print("\n⚠️  NOTE: Backend needs updating to query measurement_sets")
        print("   See APP_CODE_MIGRATION_GUIDE.md for query updates")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
