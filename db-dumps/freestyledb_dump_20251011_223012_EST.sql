-- ================================================================
-- FREESTYLEDB SQL DUMP
-- Generated: October 11, 2025 22:30:12 EST
-- Database: PostgreSQL (Supabase)
-- Schema: public
-- ================================================================
--
-- This is a human-readable SQL dump of the Freestyle database
-- containing all product catalog data, user tables, and metadata
--
-- ================================================================

BEGIN;


-- ================================================================
-- TABLE: brand
-- ================================================================

SET

-- BRANDS
                    header                    
----------------------------------------------
 INSERT INTO brand (id, name, website) VALUES
(1 row)

                                 insert_stmt                                 
-----------------------------------------------------------------------------
   (6, 'Reiss', 'https://www.reiss.com'),
   (7, 'J.Crew', 'https://www.jcrew.com'),
   (8, 'Theory', 'https://www.theory.com'),
   (9, 'Babaton', 'https://www.aritzia.com'),
   (10, 'Aritzia', 'https://www.aritzia.com'),
   (19, 'Reformation', 'https://www.thereformation.com'),
   (20, 'Lovers and Friends', 'https://www.revolve.com/br/lovers-friends/'),
   (21, 'SKIMS', 'https://skims.com'),
   (22, 'Free People', 'https://www.freepeople.com');
(9 rows)


-- CATEGORIES
                         header                          
---------------------------------------------------------
 INSERT INTO category (id, parent_id, slug, name) VALUES
(1 row)

                  insert_stmt                  
-----------------------------------------------
   (5, NULL, 'shirts', 'Shirts'),
   (6, NULL, 'jackets', 'Jackets'),
   (7, NULL, 'blazers', 'Blazers'),
   (8, NULL, 'dresses', 'Dresses'),
   (16, NULL, 'dress-shirts', 'Dress-Shirts');
(5 rows)


-- COLOR CATALOG
                            header                             
---------------------------------------------------------------
 INSERT INTO color_catalog (id, canonical, family, hex) VALUES
(1 row)

                 insert_stmt                 
---------------------------------------------
   (23, 'Bright Blue', 'Blue', NULL),
   (24, 'Stone', 'Beige', NULL),
   (25, 'Soft Blue', 'Blue', NULL),
   (26, 'Rust', 'Brown', NULL),
   (27, 'Navy', 'Blue', NULL),
   (28, 'White', 'White', NULL),
   (29, 'Black', 'Black', NULL),
   (30, 'Pink', 'Pink', NULL),
   (31, 'Mid Blue', 'Blue', NULL),
   (32, 'Ryan Gray White', 'Grey', NULL),
   (33, 'Tim White Blue', 'Blue', NULL),
   (34, 'Lilac Oxford', 'Purple', NULL),
   (35, 'Bright White', 'White', NULL),
   (36, 'Dreamhouse Pink', 'Pink', NULL),
   (37, 'Dayflower Blue', 'Blue', NULL),
   (38, 'Deep Black', 'Black', NULL),
   (39, 'Medium Charcoal', 'Grey', NULL),
   (40, 'Ash', 'Grey', NULL),
   (41, 'Rainstorm', 'Blue', NULL),
   (42, 'Pestle', 'Grey', NULL),
   (43, 'Eclipse', 'Navy', NULL),
   (44, 'Dark Wash', 'Blue', NULL),
   (50, 'Dark Azure', NULL, NULL),
   (52, 'Default', NULL, NULL),
   (53, 'Mineral', 'Grey', NULL),
   (54, 'Black Bean', 'Black', NULL),
   (55, 'Red Coral', 'Red', NULL),
   (56, 'Ivory Bridal Silk', 'White', NULL),
   (57, 'Sunshine', 'Yellow', NULL),
   (58, 'Cornflower', 'Blue', NULL),
   (59, 'Forest', 'Green', NULL),
   (60, 'Moon Dot', 'White', NULL),
   (61, 'Romance', 'Pink', NULL),
   (62, 'Light Pink', 'Pink', NULL),
   (63, 'Beige', 'Beige', NULL),
   (65, 'Champagne', 'Beige', NULL),
   (66, 'Brown', 'Brown', NULL),
   (67, 'Onyx', 'Black', NULL),
   (68, 'Heather Grey', 'Grey', NULL),
   (69, 'Oak', 'Brown', NULL),
   (70, 'Phoenix', 'Red', NULL),
   (71, 'Morganite', 'Pink', NULL),
   (72, 'Sydney', 'Blue', NULL),
   (73, 'Hothouse Rose', 'Pink', NULL),
   (74, 'Tahitian Lily', 'Pink', NULL),
   (75, 'Tana', 'Pink', NULL),
   (76, 'Ivory', 'White', NULL),
   (77, 'Green', 'Green', NULL),
   (78, 'Blush', 'Pink', NULL);
(49 rows)


-- FABRIC CATALOG
                          header                           
-----------------------------------------------------------
 INSERT INTO fabric_catalog (id, name, composition) VALUES
(1 row)

                              insert_stmt                              
-----------------------------------------------------------------------
   (11, 'Structure Knit', NULL),
   (12, 'Good Cotton', NULL),
   (13, 'Structure Twill', NULL),
   (14, 'Summer Denim', NULL),
   (15, 'Cotton Blend', NULL),
   (16, 'Sateen', NULL),
   (17, 'FigureKnit', NULL),
   (18, 'Contour', NULL),
   (19, 'Stretch Wool', NULL),
   (20, 'Corduroy', NULL),
   (24, 'Cotton-Cashmere', NULL),
   (25, 'Silk Charmeuse', '100% Silk'),
   (26, 'Modal Ribbed', '91% Modal / 9% Elastane'),
   (27, 'TENCEL Lyocell Jersey', '88% TENCEL™ Lyocell / 12% Spandex');
(14 rows)


-- STYLES
                                                 header                                                 
--------------------------------------------------------------------------------------------------------
 INSERT INTO style (id, brand_id, category_id, name, description, gender, lifecycle, created_at) VALUES
(1 row)

                                                                                                                                                                                insert_stmt                                                                                                                                                                                 
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   (14, 6, 5, 'Tucci Corduroy Overshirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (15, 6, 5, 'Voyager Long-Sleeve Travel Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (16, 6, 5, 'Remote Bengal Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (17, 6, 5, 'Ruban Linen Button-Through Shirt', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (18, 7, 5, 'Bowery Performance Stretch Oxford Shirt with Button-Down Collar', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (19, 7, 5, 'Bowery Performance Stretch Dress Shirt with Spread Collar', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (20, 8, 7, 'Chambers Blazer in Stretch Wool', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (21, 8, 5, 'Sylvain Shirt in Structure Knit', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (22, 8, 5, 'Sylvain Shirt in Good Cotton', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (23, 8, 5, 'Sylvain Shirt in Structure Twill', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (24, 8, 5, 'Button-Up Shirt in Textured Check', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (25, 8, 5, 'Noll Short-Sleeve Shirt in Summer Denim', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (26, 8, 5, 'Noll Short-Sleeve Shirt in Cotton-Blend', NULL, 'Men', NULL, '2025-09-19 00:54:53.652404+00'),
   (27, 9, 8, 'FigureKnit Eyecatcher Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00'),
   (28, 9, 8, 'FigureKnit Eyecatcher Mini Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00'),
   (29, 10, 8, 'Original Contour Ravish Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00'),
   (30, 10, 8, 'Original Contour Maxi Tube Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00'),
   (31, 10, 8, 'Original Contour Mini Tube Dress', NULL, 'Women', NULL, '2025-09-19 00:54:53.652404+00'),
   (37, 7, 5, 'Cotton-cashmere blend shirt', NULL, 'Men', NULL, '2025-09-19 03:29:02.268695+00'),
   (39, 7, 16, 'Unknown Product', NULL, 'Men', NULL, '2025-09-19 04:45:37.930385+00'),
   (40, 19, 8, 'Oren Silk Dress', 'Strapless midi dress with straight neckline, A-line silhouette, and matching scarf. Designed to have a relaxed fit throughout. Customers say this item runs large.', 'womens', 'active', '2025-10-12 02:08:25.782426+00'),
   (41, 20, 8, 'Rossa Maxi Dress', 'Stylish and elegant maxi dress by Lovers and Friends, available on Revolve.', 'womens', 'active', '2025-10-12 02:15:33.500285+00'),
   (42, 21, 8, 'Soft Lounge Long Slip Dress', 'Made with signature modal rib fabric, this addictively soft, full-length silhouette brings out curves with its slinky feel and body-hugging fit. Features a flattering straight neck and adjustable spaghetti straps. Viral product with 5,073 reviews (4.8/5 stars).', 'womens', 'active', '2025-10-12 02:21:19.71026+00'),
   (43, 19, 8, 'Elise Knit Dress', 'Soft and stretchy sleeveless full-length dress with a square neckline. Fitted at bodice with a column skirt. Made from TENCEL™ Lyocell, which comes from Eucalyptus trees with closed-loop production.', 'womens', 'active', '2025-10-12 02:24:16.258337+00'),
   (44, 22, 8, 'Onda Drop Waist Tube Midi', 'Drop waist tube midi dress with a relaxed, bohemian silhouette.', 'womens', 'active', '2025-10-12 02:27:24.247492+00');
(25 rows)


-- VARIANTS
                                                      header                                                      
------------------------------------------------------------------------------------------------------------------
 INSERT INTO variant (id, style_id, color_id, fit_id, fabric_id, size_scale, is_active, attrs, created_at) VALUES
(1 row)

                                                                     insert_stmt                                                                      
------------------------------------------------------------------------------------------------------------------------------------------------------
   (20, 17, 23, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (21, 18, 33, 5, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (22, 18, 33, 6, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (23, 18, 33, 7, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (24, 19, 32, 5, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (25, 19, 32, 6, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (26, 19, 32, 7, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (27, 20, 38, NULL, 19, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (28, 20, 39, NULL, 19, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (29, 21, 29, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (30, 21, 41, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (31, 21, 42, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (32, 21, 43, NULL, 11, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (33, 22, 29, NULL, 12, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (34, 23, 40, NULL, 13, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (35, 24, 29, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (36, 24, 39, NULL, NULL, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (37, 25, 44, NULL, 14, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (38, 26, 29, NULL, 15, NULL, true, '{}', '2025-09-19 00:54:53.652404+00'),
   (39, 27, 28, NULL, 17, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00'),
   (40, 27, 35, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00'),
   (41, 27, 36, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00'),
   (42, 28, 29, NULL, 17, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00'),
   (43, 28, 35, NULL, 17, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00'),
   (44, 29, 29, NULL, 18, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00'),
   (45, 29, 37, NULL, 18, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00'),
   (46, 30, 37, NULL, 18, NULL, true, '{"color_program": "Limited Edition"}', '2025-09-19 00:54:53.652404+00'),
   (47, 31, 29, NULL, 18, NULL, true, '{"color_program": "Essential"}', '2025-09-19 00:54:53.652404+00'),
   (51, 14, 24, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (52, 14, 25, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (53, 14, 26, NULL, 20, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (54, 15, 25, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (55, 15, 27, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (56, 15, 28, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (57, 15, 29, NULL, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (58, 16, 30, 6, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (59, 16, 30, 8, NULL, NULL, true, '{}', '2025-09-19 01:03:54.334073+00'),
   (60, 37, 50, 5, 24, NULL, true, '{}', '2025-09-19 03:29:02.268695+00'),
   (61, 37, 50, 5, NULL, NULL, true, '{}', '2025-09-19 03:31:07.892102+00'),
   (62, 39, 52, 5, NULL, NULL, true, '{"brand_color_code": null}', '2025-09-19 04:45:37.930385+00'),
   (63, 40, 53, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (64, 40, 54, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (65, 40, 55, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (66, 40, 56, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (67, 40, 27, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (68, 40, 57, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (69, 40, 58, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (70, 40, 59, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (71, 40, 60, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (72, 40, 61, NULL, 25, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:08:34.122131+00'),
   (73, 41, 62, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:15:40.279942+00'),
   (75, 41, 28, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:19:23.431746+00'),
   (76, 41, 65, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:19:23.431746+00'),
   (77, 41, 66, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:19:23.431746+00'),
   (78, 42, 67, NULL, 26, 'US-WOMENS-ALPHA-PLUS', true, '{"collection": "Classic Shades"}', '2025-10-12 02:21:28.455659+00'),
   (79, 42, 68, NULL, 26, 'US-WOMENS-ALPHA-PLUS', true, '{"collection": "Limited Edition"}', '2025-10-12 02:21:28.455659+00'),
   (80, 42, 69, NULL, 26, 'US-WOMENS-ALPHA-PLUS', true, '{"collection": "Limited Edition"}', '2025-10-12 02:21:28.455659+00'),
   (81, 42, 70, NULL, 26, 'US-WOMENS-ALPHA-PLUS', true, '{"collection": "Limited Edition"}', '2025-10-12 02:21:28.455659+00'),
   (82, 42, 71, NULL, 26, 'US-WOMENS-ALPHA-PLUS', true, '{"collection": "Limited Edition", "stock_status": "low"}', '2025-10-12 02:21:28.455659+00'),
   (83, 43, 72, NULL, 27, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:24:24.652011+00'),
   (84, 43, 73, NULL, 27, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:24:24.652011+00'),
   (85, 43, 74, NULL, 27, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:24:24.652011+00'),
   (86, 43, 75, NULL, 27, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:24:24.652011+00'),
   (87, 44, 29, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:27:59.036735+00'),
   (88, 44, 76, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:27:59.036735+00'),
   (89, 44, 77, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:27:59.036735+00'),
   (90, 44, 78, NULL, NULL, 'US-WOMENS-ALPHA', true, '{}', '2025-10-12 02:27:59.036735+00');
(67 rows)


-- PRODUCT URLS
                                           header                                            
---------------------------------------------------------------------------------------------
 INSERT INTO product_url (id, style_id, variant_id, region, url, is_current, seen_at) VALUES
(1 row)

                                                                                                                                                insert_stmt                                                                                                                                                 
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   (1, 18, 21, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00'),
   (2, 18, 22, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00'),
   (3, 18, 23, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Tall&colorProductCode=CP682&color_name=tim-white-blue', true, '2025-09-19 00:54:53.652404+00'),
   (4, 20, 27, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html', true, '2025-09-19 00:54:53.652404+00'),
   (5, 20, 28, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html', true, '2025-09-19 00:54:53.652404+00'),
   (6, 27, NULL, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html', true, '2025-09-19 00:54:53.652404+00'),
   (7, 27, 39, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=1275', true, '2025-09-19 00:54:53.652404+00'),
   (8, 27, 40, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=14396', true, '2025-09-19 00:54:53.652404+00'),
   (9, 27, 41, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=32383', true, '2025-09-19 00:54:53.652404+00'),
   (10, 14, 51, 'UK', 'https://www.reiss.com/style/su422501/e71002#e71002', true, '2025-09-19 01:03:54.334073+00'),
   (11, 14, 52, 'UK', 'https://www.reiss.com/style/su422501/e70998', true, '2025-09-19 01:03:54.334073+00'),
   (12, 14, 53, 'UK', 'https://www.reiss.com/style/su422501/ab2005', true, '2025-09-19 01:03:54.334073+00'),
   (13, 15, 54, 'US', 'https://www.reiss.com/us/en/style/su538118/f18169', true, '2025-09-19 01:03:54.334073+00'),
   (14, 15, 55, 'US', 'https://www.reiss.com/us/en/style/su538118/aw1262', true, '2025-09-19 01:03:54.334073+00'),
   (15, 15, 56, 'US', 'https://www.reiss.com/us/en/style/su538118/f18163', true, '2025-09-19 01:03:54.334073+00'),
   (16, 15, 57, 'US', 'https://www.reiss.com/us/en/style/su538118/f18205', true, '2025-09-19 01:03:54.334073+00'),
   (17, 17, 20, 'UK', 'https://www.reiss.com/style/su936297/ap6308#ap6308', true, '2025-09-19 01:03:54.334073+00'),
   (18, 18, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&color_name=white&colorProductCode=CP682', true, '2025-09-19 01:24:41.873246+00'),
   (19, 19, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Classic&colorProductCode=BX291&color_name=ryan-gray-white', true, '2025-09-19 01:24:41.873246+00'),
   (20, 21, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-structure-knit/J0794505.html', true, '2025-09-19 01:29:45.691581+00'),
   (21, 22, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-good-cotton/A0674535.html', true, '2025-09-19 01:29:45.691581+00'),
   (22, 23, NULL, 'US', 'https://www.theory.com/men/shirts/sylvain-shirt-in-structure-twill/P0794514.html', true, '2025-09-19 01:29:45.691581+00'),
   (23, 24, NULL, 'US', 'https://www.theory.com/men/shirts/button-up-shirt-in-textured-check/P0774503.html', true, '2025-09-19 01:29:45.691581+00'),
   (24, 25, NULL, 'US', 'https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-summer-denim/P0574502.html', true, '2025-09-19 01:29:45.691581+00'),
   (25, 26, NULL, 'US', 'https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-cotton-blend/P0574506.html', true, '2025-09-19 01:29:45.691581+00'),
   (26, 20, NULL, 'US', 'https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104.html', true, '2025-09-19 01:29:45.691581+00'),
   (27, 28, NULL, 'US', 'https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-mini-dress/121483.html', true, '2025-09-19 01:29:45.691581+00'),
   (28, 29, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-ravish-dress/123919.html', true, '2025-09-19 01:29:45.691581+00'),
   (29, 30, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-maxi-tube-dress/118760.html', true, '2025-09-19 01:29:45.691581+00'),
   (30, 31, NULL, 'US', 'https://www.aritzia.com/us/en/product/original-contour-mini-tube-dress/118308.html', true, '2025-09-19 01:29:45.691581+00'),
   (31, 16, 59, 'US', 'https://www.reiss.com/us/en/style/su615998/f77495', true, '2025-09-19 01:29:45.691581+00'),
   (32, 16, 58, 'US', 'https://www.reiss.com/us/en/style/su615998/f78985', true, '2025-09-19 01:29:45.691581+00'),
   (33, 15, 54, 'US', 'https://www.reiss.com/us/en/style/su538118/f18169', true, '2025-09-19 02:53:02.701004+00'),
   (34, 18, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&color_name=tim-white-blue&colorProductCode=CP682', true, '2025-09-19 02:53:16.694427+00'),
   (35, 37, NULL, 'US', 'https://www.jcrew.com/p/mens/categories/clothing/shirts/cotton-cashmere/cotton-cashmere-blend-shirt/ME053?display=standard&fit=Classic&color_name=dark-azure&colorProductCode=CC100', true, '2025-09-19 03:29:02.268695+00'),
   (36, 40, 67, 'US', 'https://www.thereformation.com/products/oren-silk-dress/1314259NVY.html', true, '2025-10-12 02:08:40.263425+00'),
   (37, 41, 73, 'US', 'https://www.revolve.com/lovers-and-friends-rossa-maxi-dress-in-light-pink/dp/LOVF-WD4013/', true, '2025-10-12 02:15:47.361198+00'),
   (38, 42, 78, 'CA', 'https://skims.com/en-ca/products/soft-lounge-long-slip-dress-onyx', true, '2025-10-12 02:21:35.167591+00'),
   (39, 43, 83, 'US', 'https://www.thereformation.com/products/elise-knit-dress/1315811.html', true, '2025-10-12 02:24:31.185894+00'),
   (40, 44, 87, 'US', 'https://www.freepeople.com/shop/onda-drop-waist-tube-midi/', true, '2025-10-12 02:28:06.574707+00');
(40 rows)


-- PRICE HISTORY
                                                  header                                                  
----------------------------------------------------------------------------------------------------------
 INSERT INTO price_history (id, variant_id, region, currency, list_price, sale_price, captured_at) VALUES
(1 row)

                                insert_stmt                                
---------------------------------------------------------------------------
   (3, 27, 'US', 'USD', 625.00, 468.75, '2025-09-19 00:54:53.652404+00'),
   (4, 28, 'US', 'USD', 625.00, 468.75, '2025-09-19 00:54:53.652404+00'),
   (5, 39, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00'),
   (6, 40, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00'),
   (7, 41, 'US', 'USD', 148.00, 148.00, '2025-09-19 00:54:53.652404+00'),
   (8, 42, 'US', 'USD', 128.00, 128.00, '2025-09-19 00:54:53.652404+00'),
   (9, 43, 'US', 'USD', 128.00, 128.00, '2025-09-19 00:54:53.652404+00'),
   (10, 44, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00'),
   (11, 45, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00'),
   (12, 46, 'US', 'USD', 98.00, 98.00, '2025-09-19 00:54:53.652404+00'),
   (13, 47, 'US', 'USD', 78.00, 78.00, '2025-09-19 00:54:53.652404+00'),
   (14, 54, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00'),
   (15, 55, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00'),
   (16, 56, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00'),
   (17, 57, 'US', 'USD', 220.00, 220.00, '2025-09-19 01:08:40.419417+00'),
   (18, 54, 'US', 'USD', 220.00, 220.00, '2025-09-19 02:53:02.701004+00'),
   (19, 60, 'US', 'USD', 148.00, 119.50, '2025-09-19 03:29:02.268695+00'),
   (20, 62, 'US', 'USD', NULL, NULL, '2025-09-19 04:45:37.930385+00'),
   (21, 63, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (22, 64, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (23, 65, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (24, 66, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (25, 67, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (26, 68, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (27, 69, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (28, 70, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (29, 71, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (30, 72, 'US', 'USD', 348.00, NULL, '2025-10-12 02:08:49.134009+00'),
   (31, 73, 'US', 'USD', 199.00, NULL, '2025-10-12 02:15:59.454321+00'),
   (33, 75, 'US', 'USD', 199.00, NULL, '2025-10-12 02:19:29.747444+00'),
   (34, 76, 'US', 'USD', 199.00, NULL, '2025-10-12 02:19:29.747444+00'),
   (35, 77, 'US', 'USD', 199.00, NULL, '2025-10-12 02:19:29.747444+00'),
   (36, 78, 'CA', 'CAD', 150.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (37, 79, 'CA', 'CAD', 150.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (38, 80, 'CA', 'CAD', 150.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (39, 81, 'CA', 'CAD', 150.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (40, 82, 'CA', 'CAD', 150.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (41, 78, 'US', 'USD', 110.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (42, 79, 'US', 'USD', 110.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (43, 80, 'US', 'USD', 110.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (44, 81, 'US', 'USD', 110.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (45, 82, 'US', 'USD', 110.00, NULL, '2025-10-12 02:21:42.735648+00'),
   (46, 83, 'US', 'USD', 178.00, NULL, '2025-10-12 02:24:38.306463+00'),
   (47, 84, 'US', 'USD', 178.00, NULL, '2025-10-12 02:24:38.306463+00'),
   (48, 85, 'US', 'USD', 178.00, NULL, '2025-10-12 02:24:38.306463+00'),
   (49, 86, 'US', 'USD', 178.00, NULL, '2025-10-12 02:24:38.306463+00'),
   (50, 87, 'US', 'USD', 78.00, NULL, '2025-10-12 02:28:14.243376+00'),
   (51, 88, 'US', 'USD', 78.00, NULL, '2025-10-12 02:28:14.243376+00'),
   (52, 89, 'US', 'USD', 78.00, NULL, '2025-10-12 02:28:14.243376+00'),
   (53, 90, 'US', 'USD', 78.00, NULL, '2025-10-12 02:28:14.243376+00');
(50 rows)


-- ================================================================
-- USER TABLES
-- ================================================================

-- PROFILES (RLS enabled)
-- Records: 0 (user data not exported for privacy)

-- USER_CLOSET (RLS enabled)
-- Records: 0 (user data not exported for privacy)

-- FIT_FEEDBACK (RLS enabled)  
-- Records: 0 (user data not exported for privacy)

-- ================================================================
-- SUMMARY
-- ================================================================

COMMIT;

-- Database dump completed successfully
-- Date: October 11, 2025 22:30:12 EST
-- 
-- Statistics:
-- - Brands: See above
-- - Categories: See above
-- - Colors: See above
-- - Fabrics: See above
-- - Styles (Products): See above
-- - Variants (Color options): See above
-- - URLs: See above
-- - Price records: See above
--
-- Note: User data (profiles, closets, feedback) not included for privacy

