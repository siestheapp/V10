#!/usr/bin/env python3
"""
Add measurements_entered column and create brand-user measurement comparison view
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

def add_measurements_entered():
    """Add measurements_entered column to user_garments and populate it"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("🔧 Adding measurements_entered column...")
        
        # 1. Add the column
        cursor.execute("""
            ALTER TABLE user_garments 
            ADD COLUMN IF NOT EXISTS measurements_entered TEXT[];
        """)
        print("✅ Added measurements_entered column")
        
        # 2. Create function to calculate measurements_entered
        cursor.execute("""
            CREATE OR REPLACE FUNCTION calculate_measurements_entered(garment_id INTEGER)
            RETURNS TEXT[] AS $$
            DECLARE
                dimensions TEXT[];
            BEGIN
                SELECT ARRAY_AGG(DISTINCT dimension ORDER BY dimension)
                INTO dimensions
                FROM user_garment_feedback
                WHERE user_garment_id = garment_id;
                
                RETURN COALESCE(dimensions, ARRAY[]::TEXT[]);
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ Created calculate_measurements_entered function")
        
        # 3. Update existing records
        cursor.execute("""
            UPDATE user_garments 
            SET measurements_entered = calculate_measurements_entered(id);
        """)
        print("✅ Populated measurements_entered for existing garments")
        
        # 4. Create trigger to auto-update measurements_entered when feedback changes
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_measurements_entered()
            RETURNS TRIGGER AS $$
            BEGIN
                -- Update the corresponding user_garment record
                IF TG_OP = 'INSERT' OR TG_OP = 'UPDATE' THEN
                    UPDATE user_garments 
                    SET measurements_entered = calculate_measurements_entered(NEW.user_garment_id)
                    WHERE id = NEW.user_garment_id;
                    RETURN NEW;
                ELSIF TG_OP = 'DELETE' THEN
                    UPDATE user_garments 
                    SET measurements_entered = calculate_measurements_entered(OLD.user_garment_id)
                    WHERE id = OLD.user_garment_id;
                    RETURN OLD;
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        cursor.execute("""
            DROP TRIGGER IF EXISTS trigger_update_measurements_entered ON user_garment_feedback;
            CREATE TRIGGER trigger_update_measurements_entered
            AFTER INSERT OR UPDATE OR DELETE ON user_garment_feedback
            FOR EACH ROW EXECUTE FUNCTION update_measurements_entered();
        """)
        print("✅ Created auto-update trigger for measurements_entered")
        
        conn.commit()
        print("🎉 measurements_entered setup complete!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def create_measurement_comparison_view():
    """Create view comparing brand measurements vs user measurements"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n🔧 Creating measurement comparison view...")
        
        cursor.execute("""
            CREATE OR REPLACE VIEW brand_user_measurement_comparison AS
            SELECT 
                ug.id as garment_id,
                ug.user_id,
                b.name as brand_name,
                ug.product_name,
                ug.size_label,
                
                -- Brand measurements available (from size_guide_entries)
                COALESCE(sge.measurements_available, ARRAY[]::TEXT[]) as brand_measurements_available,
                
                -- User measurements entered  
                COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]) as user_measurements_entered,
                
                -- Comparison analysis
                COALESCE(sge.measurements_available, ARRAY[]::TEXT[]) && COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]) as has_overlap,
                
                -- What brand offers that user hasn't provided
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    EXCEPT
                    SELECT unnest(COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]))
                ) as brand_has_user_missing,
                
                -- What user provided that brand doesn't offer
                ARRAY(
                    SELECT unnest(COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]))
                    EXCEPT  
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                ) as user_has_brand_missing,
                
                -- Matching measurements
                ARRAY(
                    SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                    INTERSECT
                    SELECT unnest(COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]))
                ) as matching_measurements,
                
                -- Coverage percentage
                CASE 
                    WHEN COALESCE(array_length(sge.measurements_available, 1), 0) = 0 THEN 0
                    ELSE ROUND(
                        (array_length(ARRAY(
                            SELECT unnest(COALESCE(sge.measurements_available, ARRAY[]::TEXT[]))
                            INTERSECT
                            SELECT unnest(COALESCE(ug.measurements_entered, ARRAY[]::TEXT[]))
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
        print("✅ Created brand_user_measurement_comparison view")
        
        # Create a summary view as well
        cursor.execute("""
            CREATE OR REPLACE VIEW brand_measurement_coverage_summary AS
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
        print("✅ Created brand_measurement_coverage_summary view")
        
        conn.commit()
        print("🎉 Measurement comparison views created!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_views():
    """Test the new views with sample data"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        print("\n🧪 Testing measurement comparison views...")
        
        # Test the main comparison view
        cursor.execute("""
            SELECT 
                brand_name,
                product_name,
                brand_measurements_available,
                user_measurements_entered,
                matching_measurements,
                coverage_percentage
            FROM brand_user_measurement_comparison
            ORDER BY brand_name
            LIMIT 10;
        """)
        
        results = cursor.fetchall()
        print(f"\n📊 Found {len(results)} garments with measurement comparison:")
        
        for row in results:
            print(f"\n🏷️  {row['brand_name']} - {row['product_name']}")
            print(f"   Brand offers: {row['brand_measurements_available']}")
            print(f"   User entered: {row['user_measurements_entered']}")
            print(f"   Matching: {row['matching_measurements']}")
            print(f"   Coverage: {row['coverage_percentage']}%")
        
        # Test the summary view
        cursor.execute("SELECT * FROM brand_measurement_coverage_summary;")
        summary = cursor.fetchall()
        
        print(f"\n📈 Brand Coverage Summary:")
        for row in summary:
            print(f"   {row['brand_name']}: {row['avg_coverage_percentage']}% avg coverage "
                  f"({row['fully_covered_garments']}/{row['total_garments']} fully covered)")
        
    except Exception as e:
        print(f"❌ Test error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    add_measurements_entered()
    create_measurement_comparison_view()
    test_views() 