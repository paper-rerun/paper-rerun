# Claims and fixed definitions

Paper: Notin et al., "ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design", NeurIPS 2023 Datasets and Benchmarks. Text read from sources/paper_neurips.pdf (sources/paper.txt). Code: OATML-Markslab/ProteinGym at tag PG_v1.3 (commit 1f8de974dead8ff7501eff087b725d14a965e9f9). Written 2026-10-23 before any model was run.

## Claims

| id | Quantity | Paper value | Where |
|---|---|---|---|
| C1 | ESM-1b, zero-shot Spearman, corrected average over the DMS substitution benchmark | 0.394 | Table 2, p.8; also Table A5 rank 22, p.38 |
| C2 | ESM2 (8M), same quantity | 0.226 | Table A5 rank 47, p.38 |
| C3 | ESM2 (35M) | 0.321 | Table A5 rank 42, p.38 |
| C4 | ESM2 (150M) | 0.387 | Table A5 rank 25, p.38 |
| C5 | ESM2 (650M), only if budget allows | 0.414 | Table A5 rank 15, p.38 |

Table A5 also gives a "Std. error" (0.010 to 0.015 for these models). The caption says it is "the non-parametric bootstrap standard error of the difference between the Spearman performance of a given model and that of the best overall model (i.e., TranceptEVE)". It is not the standard error of the score itself.

Side note, not a claim: Table A7 (p.40) gives ESM-1b "All" = 0.399 with per-function values 0.428/0.289/0.427/0.351/0.500, which are the PG_v1.0 summary numbers, while Table 2 gives 0.394 (PG_v1.1/v1.3 numbers).

## Definitions

**D1 Test set.** reference_files/DMS_substitutions.csv at PG_v1.3: 217 assays, 186 UniProt IDs, 2,465,767 mutants (runs/reference_stats.log). Paper: "Substitutions 217 2.4M" (Table 1, p.6). DMS files from https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/DMS_ProteinGym_substitutions.zip. 16 assays (13 proteins) have target_seq longer than 1022 aa.

**D2 Per-assay metric.** Spearman rank correlation between DMS_score and the model score over all mutants of the assay (paper §4.1: "the Spearman's rank correlation coefficient is the most generally appropriate metric"). Computed with scipy.stats.spearmanr, rounded to 3 decimals before averaging, as performance_DMS_benchmarks.py does.

**D3 Aggregation ("corrected average").** Paper §4.1: "we first compute each of these metrics within groups of assays that measure similar functions. The final value of the metric is then the average of these averages, giving each functional group equal weight." A.5.1, p.37: "we first average all the assays for a particular function type together, resulting in five average values (one each for Activity, Binding, Expression, Organismal Fitness, and Stability). The average of these five numbers is the final reported value." Groups = coarse_selection_type.

The text does not mention grouping by protein, but performance_DMS_benchmarks.py first averages assays of the same UniProt_ID within a function type. We checked which one the authors used with their own per-assay results (benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv at PG_v1.3, copied to sources/repo_csv/; runs/check_aggregation.log):

| Model | Paper | protein-then-function | assays-then-function (text) |
|---|---|---|---|
| ESM-1b | 0.394 | 0.3941 | 0.3982 |
| ESM2 8M | 0.226 | 0.2257 | 0.2244 |
| ESM2 35M | 0.321 | 0.3208 | 0.3196 |
| ESM2 150M | 0.387 | 0.3868 | 0.3895 |
| ESM2 650M | 0.414 | 0.4138 | 0.4184 |

Only the protein-then-function average reproduces the paper numbers, for all five models. So:
- **D3-primary (verdict):** mean of per-assay Spearman per (UniProt_ID, coarse_selection_type), then mean per coarse_selection_type, then mean of the 5 types.
- **D3-text (secondary, fixed now):** mean per coarse_selection_type over assays, then mean of the 5. Reported next to the primary, not used for the verdict.

**D4 Scoring rule.**
- ESM2 (all sizes): masked-marginals (paper A.2, p.32: "We predict fitness for ESM models with the masked-marginal approach introduced in Meier et al. [2021]"; scoring_ESM2_substitutions.sh also uses masked-marginals). Sequences >1022 aa: compute_fitness.py default scoring window "optimal" (the ESM2 script does not set one). Multi-mutants: sum over mutated positions of log p(mt) - log p(wt) at the masked position (label_row in compute_fitness.py).
- ESM-1b: the paper text says masked-marginals for "ESM models" and Brandes et al. [2023] windows for long sequences. The released script scoring_ESM1b_substitutions.sh uses wt-marginals with "overlapping" windows (Brandes et al.); masked-marginals with overlapping windows is not implemented in compute_fitness.py. Rule fixed now: before the full run, score one short assay (<1022 aa) and one long assay with both strategies and compare with the authors' released per-mutant ESM-1b scores (zero_shot_substitutions_scores.zip). **D4-ESM1b-primary** is the strategy whose per-mutant scores match the authors' (Spearman ≥ 0.999 with theirs); the other one is run in full only as a secondary if budget allows. If neither matches, primary = wt-marginals/overlapping (the released script) and that is reported.

**D5 Model weights.** Official fair-esm checkpoints from dl.fbaipublicfiles.com/fair-esm/models/: esm1b_t33_650M_UR50S, esm2_t6_8M_UR50D, esm2_t12_35M_UR50D, esm2_t30_150M_UR50D, esm2_t33_650M_UR50D (sizes checked against the server Content-Length, SHA256 in data/weights/SHA256SUMS). The repo's vendored esm package loads them; config.json maps them to ESM1b, ESM2_8M, etc.

**D6 Inference.** Single forward passes in eval mode, no dropout, no sampling. Deterministic up to GPU floating point.

## Tolerance

Recomputing D3-primary from the authors' per-assay values gives the paper numbers to rounding (|diff| ≤ 0.0004). ESM inference is deterministic, so a faithful rerun should land within rounding plus small floating point drift from a different GPU/library build.

- **Reproduced:** |ours - paper| ≤ 0.005 on the corrected average (half of the smallest bootstrap SE in Table A5, 0.010, and 10 rounding units).
- Diagnostic, not part of the verdict: per-assay Spearman between our per-mutant scores and the authors' released per-mutant scores, expected ≥ 0.999.

## Addendum after the D4 probe (appended, definitions above unchanged)

runs/results/probe_esm1b.log: on A0A192B1T2_9HIV1_Haddox_2018 (852 aa) and BRCA1_HUMAN_Findlay_2018 (1863 aa), wt-marginals with overlapping windows matches the authors' released ESM-1b scores (Spearman 1.000000, max |diff| 1.1e-4); masked-marginals does not (Spearman 0.971 and 0.977, max |diff| 9.5). So D4-ESM1b-primary = wt-marginals, overlapping windows. Masked-marginals is run as the secondary.

## Erratum, 2026-10-23 (appended during report revision, nothing above edited)

- Page and section citations above are wrong in three places (checked against sources/paper_neurips.pdf, printed page numbers): Table 2 is on p.9, not p.8 (C1). The sentence "We predict fitness for ESM models with the masked-marginal approach" is in A.4.1 "Zero-shot baselines", p.33, not "A.2, p.32" (D4). The A.5.1 quote in D3 is on p.35, not p.37. Table A5 p.38 and Table A7 p.40 are right.
- Tolerance: the "half of the smallest bootstrap SE in Table A5" reason contradicts the note under Claims, since that SE is of the difference to TranceptEVE, not of each score. It is only a loose reference. The 0.005 threshold itself is unchanged.
- The ESM-1b masked-marginals secondary was not run in full: stopped at start for time (runs/logs/ESM1b_masked.log). Only the 2-assay probe exists, and it used the single "optimal" window, since compute_fitness.py does not implement masked-marginals with overlapping windows.
