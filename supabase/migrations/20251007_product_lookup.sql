-- Migration: Product lookup acceleration and views (captured)

-- Extensions
create extension if not exists pg_trgm;

-- Indexes
create index if not exists idx_pv_variant_url on public.product_variants (variant_url);
create index if not exists idx_pv_variant_url_trgm on public.product_variants using gin (variant_url gin_trgm_ops);
create index if not exists idx_pm_product_code on public.product_master (product_code);
create index if not exists idx_jcrew_product_url on public.jcrew_product_cache (product_url);

-- Views with cache fallback
-- Drop in case they exist
DROP VIEW IF EXISTS public.v_product_variants_img CASCADE;
DROP VIEW IF EXISTS public.v_product_variants CASCADE;

CREATE VIEW public.v_product_variants AS
select b.name as brand, pm.base_name as style_name, pm.product_code as style_code,
       pv.fit_option as fit, pv.color_name as color, pv.variant_code as variant_code,
       coalesce(pv.variant_url, jc.product_url) as product_url
from public.product_variants pv
join public.product_master pm on pv.product_master_id = pm.id
left join public.brands b on pm.brand_id = b.id
left join public.jcrew_product_cache jc on jc.product_code = pm.product_code
union all
select b.name, pm.base_name, pm.product_code,
       NULL::varchar(50), NULL::varchar(100), NULL::varchar(50),
       jc.product_url
from public.product_master pm
left join public.product_variants pv on pv.product_master_id = pm.id
join public.brands b on pm.brand_id = b.id
join public.jcrew_product_cache jc on jc.product_code = pm.product_code
where pv.id is null;

CREATE VIEW public.v_product_variants_img AS
select b.name as brand, pm.base_name as style_name, pm.product_code as style_code,
       pv.fit_option as fit, pv.color_name as color, pv.variant_code as variant_code,
       coalesce(pv.variant_url, jc.product_url) as product_url,
       coalesce(
         case
           when jsonb_typeof(pv.images) = 'array' then (pv.images->0->>'url')
           when jsonb_typeof(pv.images) = 'object' and pv.images ? 'primary' then pv.images->>'primary'
           else NULL
         end,
         jc.product_image
       ) as image_url
from public.product_variants pv
join public.product_master pm on pv.product_master_id = pm.id
left join public.brands b on pm.brand_id = b.id
left join public.jcrew_product_cache jc on jc.product_code = pm.product_code
union all
select b.name, pm.base_name, pm.product_code,
       NULL::varchar(50), NULL::varchar(100), NULL::varchar(50),
       jc.product_url, jc.product_image
from public.product_master pm
left join public.product_variants pv on pv.product_master_id = pm.id
join public.brands b on pm.brand_id = b.id
join public.jcrew_product_cache jc on jc.product_code = pm.product_code
where pv.id is null;

-- RPC definition (tolerant lookup)
create or replace function public.product_lookup(input_url text)
returns table(
  brand text, style_name text, style_code text,
  fit text, color text, variant_code text,
  product_url text, image_url text
)
language sql stable
as $$
with cleaned as (
  select regexp_replace(input_url, '\\?.*$', '') as base_no_query
),
code as (
  select base_no_query,
         upper(coalesce((regexp_match(base_no_query, '/([A-Za-z0-9]{4,8})(?:\\\\W|$)'))[1], '')) as style_code_guess
  from cleaned
),
exact as (
  select v.brand, v.style_name, v.style_code, v.fit, v.color, v.variant_code, v.product_url, v.image_url
  from public.v_product_variants_img v
  join code t on v.product_url = t.base_no_query
),
prefix as (
  select v.brand, v.style_name, v.style_code, v.fit, v.color, v.variant_code, v.product_url, v.image_url
  from public.v_product_variants_img v
  join code t on v.product_url ilike t.base_no_query || '%'
),
stylecode as (
  select v.brand, v.style_name, v.style_code, v.fit, v.color, v.variant_code, v.product_url, v.image_url
  from public.v_product_variants_img v
  join code t on v.style_code = nullif(t.style_code_guess, '')
)
select * from exact
union all
select * from prefix
union all
select * from stylecode
limit 50;
$$;

-- Grants
GRANT SELECT ON public.v_product_variants      TO anon;
GRANT SELECT ON public.v_product_variants_img  TO anon;
GRANT EXECUTE ON FUNCTION public.product_lookup(text) TO anon;
