#!/usr/bin/env python3
"""
Update database with accurate scraped data from category scraper
Overwrites faulty listings with correct information
"""

import json
import psycopg2
from datetime import datetime

def update_database_from_scrape(json_file):
    """Update database with scraped results"""
    
    # Load scraped data
    with open(json_file, 'r') as f:
        scraped_data = json.load(f)
    
    # Database connection
    DB_CONFIG = {
        'database': 'postgres',
        'user': 'fs_core_rw',
        'password': 'CHANGE_ME',
        'host': 'aws-1-us-east-1.pooler.supabase.com',
        'port': '5432'
    }
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    print('='*80)
    print('📝 UPDATING DATABASE WITH ACCURATE SCRAPED DATA')
    print('='*80)
    print(f'Source: {json_file}')
    print(f'Products to update: {len(scraped_data["products"])}\n')
    
    updated_count = 0
    
    for product in scraped_data['products']:
        code = product['product_code']
        scraped_colors = product['colors']
        scraped_fits = product['fits']
        
        # Get current database values
        cur.execute('''
            SELECT product_name, colors_available, fit_options 
            FROM jcrew_product_cache 
            WHERE product_code = %s
        ''', (code,))
        
        result = cur.fetchone()
        
        if result:
            db_name, old_colors, old_fits = result
            
            # Convert colors to title case for database
            title_case_colors = []
            for color in scraped_colors:
                # Handle multi-word colors properly
                words = color.split()
                title_words = []
                for word in words:
                    # Keep acronyms uppercase (e.g., USA, NYC)
                    if len(word) <= 3 and word.isupper():
                        title_words.append(word)
                    else:
                        title_words.append(word.title())
                title_case_colors.append(' '.join(title_words))
            
            print(f'📦 Updating {code}: {db_name[:50]}...')
            print(f'   Old colors: {len(old_colors) if old_colors else 0}')
            print(f'   New colors: {len(title_case_colors)} - {title_case_colors[:2]}...')
            print(f'   Old fits: {old_fits}')
            print(f'   New fits: {scraped_fits if scraped_fits else "(single-fit product)"}\n')
            
            # Update the database
            # Converting colors to title case and setting fit_options to empty array for single-fit products
            cur.execute('''
                UPDATE jcrew_product_cache 
                SET colors_available = %s,
                    fit_options = %s,
                    updated_at = %s
                WHERE product_code = %s
            ''', (
                title_case_colors,  # Array of color names in title case
                scraped_fits if scraped_fits else [],  # Empty array for single-fit
                datetime.now(),
                code
            ))
            
            updated_count += 1
        else:
            print(f'⚠️  {code} not found in database - skipping\n')
    
    # Commit changes
    conn.commit()
    
    print('='*80)
    print(f'✅ UPDATE COMPLETE')
    print(f'   Updated: {updated_count} products')
    print('='*80)
    
    # Verify the updates
    print('\n📊 VERIFICATION - Checking updated products:')
    print('-'*40)
    
    for product in scraped_data['products']:
        code = product['product_code']
        
        cur.execute('''
            SELECT colors_available, fit_options 
            FROM jcrew_product_cache 
            WHERE product_code = %s
        ''', (code,))
        
        result = cur.fetchone()
        if result:
            db_colors, db_fits = result
            scraped_colors = product['colors']
            scraped_fits = product['fits']
            
            # Convert scraped colors to title case for comparison
            title_case_colors = []
            for color in scraped_colors:
                words = color.split()
                title_words = []
                for word in words:
                    if len(word) <= 3 and word.isupper():
                        title_words.append(word)
                    else:
                        title_words.append(word.title())
                title_case_colors.append(' '.join(title_words))
            
            colors_match = set(db_colors or []) == set(title_case_colors)
            fits_match = (db_fits or []) == scraped_fits
            
            status = '✅' if colors_match and fits_match else '⚠️'
            print(f'{status} {code}:')
            print(f'   Colors: {len(db_colors)} ({"match" if colors_match else "MISMATCH"})')
            print(f'   Fits: {db_fits if db_fits else "[]"} ({"match" if fits_match else "MISMATCH"})')
    
    cur.close()
    conn.close()

if __name__ == '__main__':
    # Use the most recent complete scrape
    json_file = 'jcrew_category_scrape_20250916_162237.json'
    update_database_from_scrape(json_file)
