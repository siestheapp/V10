#!/usr/bin/env python3
"""
Check if inch values are from our calculations or exactly as provided in the table
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

def check_inch_values():
    """Check if inch values are from calculations or exact table values"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔍 Checking inch values: calculations vs exact table values...")
        
        # Step 1: Show current inch values in database
        print("\n1. CURRENT INCH VALUES IN DATABASE:")
        print("=" * 60)
        cursor.execute("""
            SELECT 
                size_label,
                measurement_type,
                measurement_value_in,
                measurement_value_cm,
                ROUND((measurement_value_cm / 2.54)::numeric, 1) as calculated_inches
            FROM garment_guide_entries
            WHERE garment_guide_id = 1
            ORDER BY size_label, measurement_type
        """)
        
        db_values = cursor.fetchall()
        for row in db_values:
            print(f"   {row['size_label']} {row['measurement_type']}: {row['measurement_value_in']} in (stored) vs {row['calculated_inches']} in (calculated from cm)")
        
        # Step 2: Define exact inch values from the size guide table
        print("\n2. EXACT INCH VALUES FROM SIZE GUIDE TABLE:")
        print("=" * 60)
        
        # Exact inch values from the size guide table
        exact_inch_values = {
            # Size S
            ('S', 'g_chest_width'): 19.7,
            ('S', 'g_center_back_length'): 26.6,
            ('S', 'g_sleeve_length'): 25.6,
            
            # Size M
            ('M', 'g_chest_width'): 20.5,
            ('M', 'g_center_back_length'): 27.0,
            ('M', 'g_sleeve_length'): 26.0,
            
            # Size L
            ('L', 'g_chest_width'): 21.3,
            ('L', 'g_center_back_length'): 27.4,
            ('L', 'g_sleeve_length'): 26.4,
            
            # Size XL
            ('XL', 'g_chest_width'): 22.0,
            ('XL', 'g_center_back_length'): 27.8,
            ('XL', 'g_sleeve_length'): 26.8,
            
            # Size XXL
            ('XXL', 'g_chest_width'): 23.2,
            ('XXL', 'g_center_back_length'): 28.1,
            ('XXL', 'g_sleeve_length'): 27.2
        }
        
        for (size, measurement_type), exact_inch in exact_inch_values.items():
            print(f"   {size} {measurement_type}: {exact_inch} in")
        
        # Step 3: Compare database values with exact table values
        print("\n3. COMPARISON: DATABASE vs EXACT TABLE VALUES:")
        print("=" * 60)
        
        matches = 0
        mismatches = 0
        
        for row in db_values:
            size = row['size_label']
            measurement_type = row['measurement_type']
            db_inch = row['measurement_value_in']
            calculated_inch = row['calculated_inches']
            
            if (size, measurement_type) in exact_inch_values:
                exact_inch = exact_inch_values[(size, measurement_type)]
                
                if abs(float(db_inch) - exact_inch) < 0.01:
                    status = "✅ EXACT MATCH"
                    matches += 1
                elif abs(float(db_inch) - calculated_inch) < 0.01:
                    status = "🔄 CALCULATED FROM CM"
                    mismatches += 1
                else:
                    status = "❓ UNKNOWN SOURCE"
                    mismatches += 1
                
                print(f"   {size} {measurement_type}: {db_inch} in (DB) vs {exact_inch} in (table) vs {calculated_inch} in (calc) - {status}")
        
        print(f"\n   Summary: {matches} exact matches, {mismatches} different")
        
        # Step 4: Check if we need to update inch values
        print("\n4. ANALYSIS:")
        print("=" * 60)
        
        if mismatches > 0:
            print("   ⚠️  Some inch values don't match the exact table values")
            print("   This suggests the inch values might be calculated from cm rather than")
            print("   being the exact values provided by the brand in their inch table.")
            print("\n   Recommendation: Update inch values to match exact table values")
        else:
            print("   ✅ All inch values match the exact table values")
            print("   The inch values are exactly as provided by the brand")
        
        # Step 5: Show the difference between calculated and exact values
        print("\n5. DIFFERENCES BETWEEN CALCULATED AND EXACT VALUES:")
        print("=" * 60)
        
        for row in db_values:
            size = row['size_label']
            measurement_type = row['measurement_type']
            db_inch = float(row['measurement_value_in'])
            calculated_inch = float(row['calculated_inches'])
            
            if (size, measurement_type) in exact_inch_values:
                exact_inch = exact_inch_values[(size, measurement_type)]
                
                diff_calc = abs(db_inch - calculated_inch)
                diff_exact = abs(db_inch - exact_inch)
                
                if diff_calc < 0.01 and diff_exact > 0.01:
                    print(f"   {size} {measurement_type}: {db_inch} in (DB) = {calculated_inch} in (calc) ≠ {exact_inch} in (table)")
                    print(f"     Difference from table: {diff_exact:.2f} inches")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_inch_values()

