"""Extra analyses, run only after the main result. Nothing here changes the verdict.

Variant A  all context atoms, asymmetric unit instead of biological assembly 1
Variant B  context restricted to metal/ion atoms (biounit1 and asym)

Variant B exists because the authors' per-protein values on the metal panel sit on
a much coarser grid than ours (1dwh LigandMPNN = 80.0 = 24/30), which says they
scored far fewer positions per protein than "every non-protein atom" gives.

Usage: variants.py <flavor> <context>    context = all | metal
"""

import json
import sys

import numpy as np
import torch

# exec/ must come first: the authors' repo ships its own score.py
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B3-metal-split")

import score
from data_utils import parse_PDB, element_dict_rev

# Everything that is not an organic-ligand element: what is left is metals and ions
ORGANIC = {"H", "C", "N", "O", "P", "S", "SE", "F", "CL", "BR", "I", "B"}

flavor, context = sys.argv[1], sys.argv[2]
ids = json.load(open(score.ROOT + "/repo/training/test_metal.json"))


def masks(pdb_path):
    out, _, _, _, _ = parse_PDB(pdb_path, device="cpu", parse_all_atoms=True)
    xyz = out["xyz_37"].numpy()[:, score.side_chain_idx, :]
    xyz_m = out["xyz_37_m"].numpy()[:, score.side_chain_idx].astype(bool)
    Y = out["Y"].numpy()
    Y_m = out["Y_m"].numpy().astype(bool)
    Y_t = out["Y_t"].numpy()
    native = out["S"].numpy()

    keep = Y_m.copy()
    if context == "metal":
        elems = np.array([element_dict_rev.get(int(t), "?") for t in Y_t])
        keep = keep & np.array([e.upper() not in ORGANIC for e in elems])
    Y = Y[keep]

    near = np.zeros(xyz.shape[0], dtype=bool)
    if Y.shape[0]:
        for a in range(0, xyz.shape[0], 256):
            b = min(a + 256, xyz.shape[0])
            d = np.linalg.norm(xyz[a:b, :, None, :] - Y[None, None, :, :], axis=-1)
            d = np.where(xyz_m[a:b, :, None], d, np.inf)
            near[a:b] = (d <= score.CUTOFF).any(axis=(1, 2))
    return near, native, int(Y.shape[0])


res = {}
for tag in ("lmpnn", "pmpnn"):
    vals, nears = [], []
    for pdb_id in ids:
        st = torch.load("%s/out/%s_%s/stats/%s.pt" % (score.EXEC, tag, flavor, pdb_id),
                        map_location="cpu")
        near, native, n_ctx = masks(score.pdb_path(pdb_id, flavor))
        assert np.array_equal(st["native_sequence"].numpy(), native), pdb_id
        sel = near & (st["mask"].numpy() > 0) & (st["chain_mask"].numpy() > 0)
        nears.append(int(sel.sum()))
        if sel.sum() == 0:
            vals.append(np.nan)
            continue
        gen = st["generated_sequences"].numpy()
        vals.append(float((100.0 * (gen[:, sel] == native[None, sel]).mean(axis=1)).mean()))
    v = np.array(vals, dtype=float)
    ok = ~np.isnan(v)
    res[tag] = {
        "median": float(np.median(v[ok])),
        "mean": float(np.mean(v[ok])),
        "n_with_positions": int(ok.sum()),
        "median_near_positions": float(np.median(nears)),
        "per_protein": vals,
        "near_positions": nears,
    }
    print("%s %s/%s: median %.3f mean %.3f  (median near positions %.1f, %d/%d proteins)"
          % (tag, flavor, context, res[tag]["median"], res[tag]["mean"],
             res[tag]["median_near_positions"], ok.sum(), len(ids)))

json.dump(res, open("%s/variant_%s_%s.json" % (score.EXEC, flavor, context), "w"), indent=1)
