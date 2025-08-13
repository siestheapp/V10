#!/usr/bin/env python3
"""
Rename measurement_value to measurement_value_in for consistency
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

def rename_columns():
    """Rename measurement_value to measurement_value_in"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Renaming columns for consistency...")
        
        # Check current column names
        print("1. Current column structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'garment_guide_entries' 
            AND column_name LIKE 'measurement_value%'
            ORDER BY column_name
        """)
        
        columns = cursor.fetchall()
        for col in columns:
            print(f"   {col['column_name']}: {col['data_type']}")
        
        # Rename measurement_value to measurement_value_in
        print("2. Renaming measurement_value to measurement_value_in...")
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            RENAME COLUMN measurement_value TO measurement_value_in;
        """)
        
        # Verify the rename
        print("3. Updated column structure:")
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'garment_guide_entries' 
            AND column_name LIKE 'measurement_value%'
            ORDER BY column_name
        """)
        
        updated_columns = cursor.fetchall()
        for col in updated_columns:
            print(f"   {col['column_name']}: {col['data_type']}")
        
        # Show sample data with new column names
        print("4. Sample data with new column structure:")
        cursor.execute("""
            SELECT 
                size_label,
                measurement_type,
                measurement_value_in as inches,
                measurement_value_cm as centimeters,
                unit,
                measurement_source
            FROM garment_guide_entries
            WHERE unit = 'in'
            ORDER BY size_label, measurement_type
            LIMIT 6
        """)
        
        sample_data = cursor.fetchall()
        for row in sample_data:
            print(f"   {row['size_label']} - {row['measurement_type']}: {row['inches']} in / {row['centimeters']} cm")
        
        conn.commit()
        print("✅ Column rename completed successfully!")
        
        # Show the benefits
        print("\n🎯 Benefits of new structure:")
        print("   • measurement_value_in: Clear that this contains inch values")
        print("   • measurement_value_cm: Clear that this contains cm values")
        print("   • Consistent naming pattern")
        print("   • Self-documenting column names")
        
    except Exception as e:
        print(f"❌ Error during rename: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    rename_columns()

