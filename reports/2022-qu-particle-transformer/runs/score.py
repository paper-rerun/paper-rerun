"""Score weaver predictions against the pre-registered claims (claims.json, definitions D1-D8)

Usage: python score.py <pred_dir> <model: ParT|ParticleNet> <out.json> [--pilot]
"""
import json
import re
import sys

import numpy as np
import sklearn
import uproot
from sklearn.metrics import roc_auc_score, roc_curve

HERE = '/mnt/e/Ciencia/noturno/2022-qu-particle-transformer'
LABELS = ['label_QCD', 'label_Hbb', 'label_Hcc', 'label_Hgg', 'label_H4q',
          'label_Hqql', 'label_Zqq', 'label_Wqq', 'label_Tbqq', 'label_Tbl']
GROUP_TO_LABEL = {'ZJetsToNuNu': 'label_QCD', 'HToBB': 'label_Hbb', 'HToCC': 'label_Hcc', 'HToGG': 'label_Hgg',
                  'HToWW4Q': 'label_H4q', 'HToWW2Q1L': 'label_Hqql', 'ZToQQ': 'label_Zqq', 'WToQQ': 'label_Wqq',
                  'TTBar': 'label_Tbqq', 'TTBarLep': 'label_Tbl'}
JETS_PER_CLASS = 2_000_000


def load_predictions(pred_dir):
    """Read the 10 pred_<group>.root files; return scores (N,10 float32), true index (N,), per-group info"""
    all_scores = []
    all_true = []
    group_info = {}
    for group, label_name in GROUP_TO_LABEL.items():
        with uproot.open(f'{pred_dir}/pred_{group}.root') as f:
            tree = f[f.keys()[0]]
            arrays = tree.arrays(['score_' + l for l in LABELS] + LABELS + ['_label_'], library='np')
        scores = np.stack([arrays['score_' + l] for l in LABELS], axis=1)
        true_index = arrays['_label_'].astype(np.int64)
        # One-hot label branches must agree with _label_ and with the file name (D2)
        onehot_index = np.argmax(np.stack([arrays[l] for l in LABELS], axis=1), axis=1)
        expected_index = LABELS.index(label_name)
        group_info[group] = {
            'n_jets': int(len(true_index)),
            'score_dtype': str(scores.dtype),
            'n_label_branch_mismatch_vs_onehot': int(np.sum(onehot_index != true_index)),
            'n_label_mismatch_vs_filename': int(np.sum(true_index != expected_index)),
        }
        all_scores.append(scores)
        all_true.append(true_index)
    return np.concatenate(all_scores), np.concatenate(all_true), group_info


def roc_readings(y, score, tpr_target):
    """FPR at TPR = X read three ways (D7), plus ties at the main threshold"""
    fpr, tpr, thresholds = roc_curve(y, score, drop_intermediate=False)
    n_background = int(np.sum(y == 0))
    first = int(np.argmax(tpr >= tpr_target))
    nearest = int(np.argmin(np.abs(tpr - tpr_target)))
    fpr_first = float(fpr[first])
    fpr_interp = float(np.interp(tpr_target, tpr, fpr))
    fpr_nearest = float(fpr[nearest])
    threshold = thresholds[first]
    n_tied = int(np.sum(score == threshold))

    def rej(x):
        return float(1.0 / x) if x > 0 else float('inf')

    return {
        'main_first_point_tpr_ge_X': {'tpr': float(tpr[first]), 'fpr': fpr_first,
                                       'k_qcd': round(fpr_first * n_background, 3), 'rej': rej(fpr_first)},
        'interpolated': {'fpr': fpr_interp, 'k_qcd': round(fpr_interp * n_background, 3), 'rej': rej(fpr_interp)},
        'nearest_point': {'tpr': float(tpr[nearest]), 'fpr': fpr_nearest,
                          'k_qcd': round(fpr_nearest * n_background, 3), 'rej': rej(fpr_nearest)},
        'threshold': float(threshold),
        'n_jets_tied_at_threshold': n_tied,
    }


def parse_band(text):
    """Pull the number after '<=' or '>' from a tolerance string"""
    return float(re.search(r'(?:<=|>)\s*([0-9.]+)', text).group(1))


def judge(claim, ours):
    tol = claim['tolerance']
    paper = claim['paper_value']
    if 'Rej' in claim['quantity']:
        rel = ours / paper - 1
        pass_band = parse_band(tol['pass'])
        fail_band = parse_band(tol['fail'])
        if abs(rel) <= pass_band:
            status = 'pass'
        elif abs(rel) <= fail_band:
            status = 'marginal'
        else:
            status = 'fail'
        return {'paper': paper, 'ours': ours, 'rel_diff': rel, 'status': status}
    band = parse_band(tol['pass'])
    diff = ours - paper
    return {'paper': paper, 'ours': ours, 'diff': diff, 'status': 'pass' if abs(diff) <= band + 1e-12 else 'fail'}


def main():
    pred_dir, model, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    pilot = '--pilot' in sys.argv

    scores32, true_index, group_info = load_predictions(pred_dir)
    n_total = len(true_index)
    counts = {LABELS[i]: int(np.sum(true_index == i)) for i in range(10)}
    result = {'pred_dir': pred_dir, 'model': model, 'n_total': n_total, 'per_class_counts': counts,
              'groups': group_info, 'sklearn': sklearn.__version__, 'numpy': np.__version__}
    # D1: full test set must be exactly 2M per class
    counts_ok = all(c == JETS_PER_CLASS for c in counts.values()) and n_total == 10 * JETS_PER_CLASS
    result['d1_counts_ok'] = counts_ok
    if not counts_ok and not pilot:
        json.dump(result, open(out_path, 'w'), indent=1)
        sys.exit('D1 count check failed, stopping')

    # D3: accuracy, argmax of the 10 outputs
    accuracy = float(np.mean(np.argmax(scores32, axis=1) == true_index))
    result['accuracy'] = accuracy
    result['n_correct'] = int(np.sum(np.argmax(scores32, axis=1) == true_index))

    # D4: macro one-vs-one AUC on float64 scores
    scores64 = scores32.astype(np.float64)
    result['max_abs_rowsum_minus_1'] = float(np.max(np.abs(scores64.sum(axis=1) - 1)))
    try:
        auc = roc_auc_score(true_index, scores64, average='macro', multi_class='ovo')
        result['auc_renormalized'] = False
    except ValueError as e:
        result['auc_first_error'] = str(e)
        scores64 = scores64 / scores64.sum(axis=1, keepdims=True)
        auc = roc_auc_score(true_index, scores64, average='macro', multi_class='ovo')
        result['auc_renormalized'] = True
    result['auc'] = float(auc)
    print(f'accuracy {accuracy:.6f}  auc {auc:.6f}', flush=True)

    # D5-D8: rejections, signal class vs QCD only
    claims = json.load(open(f'{HERE}/claims.json'))['claims']
    rej_claims = [c for c in claims if c['id'].startswith(model + '.') and 'signal_class' in c]
    result['rej'] = {}
    for claim in rej_claims:
        signal_index = LABELS.index(claim['signal_class']['label'])
        tpr_target = claim['signal_class']['tpr']
        select = (true_index == signal_index) | (true_index == 0)
        y = (true_index[select] == signal_index).astype(np.int64)
        s_signal32 = scores32[select, signal_index]
        s_qcd32 = scores32[select, 0]
        s_signal64 = s_signal32.astype(np.float64)
        s_qcd64 = s_qcd32.astype(np.float64)
        with np.errstate(divide='ignore', invalid='ignore'):
            main_score = s_signal64 / (s_signal64 + s_qcd64)
            variant_f32 = s_signal32 / (s_signal32 + s_qcd32)
            variant_log = np.log(s_signal64) - np.log(s_qcd64)
        entry = {
            'n_signal': int(y.sum()), 'n_qcd': int((y == 0).sum()), 'tpr_target': tpr_target,
            'n_nan_main': int(np.isnan(main_score).sum()),
            'main_f64_ratio': roc_readings(y, np.nan_to_num(main_score, nan=0.0), tpr_target),
            'variant_f32_ratio': roc_readings(y, np.nan_to_num(variant_f32, nan=0.0), tpr_target),
            # A softmax output of exactly 0 in float32 gives +-inf here; map to +-1e300 so the rank order is kept
            'n_nonfinite_logdiff': int((~np.isfinite(variant_log)).sum()),
            'variant_f64_logdiff': roc_readings(y, np.nan_to_num(variant_log, nan=0.0, posinf=1e300, neginf=-1e300),
                                                tpr_target),
            'implied_k_paper': claim['implied_qcd_count_passing'],
        }
        result['rej'][claim['id']] = entry
        m = entry['main_f64_ratio']['main_first_point_tpr_ge_X']
        print(f"{claim['id']}: k={m['k_qcd']} rej={m['rej']:.1f} (paper {claim['paper_value']}, k {claim['implied_qcd_count_passing']})", flush=True)

    # Judge every claim of this model with the pre-registered tolerances
    verdicts = {}
    for claim in claims:
        if not claim['id'].startswith(model + '.'):
            continue
        if claim['id'].endswith('.accuracy'):
            verdicts[claim['id']] = judge(claim, accuracy)
        elif claim['id'].endswith('.auc'):
            verdicts[claim['id']] = judge(claim, result['auc'])
        else:
            rej_value = result['rej'][claim['id']]['main_f64_ratio']['main_first_point_tpr_ge_X']['rej']
            verdicts[claim['id']] = judge(claim, rej_value)
    result['verdicts'] = verdicts
    json.dump(result, open(out_path, 'w'), indent=1)
    for k, v in verdicts.items():
        print(k, v, flush=True)


if __name__ == '__main__':
    main()
