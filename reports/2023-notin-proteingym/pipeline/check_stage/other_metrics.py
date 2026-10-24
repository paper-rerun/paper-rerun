# ESM-1b Table 2 metrics (AUC, MCC, NDCG, Top recall) from the authors' per-assay tables at PG_v1.3
import csv, random, statistics
from collections import defaultdict
base = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources/repo_PG_v1.3/benchmarks/DMS_zero_shot/substitutions/"
mean = lambda x: sum(x) / len(x)
paper = {"AUC": 0.719, "MCC": 0.311, "NDCG": 0.747, "Top_recall": 0.203, "Spearman": 0.394}
def groups(rows, model, code):
    if code:
        pair = defaultdict(list)
        for r in rows:
            pair[(r["Selection Type"], r["UniProt ID"])].append(float(r[model]))
        g = defaultdict(list)
        for (t, u), v in pair.items():
            g[t].append(mean(v))
        return g
    g = defaultdict(list)
    for r in rows:
        g[r["Selection Type"]].append(float(r[model]))
    return g
def boot(g, n=10000, seed=0):
    rng = random.Random(seed)
    keys = sorted(g)
    return statistics.stdev([mean([mean(rng.choices(g[k], k=len(g[k]))) for k in keys]) for _ in range(n)])
for m in paper:
    rows = [r for r in csv.DictReader(open(f"{base}{m}/DMS_substitutions_{m}_DMS_level.csv")) if r["DMS ID"] not in ("", "Average")]
    summ = {r["Model_name"]: r for r in csv.DictReader(open(f"{base}{m}/Summary_performance_DMS_substitutions_{m}.csv"))}
    gc, gl = groups(rows, "ESM-1b", True), groups(rows, "ESM-1b", False)
    print(m, "n", len(rows), "paper", paper[m], "code", round(mean([mean(v) for v in gc.values()]), 4),
          "literal", round(mean([mean(v) for v in gl.values()]), 4), "summaryCSV", summ["ESM-1b"]["Average_" + m],
          "SEcode", round(boot(gc), 4), "SElit", round(boot(gl), 4))
