import csv, collections, numpy as np
rows=list(csv.DictReader(open('work/fig2b_comparison.csv')))
print('best column counts:', collections.Counter(r['best'] for r in rows))
M=np.array([[float(r[k]) for k in ['PeSTo','MaSIF-site','SPPIDER','PSIVER']] for r in rows])
am=np.argmax(M,1)
print('argmax counts (4 methods):', collections.Counter(am.tolist()))
print('ties with PeSTo max:', int(np.sum((M.max(1)==M[:,0]) )))
rng=np.random.default_rng(0)
def boot(v,n=20000):
    b=np.median(rng.choice(v,(n,len(v)),replace=True),axis=1)
    return np.median(v), np.percentile(b,[2.5,97.5])
for i,k in enumerate(['PeSTo','MaSIF-site','SPPIDER','PSIVER']):
    m,ci=boot(M[:,i]); print(f'{k}: median={m:.4f} 95%CI=[{ci[0]:.4f},{ci[1]:.4f}]')
rows2=list(csv.DictReader(open('work/fig2b_scannet.csv')))
for k in ['PeSTo_auc','ScanNet-noMSA_auc','ScanNet_auc']:
    v=np.array([float(r[k]) for r in rows2]); m,ci=boot(v); print(f'{k}: median={m:.4f} 95%CI=[{ci[0]:.4f},{ci[1]:.4f}]')
t=np.array([float(r['time']) for r in rows2]); print('time mean %.2f std %.2f'%(t.mean(),t.std()))
