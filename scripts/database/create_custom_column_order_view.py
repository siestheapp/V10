#!/usr/bin/env python3
"""
Create a view with custom column order for better readability
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

def create_custom_order_view():
    """Create a view with custom column order"""
    
    view_sql = """
    CREATE OR REPLACE VIEW user_feedback_organized AS
    SELECT 
        -- User info first
        u.email AS user_email,
        u.gender AS user_gender,
        
        -- Garment info
        b.name AS brand_name,
        ug.product_name,
        ug.size_label,
        ug.fit_type,
        
        -- Feedback info
        ugf.dimension,
        fc.feedback_text,
        fc.feedback_type,
        fc.is_positive,
        
        -- Metadata
        ugf.created_at AS feedback_created_at,
        ug.owns_garment,
        ug.created_at AS garment_created_at,
        
        -- IDs (at the end)
        u.id AS user_id,
        ug.id AS user_garment_id,
        ugf.id AS feedback_id
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
        
        print("✅ Successfully created view: user_feedback_organized")
        
        # Test the view
        cursor.execute("""
            SELECT 
                user_email,
                brand_name,
                product_name,
                dimension,
                feedback_text,
                feedback_created_at
            FROM user_feedback_organized 
            ORDER BY user_email, product_name, dimension 
            LIMIT 8;
        """)
        
        results = cursor.fetchall()
        
        print("\n📊 Sample data with organized columns:")
        print("-" * 80)
        for row in results:
            print(f"User: {row[0]} | Brand: {row[1]} | Product: {row[2]} | Dimension: {row[3]} | Feedback: {row[4]} | Date: {row[5]}")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating view: {e}")
        return False

if __name__ == "__main__":
    create_custom_order_view() 