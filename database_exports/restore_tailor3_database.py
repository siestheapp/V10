#!/usr/bin/env python3
"""
Restore script for tailor3 database tables
Restores all exported tables from SQL files to a PostgreSQL database
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys
from datetime import datetime
import glob

def get_db_connection(db_config):
    """Get a connection to the database"""
    try:
        return psycopg2.connect(**db_config)
    except Exception as e:
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def restore_from_sql_files(export_dir, db_config, drop_existing=False):
    """Restore all tables from SQL files"""
    
    # Find all SQL files (excluding metadata)
    sql_files = glob.glob(os.path.join(export_dir, "*.sql"))
    sql_files = [f for f in sql_files if not f.endswith('_metadata.sql')]
    
    if not sql_files:
        print(f"❌ No SQL files found in {export_dir}")
        return False
    
    print(f"🔍 Found {len(sql_files)} SQL files to restore")
    
    conn = get_db_connection(db_config)
    cur = conn.cursor()
    
    try:
        conn.autocommit = False  # Use transactions
        
        for sql_file in sorted(sql_files):
            table_name = os.path.basename(sql_file).replace('.sql', '')
            print(f"📊 Restoring table: {table_name}")
            
            try:
                with open(sql_file, 'r', encoding='utf-8') as f:
                    sql_content = f.read()
                
                # Execute the SQL file content
                cur.execute(sql_content)
                
                # Get row count
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cur.fetchone()[0]
                
                print(f"✅ Restored {table_name}: {row_count} rows")
                
            except Exception as e:
                print(f"❌ Error restoring {table_name}: {e}")
                conn.rollback()
                return False
        
        # Commit all changes
        conn.commit()
        print(f"🎉 Successfully restored all {len(sql_files)} tables!")
        return True
        
    except Exception as e:
        print(f"❌ Error during restoration: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

def main():
    """Main restoration function"""
    print("🚀 Starting tailor3 database restoration...")
    print(f"📅 Restore date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Configuration - MODIFY THESE FOR YOUR TARGET DATABASE
    TARGET_DB_CONFIG = {
        "database": "postgres",  # Change this to your target database name
        "user": "postgres.lbilxlkchzpducggkrxx",  # Change this to your username
        "password": "efvTower12",  # Change this to your password
        "host": "aws-0-us-east-2.pooler.supabase.com",  # Change this to your host
        "port": "6543"  # Change this to your port
    }
    
    # Find the most recent export directory
    export_dirs = glob.glob("tailor3_export_*")
    if not export_dirs:
        print("❌ No export directories found. Please run the export script first.")
        sys.exit(1)
    
    # Use the most recent export
    latest_export = sorted(export_dirs)[-1]
    print(f"📁 Using export directory: {latest_export}")
    
    # Test database connection
    try:
        conn = get_db_connection(TARGET_DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT version()")
        version = cur.fetchone()
        print(f"🔗 Connected to: {version[0]}")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"❌ Failed to connect to target database: {e}")
        sys.exit(1)
    
    # Perform restoration
    success = restore_from_sql_files(latest_export, TARGET_DB_CONFIG)
    
    if success:
        print("\n🎉 Database restoration completed successfully!")
        print(f"📊 All tables have been restored to: {TARGET_DB_CONFIG['database']}")
    else:
        print("\n❌ Database restoration failed. Check the errors above.")

if __name__ == "__main__":
    main()
