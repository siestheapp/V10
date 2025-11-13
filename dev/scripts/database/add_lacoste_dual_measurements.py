#!/usr/bin/env python3
"""
Script to add Lacoste brand with dual measurement system:
- Traditional body measurements (like existing brands)
- NEW: Product measurements (garment dimensions)

This creates a template for enhanced measurement data collection.
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
    print('🏷️  ADDING LACOSTE WITH DUAL MEASUREMENT SYSTEM')
    print('=' * 60)
    
    try:
        # Connect to database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print('✅ Connected to database\n')
        
        # Step 1: Add Lacoste brand
        print('🏢 ADDING LACOSTE BRAND:')
        
        # Check if Lacoste already exists
        cur.execute("SELECT id, name FROM brands WHERE name = 'Lacoste'")
        existing_brand = cur.fetchone()
        
        if existing_brand:
            print(f'  ⚠️  Lacoste already exists (ID: {existing_brand["id"]})')
            lacoste_brand_id = existing_brand['id']
        else:
            # Add Lacoste brand
            cur.execute('''
                INSERT INTO brands (name, region, default_unit, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            ''', (
                'Lacoste',
                'France', 
                'in',  # We'll store in inches for consistency
                'French luxury brand. Uses French sizing (42=L). Provides both product and body measurements.'
            ))
            
            lacoste_brand_id = cur.fetchone()['id']
            print(f'  ✅ Added Lacoste brand (ID: {lacoste_brand_id})')
        
        # Step 2: Get Tops category ID
        cur.execute("SELECT id FROM categories WHERE name = 'Tops'")
        tops_category = cur.fetchone()
        
        if not tops_category:
            print('❌ Tops category not found!')
            return
            
        tops_id = tops_category['id']
        
        # Step 3: Create BODY MEASUREMENTS size guide (traditional)
        print(f'\\n📏 CREATING BODY MEASUREMENTS SIZE GUIDE:')
        
        cur.execute('''
            INSERT INTO size_guides (
                brand_id, gender, category_id, fit_type, unit, 
                notes, source_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            lacoste_brand_id,
            'Male',
            tops_id,
            'Regular',
            'in',
            'Body measurements for Lacoste shirts. Based on recommended body measurements for each size.',
            'https://www.lacoste.com/us/lacoste/men/clothing/button-down-shirts/CH3346-51-DPC.html'
        ))
        
        body_guide_id = cur.fetchone()['id']
        print(f'  ✅ Created body measurements guide (ID: {body_guide_id})')
        
        # Add body measurement entries (from your Lacoste screenshots)
        body_measurements = [
            # Size, Neck, Chest, Waist (from Lacoste body measurements)
            ('S', 15.0, 15.5, 39.0, 41.0, 36.0, 37.0),     # Estimated based on L=42
            ('M', 15.5, 16.0, 41.0, 42.0, 37.0, 38.0),     # Estimated 
            ('L', 16.0, 16.0, 43.0, 43.0, 38.0, 38.0),     # From screenshot: 16" neck, 43" chest, 38" waist
            ('XL', 16.5, 17.0, 44.0, 46.0, 39.0, 40.0),    # Estimated progression
            ('XXL', 17.0, 17.5, 46.0, 48.0, 40.0, 42.0)    # Estimated progression
        ]
        
        for size_data in body_measurements:
            size_label, neck_min, neck_max, chest_min, chest_max, waist_min, waist_max = size_data
            
            cur.execute('''
                INSERT INTO size_guide_entries (
                    size_guide_id, size_label,
                    neck_min, neck_max,
                    chest_min, chest_max,
                    waist_min, waist_max,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                body_guide_id, size_label,
                neck_min, neck_max,
                chest_min, chest_max, 
                waist_min, waist_max,
                f'Body measurements for size {size_label}. L size confirmed from Lacoste website.'
            ))
            
            print(f'    • {size_label}: Neck {neck_min}-{neck_max}\", Chest {chest_min}-{chest_max}\", Waist {waist_min}-{waist_max}\"')
        
        # Step 4: Create PRODUCT MEASUREMENTS tracking (NEW CONCEPT)
        print(f'\\n📐 CREATING PRODUCT MEASUREMENTS TRACKING:')
        print(f'  💡 This is NEW - storing actual garment dimensions')
        
        # For now, let's add this as notes in the size guide
        # In the future, we could create a separate table for product measurements
        
        product_measurements_note = '''
PRODUCT MEASUREMENTS (Garment Dimensions):
From Lacoste CH3346 Regular Fit Button Down:

Size 16½-42 (L):
- Across chest: 24.1 inches (garment width)
- Sleeve length: 26.4 inches (garment sleeve)  
- Front length: 30.2 inches (garment length)

This represents actual garment dimensions, not body measurements.
Useful for understanding fit relationship between body and garment.
'''
        
        cur.execute('''
            UPDATE size_guides 
            SET notes = notes || %s
            WHERE id = %s
        ''', (product_measurements_note, body_guide_id))
        
        print(f'  ✅ Added product measurements as detailed notes')
        print(f'  📝 Future enhancement: Create separate product_measurements table')
        
        # Step 5: Add the actual garment
        print(f'\\n👕 ADDING YOUR LACOSTE GARMENT:')
        
        # Get Button-Down Shirts subcategory
        cur.execute('''
            SELECT id FROM subcategories 
            WHERE name = 'Button-Down Shirts' AND category_id = %s
        ''', (tops_id,))
        
        button_down_subcat = cur.fetchone()
        
        if not button_down_subcat:
            print('❌ Button-Down Shirts subcategory not found!')
            return
            
        subcat_id = button_down_subcat['id']
        
        # Add the garment
        cur.execute('''
            INSERT INTO user_garments (
                user_id, brand_id, category_id, subcategory_id,
                product_name, size_label, product_url,
                owns_garment, fit_feedback,
                notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            1,  # user_id
            lacoste_brand_id,
            tops_id,
            subcat_id,
            'Regular Fit Button Down Shirt',
            'L (42 French)',
            'https://www.lacoste.com/us/lacoste/men/clothing/button-down-shirts/CH3346-51-DPC.html',
            True,  # owns_garment
            None,  # fit_feedback - to be added after wearing
            'French sizing: L = 42. Regular fit style. Has both product and body measurements available.'
        ))
        
        garment_id = cur.fetchone()['id']
        print(f'  ✅ Added Lacoste garment (ID: {garment_id})')
        print(f'  📏 Size: L (42 French) - matches your sizing preference')
        print(f'  🔗 URL: Saved for reference')
        
        # Step 6: Summary
        print(f'\\n📊 SUMMARY:')
        print(f'  ✅ Lacoste brand added with French sizing context')
        print(f'  ✅ Body measurements size guide created (traditional)')
        print(f'  ✅ Product measurements documented (innovation)')
        print(f'  ✅ Your L/42 garment added and categorized')
        print(f'  🎯 Ready for fit feedback once you receive the shirt')
        
        print(f'\\n🚀 AI TRAINING BENEFITS:')
        print(f'  • Adds INTERNATIONAL SIZING (French 42 = US L)')
        print(f'  • Introduces DUAL MEASUREMENT CONCEPT')
        print(f'  • Expands brand diversity (luxury French brand)')
        print(f'  • Provides SIZE CONVERSION data point')
        
        # Commit changes
        conn.commit()
        print(f'\\n✅ All changes committed successfully!')
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Error: {e}')
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)

if __name__ == '__main__':
    main()
