#!/usr/bin/env python3
"""
Accurate Oxford color scraper - Better color detection
"""

import time
import re
from datetime import datetime

def setup_selenium():
    """Setup Selenium with Chrome"""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("❌ Selenium not installed!")
        return None, None
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver, (By, WebDriverWait, EC)
    except Exception as e:
        print(f"❌ Failed: {e}")
        return None, None

def scrape_be996_colors(driver, selenium_imports):
    """Focus on BE996 to get accurate color count"""
    By, WebDriverWait, EC = selenium_imports
    
    url = "https://www.jcrew.com/p/mens/categories/clothing/shirts/broken-in-oxford/broken-in-organic-cotton-oxford-shirt/BE996"
    
    print(f"🔗 Loading BE996 product page...")
    driver.get(url)
    time.sleep(5)  # Let page fully load
    
    print("\n🔍 Searching for color options with multiple methods...")
    
    colors_found = set()
    
    # Method 1: Look for all button elements with color-related attributes
    print("\nMethod 1: Color buttons...")
    color_buttons = driver.find_elements(By.CSS_SELECTOR, "button")
    for btn in color_buttons:
        aria_label = btn.get_attribute('aria-label')
        if aria_label and 'color' in aria_label.lower():
            colors_found.add(aria_label)
            print(f"   Found: {aria_label}")
    
    # Method 2: Look for color swatches by class patterns
    print("\nMethod 2: Color swatch classes...")
    swatch_patterns = [
        "[class*='color']",
        "[class*='Color']", 
        "[class*='swatch']",
        "[class*='Swatch']",
        "button[style*='background']",  # Color might be in style
        "label[for*='color']"
    ]
    
    for pattern in swatch_patterns:
        swatches = driver.find_elements(By.CSS_SELECTOR, pattern)
        if swatches:
            print(f"   Found {len(swatches)} elements with pattern: {pattern}")
    
    # Method 3: Look for image elements (color thumbnails)
    print("\nMethod 3: Color images...")
    color_images = driver.find_elements(By.CSS_SELECTOR, "img[alt]")
    for img in color_images:
        alt = img.get_attribute('alt')
        if alt and ('color' in alt.lower() or 'Color' in alt):
            colors_found.add(alt)
    
    # Method 4: Check radio inputs (colors might be radio buttons)
    print("\nMethod 4: Radio/input elements...")
    inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")
    for inp in inputs:
        name = inp.get_attribute('name')
        value = inp.get_attribute('value')
        id_attr = inp.get_attribute('id')
        if 'color' in str(name).lower() or 'color' in str(id_attr).lower():
            colors_found.add(value or id_attr)
    
    # Method 5: Look in the page source for color data
    print("\nMethod 5: Page source analysis...")
    page_source = driver.page_source
    
    # Look for color arrays in JavaScript
    color_pattern = r'"colors?":\s*\[(.*?)\]'
    matches = re.findall(color_pattern, page_source, re.IGNORECASE)
    for match in matches[:3]:  # Show first 3 matches
        print(f"   Found color data: {match[:100]}...")
    
    # Method 6: Count visible color elements specifically
    print("\nMethod 6: Visible clickable colors...")
    
    # Try different selectors that J.Crew might use
    specific_selectors = [
        ".product-detail__color-chips button",
        ".product__colors button",
        "[data-testid='color-selector'] button",
        ".color-selector button",
        ".ProductColorSwatches button",
        "div[class*='ColorSelector'] button",
        "div[class*='color'] button[aria-label]"
    ]
    
    for selector in specific_selectors:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        if elements:
            print(f"   ✅ Found {len(elements)} colors with selector: {selector}")
            for elem in elements[:3]:  # Show first 3
                label = elem.get_attribute('aria-label') or elem.text
                if label:
                    print(f"      - {label}")
            break
    
    # Method 7: Execute JavaScript to find colors
    print("\nMethod 7: JavaScript inspection...")
    try:
        # Count all buttons that look like color swatches
        color_count = driver.execute_script("""
            const buttons = document.querySelectorAll('button');
            let colorButtons = 0;
            buttons.forEach(btn => {
                const ariaLabel = btn.getAttribute('aria-label');
                const style = btn.getAttribute('style');
                if ((ariaLabel && ariaLabel.toLowerCase().includes('color')) || 
                    (style && style.includes('background'))) {
                    colorButtons++;
                }
            });
            return colorButtons;
        """)
        print(f"   JavaScript found {color_count} color-like buttons")
    except:
        pass
    
    print("\n" + "="*60)
    print(f"Total unique colors found: {len(colors_found)}")
    if colors_found:
        for color in list(colors_found)[:5]:
            print(f"   • {color}")

def main():
    print("="*80)
    print("ACCURATE OXFORD COLOR DETECTION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    driver, selenium_imports = setup_selenium()
    
    if not driver:
        return
    
    try:
        scrape_be996_colors(driver, selenium_imports)
        
        print("\n📋 Note: You mentioned seeing 18 colors for BE996")
        print("   If we're not detecting them all, the colors might be:")
        print("   • Loaded dynamically after scrolling")
        print("   • In a carousel that needs interaction")
        print("   • Behind a 'View More Colors' button")
        print("   • Rendered differently for headless browsers")
        
    finally:
        driver.quit()
        print("\n🔚 Browser closed")

if __name__ == "__main__":
    main()
