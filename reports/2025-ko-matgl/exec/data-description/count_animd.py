# Count ANI-MD trajectories and atoms per molecule straight from the COMP6 v1 HDF5 file
import hashlib
import json
import sys

import h5py

H5_PATH = "/mnt/e/Ciencia/pipeline/2025-ko-matgl/data/COMP6v1/ANI-MD/ani_md_bench.h5"
OUT_DIR = "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/data-description"

# Git blob sha1 so the file is tied to the pinned commit
raw = open(H5_PATH, "rb").read()
blob_sha1 = hashlib.sha1(b"blob %d\0" % len(raw) + raw).hexdigest()

molecules = []
with h5py.File(H5_PATH, "r") as f:
	def visit(name, obj):
		# A molecule group is any group that holds a species dataset
		if isinstance(obj, h5py.Group) and "species" in obj:
			species = [s.decode() if isinstance(s, bytes) else str(s) for s in obj["species"][()]]
			molecules.append({
				"group": name,
				"n_atoms": len(species),
				"n_conformations": int(obj["coordinates"].shape[0]),
				"coordinates_shape": list(obj["coordinates"].shape),
				"forces_shape": list(obj["forces"].shape) if "forces" in obj else None,
				"n_heavy_atoms": sum(1 for s in species if s != "H"),
				"elements": sorted(set(species)),
				"keys": sorted(obj.keys()),
			})
	f.visititems(visit)
	top_level = sorted(f.keys())

molecules.sort(key=lambda m: m["n_atoms"])
n_traj = len(molecules)
max_atoms = max(m["n_atoms"] for m in molecules)
n_with_312 = sum(1 for m in molecules if m["n_atoms"] == 312)
others = [m["n_atoms"] for m in molecules if m["n_atoms"] != max_atoms]

# Consistency: per-group coordinate atom axis must match len(species)
for m in molecules:
	assert m["coordinates_shape"][1] == m["n_atoms"], m["group"]

result = {
	"file": H5_PATH,
	"file_bytes": len(raw),
	"git_blob_sha1": blob_sha1,
	"top_level_keys": top_level,
	"molecules": molecules,
	"total_conformations": sum(m["n_conformations"] for m in molecules),
	"claims": {
		"data-animd-natoms": {"value": max_atoms, "paper_value": 312, "match": max_atoms == 312,
			"n_molecules_with_312_atoms": n_with_312,
			"literal_reading_every_molecule_312": n_with_312 == n_traj,
			"other_molecules_atom_range": [min(others), max(others)] if others else None,
			"n_other_molecules": len(others)},
		"data-animd-ntraj": {"value": n_traj, "paper_value": 16, "match": n_traj == 16},
	},
}
json.dump(result, open(OUT_DIR + "/results.json", "w"), indent=1)
for m in molecules:
	print(f'{m["group"]:40s} atoms={m["n_atoms"]:4d} heavy={m["n_heavy_atoms"]:4d} conf={m["n_conformations"]:4d} {m["elements"]}')
print("blob", blob_sha1, "bytes", len(raw), "top", top_level)
print(json.dumps(result["claims"], indent=1))
