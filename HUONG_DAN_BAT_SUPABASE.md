# Bật Supabase cho web (Vercel)

Khi muốn web đọc dữ liệu từ **Supabase** thay vì Apps Script/Google Sheet.

## Thứ tự nên làm
1. **Chạy collector trước** (xem `README.md`) để Supabase có dữ liệu — nếu không, dashboard sẽ trống.
2. Sau khi Supabase đã có dữ liệu → bật env trên Vercel bên dưới → Redeploy.

## Biến môi trường trên Vercel
Vercel → project `suggest-dashboard-v3` → **Settings → Environment Variables**, thêm/sửa:

| Key | Value |
|---|---|
| `DATA_PROVIDER` | `supabase` |
| `SUPABASE_URL` | `https://udgecmcsjyokmanyyfqf.supabase.co` |
| `SUPABASE_ANON_KEY` | (anon key — xem bên dưới, dùng để **đọc**, an toàn) |

> **anon key** (đọc-only, công khai được, đã grant cho các hàm đọc):
> ```
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkZ2VjbWNzanlva21hbnl5ZnFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1NzI5ODAsImV4cCI6MjA4ODE0ODk4MH0.SqgL54LRglaSZbTDi7GM2awsOgEFuD95AtShMSHNhC4
> ```
> Đây là khoá ẩn danh chỉ gọi được hàm đọc (`suggest_get_bundle`, `suggest_get_keywords`).
> Khoá **service_role** (ghi) KHÔNG đặt ở Vercel — chỉ đặt ở GitHub Secrets cho collector.

Sau đó **Redeploy** (`vercel --prod` hoặc Deployments → Redeploy).

## Cơ chế chuyển nguồn
- Khi `DATA_PROVIDER=supabase` + có `SUPABASE_URL` → **cả 4 ngành** đọc từ Supabase.
- Khi để trống / `DATA_PROVIDER` khác → quay lại Apps Script (nếu có env) hoặc mock.
- Frontend KHÔNG phải sửa gì — chỉ đổi biến môi trường. Có thể bật/tắt bất cứ lúc nào.

## Quay lại Apps Script (nếu cần)
Xoá hoặc đổi `DATA_PROVIDER` khác `supabase` → Redeploy. App tự dùng lại nguồn cũ.
