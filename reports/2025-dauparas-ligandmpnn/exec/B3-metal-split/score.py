"""Score C5-LMPNN-METAL and C6-PMPNN-METAL.

Metric, exactly as fixed in the definitions:
  near_residue  -- a residue counts if any side-chain heavy atom (every atom of
                   the deposited residue other than N, CA, C, O, OXT) lies within
                   5.0 A of any context atom of the same input structure.
                   Context atoms are what the installed parse_PDB keeps: all
                   non-protein, non-water atoms, hydrogens masked out. Glycine
                   never qualifies, alanine qualifies through CB.
  recovery      -- per sequence, 100 * matches / near positions
  aggregation   -- mean over the 10 designed sequences, then median over proteins

Residue order comes from parse_PDB (CA order), the same order run.py used, and
the script asserts the native sequence it re-parses equals the one run.py saved.

Usage: score.py <flavor>   (flavor = biounit1 | asym)
"""

import json
import sys

import numpy as np
import torch

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
from data_utils import parse_PDB

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
EXEC = ROOT + "/exec/B3-metal-split"
CUTOFF = 5.0
BACKBONE = {"N", "CA", "C", "O", "OXT"}

# Copied verbatim from parse_PDB in repo/data_utils.py (it is a local there, not importable)
atom_order = {
    "N": 0, "CA": 1, "C": 2, "CB": 3, "O": 4, "CG": 5, "CG1": 6, "CG2": 7,
    "OG": 8, "OG1": 9, "SG": 10, "CD": 11, "CD1": 12, "CD2": 13, "ND1": 14,
    "ND2": 15, "OD1": 16, "OD2": 17, "SD": 18, "CE": 19, "CE1": 20, "CE2": 21,
    "CE3": 22, "NE": 23, "NE1": 24, "NE2": 25, "OE1": 26, "OE2": 27, "CH2": 28,
    "NH1": 29, "NH2": 30, "OH": 31, "CZ": 32, "CZ2": 33, "CZ3": 34, "NZ": 35,
    "OXT": 36,
}

flavor = sys.argv[1] if len(sys.argv) > 1 else "biounit1"
ids = json.load(open(ROOT + "/repo/training/test_metal.json"))

# Side-chain slots of the 37-atom representation
side_chain_idx = sorted(i for name, i in atom_order.items() if name not in BACKBONE)


def pdb_path(pdb_id, flav):
    """Same file the design run read: 5l70 comes from the column-fixed copy (fix_5l70.py)."""
    if pdb_id == "5l70":
        return "%s/fixed/%s/5l70.pdb" % (EXEC, flav)
    return "%s/data/structures/%s/%s.pdb" % (ROOT, flav, pdb_id)


def near_ligand_mask(pdb_path):
    """Boolean [L] over residues: has a side-chain heavy atom within 5 A of a context atom."""
    out, _, _, _, _ = parse_PDB(pdb_path, device="cpu", parse_all_atoms=True)
    xyz = out["xyz_37"].numpy()[:, side_chain_idx, :]
    xyz_m = out["xyz_37_m"].numpy()[:, side_chain_idx].astype(bool)
    Y = out["Y"].numpy()
    Y_m = out["Y_m"].numpy().astype(bool)
    native = out["S"].numpy()

    L = xyz.shape[0]
    near = np.zeros(L, dtype=bool)
    if Y_m.sum() == 0:
        return near, native, 0
    Y = Y[Y_m]
    # Chunk over residues so a big assembly times a big ligand set still fits
    for start in range(0, L, 256):
        stop = min(start + 256, L)
        sc = xyz[start:stop]                       # [n, A, 3]
        m = xyz_m[start:stop]                      # [n, A]
        d = np.linalg.norm(sc[:, :, None, :] - Y[None, None, :, :], axis=-1)  # [n, A, B]
        d = np.where(m[:, :, None], d, np.inf)
        near[start:stop] = (d <= CUTOFF).any(axis=(1, 2))
    return near, native, int(Y.shape[0])


def score_model(tag):
    rows = []
    for pdb_id in ids:
        path = pdb_path(pdb_id, flavor)
        stats = torch.load("%s/out/%s_%s/stats/%s.pt" % (EXEC, tag, flavor, pdb_id),
                           map_location="cpu")
        near, native, n_ctx = near_ligand_mask(path)
        saved_native = stats["native_sequence"].numpy()
        assert np.array_equal(saved_native, native), pdb_id  # same residue order
        gen = stats["generated_sequences"].numpy()           # [n_seq, L]
        assert gen.shape[0] == 10, (pdb_id, gen.shape)

        designed = (stats["mask"].numpy() > 0) & (stats["chain_mask"].numpy() > 0)
        sel = near & designed
        n_near = int(sel.sum())
        if n_near == 0:
            per_seq = []
            mean_rec = float("nan")
        else:
            per_seq = (100.0 * (gen[:, sel] == native[None, sel]).mean(axis=1)).tolist()
            mean_rec = float(np.mean(per_seq))
        rows.append({
            "id": pdb_id,
            "n_residues": int(len(native)),
            "n_context_atoms": n_ctx,
            "n_near": n_near,
            "per_sequence_recovery": per_seq,
            "recovery": mean_rec,
        })
        print("%-6s %-5s L=%-5d ctx=%-5d near=%-4d rec=%s"
              % (tag, pdb_id, len(native), n_ctx, n_near,
                 "nan" if n_near == 0 else "%.3f" % mean_rec), flush=True)

    vals = np.array([r["recovery"] for r in rows], dtype=float)
    ok = ~np.isnan(vals)
    result = {
        "model": tag,
        "flavor": flavor,
        "n_proteins": int(len(rows)),
        "n_proteins_with_near_positions": int(ok.sum()),
        "median_recovery": float(np.median(vals[ok])),
        "mean_recovery": float(np.mean(vals[ok])),
        "total_near_positions": int(sum(r["n_near"] for r in rows)),
        "per_protein": rows,
    }
    path = "%s/recovery_%s_%s.json" % (EXEC, tag, flavor)
    json.dump(result, open(path, "w"), indent=1)
    print("%s %s: median %.3f  mean %.3f  (n=%d, %d with near positions) -> %s"
          % (tag, flavor, result["median_recovery"], result["mean_recovery"],
             result["n_proteins"], result["n_proteins_with_near_positions"], path))
    return result


def self_check():
    """One runnable check of the distance logic, independent of any structure."""
    import numpy as np
    sc = np.array([[[0.0, 0, 0], [10.0, 0, 0]]])        # 1 residue, 2 side-chain atoms
    m = np.array([[True, True]])
    Y = np.array([[4.9, 0.0, 0.0]])
    d = np.linalg.norm(sc[:, :, None, :] - Y[None, None, :, :], axis=-1)
    d = np.where(m[:, :, None], d, np.inf)
    assert (d <= CUTOFF).any(axis=(1, 2))[0]
    m2 = np.array([[False, True]])                       # first atom missing -> too far
    d2 = np.where(m2[:, :, None], np.linalg.norm(
        sc[:, :, None, :] - Y[None, None, :, :], axis=-1), np.inf)
    assert not (d2 <= CUTOFF).any(axis=(1, 2))[0]
    assert "CB" not in BACKBONE and "OXT" in BACKBONE
    print("self-check ok")


if __name__ == "__main__":
    self_check()
    tags = sys.argv[2].split(",") if len(sys.argv) > 2 else ["lmpnn", "pmpnn"]
    out = {t: score_model(t) for t in tags}
    json.dump({t: {k: v for k, v in r.items() if k != "per_protein"}
               for t, r in out.items()},
              open("%s/summary_%s.json" % (EXEC, flavor), "w"), indent=1)
