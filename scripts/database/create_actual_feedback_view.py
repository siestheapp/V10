#!/usr/bin/env python3
"""
Create a view showing only the feedback dimensions that actually exist in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connect_remote_db import create_view, test_connection

def create_actual_feedback_view():
    """Create a view showing only the feedback dimensions that actually exist."""
    
    view_sql = """
    SELECT 
        u.id AS user_id,
        u.email AS user_email,
        ug.id AS garment_id,
        b.name AS brand_name,
        ug.product_name,
        ug.size_label,
        ug.fit_type,
        c.name AS category_name,
        sc.name AS subcategory_name,
        ug.created_at AS garment_created_at,
        -- Only the dimensions that actually have data
        MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_text END) AS overall_feedback,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_text END) AS chest_feedback,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_text END) AS sleeve_feedback,
        MAX(CASE WHEN ugf.dimension = 'length' THEN fc.feedback_text END) AS length_feedback,
        -- Feedback types for the actual dimensions
        MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_type END) AS overall_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_type END) AS chest_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_type END) AS sleeve_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'length' THEN fc.feedback_type END) AS length_feedback_type,
        -- Sentiment for the actual dimensions
        MAX(CASE WHEN ugf.dimension = 'overall' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS overall_sentiment,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS chest_sentiment,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS sleeve_sentiment,
        MAX(CASE WHEN ugf.dimension = 'length' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS length_sentiment,
        -- Timestamps for the actual dimensions
        MAX(CASE WHEN ugf.dimension = 'overall' THEN ugf.created_at END) AS overall_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN ugf.created_at END) AS chest_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN ugf.created_at END) AS sleeve_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'length' THEN ugf.created_at END) AS length_feedback_timestamp
    FROM users u
    LEFT JOIN user_garments ug ON u.id = ug.user_id
    LEFT JOIN brands b ON ug.brand_id = b.id
    LEFT JOIN categories c ON ug.category_id = c.id
    LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
    LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    GROUP BY 
        u.id, u.email,
        ug.id, b.name, ug.product_name, ug.size_label, ug.fit_type,
        c.name, sc.name, ug.created_at
    ORDER BY u.email, ug.created_at DESC
    """
    
    view_name = "user_garments_actual_feedback"
    
    print("🔧 Creating Actual Feedback View (Only Used Dimensions)")
    print("=" * 60)
    print("This view shows only the feedback dimensions that actually exist:")
    print("✅ overall_feedback")
    print("✅ chest_feedback") 
    print("✅ sleeve_feedback")
    print("✅ length_feedback")
    print("❌ waist_feedback (not used in current data)")
    print("❌ neck_feedback (not used in current data)")
    print("❌ hip_feedback (not used in current data)")
    print("=" * 60)
    
    success = create_view(view_name, view_sql)
    
    if success:
        print(f"\n🎉 Successfully created view: {view_name}")
        print("\n📋 You can now query this view with:")
        print(f"SELECT * FROM {view_name};")
        print(f"SELECT * FROM {view_name} WHERE overall_feedback IS NOT NULL;")
        print(f"SELECT * FROM {view_name} WHERE chest_feedback IS NOT NULL;")
    else:
        print(f"\n❌ Failed to create view: {view_name}")
    
    return success

def create_feedback_summary_view():
    """Create a summary view showing feedback statistics."""
    
    view_sql = """
    SELECT 
        u.email AS user_email,
        b.name AS brand_name,
        ug.product_name,
        COUNT(ugf.id) AS total_feedback_count,
        COUNT(CASE WHEN ugf.dimension = 'overall' THEN 1 END) AS overall_feedback_count,
        COUNT(CASE WHEN ugf.dimension = 'chest' THEN 1 END) AS chest_feedback_count,
        COUNT(CASE WHEN ugf.dimension = 'sleeve' THEN 1 END) AS sleeve_feedback_count,
        COUNT(CASE WHEN ugf.dimension = 'length' THEN 1 END) AS length_feedback_count,
        COUNT(CASE WHEN fc.is_positive THEN 1 END) AS positive_feedback_count,
        COUNT(CASE WHEN NOT fc.is_positive THEN 1 END) AS negative_feedback_count
    FROM users u
    LEFT JOIN user_garments ug ON u.id = ug.user_id
    LEFT JOIN brands b ON ug.brand_id = b.id
    LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    GROUP BY u.email, b.name, ug.product_name
    ORDER BY u.email, ug.product_name
    """
    
    view_name = "user_garments_feedback_summary"
    
    print("🔧 Creating Feedback Summary View")
    print("=" * 50)
    print("This view shows feedback statistics:")
    print("✅ Total feedback count per garment")
    print("✅ Feedback count by dimension")
    print("✅ Positive vs negative feedback count")
    print("=" * 50)
    
    success = create_view(view_name, view_sql)
    
    if success:
        print(f"\n🎉 Successfully created view: {view_name}")
        print("\n📋 You can now query this view with:")
        print(f"SELECT * FROM {view_name};")
        print(f"SELECT * FROM {view_name} WHERE total_feedback_count > 0;")
    else:
        print(f"\n❌ Failed to create view: {view_name}")
    
    return success

if __name__ == "__main__":
    print("🎯 Creating Actual Feedback Views")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to database. Exiting.")
        sys.exit(1)
    
    # Create both views
    create_actual_feedback_view()
    print("\n" + "="*50 + "\n")
    create_feedback_summary_view() 