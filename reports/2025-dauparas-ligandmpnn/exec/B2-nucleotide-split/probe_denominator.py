"""Our main reading of 'near' gives fewer scored positions than the authors' numbers imply.
This recovers the denominator they must have used: a per-protein value is a mean of 10
per-sequence values, each a count over n positions, so value * n * 10 / 100 has to be a
whole number. Then it prints n under four readings of 'near' for comparison.

Readings:
  sc    side-chain atoms only (N, CA, C, O excluded) - the Results wording, our main
  all   every parsed heavy atom of the residue, backbone included - the Fig. 2a legend
  cb    the model's own virtual CB only
  allcb every heavy atom plus the virtual CB (covers glycine)
"""
import json
import os
import sys

import numpy as np

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
sys.path.insert(0, os.path.join(ROOT, "repo"))
from data_utils import parse_PDB  # noqa: E402

BACKBONE_IDX = [0, 1, 2, 4]
SC_IDX = [i for i in range(37) if i not in BACKBONE_IDX and i != 36]
ALL_IDX = [i for i in range(37) if i != 36]
CUTOFF = 5.0


def virtual_cb(out):
    xyz = out["xyz_37"].numpy()
    N, CA, C = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    b, c = CA - N, C - CA
    a = np.cross(b, c, axis=-1)
    return -0.58273431 * a + 0.56802827 * b - 0.54067466 * c + CA


def near_counts(pid, flavor="biounit1"):
    out, _b, _o, _i, _w = parse_PDB(
        os.path.join(ROOT, "data/structures", flavor, pid + ".pdb"), parse_all_atoms=True
    )
    xyz = out["xyz_37"].numpy()
    m = out["xyz_37_m"].numpy().astype(bool)
    Y = out["Y"].numpy()[out["Y_m"].numpy().astype(bool)]
    L = xyz.shape[0]
    res = {}

    def count(idx_list, extra=None):
        pts, owner = [], []
        for i in idx_list:
            keep = m[:, i]
            pts.append(xyz[keep, i, :])
            owner.append(np.arange(L)[keep])
        if extra is not None:
            pts.append(extra)
            owner.append(np.arange(L))
        pts = np.concatenate(pts, 0)
        owner = np.concatenate(owner, 0)
        near = np.zeros(L, dtype=bool)
        for a in range(0, pts.shape[0], 20000):
            blk = pts[a:a + 20000]
            d2 = ((blk[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
            hit = (d2 <= CUTOFF * CUTOFF).any(1)
            near[owner[a:a + 20000][hit]] = True
        return int(near.sum())

    cb = virtual_cb(out)
    res["sc"] = count(SC_IDX)
    res["all"] = count(ALL_IDX)
    res["cb"] = count([], extra=cb)
    res["allcb"] = count(ALL_IDX, extra=cb)
    res["L"] = L
    return res


def implied_n(value, nmax=400):
    """ns for which value could be a mean of 10 counts over n positions"""
    out = []
    for n in range(1, nmax + 1):
        x = value * n * 10.0 / 100.0
        if abs(x - round(x)) < 1e-6:
            out.append(n)
    return out[:4]


theirs = json.load(open(os.path.join(ROOT, "exec/B2-nucleotide-split/authors_fig2a_nucleotide.json")))
ids = theirs["ids"]
probe = sys.argv[1:] or ["3adl", "6fqr", "1ec6", "1am9", "1a0a", "1an4", "6od4", "2ypb"]
for pid in probe:
    k = ids.index(pid)
    c = near_counts(pid)
    print(f"{pid}: L={c['L']} sc={c['sc']} all={c['all']} cb={c['cb']} allcb={c['allcb']} "
          f"| authors LMPNN={theirs['LigandMPNN'][k]:.4f} implied n={implied_n(theirs['LigandMPNN'][k])} "
          f"| PMPNN={theirs['ProteinMPNN'][k]:.4f} implied n={implied_n(theirs['ProteinMPNN'][k])}")
