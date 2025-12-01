#!/usr/bin/env python3
"""
Verify and display both inch and centimeter measurements
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('src/ios_app/Backend/.env')

def get_db_connection():
    """Get database connection using environment variables or defaults"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com"),
        port=os.getenv("DB_PORT", "6543"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres.lbilxlkchzpducggkrxx"),
        password=os.getenv("DB_PASSWORD", "efvTower12"),
        cursor_factory=RealDictCursor
    )

def verify_measurements():
    """Display both inch and centimeter measurements"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get all measurements for garment guide ID 1, grouped by size and type
        cursor.execute("""
            SELECT 
                size_label,
                measurement_type,
                MAX(CASE WHEN unit = 'in' THEN measurement_value END) as inches,
                MAX(CASE WHEN unit = 'cm' THEN measurement_value END) as centimeters,
                COUNT(*) as unit_count
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
            GROUP BY size_label, measurement_type
            ORDER BY 
                CASE size_label 
                    WHEN 'S' THEN 1 
                    WHEN 'M' THEN 2 
                    WHEN 'L' THEN 3 
                    WHEN 'XL' THEN 4 
                    WHEN 'XXL' THEN 5 
                    ELSE 6 
                END,
                measurement_type
        """)
        
        results = cursor.fetchall()
        
        print("📏 Garment Measurements Comparison:")
        print("=" * 60)
        
        current_size = None
        for row in results:
            if current_size != row['size_label']:
                current_size = row['size_label']
                print(f"\n🔸 Size {row['size_label']}:")
            
            measurement_name = row['measurement_type'].replace('g_', '').replace('_', ' ').title()
            inches = row['inches']
            centimeters = row['centimeters']
            
            print(f"  {measurement_name}:")
            if inches:
                print(f"    📏 {inches} in")
            if centimeters:
                print(f"    📐 {centimeters} cm")
            
            # Show conversion if both exist
            if inches and centimeters:
                calculated_cm = round(float(inches) * 2.54, 1)
                calculated_in = round(float(centimeters) / 2.54, 1)
                print(f"    🔄 Conversion check: {inches} in = {calculated_cm} cm, {centimeters} cm = {calculated_in} in")
        
        # Show summary
        cursor.execute("""
            SELECT 
                unit,
                COUNT(*) as count
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
            GROUP BY unit
        """)
        
        summary = cursor.fetchall()
        print(f"\n📊 Summary:")
        for row in summary:
            print(f"  {row['unit']} measurements: {row['count']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verify_measurements()
