# Layer B: re-run the 9 methods of notebook cell 8 on the published .X (figshare), same arguments except
# n_jobs=4 (light mode; the authors used 10). The SCP reading/filtering part of cell 8 cannot be re-run (login).
# Restartable: one pickle per dataset x method.
import os, sys, time
import pandas as pd, scanpy as sc
from common import d, DATA, RUNS
from liana.method import cellphonedb, connectome, cellchat, scseqcomm, singlecellsignalr, natmi, logfc, rank_aggregate, geometric_mean
methods = [cellphonedb, connectome, cellchat, scseqcomm, singlecellsignalr, natmi, logfc, rank_aggregate, geometric_mean]
groupby = 'cell_type'
outdir = os.path.join(RUNS, 'layerB')
os.makedirs(outdir, exist_ok=True)

for k, v in d.items():
    adata = None
    for method in methods:
        out = os.path.join(outdir, f'{k}__{method.method_name}.pkl')
        if os.path.exists(out):
            continue
        if adata is None:
            adata = sc.read_h5ad(os.path.join(DATA, f'{k}.h5ad'))
            for key in list(adata.uns.keys()):
                if key != 'log1p':
                    del adata.uns[key]
        if v.__contains__("mouse"):
            resource_name = 'mouseconsensus'
        else:
            resource_name = 'consensus'
        if method.method_name != 'Rank_Aggregate':
            kw = {'supp_columns': ['ligand_pvals', 'receptor_pvals']}
        else:
            kw = {}
        t0 = time.time()
        res = method(adata,
                     groupby=groupby,
                     use_raw=False,
                     verbose=False,
                     n_perms=1000,
                     n_jobs=4,
                     inplace=False,
                     resource_name=resource_name,
                     **kw
                     )
        res.to_pickle(out + '.tmp')
        os.replace(out + '.tmp', out)
        print(k, v, method.method_name, res.shape, 'seconds %.0f' % (time.time() - t0), flush=True)
print('layerB done')
