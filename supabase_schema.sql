-- ĐÃ ÁP DỤNG sẵn lên project Supabase (udgecmcsjyokmanyyfqf). File này để lưu vết / khôi phục.
create schema if not exists suggest;

create table if not exists suggest.keyword_master (
  id bigint generated always as identity primary key,
  industry text not null,
  keyword text not null,
  nhom text,
  ghichu text,
  created_at timestamptz default now(),
  unique (industry, keyword)
);

create table if not exists suggest.suggest_raw (
  id bigint generated always as identity primary key,
  industry text not null,
  ngay date not null,
  keyword_goc text,
  nhom text,
  goi_y text not null,
  rank int,
  intent text,
  fetched_at timestamptz default now()
);
create index if not exists idx_raw_industry_ngay on suggest.suggest_raw (industry, ngay);
create index if not exists idx_raw_industry_goiy on suggest.suggest_raw (industry, goi_y);
create index if not exists idx_raw_industry_intent on suggest.suggest_raw (industry, intent);
create index if not exists idx_km_industry on suggest.keyword_master (industry);
create unique index if not exists uq_raw_day on suggest.suggest_raw (industry, ngay, keyword_goc, goi_y);

-- HÀM (đầy đủ định nghĩa xem trong lịch sử migration Supabase):
--   suggest.get_bundle(text)             -> jsonb  (tổng hợp toàn bộ bundle)
--   suggest.get_keywords(text)           -> jsonb  (danh sách keyword)
--   public.suggest_get_bundle(text)      -> wrapper RPC (frontend đọc, grant anon)
--   public.suggest_get_keywords(text)    -> wrapper RPC (frontend đọc, grant anon)
--   public.suggest_upsert_keywords(text, jsonb) -> int  (collector ghi, grant service_role)
--   public.suggest_insert_raw(text, date, jsonb) -> int (collector ghi, grant service_role)
--   public.suggest_prune(int)            -> int  (xoá dữ liệu cũ > N ngày)
