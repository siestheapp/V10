#!/usr/bin/env python3
"""
Create a view that shows user garment feedback with dimensions on separate rows
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

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def create_feedback_dimension_view():
    """Create a view that shows feedback with dimensions on separate rows"""
    
    view_sql = """
    CREATE OR REPLACE VIEW user_feedback_by_dimension AS
    SELECT 
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
    ORDER BY u.email, ug.created_at DESC, ugf.dimension;
    """
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create the view
        cursor.execute(view_sql)
        conn.commit()
        
        print("✅ Successfully created view: user_feedback_by_dimension")
        
        # Test the view with a sample query
        cursor.execute("""
            SELECT 
                user_id,
                user_email,
                user_garment_id,
                product_name,
                dimension,
                feedback_text,
                feedback_type,
                is_positive
            FROM user_feedback_by_dimension 
            ORDER BY user_email, user_garment_id, dimension 
            LIMIT 10;
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 Sample data from the new view:")
        print("-" * 80)
        for row in results:
            print(f"User: {row[1]} | Garment: {row[3]} | Dimension: {row[4]} | Feedback: {row[5]} ({row[6]})")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating view: {e}")
        return False

if __name__ == "__main__":
    create_feedback_dimension_view() 