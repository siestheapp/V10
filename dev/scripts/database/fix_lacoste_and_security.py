#!/usr/bin/env python3
"""
Fix two issues:
1. Enable RLS on tables that should be secured
2. Remove estimated Lacoste size data, keep only real L size data
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DB_CONFIG = {
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432',
    'database': 'postgres',
    'user': 'fs_core_rw',
    'password': 'CHANGE_ME'
}

def main():
    print('🔧 FIXING SECURITY AND DATA ISSUES')
    print('=' * 50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print('✅ Connected to database\n')
        
        # Issue 1: Fix RLS on missing tables
        print('🔒 FIXING ROW LEVEL SECURITY:')
        
        tables_needing_rls = ['brands', 'categories', 'subcategories']
        
        for table in tables_needing_rls:
            print(f'\\n  📋 Securing {table} table:')
            
            # Enable RLS
            cur.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;')
            print(f'    ✅ RLS enabled')
            
            # Create policy for service role (full access)
            cur.execute(f'''
                CREATE POLICY "Service role has full access to {table}" ON {table}
                FOR ALL USING (auth.role() = 'service_role');
            ''')
            print(f'    ✅ Service role policy created')
            
            # Create policy for authenticated users (read-only for brands/categories)
            if table in ['brands', 'categories', 'subcategories']:
                cur.execute(f'''
                    CREATE POLICY "Authenticated users can read {table}" ON {table}
                    FOR SELECT USING (auth.role() = 'authenticated');
                ''')
                print(f'    ✅ Read-only policy for authenticated users created')
        
        # Issue 2: Remove estimated Lacoste size data
        print(f'\\n🗑️  FIXING LACOSTE SIZE DATA:')
        
        # Get Lacoste size guide ID
        cur.execute('''
            SELECT sg.id 
            FROM size_guides sg
            JOIN brands b ON sg.brand_id = b.id
            WHERE b.name = 'Lacoste'
        ''')
        
        lacoste_guide = cur.fetchone()
        if not lacoste_guide:
            print('  ❌ Lacoste size guide not found')
            return
            
        guide_id = lacoste_guide['id']
        
        # Show current entries
        cur.execute('''
            SELECT size_label, chest_min, chest_max, neck_min, neck_max
            FROM size_guide_entries
            WHERE size_guide_id = %s
            ORDER BY size_label
        ''', (guide_id,))
        
        current_entries = cur.fetchall()
        print(f'\\n  📊 CURRENT ENTRIES:')
        for entry in current_entries:
            print(f'    • {entry["size_label"]}: Chest {entry["chest_min"]}-{entry["chest_max"]}, Neck {entry["neck_min"]}-{entry["neck_max"]}')
        
        # Delete estimated entries (keep only L)
        cur.execute('''
            DELETE FROM size_guide_entries 
            WHERE size_guide_id = %s AND size_label != 'L'
        ''', (guide_id,))
        
        deleted_count = cur.rowcount
        print(f'\\n  🗑️  DELETED {deleted_count} estimated entries')
        
        # Verify only L remains
        cur.execute('''
            SELECT size_label, chest_min, chest_max, neck_min, neck_max
            FROM size_guide_entries
            WHERE size_guide_id = %s
        ''', (guide_id,))
        
        remaining_entries = cur.fetchall()
        print(f'\\n  ✅ REMAINING ENTRIES (real data only):')
        for entry in remaining_entries:
            print(f'    • {entry["size_label"]}: Chest {entry["chest_min"]}-{entry["chest_max"]}, Neck {entry["neck_min"]}-{entry["neck_max"]}')
        
        # Update size guide notes to reflect this
        cur.execute('''
            UPDATE size_guides 
            SET notes = %s
            WHERE id = %s
        ''', (
            '''Body measurements for Lacoste shirts. Based on recommended body measurements for each size.

CONFIRMED DATA:
- Size L: 43" chest, 16" neck (from Lacoste website)

PRODUCT MEASUREMENTS (Garment Dimensions):
From Lacoste CH3346 Regular Fit Button Down:

Size 16½-42 (L):
- Across chest: 24.1 inches (garment width)
- Sleeve length: 26.4 inches (garment sleeve)  
- Front length: 30.2 inches (garment length)

This represents actual garment dimensions, not body measurements.
Useful for understanding fit relationship between body and garment.

NOTE: Only L size data confirmed. Other sizes should be added when real data becomes available.''',
            guide_id
        ))
        
        print(f'\\n  📝 Updated size guide notes to reflect real data only')
        
        # Commit changes
        conn.commit()
        print(f'\\n✅ All fixes applied successfully!')
        
        print(f'\\n📊 SUMMARY:')
        print(f'  🔒 Security: RLS enabled on brands, categories, subcategories')
        print(f'  🗑️  Data: Removed {deleted_count} estimated Lacoste sizes')
        print(f'  ✅ Quality: Only real L size data remains')
        print(f'  📝 Documentation: Updated notes to reflect data source')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)

if __name__ == '__main__':
    main()
