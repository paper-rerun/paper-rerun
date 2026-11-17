# Build claims.json from Table S1 (arXiv v5 SI, identical to v1 Table III and v3 Table IV), MAE rows
import json

subsets = ["PubChem", "DES370K Monomers", "DES370K Dimers", "Dipeptides", "Solvated Amino Acids", "water", "QMugs"]
paper_column = {"water": "Water"}
energy = {
	"small":  [1.41, 1.04, 0.98, 0.84, 1.60, 1.67, 1.03],
	"medium": [0.91, 0.63, 0.58, 0.52, 1.21, 0.76, 0.69],
	"large":  [0.88, 0.59, 0.54, 0.42, 0.98, 0.83, 0.45],
}
force = {
	"small":  [35.68, 17.63, 16.31, 25.07, 38.56, 28.53, 41.45],
	"medium": [20.57, 9.36, 9.02, 14.27, 23.26, 15.27, 23.58],
	"large":  [14.75, 6.58, 6.62, 10.19, 19.43, 13.57, 16.93],
}
paper_test_counts = {"PubChem": 33884, "DES370K Monomers": 889, "DES370K Dimers": 13896, "Dipeptides": 1025,
	"Solvated Amino Acids": 52, "water": 84, "QMugs": 144, "Tripeptides": 898}

def band(value):
	half_width = max(0.01, 0.01 * value)
	return [round(value - half_width, 4), round(value + half_width, 4)]

claims = []
for model in ["small", "medium", "large"]:
	for index, subset in enumerate(subsets):
		for metric, table, unit in [("energy_mae_per_atom", energy, "meV/atom"), ("force_mae_component", force, "meV/A")]:
			value = table[model][index]
			claims.append({
				"id": f"{model}|{subset}|{metric}",
				"model": f"MACE-OFF23_{model}.model",
				"subset_config_type": subset,
				"paper_column": paper_column.get(subset, subset),
				"metric": metric,
				"unit": unit,
				"published": value,
				"band_inclusive": band(value),
			})

doc = {
	"paper": "Kovacs et al., MACE-OFF, JACS 2025 147(21) 17598, DOI 10.1021/jacs.4c07099; arXiv 2312.15211",
	"source_of_numbers": "Table S1 'Summary of test set errors including inter-molecular force errors', MAE block, rows E (meV/at) and Ftotal (meV/A), arXiv v5 (2025-08-22) Supporting Information p.5. Identical values in arXiv v1 Table III and v3 Table IV. Version-of-record SI on pubs.acs.org returned HTTP 403 and was not read.",
	"test_data": "test_large_neut_all.xyz from Apollo DOI 10.17863/CAM.107498 (bitstream md5 bf1f7c7ff1714e6ac6af2cdc642a130a, xyz sha256 c65a7fcf9140fb127ccc6cc7fce243ab5052665a8741516cde143592a319745e)",
	"weights": "repo ACEsuit/mace-off @ 91a78c5a9c300d1104700d9352c8bfe449227737, mace_off23/MACE-OFF23_{small,medium,large}.model (not MACE-OFF23b, not MACE-OFF24)",
	"definitions": {
		"energy_mae_per_atom": "mean over configurations of the subset of |E_model - E_ref| / N_atoms, E = total energy (model output includes its stored E0s; reference = info['energy'] in the file, eV), times 1000 -> meV/atom",
		"force_mae_component": "mean of |F_model - F_ref| over all Cartesian components of all atoms of all configurations in the subset, pooled (MACE's mae_f and aseMolec's .flatten() convention), times 1000 -> meV/A. Reference = arrays['forces'].",
		"precision": "float64 (torch default dtype float64), MACE 0.3.4, model.double()",
		"subset": "config_type field in the xyz; 'water' = paper column Water",
	},
	"set_composition_decision": {
		"counts_in_file": {"PubChem": 34093, "DES370K Monomers": 889, "DES370K Dimers": 13908, "Dipeptides": 1025, "Solvated Amino Acids": 52, "water": 84, "QMugs": 144, "Tripeptides": 0},
		"counts_in_paper_Table1": paper_test_counts,
		"primary": "Evaluate every configuration in the released file, no filtering. The released file is what the paper points readers to; we have no rule that maps 34093->33884 or 13908->13896.",
		"tripeptides": "Not in the released test file: the Tripeptide column (898 configs) is not testable and is excluded. 42 claims = 3 models x 7 subsets x 2 metrics.",
		"extra_analyses_not_affecting_verdict": [
			"A1: same metrics after dropping configs with any per-atom |F_ref| > 15 eV/A or |sum_i F_ref| > 0.1 eV/A (the SPICE-2 filters of SI S1), to see if the PubChem/Dimers excess explains any gap.",
			"A2: per-atom vector-norm force MAE (mean over atoms of |F_model - F_ref|_2) as the alternative force definition.",
			"A3: errors of the MACE_energy / MACE_forces columns already stored in the file, against which of our three models they match.",
			"A4: mean-of-per-config force MAE instead of pooled.",
		],
	},
	"tolerance": {
		"rule": "inside if published - h <= ours <= published + h with h = max(0.01, 0.01*published) in the claim's unit",
		"reasoning": "Inference with fixed weights on fixed data is deterministic; float64 run-to-run and library-version differences are orders of magnitude below 0.01 meV. The table prints 2 decimals, so rounding alone needs +-0.005; we allow +-0.01 absolute or 1% relative, whichever is larger, for MACE-version and hardware differences. Not wider, because the paper gives no uncertainty and a wider band would hide a wrong data split or a wrong definition. PubChem and DES370K Dimers have 209 and 12 more configs in the file than in Table 1; if those subsets fall outside, A1 is reported but the verdict uses the primary numbers.",
	},
	"verdict_rule": "Reproduced if >= 38 of 42 claims inside; Partially reproduced if 21-37 inside; Not reproduced if < 21 inside.",
	"claims": claims,
}
with open("/mnt/e/Ciencia/noturno/2025-kovacs-maceoff-cego/claims.json", "w") as handle:
	json.dump(doc, handle, indent=1)
print(len(claims), "claims written")
