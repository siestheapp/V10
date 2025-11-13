# Supabase Changes

## Product Lookup Acceleration (views + indexes + RPC)
- Added pg_trgm and indexes on product URLs and product codes
- Created views `public.v_product_variants` and `public.v_product_variants_img` with cache fallback
- Created RPC `public.product_lookup(text)` for tolerant lookup (exact → prefix → style-code)
- Granted anon access to views and RPC

Applies cleanly to the `tailor3` project.
