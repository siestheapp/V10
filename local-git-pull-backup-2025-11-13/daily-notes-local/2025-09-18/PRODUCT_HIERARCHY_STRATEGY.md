# Product Hierarchy Strategy for Multi-Brand Scaling

## The Problem
Different brands organize products differently:
- **J.Crew**: Master products (MP600) with color variants (BE164, BE163)
- **Reiss**: Style codes with size/color variants
- **Uniqlo**: Base products with color codes
- **Zara**: Constantly changing SKUs with no stable master

## Proposed Solution: Unified Product Model

### 1. Database Structure (Already Have This!)
```
brands
  ↓
product_master (base product)
  ↓
product_variants (specific SKU/color/size combos)
  ↓
user_garments (what user actually bought)
```

### 2. Smart Product Deduplication System

```python
class ProductDeduplicator:
    """
    Intelligent system to determine if a product is:
    - A new master product
    - A variant of existing product
    - A duplicate entry
    """
    
    def identify_product(self, scraped_data, brand_id):
        # Strategy varies by brand
        if brand_id == 4:  # J.Crew
            return self._jcrew_strategy(scraped_data)
        elif brand_id == 10:  # Reiss
            return self._reiss_strategy(scraped_data)
        # ... etc
    
    def _jcrew_strategy(self, data):
        """
        J.Crew specific rules:
        - MP*/ME* codes = master products
        - BE*/BK*/etc = color variants
        - Same name = likely same product
        """
        rules = {
            'master_patterns': [r'^M[EP]\d{3}$'],
            'variant_patterns': [r'^B[A-Z]\d{3,4}$'],
            'name_similarity_threshold': 0.85
        }
        # ... implementation
```

### 3. Product Matching Pipeline

```
SCRAPE → EXTRACT → IDENTIFY → DEDUPE → INGEST
         ↓          ↓          ↓        ↓
      Get data   Master or   Find     Add to
      from page   variant?   existing   database
```

### 4. Key Design Principles

#### A. Flexible Product Codes
```sql
-- Allow multiple codes per product
CREATE TABLE product_codes (
    id SERIAL PRIMARY KEY,
    product_master_id INT REFERENCES product_master(id),
    code_type VARCHAR(50), -- 'master', 'variant', 'sku', 'style'
    code_value VARCHAR(50),
    is_primary BOOLEAN DEFAULT FALSE,
    UNIQUE(product_master_id, code_type, code_value)
);
```

#### B. Fuzzy Matching for Deduplication
```python
def find_similar_products(name, brand_id, threshold=0.85):
    """
    Use multiple strategies:
    1. Exact code match
    2. Name similarity (Levenshtein distance)
    3. Description overlap
    4. Price range similarity
    """
```

#### C. Brand-Specific Adapters
```python
class BrandAdapter(ABC):
    @abstractmethod
    def extract_master_code(self, url, html): pass
    
    @abstractmethod
    def extract_variant_info(self, html): pass
    
    @abstractmethod
    def should_merge(self, existing, new): pass

class JCrewAdapter(BrandAdapter):
    def extract_master_code(self, url, html):
        # Try URL first, then page content
        # Handle MP/ME codes specially
        
class ReissAdapter(BrandAdapter):
    # Different logic for Reiss
```

### 5. Implementation Plan

#### Phase 1: Fix Current Data
```python
# Merge duplicates in J.Crew products
def consolidate_jcrew_products():
    # Find products with same name
    # Keep master code (MP*) as primary
    # Move others as variants
```

#### Phase 2: Update Scraper
```python
class SmartProductScraper:
    def __init__(self, brand_adapter):
        self.adapter = brand_adapter
        self.deduplicator = ProductDeduplicator()
    
    def scrape_and_ingest(self, url):
        data = self.extract_data(url)
        
        # Check if exists
        master = self.deduplicator.find_master(data)
        
        if master:
            # Add as variant
            self.add_variant(master, data)
        else:
            # Create new master
            self.create_master(data)
```

#### Phase 3: Add Learning System
```python
# Learn from corrections
class ProductMatcher:
    def learn_from_merge(self, product1, product2):
        # Store patterns that indicate same product
        # Improve future matching
```

## Benefits of This Approach

1. **Scalable**: Works for any brand hierarchy
2. **Flexible**: Adapts to different product structures  
3. **Intelligent**: Learns from patterns
4. **Maintainable**: Clear separation of concerns
5. **Accurate**: Reduces duplicates while preserving variants

## Quick Wins for Now

1. **Add similarity checking** to scraper
2. **Create brand adapters** for J.Crew and Reiss
3. **Log uncertain matches** for manual review
4. **Build confidence scoring** for auto-merge

## Database Changes Needed

None! Current structure supports this:
- `product_master` = base products
- `product_variants` = SKUs/colors/sizes
- Just need smarter ingestion logic

## Example: J.Crew Implementation

```python
def ingest_jcrew_product(scraped_data):
    # 1. Extract all possible codes
    codes = extract_all_codes(scraped_data)  # ['MP600', 'BE164']
    
    # 2. Check if any exist
    existing = find_existing_products(codes)
    
    # 3. Decide action
    if existing:
        if is_variant(scraped_data, existing):
            add_as_variant(existing, scraped_data)
        else:
            flag_for_review("Possible duplicate", scraped_data, existing)
    else:
        # 4. Check name similarity
        similar = find_similar_by_name(scraped_data['name'])
        if similar and similarity_score > 0.85:
            add_as_variant(similar, scraped_data)
        else:
            create_new_master(scraped_data)
```

## Next Steps

1. **Build ProductDeduplicator class**
2. **Create J.Crew and Reiss adapters**
3. **Add similarity matching**
4. **Test on existing data**
5. **Deploy incrementally**

This gives us a robust, scalable system for any brand's product hierarchy!

