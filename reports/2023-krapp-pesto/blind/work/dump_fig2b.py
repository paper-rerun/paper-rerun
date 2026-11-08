import sys, csv, collections
sys.path.insert(0,'work')
from readsheet import read
import numpy as np
for sh,name in [('xl/worksheets/sheet2.xml','fig2b_comparison'),('xl/worksheets/sheet1.xml','fig2b_scannet')]:
    rows = read('downloads/MOESM6_ESM.xlsx', sh)
    hdr = rows[0]
    cols = sorted(hdr, key=lambda c:(len(c),c))
    names = [hdr[c] for c in cols]
    out = []
    for r in rows[1:]:
        out.append([r.get(c) for c in cols])
    with open(f'work/{name}.csv','w',newline='') as f:
        w=csv.writer(f); w.writerow(names); w.writerows(out)
    sids=[o[0] for o in out]
    dup=[k for k,v in collections.Counter(sids).items() if v>1]
    print(name, 'n=',len(out), 'uniq sid=',len(set(sids)), 'dups=',dup)
    # median of auc columns
    for i,n in enumerate(names):
        if 'auc' in n.lower() or n in ('PeSTo','MaSIF-site','SPPIDER','PSIVER'):
            v=np.array([float(o[i]) for o in out if o[i] is not None])
            print('   ',n,'n=',len(v),'median=%.4f'%np.median(v),'mean=%.4f'%v.mean())
