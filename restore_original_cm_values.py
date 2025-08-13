#!/usr/bin/env python3
"""
Restore original cm values from brand size guide
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

def restore_original_cm_values():
    """Restore original cm values from the brand size guide"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔄 Restoring original cm values from brand size guide...")
        
        # Step 1: Show current incorrect values
        print("\n1. CURRENT INCORRECT VALUES:")
        print("=" * 50)
        cursor.execute("""
            SELECT 
                id,
                size_label,
                measurement_type,
                measurement_value_in,
                measurement_value_cm,
                ROUND((measurement_value_in * 2.54)::numeric, 1) as calculated_cm
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
            ORDER BY size_label, measurement_type
        """)
        
        current_values = cursor.fetchall()
        for row in current_values:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']} in → {row['measurement_value_cm']} cm (should be {row['calculated_cm']} cm)")
        
        # Step 2: Define the correct cm values from the size guide
        print("\n2. CORRECT CM VALUES FROM SIZE GUIDE:")
        print("=" * 50)
        
        # Original cm values from the brand size guide
        correct_cm_values = {
            # Size S
            ('S', 'g_chest_width'): 50,
            ('S', 'g_center_back_length'): 67.5,
            ('S', 'g_sleeve_length'): 65,
            
            # Size M
            ('M', 'g_chest_width'): 52,
            ('M', 'g_center_back_length'): 68.5,
            ('M', 'g_sleeve_length'): 66,
            
            # Size L
            ('L', 'g_chest_width'): 54,
            ('L', 'g_center_back_length'): 69.5,
            ('L', 'g_sleeve_length'): 67,
            
            # Size XL
            ('XL', 'g_chest_width'): 56,
            ('XL', 'g_center_back_length'): 70.5,
            ('XL', 'g_sleeve_length'): 68,
            
            # Size XXL
            ('XXL', 'g_chest_width'): 59,
            ('XXL', 'g_center_back_length'): 71.5,
            ('XXL', 'g_sleeve_length'): 69
        }
        
        for (size, measurement_type), correct_cm in correct_cm_values.items():
            print(f"   {size} {measurement_type}: {correct_cm} cm")
        
        # Step 3: Update the database with correct cm values
        print("\n3. UPDATING DATABASE WITH CORRECT CM VALUES:")
        print("=" * 50)
        
        updated_count = 0
        for (size, measurement_type), correct_cm in correct_cm_values.items():
            cursor.execute("""
                UPDATE garment_guide_entries
                SET measurement_value_cm = %s
                WHERE garment_guide_id = 1
                AND size_label = %s
                AND measurement_type = %s
            """, (correct_cm, size, measurement_type))
            
            if cursor.rowcount > 0:
                updated_count += 1
                print(f"   ✅ Updated {size} {measurement_type}: {correct_cm} cm")
        
        print(f"   Total updates: {updated_count}")
        
        # Step 4: Verify the corrections
        print("\n4. VERIFICATION - CORRECTED VALUES:")
        print("=" * 50)
        cursor.execute("""
            SELECT 
                size_label,
                measurement_type,
                measurement_value_in,
                measurement_value_cm,
                ROUND((measurement_value_in * 2.54)::numeric, 1) as calculated_cm,
                CASE 
                    WHEN measurement_value_cm = ROUND((measurement_value_in * 2.54)::numeric, 1) THEN '✅ Match'
                    ELSE '⚠️  Different (brand provided original)'
                END as status
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
            ORDER BY size_label, measurement_type
        """)
        
        corrected_values = cursor.fetchall()
        for row in corrected_values:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']} in → {row['measurement_value_cm']} cm {row['status']}")
        
        # Step 5: Update measurement source type to reflect these are original cm values
        print("\n5. UPDATING MEASUREMENT SOURCE TYPE:")
        print("=" * 50)
        cursor.execute("""
            UPDATE garment_guide_entries
            SET measurement_source_type = 'provided_both'
            WHERE garment_guide_id = 1
            AND measurement_value_cm IS NOT NULL
            AND measurement_value_in IS NOT NULL
        """)
        
        source_updates = cursor.rowcount
        print(f"   ✅ Updated {source_updates} entries to 'provided_both' source type")
        
        # Step 6: Final summary
        print("\n6. FINAL SUMMARY:")
        print("=" * 50)
        cursor.execute("""
            SELECT 
                COUNT(*) as total_measurements,
                COUNT(CASE WHEN measurement_source_type = 'provided_both' THEN 1 END) as dual_source,
                COUNT(CASE WHEN measurement_value_cm IS NOT NULL THEN 1 END) as has_cm,
                COUNT(CASE WHEN measurement_value_in IS NOT NULL THEN 1 END) as has_inches
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
        """)
        
        summary = cursor.fetchone()
        print(f"   Total measurements: {summary['total_measurements']}")
        print(f"   Dual source (provided_both): {summary['dual_source']}")
        print(f"   Has cm values: {summary['has_cm']}")
        print(f"   Has inch values: {summary['has_inches']}")
        
        conn.commit()
        print("\n✅ Original cm values restored successfully!")
        print("\n🎯 Key insight: NN.07 measured in cm, so cm values are the original measurements.")
        print("   The inch values are the brand's conversion for US customers.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    restore_original_cm_values()

