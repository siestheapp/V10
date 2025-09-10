#!/usr/bin/env python3
"""
Test database connection and create test user Frank
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration from app.py
DB_CONFIG = {
    "database": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres.lbilxlkchzpducggkrxx"),
    "password": os.getenv("DB_PASSWORD", "efvTower12"),
    "host": os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com"),
    "port": os.getenv("DB_PORT", "6543")
}

def test_connection():
    print("🔌 Testing database connection...")
    print(f"Host: {DB_CONFIG['host']}")
    print(f"Port: {DB_CONFIG['port']}")
    print(f"Database: {DB_CONFIG['database']}")
    print(f"User: {DB_CONFIG['user']}")
    print("-" * 50)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✅ Database connection successful!")
        
        # First, check what columns exist in users table
        cur.execute("""
            SELECT column_name, data_type, is_nullable 
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position;
        """)
        schema = cur.fetchall()
        
        print(f"\n📋 Users table schema:")
        for col in schema:
            print(f"   {col['column_name']}: {col['data_type']} ({'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'})")
        
        # Get column names for dynamic query
        column_names = [col['column_name'] for col in schema]
        print(f"\n📊 Available columns: {', '.join(column_names)}")
        
        # Check current users with available columns
        if 'id' in column_names:
            cur.execute(f"SELECT * FROM users LIMIT 3;")
            users = cur.fetchall()
            
            print(f"\n📊 Current users in database:")
            for user in users:
                user_info = []
                for key, value in user.items():
                    user_info.append(f"{key}: {value}")
                print(f"   {', '.join(user_info)}")
        
        # Check if Frank already exists (using available columns)
        if 'email' in column_names:
            cur.execute("SELECT id FROM users WHERE email = 'frank@test.com';")
            frank_exists = cur.fetchone()
        else:
            frank_exists = None
        
        if frank_exists:
            print(f"\n👤 Frank already exists with ID: {frank_exists['id']}")
            frank_id = frank_exists['id']
        else:
            # Create Frank using available columns
            print(f"\n👤 Creating test user Frank...")
            
            # Build INSERT statement based on available columns
            insert_columns = []
            insert_values = []
            
            if 'email' in column_names:
                insert_columns.append('email')
                insert_values.append("'frank@test.com'")
            
            if 'gender' in column_names:
                insert_columns.append('gender')
                insert_values.append("'Male'")
            
            if 'height_in' in column_names:
                insert_columns.append('height_in')
                insert_values.append('72')
            
            if 'age' in column_names:
                insert_columns.append('age')
                insert_values.append('28')
            
            if 'preferred_units' in column_names:
                insert_columns.append('preferred_units')
                insert_values.append("'in'")
            
            if 'created_at' in column_names:
                insert_columns.append('created_at')
                insert_values.append('NOW()')
            
            if 'updated_at' in column_names:
                insert_columns.append('updated_at')
                insert_values.append('NOW()')
            
            if insert_columns:
                insert_sql = f"""
                    INSERT INTO users ({', '.join(insert_columns)})
                    VALUES ({', '.join(insert_values)})
                    RETURNING id;
                """
                cur.execute(insert_sql)
                frank_id = cur.fetchone()['id']
                conn.commit()
                print(f"✅ Frank created with ID: {frank_id}")
            else:
                print("❌ No suitable columns found to create Frank")
                frank_id = None
        
        cur.close()
        conn.close()
        
        return frank_id
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None

if __name__ == "__main__":
    frank_id = test_connection()
    if frank_id:
        print(f"\n🎉 Ready to test try-on flow with Frank (ID: {frank_id})")
    else:
        print(f"\n💥 Database connection failed - cannot proceed with try-on testing")
