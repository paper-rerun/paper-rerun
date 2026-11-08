import sys, csv, json
sys.path.insert(0,'scripts'); sys.path.insert(0,'repo')
import numpy as np
from pesto_rerun import fetch_assembly, contact_pairs, AA20, R_THR, load_model, predict
from src.structure_io import read_pdb
from src.structure import clean_structure, tag_hetatm_chains, split_by_chain, filter_non_atomic_subunits
from sklearn.metrics import roc_auc_score
r=[x for x in csv.DictReader(open('work/fig2b_scannet.csv')) if x['sid']=='4DX0_A'][0]
acc,tpr,tnr=float(r['PeSTo_acc']),float(r['PeSTo_tpr']),float(r['PeSTo_tnr'])
for n in range(100,400):
    for P in range(1,n):
        N=n-P
        TP=tpr*P; TN=tnr*N
        if abs(TP-round(TP))<1e-6 and abs(TN-round(TN))<1e-6 and abs((round(TP)+round(TN))/n-acc)<1e-6:
            print('consistent with n_res=%d, positives=%d, TP=%d, TN=%d'%(n,P,round(TP),round(TN)))
            break
    else:
        continue
    break
fp=fetch_assembly('4DX0',1)
s=read_pdb(fp); s=clean_structure(s); s=tag_hetatm_chains(s)
su=filter_non_atomic_subunits(split_by_chain(s))
tgt=su['A:0']
model=load_model()
p=predict(model,tgt)
for partners in [['P:0'],['P:0','P:1'],['P:0','P:1','A:1']]:
    pos=set()
    for c in partners:
        ia,ib=contact_pairs(tgt['xyz'],su[c]['xyz'],R_THR)
        if ia.shape[0]==0: continue
        m=np.array([x in AA20 for x in tgt['resname'][ia]]) & np.array([x in AA20 for x in su[c]['resname'][ib]])
        pos.update(tgt['resid'][ia[m]].tolist())
    u=np.unique(tgt['resid']); y=np.isin(u,sorted(pos)).astype(float)
    print('partners',partners,'positives',int(y.sum()),'auc %.4f'%roc_auc_score(y,p))
print('authors auc', r['PeSTo_auc'])
