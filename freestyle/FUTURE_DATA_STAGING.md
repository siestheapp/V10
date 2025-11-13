# Future Data Staging

This file contains structured data extracted during product ingestion that is not currently stored in FreestyleDB, but may have future use. This data can be used to enhance the database schema when we're ready to support these features.

---

## Reformation Oren Silk Dress

**Ingestion Date:** October 12, 2025  
**Source URL:** https://www.thereformation.com/products/oren-silk-dress/1314259NVY.html  
**Database IDs:** Style ID: 40, Variant IDs: 63-72

### Size Guide & Fit Data

#### Model Information
```json
{
  "model": {
    "height": "5'9\"",
    "height_cm": 175,
    "bust": "33\"",
    "bust_cm": 84,
    "waist": "24\"",
    "waist_cm": 61,
    "hips": "34.5\"",
    "hips_cm": 88,
    "size_worn": "XS",
    "style_id": 40
  }
}
```

#### Fit Information
```json
{
  "fit_profile": {
    "style_id": 40,
    "fit_type": "relaxed",
    "fit_description": "Designed to have a relaxed fit throughout",
    "customer_feedback": "Customers say this item runs large",
    "size_recommendation": "If you're in between sizes, we recommend sizing down",
    "runs_large": true,
    "runs_small": false,
    "true_to_size": false
  }
}
```

#### Size Availability (as of Oct 12, 2025)
```json
{
  "size_availability": {
    "style_id": 40,
    "region": "US",
    "sizes": {
      "XS": "waitlist",
      "S": "waitlist",
      "M": "waitlist",
      "L": "waitlist",
      "XL": "waitlist"
    },
    "in_stock": false,
    "captured_at": "2025-10-12"
  }
}
```

### Product Images

#### Image URLs (Not Captured)
```json
{
  "images": {
    "style_id": 40,
    "variant_id": 67,
    "color": "Navy",
    "urls": [
      {
        "position": 0,
        "is_primary": true,
        "url": "[Available on page but not extracted]",
        "alt_text": "Oren Silk Dress - Navy - Front View"
      }
    ],
    "video_available": true,
    "video_url": "[Product page has video player]"
  }
}
```

**Note:** Each color variant (Mineral, Black Bean, Red Coral, etc.) would have its own set of product images showing the dress in that specific color.

### Material & Care Instructions

```json
{
  "care_instructions": {
    "style_id": 40,
    "fabric": "Silk Charmeuse",
    "fabric_weight": "lightweight",
    "fabric_composition": "100% Silk",
    "is_lined": true,
    "care_method": "Dry clean only",
    "special_notes": [
      "Due to its heavier weight, and the use of more substantial, higher quality silk, our Ivory colorway is priced higher than other colors"
    ]
  }
}
```

### Sustainability Data

```json
{
  "sustainability": {
    "style_id": 40,
    "manufacturing": {
      "country": "China",
      "notes": "Sustainably made in qualified partner facility",
      "certification": "Qualified partner facility (not LA factory)",
      "disclosure": "The country of origin above refers to stuff from our most recent production run. There may be styles in our inventory that were made somewhere else."
    },
    "impact_metrics": {
      "ref_scale_available": true,
      "better_materials": true,
      "material_sustainability": "Not virgin materials",
      "circularity_program": "Available through Reformation's circularity program",
      "care_guide_available": true
    },
    "certifications": [
      "Reformation RefScale",
      "Climate Action Commitment"
    ]
  }
}
```

### Shipping & Returns

```json
{
  "fulfillment": {
    "style_id": 40,
    "shipping": {
      "method": "Free shipping on everything",
      "return_fee": "$10 return shipping fee may apply",
      "return_window": "30 days",
      "store_pickup_available": true
    },
    "payment": {
      "installment_available": true,
      "installment_provider": "Affirm",
      "installments": 4,
      "installment_amount": 87.00
    },
    "final_sale": true,
    "final_sale_note": "Final sale items are not eligible for returns except under applicable EU or UK legislation"
  }
}
```

### Product Details

```json
{
  "product_details": {
    "style_id": 40,
    "features": [
      "Strapless",
      "Straight neckline",
      "Elastic neckline",
      "A-line silhouette",
      "Separate neck scarf included",
      "Midi length"
    ],
    "also_available_in": ["Petites"],
    "style_tags": ["occasion", "date night", "wedding guest"],
    "marketing_copy": "Don't flirt with me."
  }
}
```

### Color Variants - Extended Info

```json
{
  "color_variants_extended": [
    {
      "variant_id": 63,
      "color_name": "Mineral",
      "color_family": "Grey",
      "color_collection": "Core",
      "sku_code": "1314259MNL",
      "availability": "waitlist"
    },
    {
      "variant_id": 64,
      "color_name": "Black Bean",
      "color_family": "Black",
      "color_collection": "Core",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    },
    {
      "variant_id": 65,
      "color_name": "Red Coral",
      "color_family": "Red",
      "color_collection": "Core",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    },
    {
      "variant_id": 66,
      "color_name": "Ivory Bridal Silk",
      "color_family": "White",
      "color_collection": "Core",
      "sku_code": "[Unknown]",
      "availability": "waitlist",
      "price_premium": true,
      "price_note": "Priced higher than other colors due to heavier weight and higher quality silk"
    },
    {
      "variant_id": 67,
      "color_name": "Navy",
      "color_family": "Blue",
      "color_collection": "Core",
      "sku_code": "1314259NVY",
      "availability": "waitlist",
      "product_url": "https://www.thereformation.com/products/oren-silk-dress/1314259NVY.html"
    },
    {
      "variant_id": 68,
      "color_name": "Sunshine",
      "color_family": "Yellow",
      "color_collection": "Core",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    },
    {
      "variant_id": 69,
      "color_name": "Cornflower",
      "color_family": "Blue",
      "color_collection": "Seasonal",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    },
    {
      "variant_id": 70,
      "color_name": "Forest",
      "color_family": "Green",
      "color_collection": "Seasonal",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    },
    {
      "variant_id": 71,
      "color_name": "Moon Dot",
      "color_family": "White",
      "color_collection": "Seasonal",
      "sku_code": "[Unknown]",
      "availability": "waitlist",
      "pattern": "polka dots"
    },
    {
      "variant_id": 72,
      "color_name": "Romance",
      "color_family": "Pink",
      "color_collection": "Seasonal",
      "sku_code": "[Unknown]",
      "availability": "waitlist"
    }
  ]
}
```

---

## Future Schema Enhancements

Based on the data above, here are recommended database enhancements:

### 1. Size Guide Tables

```sql
-- Store garment measurements per size
CREATE TABLE size_guide (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  region text DEFAULT 'US',
  unit text DEFAULT 'in',
  size_scale text NOT NULL,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE size_guide_measurements (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  size_guide_id bigint REFERENCES size_guide(id),
  size_label text NOT NULL,
  measurement_type text NOT NULL, -- 'bust', 'waist', 'hips', 'length', etc.
  value numeric NOT NULL,
  created_at timestamptz DEFAULT now(),
  UNIQUE(size_guide_id, size_label, measurement_type)
);

-- Store model info for reference
CREATE TABLE model_info (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  height_inches numeric,
  bust_inches numeric,
  waist_inches numeric,
  hips_inches numeric,
  size_worn text NOT NULL,
  created_at timestamptz DEFAULT now()
);
```

### 2. Enhanced Fit Feedback

```sql
-- Add columns to existing fit_feedback table
ALTER TABLE fit_feedback
ADD COLUMN runs_large boolean,
ADD COLUMN runs_small boolean,
ADD COLUMN true_to_size boolean,
ADD COLUMN customer_feedback_summary text;

-- Or create a new style-level fit profile
CREATE TABLE style_fit_profile (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id) UNIQUE,
  fit_type text, -- 'relaxed', 'slim', 'regular', 'oversized'
  fit_description text,
  runs_large boolean DEFAULT false,
  runs_small boolean DEFAULT false,
  true_to_size boolean DEFAULT true,
  size_recommendation text,
  created_at timestamptz DEFAULT now()
);
```

### 3. Care Instructions

```sql
CREATE TABLE care_instructions (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  care_method text NOT NULL, -- 'Machine wash', 'Dry clean only', 'Hand wash'
  temperature text, -- 'Cold', 'Warm', 'Cool'
  drying text, -- 'Tumble dry low', 'Hang dry', 'Dry flat'
  ironing text, -- 'Low heat', 'Do not iron', 'Steam only'
  special_notes text,
  created_at timestamptz DEFAULT now()
);
```

### 4. Sustainability Data

```sql
CREATE TABLE sustainability_info (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  manufacturing_country text,
  manufacturing_notes text,
  certifications text[], -- Array of certification names
  is_recycled boolean DEFAULT false,
  is_organic boolean DEFAULT false,
  carbon_footprint_kg numeric,
  water_usage_liters numeric,
  created_at timestamptz DEFAULT now()
);
```

### 5. Product Features

```sql
CREATE TABLE product_features (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  feature text NOT NULL, -- 'Strapless', 'Pockets', 'Adjustable straps'
  category text, -- 'construction', 'design', 'functionality'
  created_at timestamptz DEFAULT now()
);
```

### 6. Inventory Tracking

```sql
-- Extend existing inventory_history or create new table
CREATE TABLE inventory_snapshot (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  variant_id bigint REFERENCES variant(id),
  size_label text NOT NULL,
  region text DEFAULT 'US',
  availability text NOT NULL, -- 'in_stock', 'low_stock', 'out_of_stock', 'waitlist'
  quantity int,
  captured_at timestamptz DEFAULT now()
);
```

### 7. Variant Extensions

```sql
-- Add columns to variant table
ALTER TABLE variant
ADD COLUMN color_collection text, -- 'Core', 'Seasonal', 'Limited Edition'
ADD COLUMN pattern text, -- 'solid', 'stripes', 'polka dots'
ADD COLUMN price_premium boolean DEFAULT false,
ADD COLUMN price_premium_note text;
```

### 8. Shipping & Fulfillment

```sql
CREATE TABLE fulfillment_options (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  region text DEFAULT 'US',
  shipping_method text,
  shipping_cost numeric DEFAULT 0,
  return_window_days int DEFAULT 30,
  return_cost numeric,
  store_pickup_available boolean DEFAULT false,
  is_final_sale boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);
```

---

## Data Usage Examples

### Use Case 1: Size Recommendations

When a user views this dress, we could use the model info:
- "Model is 5'9\", 33/24/34.5 and wears XS"
- "This item runs large. Size down if between sizes."

### Use Case 2: Care Guidance

Show care instructions in the app:
- "Dry clean only"
- "Due to delicate silk fabric, professional cleaning recommended"

### Use Case 3: Sustainability Features

Display in product details:
- RefScale impact score
- Made in qualified partner facility
- Part of circularity program

### Use Case 4: Improved Size Twin Matching

Instead of just matching on size label (e.g., both wear "S"), we could match on actual body measurements:
- User A: 33" bust, 24" waist, 34.5" hips
- User B: 33" bust, 26" waist, 36" hips
- Match confidence: 85% (similar bust, slight difference in waist/hips)

### Use Case 5: Fit Analytics

Track fit feedback patterns:
- 78% of users say this runs large
- Most common size down: XS → XXS (if available)
- Best for body type: [based on measurements]

---

## Data Collection Strategies

### For Future Ingestion

1. **Web Scraping Enhancement**
   - Extract all product images (not just URLs)
   - Parse size chart tables when available
   - Capture customer reviews mentioning fit
   - Extract model info from image captions

2. **User-Generated Data**
   - Prompt users to add measurements when they sign up
   - Ask for fit feedback after purchase/wear
   - Collect "would you size up/down?" surveys

3. **Brand API Integration**
   - Some retailers provide size recommendation APIs
   - Product data feeds often include more detailed specs
   - Real-time inventory availability

4. **Manual Curation**
   - For high-value products, manually input size charts
   - Partner with brands for accurate measurement data
   - Photography for internal image database

---

## Implementation Priority

**Phase 1 (MVP+):**
- ✅ Size guide tables (most requested feature)
- ✅ Style fit profile (runs large/small)
- ✅ Model info

**Phase 2 (Enhanced Experience):**
- Care instructions
- Product features
- Enhanced variant metadata (color collection, pattern)

**Phase 3 (Full Feature Set):**
- Sustainability data
- Inventory tracking
- Shipping/fulfillment options
- Advanced fit analytics

---

**Last Updated:** October 12, 2025  
**Status:** Staging area for future data model enhancements


---

## Lovers and Friends Rossa Maxi Dress

**Ingestion Date:** October 12, 2025  
**Source URL:** https://www.revolve.com/lovers-and-friends-rossa-maxi-dress-in-light-pink/dp/LOVF-WD4013/  
**Database IDs:** Style ID: 41, Variant IDs: 73, 75-77  
**Retailer:** Revolve

### Product Details Captured

```json
{
  "product_summary": {
    "style_id": 41,
    "brand": "Lovers and Friends",
    "name": "Rossa Maxi Dress",
    "sku": "LOVF-WD4013",
    "price": 199.00,
    "currency": "USD",
    "category": "Dresses",
    "gender": "womens",
    "retailer": "Revolve",
    "retailer_website": "https://www.revolve.com"
  }
}
```

### Color Variants

```json
{
  "color_variants": [
    {
      "variant_id": 73,
      "color_name": "Light Pink",
      "color_family": "Pink",
      "sku_code": "LOVF-WD4013",
      "product_url": "https://www.revolve.com/lovers-and-friends-rossa-maxi-dress-in-light-pink/dp/LOVF-WD4013/",
      "price": 199.00
    },
    {
      "variant_id": 75,
      "color_name": "White",
      "color_family": "White",
      "price": 199.00
    },
    {
      "variant_id": 76,
      "color_name": "Champagne",
      "color_family": "Beige",
      "price": 199.00
    },
    {
      "variant_id": 77,
      "color_name": "Brown",
      "color_family": "Brown",
      "price": 199.00
    }
  ]
}
```

### Size Availability

```json
{
  "size_availability": {
    "style_id": 41,
    "region": "US",
    "size_scale": "US-WOMENS-ALPHA",
    "sizes_available": ["XS", "S", "M", "L", "XL"],
    "url_specified_size": "XS",
    "captured_at": "2025-10-12"
  }
}
```

### Affiliate & Tracking Data (Not Stored)

```json
{
  "affiliate_tracking": {
    "source_url": "https://www.revolve.com/lovers-and-friends-rossa-maxi-dress-in-light-pink/dp/LOVF-WD4013/?cjdata=MXxOfDB8WXww&d=Womens&sizeSelected=true&srcType=dp_coloroption&AID=11017645&PID=4441350&utm_medium=affiliate&utm_source=cj&source=cj&utm_campaign=glob_p_2975314&cjevent=336181bea62c11f0811900e20a82b82c&size=XS&code=LOVF-WD4013",
    "tracking_params": {
      "cjdata": "MXxOfDB8WXww",
      "AID": "11017645",
      "PID": "4441350",
      "utm_medium": "affiliate",
      "utm_source": "cj",
      "utm_campaign": "glob_p_2975314",
      "cjevent": "336181bea62c11f0811900e20a82b82c"
    },
    "notes": "Commission Junction (CJ) affiliate tracking - could be used for partnership analytics"
  }
}
```

### Retailer Information (Not Stored Separately)

```json
{
  "retailer_info": {
    "name": "Revolve",
    "website": "https://www.revolve.com",
    "brand_page": "https://www.revolve.com/br/lovers-friends/",
    "multi_brand_retailer": true,
    "product_code": "LOVF-WD4013",
    "notes": "Revolve is a multi-brand fashion retailer. Lovers and Friends is one of their house brands."
  }
}
```

### Missing Data (Not Available from Source)

```json
{
  "missing_data": {
    "fabric_composition": "Not provided in search results",
    "care_instructions": "Not provided in search results",
    "model_information": "Not provided in search results",
    "fit_information": "Not provided in search results",
    "product_images": "Not extracted from search results",
    "product_measurements": "Size chart not available in search results",
    "sustainability_info": "Not provided in search results",
    "customer_reviews": "Not extracted",
    "detailed_description": "Limited description available",
    "styling_suggestions": "Not provided"
  }
}
```

### Notes

- **Limited Data:** Web search provided less detailed product information compared to the Reformation dress. Full product page scraping would capture more data.
- **Retailer vs Brand:** Revolve is the retailer; Lovers and Friends is the brand. Currently we only track brand in the database.
- **Multi-brand Retail:** Consider adding a `retailer` table to differentiate between brand (manufacturer) and retailer (seller).
- **Affiliate Tracking:** The URL contains extensive affiliate tracking parameters that could be useful for partnership analytics.

### Recommended Schema Additions for Multi-Brand Retailers

```sql
-- Table to track retailers separately from brands
CREATE TABLE retailer (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE,
  website text,
  is_multi_brand boolean DEFAULT false,
  created_at timestamptz DEFAULT now()
);

-- Link product URLs to retailers
ALTER TABLE product_url
ADD COLUMN retailer_id bigint REFERENCES retailer(id);

-- Track affiliate partnerships
CREATE TABLE affiliate_tracking (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  product_url_id bigint REFERENCES product_url(id),
  affiliate_network text, -- 'CJ', 'Rakuten', 'Impact', etc.
  affiliate_id text,
  partner_id text,
  campaign text,
  tracking_params jsonb,
  captured_at timestamptz DEFAULT now()
);
```


---

## SKIMS Soft Lounge Long Slip Dress

**Ingestion Date:** October 12, 2025  
**Source URL:** https://skims.com/en-ca/products/soft-lounge-long-slip-dress-onyx  
**Database IDs:** Style ID: 42, Variant IDs: 78-82  
**Collection:** Soft Lounge

### Product Details Captured

```json
{
  "product_summary": {
    "style_id": 42,
    "brand": "SKIMS",
    "name": "Soft Lounge Long Slip Dress",
    "collection": "Soft Lounge",
    "price_cad": 150.00,
    "price_usd": 110.00,
    "category": "Dresses",
    "subcategory": "Slips & Dresses",
    "gender": "womens",
    "viral_status": true,
    "review_count": 5073,
    "rating": 4.8,
    "rating_out_of": 5
  }
}
```

### Color Variants

```json
{
  "color_variants": [
    {
      "variant_id": 78,
      "color_name": "Onyx",
      "color_family": "Black",
      "collection": "Classic Shades",
      "product_url": "https://skims.com/en-ca/products/soft-lounge-long-slip-dress-onyx",
      "price_cad": 150.00,
      "price_usd": 110.00
    },
    {
      "variant_id": 79,
      "color_name": "Heather Grey",
      "color_family": "Grey",
      "collection": "Limited Edition",
      "price_cad": 150.00,
      "price_usd": 110.00
    },
    {
      "variant_id": 80,
      "color_name": "Oak",
      "color_family": "Brown",
      "collection": "Limited Edition",
      "price_cad": 150.00,
      "price_usd": 110.00
    },
    {
      "variant_id": 81,
      "color_name": "Phoenix",
      "color_family": "Red",
      "collection": "Limited Edition",
      "price_cad": 150.00,
      "price_usd": 110.00
    },
    {
      "variant_id": 82,
      "color_name": "Morganite",
      "color_family": "Pink",
      "collection": "Limited Edition",
      "stock_status": "low",
      "price_cad": 150.00,
      "price_usd": 110.00
    }
  ]
}
```

### Size Guide & Measurements

```json
{
  "size_guide": {
    "style_id": 42,
    "region": "US/CA",
    "unit": "inches",
    "size_scale": "US-WOMENS-ALPHA-PLUS",
    "sizes_available": ["XXS", "XS", "S", "M", "L", "XL", "2X", "3X", "4X"],
    "measurements": {
      "length": {
        "XXS_to_XL": 50,
        "2X_to_4X": 51
      }
    },
    "note": "Also available in petite length for heights 5'3\""
  }
}
```

### Model Information

```json
{
  "model": {
    "name": "Dagmar",
    "dress_size": 2,
    "bra_size": "32B",
    "height": "5'9.5\"",
    "height_cm": 176,
    "size_worn": "S",
    "style_id": 42
  }
}
```

### Fit Information

```json
{
  "fit_profile": {
    "style_id": 42,
    "fit_type": "fitted",
    "fit_description": "Fitted look throughout torso and hips, Drapey fit throughout length",
    "runs_true_to_size": true,
    "runs_large": false,
    "runs_small": false,
    "neckline": "Straight neckline",
    "straps": "Partially adjustable spaghetti straps",
    "length": "Maxi length",
    "silhouette": "Body-hugging with slinky feel"
  }
}
```

### Fabric Details

```json
{
  "fabric_info": {
    "style_id": 42,
    "fabric_id": 26,
    "name": "Modal Ribbed",
    "composition": "91% Modal / 9% Elastane",
    "texture": "Ribbed fabric detail",
    "properties": {
      "softness": "high",
      "stretch": "high",
      "breathability": "high",
      "weight": "medium",
      "feel": "Addictively soft, slinky"
    },
    "collection_description": "Our viral Soft Lounge features the softest ribbed fabric with slinky stretch for supreme comfort and breathability while sleeping, lounging and leaving the house."
  }
}
```

### Care Instructions

```json
{
  "care_instructions": {
    "style_id": 42,
    "wash": "Machine wash cold with like colors",
    "bleach": "Non-Chlorine bleach only",
    "dry": "Lay flat to dry",
    "iron": "Low iron as needed",
    "dry_clean": "Do not dry clean",
    "origin": "Imported"
  }
}
```

### Customer Reviews Summary

```json
{
  "reviews": {
    "style_id": 42,
    "total_reviews": 5073,
    "overall_rating": 4.8,
    "rating_breakdown": {
      "5_star": 4400,
      "4_star": 411,
      "3_star": 137,
      "2_star": 47,
      "1_star": 45
    },
    "would_recommend_percent": 96,
    "fit_consensus": "True to Size",
    "ai_summary": "Customers say this dress is exceptionally soft and flattering on their curves. Many reviews highlight its versatility for both lounging and dressing up. The stretchy material hugs the body comfortably, and the length works well for various heights. While most praise its fit and comfort, some note the fabric is somewhat sheer. Reviews frequently mention purchasing multiple colors and wearing it for different occasions."
  }
}
```

### Product Features

```json
{
  "product_features": {
    "style_id": 42,
    "features": [
      "Fitted look throughout torso and hips",
      "Drapey fit throughout length",
      "Straight neckline",
      "Partially adjustable spaghetti straps",
      "Maxi length",
      "Ribbed fabric detail",
      "Body-hugging fit",
      "Curves enhancing",
      "Slinky feel"
    ],
    "versatility": ["Lounging", "Sleeping", "Going out", "Date night"],
    "petite_option_available": true,
    "petite_height_recommendation": "5'3\" and under"
  }
}
```

### Shipping & Fulfillment (Canadian Site)

```json
{
  "fulfillment": {
    "style_id": 42,
    "region": "CA",
    "shipping": {
      "free_shipping_threshold": "CAD $115+",
      "standard_shipping": "5-10 business days",
      "express_shipping_available": true
    },
    "returns": {
      "return_window": "Free returns for SKIMS Rewards members",
      "return_policy_url": "https://skims.com/pages/return-policy"
    },
    "rewards_program": "SKIMS Rewards"
  }
}
```

### Affiliate & Tracking Data (Not Stored)

```json
{
  "affiliate_tracking": {
    "source_url": "https://skims.com/en-ca/products/soft-lounge-long-slip-dress-onyx?irclickid=yYSXUTWEIxycWRRWP9S6xTy%3AUkp3-A1nNzsq380&irgwc=1&utm_medium=affiliate&utm_source=impact&utm_campaign=LTK",
    "tracking_params": {
      "irclickid": "yYSXUTWEIxycWRRWP9S6xTy:Ukp3-A1nNzsq380",
      "irgwc": "1",
      "utm_medium": "affiliate",
      "utm_source": "impact",
      "utm_campaign": "LTK"
    },
    "affiliate_network": "Impact Radius",
    "affiliate_campaign": "LTK (LikeToKnow.it)",
    "notes": "Influencer marketing platform tracking"
  }
}
```

### Related Products (Not Stored)

```json
{
  "related_products": [
    {
      "name": "SKIMS BODY FORM MICRO STRAP PLUNGE BRA",
      "price_cad": 108.00,
      "sale_price_cad": 78.00,
      "color": "onyx"
    },
    {
      "name": "FITS EVERYBODY DIPPED FRONT THONG",
      "price_cad": 34.00,
      "promotion": "3 for $66",
      "color": "onyx"
    },
    {
      "name": "SEAMLESS SCULPT STRAPLESS SHORTIE BODYSUIT",
      "price_cad": 138.00,
      "tag": "best seller",
      "color": "onyx"
    },
    {
      "name": "SEAMLESS SCULPT THONG BODYSUIT",
      "price_cad": 130.00,
      "tag": "best seller",
      "color": "onyx"
    },
    {
      "name": "MULTI-WAY BRA",
      "price_cad": 120.00,
      "tag": "best seller",
      "color": "onyx"
    }
  ]
}
```

### Marketing & Social Proof

```json
{
  "marketing_data": {
    "style_id": 42,
    "viral_product": true,
    "tagline": "The internet's obsessed with this dress, and you will be too",
    "key_selling_points": [
      "Signature modal rib fabric",
      "Addictively soft",
      "Body-hugging fit",
      "Curves enhancing",
      "5,073+ reviews",
      "4.8/5 star rating",
      "96% would recommend"
    ],
    "social_proof": {
      "review_highlights": [
        "So many compliments",
        "Perfect for dates",
        "Extremely versatile",
        "Fits perfectly",
        "Purchased multiple colors"
      ],
      "common_occasions": [
        "Valentine's Day dates",
        "Going out",
        "Lounging",
        "Everyday wear"
      ]
    }
  }
}
```

### Size Inclusivity

```json
{
  "size_inclusivity": {
    "style_id": 42,
    "size_range": "XXS to 4X",
    "total_sizes": 9,
    "petite_available": true,
    "extended_sizes": ["2X", "3X", "4X"],
    "notes": "One of the most inclusive size ranges in the database"
  }
}
```

### Notes

- **Viral Product:** This dress has 5,073 reviews with a 4.8/5 rating - extremely popular item
- **Collection Metadata:** Used `attrs` jsonb field to store "Limited Edition" vs "Classic Shades" collection info
- **Multi-Currency:** Added both CAD (primary) and USD pricing
- **Size Inclusivity:** XXS-4X range is exceptional, includes plus sizes
- **Customer Feedback:** 96% recommend, consistent praise for softness and fit
- **Versatility:** Customers wear it for lounging, sleeping, going out, and dates
- **Fabric Sheer Warning:** Some reviews mention fabric is somewhat sheer (not in official description)
- **Petite Option:** Available in petite length for heights 5'3" and under (separate product)
- **LTK Affiliate:** URL shows LikeToKnow.it (influencer platform) tracking

### Recommended Schema Additions for Reviews

```sql
-- Store customer reviews and ratings
CREATE TABLE product_reviews (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  variant_id bigint REFERENCES variant(id),
  rating smallint NOT NULL CHECK (rating >= 1 AND rating <= 5),
  review_text text,
  reviewer_name text,
  reviewer_verified boolean DEFAULT false,
  size_purchased text,
  reviewer_height text,
  fit_rating text, -- 'runs_small', 'true_to_size', 'runs_large'
  would_recommend boolean,
  helpful_count int DEFAULT 0,
  created_at timestamptz DEFAULT now()
);

-- Aggregate review metrics at style level
CREATE TABLE style_review_summary (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id) UNIQUE,
  total_reviews int DEFAULT 0,
  average_rating numeric(3,2),
  rating_breakdown jsonb, -- {5: 4400, 4: 411, ...}
  would_recommend_percent int,
  fit_consensus text, -- 'runs_small', 'true_to_size', 'runs_large'
  ai_summary text,
  updated_at timestamptz DEFAULT now()
);
```

### Recommended Schema Additions for Multi-Currency

```sql
-- Already implemented in price_history, but worth noting the pattern:
-- Store prices in their native currency with region
-- Example: CAD$150 for CA region, USD$110 for US region
-- This allows proper display without conversion confusion
```

### Recommended Schema Additions for Product Collections

```sql
-- Already using variant.attrs jsonb for collection metadata
-- Could formalize with a collections table:
CREATE TABLE product_collection (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  brand_id bigint REFERENCES brand(id),
  name text NOT NULL, -- 'Soft Lounge', 'Fits Everybody', etc.
  description text,
  is_limited_edition boolean DEFAULT false,
  season text, -- 'Fall 2025', 'Spring 2024'
  created_at timestamptz DEFAULT now()
);

ALTER TABLE variant
ADD COLUMN collection_id bigint REFERENCES product_collection(id);
```


---

## Reformation Elise Knit Dress

**Ingestion Date:** October 12, 2025  
**Source URL:** https://www.thereformation.com/products/elise-knit-dress/1315811.html  
**Database IDs:** Style ID: 43, Variant IDs: 83-86

### Product Details Captured

```json
{
  "product_summary": {
    "style_id": 43,
    "brand": "Reformation",
    "name": "Elise Knit Dress",
    "price": 178.00,
    "currency": "USD",
    "category": "Dresses",
    "subcategory": "Knit Dresses",
    "gender": "womens",
    "is_final_sale": true
  }
}
```

### Color Variants

```json
{
  "color_variants": [
    {
      "variant_id": 83,
      "color_name": "Sydney",
      "color_family": "Blue",
      "sku_code": "1315811TNN",
      "product_url": "https://www.thereformation.com/products/elise-knit-dress/1315811.html?dwvar_1315811_color=TNN",
      "price": 178.00
    },
    {
      "variant_id": 84,
      "color_name": "Hothouse Rose",
      "color_family": "Pink",
      "price": 178.00
    },
    {
      "variant_id": 85,
      "color_name": "Tahitian Lily",
      "color_family": "Pink",
      "price": 178.00
    },
    {
      "variant_id": 86,
      "color_name": "Tana",
      "color_family": "Pink",
      "price": 178.00
    }
  ]
}
```

### Size Availability (as of Oct 12, 2025)

```json
{
  "size_availability": {
    "style_id": 43,
    "region": "US",
    "size_scale": "US-WOMENS-ALPHA",
    "sizes": {
      "XS": "waitlist",
      "S": "waitlist",
      "M": "waitlist",
      "L": "waitlist",
      "XL": "waitlist"
    },
    "in_stock": false,
    "all_sizes_waitlist": true,
    "captured_at": "2025-10-12"
  }
}
```

### Model Information

```json
{
  "model": {
    "height": "5'9\"",
    "height_cm": 175,
    "bust": "30\"",
    "bust_cm": 76,
    "waist": "24\"",
    "waist_cm": 61,
    "hips": "34\"",
    "hips_cm": 86,
    "size_worn": "XS",
    "style_id": 43
  }
}
```

### Fit Information

```json
{
  "fit_profile": {
    "style_id": 43,
    "fit_type": "fitted",
    "fit_description": "Fitted at bodice with a column skirt",
    "customer_feedback": "Customers say this style runs true to size",
    "runs_large": false,
    "runs_small": false,
    "true_to_size": true,
    "neckline": "Square neckline (straight neckline)",
    "straps": "Adjustable straps",
    "silhouette": "Column skirt",
    "length": "Full-length"
  }
}
```

### Fabric Details

```json
{
  "fabric_info": {
    "style_id": 43,
    "fabric_id": 27,
    "name": "TENCEL Lyocell Jersey",
    "composition": "88% TENCEL™ Lyocell / 12% Spandex",
    "weight": "Medium weight",
    "texture": "Soft, stretch, jersey fabric",
    "properties": {
      "softness": "high",
      "stretch": "high",
      "feel": "Soft and stretchy"
    },
    "sustainability": {
      "material": "TENCEL™ Lyocell from Eucalyptus trees",
      "efficiency": "Half an acre produces one ton of fiber",
      "production_type": "Closed loop production",
      "solvent_reuse": "99% of non-toxic solvent is reused",
      "eco_friendly": true
    }
  }
}
```

### Care Instructions

```json
{
  "care_instructions": {
    "style_id": 43,
    "wash": "Wash cold",
    "dry": "Tumble dry low",
    "origin": "Sustainably made in Los Angeles",
    "manufacturing_note": "The country of origin above refers to stuff from our most recent production run. There may be styles in our inventory that were made somewhere else."
  }
}
```

### Sustainability Data

```json
{
  "sustainability": {
    "style_id": 43,
    "manufacturing": {
      "primary_location": "Los Angeles, USA",
      "sustainably_made": true,
      "ethical_production": true,
      "worker_treatment": "Places that treat workers well",
      "factory_network": "LA factory and qualified partner facilities worldwide"
    },
    "materials": {
      "tencel_lyocell": {
        "source": "Eucalyptus trees",
        "land_efficiency": "Half an acre per ton of fiber",
        "production_method": "Closed loop production",
        "solvent_reuse_rate": 0.99,
        "non_toxic": true
      }
    },
    "programs": {
      "ref_scale": true,
      "circularity": true,
      "climate_action": true,
      "sustainability_report": "Quarterly publication"
    }
  }
}
```

### Product Features

```json
{
  "product_features": {
    "style_id": 43,
    "features": [
      "Sleeveless",
      "Square neckline (also called straight neckline)",
      "Adjustable straps",
      "Fitted bodice",
      "Column skirt",
      "Full-length",
      "Medium weight fabric",
      "Soft and stretchy"
    ],
    "style_tags": ["knit dress", "fall dress", "occasion dress"],
    "marketing_copy": "Soft and stretchy"
  }
}
```

### Shipping & Returns

```json
{
  "fulfillment": {
    "style_id": 43,
    "shipping": {
      "method": "Free shipping on everything",
      "return_fee": "$10 return shipping fee may apply",
      "return_window": "30 days",
      "store_pickup_available": true
    },
    "payment": {
      "installment_available": true,
      "installment_provider": "Affirm",
      "installments": 4,
      "installment_amount": 44.50
    },
    "final_sale": true,
    "final_sale_note": "Final sale items are not eligible for returns except under applicable EU or UK legislation"
  }
}
```

### RefScale & Environmental Impact

```json
{
  "environmental_impact": {
    "style_id": 43,
    "ref_scale_available": true,
    "ref_scale_url": "More on RefScale section",
    "impact_categories": {
      "better_materials": {
        "available": true,
        "description": "TENCEL™ Lyocell with closed-loop production"
      },
      "not_virgins": {
        "available": true,
        "description": "Circularity program - keep clothes out of landfills"
      },
      "climate_action": {
        "available": true,
        "description": "Measures environmental impact and actively reducing it"
      },
      "wash_smart": {
        "available": true,
        "description": "Designed to last longer with care guidance"
      },
      "sustainability_report": {
        "available": true,
        "frequency": "Quarterly",
        "description": "Tracks progress together with customers"
      }
    }
  }
}
```

### Notes

- **All Sizes Waitlist:** Every size (XS-XL) is on waitlist as of Oct 12, 2025 - indicates high demand or low stock
- **Final Sale:** This item is final sale (not eligible for returns)
- **TENCEL Sustainability:** TENCEL™ Lyocell is a highly sustainable fabric with 99% solvent reuse in closed-loop production
- **Made in LA:** Primary manufacturing in Los Angeles (ethical labor, lower carbon footprint for US market)
- **Smaller Model Measurements:** Model has 30" bust compared to 33" for the Oren Silk Dress model
- **Square vs Straight Neckline:** Product uses both terms ("square neckline" in description, "straight neckline" in fit details)
- **Color Family:** 3 out of 4 colors are pink family (Hothouse Rose, Tahitian Lily, Tana)
- **SKU Pattern:** Sydney color has SKU ending in "TNN" based on URL parameter

### Comparison to Oren Silk Dress (Same Brand)

```json
{
  "product_comparison": {
    "similarities": [
      "Same brand (Reformation)",
      "Both dresses",
      "Full-length/Maxi length",
      "Adjustable straps",
      "True to size fit",
      "Final sale",
      "Free shipping",
      "Store pickup available",
      "Installment payments (4 × price/4)"
    ],
    "differences": {
      "oren_silk_dress": {
        "price": 348.00,
        "fabric": "100% Silk charmeuse",
        "neckline": "Straight neckline",
        "fit": "Relaxed, runs large",
        "colors": 10,
        "care": "Dry clean only",
        "weight": "Lightweight"
      },
      "elise_knit_dress": {
        "price": 178.00,
        "fabric": "88% TENCEL Lyocell / 12% Spandex",
        "neckline": "Square neckline",
        "fit": "Fitted bodice, true to size",
        "colors": 4,
        "care": "Wash cold / tumble dry low",
        "weight": "Medium weight"
      }
    }
  }
}
```

### Recommended Schema Additions

Already covered by previous products, but worth noting:
- Model measurements table would capture the 30" bust difference
- Stock availability/waitlist tracking (all sizes on waitlist is significant)
- Final sale flag (already captured in fulfillment staging data)


---

## Free People Onda Drop Waist Tube Midi

**Ingestion Date:** October 12, 2025  
**Source URL:** https://www.freepeople.com/shop/onda-drop-waist-tube-midi/  
**Database IDs:** Style ID: 44, Variant IDs: 87-90

### Product Details Captured

```json
{
  "product_summary": {
    "style_id": 44,
    "brand": "Free People",
    "name": "Onda Drop Waist Tube Midi",
    "price": 78.00,
    "currency": "USD",
    "category": "Dresses",
    "subcategory": "Midi Dresses",
    "gender": "womens",
    "style_type": "Drop waist, tube dress",
    "silhouette": "Strapless, relaxed fit"
  }
}
```

### Color Variants

```json
{
  "color_variants": [
    {
      "variant_id": 87,
      "color_name": "Black",
      "color_family": "Black",
      "color_code": "001",
      "product_url": "https://www.freepeople.com/shop/onda-drop-waist-tube-midi/",
      "price": 78.00
    },
    {
      "variant_id": 88,
      "color_name": "Ivory",
      "color_family": "White",
      "price": 78.00,
      "availability": "Sold out on REVOLVE"
    },
    {
      "variant_id": 89,
      "color_name": "Green",
      "color_family": "Green",
      "price": 78.00,
      "availability": "Available"
    },
    {
      "variant_id": 90,
      "color_name": "Blush",
      "color_family": "Pink",
      "price": 78.00,
      "availability": "Available"
    }
  ]
}
```

### Product Features (Not Fully Captured)

```json
{
  "product_features": {
    "style_id": 44,
    "silhouette": "Strapless, drop-waist tube dress",
    "length": "Midi",
    "fit": "Relaxed",
    "neckline": "Strapless",
    "style_vibe": "Bohemian, casual to semi-formal",
    "versatility": ["Casual", "Semi-formal"],
    "notes": "Limited product details available from search results"
  }
}
```

### Retailer Information

```json
{
  "retailer_info": {
    "primary_retailer": "Free People",
    "also_available_on": ["REVOLVE"],
    "revolve_sku": "FREE-WD2631",
    "multi_retailer": true,
    "notes": "Product available on both Free People website and REVOLVE"
  }
}
```

### Affiliate & Tracking Data (Not Stored)

```json
{
  "affiliate_tracking": {
    "source_url": "https://www.freepeople.com/shop/onda-drop-waist-tube-midi/?category=SEARCHRESULTS&color=001&quantity=1&searchparams=q=drop%20waist&type=REGULAR&cm_mmc=rakuten-_-affiliates-_-LTK-_-1&utm_medium=affiliates&utm_source=rakuten&utm_campaign=LTK&utm_term=1825046&utm_content=1&utm_kxconfid=v3sdm8r4u&ranMID=43177&ranEAID=QFGLnEolOWg&ranSiteID=QFGLnEolOWg-ShxO0e9FnnmLaj7cqxFawQ",
    "tracking_params": {
      "cm_mmc": "rakuten-_-affiliates-_-LTK-_-1",
      "utm_medium": "affiliates",
      "utm_source": "rakuten",
      "utm_campaign": "LTK",
      "utm_term": "1825046",
      "utm_content": "1",
      "utm_kxconfid": "v3sdm8r4u",
      "ranMID": "43177",
      "ranEAID": "QFGLnEolOWg",
      "ranSiteID": "QFGLnEolOWg-ShxO0e9FnnmLaj7cqxFawQ"
    },
    "affiliate_network": "Rakuten",
    "affiliate_campaign": "LTK (LikeToKnow.it)",
    "notes": "Rakuten affiliate tracking with LTK campaign"
  }
}
```

### Price Comparison

```json
{
  "price_comparison": {
    "style_id": 44,
    "price": 78.00,
    "comparison_context": [
      {
        "product": "Reformation Oren Silk Dress",
        "price": 348.00,
        "price_ratio": "4.5x more expensive"
      },
      {
        "product": "Reformation Elise Knit Dress",
        "price": 178.00,
        "price_ratio": "2.3x more expensive"
      },
      {
        "product": "Lovers and Friends Rossa Maxi",
        "price": 199.00,
        "price_ratio": "2.6x more expensive"
      },
      {
        "product": "SKIMS Soft Lounge Long Slip",
        "price": 110.00,
        "price_ratio": "1.4x more expensive"
      }
    ],
    "notes": "This Free People dress is the most affordable item in the database at $78"
  }
}
```

### Missing Data (Limited Web Search Results)

```json
{
  "missing_data": {
    "fabric_composition": "Not provided in search results",
    "care_instructions": "Not provided in search results",
    "model_information": "Not provided in search results",
    "fit_information": "Only 'relaxed fit' mentioned",
    "product_images": "Not extracted from search results",
    "size_guide": "Not provided in search results",
    "customer_reviews": "Not extracted",
    "detailed_description": "Limited description available",
    "sustainability_info": "Not provided (Free People often has eco-conscious items)",
    "size_availability": "Unknown (except Ivory sold out on REVOLVE)",
    "product_measurements": "Not provided"
  }
}
```

### Notes

- **Most Affordable:** At $78, this is the most affordable dress in the database
- **Limited Data:** Web search provided minimal product details compared to direct page scraping
- **Multi-Retailer:** Available on both Free People and REVOLVE websites
- **LTK Affiliate:** Same affiliate network (LTK/LikeToKnow.it) as previous products, but via Rakuten
- **Drop Waist Style:** Specific silhouette type (drop waist) which could be a search/filter category
- **Strapless:** First strapless dress in the database
- **Bohemian Brand:** Free People is known for bohemian, festival-style clothing
- **Color Code:** Black color coded as "001" in URL parameter

### Recommended Schema Additions

**Silhouette/Style Types:**
```sql
CREATE TABLE dress_silhouette (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE, -- 'A-line', 'Column', 'Drop waist', 'Fit and flare'
  description text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE style
ADD COLUMN silhouette_id bigint REFERENCES dress_silhouette(id);
```

**Neckline Types:**
```sql
CREATE TABLE neckline_type (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL UNIQUE, -- 'Strapless', 'Square', 'Straight', 'V-neck', 'Scoop'
  description text,
  created_at timestamptz DEFAULT now()
);

ALTER TABLE style
ADD COLUMN neckline_id bigint REFERENCES neckline_type(id);
```

**Multi-Retailer Tracking:**
```sql
-- Already recommended in previous products, but reinforced here
-- Track that same product is available on multiple retailer sites
CREATE TABLE product_retailer (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  style_id bigint REFERENCES style(id),
  retailer_id bigint REFERENCES retailer(id),
  sku text,
  url text,
  is_primary boolean DEFAULT false,
  created_at timestamptz DEFAULT now(),
  UNIQUE(style_id, retailer_id)
);
```

