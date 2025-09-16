# Shirt Category Structure Guide

## Overview
Shirts are divided into two distinct categories based on formality and use case.

---

## Category Structure

### 1. Casual Shirts
**Purpose:** Everyday wear, relaxed settings, smart casual
**Standard Category:** `casual_shirts`

#### Subcategories:
- **Oxford/Broken-In Oxford** → `garment_type: oxford_shirt`
  - J.Crew: "Broken-In Oxford"
  - Banana Republic: "Soft-Wash Oxford"
  - Uniqlo: "Oxford Shirts"

- **Secret Wash/Poplin** → `garment_type: poplin_shirt`
  - J.Crew: "Secret Wash"
  - BR: "Untucked Poplin"
  
- **Linen** → `garment_type: linen_shirt`
  - J.Crew: "Baird McNutt Irish Linen"
  - BR: "Linen Shirts"
  
- **Chambray** → `garment_type: chambray_shirt`
- **Flannel** → `garment_type: flannel_shirt`
- **Corduroy** → `garment_type: corduroy_shirt`

---

### 2. Dress Shirts
**Purpose:** Business, formal occasions, suiting
**Standard Category:** `dress_shirts`

#### Subcategories:
- **Performance/Tech** → `garment_type: dress_shirt`
  - J.Crew: "Bowery Performance Stretch"
  - BR: "Non-Iron Dress Shirts"
  - Charles Tyrwhitt: "Non-Iron Shirts"

- **Premium/Luxury** → `garment_type: dress_shirt`
  - J.Crew: "Ludlow Premium", "Thomas Mason"
  - BR: "Grant Fit Premium"
  - Theory: "Sylvain Dress Shirt"

- **Traditional** → `garment_type: dress_shirt`
  - Standard cotton dress shirts
  - French cuff options
  - Spread/point collar styles

---

## Key Differences

| Aspect | Casual Shirts | Dress Shirts |
|--------|--------------|--------------|
| **Collar** | Button-down, camp, band | Spread, point, cutaway |
| **Fit** | Relaxed, untucked options | Tailored, meant to tuck |
| **Fabric** | Oxford, linen, flannel | Poplin, broadcloth, twill |
| **Features** | Chest pockets, casual details | French cuffs, collar stays |
| **Price Range** | $50-150 | $80-300+ |

---

## Database Implementation

### For J.Crew Products:
```sql
-- Casual Shirts
INSERT INTO products (
    brand_name, 
    category, 
    subcategory,
    standard_category,
    garment_type
) VALUES (
    'J.Crew',
    'Casual Shirts',
    'Broken-In Oxford',
    'casual_shirts',
    'oxford_shirt'
);

-- Dress Shirts
INSERT INTO products (
    brand_name,
    category,
    subcategory,
    standard_category,
    garment_type
) VALUES (
    'J.Crew',
    'Dress Shirts',
    'Bowery',
    'dress_shirts',
    'dress_shirt'
);
```

---

## Cross-Brand Comparison

### Finding Similar Products:
```sql
-- Find all dress shirts across brands
SELECT brand_name, product_name, price
FROM products
WHERE standard_category = 'dress_shirts'
  AND garment_type = 'dress_shirt';

-- Compare casual vs dress oxford shirts
SELECT 
    standard_category,
    brand_name,
    AVG(price) as avg_price
FROM products
WHERE fabric_primary = 'oxford_cotton'
GROUP BY standard_category, brand_name;
```

---

## Handling Edge Cases

### Oxford Dress Shirts
Some brands have "dress shirt oxfords" - more formal oxford cloth shirts:
- **Category:** Dress Shirts
- **Garment Type:** `dress_shirt`
- **Fabric:** `oxford_cotton`
- **Formality:** `business`

### Poplin Casual Shirts
Some poplin shirts are casual (like J.Crew Secret Wash):
- **Category:** Casual Shirts
- **Garment Type:** `poplin_shirt`
- **Formality:** `business_casual`

---

## Brand Examples

### J.Crew Structure:
```
Men's Shirts
├── Casual Shirts
│   ├── Broken-In Oxford (25)
│   ├── Secret Wash (57)
│   ├── Linen (17)
│   └── Corduroy (8)
└── Dress Shirts
    ├── Ludlow Premium (12)
    ├── Bowery (22)
    └── Tech (20)
```

### Theory Structure (Example):
```
Men's Shirts
├── Shirts (all mixed)
    ├── Sylvain (dress)
    ├── Irving (casual)
    └── Zack (casual)
```

### Banana Republic Structure (Example):
```
Men's Tops
├── Dress Shirts
│   ├── Grant Fit
│   └── Non-Iron
└── Casual Shirts
    ├── Untucked
    └── Soft-Wash
```

---

## Implementation Checklist

When adding shirts to the database:
- [ ] Identify if casual or dress shirt
- [ ] Set correct category (Casual Shirts vs Dress Shirts)
- [ ] Assign appropriate garment_type
- [ ] Set formality level (casual/business_casual/business/formal)
- [ ] Identify primary fabric
- [ ] Create comparison_key for cross-brand matching



