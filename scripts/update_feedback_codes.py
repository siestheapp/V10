#!/usr/bin/env python3
"""
Add missing feedback codes for progressive feedback system
"""

import psycopg2

# Database connection
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def add_feedback_codes():
    """Add missing feedback codes for the 5-point progressive system"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    # Check existing feedback codes
    cursor.execute("SELECT feedback_text FROM feedback_codes ORDER BY feedback_text")
    existing_codes = [row[0] for row in cursor.fetchall()]
    print("Existing feedback codes:")
    for code in existing_codes:
        print(f"  - {code}")
    
    # Define the feedback codes we need for the progressive system
    new_codes = [
        ("Perfect", "fit", True),
        ("Slightly Tight", "fit", False),
        ("Slightly Loose", "fit", False),
        ("Too Loose", "fit", False),
        ("N/A", "other", None),
        ("Perfect Length", "length", True),
        ("Too Long", "length", False),
        ("Too Short", "length", False),
    ]
    
    print("\nAdding missing feedback codes...")
    
    for feedback_text, feedback_type, is_positive in new_codes:
        # Check if code already exists
        if feedback_text not in existing_codes:
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
    add_feedback_codes() 