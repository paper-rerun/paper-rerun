# Count the PG_v1.3 substitution test set (claim C0) and check it against the data files
import csv
import json
import os
import sys
from collections import Counter

Root = "/mnt/e/Ciencia/pipeline/2023-notin-proteingym"
ReferencePath = Root + "/repo/reference_files/DMS_substitutions.csv"
DataFolder = Root + "/data/DMS_ProteinGym_substitutions"
SpearmanPath = Root + "/repo/benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv"
OutFolder = Root + "/exec/B0_testset"

ReferenceRows = list(csv.DictReader(open(ReferencePath)))

# Per assay: reference count vs rows in the unpacked data file
PerAssayRows = []
for Row in ReferenceRows:
	DataFilePath = os.path.join(DataFolder, Row["DMS_filename"])
	with open(DataFilePath) as DataFile:
		DataReader = csv.DictReader(DataFile)
		DataRows = list(DataReader)
	MutantsInFile = len(DataRows)
	UniqueMutantsInFile = len(set(DataRow["mutant"] for DataRow in DataRows))
	PerAssayRows.append({
		"DMS_id": Row["DMS_id"],
		"UniProt_ID": Row["UniProt_ID"],
		"coarse_selection_type": Row["coarse_selection_type"],
		"seq_len": int(Row["seq_len"]),
		"ref_total_mutants": int(Row["DMS_total_number_mutants"]),
		"file_rows": MutantsInFile,
		"file_unique_mutants": UniqueMutantsInFile,
		"match": int(Row["DMS_total_number_mutants"]) == MutantsInFile,
	})

with open(OutFolder + "/per_assay.csv", "w", newline="") as OutFile:
	Writer = csv.DictWriter(OutFile, fieldnames=list(PerAssayRows[0].keys()))
	Writer.writeheader()
	Writer.writerows(PerAssayRows)

# Cross-check DMS ids and selection type against the authors' per-assay Spearman table
SpearmanRows = list(csv.DictReader(open(SpearmanPath)))
SpearmanIdColumn = "DMS_id" if "DMS_id" in SpearmanRows[0] else list(SpearmanRows[0].keys())[0]
SpearmanTypes = {SpearmanRow[SpearmanIdColumn]: SpearmanRow.get("Selection Type") for SpearmanRow in SpearmanRows}
ReferenceTypes = {Row["DMS_id"]: Row["coarse_selection_type"] for Row in ReferenceRows}

Summary = {
	"reference_file": ReferencePath,
	"n_assays": len(ReferenceRows),
	"n_unique_DMS_id": len(set(ReferenceTypes)),
	"n_data_files_on_disk": len([Name for Name in os.listdir(DataFolder) if Name.endswith(".csv")]),
	"sum_ref_total_mutants": sum(Item["ref_total_mutants"] for Item in PerAssayRows),
	"sum_file_rows": sum(Item["file_rows"] for Item in PerAssayRows),
	"sum_file_unique_mutants": sum(Item["file_unique_mutants"] for Item in PerAssayRows),
	"assays_where_ref_count_differs_from_file": [Item["DMS_id"] for Item in PerAssayRows if not Item["match"]],
	"n_UniProt_IDs": len(set(Row["UniProt_ID"] for Row in ReferenceRows)),
	"n_seq_len_gt_1022": sum(int(Row["seq_len"]) > 1022 for Row in ReferenceRows),
	"coarse_selection_type_counts": dict(sorted(Counter(Row["coarse_selection_type"] for Row in ReferenceRows).items())),
	"n_UniProt_function_units": len(set((Row["UniProt_ID"], Row["coarse_selection_type"]) for Row in ReferenceRows)),
	"n_single_mutants": sum(int(Row["DMS_number_single_mutants"]) for Row in ReferenceRows),
	"n_multiple_mutants": sum(int(Row["DMS_number_multiple_mutants"]) for Row in ReferenceRows),
	"n_assays_with_multiples": sum(Row["includes_multiple_mutants"].upper() == "TRUE" for Row in ReferenceRows),
	"spearman_csv_n_assays": len(SpearmanTypes),
	"spearman_csv_ids_equal_reference": set(SpearmanTypes) == set(ReferenceTypes),
	"spearman_csv_selection_type_equal_reference": SpearmanTypes == ReferenceTypes,
}
json.dump(Summary, open(OutFolder + "/summary.json", "w"), indent=1)
print(json.dumps(Summary, indent=1))

# Self-check: the claim is an exact count
assert Summary["n_assays"] == 217, Summary["n_assays"]
