#!/usr/bin/env python3
"""
Generate comprehensive User1 data profile for AI analysis
Purpose: Analyze how this data can improve clothing shopping experience around fit
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
import sys
import os

# Add backend to path for fit zone calculator
sys.path.append('src/ios_app/Backend')

# Database config
DB_CONFIG = {
    'database': 'postgres',
    'user': 'fs_core_rw', 
    'password': 'CHANGE_ME',
    'host': 'aws-1-us-east-1.pooler.supabase.com',
    'port': '5432'
}

def get_user1_complete_profile():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    profile = {}
    
    # Get basic user info
    cur.execute("SELECT id, email, created_at, gender, height_in, preferred_units FROM users WHERE id = 1")
    user_info = cur.fetchone()
    profile['user_info'] = dict(user_info) if user_info else None
    
    # Get body measurements (if available)
    try:
        cur.execute("""
            SELECT chest, waist, neck, sleeve, hip, inseam, length, created_at 
            FROM body_measurements 
            WHERE user_id = 1 
            ORDER BY created_at DESC
            LIMIT 1
        """)
        measurement = cur.fetchone()
        profile['body_measurements'] = dict(measurement) if measurement else None
    except:
        profile['body_measurements'] = None
    
    # Get owned garments with comprehensive details
    cur.execute("""
        SELECT 
            ug.id as garment_id,
            b.name as brand,
            c.name as category,
            ug.product_name,
            ug.size_label,
            ug.created_at,
            sge.chest_min, sge.chest_max,
            sge.sleeve_min, sge.sleeve_max,
            sge.neck_min, sge.neck_max,
            sge.waist_min, sge.waist_max,
            sge.center_back_length,
            ug.fit_feedback as overall_fit_feedback
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        LEFT JOIN categories c ON ug.category_id = c.id
        LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
        WHERE ug.user_id = 1 AND ug.owns_garment = true
        ORDER BY ug.created_at DESC
    """)
    garments = cur.fetchall()
    profile['owned_garments'] = [dict(g) for g in garments]
    
    # Get detailed feedback for each garment
    cur.execute("""
        SELECT 
            ugf.user_garment_id,
            ugf.dimension,
            fc.feedback_text,
            ugf.created_at
        FROM user_garment_feedback ugf
        JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
        WHERE ugf.user_garment_id IN (
            SELECT id FROM user_garments WHERE user_id = 1 AND owns_garment = true
        )
        ORDER BY ugf.user_garment_id, ugf.dimension
    """)
    feedback_data = cur.fetchall()
    
    # Group feedback by garment
    detailed_feedback = {}
    for fb in feedback_data:
        garment_id = fb['user_garment_id']
        if garment_id not in detailed_feedback:
            detailed_feedback[garment_id] = []
        detailed_feedback[garment_id].append(dict(fb))
    
    profile['detailed_feedback'] = detailed_feedback
    
    # Get complete size guide data for all brands user owns
    cur.execute("""
        SELECT DISTINCT b.id as brand_id, b.name as brand_name
        FROM user_garments ug
        JOIN brands b ON ug.brand_id = b.id
        WHERE ug.user_id = 1 AND ug.owns_garment = true
    """)
    user_brands = cur.fetchall()
    
    size_guides = {}
    for brand in user_brands:
        cur.execute("""
            SELECT 
                sge.size_label,
                sge.chest_min, sge.chest_max,
                sge.sleeve_min, sge.sleeve_max,
                sge.neck_min, sge.neck_max,
                sge.waist_min, sge.waist_max,
                sge.center_back_length,
                c.name as category
            FROM size_guide_entries sge
            JOIN size_guides sg ON sge.size_guide_id = sg.id
            JOIN categories c ON sg.category_id = c.id
            WHERE sg.brand_id = %s
            ORDER BY c.name, 
                CASE sge.size_label 
                    WHEN 'XXS' THEN 1 WHEN 'XS' THEN 2 WHEN 'S' THEN 3 
                    WHEN 'M' THEN 4 WHEN 'L' THEN 5 WHEN 'XL' THEN 6 
                    WHEN 'XXL' THEN 7 WHEN 'XXXL' THEN 8 
                    ELSE 9 
                END
        """, (brand['brand_id'],))
        
        brand_size_data = cur.fetchall()
        size_guides[brand['brand_name']] = [dict(sg) for sg in brand_size_data]
    
    profile['brand_size_guides'] = size_guides
    
    # Get recent user actions
    cur.execute("""
        SELECT action_type, target_table, target_id, is_undone, created_at
        FROM user_actions 
        WHERE user_id = 1 
        ORDER BY created_at DESC 
        LIMIT 20
    """)
    actions = cur.fetchall()
    profile['recent_actions'] = [dict(a) for a in actions]
    
    cur.close()
    conn.close()
    
    return profile

def format_report(profile):
    report = []
    
    # Header
    report.append('# USER1 COMPLETE DATA PROFILE FOR AI ANALYSIS')
    report.append('=' * 80)
    report.append('Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    report.append('')
    
    # Basic user info  
    report.append('## 1. USER PROFILE')
    report.append('-' * 50)
    if profile['user_info']:
        user = profile['user_info']
        report.append(f'User ID: {user.get("id", "N/A")}')
        report.append(f'Email: {user.get("email", "N/A")}')
        report.append(f'Gender: {user.get("gender", "N/A")}')
        report.append(f'Height: {user.get("height_in", "N/A")}" ({user.get("height_in", 0)/12:.1f} feet)')
        report.append(f'Preferred Units: {user.get("preferred_units", "N/A")}')
        report.append(f'Account Created: {user.get("created_at", "N/A")}')
    else:
        report.append('No user profile found')
    report.append('')
    
    # Body measurements
    report.append('## 2. BODY MEASUREMENTS')
    report.append('-' * 50)
    if profile['body_measurements']:
        measurements = profile['body_measurements']
        for key in ['chest', 'waist', 'neck', 'sleeve', 'hip', 'inseam', 'length']:
            if measurements.get(key):
                report.append(f'{key.title()}: {measurements[key]}"')
        report.append(f'Measured: {measurements.get("created_at", "Unknown")}')
    else:
        report.append('No body measurements found')
        report.append('Note: User relies on garment fit feedback for sizing guidance')
    report.append('')
    
    # Brand Size Guides - CRUCIAL FOR AI ANALYSIS
    report.append('## 3. BRAND SIZE GUIDE DATA')
    report.append('-' * 50)
    report.append('Complete sizing charts for all brands user1 owns garments from:')
    report.append('')
    
    for brand_name, size_data in profile['brand_size_guides'].items():
        report.append(f'### {brand_name.upper()}')
        if size_data:
            # Group by category
            categories = {}
            for entry in size_data:
                cat = entry['category']
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(entry)
            
            for category, entries in categories.items():
                report.append(f'{category}:')
                report.append('  Size | Chest      | Sleeve     | Neck       | Waist      | Length')
                report.append('  -----|------------|------------|------------|------------|------------')
                
                for entry in entries:
                    size = entry['size_label'].ljust(4)
                    
                    # Format measurements with proper handling of None values
                    def format_range(min_val, max_val):
                        if min_val is None:
                            return 'N/A'.ljust(10)
                        elif min_val == max_val:
                            return f'{min_val}"'.ljust(10)
                        else:
                            return f'{min_val}-{max_val}"'.ljust(10)
                    
                    chest = format_range(entry['chest_min'], entry['chest_max'])
                    sleeve = format_range(entry['sleeve_min'], entry['sleeve_max'])
                    neck = format_range(entry['neck_min'], entry['neck_max'])
                    waist = format_range(entry['waist_min'], entry['waist_max'])
                    length = entry['center_back_length'] if entry['center_back_length'] else 'N/A'.ljust(10)
                    
                    report.append(f'  {size} | {chest} | {sleeve} | {neck} | {waist} | {length}')
                report.append('')
        else:
            report.append('  No size guide data available')
            report.append('')
    
    # Cross-brand sizing comparison
    report.append('### CROSS-BRAND SIZING COMPARISON')
    report.append('How the same size varies across brands (Chest measurements):')
    
    # Get all sizes user owns
    user_sizes = set()
    for garment in profile['owned_garments']:
        user_sizes.add(garment['size_label'])
    
    for size in sorted(user_sizes):
        report.append(f'**Size {size}:**')
        for brand_name, size_data in profile['brand_size_guides'].items():
            for entry in size_data:
                if entry['size_label'] == size and entry['chest_min']:
                    if entry['chest_min'] == entry['chest_max']:
                        chest_range = f'{entry["chest_min"]}"'
                    else:
                        chest_range = f'{entry["chest_min"]}-{entry["chest_max"]}"'
                    report.append(f'  {brand_name}: {chest_range}')
                    break
        report.append('')
    
    # Owned garments with measurements
    report.append('## 4. OWNED GARMENTS WITH MEASUREMENTS')
    report.append('-' * 50)
    total_garments = len(profile['owned_garments'])
    report.append(f'Total Owned Garments: {total_garments}')
    report.append('')
    
    # Shopping patterns
    brands = {}
    sizes = {}
    categories = {}
    
    for i, g in enumerate(profile['owned_garments'], 1):
        # Track patterns
        brand = g['brand']
        size = g['size_label'] 
        category = g['category']
        
        brands[brand] = brands.get(brand, 0) + 1
        sizes[size] = sizes.get(size, 0) + 1
        categories[category] = categories.get(category, 0) + 1
        
        report.append(f'**GARMENT {i}: {g["brand"]} - {g["product_name"]}**')
        report.append(f'  Size: {g["size_label"]}')
        report.append(f'  Category: {g["category"] or "Unknown"}')
        report.append('  Measurements:')
        
        # Show actual measurements from size guide
        measurements = []
        if g['chest_min'] and g['chest_max']:
            if g['chest_min'] == g['chest_max']:
                measurements.append(f'Chest: {g["chest_min"]}" (avg: {g["chest_min"]}")')
            else:
                avg = (float(g['chest_min']) + float(g['chest_max'])) / 2
                measurements.append(f'Chest: {g["chest_min"]}-{g["chest_max"]}" (avg: {avg}")')
        
        if g['sleeve_min'] and g['sleeve_max']:
            if g['sleeve_min'] == g['sleeve_max']:
                measurements.append(f'Sleeve: {g["sleeve_min"]}"')
            else:
                avg = (float(g['sleeve_min']) + float(g['sleeve_max'])) / 2
                measurements.append(f'Sleeve: {g["sleeve_min"]}-{g["sleeve_max"]}" (avg: {avg}")')
        
        if g['neck_min'] and g['neck_max']:
            if g['neck_min'] == g['neck_max']:
                measurements.append(f'Neck: {g["neck_min"]}"')
            else:
                avg = (float(g['neck_min']) + float(g['neck_max'])) / 2
                measurements.append(f'Neck: {g["neck_min"]}-{g["neck_max"]}" (avg: {avg}")')
        
        for measurement in measurements:
            report.append(f'    {measurement}')
        
        # Get overall feedback from detailed feedback table
        overall_feedback = None
        for fb in profile['detailed_feedback'].get(g['garment_id'], []):
            if fb['dimension'] == 'overall':
                overall_feedback = fb['feedback_text']
                break
        report.append(f'  Overall Fit: {overall_feedback or "No feedback"}')
        report.append(f'  Added: {g["created_at"]}')
        report.append('')
    
    # Detailed feedback section
    report.append('## 5. DETAILED FIT FEEDBACK')
    report.append('-' * 50)
    
    for garment_id, feedback_list in profile['detailed_feedback'].items():
        if feedback_list:
            garment_name = next((g['product_name'] for g in profile['owned_garments'] if g['garment_id'] == garment_id), f'Garment {garment_id}')
            brand_name = next((g['brand'] for g in profile['owned_garments'] if g['garment_id'] == garment_id), 'Unknown')
            
            report.append(f'**{brand_name} - {garment_name}:**')
            for fb in feedback_list:
                report.append(f'  {fb["dimension"].capitalize()}: {fb["feedback_text"]}')
            report.append('')
    
    # Current fit zones
    report.append('## 6. CURRENT FIT ZONE CALCULATIONS')
    report.append('-' * 50)
    
    try:
        # Import the fit zone calculator
        import sys
        sys.path.append('src/ios_app/Backend')
        from fit_zone_calculator import FitZoneCalculator
        
        # Prepare garment data for calculator
        garment_list = []
        for g in profile['owned_garments']:
            if g['chest_min'] and g['chest_max']:
                chest_range = f'{g["chest_min"]}-{g["chest_max"]}' if g['chest_min'] != g['chest_max'] else str(g['chest_min'])
                
                # Get detailed feedback for this garment
                chest_feedback = None
                overall_feedback = None
                for fb in profile['detailed_feedback'].get(g['garment_id'], []):
                    if fb['dimension'] == 'chest':
                        chest_feedback = fb['feedback_text']
                    elif fb['dimension'] == 'overall':
                        overall_feedback = fb['feedback_text']
                
                garment_dict = {
                    'brand': g['brand'],
                    'garment_name': g['product_name'], 
                    'chest_range': chest_range,
                    'size': g['size_label'],
                    'fit_feedback': overall_feedback,
                    'chest_feedback': chest_feedback
                }
                garment_list.append(garment_dict)
        
        if garment_list:
            calculator = FitZoneCalculator()
            zones = calculator.calculate_chest_fit_zone(garment_list)
            
            if zones:
                report.append('**CURRENT CHEST FIT ZONES:**')
                report.append(f'  Tight: {zones.get("tight", {}).get("min", "N/A")}-{zones.get("tight", {}).get("max", "N/A")}"')
                report.append(f'  Good: {zones.get("good", {}).get("min", "N/A")}-{zones.get("good", {}).get("max", "N/A")}"')  
                report.append(f'  Relaxed: {zones.get("relaxed", {}).get("min", "N/A")}-{zones.get("relaxed", {}).get("max", "N/A")}"')
            else:
                report.append('No fit zones calculated (insufficient data)')
        else:
            report.append('No garments with chest measurements available')
            
    except Exception as e:
        report.append(f'Error calculating fit zones: {str(e)}')
    
    report.append('')
    
    # Shopping patterns analysis
    report.append('## 7. SHOPPING PATTERNS ANALYSIS')
    report.append('-' * 50)
    
    report.append('**Brand Preferences:**')
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
        report.append(f'  {brand}: {count} garments')
    
    report.append('')
    report.append('**Size Distribution:**')
    for size, count in sorted(sizes.items()):
        report.append(f'  Size {size}: {count} garments')
    
    report.append('')
    report.append('**Category Preferences:**')
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        report.append(f'  {category}: {count} garments')
    
    report.append('')
    
    # Recent activity
    report.append('## 8. RECENT USER ACTIONS')
    report.append('-' * 50)
    if profile['recent_actions']:
        for action in profile['recent_actions'][:10]:  # Show last 10
            status = '(UNDONE)' if action.get('is_undone') else ''
            report.append(f'{action["created_at"]}: {action["action_type"]} on {action["target_table"]} (ID: {action.get("target_id", "N/A")}) {status}')
    else:
        report.append('No recent actions found')
    
    report.append('')
    
    # Key insights for AI
    report.append('## 9. KEY INSIGHTS & QUESTIONS FOR AI ANALYSIS')
    report.append('-' * 50)
    report.append('**Data Available for Analysis:**')
    report.append('- Complete size guide data for all owned brands')
    report.append('- User body measurements')
    report.append('- Owned garments with specific size measurements')
    report.append('- Multi-dimensional fit feedback (overall, chest, sleeve, neck)')
    report.append('- Cross-brand sizing variations')
    report.append('')
    report.append('**Key Questions:**')
    report.append('1. How can we predict user1\'s size in new brands based on owned garment data?')
    report.append('2. What patterns exist in their fit preferences across different measurements?')
    report.append('3. How do their body measurements relate to their "Good Fit" feedback?')
    report.append('4. Which brands consistently fit well vs. poorly for this user?')
    report.append('5. Can we identify specific measurement ranges that correlate with positive feedback?')
    report.append('6. How can we improve the fit zone algorithm using this comprehensive data?')
    report.append('7. What size would user1 likely need in brands they don\'t own yet?')
    report.append('8. Are there measurement dimensions that are more predictive of satisfaction?')
    
    report.append('')
    report.append('---')
    report.append('END OF PROFILE')
    
    return '\n'.join(report)

if __name__ == '__main__':
    try:
        profile = get_user1_complete_profile()
        report = format_report(profile)
        print(report)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc() 