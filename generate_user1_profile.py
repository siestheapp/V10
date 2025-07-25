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
sys.path.append('ios_app/Backend')

# Database config
DB_CONFIG = {
    'database': 'postgres',
    'user': 'postgres.lbilxlkchzpducggkrxx', 
    'password': 'efvTower12',
    'host': 'aws-0-us-east-2.pooler.supabase.com',
    'port': '6543'
}

def get_user1_complete_profile():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    profile = {}
    
    # 1. User Profile
    cur.execute('SELECT * FROM users WHERE id = 1')
    user_row = cur.fetchone()
    profile['user'] = dict(user_row) if user_row else None
    
    # 2. Body Measurements
    cur.execute('SELECT * FROM body_measurements WHERE user_id = 1 ORDER BY created_at DESC')
    profile['body_measurements'] = [dict(row) for row in cur.fetchall()]
    
    # 3. Owned Garments with Details
    cur.execute('''
        SELECT 
            ug.id as garment_id,
            b.name as brand_name,
            ug.product_name,
            ug.size_label,
            ug.fit_type,
            c.name as category,
            sc.name as subcategory,
            ug.owns_garment,
            ug.fit_feedback as overall_fit_feedback,
            ug.feedback_timestamp,
            ug.product_url,
            ug.created_at,
            -- Size guide measurements
            sge.chest_min, sge.chest_max,
            sge.waist_min, sge.waist_max, 
            sge.sleeve_min, sge.sleeve_max,
            sge.neck_min, sge.neck_max,
            sge.center_back_length
        FROM user_garments ug
        LEFT JOIN brands b ON ug.brand_id = b.id
        LEFT JOIN categories c ON ug.category_id = c.id  
        LEFT JOIN subcategories sc ON ug.subcategory_id = sc.id
        LEFT JOIN size_guide_entries sge ON ug.size_guide_entry_id = sge.id
        WHERE ug.user_id = 1 AND ug.owns_garment = true
        ORDER BY ug.created_at DESC
    ''')
    profile['garments'] = [dict(row) for row in cur.fetchall()]
    
    # 4. Detailed Feedback per Garment
    profile['detailed_feedback'] = {}
    for garment in profile['garments']:
        cur.execute('''
            SELECT 
                ugf.dimension,
                fc.feedback_text,
                ugf.created_at
            FROM user_garment_feedback ugf
            JOIN feedback_codes fc ON ugf.feedback_code_id = fc.id
            WHERE ugf.user_garment_id = %s
            ORDER BY ugf.created_at DESC
        ''', (garment['garment_id'],))
        profile['detailed_feedback'][garment['garment_id']] = [dict(row) for row in cur.fetchall()]
    
    # 5. User Actions/History
    cur.execute('''
        SELECT action_type, target_table, target_id, created_at, is_undone
        FROM user_actions 
        WHERE user_id = 1 
        ORDER BY created_at DESC 
        LIMIT 20
    ''')
    profile['recent_actions'] = [dict(row) for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return profile

def generate_report():
    # Get complete profile
    profile = get_user1_complete_profile()
    
    report = []
    report.append('=== USER1 COMPLETE DATA PROFILE FOR AI ANALYSIS ===')
    report.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    report.append('Purpose: Analyze how this data can improve clothing shopping experience around fit')
    report.append('')
    
    # User Profile
    report.append('1. USER PROFILE')
    report.append('-' * 50)
    if profile['user']:
        user = profile['user']
        report.append(f'User ID: {user["id"]}')
        report.append(f'Email: {user["email"]}')
        report.append(f'Gender: {user["gender"]}')  
        report.append(f'Height: {user["height_in"]}" ({user["height_in"]/12:.1f} feet)')
        report.append(f'Preferred Units: {user["preferred_units"]}')
        report.append(f'Account Created: {user["created_at"]}')
    report.append('')
    
    # Body Measurements
    report.append('2. BODY MEASUREMENTS')
    report.append('-' * 50)
    if profile['body_measurements']:
        for i, bm in enumerate(profile['body_measurements'], 1):
            report.append(f'Measurement Set {i}:')
            dimensions = ['chest', 'waist', 'neck', 'sleeve', 'hip', 'inseam', 'length']
            for dim in dimensions:
                if bm.get(dim):
                    report.append(f'  {dim.capitalize()}: {bm[dim]}"')
            report.append(f'  Confidence: {bm.get("confidence_score", "N/A")}')
            report.append(f'  Source: {bm.get("source", "N/A")}')
            report.append(f'  Created: {bm["created_at"]}')
            report.append('')
    else:
        report.append('No stored body measurements')
        report.append('Note: User relies on garment fit feedback for sizing guidance')
    report.append('')
    
    # Garments with Analysis
    report.append('3. OWNED GARMENTS WITH MEASUREMENTS')
    report.append('-' * 50)
    total_garments = len(profile['garments'])
    report.append(f'Total Owned Garments: {total_garments}')
    report.append('')
    
    brands = {}
    sizes = {}
    categories = {}
    
    for i, g in enumerate(profile['garments'], 1):
        # Track patterns
        brand = g['brand_name']
        size = g['size_label'] 
        category = g['category']
        
        brands[brand] = brands.get(brand, 0) + 1
        sizes[size] = sizes.get(size, 0) + 1
        categories[category] = categories.get(category, 0) + 1
        
        report.append(f'GARMENT {i}: {g["brand_name"]} - {g["product_name"]}')
        report.append(f'  Size: {g["size_label"]} ({g["fit_type"]} fit)')
        report.append(f'  Category: {g["category"]} > {g["subcategory"]}')
        
        # Measurements with averages
        measurements = {}
        if g['chest_min'] and g['chest_max']:
            chest_avg = (float(g['chest_min']) + float(g['chest_max'])) / 2
            measurements['chest'] = f'{g["chest_min"]}"-{g["chest_max"]}" (avg: {chest_avg:.1f}")'
        if g['sleeve_min'] and g['sleeve_max']:
            sleeve_avg = (float(g['sleeve_min']) + float(g['sleeve_max'])) / 2
            measurements['sleeve'] = f'{g["sleeve_min"]}"-{g["sleeve_max"]}" (avg: {sleeve_avg:.1f}")'
        if g['neck_min'] and g['neck_max']:
            neck_avg = (float(g['neck_min']) + float(g['neck_max'])) / 2
            measurements['neck'] = f'{g["neck_min"]}"-{g["neck_max"]}" (avg: {neck_avg:.1f}")'
        if g['waist_min'] and g['waist_max']:
            waist_avg = (float(g['waist_min']) + float(g['waist_max'])) / 2
            measurements['waist'] = f'{g["waist_min"]}"-{g["waist_max"]}" (avg: {waist_avg:.1f}")'
        if g['center_back_length']:
            measurements['length'] = f'{g["center_back_length"]}"'
        
        if measurements:
            report.append('  Measurements:')
            for dim, measurement in measurements.items():
                report.append(f'    {dim.capitalize()}: {measurement}')
        
        # Get overall feedback from detailed feedback table
        overall_feedback = None
        for fb in profile['detailed_feedback'].get(g['garment_id'], []):
            if fb['dimension'] == 'overall':
                overall_feedback = fb['feedback_text']
                break
        report.append(f'  Overall Fit: {overall_feedback or "No feedback"}')
        report.append(f'  Added: {g["created_at"]}')
        report.append('')
    
    report.append('4. DETAILED FIT FEEDBACK BY DIMENSION')
    report.append('-' * 50)
    all_feedback = {}
    for garment_id, feedback_list in profile['detailed_feedback'].items():
        if feedback_list:
            garment_name = next((g['product_name'] for g in profile['garments'] if g['garment_id'] == garment_id), f'Garment {garment_id}')
            brand_name = next((g['brand_name'] for g in profile['garments'] if g['garment_id'] == garment_id), 'Unknown')
            
            report.append(f'{brand_name} - {garment_name}:')
            for fb in feedback_list:
                dimension = fb['dimension'].capitalize()
                feedback = fb['feedback_text']
                report.append(f'  {dimension}: {feedback}')
                
                # Track all feedback patterns
                if dimension not in all_feedback:
                    all_feedback[dimension] = {}
                if feedback not in all_feedback[dimension]:
                    all_feedback[dimension][feedback] = 0
                all_feedback[dimension][feedback] += 1
            report.append('')
    
    report.append('5. SHOPPING PATTERNS ANALYSIS')
    report.append('-' * 50)
    report.append('Brand Distribution:')
    for brand, count in sorted(brands.items(), key=lambda x: x[1], reverse=True):
        report.append(f'  {brand}: {count} garments')
    
    report.append('')
    report.append('Size Distribution:')  
    for size, count in sorted(sizes.items(), key=lambda x: x[1], reverse=True):
        report.append(f'  {size}: {count} garments')
    
    report.append('')
    report.append('Feedback Patterns:')
    for dimension, feedback_dict in all_feedback.items():
        report.append(f'  {dimension}:')
        for feedback, count in sorted(feedback_dict.items(), key=lambda x: x[1], reverse=True):
            report.append(f'    {feedback}: {count}x')
    
    report.append('')
    report.append('6. CURRENT FIT ZONES (FROM ALGORITHM)')
    report.append('-' * 50)
    
    # Calculate current fit zones using our algorithm
    try:
        from fit_zone_calculator import FitZoneCalculator
        
        # Prepare garment data for calculator
        garment_list = []
        for g in profile['garments']:
            if g['chest_min'] and g['chest_max']:
                chest_range = f'{g["chest_min"]}-{g["chest_max"]}' if g['chest_min'] != g['chest_max'] else str(g['chest_min'])
                
                # Get chest feedback
                chest_feedback = None
                for fb in profile['detailed_feedback'].get(g['garment_id'], []):
                    if fb['dimension'] == 'chest':
                        chest_feedback = fb['feedback_text']
                        break
                
                garment_dict = {
                    'brand': g['brand_name'],
                    'garment_name': g['product_name'], 
                    'chest_range': chest_range,
                    'size': g['size_label'],
                    'fit_feedback': g['overall_fit_feedback'],
                    'chest_feedback': chest_feedback
                }
                garment_list.append(garment_dict)
        
        if garment_list:
            calculator = FitZoneCalculator('1')
            zones = calculator.calculate_chest_fit_zone(garment_list)
            
            report.append('Calculated Fit Zones for Chest:')
            for zone_name, zone_data in zones.items():
                if zone_data['min'] is not None and zone_data['max'] is not None:
                    range_size = zone_data['max'] - zone_data['min'] 
                    report.append(f'  {zone_name.capitalize()}: {zone_data["min"]:g}"-{zone_data["max"]:g}" (range: {range_size:g}")')
    except Exception as e:
        report.append(f'Error calculating fit zones: {str(e)}')
    
    report.append('')
    report.append('7. RECENT USER ACTIONS')
    report.append('-' * 50)
    for action in profile['recent_actions'][:10]:
        undo_status = " (UNDONE)" if action.get('is_undone') else ""
        target_info = f" (ID: {action['target_id']})" if action.get('target_id') else ""
        report.append(f'{action["created_at"]}: {action["action_type"]} on {action["target_table"]}{target_info}{undo_status}')
    
    report.append('')
    report.append('8. KEY INSIGHTS & QUESTIONS FOR AI ANALYSIS')
    report.append('-' * 50)
    report.append('Based on this data, please analyze:')
    report.append('')
    report.append('A. FIT PREDICTION OPPORTUNITIES:')
    report.append('- How can we better predict this user\'s fit preferences across dimensions?')
    report.append('- What patterns exist in their brand/size relationships?')
    report.append('- Which measurements are most critical for this user\'s fit satisfaction?')
    report.append('')
    report.append('B. SHOPPING EXPERIENCE IMPROVEMENTS:')
    report.append('- How can we reduce sizing anxiety for this user?')
    report.append('- What specific guidance would be most valuable when they shop?')
    report.append('- How can we leverage their existing garment data for new purchases?')
    report.append('')
    report.append('C. DATA GAPS & COLLECTION STRATEGIES:')
    report.append('- What additional data would most improve fit predictions?')
    report.append('- How can we collect more useful feedback without user friction?')
    report.append('- What missing dimensions/measurements would be most valuable?')
    report.append('')
    report.append('D. PERSONALIZATION OPPORTUNITIES:')
    report.append('- How can we create a personalized shopping experience for this user?')
    report.append('- What are their implicit preferences we can infer from the data?')
    report.append('- How can we anticipate their needs based on current patterns?')
    report.append('')
    report.append('=== END OF USER1 DATA PROFILE ===')
    
    return '\n'.join(report)

if __name__ == '__main__':
    try:
        report = generate_report()
        print(report)
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        import traceback
        traceback.print_exc() 