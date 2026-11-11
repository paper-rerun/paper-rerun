"""Direct comparison: my from-scratch %MinMax vs the profiles published in the Source Data."""
import os, statistics, sys, openpyxl
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount import codons, sheet_rows, norm, BASE, FT
from minmax_own import load_cft, pminmax, HOSTS

wb = openpyxl.load_workbook(sys.argv[1], read_only=True, data_only=True)
pub = {}
for r in sheet_rows(wb, "%MinMax"):
    pub[(r["organism"], str(r["protein (benchmark)"]).strip(), norm(r["model"]))] = [
        float(v) for v in str(r["minmax"]).split(",") if v.strip()
    ]
seqs = list(sheet_rows(wb, "DNA sequences, CSI, CIS-element"))
tab = {h: load_cft(f"{sys.argv[2]}/cft_{h}.rda") for hs in HOSTS.values() for h in hs}

worst, diffs, nlen, n = 0.0, [], 0, 0
for r in seqs:
    org = r["organism"]
    if org not in HOSTS:
        continue
    host = HOSTS[org][0]
    for col, label in (("pretrain_transformer_dna", BASE), ("finetune_transformer_dna", FT)):
        key = (org, str(r["protein"]).strip(), label)
        if key not in pub:
            continue
        mine = pminmax(codons(r[col]), tab[host])
        theirs = pub[key]
        n += 1
        if len(mine) != len(theirs):
            nlen += 1
            continue
        dd = [abs(a - b) for a, b in zip(mine, theirs)]
        diffs += dd
        worst = max(worst, max(dd))
print(f"profiles compared: {n}, length mismatches: {nlen}")
print(f"windows compared: {len(diffs)}  mean |diff|: {statistics.fmean(diffs):.5f}  max |diff|: {worst:.5f}")
print("note: the published profiles are stored rounded to 2 decimals, so ~0.005 is the floor")
