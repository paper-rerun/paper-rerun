"""Blind recount of Fig. 4 (Base vs Fine-tuned CodonTransformer), per the frozen claims.json.

Reads only the published Source Data workbook. Metrics written from the paper's
equations and from kodonz/R/pminmax.r. No authors' R notebook was opened.
"""
import json
import sys
import statistics
import openpyxl

WB = sys.argv[1] if len(sys.argv) > 1 else None
OUT = sys.argv[2] if len(sys.argv) > 2 else None

FT = "Fine-tuned Codon-Transformer"
BASE = "Base Codon-Transformer"


def norm(s):
    """Collapse the Source Data's embedded line-break spacing in model labels."""
    return " ".join(str(s).split()).replace("Codon- Transformer", "Codon-Transformer")

ORGS = [
    "Escherichia coli",
    "Saccharomyces cerevisiae",
    "Arabidopsis thaliana",
    "Mus musculus",
    "Homo sapiens",
]


def codons(dna):
    s = str(dna).strip().upper()
    return [s[i:i + 3] for i in range(0, len(s) - len(s) % 3, 3)]


def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / len(sa | sb)


def similarity(a, b):
    assert len(a) == len(b), (len(a), len(b))
    return 100.0 * sum(1 for x, y in zip(a, b) if x == y) / len(a)


def dtw(x, y):
    """symmetric2 step pattern, |xi-yj| local cost. Returns (distance, N, M).

    symmetric2: a diagonal step costs 2*d(i,j), a horizontal or vertical step costs
    d(i,j), and the origin cell D[1][1] counts once, not twice. This is R dtw's
    default, and its normalizedDistance divides the result by N+M.
    """
    n, m = len(x), len(y)
    INF = float("inf")
    prev = [INF] * (m + 1)
    cur = [INF] * (m + 1)
    for i in range(1, n + 1):
        cur[0] = INF
        xi = x[i - 1]
        for j in range(1, m + 1):
            d = abs(xi - y[j - 1])
            if i == 1 and j == 1:
                cur[1] = d
            else:
                cur[j] = min(prev[j - 1] + 2.0 * d, prev[j] + d, cur[j - 1] + d)
        prev, cur = cur, prev
    return prev[m], n, m


def sheet_rows(wb, name):
    ws = wb[name]
    it = ws.iter_rows(values_only=True)
    hdr = [h for h in next(it)]
    ncol = len(hdr)
    for row in it:
        if row[0] is None:
            continue
        yield dict(zip(hdr, row[:ncol]))


def main():
    res = {}
    wb = openpyxl.load_workbook(WB, read_only=True, data_only=True)

    # ---- sequences, CSI, CIS ----
    seqs = list(sheet_rows(wb, "DNA sequences, CSI, CIS-element"))
    res["n_sequence_rows"] = len(seqs)
    res["organisms_found"] = sorted({r["organism"] for r in seqs})
    res["proteins_found"] = len({r["protein"] for r in seqs})

    # columns present (to confirm which tools are in the sheet)
    res["sequence_sheet_columns"] = list(seqs[0].keys())

    # ---- C1 / C2 : all tool pairs, so C6 ordering is testable ----
    tools = {}
    for col in seqs[0]:
        if isinstance(col, str) and col.endswith("_dna") or (isinstance(col, str) and col.endswith("_DNA")):
            tools[col] = col.rsplit("_", 1)[0]
    res["tool_columns"] = tools

    per_pair = {}
    length_mismatches = []
    for r in seqs:
        org = r["organism"]
        cod = {}
        for col, tool in tools.items():
            v = r.get(col)
            if v is None or not str(v).strip():
                continue
            cod[tool] = codons(v)
        names = sorted(cod)
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a, b = names[i], names[j]
                ca, cb = cod[a], cod[b]
                key = (a, b)
                if len(ca) != len(cb):
                    length_mismatches.append([org, r["protein"], a, b, len(ca), len(cb)])
                    sim = None
                else:
                    sim = similarity(ca, cb)
                per_pair.setdefault(key, []).append((org, jaccard(ca, cb), sim))
    res["length_mismatches"] = length_mismatches

    def summarise(vals):
        vals = [v for v in vals if v is not None]
        if not vals:
            return None
        return {
            "n": len(vals),
            "mean": statistics.fmean(vals),
            "sd": statistics.stdev(vals) if len(vals) > 1 else 0.0,
        }

    pairs_out = {}
    for (a, b), rows in sorted(per_pair.items()):
        # "across organisms": all 5 organisms pooled. ICOR exists only for E. coli,
        # so any pair involving it is flagged.
        orgs = sorted({o for o, _, _ in rows})
        pairs_out[f"{a} | {b}"] = {
            "organisms": orgs,
            "jaccard": summarise([j for _, j, _ in rows]),
            "sequence_similarity": summarise([s for _, _, s in rows]),
        }
    res["all_pairs"] = pairs_out

    ft_col = next(t for t in tools.values() if "finetune" in t.lower())
    base_col = next(t for t in tools.values() if "pretrain" in t.lower() or t.lower() == "base")
    k = " | ".join(sorted([ft_col, base_col]))
    res["C1_C2_base_vs_finetuned"] = {"pair_key": k, **pairs_out[k]}

    # ---- C4 : cis-element means ----
    cis_cols = [c for c in seqs[0] if isinstance(c, str) and c.endswith("_CIS")]
    c4 = {}
    for org in ORGS:
        rows = [r for r in seqs if r["organism"] == org]
        c4[org] = {
            col.rsplit("_", 1)[0]: {
                "n": len([r for r in rows if r.get(col) is not None]),
                "mean": statistics.fmean([float(r[col]) for r in rows if r.get(col) is not None]),
            }
            for col in cis_cols
            if any(r.get(col) is not None for r in rows)
        }
    res["C4_cis_means"] = c4

    # ---- C3 : DTW on the authors' published %MinMax profiles ----
    prof = {}
    for r in sheet_rows(wb, "%MinMax"):
        vals = [float(v) for v in str(r["minmax"]).split(",") if v.strip() != ""]
        prof[(r["organism"], str(r["protein (benchmark)"]).strip(), norm(r["model"]))] = vals
    res["n_minmax_profiles"] = len(prof)
    res["minmax_models"] = sorted({m for _, _, m in prof})

    models = sorted({m for _, _, m in prof})
    keys = sorted({(o, p) for o, p, _ in prof})
    dtw_pairs = {}
    for o, p in keys:
        have = [m for m in models if (o, p, m) in prof]
        for i in range(len(have)):
            for j in range(i + 1, len(have)):
                a, b = have[i], have[j]
                d, n, m_ = dtw(prof[(o, p, a)], prof[(o, p, b)])
                dtw_pairs.setdefault((a, b), []).append(
                    (o, d / (n + m_), d / n, d / max(n, m_))
                )
    dtw_out = {}
    for (a, b), rows in sorted(dtw_pairs.items()):
        dtw_out[f"{a} | {b}"] = {
            "organisms": sorted({o for o, *_ in rows}),
            "norm_n_plus_m": summarise([v for _, v, _, _ in rows]),
            "norm_n": summarise([v for _, _, v, _ in rows]),
            "norm_max": summarise([v for _, _, _, v in rows]),
        }
    res["C3_dtw_all_pairs"] = dtw_out
    kk = " | ".join(sorted([BASE, FT]))
    res["C3_base_vs_finetuned"] = dtw_out.get(kk, {"error": "pair key not found", "keys": sorted(dtw_out)})

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False, default=str)

    # ---- the pre-declared oddity in the published DTW sheet ----
    dsheet = list(sheet_rows(wb, "DTW"))
    self_rows = [r for r in dsheet if r["model1"] == r["model2"]]
    res["published_DTW_sheet_check"] = {
        "n_rows": len(dsheet),
        "n_self_comparison_rows": len(self_rows),
        "n_self_rows_with_zero_distance": len([r for r in self_rows if float(r["distance"]) == 0.0]),
        "n_groups_organism_protein": len({(r["organism"], r["protein"]) for r in dsheet}),
        "n_groups_with_a_single_distinct_distance": len(
            [
                1
                for g in {(r["organism"], r["protein"]) for r in dsheet}
                if len({round(float(r["distance"]), 9) for r in dsheet if (r["organism"], r["protein"]) == g}) == 1
            ]
        ),
        "model_labels_in_DTW_sheet": sorted({norm(r["model1"]) for r in dsheet}),
        "published_base_vs_ft_normalized": summarise(
            [
                float(r["normalized_distance"])
                for r in dsheet
                if {norm(r["model1"]), norm(r["model2"])} == {BASE, FT}
            ]
        ),
    }

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False, default=str)
    print("wrote", OUT)
    bf = res["C1_C2_base_vs_finetuned"]
    print("C1 jaccard mean  =", bf["jaccard"]["mean"], "n =", bf["jaccard"]["n"])
    print("C2 similarity    =", bf["sequence_similarity"]["mean"], "n =", bf["sequence_similarity"]["n"])
    print("C3 dtw(N+M) mean =", res["C3_base_vs_finetuned"]["norm_n_plus_m"])


if __name__ == "__main__":
    main()
