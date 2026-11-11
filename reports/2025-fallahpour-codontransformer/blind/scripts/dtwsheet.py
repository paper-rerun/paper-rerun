import json, statistics, openpyxl, sys
sys.path.insert(0,'scripts')
from recount import dtw, sheet_rows, norm, BASE, FT
wb=openpyxl.load_workbook(sys.argv[1],read_only=True,data_only=True)
prof={}
for r in sheet_rows(wb,'%MinMax'):
    prof[(r['organism'],str(r['protein (benchmark)']).strip(),norm(r['model']))]=[float(v) for v in str(r['minmax']).split(',') if v.strip()]
pub={}
for r in sheet_rows(wb,'DTW'):
    pub.setdefault((r['organism'],str(r['protein']).strip()),set()).add(round(float(r['normalized_distance']),12))
agree=0; diffs=[]; n=0
for (o,p),vals in pub.items():
    if len(vals)!=1: continue
    v=next(iter(vals))
    if (o,p,BASE) in prof and (o,p,FT) in prof:
        d,N,M=dtw(prof[(o,p,BASE)],prof[(o,p,FT)])
        mine=d/(N+M); n+=1; diffs.append(abs(mine-v))
        if abs(mine-v)<1e-3: agree+=1
print('groups with one distinct normalized value:',len([1 for v in pub.values() if len(v)==1]),'of',len(pub))
print('compared:',n,'within 1e-3 of my base-vs-FT value:',agree)
print('max abs diff %.3g  mean abs diff %.3g'%(max(diffs),statistics.fmean(diffs)))
