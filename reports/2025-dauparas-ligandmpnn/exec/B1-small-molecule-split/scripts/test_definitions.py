"""Which neighbourhood definition reproduces the authors' scored-position counts?

Test, per protein: do all three Source Data values become integers when multiplied
by 10 * n_near for the candidate definition? That is a strong check, because a
wrong count almost never satisfies three ratios at once.
"""
import csv
import json
import os

import numpy as np
from prody import parsePDB, confProDy

confProDy(verbosity="none")

SD = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/sd/x/s2"
BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"
BB = {"N", "CA", "C", "O", "OXT"}

z = np.load(os.path.join(SD, "fig_2_1_2.npz"), allow_pickle=True)
names = [str(n)[:-4] for n in z["names"]]
vals = {n: [float(z["p1x"][i]), float(z["p1y"][i])] for i, n in enumerate(names)}
rows = list(csv.DictReader(open(os.path.join(SD, "fig_2_1_1.csv"))))
pmp = [float(r["probs"]) for r in rows if r["types"] == "ProteinMPNN"]
for i, n in enumerate(names):
    vals[n].append(pmp[i])

man = {r["name"][:-4]: r for r in json.load(open(os.path.join(BASE, "inputs_manifest.json")))["records"]}
ASYM = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/structures/asym"
BIO = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/data/structures/biounit1"


def virtual_cb(n, ca, c):
    b = ca - n
    cc = c - ca
    a = np.cross(b, cc, axis=-1)
    return -0.58273431 * a + 0.56802827 * b - 0.54067466 * cc + ca


def counts(path, chain=None, ligand=None, ligand_only=True):
    """Return dict of definition -> n_near for one structure."""
    atoms = parsePDB(path)
    if atoms is None:
        return None
    atoms = atoms.select("occupancy > 0")
    if chain:
        sel = atoms.select("protein and chain " + chain)
    else:
        sel = atoms.select("protein")
    if sel is None:
        return None

    het = atoms.select("not protein and not water")
    if het is None:
        return None
    hn = het.getResnames()
    if ligand_only and ligand is not None:
        keep = hn == ligand
        if not keep.any():
            return None
        het = het[np.where(keep)[0]]
    y = het.getCoords()[np.array([e.strip().upper() != "H" for e in het.getElements()])]
    if len(y) == 0:
        return None

    ca = sel.select("name CA")
    keys = list(zip(ca.getChids(), [int(v) for v in ca.getResnums()], ca.getIcodes()))
    pos = {k: i for i, k in enumerate(keys)}
    L = len(keys)

    names_a = sel.getNames()
    elem_a = sel.getElements()
    xyz_a = sel.getCoords()
    key_a = list(zip(sel.getChids(), [int(v) for v in sel.getResnums()], sel.getIcodes()))

    def near_of(mask_atoms):
        idx = np.where(mask_atoms)[0]
        if len(idx) == 0:
            return np.zeros(L, bool)
        xyz = xyz_a[idx]
        hit = np.zeros(len(idx), bool)
        for s in range(0, len(idx), 4096):
            d2 = ((xyz[s:s + 4096, None, :] - y[None, :, :]) ** 2).sum(-1)
            hit[s:s + 4096] = d2.min(1) <= 25.0
        out = np.zeros(L, bool)
        for h, j in zip(hit, idx):
            if h and key_a[j] in pos:
                out[pos[key_a[j]]] = True
        return out

    heavy = np.array([e.strip().upper() != "H" for e in elem_a])
    sidechain = np.array([n not in BB for n in names_a]) & heavy

    res = {}
    res["sidechain_heavy"] = int(near_of(sidechain).sum())
    res["any_heavy_atom"] = int(near_of(heavy).sum())
    res["CA_only"] = int(near_of((names_a == "CA") & heavy).sum())
    res["CB_only"] = int(near_of((names_a == "CB") & heavy).sum())

    # virtual CB for every residue, as in the model's featurization
    n_xyz = {}
    for nm, k, x in zip(names_a, key_a, xyz_a):
        if nm in ("N", "CA", "C"):
            n_xyz.setdefault(k, {})[nm] = x
    cb = np.full((L, 3), 1e6, dtype=np.float32)
    for k, d in n_xyz.items():
        if k in pos and len(d) == 3:
            cb[pos[k]] = virtual_cb(d["N"], d["CA"], d["C"])
    d2 = ((cb[:, None, :] - y[None, :, :]) ** 2).sum(-1)
    res["virtual_CB"] = int((d2.min(1) <= 25.0).sum())
    res["n_res"] = L
    return res


DEFS = ["sidechain_heavy", "any_heavy_atom", "CA_only", "CB_only", "virtual_CB"]
variants = {
    "asym_chain_named_ligand": dict(root=None, chain=True, ligand_only=True),
    "asym_chain_all_hetero": dict(root=ASYM, chain=True, ligand_only=False),
    "asym_allchains_all_hetero": dict(root=ASYM, chain=False, ligand_only=False),
    "biounit_allchains_all_hetero": dict(root=BIO, chain=False, ligand_only=False),
}

score = {v: {d: 0 for d in DEFS} for v in variants}
total = {v: 0 for v in variants}
examples = {}

for n in names:
    rec = man[n]
    v3 = np.array(vals[n]) / 100.0
    for vname, cfg in variants.items():
        if cfg["root"] is None:
            path = rec["input"]
        else:
            path = os.path.join(cfg["root"], rec["pdb_id"] + (".pdb" if cfg["root"] == ASYM else ".pdb1"))
        if not os.path.exists(path):
            continue
        c = counts(path, rec["chain"] if cfg["chain"] else None,
                   rec["ligand"], cfg["ligand_only"])
        if c is None:
            continue
        total[vname] += 1
        for d in DEFS:
            k = v3 * 10 * c[d]
            if c[d] > 0 and np.abs(k - np.round(k)).max() < 2e-3:
                score[vname][d] += 1
        if n in names[:5]:
            examples.setdefault(n, {})[vname] = {d: c[d] for d in DEFS}

inf = json.load(open(os.path.join(BASE, "inferred_n_near.json")))
print("smallest denominator consistent with Source Data, first 5:",
      {n: inf[n]["inferred"] for n in names[:5]})
for vname in variants:
    print("\n%s (n=%d)" % (vname, total[vname]))
    for d in DEFS:
        print("   %-18s matches %3d / %d" % (d, score[vname][d], total[vname]))
print("\nexamples:", json.dumps(examples, indent=1)[:1500])
json.dump({"score": score, "total": total}, open(os.path.join(BASE, "definition_test.json"), "w"), indent=1)
