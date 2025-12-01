#!/usr/bin/env python3
"""
Test the new actual feedback views to show the difference.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connect_remote_db import connect_to_database

def test_actual_feedback_view():
    """Test the actual feedback view (only used dimensions)."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("📋 Testing Actual Feedback View (Only Used Dimensions)")
            print("=" * 60)
            
            # Get total count
            cur.execute("SELECT COUNT(*) FROM user_garments_actual_feedback;")
            count = cur.fetchone()[0]
            print(f"Total records: {count}")
            
            # Get sample data with feedback
            cur.execute("""
                SELECT user_email, brand_name, product_name, 
                       overall_feedback, chest_feedback, sleeve_feedback, length_feedback
                FROM user_garments_actual_feedback 
                WHERE overall_feedback IS NOT NULL OR chest_feedback IS NOT NULL 
                   OR sleeve_feedback IS NOT NULL OR length_feedback IS NOT NULL
                LIMIT 5;
            """)
            
            rows = cur.fetchall()
            if rows:
                print("\nSample data (only dimensions that actually exist):")
                for row in rows:
                    email, brand, product, overall, chest, sleeve, length = row
                    print(f"  {email}: {brand} {product}")
                    if overall:
                        print(f"    Overall: {overall}")
                    if chest:
                        print(f"    Chest: {chest}")
                    if sleeve:
                        print(f"    Sleeve: {sleeve}")
                    if length:
                        print(f"    Length: {length}")
                    print()
            else:
                print("No feedback data found.")
                
            # Show view structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_garments_actual_feedback' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            print("\nView structure (only actual dimensions):")
            for col_name, data_type in columns:
                print(f"  {col_name}: {data_type}")
                
    except Exception as e:
        print(f"❌ Error testing actual feedback view: {e}")
        return False
    finally:
        conn.close()
    
    return True

def test_feedback_summary_view():
    """Test the feedback summary view."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("\n📊 Testing Feedback Summary View")
            print("=" * 50)
            
            # Get summary data
            cur.execute("""
                SELECT user_email, brand_name, product_name, 
                       total_feedback_count, overall_feedback_count, 
                       chest_feedback_count, sleeve_feedback_count, length_feedback_count,
                       positive_feedback_count, negative_feedback_count
                FROM user_garments_feedback_summary 
                WHERE total_feedback_count > 0
                ORDER BY total_feedback_count DESC;
            """)
            
            rows = cur.fetchall()
            if rows:
                print("\nFeedback Summary by Garment:")
                for row in rows:
                    email, brand, product, total, overall, chest, sleeve, length, positive, negative = row
                    print(f"  {email}: {brand} {product}")
                    print(f"    Total feedback: {total}")
                    print(f"    By dimension: Overall({overall}), Chest({chest}), Sleeve({sleeve}), Length({length})")
                    print(f"    Sentiment: Positive({positive}), Negative({negative})")
                    print()
            else:
                print("No feedback summary data found.")
                
    except Exception as e:
        print(f"❌ Error testing feedback summary view: {e}")
        return False
    finally:
        conn.close()
    
    return True

def compare_views():
    """Compare the comprehensive view vs actual feedback view."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("\n🔍 Comparing Views")
            print("=" * 50)
            
            # Count columns in each view
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'user_garment_feedback_summary';
            """)
            comprehensive_cols = cur.fetchone()[0]
            
            cur.execute("""
                SELECT COUNT(*) 
                FROM information_schema.columns 
                WHERE table_name = 'user_garments_actual_feedback';
            """)
            actual_cols = cur.fetchone()[0]
            
            print(f"Comprehensive view columns: {comprehensive_cols}")
            print(f"Actual feedback view columns: {actual_cols}")
            print(f"Difference: {comprehensive_cols - actual_cols} fewer columns")
            
            # Show unused dimensions in comprehensive view
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user_garment_feedback_summary' 
                AND column_name LIKE '%waist%' OR column_name LIKE '%neck%' OR column_name LIKE '%hip%'
                ORDER BY column_name;
            """)
            
            unused_cols = cur.fetchall()
            if unused_cols:
                print(f"\nUnused dimensions in comprehensive view:")
                for col in unused_cols:
                    print(f"  - {col[0]}")
                    
    except Exception as e:
        print(f"❌ Error comparing views: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🧪 Testing Actual Feedback Views")
    print("=" * 50)
    
    test_actual_feedback_view()
    test_feedback_summary_view()
    compare_views() 