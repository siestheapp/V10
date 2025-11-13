# J.Crew Scraping Suite Documentation

## Overview
This suite consists of two specialized scrapers that extract accurate product data directly from J.Crew's website, with NO hardcoded fallbacks or assumptions. Each script serves a different purpose but both require URLs as input.

---

## 1. Individual Product Scraper (`scripts/precise_jcrew_html_scraper_v2.py`)

### Purpose
Scrapes **individual J.Crew product pages** to extract:
- Product name
- All available colors
- All fit options (e.g., Classic, Slim, Slim Untucked, Tall, Relaxed)

### Key Features
- **NO FALLBACKS**: Only extracts data actually present in the HTML
- Correctly handles multi-word fits like "Slim Untucked" as a single option
- Works for both multi-variant products (multiple colors/fits) and single-variant products
- Uses Selenium to handle JavaScript-rendered content
- Fails immediately if critical data (colors) can't be found

### Usage
```bash
# Single product
python scripts/precise_jcrew_html_scraper_v2.py https://www.jcrew.com/p/BE996

# Multiple products
python scripts/precise_jcrew_html_scraper_v2.py /p/CF667 /p/BW968 /p/CN406

# Full URL also works
python scripts/precise_jcrew_html_scraper_v2.py "https://www.jcrew.com/p/mens/categories/clothing/shirts/linen/baird-mcnutt-irish-linen-point-collar-shirt/CF667"
```

### Output
Returns JSON with:
```json
{
  "product_code": "BE996",
  "product_name": "Broken-in organic cotton oxford shirt",
  "url": "https://www.jcrew.com/p/BE996",
  "colors": ["WHITE", "RAINCOAT BLUE", ...],
  "color_count": 18,
  "fits": ["Classic", "Slim", "Slim Untucked", "Tall", "Relaxed"],
  "fit_count": 5,
  "scraped_at": "2025-09-16T15:38:39.123456"
}
```

### Important Notes
- **REQUIRES URL**: Will error and show usage if no URL provided
- For single-fit products, `fits` will be an empty array `[]`
- Colors are returned in UPPERCASE as found on the site

---

## 2. Category Page Scraper (`scripts/jcrew_category_scraper.py`)

### Purpose
Autonomously navigates J.Crew **category or subcategory pages**, clicking into each product listing to scrape detailed information for all products on that page.

### Key Features
- Finds all product links on a category page
- **Clicks into each product** individually (like a human browsing)
- Handles J.Crew Passport signup popups automatically
- Uses the same precise extraction logic as the individual scraper
- Supports optional limit for testing
- Saves results to timestamped JSON files

### Usage
```bash
# Scrape entire category
python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts"

# Scrape subcategory
python scripts/jcrew_category_scraper.py "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen"

# Limit for testing (scrape only first 5 products)
python scripts/jcrew_category_scraper.py "URL" 5
```

### Output
Saves to `jcrew_category_scrape_YYYYMMDD_HHMMSS.json`:
```json
{
  "category_url": "https://www.jcrew.com/plp/mens/categories/clothing/shirts?sub-categories=men-shirts-linen",
  "started_at": "2025-09-16T16:14:51.648465",
  "products": [
    {
      "url": "https://www.jcrew.com/p/...",
      "product_code": "CF667",
      "product_name": "",
      "colors": ["BENGAL STRIPE FLAX"],
      "fits": [],
      "error": null,
      "scraped_at": "2025-09-16T16:18:37.824642"
    },
    ...
  ],
  "summary": {
    "total_products": 4,
    "successful": 4,
    "failed": 0
  },
  "completed_at": "2025-09-16T16:22:37.304692",
  "duration_seconds": 465.656227
}
```

### Important Notes
- **REQUIRES URL**: Category page URL is mandatory
- Creates a new timestamped file for each run
- Will stop immediately if any product fails to scrape (no fallbacks)
- Shows progress as it scrapes each product

---

## Database Update Script (`scripts/update_db_from_scrape.py`)

### Purpose
Updates the database with results from the category scraper.

### Features
- Converts colors to proper title case (e.g., "WHITE" → "White")
- Correctly sets `fit_options` to empty array for single-fit products
- Includes verification of updates

### Usage
Edit the script to specify which JSON file to import, then:
```bash
python scripts/update_db_from_scrape.py
```

---

## Key Differences

| Aspect | Individual Product Scraper | Category Scraper |
|--------|---------------------------|------------------|
| **Input** | Individual product URL(s) | Category/subcategory page URL |
| **Process** | Direct scraping | Finds products, then clicks into each |
| **Output** | Console (JSON) | Timestamped JSON file |
| **Use Case** | Check specific products | Bulk scraping of category |
| **Speed** | Fast (single page) | Slower (navigates multiple pages) |

---

## Understanding Fit Options

### Products WITH Fit Options
Products like BE996 (Oxford shirts) have **clickable fit buttons** on the page:
- Classic, Slim, Slim Untucked, Tall, Relaxed
- These appear as `fits: ["Classic", "Slim", ...]` in results

### Products WITHOUT Fit Options  
Products like CF667 (many linen shirts) have **separate URLs for each fit**:
- `/CF667?fit=Classic` and `/CF667?fit=Tall` are different products
- These appear as `fits: []` (empty array) in results
- Each fit variant needs to be scraped as a separate product

---

## Error Handling

Both scripts follow a **fail-fast** philosophy:
- NO hardcoded fallbacks or default data
- If critical data (colors) can't be found, the script stops immediately
- This ensures data accuracy over completeness

---

## Tested Examples

Successfully tested on September 16, 2025:

1. **BE996** (Broken-in Oxford) - Multi-variant product
   - 18 colors found
   - 5 fit options including "Slim Untucked"

2. **CN406** (Corduroy with dogs) - Single-variant product  
   - 1 color: "DOG EMB BLUE BROWN"
   - 0 fit options (single fit)

3. **CF667** (Linen shirt) - Single-fit product
   - 1 color: "BENGAL STRIPE FLAX"
   - 0 fit options (fits are separate URLs)

---

## Requirements

- Python 3.x
- Selenium (`pip install selenium`)
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)
- psycopg2 (for database updates only)
