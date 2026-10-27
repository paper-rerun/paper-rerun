# Score our evaluation tables against the pre-registered claims (claims.json, read only).
# Writes runs/results/<tag>.json and a plain-text summary on stdout.
import os, sys, json, hashlib, itertools
import numpy as np, pandas as pd
from scipy.stats import kendalltau, spearmanr
from common import RUNS, R

claims_path = os.path.join(R, 'claims.json')
sha = hashlib.sha256(open(claims_path, 'rb').read()).hexdigest()
frozen = open(os.path.join(R, 'claims.sha256')).read().split()[0]
assert sha == frozen, 'claims.json changed since it was frozen'
C = json.load(open(claims_path, encoding='utf-8'))
claims = {c['id']: c for c in C['claims']}
paper_rows = pd.DataFrame(claims['R75']['paper_value'])
KEY = ['Dataset', 'Method', 'Score']
METRICS = ['AUROC', 'Balanced Accuracy', 'Precision', 'Recall', 'F1', 'F1*', 'F1 (normalised)', 'F1* (normalised)', 'Positive Calls']
PANEL_TOL = {'AUROC': 0.005, 'Balanced Accuracy': 0.005, 'F1 (normalised)': 0.025, 'F1* (normalised)': 0.025}


def load(tag):
    # V2/V3 only re-evaluated one method; the other rows are the R0 rows of the same layer
    uns = tag.split('_')[1]
    df = pd.read_csv(os.path.join(RUNS, 'eval', f'{tag}.csv'))
    if len(df) < 75:
        base = pd.read_csv(os.path.join(RUNS, 'eval', f'R0_{uns}.csv'))
        base = base[~base['Method'].isin(df['Method'].unique())]
        df = pd.concat([base, df], ignore_index=True)
    assert len(df) == 75, (tag, len(df))
    return df


def medians(df):
    out = {}
    for metric in ['AUROC', 'F1* (normalised)']:
        out[metric] = df.groupby(['Method', 'Score'])[metric].median()
    one = df.drop_duplicates(['Dataset', 'Method'])
    for metric in ['Balanced Accuracy', 'F1 (normalised)']:
        out[metric] = one.groupby('Method')[metric].median()
    return out


def order_check(claim, ours_by_label, tol):
    labels = claim['paper_value']
    paper_med = {}
    prefix = claim['id'][1]
    for c in C['claims']:
        if c['id'].startswith(prefix) and c['id'][1:].isdigit():
            lab = c['method'] if c['score'] is None else f"{c['method']} | {c['score']}"
            paper_med[lab] = c['paper_value']
    broken = []
    for a, b in itertools.combinations(labels, 2):
        if paper_med[a] - paper_med[b] > 2 * tol and not (ours_by_label[a] > ours_by_label[b]):
            broken.append([a, b])
    our_order = sorted(labels, key=lambda l: -ours_by_label[l])
    tau = kendalltau([paper_med[l] for l in labels], [ours_by_label[l] for l in labels]).correlation
    return {'pass': len(broken) == 0, 'broken_pairs': broken, 'kendall_tau_b_vs_paper_medians': tau, 'our_order': our_order}


def score(tag):
    df = load(tag)
    res = {'tag': tag, 'claims': {}}
    # Per-row comparison (R75)
    m = paper_rows.merge(df, on=KEY, suffixes=('_paper', '_ours'), how='outer', indicator=True)
    assert (m['_merge'] == 'both').all(), m[m['_merge'] != 'both'][KEY]
    cells = {}
    for metric in METRICS:
        diff = (m[f'{metric}_ours'] - m[f'{metric}_paper']).abs()
        ptol = PANEL_TOL.get(metric, 0.005)
        cells[metric] = {'max_abs_diff': float(diff.max()), 'n_within_0.0005': int((diff <= 0.0005).sum()),
                         'n_within_panel_tol': int((diff <= ptol).sum()), 'n_outside_panel_tol': int((diff > ptol).sum()),
                         'panel_tol': ptol}
    n_cells_exact = sum(v['n_within_0.0005'] for v in cells.values())
    res['claims']['R75'] = {'pass': n_cells_exact == 75 * len(METRICS), 'cells_within_0.0005': n_cells_exact,
                            'cells_total': 75 * len(METRICS), 'per_metric': cells}
    m.to_csv(os.path.join(RUNS, 'results', f'{tag}_rows_vs_paper.csv'), index=False)
    # Medians
    med = medians(df)
    panel_metric = {'A': 'AUROC', 'B': 'Balanced Accuracy', 'S': 'F1* (normalised)', 'F': 'F1 (normalised)'}
    ours_by_label = {}
    for c in C['claims']:
        cid = c['id']
        if cid[0] in panel_metric and cid[1:].isdigit():
            metric = panel_metric[cid[0]]
            ours = float(med[metric].loc[(c['method'], c['score'])] if c['score'] is not None else med[metric].loc[c['method']])
            lab = c['method'] if c['score'] is None else f"{c['method']} | {c['score']}"
            ours_by_label.setdefault(cid[0], {})[lab] = ours
            diff = ours - c['paper_value']
            res['claims'][cid] = {'paper': c['paper_value'], 'ours': ours, 'diff': diff,
                                  'pass': abs(diff) <= c['tolerance'], 'exact_tier': abs(diff) <= c['tolerance_exact_tier']}
    for oid, p in [('OA', 'A'), ('OB', 'B'), ('OS', 'S'), ('OF', 'F')]:
        tol = 0.005 if p in 'AB' else 0.025
        res['claims'][oid] = order_check(claims[oid], ours_by_label[p], tol)
    # Q1
    auc = ours_by_label['A']
    q1 = sum(v > 0.5 for v in auc.values())
    res['claims']['Q1'] = {'paper': 9, 'ours': q1, 'max_median_auroc': max(auc.values()),
                           'pass': q1 >= 8 and max(auc.values()) <= 0.60}
    # Q2
    ba = ours_by_label['B']
    dev = max(abs(v - 0.5) for v in ba.values())
    res['claims']['Q2'] = {'paper': claims['Q2']['paper_value'], 'ours': dev, 'pass': dev <= 0.03}
    # Q3
    wins_auc, wins_f1 = 0, 0
    pairs = []
    for pr in claims['Q3']['paper_value']['pairs']:
        a_m, a_s = auc[f"{pr['method']} | {pr['magnitude']}"], auc[f"{pr['method']} | {pr['specificity']}"]
        s = ours_by_label['S']
        f_m, f_s = s[f"{pr['method']} | {pr['magnitude']}"], s[f"{pr['method']} | {pr['specificity']}"]
        wins_auc += a_m > a_s
        wins_f1 += f_m > f_s
        pairs.append({'method': pr['method'], 'AUROC': [a_m, a_s], 'F1*n': [f_m, f_s]})
    res['claims']['Q3'] = {'paper': [6, 6], 'ours': [int(wins_auc), int(wins_f1)], 'pairs': pairs,
                           'pass': wins_auc >= 5 and wins_f1 >= 5}
    # Q4
    rho = spearmanr(df['Positive Calls'], df['F1']).correlation
    res['claims']['Q4'] = {'paper_SI': 0.765, 'paper_source_data': 0.7456, 'ours': rho,
                           'diff_vs_SI': rho - 0.765, 'diff_vs_source_data': rho - 0.7456,
                           'pass': abs(rho - 0.765) <= 0.02}
    return res


def truth_margin():
    # D15: how many truth labels sit near the p = 0.05 cut (|p - 0.05| <= 0.005), and truth sizes
    import scanpy as sc
    from common import d
    out = {}
    for k, v in d.items():
        row = {}
        for kind in ['lrdata', 'cpdata']:
            var = sc.read_h5ad(os.path.join(RUNS, 'truth', f'{k}_{kind}.h5ad'), backed='r').var
            p, r = var['morans_pvals'], var['morans_r']
            row[kind] = {'n': int(len(var)), 'n_true_code': int(((p <= 0.05) & (r > 0)).sum()),
                         'n_near_cut': int(((p - 0.05).abs() <= 0.005).sum())}
        out[v] = row
    return out


if __name__ == '__main__':
    os.makedirs(os.path.join(RUNS, 'results'), exist_ok=True)
    tags = sys.argv[1:]
    for tag in tags:
        if tag == 'truth':
            r = truth_margin()
            json.dump(r, open(os.path.join(RUNS, 'results', 'truth_margin.json'), 'w'), indent=1)
            print(json.dumps(r, indent=1))
            continue
        r = score(tag)
        json.dump(r, open(os.path.join(RUNS, 'results', f'{tag}.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False, default=float)
        cl = r['claims']
        npass = sum(v['pass'] for v in cl.values())
        print(f'=== {tag}: {npass}/{len(cl)} claims pass')
        for cid, v in cl.items():
            if 'diff' in v:
                print(f"{cid:4s} paper {v['paper']:.4f} ours {v['ours']:.4f} diff {v['diff']:+.4f} pass {v['pass']} exact {v['exact_tier']}")
            elif cid == 'R75':
                print('R75', v['cells_within_0.0005'], '/', v['cells_total'], 'cells within 0.0005;',
                      {k: (x['max_abs_diff'], x['n_outside_panel_tol']) for k, x in v['per_metric'].items()})
            else:
                print(cid, {k: x for k, x in v.items() if k not in ('pairs', 'our_order')})
