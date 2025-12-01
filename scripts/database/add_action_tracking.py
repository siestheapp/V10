#!/usr/bin/env python3
"""
Add User Action Tracking Tables to tailor3
Enables undo functionality and complete audit trail for user interactions
"""

import psycopg2
import psycopg2.extras
from datetime import datetime
import json

# Database configuration for remote Supabase tailor3
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw", 
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
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

def add_action_tracking_tables():
    """Add tables for tracking user actions and enabling undo functionality"""
    
    conn = connect_to_database()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating user action tracking tables...")
        
        # 1. User Sessions Table
        print("   Creating user_sessions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_id UUID DEFAULT gen_random_uuid(),
                device_type TEXT, -- 'iOS', 'Android', 'Web'
                app_version TEXT,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                action_count INTEGER DEFAULT 0,
                duration_seconds INTEGER,
                
                -- Add constraint for device types
                CHECK (device_type IN ('iOS', 'Android', 'Web', 'Unknown'))
            );
        """)
        
        # 2. User Actions Table (with undo support)
        print("   Creating user_actions table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_actions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                session_id UUID,
                action_type TEXT NOT NULL,
                target_table TEXT, -- 'user_garment_feedback', 'user_garments', etc.
                target_id INTEGER, -- record ID that was changed
                previous_values JSONB, -- what it was before (for undo)
                new_values JSONB, -- what it became
                metadata JSONB, -- extra context (screen, duration, etc.)
                is_undone BOOLEAN DEFAULT FALSE,
                undone_at TIMESTAMP,
                undone_by_action_id INTEGER REFERENCES user_actions(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Constraint for valid action types
                CHECK (action_type IN (
                    'submit_feedback', 'update_feedback', 'delete_feedback',
                    'add_garment', 'update_garment', 'delete_garment',
                    'view_garment', 'view_closet', 'app_open', 'app_close',
                    'scan_item', 'view_product', 'search', 'filter',
                    'undo_action'
                ))
            );
        """)
        
        # 3. Performance Indexes
        print("   Creating performance indexes...")
        cursor.execute("""
            -- Index for finding user's recent actions
            CREATE INDEX IF NOT EXISTS idx_user_actions_user_created 
            ON user_actions(user_id, created_at DESC);
            
            -- Index for finding actions on specific records
            CREATE INDEX IF NOT EXISTS idx_user_actions_target 
            ON user_actions(target_table, target_id);
            
            -- Index for finding non-undone actions
            CREATE INDEX IF NOT EXISTS idx_user_actions_undone 
            ON user_actions(is_undone) WHERE is_undone = FALSE;
            
            -- Index for session lookups
            CREATE INDEX IF NOT EXISTS idx_user_sessions_user_started
            ON user_sessions(user_id, started_at DESC);
        """)
        
        # 4. Create a view for easy action history lookup
        print("   Creating action history view...")
        cursor.execute("""
            CREATE OR REPLACE VIEW user_action_history AS
            SELECT 
                ua.id,
                ua.user_id,
                u.email as user_email,
                ua.session_id,
                ua.action_type,
                ua.target_table,
                ua.target_id,
                ua.previous_values,
                ua.new_values,
                ua.metadata,
                ua.is_undone,
                ua.undone_at,
                ua.created_at,
                -- Add human-readable description
                CASE 
                    WHEN ua.action_type = 'update_feedback' THEN 
                        'Updated feedback for garment #' || ua.target_id
                    WHEN ua.action_type = 'add_garment' THEN 
                        'Added new garment #' || ua.target_id
                    WHEN ua.action_type = 'view_garment' THEN 
                        'Viewed garment #' || ua.target_id
                    ELSE ua.action_type
                END as description
            FROM user_actions ua
            JOIN users u ON ua.user_id = u.id
            ORDER BY ua.created_at DESC;
        """)
        
        conn.commit()
        print("✅ Successfully created action tracking tables and indexes")
        
        # Show what was created
        cursor.execute("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name IN ('user_sessions', 'user_actions')
            ORDER BY table_name, ordinal_position;
        """)
        
        print("\n📋 Created tables and columns:")
        current_table = None
        for row in cursor.fetchall():
            table_name, column_name, data_type, is_nullable = row
            if table_name != current_table:
                print(f"\n  📄 {table_name}:")
                current_table = table_name
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"    • {column_name} ({data_type}) {nullable}")
        
        # Show indexes
        cursor.execute("""
            SELECT indexname, tablename 
            FROM pg_indexes 
            WHERE tablename IN ('user_sessions', 'user_actions')
            AND schemaname = 'public'
            ORDER BY tablename, indexname;
        """)
        
        print(f"\n🔍 Created indexes:")
        for row in cursor.fetchall():
            print(f"    • {row[1]}.{row[0]}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def test_action_tracking():
    """Test the action tracking system with sample data"""
    conn = connect_to_database()
    if not conn:
        return False
        
    cursor = conn.cursor()
    
    try:
        print("\n🧪 Testing action tracking system...")
        
        # Create a test session
        cursor.execute("""
            INSERT INTO user_sessions (user_id, device_type, app_version)
            VALUES (1, 'iOS', '1.0.0')
            RETURNING session_id;
        """)
        session_id = cursor.fetchone()[0]
        print(f"   Created test session: {session_id}")
        
        # Create a test action
        cursor.execute("""
            INSERT INTO user_actions (
                user_id, session_id, action_type, target_table, target_id,
                previous_values, new_values, metadata
            ) VALUES (
                1, %s, 'update_feedback', 'user_garment_feedback', 4,
                %s, %s, %s
            ) RETURNING id;
        """, (
            session_id,
            json.dumps({"chest": "Good Fit", "overall": "Good Fit"}),
            json.dumps({"chest": "Too Tight", "overall": "Too Tight"}),
            json.dumps({"screen": "garment_detail", "dimensions_changed": ["chest", "overall"]})
        ))
        action_id = cursor.fetchone()[0]
        print(f"   Created test action: {action_id}")
        
        # Query the action history view
        cursor.execute("""
            SELECT description, created_at, is_undone
            FROM user_action_history 
            WHERE id = %s;
        """, (action_id,))
        
        result = cursor.fetchone()
        print(f"   Action description: {result[0]}")
        print(f"   Created at: {result[1]}")
        print(f"   Is undone: {result[2]}")
        
        conn.commit()
        print("✅ Action tracking system test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing action tracking: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("🚀 Adding User Action Tracking to tailor3 Database")
    print("=" * 50)
    
    success = add_action_tracking_tables()
    if success:
        test_action_tracking()
        print("\n🎉 Action tracking system is ready!")
        print("\nNext steps:")
        print("1. Update your backend to use these tables")
        print("2. Add undo endpoints to your API")
        print("3. Update iOS app to track actions")
    else:
        print("\n❌ Failed to set up action tracking system") 