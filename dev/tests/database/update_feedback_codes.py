#!/usr/bin/env python3
"""
Update feedback codes for the new 5-point satisfaction scale system
"""

import psycopg2

# Database connection
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

def update_feedback_codes():
    """Update feedback codes for the new 5-point satisfaction system"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check existing feedback codes
    cursor.execute("SELECT id, feedback_text, feedback_type, is_positive FROM feedback_codes ORDER BY feedback_text")
    existing_codes = cursor.fetchall()
    print("Existing feedback codes:")
    for code_id, text, feedback_type, is_positive in existing_codes:
        status = "✅" if is_positive else "❌" if is_positive is False else "❓"
        print(f"  {status} {code_id}: {text} ({feedback_type})")
    
    # Define the new 5-point satisfaction scale codes
    new_codes = [
        ("Good Fit", "fit", True),
        ("Tight but I Like It", "fit", True),
        ("Loose but I Like It", "fit", True),
        ("Too Tight", "fit", False),
        ("Too Loose", "fit", False),
    ]
    
    print("\nUpdating feedback codes for 5-point satisfaction scale...")
    
    for feedback_text, feedback_type, is_positive in new_codes:
        # Check if code already exists
        existing_texts = [code[1] for code in existing_codes]
        if feedback_text not in existing_texts:
            try:
                cursor.execute("""
                    INSERT INTO feedback_codes (feedback_text, feedback_type, is_positive)
                    VALUES (%s, %s, %s)
                """, (feedback_text, feedback_type, is_positive))
                print(f"✅ Added: {feedback_text}")
            except Exception as e:
                print(f"❌ Error adding {feedback_text}: {e}")
        else:
            print(f"⏭️  Already exists: {feedback_text}")
    
    conn.commit()
    
    # Show final list
    cursor.execute("SELECT id, feedback_text, feedback_type, is_positive FROM feedback_codes ORDER BY feedback_text")
    all_codes = cursor.fetchall()
    
    print(f"\n🎉 Final feedback codes ({len(all_codes)} total):")
    for code_id, text, code_type, is_positive in all_codes:
        status = "✅" if is_positive else "❌" if is_positive is False else "❓"
        print(f"  {status} {code_id}: {text} ({code_type})")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    update_feedback_codes() 