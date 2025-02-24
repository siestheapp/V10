-- =============================================
-- TAILOR APP TESTING QUERIES
-- =============================================

-- 1. Check Current User Data
-- -------------------------
SELECT id, email, gender, unit_preference 
FROM users 
WHERE id = 1;

-- 2. Check User's Existing Garments
-- --------------------------------
SELECT 
    ug.id,
    b.name as brand,
    ug.size_label,
    ug.chest_range,
    ug.product_link,
    ug.created_at,
    uff.overall_fit
FROM user_garments ug
LEFT JOIN brands b ON ug.brand_id = b.id
LEFT JOIN user_fit_feedback uff ON ug.id = uff.garment_id
WHERE ug.user_id = 1
ORDER BY ug.created_at DESC;

-- 3. Check Available Brands
-- ------------------------
SELECT id, name, default_unit, size_guide_url
FROM brands
ORDER BY name;

-- 4. Test URL Processing
-- ---------------------
SELECT process_garment_with_feedback(
    'https://bananarepublic.gap.com/browse/product.do?pid=800139112',
    'L',
    1,
    '{}'::json
);

-- 5. Check Brand Measurements
-- --------------------------
SELECT 
    b.name as brand,
    sg.gender,
    sg.size_label,
    sg.chest_range,
    sg.neck_range,
    sg.sleeve_range,
    sg.waist_range
FROM size_guides sg
JOIN brands b ON sg.brand_id = b.id
WHERE b.name = 'Banana Republic'
AND sg.gender = 'Men'
ORDER BY sg.size_label;

-- 6. Check User's Fit Zones
-- ------------------------
SELECT *
FROM user_fit_zones
WHERE user_id = 1;

SELECT * FROM users LIMIT 1;

-- Try a new product link to avoid duplicate constraint
INSERT INTO user_garment_inputs (user_id, product_link, size_label)
VALUES (1, 'https://bananarepublic.gap.com/browse/product.do?pid=123456789', 'M');

-- Check both tables
SELECT * FROM user_garment_inputs ORDER BY created_at DESC LIMIT 1;
SELECT * FROM processing_logs ORDER BY created_at DESC LIMIT 1;