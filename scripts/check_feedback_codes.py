#!/usr/bin/env python3
"""
Check what feedback codes exist in the database.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from connect_remote_db import connect_to_database

def check_feedback_codes():
    """Check what feedback codes exist in the database."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("🔍 Checking Feedback Codes in Database")
            print("=" * 50)
            
            # Check feedback_codes table
            cur.execute("SELECT COUNT(*) FROM feedback_codes;")
            count = cur.fetchone()[0]
            print(f"Total feedback codes: {count}")
            
            if count > 0:
                cur.execute("""
                    SELECT id, feedback_text, feedback_type, is_positive
                    FROM feedback_codes
                    ORDER BY feedback_type, feedback_text;
                """)
                
                rows = cur.fetchall()
                print("\nFeedback Codes:")
                print("-" * 30)
                for row in rows:
                    code_id, text, ftype, is_pos = row
                    sentiment = "✅ Positive" if is_pos else "❌ Negative"
                    print(f"  {code_id}: '{text}' ({ftype}) - {sentiment}")
            
            # Check user_garment_feedback table
            cur.execute("SELECT COUNT(*) FROM user_garment_feedback;")
            feedback_count = cur.fetchone()[0]
            print(f"\nTotal user garment feedback records: {feedback_count}")
            
            if feedback_count > 0:
                cur.execute("""
                    SELECT ugf.dimension, fc.feedback_text, fc.feedback_type, fc.is_positive
                    FROM user_garment_feedback ugf
                    JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
                    ORDER BY ugf.dimension, fc.feedback_text;
                """)
                
                rows = cur.fetchall()
                print("\nActual Feedback Used:")
                print("-" * 30)
                for row in rows:
                    dimension, text, ftype, is_pos = row
                    sentiment = "✅ Positive" if is_pos else "❌ Negative"
                    print(f"  {dimension}: '{text}' ({ftype}) - {sentiment}")
            
            # Check dimensions used
            cur.execute("""
                SELECT DISTINCT dimension 
                FROM user_garment_feedback 
                ORDER BY dimension;
            """)
            
            dimensions = cur.fetchall()
            print(f"\nDimensions used in feedback:")
            print("-" * 30)
            for dim in dimensions:
                print(f"  - {dim[0]}")
                
    except Exception as e:
        print(f"❌ Error checking feedback codes: {e}")
        return False
    finally:
        conn.close()
    
    return True

def check_user_garments_feedback():
    """Check what feedback exists in user_garments table."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            print("\n🔍 Checking User Garments Feedback")
            print("=" * 50)
            
            # Check user_garments with feedback
            cur.execute("""
                SELECT id, product_name, fit_feedback, feedback_timestamp
                FROM user_garments
                WHERE fit_feedback IS NOT NULL
                ORDER BY feedback_timestamp DESC;
            """)
            
            rows = cur.fetchall()
            print(f"User garments with general feedback: {len(rows)}")
            
            if rows:
                print("\nGeneral Feedback in user_garments:")
                print("-" * 40)
                for row in rows:
                    garment_id, product, feedback, timestamp = row
                    print(f"  Garment {garment_id} ({product}): '{feedback}' at {timestamp}")
                    
    except Exception as e:
        print(f"❌ Error checking user garments feedback: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    check_feedback_codes()
    check_user_garments_feedback() 