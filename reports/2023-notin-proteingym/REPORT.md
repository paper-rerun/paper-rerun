# Reproduction report: ProteinGym: Large-Scale Benchmarks for Protein Fitness Prediction and Design

- Paper: Notin, Kollasch, Ritter, van Niekerk, Paul, Spinner, Rollins, Shaw, Weitzman, Frazer, Dias, Franceschi, Orenbuch, Gal, Marks. NeurIPS 2023 Datasets and Benchmarks Track. DOI: none for the NeurIPS proceedings version. bioRxiv preprint: 10.1101/2023.12.07.570727.
- Code: https://github.com/OATML-Markslab/ProteinGym @ tag PG_v1.3 (1f8de974dead8ff7501eff087b725d14a965e9f9)
- Data: https://marks.hms.harvard.edu/proteingym/ProteinGym_v1.3/ (DMS_ProteinGym_substitutions.zip, zero_shot_substitutions_scores.zip). Weights from https://dl.fbaipublicfiles.com/fair-esm/models/
- Target: zero-shot Spearman "corrected average" over the 217 DMS substitution assays:
  - ESM-1b: 0.394 (Table 2, p.9)
  - ESM2 8M / 35M / 150M / 650M: 0.226 / 0.321 / 0.387 / 0.414 (Table A5, p.38)
- Verdict: Reproduced. All 5 values fall within the 0.005 tolerance, with three caveats:
  - With the released code, ESM2 scores differ from the released scores on 5 long-protein assays, so ESM2 8M gives 0.223 against the paper's 0.226.
  - ESM-1b matches the paper when scored with the released wt-marginals script. It was not scored with the masked-marginals method that the paper text describes.
  - The tolerance is about 10 times wider than what deterministic inference alone would need.
- Date: 2026-10-23
- Hardware: Ryzen 9 3900X, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04 (31 GB RAM visible to WSL)

## Results

The definitions are in claims.md:
- the Spearman of each assay is rounded to 3 decimals, as performance_DMS_benchmarks.py does;
- assays are averaged per (UniProt_ID, function type), then per function type, then over the 5 types.

claims.md says it was written before any model ran. The files cannot prove this:
- The file was last modified at 05:41 on 2026-10-23, when the D4 addendum was appended. By then the ESM2 8M, 35M and 150M runs and the ESM-1b probes had finished.
- No copy or hash of the earlier version exists.
- The D3 table in claims.md matches runs/check_aggregation.log, written at 00:49. The first model execution, a smoke test, ran at 00:51.

Nothing in the files suggests the definitions changed after that. During this revision we appended a dated erratum to claims.md and left the earlier text as it was.

Tolerance, from claims.md: |ours - paper| ≤ 0.005, which is 10 rounding units. claims.md also calls this "half of the smallest bootstrap SE in Table A5". That SE is the SE of each model's difference to TranceptEVE, not of each model's score (note 5 below), so it is only a loose reference. A tighter standard comes from two facts:
- ESM inference is deterministic.
- runs/evaluate.py, run on the authors' released per-mutant scores, matches the paper to within rounding: the largest difference is 0.0003 (runs/results/authors_scores_summary.log).

So a faithful rerun should land within about 0.0005. ESM-1b and ESM2 35M do. ESM2 8M, 150M and 650M are off by 0.0026, 0.0014 and 0.0008. All three gaps come from the five assays discussed below.

| Quantity | Paper | Ours | Diff |
|---|---|---|---|
| ESM-1b, corrected average Spearman | 0.394 | 0.3941 | +0.0001 |
| ESM2 8M | 0.226 | 0.2234 | -0.0026 |
| ESM2 35M | 0.321 | 0.3214 | +0.0004 |
| ESM2 150M | 0.387 | 0.3884 | +0.0014 |
| ESM2 650M | 0.414 | 0.4148 | +0.0008 |

All five values are within the 0.005 tolerance. Every run covered all 217 assays and 2,465,767 mutants.

We also compared our per-mutant scores with the authors' released scores (runs/results/vs_authors.log, runs/results/*_vs_authors.csv, runs/logs/revision_checks.log):
- **ESM-1b:** all 217 assays agree. On every assay the Spearman between our scores and theirs is at least 0.9999997, and the largest difference is 1.5e-4.
- **ESM2, all four sizes:** 212 assays agree. The Spearman is at least 0.9999995 on every one, and the largest difference is 2.0e-4 or less (8M 6.7e-5, 35M 7.0e-5, 150M 2.0e-4, 650M 1.4e-4). Five assays do not agree (Spearman with the authors' scores 0.27 to 0.996):
  - KCNH2_HUMAN_Kozek_2020
  - SCN5A_HUMAN_Glazer_2019
  - POLG_HCVJF_Qi_2014
  - POLG_CXB3N_Mattenberger_2021
  - A0A140D2T1_ZIKV_Sourisseau_2019

  The cause is explained below. On the other 212 assays, our per-assay Spearman is identical to the authors' for every size. Using the authors' per-assay values for the 5 assays changes our corrected average by 0.0023 for 8M (0.2234 to 0.2257), 0.0006 for 35M, 0.0016 for 150M and 0.0010 for 650M. With that swap, each ESM2 average equals the one computed from the authors' per-assay values (runs/logs/revision_checks.log).

claims.md also defines a secondary measure: assays averaged directly into function types, as the paper text describes. It is not used for the verdict.

| Model | Paper | Ours, text definition | Diff |
|---|---|---|---|
| ESM-1b | 0.394 | 0.3982 | +0.0042 |
| ESM2 8M | 0.226 | 0.2223 | -0.0037 |
| ESM2 35M | 0.321 | 0.3202 | -0.0008 |
| ESM2 150M | 0.387 | 0.3910 | +0.0040 |
| ESM2 650M | 0.414 | 0.4194 | +0.0054 |

The authors' own per-assay CSV shows the same pattern. ESM-1b gives 0.3982 under the text definition and 0.3941 under the script's. So the paper's numbers come from the script's average, which groups by protein first, and not from the definition in the text.

## What it took

1. **Claims and definitions.** We read the paper and SI and wrote claims.md with the definitions and the tolerance. Its timing is covered under Results. Two definitions could only be settled with the authors' released results.
   - **Aggregation.** The paper text averages assays within each function type (§4.1, p.6; A.5.1, p.35). performance_DMS_benchmarks.py first averages the assays of each UniProt ID. We recomputed the averages from the authors' per-assay CSV (benchmarks/DMS_zero_shot/substitutions/Spearman/DMS_substitutions_Spearman_DMS_level.csv at PG_v1.3). Only the script's version reproduces the paper, for all 5 models (runs/check_aggregation.log).
   - **ESM-1b scoring rule.** Appendix A.4.1 (Zero-shot baselines), p.33, says ESM models are scored with masked-marginals. scoring_ESM1b_substitutions.sh uses wt-marginals with overlapping windows (Brandes et al.). Before the full run we tested both on two assays, of 852 aa and 1863 aa (runs/results/probe_esm1b.log):
     - Wt-marginals matched the authors' released ESM-1b scores (Spearman 1.000000).
     - Masked-marginals did not (0.971 and 0.977).

     compute_fitness.py does not implement masked-marginals with overlapping windows: it exits with "Overlapping not yet implemented for masked-marginals". So the masked-marginals probe used the single 1024-token "optimal" window (runs/logs/probe_ESM1b_masked.log). On the 852 aa assay that is plain masked-marginals. On BRCA1 (1863 aa) it is a hybrid that neither the paper nor the scripts describe, so that comparison is not a test of the paper's exact method. Following the rule in claims.md, wt-marginals is the primary method.
2. **Environment.** Python 3.10, torch 1.13.1+cu117, numpy 1.24.4, pandas 1.5.1, scipy 1.10.1, scikit-learn 1.3.2 and biopython 1.82. env/requirements.in pins the packages that the scoring and evaluation scripts import, at the versions in the repo's environments/proteingym_env.txt. torch is the +cu117 build of 1.13.1. env/setup.sh builds the environment with uv from env/requirements.lock. torch sees the GPU (runs/env_setup2.log). We left transitive dependencies to the resolver, so some differ from proteingym_env.txt (runs/logs/revision_checks.log):
   - python-dateutil 3.0.0 (2.8.2 in the authors' file);
   - pytz and tzdata 2026.5 (2022.6 and 2023.4);
   - joblib 1.6.0 (1.2.0);
   - threadpoolctl 3.7.0 (3.1.0);
   - six 1.17.0 (1.16.0).

   Given the per-mutant agreement above, they very likely have no effect.
3. **Scoring.**
   - We used the authors' proteingym/baselines/esm/compute_fitness.py unchanged. runs/score_driver.py calls it with the same arguments as the authors' shell scripts:
     - ESM2: masked-marginals, default "optimal" window;
     - ESM-1b: wt-marginals, overlapping windows.
   - The driver only changes how the work is run:
     - it loads each checkpoint once instead of once per assay;
     - it writes through a temporary folder;
     - it skips finished assays, so a cut run can resume.
   - runs/evaluate.py does the evaluation and follows performance_DMS_benchmarks.py. On the authors' per-mutant scores it gives the paper's numbers to rounding (runs/results/authors_scores_summary.log).
4. **GPU time on the RTX 2070 SUPER.** ESM-1b 0.2 h, ESM2 8M 0.7 h, 35M 1.1 h, 150M 2.3 h, 650M 4.9 h. Part of each run is CPU time in the pandas `apply` call inside compute_fitness.py. HIS7_YEAST_Pokusaeva_2019 alone (496,137 mutants) takes 5 to 9 minutes depending on the model: 8M 527 s, 35M 532 s, 150M 492 s, 650M 315 s, ESM-1b 319 s.

**Changes needed**
- We made no change to the authors' code, so there is no patches/ folder.
- PYTHONPATH must point to the repo root. The ESM-1b loader in the vendored esm package runs `from proteingym.baselines.esm import esm`, which only works if the repo is installed as a package (`pip install -e .`). The scoring scripts do not say so. Without it, ESM-1b fails with ModuleNotFoundError.

**Recovery after a power cut.** A power outage cut an earlier attempt in this folder during setup. Resuming the downloads and checking file sizes was not enough:
- The scores zip failed a CRC check on one entry (D7PM05_CLYGR_Somermeyer_2022.csv). It had 131,072 bad bytes near where the first download had stopped.
- esm1b_t33_650M_UR50S.pt differed from the server copy from byte 1,506,803,713 on, and torch.load failed on it.

The two files were fixed in different ways:
- **Scores zip** (env/repair_scores_zip.sh, runs/repair_scores_zip.log): we re-fetched the 22 MB range around the bad entry (bytes 183,000,000 to 205,000,000) and patched it in. The zip then passed a CRC test of every entry. The rest of the 1.9 GB file was not compared byte for byte with the server.
- **ESM-1b weights** (env/repair_esm1b.sh, runs/repair_esm1b.log): we re-fetched bytes 1.40 to 1.70 GB and patched them in, then compared the whole file byte for byte with the server copy. It is identical.

The ESM2 8M/35M/150M files written before the cut were compared with the server copies and are identical (runs/verify_weights.log). The SHA256 of every file is in data/weights/SHA256SUMS and sources/SHA256SUMS.

## Why five ESM2 assays differ from the released scores (analysis chosen after seeing the data)

reference_files/DMS_substitutions.csv gives an MSA region (MSA_start/MSA_end) for each assay. The five assays are exactly the five long proteins (over 1022 aa) whose MSA covers only part of target_seq.

- **target_seq did not change between versions.** For all five assays, the length and hash of target_seq are the same in the reference files of v1.0, v1.1 and v1.3 (runs/check_reference_versions.py, runs/logs/check_reference_versions.log). So a sequence change between PG versions does not explain the difference.
- **The released scores come from the MSA region only.** We re-scored the five assays on target_seq[MSA_start-1:MSA_end], offsetting mutant positions by MSA_start. No window is needed at that length. This reproduces the authors' released ESM2 scores for all four sizes: Spearman 1.000000 and a largest difference of 8.3e-5 or less (runs/logs/msa_region_hypothesis.log). In that log, the 150M and 650M lines carry a model label. The 8M and 35M blocks have none, because they came from an earlier version of runs/msa_region_hypothesis.py that we did not keep. They are the first and second blocks, in the order set by msa_region_hypothesis.sh, and msa_region_substitution.py reads them in that order.
- **With that change, our averages match the authors' exactly.** Scoring those five assays this way gives 0.2257 / 0.3208 / 0.3868 / 0.4138, the same as the authors' values (runs/results/msa_region_substitution.log).
- **Other settings do not match.** Scoring the full sequence in one pass, or with a 1022-token window, does not reproduce the released scores (runs/logs/window_hypothesis_8M.log).

At PG_v1.3, compute_fitness.py cuts the sequence down to the MSA region only for MSA Transformer. For ESM2 it scores the full target_seq with the 1024-token "optimal" window, and that is what we ran. So for these five assays, the released ESM2 scores come from a different setting than the released code. ESM-1b is not affected: its released scores match a full-sequence run.

Per-assay Spearman, ours (released code) / authors' (released scores), from runs/results/five_assays_table.log:

| Model | KCNH2 | SCN5A | POLG_HCVJF | POLG_CXB3N | ZIKV |
|---|---|---|---|---|---|
| ESM2 8M | -0.140 / 0.253 | 0.121 / 0.216 | 0.099 / 0.101 | -0.074 / -0.079 | -0.073 / -0.073 |
| ESM2 35M | 0.320 / 0.197 | 0.157 / 0.177 | 0.137 / 0.128 | -0.056 / -0.056 | -0.058 / -0.054 |
| ESM2 150M | 0.560 / 0.229 | 0.138 / 0.156 | 0.102 / 0.114 | 0.167 / 0.177 | -0.049 / -0.058 |
| ESM2 650M | 0.512 / 0.280 | 0.121 / 0.183 | 0.133 / 0.116 | 0.393 / 0.395 | 0.215 / 0.213 |

KCNH2 has 200 mutants at 11 positions (545-555), inside a 31-residue MSA region (535-565). Its Spearman moves by up to 0.39. The effect on the corrected average is small because of how the average weights proteins. Each of these assays is the only one for its protein and function type. A protein weighs 1/5 × 1/(number of proteins in its function type). KCNH2 is in Activity (40 proteins), so it weighs 0.5% of the corrected average. The other four are in OrganismalFitness (64 proteins), so each weighs 0.31% (runs/logs/revision_checks.log).

Not done: ESM-1b with masked-marginals on all 217 assays, which is what the paper's wording describes. We stopped that run at its start for time (runs/logs/ESM1b_masked.log). As a reference for its cost:
- ESM2 650M, a model of the same size, took 4.9 h with masked-marginals.
- On the two probe assays, ESM-1b took 268 s and 566 s with masked-marginals, against 69 s and 67 s with wt-marginals.

On the two probe assays, masked-marginals gives 0.461 and 0.485, against 0.456 and 0.494 for wt-marginals. On BRCA1 this is the single-window hybrid described in step 1.

## A second, independent run

The same paper was also run through our full pipeline, in a separate folder and without access to this run: a claims map pre-registered before any model ran, execution, blind recomputation by a different agent with scoring code written from scratch, adversarial review and revision. That report is in [pipeline/REPORT.md](pipeline/REPORT.md). Its own verdict is "Partially reproduced" for process reasons: its execution stage was cut by a machine restart for ESM-1b and, by our mistake, ran a 30-assay sample for the larger ESM2 sizes.

Its blind recomputation ran all 217 assays and lands on the same numbers as this report: ESM-1b 0.3941, ESM2 8M 0.2235, 35M 0.3214, 150M 0.3884 (650M only on a 54-assay sample). It also checked four more ESM-1b metrics against Table A5, all within tolerance: AUC 0.7188 (paper 0.719), MCC 0.3109 (0.311), NDCG@10% 0.7467 (0.747) and top-10% recall 0.2021 (0.203). It found the same three points independently: the protein-first average, the ESM-1b wt-marginals rule, and the five MSA-region assays.

## Notes for the authors

Thanks for releasing per-mutant scores for every model. They let us check each assay, not only the averages. Here is what we ran into:

1. **Released ESM2 scores vs released code, 5 assays.** For KCNH2_HUMAN_Kozek_2020, SCN5A_HUMAN_Glazer_2019, POLG_HCVJF_Qi_2014, POLG_CXB3N_Mattenberger_2021 and A0A140D2T1_ZIKV_Sourisseau_2019, the ESM2 scores in zero_shot_substitutions_scores.zip (v1.3) come from scoring only the MSA region (MSA_start..MSA_end). compute_fitness.py with scoring_ESM2_substitutions.sh scores the full target_seq instead. Someone who reruns the code gets different per-assay numbers: for KCNH2 with ESM2 8M, -0.140 instead of 0.253. Could the script or the docs say which one is intended?
2. **ESM-1b scoring rule.** Appendix A.4.1 (Zero-shot baselines, p.33) says ESM models are scored with masked-marginals. The released ESM-1b scores and scoring_ESM1b_substitutions.sh use wt-marginals with overlapping windows. This is the same point as issue #99, and a one-line fix in that section would close it.
3. **Corrected average.** §4.1 and A.5.1 describe averaging assays within each function type. The published numbers average per UniProt ID first (performance_DMS_benchmarks.py). With your own per-assay CSV and the text's definition, ESM2 650M would be 0.418 instead of 0.414, and ESM-1b 0.398 instead of 0.394. Adding the protein step to the text would fix this.
4. **Table A7 vs Table 2.** Table A7 gives ESM-1b "All" = 0.399, with per-function values 0.428/0.289/0.427/0.351/0.500. These match Summary_PG_v1.0.csv. The per-assay CSVs of v1.0, v1.1 and v1.3 all aggregate to 0.394 for ESM-1b, as in Table 2 and Table A5. So in v1.0 the summary file disagrees with its own per-assay file. A related detail: the Table A5 ESM-1b standard error (0.010) matches Summary_PG_v1.0 (0.01), not v1.1 (0.009) or v1.3 (0.012).
5. **Table A5 "Std. error".** As the caption says, this is the bootstrap SE of the difference to TranceptEVE, not the SE of each model's score. It is easy to read it as the second.
6. **ESM-1b needs the package installed.** The vendored esm loader imports `proteingym.baselines.esm`, so ESM-1b needs `pip install -e .` or PYTHONPATH set to the repo root. The scoring script does not mention this.
7. **Checksums.** Publishing MD5 or SHA256 values for the zips on marks.hms.harvard.edu would help people catch corrupted resumed downloads, which is what happened to us.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand: each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

A single agent read the paper, built the environment, ran the authors' code and released weights on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X, compared the results with the paper and wrote this report. A reviewer agent then checked the report against the logs, a reviser agent corrected it, and a human approved publication. This run itself had no blind recomputation; the independent pipeline run above provides one.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues