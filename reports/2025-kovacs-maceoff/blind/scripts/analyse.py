# Compute per-subset MAEs from the chunk predictions and compare with claims.json
# Reference values are parsed straight from the xyz text, not through ase
import glob
import json
import re
import sys

import numpy as np

root = sys.argv[1]
xyz_path = sys.argv[2]
models = sys.argv[3].split(",")

key_value_re = re.compile(r'(\w+)=("([^"]*)"|(\S+))')


def parse_xyz(path):
	# Return config_type, n_atoms, ref energy, ref forces, stored MACE energy, stored MACE forces
	records = []
	with open(path) as handle:
		while True:
			first_line = handle.readline()
			if not first_line:
				break
			number_of_atoms = int(first_line)
			header = handle.readline()
			info = {}
			for match in key_value_re.finditer(header):
				info[match.group(1)] = match.group(3) if match.group(3) is not None else match.group(4)
			properties = info["Properties"].split(":")
			columns = {}
			column = 0
			for i in range(0, len(properties), 3):
				width = int(properties[i + 2])
				columns[properties[i]] = (column, column + width)
				column += width
			rows = [handle.readline().split() for _ in range(number_of_atoms)]
			forces_begin, forces_end = columns["forces"]
			stored_begin, stored_end = columns["MACE_forces"]
			forces = np.array([[float(x) for x in row[forces_begin:forces_end]] for row in rows])
			stored_forces = np.array([[float(x) for x in row[stored_begin:stored_end]] for row in rows])
			records.append((info["config_type"], number_of_atoms, float(info["energy"]), forces, float(info["MACE_energy"]), stored_forces))
	return records


records = parse_xyz(xyz_path)
config_types = np.array([r[0] for r in records])
numbers_of_atoms = np.array([r[1] for r in records])
reference_energy = np.array([r[2] for r in records])
reference_forces = [r[3] for r in records]
stored_energy = np.array([r[4] for r in records])
stored_forces = [r[5] for r in records]

# A1 filter: drop configs with any |F| > 15 eV/A or |sum F| > 0.1 eV/A
keep_filter = np.array([not ((np.linalg.norm(f, axis=1) > 15.0).any() or np.linalg.norm(f.sum(axis=0)) > 0.1) for f in reference_forces])
subsets = ["PubChem", "DES370K Monomers", "DES370K Dimers", "Dipeptides", "Solvated Amino Acids", "water", "QMugs"]


def load_predictions(model):
	chunk_paths = sorted(glob.glob(f"{root}/runs/{model}/chunk_*.npz"))
	indices, energies, forces = [], [], []
	for path in chunk_paths:
		chunk = np.load(path)
		indices.append(chunk["index"])
		energies.append(chunk["energy"])
		split_points = np.cumsum(chunk["n_atoms"])[:-1]
		forces += np.split(chunk["forces"], split_points)
	indices = np.concatenate(indices)
	assert np.array_equal(indices, np.arange(len(records))), f"{model}: missing or duplicated configs"
	for i, f in enumerate(forces):
		assert len(f) == numbers_of_atoms[i]
	return np.concatenate(energies), forces


def metrics(predicted_energy, predicted_forces, mask):
	# Primary and alternative definitions, meV units
	selected = np.where(mask)[0]
	energy_error = np.abs(predicted_energy[selected] - reference_energy[selected]) / numbers_of_atoms[selected]
	deltas = [predicted_forces[i] - reference_forces[i] for i in selected]
	all_deltas = np.concatenate(deltas)
	return {
		"n_configs": int(len(selected)),
		"n_atoms": int(numbers_of_atoms[selected].sum()),
		"energy_mae_per_atom": 1000.0 * energy_error.mean(),
		"force_mae_component": 1000.0 * np.abs(all_deltas).mean(),
		"force_mae_vector_norm": 1000.0 * np.linalg.norm(all_deltas, axis=1).mean(),
		"force_mae_component_mean_of_configs": 1000.0 * np.mean([np.abs(d).mean() for d in deltas]),
		"energy_rmse_per_atom": 1000.0 * np.sqrt((energy_error ** 2).mean()),
		"force_rmse_component": 1000.0 * np.sqrt((all_deltas ** 2).mean()),
	}


with open(f"{root}/claims.json") as handle:
	claims = json.load(handle)["claims"]

results = {}
print("subset counts (all / after A1 filter):")
for subset in subsets:
	mask = config_types == subset
	print(f"  {subset}: {mask.sum()} / {(mask & keep_filter).sum()}")

prediction_cache = {}
for model in models:
	prediction_cache[model] = load_predictions(model)
	predicted_energy, predicted_forces = prediction_cache[model]
	for subset in subsets:
		mask = config_types == subset
		results[(model, subset, "all")] = metrics(predicted_energy, predicted_forces, mask)
		results[(model, subset, "A1")] = metrics(predicted_energy, predicted_forces, mask & keep_filter)

print("\nPRIMARY: claims (all configs in file)")
print("id\tpublished\tours\tband\tinside")
inside_count = 0
tested = 0
claim_rows = []
for claim in claims:
	model = claim["model"].split("_")[1].split(".")[0]
	if model not in models:
		continue
	value = results[(model, claim["subset_config_type"], "all")][claim["metric"]]
	low, high = claim["band_inclusive"]
	inside = low <= value <= high
	tested += 1
	inside_count += int(inside)
	claim_rows.append({"id": claim["id"], "published": claim["published"], "ours": round(value, 4), "band": [low, high], "inside": bool(inside)})
	print(f"{claim['id']}\t{claim['published']}\t{value:.4f}\t[{low}, {high}]\t{'yes' if inside else 'NO'}")
print(f"\ninside {inside_count} of {tested}")

print("\nEXTRA A1 (force filter) and A2/A4 (other force definitions), per model and subset")
print("model\tsubset\tset\tn\tE_mae\tF_mae_comp\tF_mae_norm\tF_mae_comp_meancfg\tE_rmse\tF_rmse")
for model in models:
	for subset in subsets:
		for set_name in ["all", "A1"]:
			r = results[(model, subset, set_name)]
			print(f"{model}\t{subset}\t{set_name}\t{r['n_configs']}\t{r['energy_mae_per_atom']:.4f}\t{r['force_mae_component']:.4f}\t{r['force_mae_vector_norm']:.4f}\t{r['force_mae_component_mean_of_configs']:.4f}\t{r['energy_rmse_per_atom']:.4f}\t{r['force_rmse_component']:.4f}")

print("\nEXTRA A3: stored MACE_energy/MACE_forces columns in the file")
for subset in subsets:
	mask = config_types == subset
	r = metrics(stored_energy, stored_forces, mask)
	print(f"stored\t{subset}\t{r['n_configs']}\tE_mae={r['energy_mae_per_atom']:.4f}\tF_mae_comp={r['force_mae_component']:.4f}")
for model in models:
	predicted_energy, predicted_forces = prediction_cache[model]
	energy_gap = 1000.0 * np.abs(predicted_energy - stored_energy) / numbers_of_atoms
	force_gap = 1000.0 * np.abs(np.concatenate(predicted_forces) - np.concatenate(stored_forces))
	print(f"ours_{model} vs stored: mean |dE| {energy_gap.mean():.4f} meV/atom, max {energy_gap.max():.4f}; mean |dF| {force_gap.mean():.4f} meV/A, max {force_gap.max():.4f}")

with open(f"{root}/runs/results.json", "w") as handle:
	json.dump({"claims": claim_rows, "inside": inside_count, "tested": tested,
		"per_subset": {f"{m}|{s}|{n}": v for (m, s, n), v in results.items()}}, handle, indent=1)
