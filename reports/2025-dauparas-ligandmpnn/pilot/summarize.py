#!/usr/bin/env python3
"""Print the comparison tables for REPORT.md from the recovery_*.json files."""
import json
import os

ROOT = "/mnt/e/Ciencia/artigos/2025-dauparas-ligandmpnn"
PAPER = {  # Fig. 2a medians, in percent
    "small_molecule": {"rosetta": 50.4, "protein_mpnn": 50.4, "ligand_mpnn": 63.3},
    "nucleotide": {"rosetta": 35.2, "protein_mpnn": 34.0, "ligand_mpnn": 50.5},
    "metal": {"rosetta": 36.0, "protein_mpnn": 40.6, "ligand_mpnn": 77.5},
}
# Which reading of "near the ligand" fits each split's ligand class
FITTING = {"small_molecule": "largest", "nucleotide": "all", "metal": "metal"}
CONTEXT_LABEL = {
    "all": "every non-protein atom (paper's literal wording)",
    "metal": "metal atoms only",
    "largest": "largest single het residue",
}

res = {}
for c in ["all", "metal", "largest"]:
    p = os.path.join(ROOT, "logs", f"recovery_{c}.json")
    if os.path.exists(p):
        res[c] = json.load(open(p))

models = sorted({m for c in res for m in res[c]})
pct = lambda v: "-" if v is None else f"{100 * v:.1f}"


def cell(c, m, s, key="median_recovery"):
    try:
        return res[c][m][s][key]
    except KeyError:
        return None


print("## Table 1 - split-appropriate reading of the ligand\n")
print("| Split | n | Quantity | Paper | Ours | Diff |")
print("|---|---|---|---|---|---|")
for s in PAPER:
    c = FITTING[s]
    for m, label in (("ligand_mpnn", "LigandMPNN"), ("protein_mpnn_32", "ProteinMPNN")):
        v = cell(c, m, s)
        if v is None:
            continue
        pv = PAPER[s]["ligand_mpnn" if m == "ligand_mpnn" else "protein_mpnn"]
        n = res[c][m][s]["n_scored"]
        print(f"| {s} | {n} | {label} | {pv:.1f}% | {pct(v)}% | {100*v - pv:+.1f} |")

print("\n## Table 2 - full matrix, median recovery in percent\n")
print("| Reading of 'near the ligand' | Model | small_molecule | nucleotide | metal |")
print("|---|---|---|---|---|")
for c in ["all", "metal", "largest"]:
    if c not in res:
        continue
    for m in models:
        row = [pct(cell(c, m, s)) for s in PAPER]
        ns = [cell(c, m, s, "n_scored") for s in PAPER]
        cells = " | ".join(f"{r} (n={n})" for r, n in zip(row, ns))
        print(f"| {CONTEXT_LABEL[c]} | {m} | {cells} |")

print("\n## LigandMPNN advantage over ProteinMPNN, percentage points\n")
print("| Split | Paper | Ours |")
print("|---|---|---|")
for s in PAPER:
    c = FITTING[s]
    a, b = cell(c, "ligand_mpnn", s), cell(c, "protein_mpnn_32", s)
    if a is None or b is None:
        continue
    pg = PAPER[s]["ligand_mpnn"] - PAPER[s]["protein_mpnn"]
    print(f"| {s} | {pg:+.1f} | {100*(a-b):+.1f} |")

print("\n## Coverage\n")
for s in PAPER:
    c = FITTING[s]
    d = res[c]["ligand_mpnn"][s]
    print(
        f"- {s}: {d['n_structures_in_split']} ids in the split, "
        f"{d['n_scored']} scored, {d['n_missing_stats']} with no run output, "
        f"{d['n_no_near_residues']} with no residue meeting the cutoff, "
        f"median {d['median_n_near_residues']:.0f} near-ligand residues per structure"
    )
