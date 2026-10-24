# Reproduction report: ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design

- Paper: Notin, Kollasch, Ritter, van Niekerk, Paul, Spinner, Rollins, Shaw, Orenbuch, Weitzman, Frazer, Dias, Franceschi, Gal and Marks, NeurIPS 2023 Datasets and Benchmarks Track. DOI: none for the proceedings version; bioRxiv preprint 10.1101/2023.12.07.570727
- Code: https://github.com/OATML-Markslab/ProteinGym @ 1f8de974dead8ff7501eff087b725d14a965e9f9 (tag PG_v1.3)
- Data: https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/ (DMS_ProteinGym_substitutions.zip, zero_shot_substitutions_scores.zip); weights from https://dl.fbaipublicfiles.com/fair-esm/models/
- Target: zero-shot DMS substitution benchmark. Test-set size (Table 1). ESM-1b Spearman, AUC, MCC, NDCG@10% and top-10% recall (Table 2). ESM2 8M, 35M, 150M and 650M Spearman (Table A5).
- Verdict: Partially reproduced
- Date: 2026-10-24
- Hardware: Ryzen 9 3900X, 64 GB RAM (31 GB visible to WSL2), RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04

Every claim that was computed on all 217 assays came out within its tolerance. The verdict is "Partially" for two reasons. First, ESM2 650M (C5) was recomputed only on a fixed-seed sample of assays, in both runs, because of GPU time. Second, the first run (A) did not finish ESM-1b. It stopped at 129 of 217 assays, so only the blind run (B) confirmed C1 and C6 to C9 in full. Finishing run A's ESM-1b (~3.4 GPU h) and run B's 650M on the remaining 163 assays (~3.3 GPU h) would allow a full verdict. Separately, the released ESM2 script does not reproduce the authors' released per-mutant ESM2 scores on 5 of the 217 assays. The effect on the averages is between -0.0023 and +0.0016, well inside tolerance (see Notes for the authors).

## Results

Run A used the authors' own shell scripts and `performance_DMS_benchmarks.py`. Run B was the blind recompute: a separate agent rebuilt the environment from the lockfile, called the authors' `compute_fitness.py` with the same flags, and computed the metrics with code it wrote itself. "Diff" is run B minus the paper. Values use the code definition of the corrected average, which became primary at the check stage (see "Definitions" below for when and why). Tolerance is 1 bootstrap SE of the authors' own corrected average.

| ID | Quantity | Paper | Run A | Run B | Diff (B) | Tol. | Within tol. |
|---|---|---|---|---|---|---|---|
| C0 | Substitution assays in the benchmark | 217 | 217 | 217 | 0 | 0 | A yes, B yes |
| C1 | ESM-1b Spearman, corrected avg | 0.394 | not finished (129/217) | 0.3941 | +0.0001 | 0.014 | B yes |
| C2 | ESM2 8M Spearman | 0.226 | 0.2234 | 0.2235 | -0.0025 | 0.016 | A yes, B yes |
| C3 | ESM2 35M Spearman | 0.321 | 30-assay sample only | 0.3214 | +0.0004 | 0.018 | B yes |
| C4 | ESM2 150M Spearman | 0.387 | 30-assay sample only | 0.3884 | +0.0014 | 0.017 | B yes |
| C5 | ESM2 650M Spearman | 0.414 | 30-assay sample only | 54-assay sample only | n/a | 0.017 | not tested on 217 |
| C6 | ESM-1b AUC, corrected avg | 0.719 | not finished | 0.7188 | -0.0002 | 0.008 | B yes |
| C7 | ESM-1b MCC, corrected avg | 0.311 | not finished | 0.3109 | -0.0001 | 0.012 | B yes |
| C8 | ESM-1b NDCG@10%, corrected avg | 0.747 | not finished | 0.7467 | -0.0003 | 0.015 | B yes |
| C9 | ESM-1b top-10% recall, corrected avg | 0.203 | not finished | 0.2021 | -0.0009 | 0.007 | B yes |

C0 detail: both runs counted 217 assays and 2,465,767 mutants. The reference file and the rows in the 217 data files agree for every assay. There are 186 distinct UniProt IDs and 16 targets longer than 1022 aa. Type counts are Activity 43, Binding 13, Expression 18, OrganismalFitness 77, Stability 66.

Under the original pre-registration in `claims.json` (literal A.5.1 average, tolerances 0.014/0.016/0.017/0.016/0.016 for C1 to C5), every 217-assay claim also passes. Run B gives ESM-1b 0.3983 against 0.394 (tol. 0.014), 8M 0.2223 against 0.226 (0.016), 35M 0.3202 against 0.321 (0.017) and 150M 0.3910 against 0.387 (0.016). The verdict does not depend on which version is used.

Sampled sizes. A sample average cannot be compared with the paper's 217-assay average. For these sizes, the check is per assay against the authors' per-assay table (`DMS_substitutions_Spearman_DMS_level.csv`, 3 decimals), on the same assays:

| Size | Run | Assays | Ours (corrected avg on sample) | Authors, same assays | Assays off by more than rounding |
|---|---|---|---|---|---|
| 35M | A | 30 | 0.2832 | 0.2832 | 0 of 30 |
| 150M | A | 30 | 0.3599 | 0.3601 | 1 of 30 (POLG_CXB3N, -0.010) |
| 650M | A | 30 | 0.3991 | 0.3992 | 1 of 30 (POLG_CXB3N, -0.002) |
| 650M | B | 54 | 0.4164 | 0.4170 | 2 of 54 (SCN5A, ZIKV) |

Every assay that differs is one of the 5 partial-MSA assays described below.

Per-mutant agreement with the authors' released scores (`zero_shot_substitutions_scores.zip`, PG_v1.3):

- **ESM-1b:** Run B matched all 217 assays, with the largest absolute difference at 0.00015. Run A matched all 129 assays it finished, with the largest difference at 1.51e-4. In every assay the Spearman between our scores and theirs was 1.00000. Both runs include long targets scored with overlapping windows, for example A0A140D2T1_ZIKV (3423 aa) and BRCA2 (3418 aa).
- **ESM2 8M, 35M and 150M:** 212 of 217 assays match to within 1e-3 (typically 1e-5 to 1e-4). The other 5 are the partial-MSA assays.
- **ESM2 650M:** 52 of 54 sampled assays match in run B, and 29 of 30 in run A.

Per-assay agreement for the ESM-1b metrics (run B against the authors' tables, which round to 3 decimals): the largest difference per metric is Spearman 0.00050, AUC 0.00052, NDCG 0.00050, top recall 0.00050 and MCC 0.0021. The MCC case is a single assay, BCHB_CHLTE_Tsuboyama_2023_2KRU (52 mutants): 0.3321 against 0.330. It moves the average by less than 0.0001. Every other MCC value is within 0.0006.

## What it took

1. **Test set and sources.** We cloned the repo at tag PG_v1.3. We downloaded DMS_ProteinGym_substitutions.zip (43,021,128 B, zip CRC OK, sha256 recorded) and zero_shot_substitutions_scores.zip (1,911,045,703 B, size and zip CRC checked; the server publishes no checksum). Then we fetched the five ESM checkpoints. Each checkpoint was checked against the server Content-Length and the S3 multipart ETag, and its sha256 is recorded in `data/weights/*.verified`.
2. **Environment.** The authors list their environment with `pip list` in `environments/proteingym_env.txt`. We installed only the packages the ESM path imports, at their exact versions: torch 1.13.1+cu117, numpy 1.24.4, pandas 1.5.1, scipy 1.10.1, scikit-learn 1.3.2, biopython 1.82, numba 0.58.1, tqdm 4.66.1. Python is 3.10.14, the highest version torch 1.13.1 supports. The lock is `env/requirements.lock` (uv, hashes, 21 packages), and `env/setup_env.sh` rebuilds it. fair-esm is not installed, because the code uses the vendored `proteingym/baselines/esm/esm`. Run B rebuilt the venv from the lockfile and got a freeze identical to `env/freeze.txt`.
3. **Run A (authors' scripts).** `run_authors_script.sh` runs `scoring_ESM1b_substitutions.sh` and `scoring_ESM2_substitutions.sh` with only the placeholders filled in. Those are the checkpoint path, the DMS index, our venv in place of `source activate proteingym_env`, the data and output folders, and the checkpoint pair to uncomment for the chosen ESM2 size. The diff is in `patches/scoring_ESM2_substitutions_8M_example.diff`. Scores then went through the authors' `merge.py` and `performance_DMS_benchmarks.py`. `merge.py` otherwise wants a file for every listed model, so we gave both scripts a config.json with one model and, for sampled sizes, a reference file that lists only the sampled assays.
   - ESM2 8M ran on all 217 assays. That took 4.64 h of wall time under the GPU lock, of which about 1 h was compute, because each call re-imports torch from the /mnt/e mount and reloads the checkpoint.
   - `estimate.py` estimated the full 8M, 35M, 150M and 650M runs at 3.5 + 4.1 + 8.9 + 10.0 GPU hours. These are runtime estimates, and together they are far over the ~4 h budget. So for 35M, 150M and 650M we ran a 30-assay sample. The order was drawn at 17:14 on 2026-10-23 with `random.Random(0).shuffle(range(217))` (`exec/B2_esm2/sample_order.json`), and N=30 was set by `fix_sample.py` (mtime 17:18:14). `sample.json` was rewritten at 17:21:41 only to correct its timestamp text. By then one 8M assay (index 128) had been scored. That does not affect the sample, because 8M was run on all 217. The authors' per-assay ESM2 Spearman table had already been read at the claims stage. Times for the 30-assay runs were 0.62 h, 0.77 h and 1.66 h.
   - ESM-1b took about 141 s per assay on average (median 113 s, `exec/B1_esm1b/timing.tsv`) and finished indices 0 to 128. The run died when WSL restarted while it was scoring index 129. The resumed job was killed when that agent stopped. The loop can be restarted with `exec/B1_esm1b/run_all.sh 129 216`, followed by `post.sh ours` and `analyze.py ours`. That would finish run A in about 3.4 more GPU hours (estimate).
4. **Run B (blind).** `verify/scripts/run_scores.py` does not call the shell script 217 times. It imports the authors' `compute_fitness.py` and calls `main()` once per assay with the same flags as the .sh files. It caches the loaded checkpoint, so the 7.8 GB ESM-1b file is read only once. The repo root had to go on `sys.path`, because the v1 checkpoint loader does `from proteingym.baselines.esm import esm`. Without it, the first ESM-1b attempt failed with ModuleNotFoundError.
   - Metrics were written from scratch in `verify/scripts/metrics.py`. Its `--selftest` checks Spearman, AUC and MCC against scipy and sklearn on 200 random sets with ties, to 1e-12.
   - Runtime: 8M about 41 min, 35M 78 min, 150M 134 min. ESM-1b took about 20 min of scoring: 61 min of wall time, about 41 min of it spent waiting for the GPU lock behind the 8M run.
   - 650M was run on the first 54 assays of `verify/assay_order_seed0.csv`. The order was drawn with `numpy.random.default_rng(0)` at 01:38, before any run B score was computed (sha256 in `verify/logs/draw_sample.log`). That took 93 min. The full 217 were estimated at 4.86 GPU h (`verify/logs/estimate.log`), so the remaining 163 assays would take about 3.3 h.
   - Run B worked in the same folder as run A. Blindness was by instruction and was not enforced by file permissions. None of its scripts (`verify/scripts/*`) read run A's outputs.
5. **Shell issues (environment only):**
   - Git Bash rewrites `/mnt/...` paths passed to `wsl.exe`, so every call needed `MSYS_NO_PATHCONV=1`.
   - Files written from Windows got CRLF line endings and had to be converted.
   - A temp folder left by the killed ESM-1b run was later removed.

No method or hyperparameter was changed.

## Definitions and when they were fixed

- **Two versions of the pre-registration.** The original claims file (`claims.json`, 2026-10-23 11:21) made the literal A.5.1 average primary. It set the tolerances for C1 to C5 at 0.014/0.016/0.017/0.016/0.016 and covered claims C0 to C5 only. At the check stage (11:23-11:24), the code definition became primary, the tolerances moved to 0.014/0.016/0.018/0.017/0.017, and C6 to C9 were added. That was before any of our scores existed, but after comparing both definitions on the authors' per-assay table. That version was not saved at the time. It is reconstructed from the pipeline record in `claims_checked.json`, which says so in the file. `claims.json` is unchanged. As shown under Results, the verdict is the same under either version.
- **Corrected average, primary (check stage).** This is what the code does (`performance_DMS_benchmarks.py`, lines 361-369). It averages the assays inside each (UniProt ID, function type) pair, then averages the pairs inside each of the 5 function types, then takes the plain mean of the 5. The A.5.1 text describes a different procedure: average all assays inside each function type, then take the mean of the 5. On the authors' own per-assay table, the code version gives every paper value at 3 decimals (0.394, 0.226, 0.321, 0.387, 0.414). The literal version misses all five (0.398, 0.224, 0.320, 0.390, 0.418). This is why the code version was chosen, and it was chosen after seeing the authors' data, though not ours.
- **Tolerance.** 1 non-parametric bootstrap SE of the authors' own corrected average: 10,000 resamples of (UniProt, type) units within each type, seed 0, the same scheme as the repo's bootstrap function. The original `claims.json` resampled assays under the literal definition. The paper's SEs in Table A5 (0.010 to 0.015) are SEs of the difference from TranceptEVE, not of the value, so we did not use them.
- **ESM-1b scoring.** The released script, unchanged: wt-marginals, with overlapping windows for the 16 targets longer than 1022 aa. Fixed in `claims.json`.
- **ESM2 scoring.** The released script, unchanged: masked-marginals, `--scoring-window optimal`. Fixed in `claims.json`.

## Alternative readings (chosen after seeing data)

These were not pre-registered and do not change the verdict.

- **Literal A.5.1 average.** Run B gives ESM-1b 0.3983, 8M 0.2223, 35M 0.3202 and 150M 0.3910. For ESM-1b, AUC is 0.7223, MCC 0.3146, NDCG 0.7471 and top recall 0.2042. On the 54-assay 650M sample, both definitions give 0.4164, because none of those 54 assays shares a (UniProt, type) pair. Every literal value is within the tolerances of both the original and the check-stage versions.
- **MSA-cropped input for the 5 partial-MSA assays.** We re-ran `compute_fitness.py` on `target_seq[MSA_start-1:MSA_end]` with offset MSA_start. That reproduces the authors' released ESM2 scores per mutant (max |diff| ≤ 8e-5) at all four sizes. Swapping those 5 assays into run B gives 8M 0.2257, 35M 0.3208, 150M 0.3868 and 650M (54 assays) 0.4170. These equal the authors' values on the same assays, and no assay is off by more than 0.0015 (`verify/logs/crop_aggregate.log`). Run A got 0.2257 for 8M the same way.
- **650M on all 217, under the released script.** This is an imputation, not a recompute (`verify/logs/impute_650M.log`). It combines our 54 sampled assays, a separate run of the 3 other partial-MSA assays, and the authors' per-assay values for the other 160 assays. Those authors' values matched our runs on every full-MSA assay at the other sizes. The result is 0.4148 with the code definition and 0.4194 literal, against the paper's 0.414. Run A's projection, built a different way, also gives 0.4148 (code). For 35M and 150M, that projection gives 0.3214 and 0.3884, the same as run B's full runs.

## Notes for the authors

Thanks for releasing the per-assay tables and the per-mutant scores. They made a per-mutant check possible, which is rare. Most things matched to float noise. A few things we tripped on:

1. **ESM2 script vs released ESM2 scores on 5 long assays.** These are KCNH2_HUMAN_Kozek_2020 (MSA 535-565 of 1159), SCN5A_HUMAN_Glazer_2019 (1611-1642 of 2016), POLG_CXB3N_Mattenberger_2021 (1-861 of 2185), POLG_HCVJF_Qi_2014 (1984-2089 of 3033) and A0A140D2T1_ZIKV_Sourisseau_2019 (281-804 of 3423). For them, `scoring_ESM2_substitutions.sh` scores the full `target_seq` with an optimal window, while the released ESM2 scores match scoring only the MSA region. The per-assay effect can be large. KCNH2 at 8M gives -0.140 with the script against 0.253 released, and at 150M 0.560 against 0.229. The corrected averages move by only -0.0023 to +0.0016. The other 11 long targets, whose MSA spans the whole sequence, match exactly. ESM-1b is not affected. Could the script crop to the MSA region, or the scores be regenerated, so the two agree?
2. **ESM-1b scoring strategy (issue #99).** The released ESM-1b scores are wt-marginals with overlapping windows. That is what the script does and what Brandes et al. describe, and they match on all 217 assays, including the long targets. Appendix A.4 says the ESM models use masked marginals. A one-line fix in A.4 would close the issue.
3. **Corrected average.** A.5.1 describes a plain average over each function type, but the code averages within (UniProt, function type) first. The paper's numbers follow the code. The difference is up to 0.005 per model.
4. **Leftover tables from the preprint.** Tables 2 and A5 use the v1.1/v1.3 classification (Binding 13, Expression 18). Table A2 (Binding 14, Expression 17) and Table A7 (ESM-1b "All" 0.399) still match the bioRxiv version, where SPIKE_SARS2_Starr_2020_expression was classed as Binding. Moving that one assay back reproduces the bioRxiv Table A5 values at 3 decimals for ESM-1b, all four ESM2 sizes, TranceptEVE L and GEMME. One value in Table A7 is not explained by this: ESM-1b OrganismalFitness, 0.351 in the paper against our 0.349. ESM-1v does not fit either (0.412 against 0.416 in bioRxiv), so its scores did change between versions. Tables A6 and A8 for ESM-1b also differ from the v1.3 Summary CSV (for example, A6 Low MSA depth 0.350 against 0.365).
5. **Small things:**
   - Table 1 puts 217 under "# Proteins". That number is the assay count; there are 186 proteins.
   - The ESM-1b top-10% recall in Table 2 is 0.203, but the repo's v1.3 Summary CSV and our recompute give 0.202.
   - A.4 gives the context limit as 1023 amino acids. The code windows sequences longer than 1022 aa.
   - The `--dms_index` placeholder in the scoring scripts says 1 to 217, but the index is 0-based (0 to 216).

## How this report was made

AI agents (Claude, by Anthropic) ran this reproduction on a home computer, and a human reviews it before publication. No number in this report was typed by hand. Each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder. Runtime estimates and the 650M imputation are labelled as such where they appear.

1. One agent read the paper and listed the numeric claims to check. Every definition the computation needs (cutoffs, test sets, how results are averaged) was fixed before anything ran. Most came from the paper text. Where the text and the authors' code disagree (the corrected average), the code was used. See Definitions for when that changed. A second agent checked the list against the paper.
2. One agent built the software environment once and froze it, starting from the versions the authors used.
3. Separate agents computed each group of claims with the authors' code and released weights, on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X.
4. A different agent rebuilt the environment from the frozen lockfile and recomputed the claims without seeing the first results. It called the authors' scoring function (`compute_fitness.py`) directly and computed every metric with code it wrote itself. ESM2 650M was recomputed on a fixed-seed sample of 54 assays only.
5. One agent wrote this report and another one tried to find errors in it.
6. A human read the report and approved publication.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues