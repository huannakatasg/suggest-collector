# Suggest Collector — GitHub Actions → Supabase

Bộ thu thập Google Suggest chạy **miễn phí trên GitHub Actions** (không còn giới hạn 6 phút của
Apps Script), ghi thẳng vào **Supabase (PostgreSQL)**. Hỗ trợ ~2.000–2.800 seed/ngành cho các
ngành (cơm / BĐS / khách sạn / nước uống văn phòng) — mỗi ngày bung ra hàng chục nghìn gợi ý thật.

## File trong thư mục này
- `seeds.py` — ma trận hoán vị seed cho 4 ngành (food / realestate / hotel / water).
- `classify.py` — phân loại intent + lọc negative (port từ Apps Script).
- `collector.py` — cào Suggest từng seed → ghi Supabase qua RPC.
- `.github/workflows/collect.yml` — lịch chạy 2 cữ/ngày (7:30 & 13:30 VN) + chạy tay.
- `supabase_schema.sql` — toàn bộ DDL đã áp lên Supabase (để tham khảo/khôi phục).

> Lưu ý: các bảng & hàm Supabase **đã được tạo sẵn** trên project của bạn. File schema chỉ để lưu vết.

## Cài đặt (1 lần, ~10 phút)

### 1. Tạo GitHub repo
- Vào github.com → **New repository** → đặt tên (vd `suggest-collector`).
- **Nên để Public** → GitHub Actions miễn phí không giới hạn phút. (Private chỉ 2.000 phút/tháng.)

### 2. Đưa các file lên repo
Cách dễ nhất: trên trang repo bấm **Add file → Upload files**, kéo thả toàn bộ nội dung thư mục
`_collector` (gồm cả thư mục ẩn `.github/`). Hoặc dùng git:
```
git init && git add . && git commit -m "collector"
git branch -M main
git remote add origin https://github.com/<bạn>/suggest-collector.git
git push -u origin main
```

### 3. Khai báo 2 Secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**, thêm:

| Name | Value |
|---|---|
| `SUPABASE_URL` | `https://udgecmcsjyokmanyyfqf.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Lấy ở Supabase → Project Settings → **API** → mục **service_role** (secret). KHÔNG để lộ. |

### 4. Chạy lần đầu (nạp dữ liệu ngay)
Repo → tab **Actions** → workflow **Suggest Collector** → **Run workflow**.
Lần đầu chạy ~60–120 phút (cào toàn bộ 4 ngành). Xem log để theo dõi.
Có thể chạy riêng ngành nước bằng **Run workflow** với input `industries=water`.

Từ đó, workflow tự chạy **7:30 và 13:30 giờ VN mỗi ngày**.

## An toàn
- Delay 0.6s/request, User-Agent chuẩn → endpoint Suggest ẩn danh, không rủi ro tài khoản.
- Hàm `suggest_prune` tự xoá dữ liệu > 90 ngày để giữ DB gọn trong free tier Supabase.
- Ghi dùng `on conflict do nothing` → chạy lại nhiều lần trong ngày không nhân đôi dữ liệu.

## Mở rộng thêm từ khóa
Sửa `seeds.py` (thêm loại hình / quận / modifier) → push lại. Không cần đụng phần khác.
