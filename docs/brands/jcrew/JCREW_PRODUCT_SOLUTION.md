# J.Crew Product Identification Solution

## 📌 Current Situation

**What we have:**
- ✅ J.Crew scraper exists (`scrapers/scrapers/jcrew.py`)
- ✅ Product cache table exists (`jcrew_product_cache`)
- ⚠️ Only 5 sample products in database
- ❌ Most J.Crew URLs won't be recognized

**The problem:** When a user submits a J.Crew URL, the app can't identify the product unless it's one of the 5 cached ones.

---

## 🎯 Solution: Real-Time Product Fetching

Instead of pre-scraping all J.Crew products (thousands of items), we'll fetch product data **on-demand** when a user submits a URL.

### 1. Add Real-Time J.Crew Product Fetcher

Create `src/ios_app/Backend/jcrew_fetcher.py`:

```python
import requests
from bs4 import BeautifulSoup
import re
import json
from typing import Dict, Optional
import psycopg2
from db_config import DB_CONFIG

class JCrewProductFetcher:
    """Fetch J.Crew product data on-demand and cache it"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    
    def fetch_product(self, product_url: str) -> Optional[Dict]:
        """
        Fetch product data from J.Crew URL
        Returns product info or None if failed
        """
        # First check cache
        cached = self._check_cache(product_url)
        if cached:
            print(f"✅ Found in cache: {cached['product_name']}")
            return cached
        
        # Fetch from website
        print(f"🔍 Fetching from J.Crew: {product_url}")
        product_data = self._scrape_product(product_url)
        
        if product_data:
            # Save to cache
            self._save_to_cache(product_data)
            print(f"✅ Cached new product: {product_data['product_name']}")
        
        return product_data
    
    def _check_cache(self, product_url: str) -> Optional[Dict]:
        """Check if product exists in cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT product_name, product_code, product_image,
                       category, subcategory, sizes_available,
                       colors_available, material, fit_type, price
                FROM jcrew_product_cache
                WHERE product_url = %s
            """, (product_url,))
            
            row = cur.fetchone()
            if row:
                return {
                    'product_url': product_url,
                    'product_name': row[0],
                    'product_code': row[1],
                    'product_image': row[2],
                    'category': row[3],
                    'subcategory': row[4],
                    'sizes_available': row[5],
                    'colors_available': row[6],
                    'material': row[7],
                    'fit_type': row[8],
                    'price': float(row[9]) if row[9] else None
                }
        finally:
            cur.close()
            conn.close()
        
        return None
    
    def _scrape_product(self, product_url: str) -> Optional[Dict]:
        """Scrape product data from J.Crew website"""
        try:
            response = requests.get(product_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract product data
            product_data = {
                'product_url': product_url,
                'product_name': self._extract_name(soup),
                'product_code': self._extract_code(product_url, soup),
                'product_image': self._extract_image(soup),
                'price': self._extract_price(soup),
                'sizes_available': self._extract_sizes(soup),
                'colors_available': self._extract_colors(soup),
                'material': self._extract_material(soup),
                'fit_type': self._extract_fit(soup),
                'category': 'Shirts',  # Default, improve later
                'subcategory': 'Casual'
            }
            
            return product_data
            
        except Exception as e:
            print(f"❌ Error scraping {product_url}: {e}")
            return None
    
    def _extract_name(self, soup: BeautifulSoup) -> str:
        """Extract product name"""
        # Try multiple selectors
        selectors = [
            'h1.product-name',
            'h1[data-qaid="pdpProductName"]',
            'h1.product__name',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    return element.get('content', '').strip()
                else:
                    return element.text.strip()
        
        return "J.Crew Product"
    
    def _extract_code(self, url: str, soup: BeautifulSoup) -> str:
        """Extract product code from URL or page"""
        # Try to get from URL (usually last part)
        match = re.search(r'/([A-Z0-9]{4,8})(?:\?|$)', url)
        if match:
            return match.group(1)
        
        # Try from page
        sku_element = soup.select_one('[data-qaid="pdpItemNumber"]')
        if sku_element:
            return sku_element.text.strip()
        
        return ""
    
    def _extract_image(self, soup: BeautifulSoup) -> str:
        """Extract main product image"""
        # Try multiple selectors
        selectors = [
            'img.product__image',
            'img[data-qaid="pdpMainImage"]',
            'meta[property="og:image"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if selector.startswith('meta'):
                    img_url = element.get('content', '')
                else:
                    img_url = element.get('src', '')
                
                # Make URL absolute
                if img_url and not img_url.startswith('http'):
                    img_url = f"https://www.jcrew.com{img_url}"
                
                return img_url
        
        return ""
    
    def _extract_price(self, soup: BeautifulSoup) -> Optional[float]:
        """Extract product price"""
        price_element = soup.select_one('[data-qaid="pdpSalePrice"], .product__price--sale, .product__price')
        if price_element:
            price_text = price_element.text.strip()
            # Extract number from price text
            match = re.search(r'[\d,]+\.?\d*', price_text)
            if match:
                return float(match.group().replace(',', ''))
        return None
    
    def _extract_sizes(self, soup: BeautifulSoup) -> list:
        """Extract available sizes"""
        sizes = []
        
        # Try to find size buttons
        size_elements = soup.select('[data-qaid*="size"], .size-selector__button, button[aria-label*="Size"]')
        for element in size_elements:
            size_text = element.text.strip()
            if size_text and size_text not in sizes:
                sizes.append(size_text)
        
        # Default sizes if none found
        if not sizes:
            sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        
        return sizes
    
    def _extract_colors(self, soup: BeautifulSoup) -> list:
        """Extract available colors"""
        colors = []
        
        # Try to find color options
        color_elements = soup.select('[data-qaid*="color"], .color-selector__button, button[aria-label*="Color"]')
        for element in color_elements:
            color_text = element.get('aria-label', '') or element.text.strip()
            if color_text and color_text not in colors:
                colors.append(color_text)
        
        return colors if colors else ['Default']
    
    def _extract_material(self, soup: BeautifulSoup) -> str:
        """Extract material/fabric information"""
        # Look in product details
        details = soup.select('.product-details__content li, .pdp-details li')
        for detail in details:
            text = detail.text.lower()
            if 'cotton' in text or 'polyester' in text or 'wool' in text:
                return detail.text.strip()
        
        return ""
    
    def _extract_fit(self, soup: BeautifulSoup) -> str:
        """Extract fit type"""
        # Look for fit information
        fit_element = soup.select_one('[data-qaid*="fit"], .product__fit')
        if fit_element:
            return fit_element.text.strip()
        
        # Check in title or description
        text = soup.text.lower()
        if 'slim' in text:
            return 'Slim'
        elif 'classic' in text or 'regular' in text:
            return 'Classic'
        elif 'relaxed' in text:
            return 'Relaxed'
        
        return 'Regular'
    
    def _save_to_cache(self, product_data: Dict):
        """Save product data to cache"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            cur.execute("""
                INSERT INTO jcrew_product_cache (
                    product_url, product_code, product_name, product_image,
                    category, subcategory, price, sizes_available,
                    colors_available, material, fit_type, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (product_url) DO UPDATE SET
                    product_name = EXCLUDED.product_name,
                    product_image = EXCLUDED.product_image,
                    price = EXCLUDED.price,
                    sizes_available = EXCLUDED.sizes_available,
                    updated_at = NOW()
            """, (
                product_data['product_url'],
                product_data.get('product_code', ''),
                product_data['product_name'],
                product_data.get('product_image', ''),
                product_data.get('category', 'Shirts'),
                product_data.get('subcategory', 'Casual'),
                product_data.get('price'),
                product_data.get('sizes_available', []),
                product_data.get('colors_available', []),
                product_data.get('material', ''),
                product_data.get('fit_type', 'Regular')
            ))
            
            conn.commit()
        finally:
            cur.close()
            conn.close()
```

### 2. Update Backend to Use Fetcher

In `src/ios_app/Backend/app.py`, update the `/tryon/start` endpoint:

```python
from jcrew_fetcher import JCrewProductFetcher

# Initialize fetcher
jcrew_fetcher = JCrewProductFetcher()

@app.post("/tryon/start")
async def start_tryon_session(request: dict):
    """
    Start a try-on session with real-time product fetching
    """
    try:
        product_url = request.get("product_url")
        user_id = request.get("user_id", "1")
        
        if not product_url:
            raise HTTPException(status_code=400, detail="Product URL is required")
        
        print(f"🎯 Starting try-on session for: {product_url}")
        
        # Extract brand from URL
        brand_info = extract_brand_from_url(product_url)
        if not brand_info:
            raise HTTPException(status_code=400, detail="Could not identify brand from URL")
        
        # For J.Crew, fetch product data on-demand
        if brand_info["brand_name"] == "J.Crew":
            product_data = jcrew_fetcher.fetch_product(product_url)
            if product_data:
                product_name = product_data['product_name']
                product_image = product_data['product_image']
                size_options = product_data.get('sizes_available', ['XS', 'S', 'M', 'L', 'XL'])
            else:
                # Fallback if fetching fails
                product_name = extract_product_name_from_url(product_url)
                product_image = ""
                size_options = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        else:
            # Use existing logic for other brands
            product_name = extract_product_name_from_url(product_url)
            product_image = extract_product_image_from_url(product_url)
            size_options = await get_brand_size_options(brand_info["brand_id"])
        
        # Get available measurements for this brand
        brand_measurements = await get_brand_measurements_for_feedback(brand_info["brand_id"])
        
        return {
            "session_id": f"tryon_{user_id}_{int(time.time())}",
            "brand": brand_info["brand_name"],
            "brand_id": brand_info["brand_id"],
            "product_name": product_name,
            "product_url": product_url,
            "product_image": product_image,
            "available_measurements": brand_measurements["measurements"],
            "feedback_options": brand_measurements["feedbackOptions"],
            "size_options": size_options,
            "next_step": "size_selection_and_feedback"
        }
        
    except Exception as e:
        print(f"Error starting try-on session: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 3. Test with Real J.Crew URLs

```python
# test_jcrew_fetcher.py
from jcrew_fetcher import JCrewProductFetcher

# Test URLs
test_urls = [
    "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
    "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996",
    "https://www.jcrew.com/p/BV432"  # Short URL format
]

fetcher = JCrewProductFetcher()

for url in test_urls:
    print(f"\nTesting: {url}")
    product = fetcher.fetch_product(url)
    if product:
        print(f"  ✅ Name: {product['product_name']}")
        print(f"  ✅ Code: {product['product_code']}")
        print(f"  ✅ Image: {product['product_image'][:50]}...")
        print(f"  ✅ Sizes: {product['sizes_available']}")
    else:
        print(f"  ❌ Failed to fetch")
```

---

## 🚀 Alternative: Pre-Populate Popular Products

If real-time fetching is too slow, run the scraper once to populate common products:

```bash
# Run the existing J.Crew scraper
cd scrapers
python -c "
from scrapers.jcrew import JCrewScraper
scraper = JCrewScraper()
products = scraper.scrape_products(max_pages=10)
print(f'Scraped {len(products)} products')
"
```

---

## ✅ Benefits of This Approach

1. **No need to scrape entire catalog** - Fetch only what users actually try on
2. **Always up-to-date** - Gets current price, availability, etc.
3. **Builds cache over time** - Popular products get cached automatically
4. **Handles new products** - Works with any J.Crew URL, even brand new items
5. **Fallback built-in** - If scraping fails, still returns basic info

---

## 📝 Implementation Checklist

- [ ] Create `jcrew_fetcher.py` with the JCrewProductFetcher class
- [ ] Update `/tryon/start` endpoint to use fetcher
- [ ] Test with 5-10 real J.Crew URLs
- [ ] Add error handling for network issues
- [ ] Consider adding a background job to pre-fetch popular items

---

## 🎯 Testing Instructions

1. **Start backend with new fetcher**:
```bash
cd src/ios_app/Backend
python app.py
```

2. **Test with curl**:
```bash
curl -X POST http://localhost:8000/tryon/start \
  -H "Content-Type: application/json" \
  -d '{
    "product_url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/casual/BH290",
    "user_id": "1"
  }'
```

3. **Verify in database**:
```sql
SELECT * FROM jcrew_product_cache ORDER BY created_at DESC LIMIT 5;
```

This solution means **any J.Crew URL will work**, not just pre-scraped ones!
