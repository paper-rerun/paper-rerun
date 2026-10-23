#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"
python - <<'PY'
import sys, numpy as np, torch
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B3-metal-split")
sys.argv = ["x", "biounit1", "metal"]
import score
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/repo")
from data_utils import parse_PDB, element_dict_rev
ORGANIC = {"H","C","N","O","P","S","SE","F","CL","BR","I","B"}
for pid in ("1dwh","1e4m","1e6s","1e72","1f35","1fee"):
    out,_,_,_,_ = parse_PDB("%s/data/structures/biounit1/%s.pdb"%(score.ROOT,pid), device="cpu", parse_all_atoms=True)
    xyz = out["xyz_37"].numpy()[:, score.side_chain_idx, :]
    xm = out["xyz_37_m"].numpy()[:, score.side_chain_idx].astype(bool)
    Yt = out["Y_t"].numpy(); Y = out["Y"].numpy()
    el = np.array([element_dict_rev.get(int(t),"?") for t in Yt])
    keep = np.array([e.upper() not in ORGANIC for e in el])
    Ym = Y[keep]
    d = np.linalg.norm(xyz[:,:,None,:] - Ym[None,None,:,:], axis=-1) if len(Ym) else None
    near = (np.where(xm[:,:,None], d, np.inf) <= 5.0).any(axis=(1,2)) if d is not None else np.zeros(len(xyz),bool)
    st = torch.load("%s/out/lmpnn_biounit1/stats/%s.pt"%(score.EXEC,pid), map_location="cpu")
    nat = st["native_sequence"].numpy(); gen = st["generated_sequences"].numpy()
    sel = near & (st["mask"].numpy()>0) & (st["chain_mask"].numpy()>0)
    r = (100.0*(gen[:,sel]==nat[None,sel]).mean(axis=1)).mean() if sel.sum() else float("nan")
    print(pid, "metal_atoms=%d near=%d rec=%.2f"%(keep.sum(), sel.sum(), r), "elems:", sorted(set(el[keep])))
PY
