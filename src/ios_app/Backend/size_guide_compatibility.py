"""
Size Guide Compatibility Layer
Converts normalized size_guide_entries back to wide format for existing code.

This allows us to keep the superior normalized database schema while maintaining
compatibility with existing queries until we can implement the AI-driven system.
"""

import psycopg2
from typing import Dict, List, Any, Optional
from psycopg2.extras import RealDictCursor

def get_size_guide_entries_wide_format(
    db_config: Dict[str, str],
    brand_name: str, 
    category: str = "Tops"
) -> List[Dict[str, Any]]:
    """
    Get size guide entries in the old wide format that existing code expects.
    
    Converts from normalized format:
    measurement_type, min_value, max_value, range
    
    To wide format:
    chest_min, chest_max, chest_range, sleeve_min, sleeve_max, etc.
    """
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get all normalized entries for this brand/category
        cursor.execute("""
            SELECT 
                sge.size_label,
                sge.measurement_type,
                sge.min_value,
                sge.max_value,
                sge.range
            FROM size_guide_entries sge
            JOIN size_guides sg ON sge.size_guide_id = sg.id
            JOIN brands b ON sg.brand_id = b.id
            JOIN categories c ON sg.category_id = c.id
            WHERE b.name = %s AND c.name = %s
            ORDER BY 
                CASE sge.size_label
                    WHEN 'XS' THEN 1
                    WHEN 'S' THEN 2
                    WHEN 'M' THEN 3
                    WHEN 'L' THEN 4
                    WHEN 'XL' THEN 5
                    WHEN 'XXL' THEN 6
                    ELSE 7
                END,
                sge.measurement_type
        """, (brand_name, category))
        
        normalized_entries = cursor.fetchall()
        
        if not normalized_entries:
            return []
        
        # Convert to wide format
        wide_entries = {}
        
        for entry in normalized_entries:
            size_label = entry['size_label']
            measurement_type = entry['measurement_type']
            min_val = entry['min_value']
            max_val = entry['max_value']
            range_val = entry['range']
            
            # Initialize size entry if not exists
            if size_label not in wide_entries:
                wide_entries[size_label] = {
                    'size_label': size_label,
                    # Initialize all possible measurements to None
                    'chest_min': None, 'chest_max': None, 'chest_range': None,
                    'sleeve_min': None, 'sleeve_max': None, 'sleeve_range': None,
                    'waist_min': None, 'waist_max': None, 'waist_range': None,
                    'neck_min': None, 'neck_max': None, 'neck_range': None,
                    'hip_min': None, 'hip_max': None, 'hip_range': None,
                }
            
            # Map normalized data to wide format columns
            if measurement_type in ['chest', 'sleeve', 'waist', 'neck', 'hip']:
                wide_entries[size_label][f'{measurement_type}_min'] = min_val
                wide_entries[size_label][f'{measurement_type}_max'] = max_val
                wide_entries[size_label][f'{measurement_type}_range'] = range_val
        
        # Convert to list and sort by size
        result = list(wide_entries.values())
        size_order = {'XS': 1, 'S': 2, 'M': 3, 'L': 4, 'XL': 5, 'XXL': 6}
        result.sort(key=lambda x: size_order.get(x['size_label'], 7))
        
        return result
        
    finally:
        cursor.close()
        conn.close()


def get_user_garment_measurements_wide_format(
    db_config: Dict[str, str],
    user_id: int
) -> List[Dict[str, Any]]:
    """
    Get user garment measurements in wide format for closet/measurement endpoints.
    Only considers size_guide measurements (ignores garment_guide for MVP).
    """
    
    conn = psycopg2.connect(**db_config)
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get user garments with their size guide measurements (normalized)
        cursor.execute("""
            SELECT 
                ug.id as garment_id,
                ug.size_label,
                ug.product_name,
                ug.image_url,
                ug.product_url,
                ug.created_at,
                ug.owns_garment,
                ug.fit_feedback,
                b.name as brand_name,
                c.name as category,
                sge.measurement_type,
                sge.min_value,
                sge.max_value,
                sge.range
            FROM user_garments ug
            JOIN brands b ON ug.brand_id = b.id
            LEFT JOIN categories c ON ug.category_id = c.id
            LEFT JOIN size_guide_entries sge ON ug.size_guide_id = sge.size_guide_id 
                AND ug.size_label = sge.size_label
            WHERE ug.user_id = %s AND ug.owns_garment = true
            ORDER BY ug.created_at DESC
        """, (user_id,))
        
        normalized_data = cursor.fetchall()
        
        # Convert to wide format grouped by garment
        wide_garments = {}
        
        for row in normalized_data:
            garment_id = row['garment_id']
            
            # Initialize garment if not exists
            if garment_id not in wide_garments:
                wide_garments[garment_id] = {
                    'garment_id': garment_id,
                    'size_label': row['size_label'],
                    'product_name': row['product_name'],
                    'brand_name': row['brand_name'],
                    'category': row['category'],
                    'image_url': row['image_url'],
                    'product_url': row['product_url'],
                    'created_at': row['created_at'],
                    'owns_garment': row['owns_garment'],
                    'fit_feedback': row['fit_feedback'],
                    # Initialize measurements
                    'chest_min': None, 'chest_max': None, 'chest_range': None,
                    'sleeve_min': None, 'sleeve_max': None, 'sleeve_range': None,
                    'waist_min': None, 'waist_max': None, 'waist_range': None,
                    'neck_min': None, 'neck_max': None, 'neck_range': None,
                    'hip_min': None, 'hip_max': None, 'hip_range': None,
                }
            
            # Add measurement data if it exists
            measurement_type = row['measurement_type']
            if measurement_type in ['chest', 'sleeve', 'waist', 'neck', 'hip']:
                wide_garments[garment_id][f'{measurement_type}_min'] = row['min_value']
                wide_garments[garment_id][f'{measurement_type}_max'] = row['max_value']
                wide_garments[garment_id][f'{measurement_type}_range'] = row['range']
        
        return list(wide_garments.values())
        
    finally:
        cursor.close()
        conn.close()
