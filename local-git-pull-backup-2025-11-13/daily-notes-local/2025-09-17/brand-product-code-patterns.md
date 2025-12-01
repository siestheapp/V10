# Brand Product Code Patterns & Storage Strategy

## The Challenge

Different brands use completely different systems for product variations:

### 1. **J.Crew Pattern: Fit Parameters**
Same product code, different URL parameters for fits:
- BE996 (base) → `?fit=Classic`, `?fit=Slim`, `?fit=Slim%20Untucked`
- All colors/fits share the same product code
- Fits are URL parameters, not in the product code

### 2. **J.Crew Pattern: Compound Codes**
Base code + variant suffix for colors:
- ME053-CC100 (Dark Chocolate check)
- ME053-CC101 (Elias Khaki Multi check)
- Same base (ME053), different suffixes for color variants

### 3. **Reiss Pattern: Completely Different Codes**
Each color has a unique product code with no shared base:
- D43750 (White)
- D40078 (Soft Blue)
- T53709 (Navy)
- All are the same "Greenwich" shirt, but codes are unrelated
- They share a style code in the URL: st378878

### 4. **Banana Republic Pattern** (Expected)
Likely uses numeric codes:
- 000768592 (entire product family)
- Color selected via dropdown or parameter

## Our Storage Solution

### Database Structure

```sql
product_master
├── product_code (unique identifier from brand)
├── base_name (includes color if it's a separate product)
├── fit_information (JSONB)
│   ├── product_family (e.g., "Greenwich", "Secret Wash")
│   ├── style_code (e.g., "st378878" for Reiss)
│   └── fit_type (e.g., "Slim")
└── materials, care_instructions, etc.

product_variants
├── product_master_id (references parent)
├── variant_code (same as product_code for single-variant products)
├── color_name
├── fit_option
├── sizes_available
└── current_price
```

### Storage Patterns by Brand

#### J.Crew (Fit Variations)
```
product_master: BE996 "Broken-in Oxford Shirt"
└── product_variants:
    ├── BE996-WHITE-CLASSIC (White, Classic fit)
    ├── BE996-WHITE-SLIM (White, Slim fit)
    ├── BE996-BLUE-CLASSIC (Blue, Classic fit)
    └── BE996-BLUE-SLIM (Blue, Slim fit)
```

#### J.Crew (Color Codes)
```
product_master: ME053-CC100 "Cotton-Cashmere - Dark Chocolate"
└── product_variants:
    └── ME053-CC100 (single variant)

product_master: ME053-CC101 "Cotton-Cashmere - Elias Khaki"
└── product_variants:
    └── ME053-CC101 (single variant)
```

#### Reiss (Separate Products)
```
product_master: D43750 "Greenwich Oxford - White"
└── product_variants:
    └── D43750 (White only)

product_master: D40078 "Greenwich Oxford - Soft Blue"
└── product_variants:
    └── D40078 (Soft Blue only)

product_master: T53709 "Greenwich Oxford - Navy"
└── product_variants:
    └── T53709 (Navy only, $73 sale price)
```

## Linking Related Products

For products that are the same style but have different codes (like Reiss Greenwich):

1. **Use fit_information JSONB**:
```json
{
  "product_family": "Greenwich",
  "style_code": "st378878",
  "fit_type": "Slim"
}
```

2. **Query for related products**:
```sql
-- Find all Greenwich shirts
SELECT * FROM product_master 
WHERE brand_id = 10 
AND fit_information->>'product_family' = 'Greenwich';
```

## Benefits of This Approach

1. **Flexibility**: Handles any brand's system
2. **No Data Loss**: Preserves exact brand codes
3. **Searchability**: Can find related products via JSONB
4. **Simplicity**: One product_master entry per unique code
5. **Price Tracking**: Each variant can have different prices

## URL Extraction Patterns

```python
# J.Crew: Extract base code
"BE996" from /p/BE996 or /p/.../BE996

# J.Crew: Extract compound code
"ME053-CC100" from /p/ME053?colorProductCode=ME053-CC100

# Reiss: Extract from multiple positions
"D43750" from /style/st378878/d43750
"D40078" from /style/st378878/d40078#d40078
"T53709" from /style/st378878/t53709

# Theory: Extract before .html
"J0901503" from /mens/shirts/J0901503.html
```

## Future Considerations

1. **Create a product_families table** to formally link related products
2. **Add a base_product_code field** for brands that use base+variant pattern
3. **Build UI to show "Other colors available"** by querying product_family
4. **Handle size availability per color** (some colors may have different sizes)
