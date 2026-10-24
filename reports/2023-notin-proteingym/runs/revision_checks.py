"""Numbers asked for in the report review (2026-10-23). Reads only files already in runs/ and sources/."""
import re
import pandas as pd

W = "/mnt/e/Ciencia/meio/2023-notin-proteingym"
FiveAssays = ["KCNH2_HUMAN_Kozek_2020", "SCN5A_HUMAN_Glazer_2019", "POLG_HCVJF_Qi_2014", "POLG_CXB3N_Mattenberger_2021", "A0A140D2T1_ZIKV_Sourisseau_2019"]
Models = ["ESM2_8M", "ESM2_35M", "ESM2_150M", "ESM2_650M"]


def CorrectedAverage(PerAssay):
	return PerAssay.groupby(["UniProt_ID", "coarse_selection_type"])["spearman"].mean().groupby("coarse_selection_type").mean().mean()


# Agreement with the authors' per-mutant scores, without the 5 MSA-region assays
for Model in Models + ["ESM1b"]:
	Table = pd.read_csv(f"{W}/runs/results/{Model}_vs_authors.csv")
	Rest = Table[~Table.DMS_id.isin(FiveAssays)] if Model != "ESM1b" else Table
	Worst = Rest.loc[Rest.max_abs_diff.idxmax()]
	print(f"{Model}: assays={len(Rest)} (excluding the 5 MSA-region assays: {Model != 'ESM1b'}) min_spearman={Rest.spearman_ours_vs_authors.min():.7f} max_abs_diff={Rest.max_abs_diff.max():.3g} ({Worst.DMS_id})")

# Effect of the 5 assays: swap in the authors' per-assay values for those 5 only
for Model in Models:
	Ours = pd.read_csv(f"{W}/runs/results/{Model}_per_assay.csv")
	Authors = pd.read_csv(f"{W}/runs/results/authors_{Model}_per_assay.csv").set_index("DMS_id")["spearman"]
	Others = Ours[~Ours.DMS_id.isin(FiveAssays)]
	IdenticalOthers = int((Others.spearman.values == Authors.reindex(Others.DMS_id).values).sum())
	Swapped = Ours.copy()
	for DmsId in FiveAssays:
		Swapped.loc[Swapped.DMS_id == DmsId, "spearman"] = Authors[DmsId]
	Before = CorrectedAverage(Ours)
	After = CorrectedAverage(Swapped)
	print(f"{Model}: ours={Before:.4f} with_authors_values_on_5={After:.4f} effect={After - Before:+.4f} other_assays_identical={IdenticalOthers}/{len(Others)}")

# Weight of each of the 5 proteins in the corrected average
Ours = pd.read_csv(f"{W}/runs/results/ESM2_8M_per_assay.csv")
ProteinsPerType = Ours.groupby("coarse_selection_type")["UniProt_ID"].nunique()
print("proteins per function type:", ProteinsPerType.to_dict(), "total proteins:", Ours.UniProt_ID.nunique())
for DmsId in FiveAssays:
	Row = Ours[Ours.DMS_id == DmsId].iloc[0]
	SameProtein = int(((Ours.UniProt_ID == Row.UniProt_ID) & (Ours.coarse_selection_type == Row.coarse_selection_type)).sum())
	Weight = 1.0 / 5.0 / ProteinsPerType[Row.coarse_selection_type]
	print(f"{DmsId}: type={Row.coarse_selection_type} assays_of_same_protein_and_type={SameProtein} protein_weight={Weight:.4%}")

# KCNH2: mutated positions and MSA region
Reference = pd.read_csv(f"{W}/repo/reference_files/DMS_substitutions.csv").set_index("DMS_id")
Kcnh2 = pd.read_csv(f"{W}/data/dms/DMS_ProteinGym_substitutions/{Reference.loc['KCNH2_HUMAN_Kozek_2020', 'DMS_filename']}")
Positions = sorted({int(Position) for Mutant in Kcnh2.mutant for Position in re.findall(r"[A-Z](\d+)[A-Z]", Mutant)})
print(f"KCNH2_HUMAN_Kozek_2020: mutants={len(Kcnh2)} positions={len(Positions)} ({Positions[0]}-{Positions[-1]}) MSA_start={Reference.loc['KCNH2_HUMAN_Kozek_2020', 'MSA_start']} MSA_end={Reference.loc['KCNH2_HUMAN_Kozek_2020', 'MSA_end']}")
His7 = pd.read_csv(f"{W}/data/dms/DMS_ProteinGym_substitutions/{Reference.loc['HIS7_YEAST_Pokusaeva_2019', 'DMS_filename']}")
print(f"HIS7_YEAST_Pokusaeva_2019: mutants={len(His7)}")

# Pinned versions vs the authors' environment file
Authors = {}
for Line in open(f"{W}/repo/environments/proteingym_env.txt"):
	if "==" in Line:
		Name, Version = Line.strip().split("==", 1)
		Authors[Name.lower()] = Version
Differ = []
for Line in open(f"{W}/env/requirements.lock"):
	if "==" in Line and not Line.startswith(" "):
		Name, Version = Line.strip().split("==", 1)
		Name = Name.lower()
		if Name not in Authors:
			Differ.append(f"{Name} {Version} (not in proteingym_env.txt)")
		elif Authors[Name] != Version:
			Differ.append(f"{Name} {Version} (proteingym_env.txt {Authors[Name]})")
print("lock vs proteingym_env.txt:", "; ".join(Differ))
