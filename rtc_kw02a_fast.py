# -*- coding: utf-8 -*-
"""Fast evidence-only W1 for RTC-KW-02A using Phase-02 root baseline.
No Supabase writes. Concurrent GETs to Google Suggest with bounded workers.
"""
import csv, hashlib, json, os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import rtc_kw02a_probe as rules

OUT=Path('rtc_kw_02a_fast_out'); OUT.mkdir(exist_ok=True)
WORKERS=int(os.getenv('WORKERS','8'))
ZERO_IDS=set(['RTC-SEED-010','RTC-SEED-011','RTC-SEED-012','RTC-SEED-020','RTC-SEED-021','RTC-SEED-022','RTC-SEED-023','RTC-SEED-024','RTC-SEED-031','RTC-SEED-036','RTC-SEED-039','RTC-SEED-040','RTC-SEED-041','RTC-SEED-043','RTC-SEED-044','RTC-SEED-045','RTC-SEED-047','RTC-SEED-048','RTC-SEED-049','RTC-SEED-050','RTC-SEED-057','RTC-SEED-060','RTC-SEED-061','RTC-SEED-062','RTC-SEED-065','RTC-SEED-066','RTC-SEED-067','RTC-SEED-068','RTC-SEED-069','RTC-SEED-070','RTC-SEED-071','RTC-SEED-073','RTC-SEED-076','RTC-SEED-078','RTC-SEED-079','RTC-SEED-080','RTC-SEED-081','RTC-SEED-082','RTC-SEED-083','RTC-SEED-084','RTC-SEED-086','RTC-SEED-087','RTC-SEED-090','RTC-SEED-093','RTC-SEED-095','RTC-SEED-097','RTC-SEED-098','RTC-SEED-099','RTC-SEED-103','RTC-SEED-104','RTC-SEED-105','RTC-SEED-107','RTC-SEED-108','RTC-SEED-109','RTC-SEED-110','RTC-SEED-114','RTC-SEED-115','RTC-SEED-118','RTC-SEED-120','RTC-SEED-121','RTC-SEED-122','RTC-SEED-125','RTC-SEED-126','RTC-SEED-127','RTC-SEED-128','RTC-SEED-129','RTC-SEED-130','RTC-SEED-131','RTC-SEED-132','RTC-SEED-134','RTC-SEED-135','RTC-SEED-137','RTC-SEED-139','RTC-SEED-142','RTC-SEED-143','RTC-SEED-144','RTC-SEED-145','RTC-SEED-146','RTC-SEED-148','RTC-SEED-150','RTC-SEED-152','RTC-SEED-153','RTC-SEED-154','RTC-SEED-155','RTC-SEED-156','RTC-SEED-158','RTC-SEED-159','RTC-SEED-160','RTC-SEED-161','RTC-SEED-162','RTC-SEED-163','RTC-SEED-167','RTC-SEED-168','RTC-SEED-169','RTC-SEED-170','RTC-SEED-174','RTC-SEED-176','RTC-SEED-177','RTC-SEED-178','RTC-SEED-179','RTC-SEED-180','RTC-SEED-182','RTC-SEED-184','RTC-SEED-185','RTC-SEED-186','RTC-SEED-188','RTC-SEED-189','RTC-SEED-190','RTC-SEED-192','RTC-SEED-193','RTC-SEED-194','RTC-SEED-195','RTC-SEED-196','RTC-SEED-197','RTC-SEED-198','RTC-SEED-199','RTC-SEED-200','RTC-SEED-201','RTC-SEED-202','RTC-SEED-203','RTC-SEED-204','RTC-SEED-205','RTC-SEED-206','RTC-SEED-207','RTC-SEED-208','RTC-SEED-209','RTC-SEED-210','RTC-SEED-224','RTC-SEED-225','RTC-SEED-245','RTC-SEED-246','RTC-SEED-249','RTC-SEED-250','RTC-SEED-251','RTC-SEED-252','RTC-SEED-253','RTC-SEED-254','RTC-SEED-255','RTC-SEED-256','RTC-SEED-257','RTC-SEED-258','RTC-SEED-259','RTC-SEED-260','RTC-SEED-261','RTC-SEED-262','RTC-SEED-263','RTC-SEED-264','RTC-SEED-265','RTC-SEED-266','RTC-SEED-268','RTC-SEED-269','RTC-SEED-270','RTC-SEED-271','RTC-SEED-272','RTC-SEED-273','RTC-SEED-274','RTC-SEED-275','RTC-SEED-276','RTC-SEED-277','RTC-SEED-278','RTC-SEED-279','RTC-SEED-280','RTC-SEED-281','RTC-SEED-282','RTC-SEED-283','RTC-SEED-284','RTC-SEED-285','RTC-SEED-286','RTC-SEED-287','RTC-SEED-288','RTC-SEED-289','RTC-SEED-290'])

def write_csv(path, rows, fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    raw_seeds=json.loads(Path('rtc_kw_02/rtc_seeds_compact.json').read_text(encoding='utf-8'))
    seeds=[{'seed_id':x[0],'keyword':rules.norm(x[1]),'family_code':x[2],'priority':x[3],'rtc_fit':x[4]} for x in raw_seeds]
    lineage=[]
    for s in seeds:
        st='ZERO' if s['seed_id'] in ZERO_IDS else 'HIT'
        exps=rules.zero_variants(s['keyword'],s['family_code']) if st=='ZERO' else rules.hit_variants(s['keyword'],s['family_code'],s['priority'])
        for q,t,n in exps:
            lineage.append({**s,'origin_status':st,'expansion_query':q,'expansion_type':t,'expansion_note':n})
    byq=defaultdict(list)
    for r in lineage: byq[r['expansion_query']].append(r)
    qmaster=[]
    for q,rs in sorted(byq.items()):
        qid='RTCQ-'+hashlib.sha1(q.encode()).hexdigest()[:10].upper()
        qmaster.append({'query_id':qid,'query':q,'origin_seed_ids':'|'.join(sorted({r['seed_id'] for r in rs})),'origin_statuses':'|'.join(sorted({r['origin_status'] for r in rs})),'family_codes':'|'.join(sorted({r['family_code'] for r in rs})),'expansion_types':'|'.join(sorted({r['expansion_type'] for r in rs}))})
    qid={r['query']:r['query_id'] for r in qmaster}
    for r in lineage: r['query_id']=qid[r['expansion_query']]
    print('queries',len(qmaster),'lineage',len(lineage),'workers',WORKERS)

    def one(q):
        vals,err,url=rules.fetch_suggest(q['query'])
        st='ERROR' if err else ('HIT' if vals else 'ZERO')
        return q,vals,err,url,st

    coverage=[]; sugg=[]; done=0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs=[ex.submit(one,q) for q in qmaster]
        for fut in as_completed(futs):
            q,vals,err,url,st=fut.result(); done+=1
            coverage.append({**q,'status':st,'suggestion_count':len(vals),'error':err})
            for rank,v in enumerate(vals,1): sugg.append({**q,'rank':rank,'suggestion':v,'suggestion_norm':rules.norm(v),'source_url':url})
            if done%100==0: print(done,'/',len(qmaster))

    hit_ids={r['query_id'] for r in coverage if r['status']=='HIT'}
    recovered=defaultdict(list)
    for l in lineage:
        if l['origin_status']=='ZERO' and l['query_id'] in hit_ids: recovered[l['seed_id']].append(l['query_id'])
    closure=[]
    for s in seeds:
        orig='ZERO' if s['seed_id'] in ZERO_IDS else 'HIT'
        rec=recovered.get(s['seed_id'],[])
        closure.append({**s,'original_status':orig,'closure_status':'ORIGINAL_HIT' if orig=='HIT' else ('RECOVERED' if rec else 'STILL_ZERO'),'hit_expansion_query_count':len(set(rec))})

    write_csv(OUT/'expansion_lineage.csv',lineage,list(lineage[0].keys()))
    write_csv(OUT/'expansion_query_coverage.csv',coverage,list(coverage[0].keys()))
    write_csv(OUT/'expansion_suggest_raw.csv',sugg,list(sugg[0].keys()))
    write_csv(OUT/'seed_closure_290.csv',closure,list(closure[0].keys()))
    summary={'phase':'RTC-KW-02A-FAST-W1','seed_count':290,'baseline_original_hit':118,'baseline_zero':172,'unique_expansion_queries':len(qmaster),'hit_expansion_queries':sum(r['status']=='HIT' for r in coverage),'error_queries':sum(r['status']=='ERROR' for r in coverage),'suggestion_rows':len(sugg),'unique_suggestions':len({r['suggestion_norm'] for r in sugg}),'recovered_zero_seeds':sum(r['closure_status']=='RECOVERED' for r in closure),'still_zero_seeds':sum(r['closure_status']=='STILL_ZERO' for r in closure),'final_evidence_seeds':sum(r['closure_status']!='STILL_ZERO' for r in closure),'workers':WORKERS}
    (OUT/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False))
if __name__=='__main__': main()
