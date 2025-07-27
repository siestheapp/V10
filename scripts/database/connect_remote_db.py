#!/usr/bin/env python3
"""
Remote Supabase Database Connection Script
Connects to the tailor3 database on Supabase for creating views and database operations.
"""

import psycopg2
import psycopg2.extras
from psycopg2 import sql
import sys
import os

# Database configuration for remote Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx", 
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def connect_to_database():
    """Connect to the remote Supabase database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Successfully connected to remote Supabase database (tailor3)")
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def test_connection():
    """Test the database connection and show basic info."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Test basic query
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"📊 Database version: {version[0]}")
            
            # Show current database
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()
            print(f"🗄️  Current database: {db_name[0]}")
            
            # Show tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cur.fetchall()
            print(f"📋 Available tables ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
            
            # Show existing views
            cur.execute("""
                SELECT table_name 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            views = cur.fetchall()
            print(f"👁️  Existing views ({len(views)}):")
            for view in views:
                print(f"  - {view[0]}")
                
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False
    finally:
        conn.close()
    
    return True

def create_view(view_name, view_sql):
    """Create a new view in the database."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            # Create the view
            cur.execute(sql.SQL("CREATE OR REPLACE VIEW {} AS {}").format(
                sql.Identifier(view_name),
                sql.SQL(view_sql)
            ))
            conn.commit()
            print(f"✅ Successfully created/updated view: {view_name}")
            return True
            
    except Exception as e:
        print(f"❌ Error creating view: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def drop_view(view_name):
    """Drop a view from the database."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql.SQL("DROP VIEW IF EXISTS {} CASCADE").format(
                sql.Identifier(view_name)
            ))
            conn.commit()
            print(f"✅ Successfully dropped view: {view_name}")
            return True
            
    except Exception as e:
        print(f"❌ Error dropping view: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def show_view_definition(view_name):
    """Show the definition of an existing view."""
    conn = connect_to_database()
    if not conn:
        return False
    
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT view_definition 
                FROM information_schema.views 
                WHERE table_schema = 'public' 
                AND table_name = %s;
            """, (view_name,))
            
            result = cur.fetchone()
            if result:
                print(f"📋 View definition for '{view_name}':")
                print(result[0])
            else:
                print(f"❌ View '{view_name}' not found")
                
    except Exception as e:
        print(f"❌ Error showing view definition: {e}")
        return False
    finally:
        conn.close()
    
    return True

if __name__ == "__main__":
    print("🔗 Remote Supabase Database Connection Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            test_connection()
        elif command == "show" and len(sys.argv) > 2:
            show_view_definition(sys.argv[2])
        elif command == "drop" and len(sys.argv) > 2:
            drop_view(sys.argv[2])
        else:
            print("Usage:")
            print("  python connect_remote_db.py test                    # Test connection")
            print("  python connect_remote_db.py show <view_name>       # Show view definition")
            print("  python connect_remote_db.py drop <view_name>       # Drop a view")
    else:
        # Default: test connection
        test_connection() 