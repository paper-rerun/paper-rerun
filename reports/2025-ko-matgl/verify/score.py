# Blind verify scoring, written from the pre-registered definitions only (not from any other stage's code)
# energy_MAE_per_atom: mean over conformations of |E_pred - E_DFT| / n_atoms, meV/atom, accumulated in float64
# force_MAE: pooled mean of |F_pred - F_DFT| over every Cartesian component, eV/A
import json
import os

import h5py
import numpy as np

from predict import DataDir, VerifyDir

PredDir = f"{VerifyDir}/preds"
Files = {
	"ani_md_bench": "ANI-MD",
	"drugbank_testset": "DrugBank",
	"gdb11_07_test500": "GDB07to09",
	"gdb11_08_test500": "GDB07to09",
	"gdb11_09_test500": "GDB07to09",
	"gdb11_10_test500": "GDB10to13",
	"gdb11_11_test500": "GDB10to13",
	"gdb13_12_test1000": "GDB10to13",
	"gdb13_13_test1000": "GDB10to13",
	"tripeptide_full": "Tripeptides",
	"s66x8_wb97x6-31gd": "s66x8",
}
# Primary groups (reading A for the GDB labels)
Groups = {
	"animd": ["ani_md_bench"],
	"gdb9to11": ["gdb11_09_test500", "gdb11_10_test500", "gdb11_11_test500"],
	"gdb12to13": ["gdb13_12_test1000", "gdb13_13_test1000"],
	"drugbank": ["drugbank_testset"],
	"s66x8": ["s66x8_wb97x6-31gd"],
	"tripeptides": ["tripeptide_full"],
}
AlternativeGroups = {
	"gdb9to11_readingB_gdb11_07to11": ["gdb11_07_test500", "gdb11_08_test500", "gdb11_09_test500", "gdb11_10_test500", "gdb11_11_test500"],
	"gdb9to11_readingC_folder_GDB07to09": ["gdb11_07_test500", "gdb11_08_test500", "gdb11_09_test500"],
	"gdb12to13_readingC_folder_GDB10to13": ["gdb11_10_test500", "gdb11_11_test500", "gdb13_12_test1000", "gdb13_13_test1000"],
}
ModelKeys = {"M3GNet": "m3gnet", "TensorNet": "tensornet", "SO3Net": "so3net"}
ExpectedConformations = {"animd": 1791, "gdb9to11": 35670, "gdb12to13": 24000, "drugbank": 13379, "s66x8": 528, "tripeptides": 1984}

Paper = {
	"fig4a-m3gnet-animd": 19.159, "fig4a-m3gnet-gdb9to11": 8.925, "fig4a-m3gnet-gdb12to13": 3.655, "fig4a-m3gnet-drugbank": 12.01, "fig4a-m3gnet-s66x8": 9.835, "fig4a-m3gnet-tripeptides": 2.662,
	"fig4b-m3gnet-animd": 0.142, "fig4b-m3gnet-gdb9to11": 0.074, "fig4b-m3gnet-gdb12to13": 0.118, "fig4b-m3gnet-drugbank": 0.126, "fig4b-m3gnet-s66x8": 0.029, "fig4b-m3gnet-tripeptides": 0.067,
	"fig4a-tensornet-animd": 11.099, "fig4a-tensornet-gdb9to11": 1.705, "fig4a-tensornet-gdb12to13": 3.252, "fig4a-tensornet-drugbank": 1.123, "fig4a-tensornet-s66x8": 6.031, "fig4a-tensornet-tripeptides": 2.248,
	"fig4b-tensornet-animd": 0.099, "fig4b-tensornet-gdb9to11": 0.056, "fig4b-tensornet-gdb12to13": 0.09, "fig4b-tensornet-drugbank": 0.086, "fig4b-tensornet-s66x8": 0.045, "fig4b-tensornet-tripeptides": 0.067,
	"fig4a-so3net-animd": 2.283, "fig4a-so3net-gdb9to11": 3.889, "fig4a-so3net-gdb12to13": 1.271, "fig4a-so3net-drugbank": 0.969, "fig4a-so3net-s66x8": 2.558, "fig4a-so3net-tripeptides": 1.245,
	"fig4b-so3net-animd": 0.044, "fig4b-so3net-gdb9to11": 0.032, "fig4b-so3net-gdb12to13": 0.044, "fig4b-so3net-drugbank": 0.044, "fig4b-so3net-s66x8": 0.011, "fig4b-so3net-tripeptides": 0.029,
}


def LoadPred(ModelName, Stem):
	return dict(np.load(f"{PredDir}/{ModelName}/{Stem}.npz"))


def Concat(ModelName, Stems):
	Parts = [LoadPred(ModelName, Stem) for Stem in Stems]
	return {Key: np.concatenate([Part[Key] for Part in Parts]) for Key in ["natoms", "e_dft", "e_pred", "f_abs_sum", "f_norm_sum"]}


def EnergyMaePerAtom(Data):
	return float(np.mean(np.abs(Data["e_pred"] - Data["e_dft"]) / Data["natoms"]) * 1000.0)


def ForceMae(Data):
	return float(Data["f_abs_sum"].sum() / (3 * Data["natoms"]).sum())


def Main():
	Results = []
	Extras = {}
	PrimaryValues = {}
	for ModelName, ModelKey in ModelKeys.items():
		PerFile = {}
		for Stem in Files:
			Data = Concat(ModelName, [Stem])
			PerFile[Stem] = {
				"n_conf": int(len(Data["natoms"])),
				"energy_mae_meV_atom": EnergyMaePerAtom(Data),
				"force_mae_eV_A": ForceMae(Data),
			}
		Extras[f"{ModelName}_per_file"] = PerFile
		for GroupKey, Stems in Groups.items():
			Data = Concat(ModelName, Stems)
			NumConf = int(len(Data["natoms"]))
			assert NumConf == ExpectedConformations[GroupKey], (ModelName, GroupKey, NumConf)
			for Panel, Value in [("fig4a", EnergyMaePerAtom(Data)), ("fig4b", ForceMae(Data))]:
				ClaimId = f"{Panel}-{ModelKey}-{GroupKey}"
				PrimaryValues[ClaimId] = (Value, NumConf)

			# Alternatives, only for extra_analyses
			Alternative = Extras.setdefault(f"{ModelName}_alternatives", {})
			Alternative[f"{GroupKey}_mean_of_per_file_energy"] = float(np.mean([PerFile[Stem]["energy_mae_meV_atom"] for Stem in Stems]))
			Alternative[f"{GroupKey}_mean_of_per_file_force"] = float(np.mean([PerFile[Stem]["force_mae_eV_A"] for Stem in Stems]))
			Alternative[f"{GroupKey}_energy_total_mae_over_mean_natoms"] = float(np.mean(np.abs(Data["e_pred"] - Data["e_dft"])) / np.mean(Data["natoms"]) * 1000.0)
			Alternative[f"{GroupKey}_energy_signed_mean_per_atom"] = float(np.mean((Data["e_pred"] - Data["e_dft"]) / Data["natoms"]) * 1000.0)
			Alternative[f"{GroupKey}_force_norm_mae"] = float(Data["f_norm_sum"].sum() / Data["natoms"].sum())
			Alternative[f"{GroupKey}_force_per_conf_mae_then_mean"] = float(np.mean(Data["f_abs_sum"] / (3 * Data["natoms"])))
		for AlternativeKey, Stems in AlternativeGroups.items():
			Data = Concat(ModelName, Stems)
			Alternative = Extras[f"{ModelName}_alternatives"]
			Alternative[f"{AlternativeKey}_n"] = int(len(Data["natoms"]))
			Alternative[f"{AlternativeKey}_energy"] = EnergyMaePerAtom(Data)
			Alternative[f"{AlternativeKey}_force"] = ForceMae(Data)

	Command = "MSYS_NO_PATHCONV=1 wsl -d Ubuntu -- bash /mnt/e/Ciencia/pipeline/2025-ko-matgl/verify/run_score.sh"
	OutputPath = f"{VerifyDir}/results.json"
	for ClaimId, (Value, NumConf) in PrimaryValues.items():
		Results.append({"claim_id": ClaimId, "value": Value, "n": NumConf, "paper_value": Paper[ClaimId], "diff": Value - Paper[ClaimId], "command": Command, "output_path": OutputPath})

	# Text claims, same computation as the ANI-MD bars
	Text = [
		("text-m3gnet-animd-energy-gt14", "fig4a-m3gnet-animd"),
		("text-m3gnet-animd-force-gt014", "fig4b-m3gnet-animd"),
		("text-tensornet-animd-energy", "fig4a-tensornet-animd"),
		("text-tensornet-animd-force", "fig4b-tensornet-animd"),
		("text-so3net-animd-energy", "fig4a-so3net-animd"),
		("text-so3net-animd-force", "fig4b-so3net-animd"),
	]
	for ClaimId, SourceId in Text:
		Value, NumConf = PrimaryValues[SourceId]
		Results.append({"claim_id": ClaimId, "value": Value, "n": NumConf, "command": Command, "output_path": OutputPath})

	# Data description claims, straight from the HDF5 file, no model
	with h5py.File(f"{DataDir}/ANI-MD/ani_md_bench.h5", "r") as DataFile:
		AtomCounts = {}
		DataFile.visititems(lambda Name, Item: AtomCounts.__setitem__(Name, len(Item["species"])) if isinstance(Item, h5py.Group) and "species" in Item else None)
	Results.append({"claim_id": "data-animd-natoms", "value": max(AtomCounts.values()), "n": len(AtomCounts), "command": Command, "output_path": OutputPath})
	Results.append({"claim_id": "data-animd-ntraj", "value": len(AtomCounts), "n": len(AtomCounts), "command": Command, "output_path": OutputPath})
	Extras["animd_atom_counts"] = AtomCounts

	with open(OutputPath, "w") as OutFile:
		json.dump({"results": Results, "extras": Extras}, OutFile, indent=1)
	for Row in Results:
		print(Row["claim_id"], round(Row["value"], 5), Row.get("paper_value"), Row["n"])


if __name__ == "__main__":
	Main()
