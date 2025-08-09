#!/usr/bin/env python3
"""
SQL Tutorial for Sean - Learn SQL with your own database!
"""

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12'
}

def run_query(sql, description):
    """Helper function to run a query and show results"""
    print(f"\n🎯 {description}")
    print(f"SQL: {sql}")
    print("-" * 50)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute(sql)
        results = cur.fetchall()
        
        if results:
            print(f"📊 Found {len(results)} results:")
            for i, row in enumerate(results[:5], 1):  # Show first 5 results
                print(f"   {i}. {dict(row)}")
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more")
        else:
            print("📋 No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

def sql_tutorial():
    print("📚 SQL TUTORIAL - Learn with Your Own Data!")
    print("=" * 60)
    
    print("\n🌟 SQL BASICS:")
    print("   SELECT = what columns you want")
    print("   FROM = which table to look in") 
    print("   WHERE = filter conditions")
    print("   ORDER BY = sort the results")
    print("   LIMIT = how many results to show")
    
    # Lesson 1: Basic SELECT
    run_query(
        "SELECT action_type, created_at FROM user_actions LIMIT 3",
        "LESSON 1: Basic SELECT - Get specific columns"
    )
    
    # Lesson 2: ORDER BY
    run_query(
        "SELECT action_type, created_at FROM user_actions ORDER BY created_at DESC LIMIT 3",
        "LESSON 2: ORDER BY - Sort by newest first (DESC = descending)"
    )
    
    # Lesson 3: WHERE clause
    run_query(
        "SELECT * FROM user_actions WHERE action_type = 'update_feedback'",
        "LESSON 3: WHERE - Filter for specific action types"
    )
    
    # Lesson 4: COUNT
    run_query(
        "SELECT COUNT(*) as total_actions FROM user_actions",
        "LESSON 4: COUNT - How many total actions?"
    )
    
    # Lesson 5: GROUP BY
    run_query(
        "SELECT action_type, COUNT(*) as count FROM user_actions GROUP BY action_type ORDER BY count DESC",
        "LESSON 5: GROUP BY - Count actions by type"
    )
    
    # Lesson 6: JOIN (combining tables)
    run_query(
        """SELECT 
            b.name as brand, 
            ug.product_name, 
            ug.size_label
        FROM user_garments ug 
        JOIN brands b ON ug.brand_id = b.id 
        LIMIT 5""",
        "LESSON 6: JOIN - Combine garments with brand names"
    )
    
    # Lesson 7: Recent feedback
    run_query(
        """SELECT 
            b.name as brand,
            ugf.dimension,
            fc.feedback_text,
            ugf.created_at
        FROM user_garment_feedback ugf
        JOIN user_garments ug ON ugf.user_garment_id = ug.id
        JOIN brands b ON ug.brand_id = b.id
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        ORDER BY ugf.created_at DESC
        LIMIT 5""",
        "LESSON 7: Complex JOIN - Recent feedback with brand names"
    )
    
    print("\n🎓 COMMON QUERIES YOU CAN TRY:")
    print("   1. Last action: SELECT * FROM user_actions ORDER BY created_at DESC LIMIT 1")
    print("   2. All brands: SELECT name FROM brands ORDER BY name")
    print("   3. Your garments: SELECT * FROM user_garments WHERE user_id = 1")
    print("   4. Recent feedback: SELECT * FROM user_garment_feedback ORDER BY created_at DESC LIMIT 5")
    
    print("\n💡 SQL TIPS:")
    print("   - Always end queries with semicolon ;")
    print("   - Use LIMIT to avoid huge results")
    print("   - DESC = newest first, ASC = oldest first")
    print("   - Use COUNT(*) to count rows")
    print("   - JOIN connects related tables")

if __name__ == "__main__":
    sql_tutorial()
