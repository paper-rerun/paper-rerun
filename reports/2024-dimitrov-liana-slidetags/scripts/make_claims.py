# Build claims.json from the authors' Source Data Fig. 4 plus the definitions read from paper, SI and notebook
import sys, json, csv, hashlib
sys.stdout.reconfigure(encoding='utf-8')
root = sys.argv[1]
medians = json.load(open(f'{root}/sources/fig4_source_medians.json', encoding='utf-8'))['medians']
tsv_path = f'{root}/sources/fig4_source_data.tsv'
tsv_sha = hashlib.sha256(open(tsv_path, 'rb').read()).hexdigest()
xlsx_sha = hashlib.sha256(open(f'{root}/sources/MOESM7_ESM.xlsx', 'rb').read()).hexdigest()
rows = list(csv.DictReader(open(tsv_path, encoding='utf-8'), delimiter='\t'))

SRC = 'Source Data Fig. 4 (41556_2024_1469_MOESM7_ESM.xlsx, 75 rows, md5 b4930a6023835e2aab51add8d7d790df)'
TOL_NARROW = 0.005
TOL_WIDE = 0.025
TOL_EXACT = 0.0005
tol_basis_narrow = ('Pass tolerance |ours - paper| <= 0.005, i.e. 2.5% of the plotted range of the panel (Fig. 4a,b y-axis 0.40-0.60, tick labels at 2 decimals). '
	'Exact tier |diff| <= 0.0005 is also reported: layer A is deterministic in principle (pinned liana 1.0.5, seed 1337 in lr_bivar, numpy default_rng(42) in the baseline), '
	'so a miss of the exact tier is itself informative. The paper gives no SD for these medians (n = 5 datasets).')
tol_basis_wide = ('Pass tolerance |ours - paper| <= 0.025, i.e. 2.5% of the plotted range of the panel (Fig. 4c,d y-axis 0-1, tick labels at 2 decimals); same rule as AUROC/BA. '
	'Exact tier |diff| <= 0.0005 also reported. The paper gives no SD (n = 5 datasets).')

panels = {
	'AUROC': ('A', 'Fig. 4a (AUROC per scoring function)', 'per score', TOL_NARROW, tol_basis_narrow),
	'Balanced Accuracy': ('B', 'Fig. 4b (balanced accuracy per method)', 'per method', TOL_NARROW, tol_basis_narrow),
	'F1* (normalised)': ('S', 'Fig. 4c (normalised F1* per scoring function, top-5% cap)', 'per score', TOL_WIDE, tol_basis_wide),
	'F1 (normalised)': ('F', "Fig. 4d (normalised F1 per method, authors' filters)", 'per method', TOL_WIDE, tol_basis_wide),
}
claims = []
for metric, (prefix, location, level, tol, basis) in panels.items():
	for i, (item, value, n) in enumerate(medians[metric], start=1):
		claims.append({
			'id': f'{prefix}{i:02d}',
			'tier': 'primary',
			'quantity': f'median {metric} across the 5 Slide-tags datasets, {level}: {item}',
			'method': item.split(' | ')[0],
			'score': item.split(' | ')[1] if ' | ' in item else None,
			'paper_value': value,
			'paper_value_4dp': round(value, 4),
			'paper_rank_in_panel': i,
			'unit': 'dimensionless (0-1)' if metric in ('AUROC', 'Balanced Accuracy') else 'dimensionless ratio (0.5 = random)',
			'location': f'{location}; value = median of the {n} per-dataset rows in {SRC} (the cyan median line of each box). The figure prints no numbers.',
			'tolerance': tol,
			'tolerance_exact_tier': TOL_EXACT,
			'tolerance_basis': basis,
			'conditions': 'see conditions_common; main reading R0 (code), layer A',
		})
	order = [item for item, value, n in medians[metric]]
	claims.append({
		'id': f'O{prefix}',
		'tier': 'primary',
		'quantity': f'ordering of the {len(order)} medians in {location}',
		'paper_value': order,
		'unit': 'ordered list, descending median',
		'location': f'{location}; boxes "ordered according to the median performance across datasets" (Fig. 4 legend); order taken from {SRC}',
		'tolerance': f'every pair whose paper medians differ by more than 2 x {tol} keeps its order; pairs closer than that count as ties. Kendall tau-b against the paper order is reported as description.',
		'tolerance_basis': 'Two medians that each move within the per-value tolerance can swap only if their paper gap is below twice the tolerance; such swaps are not counted as failures.',
		'conditions': 'see conditions_common; main reading R0 (code), layer A',
	})

per_row_metrics = ['AUROC', 'Balanced Accuracy', 'Precision', 'Recall', 'F1', 'F1*', 'F1 (normalised)', 'F1* (normalised)', 'Positive Calls']
claims.append({
	'id': 'R75',
	'tier': 'secondary',
	'quantity': 'the 75 per-dataset rows (5 datasets x 15 scores) of Source Data Fig. 4, columns ' + ', '.join(per_row_metrics),
	'paper_value': [{k: (float(r[k]) if k in per_row_metrics else r[k]) for k in r} for r in rows],
	'unit': 'dimensionless',
	'location': f'{SRC}; TSV copy sources/fig4_source_data.tsv sha256 {tsv_sha}; xlsx sha256 {xlsx_sha}',
	'tolerance': TOL_EXACT,
	'tolerance_basis': 'Per-row agreement is checked at the exact tier (0.0005, 4 decimals) because layer A should be deterministic; we report the count of rows/cells within 0.0005, within the panel tolerance (0.005 AUROC/BA, 0.025 F1n/F1*n) and outside. Per-row results are reported before medians (triage note 10).',
	'conditions': 'see conditions_common; main reading R0 (code), layer A',
})

auroc = dict((k, v) for k, v, n in medians['AUROC'])
fstar = dict((k, v) for k, v, n in medians['F1* (normalised)'])
pairs = [('CellPhoneDB', 'lr_means', 'cellphone_pvals'), ('Connectome', 'Product*', 'scaled_weight'), ('CellChat', 'lr_probs', 'cellchat_pvals'),
	('NATMI', 'Product✳', 'spec_weight'), ('Rank_Aggregate', 'magnitude_rank', 'specificity_rank'), ('Geometric Mean', 'lr_gmeans', 'gmean_pvals')]
claims += [
	{
		'id': 'Q1', 'tier': 'secondary',
		'quantity': 'number of the 15 scoring functions whose median AUROC is above 0.5',
		'paper_value': sum(v > 0.5 for v in auroc.values()), 'paper_max_median_auroc': max(auroc.values()),
		'paper_quote': 'SI Note 5: "the individual scoring functions of most methods performed marginally better than random (AUROC > 0.5), with the inter-dataset variance being too high to suggest which method works best (Fig. 4A)." Main text: "We found weak associations between ligand-receptor interactions predicted in a spatially agnostic manner and the co-localization of their ligands, receptors and cell types".',
		'unit': 'count (of 15)', 'location': 'Supplementary Information, Supplementary Note 5; main text section "Ligand-receptor inference weakly reflects co-localization"; count taken from ' + SRC,
		'tolerance': 'reproduced if at least 8 of 15 medians are > 0.5 ("most") and no median exceeds 0.60 ("marginally")',
		'tolerance_basis': 'Translation of the qualitative wording; the paper itself has 9/15 above 0.5 and max 0.5427.',
		'conditions': 'main reading R0, layer A',
	},
	{
		'id': 'Q2', 'tier': 'secondary',
		'quantity': 'largest |median balanced accuracy - 0.5| over the 9 methods',
		'paper_value': max(abs(v - 0.5) for k, v, n in medians['Balanced Accuracy']),
		'paper_quote': 'SI Note 5: "We again saw that the methods\' performances were closely aligned with random (Fig. 4B)."',
		'unit': 'dimensionless', 'location': 'Supplementary Note 5; value from ' + SRC,
		'tolerance': 'reproduced if every method median balanced accuracy lies within 0.5 +/- 0.03',
		'tolerance_basis': 'Paper maximum deviation is 0.0157; 0.03 is about twice that, still "closely aligned with random" on the 0.40-0.60 axis of Fig. 4b.',
		'conditions': 'main reading R0, layer A',
	},
	{
		'id': 'Q3', 'tier': 'secondary',
		'quantity': 'within-method comparison magnitude score vs specificity score, for the 6 methods that have both, in median AUROC and in median normalised F1*',
		'paper_value': {
			'AUROC_magnitude_wins': sum(auroc[f'{m} | {a}'] > auroc[f'{m} | {b}'] for m, a, b in pairs),
			'F1star_norm_magnitude_wins': sum(fstar[f'{m} | {a}'] > fstar[f'{m} | {b}'] for m, a, b in pairs),
			'pairs': [{'method': m, 'magnitude': a, 'specificity': b, 'AUROC': [auroc[f'{m} | {a}'], auroc[f'{m} | {b}']], 'F1*n': [fstar[f'{m} | {a}'], fstar[f'{m} | {b}']]} for m, a, b in pairs],
		},
		'paper_quote': 'SI Note 5: "scoring functions that focus on the magnitude of interactions (e.g. LIANA\'s magnitude rank and ligand-receptor means or products), provide superior performance than functions that reflect interaction specificity across cell type pairs (Fig. 4A&C)." Notebook cell 26: "magnitude scores per method ... performed better than specificity".',
		'unit': 'count (of 6) per metric', 'location': 'Supplementary Note 5; magnitude/specificity labels from notebook cell 21 (dark red labels) and Fig. 4 legend; values from ' + SRC,
		'tolerance': 'reproduced if magnitude beats specificity in at least 5 of 6 pairs for both AUROC and F1*n',
		'tolerance_basis': 'Paper has 6/6 for both; the CellChat AUROC pair differs by only 0.0008 in the paper, so one flip is allowed.',
		'conditions': 'main reading R0, layer A',
	},
	{
		'id': 'Q4', 'tier': 'secondary',
		'quantity': "Spearman's rho between F1 and the share of interactions called positive ('Positive Calls'), over the 75 rows",
		'paper_value': 0.765,
		'paper_quote': 'SI Note 5: "we computed F1 scores, but saw a notable correlation with the number of interactions retained by each method (Spearman\'s rho = 0.765)."',
		'unit': 'dimensionless', 'location': 'Supplementary Note 5',
		'tolerance': 0.02,
		'tolerance_basis': "Two-decimal claim; 0.02 lets ordinary rounding and small truth flips pass. Internal inconsistency recorded before any run: the authors' own Source Data Fig. 4 gives rho = 0.7456 (average-rank Spearman over the 75 published rows, stdlib) and the notebook output (cell 23) prints \"F1: 0.746\". So the SI number is not supported by the published rows. We compare ours with both 0.765 (SI text) and 0.7456 (source data); the verdict for Q4 uses the SI value.",
		'conditions': 'main reading R0, layer A; Spearman over all 75 rows as in notebook cell 23',
	},
]

definitions = [
	{'id': 'D01', 'name': 'input data',
	 'choice': 'Start from the processed figshare files (10.6084/m9.figshare.26131789.v1, slidetags.tar.xz, md5 65bb74092f73ab7f7f061390a6e35030): SCP2167.h5ad (humancortex), SCP2169.h5ad (HumanTonsil), SCP2170.h5ad (mouseembryo), SCP2171.h5ad (HumanMelanomaRNA), SCP2176.h5ad (HumanMelanomaMultiome). These are the adata.h5ad written by notebook cell 8 (filtered, normalised, with the 9 method results in .uns).',
	 'quote': 'Methods: "we used five processed and recently published spatially informed single nucleus RNA sequencing (slide-tags) datasets41."',
	 'ambiguity': 'The raw Single Cell Portal data need a login (401), so the preprocessing in cell 8 (barcode match to the spatial table, filter_cells min_genes=200, filter_genes min_cells=3, normalize_total 1e4 + log1p) is NOT re-checked. SCP2162 (mouse hippocampus) is excluded in the notebook ("barcodes between metadata and matrix do not match"); the paper says five datasets, consistent. The run must confirm with anndata that .X is log-normalised, layers["raw"] holds counts, obsm["spatial"] exists and .uns has the 9 method keys.'},
	{'id': 'D02', 'name': 'evaluation layers',
	 'choice': "Layer A (primary): authors' method outputs adata.uns[<method>] as published + Moran truth recomputed by us + authors' evaluation code (notebook cells 12-13, utils.py). Layer B (secondary, only if the light-mode budget allows): re-run the 9 methods from .X with the cell 8 settings, compare the new .uns with the published one, then repeat A.",
	 'quote': 'Methods: "Then we ran all ligand-receptor methods in LIANA+ without taking spatial information into account."',
	 'ambiguity': "The authors ran cell 8 with n_jobs=10; light mode caps us at 4 processes/threads, so layer B uses n_jobs=4. Whether n_jobs changes the permutation stream in liana 1.0.5 is not known before the run; any .uns difference is reported, not tuned away."},
	{'id': 'D03', 'name': 'software versions',
	 'choice': 'Python 3.10.13, liana==1.0.5 (wheel md5 933caee33e70e4760d07ee722b5e5679), decoupler==1.6.0, scanpy==1.10.1, anndata==0.10.7, numpy==1.23.4, pandas==1.5.3, scikit-learn==1.4.2, numba==0.59.1, omnipath==1.0.7, matplotlib==3.8.3, seaborn==0.13.2 (lianaplus_manuscript environments/env.yml, env "spiana"; torch not needed). Resource "consensus" (human) / "mouseconsensus" (mouse), bundled in the wheel.',
	 'quote': 'Code availability: "We used LIANA+ v1.0.5 release for the analyses presented here." Notebook cell 2 prints li.__version__ = \'1.0.5\'.',
	 'ambiguity': 'env.yml is the full lab env; the notebook kernel name "spiana" matches it (python 3.10.13). spiana.yml in the same folder (python 3.10.10, decoupler 1.5.1) is the laptop env and is not used. An optional liana 2.0.0 run is only a robustness note, never the main reading.'},
	{'id': 'D04', 'name': 'spatial weights for the truth',
	 'choice': 'li.ut.spatial_neighbors(adata, bandwidth=150, cutoff=0.1, set_diag=True), default kernel "gaussian" w = exp(-d^2 / (2 l^2)), coordinates obsm["spatial"].',
	 'quote': 'Methods: "Throughout the manuscript, unless otherwise specified, we used Gaussian weights with a bandwidth of 150 and a cut-off of 0.1, and the diagonal (self to self) was set to 1 for the local scores."',
	 'ambiguity': 'None between text and code. Coordinate units are whatever the SCP spatial table had (not re-checked, see D01).'},
	{'id': 'D05', 'name': 'ligand-receptor co-localisation (lrdata)',
	 'choice': "li.mt.lr_bivar(adata, function_name=\"morans\", use_raw=False, n_perms=1000, expr_prop=0.05, mask_negatives=True, resource_name=consensus|mouseconsensus, seed default 1337). Uses global Moran's R (lrdata.var[\"morans_r\"]) and its one-sided permutation p-value (lrdata.var[\"morans_pvals\"], one-sided because mask_negatives=True).",
	 'quote': "Methods: \"we estimated global Moran's R using LIANA+ to generate an indirect ground truth-that is, ligand-receptors and cell types co-localized to a greater extend than random (Moran's R >0 and FDR <0.05).\"",
	 'ambiguity': 'Methods (bivariate metrics) says interactions not expressed in at least 10% of spots are excluded "by default"; the notebook overrides with expr_prop=0.05. Follow the notebook. The truth files (lrdata/cpdata) were not published, so they are recomputed; there is no published per-item truth to check them against.'},
	{'id': 'D06', 'name': 'cell-type co-localisation (cpdata)',
	 'choice': 'ctdata = utils.onehot_groupby(adata, "cell_type") (one-hot float32, obsm/obsp copied); li.mt.lr_bivar(ctdata, function_name="morans", use_raw=False, expr_prop=0, n_perms=1000, mask_negatives=True, interactions=all ordered pairs of cell types). Self pairs (autocrine) are removed by liana ("Removing 7 self-interactions" in the authors\' output for humancortex), so autocrine cell-type pairs drop out of the evaluation through the inner join.',
	 'quote': 'Notebook cell 10: "# Run CP; NOTE: I\'m currently discarding autocrine, and only evaluating para/ortho".',
	 'ambiguity': 'The paper text does not say autocrine pairs are excluded; the code does. Follow the code.'},
	{'id': 'D07', 'name': 'truth threshold (MAIN READING R0 = code)',
	 'choice': 'Exactly utils.join_pred_truth: lr_truth = (p_adjust_fdr(morans_pvals <= 0.05)) * (morans_r > 0); same for ct_truth; truth = lr_truth * ct_truth. Note the parenthesis: p_adjust_fdr receives the BOOLEAN (pvals <= 0.05), not the p-values. With decoupler 1.6.0 p_adjust_fdr (BH via np.asfarray, cumulative minimum, capped at 1) a 0/1 input comes back unchanged, so the code truth is (raw permutation p <= 0.05) AND (R > 0), with no FDR correction.',
	 'quote': "Methods: \"(Moran's R >0 and FDR <0.05)\". utils.py: lr_truth['lr_truth'] = ((p_adjust_fdr((lr_truth['morans_pvals']) <= 0.05)) * (lr_truth['morans_r'] > 0)).astype(np.int8)",
	 'ambiguity': 'Text says FDR < 0.05; the code effectively uses unadjusted p <= 0.05. This text/code difference was NOT in the triage list (triage wrote "verdade = FDR(p) <= 0.05"); found here by reading utils.py and decoupler-py 1.6.0 decoupler/utils.py p_adjust_fdr. The main reading follows the code (it produced the Source Data). Alternative reading V4 applies BH-FDR to the p-values (p_adjust_fdr(morans_pvals) < 0.05).'},
	{'id': 'D08', 'name': 'joining predictions and truth',
	 'choice': 'Inner join of adata.uns[method] on (ligand_complex, receptor_complex) = lrdata.var (ligand, receptor), then on (source, target) = cpdata.var (ligand, receptor) renamed to source/target. Only rows present in both truths are evaluated.',
	 'quote': 'utils.join_pred_truth (how="inner").',
	 'ambiguity': 'Not described in the paper text. Follow the code.'},
	{'id': 'D09', 'name': 'AUROC per scoring function',
	 'choice': 'For each method, score keys = li.mt.show_methods() "Magnitude Score" and "Specificity Score" (None dropped). gt = li.method.process_scores(gt, score_key) (scores where lower is better, e.g. p-values and ranks, become -log10(x + eps)); AUROC = sklearn roc_auc_score(truth, score) over the whole joined table.',
	 'quote': 'Methods: "AUROC was calculated for the whole distribution of each ligand-receptor method\'s scoring functions."',
	 'ambiguity': 'Score labels: expr_prod is renamed "Product*" for Connectome and "Product✳" for NATMI (notebook cell 18). The AUROC of Product*, Product✳, lr_gmeans and lrscore is expected to be (near-)identical per dataset because they are monotone transforms of the same product; the source-data medians agree to 7 decimals (0.5292327).'},
	{'id': 'D10', 'name': 'false-positive filters (MAIN READING R0 = code, notebook cell 12)',
	 'choice': 'CellPhoneDB: cellphone_pvals < 0.05. Connectome: ligand_pvals < 0.05 & receptor_pvals < 0.05 & scaled_weight > 0. log2FC: ligand_pvals < 0.05 & receptor_pvals < 0.05 & lr_logfc > 0. NATMI: spec_weight > quantile(gt.spec_weight, 0.95). SingleCellSignalR: lrscore > 0.6. Rank_Aggregate: magnitude_rank < 0.05 & specificity_rank < 0.05. Geometric Mean: gmean_pvals < 0.05. scSeqComm: inter_score > 0.95. CellChat: cellchat_pvals < 0.05 & (ligand_pvals < 0.05 | receptor_pvals < 0.05). Applied to the joined table gt before process_scores.',
	 'quote': 'Methods: "For CellPhoneDB, CellChat and Geometric mean, interactions with P values below 0.05 were filtered. ... For LIANA\'s rank aggregate, we kept only those with a magnitude rank <0.05. Since the authors of NATMI and scSeqComm do not suggest a threshold, we kept interactions if they were within the top 5% of the specificity weight and interscore distributions, respectively."',
	 'ambiguity': 'Two text/code differences, run as alternative readings: V2 Rank_Aggregate with magnitude_rank < 0.05 only (text); V3 scSeqComm top 5% = inter_score > quantile(gt.inter_score, 0.95) (text, same form as the NATMI filter) instead of the absolute cut 0.95. Neither is decided from numbers; the Source Data rows were produced by the code, which is why the code is the main reading.'},
	{'id': 'D11', 'name': 'balanced accuracy, precision, recall, positive calls',
	 'choice': 'On the binary filter of D10: sklearn balanced_accuracy_score(truth, binary, adjusted=False), precision_score, recall_score; Positive Calls = binary.sum() / number of rows of gt. One value per method per dataset (repeated on both score rows of a method in the Source Data).',
	 'quote': 'Methods: "Balanced accuracy = 1/2 (TP/(TP+FN) + TN/(TN+FP))".',
	 'ambiguity': 'For Fig. 4b,d the per-method median is taken over the 5 datasets with one value per dataset; the duplicated rows give the same median, as the notebook groupby("Method").median() does. Checked in the Source Data: both score rows of a method carry identical BA/F1n values.'},
	{'id': 'D12', 'name': 'normalised F1 (per method, Fig. 4d) and its random baseline (MAIN READING R0 = code)',
	 'choice': 'F1 = sklearn f1_score(truth, binary, average="binary"); baseline = utils.generate_random_baseline: rng = np.random.default_rng(seed=42), 1000 successive permutations of the binary column (each permutes the already-permuted vector), mean F1 over them; F1 (normalised) = (F1 / baseline) / 2. A new rng with seed 42 is created on every call.',
	 'quote': 'Methods: "Normalized F1 = 1/2 (F1observed / F1permuted) where \'observed\' is the F1 score for the actual ligand-receptor predictions, while the \'permuted\' F1 was generated by shuffling the predictions of each method (100 times) and calculating an F1 score."',
	 'ambiguity': 'Text says 100 shuffles, code uses n_perms=1000. Main reading = code; alternative V1 = 100 permutations (same seed 42, same procedure). The Fig. 4 legend says normalised F1 "is bound between negative and positive infinity" while the formula is >= 0; text-only issue, no effect on numbers.'},
	{'id': 'D13', 'name': 'normalised F1* (per score, Fig. 4c)',
	 'choice': 'After process_scores: cap = (score >= np.quantile(score, 0.95)); F1* = f1_score(truth, cap); baseline as D12 on the cap column (1000 permutations, seed 42); F1* (normalised) = (F1* / baseline) / 2.',
	 'quote': 'Methods: "Similarly, when evaluating the individual scoring functions from each method, we considered only the top 5% as positive predictions."',
	 'ambiguity': 'With ties at the 95th quantile more than 5% can be positive (notebook comment: "not really possible due to ties"); follow the code (>=). The 100-vs-1000 permutation variant V1 also applies here.'},
	{'id': 'D14', 'name': 'aggregation and ordering',
	 'choice': 'Per-score (AUROC, F1*n) or per-method (BA, F1n) median over the 5 datasets (plain median of 5 values); order = descending median, as the figure orders boxes by groupby(x).median().',
	 'quote': 'Fig. 4 legend: "The boxes were ordered according to the median performance across datasets (central line in cyan within each box; n = 5 datasets)."',
	 'ambiguity': 'With 5 datasets a change in one dataset row can move a median directly, so per-row results (R75) are reported before medians.'},
	{'id': 'D15', 'name': 'randomness and determinism',
	 'choice': 'liana 1.0.5 default seed 1337 (liana/_constants.py DefaultValues.seed) for the Moran permutations; seed 42 for the F1 baselines. No seed is changed. Light mode: nice -n 19, OMP/MKL/OPENBLAS/NUMEXPR threads = 4, at most 4 processes, CPU only.',
	 'quote': 'Not in the paper; from the liana 1.0.5 source and utils.py.',
	 'ambiguity': 'Permutation p-values (1000 permutations) near the 0.05 cut can flip if the random stream differs (numpy/numba version, thread count); that moves truth labels and AUROC at the 3rd decimal. Since no truth was published, if layer A misses the exact tier we report how many LR pairs and cell-type pairs have p within 0.005 of the cut, instead of guessing which labels differ.'},
]

variants = [
	{'id': 'R0', 'name': 'main reading (code)', 'definitions': 'D01-D15 as written', 'role': 'used for every verdict'},
	{'id': 'V1', 'name': 'baseline with 100 permutations (text)', 'changes': 'n_perms=100 in generate_random_baseline (seed 42)', 'affects': 'F1n (F*), F1*n (S*), their orderings'},
	{'id': 'V2', 'name': 'Rank_Aggregate filter magnitude_rank < 0.05 only (text)', 'affects': 'B and F claims for Rank_Aggregate and the OB/OF orderings'},
	{'id': 'V3', 'name': 'scSeqComm top 5% by quantile of inter_score (text)', 'affects': 'B and F claims for scSeqComm and the OB/OF orderings'},
	{'id': 'V4', 'name': 'truth with BH-FDR on the Moran p-values, FDR < 0.05 (text)', 'affects': 'all claims (truth changes)'},
]
for v in variants[1:]:
	v['role'] = 'alternative reading: reported next to R0, never used for the verdict and never used to choose between readings'

out = {
	'paper': 'Dimitrov, D. et al. "LIANA+ provides an all-in-one framework for cell-cell communication inference". Nature Cell Biology 26, 1613-1622 (2024). DOI 10.1038/s41556-024-01469-w',
	'target': 'Fig. 4a-d: comparison of 9 ligand-receptor methods (15 scoring functions) against spatial co-localisation as assumed truth, 5 Slide-tags datasets',
	'code': 'saezlab/lianaplus_manuscript @ 37c712d280ed4f6ef55cd17490366c2f062ee513, notebooks/slideseq_benchmark/benchmark_slideseq.ipynb (copy sources/benchmark_slideseq.ipynb sha256 47c8c3062572ef02b67872724f71fe74651b217c046f3486caa4670340e2846e) and utils.py (sources/utils.py sha256 6265b1590e2ef736d8b27456e674afa47c9b11e7246767f8929744a6ed252ea3); package scverse/liana 1.0.5',
	'sources_used': {
		'paper_text': 'E:/Ciencia/noturno/triagem-2026-10-26/dl/liana.pdf (text liana.txt)',
		'supplementary_information': 'sources/MOESM1_ESM.pdf (968,261 B = server, md5 80fcc2c46cb27ed65f8ba07df51a8c89), Supplementary Note 5',
		'peer_review_file': 'sources/MOESM3_ESM.pdf (6,776,521 B = server, md5 94830ff3da99ed0261d0f6e9ff0c27bc); no mention of this benchmark found by text search',
		'source_data_fig4': 'sources/MOESM7_ESM.xlsx (13,746 B = server, md5 b4930a6023835e2aab51add8d7d790df, same as triage)',
	},
	'not_rechecked': 'Preprocessing from raw Single Cell Portal data (login required); the reproduction starts from the processed figshare .h5ad files.',
	'conditions_common': 'n = 5 datasets (humancortex SCP2167, HumanTonsil SCP2169, mouseembryo SCP2170, HumanMelanomaRNA SCP2171, HumanMelanomaMultiome SCP2176); definitions D01-D15; main reading R0; layer A unless stated; liana 1.0.5 env of D03; CPU only, light mode.',
	'paper_value_origin': "All paper values are medians of, or rows from, the authors' Source Data Fig. 4 (full precision, 15 significant digits) except Q4 (SI text). Nothing in this file comes from our own runs; no model or method was run at this stage.",
	'claims': claims,
	'definitions': definitions,
	'readings': variants,
}
json.dump(out, open(f'{root}/claims.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('claims', len(claims), 'definitions', len(definitions))
