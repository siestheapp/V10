#!/usr/bin/env python3
"""
Insert Centimeter Measurements into garment_guide_entries
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('src/ios_app/Backend/.env')

def get_db_connection():
    """Get database connection using environment variables or defaults"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "aws-0-us-east-2.pooler.supabase.com"),
        port=os.getenv("DB_PORT", "6543"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "postgres.lbilxlkchzpducggkrxx"),
        password=os.getenv("DB_PASSWORD", "efvTower12"),
        cursor_factory=RealDictCursor
    )

def insert_cm_measurements():
    """Insert centimeter measurements into garment_guide_entries"""
    
    # First, let's check what garment_guide_id to use
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check existing garment guides
        cursor.execute("SELECT id, guide_header FROM garment_guides ORDER BY id DESC LIMIT 5")
        guides = cursor.fetchall()
        
        print("Existing garment guides:")
        for guide in guides:
            print(f"ID: {guide['id']}, Header: {guide['guide_header']}")
        
        # Use the most recent guide or create a new one
        if guides:
            garment_guide_id = guides[0]['id']
            print(f"\nUsing existing garment guide ID: {garment_guide_id}")
        else:
            # Create a new garment guide
            cursor.execute("""
                INSERT INTO garment_guides (brand_id, guide_header, info_source, source_url)
                VALUES (1, 'Shirt Garment Measurements - CM', 'product_measurement_table', 'https://example.com/size-guide')
                RETURNING id
            """)
            garment_guide_id = cursor.fetchone()['id']
            print(f"Created new garment guide ID: {garment_guide_id}")
        
        # Insert centimeter measurements
        cm_measurements = [
            # Size S measurements
            (garment_guide_id, 'S', 'g_chest_width', 50, 'cm', 'product_page'),
            (garment_guide_id, 'S', 'g_center_back_length', 67.5, 'cm', 'product_page'),
            (garment_guide_id, 'S', 'g_sleeve_length', 65, 'cm', 'product_page'),
            
            # Size M measurements  
            (garment_guide_id, 'M', 'g_chest_width', 52, 'cm', 'product_page'),
            (garment_guide_id, 'M', 'g_center_back_length', 68.5, 'cm', 'product_page'),
            (garment_guide_id, 'M', 'g_sleeve_length', 66, 'cm', 'product_page'),
            
            # Size L measurements
            (garment_guide_id, 'L', 'g_chest_width', 54, 'cm', 'product_page'),
            (garment_guide_id, 'L', 'g_center_back_length', 69.5, 'cm', 'product_page'),
            (garment_guide_id, 'L', 'g_sleeve_length', 67, 'cm', 'product_page'),
            
            # Size XL measurements
            (garment_guide_id, 'XL', 'g_chest_width', 56, 'cm', 'product_page'),
            (garment_guide_id, 'XL', 'g_center_back_length', 70.5, 'cm', 'product_page'),
            (garment_guide_id, 'XL', 'g_sleeve_length', 68, 'cm', 'product_page'),
            
            # Size XXL measurements
            (garment_guide_id, 'XXL', 'g_chest_width', 59, 'cm', 'product_page'),
            (garment_guide_id, 'XXL', 'g_center_back_length', 71.5, 'cm', 'product_page'),
            (garment_guide_id, 'XXL', 'g_sleeve_length', 69, 'cm', 'product_page')
        ]
        
        # Insert the measurements
        cursor.executemany("""
            INSERT INTO garment_guide_entries 
            (garment_guide_id, size_label, measurement_type, measurement_value, unit, measurement_source)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, cm_measurements)
        
        conn.commit()
        print(f"✅ Successfully inserted {len(cm_measurements)} centimeter measurements!")
        
        # Verify the insertions
        cursor.execute("""
            SELECT size_label, measurement_type, measurement_value, unit, measurement_source
            FROM garment_guide_entries
            WHERE garment_guide_id = %s AND unit = 'cm'
            ORDER BY size_label, measurement_type
        """, (garment_guide_id,))
        
        results = cursor.fetchall()
        print(f"\nInserted measurements:")
        for row in results:
            print(f"  {row['size_label']} - {row['measurement_type']}: {row['measurement_value']} {row['unit']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    print("Inserting centimeter measurements into garment_guide_entries...")
    insert_cm_measurements()
