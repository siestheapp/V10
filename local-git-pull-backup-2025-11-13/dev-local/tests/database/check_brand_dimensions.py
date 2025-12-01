#!/usr/bin/env python3
"""
Quickly check what dimensions are available for each brand's size guide
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

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def check_brand_dimensions():
    """Check what dimensions are available for each brand's size guide"""
    
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get all brands with their size guides and available dimensions
        cursor.execute("""
            SELECT 
                b.id as brand_id,
                b.name as brand_name,
                sg.id as size_guide_id,
                sg.gender,
                c.name as category_name,
                sg.fit_type,
                COUNT(sge.id) as total_entries,
                -- Check which dimensions have data
                CASE WHEN COUNT(CASE WHEN sge.chest_min IS NOT NULL OR sge.chest_max IS NOT NULL OR sge.chest_range IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as chest,
                CASE WHEN COUNT(CASE WHEN sge.waist_min IS NOT NULL OR sge.waist_max IS NOT NULL OR sge.waist_range IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as waist,
                CASE WHEN COUNT(CASE WHEN sge.sleeve_min IS NOT NULL OR sge.sleeve_max IS NOT NULL OR sge.sleeve_range IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as sleeve,
                CASE WHEN COUNT(CASE WHEN sge.neck_min IS NOT NULL OR sge.neck_max IS NOT NULL OR sge.neck_range IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as neck,
                CASE WHEN COUNT(CASE WHEN sge.hip_min IS NOT NULL OR sge.hip_max IS NOT NULL OR sge.hip_range IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as hip,
                CASE WHEN COUNT(CASE WHEN sge.center_back_length IS NOT NULL THEN 1 END) > 0 THEN '✅' ELSE '❌' END as length
            FROM brands b
            LEFT JOIN size_guides sg ON b.id = sg.brand_id
            LEFT JOIN categories c ON sg.category_id = c.id
            LEFT JOIN size_guide_entries sge ON sg.id = sge.size_guide_id
            GROUP BY b.id, b.name, sg.id, sg.gender, c.name, sg.fit_type
            ORDER BY b.name, sg.gender, c.name, sg.fit_type
        """)
        
        results = cursor.fetchall()
        
        if not results:
            print("❌ No brands with size guides found.")
            return
        
        print("📊 BRAND SIZE GUIDE DIMENSIONS")
        print("=" * 80)
        
        current_brand = None
        for row in results:
            brand_id, brand_name, size_guide_id, gender, category, fit_type, total_entries, chest, waist, sleeve, neck, hip, length = row
            
            # Print brand header if it's a new brand
            if current_brand != brand_name:
                print(f"\n🏷️  BRAND: {brand_name} (ID: {brand_id})")
                print("-" * 50)
                current_brand = brand_name
            
            # Print size guide details
            print(f"  📏 Size Guide {size_guide_id}: {gender} {category} ({fit_type})")
            print(f"     📋 Entries: {total_entries}")
            print(f"     📐 Dimensions: Chest{chest} Waist{waist} Sleeve{sleeve} Neck{neck} Hip{hip} Length{length}")
            
            # Show available dimensions as a list
            available_dims = []
            if chest == '✅': available_dims.append('Chest')
            if waist == '✅': available_dims.append('Waist')
            if sleeve == '✅': available_dims.append('Sleeve')
            if neck == '✅': available_dims.append('Neck')
            if hip == '✅': available_dims.append('Hip')
            if length == '✅': available_dims.append('Length')
            
            if available_dims:
                print(f"     ✅ Available: {', '.join(available_dims)}")
            else:
                print(f"     ⚠️  No dimensions available")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking brand dimensions: {e}")

if __name__ == "__main__":
    check_brand_dimensions() 