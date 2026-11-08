# Scores the authors' released per-structure prediction files against their own released labels,
# and against mine, to find out whether a mismatch is an alignment problem or a different model.
# CC BY-NC-SA 4.0
import json, os, subprocess, csv
import numpy as np
from sklearn.metrics import roc_auc_score
from scipy.stats import spearmanr

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repo'))


def git_show(path):
    return subprocess.run(['git', 'cat-file', '-p', 'HEAD:' + path], cwd=REPO,
                          capture_output=True).stdout.decode('utf-8', 'replace')


def ca_col(text, lo, hi):
    out = []
    for line in text.splitlines():
        if line[:4] == 'ATOM' and line[12:15].strip() == 'CA':
            out.append(float(line[lo:hi]))
    return np.array(out)


auth = {}
for r in csv.DictReader(open('work/fig2b_comparison.csv')):
    auth.setdefault(r['sid'], []).append(float(r['PeSTo']))

rows = []
for l in open('out/masif.jsonl'):
    r = json.loads(l)
    if not r.get('sid') or 'note' in r:
        continue
    pid, ba, cid = r['key'].split('/')
    base = 'pdbs_test/%s_%s_%s_%s' % (pid[1:3].upper(), pid.upper(), ba, cid)
    tP, tT = git_show(base + '.pdb'), git_show(base + '_T.pdb')
    if not tT:
        continue
    yt = ca_col(tT, 60, 66)
    pr = ca_col(tP, 60, 66)
    pr_occ = ca_col(tP, 54, 60)
    y = np.array(r['y'], dtype=float)
    p = np.array(r['p'], dtype=float)
    a_rel = roc_auc_score(yt, pr) if 0 < yt.sum() < yt.shape[0] else None
    a_rel_occ = roc_auc_score(yt, pr_occ) if (0 < yt.sum() < yt.shape[0] and pr_occ.std() > 0) else None
    rows.append(dict(key=r['key'], sid=r['sid'], n=len(y),
                     auc_mine=r['auc'], auc_released_pdb=a_rel, auc_released_occ=a_rel_occ,
                     auc_sourcedata=auth.get(r['sid']),
                     spearman=float(spearmanr(p, pr).statistic),
                     maxdiff=float(np.max(np.abs(p - pr)))))

print('%-14s %7s %7s %7s %7s %7s' % ('key', 'mine', 'relpdb', 'relocc', 'rho', 'maxd'))
for d in rows:
    print('%-14s %7.4f %7s %7s %7.3f %7.3f' % (
        d['key'], d['auc_mine'],
        'None' if d['auc_released_pdb'] is None else '%.4f' % d['auc_released_pdb'],
        'None' if d['auc_released_occ'] is None else '%.4f' % d['auc_released_occ'],
        d['spearman'], d['maxdiff']))
rel = [d['auc_released_pdb'] for d in rows if d['auc_released_pdb'] is not None]
print('\nmedian AUC from the released prediction files: %.4f  (n=%d)' % (np.median(rel), len(rel)))
print('median AUC mine                            : %.4f' % np.median([d['auc_mine'] for d in rows]))
