import csv
from collections import Counter
rows = list(csv.DictReader(open("/mnt/e/Ciencia/pipeline/2023-notin-proteingym/sources/repo_PG_v1.3/reference_files/DMS_substitutions.csv")))
print("assays", len(rows), "mutants", sum(int(r["DMS_total_number_mutants"]) for r in rows))
print("seq_len>1022", sum(int(r["seq_len"]) > 1022 for r in rows), "seq_len>1024", sum(int(r["seq_len"]) > 1024 for r in rows))
print(Counter(r["coarse_selection_type"] for r in rows), Counter(r["ProteinGym_version"] for r in rows))
print("multi-mutant assays", sum(r["includes_multiple_mutants"] == "True" for r in rows))
