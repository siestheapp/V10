# Product Scrapers

Automated product scraping system for e-commerce websites, integrated with the tailor3 database.

## Overview

This scraper system is designed to automatically collect product data from major clothing brands and integrate it with the existing tailor3 fit analysis system. The scraped products work seamlessly with the existing size guides, user feedback, and recommendation engine.

## Project Structure

```
scrapers/
├── config/                 # Configuration files
│   ├── database.py        # Database connection config
│   └── scraping_config.py # Scraping settings and brand configs
├── models/                # Data models
│   └── product.py         # Product and scraping run models
├── scrapers/              # Scraper implementations
│   ├── base_scraper.py    # Abstract base class
│   └── banana_republic.py # Banana Republic scraper
├── utils/                 # Utility functions
│   ├── db_utils.py        # Database operations
│   └── scraping_utils.py  # Web scraping utilities
├── scripts/               # Execution scripts
│   ├── run_banana_republic_scraper.py  # Main scraper runner
│   └── test_scraper.py    # Test suite
├── tests/                 # Unit tests
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Setup

### 1. Install Dependencies

```bash
cd scrapers
pip install -r requirements.txt
```

### 2. Environment Configuration

Ensure your `.env` file in the parent directory contains:

```env
DB_HOST=aws-0-us-east-2.pooler.supabase.com
DB_PORT=6543
DB_NAME=postgres
DB_USER=postgres.lbilxlkchzpducggkrxx
DB_PASSWORD=efvTower12
```

### 3. Database Setup

The database schema has been automatically configured with:
- Extended `products` table with scraping columns
- New `product_catalog` schema with scraping infrastructure
- Performance indexes and constraints

## Usage

### Test the System

```bash
# Run comprehensive test suite
python scripts/test_scraper.py

# Test scrape (1 page only)
python scripts/run_banana_republic_scraper.py --test
```

### Run Full Scraping

```bash
# Scrape 3 pages (recommended for testing)
python scripts/run_banana_republic_scraper.py --pages 3

# Scrape 5 pages (production)
python scripts/run_banana_republic_scraper.py --pages 5

# Verbose output
python scripts/run_banana_republic_scraper.py --pages 3 --verbose
```

## Features

### Robust Scraping
- **Rate limiting**: Respects website terms with configurable delays
- **Error handling**: Comprehensive error handling and retry logic
- **Multiple selectors**: Tries multiple CSS selectors for reliability
- **User agent rotation**: Rotates user agents to avoid detection

### Database Integration
- **Unified products table**: Scraped products integrate with existing manual products
- **Duplicate prevention**: Prevents duplicate products using brand + external_id
- **Performance tracking**: Tracks scraping runs, success rates, and errors
- **Audit logging**: Complete audit trail of all scraping activities

### Data Quality
- **Price extraction**: Handles various price formats and discounts
- **Size normalization**: Standardizes size formats (XS, S, M, L, XL)
- **Text cleaning**: Removes unwanted characters and normalizes text
- **Image handling**: Extracts and normalizes image URLs

### Monitoring
- **Run tracking**: Each scraping session is tracked with metrics
- **Error logging**: Detailed error logging for debugging
- **Performance metrics**: Duration, success rates, products found/added/updated

## Database Schema

### Extended Products Table
The existing `products` table has been extended with:
- `external_id` - Product ID from source website
- `source_type` - 'manual' or 'scraped'
- `original_price` - Price before discounts
- `discount_percentage` - Discount amount
- `sizes_available` - JSON array of sizes
- `colors_available` - JSON array of colors
- `material` - Fabric/material information
- `fit_type` - Fit style (slim, regular, etc.)
- `last_scraped` - When last updated
- `scraping_metadata` - Raw scraping data

### New Tables
- `product_catalog.scraping_runs` - Track scraping performance
- `product_catalog.scraper_configs` - Store brand-specific settings
- `product_catalog.product_scraping_log` - Debug individual products

## Brand Configuration

Brands are configured in `config/scraping_config.py`:

```python
BRAND_CONFIGS = {
    "banana_republic": {
        "name": "Banana Republic",
        "base_url": "https://bananarepublic.gap.com",
        "selectors": {
            "product_container": "div[data-testid='product-tile']",
            "product_name": "h3[data-testid='product-title']",
            # ... more selectors
        },
        "rate_limit_ms": 2000
    }
}
```

## Adding New Brands

1. **Add brand configuration** in `config/scraping_config.py`
2. **Create brand scraper** inheriting from `BaseScraper`
3. **Implement required methods**:
   - `scrape_products()`
   - `parse_product_listing()`
   - `parse_product_details()`
4. **Create execution script** similar to `run_banana_republic_scraper.py`

## Monitoring and Debugging

### Check Scraping Performance
```sql
SELECT 
    b.name as brand,
    sr.products_found,
    sr.products_added,
    sr.run_duration_seconds,
    sr.started_at
FROM product_catalog.scraping_runs sr
JOIN public.brands b ON sr.brand_id = b.id
ORDER BY sr.started_at DESC;
```

### View Scraped Products
```sql
SELECT 
    p.name,
    b.name as brand,
    p.price,
    p.original_price,
    p.last_scraped
FROM public.products p
JOIN public.brands b ON p.brand_id = b.id
WHERE p.source_type = 'scraped'
ORDER BY p.last_scraped DESC;
```

### Debug Errors
```sql
SELECT 
    psl.external_id,
    psl.error_message,
    psl.created_at
FROM product_catalog.product_scraping_log psl
WHERE psl.action_type = 'error'
ORDER BY psl.created_at DESC;
```

## Best Practices

### Rate Limiting
- Default 2-second delay between requests
- Respect robots.txt and website terms
- Use random delays to appear more human-like

### Error Handling
- Always handle network timeouts
- Log errors for debugging
- Continue processing other products if one fails

### Data Quality
- Validate extracted data before saving
- Handle missing or malformed data gracefully
- Clean and normalize text data

### Monitoring
- Track scraping performance metrics
- Set up alerts for high error rates
- Monitor for website structure changes

## Troubleshooting

### Common Issues

1. **No products found**
   - Website structure may have changed
   - Check CSS selectors in brand config
   - Run test script to debug

2. **Database connection failed**
   - Check `.env` file configuration
   - Verify database credentials
   - Test connection with `test_scraper.py`

3. **Rate limiting/blocking**
   - Increase delay between requests
   - Rotate user agents
   - Check if IP is blocked

4. **Missing brand/category**
   - Ensure brand exists in `brands` table
   - Add category to `categories` table if needed

### Debug Mode
Run with verbose output to see detailed logs:
```bash
python scripts/run_banana_republic_scraper.py --pages 1 --verbose
```

## Integration with Existing System

Scraped products automatically integrate with:
- **Fit Analysis**: `MultiDimensionalFitAnalyzer` works with scraped products
- **Size Guides**: Can link scraped products to existing brand size guides
- **User Feedback**: Users can rate scraped products same as manual ones
- **Recommendations**: Scraped products feed into recommendation engine

## Future Enhancements

- **Automated scheduling**: Daily/weekly scraping with cron jobs
- **Price tracking**: Monitor price changes over time
- **Inventory tracking**: Track stock availability
- **Image processing**: Download and optimize product images
- **Machine learning**: Improve product categorization
- **Multi-brand orchestration**: Coordinate scraping across multiple brands
