# Score the comp6-m3gnet claims from the per-group predictions in pred/ and the COMP6 v1 files
# Definitions: energy_MAE_per_atom, force_MAE, units_and_conversion, force_sign_rule (decision read from signcheck.json),
# energy_reference (no offset), pooling_within_group, conformation_inclusion
import csv
import json
import os
import sys

import h5py
import numpy as np
from ase.units import Hartree

sys.path.insert(0, "/mnt/e/Ciencia/pipeline/2025-ko-matgl/exec/comp6-m3gnet")
from common import DATA_DIR, FILES, OUT_DIR, ListMoleculeGroups

SignCheck = json.load(open(f"{OUT_DIR}/signcheck.json"))
assert SignCheck["unit_decision"] == "Ha/A ok" and SignCheck["sign_decision"] in ("keep", "flip")
ReferenceForceSign = -1.0 if SignCheck["sign_decision"] == "flip" else 1.0

# Per-conformation arrays, keyed by file stem
PerFile = {}
PerConformationRows = []
for FileName in FILES:
	FileStem = os.path.splitext(os.path.basename(FileName))[0]
	Columns = {"natoms": [], "e_err_per_atom_meV": [], "e_err_total_eV": [], "f_abs_sum": [], "f_ncomp": [],
		"f_abs_sum_stored_sign": [], "f_norm_err_sum": [], "f_conf_mae": [], "molecule": [], "failed": []}
	with h5py.File(f"{DATA_DIR}/{FileName}", "r") as DataFile:
		GroupNames = ListMoleculeGroups(DataFile)
		for GroupIndex, GroupName in enumerate(GroupNames):
			Prediction = np.load(f"{OUT_DIR}/pred/{FileStem}/{GroupIndex:05d}.npz")
			assert str(Prediction["group"]) == GroupName
			NumAtoms = DataFile[GroupName]["species"].shape[0]
			EnergiesDft = DataFile[GroupName]["energies"][()].astype(np.float64) * Hartree
			ForcesDft = ReferenceForceSign * DataFile[GroupName]["forces"][()].astype(np.float64) * Hartree
			EnergiesPredicted = Prediction["energies_pred_eV"]
			ForcesPredicted = Prediction["forces_pred_eV_A"].astype(np.float64)
			for ConformationIndex in range(len(EnergiesDft)):
				bFailed = not np.isfinite(EnergiesPredicted[ConformationIndex])
				EnergyErrorTotal = EnergiesPredicted[ConformationIndex] - EnergiesDft[ConformationIndex]
				ForceError = ForcesPredicted[ConformationIndex] - ForcesDft[ConformationIndex]
				# Same error with the stored (unflipped) sign, only for the record
				ForceErrorStoredSign = ForcesPredicted[ConformationIndex] - ReferenceForceSign * ForcesDft[ConformationIndex]
				Columns["natoms"].append(NumAtoms)
				Columns["e_err_total_eV"].append(EnergyErrorTotal)
				Columns["e_err_per_atom_meV"].append(EnergyErrorTotal / NumAtoms * 1000.0)
				Columns["f_abs_sum"].append(np.abs(ForceError).sum())
				Columns["f_ncomp"].append(ForceError.size)
				Columns["f_abs_sum_stored_sign"].append(np.abs(ForceErrorStoredSign).sum())
				Columns["f_norm_err_sum"].append(np.linalg.norm(ForceError, axis=1).sum())
				Columns["f_conf_mae"].append(np.abs(ForceError).mean())
				Columns["molecule"].append(GroupName)
				Columns["failed"].append(bFailed)
				PerConformationRows.append([FileStem, GroupName, ConformationIndex, NumAtoms, f"{EnergiesDft[ConformationIndex]:.6f}",
					f"{EnergiesPredicted[ConformationIndex]:.6f}", f"{EnergyErrorTotal / NumAtoms * 1000.0:.6f}",
					f"{np.abs(ForceError).mean():.8f}", ForceError.size])
	PerFile[FileStem] = {Key: np.array(Value) for Key, Value in Columns.items()}

with open(f"{OUT_DIR}/per_conformation.csv", "w", newline="") as CsvFile:
	Writer = csv.writer(CsvFile)
	Writer.writerow(["file", "molecule", "conf", "n_atoms", "E_dft_eV", "E_pred_eV", "E_err_signed_meV_per_atom", "F_mae_conf_eV_A", "F_ncomp"])
	Writer.writerows(PerConformationRows)


def ScoreFiles(FileStems):
	# Pooled over all conformations of the listed files
	Pool = {Key: np.concatenate([PerFile[Stem][Key] for Stem in FileStems]) for Key in PerFile[FileStems[0]]}
	NumFailed = int(Pool["failed"].sum())
	return {
		"files": FileStems,
		"n_conf": int(len(Pool["natoms"])),
		"n_failed": NumFailed,
		"energy_mae_meV_per_atom": float(np.mean(np.abs(Pool["e_err_per_atom_meV"]))),
		"force_mae_eV_A": float(Pool["f_abs_sum"].sum() / Pool["f_ncomp"].sum()),
		# Alternatives, not the fixed definitions
		"alt_energy_mean_signed_meV_per_atom": float(np.mean(Pool["e_err_per_atom_meV"])),
		"alt_energy_total_mae_over_mean_natoms_meV_per_atom": float(np.mean(np.abs(Pool["e_err_total_eV"])) / np.mean(Pool["natoms"]) * 1000.0),
		"alt_energy_total_mae_meV": float(np.mean(np.abs(Pool["e_err_total_eV"])) * 1000.0),
		"alt_force_mae_stored_sign_eV_A": float(Pool["f_abs_sum_stored_sign"].sum() / Pool["f_ncomp"].sum()),
		"alt_force_mae_per_conf_mean_eV_A": float(np.mean(Pool["f_conf_mae"])),
		"alt_force_mae_vector_norm_eV_A": float(Pool["f_norm_err_sum"].sum() / (Pool["f_ncomp"].sum() / 3)),
	}


GroupDefinitions = {
	"animd": ["ani_md_bench"],
	"gdb9to11": ["gdb11_09_test500", "gdb11_10_test500", "gdb11_11_test500"],
	"gdb12to13": ["gdb13_12_test1000", "gdb13_13_test1000"],
	"drugbank": ["drugbank_testset"],
	"s66x8": ["s66x8_wb97x6-31gd"],
	"tripeptides": ["tripeptide_full"],
}
SensitivityGroups = {
	"gdb9to11_readingB_gdb11_07to11": ["gdb11_07_test500", "gdb11_08_test500", "gdb11_09_test500", "gdb11_10_test500", "gdb11_11_test500"],
	"gdb9to11_readingC_folder_GDB07to09": ["gdb11_07_test500", "gdb11_08_test500", "gdb11_09_test500"],
	"gdb12to13_readingC_folder_GDB10to13": ["gdb11_10_test500", "gdb11_11_test500", "gdb13_12_test1000", "gdb13_13_test1000"],
}

Results = {"force_sign": SignCheck["sign_decision"], "groups": {}, "per_file": {}, "sensitivity": {}, "claims": []}
for Stem in PerFile:
	Results["per_file"][Stem] = ScoreFiles([Stem])
for GroupKey, Stems in GroupDefinitions.items():
	Results["groups"][GroupKey] = ScoreFiles(Stems)
	PerFileEnergy = [Results["per_file"][Stem]["energy_mae_meV_per_atom"] for Stem in Stems]
	PerFileForce = [Results["per_file"][Stem]["force_mae_eV_A"] for Stem in Stems]
	Results["groups"][GroupKey]["alt_mean_of_per_file_energy_mae"] = float(np.mean(PerFileEnergy))
	Results["groups"][GroupKey]["alt_mean_of_per_file_force_mae"] = float(np.mean(PerFileForce))
for GroupKey, Stems in SensitivityGroups.items():
	Results["sensitivity"][GroupKey] = ScoreFiles(Stems)

# Per-molecule breakdown for ANI-MD
AniMd = PerFile["ani_md_bench"]
Results["animd_per_molecule"] = {}
for MoleculeName in sorted(set(AniMd["molecule"])):
	Mask = AniMd["molecule"] == MoleculeName
	Results["animd_per_molecule"][MoleculeName] = {
		"n_atoms": int(AniMd["natoms"][Mask][0]), "n_conf": int(Mask.sum()),
		"energy_mae_meV_per_atom": float(np.mean(np.abs(AniMd["e_err_per_atom_meV"][Mask]))),
		"energy_mean_signed_meV_per_atom": float(np.mean(AniMd["e_err_per_atom_meV"][Mask])),
		"force_mae_eV_A": float(AniMd["f_abs_sum"][Mask].sum() / AniMd["f_ncomp"][Mask].sum()),
	}

# Claims
ClaimSpecs = [
	("fig4a-m3gnet-animd", "animd", "energy_mae_meV_per_atom", 19.159, 0.01, "abs"),
	("fig4a-m3gnet-gdb9to11", "gdb9to11", "energy_mae_meV_per_atom", 8.925, 0.01, "abs"),
	("fig4a-m3gnet-gdb12to13", "gdb12to13", "energy_mae_meV_per_atom", 3.655, 0.01, "abs"),
	("fig4a-m3gnet-drugbank", "drugbank", "energy_mae_meV_per_atom", 12.01, 0.01, "abs"),
	("fig4a-m3gnet-s66x8", "s66x8", "energy_mae_meV_per_atom", 9.835, 0.01, "abs"),
	("fig4a-m3gnet-tripeptides", "tripeptides", "energy_mae_meV_per_atom", 2.662, 0.01, "abs"),
	("fig4b-m3gnet-animd", "animd", "force_mae_eV_A", 0.142, 0.0006, "abs"),
	("fig4b-m3gnet-gdb9to11", "gdb9to11", "force_mae_eV_A", 0.074, 0.0006, "abs"),
	("fig4b-m3gnet-gdb12to13", "gdb12to13", "force_mae_eV_A", 0.118, 0.0006, "abs"),
	("fig4b-m3gnet-drugbank", "drugbank", "force_mae_eV_A", 0.126, 0.0006, "abs"),
	("fig4b-m3gnet-s66x8", "s66x8", "force_mae_eV_A", 0.029, 0.0006, "abs"),
	("fig4b-m3gnet-tripeptides", "tripeptides", "force_mae_eV_A", 0.067, 0.0006, "abs"),
	("text-m3gnet-animd-energy-gt14", "animd", "energy_mae_meV_per_atom", 14.0, 0.0, "gt"),
	("text-m3gnet-animd-force-gt014", "animd", "force_mae_eV_A", 0.14, 0.0, "gt"),
]
for ClaimId, GroupKey, Metric, PaperValue, Tolerance, Kind in ClaimSpecs:
	OurValue = Results["groups"][GroupKey][Metric]
	bPass = (OurValue > PaperValue) if Kind == "gt" else (abs(OurValue - PaperValue) <= Tolerance)
	Results["claims"].append({"claim_id": ClaimId, "group": GroupKey, "metric": Metric, "value": OurValue, "n": Results["groups"][GroupKey]["n_conf"],
		"paper_value": PaperValue, "diff": OurValue - PaperValue, "tolerance": Tolerance, "kind": Kind, "pass": bool(bPass)})
	print(f"{ClaimId:34s} ours={OurValue:.5f} paper={PaperValue} diff={OurValue - PaperValue:+.5f} tol={Tolerance} {'PASS' if bPass else 'FAIL'}")

json.dump(Results, open(f"{OUT_DIR}/results.json", "w"), indent=1)
print("n_conf total", sum(Value["n_conf"] for Value in Results["per_file"].values()), "failed", sum(Value["n_failed"] for Value in Results["per_file"].values()))
for Stem, Value in Results["per_file"].items():
	print(f"{Stem:22s} n={Value['n_conf']:6d} E={Value['energy_mae_meV_per_atom']:.4f} F={Value['force_mae_eV_A']:.5f} Esigned={Value['alt_energy_mean_signed_meV_per_atom']:+.4f}")
for Key, Value in Results["sensitivity"].items():
	print(f"{Key:40s} n={Value['n_conf']:6d} E={Value['energy_mae_meV_per_atom']:.4f} F={Value['force_mae_eV_A']:.5f}")
