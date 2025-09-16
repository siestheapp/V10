#!/usr/bin/env python3
"""
Add smart data columns to product_master table
These columns capture HIGH-VALUE data for AI insights
"""

import psycopg2
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from db_config import DB_CONFIG

def add_smart_columns():
    """Add columns for smart data capture"""
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print("🔧 ADDING SMART DATA COLUMNS")
    print("=" * 60)
    
    try:
        # Add product ratings column (HIGH VALUE: satisfaction indicator)
        cur.execute("""
            ALTER TABLE product_master
            ADD COLUMN IF NOT EXISTS product_ratings JSONB DEFAULT '{}';
        """)
        print("✅ Added product_ratings column (avg rating, review count, quality)")
        
        # Add fit feedback column (HIGH VALUE: size prediction)
        cur.execute("""
            ALTER TABLE product_master
            ADD COLUMN IF NOT EXISTS fit_feedback JSONB DEFAULT '{}';
        """)
        print("✅ Added fit_feedback column (true to size, runs small/large)")
        
        # Add pricing data column (HIGH VALUE: value perception)
        cur.execute("""
            ALTER TABLE product_master
            ADD COLUMN IF NOT EXISTS pricing_data JSONB DEFAULT '{}';
        """)
        print("✅ Added pricing_data column (original, sale, discount %)")
        
        # Add fabric technology column (HIGH VALUE: performance features)
        cur.execute("""
            ALTER TABLE product_master
            ADD COLUMN IF NOT EXISTS fabric_technology TEXT[] DEFAULT '{}';
        """)
        print("✅ Added fabric_technology column (moisture-wicking, stretch, etc)")
        
        # Update fit_information to be JSONB if it's not already
        cur.execute("""
            ALTER TABLE product_master
            ALTER COLUMN fit_information TYPE JSONB USING fit_information::jsonb;
        """)
        print("✅ Ensured fit_information is JSONB type")
        
        # Add category_id if missing
        cur.execute("""
            ALTER TABLE product_master
            ADD COLUMN IF NOT EXISTS category_id INTEGER;
        """)
        print("✅ Added category_id column")
        
        # Create index for faster queries on ratings
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_ratings 
            ON product_master((product_ratings->>'average_rating'));
        """)
        print("✅ Created index on average ratings for fast sorting")
        
        # Create index for fit consensus
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_fit_consensus 
            ON product_master((fit_feedback->>'consensus'));
        """)
        print("✅ Created index on fit consensus for filtering")
        
        conn.commit()
        print("\n✨ Database ready for smart data!")
        
        # Show what we can now track
        print("\n📊 SMART DATA WE NOW TRACK:")
        print("-" * 40)
        print("• Product ratings & reviews (purchase confidence)")
        print("• Fit consensus from customers (size accuracy)")
        print("• Pricing & discounts (value perception)")
        print("• Fabric technology (comfort features)")
        print("• Detailed fit descriptions (preference matching)")
        
        print("\n🎯 AI INSIGHTS THIS ENABLES:")
        print("-" * 40)
        print("• 'Show highly-rated products only' (4.5+ stars)")
        print("• 'Avoid items that run small' (fit filtering)")
        print("• 'Find best value items' (discount sorting)")
        print("• 'Prefer stretch fabrics' (comfort matching)")
        print("• 'Predict satisfaction' (rating correlation)")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        conn.rollback()
        cur.close()
        conn.close()

if __name__ == "__main__":
    add_smart_columns()

