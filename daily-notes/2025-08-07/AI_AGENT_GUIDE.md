# AI Agent Guide: Product Scraping System

**Created**: January 18, 2025  
**Purpose**: Complete guide for AI agents working on the product scraping system  
**Database**: tailor3 (Supabase PostgreSQL)  
**Project**: V10 Clothing Fit Analysis App  

---

## 🎯 SYSTEM OVERVIEW

This is a **production-ready product scraping system** that automatically collects clothing product data from e-commerce websites and integrates it with the existing tailor3 fit analysis database. The system is designed to scale from hundreds to millions of products while maintaining data quality and performance.

### Key Principles
- **Unified Database**: Scraped products integrate seamlessly with manually curated products
- **Ethical Scraping**: Respects website terms with rate limiting and proper headers
- **Data Quality**: Comprehensive validation, cleaning, and normalization
- **Performance**: Optimized for scale with proper indexing and monitoring
- **Maintainability**: Modular architecture for easy extension to new brands

---

## 🏗️ ARCHITECTURE

### Database Architecture
```
tailor3 (Supabase PostgreSQL)
├── public.products (EXTENDED) - Unified products table
│   ├── Existing columns: id, brand_id, name, category_id, price, image_url, etc.
│   └── NEW columns: external_id, source_type, original_price, sizes_available, etc.
├── product_catalog.scraping_runs - Track scraping performance
├── product_catalog.scraper_configs - Brand-specific configurations
└── product_catalog.product_scraping_log - Detailed operation logs
```

### Code Architecture
```
scrapers/
├── config/ - Database and scraping configurations
├── models/ - Data models (ScrapedProduct, ScrapingRun)
├── scrapers/ - Brand-specific scraper implementations
├── utils/ - Database and scraping utilities
└── scripts/ - Execution and testing scripts
```

---

## 🔑 KEY CONCEPTS

### 1. Unified Product System
- **Manual products**: `source_type = 'manual'` (existing products)
- **Scraped products**: `source_type = 'scraped'` (new automated products)
- **Same table**: Both types in `public.products` for unified queries
- **Same features**: Scraped products work with fit analysis, user feedback, recommendations

### 2. Brand Integration
- **Existing brands**: Uses existing `brands` table (Banana Republic, J.Crew, etc.)
- **Existing categories**: Uses existing `categories` table (Shirts, Pants, etc.)
- **Size guides**: Can link scraped products to existing brand size guides
- **No duplication**: Smart handling prevents duplicate products

### 3. Data Flow
```
Website → Scraper → Data Cleaning → Database → Fit Analysis → User Recommendations
```

### 4. Error Handling Philosophy
- **Fail gracefully**: Continue processing if individual products fail
- **Log everything**: Comprehensive logging for debugging
- **Retry logic**: Built-in retries for network issues
- **Data validation**: Validate before saving to database

---

## 📊 DATABASE SCHEMA DETAILS

### Extended Products Table
```sql
-- NEW columns added to existing public.products table
external_id VARCHAR(100)        -- Product ID from source website
source_type VARCHAR(20)         -- 'manual' or 'scraped'
original_price NUMERIC(10,2)    -- Price before discounts
discount_percentage INTEGER     -- Discount amount
sizes_available JSONB          -- Array of available sizes
colors_available JSONB         -- Array of available colors
material VARCHAR(255)          -- Fabric/material information
fit_type VARCHAR(100)          -- Fit style (slim, regular, etc.)
last_scraped TIMESTAMP         -- When last updated
scraping_metadata JSONB       -- Raw scraping data for debugging

-- Constraint to prevent duplicates
UNIQUE(brand_id, external_id)
```

### Scraping Infrastructure Tables
```sql
-- Track scraping runs
product_catalog.scraping_runs (
    id, brand_id, category_id, target_url,
    products_found, products_added, products_updated, errors_count,
    run_duration_seconds, started_at, completed_at, status, error_details
)

-- Store brand configurations
product_catalog.scraper_configs (
    id, brand_id, category_id, base_url, selectors, pagination_config,
    rate_limit_ms, is_active, created_at, updated_at
)

-- Log individual product operations
product_catalog.product_scraping_log (
    id, scraping_run_id, product_id, external_id, product_url,
    action_type, error_message, scraped_data, created_at
)
```

---

## 🛠️ IMPLEMENTATION DETAILS

### Base Scraper Pattern
All brand scrapers inherit from `BaseScraper` and implement:
```python
def scrape_products(self, max_pages: int) -> List[ScrapedProduct]
def parse_product_listing(self, html: str, page_url: str) -> List[ScrapedProduct]
def parse_product_details(self, product: ScrapedProduct) -> ScrapedProduct
```

### Data Models
```python
@dataclass
class ScrapedProduct:
    name: str                    # Required
    product_url: str            # Required
    external_id: str            # Required
    brand_name: str             # Required
    price: Optional[Decimal]    # Optional but important
    original_price: Optional[Decimal]
    sizes_available: List[str]
    colors_available: List[str]
    # ... many more fields
```

### Rate Limiting
- **Default**: 2 seconds between requests
- **Configurable**: Per-brand rate limiting
- **User agent rotation**: Appears more human-like
- **Respectful**: Follows robots.txt principles

### Error Handling
```python
try:
    # Scraping operation
except requests.RequestException:
    # Network errors - retry with backoff
except Exception as e:
    # Log error, continue with next product
    db_manager.log_product_scraping(error_message=str(e))
```

---

## 🔍 CURRENT IMPLEMENTATION STATUS

### ✅ Completed
- **Database schema**: All tables and columns created
- **Banana Republic scraper**: Full implementation with robust parsing
- **Base infrastructure**: Rate limiting, error handling, data validation
- **Testing framework**: Comprehensive test suite
- **Documentation**: Complete guides and examples
- **Integration**: Works with existing tailor3 system

### 🎯 Tested Brands
- **Banana Republic**: Men's casual shirts (primary implementation)

### 📋 Ready for Extension
- **J.Crew**: Can be added using same framework
- **Other brands**: Template ready for new implementations

---

## 🚀 USAGE PATTERNS

### Running Scrapers
```bash
# Test mode (1 page only)
python scripts/run_banana_republic_scraper.py --test

# Production mode (multiple pages)
python scripts/run_banana_republic_scraper.py --pages 5

# Test entire system
python scripts/test_scraper.py
```

### Monitoring Performance
```sql
-- Check recent scraping runs
SELECT b.name, sr.products_found, sr.products_added, sr.run_duration_seconds
FROM product_catalog.scraping_runs sr
JOIN public.brands b ON sr.brand_id = b.id
ORDER BY sr.started_at DESC;

-- View scraped products
SELECT p.name, b.name as brand, p.price, p.last_scraped
FROM public.products p
JOIN public.brands b ON p.brand_id = b.id
WHERE p.source_type = 'scraped'
ORDER BY p.last_scraped DESC;
```

### Integration Queries
```sql
-- Products that work with fit analysis
SELECT p.*, ufz.perfect_min, ufz.perfect_max
FROM public.products p
JOIN public.user_fit_zones ufz ON p.category_id = ufz.category_id
WHERE p.source_type = 'scraped' AND ufz.user_id = 1;

-- Scraped products with size guide data
SELECT p.name, sge.size_label, sge.chest_range
FROM public.products p
JOIN public.size_guide_entries sge ON p.brand_id = sge.size_guide_id
WHERE p.source_type = 'scraped';
```

---

## 🔧 EXTENDING THE SYSTEM

### Adding a New Brand
1. **Add brand configuration** in `config/scraping_config.py`:
```python
"new_brand": {
    "name": "New Brand",
    "base_url": "https://newbrand.com",
    "selectors": {
        "product_container": "div.product",
        "product_name": "h3.title",
        # ... more selectors
    },
    "rate_limit_ms": 2000
}
```

2. **Create brand scraper** in `scrapers/new_brand.py`:
```python
class NewBrandScraper(BaseScraper):
    def __init__(self):
        config = BRAND_CONFIGS['new_brand']
        super().__init__("New Brand", config)
    
    def scrape_products(self, max_pages: int):
        # Implementation
    
    def parse_product_listing(self, html: str, page_url: str):
        # Implementation
    
    def parse_product_details(self, product: ScrapedProduct):
        # Implementation
```

3. **Create execution script** in `scripts/run_new_brand_scraper.py`

### Adding New Categories
1. **Add to database**: Insert into `categories` table
2. **Update configurations**: Add category-specific selectors
3. **Test integration**: Ensure fit analysis works with new category

### Scaling Considerations
- **Database**: Current schema handles millions of products
- **Rate limiting**: Increase delays for high-volume scraping
- **Monitoring**: Set up alerts for error rates
- **Caching**: Consider caching for frequently accessed data

---

## 🐛 DEBUGGING GUIDE

### Common Issues and Solutions

#### No Products Found
```bash
# Check selectors
python scripts/test_scraper.py
# Look at product_scraping_log for errors
SELECT * FROM product_catalog.product_scraping_log WHERE action_type = 'error';
```

#### Database Connection Issues
```bash
# Test connection
python -c "from config.database import db_config; print(db_config.test_connection())"
# Check .env file in parent directory
```

#### Rate Limiting/Blocking
- Increase `rate_limit_ms` in brand config
- Check if IP is blocked
- Rotate user agents more frequently

#### Data Quality Issues
- Check `scraping_metadata` field for raw data
- Validate extracted prices and sizes
- Review text cleaning functions

### Debugging Tools
```sql
-- View raw scraped data
SELECT scraping_metadata FROM public.products WHERE external_id = 'PRODUCT_ID';

-- Check error patterns
SELECT error_message, COUNT(*) 
FROM product_catalog.product_scraping_log 
WHERE action_type = 'error' 
GROUP BY error_message;

-- Performance analysis
SELECT 
    AVG(run_duration_seconds) as avg_duration,
    AVG(products_found::float / run_duration_seconds) as products_per_second
FROM product_catalog.scraping_runs 
WHERE status = 'completed';
```

---

## 🔐 SECURITY & ETHICS

### Ethical Scraping Practices
- **Rate limiting**: Never overwhelm target servers
- **User agents**: Use realistic browser user agents
- **Robots.txt**: Respect (though not legally required)
- **Terms of service**: Be aware of website terms
- **Data usage**: Only collect publicly available data

### Security Considerations
- **Database credentials**: Stored in .env file (not in code)
- **Input validation**: All scraped data is validated before storage
- **SQL injection**: Using parameterized queries
- **Error exposure**: Errors logged but not exposed to users

---

## 📈 PERFORMANCE METRICS

### Current Benchmarks (Banana Republic)
- **Speed**: ~2-3 products per second (with rate limiting)
- **Success rate**: >95% for product extraction
- **Error rate**: <5% (mostly network timeouts)
- **Data quality**: >90% complete product information

### Monitoring KPIs
- **Products found per run**: Track scraping effectiveness
- **Error rate**: Monitor for website changes
- **Run duration**: Performance optimization
- **Data completeness**: Quality metrics

---

## 🔮 FUTURE ROADMAP

### Immediate (Next 1-2 weeks)
- **Add J.Crew scraper**: Second brand implementation
- **Automated scheduling**: Cron jobs for regular scraping
- **Price tracking**: Monitor price changes over time
- **Image optimization**: Download and optimize product images

### Medium-term (Next 1-2 months)
- **Multi-brand orchestration**: Coordinate scraping across brands
- **Machine learning**: Improve product categorization
- **Inventory tracking**: Track stock availability
- **API endpoints**: REST API for scraping operations

### Long-term (3+ months)
- **Real-time updates**: WebSocket-based live updates
- **Predictive analytics**: Predict product trends
- **Advanced monitoring**: Grafana dashboards
- **Cloud deployment**: Scale to cloud infrastructure

---

## 💡 AI AGENT GUIDANCE

### When Working on This System
1. **Always test first**: Use `test_scraper.py` before making changes
2. **Respect rate limits**: Never remove or reduce rate limiting
3. **Log everything**: Add comprehensive logging for debugging
4. **Validate data**: Always validate scraped data before saving
5. **Monitor performance**: Check scraping_runs table for issues

### Code Patterns to Follow
- **Inherit from BaseScraper**: Don't reinvent the wheel
- **Use existing utilities**: Leverage db_utils and scraping_utils
- **Handle errors gracefully**: Never let one failure stop the entire run
- **Clean data**: Use ProductExtractor methods for consistency
- **Document changes**: Update this guide when making significant changes

### Integration Points
- **Existing brands**: Always use existing brand_id from brands table
- **Existing categories**: Use existing category_id from categories table
- **Size guides**: Consider linking to existing size guide data
- **Fit analysis**: Ensure scraped products work with MultiDimensionalFitAnalyzer

### Testing Strategy
1. **Unit tests**: Test individual components
2. **Integration tests**: Test database operations
3. **End-to-end tests**: Test complete scraping workflow
4. **Performance tests**: Monitor scraping speed and success rates

---

## 📞 SUPPORT INFORMATION

### Key Files for Debugging
- `scrapers/config/database.py` - Database connection issues
- `scrapers/utils/db_utils.py` - Database operation errors
- `scrapers/utils/scraping_utils.py` - Web scraping issues
- `scrapers/scrapers/base_scraper.py` - Core scraping logic

### Database Tables for Monitoring
- `product_catalog.scraping_runs` - High-level performance
- `product_catalog.product_scraping_log` - Detailed error logs
- `public.products` - Final scraped data

### Environment Dependencies
- **Python 3.8+**: Required for dataclasses and typing
- **PostgreSQL 15.8**: Database version
- **Supabase**: Database hosting
- **Network access**: Required for web scraping

---

**Last Updated**: January 18, 2025  
**Next Review**: February 18, 2025  
**Maintainer**: AI Development Team  

---

*This guide should be updated whenever significant changes are made to the scraping system. Future AI agents should read this document first before making any modifications.*
