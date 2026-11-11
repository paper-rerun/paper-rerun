"""C3b sensitivity: %MinMax written from scratch (Clarke & Clark 2008, as kodonz
implements it), window 18 codons, kodonz's built-in GenScript host tables, then my
own DTW. Cannot change the verdict; see claims.json.
"""
import json
import statistics
import sys

import rdata

import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recount import dtw, codons, sheet_rows  # noqa: E402  (own module, same dir)

import openpyxl  # noqa: E402

WB = sys.argv[1] if len(sys.argv) > 1 else None
TABLE_DIR = sys.argv[2] if len(sys.argv) > 2 else None
OUT = sys.argv[3] if len(sys.argv) > 3 else None

# kodonz spp name -> organism label in the Source Data. kodonz ships both 'yeast'
# and 'saccharomyces'; the Methods name neither, so both are reported.
HOSTS = {
    "Escherichia coli": ["ecoli"],
    "Saccharomyces cerevisiae": ["saccharomyces", "yeast"],
    "Arabidopsis thaliana": ["arabidopsis"],
    "Mus musculus": ["mouse"],
    "Homo sapiens": ["human"],
}

BASES = "TCAG"
AA = (
    "FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG"
)
CODON_AA = {}
i = 0
for a in BASES:
    for b in BASES:
        for c in BASES:
            CODON_AA[a + b + c] = AA[i]
            i += 1


def load_cft(path):
    """kodonz stores cft_<host> as a data frame; column 5 is the frequency, column 1 the codon."""
    d = rdata.read_rda(path)
    obj = list(d.values())[0]
    cols = list(obj.keys()) if hasattr(obj, "keys") else None
    if cols is None:
        raise SystemExit(f"unexpected rda structure in {path}")
    codon_col = [str(x).strip().upper().replace("U", "T") for x in obj[cols[0]]]
    freq_col = [float(x) for x in obj[cols[4]]]
    return dict(zip(codon_col, freq_col))


def pminmax(cods, cft, w=18):
    """Clarke & Clark %MinMax, exactly the arithmetic of kodonz/R/pminmax.r.

    Per amino acid family: xavg = mean of family frequencies, xmax = max, xmin = min.
    Per window: num = sum(f - xavg); den = sum(xmax - xavg) if num > 0 else sum(xavg - xmin).
    Returns num/den per window (a signed fraction), as kodonz does.
    """
    fam = {}
    for cod, aa in CODON_AA.items():
        fam.setdefault(aa, []).append(cod)
    xavg, xmax, xmin = {}, {}, {}
    for aa, members in fam.items():
        vals = [cft[c] for c in members if c in cft]
        if not vals:
            continue
        for c in members:
            xavg[c], xmax[c], xmin[c] = statistics.fmean(vals), max(vals), min(vals)
    out = []
    n = len(cods)
    if n < w:
        return out
    for i in range(n - w + 1):
        win = cods[i:i + w]
        if any(c not in cft for c in win):
            out.append(float("nan"))
            continue
        num = sum(cft[c] - xavg[c] for c in win)
        den = sum(xmax[c] - xavg[c] for c in win) if num > 0 else sum(xavg[c] - xmin[c] for c in win)
        out.append(num / den if den != 0 else 0.0)
    return out


def main():
    tables = {}
    for names in HOSTS.values():
        for nm in names:
            tables[nm] = load_cft(f"{TABLE_DIR}/cft_{nm}.rda")

    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)
    seqs = list(sheet_rows(wb, "DNA sequences, CSI, CIS-element"))

    res = {"table_sizes": {k: len(v) for k, v in tables.items()}, "variants": {}}
    for org, hostnames in HOSTS.items():
        for host in hostnames:
            vals = []
            for r in seqs:
                if r["organism"] != org:
                    continue
                pb = pminmax(codons(r["pretrain_transformer_dna"]), tables[host])
                pf = pminmax(codons(r["finetune_transformer_dna"]), tables[host])
                if not pb or not pf:
                    continue
                d, n, m = dtw(pb, pf)
                vals.append(d / (n + m))
            res["variants"].setdefault(host, {})[org] = {
                "n": len(vals),
                "mean": statistics.fmean(vals) if vals else None,
                "sd": statistics.stdev(vals) if len(vals) > 1 else None,
                "values": vals,
            }

    # pooled across the 5 organisms, one host table choice per organism
    for ychoice in ("saccharomyces", "yeast"):
        pooled = []
        for org, hostnames in HOSTS.items():
            host = ychoice if org == "Saccharomyces cerevisiae" else hostnames[0]
            pooled += res["variants"][host][org]["values"]
        res[f"C3b_pooled_yeast_table_{ychoice}"] = {
            "n": len(pooled),
            "mean": statistics.fmean(pooled),
            "sd": statistics.stdev(pooled),
        }

    for k, v in res.items():
        if k.startswith("C3b_pooled"):
            print(k, v)
    for host in res["variants"]:
        for org in res["variants"][host]:
            res["variants"][host][org].pop("values")
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
