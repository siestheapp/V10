#!/usr/bin/env python3
"""
Enrich existing J.Crew products with comprehensive data
This script fetches detailed product information for all J.Crew products
already in the database and updates them with rich data for AI analysis
"""

import psycopg2
import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

class JCrewProductEnricher:
    """Enriches J.Crew products with comprehensive data using Selenium"""
    
    def __init__(self):
        self.brand_id = 4  # J.Crew
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def get_products_to_enrich(self):
        """Get list of J.Crew products that need enrichment"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get products that lack comprehensive data
        cur.execute("""
            SELECT DISTINCT 
                pm.id,
                pm.product_code,
                pm.base_name,
                COALESCE(jpc.product_url, pv.variant_url) as url
            FROM product_master pm
            LEFT JOIN product_variants pv ON pm.id = pv.product_master_id
            LEFT JOIN jcrew_product_cache jpc ON pm.product_code = jpc.product_code
            WHERE pm.brand_id = %s
            AND (
                pm.construction_details IS NULL 
                OR pm.construction_details = '{}'
                OR pm.technical_features IS NULL
                OR ARRAY_LENGTH(pm.care_instructions, 1) < 3
            )
            AND (jpc.product_url IS NOT NULL OR pv.variant_url IS NOT NULL)
            ORDER BY pm.id
            LIMIT 10
        """, (self.brand_id,))
        
        products = cur.fetchall()
        cur.close()
        conn.close()
        
        return products
    
    def extract_comprehensive_data(self, url):
        """Extract comprehensive product data using Selenium"""
        try:
            print(f"   📥 Loading {url}...")
            self.driver.get(url)
            time.sleep(3)  # Wait for page to load
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract all the comprehensive data
            data = {
                'materials': self._extract_materials(soup),
                'care_instructions': self._extract_care(soup),
                'construction_details': self._extract_construction(soup),
                'technical_features': self._extract_features(soup),
                'sustainability': self._extract_sustainability(soup),
                'product_details': self._extract_details(soup),
                'fit_information': self._extract_fit_info(soup),
                'styling_notes': self._extract_styling(soup),
                'description_texts': self._extract_descriptions(soup)
            }
            
            return data
            
        except Exception as e:
            print(f"   ❌ Error extracting data: {str(e)}")
            return None
    
    def _extract_materials(self, soup):
        """Extract material information"""
        materials = {
            'primary_fabric': '',
            'composition': {},
            'fabric_weight': '',
            'fabric_features': [],
            'weave_type': '',
            'origin': ''
        }
        
        # Look for product details
        details_text = soup.get_text().lower()
        
        # Extract fabric composition
        comp_patterns = [
            r'(\d+)%\s+cotton',
            r'(\d+)%\s+polyester',
            r'(\d+)%\s+linen',
            r'(\d+)%\s+wool',
            r'(\d+)%\s+modal',
            r'(\d+)%\s+elastane',
            r'(\d+)%\s+spandex'
        ]
        
        for pattern in comp_patterns:
            match = re.search(pattern, details_text)
            if match:
                fabric = pattern.split()[-1]
                materials['composition'][fabric] = int(match.group(1))
        
        # Determine primary fabric
        if materials['composition']:
            primary = max(materials['composition'].items(), key=lambda x: x[1])
            materials['primary_fabric'] = primary[0].capitalize()
        
        # Extract fabric features
        features = {
            'stretch': 'Stretch',
            'breathable': 'Breathable',
            'moisture-wicking': 'Moisture-wicking',
            'wrinkle-resistant': 'Wrinkle-resistant',
            'pre-washed': 'Pre-washed',
            'garment-dyed': 'Garment-dyed',
            'quick-dry': 'Quick-dry'
        }
        
        for keyword, feature in features.items():
            if keyword in details_text:
                materials['fabric_features'].append(feature)
        
        # Fabric weight
        if 'lightweight' in details_text:
            materials['fabric_weight'] = 'Lightweight'
        elif 'midweight' in details_text:
            materials['fabric_weight'] = 'Midweight'
        elif 'heavyweight' in details_text:
            materials['fabric_weight'] = 'Heavyweight'
        
        # Weave type
        weaves = ['poplin', 'oxford', 'twill', 'chambray', 'flannel', 'jersey', 'pique']
        for weave in weaves:
            if weave in details_text:
                materials['weave_type'] = weave.capitalize()
                break
        
        # Origin
        if 'imported' in details_text:
            materials['origin'] = 'Imported'
        
        return materials
    
    def _extract_care(self, soup):
        """Extract care instructions"""
        care = []
        
        # Common care instructions to look for
        care_keywords = [
            'machine wash',
            'hand wash',
            'dry clean',
            'tumble dry',
            'line dry',
            'iron',
            'bleach',
            'wash separately'
        ]
        
        details_text = soup.get_text().lower()
        
        for keyword in care_keywords:
            if keyword in details_text:
                # Extract the full care instruction
                pattern = f'{keyword}[^.]*'
                match = re.search(pattern, details_text)
                if match:
                    instruction = match.group().strip().capitalize()
                    if instruction not in care:
                        care.append(instruction)
        
        # Default care for common fabrics if none found
        if not care:
            if 'cotton' in details_text:
                care = ['Machine wash cold', 'Tumble dry low', 'Warm iron if needed']
            elif 'linen' in details_text:
                care = ['Machine wash cold', 'Line dry', 'Iron while damp']
            elif 'wool' in details_text:
                care = ['Dry clean recommended', 'Or hand wash cold', 'Lay flat to dry']
        
        return care[:5]  # Limit to 5 instructions
    
    def _extract_construction(self, soup):
        """Extract construction details"""
        construction = {
            'collar_type': '',
            'cuff_type': '',
            'pocket_details': [],
            'hem_type': '',
            'back_details': '',
            'stitching': [],
            'closures': []
        }
        
        details_text = soup.get_text().lower()
        
        # Collar types
        collars = {
            'button-down': 'Button-down collar',
            'spread collar': 'Spread collar',
            'point collar': 'Point collar',
            'camp collar': 'Camp collar',
            'band collar': 'Band collar'
        }
        
        for pattern, collar in collars.items():
            if pattern in details_text:
                construction['collar_type'] = collar
                break
        
        # Pockets
        if 'chest pocket' in details_text:
            construction['pocket_details'].append('Chest pocket')
        if 'patch pocket' in details_text:
            construction['pocket_details'].append('Patch pocket')
        if 'side pocket' in details_text:
            construction['pocket_details'].append('Side pockets')
        
        # Hem
        if 'rounded hem' in details_text:
            construction['hem_type'] = 'Rounded hem'
        elif 'straight hem' in details_text:
            construction['hem_type'] = 'Straight hem'
        
        # Back details
        if 'box pleat' in details_text:
            construction['back_details'] = 'Box pleat'
        elif 'yoke' in details_text:
            construction['back_details'] = 'Back yoke'
        
        # Closures
        if 'button' in details_text:
            construction['closures'].append('Buttons')
        if 'zipper' in details_text or 'zip' in details_text:
            construction['closures'].append('Zipper')
        
        return construction
    
    def _extract_features(self, soup):
        """Extract technical features"""
        features = []
        details_text = soup.get_text().lower()
        
        tech_features = {
            'moisture-wicking': 'Moisture-wicking technology',
            'four-way stretch': 'Four-way stretch',
            'upf': 'UPF sun protection',
            'water-repellent': 'Water-repellent finish',
            'quick-dry': 'Quick-dry fabric',
            'breathable': 'Enhanced breathability'
        }
        
        for keyword, feature in tech_features.items():
            if keyword in details_text:
                features.append(feature)
        
        return features[:5]  # Limit to 5 features
    
    def _extract_sustainability(self, soup):
        """Extract sustainability information"""
        sustainability = {
            'certifications': [],
            'sustainable_materials': [],
            'recycled_content': 0
        }
        
        details_text = soup.get_text().lower()
        
        # Check for certifications
        if 'organic' in details_text:
            sustainability['sustainable_materials'].append('Organic materials')
        if 'bci' in details_text or 'better cotton' in details_text:
            sustainability['certifications'].append('Better Cotton Initiative')
        if 'recycled' in details_text:
            sustainability['sustainable_materials'].append('Recycled materials')
        if 'sustainable' in details_text:
            sustainability['sustainable_materials'].append('Sustainable production')
        
        # Check for recycled percentage
        recycled_match = re.search(r'(\d+)%\s*recycled', details_text)
        if recycled_match:
            sustainability['recycled_content'] = int(recycled_match.group(1))
        
        return sustainability
    
    def _extract_details(self, soup):
        """Extract product detail bullet points"""
        details = []
        
        # Look for list items that contain product details
        detail_items = soup.select('li')
        
        for item in detail_items[:20]:  # Limit to first 20 items
            text = item.get_text().strip()
            if len(text) > 10 and len(text) < 200:  # Reasonable length for a detail
                if text not in details:
                    details.append(text)
        
        return details[:10]  # Return top 10 details
    
    def _extract_fit_info(self, soup):
        """Extract fit information"""
        fit_info = {
            'fit_type': '',
            'fit_description': '',
            'how_it_fits': []
        }
        
        details_text = soup.get_text()
        
        # Look for fit types
        fits = ['Classic', 'Slim', 'Relaxed', 'Regular', 'Tailored']
        for fit in fits:
            if fit in details_text:
                fit_info['fit_type'] = fit
                break
        
        # Look for fit descriptions
        if 'relaxed through' in details_text.lower():
            fit_info['how_it_fits'].append('Relaxed through chest and body')
        if 'trim through' in details_text.lower():
            fit_info['how_it_fits'].append('Trim through chest and body')
        if 'room to move' in details_text.lower():
            fit_info['how_it_fits'].append('Room to move')
        
        return fit_info
    
    def _extract_styling(self, soup):
        """Extract styling suggestions"""
        styling = []
        details_text = soup.get_text().lower()
        
        # Look for styling keywords
        patterns = [
            r'pair with [^.]+',
            r'looks great with [^.]+',
            r'perfect for [^.]+',
            r'wear with [^.]+'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, details_text)
            for match in matches[:3]:  # Limit to 3 matches per pattern
                clean = match.strip().capitalize()
                if clean not in styling:
                    styling.append(clean)
        
        return styling[:5]  # Return top 5 styling notes
    
    def _extract_descriptions(self, soup):
        """Extract product descriptions"""
        descriptions = []
        
        # Look for paragraph text
        paragraphs = soup.select('p')
        
        for p in paragraphs[:10]:
            text = p.get_text().strip()
            if len(text) > 50 and len(text) < 500:  # Reasonable description length
                if text not in descriptions:
                    descriptions.append(text)
        
        return descriptions[:3]  # Return top 3 descriptions
    
    def update_product(self, product_id, data):
        """Update product in database with enriched data"""
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            cur.execute("""
                UPDATE product_master SET
                    materials = %s,
                    care_instructions = %s,
                    construction_details = %s,
                    technical_features = %s,
                    sustainability = %s,
                    product_details = %s,
                    fit_information = %s,
                    styling_notes = %s,
                    description_texts = %s,
                    updated_at = NOW(),
                    last_scraped = NOW()
                WHERE id = %s
            """, (
                json.dumps(data['materials']) if data['materials'] else '{}',
                data['care_instructions'] if data['care_instructions'] else [],
                json.dumps(data['construction_details']) if data['construction_details'] else '{}',
                data['technical_features'] if data['technical_features'] else [],
                json.dumps(data['sustainability']) if data['sustainability'] else '{}',
                data['product_details'] if data['product_details'] else [],
                json.dumps(data['fit_information']) if data['fit_information'] else '{}',
                data['styling_notes'] if data['styling_notes'] else [],
                data['description_texts'] if data['description_texts'] else [],
                product_id
            ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Database error: {str(e)}")
            return False
    
    def enrich_all_products(self):
        """Main method to enrich all products"""
        print("\n🚀 J.CREW PRODUCT ENRICHMENT")
        print("=" * 60)
        
        products = self.get_products_to_enrich()
        
        if not products:
            print("✅ All products already have comprehensive data!")
            return
        
        print(f"📦 Found {len(products)} products to enrich\n")
        
        success_count = 0
        
        for i, (product_id, code, name, url) in enumerate(products, 1):
            print(f"{i}. {code}: {name[:40]}...")
            
            if not url:
                print("   ⚠️  No URL available")
                continue
            
            # Extract comprehensive data
            data = self.extract_comprehensive_data(url)
            
            if data:
                # Update database
                if self.update_product(product_id, data):
                    print(f"   ✅ Enriched with {len(data['materials']['composition'])} materials, "
                          f"{len(data['care_instructions'])} care instructions, "
                          f"{len(data['technical_features'])} features")
                    success_count += 1
                else:
                    print("   ❌ Failed to update database")
            else:
                print("   ❌ Failed to extract data")
            
            # Be respectful with rate limiting
            time.sleep(2)
        
        print(f"\n✅ Successfully enriched {success_count}/{len(products)} products!")
        
        # Show summary
        self.show_enrichment_summary()
        
        # Cleanup
        self.driver.quit()
    
    def show_enrichment_summary(self):
        """Show summary of enriched data"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE materials != '{}') as with_materials,
                COUNT(*) FILTER (WHERE ARRAY_LENGTH(care_instructions, 1) > 0) as with_care,
                COUNT(*) FILTER (WHERE construction_details != '{}') as with_construction,
                COUNT(*) FILTER (WHERE ARRAY_LENGTH(technical_features, 1) > 0) as with_features
            FROM product_master
            WHERE brand_id = %s
        """, (self.brand_id,))
        
        total, materials, care, construction, features = cur.fetchone()
        
        print("\n📊 ENRICHMENT SUMMARY")
        print("=" * 60)
        print(f"Total J.Crew products: {total}")
        print(f"  • With material data: {materials} ({materials*100//total}%)")
        print(f"  • With care instructions: {care} ({care*100//total}%)")
        print(f"  • With construction details: {construction} ({construction*100//total}%)")
        print(f"  • With technical features: {features} ({features*100//total}%)")
        
        cur.close()
        conn.close()


if __name__ == "__main__":
    enricher = JCrewProductEnricher()
    enricher.enrich_all_products()

