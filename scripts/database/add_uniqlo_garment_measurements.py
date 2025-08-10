#!/usr/bin/env python3
"""
Add missing Uniqlo garment measurements to garment_measurements table
Based on Uniqlo size chart: https://www.uniqlo.com/us/en/products/E455365-000/00/size?sizeDisplayCode=004&measurementUnit=inch
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def add_uniqlo_garment_measurements():
    """Add missing Uniqlo garment measurements for the user's Medium shirt"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("🔍 Finding Uniqlo SUPIMA Cotton T-Shirt (Medium)...")
        
        # Find the Uniqlo shirt
        cursor.execute("""
            SELECT ug.id, ug.size_label, ug.product_name, b.name as brand
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 
            AND b.name = 'Uniqlo'
            AND ug.product_name ILIKE '%SUPIMA Cotton T-Shirt%'
            AND ug.size_label = 'M'
        """)
        
        shirt = cursor.fetchone()
        if not shirt:
            print("❌ Uniqlo Medium shirt not found!")
            return
        
        print(f"✅ Found shirt: ID {shirt['id']} - {shirt['brand']} {shirt['product_name']} (Size {shirt['size_label']})")
        
        # Check if measurements already exist
        cursor.execute("""
            SELECT measurement_type, measurement_value, unit
            FROM garment_measurements
            WHERE user_garment_id = %s
        """, (shirt['id'],))
        
        existing = cursor.fetchall()
        if existing:
            print(f"\n📋 Existing measurements:")
            for m in existing:
                print(f"  {m['measurement_type']}: {m['measurement_value']} {m['unit']}")
        
        # Uniqlo Medium measurements from size chart
        measurements = [
            ('body_length', 28.0, 'in', 'product_page'),
            ('shoulder_width', 17.5, 'in', 'product_page'),
            ('chest_width', 21.5, 'in', 'product_page'),
            ('sleeve_length', 17.5, 'in', 'product_page')
        ]
        
        print(f"\n📏 Adding Uniqlo Medium measurements:")
        for measurement_type, value, unit, source in measurements:
            print(f"  {measurement_type}: {value} {unit}")
        
        # Confirm addition
        confirm = input(f"\n❓ Add {len(measurements)} measurements? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Addition cancelled.")
            return
        
        # Add measurements
        added_count = 0
        for measurement_type, value, unit, source in measurements:
            cursor.execute("""
                INSERT INTO garment_measurements (
                    user_garment_id, measurement_type, measurement_value, unit, 
                    measurement_source, source_url, notes
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                shirt['id'], measurement_type, value, unit, source,
                'https://www.uniqlo.com/us/en/products/E455365-000/00/size?sizeDisplayCode=004&measurementUnit=inch',
                f'Uniqlo Medium size chart measurement for {measurement_type}'
            ))
            added_count += 1
        
        conn.commit()
        print(f"✅ Successfully added {added_count} measurements!")
        
        # Verify results
        cursor.execute("""
            SELECT measurement_type, measurement_value, unit, measurement_source
            FROM garment_measurements
            WHERE user_garment_id = %s
            ORDER BY measurement_type
        """, (shirt['id'],))
        
        final_measurements = cursor.fetchall()
        print(f"\n📊 Final measurements for Uniqlo shirt:")
        for m in final_measurements:
            print(f"  {m['measurement_type']}: {m['measurement_value']} {m['unit']} (Source: {m['measurement_source']})")
        
        print(f"\n🎉 Uniqlo shirt now has {len(final_measurements)} garment measurements!")
        print("The feedback system can now query about these additional measurements in Section 2.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_uniqlo_garment_measurements()
