#!/usr/bin/env python3
"""
Test J.Crew category page to debug product discovery
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Setup driver (visible for debugging)
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)

# Test URL - men's shirts
url = "https://www.jcrew.com/c/mens/shirts"
print(f"Testing URL: {url}")

driver.get(url)
time.sleep(5)  # Let page fully load

# Try different selectors to find products
selectors_to_try = [
    'a[href*="/p/"]',           # Product links
    'a[href*="/p/mens/"]',       # Men's product links
    'article a',                 # Links within article tags
    '[data-testid*="product"] a',  # Product test IDs
    '.product-tile a',           # Product tiles
    '[class*="ProductCard"] a',  # Product card links
    'div[class*="product"] a',   # Product divs
]

print("\nTrying different selectors:")
for selector in selectors_to_try:
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    print(f"{selector}: Found {len(elements)} elements")
    
    # Show first few URLs if found
    if elements and len(elements) > 0:
        print("  Sample URLs:")
        for i, elem in enumerate(elements[:3]):
            href = elem.get_attribute('href')
            if href:
                print(f"    {i+1}. {href}")

# Also check the page title to make sure we're on the right page
print(f"\nPage title: {driver.title}")

# Check if there's a redirect or different URL structure
print(f"Current URL: {driver.current_url}")

# Look for any error messages
error_elements = driver.find_elements(By.CSS_SELECTOR, '[class*="error"], [class*="404"], [class*="not-found"]')
if error_elements:
    print("\n⚠️ Error elements found on page")

# Keep browser open for manual inspection
input("\nPress Enter to close browser...")
driver.quit()

