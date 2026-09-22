# -*- coding: utf-8 -*-
"""Phân loại intent + lọc negative cho từng ngành (port từ Apps Script)."""
import re
import unicodedata

# Update this only when classifier logic changes. Operational-only commits do
# not create a new classifier boundary.
CLASSIFIER_VERSION = "classify-5526c9e"


def is_english(s: str) -> bool:
    t = (s or "").lower().strip()
    if not re.search(r"[a-z]", t):
        return False
    if re.search(r"[àáảãạăắằẳẵặâấầẩẫậđèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵ]", t):
        return False
    return (" " in t) or bool(re.search(r"(rent|lease|lunch|catering|apartment|office|hotel|resort|water|delivery|supply|mineral|bottle|corporate)", t))


def classify_food(s: str) -> str:
    t = (s or "").lower()
    if "đồng khởi" in t:
        return "Brand"
    if re.search(r"(suất ăn|catering|đặt cơm|đoàn|hội nghị|tiệc|sự kiện|công ty|doanh nghiệp|nhà máy|khu công nghiệp|corporate catering|office catering|bento|buffet)", t):
        return "B2B"
    if re.search(r"(giá|bao nhiêu|rẻ|khuyến mãi|price)", t):
        return "Pricing"
    if re.search(r"(giao|ship|tận nơi|đặt online|delivery|lunch box)", t):
        return "Delivery"
    if re.search(r"(review|ngon|sạch|uy tín|ở đâu|nào ngon|so sánh|best)", t):
        return "Consideration"
    if re.search(r"(thực đơn|menu|là gì|dinh dưỡng|healthy|eat clean|meal prep)", t):
        return "Awareness"
    if re.search(r"(gần|quận|phường|khu |đường |near me|district|thao dien|phu my hung)", t):
        return "Local"
    if re.search(r"(cơm|suất ăn|lunch|meal)", t):
        return "Core"
    return "Other"


def re_is_negative(s: str) -> bool:
    t = (s or "").lower()
    return bool(re.search(r"(mua bán|bán nhà|bán đất|bán căn hộ|ký gửi|sang nhượng|đất nền|đất thổ cư|condotel|nghỉ dưỡng|biệt thự|dự án|mở bán|chủ đầu tư|sổ hồng|sổ đỏ|đầu tư|sang quán|nhượng quán|định cư|vay mua|trả góp|for sale|for sell)", t))


def classify_realestate(s: str) -> str:
    t = (s or "").lower()
    if "đồng khởi" in t:
        return "Brand"
    if re.search(r"(văn phòng ảo|coworking|virtual office|hot desk|shared office|chỗ ngồi làm việc|làm việc chung|bàn làm việc|văn phòng chia sẻ)", t):
        return "Coworking"
    if re.search(r"(văn phòng|sàn văn phòng|tòa nhà|office|grade a|nhà xưởng|kho xưởng|khu công nghiệp|kcn|kcx|khu chế xuất|khu công nghệ cao|factory|warehouse)", t):
        return "Office"
    if re.search(r"(mặt bằng|shophouse|kiot|ki ốt|cửa hàng|quán|retail space|shop for rent)", t):
        return "Retail"
    if re.search(r"(căn hộ|chung cư|nhà nguyên căn|phòng trọ|nhà ở|duplex|studio|officetel|penthouse|apartment|serviced apartment|house for rent)", t):
        return "Residential"
    if re.search(r"(giá|bao nhiêu|rẻ|m2|chi phí|hạng a|cao cấp|luxury)", t):
        return "Pricing"
    if re.search(r"(kinh nghiệm|thủ tục|hợp đồng|lưu ý|là gì|cách )", t):
        return "Awareness"
    if re.search(r"(quận|phường|huyện|gần|khu |đường |district|thao dien|phu my hung)", t):
        return "Local"
    if re.search(r"(thuê|cho thuê|rent|lease)", t):
        return "Office"
    return "Other"


def classify_hotel(s: str) -> str:
    t = (s or "").lower()
    if re.search(r"(đặt|book|vé|giá phòng|đặt phòng)", t):
        return "Transactional"
    if re.search(r"(đoàn|hội nghị|tiệc|sự kiện|set menu|company|corporate)", t):
        return "B2B"
    if re.search(r"(giá|bao nhiêu|rẻ|khuyến mãi|cheap|price)", t):
        return "Pricing"
    if re.search(r"(review|tốt nhất|đáng đi|nào đẹp|best|so sánh)", t):
        return "Commercial"
    if re.search(r"(kinh nghiệm|cẩm nang|mùa nào|là gì|nên đi)", t):
        return "Informational"
    if re.search(r"(gần|quận|phường|biển|trung tâm|near|district)", t):
        return "Local"
    return "Transactional"

def water_is_negative(s: str) -> bool:
    t = (s or "").lower()
    return bool(re.search(
        r"(nước hoa|nước mắm|nước tương|nước giặt|nước rửa|nước lau|nước tẩy|"
        r"nước thải|nước sinh hoạt|nước cất|nước muối|nước tiểu|nước ối|"
        r"máy lọc nước|lọc nước|hồ cá|bể cá|nước giải khát|trà sữa|bia|rượu|"
        r"nước ép|sinh tố|nước ngọt|coca|pepsi|7up|sting)",
        t,
    ))


def classify_water(s: str) -> str:
    t = (s or "").lower()
    if is_english(t):
        return "English"
    if re.search(r"(lavie|la vie|vĩnh hảo|vinh hao|ion life|aquafina|bidrico|sapuwa|dasani|dasan|satori)", t):
        return "Brand"
    if re.search(r"(cây nước|nóng lạnh|nong lanh|bình úp|binh up|cây nóng lạnh)", t):
        return "Equipment"
    if re.search(r"(19l|20l|bình|binh|đóng bình|dong binh|bình nước|water bottle 20l)", t):
        return "Bottle20L"
    if re.search(r"(chai|thùng|thung|350ml|500ml|phòng họp|phong hop|meeting|hội nghị|hoi nghi|tiếp khách|tiep khach)", t):
        return "Meeting"
    if re.search(r"(giá|gia|sỉ|si|chiết khấu|chiet khau|công nợ|cong no|vat|hóa đơn|hoa don|bao nhiêu|bao nhieu|rẻ|re|price|invoice)", t):
        return "Pricing"
    if re.search(r"(quận|phường|huyện|gần|khu |đường |district|thao dien|phu my hung|k300|tân bình|tan binh|bình thạnh|binh thanh)", t):
        return "Local"
    if re.search(r"(đổi|doi|giao|gọi|goi|đại lý|dai ly|delivery|supply|cung cấp|cung cap)", t):
        return "Action"
    if re.search(r"(nước|nuoc|water|mineral)", t):
        return "Action"
    return "Other"


def classify_produce(s: str) -> str:
    """Rau củ quả B2B. Thứ tự nhánh có chủ đích: các ý định HẸP và đắt tiền
    (chợ đầu mối, sơ chế, chứng nhận) phải bắt TRƯỚC nhánh rộng, nếu không
    chúng bị nhánh 'B2B' hoặc 'Pricing' nuốt mất."""
    t = (s or "").lower()
    if "đồng khởi" in t or "thành gia định" in t:
        return "Brand"
    # Chợ đầu mối = mặt trận riêng, và là nơi giá hình thành. Bắt trước Pricing.
    if re.search(r"(chợ đầu mối|chợ nông sản|chợ sỉ|bình điền|hóc môn|thủ đức.*chợ|chợ.*thủ đức)", t):
        return "Market"
    # Sơ chế/cắt sẵn = dịch vụ biên lợi nhuận cao, đừng để rơi vào Service chung
    if re.search(r"(sơ chế|cắt sẵn|gọt sẵn|rửa sẵn|bóc sẵn|thái sẵn|đóng gói theo yêu cầu)", t):
        return "Processing"
    if re.search(r"(vietgap|globalgap|hữu cơ|organic|an toàn thực phẩm|attp|truy xuất|chứng nhận|kiểm định|hóa đơn|vat)", t):
        return "Certification"
    if re.search(r"(giao|ship|tận nơi|mỗi ngày|sáng sớm|trong ngày|đúng giờ|vận chuyển)", t):
        return "Delivery"
    if re.search(r"(bảng giá|báo giá|giá sỉ|giá bán|giá hôm nay|bao nhiêu|đơn giá|giá thị trường|giá rẻ)", t):
        return "Pricing"
    # Ai mua — trục thương mại chính của ngành này
    if re.search(r"(nhà hàng|quán ăn|khách sạn|bếp ăn|căn tin|canteen|suất ăn|chuỗi|trường học|công ty|siêu thị|resort|tiệc)", t):
        return "B2B"
    if re.search(r"(nguồn|ở đâu|đà lạt|miền tây|lâm đồng|nhà vườn|hợp tác xã|vùng trồng|tìm nhà cung cấp)", t):
        return "Sourcing"
    if re.search(r"(cung cấp|nhà cung cấp|đơn vị|công ty|đại lý|bán sỉ|sỉ\b|số lượng lớn|hợp đồng)", t):
        return "Supply"
    if re.search(r"(quận|phường|huyện|gần|tphcm|hồ chí minh|sài gòn|thủ đức|bình thạnh)", t):
        return "Local"
    return "Product"


def produce_is_negative(s: str) -> bool:
    """Loại nhiễu của ngành rau củ. Bốn nhóm, đều đã thấy thật khi đo SERP 18/08:
      1) THIẾT BỊ — nahaki (tủ cơm, inox) và kainox lọt cả vào top 5 SERP rau củ
      2) TRỒNG TRỌT — hạt giống, phân bón, kỹ thuật trồng: người trồng, không phải người mua
      3) NẤU ĂN / SỨC KHỎE — công thức, tác dụng, giảm cân: người tiêu dùng cuối
      4) BÁN LẺ — siêu thị, bách hóa, mua lẻ 1kg: sai hoàn toàn tệp khách B2B
    """
    t = (s or "").lower()
    return bool(re.search(
        r"(máy rửa|máy thái|máy gọt|máy sấy|tủ cơm|tủ hấp|tủ mát|tủ đông|inox|thiết bị bếp|"
        r"dụng cụ|khay đựng|rổ nhựa|kệ hàng|"
        r"hạt giống|cách trồng|kỹ thuật trồng|phân bón|thuốc trừ sâu|giống cây|ươm giống|"
        r"trồng tại nhà|trồng thủy canh|vườn nhà|"
        r"cách nấu|cách làm|công thức|món ngon|nấu món|chế biến món|ăn kiêng|giảm cân|"
        r"tác dụng|công dụng|có tốt không|bà bầu|trẻ em|dinh dưỡng của|chữa bệnh|"
        r"bách hóa xanh|winmart|co ?opmart|lotte|aeon|emart|mua lẻ|bán lẻ|đi chợ hộ|"
        r"tuyển dụng|việc làm|thực tập)", t))


def classify_vegetarian(s: str) -> str:
    """Món chay (Mộc An). Thứ tự nhánh: các ý định HẸP và ra tiền (quà, đóng gói,
    sỉ B2B, dịp lễ) bắt TRƯỚC các nhánh rộng (quán, giá, core) — nếu không chúng
    bị nuốt. 'Cách làm/công thức' là tín hiệu R&D, KHÔNG phải nhiễu ở ngành này.

    14 nhãn (thêm 'Retail' ngày 26/08/2026): Brand, Gift, Packaged, B2B, Occasion,
    Recipe, Retail, Delivery, Restaurant, Pricing, Healthy, Ingredient, Local, Core, Other.
    Ánh xạ kênh: Gift->GIFTS · Packaged+Retail->SHOP · B2B->PRO · Delivery+Restaurant->DAILY."""
    t = (s or "").lower()
    if re.search(r"(mộc an|đồng khởi|thành gia định)", t):
        return "Brand"
    # Quà chay — kênh Gifts, biên cao, bắt trước mọi nhánh rộng
    if re.search(r"(quà|giỏ quà|hộp quà|biếu|tặng)", t):
        return "Gift"
    # Đóng gói / chế biến sẵn — kênh Pro + Gifts
    if re.search(r"(đóng gói|đóng hộp|đồ hộp|cấp đông|đông lạnh|ăn liền|chân không|chế biến sẵn|đồ chay khô|hạn sử dụng|bảo quản)", t):
        return "Packaged"
    # Sỉ / B2B — kênh Pro
    if re.search(r"(sỉ|bỏ sỉ|gia công|xưởng|đại lý|nguồn hàng|mở quán|kinh doanh|hóa đơn|suất ăn chay|công ty|công nghiệp|catering|nguyên liệu.*(quán|nhà hàng))", t):
        return "B2B"
    # Dịp lễ — mùa vụ: rằm, mùng 1, Vu Lan, Tết, giỗ, tiệc
    if re.search(r"(rằm|mùng 1|mồng 1|vu lan|tết|giỗ|cúng|cỗ|lễ|phật đản|tiệc|đãi khách)", t):
        return "Occasion"
    if re.search(r"(cách làm|cách nấu|công thức|hướng dẫn|tự làm|nấu như thế nào|làm tại nhà)", t):
        return "Recipe"
    # BÁN LẺ — kênh SHOP. Thêm 26/08/2026 sau khi đo: 19 seed nhóm "mua ở đâu" sinh 220 dòng
    # nhưng 130 dòng bị dồn vào Core vì không có nhãn riêng, làm loãng cả Core lẫn tín hiệu
    # bán lẻ. Đặt TRƯỚC Delivery để "mua online" không bị nhánh "online" của Delivery nuốt,
    # và SAU Packaged để dạng sản phẩm (đóng gói/ăn liền) vẫn được ưu tiên nhận diện.
    if re.search(r"(mua ở đâu|bán ở đâu|chỗ bán|nơi bán|chỗ mua|đặt mua|mua\s.{0,25}online|"
                 r"siêu thị|bách hóa|tạp hóa|cửa hàng|store)", t):
        return "Retail"
    if re.search(r"(giao|ship|tận nơi|online|mang về|đặt cơm|đặt món)", t):
        return "Delivery"
    if re.search(r"(quán|nhà hàng|buffet|tiệm|địa chỉ|ở đâu ngon|gần đây)", t):
        return "Restaurant"
    if re.search(r"(giá|bao nhiêu|rẻ|khuyến mãi|combo|bảng giá)", t):
        return "Pricing"
    if re.search(r"(healthy|giảm cân|eat clean|dinh dưỡng|đủ chất|đạm|protein|tốt không|tốt cho|thiếu chất|khoa học)", t):
        return "Healthy"
    # Nguyên liệu — trả lời "một nguyên liệu tạo được bao nhiêu món"
    if re.search(r"(nấm|đậu hũ|tàu hũ|mì căn|củ sen|hạt sen|mít non|chuối xanh|đậu nành|rong biển|đậu gà|đậu lăng)", t):
        return "Ingredient"
    if re.search(r"(quận|phường|huyện|gần|tphcm|hồ chí minh|sài gòn|hà nội|đà nẵng|thủ đức|bình thạnh)", t):
        return "Local"
    if "chay" in t:
        return "Core"
    return "Other"


def vegetarian_is_negative(s: str) -> bool:
    """Loại nhiễu ngành món chay. Năm nhóm:
      1) TÔN GIÁO THUẦN TÚY — tụng kinh, khóa tu: không phải nhu cầu món ăn
         (nhưng rằm/Vu Lan/cúng GIỮ LẠI — đó là mùa vụ bán hàng)
      2) GIẢI TRÍ — phim, truyện, nhạc
      3) THIẾT BỊ — máy làm đậu hũ, tủ đông: người mua máy, không mua món
      4) TRỒNG TRỌT — hạt giống, cách trồng: người trồng, không phải người ăn
      5) VIỆC LÀM — tuyển dụng, lương
    KHÔNG lọc 'cách làm/công thức' (tín hiệu R&D) và KHÔNG lọc siêu thị bán lẻ
    (đối chứng kênh retail cho Daily/Gifts)."""
    t = (s or "").lower()
    return bool(re.search(
        r"(tụng kinh|nghe kinh|kinh phật|khóa tu|pháp thoại|giảng pháp|xuất gia|đi tu|thầy thích|"
        r"phim|truyện|lời bài hát|karaoke|game|"
        r"máy làm|máy ép|máy xay công nghiệp|tủ đông|tủ mát|thiết bị bếp|dụng cụ|khuôn ép|"
        r"hạt giống|cách trồng|kỹ thuật trồng|phân bón|trồng tại nhà|"
        r"tuyển dụng|việc làm|thực tập|mức lương)", t))


# ─────────────────────────── TRÁI CÂY (fruit) ───────────────────────────
# Mọi mẫu dưới đây lấy từ mẻ đo Google Suggest 17/09/2026 (1.518 seed, 4.233 gợi ý khác nhau,
# exports/trai-cay-suggest.csv ở repo app) và SERP TP.HCM cùng ngày (exports/trai-cay-serp.json).
# Kiểm chứng bằng _research/trai-cay-eval-classifier.py (repo app) + tests/test_fruit.py.

def _fruit_norm(s: str) -> str:
    # Suggest trả NFC, nhưng seed/nhập tay có thể là NFD → chuẩn hoá để regex có dấu khớp chắc.
    # "+" thay khoảng trắng: đã thấy "web+tính+giá+trái+cây+grow+a+garden" trong mẻ 17/09.
    return " ".join(unicodedata.normalize("NFC", s or "").lower().replace("+", " ").split())


# GÕ KHÔNG DẤU. Mọi regex ý định bên dưới viết CÓ dấu, còn cửa chặn ngữ cảnh nhận cả "trai cay|hoa qua"
# → chuỗi không dấu lọt cửa rồi rơi thẳng xuống Imported/Core. Đo 17/09/2026: seed "trai cay nhap khau"
# trả 7/10 gợi ý không dấu (đều thành Imported); 35 seed kiểm toán ngoài mẫu (exports/trai-cay-audit-oos-raw.json)
# có "gio trai cay quan 1", "cua hang trai cay nhap khau gan day", "trai cay cung giao thua" (bị bắt nhầm
# Delivery vì "giao"). Từ khóa KP số 1 "trai cay ngoai nhap" (14.800/tháng — số người dùng cung cấp) cũng
# không dấu. Cách sửa: CHỈ khi cả chuỗi là ASCII và có "trai cay|hoa qua", thêm dấu cho các CỤM CỐ ĐỊNH
# (có ngữ cảnh) rồi mới phân loại. KHÔNG thêm dấu cho từ đơn mơ hồ: "phat"/"ram" đứng một mình ("tien phat"
# là tên shop), "gio" (giỏ/giờ/giỗ), "hoa bien" (Suggest cho "trái cây nhập khẩu hoa biên" trả 8 gợi ý
# Biên Hòa, 0 Hoa Biển — chưa quy được cho chuỗi Hoa Biển), "si" (sỉ hay cây si).
_FRUIT_THEM_DAU = [(re.compile(a), b) for a, b in [
    (r"\bcung cap\b", "cung cấp"), (r"\btrai cay\b", "trái cây"), (r"\bhoa qua\b", "hoa quả"),
    (r"\b(trái cây|hoa quả) sach\b", r"\1 sạch"),
    (r"\bcua hang\b", "cửa hàng"), (r"\btiem\b", "tiệm"), (r"\bgan day\b", "gần đây"), (r"\bo dau\b", "ở đâu"),
    (r"\bcung gio\b", "cúng giỗ"), (r"\bdam gio\b", "đám giỗ"), (r"\bdam tang\b", "đám tang"),
    (r"\bgio (?=trái cây|hoa quả|qua\b)", "giỏ "), (r"\bhop qua\b", "hộp quà"), (r"\bqua (tang|bieu)\b", r"quà \1"),
    (r"\bquà tang\b", "quà tặng"), (r"\bbieu\b", "biếu"), (r"\bvieng\b", "viếng"), (r"\bmam ngu qua\b", "mâm ngũ quả"),
    (r"\b(trái cây|hoa quả) cung\b", r"\1 cúng"),
    (r"\bcung (ram|mung|via|than tai|ong tao|giao thua|phat|ong ba|gia tien)\b", r"cúng \1"),
    (r"\bthan tai\b", "thần tài"), (r"\bong tao\b", "ông táo"), (r"\bong dia\b", "ông địa"), (r"\bgiao thua\b", "giao thừa"),
    (r"\bram thang\b", "rằm tháng"), (r"\bban tho\b", "bàn thờ"), (r"\bmung 1\b", "mùng 1"),
    (r"\bnhap khau\b", "nhập khẩu"), (r"\bngoai nhap\b", "ngoại nhập"), (r"\bgia si\b", "giá sỉ"),
    (r"\b(lay|ban|mua|kho|bo) si\b", r"\1 sỉ"), (r"\bcho dau moi\b", "chợ đầu mối"), (r"\bvua trái cây\b", "vựa trái cây"),
    (r"\bgia (re|bao nhieu)\b", r"giá \1"), (r"^gia\b", "giá"), (r"\bbao nhieu\b", "bao nhiêu"), (r"\bgiá re\b", "giá rẻ"),
    (r"\bgiao hang\b", "giao hàng"), (r"\btan noi\b", "tận nơi"), (r"\btan nha\b", "tận nhà"),
    (r"\bquan (\d+)\b", r"quận \1"), (r"\bha noi\b", "hà nội"), (r"\bgo vap\b", "gò vấp"), (r"\bbinh thanh\b", "bình thạnh"),
    (r"\bthu duc\b", "thủ đức"), (r"\btan binh\b", "tân bình"), (r"\btan phu\b", "tân phú"), (r"\bphu nhuan\b", "phú nhuận"),
    (r"\bbinh tan\b", "bình tân"), (r"\bda nang\b", "đà nẵng"), (r"\bhai phong\b", "hải phòng"), (r"\bcan tho\b", "cần thơ"),
    (r"\bbien hoa\b", "biên hòa"), (r"\bvung tau\b", "vũng tàu"), (r"\bbinh duong\b", "bình dương"),
    (r"\bsinh nhat\b", "sinh nhật"), (r"\bdai tiec\b", "đãi tiệc"), (r"\btiec\b", "tiệc"),
    (r"\bcong ty\b", "công ty"), (r"\bco quan\b", "cơ quan"), (r"\bvan phong\b", "văn phòng"),
    (r"\bhoa don\b", "hóa đơn"), (r"\bnhan vien\b", "nhân viên"), (r"\btat nien\b", "tất niên"),
    (r"\bdam cuoi\b", "đám cưới"), (r"\ble cuoi\b", "lễ cưới"), (r"\bthuy anh\b", "thủy anh"), (r"\btrang bom\b", "trảng bom"),
]]


def _fruit_them_dau(t: str) -> str:
    if not (t.isascii() and re.search(r"\b(trai cay|hoa qua)\b", t)):
        return t
    for pat, rep in _FRUIT_THEM_DAU:
        t = pat.sub(rep, t)
    return t


# Chuỗi/siêu thị ĐỐI THỦ. Mỗi tên đều đã thấy trong Suggest hoặc SERP 17/09/2026:
#   Suggest (số gợi ý khác nhau chứa tên): Hoa Biển 55, Klever 41, Fuji Fruit 18, Vinfruits 9, Morning Fruit 9.
#   SERP TP.HCM (slot/180): farmersmarket.vn 16, kleverfruits 16, citifruit 13, morningfruit 9, tamfruit 5,
#   traicaytonyteo 4, traicayxanh.vn 3, ngonfruit 3, 360fruit 2, kingfoodmart 2, bachhoaxanh 2.
#   "Trái cây 141" (traicay141.vn) và "Trái cây 187" (traicay187.com, "Hệ thống cửa hàng…") có trên
#   SERP; Suggest trả "cửa hàng trái cây 141" ở 3 tên đường khác nhau → là tên chuỗi, không phải số nhà.
#   KHÔNG có nhà nhập khẩu (An Minh, Homefarm, Chánh Thu…) — họ là nguồn hàng, để nhánh Wholesale bắt.
#   "fuji" đứng tách (kiểm toán 17/09): "hoa quả sạch fuji nha trang", "hoa quả nhập khẩu fuji" (CSV), "hoa quả
#   sạch fuji thái nguyên" (ngoài mẫu) là chuỗi Fuji Fruit; chặn "táo fuji" (giống táo: "giá táo fuji nam phi").
#   KHÔNG thêm "hoa biên": seed KP "trái cây nhập khẩu hoa biên" trả 8/8 gợi ý Biên Hòa (cache 17/09).
_FRUIT_CHAIN = re.compile(
    r"(hoa biển|traicayhoabien|klever|vin ?fruits?|win fruits|fuji ?fruits?|hoa quả fuji|morning ?fruits?|"
    r"(?<!táo )\bfuji\b(?! ?(park|candy|co\b|apple))|"
    r"farmers? ?market|citi ?fruits?|\btony\b|tuti ?fruits?|go ?fresh|ngon ?fruits?|"
    r"trái cây xanh\b(?! (lá|dương|đậm|nhạt|ngọc))|traicayxanh|\bjodi\b|zen ?fruits?|360 ?fruits?|t[aâ]m ?fruits?|"
    r"vitamin house|thủy anh|thuỷ anh|phương toản|tú oanh|tôm fruits|gold fruit|f5 fruit|eus fruit|"
    r"deli ?fruit|chufruits|bảo yến|vietberry|\b(141|187)\b|"
    r"kingfood|king food|bách h(óa|oá) xanh|\bbhx\b|winmart|vinmart|co\.? ?op ?mart|coopmart|"
    r"\baeon\b|\bemart\b|\blotte\b|mm mega|big c\b|annam gourmet|sieuthiluxy|luxy\b)")

# B2B = TỔ CHỨC mua để dùng/tặng (văn phòng, công ty, sự kiện, nhà hàng, kế toán hoá đơn).
# Đo 17/09: đây là mặt trận CHẾT trên Suggest — 11/33 seed gốc của cụm Sỉ + B2B trả 0, và cả 11 đều là
# seed TỔ CHỨC mua (cho văn phòng / công ty / khách sạn / sự kiện / trường học / có hoá đơn / quà tặng
# doanh nghiệp); seed sỉ/nguồn hàng trong cụm không seed nào trả 0 (exports/trai-cay-suggest.json,
# theoMatTran goc SI_B2B). Chính vì hiếm nên bắt
# SỚM NHẤT sau tên riêng: một lần xuất hiện cũng đáng thấy, không được để Gift/Worship nuốt
# ("giỏ trái cây tặng doanh nghiệp", "trái cây cúng khai trương công ty", "trái cây cúng văn phòng mới").
# "hoá đơn": "xuất hóa đơn giỏ trái cây thuế suất bao nhiêu" = kế toán doanh nghiệp đang mua.
# ĐỊNH NGHĨA CHỦ DOANH NGHIỆP CHỐT 17/09/2026 (classifier sau af84344): B2B = TỔ CHỨC mua — công ty, văn phòng,
# nhà hàng, khách sạn, trường học, café, sự kiện/teabreak, hoá đơn doanh nghiệp. KHÔNG còn gồm:
#   · "tiệc" / "buffet" trần — tiệc gia đình ("trái cây tiệc cưới / tiệc trà / đãi tiệc / bày tiệc", CSV 17/09)
#     → nhãn Party. Tiệc của tổ chức vẫn B2B: teabreak, "tiệc/liên hoan/tất niên công ty|cơ quan" ("tất niên"
#     trần KHÔNG: "mâm ngũ quả bày trước hay sau cúng tất niên" là cúng tại nhà → Worship).
#   · "thuế" trần — "hoa quả nhập khẩu (chịu) thuế suất bao nhiêu", "…chịu thuế gtgt" là tình báo nhập khẩu /
#     quy định → Wholesale. Có "hoá đơn" thì vẫn B2B (bắt trước Wholesale).
_FRUIT_B2B = re.compile(
    r"(văn phòng|doanh nghiệp|\bcho (công ty|nhân viên|đối tác|khách hàng)\b|công ty mới|"
    r"khai trương công ty|công ty\s*$|\bcty\b|teabreak|tea break|"
    # tiệc CỦA TỔ CHỨC (soát độc lập 17/09): cho phép 0–3 chữ chen giữa ("tiệc year end công ty quận 7"),
    # và các loại tiệc gần như luôn của công ty: tất niên/tân niên/year end/gala/tri ân/tổng kết/nhân viên.
    # "cúng tất niên" (không có chữ tiệc) vẫn là Worship.
    # "gala" CHỈ khi là tiệc: "giá táo gala new zealand" (CSV 17/09) là GIỐNG táo Gala → Pricing.
    r"(tiệc|liên hoan|tất niên)( \S+){0,3} (công ty|cty|cơ quan)|tiệc tất niên|tân niên|year ?end|tiệc gala|gala dinner|"
    r"tri ân|tổng kết|nhân viên|"
    r"hội nghị|hội thảo|sự kiện|\bevent\b|"
    r"nhà hàng|khách sạn|\bcafe\b|cà phê|canteen|căn tin|trường học|trường (mầm non|mẫu giáo)|bếp ăn|horeca|"
    # VAT chỉ là tổ chức mua khi đòi XUẤT hoá đơn; "hoa quả nhập khẩu vat bao nhiêu" là hỏi thuế → Wholesale.
    r"h(óa|oá) đơn|xuất vat|có vat)")

# Wholesale = mua để BÁN LẠI / nguồn hàng: sỉ, vựa, kho, chợ đầu mối, nhà nhập khẩu, nhà cung cấp.
# Tách khỏi B2B vì là mặt trận khác hẳn và CÒN SỐNG trên Suggest: "giá trái cây chợ đầu mối thủ đức
# hôm nay" (9 seed trả về), "trái cây nhập khẩu giá sỉ tphcm" (10), "kho sỉ trái cây nhập khẩu sg".
# Gộp chung thì nhãn B2B sẽ toàn là sỉ và chủ DN đọc nhầm thành "văn phòng có nhu cầu".
_FRUIT_WHOLESALE = re.compile(
    r"(\bsỉ\b|bỏ mối|tìm mối|\bvựa\b|\bkho\b|tổng kho|chợ đầu mối|đầu mối|chợ sỉ|bình điền|"
    # "cung cấp" chỉ khi là cung ứng HÀNG — không bắt nghĩa dinh dưỡng "trái cây cung cấp vitamin c",
    # "trái cây cung cấp chất gì" (Suggest ngoài mẫu 17/09). 19 dòng "cung cấp" của CSV 17/09 giữ nguyên nhãn.
    r"chợ thủ đức|mỹ hiệp|nhà cung cấp|\bcung cấp (trái cây|hoa quả|giỏ|sỉ)|(đơn vị|công ty|nơi|chỗ) cung cấp|"
    r"nguồn hàng|lấy hàng|nhập hàng|"
    r"công ty (tnhh )?(xuất )?nhập khẩu|công ty (tnhh )?trái cây|nhà nhập khẩu|đại lý|"
    r"nông sản|tại vườn|thương lái|"
    # nhà nhập khẩu lộ ra trong Suggest 17/09 ("công ty nhập khẩu trái cây an minh / homefarm / biovegi…")
    r"\ban minh\b|homefarm|biovegi|chánh thu|phương sinh|sức sống xanh|phong gia|\batf\b|farm fruits|"
    r"\bgia huy\b|\bcevis\b|"
    # Tình báo NHẬP KHẨU / QUY ĐỊNH (chủ DN chốt 17/09/2026, trước đây nằm trong B2B): thuế suất, thuế GTGT,
    # hải quan, mã HS — người hỏi là bên nhập/bán hàng, không phải tổ chức mua để dùng.
    # "miễn thuế" (cửa hàng miễn thuế sân bay) không phải tình báo nhập khẩu.
    r"(?<!miễn )thuế|\bgtgt\b|\bvat\b|hải quan|mã hs\b|\bhs code\b)")

# Gift = giỏ/hộp/quà/biếu/viếng — mặt trận QUA: sâu nhất và gần như toàn ý định giao dịch
# (seed gốc TB 7,6 gợi ý, 0 seed rỗng; alphabet soup TB 8,3 — cao nhất). Bắt TRƯỚC Worship vì
# "giỏ trái cây cúng giỗ / đám tang / viếng 500k" là người đi MUA giỏ mang đi, không phải hỏi cách cúng;
# và TRƯỚC Pricing/Delivery vì thang giá "giỏ trái cây 200k…5tr" và "giỏ trái cây giao tận nơi"
# là thuộc tính của sản phẩm giỏ.
_FRUIT_GIFT = re.compile(
    r"(giỏ|lẵng|hộp quà|hộp trái cây|hộp hoa quả|\bquà\b|biếu|\btặng\b|\bset (trái cây|hoa quả|quà)|"
    r"kính viếng|\bviếng\b|phúng điếu|chia buồn|thăm bệnh|thăm người|fruit basket|"
    # Dịp mang trái cây ĐI (tang, dạm ngõ/ăn hỏi) dù không có chữ "giỏ": "tháp trái cây đám tang",
    # "mâm trái cây dạm ngõ" (Suggest ngoài mẫu 17/09), "mâm ngũ quả lễ ăn hỏi" (CSV). Có "cúng" thì để
    # Worship ("trái cây cúng đám tang", "đám tang cúng trái cây gì" là hỏi cách cúng).
    r"^(?!.*cúng).*(đám tang|tang lễ|dạm ngõ|ăn hỏi|lễ hỏi))")

# Worship = cúng / mâm ngũ quả / bàn thờ / thần tài / rằm, mùng 1 — mặt trận CUNG, thiên về THÔNG TIN
# ("gồm những gì", "đặt bên nào") nhưng có cả mua ("mua trái cây cúng rằm"). Nối thẳng mùa cúng
# rằm/mùng 1 của Mộc An. Người miền Nam gõ "rằm tháng 7 / cô hồn", KHÔNG gõ "vu lan"
# ("trái cây cúng vu lan" = 0 gợi ý).
_FRUIT_WORSHIP = re.compile(
    r"(cúng|ngũ quả|dâng lễ|dâng hương|thắp hương|bàn thờ|ban thờ|thần tài|ông địa|thổ địa|ông táo|"
    r"ông công|gia tiên|cô hồn|giao thừa|\bchưng\b|\brằm\b|mùng 1\b|mồng 1\b|\bvía\b|đầy tháng|thôi nôi|"
    r"phật(?! thủ)|chùa(?! láng| bộc)|bà chúa xứ|quan âm|trả lễ|động thổ|nhập trạch)")

# KHÔNG có nhãn Occasion chung (đã thử và bỏ, 17/09/2026): chỉ 6/3.607 gợi ý giữ lại mang dịp mà KHÔNG
# kèm giỏ/quà hoặc cúng ("giá trái cây tết") — không đủ thành mặt trận. Dịp thật nằm TRONG Gift
# (giỗ/tang 61 gợi ý, Tết 46, khai trương 33…) và Worship (thần tài 26, rằm/mùng 1 22).
#
# Party = TIỆC / đãi khách của gia đình (chủ doanh nghiệp chốt 17/09/2026, tách khỏi B2B): "trái cây tiệc cưới",
# "trái cây tiệc trà", "trái cây đãi tiệc", "dĩa trái cây đãi tiệc", "trái cây bày tiệc", "trái cây tiệc buffet"
# (CSV 17/09 — trước đây các dòng này bị tính là tổ chức mua). Cùng radar "Quà & dịp" với Gift/Worship ở app.
# Đứng SAU B2B (tiệc công ty/teabreak vẫn là tổ chức), SAU Gift ("giỏ trái cây sinh nhật" là mua giỏ) và
# Worship, TRƯỚC Delivery ("đặt trái cây tiệc giao tận nơi" — ý định chính là tiệc).
_FRUIT_PARTY = re.compile(
    r"(tiệc|buffet|đãi khách|liên hoan|sinh nhật|đám cưới|lễ cưới|\bparty\b)")

# Delivery = giao/ship/online/app. Mặt trận ONLINE MỎNG (seed gốc TB 5,2; alphabet 11/31 rỗng).
# "giao" dễ dính: "giao thừa" (Worship đã bắt trước) và địa danh "Ngãi Giao" → loại bằng lookaround.
_FRUIT_DELIVERY = re.compile(
    r"((?<!ngãi )(?<!ngoại )(?<!thuận )\bgiao\b(?! thừa)|\bship\b|tận nơi|tận nhà|online|đặt hàng|đặt mua|\bapp\b|hỏa tốc|"
    r"hoả tốc|giao nhanh|\b24h\b|\b24 7\b|shopee|lazada|\btiki\b|grab|delivery|bưu điện|viettel post|"
    r"giao hàng tiết kiệm|đi tỉnh|đi xa)")

# Store = tìm NƠI MUA vật lý: cửa hàng/shop/tiệm/sạp/siêu thị + "mua ở đâu" + mẫu gần-đây của Maps
# ("gần đây trong vòng 800m", "hiện đang mở" — 116 gợi ý tự thêm "gần đây"). Cụm cửa hàng + quận
# chiếm gần hết top gợi ý lặp nhiều nhất ("cửa hàng trái cây nhập khẩu gò vấp" 11 seed trả về).
# Đặt SAU Delivery để "shop trái cây online" là Delivery.
_FRUIT_STORE = re.compile(
    r"(cửa hàng|\bshop\b|\btiệm\b|\bsạp\b|siêu thị|chuỗi|\bstore\b|\bquán\b|^mua (trái cây|hoa quả)|"
    r"ở đâu|\bchỗ (bán|mua)\b|nơi bán|địa chỉ|gần đây|gần nhất|gần tôi|quanh đây|hiện đang mở|trong vòng)")

# Pricing — "giá" nhưng KHÔNG phải "đánh giá" (review) hay địa danh "Rạch Giá".
_FRUIT_PRICING = re.compile(
    r"((?<!đánh )(?<!rạch )\bgiá\b(?! trị)|bao nhi[êề]u(?! calo)|\brẻ\b|khuyến mãi|giảm giá|\bsale\b|đồng giá|"
    r"\d+ ?k\b|\d+ ?(tr|triệu)\b|\d+tr\d|chi phí|bình dân)")

# Trust = người mua lo AN TOÀN / THẬT GIẢ / tem mã: "trái cây trung quốc có độc không",
# "táo nhập khẩu có an toàn không", "cherry chile có phải của trung quốc không", "mã số 3/4", "klever fruit phốt".
# KHÔNG gồm "bảo quản / để được bao lâu" trần (kiểm toán 17/09): "cách bảo quản trái cây trong tủ lạnh" (7/10
# gợi ý của seed đó, ngoài mẫu) và "táo nhập khẩu để được bao lâu" (CSV) là hỏi CÁCH DÙNG, không phải lo an
# toàn. Giữ "chất/thuốc bảo quản". Thêm "có hại/gây hại/ngộ độc": "nho mẫu đơn trung quốc ăn có hại không".
_FRUIT_TRUST = re.compile(
    r"(an toàn|có độc|độc hại|có hại|gây hại|ngộ độc|hóa chất|hoá chất|chất bảo quản|thuốc bảo quản|ngâm thuốc|tẩm|"
    r"chính ngạch|kiểm dịch|mã số|\bmã\b|đầu số|\bđầu \d\b|\btem\b|dán tem|mã plu|đánh giá|review|"
    r"uy tín|phốt|lừa đảo|hàng giả|thật hay giả|có tốt không|có ngon không|ngọt không|của nước nào|"
    r"của ai|có phải|chính hãng|nguồn gốc|xuất xứ)")

# Health = dinh dưỡng / bệnh lý. Tín hiệu NỘI DUNG, không phải ý định mua (mặt trận SUCKHOE: 10/10 seed
# đủ 10 gợi ý nhưng không có gợi ý nào mang ý định giao dịch) — giữ để làm SEO, xếp sau mọi nhánh ra tiền.
# "cho bé" sau dịp lễ là mâm cỗ/tiệc, không phải dinh dưỡng: "mâm trái cây trung thu cho bé" (ngoài mẫu),
# "trái cây sinh nhật cho bé" (CSV) → nay là Party (nhãn tiệc thêm 17/09, xét trước Health).
_FRUIT_HEALTH = re.compile(
    r"(giảm cân|bà bầu|mẹ bầu|\bbầu\b|sau sinh|thai kỳ|tiểu đường|huyết áp|\bcalo\b|vitamin|dinh dưỡng|"
    r"sức kh[oỏ]e|sức khoẻ|tốt cho|ít đường|nhiều đường|ăn kiêng|\bkali\b|bổ máu|"
    r"(?<!trung thu )(?<!sinh nhật )cho bé|ăn dặm|trẻ em|"
    r"dạ dày|\bgout\b|suy thận|buổi tối|detox|đẹp da|táo bón|protein|mát cho cơ thể|nóng trong|sinh mổ)")

# Product = tên quả/giống cụ thể. Tên MỘT CHỮ dễ đồng âm (đo 17/09: "giá lê"→"giá lên thổ cư",
# "giá cam"→camera/camry, "giá bơ"→bơm ga, "giá vải"→vải áo dài, "đào"→đào tạo/bitcoin) nên chỉ
# nhận khi có ranh giới từ; các cụm đồng âm đã thấy bị fruit_is_negative loại trước.
_FRUIT_PRODUCT = re.compile(
    r"\b(cắt sẵn|gọt sẵn|"  # dạng hàng: "trái cây cắt sẵn" 10 gợi ý, 5 quận tự lộ (Morning Fruit, Vietberry, eFruit)
    r"táo|nho|cherry|anh đào|kiwi|cam(?! ranh)|quýt|mận|đào|lựu|dâu tây|việt quất|blueberry|mâm xôi|"
    r"(?:(?<=quả )|(?<=trái )|(?<=giá )|(?<=mua ))lê|lê (hàn|nam phi|úc|trung quốc|nâu|xanh|sữa|nhập)|"
    r"phúc bồn tử|dưa lưới|dưa hấu|dưa lê|bơ|hồng giòn|hồng treo gió|hồng xiêm|hồng táo|(?<!đồng )xoài|sầu riêng|"
    r"măng cụt|bưởi|thanh long|chôm chôm|vải thiều|nhãn|chuối|ổi|mít|dứa|mãng cầu|dừa|"
    r"chanh dây|chanh|chà là|vú sữa|khế|thanh trà|bòn bon|sấu|phật thủ|lựu đỏ|"
    r"envy|rockit|gala|zespri|shine muscat|mẫu đơn|musang ?king|musaking|ri6|monthong|hòa lộc|hoà lộc|"
    r"da xanh|sấy|sấy dẻo|sấy khô|mứt|hạt dẻ|óc chó|macca|hạnh nhân)\b")

# Local = địa danh (không kèm ý định nào ở trên). HCM trước, rồi tỉnh/thành khác để đo độ lệch vùng:
# "hoa quả" nghiêng Bắc (Google tự thêm HN 152 + tỉnh Bắc 91 vs HCM 18), "trái cây" nghiêng Nam
# (HCM 535 + tỉnh Nam 299). Bình Dương/Thủ Dầu Một/Vũng Tàu nay thuộc TP.HCM (sáp nhập 2025).
_FRUIT_LOCAL = re.compile(
    r"(\bquận\b|\bq\d+\b|\bphường\b|\bhuyện\b|\bđường\b|\btp\b|thành phố|\btỉnh\b|"
    r"gò vấp|tân bình|tân phú|bình thạnh|phú nhuận|bình tân|thủ đức|hóc môn|củ chi|nhà bè|bình chánh|"
    r"cần giờ|tphcm|tp hcm|\bhcm\b|hồ chí minh|ho chi minh|sài gòn|saigon|\bsg\b|thảo điền|phú mỹ hưng|"
    r"bình dương|thủ dầu một|thủ dầu 1|dĩ an|thuận an|tân uyên|bến cát|vũng tàu|bà rịa|phú mỹ|"
    r"hà nội|\bhn\b|cầu giấy|hà đông|long biên|đống đa|mỹ đình|hải phòng|đà nẵng|cần thơ|"
    r"bi[eê]n h[oò]a|biên hoà|đồng nai|long khánh|long thành|nha trang|khánh hòa|\bhuế\b|quy nhơn|"
    r"đà lạt|bảo lộc|buôn ma thuột|\bbmt\b|pleiku|gia lai|quảng ngãi|quảng nam|hội an|tây ninh|"
    r"long an|mỹ tho|tiền giang|bến tre|vĩnh long|trà vinh|sóc trăng|an giang|long xuyên|châu đốc|"
    r"kiên giang|rạch giá|phú quốc|cà mau|bạc liêu|đồng tháp|cao lãnh|sa đéc|bình phước|đồng xoài|"
    r"miền tây|miền nam|miền bắc|miền trung|thanh hóa|thanh hoá|nghệ an|\bvinh\b|hà tĩnh|quảng bình|"
    r"quảng trị|bình định|phú yên|ninh thuận|bình thuận|phan thiết|lâm đồng|đắk lắk|daklak|"
    r"quảng ninh|hạ long|bắc ninh|hải dương|nam định|thái bình|vĩnh phúc|vĩnh yên|phú thọ|việt trì|"
    r"thái nguyên|bắc giang|hưng yên|ninh bình|hà nam|lào cai|sơn la|lạng sơn|yên bái|ngãi giao|thuận giao|cam ranh|lái thiêu|chùa láng|chùa bộc|"
    # tên đường/khu Google tự thêm vào gợi ý 17/09 (HCM rồi HN) — người đang tìm cửa hàng theo địa chỉ
    r"lê văn sỹ|lê quang định|lê văn việt|lê thánh tôn|an dương vương|nguyễn tri phương|nguyễn văn cừ|"
    r"nguyễn đình chiểu|nguyễn thái học|nguyễn thiện thuật|trần xuân soạn|trần não|bàu cát|mã lò|"
    r"quang trung|cách mạng tháng 8|\bcmt8\b|võ thị sáu|hai bà trưng|hồng bàng|lý thái tổ|chợ rẫy|"
    r"bà chiểu|chợ lớn|vinhomes|landmark|tô hiệu|viện 108|trần duy hưng|xuân la|mễ trì|ocean park|"
    r"ngoại giao đoàn|phố huế|kim ngưu|linh đàm|đội cấn|cầu diễn|minh khai)")

# Imported = nhập khẩu / ngoại nhập / tên nước xuất xứ, không kèm ý định cụ thể hơn — lõi của 21 từ khóa
# Keyword Planner người dùng cung cấp ("trái cây nhập khẩu" 14.800/tháng — số KP, KHÔNG phải số mình đo).
_FRUIT_IMPORTED = re.compile(
    r"(nhập khẩu|ngoại nhập|\bnhập\b(?! trạch)|nhap khau|ngoai nhap|imported|"
    r"\bmỹ\b|\búc\b|new zealand|\bnz\b|(?<!sinh )nhật|hàn quốc|\bhàn\b|chile|nam phi|trung quốc|thái lan|\bthái\b|"
    r"đài loan|peru|canada|\bpháp\b|ai cập|châu âu)")

# ĐUÔI MAPS "trái cây nhập khẩu <X>" (kiểm toán 17/09/2026). Local là danh sách trắng đóng nên mọi địa danh
# chưa có trong _FRUIT_LOCAL rơi hết vào Imported (lõi): trên CSV 17/09 có 221 dòng Imported mà phần lớn là
# phố/quận HN, thị xã tỉnh ("hoa quả nhập khẩu bà triệu", "…đông anh", "trái cây nhập khẩu xuân lộc", "…kon
# tum") hoặc tên cửa hàng ("trái cây nhập khẩu fruitland 77", "…juli fruits"). Theo đúng định nghĩa đã công bố
# (Local = có địa danh; Store = tìm nơi mua trực tiếp): phần dư KHÔNG phải bổ ngữ chung → Local, riêng phần dư
# mang dáng tên shop (fruit/food/farm/fresh, hoặc chỉ là một con số như "…247", "…365" — cùng kiểu chuỗi
# "Trái cây 141/187") → Store. Bổ ngữ chung (giữ Imported): tính từ, màu, mùa, tên nước, câu hỏi kiến thức, và
# chữ cái gõ dở ("…nhập kh", "…nhập khẩu f"). GIỚI HẠN đã biết: tên shop tiếng Việt/không dấu không có dấu hiệu
# trên ("…kim tiến phát", "…joygreen", "…design by nina") không tách được khỏi địa danh bằng regex → vào Local.
# Đo lại CSV 17/09 sau toàn bộ bản sửa kiểm toán: Imported 221 → 77 (sang Local 116, Store 26, Chain 2 —
# Chain do "fuji" tách và "hoa qua nhap khau thuy anh" sau khi thêm dấu).
_FRUIT_IMPORTED_DUOI = re.compile(
    r"(?:các loại |tên các loại )?(?:trái cây|hoa quả)(?: tươi| sạch)? (?:nhập khẩu|ngoại nhập)(?: tươi)? (.+)")
_FRUIT_IMPORTED_CHUNG = re.compile(
    r"(?:(?:ngon|cao cấp|tuyển chọn|hảo hạng|đặc biệt|tươi|sạch|xịn|ngọt|luôn|organic|hữu cơ|chất lượng|theo mùa|mùa này|giá tốt|chính hãng|"
    r"uy tín|linh tinh|xanh|đỏ|vàng|tím|màu|mỹ|úc|new zealand|nz|hàn quốc|nhật|nhật bản|thái lan|trung quốc|"
    r"chile|nam phi|canada|peru|đài loan|pháp|vào việt nam|nhập vào việt nam|từ|loại nào|là gì|gồm những gì|"
    r"fruits?|kh|[a-zđ0-9])(?: |$))+")
_FRUIT_TEN_SHOP = re.compile(r"(fruit|food|farm|fresh|^\d{2,}$)")

_FRUIT_CORE = re.compile(r"(trái cây|hoa quả|trai cay|hoa qua|hoa quà|\bfruits?\b|\btrái\b|\bquả\b)")

# NGỮ CẢNH TRÁI CÂY — cửa chặn trước mọi nhánh ý định. Gợi ý không có chữ trái cây/quả, tên quả hay
# "cúng" là rác đồng âm lọt lưới (đo 17/09: "giao hàng hoả tốc hà nội quảng ninh" từ seed "giao hoa quả",
# "gừng hồng mua ở đâu" từ "hồng mua ở đâu") → trả Other thay vì gán nhầm Store/Delivery. Nhờ vậy % Other
# chính là thước đo nhiễu còn sót, theo dõi được theo ngày.
_FRUIT_CONTEXT = re.compile(r"(trái cây|hoa quả|trai cay|hoa qua|hoa quà|\bfruits?\b|\btrái\b|\bquả\b|cúng)")


def classify_fruit(s: str) -> str:
    """Trái cây (key `fruit`). Mô hình kinh doanh CHƯA chốt → nhãn phải tách được từng MẶT TRẬN
    để chủ doanh nghiệp chọn sau: bán lẻ nhập khẩu (Store/Imported), giỏ quà (Gift), cúng (Worship),
    giao online (Delivery), tổ chức mua (B2B), nguồn sỉ (Wholesale), mặt hàng (Product),
    chuỗi đối thủ (Chain).

    Thứ tự nhánh từ HẸP & ra tiền → RỘNG (nhánh trước thắng):
      [chuỗi ASCII có "trai cay|hoa qua" → thêm dấu cụm cố định, xem _FRUIT_THEM_DAU]
      Brand → Chain → [không có ngữ cảnh trái cây → Other] → B2B → Wholesale → Gift → Worship → Party
      → Delivery → Store → Pricing → Health → Trust → Product → Local → Imported (đuôi Maps → Local/Store) → Core
      · Brand/Chain: tên riêng là tín hiệu hẹp nhất — người gõ đã chọn nơi mua. Chain đo thị phần nhu cầu.
        Đứng TRƯỚC cửa chặn ngữ cảnh vì "klever fruit lê văn sỹ", "hoa biển gò vấp" không có chữ "trái cây".
      · B2B trước mọi thứ còn lại: hiếm nhất (đo 17/09 gần như chết) nên không được để nhánh khác nuốt.
      · Wholesale trước Gift/Pricing: "giá trái cây chợ đầu mối thủ đức hôm nay" là giá SỈ, không phải khảo giá lẻ.
      · Gift trước Worship: "giỏ trái cây cúng giỗ" = mua giỏ mang đi (giao dịch); Worship thiên về hỏi cách cúng.
      · Delivery trước Store: "shop trái cây online" là kênh online.
      · Store trước Pricing/Local: "cửa hàng trái cây nhập khẩu gò vấp giá rẻ" là tìm chỗ mua.
      · Pricing trước Product: "giá cherry mỹ" là ý định khảo giá; mặt hàng tách lại được từ chuỗi.
      · Health trước Trust (kiểm toán 17/09): "bà bầu ăn nho có tốt không" (4/10 gợi ý của seed "bà bầu ăn
        nho", ngoài mẫu) là câu hỏi dinh dưỡng; "có tốt không" nằm trong Trust nên trước đây bị bắt nhầm.
        0 dòng CSV 17/09 đổi nhãn ("trái cây trung quốc có tốt không" vẫn Trust).
      · Product trước Local/Imported: "cherry nhập khẩu tphcm" cụ thể hơn "nhập khẩu".
      · Local trước Imported: "trái cây nhập khẩu gò vấp" — địa bàn là thông tin hành động được
        (mở điểm/chạy ads theo quận); gần như MỌI seed đều chứa "nhập khẩu" nên Imported để làm lưới đỡ.

    17 nhãn: Brand, Chain, B2B, Wholesale, Gift, Worship, Party, Delivery, Store, Pricing, Trust,
    Health, Product, Local, Imported, Core, Other. (Party thêm 17/09/2026 khi chủ DN chốt định nghĩa B2B.)"""
    t = _fruit_them_dau(_fruit_norm(s))
    # Brand KHÔNG nhận "đồng khởi" trần: Đồng Khởi là tên đường dày cửa hàng (Q1, Biên Hòa, Bến Tre) —
    # "cửa hàng trái cây đồng khởi quận 1" là tìm cửa hàng, không phải tìm Đồng Khởi Catering.
    # Có dạng không dấu như _research/map-pack.mjs. CSV 17/09 có 0 gợi ý chứa các tên này.
    if re.search(r"(đồng khởi catering|dong khoi catering|thành gia định|thanh gia dinh|mộc an|moc an)", t):
        return "Brand"
    if _FRUIT_CHAIN.search(t):
        return "Chain"
    if not (_FRUIT_CONTEXT.search(t) or _FRUIT_PRODUCT.search(t)):
        return "Other"
    if _FRUIT_B2B.search(t):
        return "B2B"
    if _FRUIT_WHOLESALE.search(t):
        return "Wholesale"
    if _FRUIT_GIFT.search(t):
        return "Gift"
    if _FRUIT_WORSHIP.search(t):
        return "Worship"
    if _FRUIT_PARTY.search(t):
        return "Party"
    if _FRUIT_DELIVERY.search(t):
        return "Delivery"
    if _FRUIT_STORE.search(t):
        return "Store"
    if _FRUIT_PRICING.search(t):
        return "Pricing"
    if _FRUIT_HEALTH.search(t):
        return "Health"
    if _FRUIT_TRUST.search(t):
        return "Trust"
    if _FRUIT_PRODUCT.search(t):
        return "Product"
    if _FRUIT_LOCAL.search(t):
        return "Local"
    if _FRUIT_IMPORTED.search(t):
        duoi = _FRUIT_IMPORTED_DUOI.fullmatch(t)
        if duoi and not _FRUIT_IMPORTED_CHUNG.fullmatch(duoi.group(1)):
            return "Store" if _FRUIT_TEN_SHOP.search(duoi.group(1)) else "Local"
        # dạng Maps ngược "<tên shop> trái cây nhập khẩu": "jenny fruit trái cây nhập khẩu" (CSV 17/09)
        dau = re.fullmatch(r"(.+) (?:trái cây|hoa quả) (?:nhập khẩu|ngoại nhập)", t)
        if dau and re.search(r"(fruit|food|farm|fresh)", dau.group(1)):
            return "Store"
        return "Imported"
    if _FRUIT_CORE.search(t):
        return "Core"
    return "Other"


_FRUIT_NEGATIVE = re.compile(
    # 1) GAME — "bảng giá trái cây" / "shop trái cây" / "giao trái cây" bị game chiếm:
    #    "giá trái cây grow a garden", "shop trái cây blox fruit", "thả trái cây shopee", "robo trái cây"
    r"(blox|grow a garden|play together|roblox|one piece|trái ác quỷ|fruit ninja|\bgame\b|trò chơi|"
    r"thả trái cây|chém trái cây|robo trái cây|nối trái cây|hoa quả nổi giận|\bacc\b|"
    # 2) GIÁO DỤC / HỌC TIẾNG / VẼ — "giao"→"giáo" khi bỏ dấu: "giáo án trái cây trong vườn", "giáo xứ…";
    #    "mâm ngũ quả tiếng anh là gì", "vẽ mâm ngũ quả lớp 1", "giỏ trái cây png", "hoa biển lyrics"
    #    "mầm non" trừ "trường mầm non" (bếp ăn trường = tín hiệu B2B hiếm, kiểm toán 17/09)
    r"giáo án|giáo an\b|giáo sư|giáo xứ|giáo trình|bài giảng|(?<!trường )mầm non|\blớp \d|thuyết trình|\bvè\b|"
    r"tô màu|\bvẽ\b|hình vẽ|\bpng\b|vector|clipart|\bnặn\b|dự thi|sketchup|pinterest|lyrics|"
    r"tiếng (anh|trung|nhật|hàn|pháp)|in english|\benglish\b|what is|(?<!quay )\bphim\b|\btruyện\b|"
    # 3) BÀI TOÁN TIỂU HỌC — "một cửa hàng hoa quả có 120kg cam", "mẹ vào cửa hàng trái cây mua 3 kg",
    #    "một đại lý nhập khẩu trái cây tươi"
    r"^(một|1) (cửa hàng|đại lý|shop|người bán)|^(mẹ|bà|bác|cô|chú)( \w+)? (vào|ra|mở) (một )?(cửa hàng|shop)|"
    #    rổ/thùng chỉ khi có động từ đề toán — "1 thùng táo envy bao nhiêu kg" là khảo giá mua theo thùng
    #    (seed ngoài mẫu "thùng táo" 17/09 trả 10 gợi ý thật: "thùng táo envy 9kg", "…bao nhiêu tiền")
    r"(bán được|nhập về|lúc đầu có) \d+|dự định đóng gói|(nhập về|có|chở|bán) \d+ ?(rổ|thùng) (cam|xoài|táo)|\d+ quả gồm|"
    # 4) KHÁC NGÀNH / ĐỒ UỐNG / ĐỒNG ÂM — "rượu trái cây hàn quốc", "kẹo trái cây thái lan", "máy ép trái cây",
    #    "tiệm trà trái cây", "sữa trái cây kun", "hoa quả dầm thái phiên", "ớt trái cây";
    #    đồng âm tên quả: "giá lên thổ cư", "giả tạo", "camera/camry", "cấm nhập khẩu", "bơm ga",
    #    "vải lụa satin", "hoa hồng/muối hồng nhập khẩu", "đào tạo", "giá đào 1 bitcoin", "pha lê/cờ lê",
    #    "lựu đạn", "xi đánh giày kiwi", "rong nho", "bơ lạt", "bò nhập khẩu", "táo mỹ iphone";
    #    tham quan vườn: "giá vé vườn trái cây lái thiêu"; hành chính "biên hòa đồng nai sau sáp nhập"
    #    soát bằng mắt lượt 2: "giá trái cây icool" (đĩa trái cây karaoke), "trà măng cụt", "đồng hồ quả
    #    quýt", "giỏ trái cây anime", "táo mỹ store" (chuỗi iPhone), "trái cây nghiền hipp" (đồ ăn dặm),
    #    "giá cam bình resort", "saigon dưa lưới" (thuốc lá), "kết quả nam phi cộng hòa séc"
    # rượu/vang KHÔNG lọc khi đi kèm giỏ: "giỏ trái cây kèm rượu" là giỏ quà Tết thật (Gift)
    r"^(?!.*giỏ).*(rượu|\bvang\b)|\bbia\b|soju|(?<!nho )(?<!bánh )kẹo|\bkem\b|"
    #    kiểm toán 17/09 (CSV): "trái cây siro" (đồ ngâm siro), "trái cây si ăn được không" (quả cây si),
    #    "vitamin trái cây thái lan" (kẹo vitamin). KHÔNG lọc "ưu đàm": có "cửa hàng hoa quả ưu đàm" (tên shop);
    #    KHÔNG lọc "trái cây si" trần (gõ thiếu dấu "sỉ" hay cây si — mơ hồ).
    #    Giữ lọc (tranh luận được, ghi lý do): "trái cây tô" = quán tráng miệng (F&B, không phải mua trái cây);
    #    "long nhãn/nhãn nhục" = dược liệu/chè sấy, khác "trái cây sấy" dùng cho giỏ Tết; "công giáo" chặn
    #    "giáo" đồng âm (giao→giáo) — mất "đạo công giáo có cúng trái cây không" (1 dòng, hỏi kiến thức).
    r"(trà|sữa|nước|thạch) (trái cây|hoa quả)|\bsiro\b|trái cây si ăn|^vitamin (trái cây|hoa quả)|"
    r"tiệm trà|trái cây tô\b|icool|karaoke|"
    r"\b(trà|siro|bột) (măng cụt|việt quất|dâu tây|dâu|đào|xoài|vải|chanh|bưởi|táo|kiwi|cam|quýt|lựu)\b|"
    r"sữa (oggi|nuvi)|nước uống sữa|bánh (nhãn|mì|quy|đậu xanh|sữa)|(saigon|sài gòn) (dưa lưới|đào)|"
    r"bergamot|kakadu|đồng hồ|anime|manga|romand|cộng hòa séc|kết quả|mỹ tâm|mỹ khánh|hầm rút|"
    #    "táo mỹ <số>" = chuỗi iPhone ("táo mỹ 102") nhưng KHÔNG nuốt khảo giá "táo mỹ 1 kg"; "bà" chỉ Bà Tô/Bà Rịa
    r"fuji fruits? (park|candy)|mt\.? ?fuji|táo mỹ (store|\d+\b(?! ?(kg|k|g|gr|trái|quả|thùng))|bà (tô|rịa)|dĩ an|vũng tàu)|"
    r"nước ép|sinh tố|smoothie|sữa chua|sữa kun|nutifood|vinamilk|oishi|nutri boost|phomai|"
    r"máy (ép|xay|sấy)|thuốc la\b|thuốc lá|giấm|ớt trái cây|(hoa quả|trái cây) dầm|"
    r"giá lên|thổ cư|giả tạo|camera|camry|camping|\bcám\b|\bcấm\b|bơm|"
    r"vải (áo|lụa|kate|cotton|tencel|gấm|nỉ|canvas|vụn|microfiber|thun|các loại)|mua vải|"
    r"hoa hồng|muối hồng|hồng trà|hồng sâm|đào tạo|bitcoin|\bbtc\b|bể phốt|cờ lê|pha lê|phi lê|"
    r"lựu đạn|xi đánh giày|dao kiwi|rong nho|đường nho|"
    r"bơ (lạt|nhạt|mặn|ghee|thực vật|đậu phộng|lạc|cacao|pháp)|dầu bơ|bắp rang bơ|bánh quy bơ|"
    r"\bbò nhập khẩu|xoan đào|nhựa đào|hoa đào|mẫu đơn xin|sữa long thành|\bmì thanh long|"
    r"xôi xoài|gỏi gà|nếp cẩm|cam thảo|iphone|apple|nhãn hiệu|long nhãn|nhãn nhục|"
    r"(vỏ|cùi|hoa|hạt) (bưởi|quýt)|nước hoa|perfume|vé vườn|vườn trái cây|giá vé|resort|hotel|homestay|"
    r"(trái cây|hoa quả) nghiền|hipp\b|babybio|công giáo|"
    r"sáp nhập|ở tỉnh nào|có gì chơi|new city|hoa quảng (ngãi|trị|bình|nam|ninh)|"
    # 5) TÊN NƯỚC NGOÀI TRÙNG — true fruits (smoothie Đức), sunfruit (mỹ phẩm/Peru), koi fresh fruits & tea
    #    (Calgary), "kiwi new zealand bird/slang", "morning fruits to eat", "fuji fruits co ltd"
    r"true ?fruits|sun ?fruits?|koi fresh|ellis brooklyn|lollies|gmbh|deckel|vermisst|rewe|kritik|"
    r"aufsätze|\bpreis\b|centre st|can eat|to eat|fruit picking|persimmon|fruits? (salad|juice)|yamanashi|"
    r"\bmeaning\b|\bslang\b|\bbird\b|\bpeople\b|\bperson\b|\bflag\b|co ltd|company limited|\bltd\b|"
    # 6) VIỆC LÀM / MỞ SHOP / VẬT TƯ — người BÁN, không phải người mua: "klever fruit tuyển dụng",
    #    "mở cửa hàng trái cây cần những gì", "thiết kế cửa hàng", "xốp bọc trái cây", "màng co"
    #    Không nuốt nhu cầu MUA (kiểm toán 17/09): "tuyển chọn" (từ quảng cáo hàng cao cấp), "đối tác kinh
    #    doanh" (quà đối tác), "thiết kế theo yêu cầu" (giỏ quà), "shop bán trái cây online" (CSV — người mua
    #    tìm shop → Delivery). "cách bảo quản trái cây tươi lâu để bán" (ngoài mẫu) là phía người bán.
    r"tuyển dụng|\btuyển\b(?! chọn)|việc làm|\blương\b|mở (cửa hàng|shop|tiệm|sạp|vựa)|(?<!đối tác )kinh doanh|nhượng quyền|"
    r"\bvốn\b|thiết kế (cửa hàng|shop|tiệm|sạp|quầy|kệ|logo|biển|bảng)|set ?up cửa hàng|\bdecor\b|decal|"
    r"biển (quảng cáo|hiệu)|bảng hiệu|\blogo\b|"
    r"\bkệ\b|thùng xốp|xốp bọc|túi giấy|túi đựng|màng co|giỏ đựng|khay đựng|"
    r"(?<!shop )(?<!cửa hàng )(?<!nơi )(?<!chỗ )bán (trái cây|hoa quả|nước ép)( \S+){0,2} online|mua bán trái cây|"
    r"cách bán|để bán\b|phần mềm bán|khóa học|"
    r"\bxe (trái cây|hoa quả)|\bnạo\b|bài toán|"
    # 10) TỰ LÀM / TRANG TRÍ — người tự làm giỏ, tỉa, bày; không phải người mua (seeds_fruit đã bỏ seed
    #    "cách làm giỏ trái cây" vì lý do này). CSV 17/09: "cách làm giỏ trái cây đám tang/dạm ngõ/tại nhà…"
    #    (13 dòng đang lọt vào Gift), "trang trí giỏ trái cây tết", "trang trí trái cây tiệc"; ngoài mẫu:
    #    "khắc trái cây trung thu", "tỉa trái cây trung thu".
    r"cách (làm|gói|kết|cắm|xếp|bó) giỏ|tự làm giỏ|(khắc|tỉa|cắt tỉa) (trái cây|hoa quả)|"
    r"trang trí (trái cây|giỏ trái cây|dĩa trái cây)|"
    # 7) ĐỒ GIẢ / MÔ HÌNH — "trái cây giả cao cấp", "giỏ trái cây nhựa", "mô hình cửa hàng"
    r"(trái cây|hoa quả) giả\b|\bnhựa\b|mô hình|đồ chơi|"
    # 8) TRỒNG TRỌT — "hạt giống dưa lưới", "mua giống cây kiwi". "trồng" trừ "nhà trồng / tự trồng" (hàng nhà
    #    vườn — "trái cây nhà trồng", Suggest ngoài mẫu 17/09) và "cây ba trồng" (tên địa điểm Maps trong
    #    "cây ba trồng cửa hàng trái cây nhập khẩu gia lai", CSV 17/09).
    r"hạt giống|cây giống|giống cây|mua giống|^giống |mua cây|cách trồng|(?<!nhà )(?<!tự )(?<!ba )\btrồng\b|"
    r"phân bón|chiết cành|bonsai|"
    r"cây ăn trái|(?<!trái )\bcây (kiwi|cherry|lựu|xoài|dâu tây|dâu|quýt|cam|bưởi|táo|nho|mít|ổi|chanh|đào|"
    r"mận|việt quất|sầu riêng)\b|"
    # 9) VĨ MÔ XUẤT KHẨU — "trái cây việt nam ngày càng được ưa chuộng tại thị trường trung quốc"
    r"việt nam xuất khẩu|ưa chuộng tại|kim ngạch)")


def fruit_is_negative(s: str) -> bool:
    """Loại nhiễu ngành trái cây. Mười nhóm, MỖI nhóm đều đã thấy thật trong mẻ Suggest 17/09/2026
    (ví dụ nguyên văn ở comment từng nhóm trong _FRUIT_NEGATIVE):
      1) GAME — blox fruit, grow a garden, play together, "thả trái cây shopee" (56 gợi ý)
      2) GIÁO DỤC / HỌC TIẾNG / VẼ — "giáo án…" (bỏ dấu giao→giáo), "…tiếng anh là gì", "vẽ mâm ngũ quả lớp 1"
      3) BÀI TOÁN TIỂU HỌC — "một cửa hàng hoa quả có 120kg cam" (38)
      4) KHÁC NGÀNH & ĐỒNG ÂM — rượu/bia/kẹo/kem/trà/sữa trái cây, máy ép (124); tên quả một chữ trùng
         nghĩa: giá lên thổ cư, camera, bơm ga, vải lụa, đào tạo, pha lê, lựu đạn…; vé vườn trái cây
      5) TÊN NƯỚC NGOÀI TRÙNG — true fruits, sunfruit, koi fresh fruits & tea (73)
      6) VIỆC LÀM / MỞ SHOP / VẬT TƯ — tuyển dụng, mở cửa hàng, thùng xốp, màng co (17)
      7) ĐỒ GIẢ / MÔ HÌNH — trái cây giả, giỏ trái cây nhựa
      8) TRỒNG TRỌT — hạt giống, cây giống
      9) VĨ MÔ XUẤT KHẨU — "trái cây việt nam xuất khẩu trung quốc"
     10) TỰ LÀM / TRANG TRÍ — "cách làm giỏ trái cây…", "trang trí giỏ trái cây tết", "khắc trái cây trung thu"
    Lọc chỉ áp trên chuỗi đã chuẩn hoá (chưa thêm dấu): nhiễu gõ không dấu hiếm và không được đo riêng.
    % Other của classify_fruit chỉ đếm gợi ý KHÔNG có chữ trái cây → là CẬN DƯỚI của nhiễu còn sót; nhiễu có
    ngữ cảnh trái cây (kiểu nhóm 10 trước khi thêm) không hiện trong Other — soát bằng mắt định kỳ.
    KHÔNG lọc (có chủ đích): sức khỏe/dinh dưỡng (→ Health, tín hiệu nội dung), hóa đơn (→ B2B,
    kế toán doanh nghiệp đang mua), thuế suất/hải quan (→ Wholesale, tình báo nhập khẩu), an toàn/tem mã số (→ Trust), ý nghĩa/phong thủy mâm ngũ quả
    (→ Worship), đồ sấy/mứt (→ Product, hợp giỏ quà Tết), "cửa hàng trái cây xuất khẩu" (hàng loại xuất
    khẩu bán lẻ trong nước), siêu thị (→ Chain, đối thủ), đuôi "…ảnh" của Maps (vẫn là nhu cầu tìm cửa hàng)."""
    return bool(_FRUIT_NEGATIVE.search(_fruit_norm(s)))



# ─────────────────── RTC (thực phẩm sơ chế / Ready-to-Cook) ───────────────────
# Thêm 22/09/2026. 14 nhãn, mỗi nhãn nối thẳng tới một view chủ DN yêu cầu (xem seeds_rtc).
# Từ vựng trạng thái sơ chế lấy nguyên cột `prep_type` của suggest.rtc_keywords (24 giá trị,
# đo 22/09) — không tự nghĩ ra cách sơ chế nào không có trong bộ nghiên cứu.

# Chuẩn hoá ĐẶT DẤU trước khi khớp regex. Tiếng Việt có HAI kiểu đặt dấu đều hợp lệ trên cùng
# một chữ: "hòa/hoà", "húy/huý", "khỏe/khoẻ". Google Suggest trả kiểu nào là do người dùng gõ.
# Đo thật 22/09/2026: kho Suggest có "khoai tây cắt sẵn bách ho|á| xanh" còn chuỗi bán lẻ tự viết
# "bách h|ó|a xanh" — không chuẩn hoá thì mẫu Retailer trượt và gợi ý dò-đối-thủ bị đếm thành RTC.
_RTC_DAU = [("oà", "òa"), ("oá", "óa"), ("oả", "ỏa"), ("oã", "õa"), ("oạ", "ọa"),
            ("oè", "òe"), ("oé", "óe"), ("oẻ", "ỏe"), ("oẽ", "õe"), ("oẹ", "ọe"),
            ("uỳ", "ùy"), ("uý", "úy"), ("uỷ", "ủy"), ("uỹ", "ũy"), ("uỵ", "ụy")]


def _rtc_norm(s: str) -> str:
    t = unicodedata.normalize("NFC", s or "").lower()
    for a, b in _RTC_DAU:
        t = t.replace(a, b)
    return t


# Cách nấu xuất hiện trong tên món — dùng để nhận "đây là một MÓN", không phải danh mục.
# Rút từ 592 tên món thật của public.menu_items, không phải từ điển chung.
_RTC_CACH_NAU = (
    r"(kho|xào|chiên|nướng|hấp|luộc|rim|ram|rang|khìa|hầm|tiềm|áp chảo|sốt|cuốn|cuộn|trộn|gỏi|nộm|"
    r"nấu|đút lò|lúc lắc|xíu|xá xíu|ngâm|bóp|chưng|đúc|giả cày|giả cầy|roti|lagu|cà ri|kho tộ|"
    # Kiểu chế biến không có động từ nhiệt: "bò cuộn mỡ chài", "khổ qua nhồi thịt", "thịt lợn quay",
    # "bò xông khói". Đặt SAU nhánh RTC nên "nhồi sẵn"/"cuốn sẵn" vẫn về RTC, không lẫn sang đây.
    r"nhồi|bọc|quay|xông khói)"
)
# Nền món / kiểu món — "bún bò huế", "cơm gà hải nam" không có động từ nấu nào ở trên.
_RTC_NEN_MON = r"(bún|phở|mì|miến|nui|hủ tiếu|bánh canh|cháo|xôi|cơm|lẩu|canh|súp|soup|salad|chả|nem|bì)"


def classify_rtc(s: str) -> str:
    """Thực phẩm sơ chế / Ready-to-Cook.

    THỨ TỰ NHÁNH CÓ CHỦ ĐÍCH — các nhánh sau đều chứa từ vựng của nhánh trước nếu đặt sai:
      · Storage TRƯỚC RTC     — "thịt ướp sẵn để được bao lâu" có "ướp sẵn", nhưng nó là câu
                                hỏi bảo quản, không phải nhu cầu mua hàng ướp sẵn.
      · Recipe TRƯỚC RTC      — "cách làm thịt heo ướp sẵn" là người muốn TỰ ướp.
      · MealPrep TRƯỚC Pricing — "… bao nhiêu calo" có chữ "bao nhiêu".
      · Retailer TRƯỚC Buy    — "thực phẩm sơ chế bách hóa xanh" là dò đối thủ, không phải
                                "mua ở đâu" chung.
      · B2B TRƯỚC Buy/Pricing — tệp tổ chức mua theo hợp đồng, đắt hơn nhiều lần B2C.
      · Dish CUỐI cùng        — chỉ khi không còn tín hiệu nào khác thì mới là "tên món trần",
                                đó mới là thứ nuôi TOP 20 món nhu cầu cao / tăng nhanh.

    CHƯA KIỂM TOÁN NGOÀI MẪU: bộ này viết trước mẻ đo đầu tiên nên mẫu regex dựa trên 3.308 seed
    và 592 tên món thật, KHÔNG dựa trên gợi ý Suggest thật như classify_fruit. Bài học ngành trái
    cây (khớp trong mẫu 96% nhưng sai 25% ngoài mẫu) áp dụng y nguyên: phải rút mẫu kiểm tay sau
    mẻ đầu rồi sửa lại, đừng tin số phân bố của tuần 1.
    """
    t = _rtc_norm(s)
    if re.search(r"(đồng khởi|thành gia định|mộc an)", t):
        return "Brand"

    # Chuỗi bán lẻ — 20 nhà bán lẻ của bộ RTC. Dò đối thủ, không phải cầu danh mục.
    if re.search(r"(bách hóa xanh|bachhoaxanh|winmart|vinmart|co ?op ?mart|co\.opmart|aeon|"
                 r"lotte|kingfood|king food|homefarm|home farm|mm mega|metro|3sach|3 sạch|"
                 r"farmers ?market|annam|cp brand|cp việt nam|satra|emart|big ?c|go ?!|tops market)", t):
        return "Retailer"

    # Bảo quản / an toàn — câu hỏi sống-chết của RTC. Phải bắt trước RTC và trước Pricing.
    # Nhóm "hỏng ra sao" (bị đen, bị nhớt, ăn được không) lấy từ gợi ý THẬT trong kho đo 22/09:
    # "khoai tây cắt sẵn bị đen có ăn được không", "khoai tây cắt sẵn bỏ tủ lạnh được không" —
    # chúng vốn rơi vào RTC vì chỉ có marker "cắt sẵn", trong khi ý định là lo hàng hỏng.
    if re.search(r"(bảo quản|để được bao lâu|được bao lâu|để tủ lạnh|bỏ tủ lạnh|tủ lạnh|tủ đá|"
                 r"mấy ngày|bao nhiêu ngày|hạn sử dụng|hết hạn|rã đông|mất chất|"
                 r"an toàn không|có tốt không|có sao không|độc không|ăn được không|dùng được không|"
                 r"được không|tươi không|bị đen|bị thâm|bị nhớt|bị ủng|có mùi|ôi|hư|thối)", t):
        return "Storage"

    # Công thức — TÍN HIỆU R&D, không phải nhiễu (bài học ngành chay). Nuôi view
    # "món nào nên đưa vào menu thử nghiệm": người tìm cách làm là người muốn ăn món đó.
    if re.search(r"(cách làm|cách nấu|cách ướp|cách chế biến|công thức|hướng dẫn|tự làm|tự nấu|"
                 r"làm như thế nào|nấu như thế nào|làm sao|làm từ gì|nấu với gì|ướp gì|"
                 r"ướp như thế nào|ngon nhất|bí quyết)", t):
        return "Recipe"

    # Meal prep / healthy — tuyến Mia Meal Prep. Trước Pricing vì "bao nhiêu calo".
    if re.search(r"(meal ?prep|eat ?clean|healthy|calo|kcal|dinh dưỡng|giảm cân|tăng cơ|gym|"
                 r"gạo lứt|low ?carb|keto|protein|đủ chất|ăn sạch|cả tuần|7 ngày)", t):
        return "MealPrep"

    # B2B / HORECA — 384 dòng B2B của bộ RTC đều là P0.
    if re.search(r"(sỉ\b|bỏ sỉ|giá sỉ|horeca|nhà cung cấp|cung cấp|nhà hàng|quán ăn|khách sạn|"
                 r"bếp ăn|căn tin|canteen|suất ăn công nghiệp|trường học|công ty|chuỗi|"
                 r"gia công|xưởng|nhà máy|đại lý|nguồn hàng|số lượng lớn|hợp đồng|"
                 r"hóa đơn|vat|theo yêu cầu)", t):
        return "B2B"

    # Trạng thái sơ chế — LÕI của ngành: cùng một món, sơ chế tới đâu thì người ta mua.
    if re.search(r"(sơ chế|chế biến sẵn|nấu sẵn|làm sẵn|ướp sẵn|tẩm ướp|cắt sẵn|gọt sẵn|rửa sẵn|"
                 r"bóc vỏ|băm sẵn|xay sẵn|nhồi sẵn|thái sẵn|chia phần|cắt miếng|cắt khúc|cắt hạt lựu|"
                 r"cắt lúc lắc|thái lát|thái sợi|phi lê|rút xương|rút chỉ|làm sạch|hút chân không|"
                 r"đông lạnh|cấp đông|ready ?to ?cook|meal ?kit|chỉ việc nấu|ăn liền|tiện lợi)", t):
        return "RTC"

    # Giá — sau MealPrep (calo) và B2B (giá sỉ)
    if re.search(r"(giá|bao nhiêu tiền|bao nhiêu một|bao nhiêu 1|bảng giá|báo giá|rẻ|"
                 r"khuyến mãi|giảm giá|combo)", t):
        return "Pricing"

    # Mua ở đâu — bán lẻ B2C. Sau Retailer để tên chuỗi không rơi vào đây.
    if re.search(r"(mua ở đâu|bán ở đâu|chỗ mua|chỗ bán|nơi bán|nơi mua|đặt mua|mua|bán|"
                 r"siêu thị|cửa hàng|tạp hóa|store|shop)", t):
        return "Buy"

    if re.search(r"(giao|ship|tận nơi|tận nhà|online|app\b|đặt hàng|đặt\b|mang về)", t):
        return "Delivery"

    if re.search(r"(quận|phường|huyện|gần đây|gần nhất|tphcm|tp hcm|hồ chí minh|sài gòn|saigon|"
                 r"thủ đức|bình thạnh|tân bình|tân phú|phú nhuận|gò vấp|bình tân|hóc môn|củ chi|"
                 r"nhà bè|bình chánh|hà nội|đà nẵng|thảo điền|phú mỹ hưng)", t):
        return "Local"

    # TÊN MÓN TRẦN — nuôi TOP 20 món nhu cầu cao nhất / tăng nhanh nhất.
    # Đặt cuối: chỉ nhận là món khi không còn tín hiệu thương mại/kỹ thuật nào khác.
    if re.search(_RTC_CACH_NAU, t) or re.search(_RTC_NEN_MON, t):
        return "Dish"

    if re.search(r"(thực phẩm|thức ăn|đồ ăn|món ăn|nguyên liệu|thịt|cá|gà|bò|heo|tôm|mực|rau|"
                 r"củ|trứng|đậu hũ|nấm)", t):
        return "Core"
    return "Other"


def rtc_is_negative(s: str) -> bool:
    """Loại nhiễu ngành RTC. Năm nhóm, đều đoán được từ chính chữ "sơ chế" — nó là thuật ngữ
    dùng chung cho mọi ngành chế biến nông sản, không riêng thực phẩm cho bếp gia đình:

      1) SƠ CHẾ NGÀNH KHÁC — sơ chế cà phê / cao su / dược liệu / hạt điều / thuốc lá / chè:
         đúng chữ, sai hoàn toàn thị trường.
      2) THIẾT BỊ — máy sơ chế, dây chuyền, tủ đông, máy hút chân không: người mua MÁY.
         (câu hỏi bảo quản dùng chữ "bảo quản/để được bao lâu" → vẫn vào Storage, không lọt đây)
      3) THỨC ĂN VẬT NUÔI — thức ăn cho chó/mèo, pate mèo, hạt cho chó.
      4) TRỒNG TRỌT / CHĂN NUÔI — hạt giống, cách trồng, thức ăn chăn nuôi, con giống.
      5) VIỆC LÀM + GIẢI TRÍ + HỌC THUẬT — tuyển dụng, phim, game, luận văn, tiếng anh là gì.

    KHÔNG lọc (có chủ đích): "cách làm/công thức" (→ Recipe, tín hiệu R&D), siêu thị và tên chuỗi
    (→ Retailer, dò đối thủ), "quy trình sơ chế" và "hóa đơn/vat" (→ B2B, bếp ăn đang mua và cần
    tuân thủ), "có tốt không/an toàn không" (→ Storage, đó là hàng rào tin cậy phải trả lời).
    """
    t = _rtc_norm(s)
    return bool(re.search(
        r"(sơ chế cà phê|cà phê sơ chế|sơ chế cao su|mủ cao su|sơ chế dược liệu|dược liệu|"
        r"sơ chế hạt điều|sơ chế thuốc lá|sơ chế chè|sơ chế trà|sơ chế tổ yến|sơ chế quặng|"
        r"sơ chế mủ|sơ chế gỗ|"
        # TRÁI CÂY có radar riêng (ngành `fruit`, 3.150 gợi ý) — không đo lại ở RTC để khỏi đếm
        # hai lần. Đo 22/09: "hộp trái cây cắt sẵn", "cửa hàng trái cây cắt sẵn" và cả tên quán
        # trên Maps "morning fruit … trái cây cắt sẵn" đều rơi vào RTC nếu không cắt ở đây.
        r"trái cây|hoa quả|"
        r"máy sơ chế|máy cắt thịt|máy xay thịt|máy thái|máy hút chân không|dây chuyền|"
        # KHÔNG lọc "tủ đông/tủ mát" trần: "khoai tây cắt sẵn bỏ tủ lạnh được không" và
        # "đồ ăn cấp đông để tủ đông được bao lâu" là câu hỏi BẢO QUẢN (→ Storage), không phải
        # người mua tủ. Chỉ lọc thiết bị thương mại, thứ không ai hỏi khi đang lo hàng hỏng.
        r"tủ cấp đông|kho lạnh|thiết bị bếp|dụng cụ|khay đựng|"
        # Nồi/chảo phải có ngữ cảnh ĐỒ GIA DỤNG: "chảo" trần sẽ ăn luôn "áp chảo" — một cách
        # nấu, và là cách nấu của cả tuyến healthy "cơm gạo lứt ức gà áp chảo" (DKC-RTC-008).
        r"nồi chiên không dầu|nồi áp suất|nồi cơm điện|bộ nồi|chảo chống dính|chảo gang|"
        r"thức ăn cho chó|thức ăn cho mèo|thức ăn chó|thức ăn mèo|pate mèo|pate chó|hạt cho chó|"
        r"cho gà đẻ|thức ăn chăn nuôi|cám|"
        r"hạt giống|cách trồng|kỹ thuật trồng|phân bón|con giống|chăn nuôi|"
        r"tuyển dụng|việc làm|thực tập|mức lương|tuyển thợ|"
        r"phim|truyện|game|lời bài hát|karaoke|"
        r"luận văn|tiểu luận|đồ án|giáo trình|tiếng anh là gì|dịch sang)", t))


CLASSIFIERS = {"food": classify_food, "realestate": classify_realestate, "hotel": classify_hotel,
               "water": classify_water, "produce": classify_produce, "vegetarian": classify_vegetarian,
               "fruit": classify_fruit, "rtc": classify_rtc}
NEGATIVE = {"realestate": re_is_negative, "water": water_is_negative, "produce": produce_is_negative,
            "vegetarian": vegetarian_is_negative, "fruit": fruit_is_negative,
            "rtc": rtc_is_negative}
