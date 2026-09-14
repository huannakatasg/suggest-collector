# -*- coding: utf-8 -*-
"""RTC-KW-02 evidence-only Google Suggest materialization.
Reads the 290 canonical RTC seeds, calls Google Suggest, and writes local artifacts.
NO Supabase writes. Safe to run on an isolated branch/action.
"""
import csv, json, os, time, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HL=os.getenv('HL','vi')
GL=os.getenv('GL','vn')
DELAY=float(os.getenv('DELAY','0.25'))
MAX_SUGGEST=int(os.getenv('MAX_SUGGEST','10'))
OUT=Path(os.getenv('OUT_DIR','rtc_kw_02_out'))
OUT.mkdir(parents=True, exist_ok=True)


def fetch_suggest(keyword, retries=3):
    url=("https://suggestqueries.google.com/complete/search?client=firefox"
         f"&hl={HL}&gl={GL}&q="+urllib.parse.quote(keyword))
    last_error=''
    for attempt in range(1,retries+1):
        try:
            req=urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                data=json.loads(r.read().decode('utf-8','replace'))
                vals=data[1] if isinstance(data,list) and len(data)>1 else []
                return vals[:MAX_SUGGEST], '', url
        except Exception as e:
            last_error=f'{type(e).__name__}: {e}'
            time.sleep(DELAY*attempt)
    return [], last_error, url


def norm(s):
    return ' '.join((s or '').lower().strip().split())


def load_seeds():
    data=json.loads(Path('rtc_kw_02/rtc_seeds_compact.json').read_text(encoding='utf-8'))
    rows=[]
    for seed_id,keyword,family,priority,rtc_fit in data:
        rows.append({'seed_id':seed_id,'keyword_goc':keyword,'family_code':family,
                     'priority':priority,'rtc_fit':rtc_fit,'classifier_version':'rtc-ontology-v1.0'})
    seen=set(); out=[]
    for r in rows:
        k=norm(r['keyword_goc'])
        if k and k not in seen:
            seen.add(k); out.append(r)
    return out


def main():
    seeds=load_seeds()
    if len(seeds)!=290:
        raise SystemExit(f'Expected 290 unique active seeds, got {len(seeds)}')
    raw=[]; coverage=[]; errors=0; hits=0; total_suggestions=0
    started=datetime.now(timezone.utc)
    for idx,s in enumerate(seeds,1):
        kw=s['keyword_goc'].strip()
        vals,err,url=fetch_suggest(kw)
        if err: errors+=1
        if vals: hits+=1
        total_suggestions += len(vals)
        fetched=datetime.now(timezone.utc).isoformat()
        for rank,sug in enumerate(vals,1):
            raw.append({
                'fetched_at_utc':fetched,'seed_id':s['seed_id'],'industry':'rtc',
                'family_code':s['family_code'],'priority':s['priority'],'rtc_fit':s['rtc_fit'],
                'keyword_goc':kw,'rank':rank,'goi_y':str(sug).strip(),
                'suggestion_norm':norm(sug),'self_match':str(norm(sug)==norm(kw)).upper(),
                'hl':HL,'gl':GL,'classifier_version':s['classifier_version'],'source_url':url,
            })
        coverage.append({
            'seed_id':s['seed_id'],'family_code':s['family_code'],'priority':s['priority'],
            'rtc_fit':s['rtc_fit'],'keyword_goc':kw,'suggestion_count':len(vals),
            'status':'ERROR' if err else ('HIT' if vals else 'ZERO'),'error':err,
        })
        if idx%25==0 or idx==len(seeds):
            print(f'{idx}/{len(seeds)} seeds | hits={hits} | suggestions={total_suggestions} | errors={errors}')
        time.sleep(DELAY)

    raw_fields=['fetched_at_utc','seed_id','industry','family_code','priority','rtc_fit','keyword_goc','rank','goi_y','suggestion_norm','self_match','hl','gl','classifier_version','source_url']
    with open(OUT/'rtc_kw_02_suggest_raw.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=raw_fields); w.writeheader(); w.writerows(raw)
    cov_fields=['seed_id','family_code','priority','rtc_fit','keyword_goc','suggestion_count','status','error']
    with open(OUT/'rtc_kw_02_seed_coverage.csv','w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=cov_fields); w.writeheader(); w.writerows(coverage)
    unique_suggestions=len({r['suggestion_norm'] for r in raw if r['suggestion_norm']})
    summary={
        'phase':'RTC-KW-02','mode':'EVIDENCE_ONLY_NO_DB_WRITE','started_at_utc':started.isoformat(),
        'finished_at_utc':datetime.now(timezone.utc).isoformat(),'hl':HL,'gl':GL,
        'seed_count':len(seeds),'hit_seed_count':hits,'zero_seed_count':sum(1 for r in coverage if r['status']=='ZERO'),
        'error_seed_count':errors,'raw_suggestion_rows':len(raw),'unique_suggestions':unique_suggestions,
        'max_suggest_per_seed':MAX_SUGGEST,'delay_seconds':DELAY,
    }
    (OUT/'rtc_kw_02_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__': main()
