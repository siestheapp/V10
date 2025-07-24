#!/usr/bin/env python3
"""
Database Audit Log Setup for tailor3
Tracks ALL row changes (INSERT/UPDATE/DELETE) across all tables
"""

import psycopg2
from psycopg2.extras import RealDictCursor

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "postgres.lbilxlkchzpducggkrxx",
    "password": "efvTower12",
    "host": "aws-0-us-east-2.pooler.supabase.com",
    "port": "6543"
}

def create_audit_system():
    """Create comprehensive audit logging system"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("🔧 Creating audit log system...")
        
        # 1. Create audit log table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                table_name TEXT NOT NULL,
                operation TEXT NOT NULL, -- INSERT, UPDATE, DELETE
                row_id INTEGER, -- Primary key of affected row
                old_data JSONB, -- Previous values (for UPDATE/DELETE)
                new_data JSONB, -- New values (for INSERT/UPDATE)
                changed_by TEXT DEFAULT current_user,
                changed_at TIMESTAMPTZ DEFAULT NOW(),
                session_info JSONB -- Additional context
            );
        """)
        print("✅ Created audit_log table")
        
        # 2. Create audit function
        cursor.execute("""
            CREATE OR REPLACE FUNCTION audit_trigger_function()
            RETURNS TRIGGER AS $$
            DECLARE
                row_id_value INTEGER;
                old_data_json JSONB;
                new_data_json JSONB;
            BEGIN
                -- Get the primary key value (assumes 'id' column)
                IF TG_OP = 'DELETE' THEN
                    row_id_value := OLD.id;
                    old_data_json := row_to_json(OLD)::JSONB;
                    new_data_json := NULL;
                ELSIF TG_OP = 'UPDATE' THEN
                    row_id_value := NEW.id;
                    old_data_json := row_to_json(OLD)::JSONB;
                    new_data_json := row_to_json(NEW)::JSONB;
                ELSIF TG_OP = 'INSERT' THEN
                    row_id_value := NEW.id;
                    old_data_json := NULL;
                    new_data_json := row_to_json(NEW)::JSONB;
                END IF;
                
                -- Insert audit record
                INSERT INTO audit_log (
                    table_name,
                    operation,
                    row_id,
                    old_data,
                    new_data,
                    session_info
                ) VALUES (
                    TG_TABLE_NAME,
                    TG_OP,
                    row_id_value,
                    old_data_json,
                    new_data_json,
                    jsonb_build_object(
                        'application_name', current_setting('application_name', true),
                        'client_addr', inet_client_addr(),
                        'transaction_id', txid_current()
                    )
                );
                
                -- Return appropriate row
                IF TG_OP = 'DELETE' THEN
                    RETURN OLD;
                ELSE
                    RETURN NEW;
                END IF;
            END;
            $$ LANGUAGE plpgsql;
        """)
        print("✅ Created audit trigger function")
        
        # 3. Get all tables to audit (exclude system tables and audit_log itself)
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            AND table_name NOT IN ('audit_log', 'schema_migrations')
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        # 4. Create triggers for each table
        for (table_name,) in tables:
            trigger_name = f"audit_trigger_{table_name}"
            
            # Drop existing trigger if it exists
            cursor.execute(f"""
                DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};
            """)
            
            # Create new trigger
            cursor.execute(f"""
                CREATE TRIGGER {trigger_name}
                AFTER INSERT OR UPDATE OR DELETE ON {table_name}
                FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();
            """)
            print(f"✅ Created audit trigger for {table_name}")
        
        # 5. Create indexes for performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_log_table_name ON audit_log(table_name);
            CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at ON audit_log(changed_at DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_log_operation ON audit_log(operation);
            CREATE INDEX IF NOT EXISTS idx_audit_log_row_id ON audit_log(table_name, row_id);
        """)
        print("✅ Created performance indexes")
        
        # 6. Create view for easy querying
        cursor.execute("""
            CREATE OR REPLACE VIEW audit_log_summary AS
            SELECT 
                table_name,
                operation,
                COUNT(*) as change_count,
                MIN(changed_at) as first_change,
                MAX(changed_at) as last_change
            FROM audit_log
            GROUP BY table_name, operation
            ORDER BY last_change DESC;
        """)
        print("✅ Created audit_log_summary view")
        
        conn.commit()
        print("\n🎉 Audit log system created successfully!")
        print("\n📊 Now tracking ALL row changes across these tables:")
        for (table_name,) in tables:
            print(f"   - {table_name}")
            
    except Exception as e:
        conn.rollback()
        print(f"❌ Error creating audit system: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

def test_audit_system():
    """Test the audit system by making a sample change"""
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    
    try:
        print("\n🧪 Testing audit system...")
        
        # Make a test change (update a user record)
        cursor.execute("""
            UPDATE users SET email = email WHERE id = 1;
        """)
        
        # Check if it was logged
        cursor.execute("""
            SELECT table_name, operation, changed_at 
            FROM audit_log 
            WHERE table_name = 'users' 
            ORDER BY changed_at DESC 
            LIMIT 1;
        """)
        
        result = cursor.fetchone()
        if result:
            print(f"✅ Test successful! Logged: {result[0]} {result[1]} at {result[2]}")
        else:
            print("❌ Test failed - no audit record found")
            
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Test error: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    create_audit_system()
    test_audit_system() 