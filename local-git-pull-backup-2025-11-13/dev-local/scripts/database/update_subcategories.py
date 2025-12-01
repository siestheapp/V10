#!/usr/bin/env python3
"""
Script to add new subcategories and update garment categorization
for AI training preparation.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import sys

# Database configuration
DB_CONFIG = {
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543',
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx',
    'password': 'efvTower12'
}

def main():
    print('🔧 UPDATING SUBCATEGORIES FOR AI TRAINING')
    print('=' * 50)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print('✅ Connected to database\n')
        
        # Step 1: Check current subcategories
        print('📋 CURRENT SUBCATEGORIES:')
        cur.execute('''
            SELECT sc.id, sc.name, c.name as category
            FROM subcategories sc
            JOIN categories c ON sc.category_id = c.id
            ORDER BY c.name, sc.name
        ''')
        current_subcats = cur.fetchall()
        
        for subcat in current_subcats:
            print(f'  • {subcat["category"]} > {subcat["name"]} (ID: {subcat["id"]})')
        
        # Step 2: Get Tops category ID
        cur.execute("SELECT id FROM categories WHERE name = 'Tops'")
        tops_category = cur.fetchone()
        
        if not tops_category:
            print('❌ Tops category not found!')
            return
            
        tops_id = tops_category['id']
        print(f'\n🎯 Tops category ID: {tops_id}')
        
        # Step 3: Add new subcategories
        print('\n➕ ADDING NEW SUBCATEGORIES:')
        
        new_subcategories = [
            {
                'name': 'Long-Sleeve Polos',
                'description': 'Long-sleeve polo shirts including quarter-zip and button styles'
            },
            {
                'name': 'Lightweight Knits',
                'description': 'Light sweaters and knit shirts that function like shirts'
            }
        ]
        
        added_subcats = {}
        
        for subcat in new_subcategories:
            # Check if already exists
            cur.execute('''
                SELECT id FROM subcategories 
                WHERE name = %s AND category_id = %s
            ''', (subcat['name'], tops_id))
            
            existing = cur.fetchone()
            
            if existing:
                print(f'  ⚠️  {subcat["name"]} already exists (ID: {existing["id"]})')
                added_subcats[subcat['name']] = existing['id']
            else:
                # Add new subcategory
                cur.execute('''
                    INSERT INTO subcategories (category_id, name, description)
                    VALUES (%s, %s, %s)
                    RETURNING id
                ''', (tops_id, subcat['name'], subcat['description']))
                
                new_id = cur.fetchone()['id']
                added_subcats[subcat['name']] = new_id
                print(f'  ✅ Added {subcat["name"]} (ID: {new_id})')
        
        # Step 4: Update garment categorization
        print('\n🔄 UPDATING GARMENT CATEGORIZATION:')
        
        # Get the specific garments that need updating
        cur.execute('''
            SELECT ug.id, ug.product_name, b.name as brand, ug.subcategory_id
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            WHERE ug.user_id = 1 
            AND ug.owns_garment = true
            AND (
                (b.name = 'Lululemon' AND ug.product_name ILIKE '%evolution%')
                OR 
                (b.name = 'J.Crew' AND ug.product_name ILIKE '%sweater%')
            )
        ''')
        
        garments_to_update = cur.fetchall()
        
        for garment in garments_to_update:
            print(f'\n  📦 {garment["brand"]} - {garment["product_name"]}')
            print(f'      Current subcategory ID: {garment["subcategory_id"] or "None"}')
            
            if 'Lululemon' in garment['brand'] and 'evolution' in garment['product_name'].lower():
                # Update Lululemon to Long-Sleeve Polos
                new_subcat_id = added_subcats['Long-Sleeve Polos']
                notes = 'Quarter-zip style with buttons, athletic fit'
                
                cur.execute('''
                    UPDATE user_garments 
                    SET subcategory_id = %s, notes = %s
                    WHERE id = %s
                ''', (new_subcat_id, notes, garment['id']))
                
                print(f'      ✅ Updated to Long-Sleeve Polos (ID: {new_subcat_id})')
                print(f'      📝 Added notes: {notes}')
                
            elif 'J.Crew' in garment['brand'] and 'sweater' in garment['product_name'].lower():
                # Update J.Crew to Lightweight Knits
                new_subcat_id = added_subcats['Lightweight Knits']
                notes = 'Cotton piqué texture, functions like a shirt'
                
                cur.execute('''
                    UPDATE user_garments 
                    SET subcategory_id = %s, notes = %s
                    WHERE id = %s
                ''', (new_subcat_id, notes, garment['id']))
                
                print(f'      ✅ Updated to Lightweight Knits (ID: {new_subcat_id})')
                print(f'      📝 Added notes: {notes}')
        
        # Step 5: Verify all garments are now categorized
        print('\n🔍 VERIFICATION - ALL GARMENTS CATEGORIZATION:')
        cur.execute('''
            SELECT 
                ug.id,
                b.name as brand,
                ug.product_name,
                ug.size_label,
                c.name as category,
                sc.name as subcategory,
                ug.notes
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id
            LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
            WHERE ug.user_id = 1 
            AND ug.owns_garment = true
            ORDER BY b.name, ug.product_name
        ''')
        
        all_garments = cur.fetchall()
        uncategorized_count = 0
        
        print(f'\n📊 FINAL CATEGORIZATION STATUS:')
        for garment in all_garments:
            subcat_status = garment['subcategory'] or '❌ MISSING'
            if not garment['subcategory']:
                uncategorized_count += 1
                
            print(f'  • {garment["brand"]} {garment["size_label"]} - {garment["product_name"]}')
            print(f'    Category: {garment["category"]} > {subcat_status}')
            if garment['notes']:
                print(f'    Notes: {garment["notes"]}')
            print()
        
        print(f'📈 SUMMARY:')
        print(f'  • Total garments: {len(all_garments)}')
        print(f'  • Fully categorized: {len(all_garments) - uncategorized_count}')
        print(f'  • Missing subcategory: {uncategorized_count}')
        
        if uncategorized_count == 0:
            print(f'  🎉 ALL GARMENTS ARE FULLY CATEGORIZED!')
        
        # Commit changes
        conn.commit()
        print(f'\n✅ All changes committed successfully!')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)

if __name__ == '__main__':
    main()
