# -*- coding: utf-8 -*-
"""Kiểm thử ngành RTC — thực phẩm sơ chế / Ready-to-Cook (key `rtc`).

NGUỒN CHUỖI KIỂM — ba loại, ghi rõ để không tự lừa mình:
  [THẬT]  gợi ý Google Suggest THẬT, lấy nguyên văn từ kho `suggest.suggest_weekly` của TGD
          (truy vấn 22/09/2026: gợi ý có chữ meal prep / eat clean / sơ chế / cắt sẵn / ướp sẵn /
          đông lạnh / cấp đông / hút chân không / gạo lứt / bao nhiêu calo / bảo quản). Đây là
          các ca NGOÀI MẪU — chúng do ngành produce/vegetarian/food cào về, không phải seed RTC.
  [SEED]  chuỗi sinh bởi seeds_rtc() — ca trong mẫu, chỉ dùng để khóa thứ tự nhánh.
  [ĐẶT]   chuỗi tự đặt vì chưa có gợi ý thật (Brand, vài nhóm nhiễu).

LÝ DO TÁCH BA LOẠI: bài học classifier trái cây 17/09/2026 — khớp 96% TRONG mẫu nhưng sai 25%
NGOÀI mẫu. Bốn lỗi thật của classify_rtc đều do ca [THẬT] bắt được, không ca [SEED] nào bắt:
  1. Suggest trả "bách hoá xanh", mẫu Retailer viết "bách hóa xanh" → trượt sang RTC
  2. "khoai tây cắt sẵn bị đen có ăn được không" → RTC, đúng ra là Storage
  3. "khoai tây cắt sẵn bỏ tủ lạnh được không" → RTC, đúng ra là Storage
  4. "morning fruit … trái cây cắt sẵn" (tên quán trên Maps) → RTC, đúng ra phải loại

Chạy: cd _collector && python -m unittest discover -s tests -v
"""
import os
import re
import unittest

import classify
import seeds

LABELS = {"Brand", "Retailer", "Storage", "Recipe", "MealPrep", "B2B", "RTC",
          "Pricing", "Buy", "Delivery", "Local", "Dish", "Core", "Other"}

# (chuỗi, nhãn kỳ vọng) — ưu tiên ca ở ĐƯỜNG BIÊN giữa hai nhánh để khóa thứ tự nhánh.
LABEL_CASES = [
    # ── Retailer: tên chuỗi thắng mọi ý định khác. [THẬT] khóa lỗi đặt dấu "hoá" vs "hóa".
    ("khoai tây cắt sẵn bách hoá xanh", "Retailer"),          # [THẬT]
    ("thực phẩm sơ chế bách hóa xanh", "Retailer"),           # [SEED]
    ("thịt ướp sẵn winmart", "Retailer"),                     # [SEED]
    ("thực phẩm sơ chế co.opmart", "Retailer"),               # [SEED]

    # ── Storage: bắt TRƯỚC RTC. Câu hỏi hàng hỏng chỉ có marker sơ chế, dễ bị RTC nuốt.
    ("khoai tây cắt sẵn bị đen có ăn được không", "Storage"),  # [THẬT]
    ("khoai tây cắt sẵn bỏ tủ lạnh được không", "Storage"),    # [THẬT]
    ("khoai tây cắt sẵn để tủ lạnh được bao lâu", "Storage"),  # [THẬT]
    ("cà chua cắt sẵn để tủ lạnh được bao lâu", "Storage"),    # [THẬT]
    ("cà rốt cắt sẵn để được bao lâu", "Storage"),             # [THẬT]
    ("bí đỏ cắt sẵn để được bao lâu", "Storage"),              # [THẬT]
    ("dưa leo cắt sẵn để được bao lâu", "Storage"),            # [THẬT]
    ("cách bảo quản khoai tây cắt sẵn", "Storage"),            # [THẬT] — "cách" mà KHÔNG phải Recipe
    ("cách bảo quản rau củ cắt sẵn", "Storage"),               # [THẬT]
    ("thịt ướp sẵn để được bao lâu", "Storage"),               # [SEED]
    ("thực phẩm sơ chế sẵn có tốt không", "Storage"),          # [SEED]

    # ── Recipe: tín hiệu R&D, bắt trước RTC. "cách làm" thắng, nhưng "cách bảo quản" thì không.
    ("cách làm bánh bao chay gạo lứt", "Recipe"),              # [THẬT] — thắng cả gạo lứt (MealPrep)
    ("cách làm gà kho gừng", "Recipe"),                        # [SEED]
    ("cách làm thịt kho tiêu", "Recipe"),                      # [SEED]

    # ── MealPrep: tuyến Mia Meal Prep. Bắt trước Pricing vì "bao nhiêu calo" có "bao nhiêu".
    ("nấm kho tiêu bao nhiêu calo", "MealPrep"),               # [THẬT]
    ("đậu hũ nhồi thịt bao nhiêu calo", "MealPrep"),           # [THẬT]
    ("1 phần cơm văn phòng bao nhiêu calo", "MealPrep"),       # [THẬT]
    ("cơm eat clean thủ đức", "MealPrep"),                     # [THẬT] — thắng cả Local
    ("cơm eat clean gần đây", "MealPrep"),                     # [THẬT]
    ("daily meal prep for weight loss", "MealPrep"),           # [THẬT]
    ("healthy meal prep delivery near me", "MealPrep"),        # [THẬT] — thắng cả Delivery
    ("chả trứng hấp bao nhiêu calo", "MealPrep"),              # [SEED]

    # ── B2B: tệp tổ chức, bắt trước Buy/Pricing/RTC.
    ("khoai tây đông lạnh giá sỉ tphcm", "B2B"),               # [THẬT] — thắng RTC, Pricing, Local
    ("khoai tây chiên đông lạnh giá sỉ", "B2B"),               # [THẬT]
    ("cung cấp thực phẩm sơ chế cho bếp ăn", "B2B"),           # [SEED]
    ("thực phẩm sơ chế xuất hóa đơn", "B2B"),                  # [SEED]

    # ── RTC: lõi ngành — món/nguyên liệu ở trạng thái sơ chế, không kèm ý định nào khác.
    ("khoai tây cắt sẵn đông lạnh", "RTC"),                    # [THẬT]
    ("khoai tây cắt sẵn để chiên", "RTC"),                     # [THẬT]
    ("bịch rau củ cắt sẵn", "RTC"),                            # [THẬT]
    ("gói rau củ cắt sẵn", "RTC"),                             # [THẬT]
    ("hành tây cắt sẵn", "RTC"),                               # [THẬT]
    ("khổ qua cắt sẵn", "RTC"),                                # [THẬT]
    ("đồ chay hút chân không", "RTC"),                         # [THẬT]
    ("đồ chay cấp đông", "RTC"),                               # [THẬT]
    ("gà kho gừng ướp sẵn", "RTC"),                            # [SEED] — món + trạng thái
    ("thịt heo bóc vỏ", "RTC"),                                # [SEED] — khóa lỗi quên "bóc vỏ"
    ("cá phi lê chia phần", "RTC"),                            # [SEED]

    # ── Pricing: sau MealPrep, B2B và RTC. Chỉ thắng khi KHÔNG có marker trạng thái sơ chế —
    #    cùng chủ đích với ngành produce (Processing đặt trước Pricing): trạng thái sơ chế là
    #    thông tin đắt hơn giá, vì nó nói món đó bán được ở dạng nào.
    ("thịt kho tiêu giá bao nhiêu", "Pricing"),                # [SEED] — tên món trần + giá
    ("gà kho gừng giá bao nhiêu", "Pricing"),                  # [SEED]
    ("thực phẩm sơ chế sẵn giá", "RTC"),                       # [SEED] — "sơ chế" thắng "giá"

    # ── Buy: sau Retailer.
    ("gà kho gừng mua ở đâu", "Buy"),                          # [SEED]

    # ── Local: TOP món nổi tại TP.HCM. Sau RTC nên chỉ tên món trần mới vào đây.
    ("gà kho gừng tphcm", "Local"),                            # [SEED]
    ("trứng chiên thịt bằm tphcm", "Local"),                   # [SEED]

    # ── Dish: tên món TRẦN — nuôi TOP 20 món nhu cầu cao / tăng nhanh. Nhánh CUỐI.
    ("gà kho gừng", "Dish"),                                   # [SEED] = DKC-RTC-001
    ("thịt kho tiêu", "Dish"),                                 # [SEED] = DKC-RTC-005
    ("chả trứng hấp", "Dish"),                                 # [SEED] = DKC-RTC-011
    ("bò xào sa tế", "Dish"),                                  # [SEED] = DKC-RTC-007
    ("bún thịt nướng", "Dish"),                                # [SEED] = DKC-RTC-009
    ("khổ qua nhồi thịt", "Dish"),                             # [SEED] — "nhồi" không có động từ nhiệt
    ("bò cuộn mỡ chài", "Dish"),                               # [SEED] — "cuộn"
    ("thịt lợn quay", "Dish"),                                 # [SEED] — "quay"
    ("bún bò huế", "Dish"),                                    # [SEED] — nền món, không có cách nấu

    # ── Brand
    ("thực phẩm sơ chế đồng khởi", "Brand"),                   # [ĐẶT]
    ("đồng khởi catering thịt ướp sẵn", "Brand"),              # [ĐẶT]
]

# Phải bị LOẠI trước khi tới classifier (collector gọi NEGATIVE trước CLASSIFIERS).
NOISE_CASES = [
    # Mảng trái cây có radar riêng (ngành `fruit`) — không đo lại để khỏi đếm hai lần
    ("hộp trái cây cắt sẵn đẹp", "trái cây có radar riêng"),                        # [THẬT]
    ("cửa hàng trái cây cắt sẵn", "trái cây có radar riêng"),                       # [THẬT]
    ("cung cấp trái cây đông lạnh", "trái cây có radar riêng"),                     # [THẬT]
    ("nhà cung cấp trái cây đông lạnh", "trái cây có radar riêng"),                 # [THẬT]
    ("ảnh hộp trái cây cắt sẵn", "trái cây có radar riêng"),                        # [THẬT]
    ("morning fruit nguyễn thái học - trái cây nhập khẩu giỏ trái cây & trái cây cắt sẵn",
     "tên quán trên Maps, mảng trái cây"),                                          # [THẬT]
    # Thiết bị thương mại — người mua MÁY, không mua món
    ("báo giá kho lạnh bảo quản nông sản", "thiết bị thương mại"),                  # [THẬT]
    ("máy sơ chế rau củ công nghiệp", "thiết bị"),                                  # [ĐẶT]
    ("máy hút chân không thực phẩm", "thiết bị"),                                   # [ĐẶT]
    # Sơ chế của ngành khác — đúng chữ, sai hoàn toàn thị trường
    ("sơ chế cà phê ướt", "sơ chế ngành khác"),                                     # [ĐẶT]
    ("quy trình sơ chế dược liệu", "sơ chế ngành khác"),                            # [ĐẶT]
    ("sơ chế hạt điều", "sơ chế ngành khác"),                                       # [ĐẶT]
    # Thức ăn vật nuôi / chăn nuôi / trồng trọt / việc làm / học thuật
    ("thức ăn cho mèo pate", "thức ăn vật nuôi"),                                   # [ĐẶT]
    ("cách trồng khoai tây tại nhà", "trồng trọt"),                                 # [ĐẶT]
    ("tuyển dụng nhân viên sơ chế thực phẩm", "việc làm"),                          # [ĐẶT]
    ("luận văn về thực phẩm chế biến sẵn", "học thuật"),                            # [ĐẶT]
]

# PHẢI giữ lại — có chủ đích, đừng lọc nhầm vì trông giống nhiễu.
KEEP_CASES = [
    ("cách làm gà kho gừng", "công thức = tín hiệu R&D, như ngành chay"),
    ("khoai tây cắt sẵn bỏ tủ lạnh được không", "câu hỏi bảo quản, không phải người mua tủ"),
    ("đồ ăn cấp đông để được bao lâu", "câu hỏi bảo quản"),
    ("khoai tây cắt sẵn bách hoá xanh", "dò đối thủ ở chuỗi bán lẻ"),
    ("thực phẩm sơ chế bách hóa xanh", "dò đối thủ ở chuỗi bán lẻ"),
    ("thực phẩm sơ chế xuất hóa đơn", "bếp ăn doanh nghiệp đang mua"),
    ("thực phẩm sơ chế sẵn có tốt không", "hàng rào tin cậy phải trả lời"),
    ("thực phẩm sơ chế sẵn hà nội", "1 trong 14 cụm đã có volume [KP] — mốc so sánh"),
]


class RtcClassifyTest(unittest.TestCase):
    def test_labels(self):
        for s, expected in LABEL_CASES:
            with self.subTest(s=s):
                self.assertEqual(classify.classify_rtc(s), expected)

    def test_every_label_is_declared(self):
        for s, _ in LABEL_CASES:
            with self.subTest(s=s):
                self.assertIn(classify.classify_rtc(s), LABELS)

    def test_noise_is_filtered(self):
        for s, why in NOISE_CASES:
            with self.subTest(s=s, why=why):
                self.assertTrue(classify.rtc_is_negative(s))

    def test_keep_is_not_filtered(self):
        for s, why in KEEP_CASES:
            with self.subTest(s=s, why=why):
                self.assertFalse(classify.rtc_is_negative(s))

    def test_tone_placement_variants_match(self):
        """Hai kiểu đặt dấu hợp lệ phải cho cùng nhãn — lỗi thật đã bắt được 22/09/2026."""
        for a, b in [("thịt ướp sẵn bách hóa xanh", "thịt ướp sẵn bách hoá xanh"),
                     ("rau củ sơ chế hòa bình", "rau củ sơ chế hoà bình")]:
            with self.subTest(pair=(a, b)):
                self.assertEqual(classify.classify_rtc(a), classify.classify_rtc(b))


class RtcSeedTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = seeds.seeds_rtc()
        cls.keywords = [r["keyword"] for r in cls.rows]

    def test_seed_shape(self):
        self.assertGreater(len(self.rows), 3000)
        for r in self.rows[:50]:
            self.assertEqual(set(r), {"keyword", "nhom"})

    def test_seeds_are_unique_and_normalised(self):
        self.assertEqual(len(self.keywords), len(set(self.keywords)))
        for k in self.keywords:
            with self.subTest(k=k):
                self.assertEqual(k, k.lower().strip())
                self.assertNotIn("  ", k)

    def test_no_seed_is_filtered_as_noise(self):
        """Seed bị chính bộ lọc của mình loại = tốn request mà không bao giờ ghi được dòng nào.
        Lỗi thật 22/09: mẫu thiết bị 'chảo' ăn luôn 34 seed 'áp chảo' của tuyến healthy."""
        self.assertEqual([k for k in self.keywords if classify.rtc_is_negative(k)], [])

    def test_dish_axis_comes_from_real_menu(self):
        """Trục món phải là món DKC nấu thật, và phải phủ 12 SKU RTC."""
        self.assertGreaterEqual(len(seeds.RTC_MON), 500)
        for mon, so_lan in seeds.RTC_MON:
            with self.subTest(mon=mon):
                self.assertGreaterEqual(so_lan, 1)
        ten = {m for m, _ in seeds.RTC_MON}
        # 5/12 SKU RTC có tên khớp nguyên văn thực đơn — bằng chứng 12 SKU chọn ra từ menu_items
        for sku in ["gà kho gừng", "thịt kho tiêu", "chả trứng hấp", "thịt heo chiên muối sả",
                    "đậu hũ nhồi thịt sốt cà"]:
            with self.subTest(sku=sku):
                self.assertIn(sku, ten)

    def test_measured_keywords_are_seeded(self):
        """Cả 14 cụm đã có volume [KP] phải nằm trong seed — đây là mốc so sánh duy nhất
        giữa Suggest và search volume thật."""
        for k in seeds.RTC_DA_DO:
            with self.subTest(k=k):
                self.assertIn(k, self.keywords)

    def test_five_views_are_covered(self):
        """Mỗi view chủ DN yêu cầu 22/09/2026 phải có seed nuôi nó."""
        nhom = {}
        for r in self.rows:
            nhom.setdefault(r["nhom"], 0)
            nhom[r["nhom"]] += 1
        for view in ["Dish", "Recipe", "RTC", "MealPrep", "Local", "B2B", "Storage", "Retailer"]:
            with self.subTest(view=view):
                self.assertGreater(nhom.get(view, 0), 0)
        # TOP 20 món cần ít nhất 20 món trần được đo — bộ 2.979 từ khóa chỉ có 12 món, nên
        # trục món lấy từ thực đơn mới là thứ làm view này khả thi.
        self.assertGreaterEqual(nhom["Dish"], 20)


class RtcRegistrationTest(unittest.TestCase):
    def test_registered_everywhere(self):
        self.assertIs(seeds.INDUSTRIES["rtc"], seeds.seeds_rtc)
        self.assertIs(classify.CLASSIFIERS["rtc"], classify.classify_rtc)
        self.assertIs(classify.NEGATIVE["rtc"], classify.rtc_is_negative)

    def test_workflow_collects_rtc_by_default(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            ".github", "workflows", "collect.yml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        dispatch_default = re.search(r'industries:.*?default:\s*"([^"]+)"', text, re.S).group(1)
        schedule_default = re.search(
            r"INDUSTRIES: \$\{\{ github\.event\.inputs\.industries \|\| '([^']+)' \}\}", text).group(1)
        self.assertIn("rtc", dispatch_default.split(","))
        self.assertIn("rtc", schedule_default.split(","))


if __name__ == "__main__":
    unittest.main()
