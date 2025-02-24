SELECT * FROM size_guides ORDER BY brand, gender, size_label;

SELECT * FROM user_garments;

ALTER TABLE public.user_garments ADD COLUMN product_name text;

UPDATE public.user_garments 
SET product_name = 'Brenan Polo Shirt in Cotton-Linen'
WHERE brand_id = (SELECT id FROM brands WHERE name = 'Theory')
AND size_label = 'S';

SELECT b.name as brand, ug.size_label, ug.product_name 
FROM user_garments ug
JOIN brands b ON ug.brand_id = b.id
WHERE ug.product_name IS NOT NULL;

CREATE OR REPLACE FUNCTION process_new_garment(
    p_product_link TEXT,
    p_size_label TEXT,
    p_user_id INTEGER
) RETURNS INTEGER AS $$
DECLARE
    v_brand_id INTEGER;
    v_garment_id INTEGER;
BEGIN
    -- Extract brand name from product link (this is a simplified example)
    -- You might need more sophisticated parsing based on your link format
    WITH brand_extract AS (
        SELECT regexp_matches(p_product_link, '(?:www\.|//)([^/]+)') AS brand_domain
    )
    SELECT id INTO v_brand_id
    FROM brands b
    WHERE LOWER(b.name) = LOWER((SELECT brand_domain[1] FROM brand_extract));

    -- Insert into user_garments and get the new garment ID
    INSERT INTO user_garments (
        user_id,
        brand_id,
        size_label,
        product_link,
        created_at
    ) VALUES (
        p_user_id,
        v_brand_id,
        p_size_label,
        p_product_link,
        NOW()
    ) RETURNING id INTO v_garment_id;

    -- Copy measurements from size_guides to user_garments
    UPDATE user_garments ug
    SET 
        chest = sg.chest,
        waist = sg.waist,
        hip = sg.hip,
        -- Add other measurement columns as needed
        updated_at = NOW()
    FROM size_guides sg
    WHERE ug.id = v_garment_id
    AND sg.brand_id = ug.brand_id
    AND sg.size_label = ug.size_label;

    RETURN v_garment_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get fit feedback questions for a brand
CREATE OR REPLACE FUNCTION get_brand_fit_feedback_ranges(p_brand_id INTEGER)
RETURNS TABLE (
    measurement_name TEXT,
    min_value NUMERIC,
    max_value NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fr.measurement_name,
        fr.min_value,
        fr.max_value
    FROM fit_feedback_ranges fr
    WHERE fr.brand_id = p_brand_id;
END;
$$ LANGUAGE plpgsql;

-- Function to store fit feedback
CREATE OR REPLACE FUNCTION store_fit_feedback(
    p_garment_id INTEGER,
    p_measurement_name TEXT,
    p_feedback_value INTEGER
) RETURNS VOID AS $$
BEGIN
    INSERT INTO fit_feedback (
        garment_id,
        measurement_name,
        feedback_value,
        created_at
    ) VALUES (
        p_garment_id,
        p_measurement_name,
        p_feedback_value,
        NOW()
    );
END;
$$ LANGUAGE plpgsql;

-- Drop the function if it exists
DROP FUNCTION IF EXISTS get_brand_measurements;

-- First, let's see what measurements Banana Republic has
SELECT DISTINCT 
    'chest' as measurement_name FROM size_guides WHERE brand_id = 9 AND chest_range IS NOT NULL AND chest_range != 'N/A'
UNION
SELECT 'neck' WHERE neck_range IS NOT NULL AND neck_range != 'N/A'
UNION
SELECT 'waist' WHERE waist_range IS NOT NULL AND waist_range != 'N/A'
UNION
SELECT 'sleeve' WHERE sleeve_range IS NOT NULL AND sleeve_range != 'N/A'
UNION
SELECT 'hip' WHERE hip_range IS NOT NULL AND hip_range != 'N/A';

-- Then update our function
CREATE OR REPLACE FUNCTION get_brand_measurements(p_brand_id INTEGER)
RETURNS TABLE (measurement_name TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT DISTINCT m.name
    FROM (
        SELECT 'chest' as name FROM size_guides 
        WHERE brand_id = p_brand_id AND chest_range IS NOT NULL AND chest_range != 'N/A'
        UNION
        SELECT 'neck' FROM size_guides 
        WHERE brand_id = p_brand_id AND neck_range IS NOT NULL AND neck_range != 'N/A'
        UNION
        SELECT 'waist' FROM size_guides 
        WHERE brand_id = p_brand_id AND waist_range IS NOT NULL AND waist_range != 'N/A'
        UNION
        SELECT 'sleeve' FROM size_guides 
        WHERE brand_id = p_brand_id AND sleeve_range IS NOT NULL AND sleeve_range != 'N/A'
        UNION
        SELECT 'hip' FROM size_guides 
        WHERE brand_id = p_brand_id AND hip_range IS NOT NULL AND hip_range != 'N/A'
    ) m;
END;
$$ LANGUAGE plpgsql;

-- Function to process garment and feedback
CREATE OR REPLACE FUNCTION process_garment_with_feedback(
    p_product_link TEXT,
    p_size_label TEXT,
    p_user_id INTEGER,
    p_feedback JSON
) RETURNS INTEGER AS $$
DECLARE
    v_brand_id INTEGER;
    v_garment_id INTEGER;
    v_measurement TEXT;
    v_feedback_value INTEGER;
BEGIN
    -- Extract brand name from product link and get brand_id
    WITH brand_extract AS (
        SELECT regexp_matches(p_product_link, '(?:www\.|//)([^/]+)') AS brand_domain
    )
    SELECT id INTO v_brand_id
    FROM brands b
    WHERE LOWER(b.name) = LOWER((SELECT brand_domain[1] FROM brand_extract));

    IF v_brand_id IS NULL THEN
        RAISE EXCEPTION 'Brand not found';
    END IF;

    -- Create user_garment entry
    INSERT INTO user_garments (
        user_id,
        brand_id,
        size_label,
        product_link,
        created_at
    ) VALUES (
        p_user_id,
        v_brand_id,
        p_size_label,
        p_product_link,
        NOW()
    ) RETURNING id INTO v_garment_id;

    -- Copy measurements from size_guides
    UPDATE user_garments ug
    SET 
        chest = sg.chest,
        neck = sg.neck,
        waist = sg.waist,
        hip = sg.hip,
        sleeve = sg.sleeve,
        updated_at = NOW()
    FROM size_guides sg
    WHERE ug.id = v_garment_id
    AND sg.brand_id = ug.brand_id
    AND sg.size_label = ug.size_label;

    -- Store feedback for each measurement
    FOR v_measurement, v_feedback_value IN 
        SELECT * FROM json_each_text(p_feedback)
    LOOP
        INSERT INTO fit_feedback (
            garment_id,
            measurement_name,
            feedback_value,
            created_at
        ) VALUES (
            v_garment_id,
            v_measurement,
            v_feedback_value::INTEGER,
            NOW()
        );
    END LOOP;

    RETURN v_garment_id;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM brands WHERE id = 1;

SELECT * FROM get_brand_measurements(1);

SELECT * FROM size_guides WHERE brand_id = 1;

-- Check size guides for Lululemon
SELECT * FROM size_guides 
WHERE brand_id = 1 
AND (
    chest IS NOT NULL OR
    neck IS NOT NULL OR
    waist IS NOT NULL OR
    hip IS NOT NULL OR
    sleeve IS NOT NULL
);

-- Let's also check the structure of size_guides table
\d size_guides;