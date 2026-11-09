# Reproduction report: The NANOGrav 15 yr Data Set: Evidence for a Gravitational-wave Background

- Paper: G. Agazie et al. (NANOGrav Collaboration), ApJL 951:L8 (2023). DOI 10.3847/2041-8213/acdac6, arXiv 2306.16213 (PDF sha256 3a33495a...785aeb, `logs/get_paper.log`)
- Code and data: https://github.com/nanograv/15yr_stochastic_analysis (MIT) @ a3e8b8776a646208ca2d307f83c20bc70e029933 (2025-08-11), including its git history.
- Mode: analysis of the authors' published products: la_forge cores, data_release files, and one chain recovered from the repo's git history. No sampling was re-run.
- Target: the headline amplitude A_GWB = 2.4 +0.7/-0.6 x 10^-15 at 1/yr (HD power law, gamma = 13/3, median and 90% interval). Secondary: the Bayes factors of Fig. 2 and the abstract.
- Verdict: **Reproduced**, under the frozen verdict rule. The source of C1 was changed after the freeze; see "Source of C1".
  - C1, read from the authors' headline chain in the repo history, gives the paper's numbers exactly.
  - Three secondary claims can be computed (S1, S2, S3b), and all three land inside their bands.
  - Three are not tested: S3 as pre-registered, S4 and S5.
- Date: 2026-11-08. Pre-registration frozen 23:29:19 (`logs/claims_frozen_at.txt`).
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu 24.04, CPU only, `nice -n 19`. The GPU was not touched.

## What this run can and cannot show

We read the chains the authors posted and recomputed the summary numbers with their own post-processing: percentiles, the product-space weight correction, their thermodynamic-integration function, the phase-shift count. A pass means the published numbers follow from the published chains. It says nothing about the timing data, the noise models, the likelihood, the priors as coded or whether the samplers converged. Those would need the sampling re-run, which takes weeks of CPU and was not attempted.

**These are not blind tests.** The bands come from the paper's printed digits. For C1, S1, S2, S3, S3b, E1 and E4, the authors' stored notebook outputs were known before the freeze, and `claims.json` quotes them. So those claims check the post-processing and the products, not a hidden number.
- C1: 2.4039e-15, from `lower_left.ipynb`.
- S1: 12.1139.
- S2: derivable from the lnZ values in `model_selection.ipynb` cell 39.
- S3: 202.22.
- S3b: 198.0.
- E1: gamma 3.2492.
- E4: 7.85e-4.

Only E2, E3 and the `curn_hd` amplitude were unknown in advance. The E1 gamma band, [3.15, 3.25], also does not follow the rounding-plus-0.05 rule `claims.json` states for it; that rule gives [3.1, 3.3].

**The README caveat covers the cores, as written.** The README says the data in `tutorials` "have been reduced to make them available on GitHub and may not reproduce the results of the 15-year analysis exactly". The cores sit in `tutorials/presampled_cores/`, and nothing limits the sentence to the par/tim files, so the triage reading was not supported. Two other signs point the same way. The TI cores keep "only the likelihood parameter" (`model_selection.ipynb`, cell 32). The presampled varied-gamma core is a different chain from the one behind Fig. 1b: 6.329e-15 against 6.385e-15 (E1).

## Source of C1

The chain behind the headline, `nano15_hd_chain_fg_long_050523.npy`, was in the GitHub repo and is still in its history. `data_release/figure_1/figure1_data/` was added in 99439792 ("add data, fig 1 changes", 2024-02-08, `logs/cores_missing_before_freeze.log`) and removed in 98a4783 ("remove figure 1 data", 2024-02-11). The blob is 4923521acfd3027c1d264eb85225f62f813a4271, 1,511,832 bytes. Today the README in `data_release/figure_1` points to a Google Drive download instead.

The file was extracted from the local object store by the reviewer, with `GIT_NO_LAZY_FETCH=1`. We recomputed its git blob id from the file bytes, and it matches the tree of `98a4783^`. The same holds for `nano15_hd_chain_long_050523.npy` (ea702c6e...), `14f_PL_hd_crn.core` (e9022d69...) and `optstat_ml_gamma4p33.json` (81eaef37...). The pack list was identical before and after that run, so nothing was fetched (`runs/c1_history_blob.log`).

**Deviation from the pre-registration.** Before the freeze we did not know the chain was in the history, and `claims.json` excluded the Drive copy. The choice of source was made after the freeze, on the coordinator's instruction after the adversarial review. It is the same file the authors' `lower_left.ipynb` reads, labelled "Fixed gamma=13/3" there, and it now comes from the named source. The computation method and the bands are the frozen ones.

The first draft used the HD branch of `curn_hd.core` for C1. `claims.json` had listed `curn_hd` as varied gamma, and reading its HD branch as an hd13/3 chain was a post-freeze reading of the rule. That result has moved to the extras (E5).

## Results

`claims.json`, sha256 80d24441...c98acb, was unchanged at the end (`runs/c1_history_blob.log`). C1 comes from `runs/c1_history_blob.log` and `runs/c1_history_blob.json`. Everything else comes from `runs/compute_claims.log` and `runs/results.json`.

### Primary

| Claim | Paper | Ours (history blob) | Pre-registered band | Inside |
|---|---|---|---|---|
| C1 A_GWB, hd13/3, median | 2.4e-15 | 2.40392e-15 | [2.3, 2.5]e-15 | yes |
| C1 5% | 1.8e-15 (2.4 - 0.6) | 1.81521e-15 | [1.7, 1.9]e-15 | yes |
| C1 95% | 3.1e-15 (2.4 + 0.7) | 3.06892e-15 | [3.0, 3.2]e-15 | yes |

This is `numpy.percentile` (linear) of 10**x over all 188,963 samples. The array is already post-processed, so no burn-in was applied. The interval is +0.665/-0.589 x 10^-15. The integrated autocorrelation time is 77.8, which gives about 2,428 effective samples. The batch-means standard error of each quantile is 0.007 to 0.009 x 10^-15. Every number equals the authors' stored output in `lower_left.ipynb`. The paper's "+0.7/-0.6" rounds +0.665/-0.589. The varied-gamma long chain from the same commit gives A = 6.385e-15 [3.700, 10.559] and gamma 3.248 [2.660, 3.840], against the paper's 6.4 +4.2/-2.7 and 3.2 +- 0.6.

### Secondary

| Claim | Paper | Ours | Band | Inside |
|---|---|---|---|---|
| S1 log10 BF, CURN_gamma vs IRN (TI) | 12.1 +- 0.1 (Fig. 2) | 12.114 +- 0.085 | [11.9, 12.3] | yes |
| S2 log10 BF, HD vs IRN (TI) | "in excess of 10^14" (abstract) | 14.409 +- 0.104 | > 14 | yes (also central - 2 sigma > 14) |
| S3b BF HD_gamma vs CURN_gamma (TI, `hd_ti` vs `curn_ti`) | 226 +- 70 | 197.2 (log10 2.295 +- 0.099; 1 sigma 156.9 to 247.7) | [156, 296] | yes |
| S3 BF HD_gamma vs CURN_gamma, product space | 226 +- 70 | not tested: `curn_hd.core` is a fixed-gamma run (below) | | |
| S4 BF HD vs CURN, 5 frequencies | 965 (Fig. 2) | not tested: no 5-frequency core is published | | |
| S5 BF hd13/3 vs curn13/3 | "similar" (Sec. 3), no number | not tested: no number in the paper. `curn_hd` gives 202, roughly +-20, which supports "similar" | | |

The TI values use the authors' `ti_log_evidence()` unmodified, with `extra_functions.rng` replaced by seeded generators (seeds 1, 2, 3). The ln-evidences are irn 7972999.672 +- 0.148, curn 7973027.567 +- 0.129 and hd 7973032.851 +- 0.188. `ti_sample.py` builds the TI runs with `model_2a`/`model_3a` and varied gamma, so S3b is the real test of the HD_gamma vs CURN_gamma claim.

**Why S3 is not tested.** S3 was pre-registered from `curn_hd.core`, because the tutorial builds that run with `model_general(..., common_psd='powerlaw')`. In enterprise_extensions 3.0.3 that call has `gamma_common=None` (`models.py:811`) and passes it on as `gamma_val` (`models.py:1080`), i.e. varied gamma. The core, though, is a fixed-gamma run:
- It has all 141 expected columns: 134 pulsar parameters, `gw_crn_log10_A`, `gw_hd_log10_A`, `nmodel`, `lnpost`, `lnlike`, `chain_accept` and `pt_chain_accept`. So it was not cut down, and it has no common gamma column.
- In ee 3.0.3 a fixed gamma becomes `parameter.Constant(gamma_val)` (`blocks.py:306-307`), and Constant parameters are not saved to the chain (`runs/c1_history_blob.log`, `runs/inspect_cores.log`).
- Its HD-branch p95, 3.147e-15, lies below the p05 of the varied-gamma core, 3.780e-15.
- The authors' CURN 13/3 maximum-likelihood point, log10 A = -14.673, falls at about the 5th percentile of the CURN branch, at the edge of its 90% interval. A varied-gamma CURN sits near -14.17. That is consistent with gamma fixed at or near 13/3, but it is not a close match.

Its BF, 202.22 = 6,037 / 8,956 x 300, is therefore an hd13/3 vs curn13/3 number. The notebook-style bootstrap error, +-3.39, assumes independent samples. Accounting for the autocorrelation gives about +-17 to 19 from the effective sample size, and 23 to 25 by batch means (reviewer, `review_scratch/r2.log`).

### Extras (not in the verdict)

| Extra | Reference | Ours |
|---|---|---|
| E1 presampled vg core `hd_14f_pl_vg`, A median [5, 95] | 6.4 +4.2/-2.7 e-15 | 6.329e-15 [3.780e-15, 1.0404e-14]; inside [6.3, 6.5]e-15 |
| E1 gamma | 3.2 +- 0.6 | 3.249 [2.687, 3.832]; inside [3.15, 3.25], a band set off-rule (see above) |
| E2 free-spectrum refit at gamma = 13/3 (`hd_30f_fs`, bins 1-14, factorized likelihood) | 2.4 +0.7/-0.6 e-15 | 2.485e-15 [1.867e-15, 3.111e-15] |
| E3 vg core sliced at abs(gamma - 13/3) < 0.1 | | 2.508e-15 [2.330, 3.003]e-15 from only 10 samples |
| E4 Bayesian phase-shift p-value (`pshift_bfs.npy`, fraction > 226) | 10^-3 | 4 / 5,097 = 7.85e-4; inside [5e-4, 1.5e-3] |
| E5 `curn_hd.core` HD branch (formerly C1) | 2.4 +0.7/-0.6 e-15 | 2.4420e-15 [1.8788e-15, 3.1473e-15], 6,037 samples, about 210 effective |

On E5:
- It falls inside the C1 bands, but the p05 sits 0.021e-15 below the 1.9e-15 edge. Its batch-means standard error is 0.027 to 0.034e-15 (`review_scratch/r4.log`), so the margin is within one standard error.
- It is a shorter chain than the headline chain. The KS distance between them is D = 0.069 (`review_scratch/r1.log`); with about 210 effective samples, that difference is not significant.

E2 matches C1 to within 0.1e-15 by an independent route, from a different core.

## Independent blind rerun

A second agent redid the analysis in a separate folder (published here as `blind/`) without access to this folder, this report or our pre-registration. It was given the paper, the repository and the claims, and was not allowed to download from Google Drive or any other host. It made a full normal clone, wrote and froze its own `claims.json` (SHA-256 `82bf67d9a071f8b3da9dc43801232d50f15bb70baa398d117fc355eea9379cfd`, 2026-11-08T23:43:16−03:00) before opening any chain, pinned an older stack (numpy 1.24.4, scipy 1.10.1, against our 2.2.6 and 1.15.3) and wrote its own scripts.

| Claim | Paper | This run | Blind run |
|---|---|---|---|
| C1 A, hd13/3, median [5%, 95%] | 2.4 +0.7/−0.6 e-15 | 2.40392 [1.81521, 3.06892] e-15 | 2.40392 [1.81521, 3.06892] e-15 |
| S1 log10 BF CURN vs IRN (TI) | 12.1 ± 0.1 | 12.114 ± 0.085 | 12.110 ± 0.086 |
| S2 log10 BF HD vs IRN (TI) | > 14 | 14.409 ± 0.104 | 14.406 ± 0.105 |
| S3b BF HD vs CURN (TI) | 226 ± 70 | 197.2 | 197 |
| BF HD vs CURN, `curn_hd.core` | 226 ± 70 | 202.22 (not tested as S3; supports S5) | 202.2 (flagged as fixed-gamma) |

The TI values differ in the third decimal only through the bootstrap seeds. Both runs read the C1 chain from the same file: the blind run extracted it from its own full clone, ours from the reviewer's local object store, and the two copies have the same SHA-256 (`8468b1ef…0b113`).

Its verdict is "Reproduced", like ours. It found independently that `curn_hd.core` is a fixed-gamma chain and that the notebook's ±3.4 ignores autocorrelation (block bootstrap ±20.7). It also added two findings this run did not have, both now in the notes below: the authors' TI quadrature differs from a plain trapezoid in β by 0.35 dex, and `ti_sample.py` opens files the repository does not ship.

**One hint, disclosed.** The blind run's first version marked C1 "not tested": like ours, it looked only at the current tree and found the Figure 1 data only behind a Drive link. The coordinator then told it that the Figure 1 data were committed and removed in 98a4783 and which file `lower_left.ipynb` reads, with no number. Its band and rule were not changed. So for C1 the two runs are independent in code and in computation, but not in finding the file.

## What it took

1. **Paper.** `scripts/get_paper.sh`: curl with TLS verification on. Text extracted with pypdf 4.3.1 (`scripts/env_pdf.sh`).
2. **Repo, without the cores.** `scripts/clone_sparse.sh` ran a `--filter=blob:none` clone with a sparse checkout that excluded `tutorials/presampled_cores/`. **Process slips before the freeze:**
   - The `git ls-tree -r -l` in `clone_sparse.sh` fetched blobs one at a time, including 2 core blobs (`curn_14f_pl_vg`, `curn_hd`), before it was stopped.
   - The presence check `scripts/cores_missing.sh` (`git cat-file -e`) then fetched the other 6 (`logs/cores_missing_before_freeze.log`).
   - None was checked out or decoded before the freeze. `claims.json` comes only from the README, the notebook text and file names.
3. **Reading before the freeze.** `scripts/nb_dump.py` dumped the notebooks to `logs/nbdump_*.txt`.
4. **Freeze.** `claims.json` and `claims.sha256` at 23:29:19.
5. **Cores.** `scripts/checkout_cores.sh` recorded sizes and sha256 (`logs/checkout_cores.log`).
6. **Environment.** `scripts/setup_env.sh`: uv venv, Python 3.10.22, la_forge 1.1.0, numpy 2.2.6, scipy 1.15.3, h5py 3.16.0, emcee 3.1.6, matplotlib 3.10.9. Lockfile `env/requirements.lock`; cache `env/uv-cache`. Conda and enterprise were not needed. enterprise_extensions 3.0.3 was installed with `--no-deps` into `env/ee_src`, only to read its source.
7. **Inspection.** `runs/inspect_cores.sh`, `runs/inspect_meta.sh` and `runs/fs_range.sh`, each with a `.log`.
8. **Claims.**
   - `runs/compute_claims.sh` and `.py` write `runs/compute_claims.log` and `runs/results.json`.
   - The first run crashed at E3 on a duplicated dict key. Its log was overwritten and not kept.
   - The run with free-spectrum edges [-9, -4] is kept as `runs/compute_claims_E2edges-9.log`. The script was then edited in place to [-15.5, -4], the fallback the pre-registration allows, so that earlier version of the `.py` was not saved. E2 moved only in the 8th digit.
   - Some scripts set OMP/OpenBLAS/MKL threads to 6; `runs/fs_range.sh` set no limit.
9. **Revision run.** `runs/c1_history_blob.sh` and `.py` write `runs/c1_history_blob.log` and `.json`. They produce C1 from the history blob, verify the blob ids, and log the ee source lines, the pack lists and the folder size.
10. **The reviewer's fetch.** During the review, a `git show --stat 98a4783` lazily fetched two packs, about 219 MB, into `sources/repo/.git/objects` (`pack-dd43f30c...`, plus the small `pack-b5504016...`). They were left in place. The history blobs used here came from that store.
11. **Cleanup.** The WSL root holds only system folders (`logs/check_ee_and_hash.log`). The work folder is 1.3 GB (`runs/c1_history_blob.log`).

## Notes for the authors

Thanks for posting the chains and the per-figure notebooks with their outputs. Because of them, every number here could be checked against both the paper and your own printed values. A few things came up:

1. **The Fig. 1 chains are only in git history and on Drive.** `data_release/figure_1/figure1_data/` was removed in 98a4783 (2024-02-11) and now points to a Google Drive download. Read from the history blob, `nano15_hd_chain_fg_long_050523.npy` gives exactly 2.4039 +0.665/-0.589 e-15. A versioned archive, Zenodo for example, would make these chains easy to find and cite.
2. **`curn_hd.core` does not record its gamma, and the tutorial builds a different model.** The notebook constructs both PTAs with `model_general(..., common_psd='powerlaw')`, which varies gamma by default. The core has no gamma column, and its amplitudes put it at fixed gamma, most likely 13/3. If so, the tutorial's "202" is hd13/3 vs curn13/3, while Fig. 2's 226 +- 70 is labelled HD_gamma vs CURN_gamma. A line in the notebook or a metadata field in the core would settle it. The notebook's +-3.4 also treats correlated samples as independent: with autocorrelation it is roughly +-20.
3. **The README caveat covers the cores, as written.** "Data used in the tutorials section ... have been reduced" applies to `tutorials/presampled_cores/` too. Saying which cores are production chains, which are shortened (the presampled vg core is not the Fig. 1b chain), and that the TI cores keep only `lnlike` would help anyone citing them.
4. **Prior ranges in the cores vs Table 1.**
   - In `curn_hd.core`, `gw_hd_log10_A` reaches -11.001, the ee default upper edge (`Uniform(-18, -11)`, `blocks.py:1373`), while Table 1 lists log-Uniform[-18, -14] for gamma = 13/3. The HD-branch posterior never goes above -14.457, so the amplitude is not affected.
   - In `hd_30f_fs.core`, `log10_rho` samples reach about -15.5 in most bins; bins 2 and 3 bottom out at -14.97 and -15.19 (`runs/fs_range.log`). Table 1 gives rho_i [s^2] log-Uniform[-18, -8], i.e. log10 rho in [-9, -4], the range your `upper_left.ipynb` uses for `rho_bins`. Was the tutorial free spectrum run with a wider prior than the paper's?
5. **Phase-shift count.** The text (Sec. 3) says the observed Bayes factor is exceeded in five of 5,000 phase shifts. The posted `pshift_bfs.npy` has 5,097 values, 4 of them above 226 (`runs/compute_claims.log`), which gives p = 7.85e-4. Is the posted file a different set from the one in the paper?

6. **TI quadrature uncertainty** (found by the blind run). On the shipped TI cores, `ti_log_evidence` gives log10 BF(CURN/IRN) = 12.11 ± 0.09. A plain trapezoid in β over the same per-temperature means gives 12.49, and HD/IRN moves from 14.41 to 14.70. The ladder is geometric with a step of 1.71× near β = 1, where ⟨ln L⟩ changes by 20 to 110 per step, so the integration rule moves each log-evidence by 2 to 3 nats. The 0.35 dex shift is larger than the quoted ±0.1, which comes from the bootstrap alone. The conclusions hold either way. Should the Fig. 2 uncertainty include a quadrature term, or the ladder be denser near β = 1?
7. **`ti_sample.py` opens files that are not shipped** (found by the blind run): `data/v1p1_wn_dict.json` and `data/emp_distr.pkl`. The tutorials folder has `15yr_wn_dict.json` and `15yr_emp_distr.json`, so the script does not run from a fresh clone.

## How this report was made

This run was done by an AI agent (Claude, by Anthropic) on a home computer. The pre-registration and the computation were done by the same agent. An adversarial reviewer agent checked the first draft (`REVIEW.md`, scripts in `review_scratch/`), and this version applies its findings. C1 was recomputed by this agent from the file, not copied from the reviewer. The blind recount by a second agent agrees (section above). Still outstanding: a human reading. Every number above comes from a log or output file in this folder, with two exceptions, each labelled where it appears: the authors' stored notebook outputs, quoted from their notebooks, and the reviewer's numbers, cited to `review_scratch/`.
