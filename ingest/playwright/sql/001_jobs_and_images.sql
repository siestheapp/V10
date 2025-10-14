-- Job orchestration
create table if not exists ingestion_job (
  id bigserial primary key,
  brand text not null,
  category_url text not null,
  status text not null default 'queued', -- queued|running|done|error
  totals jsonb,
  created_at timestamptz default now(),
  started_at timestamptz,
  finished_at timestamptz,
  notes text
);

create table if not exists ingestion_task (
  id bigserial primary key,
  job_id bigint not null references ingestion_job(id) on delete cascade,
  pdp_url text not null,
  status text not null default 'queued', -- queued|running|done|error
  last_error text,
  retries int not null default 0,
  created_at timestamptz default now(),
  started_at timestamptz,
  finished_at timestamptz
);
create unique index if not exists idx_ingestion_task_job_pdp on ingestion_task(job_id, pdp_url);

-- Minimal image table (if not present in your DB)
create table if not exists product_images (
  id bigserial primary key,
  style_id bigint references product_master(id) on delete cascade,
  variant_id bigint references product_variants(id) on delete cascade,
  position int not null default 0,
  original_url text not null,
  storage_path text,
  width int,
  height int,
  is_primary boolean not null default false,
  created_at timestamptz default now()
);
create unique index if not exists idx_images_variant_url on product_images(variant_id, original_url);


