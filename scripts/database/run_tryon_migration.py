#!/usr/bin/env python3
"""
Run the try-on session tables migration
"""

import psycopg2
from psycopg2 import sql
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db_config import DB_CONFIG

def get_db_connection():
    """Create a database connection using the config"""
    return psycopg2.connect(**DB_CONFIG)

def run_migration():
    conn = None
    cur = None
    try:
        print("Connecting to database...")
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Create try_on_sessions table
        print("Creating try_on_sessions table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS try_on_sessions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                store_location VARCHAR(255),
                store_brand VARCHAR(100),
                session_date TIMESTAMP DEFAULT NOW(),
                status VARCHAR(50) DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        print("✅ Created try_on_sessions table")
        
        # Create try_on_items table
        print("Creating try_on_items table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS try_on_items (
                id SERIAL PRIMARY KEY,
                session_id INTEGER REFERENCES try_on_sessions(id) ON DELETE CASCADE,
                garment_id INTEGER REFERENCES garments(id),
                size_tried VARCHAR(10) NOT NULL,
                try_order INTEGER DEFAULT 1,
                final_decision VARCHAR(50),
                purchase_size VARCHAR(10),
                fit_score DECIMAL(3,2),
                would_recommend BOOLEAN,
                notes TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
        print("✅ Created try_on_items table")
        
        # Create dimension_feedback_sequence table
        print("Creating dimension_feedback_sequence table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dimension_feedback_sequence (
                id SERIAL PRIMARY KEY,
                try_on_item_id INTEGER REFERENCES try_on_items(id) ON DELETE CASCADE,
                dimension VARCHAR(50) NOT NULL,
                feedback_value INTEGER CHECK (feedback_value BETWEEN 1 AND 5),
                feedback_text VARCHAR(255),
                answered_at TIMESTAMP DEFAULT NOW(),
                sequence_order INTEGER,
                skipped BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        print("✅ Created dimension_feedback_sequence table")
        
        # Add garment_status column to user_garments
        print("Adding garment_status column to user_garments...")
        cur.execute("""
            ALTER TABLE user_garments 
            ADD COLUMN IF NOT EXISTS garment_status VARCHAR(50) DEFAULT 'owned'
        """)
        conn.commit()
        print("✅ Added garment_status column")
        
        # Update existing records
        print("Updating existing records...")
        cur.execute("""
            UPDATE user_garments 
            SET garment_status = CASE 
                WHEN owns_garment = true THEN 'owned'
                WHEN owns_garment = false THEN 'tried_on'
                ELSE 'unknown'
            END
            WHERE garment_status IS NULL OR garment_status = 'owned'
        """)
        conn.commit()
        print(f"✅ Updated {cur.rowcount} existing records")
        
        # Create indexes
        print("Creating indexes...")
        indexes = [
            ("idx_try_on_sessions_user_id", "try_on_sessions(user_id)"),
            ("idx_try_on_sessions_status", "try_on_sessions(status)"),
            ("idx_try_on_items_session_id", "try_on_items(session_id)"),
            ("idx_try_on_items_garment_id", "try_on_items(garment_id)"),
            ("idx_dimension_feedback_item_id", "dimension_feedback_sequence(try_on_item_id)"),
            ("idx_user_garments_status", "user_garments(garment_status)")
        ]
        
        for idx_name, idx_def in indexes:
            cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {idx_def}")
        conn.commit()
        print("✅ Created indexes")
        
        # Create view
        print("Creating try_on_summary view...")
        cur.execute("""
            CREATE OR REPLACE VIEW try_on_summary AS
            SELECT 
                ts.id as session_id,
                ts.user_id,
                ts.store_location,
                ts.store_brand,
                ts.session_date,
                ts.status as session_status,
                toi.id as try_on_item_id,
                g.id as garment_id,
                b.name as brand,
                g.product_name,
                g.product_url,
                toi.size_tried,
                toi.try_order,
                toi.final_decision,
                toi.purchase_size,
                toi.fit_score,
                COUNT(dfs.id) as feedback_count,
                STRING_AGG(
                    CONCAT(dfs.dimension, ':', dfs.feedback_text), 
                    ', ' 
                    ORDER BY dfs.sequence_order
                ) as feedback_summary
            FROM try_on_sessions ts
            JOIN try_on_items toi ON ts.id = toi.session_id
            JOIN garments g ON toi.garment_id = g.id
            JOIN brands b ON g.brand_id = b.id
            LEFT JOIN dimension_feedback_sequence dfs ON toi.id = dfs.try_on_item_id
            GROUP BY 
                ts.id, ts.user_id, ts.store_location, ts.store_brand, 
                ts.session_date, ts.status, toi.id, g.id, b.name, 
                g.product_name, g.product_url, toi.size_tried, 
                toi.try_order, toi.final_decision, toi.purchase_size, 
                toi.fit_score
        """)
        conn.commit()
        print("✅ Created try_on_summary view")
        
        # Verify tables were created
        print("\nVerifying migration...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('try_on_sessions', 'try_on_items', 'dimension_feedback_sequence')
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print(f"✅ Found {len(tables)} new tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
