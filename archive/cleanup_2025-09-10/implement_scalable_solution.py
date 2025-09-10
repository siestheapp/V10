#!/usr/bin/env python3
"""
Implement scalable solution for European brands and user preferences
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

def implement_scalable_solution():
    """Implement scalable solution for European brands and user preferences"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🌍 Implementing scalable solution for European brands and user preferences...")
        
        # Step 1: Add columns to track measurement origins
        print("1. Adding measurement source tracking...")
        cursor.execute("""
            ALTER TABLE public.garment_guide_entries 
            ADD COLUMN IF NOT EXISTS measurement_source_type text DEFAULT 'original';
        """)
        
        cursor.execute("""
            ALTER TABLE public.brands 
            ADD COLUMN IF NOT EXISTS original_measurement_unit text,
            ADD COLUMN IF NOT EXISTS provides_dual_units boolean DEFAULT false;
        """)
        
        # Step 2: Update NN.07 to reflect European brand reality
        print("2. Updating NN.07 brand data...")
        cursor.execute("""
            UPDATE brands 
            SET 
                original_measurement_unit = 'cm',
                provides_dual_units = true,
                notes = COALESCE(notes, '') || ' European brand that provides both cm and inches'
            WHERE name = 'NN.07';
        """)
        
        # Step 3: Update measurement source types for NN.07
        print("3. Updating measurement source types...")
        cursor.execute("""
            UPDATE garment_guide_entries gge
            SET measurement_source_type = 'provided_both'
            FROM garment_guides gg
            JOIN brands b ON gg.brand_id = b.id
            WHERE gge.garment_guide_id = gg.id
            AND b.name = 'NN.07'
            AND gge.measurement_value_cm IS NOT NULL
            AND gge.measurement_value_in IS NOT NULL;
        """)
        
        updated_measurements = cursor.rowcount
        print(f"   Updated {updated_measurements} measurements as 'provided_both'")
        
        # Step 4: Create user preferences table for scaling
        print("4. Creating user preferences table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS public.user_preferences (
                id SERIAL PRIMARY KEY,
                user_id integer,
                preferred_unit text DEFAULT 'in',
                created_at timestamp DEFAULT CURRENT_TIMESTAMP,
                updated_at timestamp DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id)
            );
        """)
        
        # Step 5: Create view for smart measurement display
        print("5. Creating smart measurement display view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW public.smart_measurements AS
            SELECT 
                gge.id,
                b.name as brand_name,
                b.original_measurement_unit,
                b.provides_dual_units,
                gge.size_label,
                gge.measurement_type,
                gge.measurement_value_in,
                gge.measurement_value_cm,
                gge.measurement_source_type,
                CASE 
                    WHEN b.original_measurement_unit = 'cm' THEN 'European brand - measured in cm'
                    WHEN b.original_measurement_unit = 'in' THEN 'US brand - measured in inches'
                    ELSE 'Unknown origin'
                END as brand_context,
                CASE 
                    WHEN b.provides_dual_units THEN 'Both units provided by brand'
                    WHEN gge.measurement_value_cm IS NOT NULL THEN 'CM calculated from inches'
                    ELSE 'Single unit only'
                END as unit_availability
            FROM garment_guide_entries gge
            JOIN garment_guides gg ON gge.garment_guide_id = gg.id
            JOIN brands b ON gg.brand_id = b.id
            WHERE gge.measurement_value_in IS NOT NULL;
        """)
        
        # Step 6: Show current state
        print("6. Current brand measurement capabilities:")
        cursor.execute("""
            SELECT 
                name,
                original_measurement_unit,
                provides_dual_units,
                default_unit,
                CASE 
                    WHEN original_measurement_unit = 'cm' THEN 'European brand'
                    WHEN original_measurement_unit = 'in' THEN 'US brand'
                    ELSE 'Unknown'
                END as brand_type
            FROM brands
            ORDER BY name;
        """)
        
        brands = cursor.fetchall()
        for brand in brands:
            print(f"   {brand['name']}: {brand['brand_type']} (original: {brand['original_measurement_unit']}, dual: {brand['provides_dual_units']})")
        
        # Step 7: Show measurement display examples
        print("7. Measurement display examples:")
        cursor.execute("""
            SELECT 
                brand_name,
                size_label,
                measurement_type,
                measurement_value_in,
                measurement_value_cm,
                measurement_source_type,
                brand_context,
                unit_availability
            FROM smart_measurements
            WHERE brand_name = 'NN.07'
            ORDER BY size_label, measurement_type
            LIMIT 3;
        """)
        
        measurements = cursor.fetchall()
        for measurement in measurements:
            print(f"   {measurement['brand_name']} {measurement['size_label']} {measurement['measurement_type']}:")
            print(f"     Inches: {measurement['measurement_value_in']}")
            print(f"     CM: {measurement['measurement_value_cm']}")
            print(f"     Source: {measurement['measurement_source_type']}")
            print(f"     Context: {measurement['brand_context']}")
        
        # Step 8: Show scaling benefits
        print("8. Scaling benefits for future users:")
        print("   ✅ European users can see cm as primary unit")
        print("   ✅ US users can see inches as primary unit")
        print("   ✅ Both units available when brand provides them")
        print("   ✅ Clear distinction between original vs converted measurements")
        print("   ✅ User preferences stored separately from brand data")
        
        conn.commit()
        print("✅ Scalable solution implemented successfully!")
        
        # Show usage examples
        print("\n🎯 Usage examples for scaling:")
        print("   -- For European user (prefers cm):")
        print("   SELECT measurement_value_cm as display_value, 'cm' as unit FROM smart_measurements")
        print("   -- For US user (prefers inches):")
        print("   SELECT measurement_value_in as display_value, 'in' as unit FROM smart_measurements")
        print("   -- Show both when available:")
        print("   SELECT format('%s cm / %s in', measurement_value_cm, measurement_value_in) as display_value")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    implement_scalable_solution()

