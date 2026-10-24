# Recompute the corrected average from the authors' per-assay Spearman table (PG_v1.3)
# under two definitions, and bootstrap the statistic's own standard error. Stdlib only.
import csv, random, statistics, sys, json
from collections import defaultdict

base = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources/repo_PG_v1.3/"
dms_path = base + "benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv"
summary_path = base + "benchmarks/DMS_zero_shot/substitutions/Spearman/Summary_performance_DMS_substitutions_Spearman.csv"
models = ["ESM-1b", "ESM2 (8M)", "ESM2 (35M)", "ESM2 (150M)", "ESM2 (650M)"]
paper = {"ESM-1b": 0.394, "ESM2 (8M)": 0.226, "ESM2 (35M)": 0.321, "ESM2 (150M)": 0.387, "ESM2 (650M)": 0.414}
paper_se_vs_best = {"ESM-1b": 0.010, "ESM2 (8M)": 0.015, "ESM2 (35M)": 0.015, "ESM2 (150M)": 0.013, "ESM2 (650M)": 0.012}

rows = [r for r in csv.DictReader(open(dms_path)) if r["DMS ID"] not in ("", "Average")]
print("assays in per-assay table:", len(rows))
fcount = defaultdict(int)
for r in rows:
    fcount[r["Selection Type"]] += 1
print("assays per function type:", dict(fcount), "unique UniProt:", len({r["UniProt ID"] for r in rows}))

def mean(x):
    return sum(x) / len(x)

# Units per function type: list of per-unit values
def units_assay(model):
    groups = defaultdict(list)
    for r in rows:
        groups[r["Selection Type"]].append(float(r[model]))
    return groups

def units_uniprot(model):
    by_pair = defaultdict(list)
    for r in rows:
        by_pair[(r["Selection Type"], r["UniProt ID"])].append(float(r[model]))
    groups = defaultdict(list)
    for (ftype, uniprot), values in by_pair.items():
        groups[ftype].append(mean(values))
    return groups

def corrected(groups):
    return mean([mean(v) for v in groups.values()])

# Stratified bootstrap: resample units with replacement inside each function type
def boot_se(groups, n=10000, seed=0):
    rng = random.Random(seed)
    keys = sorted(groups)
    stats = []
    for _ in range(n):
        stats.append(mean([mean(rng.choices(groups[k], k=len(groups[k]))) for k in keys]))
    return statistics.stdev(stats)

summary = {}
for r in csv.DictReader(open(summary_path)):
    summary[r["Model_name"]] = r
out = {}
print(f"{'model':12s} paper  codeDef  literal  plain  summaryCSV  SEboot_code  SEboot_literal  SE_rounding")
for m in models:
    gu, ga = units_uniprot(m), units_assay(m)
    plain = mean([float(r[m]) for r in rows])
    s = summary.get(m, {})
    # Rounding of per-assay values to 3 decimals: uniform error +-0.0005 per assay; worst case bound on corrected average is 0.0005
    res = dict(paper=paper[m], code_definition=round(corrected(gu), 4), literal_definition=round(corrected(ga), 4),
               plain_assay_mean=round(plain, 4), summary_csv=s.get("Average_Spearman"), summary_csv_se_vs_best=s.get("Bootstrap_standard_error_Spearman"),
               boot_se_code=round(boot_se(gu), 4), boot_se_literal=round(boot_se(ga), 4),
               per_function_code={k: round(mean(v), 4) for k, v in sorted(gu.items())},
               per_function_literal={k: round(mean(v), 4) for k, v in sorted(ga.items())},
               n_units_code={k: len(v) for k, v in sorted(gu.items())})
    out[m] = res
    print(f"{m:12s} {paper[m]:.3f}  {res['code_definition']:.4f}   {res['literal_definition']:.4f}   {plain:.4f}  {res['summary_csv']}  {res['boot_se_code']:.4f}  {res['boot_se_literal']:.4f}")
json.dump(out, open("/mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources/aggregate_check_out.json", "w"), indent=1)
