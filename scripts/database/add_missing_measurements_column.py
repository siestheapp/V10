#!/usr/bin/env python3
"""
Add user_measurements_missing column to the brand_user_measurement_comparison view
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

def update_view_with_missing_measurements():
    """Update the view to include user_measurements_missing column"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("🔧 Adding user_measurements_missing column to view...")
        
        # Drop and recreate the view to add new column
        cursor.execute("""
            DROP VIEW IF EXISTS brand_measurement_coverage_summary;
            DROP VIEW IF EXISTS brand_user_measurement_comparison;
        """)
        print("✅ Dropped existing views")
        
        cursor.execute("""
            CREATE VIEW brand_user_measurement_comparison AS
            SELECT 
                ug.id as garment_id,
                ug.user_id,
                b.name as brand_name,
                ug.product_name,
                ug.size_label,
                
                -- Brand measurements available (from size_guide_entries)
                COALESCE(sge.measurements_available, ARRAY[]::TEXT[]) as brand_measurements_available,
                
                -- User measurements entered (calculated dynamically from feedback)
                COALESCE((
                    SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                    FROM user_garment_feedback ugf
                    WHERE ugf.user_garment_id = ug.id
                ), ARRAY[]::TEXT[]) as user_measurements_entered,
                
                -- User measurements missing (what brand offers that user hasn't provided)
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    EXCEPT
                    SELECT unnest(COALESCE((
                        SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                        FROM user_garment_feedback ugf
                        WHERE ugf.user_garment_id = ug.id
                    ), ARRAY[]::TEXT[]))
                ) as user_measurements_missing,
                
                -- Comparison analysis
                COALESCE(sge.measurements_available, ARRAY[]::TEXT[]) && COALESCE((
                    SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                    FROM user_garment_feedback ugf
                    WHERE ugf.user_garment_id = ug.id
                ), ARRAY[]::TEXT[]) as has_overlap,
                
                -- What brand offers that user hasn't provided (same as user_measurements_missing, kept for backwards compatibility)
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    EXCEPT
                    SELECT unnest(COALESCE((
                        SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                        FROM user_garment_feedback ugf
                        WHERE ugf.user_garment_id = ug.id
                    ), ARRAY[]::TEXT[]))
                ) as brand_has_user_missing,
                
                -- What user provided that brand doesn't offer
                ARRAY(
                    SELECT unnest(COALESCE((
                        SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                        FROM user_garment_feedback ugf
                        WHERE ugf.user_garment_id = ug.id
                    ), ARRAY[]::TEXT[]))
                    EXCEPT  
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                ) as user_has_brand_missing,
                
                -- Matching measurements
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    INTERSECT
                    SELECT unnest(COALESCE((
                        SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                        FROM user_garment_feedback ugf
                        WHERE ugf.user_garment_id = ug.id
                    ), ARRAY[]::TEXT[]))
                ) as matching_measurements,
                
                -- Coverage percentage
                CASE 
                    WHEN COALESCE(array_length(sge.measurements_available, 1), 0) = 0 THEN 0
                    ELSE ROUND(
                        (array_length(ARRAY(
                            SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                            INTERSECT
                            SELECT unnest(COALESCE((
                                SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                                FROM user_garment_feedback ugf
                                WHERE ugf.user_garment_id = ug.id
                            ), ARRAY[]::TEXT[]))
                        ), 1)::NUMERIC / array_length(sge.measurements_available, 1)) * 100, 1
                    )
                END as coverage_percentage,
                
                ug.created_at
                
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
            WHERE ug.owns_garment = true
            ORDER BY b.name, ug.created_at DESC;
        """)
        print("✅ Created brand_user_measurement_comparison view with user_measurements_missing")
        
        # Recreate the summary view
        cursor.execute("""
            CREATE VIEW brand_measurement_coverage_summary AS
            SELECT 
                brand_name,
                COUNT(*) as total_garments,
                ROUND(AVG(coverage_percentage), 1) as avg_coverage_percentage,
                COUNT(*) FILTER (WHERE coverage_percentage = 100) as fully_covered_garments,
                COUNT(*) FILTER (WHERE coverage_percentage = 0) as no_coverage_garments,
                
                -- Most common missing measurements
                (
                    SELECT dimension
                    FROM (
                        SELECT unnest(brand_has_user_missing) as dimension
                        FROM brand_user_measurement_comparison 
                        WHERE brand_name = outer_summary.brand_name
                    ) missing_dims
                    GROUP BY dimension
                    ORDER BY COUNT(*) DESC
                    LIMIT 1
                ) as most_missing_dimension
                
            FROM brand_user_measurement_comparison outer_summary
            GROUP BY brand_name
            ORDER BY avg_coverage_percentage DESC;
        """)
        print("✅ Recreated brand_measurement_coverage_summary view")
        
        conn.commit()
        print("🎉 Views updated successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_updated_view():
    """Test the updated view with the new column"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n🧪 Testing updated view with user_measurements_missing...")
        
        cursor.execute("""
            SELECT 
                brand_name,
                product_name,
                brand_measurements_available,
                user_measurements_entered,
                user_measurements_missing,
                coverage_percentage
            FROM brand_user_measurement_comparison
            ORDER BY brand_name;
        """)
        
        results = cursor.fetchall()
        print(f"\n📊 Found {len(results)} garments:")
        
        for row in results:
            print(f"\n🏷️  {row['brand_name']} - {row['product_name']}")
            print(f"   Brand offers: {row['brand_measurements_available']}")
            print(f"   User entered: {row['user_measurements_entered']}")
            print(f"   📝 Missing: {row['user_measurements_missing']}")
            print(f"   Coverage: {row['coverage_percentage']}%")
        
        # Show summary of what's most commonly missing
        cursor.execute("""
            SELECT 
                brand_name,
                unnest(user_measurements_missing) as missing_dimension,
                COUNT(*) as missing_count
            FROM brand_user_measurement_comparison
            WHERE array_length(user_measurements_missing, 1) > 0
            GROUP BY brand_name, missing_dimension
            ORDER BY brand_name, missing_count DESC;
        """)
        
        missing_summary = cursor.fetchall()
        if missing_summary:
            print(f"\n📈 Most commonly missing measurements by brand:")
            current_brand = None
            for row in missing_summary:
                if row['brand_name'] != current_brand:
                    current_brand = row['brand_name']
                    print(f"\n   {current_brand}:")
                print(f"     - {row['missing_dimension']}: {row['missing_count']} garments")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    update_view_with_missing_measurements()
    test_updated_view() 