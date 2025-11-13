### Key Tables (field highlights)

This is a concise, practical reference. For exhaustive schemas, see `DATABASE_SCHEMA_COMPLETE.md` and `daily-notes/2025-09-17/DATABASE_SCHEMA_ACTUAL.md`.

#### brands
- id (pk)
- name (text)
- region (text)
- default_unit (text)

Usage: lookup by `name`; referenced by `product_master`, `user_garments`.

#### product_master
- id (pk)
- brand_id → brands.id
- product_code (varchar) unique per base product
- base_name (text)
- materials (jsonb)
- care_instructions (text[])
- fit_information (jsonb)
- category_id → categories.id
- subcategory_id → subcategories.id

Usage: canonical record for a product; variants live in `product_variants`.

#### product_variants
- id (pk)
- product_master_id → product_master.id
- variant_code (text) or combination of `color_name`, `fit_option`
- color_name (text)
- fit_option (text)

Usage: represents color/fit permutations under a base product.

#### jcrew_product_cache
- product_code (text) unique
- product_name (text)
- product_url (text)
- product_image (text)
- sizes_available (text[])
- colors_available (text[])
- category/subcategory (text)
- fit_options (text[])

Usage: staging cache for scraped data; used to populate `product_master`/`product_variants` and for cleanup/consolidation scripts.

#### user_garments
- id (pk)
- user_id (int)
- brand_id → brands.id
- product_master_id → product_master.id (when linked)
- product_name (text)
- size_label (text)
- owns_garment (bool)
- fit_feedback (text) overall, plus dimensional via join

Usage: user’s wardrobe/try-ons; central to fit/feedback features.

#### user_garment_feedback
- id (pk)
- user_garment_id → user_garments.id
- dimension (text) e.g., 'chest','waist','sleeve','neck','overall'
- feedback_code_id → feedback_codes.id
- created_at (timestamp)

Usage: normalized dimensional feedback; latest feedback commonly selected per dimension.

#### feedback_codes
- id (pk)
- feedback_text (text) standardized tokens (e.g., 'Too tight','Perfect','Too loose')

Usage: canonical set for UX and logic; referenced by `user_garment_feedback`.

#### user_actions
- id (pk)
- user_id (int)
- action_type (text) e.g., 'submit_feedback','update_feedback','scan'
- target_table (text)
- target_id (int)
- metadata (jsonb)
- created_at (timestamp)

Usage: activity/audit trail for app actions and undo flows.

#### categories / subcategories
- categories.id, categories.name
- subcategories.id, subcategories.name

Usage: classification referenced by `product_master`.

#### measurement_sets / measurements (preferred system)
- measurement_sets: defines a set context (brand/category/fit)
- measurements: actual entries keyed by dimension and size

Usage: unified replacement for older `size_guides` structure.



