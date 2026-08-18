# -*- coding: utf-8 -*-
"""Ma trận hoán vị seed cho 4 ngành — bung tới ~3.000 seed/ngành.
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
WATER_CLUSTERS = ["k300","etower","republic plaza","pearl plaza","landmark 81","saigon pearl",
                  "thảo điền","phú mỹ hưng","khu chế xuất tân thuận","khu công nghệ cao"]
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

def seeds_water():
    r=[]
    action=["đổi nước","giao nước bình","đại lý nước suối","gọi nước bình",
            "nước suối đóng chai giá sỉ","nước bình 20l giao tận nơi",
            "giao nước uống văn phòng","đổi nước văn phòng","nước uống văn phòng"]
    brands=["nước lavie","lavie văn phòng","đổi nước lavie","nước vĩnh hảo",
            "vĩnh hảo bình 20l","nước ion life","ion life văn phòng",
            "nước aquafina","aquafina văn phòng","nước bidrico","nước sapuwa"]
    bottle=["nước bình 20l","nước bình 19l","nước uống đóng bình","bình nước 20l",
            "bình nước 19l","nước bình úp","nước khoáng bình 20l"]
    meeting=["nước suối đóng chai giá sỉ","nước suối thùng","nước chai 350ml",
             "nước chai 500ml","nước khoáng phòng họp","nước suối phòng họp",
             "nước uống hội nghị"]
    equipment=["thuê cây nước nóng lạnh","mua cây nước nóng lạnh văn phòng",
               "bình nước úp cho cây nóng lạnh","cây nước nóng lạnh văn phòng"]
    en=["office water delivery","corporate water supply","mineral water for office",
        "water bottle 20l delivery","bottled water delivery service","20l water bottle near me"]
    mods=["giao tận nơi","gần đây","giá sỉ","cho công ty","cho văn phòng","có hóa đơn",
          "vat","theo tháng","chiết khấu"]

    for t in action: r.append((t,"Hành vi / Dịch vụ"))
    for t in brands: r.append((t,"Thương hiệu"))
    for t in bottle: r.append((t,"Bình 19L/20L"))
    for t in meeting: r.append((t,"Chai nhỏ / Phòng họp"))
    for t in equipment: r.append((t,"Thiết bị"))

    local_base=action+brands+bottle+meeting+equipment
    for t in local_base:
        for d in DISTRICTS: r.append((f"{t} {d}","Local"))
        for c in WATER_CLUSTERS: r.append((f"{t} {c}","Local"))
    for t in brands+bottle+action:
        for s in STREETS[:14]: r.append((f"{t} đường {s}","Local"))
    for t in action+brands+bottle+meeting:
        for m in mods: r.append((f"{t} {m}","Modifier"))
    for t in brands+bottle:
        for d in DISTRICTS:
            for m in ["giao tận nơi","giá sỉ","theo tháng"]:
                r.append((f"{t} {d} {m}","Local"))
    for t in en:
        r.append((t,"English / Corporate"))
        for d in EN_LOC: r.append((f"{t} {d}","English / Corporate"))
        for m in ["near me","price","invoice","office pantry"]:
            r.append((f"{t} {m}","English / Corporate"))
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

def seeds_produce():
    """Rau củ quả B2B cho nhà hàng/quán ăn/bếp ăn. Các trục dưới đây KHÔNG phải đoán —
    lấy từ đo SERP thật 18/08/2026 (15 seed lõi, 133 slot, 37 trang đối thủ):
      · Google coi "nông sản" gần như đồng nghĩa "rau củ quả" (8 lần trong Related Searches)
      · Cụm giá bám theo TỪNG CHỢ ĐẦU MỐI (Thủ Đức/Hóc Môn/Bình Điền) và TỪNG MẶT HÀNG
      · "Đà Lạt" là một trục nguồn hàng riêng (5 lần trong Related)
      · Chi tiết: docs/RAU_CU_B2B_NGHIEN_CUU.md của repo app
    """
    r=[]
    # Cách gọi mặt hàng — cả hai biến thể, vì Google gộp chúng
    goods=["rau củ quả","rau củ","nông sản","rau sạch","rau an toàn","thực phẩm tươi sống"]
    # Ai mua — trục quan trọng nhất, mỗi loại khách là một SERP riêng
    buyers=["nhà hàng","quán ăn","chuỗi nhà hàng","chuỗi quán ăn","khách sạn","bếp ăn công nghiệp",
            "bếp ăn tập thể","căn tin","canteen","suất ăn công nghiệp","quán chay","quán lẩu",
            "quán phở","nhà hàng tiệc cưới","trường học","công ty","siêu thị","cửa hàng thực phẩm"]
    # Động từ giao dịch
    verbs=["cung cấp","nhà cung cấp","đơn vị cung cấp","công ty cung cấp","nguồn","mua","bán sỉ","đại lý"]
    # Ý định giá — cụm có PAA duy nhất trong 15 seed đã đo
    price=["bảng giá","báo giá","giá sỉ","giá bán sỉ","giá hôm nay","giá bao nhiêu","giá thị trường","đơn giá"]
    markets=["chợ đầu mối","chợ đầu mối thủ đức","chợ đầu mối hóc môn","chợ đầu mối bình điền",
             "chợ nông sản","chợ sỉ"]
    # Nguồn hàng
    sources=["đà lạt","miền tây","củ chi","lâm đồng","nhà vườn","hợp tác xã","vùng trồng"]
    # Dịch vụ — pain point thật của bếp
    services=["giao tận nơi","giao hàng tận nơi","giao hàng mỗi ngày","giao hàng sáng sớm",
              "giao trong ngày","sơ chế sẵn","cắt sẵn","gọt sẵn","rửa sẵn","đóng gói theo yêu cầu",
              "số lượng lớn","theo hợp đồng","theo tháng","ổn định","có hóa đơn","xuất hóa đơn vat"]
    certs=["vietgap","globalgap","hữu cơ","organic","an toàn thực phẩm","attp","truy xuất nguồn gốc",
           "có giấy chứng nhận","kiểm định"]
    # Mặt hàng cụ thể — luôn kèm modifier B2B, không bao giờ để trần
    items=["cà rốt","khoai tây","xà lách","cà chua","dưa leo","bắp cải","súp lơ","hành tây","củ cải",
           "bí đỏ","bí xanh","rau muống","cải ngọt","cải thìa","cải thảo","rau thơm","hành lá","ngò rí",
           "sả","gừng","tỏi","ớt","nấm rơm","nấm bào ngư","nấm đùi gà","nấm kim châm","giá đỗ",
           "khổ qua","đậu bắp","đậu cove","bầu","mướp","rau quế","húng quế","chanh","khoai lang"]
    item_mods=["giá sỉ","giá sỉ tphcm","cho nhà hàng","sỉ hôm nay","giá hôm nay","đà lạt giá sỉ","cắt sẵn"]
    # Combo theo món — long-tail ít cạnh tranh
    combos=["rau lẩu","rau nhúng lẩu","rau sống quán phở","rau ăn kèm bún bò","rau salad",
            "rau củ luộc","rau món chay","rau món âu","rau thơm các loại"]

    for g in goods:
        r.append((g+" sỉ","Core"))
        for v in verbs: r.append((f"{v} {g}","Core"))
    # Ai mua × cách gọi × động từ  -> trục thương mại chính
    for g in goods[:4]:
        for b in buyers:
            r.append((f"{g} cho {b}","B2B"))
            for v in verbs[:5]: r.append((f"{v} {g} cho {b}","B2B"))
    # Giá — kèm địa bàn và chợ
    for g in goods[:4]:
        for p in price:
            r.append((f"{p} {g}","Pricing"))
            r.append((f"{p} {g} tphcm","Pricing"))
    for m in markets:
        r.append((f"giá rau củ quả {m} hôm nay","Market"))
        r.append((f"giá nông sản {m} hôm nay","Market"))
        r.append((f"lấy hàng {m}","Market"))
    # Nguồn hàng
    for g in goods[:4]:
        for s in sources:
            r.append((f"{g} {s}","Sourcing"))
            r.append((f"nguồn {g} {s}","Sourcing"))
    for g in goods[:3]:
        r.append((f"mua {g} sỉ ở đâu tphcm","Sourcing"))
        r.append((f"tìm nhà cung cấp {g}","Sourcing"))
    # Dịch vụ × cách gọi
    for g in goods[:4]:
        for s in services: r.append((f"{g} {s}","Service"))
    # Chứng nhận
    for g in goods[:4]:
        for c in certs: r.append((f"{g} {c}","Certification"))
    # Địa bàn — chỉ với 3 cách gọi mạnh nhất để không phình
    for g in goods[:3]:
        for d in DISTRICTS:
            r.append((f"cung cấp {g} {d}","Local"))
            r.append((f"nhà cung cấp {g} {d}","Local"))
        r.append((f"nhà cung cấp {g} tphcm","Local"))
        r.append((f"cung cấp {g} tphcm","Local"))
    # Mặt hàng cụ thể — LUÔN có modifier B2B
    for it in items:
        for m in item_mods: r.append((f"{it} {m}","Product"))
    # Combo theo món
    for c in combos:
        r.append((f"{c} giá sỉ","Product"))
        r.append((f"{c} cho nhà hàng","Product"))
    return _dedupe(r)


INDUSTRIES = {"food":seeds_food, "realestate":seeds_realestate, "hotel":seeds_hotel,
              "water":seeds_water, "produce":seeds_produce}

if __name__ == "__main__":
    for k,f in INDUSTRIES.items():
        s=f(); print(f"{k}: {len(s)} seed")
