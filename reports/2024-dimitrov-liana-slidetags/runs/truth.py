# Notebook cell 10 (Generate Truth) for one dataset, unchanged except paths. Restartable: skips if both outputs exist.
import os, sys, time
from itertools import product
import scanpy as sc, liana as li
from common import d, DATA, RUNS
from utils import onehot_groupby
k = sys.argv[1]; v = d[k]
out_lr = os.path.join(RUNS, 'truth', f'{k}_lrdata.h5ad'); out_cp = os.path.join(RUNS, 'truth', f'{k}_cpdata.h5ad')
if os.path.exists(out_lr) and os.path.exists(out_cp):
    print(k, 'truth exists, skip'); sys.exit(0)
t0 = time.time()
adata = sc.read_h5ad(os.path.join(DATA, f'{k}.h5ad'))
if v.__contains__("mouse"):
    resource_name = 'mouseconsensus'
else:
    resource_name = 'consensus'
# Run LR
li.ut.spatial_neighbors(adata, bandwidth=150, cutoff=0.1, set_diag=True)
li.mt.lr_bivar(adata,
               function_name="morans",
               inplace=True,
               use_raw=False,
               n_perms=1000,
               expr_prop=0.05,
               verbose=True,
               mask_negatives=True,
               resource_name=resource_name
               )
lrdata = adata.obsm['local_scores']
lrdata.write_h5ad(out_lr[:-5] + '.tmp.h5ad'); os.replace(out_lr[:-5] + '.tmp.h5ad', out_lr)
# Run CP; NOTE: I'm currently discarding autocrine, and only evaluating para/ortho
ctdata = onehot_groupby(adata, groupby='cell_type')
interactions = list(product(ctdata.var.index, ctdata.var.index))
li.mt.lr_bivar(ctdata,
               function_name="morans",
               inplace=True,
               use_raw=False,
               expr_prop=0, # Why consider all?
               n_perms=1000,
               verbose=True,
               mask_negatives=True,
               interactions=interactions,
               )
cpdata = ctdata.obsm['local_scores']
cpdata.write_h5ad(out_cp[:-5] + '.tmp.h5ad'); os.replace(out_cp[:-5] + '.tmp.h5ad', out_cp)
print(k, v, 'lrdata', lrdata.shape, 'cpdata', cpdata.shape, 'seconds %.0f' % (time.time() - t0))
