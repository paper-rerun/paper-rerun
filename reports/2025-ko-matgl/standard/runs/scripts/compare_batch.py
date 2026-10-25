"""Secondary: M3GNet batched (matgl 1.3.0 three-body indexing, batch composition dependent) vs per-conformation PESCalculator."""
import glob, os, sys
import numpy as np
rows = []
for path in sorted(glob.glob("runs/out_batch_m3gnet_4000/M3GNet__*.npz")):
    b = np.load(path)
    c = np.load(path.replace("out_batch_m3gnet_4000", "out_main"))
    assert (b["energy_ref_eV"] == c["energy_ref_eV"]).all()
    def emae(d): return np.mean(np.abs(d["energy_pred_eV"] - d["energy_ref_eV"]) / d["n_atoms"]) * 1000
    def fmae(d): return float(np.mean(np.abs(d["forces_pred_eV_per_A"].astype(np.float64) - d["forces_ref_eV_per_A"])))
    max_de = np.max(np.abs(b["energy_pred_eV"] - c["energy_pred_eV"]) / b["n_atoms"]) * 1000
    max_df = float(np.max(np.abs(b["forces_pred_eV_per_A"] - c["forces_pred_eV_per_A"])))
    rows.append(f"| {os.path.basename(path)[8:-4]} | {emae(c):.3f} | {emae(b):.3f} | {fmae(c):.4f} | {fmae(b):.4f} | {max_de:.3f} | {max_df:.3f} |")
print("| File | E calc | E batched | F calc | F batched | max abs dE/atom (meV) | max abs dF (eV/A) |\n|---|---|---|---|---|---|---|")
print("\n".join(rows))
