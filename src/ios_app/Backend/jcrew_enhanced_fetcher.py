#!/usr/bin/env python3
"""
Enhanced J.Crew Product Fetcher
Captures comprehensive product data for AI analysis including:
- Materials & composition
- Care instructions
- Construction details
- Technical features
- Sustainability info
- Complete descriptions
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import psycopg2
from typing import Dict, List, Optional
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "database": "postgres",
    "user": "fs_core_rw",
    "password": "CHANGE_ME",
    "host": "aws-1-us-east-1.pooler.supabase.com",
    "port": "5432"
}

class EnhancedJCrewFetcher:
    """Enhanced fetcher that captures ALL product details"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        self.brand_id = self._get_brand_id()
    
    def _get_brand_id(self) -> int:
        """Get J.Crew brand ID from database"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT id FROM brands WHERE name ILIKE '%j.crew%' LIMIT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result[0] if result else 4  # Default to 4
    
    def fetch_comprehensive_product(self, product_url: str) -> Dict:
        """
        Fetch comprehensive product data including all details for AI analysis
        """
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product code
            product_code = self._extract_product_code(product_url)
            
            # Initialize comprehensive data structure
            product_data = {
                'product_code': product_code,
                'base_name': self._extract_product_name(soup),
                'materials': self._extract_materials_comprehensive(soup),
                'care_instructions': self._extract_care_instructions(soup),
                'construction_details': self._extract_construction_details(soup),
                'technical_features': self._extract_technical_features(soup),
                'sustainability': self._extract_sustainability_info(soup),
                'product_details': self._extract_all_product_details(soup),
                'fit_information': self._extract_fit_details(soup),
                'styling_notes': self._extract_styling_notes(soup),
                'description_texts': self._extract_all_descriptions(soup),
                'measurements_guide': self._extract_measurements(soup),
                'variants': self._extract_all_variants(soup, product_url),
                'category': self._extract_category(soup),
                'metadata': {
                    'scraped_at': datetime.now().isoformat(),
                    'url': product_url
                }
            }
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error fetching {product_url}: {str(e)}")
            return None
    
    def _extract_product_code(self, url: str) -> str:
        """Extract product code from URL"""
        match = re.search(r'/([A-Z]{2}\d{3,4})(?:\?|$|/)', url)
        return match.group(1) if match else ""
    
    def _extract_product_name(self, soup: BeautifulSoup) -> str:
        """Extract product name"""
        selectors = [
            'h1.product-name',
            'h1[data-qaid="pdpProductName"]',
            'h1.product__name',
            'h1[itemprop="name"]',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    return element.get('content', '').strip()
                else:
                    return element.text.strip()
        return ""
    
    def _extract_materials_comprehensive(self, soup: BeautifulSoup) -> Dict:
        """Extract detailed material and fabric information"""
        materials = {
            'primary_fabric': '',
            'composition': {},
            'fabric_weight': '',
            'fabric_features': [],
            'weave_type': '',
            'thread_count': '',
            'lining': '',
            'origin': ''
        }
        
        # Look for product details section
        details_section = soup.select('.product-details__content li, .pdp-details li, .product-information li')
        details_text = ' '.join([elem.text for elem in details_section])
        
        # Extract fabric composition percentages
        percentages = re.findall(r'(\d+)%\s+([a-zA-Z]+)', details_text)
        for percent, material in percentages:
            materials['composition'][material.lower()] = int(percent)
        
        # Identify primary fabric
        fabric_types = ['cotton', 'linen', 'wool', 'polyester', 'silk', 'cashmere', 
                       'modal', 'tencel', 'rayon', 'nylon', 'spandex', 'elastane']
        for fabric in fabric_types:
            if fabric in details_text.lower():
                if not materials['primary_fabric']:
                    materials['primary_fabric'] = fabric.capitalize()
        
        # Extract fabric features
        feature_keywords = {
            'breathable': 'Breathable',
            'stretch': 'Stretch',
            'moisture-wicking': 'Moisture-wicking',
            'wrinkle-resistant': 'Wrinkle-resistant',
            'water-resistant': 'Water-resistant',
            'quick-dry': 'Quick-dry',
            'uv protection': 'UV Protection',
            'antimicrobial': 'Antimicrobial',
            'pre-washed': 'Pre-washed',
            'garment-dyed': 'Garment-dyed',
            'mercerized': 'Mercerized',
            'brushed': 'Brushed finish'
        }
        
        for keyword, feature in feature_keywords.items():
            if keyword in details_text.lower():
                materials['fabric_features'].append(feature)
        
        # Identify fabric weight
        if 'lightweight' in details_text.lower():
            materials['fabric_weight'] = 'Lightweight'
        elif 'midweight' in details_text.lower() or 'mid-weight' in details_text.lower():
            materials['fabric_weight'] = 'Midweight'
        elif 'heavyweight' in details_text.lower() or 'heavy-weight' in details_text.lower():
            materials['fabric_weight'] = 'Heavyweight'
        
        # Identify weave type
        weave_types = ['poplin', 'oxford', 'twill', 'chambray', 'flannel', 'corduroy', 
                      'jersey', 'pique', 'interlock', 'rib', 'waffle']
        for weave in weave_types:
            if weave in details_text.lower():
                materials['weave_type'] = weave.capitalize()
                break
        
        # Check origin
        if 'imported' in details_text.lower():
            materials['origin'] = 'Imported'
        elif 'made in' in details_text.lower():
            origin_match = re.search(r'made in ([a-zA-Z\s]+)', details_text, re.IGNORECASE)
            if origin_match:
                materials['origin'] = origin_match.group(1).strip()
        
        return materials
    
    def _extract_care_instructions(self, soup: BeautifulSoup) -> List[str]:
        """Extract care instructions"""
        care_instructions = []
        
        # Look for care section
        care_selectors = [
            '.care-instructions li',
            '.product-care li',
            '[data-qaid="careInstructions"] li'
        ]
        
        for selector in care_selectors:
            care_items = soup.select(selector)
            for item in care_items:
                instruction = item.text.strip()
                if instruction and instruction not in care_instructions:
                    care_instructions.append(instruction)
        
        # Also search in product details for care keywords
        details = soup.text.lower()
        care_patterns = [
            r'machine wash[^.]*',
            r'hand wash[^.]*',
            r'dry clean[^.]*',
            r'tumble dry[^.]*',
            r'line dry[^.]*',
            r'iron[^.]*',
            r'do not bleach',
            r'wash separately',
            r'wash inside out'
        ]
        
        for pattern in care_patterns:
            matches = re.findall(pattern, details, re.IGNORECASE)
            for match in matches:
                clean_instruction = match.strip().capitalize()
                if clean_instruction and clean_instruction not in care_instructions:
                    care_instructions.append(clean_instruction)
        
        # If no care instructions found, add defaults based on material
        if not care_instructions:
            if 'cotton' in soup.text.lower():
                care_instructions = [
                    'Machine wash cold',
                    'Tumble dry low',
                    'Warm iron if needed'
                ]
            elif 'linen' in soup.text.lower():
                care_instructions = [
                    'Machine wash cold',
                    'Line dry',
                    'Iron while damp'
                ]
        
        return care_instructions
    
    def _extract_construction_details(self, soup: BeautifulSoup) -> Dict:
        """Extract construction and design details"""
        construction = {
            'collar_type': '',
            'cuff_type': '',
            'placket_type': '',
            'pocket_details': [],
            'hem_type': '',
            'back_details': '',
            'stitching': [],
            'closures': [],
            'special_features': []
        }
        
        details_text = soup.text.lower()
        
        # Collar types
        collar_types = {
            'button-down': 'Button-down collar',
            'spread collar': 'Spread collar',
            'point collar': 'Point collar',
            'camp collar': 'Camp collar',
            'band collar': 'Band collar',
            'cutaway collar': 'Cutaway collar'
        }
        
        for pattern, collar in collar_types.items():
            if pattern in details_text:
                construction['collar_type'] = collar
                break
        
        # Cuff types
        if 'button cuff' in details_text or 'buttoned cuff' in details_text:
            construction['cuff_type'] = 'Button cuff'
        elif 'french cuff' in details_text:
            construction['cuff_type'] = 'French cuff'
        elif 'adjustable cuff' in details_text:
            construction['cuff_type'] = 'Adjustable cuff'
        
        # Pocket details
        pocket_patterns = [
            'patch pocket', 'chest pocket', 'side pocket', 
            'welt pocket', 'flap pocket', 'zip pocket'
        ]
        for pocket in pocket_patterns:
            if pocket in details_text:
                construction['pocket_details'].append(pocket.capitalize())
        
        # Hem type
        if 'rounded hem' in details_text:
            construction['hem_type'] = 'Rounded hem'
        elif 'straight hem' in details_text:
            construction['hem_type'] = 'Straight hem'
        elif 'curved hem' in details_text:
            construction['hem_type'] = 'Curved hem'
        
        # Back details
        if 'box pleat' in details_text:
            construction['back_details'] = 'Box pleat'
        elif 'side pleat' in details_text:
            construction['back_details'] = 'Side pleats'
        elif 'center pleat' in details_text:
            construction['back_details'] = 'Center pleat'
        elif 'yoke' in details_text:
            construction['back_details'] = 'Back yoke'
        
        # Stitching details
        stitching_patterns = [
            'double-needle', 'flat-felled seam', 'reinforced', 
            'bartack', 'chain stitch', 'overlock'
        ]
        for stitch in stitching_patterns:
            if stitch in details_text:
                construction['stitching'].append(stitch.replace('-', ' ').capitalize())
        
        # Closures
        if 'button' in details_text:
            construction['closures'].append('Buttons')
        if 'zipper' in details_text or 'zip' in details_text:
            construction['closures'].append('Zipper')
        if 'snap' in details_text:
            construction['closures'].append('Snaps')
        
        return construction
    
    def _extract_technical_features(self, soup: BeautifulSoup) -> List[str]:
        """Extract technical features and performance attributes"""
        features = []
        details_text = soup.text.lower()
        
        # Technical feature keywords
        tech_features = {
            'moisture-wicking': 'Moisture-wicking technology',
            'four-way stretch': 'Four-way stretch',
            'two-way stretch': 'Two-way stretch',
            'upf': 'UPF sun protection',
            'anti-odor': 'Anti-odor technology',
            'temperature regulation': 'Temperature regulation',
            'water-repellent': 'Water-repellent finish',
            'windproof': 'Windproof',
            'breathable': 'Enhanced breathability',
            'quick-dry': 'Quick-dry fabric',
            'packable': 'Packable design',
            'reversible': 'Reversible',
            'convertible': 'Convertible design',
            'articulated': 'Articulated construction',
            'gusseted': 'Gusseted design',
            'vented': 'Ventilation panels',
            'reflective': 'Reflective details'
        }
        
        for keyword, feature in tech_features.items():
            if keyword in details_text:
                features.append(feature)
        
        return features
    
    def _extract_sustainability_info(self, soup: BeautifulSoup) -> Dict:
        """Extract sustainability and ethical production information"""
        sustainability = {
            'certifications': [],
            'sustainable_materials': [],
            'production_notes': [],
            'recycled_content': 0
        }
        
        details_text = soup.text
        
        # Sustainability keywords and certifications
        sustainable_keywords = {
            'organic': 'Organic materials',
            'organic cotton': 'Organic cotton',
            'recycled': 'Recycled materials',
            'sustainable': 'Sustainable production',
            'eco-friendly': 'Eco-friendly',
            'bci cotton': 'Better Cotton Initiative',
            'gots certified': 'GOTS Certified',
            'fair trade': 'Fair Trade',
            'responsibly sourced': 'Responsibly sourced',
            'low impact': 'Low impact dyes',
            'water-saving': 'Water-saving production',
            'bluesign': 'Bluesign approved',
            'oeko-tex': 'Oeko-Tex certified'
        }
        
        for keyword, cert in sustainable_keywords.items():
            if keyword in details_text.lower():
                if 'certified' in cert.lower() or 'initiative' in cert.lower():
                    sustainability['certifications'].append(cert)
                else:
                    sustainability['sustainable_materials'].append(cert)
        
        # Check for recycled content percentage
        recycled_match = re.search(r'(\d+)%\s*recycled', details_text, re.IGNORECASE)
        if recycled_match:
            sustainability['recycled_content'] = int(recycled_match.group(1))
        
        return sustainability
    
    def _extract_all_product_details(self, soup: BeautifulSoup) -> List[str]:
        """Extract all product detail bullet points"""
        details = []
        
        # Multiple possible locations for product details
        detail_selectors = [
            '.product-details__content li',
            '.pdp-details li',
            '[data-qaid="productDetails"] li',
            '.product-information li',
            '.product-features li'
        ]
        
        for selector in detail_selectors:
            items = soup.select(selector)
            for item in items:
                text = item.text.strip()
                if text and text not in details and len(text) > 5:
                    details.append(text)
        
        return details
    
    def _extract_fit_details(self, soup: BeautifulSoup) -> Dict:
        """Extract detailed fit information"""
        fit_info = {
            'fit_type': '',
            'fit_description': '',
            'how_it_fits': [],
            'model_info': '',
            'size_recommendation': ''
        }
        
        # Extract fit type
        fit_selectors = [
            '[data-qaid*="fit"]',
            '.product__fit',
            '.fit-guide'
        ]
        
        for selector in fit_selectors:
            fit_elem = soup.select_one(selector)
            if fit_elem:
                fit_info['fit_type'] = fit_elem.text.strip()
                break
        
        # Look for fit descriptions
        fit_descriptions = soup.select('.fit-description, .fit-notes, [data-qaid="fitDescription"]')
        if fit_descriptions:
            fit_info['fit_description'] = ' '.join([d.text.strip() for d in fit_descriptions])
        
        # Extract how it fits bullet points
        fit_bullets = soup.select('.fit-details li, .how-it-fits li')
        fit_info['how_it_fits'] = [bullet.text.strip() for bullet in fit_bullets]
        
        # Model information
        model_info = soup.select_one('.model-info, [data-qaid="modelInfo"]')
        if model_info:
            fit_info['model_info'] = model_info.text.strip()
        
        # Size recommendations
        size_rec = soup.select_one('.size-recommendation, [data-qaid="sizeRecommendation"]')
        if size_rec:
            fit_info['size_recommendation'] = size_rec.text.strip()
        
        return fit_info
    
    def _extract_styling_notes(self, soup: BeautifulSoup) -> List[str]:
        """Extract styling suggestions and outfit ideas"""
        styling = []
        
        # Look for styling section
        styling_section = soup.select('.styling-notes li, .how-to-wear li, .outfit-ideas li')
        styling = [note.text.strip() for note in styling_section]
        
        # Also look for styling in description
        description_text = soup.text
        styling_patterns = [
            r'pair with [^.]+',
            r'style with [^.]+',
            r'looks great with [^.]+',
            r'perfect for [^.]+',
            r'wear with [^.]+'
        ]
        
        for pattern in styling_patterns:
            matches = re.findall(pattern, description_text, re.IGNORECASE)
            for match in matches:
                clean_note = match.strip().capitalize()
                if clean_note not in styling:
                    styling.append(clean_note)
        
        return styling
    
    def _extract_all_descriptions(self, soup: BeautifulSoup) -> List[str]:
        """Extract all descriptive text for AI analysis"""
        descriptions = []
        
        # Get main product description
        desc_selectors = [
            '.product-description',
            '[data-qaid="productDescription"]',
            '.pdp-description',
            '.product-story'
        ]
        
        for selector in desc_selectors:
            desc = soup.select_one(selector)
            if desc:
                text = desc.text.strip()
                if text and len(text) > 20:
                    descriptions.append(text)
        
        # Get additional descriptive paragraphs
        paragraphs = soup.select('.product-content p, .pdp-content p')
        for p in paragraphs:
            text = p.text.strip()
            if len(text) > 50 and text not in descriptions:
                descriptions.append(text)
        
        return descriptions
    
    def _extract_measurements(self, soup: BeautifulSoup) -> Dict:
        """Extract garment measurements and size guide"""
        measurements = {
            'size_chart': {},
            'measurement_type': 'inches',  # default
            'fit_notes': []
        }
        
        # Look for size chart
        size_chart = soup.select('.size-chart table, .measurements-table')
        if size_chart:
            # Parse table data
            rows = size_chart[0].select('tr')
            for row in rows:
                cells = row.select('td, th')
                if len(cells) >= 2:
                    measurement_type = cells[0].text.strip()
                    for i, cell in enumerate(cells[1:], 1):
                        size_label = f"Size_{i}"  # Will need header row to get actual sizes
                        value = cell.text.strip()
                        if measurement_type not in measurements['size_chart']:
                            measurements['size_chart'][measurement_type] = {}
                        measurements['size_chart'][measurement_type][size_label] = value
        
        return measurements
    
    def _extract_all_variants(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract all color and fit variants"""
        variants = []
        
        # Extract colors
        color_swatches = soup.select('.product__color-swatch, [data-qaid*="colorSwatch"]')
        
        for swatch in color_swatches:
            variant = {
                'color_name': swatch.get('title', '').strip() or swatch.get('aria-label', '').strip(),
                'color_code': swatch.get('data-color-code', ''),
                'color_hex': self._extract_hex_from_element(swatch),
                'color_swatch_url': swatch.get('data-image', ''),
                'in_stock': 'unavailable' not in swatch.get('class', [])
            }
            
            if variant['color_name']:
                variants.append(variant)
        
        # Extract fit options
        fit_options = soup.select('[data-qaid*="fitOption"], .product__fit-option')
        fits = [fit.text.strip() for fit in fit_options]
        
        # Create variants for each color/fit combination
        final_variants = []
        for color_variant in variants:
            if fits:
                for fit in fits:
                    variant_copy = color_variant.copy()
                    variant_copy['fit_option'] = fit
                    final_variants.append(variant_copy)
            else:
                color_variant['fit_option'] = 'Regular'
                final_variants.append(color_variant)
        
        return final_variants
    
    def _extract_hex_from_element(self, element) -> Optional[str]:
        """Extract hex color from element style or data attributes"""
        style = element.get('style', '')
        hex_match = re.search(r'#[0-9A-Fa-f]{6}', style)
        if hex_match:
            return hex_match.group()
        
        # Check data attributes
        for attr in ['data-hex', 'data-color-hex']:
            hex_val = element.get(attr, '')
            if hex_val and hex_val.startswith('#'):
                return hex_val
        
        return None
    
    def _extract_category(self, soup: BeautifulSoup) -> Dict:
        """Extract category hierarchy"""
        breadcrumbs = soup.select('.breadcrumb a, nav[aria-label="breadcrumb"] a')
        
        category = {
            'hierarchy': [crumb.text.strip() for crumb in breadcrumbs],
            'main': '',
            'sub': ''
        }
        
        if len(category['hierarchy']) > 1:
            category['main'] = category['hierarchy'][1] if len(category['hierarchy']) > 1 else ''
            category['sub'] = category['hierarchy'][-1] if len(category['hierarchy']) > 2 else ''
        
        return category
    
    def save_to_new_structure(self, product_data: Dict) -> bool:
        """
        Save comprehensive product data to new database structure
        """
        if not product_data:
            return False
        
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            
            # Get category IDs
            category_id = None
            if product_data['category']['main']:
                cur.execute("SELECT id FROM categories WHERE name = %s", 
                          (product_data['category']['main'],))
                result = cur.fetchone()
                category_id = result[0] if result else None
            
            # Insert or update product_master
            cur.execute("""
                INSERT INTO product_master (
                    brand_id, product_code, base_name,
                    materials, care_instructions, construction_details,
                    technical_features, sustainability,
                    product_details, fit_information,
                    styling_notes, description_texts,
                    measurements_guide, category_id,
                    created_at, last_scraped
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (brand_id, product_code) 
                DO UPDATE SET 
                    base_name = EXCLUDED.base_name,
                    materials = EXCLUDED.materials,
                    care_instructions = EXCLUDED.care_instructions,
                    construction_details = EXCLUDED.construction_details,
                    technical_features = EXCLUDED.technical_features,
                    sustainability = EXCLUDED.sustainability,
                    product_details = EXCLUDED.product_details,
                    fit_information = EXCLUDED.fit_information,
                    styling_notes = EXCLUDED.styling_notes,
                    description_texts = EXCLUDED.description_texts,
                    measurements_guide = EXCLUDED.measurements_guide,
                    updated_at = NOW(),
                    last_scraped = NOW()
                RETURNING id
            """, (
                self.brand_id,
                product_data['product_code'],
                product_data['base_name'],
                json.dumps(product_data['materials']),
                product_data['care_instructions'],
                json.dumps(product_data['construction_details']),
                product_data['technical_features'],
                json.dumps(product_data['sustainability']),
                product_data['product_details'],
                json.dumps(product_data['fit_information']),
                product_data['styling_notes'],
                product_data['description_texts'],
                json.dumps(product_data['measurements_guide']),
                category_id
            ))
            
            master_id = cur.fetchone()[0]
            
            # Insert variants
            for variant in product_data['variants']:
                cur.execute("""
                    INSERT INTO product_variants (
                        product_master_id, brand_id,
                        color_name, color_code, color_hex,
                        color_swatch_url, fit_option,
                        in_stock, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    ON CONFLICT (product_master_id, color_name, fit_option) 
                    DO UPDATE SET 
                        color_hex = EXCLUDED.color_hex,
                        color_swatch_url = EXCLUDED.color_swatch_url,
                        in_stock = EXCLUDED.in_stock,
                        updated_at = NOW()
                """, (
                    master_id,
                    self.brand_id,
                    variant['color_name'],
                    variant.get('color_code', ''),
                    variant.get('color_hex', ''),
                    variant.get('color_swatch_url', ''),
                    variant.get('fit_option', 'Regular'),
                    variant.get('in_stock', True)
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            
            print(f"✅ Saved {product_data['base_name']} with {len(product_data['variants'])} variants")
            return True
            
        except Exception as e:
            print(f"❌ Error saving to database: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    fetcher = EnhancedJCrewFetcher()
    
    # Test with a product
    test_url = "https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt-with-point-collar/CF783"
    
    print("🔍 Fetching comprehensive product data...")
    product_data = fetcher.fetch_comprehensive_product(test_url)
    
    if product_data:
        print(f"\n📦 Product: {product_data['base_name']}")
        print(f"📊 Data captured:")
        print(f"   • Materials: {product_data['materials']['primary_fabric']}")
        print(f"   • Composition: {product_data['materials']['composition']}")
        print(f"   • Care: {len(product_data['care_instructions'])} instructions")
        print(f"   • Construction: {len(product_data['construction_details'])} details")
        print(f"   • Features: {len(product_data['technical_features'])} features")
        print(f"   • Sustainability: {product_data['sustainability']}")
        print(f"   • Variants: {len(product_data['variants'])} color/fit combos")
        
        # Save to database
        success = fetcher.save_to_new_structure(product_data)
        
        if success:
            print("\n✅ Successfully saved to new database structure!")
        else:
            print("\n❌ Failed to save to database")

