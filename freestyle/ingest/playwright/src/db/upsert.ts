import { q } from './pg';

export async function upsertBrand(brandName: string): Promise<number> {
  const rows = await q<{ id: number }>(
    `insert into public.brand(name) values ($1)
     on conflict(name) do update set name=excluded.name
     returning id`,
    [brandName.trim()]
  );
  return rows[0].id;
}

export async function ensureCategory(catName: string): Promise<number> {
  const rows = await q<{ id: number }>(
    `insert into public.category(name) values ($1)
     on conflict(name) do update set name=excluded.name
     returning id`,
    [catName.trim()]
  );
  return rows[0].id;
}

export type StyleInput = {
  brand_id: number;
  category_id: number;
  name: string;
  gender?: string | null;
  description?: string | null;
};

export async function upsertStyle(s: StyleInput): Promise<number> {
  const rows = await q<{ id: number }>(
    `insert into public.style(brand_id, category_id, name, gender, description, is_active)
     values ($1,$2,$3,$4,$5,true)
     on conflict (brand_id, category_id, name)
     do update set description = coalesce(excluded.description, public.style.description),
                   is_active = true
     returning id`,
    [s.brand_id, s.category_id, s.name.trim(), s.gender ?? null, s.description ?? null]
  );
  return rows[0].id;
}

export type VariantInput = {
  style_id: number;
  color?: string | null;
  size_scale?: string | null;
};

export async function upsertVariant(v: VariantInput): Promise<number> {
  const rows = await q<{ id: number }>(
    `insert into public.variant(style_id, is_active)
     values ($1, true)
     on conflict (style_id) do update set is_active = true
     returning id`,
    [v.style_id]
  );
  return rows[0].id;
}

export async function upsertProductUrl(variantId: number, url: string) {
  await q(
    `insert into public.product_url(variant_id, url, is_current)
     values ($1,$2,true)
     on conflict (url) do update set variant_id = excluded.variant_id, is_current = true`,
    [variantId, url]
  ).catch(() => {
    /* schema differences allowed */
  });
}

export async function insertPrice(variantId: number, listPrice: number, currency = 'USD') {
  await q(
    `insert into public.price_history(variant_id, list_price, currency)
     values ($1,$2,$3)`,
    [variantId, listPrice, currency]
  ).catch(() => {
    /* optional table */
  });
}

export async function insertImageRow(
  variantId: number,
  styleId: number,
  url: string,
  position: number,
  storagePath?: string,
  isPrimary = false,
  w?: number,
  h?: number
) {
  await q(
    `insert into public.product_images(variant_id, style_id, original_url, position, storage_path, is_primary, width, height)
     values ($1,$2,$3,$4,$5,$6,$7,$8)
     on conflict (variant_id, original_url) do nothing`,
    [variantId, styleId, url, position, storagePath ?? null, isPrimary, w ?? null, h ?? null]
  );
}


