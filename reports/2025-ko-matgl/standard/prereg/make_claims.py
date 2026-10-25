# Build claims.json (pre-registration) for the MatGL COMP6 check
# Paper values come from fig4_values.json, read from the vector drawing of Fig. 4, so no number is typed by hand
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(sys.argv[1])
SOURCES = ROOT / "sources"

def sha256_of(path):
	return hashlib.sha256(path.read_bytes()).hexdigest()

figure_values = json.loads((SOURCES / "fig4_values.json").read_text())
vector_values = figure_values["vector_journal_pdf_p7"]
raster_values = figure_values["raster_arxiv_v1_p17"]

MODELS = ["M3GNet", "TensorNet", "SO3Net"]
CHECKPOINTS = {
	"M3GNet": {"path_at_tag": "pretrained_models/M3GNet-ANI-1x-Subset-PES/", "model_pt_bytes": 3969478, "state_pt_bytes": 1164446, "state_pt_sha256_prefix_from_triage": "4efa3b11"},
	"SO3Net": {"path_at_tag": "pretrained_models/SO3Net-ANI-1x-Subset-PES/", "model_pt_bytes": 3969478, "state_pt_bytes": 429416, "state_pt_sha256_prefix_from_triage": "947361c5"},
	"TensorNet": {"path_at_tag": "pretrained_models/TensorNet-ANI-1x-Subset-PES/", "model_pt_bytes": 3969478, "state_pt_bytes": 856757, "state_pt_sha256_prefix_from_triage": "02fdfcd1"},
}
GROUPS = [
	{"label": "ANI-MD", "slug": "ANIMD", "files": ["COMP6v1/ANI-MD/ani_md_bench.h5"]},
	{"label": "GDB 9-11", "slug": "GDB9-11", "files": ["COMP6v1/GDB07to09/gdb11_07_test500.h5", "COMP6v1/GDB07to09/gdb11_08_test500.h5", "COMP6v1/GDB07to09/gdb11_09_test500.h5"]},
	{"label": "GDB 12-13", "slug": "GDB12-13", "files": ["COMP6v1/GDB10to13/gdb11_10_test500.h5", "COMP6v1/GDB10to13/gdb11_11_test500.h5", "COMP6v1/GDB10to13/gdb13_12_test1000.h5", "COMP6v1/GDB10to13/gdb13_13_test1000.h5"]},
	{"label": "Drugbank", "slug": "DrugBank", "files": ["COMP6v1/DrugBank/drugbank_testset.h5"]},
	{"label": "S66x8", "slug": "S66x8", "files": ["COMP6v1/s66x8/s66x8_wb97x6-31gd.h5"]},
	{"label": "Tripeptides", "slug": "Tripeptides", "files": ["COMP6v1/Tripeptides/tripeptide_full.h5"]},
]
ALTERNATIVE_GDB_GROUPING = {
	"GDB 9-11": ["COMP6v1/GDB07to09/gdb11_09_test500.h5", "COMP6v1/GDB10to13/gdb11_10_test500.h5", "COMP6v1/GDB10to13/gdb11_11_test500.h5"],
	"GDB 12-13": ["COMP6v1/GDB10to13/gdb13_12_test1000.h5", "COMP6v1/GDB10to13/gdb13_13_test1000.h5"],
}
METRICS = {
	"energy": {"panel": "a_energy_meV_per_atom", "unit": "meV/atom", "relative_tolerance": 0.05, "absolute_floor": 0.05, "location": "Fig. 4a, p. 7 (journal PDF)"},
	"force": {"panel": "b_force_eV_per_A", "unit": "eV/Å", "relative_tolerance": 0.05, "absolute_floor": 0.001, "location": "Fig. 4b, p. 7 (journal PDF)"},
}
# Text values on p. 5, ANI-MD only, with the interval implied by how they are written
TEXT_VALUES = {
	("M3GNet", "energy"): {"text": "above 14 meV atom-1", "check": "value > 14.0"},
	("M3GNet", "force"): {"text": "above ... 0.14 eV Å-1", "check": "value > 0.14 (the sentence says errors 'above 14 meV atom-1 and 0.14 eV Å-1' for M3GNet and M3GNet-TL)"},
	("TensorNet", "energy"): {"text": "11 meV atom-1", "check": "10.5 <= value < 11.5 (rounded to integer)"},
	("TensorNet", "force"): {"text": "0.1 eV Å-1", "check": "0.05 <= value < 0.15 (one significant figure)"},
	("SO3Net", "energy"): {"text": "2.3 meV atom-1", "check": "2.25 <= value < 2.35"},
	("SO3Net", "force"): {"text": "0.044 eV Å-1", "check": "0.0435 <= value < 0.0445"},
}

QUOTE_INTRO = "To further evaluate the extrapolation abilities of GNN models, we compare the energies and forces on the molecules obtained from COMP6 benchmarks with respect to DFT. Figure 4 shows the MAE of energies and forces computed with M3GNet, M3GNet-TL, TensorNet and SO3Net. (p. 5)"
QUOTE_CAPTION = "Fig. 4 | Mean absolute errors on COMP6 benchmark. The bar plot of a energy and b force errors for M3GNet, transfer-learning M3GNet (M3GNet-TL) from ANI-1xnr, TensorNet and SO3Net with respect to DFT. (p. 7)"
QUOTE_ANIMD_1 = "Both M3GNet and M3GNet-TL perform the worst in terms of energy and force errors above 14 meV atom-1 and 0.14 eV Å-1 on the ANI-MD dataset, which comprises molecular dynamics (MD) trajectories of 14 well-known drug molecules and 2 small proteins. (p. 5)"
QUOTE_ANIMD_2 = "The TensorNet significantly reduces the error of energies and forces to 11 meV atom-1 and 0.1 eV Å-1, while SO3Net further reduces to 2.3 meV atom-1 and 0.044 eV Å-1. This trend can be also found in other benchmark datasets. (p. 5)"

claims = []
for model_name in MODELS:
	for group in GROUPS:
		for metric_name, metric in METRICS.items():
			key = f"{model_name}|{group['label']}"
			raw_value = vector_values[metric["panel"]]["values"][key]
			paper_value = round(raw_value, 3)
			tolerance = max(metric["relative_tolerance"] * paper_value, metric["absolute_floor"])
			claim = {
				"id": f"{'E' if metric_name == 'energy' else 'F'}-{model_name}-{group['slug']}",
				"quantity": f"COMP6 {metric_name} MAE",
				"model": model_name,
				"group_label_in_figure": group["label"],
				"paper_value": paper_value,
				"unit": metric["unit"],
				"paper_value_source": "bar height read from the vector drawing of Fig. 4 in the journal PDF (see figure_reading)",
				"paper_value_raw_vector_reading": round(raw_value, 6),
				"arxiv_v1_raster_reading": round(raster_values[metric["panel"]]["values"][key], 4),
				"location": metric["location"],
				"tolerance": {
					"absolute": round(tolerance, 6),
					"interval": [round(paper_value - tolerance, 6), round(paper_value + tolerance, 6)],
					"rule": f"|ours - paper| <= max({metric['relative_tolerance']:.0%} of paper value, {metric['absolute_floor']} {metric['unit']})",
				},
				"conditions": {
					"model": f"{model_name}-ANI-1x-Subset-PES as released in matgl v1.3.0",
					"checkpoint": CHECKPOINTS[model_name],
					"code": "matgl==1.3.0 (tag v1.3.0, a6ebaebd6a0021e14d49d001103508c4980d94da), DGL backend",
					"test_set": f"COMP6 v1 @ isayev/COMP6 79f41c156f8e19506fe951b5513b98e7c534a503: {', '.join(group['files'])}",
					"samples": "all conformations of all molecules in the listed file(s), pooled; filters per definitions D-FILTER",
					"metric_definition": "D-EMAE" if metric_name == "energy" else "D-FMAE",
				},
			}
			if group["label"] == "ANI-MD":
				text = TEXT_VALUES[(model_name, metric_name)]
				claim["text_value_p5"] = text["text"]
				claim["text_check_secondary"] = text["check"]
				claim["quote"] = QUOTE_ANIMD_1 if model_name == "M3GNet" else QUOTE_ANIMD_2
			else:
				claim["quote"] = QUOTE_CAPTION
			claims.append(claim)
assert len(claims) == 36

definitions = [
	{
		"id": "D-TESTSET",
		"choice": "COMP6 v1, the 11 HDF5 files under COMP6v1/ of https://github.com/isayev/COMP6 at commit 79f41c156f8e19506fe951b5513b98e7c534a503, fetched from raw.githubusercontent.com. Expected byte sizes (GitHub tree API, saved in sources/comp6_tree.json) are listed in test_set_files; each download must match its size, and its sha256 is recorded at download.",
		"quote": "COMP6: https://github.com/isayev/COMP6 (Data availability)",
		"ambiguity": "The paper gives no commit, version or download date. The repository holds only COMP6v1 (no v2 directory) and these 11 files, so v1 at the pinned commit is the only candidate in the cited location.",
	},
	{
		"id": "D-GROUPS",
		"choice": "Primary grouping follows the COMP6 directories: ANI-MD = ani_md_bench.h5; 'GDB 9-11' = GDB07to09 (gdb11_07, gdb11_08, gdb11_09); 'GDB 12-13' = GDB10to13 (gdb11_10, gdb11_11, gdb13_12, gdb13_13); Drugbank = drugbank_testset.h5; S66x8 = s66x8_wb97x6-31gd.h5; Tripeptides = tripeptide_full.h5. Each of the 7 GDB files is also scored separately and reported.",
		"quote": "Figure x-axis labels: 'ANI-MD', 'GDB 9-11', 'GDB 12-13', 'Drugbank', 'S66x8', 'Tripeptides' (Fig. 4, p. 7)",
		"ambiguity": "COMP6 ships six benchmark subsets (ANI-MD, DrugBank, GDB07to09, GDB10to13, S66x8, Tripeptides) and the figure has six groups whose other four names match, so the two GDB labels are read as relabelled GDB07to09 and GDB10to13. The labels themselves do not match: a literal reading would take gdb11_09+gdb11_10+gdb11_11 as 'GDB 9-11' and gdb13_12+gdb13_13 as 'GDB 12-13', leaving gdb11_07 and gdb11_08 unused. That alternative (alternative_gdb_grouping) is computed and reported but does not enter the verdict. The choice was fixed from the repository layout and the figure labels, before any model ran.",
		"alternative_gdb_grouping": ALTERNATIVE_GDB_GROUPING,
	},
	{
		"id": "D-EMAE",
		"choice": "Energy MAE per group = mean over all conformations c in the group of |E_pred(c) - E_ref(c)| / N_atoms(c), in meV/atom. Conformations from several files in one group are pooled (each conformation weighs the same).",
		"quote": "'Energy (meV atom-1)' (Table 5 header, p. 7) and 'errors above 14 meV atom-1' (p. 5). The authors' training code computes the energy MAE on per-atom energies: e_mae = self.mae(valid_labels[0] / valid_num_atoms, valid_preds[0] / valid_num_atoms) (matgl v1.3.0 src/matgl/utils/training.py, saved in sources/repo_text/training.py).",
		"ambiguity": "The paper does not define the per-atom normalisation for COMP6. Alternatives reported as secondary only: (b) total-energy MAE divided by the mean atom count of the group; (c) sum|dE| / sum N; (d) for multi-file groups, unweighted mean of per-file MAEs. The primary choice copies the metric the same code uses for the ANI-1x numbers in Table 5.",
	},
	{
		"id": "D-FMAE",
		"choice": "Force MAE per group = mean of |F_pred - F_ref| over every Cartesian component of every atom of every conformation in the group (pooled), in eV/Å.",
		"quote": "'Force (eV Å-1)' (Table 5 header). The authors' training code: f_mae = self.mae(valid_labels[1], valid_preds[1]) with torchmetrics.MeanAbsoluteError over the stacked per-atom force components (training.py, v1.3.0).",
		"ambiguity": "Not defined for COMP6 in the paper. Secondary alternatives: (b) mean over conformations of the per-conformation component MAE; (c) mean per-atom force-vector error norm |dF|; (d) unweighted mean of per-file MAEs for multi-file groups. Reported, not used for the verdict.",
	},
	{
		"id": "D-UNITS",
		"choice": "COMP6 'energies' are total energies in Hartree and 'forces' are in Hartree/Å; convert with 1 Ha = 27.211386245988 eV (CODATA 2018). 'coordinates' in Å. Before the batch, a format check on two molecules (first molecule of s66x8 and of ani_md_bench) fits the slope of predicted vs reference force components for one model: slope near +1 keeps the sign, near -1 flips it, near 1.89 or 0.53 indicates Ha/Bohr and is converted. This check only fixes the file format and is logged; it never selects among metric definitions.",
		"quote": "No unit statement for COMP6 in the paper; COMP6 README: 'Units: kcal/mol and kcal/mol/A (errors are NOT per atom)' refers to its own error table, not the stored data. The file format is described in Smith et al., Sci. Data 4, 170193 (2017), linked from the COMP6 README.",
		"ambiguity": "Hartree and Hartree/Å come from the ANI data format and the triage notes, not from the MatGL paper; hence the pre-batch format check. Differences between CODATA Hartree values (about 1e-8 relative) are negligible.",
	},
	{
		"id": "D-EREF",
		"choice": "Compare absolute total energies: E_pred is the Potential output in eV, which already includes the fitted element_refs stored in model.json (H -16.51807976, C -1036.37304688, N -1488.65246582, O -2046.00830078 eV), against E_ref = COMP6 total DFT energy in eV. No extra per-element shift, no relative-energy (conformer-minus-minimum) metric.",
		"quote": "'we compare the energies and forces on the molecules obtained from COMP6 benchmarks with respect to DFT' (p. 5). Both ANI-1x (training) and COMP6 use the same level of theory: 'All energies and forces of conformers are calculated using DFT at wB97x/6-31G level' (Dataset details, about ANI-1x); the COMP6 S66x8 file is named s66x8_wb97x6-31gd.h5.",
		"ambiguity": "The paper does not say whether COMP6 energies were compared as absolute or relative energies. COMP6 itself also reports a 'Relative Energy' metric. Absolute per-atom energy matches the meV/atom unit and the Table 5 metric; relative-energy MAE is not computed for the verdict.",
	},
	{
		"id": "D-SCORING",
		"choice": "Single-point energies and forces at the stored geometries, no relaxation and no MD. Forces are the model's -dE/dr (Potential with calc_forces=True, calc_stresses=False). Molecules are non-periodic; graphs are built by matgl's own converters with the model's cutoff (5.0 Å; M3GNet three-body cutoff 4.0 Å as in model.json). float32 as in model.json. Primary inference path: matgl.ext.ase.PESCalculator per conformation, or a batched Potential call over Molecule2Graph graphs if it agrees with PESCalculator on a sample of at least 50 conformations per file to within 1e-4 eV per structure and 1e-4 eV/Å per component.",
		"quote": "Code availability: 'All implementations are available in MatGL'. No COMP6 evaluation script is published (none in the v1.3.0 tree, sources/matgl_v130_tree.json).",
		"ambiguity": "The authors' evaluation script is not public, so the inference path is ours. GPU float32 non-determinism is far below the tolerances.",
	},
	{
		"id": "D-CODE",
		"choice": "matgl 1.3.0 (tag v1.3.0) with its DGL backend; weights loaded from the local v1.3.0 checkout paths, model.json taken from the tag (not from Hugging Face). M3GNet runs with the v1.3.0 three-body code, i.e. before PR #840.",
		"quote": "'The pretrained models will be provided in the latest released version of MatGL.' (Code availability)",
		"ambiguity": "The paper does not name the matgl version that produced Fig. 4. v1.3.0 is the tag that ships these checkpoints with DGL support. PR #840 (2026-09-26) changed M3GNet three-body behaviour when threebody_cutoff < cutoff; running matgl 4.x on M3GNet is an optional side note outside the verdict.",
	},
	{
		"id": "D-CHECKPOINT",
		"choice": "The three ANI-1x-Subset-PES checkpoints in pretrained_models/ at tag v1.3.0 (sizes in each claim). Their sha256 is recorded at download and compared with the Hugging Face copies (materialyze/*-PES-ANI-1x-Subset).",
		"quote": "Table 5 (p. 7): M3GNet 4.565/4.592/3.746 meV atom-1, 0.092/0.093/0.085 eV Å-1; SO3Net 2.281/2.286/1.596, 0.046/0.046/0.035. The v1.3.0 model cards of M3GNet and SO3Net repeat these exact numbers (sources/repo_text/*-README.md).",
		"ambiguity": "Nothing in the paper ties Fig. 4 to a checkpoint hash. The model cards matching Table 5 suggest the released weights are the paper's models. TensorNet has no model card at the tag. The SO3Net card calls itself 'a M3GNet potential' (copy error in the card). The card split 991,735/248,355/248,355 does not match the text ratio 0.2/0.05/0.05; note only. SI Table S5 lists num_rbf 32 for TensorNet while the released model.json has num_rbf 3; we use the released json and note the difference.",
	},
	{
		"id": "D-FILTER",
		"choice": "Use every conformation. Exclude only conformations with an element outside {H, C, N, O} or a non-finite reference energy or force; count and report exclusions (expected: none). No outlier removal, no size cut, no energy window.",
		"quote": "'ANI-1x ... a subset ... containing H, C, N, and O' (p. 5) and model.json element_types ['H', 'C', 'N', 'O'].",
		"ambiguity": "The paper states no filter for COMP6. COMP6 v1 is reported to contain only C, H, N, O.",
	},
	{
		"id": "D-READING",
		"choice": "Paper values are the Fig. 4 bar heights taken from the vector drawing in the journal PDF (page 7), calibrated on the y tick marks, rounded to 3 decimals. The ANI-MD text values on p. 5 are recorded and checked as a secondary consistency test.",
		"quote": QUOTE_CAPTION,
		"ambiguity": "Fig. 4 is vector graphics in the journal PDF, so bar tops are known to about 0.001 pt, i.e. +/-0.0002 meV/atom and +/-0.000002 eV/Å; all 24 force bars sit within 1e-5 of a 3-decimal value and all energy bars within 2e-4 of one, so the plotted data look like 3-decimal numbers. The arXiv v1 raster (150 ppi) agrees with every bar to within one pixel (max 0.07 meV/atom, 0.0006 eV/Å). The text values agree with the figure (TensorNet 11.099 vs '11', 0.099 vs '0.1'; SO3Net 2.283 vs '2.3', 0.044 vs '0.044'; M3GNet 19.159 > 14, 0.142 > 0.14).",
	},
	{
		"id": "D-PERITEM",
		"choice": "No per-item results from the authors exist to download (no source data file, no per-molecule table, no evaluation script); sources/ holds only the paper, SI, preprint, figure readings and repository metadata.",
		"quote": "Only Fig. 4 and the p. 5 text report COMP6 results.",
		"ambiguity": "Tolerances therefore cannot be set from a bootstrap of the authors' per-item values; see tolerance_policy.",
	},
]

test_set_tree = json.loads((SOURCES / "comp6_tree.json").read_text())
test_set_files = {entry["path"]: entry["size"] for entry in test_set_tree["tree"] if entry["path"].endswith(".h5")}
assert len(test_set_files) == 11

document = {
	"stage": "pre-registration",
	"created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
	"paper": {
		"title": "Materials Graph Library (MatGL), an open-source graph deep learning library for materials science and chemistry",
		"authors": "Ko, Deng, Nassar et al.",
		"venue": "npj Computational Materials 11, 253 (2025)",
		"doi": "10.1038/s41524-025-01742-y",
		"preprint": "arXiv 2503.03837 v1",
		"code": "https://github.com/materialyzeai/matgl @ v1.3.0 (a6ebaebd6a0021e14d49d001103508c4980d94da)",
		"data": "https://github.com/isayev/COMP6 @ 79f41c156f8e19506fe951b5513b98e7c534a503",
	},
	"target": "Fig. 4a (energy MAE, meV/atom) and Fig. 4b (force MAE, eV/Å) on COMP6 v1 for the three released ANI-1x-Subset potentials (M3GNet, TensorNet, SO3Net) across the 6 plotted groups: 36 numbers.",
	"source_files_sha256": {str(path.relative_to(ROOT)).replace("\\", "/"): sha256_of(path) for path in [
		SOURCES / "paper.pdf", SOURCES / "SI.pdf", SOURCES / "arxiv.pdf", SOURCES / "fig4_values.json",
		SOURCES / "read_fig4.py", SOURCES / "comp6_tree.json", SOURCES / "matgl_v130_tree.json",
		SOURCES / "repo_text" / "training.py", SOURCES / "repo_text" / "COMP6_README.md",
		SOURCES / "repo_text" / "M3GNet-model.json", SOURCES / "repo_text" / "SO3Net-model.json", SOURCES / "repo_text" / "TensorNet-model.json",
		SOURCES / "repo_text" / "M3GNet-README.md", SOURCES / "repo_text" / "SO3Net-README.md",
	]},
	"test_set_files_expected_bytes": test_set_files,
	"figure_reading": {
		"method": "sources/read_fig4.py: PyMuPDF get_drawings() on page 7 of the journal PDF; bars identified by fill colour and x slot, heights converted with a linear fit to the y tick marks (max fit residual 0.00015 meV/atom and 0.000001 eV/Å). Cross-check: column scan of the embedded raster in arXiv v1 p. 17 (sources/fig4/arxiv_p17-000.png).",
		"precision": "vector: about +/-0.0002 meV/atom and +/-0.000002 eV/Å; values reported rounded to 0.001. raster cross-check: one pixel = 0.076 meV/atom and 0.00057 eV/Å.",
	},
	"tolerance_policy": {
		"rule": "A claim matches when |ours - paper| <= max(5% of the paper value, floor); floor = 0.05 meV/atom for energy and 0.001 eV/Å for force (one unit of the figure's 3rd decimal for force).",
		"basis": "Inference with released weights is deterministic, so seed spread does not apply and the paper gives no error bars. The authors themselves state these results to two significant figures in the text (11, 2.3, 0.044, 0.14), which is a 2% to 5% resolution; 5% is the coarse end of that. Numerical noise from float32/GPU or library versions is expected below 0.1%. The floors keep the smallest bars (about 1 meV/atom, 0.011 eV/Å) from getting a tolerance below the figure's own resolution. Definition alternatives are not absorbed into the tolerance: they are pre-registered in definitions and reported separately.",
		"grades": {"match": "within tolerance", "close": "outside tolerance but within 3x tolerance (about 15%)", "mismatch": "beyond 3x tolerance"},
	},
	"verdict_rule": {
		"Reproduced": "all 36 claims match under the primary definitions",
		"Partially reproduced": "at least 18 of 36 match, or all 36 are match or close",
		"Not reproduced": "fewer than 18 match and at least one mismatch",
		"Could not run": "models or data cannot be run on matgl 1.3.0 after 3 fix attempts for the same failure",
		"secondary_reported_not_verdict": ["p. 5 text checks for ANI-MD", "alternative GDB grouping", "per-file GDB values", "alternative energy and force averaging", "optional matgl 4.x M3GNet run"],
	},
	"definitions": definitions,
	"claims": claims,
	"out_of_scope": [
		"M3GNet-TL bars (weights not released)",
		"Table 5 ANI-1x train/val/test MAE (random split, no ids or seed published)",
		"Qualitative sentence 'This trend can be also found in other benchmark datasets' (p. 5)",
	],
	"observations_from_paper_only": [
		"The p. 5 trend sentence is not true for every group in the authors' own figure: on GDB 9-11 TensorNet energy (1.705) is below SO3Net (3.889); on S66x8 TensorNet force (0.045) is above M3GNet (0.029).",
		"SO3Net force bars for ANI-MD, GDB 12-13 and Drugbank are all exactly 0.044 eV/Å; M3GNet and TensorNet Tripeptides force bars are both 0.067. Possibly coincidence; worth a look when our numbers exist.",
		"The preprint text says 'Table 4 shows the MAE ... COMP6' where the journal says 'Figure 4'; the figure itself is unchanged between versions (raster vs vector agree within one pixel).",
		"The text calls the ANI-MD molecules 312 atoms; ANI-MD has 16 systems of different sizes, so 312 is presumably the largest.",
	],
}

output_path = ROOT / "claims.json"
output_path.write_text(json.dumps(document, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print(output_path, len(claims), "claims")
