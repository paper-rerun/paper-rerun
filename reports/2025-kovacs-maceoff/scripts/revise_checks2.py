"""Are the 126 configs of issue #7 among the 209 the component cut removes? Uses the CSV plus the xyz norm."""
import csv, os, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows = list(csv.DictReader(open(os.path.join(ROOT, "runs", "out", "errors_small.csv"))))
ct = np.array([r["config_type"] for r in rows]); comp = np.array([float(r["ref_max_abs_f_eV_A"]) for r in rows])
sumf = np.array([float(r["ref_sum_f_norm_eV_A"]) for r in rows])
mx = []
with open(os.path.join(ROOT, "data", "test_extract", "test_large_neut_all.xyz")) as fh:
    while True:
        l = fh.readline()
        if not l: break
        n = int(l); fh.readline()
        f = np.array([[float(x) for x in fh.readline().split()[4:7]] for _ in range(n)])
        mx.append(np.linalg.norm(f, axis=1).max())
mx = np.array(mx); pc = ct == "PubChem"
bad = pc & ((mx > 15) | (sumf > 0.1)); drop = pc & (comp > 10)
print("PubChem failing norm>15 or |sumF|>0.1:", int(bad.sum()))
print("of those, also removed by component>10:", int((bad & drop).sum()))
print("removed by component>10 but passing the v2 filters:", int((drop & ~bad).sum()))
