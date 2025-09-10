# Unified Measurement Guides Proposal

## Current Problem
We have two separate tables that serve similar purposes:
- `size_guides` - Body measurement ranges (e.g., "chest 39-41" for size M)
- `garment_guides` - Garment specifications (e.g., "chest width 20.5" for size M)

Both are "guides" that group measurements together, just with different measurement types.

## Proposed Solution: Single `measurement_guides` Table

### Option 1: Unified Table (RECOMMENDED)

```sql
CREATE TABLE measurement_guides (
    id SERIAL PRIMARY KEY,
    
    -- Core identification
    guide_type TEXT NOT NULL CHECK (guide_type IN ('body', 'garment')),
    brand_id INTEGER REFERENCES brands(id),
    
    -- What this guide applies to
    garment_id INTEGER REFERENCES garments(id),  -- NULL for body guides
    category_id INTEGER REFERENCES categories(id),  -- NULL for garment-specific guides
    subcategory_id INTEGER REFERENCES subcategories(id),
    
    -- Guide metadata
    name TEXT NOT NULL,  -- e.g., "Banana Republic Men's Tops Size Guide" or "NN07 Clive Tee Measurements"
    gender TEXT,
    fit_type TEXT,
    version INTEGER DEFAULT 1,
    
    -- Source information
    source_url TEXT,
    source_type TEXT,  -- 'official_chart', 'product_page', 'customer_service', etc.
    screenshot_path TEXT,
    raw_source_text TEXT,
    
    -- What measurements this guide provides
    measurements_available TEXT[],  -- ['chest', 'waist'] or ['g_chest_width', 'g_sleeve_length']
    unit TEXT DEFAULT 'inches',
    provides_dual_units BOOLEAN DEFAULT false,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    updated_at TIMESTAMP,
    updated_by INTEGER,
    
    -- Constraints
    CHECK (
        (guide_type = 'body' AND category_id IS NOT NULL) OR
        (guide_type = 'garment' AND garment_id IS NOT NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_mg_brand_category ON measurement_guides(brand_id, category_id);
CREATE INDEX idx_mg_garment ON measurement_guides(garment_id);
CREATE INDEX idx_mg_type ON measurement_guides(guide_type);
```

### Benefits of Consolidation

1. **Single source of truth** for all measurement guides
2. **Simpler queries** - JOIN to one table instead of conditional JOINs
3. **Consistent structure** - Same fields for both types
4. **Easier maintenance** - One table to update/migrate
5. **Better for the measurements table** - Single foreign key to measurement_guides

### Updated Measurements Table

```sql
-- The measurements table would then reference the unified guide
ALTER TABLE measurements 
ADD COLUMN guide_id INTEGER REFERENCES measurement_guides(id);

-- And we can deprecate source_type and source_id
ALTER TABLE measurements 
ALTER COLUMN source_type DROP NOT NULL;
ALTER TABLE measurements 
ALTER COLUMN source_id DROP NOT NULL;
```

### Migration Path

```sql
-- 1. Create new unified table
CREATE TABLE measurement_guides (...);

-- 2. Migrate size_guides
INSERT INTO measurement_guides (
    guide_type, brand_id, category_id, subcategory_id,
    name, gender, fit_type, version,
    source_url, screenshot_path, raw_source_text,
    measurements_available, unit,
    notes, created_at, created_by
)
SELECT 
    'body', brand_id, category_id, subcategory_id,
    size_guide_header, gender, fit_type, version,
    source_url, screenshot_path, raw_text,
    measurements_available, unit,
    notes, created_at, created_by
FROM size_guides;

-- 3. Migrate garment_guides
INSERT INTO measurement_guides (
    guide_type, brand_id, garment_id,
    name, source_url, source_type,
    screenshot_path, raw_source_text,
    measurements_available, provides_dual_units,
    notes, created_at, created_by
)
SELECT 
    'garment', brand_id, 
    (SELECT id FROM garments WHERE garment_guide_id = garment_guides.id LIMIT 1),
    guide_header, source_url, info_source,
    screenshot_path, raw_source_text,
    measurements_available, provides_dual_units,
    notes, created_at, created_by
FROM garment_guides;

-- 4. Update measurements table to reference new guide
UPDATE measurements m
SET guide_id = (
    SELECT mg.id FROM measurement_guides mg
    WHERE 
        (m.source_type = 'size_guide' AND mg.guide_type = 'body' 
         AND mg.id = m.source_id) OR
        (m.source_type = 'garment_spec' AND mg.guide_type = 'garment'
         AND mg.id = m.source_id)
);
```

## Option 2: Keep Separate, Use a View (ALTERNATIVE)

If you prefer to keep them separate for now:

```sql
CREATE VIEW unified_guides AS
SELECT 
    'body' as guide_type,
    id as guide_id,
    brand_id,
    category_id,
    subcategory_id,
    NULL as garment_id,
    size_guide_header as name,
    gender,
    fit_type,
    source_url,
    measurements_available,
    unit,
    created_at
FROM size_guides

UNION ALL

SELECT 
    'garment' as guide_type,
    id as guide_id,
    brand_id,
    NULL as category_id,
    NULL as subcategory_id,
    (SELECT id FROM garments WHERE garment_guide_id = gg.id LIMIT 1) as garment_id,
    guide_header as name,
    NULL as gender,
    NULL as fit_type,
    source_url,
    measurements_available,
    'inches' as unit,
    created_at
FROM garment_guides gg;
```

## Recommendation

I recommend **Option 1 (Unified Table)** because:

1. **You're already doing this with measurements** - This follows the same pattern
2. **Cleaner foreign keys** - measurements.guide_id instead of complex source_type/source_id
3. **Future-proof** - Easy to add new guide types if needed
4. **Performance** - One indexed table vs UNION queries
5. **Consistency** - Both guide types are fundamentally the same thing: "a collection of measurements for a brand/product"

The distinction between body and garment measurements is preserved through:
- The `guide_type` field
- The measurement naming convention (chest vs g_chest_width)
- The relationships (category-based vs garment-specific)

What do you think? Should we proceed with the unified approach?
