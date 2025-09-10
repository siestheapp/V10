#!/usr/bin/env python3
"""
Clean up duplicate data by adding measurement_value_cm column
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

def cleanup_duplicate_data():
    """Clean up duplicate data by adding measurement_value_cm column"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🧹 Starting cleanup of duplicate measurement data...")
        
        # Step 1: Add measurement_value_cm column if it doesn't exist
        print("1. Adding measurement_value_cm column...")
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            ADD COLUMN IF NOT EXISTS measurement_value_cm numeric;
        """)
        
        # Step 2: Show current data structure
        print("2. Current data summary:")
        cursor.execute("""
            SELECT 
                unit,
                COUNT(*) as count,
                COUNT(measurement_value_cm) as has_cm
            FROM garment_guide_entries
            GROUP BY unit
        """)
        
        summary = cursor.fetchall()
        for row in summary:
            print(f"   {row['unit']}: {row['count']} rows, {row['has_cm']} have cm values")
        
        # Step 3: Copy cm values from cm rows to corresponding inch rows
        print("3. Copying cm values to inch rows...")
        cursor.execute("""
            UPDATE garment_guide_entries gge_in
            SET measurement_value_cm = gge_cm.measurement_value
            FROM garment_guide_entries gge_cm
            WHERE gge_in.garment_guide_id = gge_cm.garment_guide_id
                AND gge_in.size_label = gge_cm.size_label
                AND gge_in.measurement_type = gge_cm.measurement_type
                AND gge_in.unit = 'in'
                AND gge_cm.unit = 'cm'
        """)
        
        updated_rows = cursor.rowcount
        print(f"   Updated {updated_rows} inch rows with cm values")
        
        # Step 4: Calculate cm values for inch rows that don't have them
        print("4. Calculating cm values for remaining inch rows...")
        cursor.execute("""
            UPDATE garment_guide_entries
            SET measurement_value_cm = ROUND((measurement_value * 2.54)::numeric, 1)
            WHERE unit = 'in' AND measurement_value_cm IS NULL
        """)
        
        calculated_rows = cursor.rowcount
        print(f"   Calculated cm values for {calculated_rows} inch rows")
        
        # Step 5: Delete the duplicate cm rows
        print("5. Deleting duplicate cm rows...")
        cursor.execute("""
            DELETE FROM garment_guide_entries
            WHERE unit = 'cm'
        """)
        
        deleted_rows = cursor.rowcount
        print(f"   Deleted {deleted_rows} duplicate cm rows")
        
        # Step 6: Verify the cleanup
        print("6. Verifying cleanup results:")
        cursor.execute("""
            SELECT 
                unit,
                COUNT(*) as count,
                COUNT(measurement_value_cm) as has_cm
            FROM garment_guide_entries
            GROUP BY unit
        """)
        
        final_summary = cursor.fetchall()
        for row in final_summary:
            print(f"   {row['unit']}: {row['count']} rows, {row['has_cm']} have cm values")
        
        # Step 7: Show sample of cleaned data
        print("7. Sample of cleaned data:")
        cursor.execute("""
            SELECT 
                size_label,
                measurement_type,
                measurement_value as inches,
                measurement_value_cm as centimeters,
                unit,
                measurement_source
            FROM garment_guide_entries
            WHERE unit = 'in'
            ORDER BY size_label, measurement_type
            LIMIT 9
        """)
        
        sample_data = cursor.fetchall()
        for row in sample_data:
            print(f"   {row['size_label']} - {row['measurement_type']}: {row['inches']} in / {row['centimeters']} cm")
        
        conn.commit()
        print("✅ Cleanup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    cleanup_duplicate_data()

