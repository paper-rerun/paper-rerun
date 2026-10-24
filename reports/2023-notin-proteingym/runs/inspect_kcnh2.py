"""Diagnostic: where in the sequence do our and the authors' ESM2 8M scores disagree, for the 5 assays that differ?"""
import pandas as pd
from scipy.stats import spearmanr
W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
for DmsId in ["KCNH2_HUMAN_Kozek_2020", "SCN5A_HUMAN_Glazer_2019", "POLG_HCVJF_Qi_2014", "A0A140D2T1_ZIKV_Sourisseau_2019", "POLG_CXB3N_Mattenberger_2021", "BRCA1_HUMAN_Findlay_2018"]:
	Ours = pd.read_csv(f"{W}/runs/scores/ESM2_8M/{DmsId}.csv", usecols=["mutant", "esm2_t6_8M_UR50D"])
	Theirs = pd.read_csv(f"{W}/sources/authors_esm_scores/{DmsId}.csv")
	Merged = Ours.merge(Theirs, on="mutant")
	Merged["position"] = Merged.mutant.str.split(":").str[0].str[1:-1].astype(int)
	Merged["agree"] = (Merged.esm2_t6_8M_UR50D - Merged.ESM2_8M).abs() < 1e-3
	print(DmsId, "positions", Merged.position.min(), "-", Merged.position.max(), "agree fraction", round(Merged.agree.mean(), 3))
	Disagree = Merged[~Merged.agree]
	if len(Disagree):
		print("   disagreeing positions", Disagree.position.min(), "-", Disagree.position.max(), " agreeing positions", Merged[Merged.agree].position.min() if Merged.agree.any() else None, "-", Merged[Merged.agree].position.max() if Merged.agree.any() else None)
	print("   authors spearman between model sizes vs DMS:", {C: round(spearmanr(Merged[C], Merged.DMS_score)[0], 3) for C in ["ESM1b", "ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"]})
