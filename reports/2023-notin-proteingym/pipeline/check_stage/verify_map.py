# Independent check of the claims map: counts, aggregates, and the Table A7 reclassification hypothesis
import csv
from collections import defaultdict, Counter
base = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources/repo_PG_v1.3/"
ref = list(csv.DictReader(open(base + "reference_files/DMS_substitutions.csv")))
print("ref assays", len(ref), "mutants", sum(int(r["DMS_total_number_mutants"]) for r in ref),
      "uniprot", len({r["UniProt_ID"] for r in ref}), "len>1022", sum(int(r["seq_len"]) > 1022 for r in ref))
print(Counter(r["coarse_selection_type"] for r in ref))
print("long targets", sorted((r["DMS_id"], r["seq_len"]) for r in ref if int(r["seq_len"]) > 1022))
dms = [r for r in csv.DictReader(open(base + "benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv")) if r["DMS ID"] not in ("", "Average")]
print("per-assay rows", len(dms), "ids match ref:", {r["DMS ID"] for r in dms} == {r["DMS_id"] for r in ref})
reftype = {r["DMS_id"]: r["coarse_selection_type"] for r in ref}
print("selection type mismatches CSV vs ref:", [r["DMS ID"] for r in dms if r["Selection Type"] != reftype[r["DMS ID"]]])
mean = lambda x: sum(x) / len(x)
def agg(model, rows, typeof, code=True):
    if code:
        pair = defaultdict(list)
        for r in rows:
            pair[(typeof(r), r["UniProt ID"])].append(float(r[model]))
        g = defaultdict(list)
        for (t, u), v in pair.items():
            g[t].append(mean(v))
    else:
        g = defaultdict(list)
        for r in rows:
            g[typeof(r)].append(float(r[model]))
    per = {k: round(mean(v), 3) for k, v in sorted(g.items())}
    return round(mean([mean(v) for v in g.values()]), 4), per
for m in ["ESM-1b", "ESM2 (8M)", "ESM2 (35M)", "ESM2 (150M)", "ESM2 (650M)", "TranceptEVE L", "GEMME"]:
    print(m, "code", agg(m, dms, lambda r: r["Selection Type"]), "literal", agg(m, dms, lambda r: r["Selection Type"], False))
# Table A7 paper: ESM-1b 0.428 0.289 0.427 0.351 0.500 (All 0.399); TranceptEVE L 0.487 0.381 0.456 0.460 0.500 (0.457); GEMME 0.482 0.387 0.443 0.452 0.519 (0.457)
expr = [r["DMS ID"] for r in dms if r["Selection Type"] == "Expression"]
for e in expr:
    t = lambda r, e=e: "Binding" if r["DMS ID"] == e else r["Selection Type"]
    a = agg("ESM-1b", dms, t)
    b = agg("TranceptEVE L", dms, t)
    print("move", e, "-> Binding: ESM-1b", a, "TEVE-L", b)
print("--- SPIKE_SARS2_Starr_2020_expression -> Binding (paper-era classification hypothesis)")
t = lambda r: "Binding" if r["DMS ID"] == "SPIKE_SARS2_Starr_2020_expression" else r["Selection Type"]
for m in ["ESM-1b", "ESM2 (8M)", "ESM2 (35M)", "ESM2 (150M)", "ESM2 (650M)", "ESM-1v (ensemble)", "TranceptEVE L", "GEMME"]:
    print(m, "code", agg(m, dms, t), "literal", agg(m, dms, t, False)[0])
