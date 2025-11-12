#!/usr/bin/env python3
"""
Add J.Crew product to FreestyleDB with URL lookup support
This script:
1. Scrapes J.Crew product data
2. Inserts into FreestyleDB's normalized structure
3. Adds URL lookup indexes and RPC function
"""

import sys
import re
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Add parent directory to path
sys.path.append('/Users/seandavey/projects/V10')
from db_config import DB_CONFIG

# FreestyleDB connection (you'll need to update this)
FREESTYLEDB_CONFIG = {
    "host": "your-freestyledb-host",
    "port": "5432",
    "database": "postgres",
    "user": "your-user",
    "password": "your-password"
}

def extract_product_code_from_url(url: str) -> dict:
    """Extract product code and variant info from J.Crew URL"""
    parsed = urlparse(url)
    path = parsed.path
    
    # Extract product code (e.g., BE996 from path)
    match = re.search(r'/([A-Z][A-Z0-9]{3,5})(?:\?|$)', path)
    product_code = match.group(1).upper() if match else None
    
    # Extract variant code from query params
    query_params = parse_qs(parsed.query)
    variant_code = query_params.get('colorProductCode', [None])[0]
    
    return {
        'base_code': product_code,
        'variant_code': variant_code,
        'full_url': url
    }

def scrape_jcrew_product(url: str) -> dict:
    """Scrape J.Crew product page"""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract product name
        name_elem = soup.find('h1') or soup.find('title')
        product_name = name_elem.get_text().strip() if name_elem else "Unknown Product"
        
        # Extract colors (simplified - you might want to use your existing scraper)
        colors = []
        color_elements = soup.find_all(['button', 'a'], class_=re.compile(r'color', re.I))
        for elem in color_elements:
            color_text = elem.get_text().strip()
            if color_text and len(color_text) < 50:
                colors.append(color_text)
        
        # Extract fits
        fits = []
        fit_elements = soup.find_all(['button', 'a'], class_=re.compile(r'fit|variation', re.I))
        for elem in fit_elements:
            fit_text = elem.get_text().strip()
            if fit_text in ['Classic', 'Slim', 'Tall', 'Relaxed', 'Regular']:
                fits.append(fit_text)
        
        # Extract price
        price_elem = soup.find(string=re.compile(r'\$\d+'))
        price = None
        if price_elem:
            price_match = re.search(r'\$(\d+(?:\.\d+)?)', price_elem)
            if price_match:
                price = float(price_match.group(1))
        
        return {
            'name': product_name,
            'colors': colors,
            'fits': fits,
            'price': price,
            'url': url
        }
    except Exception as e:
        print(f"Error scraping product: {e}")
        return None

def get_or_create_brand(conn, brand_name: str) -> int:
    """Get or create brand in FreestyleDB"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if brand exists
    cur.execute("SELECT id FROM brand WHERE name = %s", (brand_name,))
    result = cur.fetchone()
    
    if result:
        return result['id']
    
    # Create brand
    cur.execute("""
        INSERT INTO brand (name, website)
        VALUES (%s, %s)
        RETURNING id
    """, (brand_name, f"https://www.{brand_name.lower().replace('.', '').replace(' ', '')}.com"))
    
    brand_id = cur.fetchone()['id']
    conn.commit()
    return brand_id

def get_or_create_category(conn, category_name: str) -> int:
    """Get or create category in FreestyleDB"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if category exists
    cur.execute("SELECT id FROM category WHERE slug = %s OR name = %s", (category_name.lower(), category_name))
    result = cur.fetchone()
    
    if result:
        return result['id']
    
    # Create category
    cur.execute("""
        INSERT INTO category (slug, name)
        VALUES (%s, %s)
        RETURNING id
    """, (category_name.lower(), category_name))
    
    category_id = cur.fetchone()['id']
    conn.commit()
    return category_id

def get_or_create_color(conn, color_name: str, family: str = None) -> int:
    """Get or create color in color_catalog"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if color exists
    cur.execute("SELECT id FROM color_catalog WHERE canonical = %s", (color_name,))
    result = cur.fetchone()
    
    if result:
        return result['id']
    
    # Create color
    cur.execute("""
        INSERT INTO color_catalog (canonical, family)
        VALUES (%s, %s)
        RETURNING id
    """, (color_name, family))
    
    color_id = cur.fetchone()['id']
    conn.commit()
    return color_id

def get_or_create_fit(conn, fit_name: str) -> int:
    """Get or create fit in fit_catalog"""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Check if fit exists
    cur.execute("SELECT id FROM fit_catalog WHERE name = %s", (fit_name,))
    result = cur.fetchone()
    
    if result:
        return result['id']
    
    # Create fit
    cur.execute("""
        INSERT INTO fit_catalog (name)
        VALUES (%s)
        RETURNING id
    """, (fit_name,))
    
    fit_id = cur.fetchone()['id']
    conn.commit()
    return fit_id

def add_jcrew_product_to_freestyledb(url: str, freestyledb_config: dict):
    """Add J.Crew product to FreestyleDB"""
    
    print(f"\n{'='*80}")
    print(f"Adding J.Crew Product to FreestyleDB")
    print(f"{'='*80}")
    print(f"URL: {url}\n")
    
    # Extract product info from URL
    url_info = extract_product_code_from_url(url)
    print(f"📝 Extracted from URL:")
    print(f"   Base code: {url_info['base_code']}")
    print(f"   Variant code: {url_info['variant_code']}")
    
    # Scrape product data
    print(f"\n🔍 Scraping product data...")
    product_data = scrape_jcrew_product(url)
    if not product_data:
        print("❌ Failed to scrape product data")
        return False
    
    print(f"   Product name: {product_data['name']}")
    print(f"   Colors: {len(product_data['colors'])}")
    print(f"   Fits: {len(product_data['fits'])}")
    print(f"   Price: ${product_data['price']}" if product_data['price'] else "   Price: N/A")
    
    # Connect to FreestyleDB
    print(f"\n💾 Connecting to FreestyleDB...")
    conn = psycopg2.connect(**freestyledb_config)
    conn.autocommit = False
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Get or create brand
        brand_id = get_or_create_brand(conn, "J.Crew")
        print(f"   ✓ Brand ID: {brand_id}")
        
        # Get or create category (shirts)
        category_id = get_or_create_category(conn, "shirts")
        print(f"   ✓ Category ID: {category_id}")
        
        # Create style
        print(f"\n📦 Creating style...")
        cur.execute("""
            INSERT INTO style (brand_id, category_id, name, description, gender, lifecycle)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (brand_id, name, category_id) DO UPDATE
            SET updated_at = NOW()
            RETURNING id
        """, (
            brand_id,
            category_id,
            product_data['name'],
            None,  # description
            'Men',  # gender
            'active'  # lifecycle
        ))
        
        style_id = cur.fetchone()['id']
        print(f"   ✓ Style ID: {style_id}")
        
        # Add style code
        if url_info['base_code']:
            cur.execute("""
                INSERT INTO style_code (style_id, code, code_type, region)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (style_id, url_info['base_code'], 'product_code', 'US'))
            print(f"   ✓ Style code: {url_info['base_code']}")
        
        # Create variant(s)
        # For simplicity, create one variant per color
        # In production, you'd want to scrape all colors and create variants for each
        colors = product_data['colors'] or ['Default']
        fits = product_data['fits'] or [None]
        
        variant_ids = []
        for color_name in colors[:1]:  # Just create first variant for now
            # Get or create color
            color_id = get_or_create_color(conn, color_name) if color_name != 'Default' else None
            
            # Get or create fit
            fit_id = get_or_create_fit(conn, fits[0]) if fits and fits[0] else None
            
            # Create variant
            cur.execute("""
                INSERT INTO variant (style_id, color_id, fit_id, is_active, attrs)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                style_id,
                color_id,
                fit_id,
                True,
                '{}'  # attrs JSONB
            ))
            
            variant_id = cur.fetchone()['id']
            variant_ids.append(variant_id)
            print(f"   ✓ Variant ID: {variant_id} (color: {color_name}, fit: {fits[0] if fits else 'None'})")
            
            # Add variant code if available
            if url_info['variant_code']:
                cur.execute("""
                    INSERT INTO variant_code (variant_id, code, code_type, region)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (variant_id, url_info['variant_code'], 'variant_code', 'US'))
        
        # Add product URL
        print(f"\n🔗 Adding product URL...")
        for variant_id in variant_ids:
            cur.execute("""
                INSERT INTO product_url (style_id, variant_id, region, url, is_current, seen_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                style_id,
                variant_id,
                'US',
                url,
                True,
                datetime.now()
            ))
        print(f"   ✓ URL added")
        
        # Add price if available
        if product_data['price']:
            print(f"\n💰 Adding price...")
            for variant_id in variant_ids:
                cur.execute("""
                    INSERT INTO price_history (variant_id, region, currency, list_price, sale_price, captured_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    variant_id,
                    'US',
                    'USD',
                    product_data['price'],
                    product_data['price'],  # Assuming no sale price
                    datetime.now()
                ))
            print(f"   ✓ Price added")
        
        conn.commit()
        print(f"\n✅ Successfully added product to FreestyleDB!")
        print(f"   Style ID: {style_id}")
        print(f"   Variant IDs: {variant_ids}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cur.close()
        conn.close()

def add_url_lookup_optimization(freestyledb_config: dict):
    """Add indexes and RPC function for URL lookup"""
    
    print(f"\n{'='*80}")
    print(f"Adding URL Lookup Optimization")
    print(f"{'='*80}\n")
    
    conn = psycopg2.connect(**freestyledb_config)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Add pg_trgm extension
        print("1. Adding pg_trgm extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")
        print("   ✓ Extension added")
        
        # Add direct URL index
        print("\n2. Adding direct URL index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_url_url 
            ON product_url(url);
        """)
        print("   ✓ Direct URL index added")
        
        # Add trigram index for fuzzy matching
        print("\n3. Adding trigram index for fuzzy matching...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_product_url_url_trgm 
            ON product_url USING gin(url gin_trgm_ops);
        """)
        print("   ✓ Trigram index added")
        
        # Create RPC function for URL lookup
        print("\n4. Creating product_lookup RPC function...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION product_lookup(input_url text)
            RETURNS TABLE(
                brand text,
                style_name text,
                style_code text,
                variant_id bigint,
                color text,
                fit text,
                product_url text,
                image_url text
            )
            LANGUAGE sql STABLE
            AS $$
            WITH cleaned AS (
                SELECT regexp_replace(input_url, '\\?.*$', '') as base_no_query
            ),
            exact AS (
                SELECT 
                    b.name as brand,
                    s.name as style_name,
                    sc.code as style_code,
                    v.id as variant_id,
                    c.canonical as color,
                    f.name as fit,
                    pu.url as product_url,
                    vi.url as image_url
                FROM product_url pu
                JOIN style s ON pu.style_id = s.id
                JOIN brand b ON s.brand_id = b.id
                LEFT JOIN variant v ON pu.variant_id = v.id
                LEFT JOIN style_code sc ON s.id = sc.style_id
                LEFT JOIN color_catalog c ON v.color_id = c.id
                LEFT JOIN fit_catalog f ON v.fit_id = f.id
                LEFT JOIN v_variant_current_image vi ON v.id = vi.variant_id
                JOIN cleaned ON pu.url = cleaned.base_no_query
                WHERE pu.is_current = true
            ),
            prefix AS (
                SELECT 
                    b.name as brand,
                    s.name as style_name,
                    sc.code as style_code,
                    v.id as variant_id,
                    c.canonical as color,
                    f.name as fit,
                    pu.url as product_url,
                    vi.url as image_url
                FROM product_url pu
                JOIN style s ON pu.style_id = s.id
                JOIN brand b ON s.brand_id = b.id
                LEFT JOIN variant v ON pu.variant_id = v.id
                LEFT JOIN style_code sc ON s.id = sc.style_id
                LEFT JOIN color_catalog c ON v.color_id = c.id
                LEFT JOIN fit_catalog f ON v.fit_id = f.id
                LEFT JOIN v_variant_current_image vi ON v.id = vi.variant_id
                JOIN cleaned ON pu.url ILIKE cleaned.base_no_query || '%'
                WHERE pu.is_current = true
            ),
            stylecode AS (
                SELECT 
                    b.name as brand,
                    s.name as style_name,
                    sc.code as style_code,
                    v.id as variant_id,
                    c.canonical as color,
                    f.name as fit,
                    pu.url as product_url,
                    vi.url as image_url
                FROM product_url pu
                JOIN style s ON pu.style_id = s.id
                JOIN brand b ON s.brand_id = b.id
                LEFT JOIN variant v ON pu.variant_id = v.id
                LEFT JOIN style_code sc ON s.id = sc.style_id AND sc.code = upper(regexp_replace(input_url, '.*/([A-Z0-9]{4,6})(?:[^A-Z0-9]|$).*', '\\1'))
                LEFT JOIN color_catalog c ON v.color_id = c.id
                LEFT JOIN fit_catalog f ON v.fit_id = f.id
                LEFT JOIN v_variant_current_image vi ON v.id = vi.variant_id
                JOIN cleaned ON sc.code IS NOT NULL
                WHERE pu.is_current = true
            )
            SELECT * FROM exact
            UNION ALL
            SELECT * FROM prefix
            WHERE NOT EXISTS (SELECT 1 FROM exact)
            UNION ALL
            SELECT * FROM stylecode
            WHERE NOT EXISTS (SELECT 1 FROM exact) AND NOT EXISTS (SELECT 1 FROM prefix)
            LIMIT 50;
            $$;
        """)
        print("   ✓ RPC function created")
        
        # Grant permissions
        print("\n5. Granting permissions...")
        cur.execute("GRANT EXECUTE ON FUNCTION product_lookup(text) TO anon, authenticated;")
        print("   ✓ Permissions granted")
        
        print(f"\n✅ URL lookup optimization complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    url = "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996"
    
    # Update this with your FreestyleDB connection details
    print("⚠️  Please update FREESTYLEDB_CONFIG in this script with your database credentials")
    
    # Uncomment when you've set the config:
    # add_jcrew_product_to_freestyledb(url, FREESTYLEDB_CONFIG)
    # add_url_lookup_optimization(FREESTYLEDB_CONFIG)
    
    print("\n📝 Next steps:")
    print("1. Update FREESTYLEDB_CONFIG with your database credentials")
    print("2. Uncomment the function calls at the bottom")
    print("3. Run the script")
    print("4. Test URL lookup with: SELECT * FROM product_lookup('your-url-here');")





