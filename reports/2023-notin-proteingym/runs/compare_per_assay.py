"""Our per-assay Spearman vs the authors' DMS_level csv (PG_v1.3). Usage: compare_per_assay.py <run name> <authors column>"""
import sys
import pandas as pd
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
Ours = pd.read_csv(f"{W}/runs/results/{sys.argv[1]}_per_assay.csv").set_index("DMS_id")
Theirs = pd.read_csv(f"{W}/sources/repo_csv/DMS_level_PG_v1.3.csv").set_index("DMS ID")[sys.argv[2]]
Diff = (Ours["spearman"] - Theirs.reindex(Ours.index)).rename("diff")
Table = pd.concat([Ours["spearman"], Theirs.reindex(Ours.index).rename("authors"), Diff], axis=1)
print(f"{sys.argv[1]}: assays |diff|>0.002: {(Diff.abs() > 0.002).sum()}  max |diff|: {Diff.abs().max():.3f}  mean diff: {Diff.mean():+.4f}")
print(Table[Diff.abs() > 0.002].sort_values("diff").to_string())
