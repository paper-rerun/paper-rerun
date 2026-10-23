#!/usr/bin/env python3
"""
Near-ligand sequence recovery from the stats files run.py wrote.

The paper (Fig. 2a) reports recovery for "residues that are close to the ligand, having
side-chain atoms within 5.0 A of any non-protein atoms", ten designed sequences per
protein, median across the proteins of a test set.

We reuse the authors' own parse_PDB so the residue ordering here is exactly the ordering
the model saw, and so "non-protein atoms" means the same set the model got as context
(prody "not protein and not water", hydrogens and unknown elements dropped).
"""
import argparse
import json
import os
import sys

import numpy as np
import torch

ROOT = "/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn"
sys.path.insert(0, os.path.join(ROOT, "repo"))
from data_utils import parse_PDB  # noqa: E402

PDBS = os.path.join(ROOT, "pdbs")
# Element numbers (Z) of the metals, for the --context metal variant. parse_PDB stores
# Y_t as the 1-based index into its element_list, which equals Z for every element here.
METAL_Z = set(
    [3, 4, 11, 12, 13]
    + list(range(19, 32))
    + list(range(37, 51))
    + list(range(55, 85))
    + list(range(87, 104))
)
SPLITS = {
    "small_molecule": "test_small_molecule.json",
    "nucleotide": "test_nucleotide.json",
    "metal": "test_metal.json",
}
# atom_order in data_utils: 0=N 1=CA 2=C 3=CB 4=O ... 36=OXT
SIDE_CHAIN_IDX = np.array([3] + list(range(5, 36)))
CUTOFF = 5.0
X_TOKEN = 20


def largest_het_coords(pdb_path):
    """Heavy-atom coords of the single biggest non-protein, non-water residue.

    Stands in for "the ligand" of a small-molecule entry. A biounit also holds buffer,
    cryoprotectant and ion junk, and residues that only touch that junk are not what the
    paper means by ligand-binding residues. Same prody selection and occupancy filter the
    authors' parse_PDB uses, so the atoms come from the same pool.
    """
    from prody import parsePDB

    atoms = parsePDB(pdb_path).select("occupancy > 0")
    het = atoms.select("not protein and not water")
    if het is None:
        return None
    el = np.array([e.upper() for e in het.getElements()])
    keep = (el != "H") & (el != "D") & (el != "")
    if keep.sum() == 0:
        return None
    coords, el = het.getCoords()[keep], el[keep]
    chids, resnums, icodes = het.getChids()[keep], het.getResnums()[keep], het.getIcodes()[keep]
    keys = np.array([f"{c}_{r}_{i}" for c, r, i in zip(chids, resnums, icodes)])
    uniq, counts = np.unique(keys, return_counts=True)
    best = uniq[np.argmax(counts)]
    return coords[keys == best]


def near_ligand_mask(pdb_path, context="all"):
    """Bool per residue: has a side-chain heavy atom within 5 A of a context atom.

    context="all": every non-protein, non-water heavy atom, i.e. exactly the set the model
    is given. This is the paper's literal wording.
    context="metal": only metal atoms.
    context="largest": only the biggest single het residue.
    The last two test whether the paper's "ligand" is the curated ligand of the split rather
    than every het atom sitting in the biounit.
    """
    out, _, _, _, _ = parse_PDB(pdb_path, device="cpu", parse_all_atoms=True)
    xyz = out["xyz_37"].numpy()[:, SIDE_CHAIN_IDX, :]
    xyz_m = out["xyz_37_m"].numpy()[:, SIDE_CHAIN_IDX].astype(bool)
    Y = out["Y"].numpy()
    Y_m = out["Y_m"].numpy().astype(bool)
    if context == "metal":
        Y_t = out["Y_t"].numpy()
        Y_m = Y_m & np.isin(Y_t, list(METAL_Z))
    if context == "largest":
        Y = largest_het_coords(pdb_path)
        if Y is None:
            return np.zeros(xyz.shape[0], bool), out
        Y_m = np.ones(len(Y), bool)
    if Y_m.sum() == 0:
        return np.zeros(xyz.shape[0], bool), out
    if context != "largest":
        Y = Y[Y_m]

    near = np.zeros(xyz.shape[0], bool)
    # Chunk over residues: a big biounit times thousands of ligand atoms does not fit at once
    step = 2000
    for a in range(0, xyz.shape[0], step):
        b = min(a + step, xyz.shape[0])
        d = np.linalg.norm(xyz[a:b, :, None, :] - Y[None, None, :, :], axis=-1)
        d = np.where(xyz_m[a:b, :, None], d, np.inf)
        near[a:b] = (d < CUTOFF).any(axis=(1, 2))
    return near, out


def per_protein(model, pdb_id, cache, context="all"):
    stats = os.path.join(ROOT, "outputs", model, "stats", f"{pdb_id}.pt")
    if not os.path.exists(stats):
        return None
    d = torch.load(stats, map_location="cpu")
    gen = d["generated_sequences"].numpy()  # [n_seq, L]
    nat = d["native_sequence"].numpy()  # [L]
    bb_mask = d["mask"].numpy().astype(bool)
    chain_mask = d["chain_mask"].numpy().astype(bool)

    if pdb_id not in cache:
        cache[pdb_id] = near_ligand_mask(os.path.join(PDBS, f"{pdb_id}.pdb"), context)[0]
    near = cache[pdb_id]
    if near.shape[0] != nat.shape[0]:
        return {"error": f"length mismatch {near.shape[0]} vs {nat.shape[0]}"}

    sel = near & bb_mask & chain_mask & (nat != X_TOKEN)
    n = int(sel.sum())
    if n == 0:
        return {"n_residues": 0}
    hits = (gen[:, sel] == nat[None, sel])
    return {
        "n_residues": n,
        "n_seqs": int(gen.shape[0]),
        "rec_per_seq": hits.mean(axis=1).tolist(),
        "rec_mean": float(hits.mean()),
        "n_correct": int(hits.sum()),
        "n_total": int(hits.size),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("models", nargs="*", default=["ligand_mpnn", "protein_mpnn_32", "protein_mpnn_48"])
    ap.add_argument("--context", choices=["all", "metal", "largest"], default="all")
    ap.add_argument("--out", default="recovery_results.json")
    args = ap.parse_args()

    models = args.models or ["ligand_mpnn", "protein_mpnn_32", "protein_mpnn_48"]
    cache = {}
    results = {}
    for model in models:
        results[model] = {}
        for split, fname in SPLITS.items():
            ids = json.load(open(os.path.join(ROOT, "repo/training", fname)))
            per = {}
            for pdb_id in ids:
                r = per_protein(model, pdb_id, cache, args.context)
                if r is not None:
                    per[pdb_id] = r
            vals = [v["rec_mean"] for v in per.values() if v.get("n_residues", 0) > 0]
            pooled_c = sum(v["n_correct"] for v in per.values() if v.get("n_residues", 0) > 0)
            pooled_t = sum(v["n_total"] for v in per.values() if v.get("n_residues", 0) > 0)
            results[model][split] = {
                "n_structures_in_split": len(ids),
                "n_scored": len(vals),
                "n_missing_stats": len([i for i in ids if i not in per]),
                "n_no_near_residues": len([v for v in per.values() if v.get("n_residues", 0) == 0]),
                "median_recovery": float(np.median(vals)) if vals else None,
                "mean_recovery": float(np.mean(vals)) if vals else None,
                "pooled_residue_recovery": pooled_c / pooled_t if pooled_t else None,
                "median_n_near_residues": float(np.median(
                    [v["n_residues"] for v in per.values() if v.get("n_residues", 0) > 0]
                )) if vals else None,
                "per_protein": per,
            }
            m = results[model][split]
            fmt = lambda v: "   n/a" if v is None else f"{v:.4f}"
            print(
                f"{model:22s} {split:15s} n={m['n_scored']:3d} "
                f"median={fmt(m['median_recovery'])} mean={fmt(m['mean_recovery'])} "
                f"pooled={fmt(m['pooled_residue_recovery'])} "
                f"missing={m['n_missing_stats']}",
                flush=True,
            )

    out = os.path.join(ROOT, "logs", args.out)
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
