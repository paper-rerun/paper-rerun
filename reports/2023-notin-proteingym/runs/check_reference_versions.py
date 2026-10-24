"""Did target_seq change between PG versions for the assays whose scores disagree with the authors'?"""
import pandas as pd
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym/sources/repo_csv"
Versions = {V: pd.read_csv(f"{W}/DMS_substitutions_PG_v{V}.csv").set_index("DMS_id") for V in ["1.0", "1.1", "1.3"]}
for DmsId in ["KCNH2_HUMAN_Kozek_2020", "SCN5A_HUMAN_Glazer_2019", "POLG_HCVJF_Qi_2014", "A0A140D2T1_ZIKV_Sourisseau_2019", "POLG_CXB3N_Mattenberger_2021", "BRCA1_HUMAN_Findlay_2018", "SPIKE_SARS2_Starr_2020_binding"]:
	Row = []
	for V, Table in Versions.items():
		if DmsId in Table.index:
			Seq = Table.loc[DmsId, "target_seq"]
			Row.append(f"v{V}: len={len(Seq)} hash={hash(Seq) % 100000}")
		else:
			Row.append(f"v{V}: absent")
	print(DmsId, " | ".join(Row))
