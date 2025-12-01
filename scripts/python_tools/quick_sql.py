#!/usr/bin/env python3
"""
Quick SQL Query Tool - Run SQL queries on your database easily!
Usage: python quick_sql.py "SELECT * FROM brands"
"""

import sys
import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'fs_core_rw',
    'password': 'CHANGE_ME'
}

def run_sql(query):
    """Run a SQL query and display results nicely"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print(f"🔍 Running: {query}")
        print("-" * 60)
        
        cur.execute(query)
        results = cur.fetchall()
        
        if results:
            print(f"📊 Found {len(results)} results:")
            print()
            
            # Show results in a nice format
            for i, row in enumerate(results, 1):
                print(f"Result {i}:")
                for key, value in row.items():
                    print(f"   {key}: {value}")
                print()
                
                # Limit to 10 results to avoid overwhelming output
                if i >= 10:
                    remaining = len(results) - 10
                    print(f"... and {remaining} more results (use LIMIT in your query to see specific ones)")
                    break
        else:
            print("📋 No results found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print()
        print("💡 Common fixes:")
        print("   - Check table/column names are correct")
        print("   - Add semicolon at the end")
        print("   - Use single quotes for text: WHERE name = 'Lacoste'")
    finally:
        if 'conn' in locals():
            conn.close()

def show_examples():
    """Show common query examples"""
    print("📚 COMMON SQL QUERIES YOU CAN TRY:")
    print()
    
    examples = [
        ("Last database action", "SELECT action_type, target_table, created_at FROM user_actions ORDER BY created_at DESC LIMIT 1"),
        ("All your brands", "SELECT name FROM brands ORDER BY name"),
        ("Your garments", "SELECT b.name as brand, ug.product_name, ug.size_label FROM user_garments ug JOIN brands b ON ug.brand_id = b.id WHERE ug.user_id = 1"),
        ("Recent feedback", "SELECT b.name as brand, ugf.dimension, fc.feedback_text FROM user_garment_feedback ugf JOIN user_garments ug ON ugf.user_garment_id = ug.id JOIN brands b ON ug.brand_id = b.id JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id ORDER BY ugf.created_at DESC LIMIT 5"),
        ("Count actions by type", "SELECT action_type, COUNT(*) FROM user_actions GROUP BY action_type ORDER BY COUNT(*) DESC"),
        ("Size L garments", "SELECT b.name, ug.product_name FROM user_garments ug JOIN brands b ON ug.brand_id = b.id WHERE ug.size_label = 'L'"),
    ]
    
    for i, (description, query) in enumerate(examples, 1):
        print(f"{i}. {description}:")
        print(f"   {query}")
        print()

def main():
    if len(sys.argv) < 2:
        print("🎯 QUICK SQL QUERY TOOL")
        print("=" * 40)
        print()
        print("Usage:")
        print('   python quick_sql.py "SELECT * FROM brands"')
        print('   python quick_sql.py "SELECT * FROM user_actions ORDER BY created_at DESC LIMIT 1"')
        print()
        show_examples()
        return
    
    query = sys.argv[1]
    
    # Add semicolon if missing
    if not query.strip().endswith(';'):
        query += ';'
    
    run_sql(query)

if __name__ == "__main__":
    main()
