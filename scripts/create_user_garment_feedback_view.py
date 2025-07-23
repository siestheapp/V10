#!/usr/bin/env python3
"""
Create User Garment Feedback View
Creates a comprehensive view showing user information, garment details, and feedback.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connect_remote_db import create_view, test_connection

def create_user_garment_feedback_view():
    """Create a comprehensive view showing user garments with feedback."""
    
    view_sql = """
    SELECT 
        u.id AS user_id,
        u.email AS user_email,
        u.gender AS user_gender,
        ug.id AS garment_id,
        b.name AS brand_name,
        ug.product_name,
        ug.size_label,
        ug.fit_type,
        ug.unit,
        c.name AS category_name,
        sc.name AS subcategory_name,
        ug.fit_feedback AS general_feedback,
        ug.feedback_timestamp,
        ug.owns_garment,
        ug.created_at AS garment_created_at,
        ug.updated_at AS garment_updated_at,
        -- Detailed feedback by dimension
        MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_text END) AS overall_feedback,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_text END) AS chest_feedback,
        MAX(CASE WHEN ugf.dimension = 'waist' THEN fc.feedback_text END) AS waist_feedback,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_text END) AS sleeve_feedback,
        MAX(CASE WHEN ugf.dimension = 'neck' THEN fc.feedback_text END) AS neck_feedback,
        MAX(CASE WHEN ugf.dimension = 'hip' THEN fc.feedback_text END) AS hip_feedback,
        MAX(CASE WHEN ugf.dimension = 'length' THEN fc.feedback_text END) AS length_feedback,
        -- Feedback types
        MAX(CASE WHEN ugf.dimension = 'overall' THEN fc.feedback_type END) AS overall_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN fc.feedback_type END) AS chest_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'waist' THEN fc.feedback_type END) AS waist_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN fc.feedback_type END) AS sleeve_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'neck' THEN fc.feedback_type END) AS neck_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'hip' THEN fc.feedback_type END) AS hip_feedback_type,
        MAX(CASE WHEN ugf.dimension = 'length' THEN fc.feedback_type END) AS length_feedback_type,
        -- Positive/negative indicators (using string conversion)
        MAX(CASE WHEN ugf.dimension = 'overall' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS overall_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS chest_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'waist' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS waist_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS sleeve_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'neck' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS neck_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'hip' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS hip_feedback_sentiment,
        MAX(CASE WHEN ugf.dimension = 'length' THEN CASE WHEN fc.is_positive THEN 'positive' ELSE 'negative' END END) AS length_feedback_sentiment,
        -- Feedback timestamps
        MAX(CASE WHEN ugf.dimension = 'overall' THEN ugf.created_at END) AS overall_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'chest' THEN ugf.created_at END) AS chest_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'waist' THEN ugf.created_at END) AS waist_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'sleeve' THEN ugf.created_at END) AS sleeve_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'neck' THEN ugf.created_at END) AS neck_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'hip' THEN ugf.created_at END) AS hip_feedback_timestamp,
        MAX(CASE WHEN ugf.dimension = 'length' THEN ugf.created_at END) AS length_feedback_timestamp
    FROM users u
    LEFT JOIN user_garments ug ON u.id = ug.user_id
    LEFT JOIN brands b ON ug.brand_id = b.id
    LEFT JOIN categories c ON ug.category_id = c.id
    LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
    LEFT JOIN user_garment_feedback ugf ON ug.id = ugf.user_garment_id
    LEFT JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
    GROUP BY 
        u.id, u.email, u.gender,
        ug.id, b.name, ug.product_name, ug.size_label, ug.fit_type, ug.unit,
        c.name, sc.name, ug.fit_feedback, ug.feedback_timestamp, ug.owns_garment,
        ug.created_at, ug.updated_at
    ORDER BY u.email, ug.created_at DESC
    """
    
    view_name = "user_garment_feedback_summary"
    
    print("🔧 Creating User Garment Feedback Summary View...")
    print("=" * 60)
    print("This view will show:")
    print("✅ User ID and email")
    print("✅ Garment ID and details")
    print("✅ Brand name and product name")
    print("✅ Category and subcategory")
    print("✅ General fit feedback")
    print("✅ Detailed feedback by dimension (chest, waist, sleeve, etc.)")
    print("✅ Feedback types and sentiment indicators")
    print("✅ Timestamps for all feedback")
    print("=" * 60)
    
    success = create_view(view_name, view_sql)
    
    if success:
        print(f"\n🎉 Successfully created view: {view_name}")
        print("\n📋 You can now query this view with:")
        print(f"SELECT * FROM {view_name};")
        print(f"SELECT * FROM {view_name} WHERE user_email = 'example@email.com';")
        print(f"SELECT * FROM {view_name} WHERE brand_name = 'Brand Name';")
        print(f"SELECT * FROM {view_name} WHERE overall_feedback IS NOT NULL;")
    else:
        print(f"\n❌ Failed to create view: {view_name}")
    
    return success

def create_simple_user_garment_view():
    """Create a simpler view with just the basic requested fields."""
    
    view_sql = """
    SELECT 
        u.id AS user_id,
        u.email AS user_email,
        ug.id AS garment_id,
        b.name AS brand_name,
        ug.product_name,
        ug.fit_feedback,
        ug.feedback_timestamp,
        ug.size_label,
        ug.fit_type,
        c.name AS category_name,
        sc.name AS subcategory_name
    FROM users u
    LEFT JOIN user_garments ug ON u.id = ug.user_id
    LEFT JOIN brands b ON ug.brand_id = b.id
    LEFT JOIN categories c ON ug.category_id = c.id
    LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
    ORDER BY u.email, ug.created_at DESC
    """
    
    view_name = "user_garments_simple"
    
    print("🔧 Creating Simple User Garments View...")
    print("=" * 50)
    print("This view shows the basic requested fields:")
    print("✅ User ID and email")
    print("✅ Garment ID")
    print("✅ Brand name")
    print("✅ Product name")
    print("✅ General fit feedback")
    print("=" * 50)
    
    success = create_view(view_name, view_sql)
    
    if success:
        print(f"\n🎉 Successfully created view: {view_name}")
        print("\n📋 You can now query this view with:")
        print(f"SELECT * FROM {view_name};")
        print(f"SELECT * FROM {view_name} WHERE user_email = 'example@email.com';")
    else:
        print(f"\n❌ Failed to create view: {view_name}")
    
    return success

if __name__ == "__main__":
    print("👕 User Garment Feedback View Creator")
    print("=" * 50)
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot connect to database. Exiting.")
        sys.exit(1)
    
    if len(sys.argv) > 1 and sys.argv[1] == "simple":
        create_simple_user_garment_view()
    else:
        # Create the comprehensive view by default
        create_user_garment_feedback_view() 