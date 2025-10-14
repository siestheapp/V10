              info               
---------------------------------
 -- ALL TABLES IN PUBLIC SCHEMA:
(1 row)

        table_name        
--------------------------
 __migrations_applied
 brand
 brand_category_map
 brand_color_map
 brand_profile
 category
 color_catalog
 evidence
 fabric_catalog
 fit_catalog
 fit_feedback
 ingest_run
 ingestion_job
 ingestion_task
 inventory_history
 media_asset
 price_history
 product_image
 product_images
 product_url
 profiles
 style
 style_code
 user_closet
 v_product_variants
 v_product_variants_img
 v_variant_current_image
 v_variant_current_url
 v_variant_latest_price
 v_variants_missing_image
 variant
 variant_code
(32 rows)

        ?column?        
------------------------
 -- BRANDS (13 records)
(1 row)

 id |        name        |                  website                   
----+--------------------+--------------------------------------------
  6 | Reiss              | https://www.reiss.com
  7 | J.Crew             | https://www.jcrew.com
  8 | Theory             | https://www.theory.com
  9 | Babaton            | https://www.aritzia.com
 10 | Aritzia            | https://www.aritzia.com
 19 | Reformation        | https://www.thereformation.com
 20 | Lovers and Friends | https://www.revolve.com/br/lovers-friends/
 21 | SKIMS              | https://skims.com
 22 | Free People        | https://www.freepeople.com
 29 | ALC                | https://alcltd.com
 30 | Camila Coelho      | https://www.revolve.com
 31 | ASTR the Label     | https://www.astrthelabel.com
 32 | VICI Collection    | https://www.vicicollection.com
(13 rows)

         ?column?          
---------------------------
 -- CATEGORIES (5 records)
(1 row)

 id | parent_id |     slug     |     name     
----+-----------+--------------+--------------
  5 |           | shirts       | Shirts
  6 |           | jackets      | Jackets
  7 |           | blazers      | Blazers
  8 |           | dresses      | Dresses
 16 |           | dress-shirts | Dress-Shirts
(5 rows)

        ?column?        
------------------------
 -- COLORS (64 records)
(1 row)

 id |     canonical     | family |   hex   
----+-------------------+--------+---------
 23 | Bright Blue       | Blue   | 
 24 | Stone             | Beige  | 
 25 | Soft Blue         | Blue   | 
 26 | Rust              | Brown  | 
 27 | Navy              | Blue   | 
 28 | White             | White  | 
 29 | Black             | Black  | 
 30 | Pink              | Pink   | 
 31 | Mid Blue          | Blue   | 
 32 | Ryan Gray White   | Grey   | 
 33 | Tim White Blue    | Blue   | 
 34 | Lilac Oxford      | Purple | 
 35 | Bright White      | White  | 
 36 | Dreamhouse Pink   | Pink   | 
 37 | Dayflower Blue    | Blue   | 
 38 | Deep Black        | Black  | 
 39 | Medium Charcoal   | Grey   | 
 40 | Ash               | Grey   | 
 41 | Rainstorm         | Blue   | 
 42 | Pestle            | Grey   | 
 43 | Eclipse           | Navy   | 
 44 | Dark Wash         | Blue   | 
 50 | Dark Azure        |        | 
 52 | Default           |        | 
 53 | Mineral           | Grey   | 
 54 | Black Bean        | Black  | 
 55 | Red Coral         | Red    | 
 56 | Ivory Bridal Silk | White  | 
 57 | Sunshine          | Yellow | 
 58 | Cornflower        | Blue   | 
 59 | Forest            | Green  | 
 60 | Moon Dot          | White  | 
 61 | Romance           | Pink   | 
 62 | Light Pink        | Pink   | 
 63 | Beige             | Beige  | 
 65 | Champagne         | Beige  | 
 66 | Brown             | Brown  | 
 67 | Onyx              | Black  | 
 68 | Heather Grey      | Grey   | 
 69 | Oak               | Brown  | 
 70 | Phoenix           | Red    | 
 71 | Morganite         | Pink   | 
 72 | Sydney            | Blue   | 
 73 | Hothouse Rose     | Pink   | 
 74 | Tahitian Lily     | Pink   | 
 75 | Tana              | Pink   | 
 76 | Ivory             | White  | 
 77 | Green             | Green  | 
 78 | Blush             | Pink   | 
 79 | Emerald           | Green  | #50C878
 80 | Wine              | Red    | #722F37
 81 | Mocha             | Brown  | #967969
 82 | Midnight Plum     | Purple | #4A2E4C
 83 | Garnet            | Red    | #733635
 84 | Ivy               | Green  | #4A5D23
 85 | Brown Leopard     | Brown  | #8B6F47
 86 | Brown Butterfly   | Brown  | #8B7355
 87 | Brown Floral      | Brown  | #8B6F47
 88 | Dark Sage         | Green  | #4A5D4F
 89 | Lilac             | Purple | #C8A2C8
 90 | Lime              | Green  | #BFFF00
 91 | Slate Blue        | Blue   | #6A7B8C
 92 | Burgundy          | Red    | #800020
 93 | Red               | Red    | #FF0000
(64 rows)

        ?column?         
-------------------------
 -- FABRICS (14 records)
(1 row)

 id |         name          |            composition            
----+-----------------------+-----------------------------------
 11 | Structure Knit        | 
 12 | Good Cotton           | 
 13 | Structure Twill       | 
 14 | Summer Denim          | 
 15 | Cotton Blend          | 
 16 | Sateen                | 
 17 | FigureKnit            | 
 18 | Contour               | 
 19 | Stretch Wool          | 
 20 | Corduroy              | 
 24 | Cotton-Cashmere       | 
 25 | Silk Charmeuse        | 100% Silk
 26 | Modal Ribbed          | 91% Modal / 9% Elastane
 27 | TENCEL Lyocell Jersey | 88% TENCEL™ Lyocell / 12% Spandex
(14 rows)

      ?column?       
---------------------
 -- FITS (4 records)
(1 row)

 id |  name   
----+---------
  5 | Classic
  6 | Slim
  7 | Tall
  8 | Regular
(4 rows)

        ?column?        
------------------------
 -- STYLES (30 records)
(1 row)

 id | brand_id | category_id |                              name                               |                                                                                                                              description                                                                                                                              | gender |  lifecycle   |          created_at           
----+----------+-------------+-----------------------------------------------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+--------+--------------+-------------------------------
 14 |        6 |           5 | Tucci Corduroy Overshirt                                        |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 15 |        6 |           5 | Voyager Long-Sleeve Travel Shirt                                |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 16 |        6 |           5 | Remote Bengal Shirt                                             |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 17 |        6 |           5 | Ruban Linen Button-Through Shirt                                |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 18 |        7 |           5 | Bowery Performance Stretch Oxford Shirt with Button-Down Collar |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 19 |        7 |           5 | Bowery Performance Stretch Dress Shirt with Spread Collar       |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 20 |        8 |           7 | Chambers Blazer in Stretch Wool                                 |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 21 |        8 |           5 | Sylvain Shirt in Structure Knit                                 |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 22 |        8 |           5 | Sylvain Shirt in Good Cotton                                    |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 23 |        8 |           5 | Sylvain Shirt in Structure Twill                                |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 24 |        8 |           5 | Button-Up Shirt in Textured Check                               |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 25 |        8 |           5 | Noll Short-Sleeve Shirt in Summer Denim                         |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 26 |        8 |           5 | Noll Short-Sleeve Shirt in Cotton-Blend                         |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 00:54:53.652404+00
 27 |        9 |           8 | FigureKnit Eyecatcher Dress                                     |                                                                                                                                                                                                                                                                       | Women  |              | 2025-09-19 00:54:53.652404+00
 28 |        9 |           8 | FigureKnit Eyecatcher Mini Dress                                |                                                                                                                                                                                                                                                                       | Women  |              | 2025-09-19 00:54:53.652404+00
 29 |       10 |           8 | Original Contour Ravish Dress                                   |                                                                                                                                                                                                                                                                       | Women  |              | 2025-09-19 00:54:53.652404+00
 30 |       10 |           8 | Original Contour Maxi Tube Dress                                |                                                                                                                                                                                                                                                                       | Women  |              | 2025-09-19 00:54:53.652404+00
 31 |       10 |           8 | Original Contour Mini Tube Dress                                |                                                                                                                                                                                                                                                                       | Women  |              | 2025-09-19 00:54:53.652404+00
 37 |        7 |           5 | Cotton-cashmere blend shirt                                     |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 03:29:02.268695+00
 39 |        7 |          16 | Unknown Product                                                 |                                                                                                                                                                                                                                                                       | Men    |              | 2025-09-19 04:45:37.930385+00
 40 |       19 |           8 | Oren Silk Dress                                                 | Strapless midi dress with straight neckline, A-line silhouette, and matching scarf. Designed to have a relaxed fit throughout. Customers say this item runs large.                                                                                                    | womens | active       | 2025-10-12 02:08:25.782426+00
 41 |       20 |           8 | Rossa Maxi Dress                                                | Stylish and elegant maxi dress by Lovers and Friends, available on Revolve.                                                                                                                                                                                           | womens | active       | 2025-10-12 02:15:33.500285+00
 42 |       21 |           8 | Soft Lounge Long Slip Dress                                     | Made with signature modal rib fabric, this addictively soft, full-length silhouette brings out curves with its slinky feel and body-hugging fit. Features a flattering straight neck and adjustable spaghetti straps. Viral product with 5,073 reviews (4.8/5 stars). | womens | active       | 2025-10-12 02:21:19.71026+00
 43 |       19 |           8 | Elise Knit Dress                                                | Soft and stretchy sleeveless full-length dress with a square neckline. Fitted at bodice with a column skirt. Made from TENCEL™ Lyocell, which comes from Eucalyptus trees with closed-loop production.                                                                | womens | active       | 2025-10-12 02:24:16.258337+00
 44 |       22 |           8 | Onda Drop Waist Tube Midi                                       | Drop waist tube midi dress with a relaxed, bohemian silhouette.                                                                                                                                                                                                       | womens | active       | 2025-10-12 02:27:24.247492+00
 46 |       29 |           8 | Lara Satin Pleated Gown                                         | Rendered in vintage satin, this floor-length gown features a one-shoulder neckline, sunburst pleating, a ruched waist, and a semi-open back. 100% Polyester. Length: 60.25 inches.                                                                                    | womens | active       | 2025-10-12 05:22:26.82315+00
 48 |       30 |           8 | Gilma Maxi Dress                                                | Maxi dress featuring brown butterfly print pattern.                                                                                                                                                                                                                   | womens | active       | 2025-10-12 05:31:21.583778+00
 49 |       31 |           8 | Gaia Burnout Midi Dress                                         | Burnout midi dress with cowl neck, fully lined, low back with adjustable cross strap tie closure, left leg thigh slit. 60% Viscose, 40% Nylon with 100% Polyester lining.                                                                                             | womens | active       | 2025-10-12 05:34:03.34937+00
 50 |       31 |           8 | Maeve Dress                                                     | Tiered maxi dress with square neckline, adjustable straps, side pockets, smocked back. 73% Rayon, 24% Nylon, 3% Spandex with 100% Rayon lining.                                                                                                                       | womens | active       | 2025-10-12 05:35:10.53155+00
 51 |       32 |           8 | Forbidden Love Floral Print Mesh Maxi Dress                     | Lightweight mesh fabric overlay with delicate floral print, bodice and back cut-out, lace panels, back S-hook closure. 95% Polyester, 5% Spandex with 100% Polyester lining.                                                                                          | womens | discontinued | 2025-10-12 05:43:18.914318+00
(30 rows)

         ?column?         
--------------------------
 -- VARIANTS (78 records)
(1 row)

 id  | style_id | color_id | fit_id | fabric_id |      size_scale      | is_active |                                                attrs                                                |          created_at           
-----+----------+----------+--------+-----------+----------------------+-----------+-----------------------------------------------------------------------------------------------------+-------------------------------
  20 |       17 |       23 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  21 |       18 |       33 |      5 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  22 |       18 |       33 |      6 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  23 |       18 |       33 |      7 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  24 |       19 |       32 |      5 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  25 |       19 |       32 |      6 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  26 |       19 |       32 |      7 |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  27 |       20 |       38 |        |        19 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  28 |       20 |       39 |        |        19 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  29 |       21 |       29 |        |        11 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  30 |       21 |       41 |        |        11 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  31 |       21 |       42 |        |        11 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  32 |       21 |       43 |        |        11 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  33 |       22 |       29 |        |        12 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  34 |       23 |       40 |        |        13 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  35 |       24 |       29 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  36 |       24 |       39 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  37 |       25 |       44 |        |        14 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  38 |       26 |       29 |        |        15 |                      | t         | {}                                                                                                  | 2025-09-19 00:54:53.652404+00
  39 |       27 |       28 |        |        17 |                      | t         | {"color_program": "Essential"}                                                                      | 2025-09-19 00:54:53.652404+00
  40 |       27 |       35 |        |        17 |                      | t         | {"color_program": "Limited Edition"}                                                                | 2025-09-19 00:54:53.652404+00
  41 |       27 |       36 |        |        17 |                      | t         | {"color_program": "Limited Edition"}                                                                | 2025-09-19 00:54:53.652404+00
  42 |       28 |       29 |        |        17 |                      | t         | {"color_program": "Essential"}                                                                      | 2025-09-19 00:54:53.652404+00
  43 |       28 |       35 |        |        17 |                      | t         | {"color_program": "Limited Edition"}                                                                | 2025-09-19 00:54:53.652404+00
  44 |       29 |       29 |        |        18 |                      | t         | {"color_program": "Essential"}                                                                      | 2025-09-19 00:54:53.652404+00
  45 |       29 |       37 |        |        18 |                      | t         | {"color_program": "Limited Edition"}                                                                | 2025-09-19 00:54:53.652404+00
  46 |       30 |       37 |        |        18 |                      | t         | {"color_program": "Limited Edition"}                                                                | 2025-09-19 00:54:53.652404+00
  47 |       31 |       29 |        |        18 |                      | t         | {"color_program": "Essential"}                                                                      | 2025-09-19 00:54:53.652404+00
  51 |       14 |       24 |        |        20 |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  52 |       14 |       25 |        |        20 |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  53 |       14 |       26 |        |        20 |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  54 |       15 |       25 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  55 |       15 |       27 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  56 |       15 |       28 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  57 |       15 |       29 |        |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  58 |       16 |       30 |      6 |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  59 |       16 |       30 |      8 |           |                      | t         | {}                                                                                                  | 2025-09-19 01:03:54.334073+00
  60 |       37 |       50 |      5 |        24 |                      | t         | {}                                                                                                  | 2025-09-19 03:29:02.268695+00
  61 |       37 |       50 |      5 |           |                      | t         | {}                                                                                                  | 2025-09-19 03:31:07.892102+00
  62 |       39 |       52 |      5 |           |                      | t         | {"brand_color_code": null}                                                                          | 2025-09-19 04:45:37.930385+00
  63 |       40 |       53 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  64 |       40 |       54 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  65 |       40 |       55 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  66 |       40 |       56 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  67 |       40 |       27 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  68 |       40 |       57 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  69 |       40 |       58 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  70 |       40 |       59 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  71 |       40 |       60 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  72 |       40 |       61 |        |        25 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:08:34.122131+00
  73 |       41 |       62 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:15:40.279942+00
  75 |       41 |       28 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:19:23.431746+00
  76 |       41 |       65 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:19:23.431746+00
  77 |       41 |       66 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:19:23.431746+00
  78 |       42 |       67 |        |        26 | US-WOMENS-ALPHA-PLUS | t         | {"collection": "Classic Shades"}                                                                    | 2025-10-12 02:21:28.455659+00
  79 |       42 |       68 |        |        26 | US-WOMENS-ALPHA-PLUS | t         | {"collection": "Limited Edition"}                                                                   | 2025-10-12 02:21:28.455659+00
  80 |       42 |       69 |        |        26 | US-WOMENS-ALPHA-PLUS | t         | {"collection": "Limited Edition"}                                                                   | 2025-10-12 02:21:28.455659+00
  81 |       42 |       70 |        |        26 | US-WOMENS-ALPHA-PLUS | t         | {"collection": "Limited Edition"}                                                                   | 2025-10-12 02:21:28.455659+00
  82 |       42 |       71 |        |        26 | US-WOMENS-ALPHA-PLUS | t         | {"collection": "Limited Edition", "stock_status": "low"}                                            | 2025-10-12 02:21:28.455659+00
  83 |       43 |       72 |        |        27 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:24:24.652011+00
  84 |       43 |       73 |        |        27 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:24:24.652011+00
  85 |       43 |       74 |        |        27 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:24:24.652011+00
  86 |       43 |       75 |        |        27 | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:24:24.652011+00
  87 |       44 |       29 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:27:59.036735+00
  88 |       44 |       76 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:27:59.036735+00
  89 |       44 |       77 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:27:59.036735+00
  90 |       44 |       78 |        |           | US-WOMENS-ALPHA      | t         | {}                                                                                                  | 2025-10-12 02:27:59.036735+00
  99 |       46 |       84 |        |           | US-WOMENS-NUMERIC    | t         | {"sku": "6DRES02866", "source": "alc", "color_name": "Ivy"}                                         | 2025-10-12 05:22:34.154378+00
 101 |       48 |       86 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "COEL-WD395", "source": "revolve", "pattern": "butterfly", "color_name": "Brown Butterfly"} | 2025-10-12 05:31:28.999821+00
 102 |       49 |       87 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ACDR100133NC", "source": "astr", "pattern": "floral", "color_name": "Brown Floral"}        | 2025-10-12 05:34:10.700582+00
 103 |       50 |       80 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Wine"}                                        | 2025-10-12 05:35:30.786754+00
 104 |       50 |       88 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Dark Sage"}                                   | 2025-10-12 05:35:30.786754+00
 105 |       50 |       89 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Lilac"}                                       | 2025-10-12 05:35:30.786754+00
 106 |       50 |       90 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Lime"}                                        | 2025-10-12 05:35:30.786754+00
 107 |       50 |       91 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Slate Blue"}                                  | 2025-10-12 05:35:30.786754+00
 108 |       50 |       29 |        |           | US-WOMENS-ALPHA      | t         | {"sku": "ADR102384", "source": "astr", "color_name": "Black"}                                       | 2025-10-12 05:35:30.786754+00
 109 |       51 |       92 |        |           | US-WOMENS-ALPHA      | f         | {"sku": "IPK1469D", "source": "vici", "pattern": "floral", "color_name": "Burgundy"}                | 2025-10-12 05:43:27.929265+00
 110 |       51 |       93 |        |           | US-WOMENS-ALPHA      | f         | {"sku": "IPK1469D", "source": "vici", "pattern": "floral", "color_name": "Red"}                     | 2025-10-12 05:43:27.929265+00
(78 rows)

           ?column?           
------------------------------
 -- PRODUCT URLS (51 records)
(1 row)

 id | style_id | variant_id | region |                                                                                                                   url                                                                                                                    | is_current |            seen_at            
----+----------+------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+------------+-------------------------------
  1 |       18 |         21 | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&colorProductCode=CP682&color_name=tim-white-blue            | t          | 2025-09-19 00:54:53.652404+00
  2 |       18 |         22 | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&colorProductCode=CP682&color_name=tim-white-blue               | t          | 2025-09-19 00:54:53.652404+00
  3 |       18 |         23 | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Tall&colorProductCode=CP682&color_name=tim-white-blue               | t          | 2025-09-19 00:54:53.652404+00
  4 |       20 |         27 | US     | https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html                                                                                                                                         | t          | 2025-09-19 00:54:53.652404+00
  5 |       20 |         28 | US     | https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104_G0F.html                                                                                                                                         | t          | 2025-09-19 00:54:53.652404+00
  6 |       27 |            | US     | https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html                                                                                                                                                   | t          | 2025-09-19 00:54:53.652404+00
  7 |       27 |         39 | US     | https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=1275                                                                                                                                        | t          | 2025-09-19 00:54:53.652404+00
  8 |       27 |         40 | US     | https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=14396                                                                                                                                       | t          | 2025-09-19 00:54:53.652404+00
  9 |       27 |         41 | US     | https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-dress/109178.html?color=32383                                                                                                                                       | t          | 2025-09-19 00:54:53.652404+00
 10 |       14 |         51 | UK     | https://www.reiss.com/style/su422501/e71002#e71002                                                                                                                                                                                       | t          | 2025-09-19 01:03:54.334073+00
 11 |       14 |         52 | UK     | https://www.reiss.com/style/su422501/e70998                                                                                                                                                                                              | t          | 2025-09-19 01:03:54.334073+00
 12 |       14 |         53 | UK     | https://www.reiss.com/style/su422501/ab2005                                                                                                                                                                                              | t          | 2025-09-19 01:03:54.334073+00
 13 |       15 |         54 | US     | https://www.reiss.com/us/en/style/su538118/f18169                                                                                                                                                                                        | t          | 2025-09-19 01:03:54.334073+00
 14 |       15 |         55 | US     | https://www.reiss.com/us/en/style/su538118/aw1262                                                                                                                                                                                        | t          | 2025-09-19 01:03:54.334073+00
 15 |       15 |         56 | US     | https://www.reiss.com/us/en/style/su538118/f18163                                                                                                                                                                                        | t          | 2025-09-19 01:03:54.334073+00
 16 |       15 |         57 | US     | https://www.reiss.com/us/en/style/su538118/f18205                                                                                                                                                                                        | t          | 2025-09-19 01:03:54.334073+00
 17 |       17 |         20 | UK     | https://www.reiss.com/style/su936297/ap6308#ap6308                                                                                                                                                                                       | t          | 2025-09-19 01:03:54.334073+00
 18 |       18 |            | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Classic&color_name=white&colorProductCode=CP682                     | t          | 2025-09-19 01:24:41.873246+00
 19 |       19 |            | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/business-casual-shirts/slim-bowery-performance-stretch-dress-shirt-with-spread-collar/BX291?display=standard&fit=Classic&colorProductCode=BX291&color_name=ryan-gray-white | t          | 2025-09-19 01:24:41.873246+00
 20 |       21 |            | US     | https://www.theory.com/men/shirts/sylvain-shirt-in-structure-knit/J0794505.html                                                                                                                                                          | t          | 2025-09-19 01:29:45.691581+00
 21 |       22 |            | US     | https://www.theory.com/men/shirts/sylvain-shirt-in-good-cotton/A0674535.html                                                                                                                                                             | t          | 2025-09-19 01:29:45.691581+00
 22 |       23 |            | US     | https://www.theory.com/men/shirts/sylvain-shirt-in-structure-twill/P0794514.html                                                                                                                                                         | t          | 2025-09-19 01:29:45.691581+00
 23 |       24 |            | US     | https://www.theory.com/men/shirts/button-up-shirt-in-textured-check/P0774503.html                                                                                                                                                        | t          | 2025-09-19 01:29:45.691581+00
 24 |       25 |            | US     | https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-summer-denim/P0574502.html                                                                                                                                                  | t          | 2025-09-19 01:29:45.691581+00
 25 |       26 |            | US     | https://www.theory.com/men/shirts/noll-short-sleeve-shirt-in-cotton-blend/P0574506.html                                                                                                                                                  | t          | 2025-09-19 01:29:45.691581+00
 26 |       20 |            | US     | https://www.theory.com/men/blazers-and-jackets/chambers-blazer-in-stretch-wool/I0171104.html                                                                                                                                             | t          | 2025-09-19 01:29:45.691581+00
 27 |       28 |            | US     | https://www.aritzia.com/us/en/product/figureknit%E2%84%A2-eyecatcher-mini-dress/121483.html                                                                                                                                              | t          | 2025-09-19 01:29:45.691581+00
 28 |       29 |            | US     | https://www.aritzia.com/us/en/product/original-contour-ravish-dress/123919.html                                                                                                                                                          | t          | 2025-09-19 01:29:45.691581+00
 29 |       30 |            | US     | https://www.aritzia.com/us/en/product/original-contour-maxi-tube-dress/118760.html                                                                                                                                                       | t          | 2025-09-19 01:29:45.691581+00
 30 |       31 |            | US     | https://www.aritzia.com/us/en/product/original-contour-mini-tube-dress/118308.html                                                                                                                                                       | t          | 2025-09-19 01:29:45.691581+00
 31 |       16 |         59 | US     | https://www.reiss.com/us/en/style/su615998/f77495                                                                                                                                                                                        | t          | 2025-09-19 01:29:45.691581+00
 32 |       16 |         58 | US     | https://www.reiss.com/us/en/style/su615998/f78985                                                                                                                                                                                        | t          | 2025-09-19 01:29:45.691581+00
 33 |       15 |         54 | US     | https://www.reiss.com/us/en/style/su538118/f18169                                                                                                                                                                                        | t          | 2025-09-19 02:53:02.701004+00
 34 |       18 |            | US     | https://www.jcrew.com/p/mens/categories/clothing/dress-shirts/tech-bowery/bowery-performance-stretch-oxford-shirt-with-button-down-collar/CP682?display=standard&fit=Slim&color_name=tim-white-blue&colorProductCode=CP682               | t          | 2025-09-19 02:53:16.694427+00
 35 |       37 |            | US     | https://www.jcrew.com/p/mens/categories/clothing/shirts/cotton-cashmere/cotton-cashmere-blend-shirt/ME053?display=standard&fit=Classic&color_name=dark-azure&colorProductCode=CC100                                                      | t          | 2025-09-19 03:29:02.268695+00
 36 |       40 |         67 | US     | https://www.thereformation.com/products/oren-silk-dress/1314259NVY.html                                                                                                                                                                  | t          | 2025-10-12 02:08:40.263425+00
 37 |       41 |         73 | US     | https://www.revolve.com/lovers-and-friends-rossa-maxi-dress-in-light-pink/dp/LOVF-WD4013/                                                                                                                                                | t          | 2025-10-12 02:15:47.361198+00
 38 |       42 |         78 | CA     | https://skims.com/en-ca/products/soft-lounge-long-slip-dress-onyx                                                                                                                                                                        | t          | 2025-10-12 02:21:35.167591+00
 39 |       43 |         83 | US     | https://www.thereformation.com/products/elise-knit-dress/1315811.html                                                                                                                                                                    | t          | 2025-10-12 02:24:31.185894+00
 40 |       44 |         87 | US     | https://www.freepeople.com/shop/onda-drop-waist-tube-midi/                                                                                                                                                                               | t          | 2025-10-12 02:28:06.574707+00
 51 |       46 |         99 | US     | https://alcltd.com/products/lara-gown-ivy                                                                                                                                                                                                | t          | 2025-10-12 05:26:14.696826+00
 53 |       48 |        101 | US     | https://www.revolve.com/camila-coelho-gilma-maxi-dress-in-brown-butterfly/dp/COEL-WD395/                                                                                                                                                 | t          | 2025-10-12 05:31:36.018989+00
 54 |       49 |        102 | US     | https://www.astrthelabel.com/products/gaia-dress-acdr100133nc                                                                                                                                                                            | t          | 2025-10-12 05:34:17.865704+00
 55 |       50 |        103 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=wine                                                                                                                                                                 | t          | 2025-10-12 05:35:40.680915+00
 56 |       50 |        104 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=darksage                                                                                                                                                             | t          | 2025-10-12 05:35:40.680915+00
 57 |       50 |        105 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=lilac                                                                                                                                                                | t          | 2025-10-12 05:35:40.680915+00
 58 |       50 |        106 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=lime                                                                                                                                                                 | t          | 2025-10-12 05:35:40.680915+00
 59 |       50 |        107 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=slateblue                                                                                                                                                            | t          | 2025-10-12 05:35:40.680915+00
 60 |       50 |        108 | US     | https://www.astrthelabel.com/products/maeve-dress-adr102384?variant=black                                                                                                                                                                | t          | 2025-10-12 05:35:40.680915+00
 61 |       51 |        109 | US     | https://www.vicicollection.com/products/floral-print-satin-and-lace-maxi-dress-with-cutout?variant=burgundy                                                                                                                              | t          | 2025-10-12 05:43:39.300949+00
 62 |       51 |        110 | US     | https://www.vicicollection.com/products/floral-print-satin-and-lace-maxi-dress-with-cutout?variant=red                                                                                                                                   | t          | 2025-10-12 05:43:39.300949+00
(51 rows)

           ?column?            
-------------------------------
 -- PRICE HISTORY (61 records)
(1 row)

 id | variant_id | region | currency | list_price | sale_price |          captured_at          
----+------------+--------+----------+------------+------------+-------------------------------
  3 |         27 | US     | USD      |     625.00 |     468.75 | 2025-09-19 00:54:53.652404+00
  4 |         28 | US     | USD      |     625.00 |     468.75 | 2025-09-19 00:54:53.652404+00
  5 |         39 | US     | USD      |     148.00 |     148.00 | 2025-09-19 00:54:53.652404+00
  6 |         40 | US     | USD      |     148.00 |     148.00 | 2025-09-19 00:54:53.652404+00
  7 |         41 | US     | USD      |     148.00 |     148.00 | 2025-09-19 00:54:53.652404+00
  8 |         42 | US     | USD      |     128.00 |     128.00 | 2025-09-19 00:54:53.652404+00
  9 |         43 | US     | USD      |     128.00 |     128.00 | 2025-09-19 00:54:53.652404+00
 10 |         44 | US     | USD      |      78.00 |      78.00 | 2025-09-19 00:54:53.652404+00
 11 |         45 | US     | USD      |      78.00 |      78.00 | 2025-09-19 00:54:53.652404+00
 12 |         46 | US     | USD      |      98.00 |      98.00 | 2025-09-19 00:54:53.652404+00
 13 |         47 | US     | USD      |      78.00 |      78.00 | 2025-09-19 00:54:53.652404+00
 14 |         54 | US     | USD      |     220.00 |     220.00 | 2025-09-19 01:08:40.419417+00
 18 |         54 | US     | USD      |     220.00 |     220.00 | 2025-09-19 02:53:02.701004+00
 15 |         55 | US     | USD      |     220.00 |     220.00 | 2025-09-19 01:08:40.419417+00
 16 |         56 | US     | USD      |     220.00 |     220.00 | 2025-09-19 01:08:40.419417+00
 17 |         57 | US     | USD      |     220.00 |     220.00 | 2025-09-19 01:08:40.419417+00
 19 |         60 | US     | USD      |     148.00 |     119.50 | 2025-09-19 03:29:02.268695+00
 20 |         62 | US     | USD      |            |            | 2025-09-19 04:45:37.930385+00
 21 |         63 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 22 |         64 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 23 |         65 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 24 |         66 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 25 |         67 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 26 |         68 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 27 |         69 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 28 |         70 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 29 |         71 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 30 |         72 | US     | USD      |     348.00 |            | 2025-10-12 02:08:49.134009+00
 31 |         73 | US     | USD      |     199.00 |            | 2025-10-12 02:15:59.454321+00
 33 |         75 | US     | USD      |     199.00 |            | 2025-10-12 02:19:29.747444+00
 34 |         76 | US     | USD      |     199.00 |            | 2025-10-12 02:19:29.747444+00
 35 |         77 | US     | USD      |     199.00 |            | 2025-10-12 02:19:29.747444+00
 41 |         78 | US     | USD      |     110.00 |            | 2025-10-12 02:21:42.735648+00
 36 |         78 | CA     | CAD      |     150.00 |            | 2025-10-12 02:21:42.735648+00
 42 |         79 | US     | USD      |     110.00 |            | 2025-10-12 02:21:42.735648+00
 37 |         79 | CA     | CAD      |     150.00 |            | 2025-10-12 02:21:42.735648+00
 38 |         80 | CA     | CAD      |     150.00 |            | 2025-10-12 02:21:42.735648+00
 43 |         80 | US     | USD      |     110.00 |            | 2025-10-12 02:21:42.735648+00
 44 |         81 | US     | USD      |     110.00 |            | 2025-10-12 02:21:42.735648+00
 39 |         81 | CA     | CAD      |     150.00 |            | 2025-10-12 02:21:42.735648+00
 40 |         82 | CA     | CAD      |     150.00 |            | 2025-10-12 02:21:42.735648+00
 45 |         82 | US     | USD      |     110.00 |            | 2025-10-12 02:21:42.735648+00
 46 |         83 | US     | USD      |     178.00 |            | 2025-10-12 02:24:38.306463+00
 47 |         84 | US     | USD      |     178.00 |            | 2025-10-12 02:24:38.306463+00
 48 |         85 | US     | USD      |     178.00 |            | 2025-10-12 02:24:38.306463+00
 49 |         86 | US     | USD      |     178.00 |            | 2025-10-12 02:24:38.306463+00
 50 |         87 | US     | USD      |      78.00 |            | 2025-10-12 02:28:14.243376+00
 51 |         88 | US     | USD      |      78.00 |            | 2025-10-12 02:28:14.243376+00
 52 |         89 | US     | USD      |      78.00 |            | 2025-10-12 02:28:14.243376+00
 53 |         90 | US     | USD      |      78.00 |            | 2025-10-12 02:28:14.243376+00
 63 |         99 | US     | USD      |     795.00 |            | 2025-10-12 05:26:20.977723+00
 65 |        101 | US     | USD      |     258.00 |            | 2025-10-12 05:31:37.966687+00
 66 |        102 | US     | USD      |     148.00 |            | 2025-10-12 05:34:19.778749+00
 67 |        103 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 68 |        104 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 69 |        105 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 70 |        106 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 71 |        107 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 72 |        108 | US     | USD      |     128.00 |            | 2025-10-12 05:35:43.183683+00
 73 |        109 | US     | USD      |      74.00 |            | 2025-10-12 05:43:39.300949+00
 74 |        110 | US     | USD      |      74.00 |            | 2025-10-12 05:43:39.300949+00
(61 rows)

           ?column?            
-------------------------------
 -- VARIANT CODES (42 records)
(1 row)

 id | variant_id |        code         |     code_type      | region 
----+------------+---------------------+--------------------+--------
 10 |         20 | AP6-308             | product_code       | ALL
 11 |         21 | CP682               | item_code          | ALL
 12 |         22 | CP684               | item_code          | ALL
 13 |         23 | CP683               | item_code          | ALL
 14 |         24 | BX291               | item_code          | ALL
 15 |         25 | CA351               | item_code          | ALL
 16 |         26 | CA352               | item_code          | ALL
 17 |         27 | I0171104_G0F        | suffix             | ALL
 18 |         28 | I0171104_G0F        | suffix             | ALL
 19 |         39 | 109178-1275         | derived_color_id   | ALL
 20 |         40 | 109178-14396        | derived_color_id   | ALL
 21 |         41 | 109178-32383        | derived_color_id   | ALL
 22 |         42 | 121483-1274         | derived_color_id   | ALL
 23 |         43 | 121483-14396        | derived_color_id   | ALL
 24 |         44 | 123919-1274         | derived_color_id   | ALL
 25 |         45 | 123919-33952        | derived_color_id   | ALL
 26 |         46 | 118760-33952        | derived_color_id   | ALL
 27 |         47 | 118308-1274         | derived_color_id   | ALL
 28 |         51 | E71-002             | product_code       | ALL
 29 |         52 | E70-998             | product_code       | ALL
 30 |         53 | AB2-005             | product_code       | ALL
 31 |         54 | F18-169             | product_code       | ALL
 32 |         55 | AW1-262             | product_code       | ALL
 33 |         56 | F18-163             | product_code       | ALL
 34 |         57 | F18-205             | product_code       | ALL
 35 |         58 | F78-985             | product_code       | ALL
 36 |         59 | F77-495             | product_code       | ALL
 42 |         60 | ME053               | item_code          | ALL
 43 |         61 | CC100               | color_product_code | ALL
 44 |         62 | BX291               | item_code          | ALL
 45 |         73 | LOVF-WD4013         | SKU                | US
 48 |         99 | 6DRES02866          | SKU                | US
 50 |        101 | COEL-WD395          | SKU                | US
 51 |        102 | ACDR100133NC        | SKU                | US
 52 |        103 | ADR102384-WINE      | SKU                | US
 53 |        104 | ADR102384-DARKSAGE  | SKU                | US
 54 |        105 | ADR102384-LILAC     | SKU                | US
 55 |        106 | ADR102384-LIME      | SKU                | US
 56 |        107 | ADR102384-SLATEBLUE | SKU                | US
 57 |        108 | ADR102384-BLACK     | SKU                | US
 58 |        109 | IPK1469D-BURGUNDY   | SKU                | US
 59 |        110 | IPK1469D-RED        | SKU                | US
(42 rows)

         ?column?          
---------------------------
 -- INVENTORY (58 records)
(1 row)

 id | variant_id | size_label | region |    status    | qty |          captured_at          
----+------------+------------+--------+--------------+-----+-------------------------------
 22 |         99 | 0          | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 21 |         99 | 00         | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 27 |         99 | 10         | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 28 |         99 | 12         | US     | out_of_stock |     | 2025-10-12 05:26:49.680954+00
 29 |         99 | 14         | US     | out_of_stock |     | 2025-10-12 05:26:49.680954+00
 23 |         99 | 2          | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 24 |         99 | 4          | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 25 |         99 | 6          | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 26 |         99 | 8          | US     | in_stock     |     | 2025-10-12 05:26:49.680954+00
 39 |        101 | L          | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 38 |        101 | M          | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 37 |        101 | S          | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 40 |        101 | XL         | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 36 |        101 | XS         | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 35 |        101 | XXS        | US     | in_stock     |     | 2025-10-12 05:31:42.478638+00
 44 |        102 | L          | US     | in_stock     |     | 2025-10-12 05:34:24.695246+00
 43 |        102 | M          | US     | in_stock     |     | 2025-10-12 05:34:24.695246+00
 42 |        102 | S          | US     | out_of_stock |     | 2025-10-12 05:34:24.695246+00
 45 |        102 | XL         | US     | out_of_stock |     | 2025-10-12 05:34:24.695246+00
 41 |        102 | XS         | US     | out_of_stock |     | 2025-10-12 05:34:24.695246+00
 49 |        103 | L          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 48 |        103 | M          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 47 |        103 | S          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 50 |        103 | XL         | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 46 |        103 | XS         | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 54 |        104 | L          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 53 |        104 | M          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 52 |        104 | S          | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 55 |        104 | XL         | US     | out_of_stock |     | 2025-10-12 05:36:00.631737+00
 51 |        104 | XS         | US     | in_stock     |     | 2025-10-12 05:36:00.631737+00
 59 |        105 | L          | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 58 |        105 | M          | US     | in_stock     |     | 2025-10-12 05:36:03.549721+00
 57 |        105 | S          | US     | in_stock     |     | 2025-10-12 05:36:03.549721+00
 60 |        105 | XL         | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 56 |        105 | XS         | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 64 |        106 | L          | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 63 |        106 | M          | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 62 |        106 | S          | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 65 |        106 | XL         | US     | out_of_stock |     | 2025-10-12 05:36:03.549721+00
 61 |        106 | XS         | US     | in_stock     |     | 2025-10-12 05:36:03.549721+00
 69 |        107 | L          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 68 |        107 | M          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 67 |        107 | S          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 70 |        107 | XL         | US     | out_of_stock |     | 2025-10-12 05:36:06.719054+00
 66 |        107 | XS         | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 74 |        108 | L          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 73 |        108 | M          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 72 |        108 | S          | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 75 |        108 | XL         | US     | out_of_stock |     | 2025-10-12 05:36:06.719054+00
 71 |        108 | XS         | US     | in_stock     |     | 2025-10-12 05:36:06.719054+00
 79 |        109 | L          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 78 |        109 | M          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 77 |        109 | S          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 80 |        109 | XL         | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 76 |        109 | XS         | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 83 |        110 | L          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 82 |        110 | M          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
 81 |        110 | S          | US     | out_of_stock |     | 2025-10-12 05:43:48.652019+00
(58 rows)

           ?column?            
-------------------------------
 -- PRODUCT IMAGES (1 records)
(1 row)

 id | style_id | variant_id | region |                                                             url                                                             | position | is_primary | color_code | alt | source |          captured_at          
----+----------+------------+--------+-----------------------------------------------------------------------------------------------------------------------------+----------+------------+------------+-----+--------+-------------------------------
  1 |       30 |            | US     | https://assets.aritzia.com/image/upload/c_crop,ar_1920:2623,g_south/q_auto,f_auto,dpr_auto,w_1500/f25_a08_118760_34880_on_a |        0 | t          |            |     | scrape | 2025-09-19 04:27:06.163599+00
(1 row)

        ?column?         
-------------------------
 -- PROFILES (0 records)
(1 row)

          ?column?           
-----------------------------
 -- USER CLOSETS (0 records)
(1 row)

 id | user_id | variant_id | size | created_at | env 
----+---------+------------+------+------------+-----
(0 rows)

          ?column?           
-----------------------------
 -- FIT FEEDBACK (0 records)
(1 row)

 id | user_id | variant_id | tried_size | fit_result | notes | created_at | env 
----+---------+------------+------------+------------+-------+------------+-----
(0 rows)

           ?column?            
-------------------------------
 -- BRAND PROFILES (1 records)
(1 row)

 id | brand_id | slug  |                                                                                                                                          rules                                                                                                                                          |                                   notes_md                                    
----+----------+-------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+-------------------------------------------------------------------------------
  1 |        7 | jcrew | {"fit_codes": {"Slim": "item_code", "Tall": "item_code", "Classic": "item_code"}, "variant_url": "style_level", "price_source": "page_state", "derived_fields": {"fabric": "Cotton-Cashmere"}, "color_code_source": "colorsList[*].colors[*].code", "style_code_source": "url_segment"} | J.Crew: BX291/CP682 patterns; use item codes per fit; colors from colorsList.
(1 row)

          ?column?           
-----------------------------
 -- STYLE CODES (20 records)
(1 row)

 id | style_id |   code   | code_type  | region 
----+----------+----------+------------+--------
 14 |       14 | su422501 | style_code | ALL
 15 |       15 | su538118 | style_code | ALL
 16 |       16 | su615998 | style_code | ALL
 17 |       17 | su936297 | style_code | ALL
 18 |       18 | CP682    | item_code  | ALL
 19 |       19 | BX291    | item_code  | ALL
 20 |       20 | I0171104 | style_code | ALL
 21 |       21 | J0794505 | style_code | ALL
 22 |       22 | A0674535 | style_code | ALL
 23 |       23 | P0794514 | style_code | ALL
 24 |       24 | P0774503 | style_code | ALL
 25 |       25 | P0574502 | style_code | ALL
 26 |       26 | P0574506 | style_code | ALL
 27 |       27 | 109178   | style_code | ALL
 28 |       28 | 121483   | style_code | ALL
 29 |       29 | 123919   | style_code | ALL
 30 |       30 | 118760   | style_code | ALL
 31 |       31 | 118308   | style_code | ALL
 37 |       37 | ME053    | item_code  | ALL
 39 |       39 | BX291    | style_code | ALL
(20 rows)

           ?column?            
-------------------------------
 -- INGESTION JOBS (2 records)
(1 row)

 id |    brand    | source_url | payload | status  | started_at |          finished_at          | error |                    category_url                    |    totals     |          created_at           | notes 
----+-------------+------------+---------+---------+------------+-------------------------------+-------+----------------------------------------------------+---------------+-------------------------------+-------
  1 | Reformation |            |         | done    |            | 2025-10-12 04:55:43.089289+00 |       | https://www.thereformation.com/collections/dresses | {"tasks": 2}  | 2025-10-12 04:54:46.521905+00 | 
  2 | Reformation |            |         | running |            |                               |       | https://www.thereformation.com/dresses             | {"tasks": 65} | 2025-10-12 05:02:10.093502+00 | 
(2 rows)

            ?column?             
---------------------------------
 -- INGESTION TASKS (67 records)
(1 row)

 id | job_id |                                                pdp_url                                                 | status |                                    last_error                                     | retries |          created_at           |          started_at           | finished_at 
----+--------+--------------------------------------------------------------------------------------------------------+--------+-----------------------------------------------------------------------------------+---------+-------------------------------+-------------------------------+-------------
  1 |      1 | https://www.thereformation.com/products/GIFT_CARD.html                                                 | error  | there is no unique or exclusion constraint matching the ON CONFLICT specification |       3 | 2025-10-12 04:55:08.29909+00  | 2025-10-12 04:55:39.373396+00 | 
  2 |      1 | https://www.onetrust.com/products/cookie-consent/                                                      | error  | there is no unique or exclusion constraint matching the ON CONFLICT specification |       3 | 2025-10-12 04:55:08.330389+00 | 2025-10-12 04:55:41.15678+00  | 
  3 |      2 | https://www.thereformation.com/products/franceska-dress/1318964SBY.html?dwvar_1318964SBY_color=SBY     | queued |                                                                                   |       0 | 2025-10-12 05:02:32.570765+00 |                               | 
  4 |      2 | https://www.thereformation.com/products/frankie-dress/1314189LCK.html?dwvar_1314189LCK_color=LCK       | queued |                                                                                   |       0 | 2025-10-12 05:02:32.604694+00 |                               | 
  5 |      2 | https://www.thereformation.com/products/frankie-dress/1314189LCK.html?dwvar_1314189LCK_color=ICX       | queued |                                                                                   |       0 | 2025-10-12 05:02:32.636104+00 |                               | 
  6 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=LYI         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.667351+00 |                               | 
  7 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=FDL         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.698498+00 |                               | 
  8 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=CRQ         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.728698+00 |                               | 
  9 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=BLK         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.759741+00 |                               | 
 10 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=OOL         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.791832+00 |                               | 
 11 |      2 | https://www.thereformation.com/products/maven-dress/1316476LYI.html?dwvar_1316476LYI_color=TON         | queued |                                                                                   |       0 | 2025-10-12 05:02:32.824747+00 |                               | 
 12 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065NVY.html?dwvar_1319065NVY_color=NVY | queued |                                                                                   |       0 | 2025-10-12 05:02:32.855101+00 |                               | 
 13 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065NVY.html?dwvar_1319065NVY_color=ALO | queued |                                                                                   |       0 | 2025-10-12 05:02:32.885972+00 |                               | 
 14 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065NVY.html?dwvar_1319065NVY_color=OGN | queued |                                                                                   |       0 | 2025-10-12 05:02:32.916627+00 |                               | 
 15 |      2 | https://www.thereformation.com/products/lucine-dress/1317288MHG.html?dwvar_1317288MHG_color=MHG        | queued |                                                                                   |       0 | 2025-10-12 05:02:32.947375+00 |                               | 
 16 |      2 | https://www.thereformation.com/products/lucine-dress/1317288MHG.html?dwvar_1317288MHG_color=STY        | queued |                                                                                   |       0 | 2025-10-12 05:02:32.979104+00 |                               | 
 17 |      2 | https://www.thereformation.com/products/lucine-dress/1317288MHG.html?dwvar_1317288MHG_color=ELE        | queued |                                                                                   |       0 | 2025-10-12 05:02:33.009728+00 |                               | 
 18 |      2 | https://www.thereformation.com/products/camille-knit-dress/1318703CUS.html?dwvar_1318703CUS_color=CUS  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.040247+00 |                               | 
 19 |      2 | https://www.thereformation.com/products/camille-knit-dress/1318703CUS.html?dwvar_1318703CUS_color=OGN  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.071373+00 |                               | 
 20 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065OGN.html?dwvar_1319065OGN_color=OGN | queued |                                                                                   |       0 | 2025-10-12 05:02:33.101974+00 |                               | 
 21 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065OGN.html?dwvar_1319065OGN_color=ALO | queued |                                                                                   |       0 | 2025-10-12 05:02:33.132496+00 |                               | 
 22 |      2 | https://www.thereformation.com/products/jessalyn-silk-dress/1319065OGN.html?dwvar_1319065OGN_color=NVY | queued |                                                                                   |       0 | 2025-10-12 05:02:33.162723+00 |                               | 
 23 |      2 | https://www.thereformation.com/products/nemy-knit-dress/1316530CAF.html?dwvar_1316530CAF_color=CAF     | queued |                                                                                   |       0 | 2025-10-12 05:02:33.193716+00 |                               | 
 24 |      2 | https://www.thereformation.com/products/nemy-knit-dress/1316530CAF.html?dwvar_1316530CAF_color=CHN     | queued |                                                                                   |       0 | 2025-10-12 05:02:33.223973+00 |                               | 
 25 |      2 | https://www.thereformation.com/products/nemy-knit-dress/1316530CAF.html?dwvar_1316530CAF_color=PNT     | queued |                                                                                   |       0 | 2025-10-12 05:02:33.254331+00 |                               | 
 26 |      2 | https://www.thereformation.com/products/nemy-knit-dress/1316530CAF.html?dwvar_1316530CAF_color=BLK     | queued |                                                                                   |       0 | 2025-10-12 05:02:33.284833+00 |                               | 
 27 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=BLK         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.315317+00 |                               | 
 28 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=FDL         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.345986+00 |                               | 
 29 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=CRQ         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.377267+00 |                               | 
 30 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=LYI         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.407965+00 |                               | 
 31 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=OOL         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.438586+00 |                               | 
 32 |      2 | https://www.thereformation.com/products/maven-dress/1316476BLK.html?dwvar_1316476BLK_color=TON         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.469855+00 |                               | 
 33 |      2 | https://www.thereformation.com/products/jonelle-silk-dress/1318312MTT.html?dwvar_1318312MTT_color=MTT  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.502246+00 |                               | 
 34 |      2 | https://www.thereformation.com/products/jonelle-silk-dress/1318312MTT.html?dwvar_1318312MTT_color=HZN  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.533239+00 |                               | 
 35 |      2 | https://www.thereformation.com/products/jonelle-silk-dress/1318312MTT.html?dwvar_1318312MTT_color=SUA  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.563843+00 |                               | 
 36 |      2 | https://www.thereformation.com/products/jonelle-silk-dress/1318312MTT.html?dwvar_1318312MTT_color=NVY  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.596847+00 |                               | 
 37 |      2 | https://www.thereformation.com/products/jonelle-silk-dress/1318312MTT.html?dwvar_1318312MTT_color=RMC  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.627351+00 |                               | 
 38 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=SLT  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.659093+00 |                               | 
 39 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=CAF  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.689731+00 |                               | 
 40 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=ROB  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.720706+00 |                               | 
 41 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=TTR  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.751468+00 |                               | 
 42 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=HLW  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.782442+00 |                               | 
 43 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=LYI  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.812835+00 |                               | 
 44 |      2 | https://www.thereformation.com/products/frankie-silk-dress/1304134SLT.html?dwvar_1304134SLT_color=PIP  | queued |                                                                                   |       0 | 2025-10-12 05:02:33.843454+00 |                               | 
 45 |      2 | https://www.thereformation.com/products/monica-silk-dress/1318997SNG.html?dwvar_1318997SNG_color=SNG   | queued |                                                                                   |       0 | 2025-10-12 05:02:33.874076+00 |                               | 
 46 |      2 | https://www.thereformation.com/products/monica-silk-dress/1318997SNG.html?dwvar_1318997SNG_color=BLK   | queued |                                                                                   |       0 | 2025-10-12 05:02:33.906384+00 |                               | 
 47 |      2 | https://www.thereformation.com/products/irisa-dress/1313942DAM.html?dwvar_1313942DAM_color=DAM         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.940953+00 |                               | 
 48 |      2 | https://www.thereformation.com/products/irisa-dress/1313942DAM.html?dwvar_1313942DAM_color=PTF         | queued |                                                                                   |       0 | 2025-10-12 05:02:33.971896+00 |                               | 
 49 |      2 | https://www.thereformation.com/products/irisa-dress/1313942DAM.html?dwvar_1313942DAM_color=BBR         | queued |                                                                                   |       0 | 2025-10-12 05:02:34.003524+00 |                               | 
 50 |      2 | https://www.thereformation.com/products/irisa-dress/1313942DAM.html?dwvar_1313942DAM_color=LKU         | queued |                                                                                   |       0 | 2025-10-12 05:02:34.0355+00   |                               | 
 51 |      2 | https://www.thereformation.com/products/irisa-dress/1313942DAM.html?dwvar_1313942DAM_color=BLK         | queued |                                                                                   |       0 | 2025-10-12 05:02:34.067023+00 |                               | 
 52 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=MOR   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.09754+00  |                               | 
 53 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=FOE   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.127609+00 |                               | 
 54 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=RSX   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.158196+00 |                               | 
 55 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=HTE   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.188579+00 |                               | 
 56 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=HLW   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.22145+00  |                               | 
 57 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=MFO   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.252239+00 |                               | 
 58 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=NVY   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.283473+00 |                               | 
 59 |      2 | https://www.thereformation.com/products/anaiis-silk-dress/1314547MOR.html?dwvar_1314547MOR_color=TAV   | queued |                                                                                   |       0 | 2025-10-12 05:02:34.314849+00 |                               | 
 60 |      2 | https://www.thereformation.com/products/kayla-knit-dress/1317998RMC.html?dwvar_1317998RMC_color=RMC    | queued |                                                                                   |       0 | 2025-10-12 05:02:34.345547+00 |                               | 
 61 |      2 | https://www.thereformation.com/products/kayla-knit-dress/1317998RMC.html?dwvar_1317998RMC_color=FDL    | queued |                                                                                   |       0 | 2025-10-12 05:02:34.377198+00 |                               | 
 62 |      2 | https://www.thereformation.com/products/kayla-knit-dress/1317998RMC.html?dwvar_1317998RMC_color=PRI    | queued |                                                                                   |       0 | 2025-10-12 05:02:34.407917+00 |                               | 
 63 |      2 | https://www.thereformation.com/products/kayla-knit-dress/1317998RMC.html?dwvar_1317998RMC_color=OOL    | queued |                                                                                   |       0 | 2025-10-12 05:02:34.438434+00 |                               | 
 64 |      2 | https://www.thereformation.com/products/amor-two-piece/1318148LYI.html?dwvar_1318148LYI_color=LYI      | queued |                                                                                   |       0 | 2025-10-12 05:02:34.469063+00 |                               | 
 65 |      2 | https://www.thereformation.com/products/amor-two-piece/1318148LYI.html?dwvar_1318148LYI_color=CHN      | queued |                                                                                   |       0 | 2025-10-12 05:02:34.499665+00 |                               | 
 66 |      2 | https://www.thereformation.com/products/amor-two-piece/1318148LYI.html?dwvar_1318148LYI_color=CMZ      | queued |                                                                                   |       0 | 2025-10-12 05:02:34.532659+00 |                               | 
 67 |      2 | https://www.thereformation.com/products/amor-two-piece/1318148LYI.html?dwvar_1318148LYI_color=BLK      | queued |                                                                                   |       0 | 2025-10-12 05:02:34.562968+00 |                               | 
(67 rows)

          ?column?          
----------------------------
 -- INGEST RUNS (0 records)
(1 row)

 id | brand_id | source | started_at | finished_at | notes 
----+----------+--------+------------+-------------+-------
(0 rows)

          ?column?           
-----------------------------
 -- MEDIA ASSETS (0 records)
(1 row)

 id | style_id | variant_id | type | url | position | alt 
----+----------+------------+------+-----+----------+-----
(0 rows)

        ?column?         
-------------------------
 -- EVIDENCE (0 records)
(1 row)

 id | ingest_run_id | style_id | variant_id | url | raw_blob_ref | captured_at 
----+---------------+----------+------------+-----+--------------+-------------
(0 rows)

             ?column?              
-----------------------------------
 -- BRAND CATEGORY MAP (0 records)
(1 row)

 id | brand_id | original_label | category_id | created_at 
----+----------+----------------+-------------+------------
(0 rows)

            ?column?             
---------------------------------
 -- BRAND COLOR MAP (28 records)
(1 row)

 id | brand_id |     original     | color_id |      notes       
----+----------+------------------+----------+------------------
 26 |        6 | Soft Blue        |       25 | 
 27 |        6 | Stone            |       24 | 
 28 |        6 | Rust             |       26 | 
 29 |        6 | Navy             |       27 | 
 30 |        6 | White            |       28 | 
 31 |        6 | Black            |       29 | 
 32 |        6 | Pink             |       30 | 
 33 |        6 | Mid Blue         |       31 | 
 34 |        7 | tim white blue   |       33 | 
 35 |        7 | ryan-gray-white  |       32 | 
 36 |        7 | soft-blue-oxford |       25 | 
 37 |        7 | lilac-oxford     |       34 | 
 38 |        8 | Deep Black       |       38 | 
 39 |        8 | Medium Charcoal  |       39 | 
 40 |        8 | Ash              |       40 | 
 41 |        8 | Rainstorm        |       41 | 
 42 |        8 | Pestle           |       42 | 
 43 |        8 | Eclipse          |       43 | 
 44 |        8 | Dark Wash        |       44 | 
 45 |        8 | Black            |       29 | 
 46 |        9 | White            |       28 | Essential Colors
 47 |        9 | Bright White     |       35 | Limited Edition
 48 |        9 | Dreamhouse Pink  |       36 | Limited Edition
 49 |       10 | Black            |       29 | Essential Colors
 50 |       10 | Dayflower Blue   |       37 | Limited Edition
 52 |        7 | Tim White Blue   |       33 | 
 56 |        7 | Dark Azure       |       50 | 
 58 |        7 | Default          |       52 | 
(28 rows)

