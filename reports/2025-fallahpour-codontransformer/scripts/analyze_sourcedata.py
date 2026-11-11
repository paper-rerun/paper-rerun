"""L1 and L2 of the pre-registration: Fig. 4a/4b/4c from the published Source Data.

L1 averages the authors' own per-protein values.
L2 recomputes the three metrics with our code, from the published sequences
(Jaccard, sequence similarity) and from the published %MinMax profiles (DTW),
then compares per protein against the authors' values.

Writes runs/out/*.csv and prints everything it computes.
"""
import csv
import os
import re
import sys

import numpy as np
import openpyxl
from dtw import dtw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WB = os.path.join(
    ROOT, "data", "sourcedata", "unzipped", "Source Data",
    "Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx",
)
OUT = os.path.join(ROOT, "runs", "out")
# The workbook writes the figure labels, hyphen-split and with non-breaking spaces:
# "Base Codon- Transformer" and "Fine-tuned Codon- Transformer".
BASE = "Base Codon- Transformer"
FINE = "Fine-tuned Codon- Transformer"


def norm_model(s):
    """The workbook stores the figure labels with non-breaking spaces and line breaks."""
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def codons(dna):
    """Same split as the authors' str_extract_all('[:alpha:]{3}'): 3-letter chunks, drop a short tail."""
    dna = str(dna).strip().upper()
    return [dna[i:i + 3] for i in range(0, len(dna) - len(dna) % 3, 3)]


def jaccard(a, b):
    if len(a) != len(b):
        return None
    return len(set(a) & set(b)) / len(set(a) | set(b))


def seq_similarity(a, b):
    if len(a) != len(b):
        return None
    return 100.0 * sum(1 for x, y in zip(a, b) if x == y) / len(a)


def norm_dtw(p, q):
    return dtw(np.asarray(p, dtype=float), np.asarray(q, dtype=float)).normalizedDistance


def sheet_rows(wb, name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    head = [str(h) for h in next(it)]
    for row in it:
        if all(c is None for c in row):
            continue
        yield dict(zip(head, row))


def main():
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)

    # ---- the published sequences, one row per protein x organism
    seqs = {}
    for r in sheet_rows(wb, "DNA sequences, CSI, CIS-element"):
        if not r.get("protein"):
            continue
        seqs[(r["organism"], r["protein"])] = {
            "fine": r["finetune_transformer_dna"],
            "base": r["pretrain_transformer_dna"],
            "protein_seq": r["protein sequence"],
        }
    print(f"sequence rows: {len(seqs)}; organisms: {sorted({k[0] for k in seqs})}")

    # ---- the published %MinMax profiles
    profiles = {}
    for r in sheet_rows(wb, "%MinMax"):
        key = (r["organism"], r["protein (benchmark)"], norm_model(r["model"]))
        vals = [float(x) for x in str(r["minmax"]).split(",") if x not in ("", "NA")]
        profiles[key] = vals
    print(f"minmax profiles: {len(profiles)}; models: {sorted({k[2] for k in profiles})}")

    # ---- the authors' per-protein metric values, Base vs Fine-tuned only
    def pair_rows(sheet, col):
        got = {}
        for r in sheet_rows(wb, sheet):
            m1, m2 = norm_model(r["model1"]), norm_model(r["model2"])
            if {m1, m2} != {BASE, FINE}:
                continue
            key = (r["organism"], r["protein"])
            got.setdefault(key, []).append(float(r[col]))
        return got

    l1 = {}
    for name, (sheet, col) in {
        "C1_jaccard": ("Jaccard", "jaccard"),
        "C2_similarity": ("Sequence similarity", "seq_similarity"),
        "C3_dtw": ("DTW", "normalized_distance"),
    }.items():
        got = pair_rows(sheet, col)
        # complete() in the authors' pipeline writes both orderings of each pair
        per_pair = {k: v[0] for k, v in got.items()}
        spread = max(max(v) - min(v) for v in got.values())
        vals = np.array(list(per_pair.values()))
        l1[name] = {"n": len(vals), "mean": vals.mean(), "sd": vals.std(ddof=1),
                    "orderings": sorted({len(v) for v in got.values()}),
                    "max_spread_within_pair": spread, "per_pair": per_pair}
        print(f"L1 {name}: n={len(vals)} mean={vals.mean():.6f} sd={vals.std(ddof=1):.6f} "
              f"(rows per pair {l1[name]['orderings']}, max spread {spread:g})")

    # ---- A3: is the DTW diagonal zero?
    diag, offdiag_first = [], []
    for r in sheet_rows(wb, "DTW"):
        m1, m2 = norm_model(r["model1"]), norm_model(r["model2"])
        if m1 == m2:
            diag.append(float(r["normalized_distance"]))
        if (m1, m2) == (FINE, BASE):
            offdiag_first.append(float(r["normalized_distance"]))
    print(f"A3 DTW diagonal (model vs itself): n={len(diag)} min={min(diag):g} max={max(diag):g} "
          f"nonzero={sum(1 for d in diag if d != 0)}")

    # ---- L2: our code on the authors' sequences and profiles
    rows = []
    for (org, prot), s in sorted(seqs.items()):
        ca, cb = codons(s["base"]), codons(s["fine"])
        pb = profiles.get((org, prot, BASE))
        pf = profiles.get((org, prot, FINE))
        rows.append({
            "organism": org, "protein": prot,
            "n_codons_base": len(ca), "n_codons_fine": len(cb),
            "jaccard_ours": jaccard(ca, cb),
            "similarity_ours": seq_similarity(ca, cb),
            "dtw_ours": norm_dtw(pb, pf) if pb and pf else None,
            "jaccard_authors": l1["C1_jaccard"]["per_pair"].get((org, prot)),
            "similarity_authors": l1["C2_similarity"]["per_pair"].get((org, prot)),
            "dtw_authors": l1["C3_dtw"]["per_pair"].get((org, prot)),
            "len_profile_base": len(pb) if pb else 0,
            "len_profile_fine": len(pf) if pf else 0,
        })

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "l1_l2_per_protein.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    for ours, authors, label, tol in [
        ("jaccard_ours", "jaccard_authors", "C1 jaccard", 1e-6),
        ("similarity_ours", "similarity_authors", "C2 similarity", 1e-6),
        ("dtw_ours", "dtw_authors", "C3 normalized DTW", 1e-6),
    ]:
        pairs = [(r[ours], r[authors]) for r in rows if r[ours] is not None and r[authors] is not None]
        o = np.array([p[0] for p in pairs])
        a = np.array([p[1] for p in pairs])
        agree = int(np.sum(np.abs(o - a) <= tol))
        print(f"L2 {label}: n={len(o)} our mean={o.mean():.6f} sd={o.std(ddof=1):.6f} | "
              f"authors mean={a.mean():.6f} | agree<=1e-6: {agree}/{len(o)} "
              f"| max |diff|={np.abs(o - a).max():.3e}")
        bad = [(r["organism"], r["protein"], r[ours], r[authors])
               for r in rows if r[ours] is not None and r[authors] is not None
               and abs(r[ours] - r[authors]) > tol]
        for b in bad[:8]:
            print(f"    mismatch {b[0]} / {b[1]}: ours={b[2]!r} authors={b[3]!r}")
        if len(bad) > 8:
            print(f"    ... {len(bad)} mismatches in total")

    missing = [(r["organism"], r["protein"]) for r in rows if r["jaccard_ours"] is None]
    print(f"pairs where the two codon lists differ in length (metric undefined): {len(missing)}")
    for m in missing[:10]:
        print("   ", m)
    wb.close()


if __name__ == "__main__":
    sys.exit(main())
