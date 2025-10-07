# Brand Integration Guide
## Multi-Brand Product Database System

### Overview
This system allows different brands to use their own categorization while enabling cross-brand product comparison.

---

## Database Structure

### Core Fields for Each Product
```python
# Brand-Specific Fields (preserve original)
brand_name: "J.Crew"                    # Brand name
brand_category: "Casual Shirts"         # Brand's category name
brand_subcategory: "Broken-In Oxford"   # Brand's subcategory

# Normalized Fields (for comparison)
standard_category: "Shirts"             # Universal category
standard_subcategory: "Oxford"          # Universal subcategory  
garment_type: "oxford_shirt"            # Specific garment type
fabric_primary: "oxford_cotton"         # Primary fabric
comparison_key: "oxford_shirt_oxford"   # Comparison identifier
```

---

## Adding a New Brand - Step by Step

### 1. Initial Product Import
```python
# Import products with their original categorization
{
    "brand_name": "Theory",
    "product_code": "TH123",
    "product_name": "Sylvain Shirt in Good Cotton",
    "category": "Shirts",  # Theory's term
    "subcategory": None,    # Theory might not use subcategories
    "price": 225.00
}
```

### 2. Run Category Normalizer
```bash
# Normalize all products from new brand
python scripts/database/normalize_brand_products.py --brand "Theory"
```

### 3. Verify Mappings
```sql
-- Check normalized categories
SELECT DISTINCT 
    brand_category,
    brand_subcategory,
    standard_category,
    garment_type,
    COUNT(*) as products
FROM products
WHERE brand_name = 'Theory'
GROUP BY 1,2,3,4;
```

---

## Garment Type Definitions

### Shirts Category
| Garment Type | Keywords | Example Products |
|-------------|----------|------------------|
| `oxford_shirt` | oxford, button-down | J.Crew Broken-In Oxford, BR Grant Oxford |
| `poplin_shirt` | poplin, dress shirt, secret wash | J.Crew Secret Wash, Theory Sylvain |
| `linen_shirt` | linen, irish linen | Baird McNutt Linen, BR Linen Shirt |
| `flannel_shirt` | flannel, brushed cotton | J.Crew Flannel, LL Bean Flannel |
| `chambray_shirt` | chambray, workshirt | J.Crew Chambray, Gap Workshirt |
| `dress_shirt` | dress shirt, formal, non-iron | BR Non-Iron, CT Dress Shirts |

### Knitwear Category
| Garment Type | Keywords | Example Products |
|-------------|----------|------------------|
| `tshirt` | t-shirt, tee, crew neck | J.Crew Broken-In Tee |
| `polo_shirt` | polo, golf shirt | J.Crew Flex Polo |
| `henley` | henley, button neck | J.Crew Garment-Dyed Henley |

---

## Brand-Specific Mappings

### J.Crew
```python
"Casual Shirts" → "Shirts"
"T-Shirts & Polos" → "Knitwear"
"Pants & Chinos" → "Bottoms"
```

### Banana Republic (Example)
```python
"Tops" → "Shirts"
"Polos & Tees" → "Knitwear"
"Pants" → "Bottoms"
```

### Theory (To Add)
```python
"Shirts" → "Shirts"
"Tees" → "Knitwear"
"Pants" → "Bottoms"
```

---

## SQL Queries for Cross-Brand Comparison

### Find Similar Products Across Brands
```sql
-- Find all oxford shirts across brands
SELECT 
    brand_name,
    product_name,
    price,
    garment_type
FROM products
WHERE garment_type = 'oxford_shirt'
ORDER BY price;

-- Compare average prices by garment type
SELECT 
    garment_type,
    brand_name,
    AVG(price) as avg_price,
    COUNT(*) as product_count
FROM products
WHERE standard_category = 'Shirts'
GROUP BY garment_type, brand_name
ORDER BY garment_type, avg_price;
```

### Find Equivalent Products
```sql
-- Find Theory equivalents to J.Crew products
SELECT 
    jc.product_name as jcrew_product,
    jc.price as jcrew_price,
    t.product_name as theory_product,
    t.price as theory_price
FROM products jc
JOIN products t ON t.garment_type = jc.garment_type
WHERE jc.brand_name = 'J.Crew'
  AND t.brand_name = 'Theory'
  AND jc.garment_type = 'poplin_shirt';
```

---

## Testing New Brand Integration

### 1. Test Normalizer
```python
from scripts.database.category_normalizer import CategoryNormalizer

normalizer = CategoryNormalizer()
test_product = {
    'brand_name': 'Theory',
    'product_name': 'Sylvain Shirt in Good Cotton',
    'category': 'Shirts',
    'subcategory': None
}

result = normalizer.normalize_product(test_product)
print(f"Garment Type: {result['garment_type']}")
print(f"Standard Category: {result['standard_category']}")
```

### 2. Validate Mappings
```bash
# Run QA check after import
python scripts/qa_database_check.py --brand "Theory"
```

---

## Common Issues & Solutions

### Issue: Products not matching across brands
**Solution:** Check garment_type detection
```sql
SELECT product_name, garment_type 
FROM products 
WHERE garment_type IS NULL 
  AND brand_name = 'Theory';
```

### Issue: Wrong garment type assigned
**Solution:** Update normalizer keywords
```python
# In category_normalizer.py, add keywords:
'poplin_shirt': {
    'keywords': ['poplin', 'dress shirt', 'good cotton'],  # Added 'good cotton' for Theory
}
```

### Issue: New category not recognized
**Solution:** Add to brand_mappings
```python
# In category_normalizer.py:
'theory': {
    'shirts': 'shirts',
    'knitwear': 'knitwear',
    'new_category': 'standard_category'
}
```

---

## Checklist for Adding New Brand

- [ ] Import products with original categorization
- [ ] Run category normalizer
- [ ] Verify garment_type assignments
- [ ] Check for NULL values in normalized fields
- [ ] Test cross-brand comparison queries
- [ ] Document any brand-specific mappings
- [ ] Run QA check script
- [ ] Update this guide with brand-specific notes

---

## Current Brands in System

| Brand | Products | Categories | Status |
|-------|----------|------------|--------|
| J.Crew | 46 | Casual Shirts, T-Shirts | ✅ Normalized |
| Theory | 0 | - | 📋 To Add |
| Banana Republic | 0 | - | 📋 Planned |
| Uniqlo | 0 | - | 📋 Planned |

---

## Next Steps

1. **Finish J.Crew Casual Shirts**
   - Scrape remaining subcategories (Corduroy, Seaboard, Cotton-Hemp, etc.)
   - Apply normalizer to all products

2. **Add Theory**
   - Scrape Theory shirts
   - Apply normalizer
   - Verify cross-brand matching

3. **Test System**
   - Run comparison queries
   - Validate garment type detection
   - Check for edge cases





