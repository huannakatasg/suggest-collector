# -*- coding: utf-8 -*-
"""Phân loại intent + lọc negative cho từng ngành (port từ Apps Script)."""
import re


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


CLASSIFIERS = {"food": classify_food, "realestate": classify_realestate, "hotel": classify_hotel, "water": classify_water}
NEGATIVE = {"realestate": re_is_negative, "water": water_is_negative}
