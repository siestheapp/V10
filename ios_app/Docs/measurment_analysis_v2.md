# Size Guide and Measurement System Update

## Database Structure Changes
Created new standardized size_guides_v2 table with:
- Precise NUMERIC(5,2) columns for measurements
- Split ranges into min/max pairs
- Consistent decimal handling
- Foreign key constraints for data integrity

```sql
CREATE TABLE size_guides_v2 (
    id SERIAL PRIMARY KEY,
    brand TEXT NOT NULL,
    brand_id INTEGER,
    gender TEXT NOT NULL,
    category TEXT NOT NULL,
    size_label TEXT NOT NULL,
    unit TEXT NOT NULL,
    data_quality TEXT,
    
    -- Measurements with 2 decimal precision
    chest_min NUMERIC(5,2),
    chest_max NUMERIC(5,2),
    sleeve_min NUMERIC(5,2),
    sleeve_max NUMERIC(5,2),
    neck_min NUMERIC(5,2),
    neck_max NUMERIC(5,2),
    waist_min NUMERIC(5,2),
    waist_max NUMERIC(5,2),
    hip_min NUMERIC(5,2),
    hip_max NUMERIC(5,2),
    
    measurements_available TEXT[],
    
    -- Constraints
    CONSTRAINT valid_chest_range CHECK (chest_max >= chest_min),
    CONSTRAINT valid_sleeve_range CHECK (sleeve_max >= sleeve_min),
    CONSTRAINT valid_neck_range CHECK (neck_max >= neck_min),
    CONSTRAINT valid_waist_range CHECK (waist_max >= waist_min),
    CONSTRAINT valid_hip_range CHECK (hip_max >= hip_min)
);
```

## Measurement Format Examples
- Whole numbers: "32", "24"
- One decimal place: "30.5", "31.5"
- Two decimal places: "29.75", "33.25"
- Ranges: "39-40.5", "31.5-33.25"

## Helper Functions

### Parse Measurement Range
```sql
CREATE OR REPLACE FUNCTION parse_measurement_range(range_str TEXT)
RETURNS TABLE(min_val NUMERIC, max_val NUMERIC) AS $$
BEGIN
    IF range_str IS NULL THEN
        RETURN QUERY SELECT NULL::NUMERIC, NULL::NUMERIC;
    ELSIF range_str NOT LIKE '%-%' THEN
        RETURN QUERY SELECT range_str::NUMERIC, range_str::NUMERIC;
    ELSE
        RETURN QUERY 
        SELECT 
            SPLIT_PART(range_str, '-', 1)::NUMERIC,
            SPLIT_PART(range_str, '-', 2)::NUMERIC;
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### Get Missing Feedback
```sql
CREATE OR REPLACE FUNCTION get_missing_feedback(p_garment_id INTEGER)
RETURNS TABLE (
    dimension_name TEXT,
    measurement_range TEXT,
    has_measurement BOOLEAN,
    current_feedback INTEGER
) AS $$
BEGIN
    RETURN QUERY
    WITH garment_measurements AS (
        SELECT 
            g.id,
            g.brand_id,
            g.size_label,
            sg.measurements_available,
            g.chest_min, g.chest_max,
            sg.sleeve_range,
            sg.neck_range,
            sg.waist_range,
            g.overall_code,
            g.chest_code,
            g.sleeve_code,
            g.neck_code,
            g.waist_code
        FROM user_garments_v2 g
        JOIN size_guides_v2 sg ON 
            sg.brand_id = g.brand_id AND 
            sg.size_label = g.size_label
        WHERE g.id = p_garment_id
    )
    SELECT 
        d.dim_name,
        d.range_value,
        d.has_measurement,
        d.feedback_code
    FROM (
        -- Dimension queries here
    ) d
    WHERE 
        d.has_measurement = true
        AND d.feedback_code IS NULL;
END;
$$ LANGUAGE plpgsql;
```

## Next Steps
1. Verify migration for all brands
2. Update related functions and views
3. Drop old table and rename v2 to primary
4. Update API endpoints to use new structure

## Feedback System
- Codes: 1="Good Fit", 2="Too Tight", 3="Tight but I Like It", 4="Too Loose", 5="Loose but I Like It"
- Collecting feedback per dimension (chest, sleeve, neck, waist)
- Only requesting feedback for dimensions with measurements

## Sample Data Verification
```sql
SELECT 
    brand,
    size_label,
    chest_range as old_chest,
    CASE 
        WHEN chest_min = chest_max THEN
            CASE 
                WHEN chest_range NOT LIKE '%.%' THEN chest_min::INTEGER::TEXT
                WHEN chest_range LIKE '%.5' THEN TRIM(TRAILING '0' FROM chest_min::TEXT)
                ELSE chest_range
            END
        ELSE
            -- Range formatting
            CASE 
                WHEN SPLIT_PART(chest_range, '-', 1) NOT LIKE '%.%' THEN chest_min::INTEGER::TEXT
                ELSE TRIM(TRAILING '0' FROM chest_min::TEXT)
            END || '-' ||
            CASE 
                WHEN SPLIT_PART(chest_range, '-', 2) NOT LIKE '%.%' THEN chest_max::INTEGER::TEXT
                ELSE TRIM(TRAILING '0' FROM chest_max::TEXT)
            END
    END as new_chest
FROM size_guides sg
JOIN size_guides_v2 sgv2 USING (brand, size_label);
```

Would you like me to add any additional sections or details to this summary?