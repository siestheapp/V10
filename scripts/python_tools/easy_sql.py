#!/usr/bin/env python3
"""
Easy SQL - Shortcuts for common queries!
No more typing massive SQL statements!
"""

import sys
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12'
}

def run_query(query, description):
    """Run a query and show results"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"🔍 {description}")
        print("-" * 40)
        
        cur.execute(query)
        results = cur.fetchall()
        
        if results:
            # Show results
            display_limit = 10
            for i, row in enumerate(results, 1):
                print(f"{i}. {dict(row)}")
                if i >= display_limit:
                    break
            
            # Show summary
            total = len(results)
            if total > display_limit:
                print(f"... and {total - display_limit} more results")
                print(f"\nShowing {display_limit} of {total} total results")
            else:
                print(f"\nTotal: {total} results")
        else:
            print("No results found")
        print()
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def main():
    if len(sys.argv) < 2:
        print("🚀 EASY SQL - No More Typing Giant Queries!")
        print("=" * 50)
        print()
        print("Usage: python easy_sql.py <shortcut>")
        print()
        print("📝 SHORTCUTS:")
        print("   last        - Last database action")
        print("   brands      - All brands")
        print("   garments    - Your garments") 
        print("   feedback    - Recent feedback")
        print("   actions     - Count actions by type")
        print("   lacoste     - Everything about Lacoste")
        print("   sizes       - All size L garments")
        print()
        print("Examples:")
        print("   python easy_sql.py last")
        print("   python easy_sql.py feedback")
        print("   python easy_sql.py lacoste")
        return
    
    shortcut = sys.argv[1].lower()
    
    # Define shortcuts for common queries
    shortcuts = {
        'last': (
            "SELECT action_type, target_table, created_at FROM user_actions ORDER BY created_at DESC LIMIT 1",
            "Last database action"
        ),
        'brands': (
            "SELECT name FROM brands ORDER BY name",
            "All brands in database"
        ),
        'garments': (
            """SELECT b.name as brand, ug.product_name, ug.size_label 
               FROM user_garments ug 
               JOIN brands b ON ug.brand_id = b.id 
               WHERE ug.user_id = 1""",
            "Your garments"
        ),
        'feedback': (
            """SELECT b.name as brand, ugf.dimension, fc.feedback_text, ugf.created_at
               FROM user_garment_feedback ugf
               JOIN user_garments ug ON ugf.user_garment_id = ug.id
               JOIN brands b ON ug.brand_id = b.id
               JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
               ORDER BY ugf.created_at DESC LIMIT 5""",
            "Recent feedback"
        ),
        'actions': (
            "SELECT action_type, COUNT(*) FROM user_actions GROUP BY action_type ORDER BY COUNT(*) DESC",
            "Count actions by type"
        ),
        'lacoste': (
            """SELECT ug.product_name, ug.size_label, ug.image_url, ug.product_url
               FROM user_garments ug 
               JOIN brands b ON ug.brand_id = b.id 
               WHERE b.name = 'Lacoste'""",
            "Everything about your Lacoste garments"
        ),
        'sizes': (
            """SELECT b.name, ug.product_name, ug.size_label
               FROM user_garments ug 
               JOIN brands b ON ug.brand_id = b.id 
               WHERE ug.size_label = 'L'""",
            "All size L garments"
        )
    }
    
    if shortcut in shortcuts:
        query, description = shortcuts[shortcut]
        run_query(query, description)
    else:
        print(f"❌ Unknown shortcut: {shortcut}")
        print("Run 'python easy_sql.py' to see available shortcuts")

if __name__ == "__main__":
    main()
