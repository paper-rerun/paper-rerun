"""Check each pre-registered claim against its interval. Reads only the JSON the eval scripts wrote."""
import json
import os

B = "/mnt/e/Ciencia/noturno/2023-yuksel-selformer"
PAPER = {"bbbp": ("C1_bbbp_scaffold_roc_auc", 0.902, "primary"),
         "bace": ("C2_bace_scaffold_roc_auc", 0.832, "secondary"),
         "hiv": ("C3_hiv_scaffold_roc_auc", 0.681, "secondary"),
         "tox21": ("C4_tox21_scaffold_roc_auc", 0.653, "secondary"),
         "sider": ("C5_sider_scaffold_roc_auc", 0.745, "secondary")}
BAND = 0.020
DISPLAY = 0.001

rows = []
for task, (cid, paper, tier) in PAPER.items():
    path = os.path.join(B, "runs/out", task + "_test.json")
    if not os.path.exists(path):
        rows.append((cid, task, tier, paper, None, None, "no published fine-tuned model"))
        continue
    r = json.load(open(path))
    ours = r["roc_auc_hard_pred"]
    d = abs(ours - paper)
    status = "display match" if d < DISPLAY else ("inside band" if d <= BAND else "outside band")
    rows.append((cid, task, tier, paper, ours, r["roc_auc_probability"], status))

print("{:<34} {:<6} {:<10} {:>7} {:>8} {:>9} {:>9}  {}".format(
    "claim", "task", "tier", "paper", "ours", "diff", "prob-AUC", "result"))
for cid, task, tier, paper, ours, prob, status in rows:
    if ours is None:
        print("{:<34} {:<6} {:<10} {:>7.3f} {:>8} {:>9} {:>9}  {}".format(cid, task, tier, paper, "-", "-", "-", status))
    else:
        print("{:<34} {:<6} {:<10} {:>7.3f} {:>8.4f} {:>+9.4f} {:>9.4f}  {}".format(
            cid, task, tier, paper, ours, ours - paper, prob, status))

primary = [r for r in rows if r[2] == "primary"][0]
print("\nprimary claim {}: {}".format(primary[0], primary[6]))
print("bands fixed before the runs: display |d| < {}, accept |d| <= {}".format(DISPLAY, BAND))
