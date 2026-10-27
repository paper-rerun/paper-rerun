# Facts behind the alternative readings: truth sizes under code (raw p <= 0.05) vs text (BH-FDR < 0.05),
# and how many scSeqComm inter_score values sit at/above the 95th quantile (V3)
import os, json
import numpy as np, scanpy as sc
from decoupler import p_adjust_fdr
from common import d, DATA, RUNS
from utils import join_pred_truth

out = {}
for k, v in d.items():
    row = {}
    for kind in ['lrdata', 'cpdata']:
        var = sc.read_h5ad(os.path.join(RUNS, 'truth', f'{k}_{kind}.h5ad'), backed='r').var
        p, r = var['morans_pvals'], var['morans_r']
        row[kind] = {'n': int(len(var)), 'true_code_raw_p': int(((p <= 0.05) & (r > 0)).sum()),
                     'true_text_bh_fdr': int(((p_adjust_fdr(p) < 0.05) & (r > 0)).sum()),
                     'p_adjust_fdr_of_boolean_is_identity': bool(np.array_equal(p_adjust_fdr(p <= 0.05), (p <= 0.05).astype(float)))}
    adata = sc.read_h5ad(os.path.join(DATA, f'{k}.h5ad'))
    lrdata = sc.read_h5ad(os.path.join(RUNS, 'truth', f'{k}_lrdata.h5ad'))
    cpdata = sc.read_h5ad(os.path.join(RUNS, 'truth', f'{k}_cpdata.h5ad'))
    gt = join_pred_truth(adata.uns['scSeqComm'].copy(), lrdata, cpdata)
    q = np.quantile(gt['inter_score'], 0.95)
    row['scSeqComm'] = {'rows': int(len(gt)), 'q95_inter_score': float(q), 'max_inter_score': float(gt['inter_score'].max()),
                        'n_at_or_above_q95': int((gt['inter_score'] >= q).sum()), 'n_above_q95': int((gt['inter_score'] > q).sum()),
                        'n_above_0.95_code': int((gt['inter_score'] > 0.95).sum()), 'truth_positive_rate': float(gt['truth'].mean())}
    out[v] = row
    print(v, json.dumps(row))
json.dump(out, open(os.path.join(RUNS, 'results', 'variant_facts.json'), 'w'), indent=1)
