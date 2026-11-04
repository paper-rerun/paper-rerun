# Reproduction report: Population of Merging Compact Binaries Inferred Using Gravitational Waves through GWTC-3

- Paper: R. Abbott et al. (LIGO Scientific, Virgo and KAGRA Collaborations), Phys. Rev. X 13, 011048 (2023). DOI: 10.1103/PhysRevX.13.011048 (arXiv 2111.03634v5)
- Code: https://git.ligo.org/RatesAndPopulations/gwpopulation_pipe @ 83c9bb97a755690a2d42930ff4ae43f239254cc2, with gwpopulation 0.6.3 from PyPI (sdist sha256 61f521e8...b28895). Both versions are the ones recorded in `meta_data.loaded_modules` of the published result. Library repo: https://github.com/ColmTalbot/gwpopulation
- Data: Zenodo 11254021 (GWTC-3 population data release v3, `analyses_PowerLawPeak.tar.gz`, md5 85c3b659...cb36) and Zenodo 5636816 (injections `o1+o2+o3_bbhpop_real+semianalytic-LIGO-T2100377-v2.hdf5`, md5 c21337a2...547e). Size and md5 checked for both.
- Target: POWER LAW+PEAK run (`o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift`, 69 BBH events). Primary claims are the Gaussian peak location mu_m = 34 +2.6/-4.0 Msun (Sec. VI.A) and the BBH merger rate R(z=0.2) = 28.3 +13.9/-9.1 Gpc^-3 yr^-1 (Table IV and Table XVI, row PP). Secondary: alpha, beta_q, kappa from the same run.
- Verdict: **Reproduced**
- Scope: the hierarchical inference and the rate step, run on the authors' released per-event arrays and injection set. Event selection and PE downsampling were not redone.
- Date: 2026-11-04
- Hardware: Ryzen 9 3900X, RTX 2070 SUPER 8 GB, WSL2 Ubuntu 24.04 (31 GB RAM visible to WSL)

## Results

We reran the full hierarchical inference (dynesty over the 13 hyper-parameters) and the authors' rate post-processing twice, with seeds 101 and 202. The verdict rule in `claims.json` compares the two primary claims with the published posterior (`result.json` from the data release). The tolerances were fixed before any run. Values are the median and the 5th/95th percentiles.

**Primary claims** (pre-registered tolerances vs the released result):

| Quantity | Paper | Released result (re-read) | Ours, seed 101 | Ours, seed 202 | Diff vs released (101 / 202) | Within tolerance |
|---|---|---|---|---|---|---|
| mu_m [Msun], median | 34 | 33.563 | 33.563 | 33.491 | -0.001 / -0.072 (tol 0.5) | yes / yes |
| mu_m, 5% | 30.0 | 29.515 | 29.164 | 29.293 | -0.351 / -0.222 (tol 0.8) | yes / yes |
| mu_m, 95% | 36.6 | 36.207 | 36.157 | 36.204 | -0.050 / -0.003 (tol 0.8) | yes / yes |
| R(z=0.2) [Gpc^-3 yr^-1], median | 28.3 | 28.221 | 28.391 | 28.297 | +0.169 / +0.075 (tol 2.0) | yes / yes |
| R(z=0.2), 5% | 19.2 | 19.287 | 19.375 | 19.179 | +0.088 / -0.108 (tol 1.5) | yes / yes |
| R(z=0.2), 95% | 42.2 | 42.051 | 41.379 | 41.648 | -0.672 / -0.403 (tol 3.0) | yes / yes |

Both runs also pass both primary claims against the printed paper values, using the pre-registered "vs paper" tolerances. The closest call is the 5% edge of mu_m in seed 101. It is 29.164 against the paper's 30.0, a gap of 0.836 with a tolerance of 0.85. The released posterior itself sits 0.485 below the printed 30.0 at that edge, so most of that gap is already in the authors' own result.

**Secondary claims.** `claims.json` pre-registers tolerances for these against the paper only: the median within 0.25 sigma and the edges within 0.4 sigma, with sigma taken from the paper's interval. Values are median [5%, 95%]. Each difference is given as median / 5% / 95%.

| Quantity | Paper | Ours, seed 101 | Ours, seed 202 | Diff vs paper, seed 101 | Diff vs paper, seed 202 | Tolerance (median / edges) | Within tolerance |
|---|---|---|---|---|---|---|---|
| alpha | 3.5 [2.94, 4.10] | 3.524 [2.978, 4.115] | 3.513 [2.975, 4.089] | +0.024 / +0.038 / +0.015 | +0.013 / +0.035 / -0.011 | 0.09 / 0.14 | yes / yes |
| beta_q | 1.1 [-0.20, 2.80] | 1.067 [-0.269, 2.698] | 1.070 [-0.183, 2.783] | -0.033 / -0.069 / -0.102 | -0.030 / +0.017 / -0.017 | 0.23 / 0.36 | yes / yes |
| kappa | 2.9 [1.10, 4.60] | 2.857 [1.082, 4.643] | 2.862 [1.038, 4.697] | -0.043 / -0.018 / +0.043 | -0.038 / -0.062 / +0.097 | 0.27 / 0.43 | yes / yes |

As an informal check that was not pre-registered, we also compared the secondaries with the released posterior, using the same tolerances taken from the paper. The released values are alpha 3.515 [2.959, 4.114], beta_q 1.095 [-0.188, 2.787] and kappa 2.875 [1.108, 4.615]. Every difference is within those tolerances. The largest are -0.089 (beta_q 95%, seed 101) and +0.081 (kappa 95%, seed 202).

Our two seeds differ from each other by at most 0.13 Msun (mu_m) and 0.27 Gpc^-3 yr^-1 (R(0.2) percentiles). Both are well inside the pre-registered tolerances, which shows the tolerances were not too tight.

The published posterior has 11,184 samples and our runs have 11,141 and 10,829. Full per-claim output is in `runs/evaluation.log` and `runs/evaluation_summary.json`.

### Check before sampling: the likelihood is the same

Before running the sampler we evaluated our likelihood at 20 hyper-parameter samples from the published posterior (`runs/check_setup.py`, `runs/check_setup.log`). The 20 picks include two duplicated posterior rows (11183/11182 and 11181/11180 have identical values), so they cover 18 distinct points. Our log-likelihood matched the published `log_likelihood` column to within 6e-14. Of the 20 samples, 18 are bitwise identical, and the other two (5398 and 6776) differ by 5.7e-14. The surveyed hypervolume matched the published column exactly on all 20 samples. That confirms the data, the injections, the thresholds, the models and `max_redshift = 2.3` from the pre-registration. The hypervolume depends on z_max, so the value of 1.9 in the example ini would not have matched. The published `selection` column differed from ours by 0.06 to 2.6% (absolute relative difference). The cause is explained in "Notes for the authors".

## What it took

1. **Environment** (`env/setup_env.sh`, `env/requirements.in`, `env/requirements.lock`). The published run used Python 3.7.3. uv cannot fetch 3.7, so we used 3.8.20 with the recorded versions: numpy 1.19.5, scipy 1.6.3, astropy 4.0, pandas 1.0.1, h5py 2.10.0, bilby 1.1.3, bilby_pipe 1.0.4, cupy 8.4.0 and gwpopulation 0.6.3 (PyPI). The metadata records dynesty as "None", so we used dynesty 1.1, the current release in late 2021. We cloned gwpopulation_pipe from git.ligo.org and checked out 83c9bb97. After install it reports exactly the published version string, `0.2.0: (CLEAN) 83c9bb9 2021-11-07 14:45:15 -0500`. `env/fix_tables.sh` regenerated the lockfile at 03:36, after both runs had finished. The lockfile now includes `setuptools==59.8.0`, which was added at that point (item 6). The runs used this lockfile minus setuptools.
2. **GPU**. cupy 8.4.0 has no wheel for CUDA 11.2, so we used `cupy-cuda111==8.4.0`. That wheel needs the CUDA 11.1 runtime libraries, which are not on the machine. We took them as `.deb` packages from NVIDIA's public apt repository (cudart, nvrtc, nvtx, cublas, cufft, curand, cusparse, cusolver). We checked size and sha256 against the repository index (`runs/cuda_get.log`) and unpacked them into `env/cuda111/` without a system install. With those libraries cupy runs on the WSL driver. `runs/test_cupy.log` shows cupy 8.4.0 with CUDA runtime 11010 and driver API 13050. `runs/check_gpu.log` shows the driver (CUDA 13.5 UMD) and the GPU. Both logs were captured from the same environment by `runs/evidence.sh` during the report revision, after the runs. `runs/check_setup.log` was taken in that environment before the runs and reports `backend cupy`. The first attempt to use cupy failed because the runtime libraries were missing, and that attempt was not logged. There was no CPU fallback. All computation is float64, as in the original.
3. **bilby_pipe import chain**. gwpopulation_pipe imports `bilby_pipe.utils` for one helper. We installed bilby_pipe without dependencies, plus the few packages its import needs (configargparse, pycondor, gwosc, jinja2).
4. **Input data** (`runs/prep_data.py`). As pre-registered, we used the per-event arrays that the authors' likelihood actually saw. These are the `original` group of the released `_samples.hdf5`: 69 events x 3194 samples, with the `prior` column as the sampling prior. They are written in the pickle format that `gwpopulation_pipe_analysis` reads, and the script asserts that the event order equals `meta_data.event_ids`. The priors (`data/pp_published.prior`) are the ones stored in the published `result.json`, checked key by key by the same script. The run options (`data/pp_rerun.ini`) come from `example/gwtc3-bbh.ini` at 83c9bb97, except `max-redshift` (2.3, see claims.json).
5. **Runs** (`runs/run_pp.sh`, `runs/run_pp.py`). The runs call the authors' entry point `gwpopulation_pipe.data_analysis.main()` with the same command-line model lists that the authors' DAG generator builds. The only addition is `np.random.seed(seed)` before `main()`. It is meant to fix both dynesty (`rstate=None` uses the global numpy RNG) and the Gamma draw in `compute_rate_posterior`. We did not verify this by repeating a seed. The sampler settings stored in both our result files are identical to the published ones: nlive 500, rwalk, walks 5, nact 3, maxmcmc 5000, dlogz 0.1, reflective delta_m, and so on. `runs/sk.sh` compares them, and its output in `runs/sampler_kwargs_compare.log` shows zero differences for both seeds. The stored priors differ only in the LaTeX labels of alpha and beta. Single backslashes in our `data/pp_published.prior` cause this: Python reads `'$\alpha$'` as BEL + "lpha". It has no effect on the numbers, and we left the file as it was run. The two seeds ran at the same time on one GPU. GPU use, CPU load and RAM were watched by hand during the runs (`runs/status.sh` prints RAM to the terminal), but none of them were logged. The single-process timing in `runs/check_setup.log`, taken before the runs, is 29 ms per likelihood evaluation. The runs are consistent with it: 19,275 s / 649,359 calls = 29.7 ms per call for seed 101, and 18,601 s / 565,059 calls = 32.9 ms for seed 202.
     - Seed 101: 649,359 likelihood calls, sampling time 19,275 s (5.4 h).
     - Seed 202: 565,059 calls, 18,601 s (5.2 h).
     - The original run: 621,358 calls, 27,302 s on one GPU.
6. **One crash, after the numbers were saved**. Both runs wrote `result.json` (posterior, rate and n_eff columns) and then crashed in the last step, `resample_single_event_posteriors`. deepdish needs PyTables, and PyTables 3.6.1 imports `pkg_resources`, which a fresh uv venv does not include. After the runs we added `setuptools==59.8.0` to the environment (`env/fix_tables.sh`). `runs/fix_tables.log`, captured during the revision, shows that `import setuptools, tables, deepdish` now works (setuptools 59.8.0, tables 3.6.1). We did not rerun that step. It only writes the population-reweighted per-event samples, and no claim uses them.
7. **Not done**. We did not do the pre-registered sensitivity run with gwpopulation GitHub commit 5cd44c2012 (also labelled 0.6.3). The agent harness's permission settings refused the clone of that repository, and no log in this folder records that refusal. The verdict uses the PyPI build, so this does not affect it. The PyPI build matches the published likelihood to within 6e-14, which is consistent with the published run having used it. We did not test whether the other commit would also match.
8. **Logs**. On the Windows side, stdout and stderr of the two runs went to the same file through `wsl.exe`. As a result, progress bars and log lines overwrite each other in places in `runs/pp_seed101.log` and `runs/pp_seed202.log`. Run statistics are taken from the result files, not from those logs.

No source code of the authors was changed (`patches/README.md`).

## Alternative readings

This section does not change the verdict.

The authors' `compute_rate_posterior` evaluates the detection efficiency with a stale spin-magnitude shape (see Notes for the authors). We recomputed the efficiency for every posterior sample with that sample's own `alpha_chi`/`beta_chi`. We kept the same Gamma draw and recomputed R(0.2) (`runs/alt_selection_fix.py`, `runs/alt_selection_fix.log`):

| R(z=0.2) [Gpc^-3 yr^-1] | as run: p05 / p50 / p95 | own spin shape: p05 / p50 / p95 |
|---|---|---|
| Published result | 19.287 / 28.221 / 42.051 | 19.146 / 28.093 / 41.834 |
| Ours, seed 101 | 19.375 / 28.391 / 41.379 | 19.173 / 28.173 / 41.150 |
| Ours, seed 202 | 19.179 / 28.297 / 41.648 | 19.169 / 28.207 / 41.564 |

The median moves down by 0.09 to 0.22 (under 1%). That is far below the statistical width (+13.9/-9.1).

## Notes for the authors

Thanks for publishing the exact per-event arrays, the injection set and the full result files. Because of them we could rerun the analysis without rebuilding the event selection, and the likelihood matched to within 6e-14. We noticed a few things along the way:

1. **`compute_rate_posterior` uses a stale spin-magnitude shape** (gwpopulation_pipe 83c9bb97, `data_analysis.py`). The loop passes `dict(posterior.iloc[ii])` straight to `selection.detection_efficiency()` without calling `convert_to_beta_parameters`. The posterior has `mu_chi`/`sigma_chi` but no `alpha_chi`/`beta_chi`, so the VT model keeps whatever Beta shape it last held. We fitted a single pair (alpha_chi = 1.4279, beta_chi = 4.1400) on 6 rows. It reproduces the published `selection` column to 3e-15 on 6 held-out rows, out of 12 random rows checked in total (`runs/check_selection_column.log`). Together with the code path, this indicates that all rows of the published `selection`, `pdet_n_effective` and `rate` columns used that one shape. On the published result it lowers the R(0.2) median by about 0.13 Gpc^-3 yr^-1 (see Alternative readings), which is small next to the uncertainty. Applying the conversion would fix it, as `fill_minimum_n_effective` already does. We have not checked whether later versions changed this.
2. **The example config does not match the published run.** `example/gwtc3-bbh.ini` has `max-redshift=1.9`. `example/gwtc3-bbh.prior` has mmax U(60,100), mmin U(2,7) and lamb U(-2,8), and gives delta_m no reflective boundary. The published result used z_max = 2.3 (our exact match of the surveyed hypervolume confirms it), mmax U(30,100), mmin U(2,10), lamb U(-10,10) and a reflective boundary on delta_m. The kappa prior also differs from the paper's App. B 3 ("kappa in [-6, 6]"). In our runs and in the released result, the 90% interval of kappa lies between 1.0 and 4.7, well inside all of these ranges, so the kappa difference does not matter here. We did not test the effect of the differences in the mass priors or the delta_m boundary. Shipping the exact ini and prior files of the release runs would remove the guesswork.
3. **Two codebases carry the version 0.6.3**: the PyPI sdist and GitHub commit 5cd44c2012 ("Mass bounds fix (#37)"). The result metadata records `gwpopulation 0.6.3:` with an empty git field. The PyPI build reproduces the published log-likelihood to within 6e-14 (18 of 20 samples bitwise identical, 18 distinct points). A tag, or a hash in the metadata, would make this unambiguous.
4. **Small environment points**. `gwpopulation_pipe_analysis` imports `bilby_pipe` for one helper (`convert_string_to_dict`), which pulls in gwosc, jinja2 and pycondor. Writing `_samples.hdf5` through deepdish/PyTables also needs `setuptools` (`pkg_resources`) to be installed.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. The numbers in this report come from code that ran on this machine, and the commands, logs and outputs are in this folder. "What it took" states the exceptions where they occur. Four observations were made but not logged: GPU use, CPU load and RAM during the runs, the failed first cupy attempt and the refused clone. The GPU, cupy and PyTables checks in `runs/check_gpu.log`, `runs/test_cupy.log` and `runs/fix_tables.log` were captured after the runs.

Before any run, a separate agent read the paper and pre-registered the claims, definitions and tolerances in `claims.json`. Its hash is in `claims.sha256` and was unchanged at the end of this run. A single agent then built the environment and ran the authors' code and released data on one RTX 2070 SUPER (8 GB) and a Ryzen 9 3900X. The same agent compared the results with the paper and the released posterior and wrote this report. A reviewer agent and a reviser agent checked the report against the logs, and a human approved publication. This run had no blind recomputation by a second agent.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues