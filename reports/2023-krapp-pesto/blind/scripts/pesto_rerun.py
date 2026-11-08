# Blind rerun of PeSTo (Krapp et al., Nat Commun 14:2175, 2023) on CPU.
# Licence: CC BY-NC-SA 4.0, same as the authors' code and weights. Non-commercial use only.
# The parsing, the feature encoding and the network come from the authors' published source
# (repo/src, repo/model/save/i_v4_1_2021-09-07_11-21). The dataset assembly, the interface labels
# and the scoring are rewritten here from the paper and from processing/build_dataset.py, so they
# do not depend on the authors' HDF5 file, which is not published.
import os, sys, json, time, argparse, urllib.request, urllib.error
import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'repo'))
SAVE = os.path.join(REPO, 'model/save/i_v4_1_2021-09-07_11-21')
sys.path.insert(0, REPO)
sys.path.append(SAVE)  # repo/src must win: the snapshot under save/ is a 2021 copy that needs numpy<1.20

import torch as pt
pt.set_num_threads(int(os.environ.get('N_THREADS', '4')))

from src.structure_io import read_pdb
from src.structure import clean_structure, tag_hetatm_chains, split_by_chain, \
    filter_non_atomic_subunits, remove_duplicate_tagged_subunits
from src.data_encoding import encode_structure, encode_features, extract_topology, categ_to_resnames
from src.dataset import collate_batch_features
from scipy.spatial import cKDTree
from sklearn.metrics import roc_auc_score

MAX_NUM_ATOMS = 1024 * 8
R_THR = 5.0
AA20 = set(categ_to_resnames['protein'])
MOL79 = set(categ_to_resnames['protein'] + categ_to_resnames['rna'] + categ_to_resnames['dna']
            + categ_to_resnames['ion'] + categ_to_resnames['ligand'] + categ_to_resnames['lipid'])
BIOUNIT_URL = "https://files.rcsb.org/pub/pdb/data/biounit/PDB/divided/{xx}/{pid}.pdb{n}.gz"
CACHE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'biounits'))


def fetch_assembly(pdbid, n):
    # Return the local path of assembly n, or None when the PDB entry has no such assembly
    pid = pdbid.lower()
    xx = pid[1:3]
    d = os.path.join(CACHE, xx)
    os.makedirs(d, exist_ok=True)
    fp = os.path.join(d, "%s.pdb%d.gz" % (pid, n))
    miss = fp + ".404"
    if os.path.exists(fp):
        return fp
    if os.path.exists(miss):
        return None
    url = BIOUNIT_URL.format(xx=xx, pid=pid, n=n)
    # the network drops now and then, so retry instead of losing the whole run
    for attempt in range(8):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                data = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(miss, 'w').close()
                return None
            if attempt == 7:
                raise
            time.sleep(5 * (attempt + 1))
        except Exception:
            if attempt == 7:
                raise
            time.sleep(5 * (attempt + 1))
    with open(fp, 'wb') as f:
        f.write(data)
    return fp


def assemblies_of(pdbid, max_n=30):
    out = []
    for n in range(1, max_n + 1):
        fp = fetch_assembly(pdbid, n)
        if fp is None:
            break
        out.append((n, fp))
    return out


def contact_pairs(xyz_a, xyz_b, r):
    # same pairs as a full distance matrix with D < r, only without building it
    ta, tb = cKDTree(xyz_a), cKDTree(xyz_b)
    d = ta.sparse_distance_matrix(tb, r, output_type='ndarray')
    m = d['v'] < r  # sparse_distance_matrix is inclusive of r, the authors use a strict <
    return d['i'][m].astype(np.int64), d['j'][m].astype(np.int64)


def build_assembly(fp, targets=None):
    # Replicates processing/build_dataset.py and returns {cid: (subunit, protein_label)} for the
    # subunits that would end up in the authors' dataset with a protein-type interface
    structure = read_pdb(fp)
    n_raw = int(structure['xyz'].shape[0])
    if n_raw >= MAX_NUM_ATOMS:
        return {}, dict(skip='size', n_raw=n_raw)
    structure = clean_structure(structure)
    structure = tag_hetatm_chains(structure)
    subunits = split_by_chain(structure)
    subunits = filter_non_atomic_subunits(subunits)
    if len(subunits) < 2:
        return {}, dict(skip='monomer', n_raw=n_raw)
    subunits = remove_duplicate_tagged_subunits(subunits)
    snames = list(subunits)

    qualifies = dict((c, False) for c in snames)
    pos = dict((c, set()) for c in snames)
    # only the pairs that touch a chain we are asked about: the label and the qualification of a
    # subunit depend on its own contacts only, so the other pairs would be thrown away anyway
    def wanted(c):
        p = c.split(':')
        return targets is None or (len(p) == 2 and p[0] in targets)

    for i in range(len(snames)):
        for j in range(i + 1, len(snames)):
            ci, cj = snames[i], snames[j]
            if not (wanted(ci) or wanted(cj)):
                continue
            si, sj = subunits[ci], subunits[cj]
            ia, ib = contact_pairs(si['xyz'], sj['xyz'], R_THR)
            if ia.shape[0] == 0:
                continue
            rni = si['resname'][ia]
            rnj = sj['resname'][ib]
            ai = np.array([x in AA20 for x in rni])
            aj = np.array([x in AA20 for x in rnj])
            mi = np.array([x in MOL79 for x in rni])
            mj = np.array([x in MOL79 for x in rnj])
            # the entry exists if the target residue is an amino acid and the partner is in the 79 list
            if np.any(ai & mj):
                qualifies[ci] = True
            if np.any(aj & mi):
                qualifies[cj] = True
            # protein-protein label: both residues are standard amino acids
            m = ai & aj
            if np.any(m):
                pos[ci].update(si['resid'][ia[m]].tolist())
                pos[cj].update(sj['resid'][ib[m]].tolist())

    out = {}
    for c in snames:
        if not qualifies[c]:
            continue
        s = subunits[c]
        uresids = np.unique(s['resid'])
        pset = np.array(sorted(pos[c]), dtype=uresids.dtype) if pos[c] else np.array([], dtype=uresids.dtype)
        y = np.isin(uresids, pset).astype(np.float32)
        out[c] = (s, y)
    return out, dict(skip=None, n_raw=n_raw, n_subunits=len(snames))


def load_model():
    from config import config_model
    from model import Model
    m = Model(config_model)
    m.load_state_dict(pt.load(os.path.join(SAVE, 'model_ckpt.pt'), map_location=pt.device('cpu')))
    return m.eval()


def predict(model, s):
    X, M = encode_structure(s)
    qe, qr, qn = encode_features(s)
    q = qe  # i_v4_1 uses the element one-hot only, features_flags = (True, False, False)
    ids_topk = extract_topology(X, 64)[0]
    X, ids_topk, q, M = collate_batch_features([[X, ids_topk, q, M]])
    with pt.no_grad():
        z = model(X, ids_topk, q, M.float())
        p = pt.sigmoid(z)
    return p[:, 0].numpy()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sids', required=True, help='file with one sid (PDBID_chain) per line')
    ap.add_argument('--mode', choices=['all_ba', 'first_ba'], required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--masif-json', default=None, help='apply the residue count filter against this file')
    ap.add_argument('--keep-scores', action='store_true')
    a = ap.parse_args()

    sids = [l.strip() for l in open(a.sids) if l.strip()]
    want = {}
    for s in sids:
        pid, ch = s.split('_')
        want.setdefault(pid.upper(), set()).add(ch)

    masif = json.load(open(a.masif_json)) if a.masif_json else None
    model = load_model()

    done = set()
    if os.path.exists(a.out):
        for l in open(a.out):
            try:
                done.add(json.loads(l)['key'])
            except Exception:
                pass
    fo = open(a.out, 'a', buffering=1)

    pids = sorted(want)
    for k, pid in enumerate(pids):
        hit = False
        n = 0
        while True:
            n += 1
            fp = fetch_assembly(pid, n)
            if fp is None:
                if n == 1:
                    fo.write(json.dumps(dict(key=pid + '/NA', sid=None, note='no legacy biounit file')) + '\n')
                break
            entries, info = build_assembly(fp, targets=want[pid])
            for cid in sorted(entries):
                s, y = entries[cid]
                parts = cid.split(':')
                if len(parts) != 2:
                    continue  # tagged non-polymer subunit, not a chain
                if parts[0] not in want[pid]:
                    continue
                hit = True
                sid = '%s_%s' % (pid, parts[0])
                key = '%s/%d/%s' % (pid, n, cid)
                nres = int(y.shape[0])
                rec = dict(key=key, sid=sid, ba=n, cid=cid, n_res=nres,
                           n_atoms=int(s['xyz'].shape[0]), n_pos=int(y.sum()),
                           n_raw=info.get('n_raw'), n_subunits=info.get('n_subunits'))
                if masif is not None:
                    rec['n_masif'] = len(masif.get(sid, []))
                    if rec['n_masif'] != nres:
                        rec['note'] = 'residue count mismatch, excluded from the set'
                        if key not in done:
                            fo.write(json.dumps(rec) + '\n')
                        continue
                if key in done:
                    continue
                t0 = time.time()
                p = predict(model, s)
                rec['t'] = round(time.time() - t0, 2)
                rec['auc'] = float(roc_auc_score(y, p)) if (0 < y.sum() < y.shape[0]) else None
                if a.keep_scores:
                    rec['p'] = [round(float(v), 6) for v in p]
                    rec['y'] = [int(v) for v in y]
                fo.write(json.dumps(rec) + '\n')
            if a.mode == 'first_ba' and hit:
                break
        print('[%d/%d] %s' % (k + 1, len(pids), pid), flush=True)
    fo.close()


if __name__ == '__main__':
    main()
