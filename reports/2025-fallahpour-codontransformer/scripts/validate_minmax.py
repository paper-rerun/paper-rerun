"""Prerequisite for C3 at L3: can we reproduce the authors' %MinMax profiles?

The authors computed %MinMax in R with kodonz::pminmax(z=18, y=0, spp=species). The
release does not say which codon-frequency table that used, so we try two candidates
on the authors' own published Fig. 4 sequences and compare against their published
profiles, using the repo's own get_min_max_percentage:

  P (pre-registered): frequencies counted from the natural_dna of the Fig. 3 Source Data,
      per organism.
  K (extra): the Kazusa table that the repo itself ships a loader for, via python_codon_tables.

Accept a table only if the mean absolute difference is <= 0.02 on the 0-1 scale.
"""
import os
import re
import sys

import numpy as np
import openpyxl
import python_codon_tables as pct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "data", "repo"))
from CodonTransformer.CodonEvaluation import get_min_max_percentage  # noqa: E402

SD = os.path.join(ROOT, "data", "sourcedata", "unzipped", "Source Data")
WB4 = os.path.join(SD, "Fig. 4, Supplementary Fig. 19f-h, 20, 21, 22 and 25.xlsx")
WB3 = os.path.join(SD, "Fig. 3, Supplementary Fig. 18, 19a-e, 23, 24.xlsx")
BASE = "Base Codon- Transformer"
FINE = "Fine-tuned Codon- Transformer"

KAZUSA = {
    "Escherichia coli": "e_coli_316407",
    "Saccharomyces cerevisiae": "s_cerevisiae_4932",
    # python_codon_tables ships no A. thaliana table, so this one is fetched by taxid
    "Arabidopsis thaliana": 3702,
    "Mus musculus": "m_musculus_10090",
    "Homo sapiens": "h_sapiens_9606",
}


def norm(s):
    return re.sub(r"\s+", " ", str(s).replace("\xa0", " ")).strip()


def rows(path, sheet):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb[sheet]
    it = ws.iter_rows(values_only=True)
    head = [str(h) for h in next(it)]
    for r in it:
        if not all(c is None for c in r):
            yield dict(zip(head, r))
    wb.close()


def codon_freqs_from_sequences(dnas):
    """Relative frequency of each codon among the synonyms of its amino acid."""
    from Bio.Seq import Seq
    counts = {}
    for dna in dnas:
        dna = str(dna).strip().upper()
        for i in range(0, len(dna) - len(dna) % 3, 3):
            c = dna[i:i + 3]
            if set(c) <= set("ACGT"):
                counts[c] = counts.get(c, 0) + 1
    by_aa = {}
    for c in ["".join(x) for x in __import__("itertools").product("ACGT", repeat=3)]:
        aa = str(Seq(c).translate())
        by_aa.setdefault(aa, []).append(c)
    table = {}
    for aa, cods in by_aa.items():
        tot = sum(counts.get(c, 0) for c in cods)
        table[aa] = (cods, [counts.get(c, 0) / tot if tot else 0.0 for c in cods])
    return table


def kazusa_table(organism):
    t = pct.get_codons_table(KAZUSA[organism])
    return {aa: (list(d.keys()), list(d.values())) for aa, d in t.items()}


def profile(dna, table):
    vals = get_min_max_percentage(str(dna).strip().upper(), table, window_size=18)
    return np.array([v for v in vals if v is not None], dtype=float) / 100.0


def main():
    published = {}
    for r in rows(WB4, "%MinMax"):
        published[(r["organism"], r["protein (benchmark)"], norm(r["model"]))] = np.array(
            [float(x) for x in str(r["minmax"]).split(",") if x not in ("", "NA")]
        )
    seqs = {}
    for r in rows(WB4, "DNA sequences, CSI, CIS-element"):
        if r.get("protein"):
            seqs[(r["organism"], r["protein"])] = {
                BASE: r["pretrain_transformer_dna"], FINE: r["finetune_transformer_dna"]}

    # table P: natural genes of the Fig. 3 Source Data, per organism
    nat = {}
    for r in rows(WB3, "DNA sequences"):
        if not r.get("natural_dna"):
            continue
        org = str(r["organism"])
        key = next((k for k in KAZUSA if k.split()[1][:4] in org), org)
        nat.setdefault(key, []).append(r["natural_dna"])
    print("natural genes per organism:", {k: len(v) for k, v in sorted(nat.items())})

    tables = {}
    for org in KAZUSA:
        tables[("P", org)] = codon_freqs_from_sequences(nat.get(org, []))
        tables[("K", org)] = kazusa_table(org)

    for which in ("P", "K"):
        diffs, worst = [], (0.0, None)
        for (org, prot), models in sorted(seqs.items()):
            for mdl in (BASE, FINE):
                pub = published.get((org, prot, mdl))
                if pub is None:
                    continue
                try:
                    ours = profile(models[mdl], tables[(which, org)])
                except Exception as exc:
                    print(f"  {which} {org}/{prot}/{mdl}: {type(exc).__name__}: {exc}")
                    continue
                n = min(len(ours), len(pub))
                d = float(np.mean(np.abs(ours[:n] - pub[:n])))
                diffs.append(d)
                if d > worst[0]:
                    worst = (d, (org, prot, mdl, len(ours), len(pub)))
        a = np.array(diffs)
        print(f"table {which}: n={len(a)} mean|diff|={a.mean():.4f} median={np.median(a):.4f} "
              f"p95={np.percentile(a, 95):.4f} max={a.max():.4f}")
        print(f"   worst: {worst[1]} at {worst[0]:.4f}")
        print(f"   verdict at the pre-registered 0.02 ceiling: "
              f"{'ACCEPT' if a.mean() <= 0.02 else 'REJECT'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
