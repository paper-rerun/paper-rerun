"""Per-assay Spearman, ours vs the authors', for the 5 assays scored on the MSA region by the authors; plus the ESM-1b probe."""
import pandas as pd
from scipy.stats import spearmanr
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym/runs"
Five = ["KCNH2_HUMAN_Kozek_2020", "SCN5A_HUMAN_Glazer_2019", "POLG_HCVJF_Qi_2014", "POLG_CXB3N_Mattenberger_2021", "A0A140D2T1_ZIKV_Sourisseau_2019"]
for Model in ["ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"]:
	Ours = pd.read_csv(f"{W}/results/{Model}_per_assay.csv").set_index("DMS_id")["spearman"]
	Theirs = pd.read_csv(f"{W}/results/authors_{Model}_per_assay.csv").set_index("DMS_id")["spearman"]
	print(Model, " | ".join(f"{D.split('_')[0]} {Ours[D]:.3f}/{Theirs[D]:.3f}" for D in Five))
for Strategy in ["wt", "masked"]:
	for DmsId in ["A0A192B1T2_9HIV1_Haddox_2018", "BRCA1_HUMAN_Findlay_2018"]:
		Scores = pd.read_csv(f"{W}/scores/probe_ESM1b_{Strategy}/{DmsId}.csv")
		print(f"probe ESM1b {Strategy} {DmsId} spearman_vs_DMS={spearmanr(Scores.DMS_score, Scores.esm1b_t33_650M_UR50S)[0]:.3f}")
