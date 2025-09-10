#!/usr/bin/env python3
"""
Setup J.Crew data in the database for production readiness.
This script adds J.Crew size guides and pre-stores some popular products.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

# Database connection
conn = psycopg2.connect(
    database='postgres',
    user='postgres.lbilxlkchzpducggkrxx',
    password='efvTower12',
    host='aws-0-us-east-2.pooler.supabase.com',
    port='6543',
    cursor_factory=RealDictCursor
)
cur = conn.cursor()

def add_jcrew_size_guides():
    """Add J.Crew size guides for men's tops"""
    
    print("Adding J.Crew size guides...")
    
    # J.Crew Men's Shirts Size Guide (in inches)
    shirts_size_guide = {
        'XS': {'chest': [34, 36], 'neck': [14, 14.5], 'sleeve': [32, 32.5]},
        'S': {'chest': [36, 38], 'neck': [14.5, 15], 'sleeve': [33, 33.5]},
        'M': {'chest': [38, 40], 'neck': [15, 15.5], 'sleeve': [34, 34.5]},
        'L': {'chest': [41, 43], 'neck': [15.5, 16], 'sleeve': [35, 35.5]},
        'XL': {'chest': [44, 46], 'neck': [16, 16.5], 'sleeve': [36, 36.5]},
        'XXL': {'chest': [47, 49], 'neck': [16.5, 17], 'sleeve': [37, 37.5]}
    }
    
    # J.Crew Men's T-Shirts & Polos Size Guide
    tshirts_size_guide = {
        'XS': {'chest': [34, 36], 'length': [26.5, 27]},
        'S': {'chest': [36, 38], 'length': [27, 27.5]},
        'M': {'chest': [38, 40], 'length': [27.5, 28]},
        'L': {'chest': [41, 43], 'length': [28, 28.5]},
        'XL': {'chest': [44, 46], 'length': [28.5, 29]},
        'XXL': {'chest': [47, 49], 'length': [29, 29.5]}
    }
    
    # Create garment guide for shirts
    cur.execute("""
        INSERT INTO garment_guides (
            brand_id, 
            info_source, 
            guide_header,
            measurements_available,
            source_url,
            notes,
            created_at,
            created_by
        ) VALUES (
            4,  -- J.Crew brand ID
            'size_chart',
            'J.Crew Men''s Shirts Size Guide',
            ARRAY['chest', 'neck', 'sleeve'],
            'https://www.jcrew.com/size-charts',
            'Standard J.Crew men''s shirts sizing',
            NOW(),
            1
        )
        RETURNING id
    """)
    shirts_guide_id = cur.fetchone()['id']
    
    # Add shirt size entries
    for size, measurements in shirts_size_guide.items():
        # Add chest measurement (using midpoint of range)
        chest_value = (measurements['chest'][0] + measurements['chest'][1]) / 2
        cur.execute("""
            INSERT INTO garment_guide_entries (
                garment_guide_id, size_label, measurement_type, 
                measurement_value_in, measurement_value_cm,
                measurement_source, source_term, measurement_format,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
        """, (
            shirts_guide_id, size, 'g_chest_width',
            chest_value, chest_value * 2.54,  # Convert to cm
            'size_chart', 'Chest', 'table'
        ))
        
        # Add neck measurement
        neck_value = (measurements['neck'][0] + measurements['neck'][1]) / 2
        cur.execute("""
            INSERT INTO garment_guide_entries (
                garment_guide_id, size_label, measurement_type, 
                measurement_value_in, measurement_value_cm,
                measurement_source, source_term, measurement_format,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
        """, (
            shirts_guide_id, size, 'g_neck_opening',
            neck_value, neck_value * 2.54,
            'size_chart', 'Neck', 'table'
        ))
        
        # Add sleeve measurement
        sleeve_value = (measurements['sleeve'][0] + measurements['sleeve'][1]) / 2
        cur.execute("""
            INSERT INTO garment_guide_entries (
                garment_guide_id, size_label, measurement_type, 
                measurement_value_in, measurement_value_cm,
                measurement_source, source_term, measurement_format,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
        """, (
            shirts_guide_id, size, 'g_sleeve_length',
            sleeve_value, sleeve_value * 2.54,
            'size_chart', 'Sleeve', 'table'
        ))
    
    print(f"✅ Added shirts guide (ID: {shirts_guide_id}) with {len(shirts_size_guide)} sizes")
    
    # Create garment guide for t-shirts
    cur.execute("""
        INSERT INTO garment_guides (
            brand_id, 
            info_source, 
            guide_header,
            measurements_available,
            source_url,
            notes,
            created_at,
            created_by
        ) VALUES (
            4,  -- J.Crew brand ID
            'size_chart',
            'J.Crew Men''s T-Shirts & Polos Size Guide',
            ARRAY['chest', 'length'],
            'https://www.jcrew.com/size-charts',
            'Standard J.Crew men''s t-shirts and polos sizing',
            NOW(),
            1
        )
        RETURNING id
    """)
    tshirts_guide_id = cur.fetchone()['id']
    
    # Add t-shirt size entries
    for size, measurements in tshirts_size_guide.items():
        # Add chest measurement (using midpoint of range)
        chest_value = (measurements['chest'][0] + measurements['chest'][1]) / 2
        cur.execute("""
            INSERT INTO garment_guide_entries (
                garment_guide_id, size_label, measurement_type, 
                measurement_value_in, measurement_value_cm,
                measurement_source, source_term, measurement_format,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
        """, (
            tshirts_guide_id, size, 'g_chest_width',
            chest_value, chest_value * 2.54,
            'size_chart', 'Chest', 'table'
        ))
        
        # Add length measurement
        length_value = (measurements['length'][0] + measurements['length'][1]) / 2
        cur.execute("""
            INSERT INTO garment_guide_entries (
                garment_guide_id, size_label, measurement_type, 
                measurement_value_in, measurement_value_cm,
                measurement_source, source_term, measurement_format,
                created_at, created_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 1)
        """, (
            tshirts_guide_id, size, 'g_body_length',
            length_value, length_value * 2.54,
            'size_chart', 'Length', 'table'
        ))
    
    print(f"✅ Added t-shirts guide (ID: {tshirts_guide_id}) with {len(tshirts_size_guide)} sizes")
    
    conn.commit()
    return shirts_guide_id, tshirts_guide_id

def add_jcrew_product_cache():
    """Add a table to cache J.Crew product data including images"""
    
    print("\nCreating product cache table...")
    
    # Create product cache table if it doesn't exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jcrew_product_cache (
            id SERIAL PRIMARY KEY,
            product_url TEXT UNIQUE NOT NULL,
            product_code TEXT,
            product_name TEXT NOT NULL,
            product_image TEXT,
            category TEXT,
            subcategory TEXT,
            price DECIMAL(10, 2),
            sizes_available TEXT[],
            colors_available TEXT[],
            material TEXT,
            fit_type TEXT,
            description TEXT,
            metadata JSONB,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP
        )
    """)
    
    # Create index for faster lookups
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_jcrew_product_url 
        ON jcrew_product_cache(product_url)
    """)
    
    conn.commit()
    print("✅ Product cache table created")

def add_sample_products():
    """Add some popular J.Crew products for immediate use"""
    
    print("\nAdding sample J.Crew products...")
    
    sample_products = [
        {
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996',
            'product_code': 'BE996',
            'product_name': 'Broken-in organic cotton oxford shirt',
            'product_image': 'https://www.jcrew.com/s7-img-facade/BE996_WZ2195',
            'category': 'Shirts',
            'subcategory': 'Oxford Shirts',
            'sizes_available': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
            'colors_available': ['White', 'Light Blue', 'Navy', 'Pink'],
            'material': '100% organic cotton',
            'fit_type': 'Classic',
            'description': 'Our broken-in shirts are garment-dyed and washed for a soft feel from day one.'
        },
        {
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/t-shirts-polos/long-sleeve-t-shirts/long-sleeve-broken-in-t-shirt/AW939',
            'product_code': 'AW939',
            'product_name': 'Long-sleeve broken-in T-shirt',
            'product_image': 'https://www.jcrew.com/s7-img-facade/AW939_WT0002',
            'category': 'T-Shirts',
            'subcategory': 'Long Sleeve T-Shirts',
            'sizes_available': ['XS', 'S', 'M', 'L', 'XL', 'XXL'],
            'colors_available': ['White', 'Black', 'Navy', 'Heather Gray'],
            'material': '100% cotton',
            'fit_type': 'Classic',
            'description': 'Our signature broken-in tee in a long-sleeve version.'
        },
        {
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/shirts/flex-casual/flex-casual-shirt/BU222',
            'product_code': 'BU222',
            'product_name': 'Flex Casual Shirt',
            'product_image': 'https://www.jcrew.com/s7-img-facade/BU222_WZ2046',
            'category': 'Shirts',
            'subcategory': 'Casual Shirts',
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'colors_available': ['Blue Check', 'Red Plaid', 'Green Stripe'],
            'material': 'Cotton blend with stretch',
            'fit_type': 'Slim',
            'description': 'Our Flex Casual shirt is designed for comfort and ease of movement.'
        },
        {
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/polos/short-sleeve-polos/garment-dyed-slub-cotton-polo/AZ876',
            'product_code': 'AZ876',
            'product_name': 'Garment-dyed slub cotton polo',
            'product_image': 'https://www.jcrew.com/s7-img-facade/AZ876_WX0144',
            'category': 'Polos',
            'subcategory': 'Short Sleeve Polos',
            'sizes_available': ['S', 'M', 'L', 'XL'],
            'colors_available': ['White', 'Navy', 'Green', 'Pink'],
            'material': '100% cotton',
            'fit_type': 'Classic',
            'description': 'A textured polo that gets better with every wear.'
        },
        {
            'product_url': 'https://www.jcrew.com/p/mens/categories/clothing/sweaters/pullover/cotton-crewneck-sweater/AY671',
            'product_code': 'AY671',
            'product_name': 'Cotton crewneck sweater',
            'product_image': 'https://www.jcrew.com/s7-img-facade/AY671_WZ0971',
            'category': 'Sweaters',
            'subcategory': 'Pullover',
            'sizes_available': ['S', 'M', 'L', 'XL', 'XXL'],
            'colors_available': ['Navy', 'Gray', 'Cream', 'Forest Green'],
            'material': '100% cotton',
            'fit_type': 'Regular',
            'description': 'A classic crewneck sweater in soft cotton.'
        }
    ]
    
    for product in sample_products:
        try:
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, sizes_available, colors_available,
                    material, fit_type, description
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                ON CONFLICT (product_url) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_image = EXCLUDED.product_image,
                    updated_at = NOW()
            """, (
                product['product_url'],
                product['product_code'],
                product['product_name'],
                product['product_image'],
                product['category'],
                product['subcategory'],
                product['sizes_available'],
                product['colors_available'],
                product['material'],
                product['fit_type'],
                product['description']
            ))
            print(f"✅ Added: {product['product_name']}")
        except Exception as e:
            print(f"❌ Error adding {product['product_name']}: {e}")
    
    conn.commit()

def main():
    try:
        print("🚀 Setting up J.Crew data for production...")
        print("=" * 60)
        
        # Add size guides
        shirts_guide_id, tshirts_guide_id = add_jcrew_size_guides()
        
        # Create product cache table
        add_jcrew_product_cache()
        
        # Add sample products
        add_sample_products()
        
        print("\n" + "=" * 60)
        print("✅ J.Crew setup complete!")
        print("\nSummary:")
        print(f"  - Added 2 size guides (Shirts: {shirts_guide_id}, T-Shirts: {tshirts_guide_id})")
        print(f"  - Created product cache table")
        print(f"  - Added 5 sample products")
        print("\n📝 Next steps:")
        print("  1. Update backend to check cache before scraping")
        print("  2. Test with J.Crew product URLs")
        print("  3. Add more products as needed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
