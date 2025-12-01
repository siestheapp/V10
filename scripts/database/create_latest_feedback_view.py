#!/usr/bin/env python3
"""
Create a view that shows only the most recent feedback for each garment and dimension
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

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def create_latest_feedback_view():
    """Create a view that shows only the most recent feedback per garment/dimension"""
    
    view_sql = """
    CREATE OR REPLACE VIEW user_latest_feedback_by_dimension AS
    SELECT DISTINCT ON (user_id, user_garment_id, dimension) 
        u.id AS user_id,
        u.email AS user_email,
        u.gender AS user_gender,
        ug.id AS user_garment_id,
        ug.product_name,
        ug.size_label,
        ug.fit_type,
        ug.owns_garment,
        ug.created_at AS garment_created_at,
        b.name AS brand_name,
        c.name AS category_name,
        sc.name AS subcategory_name,
        ugf.dimension,
        fc.feedback_text,
        fc.feedback_type,
        fc.is_positive,
        ugf.created_at AS feedback_created_at,
        ugf.created_by AS feedback_created_by
    FROM users u
    JOIN user_garments ug ON u.id = ug.user_id
    JOIN brands b ON ug.brand_id = b.id
    JOIN categories c ON ug.category_id = c.id
    LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
    JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
    JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    ORDER BY user_id, user_garment_id, dimension, ugf.created_at DESC;
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create the view
        cursor.execute(view_sql)
        conn.commit()
        
        print("✅ Successfully created view: user_latest_feedback_by_dimension")
        
        # Test the view with a sample query
        cursor.execute("""
            SELECT 
                user_id,
                user_email,
                user_garment_id,
                product_name,
                dimension,
                feedback_text,
                feedback_created_at
            FROM user_latest_feedback_by_dimension 
            ORDER BY user_email, user_garment_id, dimension 
            LIMIT 10;
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 Sample data from the new view (latest feedback only):")
        print("-" * 80)
        for row in results:
            print(f"User: {row[1]} | Garment: {row[3]} | Dimension: {row[4]} | Feedback: {row[5]} | Date: {row[6]}")
        
        # Show comparison with original view
        cursor.execute("""
            SELECT COUNT(*) as total_feedback_entries 
            FROM user_feedback_by_dimension;
        """)
        total_entries = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) as latest_feedback_entries 
            FROM user_latest_feedback_by_dimension;
        """)
        latest_entries = cursor.fetchone()[0]
        
        print(f"\n📈 Comparison:")
        print(f"Original view entries: {total_entries}")
        print(f"Latest feedback entries: {latest_entries}")
        print(f"Duplicate entries removed: {total_entries - latest_entries}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating view: {e}")
        return False

if __name__ == "__main__":
    create_latest_feedback_view() 