import json, csv, collections
import numpy as np
rng=np.random.default_rng(0)
def boot(v,n=20000):
    v=np.asarray(v,float); b=np.median(rng.choice(v,(n,len(v)),replace=True),axis=1)
    return float(np.median(v)), float(np.percentile(b,2.5)), float(np.percentile(b,97.5))
# MaSIF
m=[json.loads(l) for l in open('out/masif.jsonl')]
m=[r for r in m if r.get('sid') and 'note' not in r]
a=[r['auc'] for r in m]
print('MaSIF n=%d median=%.4f CI=[%.4f,%.4f] mean=%.4f'%((len(a),)+boot(a)+(np.mean(a),)))
# ScanNet
s=[json.loads(l) for l in open('out/scannet.jsonl')]
s=[r for r in s if r.get('sid')]
by=collections.defaultdict(list)
for r in s: by[r['sid']].append(r)
chosen={k:sorted(v,key=lambda r:(r['ba'],r['cid']))[0] for k,v in by.items()}
v=[r['auc'] for r in chosen.values()]
print('ScanNet n=%d median=%.4f CI=[%.4f,%.4f] mean=%.4f'%((len(v),)+boot(v)+(np.mean(v),)))
v2=[(0.909057557582855 if k=='4DX0_A' else r['auc']) for k,r in chosen.items()]
print('ScanNet with 4DX0_A on the 2023 assembly: median=%.4f CI=[%.4f,%.4f]'%boot(v2))
auth={r['sid']:float(r['PeSTo_auc']) for r in csv.DictReader(open('work/fig2b_scannet.csv'))}
print('authors median over the same 416 sids: %.4f'%np.median([auth[k] for k in chosen]))
print('authors median over all 417: %.4f'%np.median(list(auth.values())))
d=np.array([chosen[k]['auc']-auth[k] for k in chosen])
print('agreement: |d|<=0.001 in %d/%d, <=0.005 in %d/%d'%(int((abs(d)<=0.001).sum()),len(d),int((abs(d)<=0.005).sum()),len(d)))
t=[r['t'] for r in chosen.values() if r.get('t')]
print('time per structure: mean %.1f s median %.1f s'%(np.mean(t),np.median(t)))
