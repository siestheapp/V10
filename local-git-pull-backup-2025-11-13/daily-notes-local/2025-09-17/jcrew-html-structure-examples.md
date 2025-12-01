# J.Crew HTML Structure & Scraping Examples

## Actual J.Crew HTML Structure

### Product Page Main Elements
```html
<!-- Product Title -->
<h1 class="ProductDetailsTitle__name___1wYnq" data-qaid="pdpProductName">
  Secret Wash cotton poplin shirt
</h1>

<!-- Price -->
<div class="ProductPrice__container___3JXBS">
  <span class="ProductPrice__price___2Gvmg">$89.50</span>
  <span class="ProductPrice__original___1OYXI">$98.00</span>
</div>

<!-- Color Selection -->
<div class="ColorSwatches__container___2X_kh">
  <button class="ColorSwatch__swatch___3Jc0W" 
          data-testid="color-swatch"
          aria-label="White">
    <img src="white-swatch.jpg" alt="White">
  </button>
  <button class="ColorSwatch__swatch___3Jc0W"
          data-testid="color-swatch"  
          aria-label="Vintage Navy">
    <img src="navy-swatch.jpg" alt="Vintage Navy">
  </button>
</div>

<!-- Fit Dropdown (Tricky Part!) -->
<div class="FitSelector__container___1xY9p">
  <label for="fit-select">Fit</label>
  <select id="fit-select" aria-label="Select fit">
    <option value="">Select a fit</option>
    <option value="Classic">Classic</option>
    <option value="Slim">Slim</option>
    <option value="Slim Untucked">Slim Untucked</option>
    <option value="Tall">Tall</option>
  </select>
</div>

<!-- Size Selection -->
<div class="SizeSelector__container___2kXnS">
  <button class="SizeButton__button___3bwZg" data-testid="size-option">XS</button>
  <button class="SizeButton__button___3bwZg" data-testid="size-option">S</button>
  <button class="SizeButton__button___3bwZg" data-testid="size-option">M</button>
  <!-- Out of stock sizes have different class -->
  <button class="SizeButton__button___3bwZg SizeButton__outOfStock___1aY7B" disabled>L</button>
</div>

<!-- Product Details -->
<div class="ProductDetails__details___3xqCg">
  <h3>Details</h3>
  <ul>
    <li>Cotton.</li>
    <li>Point collar.</li>
    <li>Machine wash.</li>
    <li>Import.</li>
  </ul>
</div>
```

## JavaScript-Rendered Data

### Product Data in JSON-LD
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Secret Wash cotton poplin shirt",
  "image": ["image1.jpg", "image2.jpg"],
  "description": "Our Secret Wash shirts are garment-dyed...",
  "sku": "MP694",
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "89.50",
    "highPrice": "98.00",
    "priceCurrency": "USD"
  }
}
</script>
```

### React Props Data (Sometimes Available)
```html
<script>
window.__INITIAL_STATE__ = {
  "product": {
    "id": "MP694",
    "name": "Secret Wash cotton poplin shirt",
    "variants": [
      {
        "color": "White",
        "colorCode": "WT0002",
        "fit": "Classic",
        "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
        "price": 89.50
      },
      {
        "color": "White", 
        "fit": "Slim",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "price": 89.50
      }
    ]
  }
}
</script>
```

## Our Scraping Approach

### Current Selenium-Based Approach
```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

def scrape_jcrew_product(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)  # Wait for JS to load
    
    # Extract product name
    product_name = driver.find_element(
        By.CSS_SELECTOR, 
        '[data-qaid="pdpProductName"]'
    ).text
    
    # Extract colors - need to click each swatch
    color_swatches = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="color-swatch"]'
    )
    colors = [swatch.get_attribute('aria-label') for swatch in color_swatches]
    
    # Extract fits - from dropdown
    fit_select = Select(driver.find_element(By.ID, 'fit-select'))
    fits = [opt.text for opt in fit_select.options if opt.text != 'Select a fit']
    
    # Extract available sizes
    size_buttons = driver.find_elements(
        By.CSS_SELECTOR,
        '[data-testid="size-option"]:not([disabled])'
    )
    sizes = [btn.text for btn in size_buttons]
    
    return {
        'product_name': product_name,
        'colors': colors,
        'fits': fits,
        'sizes': sizes
    }
```

### Alternative: Hybrid Approach (Proposed)
```python
import requests
from bs4 import BeautifulSoup
import json
import re

def scrape_jcrew_hybrid(url):
    # First try with requests (faster)
    response = requests.get(url, headers={'User-Agent': '...'})
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Try to extract from JSON-LD
    json_ld = soup.find('script', type='application/ld+json')
    if json_ld:
        data = json.loads(json_ld.string)
        product_name = data.get('name')
        sku = data.get('sku')
    
    # Try to extract from __INITIAL_STATE__
    state_script = soup.find('script', string=re.compile('__INITIAL_STATE__'))
    if state_script:
        # Parse the JavaScript object
        state_match = re.search(r'__INITIAL_STATE__\s*=\s*({.*?});', state_script.string)
        if state_match:
            state_data = json.loads(state_match.group(1))
            variants = state_data.get('product', {}).get('variants', [])
    
    # If critical data is missing, fall back to Selenium
    if not product_name or not variants:
        return scrape_with_selenium(url)
    
    return process_data(...)
```

## Challenges with J.Crew's Structure

### 1. **Dynamic Fit/Color Relationships**
- Each fit has different available colors
- Each color has different available sizes
- Price can vary by combination

### 2. **URL Parameter Complexity**
```
Base: /p/MP694
With fit: /p/MP694?fit=Slim
With color: /p/MP694?color=white
With both: /p/MP694?fit=Slim&color=white
Mobile: /m/mens/.../MP694
```

### 3. **Class Names Change Frequently**
- `ProductDetailsTitle__name___1wYnq` - Generated hash changes
- Need to rely on data attributes like `data-testid`

### 4. **Lazy Loading**
- Images load as you scroll
- Some variants only load when selected
- Stock status updates via API calls

## Questions for ChatGPT

1. **Should we parse the `__INITIAL_STATE__` JavaScript object instead of clicking through the UI?**

2. **Is there a better way to handle the fit/color/size relationship without clicking each combination?**

3. **Should we use their internal API endpoints directly?** (e.g., `/api/v3/products/MP694/availability`)

4. **How to handle when they A/B test different page layouts?**

5. **Best practice for detecting and adapting to HTML structure changes?**
