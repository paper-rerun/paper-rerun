# Reproduction report (blind rerun): The NANOGrav 15 yr Data Set: Evidence for a Gravitational-wave Background

- **Paper:** Agazie, G. et al. (NANOGrav), ApJL 951:L8, 2023. Numbers come from arXiv 2306.16213v1 (28 Jun 2023), `paper/2306.16213.pdf`, sha256 `3a33495ae465768f832d5e55efff0769a6a6c41564ce8714e3f51ba929785aeb`.
- **Code and products:** https://github.com/nanograv/15yr_stochastic_analysis @ `a3e8b8776a646208ca2d307f83c20bc70e029933` (11 Aug 2025), full normal clone in `repo/`. The C1 chain was recovered from the clone's own history, at commit `459f99a285fae660fa8afd0464520f4a880db13d`, the parent of 98a4783. Nothing came from Google Drive or any other host.
- **Mode:** analysis of published products. No sampling was rerun.
- **Pre-registration:** `claims.json`, sha256 `82bf67d9a071f8b3da9dc43801232d50f15bb70baa398d117fc355eea9379cfd`. It was frozen at 2026-11-08T23:43:16-03:00, before any chain file was opened (`logs/freeze.log`). `sha256sum -c` still passed at the end, in `logs/c1_history.log`.
- **Verdict: Reproduced.** All 5 pre-registered claims fall inside their bands. Caveat: C2 was computed on a fixed-gamma product-space chain, so it is tested against the paper's "similar for hd13/3 vs curn13/3" statement, not against the variable-gamma 226 ± 70 itself.
- **Date and hardware:** 2026-11-08 / 09. CPU only, WSL2 Ubuntu 24.04.1, `nice -n 19`, at most 6 threads. About 10 minutes of compute and roughly 1 h 15 min in total. Folder about 1.7 GB.

## What this mode can and cannot show

This mode can show two things:
- the chains the authors ship give the paper's numbers when post-processed with the paper's estimators;
- whether a given chain is the right model for a given number.

It cannot show that the sampling converged, that the noise models are right, or that the data imply these posteriors. Every number below is the authors' MCMC output, re-read by us. An agreement means "the published products and the paper agree", and nothing more.

## Which product holds which claim

The README warns that the tutorial data "have been reduced to make them available on GitHub and may not reproduce the results of the 15-year analysis exactly". It points to `data_release` for the full products. In the current tree, the `data_release` folders for figures 1, 4, 5 and 7 only hold Google Drive links. The Figure 1 data were once committed to the repo and removed in 98a4783 ("remove figure 1 data", 2024-02-11). They are still in the git history.

| Claim | Product used | Why it is the right one | Caveat |
|---|---|---|---|
| C1, A = 2.4 (+0.7/−0.6)e-15, hd, gamma = 13/3 | `data_release/figure_1/figure1_data/nano15_hd_chain_fg_long_050523.npy` at 98a4783^ (from history) | `lower_left.ipynb` loads this file as the fixed-gamma ("fg") HD chain, takes percentiles of the whole array as log10 A, and uses gamma = 13/3 for its f_ref correction | The file holds 1-D log10 A only. It does not record whether burn-in was already removed. |
| C2, BF hd vs curn = 226 ± 70 (Fig. 2) | `tutorials/presampled_cores/curn_hd.core` | product-space chain, 14 freqs, weight 300 on curn | **No common-gamma parameter**, so gamma is fixed. Flagged. |
| C3, BF curn vs irn = 10^(12.1 ± 0.1) | `irn_ti.core`, `curn_ti.core` | TI slices with 31 temperatures; `ti_sample.py` uses model_1 / model_2a, 14 freqs, varied gamma | — |
| C4, abstract: hd over irn, BF > 10^14 | `irn_ti.core`, `hd_ti.core` | TI | — |
| C5, hd vs curn by TI (second method for C2) | `curn_ti.core`, `hd_ti.core` | TI, varied gamma | — |

## Results

| Id | Quantity | Published | Ours | Pre-registered band | Inside |
|---|---|---|---|---|---|
| C1 | A_HD,13/3 median | 2.4e-15 | **2.404e-15** | [2.35, 2.45)e-15 | yes |
| C1 | 5% quantile | 1.8e-15 (2.4 − 0.6) | **1.815e-15** | [1.75, 1.85)e-15 | yes |
| C1 | 95% quantile | 3.1e-15 (2.4 + 0.7) | **3.069e-15** | [3.05, 3.15)e-15 | yes |
| C2 | BF hd vs curn, product space | 226 ± 70 (variable gamma) | **202.2** (iid bootstrap ±3.4, block bootstrap ±20.7) | [86, 366] | yes, flagged: fixed-gamma chain |
| C3 | log10 BF curn vs irn, TI | 12.1 ± 0.1 | **12.110 ± 0.086** | [11.9, 12.3] | yes |
| C4 | log10 BF hd vs irn, TI | > 14 | **14.406 ± 0.105** | > 14.0 | yes |
| C5 | BF hd vs curn, TI | 226 ± 70 | **197** (1σ 157 to 248) | [86, 366] | yes |

The next table is context only and does not enter the verdict:

| Id | Quantity | Published | Ours | Band | Inside |
|---|---|---|---|---|---|
| P1 | A_HD, varied gamma, median [5%, 95%] | 6.4 [3.7, 10.6] e-15 | 6.33 [3.78, 10.40] e-15 | median in [5.9, 6.9] | yes |
| P1 | gamma_HD median [5%, 95%] | 3.2 [2.6, 3.8] | 3.25 [2.69, 3.83] | median in [3.1, 3.3] | yes |
| E1 | A at gamma = 13/3, taken from the varied-gamma chain | 2.4 [1.8, 3.1] e-15 | 2.55 [2.25, 3.25] e-15, **n = 18** | at least 100 samples, plus bands | **no** (18 samples, q05 outside) |

Sources:
- C1: `outputs/c1_history.json`, `logs/c1_history.log`
- everything else: `outputs/results.json`, `logs/analyze.log`, `logs/diagnose_ti.log`, `outputs/ti_diagnostic.json`

### C1 from the chain in git history

- **Extraction.** Ran `git -C repo show 98a4783^:data_release/figure_1/figure1_data/nano15_hd_chain_fg_long_050523.npy > history/nano15_hd_chain_fg_long_050523.npy`. The clone is a full one with no promisor remote, so nothing was fetched.
- **File.** 1,511,832 bytes, sha256 `8468b1ef5046870771350c266b0767f392cd2d9dc54c4e6584261d94a8d0b113` (`logs/history_extract.log`). Loaded with `np.load(allow_pickle=False)`: float64, shape (188963,), all values finite, log10 A from −14.903 to −14.361.
- **How the authors read it.** From the source of `lower_left.ipynb` (outputs not read, `logs/nb_lower_left.src.txt`): `10**np.percentile(hd_chain_fg, q=5/95/50)` on the whole array, with no burn and no thinning. That is the same as our frozen rule: quantiles of log10 A, then 10**.
- **Result.** Median 2.404e-15, q05 1.815e-15, q95 3.069e-15, which is +0.665 / −0.589 e-15. All three round to the printed 2.4 (+0.7/−0.6).
- **Sensitivity (not in the verdict).** An extra 25% burn gives 1.806 / 2.401 / 3.072 e-15. The iid bootstrap std of the quantiles is about 2e-18, so the result is far from the band edges.

### E1, in hindsight

Before we had the hint, E1 tried to recover C1 by slicing the short varied-gamma tutorial core at gamma = 13/3:
- only 18 samples fell in the window, against the pre-registered minimum of 100;
- the slice median came out at 2.55e-15, 6% above the real fixed-gamma chain (2.404e-15);
- the slice could not reach the 5% quantile, since the smallest A anywhere in that core is 2.26e-15.

So the short core is not a substitute for the Figure 1 chain.

### C2: the product-space chain is a fixed-gamma chain

The notebook says `curn_hd.core` "reproduces one of the Bayes factors found in figure 2". All Fig. 2 models use variable-gamma power laws. Yet the stored core has no common-gamma parameter and no runtime metadata (`logs/core_meta.log`). Gamma was therefore fixed, at a value the core does not record, most likely 13/3.

As the frozen rule requires, we report C2 against the paper's "Results are similar for hd13/3 vs. curn13/3" and flag it.

- BF = 6037 / 8956 × 300 = 202.2, from 14993 post-burn samples.
- The iid bootstrap std is 3.45, matching the notebook's "202 ± 3.4".
- The chain has 587 model switches. A block bootstrap (14 blocks of 1000) gives std 20.7.
- An extra 25% burn gives BF 209.7.

### C3, C4, C5: thermodynamic integration

We ran the authors' `ti_log_evidence` from `tutorials/extra_functions.py` unchanged, with its RNG reseeded to 20231108.

The pre-registered cross-check was a plain trapezoid in beta over the mean lnlike at each temperature:

| | Authors' function | Authors' quadrature, no bootstrap | Plain trapezoid in beta |
|---|---|---|---|
| log10 BF curn vs irn | 12.110 | 12.143 | 12.491 |
| log10 BF hd vs irn | 14.406 | 14.391 | 14.703 |
| log10 BF hd vs curn | 2.295 | 2.249 | 2.211 |

The difference comes only from the quadrature:
- The authors interpolate linearly in log10 beta and integrate with Simpson's rule. The trapezoid is linear in beta.
- The ladder is geometric, with a step of 1.71× near beta = 1, and <lnL> moves by 20 to 110 per step there.
- Each log-evidence shifts by 2 to 3 nats between the two rules. The shifts do not cancel between models: the gap is 0.35 dex for curn vs irn.
- Sorting the bootstrap means changes nothing (1e-6 nats).

Every reading stays inside the C3 to C5 bands, except the trapezoid for curn vs irn (12.49). The verdict uses the pre-registered estimator, the authors' function. The trapezoid gap is reported as Note 3.

## Not tested

- BF hd vs curn with 5 frequencies (965): no product found. We did not look further.
- The monopole, dipole and HD+X Bayes factors in Fig. 2.
- The p-values: 1e-3 for the Bayesian background, 5e-5 to 1.9e-4 for the optimal statistic.
- The other files removed in 98a4783. Among them is `14f_PL_hd_crn.core`, which may be the variable-gamma product-space chain behind 226 ± 70. It was not opened: it was outside the coordinator's request and is not in claims.json.

## Environment

- WSL2 Ubuntu 24.04.1 (kernel 5.15.153.1), uv 0.13.4, CPython 3.10.22, venv in `env/venv`. The uv caches are in `env/uv-cache` and `env/uv-python-cache`.
- Pinned in `env/requirements.in`, locked in `env/requirements.lock`: la_forge 1.1.0, numpy 1.24.4, scipy 1.10.1, h5py 3.9.0, emcee 3.1.4, matplotlib 3.7.2, pandas 2.0.3. These are mid-2023 versions. enterprise was not installed.
- `OMP/OPENBLAS/MKL_NUM_THREADS=6`, `MPLBACKEND=Agg`, everything run under `nice -n 19`.

## Commands

From Git Bash, in `E:\Ciencia\noturno\2023-agazie-nanograv15-cego`:

```
git clone https://github.com/nanograv/15yr_stochastic_analysis.git repo          # logs/clone.log
curl -sSL -o paper/2306.16213.pdf https://arxiv.org/pdf/2306.16213
pdftotext -layout paper/2306.16213.pdf paper/paper.txt
python -I scripts/nb_source.py repo/tutorials/parameter_est.ipynb   > logs/nb_parameter_est.src.txt
python -I scripts/nb_source.py repo/tutorials/model_selection.ipynb > logs/nb_model_selection.src.txt
sha256sum claims.json | tee claims.json.sha256                                    # logs/freeze.log
MSYS_NO_PATHCONV=1 wsl bash -lc "bash /mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/scripts/setup_env.sh" > logs/setup_env.log 2>&1
MSYS_NO_PATHCONV=1 wsl bash -lc "bash /mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/scripts/run.sh"       > logs/analyze.log 2>&1
MSYS_NO_PATHCONV=1 wsl bash -lc "bash /mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/scripts/run_diag.sh"  > logs/diagnose_ti.log 2>&1
MSYS_NO_PATHCONV=1 wsl bash -lc "bash /mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/scripts/run_meta.sh"  > logs/core_meta.log 2>&1
# after the coordinator's hint:
git -C repo show 98a4783^:data_release/figure_1/figure1_data/nano15_hd_chain_fg_long_050523.npy > history/nano15_hd_chain_fg_long_050523.npy   # logs/history_extract.log
python -I scripts/nb_source.py repo/data_release/figure_1/lower_left.ipynb > logs/nb_lower_left.src.txt
MSYS_NO_PATHCONV=1 wsl bash -lc "bash /mnt/e/Ciencia/noturno/2023-agazie-nanograv15-cego/scripts/run_c1.sh"    > logs/c1_history.log 2>&1
```

`nb_source.py` prints only markdown and code cells, never outputs. The scripts are:
- `scripts/analyze.py`: C2 to C5, P1, E1
- `scripts/diagnose_ti.py`
- `scripts/core_meta.py`
- `scripts/c1_history.py`: C1

## Logs and outputs

- `logs/freeze.log`: freeze time and hash
- `logs/c1_history.log`, `outputs/c1_history.json`, `logs/history_extract.log`: C1
- `logs/analyze.log`, `outputs/results.json`: C2 to C5, P1, E1
- `logs/diagnose_ti.log`, `outputs/ti_diagnostic.json`: TI quadrature, betas, <lnL> per temperature, curn_hd parameter list
- `logs/core_meta.log`, `logs/setup_env.log`, `logs/clone.log`, `logs/nb_*.src.txt`

## Blindness and disclosures

- We did not open, list or grep any forbidden folder or file: the earlier run's folder, fila.md, log.md, triagem-2026-11-08, and the NANOGrav reports and issues.
- **Hint from the coordinator (the only one).** After the first version of this report, where C1 was "not tested", the coordinator said the Figure 1 data had been committed and later removed in 98a4783. It also said that `nano15_hd_chain_fg_long_050523.npy` in the parent commit is what `lower_left.ipynb` reads for the hd13/3 amplitude. No number was given. We would not have found this file without the hint, because our first pass looked only at the current tree. claims.json and its band were not changed.
- The markdown in the model_selection notebook quotes tutorial results ("202 +/- 3.4", "10^{12.11 ± 0.087}"). We read it before the freeze, to find out what each core holds. Our bands come from the paper, not from those lines.
- No chain was opened before the freeze. The clone is a full normal clone.

## Notes for the authors

1. **The hd13/3 amplitude chain was removed from the repository in 98a4783 and is still in its history. It is now distributed only through Google Drive.** The headline A = 2.4 (+0.7/−0.6)e-15 reproduces exactly from `nano15_hd_chain_fg_long_050523.npy` at 98a4783^: we get 2.404 (+0.665/−0.589)e-15. The README's pointer to `data_release` now leads to a Drive link only. Would you consider archiving the Figure 1 files with a DOI (for example on Zenodo), linked from the repo? Also, the `.npy` does not say whether burn-in was already removed. One line in the README would settle that.
2. **`curn_hd.core` looks like a fixed-gamma comparison.** It has no common-gamma parameter, while Fig. 2 says all models use variable-gamma power laws (226 ± 70). Its BF is 202.2, which fits the paper's "similar for hd13/3 vs curn13/3". Is this the hd13/3 vs curn13/3 run? If so, the notebook could say which Fig. 2 number it reproduces. Also, the notebook's ±3.4 is an iid bootstrap on an autocorrelated chain with 587 model switches. A block bootstrap with blocks of 1000 gives ±20.7.
3. **TI quadrature uncertainty.** On the shipped TI cores, `ti_log_evidence` gives log10 BF(curn/irn) = 12.11 ± 0.09. A plain trapezoid in beta over the same means per temperature gives 12.49, and hd/irn moves from 14.41 to 14.70. That 0.35 dex shift is larger than the quoted ±0.1, which comes from the bootstrap alone. The conclusions hold either way. Could the Fig. 2 uncertainty include a quadrature term, or could the ladder be denser near beta = 1?
4. **`ti_sample.py` reads files that are not shipped.** It opens `data/v1p1_wn_dict.json` and `data/emp_distr.pkl`. The tutorials folder has `15yr_wn_dict.json` and `15yr_emp_distr.json` instead. As written, the script will not run from a fresh clone.
5. **Which data the tutorial cores come from.** The README warns that the tutorial data are reduced, but does not say whether the presampled cores were run on reduced or full data. P1 matches Sec. 3 closely: A 6.33e-15 and gamma 3.25, against 6.4e-15 and 3.2. That suggests full data with short chains.
6. **Small points.** `hd_ti.core` has 24230 samples per temperature, against 49990 for irn and curn. The infinite temperature is stored as T = 1e80. Neither affects the results.

## How this report was made

A single agent did the whole run, blind to the earlier attempt:
1. Cloned the repo and read the README, the notebook sources and the helper scripts.
2. Wrote and hashed claims.json.
3. Built the environment and read the tutorial cores.
4. Ran the pre-registered estimators, plus a diagnostic for the one cross-check that disagreed.
5. After the coordinator's hint, recovered the Figure 1 chain from git history and computed C1 with the frozen rule and band.

No adversarial review of this report has been done yet. REPORT.md itself could not be written by the subagent (the write was blocked); the coordinator should save this text there.
