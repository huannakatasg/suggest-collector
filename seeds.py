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


def seeds_vegetarian():
    """Món chay — module Mộc An (3 kênh: Daily cơm phần / Gifts quà chay / Pro B2B).
    Trục lấy từ spec 'Mộc An Vegetarian Food R&D' trong repo app: intent
    recipe/buy/delivery/restaurant/price/healthy/gift/b2b/occasion + trục MÓN
    và NGUYÊN LIỆU (nấm, đậu hũ, sen, mít non...).
    KHÁC ngành food (suất ăn văn phòng/catering): ở đây đơn vị nhu cầu là MÓN
    và SẢN PHẨM chay — dữ liệu này về sau map về Dish entity cho R&D.
    Lưu ý: "cách làm/công thức" KHÔNG phải nhiễu ở ngành này — đó là tín hiệu
    R&D trực tiếp (người tìm công thức = món có nhu cầu), ngược với produce."""
    r=[]
    # Cách gọi chung — nền phủ rộng
    goods=["món chay","đồ chay","cơm chay","đồ ăn chay","thực phẩm chay","món ăn chay"]
    for g in goods:
        r.append((g,"Core")); r.append((g+" ngon","Core"))
        r.append((g+" gần đây","Local")); r.append((g+" tphcm","Local"))
    # Món cụ thể — trái tim của R&D: mỗi món một cụm demand riêng, sau này thành Dish
    dishes=["lẩu chay","bún chay","phở chay","bún riêu chay","bún bò chay","hủ tiếu chay",
            "mì chay","miến chay","bánh mì chay","cơm tấm chay","cơm chiên chay","xôi chay",
            "cháo chay","súp chay","gỏi chay","salad chay","gỏi cuốn chay","bì cuốn chay",
            "chả chay","chả giò chay","chả lụa chay","nem chay","pate chay","ruốc nấm",
            "chà bông chay","xúc xích chay","lạp xưởng chay","há cảo chay","bánh xèo chay",
            "bánh cuốn chay","cà ri chay","bò kho chay","kho quẹt chay","mắm chay",
            "canh chua chay","canh kiểm","thịt kho chay","sườn non chay","cá kho chay",
            "gà chay","heo quay chay","khô bò chay","bánh bao chay","đậu hũ nhồi",
            "nấm kho tiêu","cơm sen","chả nấm"]
    for d in dishes:
        r.append((d,"Dish")); r.append((d+" ngon","Dish"))
        r.append(("cách làm "+d,"Recipe")); r.append(("cách nấu "+d,"Recipe"))
        r.append((d+" mua ở đâu","Buy")); r.append((d+" giá bao nhiêu","Pricing"))
    # Nguyên liệu chủ lực — một nguyên liệu tạo được bao nhiêu món?
    ingredients=["nấm","đậu hũ","tàu hũ ky","mì căn","củ sen","hạt sen","mít non",
                 "chuối xanh","đậu nành","rong biển","nấm đùi gà","nấm bào ngư","nấm rơm",
                 "nấm kim châm","nấm hương","nấm mối đen","đậu gà","đậu lăng"]
    for i in ingredients:
        r.append(("món chay từ "+i,"Ingredient"))
        r.append(("món chay với "+i,"Ingredient"))
        r.append((i+" làm món gì","Ingredient"))
    # Công thức & thực đơn — tín hiệu R&D trực tiếp
    recipes=["món chay dễ làm","món chay đơn giản","món chay đãi tiệc","món chay ngon dễ làm",
             "thực đơn chay","thực đơn chay 7 ngày","thực đơn chay hàng ngày","mâm cơm chay",
             "món chay mới lạ","món chay sang trọng","món chay đẹp mắt","nấu chay",
             "món chay cho người mới ăn chay","món chay cuối tuần"]
    for x in recipes: r.append((x,"Recipe"))
    # Healthy / đạm — trục sức khỏe của spec
    healthy=["món chay healthy","ăn chay healthy","món chay giảm cân","thực đơn chay giảm cân",
             "món chay giàu đạm","món chay giàu protein","đạm chay","protein thực vật",
             "ăn chay đủ chất","ăn chay khoa học","eat clean chay","món chay ít dầu mỡ",
             "ăn chay có tốt không","ăn chay trường thiếu chất gì","đạm thực vật từ đâu"]
    for x in healthy: r.append((x,"Healthy"))
    # Dịp — mùa vụ của ngành: rằm, mùng 1, Vu Lan, Tết, giỗ
    occasions=["món chay ngày rằm","món chay mùng 1","mâm cơm chay cúng","mâm cỗ chay",
               "cỗ chay ngày giỗ","món chay cúng rằm tháng 7","món chay vu lan","món chay ngày tết",
               "thực đơn tiệc chay","đặt tiệc chay","nấu cỗ chay thuê","buffet chay",
               "món chay đãi khách","mâm chay cúng về nhà mới","mâm chay cúng khai trương"]
    for x in occasions: r.append((x,"Occasion"))
    # Quán / nhà hàng — kênh cạnh tranh + demand ăn ngoài
    resto=["quán chay","quán chay ngon","nhà hàng chay","buffet chay","quán cơm chay",
           "tiệm chay","quán chay bình dân","nhà hàng chay sang trọng","quán chay gần đây"]
    for x in resto:
        r.append((x,"Restaurant")); r.append((x+" tphcm","Restaurant"))
    for d in DISTRICTS:
        r.append((f"quán chay {d}","Local")); r.append((f"cơm chay {d}","Local"))
    # Giao hàng — kênh Mộc An Daily
    delivery=["cơm chay giao tận nơi","đặt cơm chay online","cơm chay văn phòng",
              "cơm chay giao hàng","đồ chay giao tận nơi","đặt món chay","ship đồ chay",
              "cơm chay trưa","đặt cơm chay theo tháng","cơm chay phần","cơm chay hộp"]
    for x in delivery: r.append((x,"Delivery"))
    # Quà chay — kênh Mộc An Gifts
    gifts=["quà chay","quà tặng chay","giỏ quà chay","hộp quà chay","quà tết chay",
           "quà vu lan","quà tặng người ăn chay","set quà chay","giỏ quà tết chay",
           "quà biếu người ăn chay","bánh chay làm quà"]
    for x in gifts: r.append((x,"Gift"))
    # Đóng gói / chế biến sẵn — Mộc An Gifts + Pro
    packaged=["đồ chay đóng gói","thực phẩm chay đóng gói","đồ chay đông lạnh","đồ chay cấp đông",
              "chả chay đóng gói","đồ chay ăn liền","đồ chay khô","thực phẩm chay chế biến sẵn",
              "pate chay hộp","đồ chay hút chân không","gia vị chay","nước mắm chay",
              "hạt nêm chay","sốt chay","đồ hộp chay","mì chay gói"]
    for x in packaged: r.append((x,"Packaged"))
    # B2B / sỉ — kênh Mộc An Pro
    b2b=["đồ chay sỉ","đồ chay giá sỉ","bỏ sỉ đồ chay","sỉ đồ chay","nguồn hàng đồ chay",
         "nguyên liệu chay cho quán","nguyên liệu nấu chay","cung cấp đồ chay","cung cấp đồ chay cho quán",
         "gia công đồ chay","xưởng sản xuất đồ chay","đại lý đồ chay","mở quán chay",
         "mở quán chay cần bao nhiêu vốn","kinh doanh đồ chay","đồ chay xuất hóa đơn",
         "cung cấp suất ăn chay","suất ăn chay công nghiệp","cơm chay công ty","đặt cơm chay công ty",
         "cung cấp tiệc chay","đặt cỗ chay công ty"]
    for x in b2b: r.append((x,"B2B"))
    # Giá — nhánh thương mại chung
    prices=["giá đồ chay","cơm chay bao nhiêu 1 phần","giá tiệc chay","bảng giá tiệc chay",
            "giá buffet chay","đồ chay rẻ","giá chả chay","combo cơm chay"]
    for x in prices: r.append((x,"Pricing"))
    return _dedupe(r)


def seeds_fruit():
    """Trái cây (key `fruit`, nhãn "Trái cây"). Mô hình kinh doanh CHƯA chốt → seed chia theo MẶT TRẬN
    để chủ doanh nghiệp chọn sau (bán lẻ nhập khẩu · cửa hàng/gần đây · giỏ quà · cúng · giao online ·
    giá · sỉ/nguồn hàng · tổ chức mua B2B · mặt hàng · chuỗi đối thủ). Trục KHÔNG đoán — lấy từ đo thật:
      · Google Suggest 17/09/2026 08:32–08:44 giờ VN (1.518 seed, 4.233 gợi ý khác nhau, 0 lỗi):
        _research/trai-cay-suggest.mjs → exports/trai-cay-suggest.json (repo app).
      · Đo bổ sung 17/09/2026 09:17–09:18 giờ VN cho 109 seed dưới đây CHƯA có trong mẻ trên (114 request
        gồm 5 canary, 0 lỗi): _research/trai-cay-seed-probe.py → exports/trai-cay-seed-probe.json.
      · Kiểm toán 17/09/2026 09:38 giờ VN (36 request, 0 lỗi) cho 7 seed ở mục 16:
        exports/trai-cay-audit-oos-raw.json.
        ⇒ MỌI seed trong hàm này đều đã được đo; "(n)" = số gợi ý seed trả về hôm đo (trần 10).
        Suggest là TÍN HIỆU NHU CẦU, KHÔNG phải search volume.
      · SERP TP.HCM cùng ngày (Serper, 21 từ khóa, 180 slot): _research/trai-cay-serp.mjs.
      · 21 từ khóa + volume Keyword Planner do NGƯỜI DÙNG cung cấp 17/09/2026 — không phải số mình đo.
    Nguyên tắc chọn:
      · Giữ seed đo ≥3 gợi ý. Seed 0–2 bị BỎ (ghi lý do từng nhóm), trừ: 21 từ khóa KP (giữ để nối volume),
        CỜ CANH có chủ đích (B2B văn phòng, giá Tết), chữ cái alphabet trả ≥1 gợi ý SẠCH, và hàng 23 quận đầy đủ của
        cụm mạnh nhất. Nhiều cụm "lộ ra" trong gợi ý khi query lại chỉ trả chính nó (1) — chúng vẫn được
        quan sát qua seed cha, không cần seed riêng. Kết quả (sau kiểm toán 17/09): 552 seed, 4/552 seed đo 0
        (đều là cờ canh), tổng 4.479 gợi ý thô / 4.237 sạch hôm đo (TB 8,1/seed; trước kiểm toán 558 seed,
        4.434 thô). Tính lại: cộng số gợi ý của từng seed trong 3 tệp đo ở trên. Đối chiếu log Actions 16/09/2026: vegetarian 535 seed → 3.008
        dòng/mẻ, produce 1.144 seed → 815 dòng/mẻ — ma trận hoán vị sâu cho ít dòng hơn seed được đo.
      · Địa bàn CHỈ TP.HCM: quận lấy từ DISTRICTS nhưng chỉ giữ quận đo ≥3; thêm khu sáp nhập 2025
        (Bình Dương, Dĩ An, Thuận An, Vũng Tàu, Bà Rịa) vì đo được: "trái cây nhập khẩu bình dương" (10),
        "…vũng tàu" (9) và "cửa hàng trái cây nhập khẩu thủ dầu một" do 7 seed trả về. Bỏ seed Hà Nội /
        Đà Nẵng / Cần Thơ / Hải Phòng / Biên Hòa của mẻ đo.
      · "hoa quả" chỉ còn trong 21 từ khóa KP: đo 17/09 "hoa quả" nghiêng Bắc (Google tự thêm HN 152 +
        tỉnh Bắc 91 lần, HCM 18); SERP "cửa hàng hoa quả sạch" 8/8 slot gắn Hà Nội dù đặt location TP.HCM.
      · Tên quả MỘT CHỮ không bao giờ để trần: "giá lê"→"giá lên thổ cư", "cam nhập khẩu"→"cấm nhập
        khẩu" (7/10), "giá bơ"→"bơm ga", "vải mua ở đâu"→vải may, "hồng nhập khẩu"→hoa hồng/muối hồng.
      · Alphabet soup (seed lõi + a..z, đ, 1, 2, 3, 5) chỉ cho tiền tố có TB gợi ý SẠCH ≥ 4,9 (đã trừ nhiễu
        bằng fruit_is_negative): trái cây nhập khẩu 8,6 · giỏ trái cây 8,0 · mâm ngũ quả 6,9 · cửa hàng
        trái cây 6,9 · trái cây cúng 6,5 · shop trái cây 6,5 · cửa hàng trái cây nhập khẩu 4,9; bỏ các chữ
        cái trả 0. Bỏ tiền tố: hoa quả nhập khẩu (7,1 nhưng lệch Hà Nội), giá trái cây (3,9 — game "grow a
        garden/blox fruit" chiếm), trái cây sỉ (3,3; 15/31 rỗng), giao trái cây (1,3 — "giáo án…"),
        trái cây ngoại nhập (0,6).
      · Không lấy tầng 2 của mẻ đo: TB 2,2 gợi ý, 457/700 seed chỉ trả lại chính nó.
    Thời gian cào thêm mỗi mẻ: 552 seed × ~0,69 s (đo thật trên Actions 16/09/2026, run 35058202573:
    11.485 seed / 2h12m49s) ≈ 6,3 phút; ước lượng bảo thủ 0,9 s/seed (0,6 delay + ~0,3 request) ≈ 8,3 phút.
    """
    r=[]
    HAU_TO=list("abcdefghijklmnopqrstuvwxyz")+["đ","1","2","3","5"]

    # 0) 21 TỪ KHÓA KEYWORD PLANNER người dùng cung cấp (volume/tháng là số KP, KHÔNG phải số đo).
    #    Giữ nguyên văn để nối volume ↔ thứ hạng Suggest, kể cả 3 từ chỉ trả 2 gợi ý. Không từ nào trả 0.
    #    "trái cây nhập khẩu hoa biên" (2.400/tháng KP): MƠ HỒ, không quy cho chuỗi Hoa Biển. Suggest 17/09
    #    trả 9 gợi ý = chính nó + 8 gợi ý Biên Hòa ("tiệm trái cây nhập khẩu biên hoà", "f79 fruits - …biên
    #    hòa"), 0 gợi ý Hoa Biển (cache exports/trai-cay-suggest-cache.json). Có thể là gõ thiếu dấu "Hoa Biển"
    #    nhưng CHƯA kiểm chứng → nhom = Local (đúng nhãn classify_fruit trả), KHÔNG cộng volume KP vào thị phần
    #    Hoa Biển. Tên chuỗi đúng dấu nằm ở nhóm Chain.
    kp21=[("trai cay ngoai nhap","Imported"),("trái cây nhập khẩu","Imported"),("hoa qua nhập khẩu","Imported"),
          ("hoa quả nhập khẩu","Imported"),("trái cây nhập khẩu gần đây","Store"),("các loại trái cây","Core"),
          ("trái cây nhập khẩu hoa biên","Local"),("giỏ hoa quả nhập khẩu","Gift"),
          ("hoa quả nhập khẩu gần đây","Store"),("cửa hàng trái cây nhập khẩu","Store"),
          ("cửa hàng hoa quả sạch","Store"),("hoa quả sạch gần đây","Store"),("klever fruit gần đây","Chain"),
          ("shop trái cây gần đây","Store"),("trái cây nhập","Imported"),
          ("cửa hàng trái cây nhập khẩu gần đây","Store"),("cửa hàng hoa quả nhập khẩu gần đây","Store"),
          ("cửa hàng trái cây vinfruits","Chain"),("giỏ trái cây 200k","Gift"),
          ("tiệm trái cây nhập khẩu gần đây","Store"),("5 loại trái cây cúng","Worship")]
    r+=kp21

    # 1) ALPHABET SOUP — cách rẻ nhất để Suggest tự bung long-tail thật (ngưỡng ở docstring).
    #    Thang giá giỏ quà (50k…5 triệu) lộ ra qua "giỏ trái cây 1/2/3/5" → không cần seed giá riêng
    #    ("giỏ trái cây 100k/150k/250k/350k/2 triệu" query riêng chỉ trả 1).
    #    Tập loại = chữ cái trả 0 gợi ý SẠCH ngày 17/09 (sau fruit_is_negative), không chỉ 0 thô. Kiểm toán
    #    17/09 thêm: "mâm ngũ quả a/i/w" (chỉ trả "…tiếng anh là gì", "in english", "what is mâm ngũ quả") và
    #    "giỏ trái cây i" (chỉ "giỏ đựng trái cây inox"). "cửa hàng trái cây nhập khẩu a/d/j/r/u/1/2/3/5":
    #    trả 1–3 gợi ý, TẤT CẢ đã do seed khác trả về (bỏ cả 9 cùng lúc: mất 0 gợi ý sạch, đo trên cache 17/09)
    #    — bỏ để giảm lặp dòng và thổi phồng tần suất cụm cửa hàng.
    abc=[("trái cây nhập khẩu","Imported",{"i"}),("giỏ trái cây","Gift",{"i","z"}),
         ("mâm ngũ quả","Worship",{"a","i","w","z"}),
         ("cửa hàng trái cây","Store",{"e","i","w","y","z"}),("trái cây cúng","Worship",{"f","i","j","u","w","y","z"}),
         ("shop trái cây","Store",{"e","i","j","p","w","z"}),
         ("cửa hàng trái cây nhập khẩu","Store",{"e","i","p","w","y","z","a","d","j","r","u","1","2","3","5"})]
    for p,n,rong in abc:
        r.append((p,n))
        for h in HAU_TO:
            if h not in rong: r.append((f"{p} {h}",n))
    # Alphabet CHỌN LỌC cho hai mặt trận mỏng (Giá, Sỉ): chỉ chữ cái có ≥3 gợi ý SẠCH hôm 17/09 — phần còn
    # lại của "giá trái cây" bị game chiếm ("giá trái cây a" → grow a garden), "trái cây sỉ" 15/31 rỗng.
    for p,n,chu in [("giá trái cây","Pricing","b c d h k l m n o q r s t v x đ 1"),
                    ("trái cây sỉ","Wholesale","b c g k l m n s t đ")]:
        for h in chu.split(): r.append((f"{p} {h}",n))

    # 2) LÕI / NHẬP KHẨU. Bỏ: "trái cây nhập khẩu chính hãng" (0), "…mùa này" (1), "trái cây chile" (1),
    #    "trái cây nam phi" (1), "các loại trái cây nhập khẩu" (7 nhưng thiên kiến thức "vào việt nam").
    #    Xuất xứ: kim ngạch rau quả 7T/2026 Trung Quốc 39,5%, Mỹ 24,5% (nguồn ngoài, An ninh Thủ đô 09/09/2026).
    imported=[("trai cay nhap khau",10),("trái cây ngoại nhập",9),("trái cây nhập khẩu ngon",8),
              ("trái cây nhập khẩu cao cấp",4),("trái cây nhập khẩu tphcm",10),("trái cây nhập khẩu uy tín",4),
              ("trái cây mỹ",10),("trái cây úc",10),("trái cây new zealand",3),("trái cây nhật bản",10),
              ("trái cây hàn quốc",10),("trái cây thái lan",10),("trái cây nhập khẩu mỹ",9),("trái cây nhập khẩu úc",3)]
    for x,_ in imported: r.append((x,"Imported"))
    core=[("trái cây",10),("trái cây tươi",10),("trái cây sạch",10),("trái cây cao cấp",10),("trái cây hữu cơ",10),
          ("trái cây organic",10),("trái cây theo mùa",10)]
    for x,_ in core: r.append((x,"Core"))

    # 3) CỬA HÀNG / GẦN ĐÂY — cụm cửa hàng + quận chiếm gần hết top gợi ý lặp nhiều nhất; 116 gợi ý tự thêm
    #    "gần đây" kiểu Maps ("trong vòng 800m", "hiện đang mở"). Serper không đo được Map Pack.
    #    Bỏ: "siêu thị trái cây gần đây" (1), "cửa hàng trái cây cao cấp" (2), "…nhập khẩu tphcm" (2),
    #    "…nhập khẩu uy tín tphcm" (1), "mua trái cây ngon ở sài gòn" (1), mọi seed thành phố ngoài HCM.
    store=[("tiệm trái cây",10),("tiệm trái cây nhập khẩu",10),("shop trái cây nhập khẩu",10),("siêu thị trái cây",10),
           ("siêu thị trái cây nhập khẩu",4),("sạp trái cây",10),("cửa hàng trái cây gần đây",10),
           ("tiệm trái cây gần đây",10),("trái cây gần đây",10),("trái cây tươi gần đây",9),
           ("cửa hàng trái cây sạch",10),("cửa hàng trái cây tươi",6),("cửa hàng trái cây uy tín",4),
           ("cửa hàng trái cây tphcm",5),("shop trái cây tphcm",3),("cửa hàng trái cây sài gòn",4),
           ("chuỗi cửa hàng trái cây",3),("chuỗi trái cây nhập khẩu",3),("mua trái cây ở đâu",10),
           ("mua trái cây nhập khẩu ở đâu",3)]
    for x,_ in store: r.append((x,"Store"))

    # 4) ĐỊA BÀN TP.HCM — mẻ đo thử 6 cụm × 3 quận mẫu rồi chọn 3 cụm mạnh nhất (trái cây nhập khẩu 21 ·
    #    cửa hàng trái cây 9 · shop trái cây 8), chạy đủ 23 quận: TB 2,7 gợi ý. Giỏ trái cây × 23 quận đo bổ
    #    sung: 17/23 quận trả 0. Cụm mạnh nhất "trái cây nhập khẩu" giữ ĐỦ 23 quận (1–10 gợi ý; bản đồ quận
    #    liền mạch cho câu hỏi "quận nào có nhu cầu", chỉ tốn ~6 giây); các cụm khác chỉ giữ quận ≥3.
    #    Bỏ cả ma trận "trái cây cắt sẵn × quận" (22/23 quận trả 0–1; seed trần "trái cây cắt sẵn" (10) đã tự
    #    lộ quận 7/gò vấp/thủ đức/bình thạnh/quận 1) và "cửa hàng trái cây nhập khẩu × khu sáp nhập" (0–1).
    local={"trái cây nhập khẩu":DISTRICTS+["bình dương","dĩ an","thuận an","vũng tàu","bà rịa"],
           "cửa hàng trái cây":["quận 1","quận 3","quận 4","quận 7","quận 8","gò vấp"],
           "shop trái cây":["quận 1","quận 5","quận 7","tân bình","tân phú","bình tân","thủ đức"],
           "giỏ trái cây":["quận 7","tân phú","bình thạnh","gò vấp","bình tân","thủ đức","bình dương","dĩ an","vũng tàu"]}
    for t,ds in local.items():
        for d in ds:
            assert d in DISTRICTS or d in ("bình dương","dĩ an","thuận an","vũng tàu","bà rịa")
            r.append((f"{t} {d}","Local"))

    # 5) GIỎ QUÀ — mặt trận sâu nhất: gốc TB 7,6 gợi ý, 0 seed rỗng; gần như toàn ý định giao dịch.
    #    Dịp lộ ra: giỗ/tang 61 gợi ý · Tết 46 · khai trương/tân gia 33 · sinh nhật 16 · trung thu 14.
    #    SERP: Tam Fruit #1 "giỏ trái cây 200k" bằng trang chia theo ngân sách; Farmers Market 6 slot nhóm quà.
    #    Bỏ: "giỏ trái cây thăm người ốm" (1), "giỏ trái cây doanh nghiệp" (1), "giỏ quà tết trái cây nhập khẩu"
    #    (1), "giỏ trái cây 1 triệu" (2), "…1tr" (2), "…8 3" (1), "…biếu tết" (2), "hoa quả biếu tết" (4, lệch
    #    Bắc), "cách làm giỏ trái cây" (10 nhưng là người TỰ LÀM, không phải người mua).
    gift=[("giỏ trái cây nhập khẩu",10),("hộp quà trái cây",10),("hộp trái cây",10),("giỏ quà trái cây",10),
          ("quà tặng trái cây",10),("trái cây quà tặng",10),("giỏ trái cây quà tặng",10),("giỏ trái cây biếu",10),
          ("giỏ trái cây tết",10),("quà tết trái cây",8),("giỏ trái cây sinh nhật",10),("giỏ trái cây khai trương",10),
          ("giỏ trái cây thăm bệnh",3),("giỏ trái cây đám tang",10),("giỏ trái cây đám giỗ",10),("giỏ trái cây viếng",10),
          ("giỏ trái cây cúng",10),("giỏ trái cây 20 10",4),("giỏ trái cây 20 11",5),("giỏ trái cây trung thu",4),
          ("giỏ trái cây dạm ngõ",8),("giỏ trái cây và hoa",10),("giỏ trái cây đẹp",10),("giỏ trái cây cao cấp",4),
          ("giỏ trái cây giá rẻ",7),("giá giỏ trái cây",10),("mẫu giỏ trái cây",9),("giỏ trái cây gần đây",10),
          ("giỏ trái cây tphcm",10),("giỏ trái cây giao tận nơi",6),("đặt giỏ trái cây",10),("mua giỏ trái cây",10),
          ("shop giỏ trái cây",10),("giỏ trái cây 300k",10),("giỏ trái cây 500k",10)]
    for x,_ in gift: r.append((x,"Gift"))

    # 6) CÚNG — thiên về THÔNG TIN (gồm những gì, đặt đâu, kiêng) nhưng có ý định mua ("mua trái cây cúng" (10)).
    #    Nối mùa cúng Mộc An. Lịch âm đã tính (_research/lib/am-lich.mjs): Trung thu 25/09/2026 · rằm tháng 10
    #    23/11/2026 · Ông Táo 30/01/2027 · Tết 06/02/2027 · Vía Thần Tài 15/02/2027 · rằm tháng Giêng 20/02/2027.
    #    Bỏ: "trái cây cúng vu lan" (0 — người miền Nam gõ "rằm tháng 7"/"cô hồn"), "…giao tận nơi" (0),
    #    "…nhập khẩu" (0 — mâm ngũ quả miền Nam kiêng táo/lê, hàng nhập hợp giỏ biếu hơn mâm cúng),
    #    "…ngày rằm" (1), "…30 tết" (1), "…rằm tháng 8" (1), "…rằm tháng 10" (1), "…tân gia" (1),
    #    "trái cây kiêng cúng" (1), "cúng rằm nên mua trái cây gì" (1), "mâm ngũ quả miền bắc" (ngoài địa bàn).
    worship=[("mâm ngũ quả miền nam",10),("mâm ngũ quả ngày tết",10),("mâm trái cây cúng",10),("đặt mâm ngũ quả",10),
             ("mâm ngũ quả cúng khai trương",6),("trái cây cúng rằm",10),("trái cây cúng mùng 1",6),
             ("trái cây cúng tết",10),("trái cây cúng thần tài",10),("trái cây cúng vía thần tài",5),
             ("trái cây cúng ông táo",10),("trái cây cúng khai trương",10),("trái cây cúng đầy tháng",8),
             ("trái cây cúng phật",10),("trái cây cúng ông bà",5),("trái cây cúng gia tiên",4),
             ("trái cây cúng đám giỗ",6),("trái cây cúng rằm tháng 7",4),("trái cây cúng cô hồn",5),
             ("trái cây cúng trung thu",3),("trái cây cúng rằm tháng giêng",4),("trái cây cúng giao thừa",10),
             ("trái cây cúng nhà mới",8),("trái cây cúng nhập trạch",6),("trái cây cúng động thổ",10),
             ("trái cây cúng xe",10),("trái cây cúng gồm những gì",10),("trái cây không nên cúng",5),
             ("dĩa trái cây cúng",10),("mua trái cây cúng",10)]
    for x,_ in worship: r.append((x,"Worship"))

    # 7) GIAO / ONLINE — mặt trận MỎNG: gốc TB 5,2; alphabet "giao trái cây" 17/31 rỗng sau lọc.
    #    SERP ONLINE: 15/18 slot của TP.HCM, 360fruit.vn #1 (giao hỏa tốc 60 phút).
    #    Bỏ: "ship trái cây nhập khẩu" (0), "trái cây online tphcm" (1), "app bán trái cây" (1), "web bán trái
    #    cây" (1), "trái cây nhập khẩu online" (1), "đặt giỏ trái cây online" (1), "trái cây giao nhanh" (1),
    #    "giao trái cây tận nhà" (1), "trái cây giao tận nơi tphcm" (1), "ship trái cây gần đây" (1),
    #    "shop trái cây online" (1), "giao trái cây"/"giao hoa quả" (bỏ dấu thành "giáo án", "giáo xứ"),
    #    "trái cây shopee" (10 nhưng game "thả trái cây shopee" chiếm).
    delivery=[("trái cây online",10),("mua trái cây online",8),("đặt trái cây online",3),("trái cây giao tận nơi",10),
              ("giao trái cây tận nơi",7),("ship trái cây",10),("giao hàng trái cây",4),("app mua trái cây",3)]
    for x,_ in delivery: r.append((x,"Delivery"))

    # 8) GIÁ BÁN LẺ. Bỏ: "trái cây nhập khẩu khuyến mãi" (0), "trái cây đồng giá" (0), "trái cây khuyến mãi"
    #    (1, toàn máy ép), "bảng giá trái cây nhập khẩu" (1), "trái cây nhập khẩu giá rẻ" (1), "…giá tốt" (1),
    #    "trái cây giá rẻ tphcm" (2). GIỮ "giá trái cây tết" dù đo 1 (tháng 9): CỜ CANH mùa Tết 06/02/2027.
    pricing=[("giá trái cây nhập khẩu",10),("giá trái cây",10),("giá trái cây hôm nay",9),("bảng giá trái cây",10),
             ("trái cây giá rẻ",10),("giá các loại trái cây",10),("giá trái cây tết",1)]
    for x,_ in pricing: r.append((x,"Pricing"))

    # 9) SỈ / NGUỒN HÀNG — còn SỐNG trên Suggest: "trái cây nhập khẩu giá sỉ tphcm" (10 seed trả về),
    #    "giá trái cây chợ đầu mối thủ đức hôm nay" (9 seed trả về). SERP nhóm B2B phân mảnh nhất (34 slot/25
    #    domain); nhóm FB "chợ đầu mối trái cây Sài Gòn" #1 "trái cây sỉ tphcm".
    #    Bỏ: "nguồn hàng trái cây nhập khẩu" (1), "nhà cung cấp trái cây nhập khẩu" (1), "chợ đầu mối trái cây
    #    nhập khẩu" (2), "vựa trái cây nhập khẩu" (2), "nhượng quyền trái cây nhập khẩu" (1, người mở shop),
    #    và các cụm lộ ra nhưng query lại chỉ trả chính nó: "lấy sỉ…", "chợ trái cây sỉ tphcm", "vựa trái cây
    #    sỉ sài gòn", "giá trái cây chợ đầu mối thủ đức/bình điền hôm nay", "giá trái cây tại vườn" (đều 1),
    #    "trái cây giá sỉ tphcm" (2) — chúng vẫn hiện qua "giá trái cây chợ đầu mối" (9), "trái cây sỉ" (10).
    wholesale=[("trái cây sỉ",10),("sỉ trái cây nhập khẩu",10),("nhập sỉ trái cây nhập khẩu",9),("mua sỉ trái cây",3),
               ("bỏ sỉ trái cây",3),("kho sỉ trái cây nhập khẩu",4),("tổng kho trái cây nhập khẩu",5),
               ("trái cây nhập khẩu giá sỉ",5),("trái cây sỉ tphcm",3),("vựa trái cây",10),("chợ đầu mối trái cây",10),
               ("chợ trái cây nhập khẩu",6),("giá trái cây chợ đầu mối",9),("nhà cung cấp trái cây",10),
               ("cung cấp trái cây",10),("công ty nhập khẩu trái cây",10),("công ty trái cây nhập khẩu",10),
               ("đại lý trái cây nhập khẩu",4)]
    for x,_ in wholesale: r.append((x,"Wholesale"))

    # 10) B2B — TỔ CHỨC mua để dùng/tặng. Mặt trận CHẾT trên Suggest: 11/33 seed gốc của cụm Sỉ + B2B trả 0, cả 11
    #     đều là seed tổ chức mua (văn phòng, công ty, khách sạn, sự kiện, trường học, có hóa đơn, quà tặng doanh
    #     nghiệp); seed sỉ/nguồn hàng trong cụm không seed nào trả 0 (theoMatTran goc SI_B2B, exports/
    #     trai-cay-suggest.json). SERP "trái cây văn phòng" chỉ 6
    #     organic (eFruit #1, DT-PRO #2); không đơn vị TP.HCM nào công khai giá gói định kỳ (nguồn ngoài).
    #     Giữ phần còn sống + 6 CỜ CANH (0–1 gợi ý ngày 17/09): mặt trận gần khách hiện có của TGD (văn phòng);
    #     tốn ~4 giây/mẻ; ngày Suggest bắt đầu trả gợi ý là tín hiệu thị trường thức dậy.
    #     Bỏ: khách sạn/sự kiện/trường học/có hóa đơn (0), "trái cây tiệc teabreak/buffet", "…cho quán cafe",
    #     "trái cây cúng khai trương công ty/văn phòng mới" (đều 1 — con của "trái cây tiệc", "cung cấp trái
    #     cây", alphabet "trái cây cúng k/v").
    b2b=[("trái cây tiệc",10),("trái cây xuất hóa đơn",3),("trái cây văn phòng",2),("xuất hóa đơn giỏ trái cây",2),
         # cờ canh
         ("trái cây cho văn phòng",0),("cung cấp trái cây cho công ty",0),("quà tặng trái cây doanh nghiệp",0),
         ("trái cây cắt sẵn văn phòng",0),("cung cấp trái cây cho nhà hàng",1),("giỏ trái cây tặng doanh nghiệp",1)]
    for x,_ in b2b: r.append((x,"B2B"))

    # 11) MẶT HÀNG — luôn kèm "nhập khẩu"/xuất xứ/"giá"; không để tên một chữ trần (đồng âm, xem docstring).
    #     Lộ ra nhiều nhất: đồ sấy 43 gợi ý, rồi chuối, xoài, dừa, cherry, táo (envy, rockit, gala NZ, fuji Nam
    #     Phi), nho mẫu đơn/shine muscat. Bỏ: "cam nhập khẩu" (7/10 là "cấm nhập khẩu"), "bơ nhập khẩu" (bơ
    #     lạt/bơ thực vật), "hồng nhập khẩu" (hoa hồng/muối hồng), "nho shine muscat nhập khẩu" (0), "…mua ở
    #     đâu" (0), "nho mẫu đơn mua ở đâu" (1); "giá/mua ở đâu" của lê, cam, bơ, vải, hồng, đào; "dưa lưới/quýt/
    #     xoài/bưởi/thanh long/nhãn mua ở đâu" (≥4/10 là thuốc lá, cây giống, vỏ quýt, đồng hồ quả quýt, kem
    #     xoài, mì thanh long, long nhãn…); "táo mỹ" (Táo Mỹ = chuỗi iPhone); "kiwi new zealand" (nửa là tiếng
    #     Anh bird/slang). Giá quả nội bị giá tại vườn/đầu mối chiếm → chỉ giữ 4 quả nội hay vào giỏ quà.
    product=[("táo nhập khẩu",10),("nho nhập khẩu",10),("cherry nhập khẩu",10),("kiwi nhập khẩu",5),("lê nhập khẩu",10),
             ("mận nhập khẩu",10),("quýt nhập khẩu",8),("lựu nhập khẩu",7),("dâu tây nhập khẩu",7),
             ("dưa lưới nhập khẩu",6),("việt quất nhập khẩu",3),("nho mẫu đơn nhập khẩu",3),("đào nhập khẩu",10),
             ("giá cherry",10),("giá kiwi",10),("giá nho",10),("giá nho mẫu đơn",10),("giá nho shine muscat",5),
             ("giá táo",10),("giá việt quất",9),("giá dâu tây",10),("giá lựu",10),("giá mận",10),("giá dưa lưới",10),
             ("giá quýt",10),("giá sầu riêng",10),("giá măng cụt",10),("giá xoài",10),("giá bưởi",10),
             ("cherry mua ở đâu",10),("kiwi mua ở đâu",10),("việt quất mua ở đâu",10),("sầu riêng mua ở đâu",10),
             ("măng cụt mua ở đâu",10),
             # xuất xứ × mặt hàng. Mùa vụ (nguồn ngoài): cherry Mỹ 5–8, cherry Chile 11–3, cherry NZ 12–2, nho Nam
             # Phi 11–4, kiwi Zespri NZ 5–10; cam quýt California mở cửa 16/03/2026; ND 73/2025 hạ thuế táo 8→5%,
             # cherry 10→5%.
             ("cherry mỹ",10),("cherry úc",9),("cherry chile",10),("cherry new zealand",10),("nho úc",10),("nho mỹ",10),
             ("nho nam phi",10),("nho mẫu đơn hàn quốc",10),("táo envy",10),("táo new zealand",10),("táo gala",10),
             ("kiwi zespri",10),("kiwi vàng",10),("cam úc",10),("quýt úc",10),("lê hàn quốc",8),("dâu tây hàn quốc",10),
             ("việt quất mỹ",10),("dưa lưới nhật",7),
             # dạng hàng: đồ sấy (43 gợi ý tự lộ, hợp giỏ Tết), cắt sẵn (gần nhất với trái cây văn phòng)
             ("trái cây sấy",10),("trái cây cắt sẵn",10),("hộp trái cây cắt sẵn",8)]
    for x,_ in product: r.append((x,"Product"))

    # 12) CHUỖI ĐỐI THỦ — đo nhu cầu điều hướng tới từng chuỗi. Suggest (gợi ý chứa tên): Hoa Biển 55,
    #     Klever 41, Vinfruits 9, Morning Fruit 9. SERP TP.HCM (slot/180): farmersmarket.vn 16, kleverfruits 16,
    #     citifruit 13, morningfruit 9, traicaytonyteo 4, traicayxanh 3, ngonfruit 3; traicay141.vn và
    #     traicay187.com có mặt. Bỏ: "fuji fruit" (chuỗi gốc Bắc, 2 cửa hàng HCM theo trang của họ), "truefruits/
    #     true fruits" (smoothie Đức), "sunfruit" (mỹ phẩm/Peru), "koi fruits" (quán trà Calgary), "hoa biên"
    #     trần (tin hành chính Biên Hòa), "fujifruit" (1), "giỏ trái cây farmers market" (2).
    chain=[("klever fruit",10),("klever fruits",10),("hoa biển",10),("trái cây hoa biển",10),
           ("trái cây nhập khẩu hoa biển",9),("vinfruits",7),("morning fruit",10),("citi fruit",10),("tony fruit",10),
           ("farmers market",10),("tuti fruit",10),("ngon fruit",6),("trái cây 141",7),("trái cây 187",10),
           ("cửa hàng trái cây xanh",7),("trái cây kingfoodmart",3),("trái cây bách hóa xanh",10),("trái cây winmart",10)]
    for x,_ in chain: r.append((x,"Chain"))

    # 13) NIỀM TIN — "trái cây trung quốc có độc không", "táo nhập khẩu có an toàn không", tem mã số 3/4
    #     (14 gợi ý). SERP: 20% trang đích có FAQ, 20% nêu chứng nhận → khoảng trống nội dung.
    #     Bỏ: "trái cây nhập khẩu có an toàn không" (1), "cherry chile có phải của trung quốc không" (1).
    trust=[("trái cây trung quốc",10),("trái cây nhập khẩu mã số",8),("tem trái cây nhập khẩu",3)]
    for x,_ in trust: r.append((x,"Trust"))

    # 14) SỨC KHỎE — 10/10 seed đủ 10 gợi ý nhưng KHÔNG có ý định mua; giữ 6 làm tín hiệu nội dung.
    #     Bỏ "trái cây ăn kiêng" (3), "…nhiều calo" / "…giàu vitamin c" / "…không nên ăn buổi tối" (thuần kiến thức).
    health=[("trái cây giảm cân",10),("trái cây cho bà bầu",10),("trái cây cho người tiểu đường",10),
            ("trái cây tốt cho sức khỏe",10),("trái cây ít đường",10),("trái cây cho bé",10)]
    for x,_ in health: r.append((x,"Health"))

    # 15) TẦNG 2 CÓ CHỌN LỌC — trong 700 seed tầng 2 của mẻ đo (TB chỉ 2,2 gợi ý), giữ đúng những seed
    #     thuộc mặt trận ra tiền, trong địa bàn HCM, có ≥5 gợi ý SẠCH (sau fruit_is_negative). Bỏ các seed
    #     "hoa quả…" (lệch Bắc), "shop trái cây bảo yến" (Cần Thơ), "mâm ngũ quả 2026" (gắn năm, sẽ cũ),
    #     "trái cây si" (mơ hồ: gõ thiếu dấu "sỉ" hay quả cây si).
    tang2=[("cửa hàng trái cây hoa biển","Chain",8),("hoa biển quận 7","Chain",7),("hoa biển tân bình","Chain",6),
           ("cửa hàng trái cây 141","Chain",5),("mùa trái cây","Core",10),
           ("giỏ trái cây viếng đám tang","Gift",10),("giỏ trái cây hoa","Gift",10),("giỏ trái cây hcm","Gift",10),
           ("giỏ trái cây rẻ","Gift",8),("giỏ quà trái cây gần đây","Gift",6),("giỏ trái cây tặng sinh nhật","Gift",6),
           ("giá trái cây nhập","Pricing",10),("giá trái cây các loại","Pricing",10),("giá trái cây rẻ","Pricing",10),
           ("mua trái cây nhập khẩu","Store",10),("trái cây cắt sẵn gần đây","Store",5),
           ("trái cây nhập khẩu sỉ","Wholesale",10),("trái cây nhập sỉ","Wholesale",10),
           ("chợ đầu mối trái cây thủ đức","Wholesale",10),("giá trái cây sỉ","Wholesale",10),
           ("trái cây giá sỉ","Wholesale",10),("công ty xuất nhập khẩu trái cây","Wholesale",10),
           ("nhập trái cây giá sỉ","Wholesale",6),("chợ trái cây sỉ","Wholesale",6),("trái cây sấy sỉ","Wholesale",10),
           ("trái cây cúng nên mua gì","Worship",10),("trái cây cúng 5 loại","Worship",10),
           ("trái cây giao thừa","Worship",10),("trái cây cúng ngày thần tài","Worship",7),
           ("mâm ngũ quả khai trương","Worship",7),("mâm ngũ quả ngày tết miền nam","Worship",6),
           ("trái cây cúng đám tang","Worship",5),("trái cây cúng thần tài ông địa","Worship",5)]
    for x,n,_ in tang2: r.append((x,n))

    # 16) BỔ SUNG SAU KIỂM TOÁN 17/09/2026 — đo Suggest 17/09/2026 09:38 giờ VN (35 seed kiểm toán + canary,
    #     0 lỗi): exports/trai-cay-audit-oos-raw.json (repo app). "(n)" = gợi ý thô / gợi ý SẠCH sau
    #     fruit_is_negative. nhom = nhãn classify_fruit trả cho chính seed.
    #     · Trục mùa vụ đang sống: Trung thu 25/09/2026 (8 ngày nữa; trước đây chỉ có "giỏ trái cây trung thu" 4
    #       và "trái cây cúng trung thu" 3), cụm Tết đã có gợi ý từ tháng 9 (mâm/dĩa/tháp/mẹt chưng tết),
    #       tháp trái cây (cúng/cưới/đám tang/sinh nhật), mua theo THÙNG (envy 9kg, NZ, dazzle — gần sỉ/văn phòng).
    #     · Không dấu: seed chỉ thêm SAU khi classify_fruit thêm dấu cho cụm cố định (_FRUIT_THEM_DAU); đo 17/09
    #       mỗi seed trả 10, đa số gợi ý không dấu ("gio trai cay quan 1", "trai cay cung giao thua").
    #     Bỏ: "hoa qua sach" (10 nhưng 7/10 gắn Hà Nội/tỉnh Bắc — ngoài địa bàn), "360fruit" (2 < ngưỡng 3),
    #     "tâm fruit" (5 nhưng Suggest trả "tâm fruits … biên hòa", "an tâm fruits … thủ đức", "tâm ngọc fruit" —
    #     chưa quy được cho tamfruit.vn trên SERP), "mâm trái cây" (10, trùng mặt trận cúng đã dày),
    #     "cherry mỹ giá"/"táo envy giá"/"kiwi vàng giá" (10/10 sạch nhưng thay seed xuất xứ trần thì mất 18 gợi
    #     ý sạch trên cache 17/09 — giữ seed cũ, chưa thêm), seed B2B "trái cây cho công ty", "đặt trái cây cho
    #     văn phòng", "trái cây cắt sẵn giao tận nơi", "hộp quà trung thu trái cây" (đều 0).
    audit=[("trái cây trung thu","Core",10,8),("trái cây chưng tết","Worship",10,9),("tháp trái cây","Core",10,10),
           ("thùng táo","Product",10,10),
           ("gio trai cay","Gift",10,10),("cua hang trai cay","Store",10,10),("trai cay cung","Worship",10,10)]
    for x,n,_,_ in audit: r.append((x,n))
    return _dedupe(r)


INDUSTRIES = {"food":seeds_food, "realestate":seeds_realestate, "hotel":seeds_hotel,
              "water":seeds_water, "produce":seeds_produce, "vegetarian":seeds_vegetarian,
              "fruit":seeds_fruit}

if __name__ == "__main__":
    for k,f in INDUSTRIES.items():
        s=f(); print(f"{k}: {len(s)} seed")
