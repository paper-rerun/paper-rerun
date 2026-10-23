"""Score C1 and C2: median per-protein native sequence recovery near the ligand.

Per sequence : 100 * matches / n_near
Per protein  : mean over the 10 designed sequences
Headline     : median over the 317 proteins

Two neighbourhoods are scored from the same designs:
  "near"           the fixed definition (side-chain atoms within 5.0 A) -> main result
  "near_any_atom"  any heavy atom of the residue within 5.0 A -> extra analysis
"""

import csv
import json
import os

import numpy as np
import torch

BASE = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/exec/B1-small-molecule-split"
SD = "/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/sd/x/s2"
ALPHABET = "ACDEFGHIKLMNPQRSTVWYX"

mask_data = json.load(open(os.path.join(BASE, "near_mask.json")))
order = [n[:-4] for n in json.load(
    open("/mnt/e/Ciencia/pipeline/2025-dauparas-ligandmpnn/sources/fig2b_names.json")
)["small_molecule"]]

RUNS = [("C1-LMPNN-SMALLMOL", "out_lmpnn"), ("C2-PMPNN-SMALLMOL", "out_pmpnn")]


def load(stats_dir):
    seqs, problems = {}, []
    for stem in order:
        p = os.path.join(stats_dir, stem + ".pt")
        if not os.path.exists(p):
            problems.append(stem + ": no stats file")
            continue
        d = torch.load(p, map_location="cpu")
        nat = d["native_sequence"].numpy()
        if "".join(ALPHABET[i] for i in nat) != mask_data[stem]["native"]:
            problems.append(stem + ": native sequence does not match the mask parse")
            continue
        if d["generated_sequences"].shape[0] != 10:
            problems.append("%s: %d sequences, expected 10" % (stem, d["generated_sequences"].shape[0]))
        seqs[stem] = (d["generated_sequences"].numpy(), nat, int(d["seed"]),
                      float(d["temperature"]))
    return seqs, problems


def recoveries(seqs, mask_key):
    per = {}
    for stem, (gen, nat, seed, temp) in seqs.items():
        m = np.array([c == "1" for c in mask_data[stem][mask_key]])
        if m.sum() == 0:
            continue
        rec = 100.0 * (gen[:, m] == nat[m]).sum(1) / m.sum()
        per[stem] = {"n_near": int(m.sum()), "n_seq": int(gen.shape[0]),
                     "per_sequence": [float(x) for x in rec],
                     "mean": float(rec.mean()), "seed": seed, "temperature": temp}
    return per


results = {}
for claim, sub in RUNS:
    seqs, problems = load(os.path.join(BASE, sub, "stats"))
    entry = {"problems": problems, "n_structures_scored": len(seqs)}
    if not seqs:
        print(claim, "no stats yet, skipped")
        continue
    for key, label in [("near", "sidechain_within_5A"),
                       ("near_any_atom", "any_heavy_atom_within_5A")]:
        per = recoveries(seqs, key)
        vals = np.array([per[s]["mean"] for s in order if s in per])
        entry[label] = {"n": int(len(vals)), "median": float(np.median(vals)),
                        "mean": float(vals.mean()), "per_protein": per}
        print("%s %-26s n=%d median=%.4f mean=%.4f"
              % (claim, label, len(vals), np.median(vals), vals.mean()))
    if problems:
        print("   problems:", len(problems), problems[:3])
    results[claim] = entry

json.dump(results, open(os.path.join(BASE, "results.json"), "w"), indent=1)

# Side by side with the authors' Source Data, protein by protein
z = np.load(os.path.join(SD, "fig_2_1_2.npz"), allow_pickle=True)
names = [str(n)[:-4] for n in z["names"]]
rows = list(csv.DictReader(open(os.path.join(SD, "fig_2_1_1.csv"))))
theirs = {"C1-LMPNN-SMALLMOL": np.array(z["p1y"], dtype=float),
          "C2-PMPNN-SMALLMOL": np.array([float(r["probs"]) for r in rows
                                         if r["types"] == "ProteinMPNN"])}
comp = {}
for claim, t in theirs.items():
    if claim not in results:
        continue
    comp[claim] = {"their_median": float(np.median(t))}
    for label in ["sidechain_within_5A", "any_heavy_atom_within_5A"]:
        per = results[claim][label]["per_protein"]
        ok = [i for i, n in enumerate(names) if n in per]
        ours = np.array([per[names[i]]["mean"] for i in ok])
        tt = t[ok]
        d = ours - tt
        comp[claim][label] = {
            "n": len(ok), "our_median": float(np.median(ours)),
            "mean_diff_pp": float(d.mean()),
            "median_abs_diff_pp": float(np.median(np.abs(d))),
            "corr": float(np.corrcoef(ours, tt)[0, 1]),
        }
        print("%s %-26s vs source data: n=%d mean diff %+.2f pp, median |diff| %.2f pp, corr %.3f"
              % (claim, label, len(ok), d.mean(), np.median(np.abs(d)), comp[claim][label]["corr"]))
json.dump(comp, open(os.path.join(BASE, "vs_source_data.json"), "w"), indent=1)
