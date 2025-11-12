# J.Crew Product Variant Strategy Documentation

## Overview
J.Crew uses a dual-code system for product variants where the same base product (e.g., a shirt style) can have multiple color/pattern variants, each with its own variant code.

## Product Code Structure

### Base Product Code
- **Format**: `XXNNN` where XX = letters, NNN = numbers
- **Example**: `ME053` (Cotton-cashmere blend shirt)
- This identifies the product style/cut/fit

### Color/Variant Code  
- **Format**: `CCNNN` where CC = letters, NNN = numbers
- **Examples**:
  - `CC100` = Dark chocolate (solid color)
  - `CC101` = Elias khaki multi (check pattern)
- This identifies the specific color/pattern variant

### URL Structure
```
https://www.jcrew.com/m/mens/.../[BASE_CODE]?...&colorProductCode=[VARIANT_CODE]

Example:
https://www.jcrew.com/m/mens/.../ME053?...&colorProductCode=CC100
```

## Our Database Strategy

### Compound Product Codes
We store products using a **compound code** format:
```
[BASE_CODE]-[VARIANT_CODE]
```

**Examples in our database:**
- `ME053-CC100` (Cotton-cashmere shirt in dark chocolate)
- `ME053-CC101` (Cotton-cashmere shirt in elias khaki multi check)
- `BE996` (Product without color variant - base code only)

### Why This Approach?

1. **Avoids Duplicates**: Each color variant gets a unique database entry
2. **Preserves Relationships**: We can query by base code to find all variants
3. **Matches J.Crew's System**: Aligns with how they structure their URLs
4. **Supports Inventory**: Different colors may have different sizes/availability

## Implementation in Our Scrapers

### Code Extraction Logic (from `jcrew_variant_crawler.py`)
```python
def extract_product_codes(self, url: str) -> Tuple[str, str, Optional[str]]:
    """
    Returns: (compound_code, base_code, variant_code)
    e.g., ('ME053-CC100', 'ME053', 'CC100')
    """
    # Extract base code from URL path
    base_code = extract_from_url_path(url)
    
    # Extract variant code from colorProductCode param
    variant_code = extract_from_params(url, 'colorProductCode')
    
    # Create compound code
    if variant_code:
        compound_code = f"{base_code}-{variant_code}"
    else:
        compound_code = base_code
    
    return compound_code, base_code, variant_code
```

## Database Schema Considerations

### Current Structure
```sql
jcrew_product_cache:
- product_code: 'ME053-CC100' (UNIQUE)
- product_name: 'Cotton-cashmere blend shirt'
- product_url: Full URL with colorProductCode
- colors_available: ['Dark Chocolate'] (specific to this variant)
- fit_options: ['Classic', 'Slim'] (shared across variants)
```

### Querying Strategies

**Find all variants of a product:**
```sql
SELECT * FROM jcrew_product_cache 
WHERE product_code LIKE 'ME053-%';
```

**Find base product (if exists without variant):**
```sql
SELECT * FROM jcrew_product_cache 
WHERE product_code = 'ME053';
```

**Check if we have a specific variant:**
```sql
SELECT * FROM jcrew_product_cache 
WHERE product_code = 'ME053-CC100';
```

## Validation Rules

Our protection framework validates:
1. **No duplicate compound codes** (enforced by UNIQUE constraint)
2. **Consistent format** for compound codes
3. **Base code extraction** for relationship tracking

## Edge Cases

### 1. Products Without Variants
Some products don't have color variants:
- Store with base code only: `BE996`
- No hyphen or variant code needed

### 2. Multiple Variant Parameters
Some products may have both color AND fit variants:
- We primarily track by color variant
- Fit options stored in `fit_options` array field

### 3. Renamed/Reused Codes
J.Crew may reuse codes over time:
- Our timestamp tracking helps identify when products were added
- URL preservation helps verify current products

## Benefits of This Approach

✅ **No Duplicates**: Each color variant is unique  
✅ **Complete Data**: We capture all color options  
✅ **Searchable**: Can find products by base or full code  
✅ **Maintainable**: Clear, consistent naming convention  
✅ **Scalable**: Works for any number of variants  

## Example Products in Database

| product_code | Base | Variant | Description |
|-------------|------|---------|-------------|
| ME053-CC100 | ME053 | CC100 | Cotton-cashmere shirt - Dark Chocolate |
| ME053-CC101 | ME053 | CC101 | Cotton-cashmere shirt - Elias Khaki Multi |
| BE996 | BE996 | None | Broken-in oxford (no variant codes) |
| BM492 | BM492 | None | Ludlow dress shirt (no variant codes) |

## Scraping Best Practices

1. **Always extract both codes** when available
2. **Use compound code** as primary key
3. **Store base code** for grouping/analysis
4. **Preserve full URL** with colorProductCode param
5. **Track color name** in colors_available field

## Future Enhancements

Consider adding:
- `base_product_code` field for easier querying
- `variant_code` field for direct variant access
- `product_family` table to group variants
- View that aggregates all variants of a base product

## Summary

The compound code system (`BASE-VARIANT`) successfully:
- Prevents duplicates
- Preserves J.Crew's structure  
- Enables complete product tracking
- Supports our validation framework

This approach ensures we capture the full J.Crew catalog without duplication while maintaining data integrity.
