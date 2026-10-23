#!/usr/bin/env bash
set -euo pipefail
ROOT=/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn
source "$ROOT/env/activate.sh"
python - <<'PY'
import sys, json, numpy as np, torch
sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B3-metal-split")
import score
score.self_check()
ROOT = score.ROOT; EXEC = score.EXEC
import os
done = sorted(f[:-3] for f in os.listdir(EXEC + "/out/lmpnn_biounit1/stats"))[:3]
for pid in done:
    near, native, nctx = score.near_ligand_mask("%s/data/structures/biounit1/%s.pdb" % (ROOT, pid))
    st = torch.load("%s/out/lmpnn_biounit1/stats/%s.pt" % (EXEC, pid), map_location="cpu")
    assert np.array_equal(st["native_sequence"].numpy(), native), pid
    gen = st["generated_sequences"].numpy()
    des = (st["mask"].numpy() > 0) & (st["chain_mask"].numpy() > 0)
    sel = near & des
    rec = 100.0 * (gen[:, sel] == native[None, sel]).mean(axis=1)
    print(pid, "L=%d ctx=%d near=%d nseq=%d rec=%.2f" % (len(native), nctx, sel.sum(), gen.shape[0], rec.mean()))
PY
