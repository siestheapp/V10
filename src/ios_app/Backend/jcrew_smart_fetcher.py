#!/usr/bin/env python3
"""
Smart J.Crew Product Fetcher
Captures high-value data for AI insights without excess hoarding
Focus: User preference learning, not marketing fluff
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import psycopg2
from typing import Dict, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

class SmartJCrewFetcher:
    """
    Captures ONLY high-value data for AI insights:
    - What affects fit preferences
    - What impacts purchase decisions  
    - What helps predict user satisfaction
    
    SKIPS low-value data:
    - Marketing badges ("best seller")
    - View counts ("26 people looked")
    - Store availability
    """
    
    def __init__(self):
        self.brand_id = 4  # J.Crew
        self.setup_driver()
    
    def setup_driver(self):
        """Setup headless Chrome"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def fetch_smart_data(self, url: str) -> Dict:
        """
        Fetch only HIGH-VALUE data for AI insights
        """
        print(f"🔍 Fetching smart data from: {url}")
        
        try:
            self.driver.get(url)
            time.sleep(2)  # Let page load
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Extract product code from URL
            product_code = self._extract_product_code(url)
            
            # HIGH-VALUE DATA for AI
            smart_data = {
                'product_code': product_code,
                'base_name': self._extract_name(soup),
                
                # 1. RATINGS & REVIEWS (affects purchase decisions)
                'ratings': self._extract_ratings(soup),
                
                # 2. DETAILED MATERIALS (for preference learning)
                'materials': self._extract_rich_materials(soup),
                
                # 3. FIT FEEDBACK (critical for size prediction)
                'fit_feedback': self._extract_fit_feedback(soup),
                
                # 4. PRICING (for value perception)
                'pricing': self._extract_pricing(soup),
                
                # 5. FABRIC TECHNOLOGY (affects comfort)
                'fabric_tech': self._extract_fabric_tech(soup),
                
                # 6. FIT OPTIONS & DESCRIPTIONS
                'fit_details': self._extract_fit_details(soup),
                
                # 7. CARE REQUIREMENTS (dealbreaker for some)
                'care_instructions': self._extract_detailed_care(soup),
                
                # 8. CONSTRUCTION (quality indicators)
                'construction': self._extract_construction(soup),
                
                # SKIP: Marketing fluff, social proof, store availability
            }
            
            return smart_data
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None
    
    def _extract_product_code(self, url: str) -> str:
        """Extract product code from URL"""
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$|/)', url)
        return match.group(1) if match else ""
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name"""
        name_elem = soup.select_one('h1.product__name, h1[data-qaid="pdpProductName"]')
        return name_elem.text.strip() if name_elem else ""
    
    def _extract_ratings(self, soup: BeautifulSoup) -> Dict:
        """
        Extract ratings and review data
        HIGH VALUE: Indicates product satisfaction
        """
        ratings = {
            'average_rating': None,
            'review_count': 0,
            'fit_consensus': None,  # "true to size", "runs small", etc.
            'quality_score': None
        }
        
        # Look for rating score
        rating_elem = soup.select_one('[data-qaid*="rating"], .product-rating')
        if rating_elem:
            rating_text = rating_elem.text
            # Extract rating like "4.7"
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                ratings['average_rating'] = float(rating_match.group(1))
        
        # Extract review count
        review_elem = soup.select_one('[data-qaid*="review"], .review-count')
        if review_elem:
            review_match = re.search(r'(\d+)\s*review', review_elem.text, re.IGNORECASE)
            if review_match:
                ratings['review_count'] = int(review_match.group(1))
        
        # Extract fit consensus
        fit_elem = soup.select_one('.fit-feedback, [data-qaid*="fit"]')
        if fit_elem and 'true to size' in fit_elem.text.lower():
            ratings['fit_consensus'] = 'true_to_size'
        elif fit_elem and 'runs small' in fit_elem.text.lower():
            ratings['fit_consensus'] = 'runs_small'
        elif fit_elem and 'runs large' in fit_elem.text.lower():
            ratings['fit_consensus'] = 'runs_large'
        
        return ratings
    
    def _extract_rich_materials(self, soup: BeautifulSoup) -> Dict:
        """
        Extract detailed material information
        HIGH VALUE: Critical for comfort preferences
        """
        materials = {
            'composition': {},
            'fabric_quality': {},  # "100s two-ply", etc.
            'fabric_weight': None,
            'stretch_content': 0,
            'special_treatments': []  # "Secret Wash", "garment-dyed", etc.
        }
        
        # Get product details text
        details = soup.get_text()
        
        # Extract fabric composition
        comp_patterns = [
            r'(\d+)%\s+cotton',
            r'(\d+)%\s+polyester',
            r'(\d+)%\s+linen',
            r'(\d+)%\s+wool',
            r'(\d+)%\s+elastane',
            r'(\d+)%\s+spandex'
        ]
        
        for pattern in comp_patterns:
            match = re.search(pattern, details, re.IGNORECASE)
            if match:
                material = pattern.split()[-1]
                materials['composition'][material] = int(match.group(1))
                
                # Track stretch content
                if material in ['elastane', 'spandex']:
                    materials['stretch_content'] += int(match.group(1))
        
        # Extract fabric quality details
        if '100s' in details:
            materials['fabric_quality']['yarn_count'] = '100s'
        if 'two-ply' in details or '2-ply' in details:
            materials['fabric_quality']['ply'] = '2-ply'
        if 'organic' in details.lower():
            materials['fabric_quality']['organic'] = True
        
        # Extract special treatments
        treatments = ['Secret Wash', 'garment-dyed', 'pre-washed', 'mercerized', 'brushed']
        for treatment in treatments:
            if treatment.lower() in details.lower():
                materials['special_treatments'].append(treatment)
        
        return materials
    
    def _extract_fit_feedback(self, soup: BeautifulSoup) -> Dict:
        """
        Extract fit feedback from reviews
        HIGH VALUE: Critical for size prediction
        """
        fit_feedback = {
            'consensus': None,  # "true to size", "runs small", etc.
            'recommended_sizing': None,
            'model_info': None,
            'customer_feedback_summary': []
        }
        
        # Look for fit consensus
        fit_text = soup.get_text()
        if 'fits true to size' in fit_text.lower():
            fit_feedback['consensus'] = 'true_to_size'
        elif 'runs small' in fit_text.lower():
            fit_feedback['consensus'] = 'runs_small'
        elif 'runs large' in fit_text.lower():
            fit_feedback['consensus'] = 'runs_large'
        
        # Extract model info
        model_match = re.search(r"model is ([\d'\"]+)\s+wearing size (\w+)", fit_text, re.IGNORECASE)
        if model_match:
            fit_feedback['model_info'] = {
                'height': model_match.group(1),
                'wearing_size': model_match.group(2)
            }
        
        return fit_feedback
    
    def _extract_pricing(self, soup: BeautifulSoup) -> Dict:
        """
        Extract pricing information
        HIGH VALUE: Affects value perception
        """
        pricing = {
            'original_price': None,
            'sale_price': None,
            'discount_percent': None,
            'promo_code': None
        }
        
        # Extract original price
        price_elem = soup.select_one('.product__price, [data-qaid*="price"]')
        if price_elem:
            price_match = re.search(r'\$(\d+\.?\d*)', price_elem.text)
            if price_match:
                pricing['original_price'] = float(price_match.group(1))
        
        # Look for sale info
        sale_text = soup.get_text()
        discount_match = re.search(r'(\d+)%\s+off', sale_text)
        if discount_match:
            pricing['discount_percent'] = int(discount_match.group(1))
            
        # Extract promo code
        code_match = re.search(r'code\s+([A-Z]+)', sale_text)
        if code_match:
            pricing['promo_code'] = code_match.group(1)
        
        return pricing
    
    def _extract_fabric_tech(self, soup: BeautifulSoup) -> list:
        """
        Extract fabric technology features
        HIGH VALUE: Affects comfort and performance
        """
        tech_features = []
        
        details = soup.get_text().lower()
        
        # Technology keywords that matter for comfort
        tech_keywords = {
            'moisture-wicking': 'Moisture-wicking',
            'breathable': 'Breathable',
            'stretch': 'Stretch technology',
            'quick-dry': 'Quick-dry',
            'wrinkle-resistant': 'Wrinkle-resistant',
            'stain-resistant': 'Stain-resistant',
            'temperature-regulating': 'Temperature-regulating',
            'anti-odor': 'Anti-odor',
            'uv protection': 'UV protection'
        }
        
        for keyword, feature in tech_keywords.items():
            if keyword in details:
                tech_features.append(feature)
        
        return tech_features
    
    def _extract_fit_details(self, soup: BeautifulSoup) -> Dict:
        """
        Extract all fit options and descriptions
        HIGH VALUE: Essential for fit preference learning
        """
        fit_details = {
            'available_fits': [],
            'fit_descriptions': {},
            'current_fit': None
        }
        
        # Extract available fits
        fit_options = soup.select('.fit-option, [data-qaid*="fitOption"]')
        for option in fit_options:
            fit_name = option.text.strip()
            if fit_name:
                fit_details['available_fits'].append(fit_name)
        
        # Common J.Crew fits
        standard_fits = ['Classic', 'Slim', 'Slim Untucked', 'Tall', 'Relaxed']
        for fit in standard_fits:
            if fit.lower() in soup.get_text().lower():
                if fit not in fit_details['available_fits']:
                    fit_details['available_fits'].append(fit)
        
        # Extract fit descriptions
        if 'Classic' in fit_details['available_fits']:
            fit_details['fit_descriptions']['Classic'] = 'Time-tested fit for range of body types'
        if 'Slim' in fit_details['available_fits']:
            fit_details['fit_descriptions']['Slim'] = 'Trim through chest and body'
        if 'Relaxed' in fit_details['available_fits']:
            fit_details['fit_descriptions']['Relaxed'] = 'Roomiest fit through chest and body'
        
        return fit_details
    
    def _extract_detailed_care(self, soup: BeautifulSoup) -> list:
        """
        Extract detailed care instructions
        HIGH VALUE: Dealbreaker for many users
        """
        care = []
        
        details = soup.get_text().lower()
        
        # Primary care instruction
        if 'machine wash' in details:
            care.append('Machine wash cold')
        elif 'hand wash' in details:
            care.append('Hand wash cold')
        elif 'dry clean' in details:
            care.append('Dry clean only')
        
        # Additional care details
        if 'tumble dry' in details:
            care.append('Tumble dry low')
        if 'line dry' in details:
            care.append('Line dry')
        if 'no bleach' in details or 'non-chlorine bleach' in details:
            care.append('Non-chlorine bleach when needed')
        if 'iron' in details:
            if 'low' in details:
                care.append('Cool iron if needed')
            else:
                care.append('Warm iron if needed')
        
        return care
    
    def _extract_construction(self, soup: BeautifulSoup) -> Dict:
        """
        Extract construction details
        HIGH VALUE: Quality indicators
        """
        construction = {
            'collar_type': None,
            'cuff_type': None,
            'placket_type': None,
            'hem_type': None
        }
        
        details = soup.get_text().lower()
        
        # Collar type
        if 'point collar' in details:
            construction['collar_type'] = 'Point collar'
        elif 'button-down' in details:
            construction['collar_type'] = 'Button-down collar'
        elif 'spread collar' in details:
            construction['collar_type'] = 'Spread collar'
        
        # Hem type
        if 'rounded hem' in details:
            construction['hem_type'] = 'Rounded hem'
        elif 'straight hem' in details:
            construction['hem_type'] = 'Straight hem'
        
        return construction
    
    def save_smart_data(self, data: Dict) -> bool:
        """
        Save smart data to enhanced structure
        """
        if not data:
            return False
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Update product_master with smart data
            cur.execute("""
                UPDATE product_master SET
                    materials = materials || %s::jsonb,
                    product_ratings = %s,
                    fit_feedback = %s,
                    pricing_data = %s,
                    fabric_technology = %s,
                    fit_information = fit_information || %s::jsonb,
                    care_instructions = %s,
                    construction_details = construction_details || %s::jsonb,
                    updated_at = NOW(),
                    last_scraped = NOW()
                WHERE brand_id = %s AND product_code = %s
            """, (
                json.dumps(data['materials']),
                json.dumps(data['ratings']),
                json.dumps(data['fit_feedback']),
                json.dumps(data['pricing']),
                data['fabric_tech'],
                json.dumps(data['fit_details']),
                data['care_instructions'],
                json.dumps(data['construction']),
                self.brand_id,
                data['product_code']
            ))
            
            if cur.rowcount == 0:
                # Product doesn't exist, create it
                cur.execute("""
                    INSERT INTO product_master (
                        brand_id, product_code, base_name,
                        materials, product_ratings, fit_feedback,
                        pricing_data, fabric_technology, fit_information,
                        care_instructions, construction_details,
                        created_at, last_scraped
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                """, (
                    self.brand_id,
                    data['product_code'],
                    data['base_name'],
                    json.dumps(data['materials']),
                    json.dumps(data['ratings']),
                    json.dumps(data['fit_feedback']),
                    json.dumps(data['pricing']),
                    data['fabric_tech'],
                    json.dumps(data['fit_details']),
                    data['care_instructions'],
                    json.dumps(data['construction'])
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Saved smart data for {data['product_code']}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving: {str(e)}")
            return False
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'driver'):
            self.driver.quit()


# Example usage
if __name__ == "__main__":
    fetcher = SmartJCrewFetcher()
    
    # Test with the URL you provided
    test_url = "https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783"
    
    print("🚀 SMART DATA FETCHING DEMO")
    print("=" * 60)
    
    data = fetcher.fetch_smart_data(test_url)
    
    if data:
        print("\n📊 HIGH-VALUE DATA CAPTURED:")
        print("-" * 40)
        
        print(f"\n1️⃣ RATINGS (Purchase Decision):")
        print(f"   • Average: {data['ratings']['average_rating']}")
        print(f"   • Reviews: {data['ratings']['review_count']}")
        print(f"   • Fit: {data['ratings']['fit_consensus']}")
        
        print(f"\n2️⃣ MATERIALS (Comfort Preference):")
        print(f"   • Composition: {data['materials']['composition']}")
        print(f"   • Quality: {data['materials']['fabric_quality']}")
        print(f"   • Treatments: {data['materials']['special_treatments']}")
        
        print(f"\n3️⃣ FIT FEEDBACK (Size Prediction):")
        print(f"   • Consensus: {data['fit_feedback']['consensus']}")
        print(f"   • Model: {data['fit_feedback']['model_info']}")
        
        print(f"\n4️⃣ PRICING (Value Perception):")
        print(f"   • Original: ${data['pricing']['original_price']}")
        print(f"   • Discount: {data['pricing']['discount_percent']}%")
        
        print(f"\n5️⃣ FABRIC TECH (Performance):")
        for tech in data['fabric_tech'][:3]:
            print(f"   • {tech}")
        
        print("\n\n❌ DATA WE INTENTIONALLY SKIP:")
        print("-" * 40)
        print("• 'Best seller' badge (marketing fluff)")
        print("• '26 people viewed' (FOMO tactic)")
        print("• Store availability (not relevant)")
        print("• Monogram options (edge case)")
        
        print("\n✅ WHY THIS IS SMART:")
        print("Every data point directly helps AI:")
        print("• Learn user preferences")
        print("• Predict fit satisfaction")
        print("• Recommend similar products")
        print("• Avoid dealbreakers")
    
    fetcher.__del__()

