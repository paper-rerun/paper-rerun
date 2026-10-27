# Reproduction report: LIANA+ provides an all-in-one framework for cell-cell communication inference

- Paper: Dimitrov, D., Schäfer, P.S.L., Farr, E., Rodriguez-Mier, P., Lobentanzer, S., Badia-i-Mompel, P., Dugourd, A., Tanevski, J., Ramirez Flores, R.O. & Saez-Rodriguez, J., Nature Cell Biology 26, 1613-1622 (2024). DOI: 10.1038/s41556-024-01469-w
- Code: https://github.com/saezlab/lianaplus_manuscript @ 37c712d280ed4f6ef55cd17490366c2f062ee513 (`notebooks/slideseq_benchmark/benchmark_slideseq.ipynb` and `utils.py`), package https://github.com/scverse/liana at release 1.0.5 (PyPI wheel, md5 933caee33e70e4760d07ee722b5e5679)
- Data: figshare 10.6084/m9.figshare.26131789.v1, `slidetags.tar.xz` (212,359,900 B, md5 65bb74092f73ab7f7f061390a6e35030, the same as the md5 figshare computes); Source Data Fig. 4 (`41556_2024_1469_MOESM7_ESM.xlsx`, md5 b4930a6023835e2aab51add8d7d790df)
- Target: Fig. 4a-d. Nine ligand-receptor methods and 15 scoring functions are scored against spatial co-localisation on 5 Slide-tags datasets. The claims are 48 medians, 4 orderings, the 75 per-dataset rows of Source Data Fig. 4 and 4 statements from Supplementary Note 5, which makes 57. They were pre-registered in `claims.json` (sha256 a5008e24...be31ad) before any run. Fig. 4 prints no numbers, so every paper value except Q4 is a median we computed from the authors' Source Data Fig. 4
- Verdict: **Reproduced**
- Date: 2026-10-27
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04 (31 GB RAM visible), CPU only. We did not use the RTX 2070 SUPER. Everything ran under `nice -n 19` with OMP/MKL/OpenBLAS/NumExpr capped at 4 threads per process, because the machine was busy with other jobs. The cap applied per process, not to the whole run. A 1-thread quick check briefly overlapped the 4-thread truth run (5 threads in total), and layer B used 4 joblib workers that each inherited the 4-thread cap (average 192% CPU).

## Results

The main reading (R0) is the authors' code as written. Layer A re-runs the evaluation on the authors' published method outputs from figshare, plus the Moran's R truth, which we recomputed because it was never published. Layer B re-runs the methods themselves. So layer A shows that the evaluation code plus our recomputed truth regenerate the Source Data, and only layer B covers the method step.

**Layer A: 57 of 57 claims pass.** The 48 medians and all 675 R75 cells agree at the exact tier (max |diff| 5.6e-16). The orderings and Q1-Q3 pass their own rules. Q4 passes its 0.02 tolerance with diff -0.0194 against the SI value 0.765. Across all 75 Source Data rows × 9 columns (675 cells) our table is identical to the authors' up to floating-point rounding (max 5.6e-16).

| Claim | Quantity (median over 5 datasets) | Paper (Source Data median) | Ours (layer A) | Diff | Ours (layer B) |
|---|---|---|---|---|---|
| A01 | Fig. 4a AUROC: CellPhoneDB / lr_means | 0.5427 | 0.5427 | +3.3e-16 | 0.5427 |
| A02 | Fig. 4a AUROC: Rank_Aggregate / magnitude_rank | 0.5361 | 0.5361 | +1.1e-16 | 0.5361 |
| A03 | Fig. 4a AUROC: Geometric Mean / lr_gmeans | 0.5292 | 0.5292 | +4.4e-16 | 0.5292 |
| A04 | Fig. 4a AUROC: Connectome / Product* | 0.5292 | 0.5292 | +3.3e-16 | 0.5292 |
| A05 | Fig. 4a AUROC: NATMI / Product✳ | 0.5292 | 0.5292 | +3.3e-16 | 0.5292 |
| A06 | Fig. 4a AUROC: SingleCellSignalR / lrscore | 0.5292 | 0.5292 | +2.2e-16 | 0.5292 |
| A07 | Fig. 4a AUROC: scSeqComm / inter_score | 0.5189 | 0.5189 | +4.4e-16 | 0.5189 |
| A08 | Fig. 4a AUROC: CellChat / lr_probs | 0.5130 | 0.5130 | +3.3e-16 | 0.5130 |
| A09 | Fig. 4a AUROC: CellChat / cellchat_pvals | 0.5123 | 0.5123 | -3.3e-16 | 0.5123 |
| A10 | Fig. 4a AUROC: NATMI / spec_weight | 0.4967 | 0.4967 | +2.2e-16 | 0.4967 |
| A11 | Fig. 4a AUROC: Connectome / scaled_weight | 0.4965 | 0.4965 | -4.4e-16 | 0.4965 |
| A12 | Fig. 4a AUROC: Rank_Aggregate / specificity_rank | 0.4947 | 0.4947 | -1.7e-16 | 0.4947 |
| A13 | Fig. 4a AUROC: CellPhoneDB / cellphone_pvals | 0.4926 | 0.4926 | +2.8e-16 | 0.4926 |
| A14 | Fig. 4a AUROC: log2FC / lr_logfc | 0.4916 | 0.4916 | +0.0e+00 | 0.4916 |
| A15 | Fig. 4a AUROC: Geometric Mean / gmean_pvals | 0.4884 | 0.4884 | -5.0e-16 | 0.4884 |
| B01 | Fig. 4b Balanced accuracy: Connectome | 0.5157 | 0.5157 | +3.3e-16 | 0.5157 |
| B02 | Fig. 4b Balanced accuracy: log2FC | 0.5148 | 0.5148 | -2.2e-16 | 0.5148 |
| B03 | Fig. 4b Balanced accuracy: scSeqComm | 0.5129 | 0.5129 | +1.1e-16 | 0.5129 |
| B04 | Fig. 4b Balanced accuracy: CellChat | 0.5094 | 0.5094 | -1.1e-16 | 0.5094 |
| B05 | Fig. 4b Balanced accuracy: SingleCellSignalR | 0.5027 | 0.5027 | +2.2e-16 | 0.5027 |
| B06 | Fig. 4b Balanced accuracy: Rank_Aggregate | 0.5017 | 0.5017 | +1.1e-16 | 0.5017 |
| B07 | Fig. 4b Balanced accuracy: Geometric Mean | 0.5014 | 0.5014 | +1.1e-16 | 0.5014 |
| B08 | Fig. 4b Balanced accuracy: NATMI | 0.5010 | 0.5010 | +2.2e-16 | 0.5010 |
| B09 | Fig. 4b Balanced accuracy: CellPhoneDB | 0.4987 | 0.4987 | +1.7e-16 | 0.4987 |
| S01 | Fig. 4c F1* (normalised): CellPhoneDB / lr_means | 0.6565 | 0.6565 | -1.1e-16 | 0.6565 |
| S02 | Fig. 4c F1* (normalised): CellChat / lr_probs | 0.6207 | 0.6207 | -2.2e-16 | 0.6207 |
| S03 | Fig. 4c F1* (normalised): Rank_Aggregate / magnitude_rank | 0.5788 | 0.5788 | -4.4e-16 | 0.5789 |
| S04 | Fig. 4c F1* (normalised): Connectome / Product* | 0.5768 | 0.5768 | +5.6e-16 | 0.5768 |
| S05 | Fig. 4c F1* (normalised): SingleCellSignalR / lrscore | 0.5768 | 0.5768 | +5.6e-16 | 0.5769 |
| S06 | Fig. 4c F1* (normalised): NATMI / Product✳ | 0.5768 | 0.5768 | +5.6e-16 | 0.5768 |
| S07 | Fig. 4c F1* (normalised): Geometric Mean / lr_gmeans | 0.5768 | 0.5768 | +5.6e-16 | 0.5768 |
| S08 | Fig. 4c F1* (normalised): Connectome / scaled_weight | 0.5348 | 0.5348 | +0.0e+00 | 0.5348 |
| S09 | Fig. 4c F1* (normalised): scSeqComm / inter_score | 0.5182 | 0.5182 | +2.2e-16 | 0.5182 |
| S10 | Fig. 4c F1* (normalised): NATMI / spec_weight | 0.5167 | 0.5167 | +4.4e-16 | 0.5167 |
| S11 | Fig. 4c F1* (normalised): CellChat / cellchat_pvals | 0.5132 | 0.5132 | +3.3e-16 | 0.5132 |
| S12 | Fig. 4c F1* (normalised): CellPhoneDB / cellphone_pvals | 0.5074 | 0.5074 | +4.4e-16 | 0.5074 |
| S13 | Fig. 4c F1* (normalised): Rank_Aggregate / specificity_rank | 0.4874 | 0.4874 | -3.3e-16 | 0.4874 |
| S14 | Fig. 4c F1* (normalised): Geometric Mean / gmean_pvals | 0.4822 | 0.4822 | +2.2e-16 | 0.4822 |
| S15 | Fig. 4c F1* (normalised): log2FC / lr_logfc | 0.4505 | 0.4505 | +2.8e-16 | 0.4505 |
| F01 | Fig. 4d F1 (normalised): Rank_Aggregate | 0.5595 | 0.5595 | +0.0e+00 | 0.5595 |
| F02 | Fig. 4d F1 (normalised): log2FC | 0.5483 | 0.5483 | +3.3e-16 | 0.5483 |
| F03 | Fig. 4d F1 (normalised): Connectome | 0.5417 | 0.5417 | +2.2e-16 | 0.5417 |
| F04 | Fig. 4d F1 (normalised): CellChat | 0.5268 | 0.5268 | +3.3e-16 | 0.5268 |
| F05 | Fig. 4d F1 (normalised): NATMI | 0.5167 | 0.5167 | +4.4e-16 | 0.5167 |
| F06 | Fig. 4d F1 (normalised): scSeqComm | 0.5159 | 0.5159 | +1.1e-16 | 0.5159 |
| F07 | Fig. 4d F1 (normalised): SingleCellSignalR | 0.5025 | 0.5025 | +0.0e+00 | 0.5025 |
| F08 | Fig. 4d F1 (normalised): Geometric Mean | 0.5019 | 0.5019 | +2.2e-16 | 0.5019 |
| F09 | Fig. 4d F1 (normalised): CellPhoneDB | 0.4981 | 0.4981 | -3.9e-16 | 0.4981 |
| OA, OB, OS, OF | Box order in Fig. 4a-d | paper order | same (Kendall tau-b 1.0 in all four) | none | same (tau-b 1.0, 1.0, 0.985, 1.0) |
| R75 | 75 per-dataset rows × 9 columns of Source Data Fig. 4 | - | 675/675 cells within 0.0005 (max 5.6e-16) | - | 673/675 within 0.0005 (max 0.00053): **fails** |
| Q1 | Scoring functions with median AUROC > 0.5 ("most ... marginally better than random") | 9 of 15, max 0.5427 | 9 of 15, max 0.5427 | 0 | same |
| Q2 | Largest abs(median balanced accuracy - 0.5) ("closely aligned with random") | 0.0157 | 0.0157 | 0 | same |
| Q3 | Magnitude score beats specificity score, out of 6 methods (AUROC, F1*n) | 6, 6 | 6, 6 | 0 | same |
| Q4 | Spearman rho, F1 vs share of positive calls, 75 rows | 0.765 (SI text, not Source Data) | 0.7456 | -0.0194 (tolerance 0.02) | 0.7456 |

Q4 passes its pre-registered 0.02 tolerance with 0.0006 to spare. Our 0.7456 matches the authors' own Source Data (0.7456, diff 3.8e-5) and their notebook output ("F1: 0.746"). The 0.02 tolerance was set with the Source Data value 0.7456 already known (claims.json), so this pass shows that our run equals the authors' data, not that the SI figure 0.765 is reproduced. The 0.765 printed in Supplementary Note 5 is not what the released code gives. See the notes for the authors.

Layer B (secondary): we re-ran the 9 methods on the published `.X` with the notebook's cell 8 settings. **Layer B: 56/57 claims pass.** R75 fails on 2 cells: mouseembryo CellChat F1 (normalised) is off by +0.00053 on both score rows, which is a row-order effect of the baseline permutation (explained below). The AUROC rows are within 5.3e-10 of Source Data, and every median still sits within 0.0005 of the paper. Against the published `.uns`, 4 of 45 tables are identical (Rank_Aggregate in 4 datasets). Another 39 differ only in the scanpy t-test `ligand_pvals`/`receptor_pvals` (max 1.1e-16). In mouseembryo, NATMI `ligand_means_sums`/`receptor_means_sums` differ by 1.9e-6 and `spec_weight` by 3.0e-8 (float32 summation order), and Rank_Aggregate `specificity_rank` differs by 4.9e-5. All 9 mouseembryo tables come back in a different row order, because ties sort differently. The F1 baselines permute the binary column in row order, so that row order moves a few normalised F1/F1* values in mouseembryo by at most 0.00053.

## What it took

1. Environment (`env/`): Python 3.10.13 via uv, with the pins from the authors' `environments/env.yml` (env "spiana", the kernel the notebook names): liana 1.0.5 (local wheel, md5 checked), decoupler 1.6.0, scanpy 1.10.1, anndata 0.10.7, numpy 1.23.4, pandas 1.5.3, scikit-learn 1.4.2, numba 0.59.1, omnipath 1.0.7, matplotlib 3.8.3, seaborn 0.13.2. We left torch out because this notebook does not use it. Dependencies the authors did not pin were resolved with `--exclude-newer 2024-05-15` (scipy came out as 1.13.0). The hashed lockfile is `env/requirements.lock`, the build script is `env/setup_env.sh`, and `env/pip_freeze.txt` lists what got installed. The build took about 2 min.
2. Data (`data/get_data.sh`): we copied the figshare tarball fetched at triage, checked its size (212,359,900 B) and md5 against figshare's metadata, and extracted it. The five `.h5ad` md5s match the triage record. `runs/inspect_data.py` confirms each file is the `adata.h5ad` written by notebook cell 8: `.X` is log1p of counts normalised to 1e4 (expm1 row sums of the first 200 cells: 9999.3 to 10000.6), `layers['raw']` holds integer counts, `obsm['spatial']` is present and `.uns` holds the 9 method tables. Cells × genes after filtering: humancortex 4,065 × 28,568; HumanTonsil 5,778 × 27,805; mouseembryo 4,623 × 22,441; HumanMelanomaRNA 4,804 × 25,920; HumanMelanomaMultiome 2,535 × 24,359.
3. Truth (`runs/truth.py`): notebook cell 10 unchanged (`spatial_neighbors(bandwidth=150, cutoff=0.1, set_diag=True)`, `lr_bivar(function_name="morans", n_perms=1000, expr_prop=0.05, mask_negatives=True)` for ligand-receptor pairs and for one-hot cell types). It took 69 min wall for the 5 datasets at 4 threads. The progress bars of the authors' cell 10 add up to about 17 min, about 3.6x faster than our 4-thread run (2.4x to 9x depending on the dataset). The truth has 762/355/467/484/873 ligand-receptor pairs and 42/156/420/132/90 cell-type pairs.
4. Evaluation (`runs/evaluate.py`): notebook cells 12-13 copied as they are, with the authors' `utils.py` imported unchanged from `sources/`. Its sha256 (6265b159...52ea3) matches the value pre-registered in claims.json, checked after the run; no script checked it during the run. About 22 min per full pass. Before the full pass we ran a quick check (`runs/quick_check.py`, 1 thread): all 15 humancortex AUROCs matched the Source Data to 6 decimals.
5. Layer B (`runs/layerB.py`): the 9 methods with notebook cell 8 settings, except `n_jobs=4` where the authors used 10. It took 15.6 min, with a peak RSS of 10.5 GB. In liana 1.0.5 the permutation stream is drawn in order from a single `default_rng(1337)`, so `n_jobs` does not change it, and our results agree.
6. Scoring (`runs/compare.py`, `runs/compare_uns.py`, `runs/variant_facts.py`): every number above comes from `runs/results/*.json` and the logs in `runs/logs/`. `compare.py` refuses to run if `claims.json` no longer matches its frozen sha256.

The whole pipeline (`runs/run_all.sh`, restartable) ran from 10:58 to 13:42 local time: 2 h 44 min wall and about 4 CPU-hours of user time. We did not change the authors' code. `patches/` holds only a README saying no patches were needed. The only differences are new file paths, `n_jobs=4` in layer B, and command-line switches for the alternative readings below. The wrappers keep the notebook's code line for line.

Not re-checked: the preprocessing in notebook cell 8 (matching barcodes to the spatial table, `filter_cells(min_genes=200)`, `filter_genes(min_cells=3)`, normalisation). It reads the raw Single Cell Portal studies SCP2167/2169/2170/2171/2176, and downloading those needs a login (HTTP 401 without one). We started from the authors' processed figshare files, so the cell and gene counts above are taken as published.

## Alternative readings

The Methods text and the code disagree in four places. The verdict uses the code (R0), because the code produced the Source Data. We ran each text reading afterwards on the full data (layer A). None of them changes the verdict.

| Reading | What changes | Claims passing | Effect |
|---|---|---|---|
| V1 | F1 baseline from 100 shuffles (Methods) instead of 1000 (code) | 56/57 | R75 fails (573/675 cells within 0.0005; F1*n rows up to 0.0186 off). 12 S/F medians (S01, S02, S08, S09, S10, S12, S13, F01-F05) pass their tolerance but miss the exact tier, the largest being S01 at 0.6379 (-0.0186). AUROC, BA and the four orderings are unchanged. |
| V2 | Rank_Aggregate kept at magnitude_rank < 0.05 only (Methods) instead of magnitude AND specificity < 0.05 (code) | 55/57 | Rank_Aggregate BA 0.5035 (paper 0.5017) and F1n 0.5580 (paper 0.5595). It keeps first place in Fig. 4d. Fig. 4b: Rank_Aggregate moves above SingleCellSignalR (0.5027), tau-b 0.94, which is still within the tie rule. Failing claims: Q4 (rho 0.697, because the share of positive calls changes) and R75 (617/675). |
| V3 | scSeqComm "top 5%" as inter_score > 95th quantile (Methods) instead of inter_score > 0.95 (code) | 52/57 | Selects **no** interactions in any dataset. The 95th quantile of inter_score is 1.0 everywhere, because 19.7% to 33.3% of rows are tied at 1.0. F1n becomes 0/0 (NaN, so the OF tau-b is NaN too). BA falls to 0.5000, which moves scSeqComm from 3rd to 8th of 9 in Fig. 4b (OB fails, tau-b 0.72; it stays above CellPhoneDB at 0.4987). Q4 rho becomes 0.802 (fails). Failing claims: B03, F06, OB, Q4 and R75 (107/675). |
| V4 | Truth with BH-FDR < 0.05 on the Moran p-values (Methods: "Moran's R > 0 and FDR < 0.05") | 20/57 | See below. |

V4 needs a closer look. In `utils.join_pred_truth` the FDR correction is applied to the boolean `(pvals <= 0.05)` instead of to the p-values: `p_adjust_fdr((lr_truth['morans_pvals']) <= 0.05)`. Given a 0/1 input, `decoupler.p_adjust_fdr` returns it unchanged (we checked this on all 10 truth tables). So the published truth is raw permutation p <= 0.05 and R > 0, with no multiple-testing correction. Our V4 run applies a real BH-FDR with a strict `< 0.05`, as the Methods say. The truth shrinks a little: 318→296, 158→148, 207→204, 190→168 and 319→289 true ligand-receptor pairs, and 14→12, 70→70, 116→114, 50→48 and 18→4 cell-type pairs. The rankings change a lot, though. Kendall tau-b against the paper order falls to 0.54 (Fig. 4a), 0.06 (4b), -0.15 (4c) and 0.06 (4d). The specificity scores overtake the magnitude scores on F1*n: magnitude wins only 2 of 6 pairs there (5 of 6 on AUROC), against 6 of 6 in the paper. The weak-association reading holds: 14 of 15 median AUROCs exceed 0.5, max 0.5432, and the largest |median BA - 0.5| is 0.035. But Q2 fails its 0.03 tolerance under V4 (0.0352, Geometric Mean BA 0.5352), so Q2-Q4 all fail. What does not survive is the finer ordering of methods, the magnitude-over-specificity statement, and the "closely aligned with random" margin as pre-registered. All of those depend on this one line.

## Notes for the authors

Thanks for publishing the processed `.h5ad` files, the Source Data and the notebook with its outputs. With those, the whole Fig. 4 evaluation could be re-run from public files, and it matched to about 1e-16. We spotted four small things while doing it:

1. `utils.join_pred_truth` calls `p_adjust_fdr((pvals) <= 0.05)`. The parenthesis sits where it applies BH to a 0/1 vector, which comes back unchanged, so the truth has no FDR correction. The Methods say "FDR < 0.05". Moving the comparison outside, `p_adjust_fdr(pvals) < 0.05`, follows the text. In our run that change reorders the methods in all four panels and flips the magnitude-vs-specificity comparison on F1*. The weak-association reading holds (max median AUROC 0.5432), but the largest median balanced accuracy moves to 0.035 from 0.5. Could you say which one was intended?
2. scSeqComm: the Methods say "top 5% of the interscore distribution", while the code keeps `inter_score > 0.95`. On these datasets that keeps 54% to 78% of interactions, because inter_score has a large mass at exactly 1.0. Read as the 95th quantile, the text would select nothing (that quantile is 1.0). Updating the Methods to the absolute cut-off would make the text match the code.
3. Supplementary Note 5 gives Spearman's rho = 0.765 between F1 and the number of interactions retained. The released code, the notebook output (`F1: 0.746`) and Source Data Fig. 4 all give 0.746.
4. Smaller items: the Methods give 100 shuffles for the permuted F1, while the code uses 1000 (with 100, F1*n medians move by up to 0.019); the Rank_Aggregate filter in the code also requires `specificity_rank < 0.05`, which the text does not mention; and the Fig. 4 legend says normalised F1 is bounded between minus and plus infinity, while (F1obs/F1perm)/2 cannot be negative.

## How this report was made

AI agents (Claude, by Anthropic) ran this reproduction on a home computer, and a human reviewed it before publication. No number in this report was estimated or typed by hand. Each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A separate agent read the paper and pre-registered the claims, their definitions and tolerances in `claims.json` before anything ran. Then a single agent built the environment, ran the authors' code on the published data on a Ryzen 9 3900X (CPU only; the RTX 2070 SUPER was not used), compared the results with the paper and wrote this report. A reviewer agent and a reviser agent checked the report against the logs, and a human approved publication. Nobody ran a blind recomputation with a second agent for this paper.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues