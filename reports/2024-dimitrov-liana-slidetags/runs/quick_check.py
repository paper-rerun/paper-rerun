# Early sanity check on humancortex: AUROC of each score with our recomputed truth vs Source Data (no baselines)
import os, json, numpy as np, scanpy as sc, liana as li
from common import d, DATA, RUNS, R
from utils import join_pred_truth, calc_auroc
C = json.load(open(os.path.join(R, 'claims.json'), encoding='utf-8'))
rows = [r for c in C['claims'] if c['id'] == 'R75' for r in c['paper_value'] if r['Dataset'] == 'humancortex']
adata = sc.read_h5ad(os.path.join(DATA, 'SCP2167.h5ad'))
lrdata = sc.read_h5ad(os.path.join(RUNS, 'truth', 'SCP2167_lrdata.h5ad'))
cpdata = sc.read_h5ad(os.path.join(RUNS, 'truth', 'SCP2167_cpdata.h5ad'))
for r in rows:
    gt = join_pred_truth(adata.uns[r['Method']].copy(), lrdata, cpdata)
    sk = 'expr_prod' if r['Score'].startswith('Product') else r['Score']
    gt = li.method.process_scores(gt, score_key=sk)
    print(r['Method'], r['Score'], gt.shape[0], int(gt.truth.sum()), 'ours %.6f paper %.6f' % (calc_auroc(gt, sk, show_plot=False), r['AUROC']))
