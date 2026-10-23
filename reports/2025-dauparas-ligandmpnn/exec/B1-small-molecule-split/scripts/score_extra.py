"""Score the extra ProteinMPNN run (proteinmpnn_v_48_020.pt, 0.2 A noise)."""
import json
import os

import numpy as np
import torch

BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"
ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"
mask_data = json.load(open(os.path.join(BASE, "near_mask.json")))
order = [n[:-4] for n in json.load(
    open("/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/fig2b_names.json")
)["small_molecule"]]

out = {}
for label, key in [("sidechain_within_5A", "near"),
                   ("any_heavy_atom_within_5A", "near_any_atom")]:
    means, seed = [], None
    for stem in order:
        p = os.path.join(BASE, "out_pmpnn020", "stats", stem + ".pt")
        d = torch.load(p, map_location="cpu")
        gen = d["generated_sequences"].numpy()
        nat = d["native_sequence"].numpy()
        seed = int(d["seed"])
        assert "".join(ALPHABET[i] for i in nat) == mask_data[stem]["native"], stem
        m = np.array([c == "1" for c in mask_data[stem][key]])
        means.append((100.0 * (gen[:, m] == nat[m]).sum(1) / m.sum()).mean())
    v = np.array(means)
    out[label] = {"n": len(v), "median": float(np.median(v)), "mean": float(v.mean()),
                  "seed": seed}
    print("extra pmpnn_v_48_020 %-26s n=%d median=%.4f mean=%.4f"
          % (label, len(v), np.median(v), v.mean()))
json.dump(out, open(os.path.join(BASE, "results_extra_pmpnn020.json"), "w"), indent=1)
