#!/usr/bin/env python3
"""
Test the newly created views to see sample data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connect_remote_db import connect_to_database

def test_simple_view():
    """Test the simple user garments view."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("📋 Testing Simple User Garments View:")
            print("=" * 50)
            
            # Get total count
            cur.execute("SELECT COUNT(*) FROM user_garments_simple;")
            count = cur.fetchone()[0]
            print(f"Total records: {count}")
            
            # Get sample data
            cur.execute("""
                SELECT user_id, user_email, garment_id, brand_name, product_name, fit_feedback
                FROM user_garments_simple 
                LIMIT 5;
            """)
            
            rows = cur.fetchall()
            if rows:
                print("\nSample data:")
                for row in rows:
                    user_id, email, garment_id, brand, product, feedback = row
                    print(f"  User {user_id} ({email}): Garment {garment_id} - {brand} {product}")
                    if feedback:
                        print(f"    Feedback: {feedback}")
                    print()
            else:
                print("No data found in the view.")
                
    except Exception as e:
        print(f"❌ Error testing simple view: {e}")
        return False
    finally:
        conn.close()
    
    return True

def test_comprehensive_view():
    """Test the comprehensive user garment feedback view."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("📋 Testing Comprehensive User Garment Feedback View:")
            print("=" * 60)
            
            # Get total count
            cur.execute("SELECT COUNT(*) FROM user_garment_feedback_summary;")
            count = cur.fetchone()[0]
            print(f"Total records: {count}")
            
            # Get sample data with feedback
            cur.execute("""
                SELECT user_id, user_email, garment_id, brand_name, product_name, 
                       overall_feedback, chest_feedback, waist_feedback
                FROM user_garment_feedback_summary 
                WHERE overall_feedback IS NOT NULL OR chest_feedback IS NOT NULL OR waist_feedback IS NOT NULL
                LIMIT 5;
            """)
            
            rows = cur.fetchall()
            if rows:
                print("\nSample data with feedback:")
                for row in rows:
                    user_id, email, garment_id, brand, product, overall, chest, waist = row
                    print(f"  User {user_id} ({email}): Garment {garment_id} - {brand} {product}")
                    if overall:
                        print(f"    Overall: {overall}")
                    if chest:
                        print(f"    Chest: {chest}")
                    if waist:
                        print(f"    Waist: {waist}")
                    print()
            else:
                print("No feedback data found.")
                
            # Show view structure
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'user_garment_feedback_summary' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            print("\nView structure:")
            for col_name, data_type in columns:
                print(f"  {col_name}: {data_type}")
                
    except Exception as e:
        print(f"❌ Error testing comprehensive view: {e}")
        return False
    finally:
        conn.close()
    
    return True

def show_view_definitions():
    """Show the definitions of both views."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("📋 View Definitions:")
            print("=" * 50)
            
            # Show simple view definition
            cur.execute("""
                SELECT view_definition 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = 'user_garments_simple';
            """)
            
            result = cur.fetchone()
            if result:
                print("Simple View (user_garments_simple):")
                print("-" * 30)
                print(result[0][:500] + "..." if len(result[0]) > 500 else result[0])
                print()
            
            # Show comprehensive view definition
            cur.execute("""
                SELECT view_definition 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = 'user_garment_feedback_summary';
            """)
            
            result = cur.fetchone()
            if result:
                print("Comprehensive View (user_garment_feedback_summary):")
                print("-" * 40)
                print(result[0][:500] + "..." if len(result[0]) > 500 else result[0])
                
    except Exception as e:
        print(f"❌ Error showing view definitions: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🧪 Testing User Garment Views")
    print("=" * 50)
    
    # Test both views
    test_simple_view()
    print("\n" + "="*50 + "\n")
    test_comprehensive_view()
    print("\n" + "="*50 + "\n")
    show_view_definitions() 