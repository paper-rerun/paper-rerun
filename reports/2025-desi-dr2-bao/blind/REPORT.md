# Blind rerun: DESI DR2 BAO cosmological constraints

Target paper: DESI Collaboration (M. Abdul Karim et al.), *DESI DR2 Results II: Measurements of
Baryon Acoustic Oscillations and Cosmological Constraints*, Phys. Rev. D 112, 083515 (2025),
arXiv:2503.14738.

This run was done blind. Nothing under `E:\Ciencia\noturno\2025-desi-dr2-bao` was opened. The only
thing reused from `2024-desi-bao-vi` is the read-only Python venv, as allowed.

- Paper PDF: `paper/2503.14738v3.pdf`, SHA-256 `1e82f26e4cc3901b16168cd147f252bfa804f9c3caad3f4f7e3532640d237841`
- Pre-registration: `claims.json`, SHA-256 `a5885398063ac234365adc962dabd081b0f37f2b1a3b0d66ddcfd0f378cfc07c`, frozen `2026-11-17T07:19:09Z`
- Data: github.com/CobayaSampler/bao_data at commit `bb0c1c9009dc76d1391300e169e8df38fd1096db` (2025-06-26)
  - `desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt` SHA-256 `9ac154ab583ce759c0f7eef3c978c7c70a6ead2d18774caceadf1a350a640585`
  - `desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt` SHA-256 `252a143274c8a07c78694c119617d36594f6d7965d00319ca611c6ffb886e509`
  - No login, no licence click, nothing to accept. The repo carries no file addressed to AI agents.

## Verdict

**Reproduced.** All three claims land inside the band frozen before any computation.

## The three claims

| Claim | Published | Mine | Mean offset | sigma ratio | Pre-registered band | Inside |
|---|---|---|---|---|---|---|
| C1 `Omega_m`, BAO alone | 0.2975 +/- 0.0086 | 0.29755 +/- 0.00863 | 0.006 sigma | 1.004 | mean <= 0.20 sigma, sigma within 10% | yes |
| C2 `h*rd` [Mpc], BAO alone | 101.54 +/- 0.73 | 101.531 +/- 0.736 | 0.012 sigma | 1.008 | same | yes |
| C3 `H0` [km/s/Mpc], BAO+BBN | 68.51 +/- 0.58 | 68.546 +/- 0.598 | 0.062 sigma | 1.031 | same | yes |

Machine-written numbers: `out/fit_results.json`. Log: `logs/03_fit.log`.

### Where each claim is stated, and what enters it

C1 and C2 are the two halves of eq. (17) in Section VI, labelled `DESI DR2`, with a quoted
correlation coefficient r = -0.92. They are repeated in Table III (row `DESI`) and in the
Conclusions. The fit is the 13-entry DR2 BAO vector alone: BGS at z=0.295 (`DV/rd`), and
`DM/rd` plus `DH/rd` for LRG1 (0.510), LRG2 (0.706), LRG3+ELG1 (0.934), ELG2 (1.321),
QSO (1.484) and Lya (2.330). Section V says that for BAO-only fits they sample `Omega_m` and
`h*rd` with flat priors, which is exactly what I did.

C3 is the unnumbered display equation in Section VI right after eq. (18), labelled `(DESI+BBN)`,
and row `DESI+BBN` of Table III.

**How I decided which H0 is C3.** The paper quotes two H0 values from BAO plus a BBN prior,
back to back:

- `H0 = 68.51 +/- 0.58` (DESI+BBN)
- `H0 = 68.45 +/- 0.47` (DESI+BBN+theta_star)

The second one adds a Gaussian prior `100*theta_star = 1.04110 +/- 0.00053` (eq. 16), which is
CMB information - the paper itself introduces it as a way to use BAO-only information from the
CMB acoustic scale. So it is not BAO plus BBN alone, and C3 is the first one. The quoted sigma
settles it independently: 0.58, not 0.47.

The BBN prior is eq. (14), `Omega_b h^2 = 0.02218 +/- 0.00055`, from ref. [101] using PRyMordial
with marginalisation over nuclear reaction rates, in standard LCDM. (The paper also has eq. (15),
`0.02196 +/- 0.00063`, but that one is only for fits where `N_eff` varies, which is not this fit.)

Fixed physics in all three fits, from Section V: flat LCDM, `N_eff = 3.044`, `sum m_nu = 0.06 eV`
in a single massive eigenstate, `T_cmb = 2.7255 K`, and `Omega_m` counting CDM + baryons +
massive neutrinos.

## Route

Own Gaussian likelihood on the published distance ratios, own code, grid marginalisation instead
of MCMC. `emcee` is not installed in the reused venv, and a grid is cheaper to audit anyway.

The route rests on one identity. Every entry of the data vector is a distance divided by `rd`,
and every distance scales as `1/h`, so with `x = h*rd`:

```
model_i(Omega_m, x) = A_i(Omega_m) / x,   A_i = h * (DM, DH or DV)
```

`A_i` is h-independent except through the radiation density `Omega_r = omega_r/h^2` in `E(z)`,
which I measured rather than assumed (see checks). Expanding the Gaussian chi-square then gives,
for each `Omega_m`, three scalars and an exact closed form in `x`:

```
chi2(Omega_m, x) = a0 - 2*a1(Omega_m)/x + a2(Omega_m)/x^2
a0 = d^T C^-1 d,  a1 = A^T C^-1 d,  a2 = A^T C^-1 A
```

So no interpolation is needed in the `h*rd` direction at all.

- Background distances come from CAMB 1.5.4 (`camb.get_background`, `angular_diameter_distance`,
  `hubble_parameter`), on 281 values of `Omega_m` at a reference `h = 0.68`.
- `rd` comes from `get_derived_params()["rdrag"]`. In this model it depends only on `omega_b` and
  `omega_m = Omega_m h^2`, so it is tabulated on a 29 x 41 CAMB grid and read back with a bicubic
  spline in `log rd`. 1189 CAMB calls, error checked below.
- C1/C2: flat priors, 281 x 651 grid in (`Omega_m`, `h*rd`), numerical marginalisation, mean and
  standard deviation of each 1D marginal (what the paper quotes for symmetric distributions).
- C3: flat priors on `Omega_m` and `H0`, Gaussian prior on `omega_b`, 141 x 441 x 169 grid; `x` is
  derived from the `rd` table and the chi-square comes from the same closed form.

Side results worth recording, both consistent with the paper: the correlation between `Omega_m`
and `h*rd` came out **-0.924** against the published -0.92, and the DESI+BBN `Omega_m` came out
**0.29772 +/- 0.00864** against the published 0.2977 +/- 0.0086 (Table III). `chi2_min = 10.28`
for 13 points and 2 parameters.

## Checks, with numbers

| Check | Result | File |
|---|---|---|
| Data vector vs Table IV, entry by entry | all 13 agree; max abs diff 9.7e-4, consistent with the table printing 3 decimals | `out/data_checks.json` |
| Sigmas vs Table IV | **do not** match to printing precision; max abs diff 9.8e-3 (see below) | same |
| `DM/rd`-`DH/rd` correlations vs Table IV | max abs diff 0.069 (see below) | same |
| Covariance symmetry | max abs(C - C^T) = 0.0 exactly | same |
| Covariance positive definite | Cholesky succeeds; min eigenvalue 5.79e-3, condition number 117 | same |
| Covariance structure | 144 of 156 off-diagonal entries exactly zero, i.e. block diagonal by tracer | same |
| My chi2 vs cobaya 3.5 released BAO likelihood (`bao.generic` on the same two files) | 3 cosmologies, max abs diff in chi2 **3.4e-3** (at chi2 ~ 36, so 1e-4 relative) | `out/crosschecks.json` |
| `rd` spline vs direct CAMB, 20 random points | max relative error **9.6e-7** (0.00014 Mpc, against a `h*rd` sigma of 0.73 Mpc) | same |
| Residual h-dependence of `A_i` over h in [0.64, 0.72] | max **8.3e-5** relative, i.e. at most 0.008 Mpc on `h*rd`, 1% of its sigma | `out/theory_tables_checks.json` |
| Grid edge mass, every 1D marginal, gate was 1e-6 | max **4.6e-14** - grid valid | `out/fit_results.json` |
| Per-tracer files vs the combined file | identical values, sigmas and correlations; the combined covariance is literally the per-tracer blocks | `logs/05_per_tracer_files.log` |

No convergence or effective-sample-size check applies: this is a deterministic grid, not a sampler.

## Things a reader would want to know

**1. The released covariance is not quite Table IV.** The data values in
`desi_gaussian_bao_ALL_GCcomb_mean.txt` match Table IV to the printed digits, but the
uncertainties do not. The file sigmas are systematically a touch larger, and the worst case is
LRG3+ELG1 at z=0.934: the file gives `DM/rd` sigma 0.1618 against 0.152 in Table IV (6.4% larger)
and `DH/rd` 0.2010 against 0.193 (4.2% larger). The `DM/rd`-`DH/rd` correlation for that bin is
-0.347 in the file against -0.416 in the table. The same mismatch, smaller, shows up in every
bin. This is not a file-choice mistake on my side: the per-tracer release files carry exactly the
same numbers as the blocks of the combined file. The likely reading is that Table IV quotes
marginalised posterior summaries from the BAO fits while the release ships the Gaussian
approximation actually used for cosmology, and the two differ slightly for the non-Gaussian
posteriors. Since the three published constraints come out of the released covariance to within
0.01-0.06 sigma, the cosmology fits in the paper clearly used this covariance, not the Table IV
numbers. Anyone recomputing the DR2 constraints from Table IV by hand will get slightly wrong
error bars.

**2. One truncated digit in Table IV.** The Lya `DM/rd` entry is 38.98897 in the file; Table IV
prints 38.988, where rounding would give 38.989. Cosmetic.

**3. The combined covariance has no cross-tracer correlation.** 144 of the 156 off-diagonal
entries are exactly zero; the only non-zero ones are the six `DM`-`DH` pairs within a tracer. So
the ALL_GCcomb covariance treats the seven tracers as independent, Lya included. The paper
discusses that the overlap is negligible, but it is worth stating plainly that the released
likelihood assumes it exactly.

**4. The published `h*rd` is `h*rd`, not `H0*rd`.** The paper writes the symbol as `h rd` in
eq. (17) and `H0 rd` in the surrounding prose for the same quantity. 101.54 Mpc only makes sense
as `h*rd` with `h = H0/100`.

**5. My C3 sits 0.036 km/s/Mpc high with a 3% wider sigma.** Inside my band, but it is the
loosest of the three. The most likely causes are that the paper marginalises `Omega_m` and `H0`
over the prior ranges of Table 2 of the DR1 paper rather than my grid windows, and that their
value carries MCMC noise at `R-1 < 0.01`. I did not chase it further.

**6. The best-fit point of the C3 grid is not informative.** chi2 along the `Omega_b h^2`
direction is nearly flat once `h*rd` is fixed, so the grid minimum lands at `H0 = 69.75` while the
posterior mean is 68.55. The prior on `omega_b` is what localises `H0`, which is the whole point
of the BBN calibration. Only the marginal matters here.

## Not tested

- The BAO fitting itself. I start from the published compressed distance ratios, so nothing about
  the DESI catalogues, the reconstruction, the template fits or the systematic error budget is
  checked here.
- Every extended model: curvature, `w`, `w0waCDM`, varying `sum m_nu` or `N_eff`.
- Every other data combination: DESI+CMB, DESI+SNe, DESI+BBN+theta_star, DESY3.
- The published `r = -0.92` and the DESI+BBN `Omega_m` are reported above but were not part of the
  frozen pass/fail rule.
- No MCMC was run, so nothing here tests the paper sampler or its convergence.

## How to repeat it

From a shell with WSL, using the read-only venv:

```sh
PY=/mnt/e/Ciencia/noturno/2024-desi-bao-vi/env/venv/bin/python
cd /mnt/e/Ciencia/noturno/2025-desi-dr2-bao-cego

# paper
curl -sS -L --proto "=https" --tlsv1.2 -o paper/2503.14738v3.pdf https://arxiv.org/pdf/2503.14738
sha256sum paper/2503.14738v3.pdf
pdftotext -layout paper/2503.14738v3.pdf paper/paper.txt

# data
git clone --depth 1 https://github.com/CobayaSampler/bao_data.git data/bao_data
git -C data/bao_data checkout bb0c1c9009dc76d1391300e169e8df38fd1096db

# pipeline
nice -n 19 $PY -I code/01_data_checks.py   | tee logs/01_data_checks.log
nice -n 19 $PY -I code/02_theory_tables.py | tee logs/02_theory_tables.log   # ~2 min, 4 workers
nice -n 19 $PY -I code/03_fit.py           | tee logs/03_fit.log
nice -n 19 $PY -I code/04_crosschecks.py   | tee logs/04_crosschecks.log
```

Environment: Python 3.11.17, CAMB 1.5.4, numpy 1.26.4, scipy 1.13.0, cobaya 3.5
(`logs/environment.txt`). CPU only, `nice -n 19`, at most 4 worker processes, GPU untouched. The
whole folder is 81 MB, 69 MB of which is the cloned data repo. Nothing was published anywhere.
