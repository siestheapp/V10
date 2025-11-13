#!/usr/bin/env python3
"""Debug why cotton-cashmere subcategory isn't finding products"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Setup driver (visible for debugging)
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

# Test URL - cotton-cashmere shirts
url = "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=mens-shirts-cotton-cashmere"
print(f"Testing URL: {url}")

driver.get(url)
time.sleep(5)  # Let page fully load

# Check if page redirected
print(f"Current URL: {driver.current_url}")
print(f"Page title: {driver.title}")

# Try to find products with various selectors
selectors = [
    'a[href*="/p/mens/"]',
    'a[href*="/p/"]',
    'article',
    '[data-testid*="product"]',
    '.product-tile',
    'div[class*="ProductCard"]',
    'img[alt*="mens"]'
]

for selector in selectors:
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    if elements:
        print(f"{selector}: Found {len(elements)} elements")
        if len(elements) > 0 and 'href' in selector:
            # Show first URL
            href = elements[0].get_attribute('href')
            if href:
                print(f"  First URL: {href}")

# Check page source for product codes
page_source = driver.page_source
if 'Cotton-cashmere' in page_source:
    print("\n✓ Found 'Cotton-cashmere' in page source")
else:
    print("\n✗ 'Cotton-cashmere' NOT found in page source")

# Look for any error or empty state messages
empty_state = driver.find_elements(By.CSS_SELECTOR, '[class*="empty"], [class*="no-results"]')
if empty_state:
    print("\n⚠️ Empty state found on page")

input("\nPress Enter to close browser...")
driver.quit()

