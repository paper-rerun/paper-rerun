# Writes claims.json from the paper's Table 1 values (typed from paper/paper.txt and checked against Table S4/S7)
import json, math

TABLE1 = [
    # key, species, lineage, accession, size class, compleasm (C,S,D,F,M,N), BUSCO (C,S,D,F,M,N)
    ("scer", "S. cerevisiae", "saccharomycetes_odb10", "GCF_000146045.2_R64", "small",
     (99.2, 97.6, 1.6, 0.3, 0.5, 2137), (99.5, 97.3, 2.2, 0.1, 0.4, 2137)),
    ("cele", "C. elegans", "nematoda_odb10", "GCF_000002985.6_WBcel235", "small",
     (99.8, 99.7, 0.1, 0.2, 0.0, 3131), (98.8, 98.3, 0.5, 0.6, 0.6, 3131)),
    ("atha", "A. thaliana", "brassicales_odb10", "GCF_000001735.4_TAIR10.1", "small",
     (99.9, 98.9, 1.0, 0.1, 0.0, 4596), (99.2, 97.9, 1.3, 0.1, 0.7, 4596)),
    ("dmel", "D. melanogaster", "diptera_odb10", "GCF_000001215.4_Release_6_plus_ISO1_MT", "small",
     (99.7, 99.4, 0.3, 0.2, 0.1, 3285), (98.6, 98.4, 0.2, 0.5, 0.9, 3285)),
    ("mmus", "M. musculus", "glires_odb10", "GCF_000001635.27_GRCm39", "large",
     (99.7, 97.8, 1.9, 0.3, 0.0, 13798), (96.5, 93.6, 2.9, 0.6, 2.9, 13798)),
    ("hsap", "H. sapiens (T2T-CHM13)", "primates_odb10", "GCF_009914755.1_T2T-CHM13v2.0", "large",
     (99.6, 98.9, 0.7, 0.3, 0.1, 13780), (95.7, 94.1, 1.6, 1.1, 3.2, 13780)),
    ("zmay", "Z. mays", "liliopsida_odb10", "GCF_902167145.1_Zm-B73-REFERENCE-NAM-5.0", "large",
     (96.7, 82.2, 14.5, 3.0, 0.3, 3236), (93.8, 79.2, 14.6, 5.3, 0.9, 3236)),
]
NAMES = {"C": "Completed", "S": "Single-copy", "D": "Duplicated", "F": "Fragmented", "M": "Missing"}
DEFS = {"C": "D-METRIC-C", "S": "D-METRIC-S", "D": "D-METRIC-D", "F": "D-METRIC-F", "M": "D-METRIC-M"}


def implied_counts(value, n):
    # Integer gene counts k whose k/n*100 rounds to the paper's one-decimal value
    low = math.ceil((value - 0.05) * n / 100 - 1e-9)
    high = math.floor((value + 0.05) * n / 100 + 1e-9)
    return [max(low, 0), min(high, n)]


def make_claims():
    claims = []
    for key, species, lineage, acc, size, cvals, bvals in TABLE1:
        for tool, vals in (("compleasm", cvals), ("busco", bvals)):
            if tool == "busco" and size != "small":
                continue
            role = "primary" if tool == "compleasm" else "optional"
            if tool == "compleasm" and key == "hsap":
                role = "primary (headline: abstract '99.6% than BUSCO's 95.7%')"
            n = vals[5]
            tol = "|ours - paper| <= 0.3 percentage points" if tool == "compleasm" else "|ours - paper| <= 0.5 percentage points"
            tol_def = "D-TOL-COMPLEASM" if tool == "compleasm" else "D-TOL-BUSCO"
            for i, m in enumerate("CSDFM"):
                claims.append({
                    "id": "t1.{}.{}.{}".format(key, tool, m),
                    "role": role,
                    "quantity": "{} (%) reported by {} for {} with {}".format(NAMES[m], "compleasm" if tool == "compleasm" else "BUSCO", species, lineage),
                    "paper_value": vals[i],
                    "unit": "percent of N BUSCO genes (one decimal in the paper)",
                    "location": "Table 1, row '{}' / {} / {}".format(species.split(" (")[0], lineage, "compleasm" if tool == "compleasm" else "BUSCO") + (", also abstract and Table S4" if key == "hsap" and m == "C" else "") + ("; also Table S4" if key == "hsap" and m != "C" else "") + ("; same value in Table S7 '<species>-reference' row" if tool == "compleasm" and key in ("atha", "cele", "dmel") else ""),
                    "implied_count_range": implied_counts(vals[i], n),
                    "tolerance": tol,
                    "tolerance_basis": "See " + tol_def + ". Exact tier: ours rounded to one decimal equals the paper value.",
                    "conditions": {
                        "genome": acc + "_genomic.fna.gz, NCBI RefSeq, used as downloaded (D-GENOME, D-ORDER)",
                        "lineage": lineage + " 2024-01-08 re-release (D-LINEAGE)",
                        "tool": "compleasm v0.2.2 release kit, mode busco, default thresholds (D-CODE, D-MODE, D-OUTS, D-THRESH)" if tool == "compleasm" else "BUSCO 5.4.7, -m genome, MetaEuk (D-BUSCO)",
                        "metric": DEFS[m] + ", D-ROUND",
                        "threads": "-t 8 under nice -n 19 (D-THREADS)",
                        "seed": "not applicable (deterministic for a fixed input, D-REPEAT)",
                    },
                })
            claims.append({
                "id": "t1.{}.{}.N".format(key, tool),
                "role": role.split(" (")[0],
                "quantity": "N, number of BUSCO genes in {} as counted by {}".format(lineage, "compleasm" if tool == "compleasm" else "BUSCO"),
                "paper_value": n,
                "unit": "genes",
                "location": "Table 1, column N, {} row".format(species.split(" (")[0]),
                "tolerance": "exact",
                "tolerance_basis": "Integer count of gene groups in the lineage (D-N). A different N means the re-released lineage has a different gene set; that is recorded as a lineage difference and the percentages are still graded.",
                "conditions": {"lineage": lineage + " 2024-01-08 re-release (D-LINEAGE)", "metric": "D-N"},
            })
    return claims


def main():
    with open("scripts/claims_body.json", "r", encoding="utf-8") as fin:
        doc = json.load(fin)
    doc["claims"] = make_claims()
    with open("claims.json", "w", encoding="utf-8", newline="\n") as fout:
        json.dump(doc, fout, indent=1, ensure_ascii=False)
        fout.write("\n")
    print(len(doc["claims"]), "claims")


if __name__ == "__main__":
    # Self-check of the count range on a value we can do by hand: 97.6% of 2137 -> 2085.7, range 2085-2086
    assert implied_counts(97.6, 2137) == [2085, 2086]
    assert implied_counts(0.0, 4596) == [0, 2]
    main()
