import type { SupabaseClient } from '@supabase/supabase-js';
import { APP_MODE, API_BASE } from './config';
import { supabase as defaultSupabase } from './supabase';

export type ProductResult = {
  brand: string;
  style_name: string;
  style_code: string | null;
  fit: string | null;
  color: string | null;
  variant_code: string | null;
  product_url: string;
  image_url?: string | null;
};

const IMAGE_VIEW = 'v_product_variants_img';
const FALLBACK_VIEW = 'v_product_variants';

export function normalizeUrl(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed) return '';
  const withProtocol = /^[a-zA-Z][a-zA-Z\d+.-]*:/.test(trimmed) ? trimmed : `https://${trimmed}`;
  try {
    const url = new URL(withProtocol);
    url.hostname = url.hostname.toLowerCase();

    const removable = new Set(['fbclid', 'gclid', 'ref']);
    const params = url.searchParams;
    Array.from(params.keys()).forEach((key) => {
      const lower = key.toLowerCase();
      if (lower.startsWith('utm') || removable.has(lower)) {
        params.delete(key);
      }
    });
    url.search = params.toString() ? `?${params.toString()}` : '';
    url.hash = '';

    if (url.pathname !== '/') {
      url.pathname = url.pathname.replace(/\/+/g, '/');
      if (url.pathname.endsWith('/')) {
        url.pathname = url.pathname.replace(/\/+$/, '');
        if (!url.pathname) url.pathname = '/';
      }
    }

    return url.toString();
  } catch {
    return trimmed;
  }
}

export async function fetchProductByUrl(
  client: SupabaseClient = defaultSupabase,
  url: string,
): Promise<ProductResult[]> {
  const normalized = normalizeUrl(url);
  if (!normalized) return [];

  // Prefer RPC for tolerant server-side lookup (exact → prefix → style-code)
  try {
    const rpc = await client.rpc('product_lookup', { input_url: normalized });
    if (!rpc.error && Array.isArray(rpc.data) && rpc.data.length) {
      return rpc.data.map((row: any) => ({
        brand: row.brand ?? '',
        style_name: row.style_name ?? '',
        style_code: row.style_code ?? null,
        fit: row.fit ?? null,
        color: row.color ?? null,
        variant_code: row.variant_code ?? null,
        product_url: row.product_url ?? normalized,
        image_url: row.image_url ?? null,
      }));
    }
  } catch {
    // Fall through to the existing view-based strategy
  }

  if (APP_MODE === 'render' && API_BASE) {
    try {
      const remote = new URL('/product/lookup', API_BASE);
      remote.searchParams.set('url', normalized);
      const response = await fetch(remote.toString(), { method: 'GET' });
      if (response.ok) {
        const payload = await response.json();
        if (Array.isArray(payload) && payload.length) {
          return payload.map(mapRenderProduct);
        }
        if (payload && !Array.isArray(payload) && payload.brand) {
          return [mapRenderProduct(payload)];
        }
      }
    } catch {
      // Ignore network/API errors and fall back to Supabase lookup
    }
  }

  const trailing = getTrailingPath(normalized);

  const withImages = await selectFromView(client, IMAGE_VIEW, normalized, trailing, true);
  if (withImages !== null) {
    return withImages;
  }

  const fallback = await selectFromView(client, FALLBACK_VIEW, normalized, trailing, false);
  if (fallback && fallback.length) {
    return fallback;
  }

  // Final safety net: use cache when variants don't exist yet
  const cache = await selectFromCache(client, normalized, trailing);
  return cache;
}

async function selectFromView(
  client: SupabaseClient,
  view: string,
  normalized: string,
  trailing: string | null,
  includeImage: boolean,
): Promise<ProductResult[] | null> {
  const columns = includeImage
    ? 'brand, style_name, style_code, fit, color, variant_code, product_url, image_url'
    : 'brand, style_name, style_code, fit, color, variant_code, product_url';

  const exact = await client.from(view).select(columns).eq('product_url', normalized);
  if (exact.error) {
    if (exact.error.code === '42P01') {
      return null;
    }
    throw new Error(exact.error.message);
  }

  let rows = exact.data ?? [];

  if (!rows.length && trailing) {
    const fuzzy = await client
      .from(view)
      .select(columns)
      .ilike('product_url', `%${escapeForILike(trailing)}`);
    if (fuzzy.error) {
      throw new Error(fuzzy.error.message);
    }
    rows = fuzzy.data ?? [];
  }

  return rows.map((row) => mapRow(row, normalized, includeImage));
}

function mapRow(row: Record<string, any>, normalized: string, includeImage: boolean): ProductResult {
  return {
    brand: row.brand ?? '',
    style_name: row.style_name ?? '',
    style_code: row.style_code ?? null,
    fit: row.fit ?? null,
    color: row.color ?? null,
    variant_code: row.variant_code ?? null,
    product_url: row.product_url ?? normalized,
    image_url: includeImage ? row.image_url ?? null : row.image_url ?? null,
  };
}

function mapRenderProduct(record: Record<string, any>): ProductResult {
  return {
    brand: record.brand ?? record.brand_name ?? '',
    style_name: record.style_name ?? record.name ?? '',
    style_code: record.style_code ?? record.sku ?? null,
    fit: record.fit ?? null,
    color: record.color ?? null,
    variant_code: record.variant_code ?? record.variant ?? null,
    product_url: record.product_url ?? record.url ?? '',
    image_url: record.image_url ?? record.image ?? null,
  };
}

function getTrailingPath(input: string): string | null {
  try {
    const url = new URL(input);
    const pathname =
      url.pathname.endsWith('/') && url.pathname !== '/' ? url.pathname.replace(/\/+$/, '') : url.pathname;
    const pathOnly = pathname === '/' ? '' : pathname;
    const search = url.search;
    const trailing = `${pathOnly}${search}`.replace(/^\/+/, '');
    return trailing || null;
  } catch {
    return null;
  }
}

function escapeForILike(value: string): string {
  return value.replace(/[\\%_]/g, (char) => `\\${char}`);
}

async function selectFromCache(
  client: SupabaseClient,
  normalized: string,
  trailing: string | null,
): Promise<ProductResult[]> {
  // 1) Exact in cache
  const exact = await client
    .from('jcrew_product_cache')
    .select('product_url, product_image, product_code')
    .eq('product_url', normalized)
    .limit(1);
  if (exact.error) return [];
  let row = exact.data?.[0] as { product_url: string; product_image: string | null; product_code: string | null } | undefined;

  // 2) Prefix in cache (by URL)
  if (!row && trailing) {
    const pref = await client
      .from('jcrew_product_cache')
      .select('product_url, product_image, product_code')
      .ilike('product_url', `%${escapeForILike(trailing)}`)
      .limit(1);
    if (pref.error) return [];
    row = pref.data?.[0];
  }

  if (!row) return [];

  // 3) Get product_master for base name and brand
  const code = row.product_code ?? null;
  let styleName = '';
  let brandName = '';
  if (code) {
    const pm = await client
      .from('product_master')
      .select('base_name, brand_id')
      .eq('product_code', code)
      .limit(1);
    if (!pm.error && pm.data && pm.data[0]) {
      styleName = (pm.data[0] as any).base_name ?? '';
      const brandId = (pm.data[0] as any).brand_id as number | null;
      if (brandId != null) {
        const b = await client.from('brands').select('name').eq('id', brandId).limit(1);
        if (!b.error && b.data && b.data[0]) {
          brandName = (b.data[0] as any).name ?? '';
        }
      }
    }
  }

  return [
    {
      brand: brandName,
      style_name: styleName,
      style_code: code,
      fit: null,
      color: null,
      variant_code: null,
      product_url: row.product_url ?? normalized,
      image_url: row.product_image ?? null,
    },
  ];
}
