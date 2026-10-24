import pandas as pd
R = pd.read_csv("/mnt/e/Ciencia/meio/2023-notin-proteingym/repo/reference_files/DMS_substitutions.csv")
print("assays", len(R), "mutants", R.DMS_total_number_mutants.sum(), "proteins", R.UniProt_ID.nunique())
print("assays with seq_len>1022:", (R.seq_len > 1022).sum(), "proteins:", R[R.seq_len > 1022].UniProt_ID.nunique())
print(R.coarse_selection_type.value_counts().to_string())
print("sum seq_len", R.seq_len.sum())
print(R[R.seq_len > 1022][["DMS_index", "DMS_id", "seq_len", "DMS_total_number_mutants"]].to_string())
