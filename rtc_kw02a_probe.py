# -*- coding: utf-8 -*-
"""RTC-KW-02A — zero-gap & query-expansion closure.
Evidence-only: calls Google Suggest and writes artifacts. NO Supabase writes.
Lineage: original seed -> expansion query -> Google suggestion.
"""
import csv, hashlib, json, os, re, time, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

SEEDS_FILE = Path('rtc_kw_02/rtc_seeds_compact.json')
OUT = Path(os.getenv('OUT_DIR', 'rtc_kw_02a_out'))
OUT.mkdir(parents=True, exist_ok=True)
HL = os.getenv('HL', 'vi')
GL = os.getenv('GL', 'vn')
DELAY = float(os.getenv('DELAY', '0.20'))
MAX_SUGGEST = int(os.getenv('MAX_SUGGEST', '10'))


def norm(s):
    s = re.sub(r'\s+', ' ', str(s or '').lower().strip())
    for phrase in ['sơ chế', 'ướp sẵn', 'cắt sẵn', 'gọt sẵn', 'nhặt sẵn']:
        s = s.replace(f'{phrase} {phrase}', phrase)
    return s.strip(' -–—,.;:')


def fetch_suggest(q, retries=3):
    url = ('https://suggestqueries.google.com/complete/search?client=firefox'
           f'&hl={HL}&gl={GL}&q=' + urllib.parse.quote(q))
    err = ''
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode('utf-8', 'replace'))
                vals = data[1] if isinstance(data, list) and len(data) > 1 else []
                return [str(x).strip() for x in vals[:MAX_SUGGEST] if str(x).strip()], '', url
        except Exception as e:
            err = f'{type(e).__name__}: {e}'
            time.sleep(DELAY * attempt)
    return [], err, url


def add(out, q, typ, note=''):
    q = norm(q)
    if 2 < len(q) <= 100:
        out.append((q, typ, note))


def zero_variants(k, fam):
    out, k = [], norm(k)
    repls = [
        (' ready to cook',''), ('ready to cook ',''), (' rtc',''),
        ('sơ chế sẵn','sơ chế'), ('làm sạch sẵn','làm sạch'), ('rửa sạch sẵn','rửa sạch'),
        ('cắt khúc sẵn','cắt khúc'), ('thái lát sẵn','thái lát'), ('fillet sẵn','fillet'),
        ('gọt sẵn','gọt'), ('nhặt sẵn','nhặt'), ('rút chỉ sẵn','rút chỉ'),
        ('ướp sẵn','ướp'), ('chia phần sẵn','chia phần'), ('đóng khay sẵn','đóng khay'),
        ('bóc vỏ rút chỉ','bóc vỏ'), ('sơ chế theo yêu cầu','sơ chế')]
    for a,b in repls:
        if a in k: add(out, k.replace(a,b), 'ZERO_SHORTEN', f'{a}->{b}')
    if k.startswith('thực phẩm ') and len(k.split()) >= 4:
        add(out, k[len('thực phẩm '):], 'ZERO_SHORTEN', 'remove generic noun')
    if k.startswith('nguyên liệu nấu ăn '):
        add(out, k.replace('nguyên liệu nấu ăn ','nguyên liệu '), 'ZERO_SHORTEN', 'shorten phrase')
    for a,b in [('thịt heo ','heo '),('thịt bò ','bò '),('thủy sản ','hải sản '),('fillet','phi lê')]:
        if a in k: add(out, k.replace(a,b), 'ZERO_SYNONYM', f'{a}->{b}')
    if k.startswith('combo '): add(out, 'set '+k[6:], 'ZERO_SYNONYM', 'combo->set')
    if k.startswith('set '): add(out, 'combo '+k[4:], 'ZERO_SYNONYM', 'set->combo')

    if fam == 'RTC-01':
        if 'nguyên liệu' in k:
            for q in ['set nguyên liệu nấu ăn','combo nấu ăn','nguyên liệu sơ chế sẵn']:
                add(out,q,'ZERO_NATURAL','market language')
        add(out,'thực phẩm sơ chế sẵn','ZERO_ANCHOR','validated anchor')
    elif fam == 'RTC-02':
        if k.startswith('thực phẩm '):
            add(out,'đồ ăn '+k[len('thực phẩm '):],'ZERO_NATURAL','noun synonym')
            add(out,'nguyên liệu '+k[len('thực phẩm '):],'ZERO_NATURAL','noun synonym')
        if 'rau củ' in k:
            for p in ['sơ chế','cắt sẵn','gọt sẵn']: add(out,f'rau củ {p}','ZERO_ANCHOR','process anchor')
        if 'hải sản' in k or 'thủy sản' in k:
            for p in ['sơ chế','làm sạch','cắt sẵn']: add(out,f'hải sản {p}','ZERO_ANCHOR','seafood anchor')
    elif fam == 'RTC-03':
        ingredient = re.sub(r'\b(gọt|cắt|nhặt|rửa|sơ chế|bỏ ruột|sẵn|set|vỉ|3 loại|ăn ghém|nguyên liệu|nấu canh chua)\b',' ',k)
        ingredient = norm(ingredient)
        if ingredient and len(ingredient.split()) <= 5:
            add(out,f'{ingredient} sơ chế','ZERO_NATURAL','ingredient + prep')
            add(out,f'{ingredient} cắt sẵn','ZERO_NATURAL','ingredient + cut')
        if 'canh chua' in k:
            add(out,'set canh chua','ZERO_ANCHOR','validated meal wording')
            add(out,'nguyên liệu nấu canh chua','ZERO_NATURAL','shorter meal wording')
    elif fam in ['RTC-04','RTC-05','RTC-06','RTC-07']:
        clean = norm(k.replace(' ready to cook',''))
        add(out,clean,'ZERO_SHORTEN','remove RTC jargon')
        if 'sơ chế' not in clean: add(out,clean+' sơ chế','ZERO_NATURAL','dish + prep')
        if any(x in clean for x in ['kho','nướng','xào','sốt','chiên','bbq','teriyaki','mật ong','sa tế']) and 'ướp sẵn' not in clean:
            add(out,clean+' ướp sẵn','ZERO_NATURAL','dish + marinated')
    elif fam == 'RTC-08':
        clean = norm(k.replace(' ready to cook',''))
        add(out,clean,'ZERO_SHORTEN','remove RTC jargon')
        if not clean.startswith(('set ','combo ')):
            add(out,'set '+clean,'ZERO_NATURAL','set wording')
            add(out,'combo '+clean,'ZERO_NATURAL','combo wording')
        if 'canh' in clean: add(out,'nguyên liệu '+clean,'ZERO_NATURAL','meal ingredients')
    elif fam == 'RTC-09':
        for q in ['thịt ướp sẵn','combo thịt ướp sẵn','thịt ướp nhiều vị']:
            add(out,q,'ZERO_NATURAL','marinade anchor')
    elif fam == 'RTC-10':
        buyer = next((b for b in ['nhà hàng','quán ăn','khách sạn','căn tin','bếp ăn','bếp công nghiệp'] if b in k),'')
        core = 'rau củ sơ chế' if 'rau củ' in k else ('thịt ướp sẵn' if 'thịt ướp' in k else ('thịt sơ chế' if 'thịt sơ chế' in k else ('ready to cook' if 'ready to cook' in k else 'thực phẩm sơ chế')))
        for q in [f'cung cấp {core}',f'{core} giá sỉ',f'{core} tphcm']:
            add(out,q,'ZERO_B2B_REWRITE','commercial rewrite')
        if buyer:
            add(out,f'cung cấp {core} cho {buyer}','ZERO_B2B_REWRITE','buyer-specific')
            add(out,f'{core} cho {buyer}','ZERO_B2B_REWRITE','buyer-specific short')
        if any(x in k for x in ['gia công','oem','nhà máy']):
            add(out,'gia công thực phẩm sơ chế','ZERO_B2B_REWRITE','Vietnamese OEM')
            add(out,'xưởng thực phẩm sơ chế','ZERO_B2B_REWRITE','factory wording')
    elif fam == 'RTC-11':
        core='thực phẩm sơ chế sẵn'
        for q in ['mua '+core, core+' tphcm', core+' gần đây', core+' giao hàng', core+' giá', 'cửa hàng '+core]:
            add(out,q,'ZERO_CONSUMER_REWRITE','consumer wording')
        if 'meal kit' in k:
            add(out,'meal kit tphcm','ZERO_LOCAL','HCMC')
            add(out,'meal kit giao tận nơi','ZERO_CONSUMER_REWRITE','delivery')
        if 'món nấu nhanh' in k:
            add(out,'món ăn nấu nhanh','ZERO_CONSUMER_REWRITE','natural wording')
    elif fam == 'RTC-12':
        topic = k.replace('thực phẩm sơ chế ','').strip()
        if 'hạn sử dụng' in k:
            add(out,'thực phẩm sơ chế để được bao lâu','ZERO_QUALITY_REWRITE','shelf-life question')
            add(out,'bảo quản thực phẩm sơ chế','ZERO_QUALITY_REWRITE','preservation question')
        elif any(x in k for x in ['haccp','iso 22000','vsattp']):
            add(out,'xưởng thực phẩm sơ chế '+topic,'ZERO_QUALITY_REWRITE','certification context')
            add(out,'nhà máy thực phẩm sơ chế '+topic,'ZERO_QUALITY_REWRITE','certification context')
        else:
            add(out,'thực phẩm sơ chế sẵn '+topic,'ZERO_QUALITY_REWRITE','validated core + quality')
            add(out,topic+' thực phẩm sơ chế','ZERO_QUALITY_REWRITE','reordered phrase')

    compact = norm(k.replace(' ready to cook','').replace('ready to cook ','').replace(' sẵn',''))
    if compact and compact != k: add(out,compact,'ZERO_FALLBACK','strip RTC/sẵn')
    base = compact if compact and len(compact) <= len(k) else k
    for q,t in [(base+' tphcm','ZERO_FALLBACK_LOCAL'),(base+' giá','ZERO_FALLBACK_PRICE'),('mua '+base,'ZERO_FALLBACK_PURCHASE')]:
        add(out,q,t,'generic closure probe')
    return dedupe(out, k)


def hit_variants(k, fam, priority):
    out=[]; k=norm(k)
    if fam in ['RTC-01','RTC-02']:
        mods=[('tphcm','HIT_LOCAL'),('gần đây','HIT_LOCAL'),('giá','HIT_PRICE'),('giao tận nơi','HIT_DELIVERY')]
        if priority == 'P0': mods.append(('bán sỉ','HIT_B2B'))
    elif fam in ['RTC-03','RTC-04','RTC-05','RTC-06','RTC-07','RTC-09']:
        mods=[('giá','HIT_PRICE'),('mua ở đâu','HIT_PURCHASE'),('tphcm','HIT_LOCAL')]
        if priority == 'P0': mods += [('giao tận nơi','HIT_DELIVERY'),('bán sỉ','HIT_B2B'),('để được bao lâu','HIT_PRESERVATION')]
    elif fam == 'RTC-08':
        mods=[('giá','HIT_PRICE'),('tphcm','HIT_LOCAL'),('giao tận nơi','HIT_DELIVERY'),('gần đây','HIT_LOCAL')]
    else:
        mods=[('tphcm','HIT_LOCAL')]
    for mod,typ in mods:
        if mod not in k: add(out,k+' '+mod,typ,'expand validated root')
    return dedupe(out,k)


def dedupe(rows, original=''):
    seen=set(); out=[]
    for q,t,n in rows:
        q=norm(q)
        if not q or q == norm(original) or q in seen: continue
        seen.add(q); out.append((q,t,n))
    return out


def wave2_variants(k, fam):
    """More aggressive rescue only for still-zero original seeds."""
    out=[]; k=norm(k)
    # Strip generic RTC/process tokens to recover the market head, then reattach a natural prep term.
    head=re.sub(r'\b(ready to cook|thực phẩm|nguyên liệu|sơ chế|làm sạch|rửa sạch|cắt khúc|cắt miếng|cắt|thái lát|thái|gọt|nhặt|rút chỉ|bóc vỏ|chia phần|đóng khay|hút chân không|đông lạnh|ướp|sẵn|theo yêu cầu|định lượng)\b',' ',k)
    head=norm(head)
    if head and len(head)>=3:
        add(out,head,'W2_HEAD','head term')
        if fam in ['RTC-03','RTC-04','RTC-05','RTC-06','RTC-07']:
            add(out,head+' sơ chế','W2_HEAD_PREP','head + prep')
            add(out,head+' cắt sẵn','W2_HEAD_CUT','head + cut')
        if fam in ['RTC-04','RTC-05','RTC-06','RTC-07','RTC-09']:
            add(out,head+' ướp sẵn','W2_HEAD_MARINADE','head + marinade')
        add(out,head+' tphcm','W2_HEAD_LOCAL','head + HCMC')
    return dedupe(out,k)


def write_csv(path, rows, fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)


def main():
    seeds=json.loads(SEEDS_FILE.read_text(encoding='utf-8'))
    if len(seeds)!=290: raise SystemExit(f'Expected 290 seeds, got {len(seeds)}')
    seed_rows=[{'seed_id':x[0],'keyword':norm(x[1]),'family_code':x[2],'priority':x[3],'rtc_fit':x[4]} for x in seeds]
    started=datetime.now(timezone.utc)

    # Re-measure roots so this run is self-contained.
    root_cov=[]; root_raw=[]
    for i,s in enumerate(seed_rows,1):
        vals,err,url=fetch_suggest(s['keyword'])
        status='ERROR' if err else ('HIT' if vals else 'ZERO')
        root_cov.append({**s,'status':status,'suggestion_count':len(vals),'error':err})
        for rank,v in enumerate(vals,1):
            root_raw.append({**s,'query_type':'ROOT','query':s['keyword'],'rank':rank,'suggestion':v,'suggestion_norm':norm(v),'source_url':url})
        if i%50==0: print(f'ROOT {i}/290')
        time.sleep(DELAY)

    status_by_seed={r['seed_id']:r['status'] for r in root_cov}
    # Build Wave 1 query master + many-to-many lineage.
    lineage=[]
    for s in seed_rows:
        exps=zero_variants(s['keyword'],s['family_code']) if status_by_seed[s['seed_id']]=='ZERO' else hit_variants(s['keyword'],s['family_code'],s['priority'])
        for q,t,n in exps:
            lineage.append({**s,'origin_status':status_by_seed[s['seed_id']],'expansion_query':q,'expansion_type':t,'expansion_note':n,'wave':'W1'})
    byq=defaultdict(list)
    for r in lineage: byq[r['expansion_query']].append(r)
    qmaster=[]
    for q,rs in sorted(byq.items()):
        qid='RTCQ-'+hashlib.sha1(q.encode('utf-8')).hexdigest()[:10].upper()
        qmaster.append({'query_id':qid,'query':q,'origin_seed_ids':'|'.join(sorted({r['seed_id'] for r in rs})),
                        'origin_statuses':'|'.join(sorted({r['origin_status'] for r in rs})),
                        'family_codes':'|'.join(sorted({r['family_code'] for r in rs})),
                        'expansion_types':'|'.join(sorted({r['expansion_type'] for r in rs})),'wave':'W1'})
    qid_by_q={r['query']:r['query_id'] for r in qmaster}
    for r in lineage: r['query_id']=qid_by_q[r['expansion_query']]

    query_cov=[]; exp_raw=[]
    for i,q in enumerate(qmaster,1):
        vals,err,url=fetch_suggest(q['query'])
        st='ERROR' if err else ('HIT' if vals else 'ZERO')
        query_cov.append({**q,'status':st,'suggestion_count':len(vals),'error':err})
        for rank,v in enumerate(vals,1):
            exp_raw.append({**q,'rank':rank,'suggestion':v,'suggestion_norm':norm(v),'source_url':url})
        if i%100==0: print(f'W1 {i}/{len(qmaster)}')
        time.sleep(DELAY)

    hit_q={r['query_id']:r for r in query_cov if r['status']=='HIT'}
    hit_by_seed=defaultdict(list)
    for l in lineage:
        if l['query_id'] in hit_q: hit_by_seed[l['seed_id']].append((l,hit_q[l['query_id']]))
    still_zero=[s for s in seed_rows if status_by_seed[s['seed_id']]=='ZERO' and not hit_by_seed[s['seed_id']]]

    # Wave 2: aggressive but bounded rescue of still-zero roots.
    w2_lineage=[]
    existing_queries=set(byq)
    for s in still_zero:
        for q,t,n in wave2_variants(s['keyword'],s['family_code']):
            if q in existing_queries: continue
            existing_queries.add(q)
            qid='RTCQ-'+hashlib.sha1(q.encode('utf-8')).hexdigest()[:10].upper()
            w2_lineage.append({**s,'origin_status':'ZERO','expansion_query':q,'expansion_type':t,'expansion_note':n,'wave':'W2','query_id':qid})
    w2_q=[]
    for l in w2_lineage:
        vals,err,url=fetch_suggest(l['expansion_query'])
        st='ERROR' if err else ('HIT' if vals else 'ZERO')
        qc={'query_id':l['query_id'],'query':l['expansion_query'],'origin_seed_ids':l['seed_id'],'origin_statuses':'ZERO','family_codes':l['family_code'],'expansion_types':l['expansion_type'],'wave':'W2','status':st,'suggestion_count':len(vals),'error':err}
        w2_q.append(qc)
        if st=='HIT': hit_by_seed[l['seed_id']].append((l,qc))
        for rank,v in enumerate(vals,1):
            exp_raw.append({**qc,'rank':rank,'suggestion':v,'suggestion_norm':norm(v),'source_url':url})
        time.sleep(DELAY)
    lineage += w2_lineage; query_cov += w2_q

    # Original seed closure ledger.
    closure=[]
    for s in seed_rows:
        sid=s['seed_id']; orig=status_by_seed[sid]
        lrows=[x for x in lineage if x['seed_id']==sid]
        hits=hit_by_seed[sid]
        if orig=='HIT': c='ORIGINAL_HIT'
        elif hits: c='RECOVERED'
        elif orig=='ERROR': c='ROOT_ERROR'
        else: c='STILL_ZERO'
        best=max((h[1] for h in hits), key=lambda x:x['suggestion_count'], default=None)
        closure.append({**s,'original_status':orig,'expansion_query_count':len(lrows),'hit_expansion_query_count':len(hits),
                        'closure_status':c,'best_hit_query':best['query'] if best else '',
                        'best_hit_suggestion_count':best['suggestion_count'] if best else 0,
                        'waves_used':'W1+W2' if any(x['wave']=='W2' for x in lrows) else 'W1'})

    # Family closure summary.
    fam=[]
    for f in sorted({s['family_code'] for s in seed_rows}):
        rows=[r for r in closure if r['family_code']==f]
        fam.append({'family_code':f,'seed_count':len(rows),
                    'original_hit':sum(r['closure_status']=='ORIGINAL_HIT' for r in rows),
                    'recovered':sum(r['closure_status']=='RECOVERED' for r in rows),
                    'still_zero':sum(r['closure_status']=='STILL_ZERO' for r in rows),
                    'final_evidence_seeds':sum(r['closure_status'] in ('ORIGINAL_HIT','RECOVERED') for r in rows)})

    # Demand-signal leaderboard across expansion suggestions.
    sig=defaultdict(lambda:{'query_count':0,'origin_seeds':set(),'best_rank':99,'rank_sum':0,'rows':0})
    lineage_by_q=defaultdict(set)
    for l in lineage: lineage_by_q[l['query_id']].add(l['seed_id'])
    for r in exp_raw:
        k=r['suggestion_norm']; d=sig[k]; d['query_count']+=1; d['origin_seeds'] |= lineage_by_q[r['query_id']]; d['best_rank']=min(d['best_rank'],r['rank']); d['rank_sum']+=r['rank']; d['rows']+=1
    signals=[]
    for k,d in sig.items():
        signals.append({'suggestion':k,'query_hits':d['query_count'],'origin_seed_count':len(d['origin_seeds']),
                        'best_rank':d['best_rank'],'avg_rank':round(d['rank_sum']/d['rows'],2)})
    signals.sort(key=lambda x:(-x['origin_seed_count'],-x['query_hits'],x['avg_rank']))

    write_csv(OUT/'root_coverage_290.csv',root_cov,list(root_cov[0].keys()))
    write_csv(OUT/'expansion_lineage.csv',lineage,list(lineage[0].keys()))
    write_csv(OUT/'expansion_query_coverage.csv',query_cov,list(query_cov[0].keys()))
    write_csv(OUT/'expansion_suggest_raw.csv',exp_raw,list(exp_raw[0].keys()))
    write_csv(OUT/'seed_closure_290.csv',closure,list(closure[0].keys()))
    write_csv(OUT/'family_closure.csv',fam,list(fam[0].keys()))
    write_csv(OUT/'demand_signals.csv',signals,list(signals[0].keys()))
    summary={'phase':'RTC-KW-02A','mode':'EVIDENCE_ONLY_NO_DB_WRITE','started_at_utc':started.isoformat(),
             'finished_at_utc':datetime.now(timezone.utc).isoformat(),'seed_count':len(seed_rows),
             'original_hit':sum(r['closure_status']=='ORIGINAL_HIT' for r in closure),
             'recovered':sum(r['closure_status']=='RECOVERED' for r in closure),
             'still_zero':sum(r['closure_status']=='STILL_ZERO' for r in closure),
             'final_evidence_seeds':sum(r['closure_status'] in ('ORIGINAL_HIT','RECOVERED') for r in closure),
             'w1_unique_queries':len(qmaster),'w2_queries':len(w2_q),'total_expansion_queries':len(query_cov),
             'hit_expansion_queries':sum(r['status']=='HIT' for r in query_cov),
             'expansion_suggestion_rows':len(exp_raw),'unique_expansion_suggestions':len(sig),
             'request_errors':sum(r['status']=='ERROR' for r in root_cov)+sum(r['status']=='ERROR' for r in query_cov),
             'hl':HL,'gl':GL,'delay_seconds':DELAY,'max_suggest_per_query':MAX_SUGGEST}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__': main()
