# Notebook cells 4, 12, 13 (Evaluate), code kept as in the notebook; only paths, CLI switches for the
# pre-registered alternative readings, and a per-dataset restart cache were added.
#   --reading R0 (code, main) | V1 (100 baseline perms) | V2 (Rank_Aggregate magnitude only) | V3 (scSeqComm top 5% quantile) | V4 (BH-FDR truth)
#   --uns figshare (authors' published method outputs) | layerB (our re-run of the 9 methods)
import os, sys, argparse, functools
import numpy as np, pandas as pd, scanpy as sc, liana as li
from common import d, DATA, RUNS
import utils
from utils import *

ap = argparse.ArgumentParser()
ap.add_argument('--reading', default='R0', choices=['R0', 'V1', 'V2', 'V3', 'V4'])
ap.add_argument('--uns', default='figshare', choices=['figshare', 'layerB'])
ap.add_argument('--methods', default=None, help='comma list of method names to evaluate (default all)')
args = ap.parse_args()
tag = f'{args.reading}_{args.uns}'
outdir = os.path.join(RUNS, 'eval', tag)
os.makedirs(outdir, exist_ok=True)

from liana.method import cellphonedb, connectome, cellchat, scseqcomm, singlecellsignalr, natmi, logfc, rank_aggregate, geometric_mean
methods = [cellphonedb, connectome, cellchat, scseqcomm, singlecellsignalr, natmi, logfc, rank_aggregate, geometric_mean]
if args.methods:
    keep = args.methods.split(',')
    methods = [m for m in methods if m.method_name in keep]

# define custom filter functions
lambdas = {}
lambdas['CellPhoneDB'] = lambda x: x['cellphone_pvals'] < 0.05
lambdas['Connectome'] = lambda x: ((x['ligand_pvals'] < 0.05) & (x['receptor_pvals'] < 0.05) & (x['scaled_weight'] > 0))
lambdas['log2FC'] = lambda x: ((x['ligand_pvals'] < 0.05) & (x['receptor_pvals'] < 0.05) & (x['lr_logfc'] > 0))
# top 5% of ligand-receptor pairs
lambdas['NATMI'] = lambda x: ((x['spec_weight'] > np.quantile(gt['spec_weight'], 0.95))) # NOTE gt
lambdas['SingleCellSignalR'] = lambda x: (x['lrscore'] > 0.6)
lambdas['Rank_Aggregate'] = lambda x: ((x['magnitude_rank'] < 0.05) & (x['specificity_rank'] < 0.05))
lambdas['Geometric Mean'] = lambda x: (x['gmean_pvals'] < 0.05)
lambdas['scSeqComm'] = lambda x: ((x['inter_score'] > 0.95))
lambdas['CellChat'] = lambda x: ((x['cellchat_pvals'] < 0.05) & ((x['ligand_pvals'] < 0.05) | (x['receptor_pvals'] < 0.05)))

# Alternative readings (pre-registered, claims.json "readings"); R0 leaves everything above untouched
if args.reading == 'V1':
    generate_random_baseline = functools.partial(utils.generate_random_baseline, n_perms=100)
if args.reading == 'V2':
    lambdas['Rank_Aggregate'] = lambda x: (x['magnitude_rank'] < 0.05)
if args.reading == 'V3':
    lambdas['scSeqComm'] = lambda x: ((x['inter_score'] > np.quantile(gt['inter_score'], 0.95)))
if args.reading == 'V4':
    from decoupler import p_adjust_fdr

    def join_pred_truth(lr_res, lrdata, cpdata, lr_cols=['ligand', 'receptor'], ct_cols=['source', 'target']):
        # Same as utils.join_pred_truth, but BH-FDR applied to the p-values (text: "Moran's R >0 and FDR <0.05")
        lr_res = lr_res.copy()
        lr_truth = lrdata.var
        lr_truth['lr_truth'] = ((p_adjust_fdr(lr_truth['morans_pvals']) < 0.05) * (lr_truth['morans_r'] > 0)).astype(np.int8)
        lr_truth = lr_truth[lr_cols + ['lr_truth']]
        ct_truth = cpdata.var.copy().rename(columns={'ligand': 'source', 'receptor': 'target'})
        ct_truth['ct_truth'] = ((p_adjust_fdr(ct_truth['morans_pvals']) < 0.05) * (ct_truth['morans_r'] > 0)).astype(np.int8)
        ct_truth = ct_truth[ct_cols + ['ct_truth']]
        gt = lr_res.merge(lr_truth, left_on=['ligand_complex', 'receptor_complex'], right_on=lr_cols, how='inner')
        gt = gt.merge(ct_truth, left_on=ct_cols, right_on=ct_cols, how='inner')
        gt['truth'] = gt['lr_truth'] * gt['ct_truth']
        return gt

cols = ['Dataset', 'Method', 'Score', 'AUROC', "Balanced Accuracy", 'Precision', "Recall", "F1", "F1*",
        "F1 (normalised)", "F1* (normalised)", "Positive Calls", 'n_rows', 'n_truth']
scores = li.mt.show_methods()

for k, v in d.items():
    part = os.path.join(outdir, f'{k}.csv')
    if os.path.exists(part):
        print(k, 'done, skip')
        continue
    eval_results = pd.DataFrame(columns=cols)
    adata = sc.read_h5ad(os.path.join(DATA, f"{k}.h5ad"))
    lrdata = sc.read_h5ad(os.path.join(RUNS, 'truth', f"{k}_lrdata.h5ad"))
    cpdata = sc.read_h5ad(os.path.join(RUNS, 'truth', f"{k}_cpdata.h5ad"))

    for method in methods:
        method_name = method.method_name
        score_keys = scores[scores['Method Name'] == method.method_name]
        if args.uns == 'figshare':
            lr_res = adata.uns[method_name].copy()
        else:
            lr_res = pd.read_pickle(os.path.join(RUNS, 'layerB', f'{k}__{method_name}.pkl')).copy()

        score_keys = score_keys[['Magnitude Score', 'Specificity Score']].values[0]
        # if None in score_keys, remove it
        score_keys = [s for s in score_keys if s is not None]

        gt = join_pred_truth(lr_res, lrdata, cpdata)
        gt['binary'] = gt.apply(lambdas[method_name], axis=1).astype(int)

        f1 = calc_weighted_f1(gt, score_key='binary', average='binary')
        f1_baseline = generate_random_baseline(gt, score_key='binary',
                                               metric_fun=calc_weighted_f1,
                                               average='binary')
        f1_norm = (f1/f1_baseline) / 2
        print(f"{k} __{method_name}; f1:{round(f1, 2)}; f1_norm:{round(f1_norm, 2)}", flush=True)

        acc = calc_accuracy(gt, score_key='binary')

        precision = calc_precision(gt, score_key='binary')
        recall = calc_recall(gt, score_key='binary')
        # n times positive calls / total calls
        call_ratio = gt['binary'].sum() / gt.shape[0]

        for score_key in score_keys:
            gt = li.method.process_scores(gt, score_key=score_key)
            auroc = calc_auroc(gt, score_key=score_key, show_plot=False)

            # capped F1 - i.e. all scores are evaluated at the same threshold (not really possible due to ties)
            gt['cap'] = (gt[score_key] >= np.quantile(gt[score_key], 0.95)).astype(int)

            f1_cap = calc_weighted_f1(gt, score_key='cap', average='binary')
            f1_baseline = generate_random_baseline(gt, score_key='cap',
                                                   metric_fun=calc_weighted_f1,
                                                   average='binary')
            f1_cnorm = (f1_cap / f1_baseline) / 2

            # NOTE: f1 and acc are calculated above - i.e. once per method
            eval_results.loc[len(eval_results)] = [v, method_name, score_key,
                                                   auroc,
                                                   acc, precision, recall,
                                                   f1, f1_cap,
                                                   f1_norm, f1_cnorm,
                                                   call_ratio, gt.shape[0], int(gt['truth'].sum())]
    # cell 18 renames
    res = eval_results
    res.loc[(res['Score'] == 'expr_prod') & (res['Method'] == 'Connectome'), 'Score'] = 'Product*'
    res.loc[(res['Score'] == 'expr_prod') & (res['Method'] == 'NATMI'), 'Score'] = 'Product✳'
    res.to_csv(part + '.tmp', index=False)
    os.replace(part + '.tmp', part)

pd.concat([pd.read_csv(os.path.join(outdir, f'{k}.csv')) for k in d]).to_csv(os.path.join(RUNS, 'eval', f'{tag}.csv'), index=False)
print('wrote', tag)
