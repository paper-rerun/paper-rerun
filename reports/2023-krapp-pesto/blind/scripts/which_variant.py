# Which of the four released checkpoints produced the prediction PDB files in repo/pdbs_test?
# Runs every variant on a few structures and compares with the released b-factors. CC BY-NC-SA 4.0
import os, sys, json, subprocess, importlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', 'repo'))
sys.path.insert(0, REPO)
import torch as pt
pt.set_num_threads(1)
from src.data_encoding import encode_structure, encode_features, extract_topology
from src.dataset import collate_batch_features
from sklearn.metrics import roc_auc_score

sys.path.insert(0, HERE)
from pesto_rerun import fetch_assembly, build_assembly

VARIANTS = {
    'i_v3_0': ('model/save/i_v3_0_2021-05-27_14-27', (True, True, True)),
    'i_v3_1': ('model/save/i_v3_1_2021-05-28_12-40', (True, True, True)),
    'i_v4_0': ('model/save/i_v4_0_2021-09-07_11-20', (True, False, False)),
    'i_v4_1': ('model/save/i_v4_1_2021-09-07_11-21', (True, False, False)),
}
KEYS = ['5J57/1/A:0', '1EWY/1/A:0', '3BH6/1/B:0']


def git_show(path):
    return subprocess.run(['git', 'cat-file', '-p', 'HEAD:' + path], cwd=REPO,
                          capture_output=True).stdout.decode('utf-8', 'replace')


def ca_col(text, lo, hi):
    return np.array([float(l[lo:hi]) for l in text.splitlines()
                     if l[:4] == 'ATOM' and l[12:15].strip() == 'CA'])


def load(save_rel):
    save = os.path.join(REPO, save_rel)
    for m in ['config', 'model']:
        sys.modules.pop(m, None)
    sys.path.insert(0, save)
    cfg = importlib.import_module('config')
    mod = importlib.import_module('model')
    m = mod.Model(cfg.config_model)
    m.load_state_dict(pt.load(os.path.join(save, 'model_ckpt.pt'), map_location='cpu'))
    sys.path.remove(save)
    return m.eval()


def run(model, s, flags):
    X, M = encode_structure(s)
    qe, qr, qn = encode_features(s)
    q = pt.cat([x for x, f in zip([qe, qr, qn], flags) if f], dim=1)
    ids_topk = extract_topology(X, 64)[0]
    X, ids_topk, q, M = collate_batch_features([[X, ids_topk, q, M]])
    with pt.no_grad():
        return pt.sigmoid(model(X, ids_topk, q, M.float()))[:, 0].numpy()


structs = {}
for key in KEYS:
    pid, ba, cid = key.split('/')
    fp = fetch_assembly(pid, int(ba))
    entries, _ = build_assembly(fp, targets={cid.split(':')[0]})
    structs[key] = entries[cid]

for name, (rel, flags) in VARIANTS.items():
    try:
        model = load(rel)
    except Exception as e:
        print(name, 'load failed:', e)
        continue
    for key in KEYS:
        s, y = structs[key]
        p = run(model, s, flags)
        pid, ba, cid = key.split('/')
        base = 'pdbs_test/%s_%s_%s_%s' % (pid[1:3].upper(), pid.upper(), ba, cid)
        rel_p = ca_col(git_show(base + '.pdb'), 60, 66)
        ok = rel_p.shape == p.shape
        print('%-7s %-13s auc=%.4f  max|p-released|=%s  released_auc=%.4f' % (
            name, key, roc_auc_score(y, p),
            '%.3f' % np.max(np.abs(np.round(p, 2) - rel_p)) if ok else 'size',
            roc_auc_score(y, rel_p) if ok else float('nan')))
