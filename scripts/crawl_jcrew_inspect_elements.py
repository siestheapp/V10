#!/usr/bin/env python3
"""
Inspect J.Crew page elements exactly like using Chrome DevTools
Mimics the manual process of inspecting, clicking, and extracting data
"""

import time
import json
import sys
import os
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("❌ Selenium not installed! Run: pip install selenium")
    sys.exit(1)

def setup_driver(headless=False):
    """Setup Chrome driver with DevTools capabilities"""
    chrome_options = Options()
    
    if headless:
        chrome_options.add_argument("--headless")
    
    # Enable DevTools Protocol
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--auto-open-devtools-for-tabs")  # Auto-open DevTools
    
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def inspect_page_structure(driver):
    """Inspect the page structure to understand the DOM"""
    
    print("\n🔍 INSPECTING PAGE STRUCTURE (like Chrome DevTools)...")
    
    # Get the full HTML to understand structure
    html = driver.page_source
    
    # Use JavaScript to inspect the DOM structure
    structure = driver.execute_script("""
        // Inspect the page structure
        var result = {
            products: [],
            selectors: {},
            structure: {}
        };
        
        // Find all anchor tags with product links
        var productLinks = document.querySelectorAll('a[href*="/p/"]');
        console.log('Found ' + productLinks.length + ' product links');
        
        // Analyze each product link
        productLinks.forEach(function(link) {
            // Get parent elements to understand structure
            var parent = link.parentElement;
            var grandparent = parent ? parent.parentElement : null;
            var greatGrandparent = grandparent ? grandparent.parentElement : null;
            
            // Extract product info
            var productInfo = {
                href: link.href,
                classes: link.className,
                parentClasses: parent ? parent.className : '',
                grandparentClasses: grandparent ? grandparent.className : '',
                // Look for product name
                productName: '',
                // Look for price
                price: '',
                // Look for image
                image: ''
            };
            
            // Find product name
            var nameElement = link.querySelector('h3, h4, [class*="name"], [class*="title"]');
            if (!nameElement && parent) {
                nameElement = parent.querySelector('h3, h4, [class*="name"], [class*="title"]');
            }
            if (!nameElement && grandparent) {
                nameElement = grandparent.querySelector('h3, h4, [class*="name"], [class*="title"]');
            }
            if (nameElement) {
                productInfo.productName = nameElement.textContent.trim();
            }
            
            // Find image
            var img = link.querySelector('img');
            if (!img && parent) {
                img = parent.querySelector('img');
            }
            if (img) {
                productInfo.image = img.src;
            }
            
            // Find price
            var priceElement = parent ? parent.querySelector('[class*="price"]') : null;
            if (!priceElement && grandparent) {
                priceElement = grandparent.querySelector('[class*="price"]');
            }
            if (priceElement) {
                productInfo.price = priceElement.textContent.trim();
            }
            
            result.products.push(productInfo);
        });
        
        // Find common selectors
        result.selectors = {
            productTiles: document.querySelectorAll('[class*="product-tile"], [class*="product-card"], article').length,
            productLinks: document.querySelectorAll('a[href*="/p/"]').length,
            images: document.querySelectorAll('img[src*="jcrew.com"]').length,
            buttons: document.querySelectorAll('button').length
        };
        
        return result;
    """)
    
    return structure

def extract_products_from_listing(driver):
    """Extract all products from the listing page by inspecting elements"""
    
    url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"
    print(f"\n🌐 Opening J.Crew linen shirts page...")
    driver.get(url)
    
    # Wait for page to load
    time.sleep(4)
    
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
        driver.execute_script("window.scrollBy(0, 800);")
        time.sleep(1)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # Inspect the page structure
    structure = inspect_page_structure(driver)
    
    print(f"\n📊 PAGE INSPECTION RESULTS:")
    print(f"   Product tiles found: {structure['selectors']['productTiles']}")
    print(f"   Product links found: {structure['selectors']['productLinks']}")
    print(f"   Images found: {structure['selectors']['images']}")
    
    # Extract detailed product information using element inspection
    print("\n🔍 EXTRACTING PRODUCT DATA (inspecting each element)...")
    
    products = driver.execute_script("""
        // Extract all product data by inspecting elements
        var products = [];
        var seen = new Set();
        
        // Method 1: Find all product links
        document.querySelectorAll('a[href*="/p/"]').forEach(function(link) {
            var href = link.href;
            if (!href.includes('/mens/')) return;
            
            // Extract product code
            var codeMatch = href.match(/\/([A-Z0-9]{4,6})(\\?|$)/);
            if (!codeMatch) return;
            
            var code = codeMatch[1];
            if (seen.has(code)) return;
            seen.add(code);
            
            // Get the product container (traverse up the DOM)
            var container = link.closest('article, [class*="product"], li');
            
            var product = {
                code: code,
                url: href.split('?')[0],
                name: '',
                price: '',
                image: '',
                colors: []
            };
            
            // Find product name (inspect various possible locations)
            var nameSelectors = ['h3', 'h4', '[class*="name"]', '[class*="title"]', '[data-testid*="name"]'];
            for (var i = 0; i < nameSelectors.length; i++) {
                var nameEl = container ? container.querySelector(nameSelectors[i]) : null;
                if (nameEl) {
                    product.name = nameEl.textContent.trim();
                    break;
                }
            }
            
            // Find image
            var img = container ? container.querySelector('img') : null;
            if (img) {
                product.image = img.src || img.dataset.src || '';
            }
            
            // Find price
            var priceEl = container ? container.querySelector('[class*="price"]') : null;
            if (priceEl) {
                product.price = priceEl.textContent.trim();
            }
            
            // Try to find color swatches on the listing page
            if (container) {
                var colorSwatches = container.querySelectorAll('[class*="color"], [aria-label*="Color"]');
                colorSwatches.forEach(function(swatch) {
                    var colorName = swatch.getAttribute('aria-label') || swatch.getAttribute('title') || '';
                    if (colorName && !colorName.includes('List')) {
                        product.colors.push(colorName);
                    }
                });
            }
            
            products.push(product);
        });
        
        // Method 2: Also check for products in structured data
        var scripts = document.querySelectorAll('script[type="application/ld+json"]');
        scripts.forEach(function(script) {
            try {
                var data = JSON.parse(script.textContent);
                if (data['@graph']) {
                    data['@graph'].forEach(function(item) {
                        if (item['@type'] === 'Product') {
                            // Extract product info from structured data
                            var url = item.url || '';
                            var codeMatch = url.match(/\/([A-Z0-9]{4,6})(\\?|$)/);
                            if (codeMatch) {
                                var code = codeMatch[1];
                                if (!seen.has(code)) {
                                    seen.add(code);
                                    products.push({
                                        code: code,
                                        url: url,
                                        name: item.name || '',
                                        price: item.offers ? item.offers.price : '',
                                        image: item.image || '',
                                        colors: []
                                    });
                                }
                            }
                        }
                    });
                }
            } catch(e) {}
        });
        
        console.log('Total products found:', products.length);
        return products;
    """)
    
    print(f"\n✅ Found {len(products)} products by inspecting elements")
    
    return products

def inspect_product_page_for_colors(driver, product_url):
    """Open a product page and inspect elements to find all colors"""
    
    print(f"\n🔍 Inspecting product page: {product_url.split('/')[-1]}")
    driver.get(product_url)
    
    # Wait for page load
    time.sleep(3)
    
    # Inspect the page for color information
    color_data = driver.execute_script("""
        // Inspect the product page for all color options
        var colors = [];
        var seen = new Set();
        
        // Method 1: Find color swatches
        var swatchSelectors = [
            '[data-testid*="color"]',
            '[aria-label*="Color"]',
            '[class*="color-swatch"]',
            '[class*="color-selector"]',
            '[class*="color-chip"]',
            'button[aria-label*="Color"]',
            '[role="button"][aria-label*="Color"]'
        ];
        
        swatchSelectors.forEach(function(selector) {
            document.querySelectorAll(selector).forEach(function(element) {
                // Get color name
                var colorName = element.getAttribute('aria-label') || 
                               element.getAttribute('title') || 
                               element.getAttribute('data-color') ||
                               element.textContent.trim();
                
                if (colorName && !seen.has(colorName) && !colorName.includes('List')) {
                    seen.add(colorName);
                    
                    var colorInfo = {
                        name: colorName.split('$')[0].trim(),
                        code: element.getAttribute('data-color-code') || '',
                        image: ''
                    };
                    
                    // Find swatch image
                    var img = element.querySelector('img');
                    if (img) {
                        colorInfo.image = img.src || img.dataset.src || '';
                    } else {
                        // Check for background image
                        var style = window.getComputedStyle(element);
                        var bgImage = style.backgroundImage;
                        if (bgImage && bgImage !== 'none') {
                            var match = bgImage.match(/url\\(["']?([^"']+)["']?\\)/);
                            if (match) {
                                colorInfo.image = match[1];
                            }
                        }
                    }
                    
                    colors.push(colorInfo);
                }
            });
        });
        
        // Method 2: Look in JavaScript objects
        if (window.__NEXT_DATA__) {
            try {
                var str = JSON.stringify(window.__NEXT_DATA__);
                var colorMatches = str.match(/"color[^"]*":\\s*"([^"]+)"/gi) || [];
                colorMatches.forEach(function(match) {
                    var color = match.split(':')[1].replace(/"/g, '').trim();
                    if (color && !seen.has(color) && color.length < 50) {
                        seen.add(color);
                        colors.push({name: color, code: '', image: ''});
                    }
                });
            } catch(e) {}
        }
        
        // Get other product info
        var productInfo = {
            name: '',
            price: '',
            sizes: [],
            fits: []
        };
        
        // Get product name
        var nameEl = document.querySelector('h1, [data-testid="product-name"]');
        if (nameEl) productInfo.name = nameEl.textContent.trim();
        
        // Get price
        var priceEl = document.querySelector('[data-testid*="price"], [class*="price"]');
        if (priceEl) productInfo.price = priceEl.textContent.trim();
        
        // Get sizes
        document.querySelectorAll('[data-testid*="size"], button[aria-label*="Size"]').forEach(function(el) {
            var size = el.textContent.trim();
            if (size && size.length < 10 && !productInfo.sizes.includes(size)) {
                productInfo.sizes.push(size);
            }
        });
        
        // Get fit options
        document.querySelectorAll('[data-testid*="fit"], button[aria-label*="Fit"]').forEach(function(el) {
            var fit = el.textContent.trim();
            if (fit && !productInfo.fits.includes(fit)) {
                productInfo.fits.push(fit);
            }
        });
        
        return {
            colors: colors,
            productInfo: productInfo
        };
    """)
    
    return color_data

def main():
    print("=" * 60)
    print("J.CREW ELEMENT INSPECTOR")
    print("Mimics manual inspection with Chrome DevTools")
    print("=" * 60)
    
    # Setup driver (visible so you can see it working)
    driver = setup_driver(headless=False)
    
    try:
        # Step 1: Extract all products from listing page
        products = extract_products_from_listing(driver)
        
        if not products:
            print("❌ No products found")
            return
        
        # Display what we found
        print("\n📋 PRODUCTS FOUND ON LISTING PAGE:")
        for i, product in enumerate(products[:10], 1):
            print(f"   {i}. {product['code']}: {product['name'][:50] if product['name'] else 'No name'}")
        if len(products) > 10:
            print(f"   ... and {len(products) - 10} more")
        
        # Save initial extraction
        with open('jcrew_linen_inspection_raw.json', 'w') as f:
            json.dump(products, f, indent=2)
        print(f"\n💾 Saved raw inspection to jcrew_linen_inspection_raw.json")
        
        # Step 2: Visit each product page to get all colors
        print(f"\n📸 INSPECTING EACH PRODUCT PAGE FOR COLORS...")
        print(f"Will visit {len(products)} product pages")
        
        complete_products = []
        
        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{len(products)}]", end='')
            
            try:
                color_data = inspect_product_page_for_colors(driver, product['url'])
                
                # Merge data
                product['colors'] = color_data['colors']
                product['name'] = color_data['productInfo']['name'] or product['name']
                product['price'] = color_data['productInfo']['price'] or product['price']
                product['sizes'] = color_data['productInfo']['sizes']
                product['fits'] = color_data['productInfo']['fits']
                
                complete_products.append(product)
                
                print(f" {product['name'][:40]}")
                print(f"   Colors found: {len(color_data['colors'])}")
                if color_data['colors']:
                    for color in color_data['colors'][:3]:
                        print(f"      - {color['name']}")
                
                # Save progress
                if i % 5 == 0:
                    with open('jcrew_linen_inspection_progress.json', 'w') as f:
                        json.dump(complete_products, f, indent=2)
                    print(f"\n💾 Progress saved ({i}/{len(products)})")
                
            except Exception as e:
                print(f" ❌ Error: {str(e)[:50]}")
            
            # Be polite
            time.sleep(2)
        
        # Save final results
        with open('jcrew_linen_inspection_complete.json', 'w') as f:
            json.dump(complete_products, f, indent=2)
        
        print("\n" + "=" * 60)
        print("INSPECTION COMPLETE")
        print("=" * 60)
        print(f"💾 Saved {len(complete_products)} products to jcrew_linen_inspection_complete.json")
        
        # Statistics
        total_colors = sum(len(p['colors']) for p in complete_products)
        products_with_colors = sum(1 for p in complete_products if len(p['colors']) > 1)
        
        print(f"\n📊 SUMMARY:")
        print(f"   Products inspected: {len(complete_products)}")
        print(f"   Total colors found: {total_colors}")
        print(f"   Products with multiple colors: {products_with_colors}")
        if len(complete_products) > 0:
            print(f"   Average colors per product: {total_colors/len(complete_products):.1f}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()

