# -*- coding: utf-8 -*-
"""Kiểm thử ngành trái cây (key `fruit`): classify_fruit, fruit_is_negative, seeds_fruit, đăng ký ngành.

MỌI chuỗi trong LABEL_CASES / NOISE_CASES / KEEP_CASES là gợi ý Google Suggest THẬT, lấy nguyên văn từ
mẻ đo 17/09/2026 (repo app: exports/trai-cay-suggest.csv — 4.233 gợi ý khác nhau) hoặc lượt đo bổ sung
cùng ngày (exports/trai-cay-seed-probe.json). Riêng Brand chưa có gợi ý thật nào → kiểm ở test riêng,
ghi rõ là chuỗi tự đặt.
Kiểm chứng toàn tập: python _research/trai-cay-eval-classifier.py (repo app).
"""
import os
import re
import unicodedata
import unittest

import classify
import seeds

LABELS = {"Brand", "Chain", "B2B", "Wholesale", "Gift", "Worship", "Party", "Delivery", "Store", "Pricing",
          "Trust", "Health", "Product", "Local", "Imported", "Core", "Other"}

# (gợi ý thật, nhãn kỳ vọng) — nhiều ca chọn ở ĐƯỜNG BIÊN giữa hai nhánh để khóa thứ tự nhánh
LABEL_CASES = [
    # Chain — tên chuỗi thắng mọi ý định khác (kể cả cửa hàng / giỏ / siêu thị)
    ("trái cây nhập khẩu hoa biển gò vấp", "Chain"),
    ("klever fruit lê văn sỹ", "Chain"),
    ("cửa hàng trái cây 141 an dương vương", "Chain"),
    ("giỏ trái cây farmers market", "Chain"),
    ("trái cây bách hóa xanh", "Chain"),
    ("siêu thị trái cây cao cấp citi fruit", "Chain"),
    ("tuti fruit chuỗi cửa hàng trái cây nhập khẩu", "Chain"),
    # B2B — tổ chức mua; bắt trước Gift / Worship / Wholesale
    ("trái cây văn phòng", "B2B"),
    ("giỏ trái cây tặng doanh nghiệp", "B2B"),
    ("trái cây cúng khai trương công ty", "B2B"),
    ("xuất hóa đơn giỏ trái cây thuế suất bao nhiêu", "B2B"),
    ("trái cây tiệc teabreak", "B2B"),
    ("cung cấp trái cây cho quán cafe", "B2B"),
    # Định nghĩa B2B chủ DN chốt 17/09/2026: tiệc gia đình → Party; thuế suất nhập khẩu → Wholesale
    ("trái cây tiệc cưới", "Party"),
    ("dĩa trái cây đãi tiệc", "Party"),
    ("trái cây tiệc buffet", "Party"),
    ("trái cây bày tiệc", "Party"),
    ("hoa quả nhập khẩu thuế suất bao nhiêu", "Wholesale"),
    ("trái cây nhập khẩu chịu thuế gtgt bao nhiêu", "Wholesale"),
    # Wholesale — sỉ / đầu mối / nhà nhập khẩu; bắt trước Pricing và Store
    ("giá trái cây chợ đầu mối thủ đức hôm nay", "Wholesale"),
    ("trái cây nhập khẩu giá sỉ tphcm", "Wholesale"),
    ("kho sỉ trái cây nhập khẩu sg", "Wholesale"),
    ("công ty nhập khẩu trái cây an minh", "Wholesale"),
    ("vựa trái cây gần đây", "Wholesale"),
    ("tìm mối bỏ sỉ trái cây", "Wholesale"),
    # Gift — giỏ thắng cúng, giá, giao, địa bàn
    ("giỏ trái cây 200k", "Gift"),
    ("giỏ trái cây viếng đám tang gò vấp", "Gift"),
    ("giỏ trái cây cúng giỗ", "Gift"),
    ("giỏ trái cây giao tận nơi", "Gift"),
    ("hộp quà trái cây nhập khẩu", "Gift"),
    ("giỏ trái cây kèm rượu", "Gift"),
    ("giỏ trái cây 500k tphcm", "Gift"),
    # Worship
    ("mâm ngũ quả miền nam gồm những gì", "Worship"),
    ("trái cây cúng rằm tháng 7", "Worship"),
    ("5 loại trái cây cúng thần tài", "Worship"),
    ("mua trái cây cúng mùng 1", "Worship"),
    ("trái cây cúng quay phim", "Worship"),
    ("mâm ngũ quả ý nghĩa", "Worship"),
    # Delivery — trước Store ("shop trái cây online")
    ("trái cây giao tận nơi tphcm", "Delivery"),
    ("mua trái cây online", "Delivery"),
    ("viettel post có giao trái cây không", "Delivery"),
    ("shop trái cây online", "Delivery"),
    # Store — cửa hàng / gần đây kiểu Maps / mua ở đâu
    ("cửa hàng trái cây nhập khẩu gò vấp", "Store"),
    ("trái cây nhập khẩu gần đây trong vòng 800m", "Store"),
    ("mua trái cây nhập khẩu ở đâu", "Store"),
    ("sạp trái cây chợ bến thành", "Store"),
    ("cửa hàng hoa quả chùa láng", "Store"),       # Chùa Láng là tên phố, không phải cúng chùa
    ("cửa hàng trái cây xuất khẩu", "Store"),
    # Pricing
    ("giá cherry mỹ", "Pricing"),
    ("trái cây nhập khẩu bao nhiêu tiền", "Pricing"),
    ("bảng giá trái cây nhập khẩu", "Pricing"),
    ("trái cây giá rẻ", "Pricing"),
    ("giá nho kẹo mỹ", "Pricing"),
    # Trust
    ("trái cây trung quốc có độc hay không", "Trust"),
    ("táo nhập khẩu có an toàn không", "Trust"),
    ("trái cây nhập khẩu mã số 3", "Trust"),
    ("cherry chile có phải của trung quốc không", "Trust"),
    # Health — "giá trị" và "bao nhiêu calo" KHÔNG phải khảo giá
    ("trái cây cho bà bầu 3 tháng đầu", "Health"),
    ("trái cây có giá trị dinh dưỡng cao", "Health"),
    ("cam úc bao nhiêu calo", "Health"),
    # Product
    ("cherry nhập khẩu tphcm", "Product"),
    ("nho mẫu đơn hàn quốc", "Product"),
    ("trái cây cắt sẵn", "Product"),
    ("trái cây sấy", "Product"),
    ("nho kẹo nhập khẩu", "Product"),
    ("táo nhập khẩu envy", "Product"),
    ("cam nhập khẩu úc", "Product"),
    # Local — địa danh, kể cả tên đường và "Ngãi Giao"/"Ngoại Giao Đoàn" (không phải "giao hàng")
    ("trái cây nhập khẩu quận 7", "Local"),
    ("trái cây nhập khẩu thủ dầu một", "Local"),
    ("trái cây nhập khẩu lê quang định", "Local"),
    ("trái cây nhập khẩu ngãi giao", "Local"),
    ("hoa quả nhập khẩu ngoại giao đoàn", "Local"),
    # Imported
    ("trái cây nhập khẩu", "Imported"),
    ("trai cay ngoai nhap", "Imported"),
    ("trái cây mỹ nhập khẩu", "Imported"),
    ("trái cây nhập", "Imported"),
    # Core; và "sinh nhật" không được đọc thành xuất xứ "nhật" — là dịp tiệc → Party (chốt 17/09/2026)
    ("các loại trái cây", "Core"),
    ("trái cây hữu cơ", "Core"),
    ("trái cây sinh nhật", "Party"),
    # Other — không có ngữ cảnh trái cây (rác đồng âm lọt lưới)
    ("biên hòa đồng nai", "Other"),
    ("giao hàng hoả tốc hà nội quảng ninh", "Other"),
    ("gừng hồng mua ở đâu", "Other"),
]

# HỒI QUY KIỂM TOÁN 17/09/2026 — mỗi misroute đã sửa có ca thật. Nguồn: "CSV" = exports/trai-cay-suggest.csv;
# "OOS" = Suggest ngoài mẫu cùng ngày, exports/trai-cay-audit-oos-raw.json (repo app).
AUDIT_LABEL_CASES = [
    # F1 gõ không dấu: trước đây rơi hết xuống Imported/Core, "giao thua" bị bắt thành Delivery
    ("gio trai cay quan 1", "Gift"),                          # OOS
    ("cua hang trai cay nhap khau gan day", "Store"),         # OOS
    ("trai cay cung giao thua", "Worship"),                   # OOS
    ("trai cay nhap khau quan 1", "Local"),                   # CSV
    ("hoa qua nhap khau ha noi", "Local"),                    # CSV
    ("cua hang trai cay hoa bien", "Store"),                  # OOS — KHÔNG đoán "hoa bien" = Hoa Biển
    # F6 đuôi Maps "trái cây nhập khẩu <X>": địa danh → Local, tên shop → Store, bổ ngữ chung → Imported
    ("hoa quả nhập khẩu bà triệu", "Local"),                  # CSV (phố Bà Triệu)
    ("trái cây nhập khẩu kon tum", "Local"),                  # CSV
    ("trái cây nhập khẩu hoa biên", "Local"),                 # CSV — từ khóa KP, Suggest trả toàn Biên Hòa
    ("trái cây nhập khẩu fruitland 77", "Store"),             # CSV
    ("jenny fruit trái cây nhập khẩu", "Store"),              # CSV
    ("trái cây nhập khẩu 365", "Store"),                      # CSV
    ("trái cây nhập khẩu úc mỹ new zealand canada", "Imported"),  # CSV
    ("các loại trái cây nhập khẩu vào việt nam", "Imported"),  # CSV
    ("hoa quả nhập khẩu màu tím", "Imported"),                # CSV
    ("trái cây nhập kh", "Imported"),                         # CSV (gõ dở)
    # F3 Health trước Trust
    ("bà bầu ăn nho có tốt không", "Health"),                 # OOS
    ("trái cây trung quốc có tốt không", "Trust"),            # CSV — không đổi
    # F2 "cung cấp" nghĩa dinh dưỡng không phải sỉ
    ("trái cây cung cấp vitamin c", "Health"),                # OOS
    ("nhà cung cấp trái cây tươi", "Wholesale"),              # CSV — không đổi
    ("organic farm cung cấp trái cây sỉ & lẻ", "Wholesale"),  # CSV — không đổi
    # Trust bỏ "bảo quản" trần, thêm "có hại"
    ("táo nhập khẩu để được bao lâu", "Product"),             # CSV
    ("cách bảo quản trái cây trong tủ lạnh", "Core"),         # OOS
    ("nho mẫu đơn trung quốc ăn có hại không", "Trust"),      # OOS
    # Chain "fuji" đứng tách, chặn "táo fuji"
    ("hoa quả sạch fuji nha trang", "Chain"),                 # CSV
    ("hoa qua sach fuji", "Chain"),                           # OOS
    ("giá táo fuji nam phi", "Pricing"),                      # CSV
    # Gift: dịp mang trái cây đi dù không có "giỏ"; có "cúng" thì vẫn Worship
    ("tháp trái cây đám tang", "Gift"),                       # OOS
    ("mâm ngũ quả lễ ăn hỏi", "Gift"),                        # CSV
    ("đám tang cúng trái cây gì", "Worship"),                 # CSV
    ("trái cây cúng đám tang", "Worship"),                    # CSV
    # "cho bé" sau dịp lễ không phải dinh dưỡng
    ("mâm trái cây trung thu cho bé", "Core"),                # OOS
    ("trái cây sinh nhật cho bé", "Party"),                   # CSV — Health không nuốt; dịp tiệc (chốt 17/09)
    ("trái cây cho bé ăn dặm", "Health"),                     # CSV — không đổi
    # Nhu cầu mua trước đây bị lọc nhầm
    ("trái cây nhà trồng", "Core"),                           # OOS ("trồng")
    ("cây ba trồng cửa hàng trái cây nhập khẩu gia lai", "Store"),  # CSV ("trồng")
    ("shop bán trái cây online", "Delivery"),                 # CSV ("bán … online")
    ("thùng táo envy bao nhiêu kg", "Pricing"),               # OOS
    ("táo mỹ bao nhiêu 1kg", "Pricing"),                      # OOS
    ("cửa hàng hoa quả ưu đàm", "Store"),                     # CSV — tên shop, KHÔNG lọc "ưu đàm"
]

# Nhiễu có ngữ cảnh trái cây trước đây lọt vào Gift/Core/Health/B2B/Trust — nay phải bị lọc
AUDIT_NOISE_CASES = [
    "cách làm giỏ trái cây đám tang",               # CSV, trước là Gift
    "cách làm giỏ trái cây đơn giản tại nhà",       # CSV, trước là Gift
    "trang trí giỏ trái cây tết",                   # CSV, trước là Gift
    "trang trí trái cây tiệc",                      # CSV, trước là B2B
    "khắc trái cây trung thu",                      # OOS, trước là Core
    "tỉa trái cây trung thu",                       # OOS, trước là Core
    "trái cây siro",                                # CSV, trước là Core
    "trái cây si ăn được không",                    # CSV, trước là Core
    "vitamin trái cây thái lan",                    # CSV, trước là Health
    "cách bảo quản trái cây tươi lâu để bán",       # OOS, trước là Trust
    "táo mỹ 102",                                   # CSV, vẫn lọc (chuỗi iPhone)
    "táo mỹ bà tô",                                 # CSV, vẫn lọc
    "một cửa hàng hoa quả nhập về 15 thùng xoài",   # CSV, vẫn lọc (bài toán)
    "thiết kế cửa hàng trái cây nhập khẩu",         # CSV, vẫn lọc (người mở shop)
    "bán trái cây nhập khẩu online",                # OOS, vẫn lọc (người bán)
]

# Nhiễu PHẢI bị lọc — mỗi nhóm trong fruit_is_negative có ít nhất một ca
NOISE_CASES = [
    "giá trái cây grow a garden",                  # game
    "shop trái cây blox fruit",                    # game
    "thả trái cây shopee",                         # game
    "web+tính+giá+trái+cây+grow+a+garden",         # game, dấu "+" thay khoảng trắng
    "giáo án trái cây trong vườn",                 # giáo dục (giao→giáo)
    "mâm ngũ quả tiếng anh là gì",                 # học tiếng
    "một cửa hàng hoa quả có 120kg cam",           # bài toán tiểu học
    "rượu trái cây hàn quốc",                      # khác ngành
    "giá máy ép trái cây panasonic",               # khác ngành
    "giá lên thổ cư bình dương",                   # đồng âm "giá lê"
    "cấm nhập khẩu gạo",                           # đồng âm "cam nhập khẩu"
    "hoa hồng nhập khẩu",                          # đồng âm "hồng nhập khẩu"
    "táo mỹ iphone",                               # đồng âm "táo mỹ"
    "giá vé vườn trái cây lái thiêu",              # tham quan vườn
    "biên hòa đồng nai sau sáp nhập",              # hành chính ("hoa biên")
    "true fruits deckel",                          # tên nước ngoài trùng
    "klever fruit tuyển dụng",                     # việc làm
    "trái cây giả cao cấp",                        # đồ giả
    "hạt giống dưa lưới mua ở đâu",                # trồng trọt
    "trái cây việt nam xuất khẩu trung quốc",      # vĩ mô xuất khẩu
]

# KHÔNG được lọc nhầm — đều là ca biên có từ nằm trong danh sách nhiễu
KEEP_CASES = [
    "giỏ trái cây kèm rượu",                       # "rượu" nhưng là giỏ quà thật
    "nho kẹo nhập khẩu",                           # "kẹo" nhưng là giống nho
    "an nhiên fruits trái cây bánh kẹo nhập khẩu vũng tàu",
    "trái cây cúng quay phim",                     # "phim" nhưng là cúng khai máy
    "hoa quả nhập khẩu thuế suất bao nhiêu",       # tình báo nhập khẩu → Wholesale (chốt 17/09)
    "trái cây cho người tiểu đường",               # sức khỏe → Health, không lọc
    "cửa hàng trái cây xuất khẩu",                 # hàng loại xuất khẩu bán lẻ
    "trái cây sấy dẻo giá sỉ",                     # đồ sấy là mặt hàng
    "mâm ngũ quả ý nghĩa",
    "trái cây nhập khẩu mã số 3",
    "trái cây nhập khẩu hoa biển gò vấp ảnh",      # đuôi "ảnh" của Maps vẫn là nhu cầu
    "trái cây tiệc trà",                           # "trà" nhưng không phải trà trái cây
    "hoa quả nhập khẩu phạm ngọc thạch",           # "thạch" là tên đường
    "cam nhập khẩu úc",                            # không dính "cấm"
    "giỏ trái cây kèm bánh trung thu",
]


class FruitClassifierTest(unittest.TestCase):
    def test_labels_on_real_suggestions(self):
        self.assertGreaterEqual(len(LABEL_CASES), 50)
        for text, expected in LABEL_CASES:
            with self.subTest(text=text):
                self.assertFalse(classify.fruit_is_negative(text), "ca nhãn không được bị lọc")
                self.assertEqual(classify.classify_fruit(text), expected)

    def test_every_label_except_brand_is_exercised(self):
        self.assertEqual({e for _, e in LABEL_CASES}, LABELS - {"Brand"})

    def test_brand_synthetic(self):
        # Chưa có gợi ý thật chứa tên nhà → chuỗi tự đặt, chỉ khóa nhánh đầu tiên
        self.assertEqual(classify.classify_fruit("giỏ trái cây mộc an"), "Brand")
        self.assertEqual(classify.classify_fruit("trái cây thành gia định"), "Brand")
        self.assertEqual(classify.classify_fruit("trai cay thanh gia dinh"), "Brand")
        # Đồng Khởi là tên đường dày cửa hàng → không được thắng nhánh Brand (kiểm toán 17/09, chuỗi TỰ ĐẶT)
        self.assertEqual(classify.classify_fruit("cửa hàng trái cây đồng khởi quận 1"), "Store")
        self.assertEqual(classify.classify_fruit("giỏ trái cây đồng khởi catering"), "Brand")

    def test_audit_regressions_on_real_suggestions(self):
        for text, expected in AUDIT_LABEL_CASES:
            with self.subTest(text=text):
                self.assertFalse(classify.fruit_is_negative(text), "ca nhãn không được bị lọc")
                self.assertEqual(classify.classify_fruit(text), expected)

    def test_audit_noise_is_filtered(self):
        for text in AUDIT_NOISE_CASES:
            with self.subTest(text=text):
                self.assertTrue(classify.fruit_is_negative(text))

    def test_audit_rare_b2b_not_dropped_synthetic(self):
        # Chuỗi TỰ ĐẶT (chưa thấy trong Suggest): các từ lọc quá rộng từng nuốt tín hiệu mua hiếm
        keep = {"giỏ trái cây tặng đối tác kinh doanh": "Gift",
                "cung cấp trái cây cho trường mầm non": "B2B",
                "trái cây nhập khẩu tuyển chọn": "Imported",
                "giỏ trái cây thiết kế theo yêu cầu": "Gift",
                "táo mỹ 1 kg giá bao nhiêu": "Pricing",
                # Định nghĩa B2B chủ DN chốt 17/09/2026 + soát độc lập cùng ngày (chuỗi TỰ ĐẶT):
                # tiệc của TỔ CHỨC vẫn B2B; tiệc gia đình → Party; hỏi thuế/VAT nhập khẩu → Wholesale.
                "trái cây tiệc cty": "B2B",
                "trái cây tiệc year end công ty quận 7": "B2B",
                "trái cây tiệc tất niên": "B2B",
                "trai cay tiec cong ty": "B2B",
                "trái cây có xuất vat không": "B2B",
                "hoa quả nhập khẩu vat bao nhiêu": "Wholesale",
                "cửa hàng miễn thuế trái cây": "Store",
                "trai cay tiec cuoi": "Party",
                "trái cây party": "Party",
                "mâm ngũ quả bày trước hay sau cúng tất niên": "Worship"}
        for text, expected in keep.items():
            with self.subTest(text=text):
                self.assertFalse(classify.fruit_is_negative(text))
                self.assertEqual(classify.classify_fruit(text), expected)

    def test_noise_is_filtered(self):
        self.assertGreaterEqual(len(NOISE_CASES), 12)
        for text in NOISE_CASES:
            with self.subTest(text=text):
                self.assertTrue(classify.fruit_is_negative(text))

    def test_borderline_real_demand_is_kept(self):
        self.assertGreaterEqual(len(KEEP_CASES), 8)
        for text in KEEP_CASES:
            with self.subTest(text=text):
                self.assertFalse(classify.fruit_is_negative(text))

    def test_nfd_input_is_normalized(self):
        nfd = unicodedata.normalize("NFD", "giỏ trái cây viếng đám tang gò vấp")
        self.assertEqual(classify.classify_fruit(nfd), "Gift")
        self.assertTrue(classify.fruit_is_negative(unicodedata.normalize("NFD", "giáo án trái cây trong vườn")))

    def test_output_always_in_label_set(self):
        for text in ([t for t, _ in LABEL_CASES] + [t for t, _ in AUDIT_LABEL_CASES] + NOISE_CASES
                     + AUDIT_NOISE_CASES + KEEP_CASES + ["", None]):
            with self.subTest(text=text):
                self.assertIn(classify.classify_fruit(text), LABELS)


class FruitSeedsTest(unittest.TestCase):
    def setUp(self):
        self.rows = seeds.seeds_fruit()
        self.keywords = [r["keyword"] for r in self.rows]

    def test_size_and_dedupe(self):
        self.assertTrue(400 <= len(self.rows) <= 1500, len(self.rows))
        self.assertEqual(len(self.keywords), len(set(self.keywords)))

    def test_nhom_is_a_classifier_label(self):
        self.assertTrue({r["nhom"] for r in self.rows} <= LABELS - {"Brand", "Other"})

    def test_all_21_keyword_planner_terms_are_seeds(self):
        kp21 = ["trai cay ngoai nhap", "trái cây nhập khẩu", "hoa qua nhập khẩu", "hoa quả nhập khẩu",
                "trái cây nhập khẩu gần đây", "các loại trái cây", "trái cây nhập khẩu hoa biên",
                "giỏ hoa quả nhập khẩu", "hoa quả nhập khẩu gần đây", "cửa hàng trái cây nhập khẩu",
                "cửa hàng hoa quả sạch", "hoa quả sạch gần đây", "klever fruit gần đây", "shop trái cây gần đây",
                "trái cây nhập", "cửa hàng trái cây nhập khẩu gần đây", "cửa hàng hoa quả nhập khẩu gần đây",
                "cửa hàng trái cây vinfruits", "giỏ trái cây 200k", "tiệm trái cây nhập khẩu gần đây",
                "5 loại trái cây cúng"]
        for k in kp21:
            with self.subTest(k=k):
                self.assertIn(k, self.keywords)

    def test_no_bare_homonym_or_dead_seeds(self):
        # Đo 17/09/2026: các seed này trả nhiễu đồng âm hoặc 0 gợi ý
        banned = ["giá lê", "giá cam", "giá bơ", "giá vải", "giá hồng", "giá đào", "cam nhập khẩu", "bơ nhập khẩu",
                  "hồng nhập khẩu", "vải mua ở đâu", "lê mua ở đâu", "hoa biên", "truefruits", "true fruits",
                  "sunfruit", "koi fruits", "giao trái cây", "giao hoa quả", "trái cây shopee", "táo mỹ",
                  "trái cây cúng vu lan", "trái cây nhập khẩu chính hãng", "ship trái cây nhập khẩu",
                  "trái cây đồng giá", "trái cây nhập khẩu khuyến mãi"]
        for k in banned:
            with self.subTest(k=k):
                self.assertNotIn(k, self.keywords)

    def test_geography_is_hcm_only(self):
        outside = re.compile(r"(hà nội|đà nẵng|cần thơ|hải phòng|biên hòa|biên hoà|nha trang|huế|quy nhơn|đà lạt)")
        self.assertEqual([k for k in self.keywords if outside.search(k)], [])

    def test_no_seed_is_filtered_as_noise(self):
        self.assertEqual([k for k in self.keywords if classify.fruit_is_negative(k)], [])

    def test_audit_seed_changes(self):
        # Kiểm toán 17/09/2026: bỏ chữ cái chỉ trả nhiễu / trùng hoàn toàn; thêm trục đo được; KP "hoa biên" không phải Chain
        for k in ["mâm ngũ quả a", "mâm ngũ quả i", "mâm ngũ quả w", "giỏ trái cây i",
                  "cửa hàng trái cây nhập khẩu a", "cửa hàng trái cây nhập khẩu 5"]:
            with self.subTest(removed=k):
                self.assertNotIn(k, self.keywords)
        for k in ["trái cây trung thu", "trái cây chưng tết", "tháp trái cây", "thùng táo",
                  "gio trai cay", "cua hang trai cay", "trai cay cung"]:
            with self.subTest(added=k):
                self.assertIn(k, self.keywords)
        nhom = {r["keyword"]: r["nhom"] for r in self.rows}
        self.assertEqual(nhom["trái cây nhập khẩu hoa biên"], "Local")
        # seed không dấu phải được classifier thêm dấu → đúng nhóm, không rơi xuống Imported/Core
        for k in ["gio trai cay", "cua hang trai cay", "trai cay cung"]:
            with self.subTest(ascii_seed=k):
                self.assertEqual(classify.classify_fruit(k), nhom[k])


class FruitRegistrationTest(unittest.TestCase):
    def test_registered_everywhere(self):
        self.assertIs(seeds.INDUSTRIES["fruit"], seeds.seeds_fruit)
        self.assertIs(classify.CLASSIFIERS["fruit"], classify.classify_fruit)
        self.assertIs(classify.NEGATIVE["fruit"], classify.fruit_is_negative)

    def test_workflow_collects_fruit_by_default(self):
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            ".github", "workflows", "collect.yml")
        with open(path, encoding="utf-8") as f:
            text = f.read()
        dispatch_default = re.search(r'industries:.*?default:\s*"([^"]+)"', text, re.S).group(1)
        schedule_default = re.search(r"INDUSTRIES: \$\{\{ github\.event\.inputs\.industries \|\| '([^']+)' \}\}", text).group(1)
        self.assertIn("fruit", dispatch_default.split(","))
        self.assertIn("fruit", schedule_default.split(","))


if __name__ == "__main__":
    unittest.main()
