# -*- coding: utf-8 -*-
"""Ma trận hoán vị seed cho 3 ngành — bung tới ~3.000 seed/ngành.
Suggest sẽ tự bung tiếp tổ hợp con, nên đây đã là độ phủ rất sâu.
Mỗi seed = dict(keyword, nhom). Trả về list đã dedupe."""

DISTRICTS = ["quận 1","quận 2","quận 3","quận 4","quận 5","quận 6","quận 7","quận 8","quận 9",
             "quận 10","quận 11","quận 12","tân bình","tân phú","bình thạnh","phú nhuận","gò vấp",
             "bình tân","thủ đức","hóc môn","củ chi","nhà bè","bình chánh"]
STREETS = ["nguyễn huệ","lê lợi","điện biên phủ","cách mạng tháng 8","cộng hòa","phổ quang",
           "nguyễn thị minh khai","3 tháng 2","nguyễn văn trỗi","hoàng văn thụ","trường sơn",
           "nam kỳ khởi nghĩa","pasteur","võ văn tần","tôn đức thắng","lê duẩn","trần hưng đạo",
           "phạm văn đồng","quang trung","lê văn việt"]
CLUSTERS = ["thảo điền","phú mỹ hưng","an phú","sala","vinhomes grand park","vinhomes central park",
            "masteri","landmark 81","khu công nghệ cao","khu chế xuất tân thuận"]
EN_LOC = ["district 1","district 2","district 3","district 4","district 7","district 10","binh thanh",
          "tan binh","phu nhuan","go vap","thu duc","thao dien","phu my hung","an phu","ho chi minh","saigon"]

def _dedupe(rows):
    seen=set(); out=[]
    for k,n in rows:
        k=" ".join(k.split()).lower().strip()
        if not k or k in seen: continue
        seen.add(k); out.append({"keyword":k,"nhom":n})
    return out

def seeds_food():
    r=[]
    types=["cơm trưa văn phòng","cơm văn phòng","suất ăn văn phòng","suất ăn công nghiệp",
           "cơm phần văn phòng","cơm hộp văn phòng","cơm trưa công sở","đặt cơm văn phòng",
           "cơm trưa nhân viên","suất ăn công ty","cơm gà","cơm tấm","cơm chay","cơm healthy",
           "cơm eat clean","cơm văn phòng ngon","quán cơm trưa văn phòng","cơm trưa giao tận nơi",
           "catering cơm trưa","suất ăn cho công ty"]
    place_types=["cơm trưa văn phòng","cơm văn phòng","suất ăn công nghiệp","đặt cơm văn phòng",
                 "cơm trưa giao tận nơi","cơm hộp văn phòng","cơm chay","cơm gà","cơm tấm",
                 "quán cơm trưa văn phòng","catering","suất ăn công ty"]
    mods=["giá rẻ","theo tháng","theo tuần","giao tận nơi","gần đây","ngon","sạch","ship nhanh",
          "đặt online","khuyến mãi","buffet trưa","cao cấp"]
    en=["office lunch delivery","corporate catering","healthy lunch box","lunch box delivery",
        "office catering","bento box catering","eat clean lunch","daily meal prep",
        "premium lunch box","best lunch delivery","healthy meal delivery"]
    for t in types: r.append((t,"Core"))
    for t in place_types:
        for d in DISTRICTS: r.append((f"{t} {d}","Local"))
        for c in CLUSTERS: r.append((f"{t} {c}","Local"))
    for t in types:
        for m in mods: r.append((f"{t} {m}","Modifier"))
    top_mods=["giá rẻ","gần đây","giao tận nơi","theo tháng","ngon"]
    for t in place_types:
        for d in DISTRICTS:
            for m in top_mods: r.append((f"{t} {d} {m}","Local"))
    for t in en:
        r.append((t,"English / Expat"))
        for d in EN_LOC: r.append((f"{t} {d}","English / Expat"))
        for m in ["near me","cheap","price","menu"]: r.append((f"{t} {m}","English / Expat"))
    return _dedupe(r)

def seeds_realestate():
    r=[]
    office=["thuê văn phòng","cho thuê văn phòng","thuê sàn văn phòng","thuê tòa nhà văn phòng",
            "thuê văn phòng trọn gói","thuê văn phòng hạng a","thuê văn phòng nhỏ","thuê văn phòng cao cấp"]
    resi=["thuê căn hộ","thuê căn hộ dịch vụ","thuê chung cư","thuê chung cư mini","thuê nhà nguyên căn",
          "thuê officetel","thuê căn hộ studio","thuê phòng trọ cao cấp","thuê căn hộ 1 phòng ngủ",
          "thuê căn hộ 2 phòng ngủ"]
    retail=["thuê mặt bằng kinh doanh","cho thuê shophouse","thuê kiot","thuê mặt bằng quán ăn","thuê mặt bằng nhỏ"]
    cowork=["thuê văn phòng ảo","coworking space","thuê chỗ ngồi làm việc","không gian làm việc chung","thuê văn phòng chia sẻ"]
    kcn=["thuê nhà xưởng","cho thuê nhà xưởng","thuê kho xưởng","thuê văn phòng khu công nghiệp"]
    mods=["giá rẻ","cao cấp","trọn gói","có nội thất","gần trung tâm","mới"]
    en=["office for rent","serviced office","virtual office","coworking space","apartment for rent",
        "serviced apartment","studio apartment for rent","house for rent","shophouse for rent","grade a office for rent"]
    for t in office+resi+retail+cowork+kcn:
        nhom = ("Văn phòng" if t in office else "Nhà ở / Căn hộ" if t in resi else
                "Mặt bằng / Shophouse" if t in retail else "Coworking" if t in cowork else "Khu công nghiệp")
        r.append((t,nhom))
    for t in office:
        for d in DISTRICTS: r.append((f"{t} {d}","Văn phòng"))
        for s in STREETS: r.append((f"{t} đường {s}","Văn phòng"))
    for t in resi:
        for d in DISTRICTS: r.append((f"{t} {d}","Nhà ở / Căn hộ"))
        for c in CLUSTERS: r.append((f"{t} {c}","Nhà ở / Căn hộ"))
    for t in retail:
        for d in DISTRICTS: r.append((f"{t} {d}","Mặt bằng / Shophouse"))
    for t in cowork:
        for d in DISTRICTS[:12]: r.append((f"{t} {d}","Coworking"))
    for t in (office+resi):
        for m in mods: r.append((f"{t} {m}","Giá thuê"))
    for t in resi:
        for s2 in STREETS: r.append((f"{t} đường {s2}","Nhà ở / Căn hộ"))
    for t in office:
        for c in CLUSTERS: r.append((f"{t} {c}","Văn phòng"))
    for t in retail:
        for s2 in STREETS: r.append((f"{t} đường {s2}","Mặt bằng / Shophouse"))
    top_mods=["giá rẻ","cao cấp","có nội thất"]
    for t in (office+resi):
        for d in DISTRICTS:
            for m in top_mods: r.append((f"{t} {d} {m}","Giá thuê"))
    for t in en:
        r.append((t,"English / Expat"))
        for d in EN_LOC: r.append((f"{t} {d}","English / Expat"))
        for m in ["near me","cheap","fully furnished"]: r.append((f"{t} {m}","English / Expat"))
    return _dedupe(r)

def seeds_hotel():
    r=[]
    DEST=["vũng tàu","đà lạt","nha trang","phú quốc","phan thiết","mũi né","đà nẵng","hội an","huế",
          "sa pa","hạ long","ninh bình","quy nhơn","côn đảo","cần thơ","châu đốc","bến tre","tây ninh",
          "buôn ma thuột","pleiku","cà mau","hà giang","mộc châu","tam đảo"]
    types=["khách sạn","resort","homestay","villa","căn hộ du lịch","nhà nghỉ","khách sạn gần biển",
           "resort có hồ bơi","combo du lịch","tour du lịch","vé máy bay","thuê xe du lịch"]
    place_types=["khách sạn","resort","homestay","villa","combo du lịch","tour du lịch","khách sạn gần biển"]
    mods=["giá rẻ","cao cấp","gần biển","có hồ bơi","cho gia đình","2 ngày 1 đêm","3 ngày 2 đêm",
          "view đẹp","gần trung tâm","đáng đi","tốt nhất","có ăn sáng"]
    en=["hotel","resort","homestay","beach hotel","family resort","travel package","cheap hotel","luxury resort"]
    for t in types: r.append((t,"Core"))
    for t in place_types:
        for d in DEST: r.append((f"{t} {d}","Local"))
    for t in types:
        for m in mods: r.append((f"{t} {m}","Modifier"))
    top_mods=["giá rẻ","gần biển","cho gia đình","2 ngày 1 đêm","view đẹp","tốt nhất"]
    for t in place_types:
        for d in DEST:
            for m in top_mods: r.append((f"{t} {d} {m}","Local"))
    for t in en:
        for d in DEST[:16]: r.append((f"{t} {d}","English / Expat"))
        r.append((t,"English / Expat"))
    return _dedupe(r)

INDUSTRIES = {"food":seeds_food, "realestate":seeds_realestate, "hotel":seeds_hotel}

if __name__ == "__main__":
    for k,f in INDUSTRIES.items():
        s=f(); print(f"{k}: {len(s)} seed")
