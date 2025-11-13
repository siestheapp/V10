Implementation Plan for Evolving the fs-core Database
Overview and Goals

The goal is to transform the current fs-core database into a unified, scalable foundation for the Fashion-Fit App. This new design will merge features from two previous systems – Tailor3 and FreestyleDB – and align with the Proposed Database Schema outlined in the provided PDF. The unified schema will support the app’s three phases: LOGGER (clothing try-on logging), SIES (size guide & measurement inference), and PROXI (social “size-twin” matching), while being robust enough for millions of users and garments. Key objectives include normalization of data, consolidation of overlapping features, and forward-looking design for future social additions (likes, saves, messages, etc.).

Key improvements in the target schema:

Consolidation of user fit logging into one comprehensive system (combining Tailor’s detailed feedback model with Freestyle’s simpler logging).

Introduction of a flexible measurement schema for size guides and garment measurements (replacing any hard-coded size fields with a measurement set model).

Separation of concerns via modular schemas or table groupings (core product data vs. user-generated content vs. auth/security data), following best practices for clarity and access control.

Proper use of Supabase features: leveraging Supabase Auth (UUID-based user IDs) and Storage (for images/videos) instead of storing sensitive or large data directly in tables.

Ensuring performance at scale with indexing, constraints, and considering partitioning or sharding strategies as needed for growth.

Aligning naming and structure to the Proposed Schema document for consistency and easier maintenance.

Below, we compare the current fs-core structure to the target design, identify gaps, and then detail a step-by-step plan to implement the new schema.

Current fs-core vs. Target Schema
Users and Profiles

Current: User accounts are managed by Supabase Auth (with a UUID auth.users table). The fs-core likely has a basic profile table (user_profile) to store app-specific info like username, but it may not enforce a foreign key to auth.users (in Freestyle DB, user_profile.id was a UUID with no explicit FK) and might lack additional user settings.

Target: Rely fully on Supabase’s auth.users for authentication and have a separate profiles table linked 1:1 with it. In the new schema, profiles.user_id is a UUID FK to auth.users.id (ensuring each app profile corresponds to a real auth user). This table will hold display name, avatar URL, etc., and can be extended with preferences (e.g. preferred units) which Tailor3 had conceptually planned in user_preferences.preferred_unit. Using UUIDs for user IDs and indexing the profile table on user_id ensures we can handle millions of users with fast lookups.

Changes: We need to update the current profile implementation to ensure a one-to-one profiles table with proper foreign keys to auth.users. If the current user_profile table is missing data or constraints, we will add user_id UUID NOT NULL (FK to auth.users) and migrate existing user info. This change improves data integrity (preventing orphan profiles) and security by keeping authentication data in the auth schema and profile data in a separate schema/table.

Brands, Categories, and Products

Current: The fs-core likely has tables for brands, products, and variants (in Freestyle, called brand, style, and variant). Brands in the current setup have basic fields (id, name, website) but may not enforce uniqueness or track region. Categories might exist as a single table (category) with a parent-child structure (Freestyle had category with parent_id and a slug) but possibly without a dedicated subcategory table. Freestyle’s design included mapping tables like brand_category_map to link a brand’s own category labels to a normalized category. Product data is likely split into a master style table and a variant table (as Freestyle did), but naming might differ (e.g. style and variant). For example, Freestyle’s style table tracked brand, category, gender, etc., and variant tracked color, fit, and had an attrs JSON for extra info. There was also a product_image table for images, price_history for pricing, and possibly variant_size for available sizes per variant.

Target: Use a normalized, two-tier product model: a products table (each a base style) and a product_variants table (specific SKU or option). In the new schema:

brands: Keep a brands table with id (bigserial PK), name, website, and optionally region. Add a unique index on (name, region) to prevent duplicates. We also include a default_unit field to record if a brand uses "cm" vs "in" for its measurements. A brand_profile extension table (1-to-1 with brand) will store extra metadata or rules. Notably, Freestyle’s brand_profile used a JSON field for brand-specific sizing quirks (e.g. “Brand runs small”); we will retain this idea so that brand-specific conversion rules or notes can be captured in JSON, along with any internal notes.

categories & subcategories: Implement a hierarchical taxonomy. A primary categories table holds top-level categories (e.g. “Shirt”, “Pants”) and can be self-referential for hierarchy or used in tandem with a subcategories table. Tailor3 had a separate subcategories table linked to a parent category, so we can do the same: each subcategory has a FK to its parent category. This prevents inconsistencies (e.g. “Jeans” always falls under “Pants”). We will enforce subcategories.category_id → categories.id. Additionally, maintain a brand_category_map table to map arbitrary category labels from various brands into our standardized categories – this proved useful in Freestyle and remains important when ingesting product data from different sources.

products: The products table (analogous to Freestyle’s style or Tailor’s product_master) will include: id (bigserial PK), brand_id (FK to brands), category_id (FK), subcategory_id (FK, optional), the brand’s product code or SKU (stored in a product_code field), a name (descriptive title), and other attributes like description, gender (which could be an enum or text), plus timestamps (created_at, updated_at). We will enforce that combination of brand_id + product_code is unique to avoid duplicate entries for the same style. This structure collects all generic information about a style in one place (e.g. a shirt’s general description or material), avoiding duplication across variants. (In the current fs-core, similar fields exist in style, but we will verify any differences, such as ensuring we have product_code and using consistent naming like product instead of style for clarity.)

product_variants: The product_variants table (analogous to Freestyle’s variant) stores variant-specific details: id (bigserial PK), product_id (FK to products), and fields like variant_code (the SKU for that specific color/size combination or an identifier), color_name (and optionally a standardized color_code or reference to a color table), fit_option (if the product has fit types like Regular/Slim), etc.. We will also include inventory-related info such as current_price (with currency), in_stock or quantity, and maybe a JSON attrs for any extra metadata (similar to Freestyle’s variant.attrs). Each variant can list what sizes are offered and which are in stock – in Freestyle, a separate variant_size table was used to list all size labels for a variant, and inventory records tracked stock by size. We can keep a simple approach: a sizes_available text array or a child table if needed, plus possibly a sizes_in_stock array or an inventory_history table for detailed stock changes (Freestyle had inventory_history to log status/qty over time). We will maintain an index on product_variants.product_id to quickly fetch all variants for a given product. All variant records will reference a valid product and thereby a brand, maintaining referential integrity via FKs.

Product media: Instead of embedding images in a JSON or array, we use a separate product_images table to store multiple images per product or variant. Each image entry has an id, a FK to either product_id or variant_id (allowing variant-specific images), a url (or storage path), and fields like position (to order images) and is_primary (to flag the main image). This design (already present in Freestyle’s product_image table) makes it easy to query and manage images and allows marking one primary image for quick access. We will also include optional metadata (dimensions, etc.) as needed.
For color consistency across brands, we have a mechanism to map brand-specific color names to a canonical color list (Freestyle had color_catalog and brand_color_map or color_swatch tables). We can incorporate a similar colors reference table and a mapping table if needed, to ensure one brand’s "Navy" and another’s "Midnight Blue" can be recognized as the same standard color internally. This is an optional enhancement that supports consistency in the PROXI phase when matching items by color.

Changes: The current schema’s tables (brand, style, variant, etc.) will be migrated/renamed to the new structure:

Rename style → products (and adjust columns to include product_code, enforce non-null brand/category).

Ensure variant → product_variants and add any missing fields (e.g. if current variant lacks fit_option or color_name, include them). If the current design has some fields in JSON (attrs), consider pulling out frequently queried attributes into columns for indexing (e.g. is_active, size_scale were present in Freestyle).

Add the product_images table if not already present (Freestyle had product_image in schema, which we can reuse but ensure it links to new product IDs and uses proper FK references).

Create categories and subcategories tables (if current fs-core only has a single categories list or none). Migrate any existing category data into this structure. Add the brand_category_map (and brand_profile, brand_color_map) as needed, migrating any data from Freestyle’s dump into these tables to preserve rules and mappings.

Enforce new constraints: unique index on brand name (and region), unique index on product (brand+code), unique index on category names per hierarchy, etc., to prevent duplicates and maintain data quality.

Size Guides and Measurements (SIES phase)

Current: The current fs-core likely has minimal support for structured size guides. Freestyle DB did not implement a flexible size chart model – it might have had some placeholders or none at all. Tailor3, on the other hand, had a more developed concept: it introduced a measurement set approach and moved away from fixed columns for each size. Tailor’s schema included legacy tables like size_guides and size_guide_entries (with columns like chest_min, chest_max, etc.), as well as garment_guide entries for specific garment measurements. These were being phased out in favor of a more normalized approach with measurement sets and entries. There was also an unused body_measurements table in Tailor for storing user body dimensions. In summary, the current state likely does not yet have the full measurement schema – this is a major missing piece.

Target: Implement a robust Measurement Set schema to handle any brand’s size chart or garment specifications flexibly. The design is inspired by Tailor3’s approach and detailed in the proposal:

measurement_sets: Each represents a collection of measurements (a size guide). This could be a brand-level size chart for a category (e.g. Levi’s men’s jeans chart) or a specific product’s spec sheet. Key fields for measurement_sets include an id (PK), a reference to what this guide applies to, and context fields. We will have FKs like brand_id, category_id and possibly gender or fit to identify the context of the guide. For a product-specific guide, we can use a product_id FK (or a separate field indicating it’s a garment-specific measurement set). We also include metadata such as title or guide_name (e.g. "Summer 2025 Size Chart"), and perhaps a boolean is_active. By ensuring each brand-category-gender-fit combination has at most one active guide at a time, we avoid ambiguity in lookup (this can be enforced with a unique index on those columns, or by including an effective_date/obsolete_date for versioning if we plan to keep historical guides).

measurements: A measurements table stores the actual measurement data points that belong to a measurement_set. Each row corresponds to one specific dimension for one size. Key fields: id (PK), set_id (FK to measurement_sets), size_label (text, e.g. "M", "32" etc.), measurement_type (text code for the dimension name, e.g. "chest", "waist", "sleeve_length"), and numeric fields for the measurement values. We support ranges by having perhaps min_value and max_value columns (if a size guide says a size fits a range, e.g. chest 38–40 inches, we store 38 and 40). If only a single value is given (like a garment spec of exactly 40 inches chest), we can store that in min_value and leave max_value null or equal. We also include a unit (or refer to the brand’s default_unit) to know whether values are in inches or centimeters. To handle different kinds of measurements, we might include a measurement_category (for example, distinguish between body measurements vs garment measurements if needed, or we infer it from context). Each measurement record ties back to its set so we can query all measurements for "Size M of Guide #123". This structure is highly flexible: adding a new measurement type (e.g. sleeve width) doesn’t require altering the schema, just adding new rows for that type.

Using this model, the system can support the SIES phase by linking products and size guides. For example, a products record might have a field measurement_set_id linking it to its specific spec sheet (if available). More commonly, a product’s recommended size guide might be determined by brand + category: we’d find the active measurement_set for that brand/category and use its measurements. The schema will also accommodate fit adjustments: if a particular product runs large or small, we could capture that either in the brand_profile.rules JSON (like “waist runs 2 inches large” adjustments) or by a specialized field. Tailor’s approach of capturing brand quirks will be preserved so that SIES calculations can be fine-tuned per brand.

Changes: We will create the new tables measurement_sets and measurements. Any existing tables like size_guide_entries or similar (from Tailor3) will be deprecated in favor of this model. If the current DB has no such tables, this is purely additive. We will migrate any useful data from the Tailor3 dump: for instance, if Tailor3 had a size guide for a particular brand, we will convert that into measurement_sets and measurements rows. We also update references: remove any obsolete references to old guide IDs in other tables. (E.g., Tailor’s user_garments had size_guide_id and size_guide_entry_id which were marked deprecated; in our unified schema, user logs will not point directly to those, but rather we can derive needed info via product and measurement sets.)

Finally, ensure indexing and constraints here: index measurements on set_id for quick retrieval of all sizes in a chart, and consider a composite unique index on (set_id, size_label, measurement_type) to prevent duplicate entries. We might also add check constraints to ensure min_value <= max_value when both exist, etc., for data consistency.

User Fit Logging (LOGGER phase)

Current: Currently, fs-core likely uses a simpler logging mechanism inherited from Freestyle – specifically:

A user_closet table to record garments a user owns or tried, with fields like user_id, variant_id, size (the size label worn) and perhaps a timestamp and an environment flag (env used in Freestyle to distinguish real vs. sandbox entries).

A separate fit_feedback table to capture basic fit outcomes, with fields such as user_id, variant_id, tried_size, a fit_result (e.g. numeric code or enum indicating too small/just right/too large), a freeform notes field, etc.. Each fit_feedback entry corresponded to one try-on event. In Freestyle’s design, these two tables were linked by user+variant+size, but not in a single row (meaning you’d join them to get both what was tried and how it fit). The feedback was simplistic – likely one overall fit rating per entry plus notes.

Freestyle’s data model didn’t explicitly track whether the user actually owns the item or just tried it; it may have assumed closet = owned, and used environment or other flags for try-ons. Also, Freestyle had RLS (row-level security) policies on these tables to ensure users only see their own data.

Tailor3’s approach was more sophisticated: it introduced a unified user_garments table and a related user_garment_feedback table. Each user_garments record in Tailor included fields to indicate ownership (owns_garment boolean) and status (garment_status like 'owned' vs 'tried'), as well as direct links to product_master_id and product_variant_id (instead of just variant). Tailor also allowed capturing a photo (tag_photo_path) and stored the source of input (scanned, linked, manual). Tailor’s user_garment_feedback table could record multiple feedback points for one user_garments entry – e.g. feedback on chest fit, sleeve length, etc., each referencing a standardized feedback code.

Target: We will combine and optimize both systems into one comprehensive logging schema. The core will be a UserGarments table (also called Fit Log entries) with auxiliary tables for detailed feedback and media:

user_garments: Each row represents a single instance of a user trying on or owning a particular product variant. It will include:

id (bigserial PK)

user_id (UUID FK to the user – using Supabase Auth ID)

product_id and variant_id (FKs to the item that was tried or owned). The presence of both allows linking to the catalog. In some cases, variant_id might be null initially (if the item isn’t in the catalog yet), but product_id or a placeholder product record should exist or be created. We’ll allow nulls temporarily with the expectation of back-filling once data is available (see “Logging workflow” below).

size_label – the size the user wore/tried (e.g. “M”, “32”, “8 US”). This is stored directly on the log entry for quick reference.

garment_status – an enum or text indicating the outcome/status (examples: 'owned', 'tried', 'returned', 'wishlist'). By default if a user logs an item, we might mark it 'owned' if they indicated they have it, or 'tried' if they just tried in a store. This replaces Freestyle’s use of separate tables or the env flag as a proxy for status. Tailor3’s default was 'owned', but we will make it explicit and extensible.

owns_garment (boolean) – we may include this for quick filtering (true if garment_status is owned, false if it was just tried on). In practice, garment_status alone might suffice, but this is a convenient denormalization.

Timestamps (created_at, etc.) and possibly a source or input_method field – e.g. 'link', 'scan', 'manual' – to record how the entry was added. If added via scanning a garment’s barcode or via entering a product URL, we capture that. Also a link_provided field to store a URL if the user logged the item by pasting a link (as Tailor did).

notes – a freeform text for any user comments about this specific try-on or purchase (Tailor had a notes field).

We do not store a single fit rating or result here (as Freestyle did in fit_feedback.fit_result); instead, detailed fit feedback goes into the related feedback table described next. However, for convenience we might include an overall_fit summary or rating in this table (could be a short code or numeric score) to allow quick filtering (e.g. user marks something “too small overall” without detail). This could be derived from the detailed feedback codes or set via a simplified prompt. It’s optional – our design leans on the detailed feedback entries for richness.

user_garment_feedback: A separate table capturing detailed fit feedback entries for a user_garments log. Multiple rows here can link to one user_garments.id. Fields include:

id (PK), user_garment_id (FK to user_garments), and possibly also user_id for convenience (and to simplify RLS policies – we can have a policy that user_id = auth.uid() on this table too) with a check or trigger to keep it in sync.

dimension – the aspect of fit this feedback is about, e.g. "chest", "waist", "length", or "overall".

feedback_code_id – FK to a feedback_codes reference table for standardized feedback phrases. For example, a feedback_code could represent "Too Tight" (of type fit issue) or "Too Short" (of type length issue). Using codes ensures consistency and easy analysis across users (everyone uses the same terms).

Optionally, measurement_source and measurement_id – these fields (from Tailor’s design) capture context if the feedback relates to a specific size guide measurement or a garment spec measurement. For instance, if a user says "Too tight in chest", the system might note whether this is relative to the size guide’s expected chest for that size or a garment’s actual measured chest. This can get complex; initially, we might omit or simplify these fields, but the schema leaves room (e.g. values could be 'size_guide', 'garment_spec', or 'none'). Tailor3 tracked this to differentiate whether feedback was about body vs garment dimensions. We can include it for future analytics.

created_at timestamp for when the feedback was given.

Using this design, each try-on (user_garments) can have multiple feedback points. For example, user_garment 123 (User tried product X in size M) might have two feedback entries: one with dimension="chest", feedback_code="Too Tight"; another with dimension="length", feedback_code="Too Short". This granular data is far richer than a single number rating. We also allow an "overall" dimension to capture general feedback like “Runs small overall”. An "overall fit" entry could be created behind the scenes if the user provides an overall rating, so we don’t need a separate column for it. This generalizes Freestyle’s single fit_result approach: instead of one fit_result field, we record an overall feedback entry and still capture specifics.

feedback_codes: A reference table listing all possible feedback options. Each code would have an id, a feedback_text (e.g. "Too Tight", "Perfect Fit"), and perhaps a feedback_type or category ("fit", "length", etc.). It might also include an order or severity. This table will be pre-populated with common fit comments to choose from (Tailor3’s dump provides a set of these codes). Having this table makes it easy to normalize user feedback and perform analytics like “how often do people report ‘Too Loose’ for this brand”.

user_garment_photos: To support image uploads for logged items, we introduce a table for photos (and possibly videos) associated with a user_garments entry. Each photo record has an id, user_garment_id (FK), a photo_url (or storage path reference), and metadata like is_primary (true for the main photo to display for that log), plus created_at. By using a separate table, a user can add multiple images per fit log (e.g. front, side pictures of the outfit). We can also accommodate videos in the same table by adding a media_type field (image/video) or a parallel table for videos – initially, we’ll keep it simple with one table and a type field. The actual files are stored in Supabase Storage (not in the database), and we only save the URLs/paths in this table. This ensures we scale efficiently for potentially millions of photos without bloating the database with blobs.

Logging Workflow Integration: When a user logs a new item in LOGGER, the flow will utilize these tables as follows: Upon entering a product URL or scanning a code, we create a placeholder user_garments entry with the information we have (user_id, maybe brand or product if known, and store the raw URL in link_provided). We then trigger a background ingestion job (the system has tables like ingestion_job and ingestion_task from Freestyle to handle scraping product data). As the product details get fetched and saved into our products and product_variants tables, we update the placeholder log entry with the correct product_id/variant_id. The user then records what size they tried (we update size_label in user_garments) and answers the fit questions, which create one or more user_garment_feedback records. If they upload a photo of the try-on, a user_garment_photos entry is added linking to that log. All of this ties the user’s experience back to the core product data and size guides, enabling the SIES phase to use these data points for refining the user’s body measurements.

Changes: Migrating to this model requires significant consolidation:

We will merge the data from user_closet and fit_feedback into user_garments and user_garment_feedback. Specifically, each entry in user_closet (especially those in production env) will become a user_garments row (with garment_status = 'owned' by default, since closet presumably meant owned items). The associated fit_feedback entries (matching by user and variant and size) will be transformed into user_garment_feedback rows linked to that user_garments entry. Freestyle’s fit_feedback.fit_result can be interpreted into an overall feedback code: e.g., if fit_result = 0 meant "too small", we create a feedback entry with dimension "overall" and code "Too Small". The fit_feedback.notes goes into the notes field of user_garments or we might create a generic “notes” dimension feedback if needed. This migration will unify historical data.

We will import Tailor3’s richer data if available. Tailor’s user_garments and user_garment_feedback records (perhaps from a testing environment) can be mapped onto the new structure. This requires mapping integer user IDs from Tailor to UUID user IDs in Supabase (likely via email or a lookup if those users exist in auth). If this is too complex, we might choose to only carry over the schema concepts and not actual data from Tailor, depending on project needs.

Create the new tables: user_garments, user_garment_feedback, feedback_codes, user_garment_photos. Pre-fill feedback_codes with the standardized values (from Tailor’s dump or the PDF’s list: Too Tight, Too Loose, Perfect Fit, etc.). Ensure that user_garments.user_id and user_garment_feedback.user_id (if included) both have foreign keys to the auth.users table for integrity.

Apply Row-Level Security (RLS) policies to these tables similar to the current ones: each user can only view or modify their own logs and feedback. For example, we’ll add a policy on user_garments like USING (user_id = auth.uid()), and similarly on user_garment_feedback and user_garment_photos. We enable RLS on these tables to enforce privacy by default.

Indexing: add an index on user_garments(user_id) to efficiently query a user’s entire closet or log history. Also index user_garments(product_id) if we need to find all users who tried a given product (useful for analytics or PROXI matching). For feedback, index user_garment_feedback.user_garment_id and possibly (dimension, feedback_code_id) if we run aggregated queries like “how many times was code X given for dimension Y”.

The old tables user_closet and fit_feedback can be retired after migration. We might keep them temporarily (or create a view mapping to new tables) to ensure any legacy code still runs until we update it.

PROXI Social Features and Scaling for Future

Current: The current fs-core is focused on logging and product data; explicit social features (such as user-to-user interactions, matching, messaging) are minimal or absent. Freestyle had a concept of finding “size twins” by comparing user_closet entries (the v_proxy_feed view in the dump indicates logic to find users with the same item in the same size). There was likely no direct friend/follow system or messaging yet. Thus, features like likes, saves (wishlist), and messages are not implemented in current schema.

Target: While these features are slated for the future, our database design should accommodate them with minimal friction. Key considerations:

User Matching (Size Twins): The PROXI phase will match users with similar sizes or overlapping wardrobe items. Our new schema actually enhances the ability to do this by providing richer data:

The user_body_measurements table will store each user’s estimated body measurements (chest, waist, etc.) as computed from their fit logs. We will implement this table (one row per user, updated whenever the system recalculates their measurements). Fields: user_id (PK/FK), and columns for each measurement (e.g. chest, waist, hips, inseam, etc., numeric), plus perhaps a confidence or last_updated. This is essentially a cached summary of SIES outputs. Tailor had a similar table planned (named body_measurements) which was unused, but we will make use of the concept. Keeping these values precomputed and indexed will allow efficient querying for similar body profiles (e.g. find users with chest within 2 inches) without recalculating on the fly for millions of users. We can index each measurement column or use more advanced indexing (like a Postgres RUM index for vector similarity, if doing multi-dimensional comparisons). Initially, even a simple btree index on each key dimension (chest, waist, etc.) enables range queries to find potential matches.

The user_garments logs can also be used for matching: e.g. find users who own the same product in the same size (like the existing proxy logic did), or more generally, count how many size labels two users share in common (to gauge how close their overall sizing is). With our unified table, such queries become easier (single table join on user_id with conditions on sizes, etc.). We might create a materialized view or use a specialized search for this if needed in the future.

Social Graph: We should plan for tables to support social connections if needed. This might include a follows table (user A follows user B), or a friends table (mutual follow). While not implemented yet, reserving a namespace for these (perhaps in a social schema or as part of public schema) is wise. These tables would be straightforward: follower_id, followee_id, status, created_at. No immediate action needed except to acknowledge the likely addition.

Likes & Saves: We anticipate features like liking a product or someone’s outfit, or saving an item to a wishlist or for later. The DB can support this via generic interaction tables. For instance:

A user_likes table: could be polymorphic (with fields to identify what is liked – e.g. a product, a user_garment entry, a photo, etc.) or we maintain separate like tables per object type. A simple approach is a single table with columns: user_id, item_type (enum: product, outfit, etc.), item_id (the target’s ID), timestamp. We won’t implement it now, but our schema doesn’t conflict with adding this.

A user_wishlist or user_saved_items table: similar structure, probably just saving products. But note, our user_garments with status 'wishlist' could double as a “wants to have” list. We might leverage garment_status for this (if a user logs an item with garment_status 'wishlist', meaning they are interested in it). Alternatively, keep a separate wishlist table for clarity. This detail can be decided when the feature is built; the current schema is flexible enough either way.

Messaging: For direct messaging between users, if needed later, we’d introduce messages threads and message entries tables. These would not impact existing tables but again should be planned in a separate schema or module.

Scaling Considerations: The target schema is designed with large scale in mind:

All primary keys are bigserial or UUID, so they can accommodate millions of records without collision or overflow. Table relationships use foreign keys to ensure integrity; we will use ON DELETE CASCADE or RESTRICT appropriately (e.g., if a user account is deleted, we might want to cascade delete their profile and all their user_garments and feedback for privacy). For products, we might restrict deletion if there are logs referencing them, to maintain historical data – or use soft deletes (an is_active flag) instead of actual deletion in some cases.

Indexing is thoroughly applied: every foreign key column should be indexed (most Postgres FK automatically get indexed if they are primary keys on the target, but indexing the FK column on the child table is also important for reverse lookups). We will index crucial queries: e.g., products on (brand_id, category_id) if we often fetch products by brand or category, product_variants on (product_id), user_garments on (user_id) and possibly a composite (user_id, garment_status) if filtering owned vs tried frequently. We will also index user_body_measurements on each measurement or consider a trigram or vector index if doing similarity search across multiple columns.

Partitioning: The design notes mention we can consider partitioning very large tables by brand or category in the future for performance. Initially, it’s unnecessary (Postgres can handle tens of millions of rows with proper indexing). But our design allows this in future without major schema changes. For example, the products table could be partitioned by brand_id if we end up with tens of millions of products across many brands – queries per brand would then be faster. Similarly, user_garments could be partitioned by user_id range or by year (if logs grow endlessly) to manage table size. These are just contingency plans; we note them but won’t implement until needed.

Supabase-specific features: Because we are on Supabase (Postgres), all the traditional features (FKs, check constraints, etc.) are available and used. We will also use Supabase Storage to handle images/videos as mentioned, keeping the database lean. For real-time updates or subscriptions (if the app needs live feed updates when someone you follow logs a fit, for example), Supabase’s real-time could be leveraged out-of-the-box once RLS policies are properly set. We ensure our schema changes stay compatible with Supabase’s auth system and any existing functions or triggers from the old schema (e.g., any custom RPC functions for adding items should be updated to use the new tables).

Identified Gaps and Suboptimal Structures

Comparing the current fs-core to the ideal schema, we found several gaps or areas to improve:

Unified Logging: The current split between user_closet and fit_feedback is not optimal. It lacks the ability to record multiple fit issues per try-on and scatters data across tables. The new unified user_garments with detailed feedback fixes this by consolidating try-on records and allowing rich feedback. We eliminate duplication (no need for separate tables for essentially the same event) and add expressiveness (multiple feedback points instead of one).

Feedback Standardization: Currently, fit feedback is likely a freeform numeric or text with no standardization. This is suboptimal for analysis. Introducing a feedback_codes reference provides consistency (e.g., one user’s "runs small" can be correlated with another’s because both use the same code rather than arbitrary text). This was missing in fs-core, but Tailor3 had it and we adopt it.

Measurement Data: The absence of a flexible measurement schema in the current db is a major gap. Using fixed columns or not having size charts at all limits the SIES capabilities. The new measurement_sets and measurements tables address this by normalizing size guide info, which was previously either not stored or stored in a less accessible form (Tailor3’s old size_guide_entries with many columns was not scalable). The new approach is more modular and can handle any measurement type.

Profile Linkage: If the current user_profile (or equivalent) isn’t tied to auth.users via FK, that’s a data integrity issue. Also, if it lacks fields like avatar or preferences, it’s incomplete. We identify this as suboptimal and plan to enforce the linkage and include fields for a fuller user profile.

Misc. Legacy Fields: The current schema (from Freestyle) has some legacy or redundant fields we can clean up. For example, the env field used in user_closet/fit_feedback to separate sandbox data – in our unified design, we can drop this and use dedicated test environments or flags if needed, but it shouldn’t be in production data. Tailor’s user_garments had deprecated fields (garment_id, size_guide_id, etc.) – we will not carry those forward at all, focusing only on the current fields. Similarly, Freestyle’s is_active flags on products or variants (if any) and lifecycle fields can be reconsidered; a simpler approach might be to just mark discontinued products or keep them for completeness but not heavily use them.

Schema Modularity: Currently, most tables might all reside in the public schema. While functional, this can get cluttered. We propose a logical grouping (which could be achieved via schemas or at least naming conventions). For instance, core catalog tables (brands, products, etc.) could remain in public or move to a catalog schema; user-generated content (user_garments, feedback, photos) could live in a user_content schema; auth remains in auth. This modular separation wasn’t present but would improve maintainability. Even if we don’t physically move schemas right now, we will conceptually separate concerns (and possibly use schema prefixes in naming for clarity, e.g. user.user_garments vs catalog.products).

Indexes/Constraints: We noticed some needed constraints that might be missing in current fs-core. For example, ensuring uniqueness of certain fields (unique brand names, unique category names per level, unique user+variant in closet which Freestyle did enforce). We will add any missing unique constraints (like no duplicate closet entries for same item, which Freestyle already had, but now it will be ensured in user_garments for (user, product or variant, size)). Also, proper foreign keys (Freestyle did link to auth.users and variant etc., which is good). We will double-check that all new tables have foreign keys where appropriate and set ON DELETE rules (e.g., if a product is deleted, perhaps cascade delete its images and variants; if a user is deleted, cascade their profile, logs, etc.). These were not fully fleshed out previously.

Media Handling: The current setup might not have had a formal solution for user-uploaded images (perhaps it wasn’t implemented yet). Relying on Supabase Storage and a linking table is the proposed best practice. We highlight this as an improvement over any ad-hoc or future approach that might have considered storing images in base64 or external links sprinkled in notes. The new media table centralizes this.

Future-Proofing Social: While likes, follows, messages aren’t in current schema, our design plans for them. We identify that as a gap – no tables for social graph or interactions – but also a future task. The plan ensures adding these will not require reworking existing tables, only adding new ones with FKs to users and possibly to content (e.g., liking a user_garment by referencing its ID). We have reserved this conceptual space so the team knows these needs.

By addressing all these gaps, the fs-core database will be in an ideal state to support current features and scale for new ones.

Step-by-Step Upgrade Tasks

To implement this evolution safely and systematically, we outline the following steps:

Schema Backup and Preparation:

Take a backup of the current fs-core database (schema and data) before making changes. This ensures we can rollback if needed.

Load the schema diagrams or dumps of Tailor3 and FreestyleDB in a dev environment for reference (if not already done) so we can copy data or compare structures during migration.

Introduce New Schema Objects:
Create the new tables and schema structure alongside the existing one, so we can migrate gradually:

Core tables: Create brands_new, products_new, product_variants_new, categories_new, subcategories_new tables (or alter existing tables if we choose to rename in place). Define all columns, data types, and constraints as per the target design (including NOT NULL where applicable, default values, etc.). For example, create products_new with the schema combining Freestyle’s style and Tailor’s product_master fields, and product_variants_new combining Freestyle’s variant and Tailor’s product_variants fields.

Measurement schema: Create measurement_sets and measurements tables. Ensure to set foreign keys (e.g., measurement_sets.brand_id → brands_new.id, measurements.set_id → measurement_sets.id). Add the unique constraints (brand+category+gender on measurement_sets if needed) and check constraints for valid values.

Logging schema: Create user_garments_new, user_garment_feedback, feedback_codes, and user_garment_photos tables. Also create the user_body_measurements table for PROXI. Define all necessary foreign keys:

user_garments_new.user_id → auth.users.id (UUID FK),

user_garments_new.product_id → products_new.id,

user_garments_new.variant_id → product_variants_new.id (allow nulls initially),

user_garment_feedback.user_garment_id → user_garments_new.id (and maybe user_id → auth.users for double security),

user_garment_feedback.feedback_code_id → feedback_codes.id,

user_garment_photos.user_garment_id → user_garments_new.id.
Set up primary keys and required indexes (we can create indexes in this step or after data load). Populate feedback_codes with the standardized entries.

Social future tables (optional at this stage): If we want to get ahead, create stub tables for user_follows, user_likes, etc. However, this can wait until those features are closer to implementation. It’s mentioned here mainly to consider schema placement (e.g., maybe decide to use a separate schema social and create it now).

Migrating Data to New Core Tables:

Brands/Categories: Migrate existing brand data into brands_new. If the current brand table lacks region or default_unit, populate with defaults (NULL or a sensible default like region 'US', unit "in"). Enforce name uniqueness by merging duplicates if any (e.g., if "Nike" existed twice with slight differences). Migrate category into categories_new and subcategories_new: e.g., all entries with no parent go to categories, those with a parent go to subcategories with the parent_id linked. If the current data wasn’t hierarchical, we might just insert them all as top-level categories for now and refine later.

Products/Variants: Migrate from current style → products_new, and variant → product_variants_new. This involves mapping columns: e.g., Freestyle’s style.id becomes products_new.id, style.brand_id → products_new.brand_id, etc. Include new fields: if we add product_code, populate it with the current SKU if available (Freestyle might have stored SKU in a separate table variant_code – we can join that to fill product_code or variant_code accordingly). Assign each variant in product_variants_new a product_id (this is the style id from old data). For any data present in old variant_size or price_history, migrate them if needed: e.g., ensure that if a variant had size options listed, we fill sizes_available or consider populating a measurements entry for it (though sizes_available might be better recalculated from measurements or external data).

Profiles: Link user profiles properly. If a user_profile table exists: alter it to add user_id UUID FK to auth.users (if not already), or if the current table’s PK is already the UUID, that works – in that case, consider renaming it to profiles and adding any missing columns (avatar, etc.). Migrate any data needed (e.g., Tailor’s user preferences if that existed).

Legacy fit data: This is a crucial step. For each user’s data:

Create a user_garments_new entry from every user_closet row. Set user_id, link to product_id/variant_id (point it to the new products_new and product_variants_new IDs, which should match the old ones if we kept the same IDs – if we didn’t preserve IDs, we need a mapping; ideally, we keep the same primary keys for continuity). Set size_label from closet.size, and set garment_status = 'owned' (assuming closet implies ownership). If env was 'sandbox' for some entries (test entries), we might choose not to migrate those or mark them differently (e.g., skip or mark as test).

For each fit_feedback row: find the corresponding new user_garments_new (by user_id + variant_id + size_label). Then create one or more user_garment_feedback entries. If fit_feedback.fit_result exists: map it to a feedback_code. For example, define: 0 = Too Small, 1 = Perfect, 2 = Too Large, etc., and use the codes accordingly. This becomes an "overall" dimension feedback. If fit_feedback.notes is non-empty, we could either append it to the user_garments.notes field (if it’s general commentary) or create a special feedback entry with dimension "notes" (though that’s not in our schema explicitly; better to put it in the notes column of user_garments to keep one place for free text). Set the timestamps (we might use fit_feedback.created_at if available for both the log and feedback entries). All these user_garment_feedback link by the new user_garment_id.

Migrate Tailor3 logs if we have them: Tailor’s user_garments had possibly test data with more detailed feedback. If merging, we have to map Tailor’s feedback_code_id to our new feedback_codes (likely same IDs if we imported Tailor’s codes). This can enrich our initial dataset. Ensure no duplicate entries for the same event; if a user exists in both systems, coordinate their data carefully (this might be rare).

Photos: If Tailor3 had a user_garment_photos table or if any image paths were stored (Tailor’s tag_photo_path field in user_garments), migrate those into the new user_garment_photos. For each user_garment with a photo path, create a record with that path as photo_url. Mark it is_primary = true (if only one). If multiple photos per item were in Tailor, create multiple entries. Store the user_id as well if we include that in the table for easier querying by user. The actual image files should be moved to Supabase storage if they aren’t already; update the URLs accordingly (e.g., Tailor might have stored local file paths – those need to become public URLs or storage paths accessible in the new app). This step ensures no user content is lost.

Apply Constraints and Indexes:
After data migration into new tables, add any constraints or indexes that were deferred:

Add primary keys and unique constraints (if not created earlier). E.g., ALTER TABLE products_new ADD PRIMARY KEY (id), unique index on brand(name, region), etc. If we preserved IDs from old tables, the PK should already be set; if we allowed new serials, ensure the sequences are set to correct values (to not conflict with migrated IDs).

Add foreign key constraints now that all referenced data is in place. For example, ensure product_variants_new.brand_id (if exists) references brands, etc. We might have postponed some FKs during migration for ease of data load; now add them and validate.

Create indexes for performance: on user_garments_new(user_id), user_garments_new(product_id), user_garment_feedback(user_id) (or ensure a composite index on feedback via user_garment -> user, as RLS may use that), on measurements(set_id), etc. Also index user_body_measurements.user_id (though that table will have one row per user, PK could be user_id itself).

Enable Row Level Security on the new tables and add policies:

For user_garments_new: ENABLE ROW LEVEL SECURITY; CREATE POLICY "user_garments_sel" ON user_garments_new USING (user_id = auth.uid()); (and similar policy for write if needed).

Similarly for user_garment_feedback and user_garment_photos: policies that ensure only the owner can select/modify their data.

For tables that are global (products, brands), we might not need RLS (those are generally public data). But for any user-specific data (logs, body_measurements), enforce RLS.
These policies mirror what existed on user_closet and fit_feedback, extended to new tables.

Data Verification and Integrity Checks:

Run queries to spot-check that the migrated data is consistent. For example, pick a few users and ensure that if they had 5 items in closet and corresponding feedback, now you see 5 entries in user_garments_new and the appropriate feedback details. Verify that no data was lost (notes carried over, sizes match, etc.).

Check that all foreign keys are satisfied (no orphan references). For instance, ensure every user_garments_new.product_id points to a valid product in products_new (if any are null because product wasn’t found, flag those to address – possibly those products need to be ingested or created as placeholder records).

If any constraints failed to add (due to bad data, e.g., duplicate brand names), resolve those by cleaning data (merge duplicates, delete invalid rows) and then add the constraints again.

Performance sanity: do EXPLAIN on a couple of typical queries (like get a user’s closet, or find matches) to see that indexes are being used. Tweak indexes if needed.

Swap to New Schema (Cutover):

Update the application code (or Supabase restful endpoints) to use the new tables. This might involve changing table names in queries or updating any stored procedures. For instance, if the app formerly queried user_closet, it should now query user_garments. If a function log_try_on(user, variant, size) existed, rewrite it to insert into user_garments and user_garment_feedback as needed.

If we kept the same table names but altered in place (renaming old and new), then ensure the renaming: e.g., drop old products table (if renamed to backup) and rename products_new to products. We could also utilize PostgreSQL’s ability to transactionally swap by renaming tables. For safety, it might be better to keep the new tables with temporary names until fully verified, then in one transaction do: rename old tables (append _old), rename new tables to official names. This minimizes downtime and confusion.

Update any Supabase Row Level Security references (policies already added on new tables should carry over on rename). Also update any foreign key references if table names changed (though renaming tables in Postgres automatically updates FKs that target them).

Run the app against the new schema in a staging environment to ensure everything works. Test user signup, logging an item, retrieving size guide info, etc., to confirm all the pieces connect properly.

Deprecate Old Structures:

Once the new schema is live and stable, drop the old tables (user_closet, fit_feedback, etc.) and any now-unused sequences or views. Also drop obsolete columns in auth or profile if any (for example, if we had a column storing something that moved to a new table). However, keep a backup export of these just in case.

Remove or archive any legacy code that referenced the old schema to avoid confusion.

Documentation and Knowledge Sharing:

Update the database schema documentation to reflect this new design (essentially, much of what is in this plan can go into the docs). Provide an ER diagram if possible for the new schema. Highlight how data flows in LOGGER, SIES, PROXI phases with the new tables. This documentation will help new team members quickly understand the structure without needing the old dumps.

Note the rationale for major changes in the docs: e.g., “why we merged closet and feedback into user_garments – for normalization and richer feedback; why measurement_sets were introduced – for flexible size charts; etc.” and cite the relevant design document sections.

Supabase Policies and Performance Follow-up:

Implement any additional Supabase-specific configurations: for example, enable Realtime on the user_garments table if the app should get live updates when a new fit is logged. Ensure RLS policies are compatible with that (likely need a similar auth.uid() check, which we have).

If any computed columns or triggers are needed (for example, a trigger to update user_body_measurements whenever a user_garment_feedback is inserted or updated), implement those. Possibly, whenever a new feedback is added, we could recalc the user’s body measurements estimate and update user_body_measurements. This could be done in app logic or via a PostgreSQL function. In Tailor, this was done externally, but we can automate some of it now or later.

Monitor performance as data grows. The design should handle it, but if we notice slow queries on certain operations (e.g., searching for size twins), we can consider adding indexes or even building a specialized matching index using Postgres extensions (like pg_trgm for text similarity on size strings or a vector approach for body measurements). We note that pg_trgm is available (Tailor3 enabled it for perhaps fuzzier searches), so we have tools ready if needed.

Future Feature Stubs:

As a final step, lay the groundwork for upcoming social features. For instance, if we know “likes” or “follows” are next, we might create empty tables now to avoid another round of migrations later. Adding them now with simple schema (and perhaps basic RLS like user can only like as themselves, etc.) could be wise. If we decide to wait, we at least ensure that nothing in the current schema design would conflict with adding those later. (Our current design is decoupled, so adding new tables for likes or messages will be straightforward.)

One example: creating a user_followers table with user_id and follower_id FKs to auth.users, so we can start recording follows once that feature is live. This doesn’t affect anything else but shows foresight. Similarly, a user_messages and user_message_threads table can be outlined for when messaging is tackled.

By following these steps, we gradually transition the fs-core database from its current state to the target state with minimal downtime and data integrity preserved. Each step should be tested and verified before moving to the next, especially the data migration. Once complete, the new fs-core will encapsulate the combined wisdom of the Tailor3 and Freestyle schemas, matching the proposed architecture and positioning the platform for robust growth and new features. All changes are made with scalability, consistency, and maintainability in mind, ensuring this foundation will serve the app and team well for the long term.

References Used (from design proposal and legacy schemas for justification):

Unified schema supports LOGGER, SIES, PROXI phases with strong relational design.

Use of Supabase Auth (UUIDs) and one-to-one profiles for millions of users.

Brands, unique by name+region, with optional JSON profiles for sizing quirks.

Category hierarchy and brand-specific category mapping for consistency.

Product & variant split for normalization (Tailor3’s improvement over single garments table).

Product images in a separate table, multiple per variant, with primary flags.

Performance: indexing keys, considering partitioning at extreme scale.

Flexible measurement_sets and measurements tables for size guides.

Combining Freestyle’s closet/feedback with Tailor’s user_garments and codes for comprehensive fit logging.

Standardized feedback codes (e.g. "Too Tight", "Too Loose") for consistency.

Storing only references to images/videos and using Supabase Storage (not DB blobs) for scalability.

Using user_body_measurements table to cache inferred body sizes for fast size-twin matching.

Supabase considerations: leveraging row-level security policies and real-time features for future social interactions.