"""Per-jet comparison of two prediction folders (same files, same jet order)

Usage: python compare_perjet.py <dir_a> <dir_b> <out.json>
Checks the jets line up (jet_pt, jet_eta, _label_ equal), then reports score differences and argmax flips
"""
import json
import sys

import numpy as np
import uproot

LABELS = ['label_QCD', 'label_Hbb', 'label_Hcc', 'label_Hgg', 'label_H4q',
          'label_Hqql', 'label_Zqq', 'label_Wqq', 'label_Tbqq', 'label_Tbl']
GROUPS = ['HToBB', 'HToCC', 'HToGG', 'HToWW2Q1L', 'HToWW4Q', 'TTBar', 'TTBarLep', 'WToQQ', 'ZToQQ', 'ZJetsToNuNu']


def read(path):
    with uproot.open(path) as f:
        tree = f[f.keys()[0]]
        arrays = tree.arrays(['score_' + l for l in LABELS] + ['_label_', 'jet_pt', 'jet_eta'], library='np')
    return np.stack([arrays['score_' + l] for l in LABELS], axis=1), arrays


def main():
    dir_a, dir_b, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    result = {'dir_a': dir_a, 'dir_b': dir_b, 'groups': {}}
    all_diff = []
    flips = 0
    total = 0
    for group in GROUPS:
        scores_a, arr_a = read(f'{dir_a}/pred_{group}.root')
        scores_b, arr_b = read(f'{dir_b}/pred_{group}.root')
        aligned = (len(scores_a) == len(scores_b)
                   and np.array_equal(arr_a['jet_pt'], arr_b['jet_pt'])
                   and np.array_equal(arr_a['jet_eta'], arr_b['jet_eta'])
                   and np.array_equal(arr_a['_label_'], arr_b['_label_']))
        entry = {'n_a': int(len(scores_a)), 'n_b': int(len(scores_b)), 'aligned': bool(aligned)}
        if aligned:
            diff = np.abs(scores_a.astype(np.float64) - scores_b.astype(np.float64))
            group_flips = int(np.sum(np.argmax(scores_a, 1) != np.argmax(scores_b, 1)))
            entry.update({'max_abs_score_diff': float(diff.max()), 'mean_abs_score_diff': float(diff.mean()),
                          'n_identical_rows': int(np.sum(np.all(scores_a == scores_b, axis=1))),
                          'argmax_flips': group_flips})
            all_diff.append(diff.max(axis=1))
            flips += group_flips
            total += len(scores_a)
        result['groups'][group] = entry
    if all_diff:
        all_diff = np.concatenate(all_diff)
        result['total_jets_compared'] = total
        result['max_abs_score_diff'] = float(all_diff.max())
        result['median_rowmax_abs_score_diff'] = float(np.median(all_diff))
        result['argmax_flips'] = flips
    json.dump(result, open(out_path, 'w'), indent=1)
    print(json.dumps({k: v for k, v in result.items() if k != 'groups'}, indent=1))


if __name__ == '__main__':
    main()
