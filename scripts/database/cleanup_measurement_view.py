#!/usr/bin/env python3
"""
Clean up the measurement comparison view by removing redundant column and renaming
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

def cleanup_measurement_view():
    """Remove redundant column and rename user_measurements_missing to user_dimension_feedback_missing"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("🔧 Cleaning up measurement comparison view...")
        
        # Drop and recreate the views
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
                
                -- User dimension feedback missing (what brand offers that user hasn't provided)
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    EXCEPT
                    SELECT unnest(COALESCE((
                        SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                        FROM user_garment_feedback ugf
                        WHERE ugf.user_garment_id = ug.id
                    ), ARRAY[]::TEXT[]))
                ) as user_dimension_feedback_missing,
                
                -- Comparison analysis
                COALESCE(sge.measurements_available, ARRAY[]::TEXT[]) && COALESCE((
                    SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                    FROM user_garment_feedback ugf
                    WHERE ugf.user_garment_id = ug.id
                ), ARRAY[]::TEXT[]) as has_overlap,
                
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
        print("✅ Created cleaned up brand_user_measurement_comparison view")
        
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
                        SELECT unnest(user_dimension_feedback_missing) as dimension
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
        print("🎉 View cleanup complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_cleaned_view():
    """Test the cleaned up view"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n🧪 Testing cleaned up view...")
        
        cursor.execute("""
            SELECT 
                brand_name,
                product_name,
                brand_measurements_available,
                user_measurements_entered,
                user_dimension_feedback_missing,
                user_has_brand_missing,
                matching_measurements,
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
            print(f"   📝 Missing feedback: {row['user_dimension_feedback_missing']}")
            print(f"   🔄 User extra: {row['user_has_brand_missing']}")
            print(f"   ✅ Matching: {row['matching_measurements']}")
            print(f"   📊 Coverage: {row['coverage_percentage']}%")
        
        print(f"\n📋 Column meanings:")
        print(f"   • brand_measurements_available: What the brand's size guide covers")
        print(f"   • user_measurements_entered: What dimensions user provided feedback for")
        print(f"   • user_dimension_feedback_missing: What brand offers but user hasn't provided")
        print(f"   • user_has_brand_missing: What user provided but brand doesn't offer")
        print(f"   • matching_measurements: Overlap between brand and user")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    cleanup_measurement_view()
    test_cleaned_view() 