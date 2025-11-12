#!/usr/bin/env python3
"""
Scrape the chambray/denim shirts batch
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.jcrew_smart_scraper import SmartJCrewScraper

# Load chambray URLs
with open('jcrew_chambray_urls.txt', 'r') as f:
    urls = [line.strip() for line in f if line.strip()]

print('🚀 Scraping J.Crew Chambray & Denim Shirts')
print('=' * 80)

# Create scraper and process
scraper = SmartJCrewScraper()
results = scraper.scrape_batch(urls)

print('\n' + '=' * 80)
if results:
    print(f'✅ Successfully scraped {len(results)} new products!')
else:
    print('⚠️ No new products scraped (may be due to 403 errors)')

