# Reproduction report: The Pantheon+ Analysis: Cosmological Constraints

- Paper: Brout, D., Scolnic, D., Popovic, B. et al., ApJ 938, 110 (2022). DOI: 10.3847/1538-4357/ac8e04. We compared against arXiv 2202.04077 v2, which matches the published version. v1 (Omega_m = 0.338) was not the target.
- Code: https://github.com/PantheonPlusSH0ES/DataRelease @ c447f0fea703fcd0fff57de5000947b5ca81286b. The likelihood logic comes from `Pantheon+_Data/5_COSMOLOGY/cosmosis_likelihoods/Pantheon+_only_cosmosis_likelihood.py` and `Pantheon+SH0ES_cosmosis_likelihood.py`, both unchanged since f959603b55.
- Data: `Pantheon+SH0ES.dat` and `Pantheon+SH0ES_STAT+SYS.cov` from raw.githubusercontent.com at the commit above. Both files are unchanged since 7fc680548d.
- Target: Table 3 (Pantheon+ SNe Ia only). The primary claim is Omega_m = 0.334 ± 0.018 in Flat ΛCDM. The secondary claims are the ΛCDM, Flat wCDM and Flat w0waCDM rows. As an optional check we also targeted H0 = 73.6 ± 1.1 from the Pantheon+SH0ES likelihood.
- Verdict: **Reproduced**. The primary claim reproduced. Of S1–S4, three reproduced and one (S3) partially reproduced. The prior-sensitive w0waCDM claims S5 and S7 were not reproduced, and under the pre-registered rule they do not count toward the verdict. The paper sampled with PolyChord. We used the pre-registered dynesty fallback with the same number of live points, repeats and tolerance (see What it took, item 4).
- Date: 2026-10-26
- Hardware: Ryzen 9 3900X, 31 GB RAM visible to WSL2 Ubuntu 24.04. The run used the CPU only, at most 4 single-thread processes under `nice -n 19`. The RTX 2070 SUPER was not used.

## Results

Before any run, the claims, definitions and tolerances were pre-registered in `claims.json` (sha256 `dc0f1abf…0fca31`, frozen 2026-10-26T20:47:36Z). Our values are weighted posterior means. The interval is the equal-tailed 16–84% range around the mean, and std is the weighted standard deviation. All of them come from the main nested-sampling run on the full data. That run used dynesty in place of the paper's PolyChord, with seed 1, on 1590 light curves (rows with zHD > 0.01) for Pantheon+ only and 1657 rows for Pantheon+SH0ES.

| Quantity | Paper | Ours | Diff | Grade |
|---|---|---|---|---|
| **P1** Omega_m, Flat ΛCDM | 0.334 ± 0.018 | 0.3327 +0.0181/−0.0182 (std 0.0183) | −0.0013 (width +0.0003) | reproduced |
| S1 Omega_m, ΛCDM | 0.306 ± 0.057 | 0.2953 +0.0547/−0.0572 (std 0.0558) | −0.0107 (−0.19σ; width −2%) | reproduced |
| S2 Omega_Λ, ΛCDM | 0.625 ± 0.084 | 0.6112 +0.0806/−0.0831 (std 0.0843) | −0.0138 (−0.16σ; width +0.4%) | reproduced |
| S3 Omega_m, Flat wCDM | 0.309 +0.063/−0.069 | 0.2851 +0.0732/−0.0696 (std 0.0693) | −0.0239 (−0.35σ; width +16% / +1%) | partial |
| S4 w, Flat wCDM | −0.90 ± 0.14 | −0.9091 +0.1492/−0.1532 (std 0.1486) | −0.0091 (−0.06σ; width +6%) | reproduced |
| S5 Omega_m, Flat w0waCDM (not in verdict) | 0.403 +0.054/−0.098 | 0.3184 +0.1066/−0.1199 (std 0.1109) | −0.0846 (−0.86σ; width +97% / +22%) | not reproduced |
| S6 w0, Flat w0waCDM (not in verdict) | −0.93 ± 0.15 | −0.9253 +0.1528/−0.1561 (std 0.1527) | +0.0047 (+0.03σ; width +2%) | reproduced |
| S7 wa, Flat w0waCDM (not in verdict) | −0.1 +0.9/−2.0 | −0.763 +1.377/−1.599 (std 1.382) | −0.663 (−0.33σ; width +53% / −20.04%) | not reproduced |
| O1 H0, Flat ΛCDM, Pantheon+SH0ES (not in verdict) | 73.6 ± 1.1 | 73.54 +1.03/−1.04 (std 1.05) | −0.06 (width −0.05) | reproduced |

The tolerances are the pre-registered ones:
- P1: the mean must be within 0.003 (reproduced) or 0.009 (partial), and the width within 0.002 or 0.004.
- S1–S7: the mean must be within 0.25σ or 0.5σ of the paper's half-width on the relevant side. Each error component must be within 20% or 40%.
- O1: the mean must be within 0.2 or 0.55 km/s/Mpc, and the width within 0.15 or 0.3.

S7 has its mean (−0.33σ) and its minus-side width (−20.04%) in the partial band. The plus-side width is +53%, above the 40% partial bound, and that makes S7 not reproduced.

The verdict holds for each of the three seeds, but with little margin. S1 seed 3 is at −0.245σ and S2 seed 3 is at −0.236σ, just inside the 0.25σ bound (`runs/seed_margins.py`, log in `runs/logs/seed_margins.log`).

**Variants and checks for P1 (Omega_m, Flat ΛCDM).** None of these were used for the verdict.

| Run | Omega_m |
|---|---|
| Nested sampling, seeds 1 / 2 / 3 | 0.3327 / 0.3320 / 0.3323 (std 0.0183 / 0.0174 / 0.0184) |
| emcee, 16 walkers × 10,000 steps, first 30% dropped | 0.3319 ± 0.0186 |
| M marginalised analytically (Cobaya style), h0 fixed | 0.3325 ± 0.0176 |
| CAMB background (importance reweighting of seed 1) | 0.3326 (analytic: 0.3327). Largest Δμ at the data redshifts, evaluated at Om = 0.334, h = 0.7: 0.00022 mag. Reweighting used the 1576 seed-1 samples carrying 99.99998% of the weight (ESS 986 after reweighting); Δχ² mean 0.0018, std 0.029 |
| Authors' released emcee chain | 0.3319 ± 0.0208 with no burn-in; 0.3314 ± 0.0179 with 30% dropped |

The emcee integrated autocorrelation times are 95–386 steps. The 7,000 kept steps are therefore 18–74 τ, fewer than the 50 τ that emcee recommends for the 4–5 parameter models. That gives roughly 300–450 effective samples per run (`runs/out/*_emcee_s1.json`, `runs/logs/seed_margins.log`). The Pantheon+SH0ES emcee run is the exception, with τ of 38–43 steps and about 2,600 effective samples. The authors' released FlatLambdaCDM chain (3,100 steps) is about 12 τ long, so its summary values carry similar Monte Carlo noise.

**Spread over the three seeds and the emcee variant for the other claims.**

| Claim | Three seeds | emcee | Authors' released chain |
|---|---|---|---|
| S1 | 0.2953 / 0.2939 / 0.2920 | 0.2974 | 0.2956–0.2966 |
| S2 | 0.611 / 0.608 / 0.605 | 0.613 | 0.605–0.611 |
| S3 | 0.285 / 0.288 / 0.291 | 0.287 | 0.289 |
| S4 | −0.909 / −0.916 / −0.921 | −0.908 | −0.915 |
| S5 | 0.318 / 0.311 / 0.318 | 0.307 | — |
| S6 | −0.925 / −0.919 / −0.937 | −0.914 | — |
| S7 | −0.76 / −0.66 / −0.64 | −0.59 | — |
| O1 | — | 73.54 ± 1.01 | 73.54 ± 1.02 |

S3 is in the partial band for all three seeds, at −0.26σ to −0.35σ. The authors' own released chain sits at −0.29σ.

With the alternative wa prior [−2, 2], w0waCDM gives:

| Run | Omega_m | w0 | wa |
|---|---|---|---|
| Nested sampling | 0.282 | −0.913 | −0.13 +0.87/−1.03 |
| emcee | 0.284 | −0.914 | −0.15 |
| Authors' released Pantheon+only chain (same prior) | 0.213 | −0.82 | +0.34 |

**Likelihood equivalence with the authors' runs.** We took 1000 random points from each released chain (rng seed 0) and evaluated our numpy likelihood on them. We then compared the result with the authors' stored CosmoSIS+CAMB log-likelihood (post − prior):

| Chain | Finite points | Median difference in ln L | Std, all points | Points within 10 of best ln L | Std / max, those points |
|---|---|---|---|---|---|
| Flat ΛCDM | 1000 | −0.00002 | 0.066 | 985 | 0.013 / 0.052 |
| ΛCDM | 1000 | −0.0008 | 0.077 | 976 | 0.011 / 0.038 |
| Flat wCDM | 1000 | 0.0002 | 0.014 | 997 | 0.012 / 0.041 |
| Flat w0waCDM | 999 | 0.0002 | 0.076 | 991 | 0.011 / 0.042 |
| Pantheon+SH0ES Flat ΛCDM | 1000 | 0.0002 | 0.053 | 990 | 0.011 / 0.035 |

Over all points, the largest single deviation is 0.17–1.27. Those deviations sit at burn-in points far into the tails, where the authors' ln L goes down to −7760, against about −701 at the best fit.

Within 10 units of the best-fit ln L (976–997 of the 1000 points per chain), the difference has std 0.011–0.013 and max 0.035–0.052. That matches the size of the shift between the CAMB and analytic backgrounds (Δχ² std 0.029 in `runs/out/camb_check_flcdm_dynesty_s1.json`).

In Flat w0waCDM, 999 of 1000 points are finite. The authors' chain has ln L = −inf at one point, w0 = −1.005, wa = +0.002. There w crosses −1, which is where CAMB without PPF fails.

So our likelihood agrees with the authors' likelihood to about 0.01 in ln L near the posterior. The remaining differences come from two things in the authors' pipeline: the radiation and neutrino terms that CAMB adds to the background, and the `interp1d` interpolation of the CAMB D_A that their code does. Script: `runs/released_like_near_bestfit.py`, log in `runs/logs/released_like_near_bestfit.log`.

## What it took

1. **Environment** (`env/setup_env.sh`, lockfile `env/requirements.lock.txt`, sha256 `f667d633…98c4`). We used Python 3.10 with mid-2022 releases: numpy 1.22.4, scipy 1.8.1, pandas 1.4.3, emcee 3.1.2, dynesty 1.2.3, camb 1.3.5 and matplotlib 3.5.2. camb 1.3.5 is a source distribution whose `setup.py` imports `pkg_resources`, so it was built with gfortran under a `setuptools<70` build constraint (`env/build_constraints.txt`). The authors released no version pins.
2. **Data** (`env/download_data.sh`, log in `runs/logs/download.log`). Both files matched the server Content-Length, the expected md5 and the git blob sha1:
   - `Pantheon+SH0ES.dat`: 579,283 B, md5 2049b142…
   - `Pantheon+SH0ES_STAT+SYS.cov`: 33,284,960 B, md5 041bdb66…
3. **Likelihood** (`runs/pp_like.py`). We wrote a numpy copy of the authors' CosmoSIS modules.
   - It keeps zHD > 0.01, which leaves 1590 rows. For the SH0ES likelihood it also keeps the rows with IS_CALIBRATOR == 1, which gives 1657 rows.
   - The model is m = 5 log10[(1+zHD)(1+zHEL) D_A(zHD)] + 25 + M. The covariance subset is inverted once, and there is no log-determinant term.
   - The background is analytic, flat or curved, with CPL dark energy. The comoving distance uses 8-point Gauss–Legendre integration between consecutive data redshifts.
   - We checked the distances against adaptive quadrature at all 1590 rows for 6 cosmologies (flat, open, closed, wCDM and two w0waCDM). The largest relative distance error is 3e-15 (`runs/selftest_all_rows.py`, log in `runs/logs/selftest_all_rows.log`).
   - We also ran the authors' nested covariance loop verbatim. It gives exactly the same 1590 × 1590 matrix as our reshape (`runs/logs/check_inputs.log`).
4. **Sampling** (`runs/run_fit.py`, `runs/run_queue.sh`; outputs in `runs/out/`, logs in `runs/logs/`). The paper used PolyChord with 250 live points, 30 repeats and tolerance 0.1.
   - We did not build PolyChordLite from source. Fetching and compiling it from GitHub was not permitted in this session, so it was not attempted.
   - PyPI carries only pypolychord 1.15 and 1.15.1 wheels from January 2019, for cp27–cp37. They do not install on Python 3.10 (log in `env/polychord_attempt.log`, from `env/polychord_probe.sh`).
   - We therefore used the pre-registered dynesty fallback: a static NestedSampler with nlive = 250, `rslice`, 30 slices and dlogz = 0.1, on seeds 1, 2 and 3.
   - The emcee variant uses 16 walkers and 10,000 steps, with 30% burn-in. It starts from a ball of 1e-3 of the prior width around the values.ini start, as CosmoSIS does with `random_start = F`.
   - Flat priors come from the released chain headers.
   - dynesty 1.2.3 does not accept −inf, so cosmologies with an undefined distance get ln L = −1e300.
5. **Checks.**
   - `runs/camb_check.py` reweights the posterior with a CAMB background, using Omega_b 0.048, omnuh2 0.00083, 3 massive neutrinos and N_eff 3.046.
   - `runs/released_like_check.py` and `runs/released_like_near_bestfit.py` compare our likelihood with the stored likelihood of the released chains.
   - `runs/compare.py` applies the pre-registered verdict rule and writes `runs/results.json`.
   - `runs/seed_margins.py` gives the per-seed margins and the emcee chain lengths in τ.
6. **Runtime.** About 3 h 10 min wall clock and about 11.6 core-hours in total. Each 3–5 parameter nested run took 28–65 min and 290k–400k likelihood calls, at 3–8 ms per call on one thread with the other runs going in parallel. Each emcee run took 13–24 min. The checks added in the revision (`runs/revision_checks.sh`) took a few minutes.

We changed none of the authors' code, and no patches were needed (`patches/` holds only a `.gitkeep`). The CosmoSIS pipeline itself (consistency → camb → pantheon) was not installed. We transcribed its likelihood logic and checked it point by point against the released chains (above).

## Alternative readings

- **Medians and highest-density intervals for the prior-sensitive w0waCDM posteriors** (seed 1, wa ∈ [−4, 4]):

  | Parameter | Median | 68% HPD |
  |---|---|---|
  | Omega_m | 0.342 | 0.266–0.458 |
  | w0 | −0.908 | −1.050 to −0.745 |
  | wa | −0.47 | −1.59 to 1.06 |

  The Omega_m median is closer to 0.403, but still 0.62σ away. These posteriors are strongly non-Gaussian, with mass near the prior edges, so the choice of summary statistic matters. No reading we tried recovers Omega_m = 0.403 +0.054/−0.098. This changes nothing in the verdict.
- **wa prior [−2, 2].** This is the prior in the released Pantheon+only w0waCDM chain. It moves Omega_m further from the paper's value (0.282) and brings wa close to the paper's central value (−0.13 against −0.1). We could not find a single setting that matches all three w0waCDM numbers in Table 3.

## Notes for the authors

Thank you for releasing the distances, the full covariance, the CosmoSIS likelihoods and the chains. With all of them available, this check was straightforward. The headline Omega_m = 0.334 ± 0.018 reproduces, and so do the ΛCDM and wCDM rows and the SH0ES H0. A few things would help the next person:

1. **Table 3 seems to come from PolyChord runs that were not released.** The chains in `5_COSMOLOGY/chains` are emcee runs from 05/07/2022. The FlatLambdaCDM chain stops at 3100 of 10,000 steps, with no burn-in noted. Releasing the PolyChord chains, or saying which runs produced Table 3, would make the comparison exact.
2. **Flat w0waCDM.** With your likelihood and a wa prior of [−4, 4], we get Omega_m = 0.32 ± 0.11, w0 = −0.93 ± 0.15 and wa = −0.8 +1.4/−1.6. Table 3 gives 0.403 +0.054/−0.098, −0.93 ± 0.15 and −0.1 +0.9/−2.0.
   - With a wa prior of [−2, 2] we get Omega_m = 0.28. Your released Pantheon+only chain (same prior, no `use_ppf_w`) gives 0.213.
   - At that chain's own points, our likelihood matches its stored log-likelihood (median difference 0.0002, std 0.011 near the posterior).
   - One of the 1000 points we checked has ln L = −inf in your chain, at w0 = −1.005, wa = +0.002, where w crosses −1 and CAMB without PPF fails.

   So the gap is probably in the prior range or in regions where CAMB fails without PPF, not in the data. Could you say which wa prior and which PPF setting the Table 3 run used?
3. **Prior ranges.** The paper does not give the prior ranges, and we could only recover them from the chain headers. It would help to state them, especially M ∈ [−20, −18] and h ∈ [0.55, 0.91], since only M − 5 log10 h enters the likelihood.
4. **Two small text points.** The paper writes w = w0 + wa(1+z), while CAMB and CosmoSIS use CPL, w0 + wa(1−a). Also, Eq. 9 refers to 1701 residuals, while the SN-only fits use the 1590 rows with zHD > 0.01.

## How this report was made

This reproduction was run by AI agents (Claude, by Anthropic) on a home computer and reviewed by a human before publication. No number in this report was estimated or typed by hand. Each one comes from code that ran on this machine, and the commands, logs and outputs are in this folder.

Before any run, a separate agent read the paper and pre-registered the claims, definitions and tolerances in `claims.json`, then froze the file with its hash. A single agent then did the main work on a Ryzen 9 3900X (CPU only, at most 4 low-priority threads, GPU not used). It built the environment, ran the authors' likelihood logic, compared the results with the paper and the authors' released chains, and wrote this report. A reviewer agent checked the report against the logs, a reviser agent fixed what it found, and a human approved publication. There was no blind recomputation by a second agent in this run.

We do this because most published code is never re-run by anyone else, and AI agents make that check cheap. The method, prompts and scripts are public at https://github.com/paper-rerun/paper-rerun/blob/main/METHOD.md, so anyone can run the same checks on papers in their own field.

Contact: Filipe Tessaro, https://github.com/paper-rerun/paper-rerun/issues