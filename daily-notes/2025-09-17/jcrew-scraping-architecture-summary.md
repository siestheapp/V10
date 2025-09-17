# J.Crew Data Scraping & Storage Architecture Summary

## Overview
We're building a clothing try-on app that needs to store product data from multiple brands. J.Crew is our test case. Users input product URLs, and the app returns product data for try-on sessions.

## Current Database Architecture

### 1. **Two-Table System**
```sql
-- Legacy table (being phased out)
jcrew_product_cache: 47 J.Crew products
  - product_code (text)
  - product_name (text)
  - fit_options (text[])
  - colors_available (text[])
  - sizes_available (text[])
  - category, subcategory (text)
  - metadata (jsonb)

-- New unified structure
product_master: 51 J.Crew products (+ other brands)
  - id (serial)
  - brand_id (references brands)
  - product_code (varchar)
  - base_name (text)
  - materials (jsonb)
  - fit_information (jsonb)
  - category_id, subcategory_id (references)

product_variants: Color/fit combinations
  - product_master_id (references)
  - color_name, fit_option
  - sizes_available (text[])
  - current_price, in_stock
```

## J.Crew Website Structure

### URL Patterns
```
https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/MP694
https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/ludlow/slim-fit-ludlow-dress-shirt/AI873?color=white

Pattern: /p/{product_code} or /p/.../{product_code}
Product codes: 5-6 character alphanumeric (MP694, AI873, BN184)
```

### J.Crew's Category Hierarchy
```
Dress Shirts/
  ├── Bowery (work-appropriate, wrinkle-free)
  ├── Ludlow Premium (luxury dress shirts)
  └── Flex (performance stretch)

Casual Shirts/
  ├── Secret Wash (soft casual shirts)
  ├── Oxford (broken-in oxfords)
  ├── Linen (seasonal)
  └── Flex (stretch casual)
```

### Fit Options (vary by product)
- Classic
- Slim  
- Slim Untucked
- Tall
- Relaxed

## Current Scraping Approach

### Main Scraper: `scripts/precise_jcrew_html_scraper_v2.py`

```python
# Key features:
1. Extracts from actual HTML (no hardcoded fallbacks)
2. Handles multi-variant products (multiple colors/fits)
3. Uses Selenium for JavaScript-rendered content
4. Fails gracefully if data can't be found

# Extraction logic:
def scrape_product(url):
    # 1. Load page with Selenium
    driver.get(url)
    
    # 2. Extract product code from URL
    product_code = extract_from_url_pattern(url)
    
    # 3. Find color swatches
    colors = driver.find_elements(By.CSS_SELECTOR, '[data-testid="color-swatch"]')
    
    # 4. Find fit options (tricky - they're in a select dropdown)
    fit_dropdown = driver.find_element(By.CSS_SELECTOR, 'select[aria-label*="fit"]')
    fits = [option.text for option in fit_dropdown.find_elements(By.TAG_NAME, 'option')]
    
    # 5. Extract sizes (also in dropdown)
    size_elements = driver.find_elements(By.CSS_SELECTOR, '[data-testid="size-option"]')
    
    # 6. Get price, materials, description
    price = driver.find_element(By.CSS_SELECTOR, '[data-testid="product-price"]')
    
    return {
        'product_code': product_code,
        'colors_available': colors,
        'fit_options': fits,
        'sizes_available': sizes,
        ...
    }
```

### Multiple Fetcher Classes
```
JCrewProductFetcher - Basic fetching with caching
JCrewDynamicFetcher - Handles fit variations
JCrewComprehensiveFetcher - Gets all product family data
JCrewEnhancedFetcher - Enriched product data
```

## Data Flow

```
User inputs J.Crew URL
    ↓
Extract product code (e.g., MP694)
    ↓
Check product_master table
    ↓
If found → Return data
If not found → Return "Product not found"
(No real-time scraping in production)
```

## Challenges We've Encountered

### 1. **Fit Variations Complexity**
J.Crew uses URL parameters for fits:
- `?fit=Classic` 
- `?fit=Slim%20Untucked`

Same product code (MP694) can have different fits, each with different:
- Available colors
- Available sizes  
- Prices
- Images

### 2. **Dynamic Content**
- Product pages load data via JavaScript
- Color/size availability changes based on selection
- Some content only appears after user interaction

### 3. **Data Normalization**
J.Crew categories don't map cleanly to universal categories:
- "Bowery" is a J.Crew sub-brand, not a universal category
- "Secret Wash" is J.Crew's fabric treatment name
- Need to map to normalized categories for cross-brand search

## Questions for Optimization

1. **Is our scraping approach optimal?** We use Selenium for everything - should we use requests + BeautifulSoup when possible and only Selenium when needed?

2. **Database structure:** Is the product_master/product_variants split optimal? Should we denormalize for faster queries?

3. **Caching strategy:** Currently pre-loading all products. Should we implement real-time scraping with caching?

4. **Fit handling:** Each brand has unique fit systems. How to best normalize while preserving brand-specific data?

5. **Update frequency:** How often should we re-scrape to catch price changes, new colors, stock status?

## Sample J.Crew Product Data

```json
{
  "product_code": "MP694",
  "product_name": "Secret Wash Cotton Poplin Shirt",
  "brand": "J.Crew",
  "category": "Casual Shirts",
  "subcategory": "Secret Wash",
  "fit_options": ["Classic", "Slim", "Slim Untucked", "Tall"],
  "colors_available": ["White", "Blue", "Pink", "Stripe"],
  "sizes_available": ["XS", "S", "M", "L", "XL", "XXL"],
  "price": 89.50,
  "materials": {
    "primary": "Cotton",
    "composition": "100% Cotton"
  },
  "url": "https://www.jcrew.com/p/mens/categories/clothing/shirts/secret-wash/secret-wash-cotton-poplin-shirt/MP694"
}
```

## Current Performance

- **Database queries**: ~10-50ms
- **Scraping time**: 3-5 seconds per product (with Selenium)
- **Storage**: 51 J.Crew products = ~500KB in database
- **Success rate**: ~85% (some products fail due to page structure changes)

## Next Steps

1. Add more brands (Banana Republic, Theory ready)
2. Implement better error handling for scraping failures
3. Consider caching layer (Redis?) for frequently accessed products
4. Build admin interface for managing product data

---

**Please review this architecture and suggest optimizations for:**
- Scraping efficiency
- Database structure  
- Handling multi-brand complexity
- Real-time vs pre-loaded approach
