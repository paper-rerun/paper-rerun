# Collect results_<size>.json into summary.json, plus one extra number per size: our corrected average after replacing the assays
# that analyze.py flags as different from the authors' scores with the MSA-region re-score from extra_slices (when one exists).
# That extra number is not the authors' method as released; it tests the explanation for the gap
import csv, glob, json, os
from collections import defaultdict

B = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym/exec/B2_esm2"


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


Summary = {}
for Size in ["8M", "35M", "150M", "650M"]:
	if not os.path.exists(f"{B}/results_{Size}.json"):
		continue
	Result = json.load(open(f"{B}/results_{Size}.json"))
	Rows = {Row["DMS_id"]: (float(Row["ours"]), Row["Selection_Type"], Row["UniProt_ID"]) for Row in csv.DictReader(open(f"{B}/per_assay_Spearman_{Size}.csv"))}
	Mutants = {Row["DMS_id"]: float(Row["max_abs_diff"]) for Row in csv.DictReader(open(f"{B}/per_mutant_check_{Size}.csv"))}
	Differing = sorted(DmsId for DmsId, Value in Mutants.items() if Value > 1e-3)
	Replaced, NotExplained = {}, []
	for DmsId in Differing:
		Path = f"{B}/extra_slices_{Size}_{DmsId}.json"
		if not os.path.exists(Path):
			NotExplained.append(DmsId)
			continue
		Slices = json.load(open(Path))
		Full = [Key for Key in Slices if Key.startswith("1-")][0]
		Region = [Key for Key in Slices if Key != Full][0]
		Replaced[DmsId] = {"region": Region, "region_max_abs_diff_vs_authors": Slices[Region]["max_abs_diff_vs_authors"],
			"spearman_full_seq": round(Slices[Full]["spearman_vs_DMS"], 4), "spearman_region": round(Slices[Region]["spearman_vs_DMS"], 4),
			"authors_spearman": round(Slices[Region]["authors_spearman_vs_DMS"], 4)}
		Rows[DmsId] = (round(Slices[Region]["spearman_vs_DMS"], 3), Rows[DmsId][1], Rows[DmsId][2])
	Result["assays_with_per_mutant_diff_gt_1e-3"] = Differing
	Result["msa_region_rescore"] = Replaced
	Result["differing_assays_without_region_check"] = NotExplained
	Result["ours_code_definition_with_region_rescore"] = round(Corrected(Rows, True), 4)
	Result["ours_literal_definition_with_region_rescore"] = round(Corrected(Rows, False), 4)
	Summary[Size] = Result
json.dump(Summary, open(f"{B}/summary.json", "w"), indent=1)
for Size, Result in Summary.items():
	print(Size, Result["n_assays_ours"], "ours", Result["ours_code_definition"], Result["ours_literal_definition"], "| authors same assays", Result["authors_same_assays_code_definition"],
		"| authors 217", Result["authors_all_217_code_definition"], "| with region rescore", Result["ours_code_definition_with_region_rescore"],
		"| differing", Result["assays_with_per_mutant_diff_gt_1e-3"], "| unexplained", Result["differing_assays_without_region_check"])
