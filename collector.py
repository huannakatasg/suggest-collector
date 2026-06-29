# -*- coding: utf-8 -*-
"""
Collector Suggest -> Supabase (chạy trên GitHub Actions, không giới hạn 6 phút).
Mỗi lần chạy: nạp seed vào keyword_master, cào Google Suggest từng seed,
phân loại intent, lọc negative, ghi vào suggest_raw qua RPC public.suggest_insert_raw.

ENV bắt buộc (đặt ở GitHub Secrets):
  SUPABASE_URL                 vd https://xxxx.supabase.co
  SUPABASE_SERVICE_ROLE_KEY    service_role key (KHÔNG public)
ENV tùy chọn:
  INDUSTRIES=food,realestate,hotel,water   (mặc định cả 4)
  DELAY=0.6                            giây giữa các request (an toàn)
  MAX_SUGGEST=10
"""
import os
import sys
import time
import json
import urllib.parse
import urllib.request

import seeds
import classify

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
INDUSTRIES = [x.strip() for x in os.environ.get("INDUSTRIES", "food,realestate,hotel,water").split(",") if x.strip()]
DELAY = float(os.environ.get("DELAY", "0.6"))
MAX_SUGGEST = int(os.environ.get("MAX_SUGGEST", "10"))
HL, GL = "vi", "vn"

if not SUPABASE_URL or not SERVICE_KEY:
    print("Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY")
    sys.exit(1)


def rpc(fn, payload):
    req = urllib.request.Request(
        f"{SUPABASE_URL}/rest/v1/rpc/{fn}",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "apikey": SERVICE_KEY,
            "Authorization": f"Bearer {SERVICE_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8") or "null")


def fetch_suggest(keyword, retries=2):
    url = ("https://suggestqueries.google.com/complete/search?client=firefox"
           f"&hl={HL}&gl={GL}&q=" + urllib.parse.quote(keyword))
    for a in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read().decode("utf-8", "replace"))
                return data[1] if isinstance(data, list) and len(data) > 1 else []
        except Exception:
            time.sleep(DELAY * a)
    return []


def chunked(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def run_industry(ind):
    seed_list = seeds.INDUSTRIES[ind]()
    classifier = classify.CLASSIFIERS[ind]
    is_neg = classify.NEGATIVE.get(ind)
    print(f"[{ind}] {len(seed_list)} seed")

    # 1) upsert keyword_master
    upserted = 0
    for batch in chunked(seed_list, 500):
        upserted += rpc("suggest_upsert_keywords", {"p_industry": ind, "p_rows": batch}) or 0
    print(f"[{ind}] keyword_master +{upserted} mới")

    # 2) cào Suggest -> gom rows
    rows, skipped, done = [], 0, 0
    for it in seed_list:
        kw, nhom = it["keyword"], it["nhom"]
        for rk, sug in enumerate(fetch_suggest(kw)[:MAX_SUGGEST], start=1):
            sug = (sug or "").strip()
            if not sug:
                continue
            if is_neg and is_neg(sug):
                skipped += 1
                continue
            rows.append({"keyword_goc": kw, "nhom": nhom, "goi_y": sug,
                         "rank": rk, "intent": classifier(sug)})
        done += 1
        if done % 200 == 0:
            print(f"[{ind}] ...{done}/{len(seed_list)} seed, {len(rows)} gợi ý")
        time.sleep(DELAY)

    # 3) ghi suggest_raw theo batch (ngày = hôm nay, server tự gán)
    import datetime
    today = datetime.date.today().isoformat()
    inserted = 0
    for batch in chunked(rows, 500):
        inserted += rpc("suggest_insert_raw", {"p_industry": ind, "p_ngay": today, "p_rows": batch}) or 0
    print(f"[{ind}] suggest_raw +{inserted} dòng (lọc bỏ {skipped})")
    return inserted


def main():
    total = 0
    for ind in INDUSTRIES:
        if ind not in seeds.INDUSTRIES:
            print(f"Bỏ qua ngành lạ: {ind}")
            continue
        total += run_industry(ind)
    # dọn dữ liệu > 90 ngày
    try:
        pruned = rpc("suggest_prune", {"p_days": 90})
        print(f"prune: xoá {pruned} dòng cũ")
    except Exception as e:
        print("prune lỗi:", e)
    print(f"XONG. Tổng ghi {total} dòng.")


if __name__ == "__main__":
    main()
