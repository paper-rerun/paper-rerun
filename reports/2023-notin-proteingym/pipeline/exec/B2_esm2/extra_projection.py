# Extra analysis for the sampled sizes: projected full-217 corrected average of the released script.
# Assumption, from the 8M full run (212 of 217 assays equal to the authors' per-mutant scores, the other 5 fully explained by MSA-region input)
# and the 30-assay samples (29 of 30 equal at every size): every assay equals the authors' value except the 5 region-scored ones,
# which take our full-target_seq Spearman (pipeline run when available, extra_slices full-sequence score otherwise), rounded to 3 decimals like the CSV.
# For 8M the projection is checked against the real full run
import csv, json, os
from collections import defaultdict

W = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym"
B = W + "/exec/B2_esm2"
Region = ["A0A140D2T1_ZIKV_Sourisseau_2019", "KCNH2_HUMAN_Kozek_2020", "POLG_CXB3N_Mattenberger_2021", "POLG_HCVJF_Qi_2014", "SCN5A_HUMAN_Glazer_2019"]


def Mean(Values):
	return sum(Values) / len(Values)


def Corrected(Rows, CodeDefinition):
	ByType = defaultdict(list)
	if CodeDefinition:
		ByPair = defaultdict(list)
		for Value, Ftype, Uniprot in Rows.values():
			ByPair[(Ftype, Uniprot)].append(Value)
		for (Ftype, Uniprot), Values in ByPair.items():
			ByType[Ftype].append(Mean(Values))
	else:
		for Value, Ftype, Uniprot in Rows.values():
			ByType[Ftype].append(Value)
	return Mean([Mean(Values) for Values in ByType.values()])


Output = {}
for Size in ["8M", "35M", "150M", "650M"]:
	Rows = {}
	for Row in csv.DictReader(open(f"{W}/repo/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv")):
		Rows[Row["DMS ID"]] = (float(Row[f"ESM2 ({Size})"]), Row["Selection Type"], Row["UniProt ID"])
	Ours = {Row["DMS_id"]: float(Row["ours"]) for Row in csv.DictReader(open(f"{B}/per_assay_Spearman_{Size}.csv"))}
	Sources = {}
	for DmsId in Region:
		if DmsId in Ours:
			Value, Sources[DmsId] = Ours[DmsId], "pipeline run"
		else:
			Path = f"{B}/extra_slices_{Size}_{DmsId}.json"
			if not os.path.exists(Path):
				Sources[DmsId] = "missing"
				continue
			Slices = json.load(open(Path))
			Value, Sources[DmsId] = round(Slices[[Key for Key in Slices if Key.startswith("1-")][0]]["spearman_vs_DMS"], 3), "extra_slices full target_seq"
		Rows[DmsId] = (Value, Rows[DmsId][1], Rows[DmsId][2])
	Output[Size] = {"projected_code_definition": round(Corrected(Rows, True), 4), "projected_literal_definition": round(Corrected(Rows, False), 4),
		"region_assay_values": {DmsId: Rows[DmsId][0] for DmsId in Region}, "sources": Sources}
	print(Size, Output[Size])
json.dump(Output, open(f"{B}/extra_projection.json", "w"), indent=1)
