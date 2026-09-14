# -*- coding: utf-8 -*-
import csv, hashlib, json, os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import rtc_kw02a_probe as rules

OUT=Path('rtc_kw_02a_w2_out'); OUT.mkdir(exist_ok=True)
TARGET=set(['RTC-SEED-043','RTC-SEED-114','RTC-SEED-120','RTC-SEED-121','RTC-SEED-127','RTC-SEED-129','RTC-SEED-130','RTC-SEED-132','RTC-SEED-144','RTC-SEED-145','RTC-SEED-146','RTC-SEED-170','RTC-SEED-188','RTC-SEED-192','RTC-SEED-201','RTC-SEED-202','RTC-SEED-203','RTC-SEED-204','RTC-SEED-225','RTC-SEED-257','RTC-SEED-258','RTC-SEED-259','RTC-SEED-260','RTC-SEED-281','RTC-SEED-283','RTC-SEED-284','RTC-SEED-286','RTC-SEED-287','RTC-SEED-288','RTC-SEED-289','RTC-SEED-290'])

def add(rows,s,q,t):
    q=rules.norm(q)
    if q and q!=s['keyword']:
        rows.append({**s,'query':q,'query_type':t,'query_id':'RTCQ-'+hashlib.sha1(q.encode()).hexdigest()[:10].upper()})

def extra(s):
    k=s['keyword']; f=s['family_code']; out=[]
    for q,t,n in rules.wave2_variants(k,f): add(out,s,q,t)
    # Explicit natural-language rescue for remaining hard gaps.
    if s['seed_id']=='RTC-SEED-043':
        for q in ['tôm bóc vỏ rút chỉ','tôm rút chỉ','tôm bóc vỏ']: add(out,s,q,'W2_NATURAL')
    if s['seed_id']=='RTC-SEED-114':
        for q in ['thịt heo chia phần','thịt heo đóng khay','thịt heo portion']: add(out,s,q,'W2_NATURAL')
    if s['seed_id'] in {'RTC-SEED-120','RTC-SEED-121'}:
        for q in ['bò lúc lắc','thịt bò lúc lắc']: add(out,s,q,'W2_DISH_HEAD')
    if s['seed_id']=='RTC-SEED-127':
        for q in ['bò ăn lẩu','thịt bò ăn lẩu','bò nhúng lẩu']: add(out,s,q,'W2_DISH_HEAD')
    if s['seed_id']=='RTC-SEED-129':
        for q in ['bò cuộn nấm','thịt bò cuộn nấm']: add(out,s,q,'W2_DISH_HEAD')
    if s['seed_id']=='RTC-SEED-130':
        for q in ['bò cuộn phô mai','thịt bò cuộn phô mai']: add(out,s,q,'W2_DISH_HEAD')
    if s['seed_id']=='RTC-SEED-132':
        for q in ['thịt bò chia phần','thịt bò đóng khay','bò portion']: add(out,s,q,'W2_NATURAL')
    if s['seed_id'] in {'RTC-SEED-144','RTC-SEED-145','RTC-SEED-146'}:
        for q in ['đùi gà ướp','đùi gà nướng','đùi gà kho gừng','má đùi gà']: add(out,s,q,'W2_DISH_HEAD')
    if s['seed_id']=='RTC-SEED-170':
        for q in ['cá hồi portion','cá hồi cắt khúc','cá hồi cắt miếng']: add(out,s,q,'W2_NATURAL')
    if s['seed_id']=='RTC-SEED-188':
        for q in ['hải sản làm sạch','hải sản sơ chế','hải sản làm sẵn']: add(out,s,q,'W2_NATURAL')
    if s['seed_id']=='RTC-SEED-192':
        for q in ['nguyên liệu canh chua','set canh chua','combo canh chua']: add(out,s,q,'W2_MEAL_HEAD')
    if s['seed_id'] in {'RTC-SEED-201','RTC-SEED-202','RTC-SEED-203','RTC-SEED-204'}:
        dish=k.replace('combo ','').replace('set ','')
        for q in [dish,'set '+dish,'nguyên liệu '+dish]: add(out,s,q,'W2_MEAL_HEAD')
    if s['seed_id']=='RTC-SEED-225':
        for q in ['meal kit việt nam','meal kit món ăn việt','set nguyên liệu món việt']: add(out,s,q,'W2_MEAL_HEAD')
    if s['family_code']=='RTC-10':
        core='rau củ sơ chế' if 'rau củ' in k else 'thịt sơ chế'
        for q in [core+' giá sỉ','cung cấp '+core,core+' tphcm',core+' cho nhà hàng']: add(out,s,q,'W2_B2B')
    if s['family_code']=='RTC-12':
        topic=k.replace('thực phẩm sơ chế ','')
        for q in [topic,'thực phẩm sơ chế sẵn '+topic,'xưởng sơ chế thực phẩm '+topic,'nhà máy thực phẩm '+topic]: add(out,s,q,'W2_QUALITY')
    # dedupe
    seen=set(); ret=[]
    for r in out:
        if r['query'] not in seen: seen.add(r['query']); ret.append(r)
    return ret

def write(path,rows,fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    raw=json.loads(Path('rtc_kw_02/rtc_seeds_compact.json').read_text(encoding='utf-8'))
    seeds=[{'seed_id':x[0],'keyword':rules.norm(x[1]),'family_code':x[2],'priority':x[3],'rtc_fit':x[4]} for x in raw if x[0] in TARGET]
    queries=[]
    for s in seeds: queries.extend(extra(s))
    # dedupe query globally but preserve lineage separately
    unique={r['query_id']:r for r in queries}
    cov=[]; sug=[]
    def one(r):
        vals,err,url=rules.fetch_suggest(r['query']); st='ERROR' if err else ('HIT' if vals else 'ZERO'); return r,vals,err,url,st
    with ThreadPoolExecutor(max_workers=8) as ex:
        for fut in as_completed([ex.submit(one,r) for r in unique.values()]):
            r,vals,err,url,st=fut.result(); cov.append({**r,'status':st,'suggestion_count':len(vals),'error':err})
            for rank,v in enumerate(vals,1): sug.append({**r,'rank':rank,'suggestion':v,'suggestion_norm':rules.norm(v),'source_url':url})
    hit={r['query_id'] for r in cov if r['status']=='HIT'}
    closure=[]
    for s in seeds:
        own=[r for r in queries if r['seed_id']==s['seed_id']]
        h=[r for r in own if r['query_id'] in hit]
        closure.append({**s,'w2_query_count':len(own),'w2_hit_query_count':len(h),'w2_status':'RECOVERED_W2' if h else 'STILL_ZERO','best_hit_query':h[0]['query'] if h else ''})
    write(OUT/'w2_lineage.csv',queries,list(queries[0].keys()))
    write(OUT/'w2_query_coverage.csv',cov,list(cov[0].keys()))
    write(OUT/'w2_suggest_raw.csv',sug,list(sug[0].keys()))
    write(OUT/'w2_seed_closure.csv',closure,list(closure[0].keys()))
    summary={'target_seeds':len(seeds),'unique_w2_queries':len(unique),'hit_w2_queries':sum(r['status']=='HIT' for r in cov),'error_queries':sum(r['status']=='ERROR' for r in cov),'recovered_w2':sum(r['w2_status']=='RECOVERED_W2' for r in closure),'still_zero_after_w2':sum(r['w2_status']=='STILL_ZERO' for r in closure),'suggestion_rows':len(sug),'unique_suggestions':len({r['suggestion_norm'] for r in sug})}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__': main()
