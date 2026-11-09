# Reproduction report: DESI 2024 VI: cosmological constraints from the measurements of baryon acoustic oscillations

- Paper: DESI Collaboration (A. G. Adame et al.), JCAP 02 (2025) 021, DOI 10.1088/1475-7516/2025/02/021. Numbers taken from the arXiv PDF 2404.03002 (`paper/2404.03002.pdf`, SHA-256 `8e603ac8…b487cd36`). Equation and table numbers below are the arXiv numbering.
- Data: the DESI DR1 BAO distance ratios and their 12×12 covariance, as plain text in https://github.com/CobayaSampler/bao_data @ `bb0c1c9009dc76d1391300e169e8df38fd1096db` (2025-06-26). No login, no terms to accept.
- Code: our own likelihood and posterior grid, with CAMB 1.5.4 (the paper's Boltzmann code) for the background expansion and the drag-epoch sound horizon. cobaya 3.5 was used twice: once to check our likelihood against its released BAO likelihood, and once to run a real Metropolis-Hastings chain as a check on the grid.
- Also downloaded, as a diagnostic and not as the route: the authors' own published chains from https://data.desi.lbl.gov/public/dr1/vac/dr1/bao-cosmo-params/v1.0/cobaya/base/ (no login, plain directory index).
- Target: the three claims frozen in `claims.json` — Ω<sub>m</sub> and r<sub>d</sub>h from DESI BAO alone, and H<sub>0</sub> from DESI BAO + BBN, all flat ΛCDM.
- Verdict: **Partially reproduced** — two of three claims inside the pre-registered band, the third outside it by 0.002σ, with the cause identified.
- Date: 2026-11-08
- Hardware: Ryzen 9 3900X, WSL2 Ubuntu, CPU only, 6 threads, everything under `nice -n 19`. The GPU was not touched.
- Wall clock: about 35 minutes of computation, inside the 1–3 h target. Folder 638 MB, cap was 30 GB.

**Route.** We re-ran the likelihood ourselves. We did **not** reproduce these numbers by re-analysing the published chains. Because the paper samples only (Ω<sub>m</sub>, r<sub>d</sub>h) for BAO alone and (Ω<sub>m</sub>, H<sub>0</sub>, ω<sub>b</sub>) for BAO+BBN, with flat priors (Table 2), we evaluated the posterior on a dense grid and marginalised exactly. That has no sampling scatter and finishes in minutes. This choice, and the risk it carries, were written into `claims.json` before anything was computed. The authors' chains enter the report only as diagnostics, and every place they do is labelled.

## Results

**Tolerance.** Fixed before any run, in `claims.json`: our central value within **0.20σ** of the published one, **and** our uncertainty within **10%** of the published one. The reasoning is in the file: the paper's own stated effective sample size of ≳1000 puts Monte Carlo error on a posterior mean at about 0.03σ and on a width at about 2.2%; rounding of the printed numbers adds up to 0.04σ and 4%; 0.20σ leaves about 0.13σ for method differences we could not estimate in advance.

| Claim | Published | Ours (pre-registered setup) | Pre-registered band | Inside? |
|---|---|---|---|---|
| C1 Ω<sub>m</sub>, DESI BAO alone (Table 3, Eq. 4.1) | 0.295 ± 0.015 | **0.29468 ± 0.01463** | mean [0.2920, 0.2980], σ [0.0135, 0.0165] | **yes** (−0.021σ) |
| C2 r<sub>d</sub>h, same fit (Eq. 4.1) | (101.8 ± 1.3) Mpc | **101.8953 ± 1.2672 Mpc** | mean [101.54, 102.06], σ [1.17, 1.43] | **yes** (+0.073σ) |
| C3 H<sub>0</sub>, DESI BAO + BBN (Eq. 4.4, Table 3) | (68.53 ± 0.80) km/s/Mpc | **68.6912 ± 0.8127** | mean [68.37, 68.69], σ [0.72, 0.88] | **no** (+0.202σ) |

C3 misses the band by 0.0012 km/s/Mpc, that is 0.0015σ past the edge. We are not moving the band: it was frozen, 0.202 > 0.200, and the claim is reported as outside. It is worth saying plainly that a band of 0.25σ, which would have been just as defensible when we wrote it, would have made this "Reproduced". The band was our choice and this claim sits on its edge.

The width of all three matches well: our σ is 2.5% low on C1, 2.5% low on C2 and 1.6% high on C3.

### Why C3 lands high: the BBN prior the paper states is not the one the published chain used

This is the one real finding of the rerun, and it is not a bug on either side.

The paper's Section 2.4.1 gives two BBN priors: Eq. (2.8), ω<sub>b</sub> = 0.02218 ± 0.00055, "in the standard ΛCDM model", and Eq. (2.9), ω<sub>b</sub> = 0.02196 ± 0.00063, for ΛCDM+N<sub>eff</sub>. We pre-registered Eq. (2.8), because C3 is a flat ΛCDM claim.

The authors' own base-ΛCDM DESI+BBN chain (`base/desi-bao-all_schoneberg2024-bbn/`) reproduces the published number exactly: H<sub>0</sub> = 68.52995 ± 0.80466 against the printed 68.53 ± 0.80, and Ω<sub>m</sub> = 0.29514 ± 0.01479. So that is the chain behind Eq. (4.4), and we are reading the claim correctly. But its `chi2__bbn` column is a Gaussian in ω<sub>b</sub> with **mean 0.021976 and σ 0.000534** (parabola fit, residual rms 1.1×10⁻⁶, so it really is Gaussian), and its ω<sub>b</sub> marginal is 0.021979 ± 0.000533. That is not Eq. (2.8). It is 0.37σ below it.

The release also ships a sibling, `base/desi-bao-all_schoneberg2024-bbn-fixed-nnu/`. Its BBN term **is** exactly Eq. (2.8): parabola fit mean 0.022180, σ 0.000550. And it gives **H<sub>0</sub> = 68.669 ± 0.806** (chains 1–2 of 4, 30% burn-in; 68.651 with no burn-in).

So:

| ω<sub>b</sub> constraint | H<sub>0</sub>, authors' chain | H<sub>0</sub>, our grid | ours − theirs |
|---|---|---|---|
| 0.021976 ± 0.000534 (what the published ΛCDM chain imposes) | 68.5300 ± 0.8047 | 68.5256 ± 0.8033 | −0.0044 (−0.005σ) |
| 0.022180 ± 0.000550 (paper Eq. 2.8, what we pre-registered) | 68.669 ± 0.806 | 68.6912 ± 0.8127 | +0.022 (+0.03σ; +0.05σ against 68.651 with no burn-in) |
| 0.021960 ± 0.000630 (paper Eq. 2.9, the +N<sub>eff</sub> value) | — | 68.5151 ± 0.8466 | — |

Our grid agrees with the authors' own chain under **both** priors, to 0.005σ and 0.03–0.05σ. The entire +0.202σ offset on C3 is the prior, not our code and not their number. Reading Eq. (2.8) literally, as the paper's text prescribes for ΛCDM, gives 68.67–68.69 rather than the printed 68.53.

The chain's own `chain.updated.yaml` says where the number comes from. Its `bbn_likelihoods.schoneberg2024` block is a two-dimensional Gaussian in (ω<sub>b</sub>, N<sub>eff</sub>) with mean (0.02196, 3.034) and covariance [[4.0311226e-07, 7.30390042e-05], [7.30390042e-05, 0.0452831584]]. That is the ΛCDM+N<sub>eff</sub> result: its ω<sub>b</sub> marginal is 0.02196 ± 0.000635, which is Eq. (2.9). The base ΛCDM run fixes N<sub>eff</sub> = 3.044 and evaluates this 2D Gaussian there, which gives the conditional ω<sub>b</sub> = 0.0219761 ± 0.0005341 (correlation 0.54). That matches the parabola fit to `chi2__bbn` to every printed digit, and the minimum of `chi2__bbn`, 0.0022, is exactly the N<sub>eff</sub> term (3.044 − 3.034)²/0.04528. So the published ΛCDM DESI+BBN chain uses the ΛCDM+N<sub>eff</sub> BBN likelihood sliced at N<sub>eff</sub> = 3.044, not Eq. (2.8). The `_fixed-nnu` sibling is the one that uses Eq. (2.8).

The paper does not say this anywhere we could find. Section 2.4.1 adopts Eq. (2.8) for ΛCDM. For the θ<sub>*</sub> prior the paper does explain a parallel choice (the width is inflated by about 75% "to accommodate" ΛCDM+N<sub>eff</sub>, paper.txt lines 801–804), but there is no equivalent sentence for BBN. And the slice cannot be read as the conservative choice: its σ of 0.000534 is narrower than Eq. (2.8)'s 0.00055. What it does is move the mean down by 0.37σ.

### Checks that rule our own code out

Every one of these was run after the grid, and each is in `runs/logs/`.

| Check | Result | Log |
|---|---|---|
| Data vector equals Table 1 of the paper, all 12 entries | 0 mismatches at the printed 2 decimals | `probe.log` |
| Covariance symmetric and positive definite | yes, eigenvalues 0.0224 to 0.897 | `probe.log` |
| CAMB comoving distance against CAMB (1+z)D<sub>A</sub>, the flat-space identity | identical, relative difference 0. This checks how we call CAMB, not an independent distance integral | `probe.log` |
| Our χ² against cobaya's released BAO likelihood, same cosmology | 12.751088 vs 12.751089, difference 8×10⁻⁷ | `crosscheck.log` |
| Our CAMB r<sub>drag</sub> against the r<sub>drag</sub> column of their chain, 200 of their own samples | −9.6×10⁻⁶ ± 5.7×10⁻⁷ relative; worth +0.0007 km/s/Mpc in H<sub>0</sub> | `diagnose_h0.log` |
| r<sub>drag</sub> against CAMB AccuracyBoost 1 / 2 / 3 | stable to 2×10⁻⁷ | `crosscheck.log` |
| Our r<sub>d</sub> spline against direct CAMB, 40 points it never saw | worst 4.0×10⁻⁶ relative, median 7.6×10⁻⁸ | `fit.log` |
| Grid wide enough: posterior mass in the edge bins | 10⁻²⁶ to 10⁻¹³ for C1–C3; 3.6×10⁻⁵ for ω<sub>b</sub>, which is the BBN prior's own tail | `fit.log` |
| Grid fine enough: our true χ² minimum by Nelder-Mead vs the grid's | 12.73770 vs 12.73826, so the grid is 0.0006 coarse in χ² | `chi2_at_their_bestfit.log` |
| h fixed at 0.68 for the radiation term in the BAO-alone fit (pre-registered sensitivity test, h = 0.64 and 0.72) | Ω<sub>m</sub> moves 7×10⁻⁵, r<sub>d</sub>h moves 0.002 Mpc | `fit.log` |
| Our grid against the authors' own BAO-alone chain | Ω<sub>m</sub> −0.024σ, r<sub>d</sub>h +0.022σ | `diagnose_bao_alone.log` |
| Our grid against our own cobaya MCMC, BAO+BBN, Eq. (2.8) prior | H<sub>0</sub> 68.7023 ± 0.8193 vs grid 68.6912 ± 0.8127, difference +0.014σ | `analyse_chains.log` |

The MCMC check deserves a line of its own. Four chains, our pinned cobaya 3.5 with its own `bao.generic` likelihood pointed at the same two DESI text files, the Table 2 priors and the Eq. (2.8) BBN prior. Gelman-Rubin R−1 across the four chains is 0.0004 and the effective sample size is about 6300 per parameter, well past the ≳1000 the paper asks of itself. It lands on our grid. So the grid is not the reason C3 sits high, and neither is the choice of sampler.

### A smaller thing: the public text files are not quite the vector their likelihood used

Their BAO-alone chain reports a best `chi2__BAO` of 12.6610. Our minimum on the public files is 12.7377, and the gap is not a grid artefact (our true minimum is 12.73770). Evaluated at 300 of their own posterior samples, our χ² minus their `chi2__BAO` is **+0.0758** (sd across samples 0.0109), a near-constant offset across the posterior. The reviewer's recheck on 600 samples gives +0.0760, sd 0.0105, range 0.045 to 0.107.

It is not the dark energy model: with `dark_energy_model: ppf`, which is what their input yaml sets, our χ² is unchanged to all printed digits. It is not a column mix-up: `chi2`, `chi2__BAO` and the long-form column are bitwise identical in their files. It is not a rescaling of the covariance either. A rescaling by 0.99397 closes the gap at the best fit, but it predicts an offset that grows with χ² (slope +0.006), and the measured offset is flat: slope −0.0005 against their χ², correlation −0.10, and the rescaled model leaves a residual sd of 0.017, worse than a plain constant. Nor is it a hidden version of the public files: both DR1 files in `bao_data` have a single commit (`75b9557d34`, 2024-04-05). What we can say is that their run does not read the public files: its yaml points at `bao_data/desi_gaussian_bao_ALL_GCcomb_{mean,cov}.txt`, without the `2024_`, inside their internal package. We did not find the cause.

This does not matter for the claims: our parameters match their chains to 0.02σ. It is worth a note only because someone comparing χ² values against the paper will find 0.08 they cannot account for.

## Independent blind rerun

A second agent redid the paper in a separate folder (published here as `blind/`) without access to this folder, this report, our scripts or our pre-registration. It was given the paper, the `bao_data` repository, the DESI data server and the three published numbers, and nothing about the BBN prior. It wrote and froze its own `claims.json` (SHA-256 `e83c18155306d6cdfd559496cdbb041286b3658b0ccf90f2f805237d33ac6b22`, 2026-11-09T00:44:17Z), took its own route (a grid for BAO alone, emcee calling CAMB at every point for BAO+BBN, no interpolation) and wrote its own code.

| Claim | Published | This run | Blind run |
|---|---|---|---|
| C1 Ω<sub>m</sub> | 0.295 ± 0.015 | 0.29468 ± 0.01463 | 0.29468 ± 0.01463 |
| C2 r<sub>d</sub>h (Mpc) | 101.8 ± 1.3 | 101.8953 ± 1.2672 | 101.8953 ± 1.2672 |
| C3 H<sub>0</sub> (km/s/Mpc) | 68.53 ± 0.80 | 68.6912 ± 0.8127 | 68.694 ± 0.810 |

C1 and C2 agree to every printed digit, which is expected for two exact grids on the same likelihood. C3 differs by 0.003, inside the blind chain's Monte Carlo error of about 0.008.

The blind run found the BBN mismatch on its own: with Eq. (2.8) it lands at 68.69, it identifies `schoneberg2024-bbn` as the chain behind the published 68.53 and `-fixed-nnu` as the one carrying Eq. (2.8) (68.680 with its burn-in), and swapping its prior for the chain's ω<sub>b</sub> posterior moves it to 68.565. It also found the same χ² offset (12.738 against 12.661) and the same reason the files might differ: the chain reads `desi_gaussian_bao_ALL_GCcomb_*.txt` from the internal package.

Its verdict label is "Reproduced" and ours is "Partially reproduced", from the same number. Its band added half of the last printed digit to the 0.2σ allowance, so its upper edge was 68.695 instead of our 68.69. Neither run moved its band after the fact. We keep our label, because ours is the one that was frozen for this report.

Two corrections to the blind report, made by the coordinator and noted at the top of that file: it guesses that the `schoneberg2024` likelihood is "presumably the N<sub>eff</sub>-marginalised variant", but the chain's yaml shows it is the 2D Gaussian evaluated at N<sub>eff</sub> = 3.044, a conditional rather than a marginal (see above); and it calls the Lyα correlation −0.4775000004 a rounding tie, while its magnitude is just above 0.4775, so −0.478 is the correct rounding and the paper's −0.477 is off by one in the last digit. Neither affects any number.

## What it took

1. **Triage.** Cloned `CobayaSampler/bao_data` and downloaded the arXiv PDF, then checked all three target numbers against the PDF text (`paper/paper.txt`, from `pdftotext -layout`): Ω<sub>m</sub> = 0.295 ± 0.015 at lines 79/1243/1262/2631, r<sub>d</sub>h = (101.8 ± 1.3) Mpc at 1245/2632 (and printed as (101.9 ± 1.3) Mpc at line 2238, Section 6, which the triage missed), H<sub>0</sub> = (68.53 ± 0.80) at 1376/1263. Table 2 gave the sampled parameters and priors, Section 2.4.1 the BBN prior, Section 2.5 the convergence and reporting conventions.
2. **Freeze.** `claims.json` written and hashed at 2026-11-08T21:02:22−03:00, SHA-256 `adb3ebf3a7819b5a602776d17303b21c863cbca1fdfdbed34a31aa4591b0ac70`, in `claims.sha256`. Verified unchanged after all runs. It fixes the three claims, the route, the grids, the priors, the neutrino treatment, the h = 0.68 choice and the tolerance, and names in advance the three checks that would catch a bug in our own likelihood. No number had been computed from the data at that point, and nothing could have been: the venv was only ready at 21:04:21 and the first log is from 21:05:49. (The `frozen_at` field inside `claims.json` says 21:05:00Z, which is wrong; the file's mtime is 21:02:18−03:00. The hash is not anchored anywhere outside this machine.) The cobaya MCMC in step 7 was not in the pre-registration, which said there would be none; it was added as an extra check after the grid.
3. **Environment.** Python 3.11 venv built with `uv`, resolved with `--exclude-newer 2024-04-05` (the arXiv submission date) so we start from versions contemporary with the paper rather than today's. numpy 1.26.4, scipy 1.13.0, **camb 1.5.4**, **cobaya 3.5**, getdist 1.4.7. The authors' yaml records cobaya 3.4.1. Lockfile `env/requirements.lock`, inputs `env/requirements.in`, build script `env/setup_env.sh`. `MPLBACKEND=Agg` throughout.
4. **Probe** (`runs/scripts/probe.py`). The three pre-registered sanity checks, plus timing: a CAMB background call costs 12 ms, which is what made the exact grid affordable.
5. **Fit** (`runs/scripts/fit.py`). Four stages, each cached to `runs/out` so the run is restartable.
   - C1/C2: 701 × 701 grid in (Ω<sub>m</sub>, r<sub>d</sub>h). Only 701 CAMB calls are needed, because at fixed Ω<sub>m</sub> the observables scale as 1/(r<sub>d</sub>h) analytically: D<sub>M</sub>/r<sub>d</sub> = c·I(z;Ω<sub>m</sub>)/(100·r<sub>d</sub>h) and D<sub>H</sub>/r<sub>d</sub> = c/(100·r<sub>d</sub>h·E(z)).
   - C3: 351 × 351 × 61 grid in (Ω<sub>m</sub>, H<sub>0</sub>, ω<sub>b</sub>). The distances depend only on (Ω<sub>m</sub>, H<sub>0</sub>), so those are exact on the full 351 × 351 = 123 201 CAMB calls, no interpolation. r<sub>d</sub> depends only on (ω<sub>b</sub>, ω<sub>m</sub>), precomputed on a 45 × 120 grid and bicubic-splined, with the spline checked against direct CAMB.
   - 1 826 s of CPU across 6 processes, 5 min 21 s wall, peak RSS 2.97 GB (`/usr/bin/time -v` in `runs/logs/fit.log`).
6. **Cross-checks and diagnosis.** `crosscheck.py`, then the authors' chains: `get_official_chain.sh`, `check_sibling.sh`, `get_bao_alone_chain.sh` to download; `diagnose_h0.py`, `diagnose_sibling.py`, `diagnose_bao_alone.py`, `chi2_at_their_bestfit.py`, `chi2_offset_cause.py` to read them. `variant_bbn.py` reran the frozen C3 grid under the three candidate ω<sub>b</sub> priors.
7. **MCMC** (`mcmc_bbn.sh`, `desi_bbn.yaml`, `analyse_chains.py`). Four chains, one thread each.

### Commands

Run from Git Bash; `MSYS_NO_PATHCONV=1` keeps Windows from rewriting the WSL paths. Variables are kept inside `.sh` files, not on the `wsl bash -lc` line, because the Windows shell expands them first and they arrive empty.

```bash
# triage
mkdir -p /e/Ciencia/noturno/2024-desi-bao-vi/{env,data,runs/scripts,runs/out,runs/logs,paper}
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi/data && nice -n 19 git clone --depth 1 https://github.com/CobayaSampler/bao_data.git bao_data'
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi/paper && nice -n 19 curl -sSL -o 2404.03002.pdf https://arxiv.org/pdf/2404.03002 && sha256sum 2404.03002.pdf && pdftotext -layout 2404.03002.pdf paper.txt'

# freeze
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi && sha256sum claims.json | tee claims.sha256'

# environment
MSYS_NO_PATHCONV=1 wsl bash -lc 'bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/env/setup_env.sh'

# probe, fit
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi && export OMP_NUM_THREADS=6 MPLBACKEND=Agg && nice -n 19 env/venv/bin/python -I runs/scripts/probe.py 2>&1 | tee runs/logs/probe.log'
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi && export OMP_NUM_THREADS=1 MPLBACKEND=Agg NPROC=6 && nice -n 19 /usr/bin/time -v env/venv/bin/python -I runs/scripts/fit.py 2>&1 | tee runs/logs/fit.log'

# cross-check against cobaya's own likelihood
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi && export OMP_NUM_THREADS=6 MPLBACKEND=Agg && nice -n 19 env/venv/bin/python -I runs/scripts/crosscheck.py 2>&1 | tee runs/logs/crosscheck.log'

# the authors' chains, as diagnostics
MSYS_NO_PATHCONV=1 wsl bash -lc 'bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts/get_official_chain.sh walk'
MSYS_NO_PATHCONV=1 wsl bash -lc 'bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts/get_official_chain.sh cobaya/base/desi-bao-all_schoneberg2024-bbn'
MSYS_NO_PATHCONV=1 wsl bash -lc 'bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts/check_sibling.sh'
MSYS_NO_PATHCONV=1 wsl bash -lc 'bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts/get_bao_alone_chain.sh'
# then, each as: nice -n 19 env/venv/bin/python -I runs/scripts/<name>.py 2>&1 | tee runs/logs/<name>.log
#   diagnose_h0.py  diagnose_sibling.py  diagnose_bao_alone.py
#   chi2_at_their_bestfit.py  chi2_offset_cause.py  variant_bbn.py

# our own MCMC
MSYS_NO_PATHCONV=1 wsl bash -lc 'nice -n 19 bash /mnt/e/Ciencia/noturno/2024-desi-bao-vi/runs/scripts/mcmc_bbn.sh'
MSYS_NO_PATHCONV=1 wsl bash -lc 'cd /mnt/e/Ciencia/noturno/2024-desi-bao-vi && nice -n 19 env/venv/bin/python -I runs/scripts/analyse_chains.py 2>&1 | tee runs/logs/analyse_chains.log'
```

### Where things are

- `claims.json`, `claims.sha256` — the frozen pre-registration and its hash.
- `env/requirements.in`, `env/requirements.lock`, `env/setup_env.sh` — the pinned environment.
- `runs/scripts/` — every script, 15 files (10 `.py`, 4 `.sh`, 1 `.yaml`).
- `runs/logs/` — one log per script, named after it. `fit.log` holds the main result and the `time -v` block; `mcmc_c{1..4}.log` the four chains.
- `runs/out/results.json` — the pre-registered numbers and the band verdicts, machine-readable.
- `runs/out/variant_bbn.json` — the three ω<sub>b</sub>-prior variants.
- `runs/out/dist_{c,d}.npz`, `runs/out/rd_table.npz` — the cached CAMB tables, so the grids rerun in seconds.
- `runs/chains/` — our four cobaya chains and their input yamls.
- `data/bao_data/` — the clone. `data/official/` — the authors' chains, three directories.
- `paper/` — the PDF and its text dump.

## Alternative readings

None of these changes the verdict.

- **The ω<sub>b</sub> prior.** Covered above. With the prior the published chain imposes, our C3 is 68.5256 ± 0.8033, i.e. −0.006σ. With Eq. (2.9) instead, 68.5151 ± 0.8466. The pre-registered answer stays the one in the table.
- **h in the BAO-alone radiation term.** Pre-registered at 0.68; their chain fixed H<sub>0</sub> = 67.36. Across h = 0.64 to 0.72 our Ω<sub>m</sub> moves by 7×10⁻⁵ and r<sub>d</sub>h by 0.002 Mpc, so the choice is irrelevant at the precision of these claims.
- **Mean versus mode.** We report the mean of the 1D marginal, which is what Section 2.5 says the paper reports for symmetric marginals. We did not test whether any of the three published numbers is a mode or a 68% minimal interval instead.
- **r<sub>d</sub>h printed as 101.8.** The chain mean is 101.85–101.87 depending on burn-in (101.848 with none, which is the chain's own `burn_in: 0`), right on the rounding edge; the paper prints 101.8 in Eq. (4.1) and Section 8 and 101.9 in Section 6. Not pursued.

## Not tested

- Everything else in the paper: the DESI+CMB and DESI+SN combinations, w<sub>0</sub>–w<sub>a</sub>, curvature, neutrino mass, N<sub>eff</sub>, the per-tracer BAO fits of Section 3, and H<sub>0</sub> = 68.52 ± 0.62 from DESI+BBN+θ<sub>*</sub>.
- The DESI DR1 BAO measurements themselves. We took the published distance ratios and covariance as given and did not re-measure them from the galaxy catalogues. A reproduction of these three claims is therefore a reproduction of the cosmological inference, not of the BAO fitting.
- The cause of the +0.076 χ² offset. A covariance rescaling is ruled out; the internal data files their run reads are not public.

## Notes for the authors

Thanks for putting the BAO distances and covariance out as plain text and the chains out on an open server with no login — the whole thing ran in half an hour on a home desktop, and the chains are what let us tell our own mistakes from everything else. Two things, and a postscript.

1. **The ΛCDM BBN prior in Section 2.4.1 is not the one the base ΛCDM DESI+BBN chain imposes.** Section 2.4.1 adopts Eq. (2.8), ω<sub>b</sub> = 0.02218 ± 0.00055, for standard ΛCDM. But `base/desi-bao-all_schoneberg2024-bbn/chain.updated.yaml` uses the two-dimensional (ω<sub>b</sub>, N<sub>eff</sub>) Gaussian with mean (0.02196, 3.034), i.e. the ΛCDM+N<sub>eff</sub> result of Eq. (2.9), evaluated at N<sub>eff</sub> = 3.044. That conditional is ω<sub>b</sub> = 0.021976 ± 0.000534, and it is what the `chi2__bbn` column shows. This is the chain behind Eq. (4.4): we recover H<sub>0</sub> = 68.52995 ± 0.80466 from it. The `_schoneberg2024-bbn-fixed-nnu` sibling does impose Eq. (2.8) and gives H<sub>0</sub> = 68.669 ± 0.806. So a reader who applies Eq. (2.8) as Section 2.4.1 says lands at 68.67–68.69, 0.2σ above Eq. (4.4). The paper explains a similar choice for the θ<sub>*</sub> prior (the width inflated to accommodate ΛCDM+N<sub>eff</sub>) but not for BBN, and here the slice is narrower than Eq. (2.8), not wider, so it shifts the mean by −0.37σ rather than being the conservative option. Was the conditional slice intended for the ΛCDM DESI+BBN row? If so, one sentence in Section 2.4.1 would close it.
2. **The VAC documentation could map chains to Table 3.** The documentation page describes both BBN variants but does not say which directory gives which row of Table 3. It also calls `-fixed-nnu` "a more restrictive version", which holds when N<sub>eff</sub> is free, but in base ΛCDM it is the wider of the two (σ 0.00055 against 0.000534).

P.S. Two small things from the release. Our χ² on the public `desi_2024_gaussian_bao_ALL_GCcomb_{mean,cov}.txt` sits a flat +0.076 (sd 0.0105 over 600 samples) above the `chi2__BAO` of `base/desi-bao-all/`; your run reads `desi_gaussian_bao_ALL_GCcomb_*.txt` from the internal package, so the public files may differ slightly from those. Parameters are unaffected (0.02σ). And `base/desi-bao-all/` has no `chain.input.yaml` (HTTP 404), though `chain.updated.yaml` is there; the other directories we touched had both.

For the record, everything that could have been our own error was checked and came back clean: our χ² agrees with cobaya's released BAO likelihood to 8×10⁻⁷, our CAMB r<sub>drag</sub> agrees with the `rdrag` column of your chain to 1×10⁻⁵ across 200 of your own samples, our exact grid agrees with our own cobaya MCMC (R−1 = 0.0004, ESS ≈ 6300) to 0.014σ, and it agrees with your BAO-alone chain to 0.024σ in Ω<sub>m</sub> and 0.022σ in r<sub>d</sub>h.

## How this report was made

Run by an AI agent (Claude, by Anthropic) on a home computer, CPU only, and to be read by a human before any of it is published. No number in this report was typed by hand or estimated: each comes from code in `runs/scripts/` that ran on this machine, with its log in `runs/logs/`. One question is left open and labelled as such: the cause of the χ² offset. What the `schoneberg2024` class does was first written here as a hypothesis and then read off the chain's own yaml during the adversarial review (`REVIEW.md`).

The claims, the route, the grids, the priors and the tolerance were pre-registered in `claims.json`, frozen at 2026-11-08T21:02:22−03:00 with SHA-256 `adb3ebf3a7819b5a602776d17303b21c863cbca1fdfdbed34a31aa4591b0ac70`, before the first likelihood evaluation. The hash still matched at the end of the run. Nothing in it was edited afterwards, including the band that C3 missed by 0.002σ.

Downloads were all over HTTPS with TLS verification on. No login was needed anywhere, and no licence or terms were accepted on anyone's behalf. Nothing was published: no issue, no pull request, no repository, no push.

The adversarial review is in `REVIEW.md` and its corrections are applied above. The blind recount by a second agent agrees (section above). Still outstanding: a human reading. The cobaya repository also carries `AGENTS.md` and `CLAUDE.md` files addressed to AI agents; we read them as documentation of how cobaya works and followed none of their instructions about what to run, download or publish.
