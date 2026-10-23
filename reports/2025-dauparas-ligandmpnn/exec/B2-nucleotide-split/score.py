"""Scores C3 and C4: median per-protein native sequence recovery at residues whose
side-chain atoms sit within 5.0 A of any non-protein atom.

Geometry comes from the authors' own parse_PDB with parse_all_atoms=True, so the residue
order is identical to the one run.py designed in; the script asserts that the native
sequence in the .pt stats matches, which is what makes the index alignment safe.

Side-chain atoms = the 37-atom set minus N, CA, C, O (OXT is not even parsed in the
all-atom branch). Glycine therefore never qualifies and alanine qualifies through CB,
exactly as the claim definition fixed it.

Main number: positions near the ligand AND with a complete backbone (parse_PDB's own
mask), which is the mask the authors' get_seq_rec uses. The unmasked variant is printed
next to it so the choice is visible.
"""

import json
import os
import sys

import numpy as np
import torch

ROOT = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn"
sys.path.insert(0, os.path.join(ROOT, "repo"))
from data_utils import parse_PDB  # noqa: E402

ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
BACKBONE_IDX = [0, 1, 2, 4]  # N, CA, C, O in the 37-atom order
SIDE_CHAIN_IDX = [i for i in range(37) if i not in BACKBONE_IDX and i != 36]
ALL_ATOM_IDX = [i for i in range(37) if i != 36]  # the Fig. 2a legend reading
CUTOFF = 5.0

flavor = sys.argv[1]
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0  # smoke the metric on a few ids
out_rows = {}

ids = json.load(open(os.path.join(ROOT, "repo/training/test_nucleotide.json")))
if limit:
    ids = ids[:limit]

models = (("LigandMPNN", f"lmpnn_{flavor}"), ("ProteinMPNN", f"pmpnn_{flavor}"))
for tag, folder in models:
    if not os.path.isdir(os.path.join(ROOT, "exec/B2-nucleotide-split", folder, "stats")):
        print(f"skip {tag}: no stats yet")
        continue
    per_protein = []
    per_protein_nomask = []
    per_protein_allatom = []
    detail = []
    for pid in ids:
        pdb = os.path.join(ROOT, "data/structures", flavor, pid + ".pdb")
        stats = torch.load(
            os.path.join(ROOT, "exec/B2-nucleotide-split", folder, "stats", pid + ".pt"),
            map_location="cpu",
        )
        out, _bb, _oa, _ic, _w = parse_PDB(pdb, parse_all_atoms=True)

        native = out["S"].numpy().astype(np.int64)
        assert np.array_equal(native, stats["native_sequence"].numpy().astype(np.int64)), pid
        gen = stats["generated_sequences"].numpy().astype(np.int64)
        assert gen.shape == (10, native.shape[0]), (pid, gen.shape)

        xyz = out["xyz_37"].numpy()
        xyz_m = out["xyz_37_m"].numpy().astype(bool)
        Y = out["Y"].numpy()
        Y_m = out["Y_m"].numpy().astype(bool)
        Y = Y[Y_m]

        def near_set(idx_list):
            near = np.zeros(native.shape[0], dtype=bool)
            if Y.shape[0] == 0:
                return near
            pts = xyz[:, idx_list, :].reshape(-1, 3)
            keep = xyz_m[:, idx_list].reshape(-1)
            owner = np.repeat(np.arange(native.shape[0]), len(idx_list))[keep]
            pts = pts[keep]
            # chunked so a big assembly does not blow up the RAM
            for a in range(0, pts.shape[0], 20000):
                blk = pts[a:a + 20000]
                d2 = ((blk[:, None, :] - Y[None, :, :]) ** 2).sum(-1)
                hit = (d2 <= CUTOFF * CUTOFF).any(1)
                near[owner[a:a + 20000][hit]] = True
            return near

        near = near_set(SIDE_CHAIN_IDX)
        near_all = near_set(ALL_ATOM_IDX)

        bb_ok = out["xyz_37_m"].numpy()[:, BACKBONE_IDX].all(1)
        sel = near & bb_ok
        if sel.sum() == 0:
            raise SystemExit(f"{pid}: no near-ligand position with a complete backbone")

        rec = (gen[:, sel] == native[None, sel]).mean(1) * 100.0
        rec_nm = (gen[:, near] == native[None, near]).mean(1) * 100.0
        rec_all = (gen[:, near_all] == native[None, near_all]).mean(1) * 100.0
        per_protein.append(float(rec.mean()))
        per_protein_nomask.append(float(rec_nm.mean()))
        per_protein_allatom.append(float(rec_all.mean()))
        detail.append(
            dict(
                id=pid,
                n_res=int(native.shape[0]),
                n_context_atoms=int(Y.shape[0]),
                n_near=int(near.sum()),
                n_near_allatom=int(near_all.sum()),
                recovery_allatom=float(rec_all.mean()),
                n_near_bb_ok=int(sel.sum()),
                n_near_native_X=int((native[sel] == 20).sum()),
                recovery=float(rec.mean()),
                recovery_nomask=float(rec_nm.mean()),
                per_seq=[float(v) for v in rec],
            )
        )
        print(f"{tag} {pid} near={int(sel.sum())}/{native.shape[0]} rec={rec.mean():.3f}")

    med = float(np.median(per_protein))
    out_rows[tag] = dict(
        n=len(per_protein),
        median=med,
        mean=float(np.mean(per_protein)),
        median_nomask=float(np.median(per_protein_nomask)),
        median_allatom=float(np.median(per_protein_allatom)),
        mean_allatom=float(np.mean(per_protein_allatom)),
        detail=detail,
    )
    print(f"== {tag} {flavor}: n={len(per_protein)} median={med:.3f} "
          f"mean={np.mean(per_protein):.3f} median_nomask={np.median(per_protein_nomask):.3f} "
          f"median_allatom={np.median(per_protein_allatom):.3f}")

suffix = f"_first{limit}" if limit else ""
dest = os.path.join(ROOT, "exec/B2-nucleotide-split", f"results_{flavor}{suffix}.json")
json.dump(out_rows, open(dest, "w"), indent=1)
print("wrote", dest)
