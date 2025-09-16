#!/usr/bin/env python3
"""
Create Try-On Photos Table
Stores photos taken during the try-on process for user garments.
"""

import sys
import os
import asyncio
import asyncpg
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db_config import DB_CONFIG

async def create_tryon_photos_table():
    """Create table for storing try-on photos."""
    
    # Get database configuration
    config = DB_CONFIG
    
    # Connect to database
    conn = await asyncpg.connect(**config)
    
    try:
        # Create the user_garment_photos table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_garment_photos (
            id SERIAL PRIMARY KEY,
            user_garment_id INTEGER NOT NULL REFERENCES user_garments(id) ON DELETE CASCADE,
            photo_url TEXT NOT NULL,
            photo_type TEXT CHECK (photo_type IN ('camera', 'gallery', 'tag')) DEFAULT 'camera',
            caption TEXT,
            metadata JSONB,  -- Store additional info like angle, lighting, etc.
            is_primary BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        await conn.execute(create_table_sql)
        print("✅ Created user_garment_photos table")
        
        # Create indexes for better performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_user_garment_photos_garment ON user_garment_photos(user_garment_id);",
            "CREATE INDEX IF NOT EXISTS idx_user_garment_photos_primary ON user_garment_photos(user_garment_id, is_primary) WHERE is_primary = TRUE;",
            "CREATE INDEX IF NOT EXISTS idx_user_garment_photos_created ON user_garment_photos(created_at DESC);"
        ]
        
        for index_sql in indexes:
            await conn.execute(index_sql)
            print(f"✅ Created index: {index_sql.split('INDEX IF NOT EXISTS ')[1].split(' ')[0]}")
        
        # Add comment to table
        comment_sql = """
        COMMENT ON TABLE user_garment_photos IS 
        'Stores photos taken during try-on sessions. Each user_garment can have multiple photos.';
        """
        await conn.execute(comment_sql)
        
        # Add column comments
        column_comments = {
            'photo_type': 'Source of the photo: camera (taken in-app), gallery (selected from gallery), tag (product tag photo)',
            'metadata': 'JSON data for photo context: angle (front/side/back), lighting conditions, notes, etc.',
            'is_primary': 'Whether this is the primary/featured photo for this garment'
        }
        
        for column, comment in column_comments.items():
            await conn.execute(f"COMMENT ON COLUMN user_garment_photos.{column} IS '{comment}';")
        
        print("✅ Added table and column comments")
        
        # Verify table structure
        verify_sql = """
        SELECT 
            column_name, 
            data_type, 
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'user_garment_photos'
        ORDER BY ordinal_position;
        """
        
        columns = await conn.fetch(verify_sql)
        print("\n📋 Table structure:")
        for col in columns:
            print(f"  - {col['column_name']}: {col['data_type']} (nullable: {col['is_nullable']}, default: {col['column_default']})")
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(create_tryon_photos_table())
