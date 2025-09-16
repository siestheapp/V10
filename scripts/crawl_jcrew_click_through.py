#!/usr/bin/env python3
"""
Click through each J.Crew linen shirt product page to extract all color options
Acts exactly like a human browsing - visits each product page individually
"""

import time
import json
import sys
import os
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
except ImportError:
    print("❌ Selenium not installed! Run: pip install selenium")
    sys.exit(1)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_driver(headless=False):
    """Setup Chrome driver - visible by default to show progress"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_product_urls_from_listing(driver):
    """Get all product URLs from the listing page"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    print(f"🌐 Loading linen shirts listing page...")
    driver.get(url)
    
    # Wait for page load
    time.sleep(3)
    
    # Handle cookie banner
    try:
        cookie_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Accept')]")
        cookie_btn.click()
        time.sleep(1)
    except:
        pass
    
    print("📜 Scrolling to load all products...")
    
    # Scroll to load all products
    for i in range(5):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        time.sleep(1.5)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Extract product URLs
    product_urls = set()
    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
    
    for link in links:
        href = link.get_attribute('href')
        if href and '/p/' in href and 'categories/clothing/shirts' in href:
            clean_url = href.split('?')[0]
            product_urls.add(clean_url)
    
    print(f"✅ Found {len(product_urls)} unique product URLs")
    return list(product_urls)

def extract_colors_from_product_page(driver, product_url):
    """Visit a product page and extract all color options"""
    
    print(f"\n🔍 Visiting: {product_url.split('/')[-1]}")
    driver.get(product_url)
    
    # Wait for page to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h1, [data-testid='product-name']"))
        )
    except:
        time.sleep(3)
    
    product_data = {
        'url': product_url,
        'code': '',
        'name': '',
        'colors': [],
        'sizes': [],
        'fit_options': [],
        'price': '',
        'material': ''
    }
    
    # Extract product code from URL
    match = re.search(r'/([A-Z0-9]{4,6})(?:\?|$)', product_url)
    if match:
        product_data['code'] = match.group(1)
    
    # Extract product name
    try:
        name_elem = driver.find_element(By.CSS_SELECTOR, "h1, [data-testid='product-name'], .product-name")
        product_data['name'] = name_elem.text.strip()
    except:
        pass
    
    print(f"   Product: {product_data['name']}")
    
    # Extract all color options
    color_selectors = [
        "[data-testid*='color']",
        "[aria-label*='Color']",
        "[class*='color-swatch']",
        "[class*='color-button']",
        "[class*='color-selector']",
        "button[aria-label*='color']",
        ".color-chips button",
        "[role='button'][aria-label*='Color']"
    ]
    
    colors_found = []
    
    for selector in color_selectors:
        try:
            color_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in color_elements:
                try:
                    # Get color name from aria-label or title
                    color_name = elem.get_attribute('aria-label') or elem.get_attribute('title') or elem.text
                    
                    if color_name and len(color_name) < 100:  # Filter out long text
                        # Clean up color name (remove price if present)
                        color_name = color_name.split('$')[0].strip()
                        
                        # Get color code from data attributes
                        color_code = elem.get_attribute('data-color-code') or ''
                        
                        # Try to get swatch image
                        swatch_img = ''
                        try:
                            img = elem.find_element(By.TAG_NAME, "img")
                            swatch_img = img.get_attribute('src')
                        except:
                            # Check for background image
                            style = elem.get_attribute('style') or ''
                            if 'url(' in style:
                                img_match = re.search(r'url\(["\']?([^"\']+)["\']?\)', style)
                                if img_match:
                                    swatch_img = img_match.group(1)
                        
                        if color_name and color_name not in [c['name'] for c in colors_found]:
                            colors_found.append({
                                'name': color_name,
                                'code': color_code,
                                'image': swatch_img
                            })
                except:
                    continue
        except:
            continue
    
    # Alternative: Look for color names in JavaScript
    if len(colors_found) == 0:
        try:
            colors_js = driver.execute_script("""
                var colors = [];
                // Look for color data in various places
                var scripts = document.querySelectorAll('script');
                for (var i = 0; i < scripts.length; i++) {
                    var content = scripts[i].innerHTML;
                    if (content.includes('colors') || content.includes('swatches')) {
                        // Try to extract color names
                        var matches = content.match(/"color[^"]*":\\s*"([^"]+)"/gi);
                        if (matches) {
                            matches.forEach(function(m) {
                                var name = m.split(':')[1].replace(/"/g, '').trim();
                                if (name && name.length < 50) {
                                    colors.push({name: name});
                                }
                            });
                        }
                    }
                }
                return colors;
            """)
            if colors_js:
                for color in colors_js:
                    if color['name'] not in [c['name'] for c in colors_found]:
                        colors_found.append(color)
        except:
            pass
    
    product_data['colors'] = colors_found
    print(f"   Found {len(colors_found)} colors: {', '.join([c['name'] for c in colors_found[:5]])}")
    
    # Extract sizes
    try:
        size_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='size'], [aria-label*='Size'], button[class*='size']")
        sizes = []
        for elem in size_elements:
            size_text = elem.text.strip()
            if size_text and len(size_text) < 10 and size_text not in sizes:
                sizes.append(size_text)
        product_data['sizes'] = sizes
    except:
        pass
    
    # Extract fit options
    try:
        fit_elements = driver.find_elements(By.CSS_SELECTOR, "[data-testid*='fit'], [aria-label*='Fit'], button[class*='fit']")
        fits = []
        for elem in fit_elements:
            fit_text = elem.text.strip()
            if fit_text and fit_text not in fits and any(word in fit_text.lower() for word in ['classic', 'slim', 'tall', 'relaxed']):
                fits.append(fit_text)
        product_data['fit_options'] = fits
    except:
        pass
    
    # Extract price
    try:
        price_elem = driver.find_element(By.CSS_SELECTOR, "[data-testid*='price'], .product-price, [class*='price']")
        product_data['price'] = price_elem.text.strip()
    except:
        pass
    
    # Extract material
    try:
        details = driver.find_elements(By.CSS_SELECTOR, ".product-details li, [class*='fabric'], [class*='material']")
        for detail in details:
            text = detail.text.lower()
            if any(word in text for word in ['cotton', 'linen', 'wool', 'polyester']):
                product_data['material'] = detail.text.strip()
                break
    except:
        pass
    
    return product_data

def main():
    print("=" * 60)
    print("J.CREW LINEN SHIRTS - CLICK-THROUGH EXTRACTION")
    print("=" * 60)
    print("This will visit each product page to get all color options")
    print("Set headless=True to run in background, False to watch progress")
    print("=" * 60)
    
    # Setup browser (set headless=True to hide browser)
    driver = setup_driver(headless=False)  # Set to False so you can see it working!
    
    try:
        # Step 1: Get all product URLs from listing page
        product_urls = get_product_urls_from_listing(driver)
        
        if not product_urls:
            print("❌ No product URLs found")
            return
        
        # Step 2: Visit each product page
        print(f"\n📋 Will visit {len(product_urls)} product pages")
        print("This will take a few minutes...\n")
        
        all_products = []
        
        for i, url in enumerate(product_urls, 1):
            print(f"[{i}/{len(product_urls)}]", end='')
            
            try:
                product_data = extract_colors_from_product_page(driver, url)
                all_products.append(product_data)
                
                # Save progress periodically
                if i % 5 == 0:
                    with open('jcrew_linen_progress.json', 'w') as f:
                        json.dump(all_products, f, indent=2)
                    print(f"\n💾 Progress saved ({i}/{len(product_urls)})")
                
            except Exception as e:
                print(f"\n   ❌ Error on product {i}: {str(e)[:100]}")
            
            # Be polite - wait between requests
            time.sleep(2)
        
        # Save final results
        print("\n" + "=" * 60)
        print("EXTRACTION COMPLETE")
        print("=" * 60)
        
        if all_products:
            # Save full data
            with open('jcrew_linen_all_colors.json', 'w') as f:
                json.dump(all_products, f, indent=2)
            print(f"💾 Saved {len(all_products)} products to jcrew_linen_all_colors.json")
            
            # Statistics
            total_colors = sum(len(p['colors']) for p in all_products)
            products_with_multiple_colors = sum(1 for p in all_products if len(p['colors']) > 1)
            
            print(f"\n📊 SUMMARY:")
            print(f"   Total products: {len(all_products)}")
            print(f"   Total color variants: {total_colors}")
            print(f"   Products with multiple colors: {products_with_multiple_colors}")
            if len(all_products) > 0:
                print(f"   Average colors per product: {total_colors/len(all_products):.1f}")
            
            # Show sample
            print(f"\n🎨 SAMPLE PRODUCTS WITH COLORS:")
            for product in all_products[:3]:
                if product['colors']:
                    print(f"\n   {product['name']}")
                    print(f"   Code: {product['code']}")
                    print(f"   Colors ({len(product['colors'])}):")
                    for color in product['colors'][:5]:
                        print(f"      - {color['name']}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()
        print("✅ Done!")

if __name__ == "__main__":
    main()
