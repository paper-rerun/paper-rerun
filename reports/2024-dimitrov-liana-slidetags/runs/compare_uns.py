# Layer B check: our re-run of the 9 methods vs the .uns published in the figshare .h5ad files
import os, json
import numpy as np, pandas as pd, scanpy as sc
from common import d, DATA, RUNS

KEYS = ['source', 'target', 'ligand_complex', 'receptor_complex']
out = {}
for k, v in d.items():
    adata = sc.read_h5ad(os.path.join(DATA, f'{k}.h5ad'))
    for m in ['CellPhoneDB', 'Connectome', 'CellChat', 'scSeqComm', 'SingleCellSignalR', 'NATMI', 'log2FC', 'Rank_Aggregate', 'Geometric Mean']:
        pub = adata.uns[m].copy()
        ours = pd.read_pickle(os.path.join(RUNS, 'layerB', f'{k}__{m}.pkl'))
        row = {'rows_published': len(pub), 'rows_ours': len(ours),
               'same_row_order': bool(len(pub) == len(ours) and (pub[KEYS].astype(str).values == ours[KEYS].astype(str).values).all())}
        mg = pub.merge(ours, on=KEYS, how='outer', suffixes=('_pub', '_ours'), indicator=True)
        row['rows_only_one_side'] = int((mg['_merge'] != 'both').sum())
        maxdiff = {}
        for c in pub.columns:
            if c in KEYS or c not in ours.columns or not np.issubdtype(pub[c].dtype, np.number):
                continue
            a, b = mg[f'{c}_pub'].astype(float), mg[f'{c}_ours'].astype(float)
            maxdiff[c] = float(np.nanmax(np.abs(a - b))) if len(a) else 0.0
        row['max_abs_diff'] = maxdiff
        row['identical'] = row['rows_only_one_side'] == 0 and all(x == 0 for x in maxdiff.values())
        out[f'{v}|{m}'] = row
        print(v, m, row['rows_published'], row['rows_ours'], 'identical' if row['identical'] else 'DIFF', max(maxdiff.values()) if maxdiff else None)
json.dump(out, open(os.path.join(RUNS, 'results', 'layerB_uns_vs_published.json'), 'w'), indent=1)
print('identical pairs:', sum(r['identical'] for r in out.values()), '/', len(out))
