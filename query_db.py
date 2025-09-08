#!/usr/bin/env python3
"""
Simple database query helper for V10 project
Usage: python query_db.py "SELECT * FROM users LIMIT 5;"
"""

import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from db_config import DB_CONFIG

def run_query(query):
    """Run a SQL query and return results"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute(query)
        results = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return results
        
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return None

def print_results(results):
    """Print query results in a nice format"""
    if not results:
        print("No results returned.")
        return
    
    if not results[0]:
        print("Query executed successfully (no data returned).")
        return
    
    # Print column headers
    columns = list(results[0].keys())
    print(" | ".join(columns))
    print("-" * (len(" | ".join(columns))))
    
    # Print rows
    for row in results:
        values = [str(row[col]) if row[col] is not None else "NULL" for col in columns]
        print(" | ".join(values))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python query_db.py \"YOUR_SQL_QUERY\"")
        print("Example: python query_db.py \"SELECT id, email FROM users LIMIT 3;\"")
        sys.exit(1)
    
    query = sys.argv[1]
    print(f"🔍 Running query: {query}")
    print("-" * 50)
    
    results = run_query(query)
    if results is not None:
        print_results(results)
