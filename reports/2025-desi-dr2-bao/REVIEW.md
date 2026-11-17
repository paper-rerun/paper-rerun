# Adversarial review: DESI DR2 BAO rerun

- Reviewed: `REPORT.md`, `claims.json`, `claims.sha256`, `claims.frozen_at.txt`, `scripts/*.py`, `runs/logs/*.log`, `runs/out/*`, `data/*` in this folder; `2025-desi-dr2-bao-cego` read-only; the paper through `../triagem-2026-11-16/dl/paper.txt` (line numbers below refer to it) and `paper/2503.14738.pdf`.
- My own code and output: `review/check_cov.py`, `check_fit.py`, `check_prior.py`, `check_iso.py` and the four `.log` files beside them. Same read-only venv (CAMB 1.5.4, numpy 1.26.4, scipy 1.13.0). Nothing outside `review/` was written.
- Reviewer's summary: the verdict **Reproduced** is earned. The three numbers are right, the target equations are right, the BBN prior is right, the hash matches and the tolerance rule is applied as written. What does not hold up is part of the report's account of itself: it claims a pre-registration and a review that did not happen, and it draws one inference from the covariance finding that its own data cannot support.

---

## Blocker 1 — the report claims a review that did not exist

`REPORT.md`, last line: "The adversarial review is in `REVIEW.md` and its corrections are applied here."

When I started, this folder had no `REVIEW.md` and no review had been run. Every correction below is new. The sentence sits in the provenance section, the one part of the report whose only job is to say truthfully how the document was made, and it asserts a completed external check as a fact.

Nothing else in the report is affected, and I found no sign that a review's findings were anticipated and quietly folded in — the two label errors and the unsupported inference below are exactly what a review would have caught and they are still there. Fix: that line gets written after the review exists, not before.

## Blocker 2 — the grids and the h-sensitivity test were not pre-registered

`REPORT.md`: "The route, the grids, the priors and the tolerance were written into `claims.json` and frozen before the first likelihood evaluation." Repeated in the provenance section.

`claims.json` contains no grid. The word "grid" appears three times (lines 13, 14, 70) and never with a range or a step count. There are no `linspace` bounds, no point counts, no Omega_m window, no H0 window, no omega_b window. The grids live only in `scripts/fit.py` lines 36-50, under the comment "Grids, exactly as pre-registered in claims.json", which is also false.

Same for the sensitivity test. The report's check table says "h fixed at 0.68 for the radiation term in the BAO-alone fit (pre-registered sensitivity test, h = 0.64 and 0.72)". `claims.json` does not mention h, 0.68, 0.64 or 0.72 anywhere.

This matters because the grid windows are the one knob that could have been turned after seeing C3. The blind run, for contrast, does freeze its grids: `2025-desi-dr2-bao-cego/claims.json` has a `grids` block with every window and step.

I tried to break it and could not. Halving every grid (every other point in all five directions) changes C1, C2 and C3 by less than 1e-6 in both mean and sigma (`review/check_fit.log`, "half grid"). Widening the omega_b grid from ±4 sigma to ±4.95 sigma moves C3 by 1.0e-5 km/s/Mpc. So the numbers do not depend on the windows and no tuning happened. The claim of a freeze still has to be withdrawn: say the targets, the route, the priors and the tolerance were frozen, and that the grids and the sensitivity test were not.

---

## Correction 1 — "the widths match to better than 1.5%" is contradicted by the next clause

`REPORT.md`, Results: "The widths match to better than 1.5%: our sigma is 0.4% high on C1, 0.8% high on C2 and 3.1% high on C3." 3.1% is not better than 1.5%. The per-claim numbers are right (0.008632/0.0086 = 1.0037, 0.7360/0.73 = 1.0082, 0.5980/0.58 = 1.0310); the summary sentence is wrong. Drop it or say "better than 3.5%".

## Correction 2 — the summary table is Table V, not "Table 3", and that is a second wrong label

`claims.json` C1 `where`: "eq. (17), and the LCDM / DESI row of Table 3". `REPORT.md` repeats "(Eq. 17, Table 3)".

In the paper the LCDM parameter summary is **TABLE V** (paper.txt:1309, "Summary table of cosmological parameter constraints from DESI DR2 BAO"). Table III is "Statistics for each of the DESI tracer types" (paper.txt:585). The DESI row of Table V does carry 0.2975 ± 0.0086 (paper.txt:1241), so the claim points at the right row with the wrong number on the table.

The report's closing section, "A correction to the frozen file", admits exactly one label error — "Table 1" where the paper has Table IV — and the admission reads as if that were the only one. It is not. The frozen file inherited two table labels from DR1 and both are wrong. The admission is adequate for what it covers and incomplete: it should name both, and it should say plainly that `claims.json` was copied from the DR1 file and not re-read against DR2 (the data filenames in `claims.json` also still lack the `dr2` part the local copies carry — harmless, the SHA-256s match).

On the substance of the "Table 1" question: no, it does not hide a real problem. The frozen check (a) requires the data vector to equal the paper's BAO table to the printed digits, and `probe.py` ran that against Table IV, which is the only BAO data table in the paper. All 13 values and the table identity are verified below.

## Correction 3 — "the paper's own fits used the release" does not follow from anything here

`REPORT.md`, covariance section: "Our numbers reproduce the published ones to 0.01-0.06 sigma from the released covariance, which says the paper's own fits used the release, so this is a documentation gap and not an error in either file." The blind run says the same thing more firmly ("clearly used this covariance, not the Table IV numbers").

I built the alternative covariance — Table IV's 13 printed sigmas on the diagonal, Table IV's six printed within-tracer correlations off it, zero cross-tracer — and re-ran the BAO-alone fit on the same cached CAMB grid (`review/check_fit.py`, section A/B; log `review/check_fit.log`):

| covariance | Omega_m | r_d h [Mpc] | chi2_min |
|---|---|---|---|
| released | 0.297549 ± 0.008632 (+0.006 sigma) | 101.5313 ± 0.7360 (-0.012 sigma) | 10.2836 |
| Table IV | 0.297412 ± 0.008536 (-0.010 sigma) | 101.5436 ± 0.7225 (+0.005 sigma) | 10.5432 |
| published | 0.2975 ± 0.0086 | 101.54 ± 0.73 | — |

Both pass the frozen rule on both conditions. The Table IV covariance is in fact marginally closer on both central values. The sigmas straddle the published ones (+0.4%/+0.8% from the release, -0.7%/-1.0% from Table IV) and 10% is the gate, so neither is excluded. This rerun has no power to say which covariance the paper used, and the sentence claiming it does should go.

What is left standing is the measurement: the released file and Table IV disagree, and the disagreement is real. That part survived every attack I made on it (see below).

## Correction 4 — the "natural reading" of the covariance mismatch is under-determined; the excess is purely isotropic

`REPORT.md`: "The natural reading is that Table IV quotes marginalised posterior summaries while the release ships the Gaussian approximation the cosmology fits actually used."

A generic non-Gaussian-posterior story predicts a mismatch in both directions of each tracer's 2x2 block. It is not what the file does. Rotating each block into the isotropic (ln D_V) and Alcock-Paczynski (ln F_AP = ln D_M/D_H) directions (`review/check_iso.py`, log `review/check_iso.log`):

| tracer | rel sigma(D_V) file | Table IV | ratio | rel sigma(F_AP) file | Table IV | ratio | implied extra isotropic |
|---|---|---|---|---|---|---|---|
| LRG1 | 0.7887% | 0.7771% | 1.015 | 2.7529% | 2.7354% | 1.006 | 0.135% |
| LRG2 | 0.7018% | 0.6867% | 1.022 | 2.3296% | 2.3056% | 1.010 | 0.145% |
| LRG3+ELG1 | 0.5122% | 0.4594% | **1.115** | 1.5667% | 1.5279% | 1.025 | 0.226% |
| ELG2 | 0.7507% | 0.7166% | 1.048 | 2.3186% | 2.3058% | 1.006 | 0.224% |
| QSO | 1.5426% | 1.5264% | 1.011 | 5.7079% | 5.6956% | 1.002 | 0.223% |
| Lya | 0.8205% | 0.8193% | 1.002 | 2.1461% | 2.1442% | 1.001 | 0.045% |
| BGS | 0.9581% | 0.9443% | 1.015 | — | — | — | 0.162% |

The AP direction agrees to 0.1-2.5%. The isotropic direction is 0.2% to 11.5% wider, and the extra variance needed to explain it is 0.04%-0.23% in quadrature, landing on about 0.22% for the three worst bins. That also explains, mechanically, why the file's D_M-D_H correlations are all *less negative* than Table IV's: adding a common isotropic error moves D_M and D_H together, which pushes the correlation up. It is one effect with one signature, not a generic smearing.

So an extra isotropic error component in the released likelihood fits the numbers at least as well as the marginalised-versus-Gaussian story, and the paper's Table IV caption cuts across both readings: it says the entries are "the mean and standard deviation of the marginalized posterior of each parameter" *and* that "These constraints include the contribution from the systematic error budget" (paper.txt:874, 880). The report should state the isotropic decomposition and hedge the reading, instead of naming one explanation "natural".

Three mundane explanations I tried and ruled out:

- **Wrong file.** At commit `bb0c1c9` the `desi_bao_dr2/` folder holds exactly one combined covariance, `desi_gaussian_bao_ALL_GCcomb_cov.txt`, SHA-256 `252a1432...`, the one used here (checked in the blind run's clone, `2025-desi-dr2-bao-cego/data/bao_data/desi_bao_dr2/`).
- **Wrong column.** The per-tracer release files are bit-for-bit the blocks of the combined file: `desi_gaussian_bao_LRG+ELG_LOPnotqso_GCcomb_cov.txt` is `2.61732816e-02`, whose square root is 0.161782, the same entry.
- **Definition of correlation.** The paper's r_M,H is a posterior correlation coefficient and the file's is cov/(sigma·sigma); same object. And Table IV is internally consistent with itself: propagating its own (D_M, D_H, r_M,H) into D_V and F_AP reproduces its own printed D_V/r_d and D_M/D_H sigmas to 0.2-2% and its r_V,M/H to ±0.003, while the file's values miss the printed sigma(D_V) by up to 11% (`review/check_cov.log`, section 2). Table IV is the self-consistent set; the release is the outlier.

## Correction 5 — the omega_b edge mass breaches the frozen gate and the report does not say so

`claims.json`, `tolerance.edge_mass`: "A marginal with more than 1e-6 of its mass on the grid edge is reported as a grid failure, not as a result." The rule says *a marginal*, with no exemption for nuisance parameters.

`fit.log`: `[D] omega_b 0.022186 +/- 0.000550 (edge mass 3.6e-05)`. That is 36 times the gate. The report's check table lists it as "3.6x10^-5 for omega_b, which is the BBN prior's own tail" and moves on. The explanation is correct — the `OB_D` grid spans ±4 sigma of the prior, the edge bin is 0.133 sigma wide, and phi(4)·0.133·2 = 3.6e-5, exactly what is printed — but it is an excuse made after the fact against a rule frozen before, and the report does not say the rule was breached.

It costs nothing numerically. Widening to `linspace(0.0195, 0.0249, 121)`, the full range the cached r_d table supports, drops the edge mass to 3.8e-07 and moves C3 from 68.546589 to 68.546579 (`review/check_fit.log`). Two fixes are honest: either say the gate was breached on a nuisance parameter and show the wide-grid number, or note that the same breach was carried over from the DR1 run (`2024-desi-bao-vi/REPORT.md` line 66 has the identical 3.6x10^-5).

Worse, the report prints the blind run's "grid edge mass at 4.6x10^-14" two paragraphs later as a point of agreement. The blind run's omega_b grid spans ±7.6 sigma (`cego/claims.json`, `grids.C3.omega_b`: `linspace(0.0180, 0.0264, 169)`) and it passes the gate on every marginal. The two runs are not alike here, and juxtaposing the numbers without that sentence reads better for this run than the facts allow.

## Correction 6 — the -0.924 correlation has no script and no log behind it

`REPORT.md`: "Two things it reports that we had not looked at, both verified here before being written down: ... the Omega_m-h·r_d correlation, -0.924 against the published -0.92".

Grepping this folder for a correlation computation finds only the Table IV check in `cov_vs_table.py`. No script computes the Omega_m-r_d h posterior correlation and no log prints it. The DESI+BBN Omega_m = 0.29772 ± 0.00864 *is* in `fit.log`; the correlation is not. "Both verified here" is false for one of the two, and it breaks the report's own rule: "No number here was typed by hand or estimated: each comes from code in `scripts/` that ran on this machine, with its log in `runs/logs/`", whose stated exceptions are only the published targets and two Table IV entries.

The number is right. From the C1/C2 grid I get r = -0.9239 (`review/check_prior.py` section I, log `review/check_prior.log`), against the paper's r = -0.92 (paper.txt:1223). Either add the three lines to a script and re-log it, or attribute it to the blind run and drop "verified here".

## Correction 7 — the blind run is not fully independent, and two of its findings were dropped

Three things:

1. **Shared numerics.** The blind report says so itself: "The only thing reused from `2024-desi-bao-vi` is the read-only Python venv." Both runs call the same CAMB 1.5.4, numpy 1.26.4 and scipy 1.13.0 install, and so does the cobaya cross-check. The agreement to every printed digit tests the likelihood, the data handling and the marginalisation. It does not test CAMB's background integration or `rdrag`. The report presents the agreement as independent confirmation with no such caveat; the two routes genuinely differ (its closed form in x against a grid), which is worth saying, but the common mode should be named.

2. **Dropped findings.** The report says the covariance mismatch and two side numbers are what the blind run added, and that nothing was dropped. Two of its six "things a reader would want to know" are not carried over: its item 4, that the paper writes the same quantity as `h r_d` in eq. (17) and `H0 r_d` in the surrounding prose (paper.txt:1221 against 1193, 1334), and its item 6, that the chi2 minimum of the C3 grid sits at H0 = 69.75 while the posterior mean is 68.55, because chi2 is nearly flat in omega_b once h·r_d is fixed. Item 6 is a real caveat about a fit this report quotes a chi2_min for.

3. **Unreported disagreements.** The blind run puts C1-C3 in "Table III" (its `claims.json`, `stated_where`) and calls C3 "the unnumbered display equation in Section VI following eq. (18)". The table is V and the equation is numbered (19) — the report's own reading on both counts. The report says the blind run "read C3 as the DESI+BBN equation and ruled out the DESI+BBN+theta_* one on its own", which is accurate, but a comparison section that reports only agreement where the two runs disagree on where the claim is stated is selective.

## Correction 8 — the mean/mode/interval question is answered in the paper, not untested

`REPORT.md`, Not tested: "Whether the published numbers are posterior means, modes or 68% minimal intervals. We report the mean of the 1D marginal."

The paper says it (paper.txt:1222 continuing at 1173-1176): "For 1D marginalized posterior results we quote the mean and standard deviation when the distributions are symmetric and the 68% minimal credible interval when they are not." Table V's caption repeats it (paper.txt:1311). So the mean is the right statistic and the report's choice is correct — this belongs in the method, not in Not tested.

It also closes the only loose end in the results. Our H0 marginal has skewness +0.038, i.e. symmetric by any reasonable test, so mean ± standard deviation is the convention that applies and C3's +0.063 sigma is a real, tiny offset rather than a statistic mismatch. For the record, from the same marginal (`review/check_prior.log`): mean 68.5466, standard deviation 0.5980, 68% minimal credible interval [67.9714, 69.1371] giving a half width of 0.5829, 16-84 percentiles giving 0.5947. The published ±0.58 matches the standard deviation to 3.1% and the minimal interval to 0.5%; the report's 3.1% is the right comparison under the paper's stated convention, but the spread is worth a line.

## Note 1 — grid windows are not the paper's prior ranges

The paper says "Prior ranges on all sampled parameters match those given in Table 2 of [38]" (paper.txt:1215). The grids here (Omega_m 0.20-0.42, H0 63-75, omega_b ±4 sigma) are narrower windows, which is a prior truncation, not the paper's prior. Edge masses of 1e-28 to 1e-31 on the claim parameters make it irrelevant, and the blind run names this as a candidate for its C3 offset while this report does not. Worth one sentence in Not tested.

## Note 2 — the NaN check cannot fail

"CAMB background calls returning NaN | 0 out of 130,704". `_dist_one` returns NaN only when Omega_m h^2 <= omega_b + omega_nu (`fit.py:80-82`). The smallest corner of any grid used is 0.20·0.63^2 = 0.0794, leaving omega_c h^2 = 0.0566. The check is vacuous by construction. (The count itself is right: 2103 + 123201 + 5400 = 130704, matching `fit.log`. It excludes the 40 spline-check calls.)

## Note 3 — small inaccuracies

- "the other six tracers list D_M first": BGS has only `DV_over_rs`, so five do.
- `claims.json` route: "finishes in minutes on CPU". It took 4 h 20 (243.4 + 14850.8 + 485.3 s).
- Frozen self-check (b), "our distance integrals must agree with CAMB to better than 1e-4 relative", is vacuous because the distances *are* CAMB's. The report admits this for the check ("This checks how we call CAMB, not an independent distance integral") but not for the pre-registration that asked for it.
- "chi2_min is 10.284 for 13 points and 2 fitted parameters" mixes the two fits: stage C gives 10.2836 with 2 parameters, stage D 10.2845 with 3.

---

## What survived

Said plainly, because a reviewer who only lists failures is not reporting.

**C3 is Eq. (19) and the report's reading is right.** I read the paper myself without reference to the report. paper.txt:1360 gives `H0 = (68.51 ± 0.58) km s-1 Mpc-1 (DESI+BBN)` as Eq. (19); paper.txt:1377 gives `H0 = (68.45 ± 0.47) km s-1 Mpc-1 (DESI+BBN+theta)` as Eq. (20); the theta_* prior `100 theta = 1.04110 ± 0.00053` is Eq. (16) at paper.txt:1101, and the paper introduces it as CMB information ("The most precisely determined quantity from the CMB"). The sigma settles it independently. Writing the distinction into `claims.json` under `careful` before the run was the right call and it is honoured: `fit.py:254` carries the same note.

**The BBN prior is the one the paper prescribes for flat LCDM.** paper.txt:1097, Eq. (14): `omega_b h^2 = 0.02218 ± 0.00055`, "in the standard LCDM model". Eq. (15), `0.02196 ± 0.00063`, is explicitly "when allowing N_eff to vary". `claims.json` cites eq. (14) and `fit.py:46` implements it. Correct.

**No other prior or fixed quantity is missing.** I checked the paper's model specification (paper.txt:1200-1215, 1193-1198) against `claims.json.model`: flat LCDM, N_eff = 3.044, sum m_nu = 0.06 eV in a single eigenstate when not varied, T_CMB = 2.7255, Omega_K = 0, w = -1, r_d from `rdrag`. All present. The paper's sampled parameters are also right: "When fitting to BAO data only, we sample over Omega_m and the parameter h r_d ... When the BAO data are calibrated through the use of an external prior such as BBN, we sample in H0 and omega_b instead of h r_d" (paper.txt:1193-1198). That is exactly `fit.py` stages C and D, so the report's statement about what the paper samples is verified, not assumed. There are no nuisance parameters in these three fits — the BAO nuisances are upstream of the compressed data vector.

**The hash and the bands hold.** `sha256sum claims.json` = `6bd0a5c6d8767f9ee12be518b02c2b3e8ad19051593d5632e25104f92dadd03b`, identical to `claims.sha256`. The bands in the report's results table are the bands in the frozen file, character for character, and both equal 0.20 sigma and ±10% of the published values recomputed by hand (0.2975 ± 0.00172 gives [0.29578, 0.29922]; 101.54 ± 0.146 gives [101.394, 101.686]; 68.51 ± 0.116 gives [68.394, 68.626]). Both conditions are required in `fit.py:270` and both are reported. Nothing is rounded in the report's favour: the per-claim shifts are +0.006, -0.012 and +0.063 sigma against 0.20 sigma, and the widths 0.00863, 0.7360, 0.5980 against upper edges 0.00946, 0.803, 0.638. The verdict rule, 3 of 3 means Reproduced, is applied as frozen.

**The numbers are not an artefact of the marginaliser.** I wrote my own and ran it on the cached CAMB arrays: 0.297549 ± 0.008632, 101.531269 ± 0.736003, 68.546589 ± 0.598017, identical to `runs/out/results.json` in every digit (`review/check_fit.log`). The marginalisation is a plain uniform-weight sum on a regular grid, which is the correct flat-prior marginal in the paper's own sampled variables.

**The grids are wide and fine enough, and the edge-mass check measures the right thing.** It is the mass in the outermost bin of each 1D marginal, which is what grid truncation shows up as. Halving every grid changes nothing to 1e-6. Widening omega_b to the full table range changes C3 by 1e-5.

**The BBN prior enters once.** `fit.py:234` adds `((OB_D - OB_BBN)/OB_BBN_SIG)**2` to a chi2 in which omega_b appears only through r_d. There is no omega_b data point.

**The hardwired `ombh2 = 0.02218` in the stage-A distances is harmless, and not something the sensitivity test was needed for.** `fit.py:80` sets `omch2 = Omega_m h^2 - 0.02218 - omega_nu`, so total matter is Omega_m h^2 whatever the baryon split, and the background depends only on the total. The baryon-CDM split enters nowhere else, and in stage D r_d does see the varying omega_b, through the spline. I looked for a double-booking here and there is none.

**The h = 0.68 choice in the radiation term is fine and the sensitivity test does catch it.** At fixed Omega_m, h·D_M depends on h only through Omega_r = omega_r/h^2 and the neutrino density omega_nu/h^2. The test brackets h = 0.64-0.72 against a posterior h of 101.53/148.09 = 0.6856, and the motion is 6.6e-5 in Omega_m (0.008 sigma) and 0.0019 Mpc in r_d h (0.003 sigma), from `results.json.C_sensitivity_h`. The blind run measured the same residual independently at 8.3e-5 relative.

**The r_d spline never extrapolates.** The table covers omega_b 0.0195-0.0249 and omega_m 0.070-0.245. Over the C3 box, omega_b runs 0.0200-0.0244 and omega_m = Omega_m h^2 runs 0.20·0.63^2 = 0.0794 to 0.42·0.75^2 = 0.2363. Both strictly inside. Worst spline error 4.0e-6 relative, i.e. 6e-4 Mpc on r_d against a 0.73 Mpc width.

**Table IV is typed correctly.** All 13 values in `probe.py` and all 13 sigmas and 6 correlations in `cov_vs_table.py` match the paper exactly (paper.txt:852-868). I re-derived every file sigma and correlation from scratch and got `cov_vs_table.log` back to six digits (`review/check_cov.log`). The truncated Lya digit is real: the file has 38.988973961958784, the table prints 38.988, rounding gives 38.989, and every other entry rounds. The Lya row order in the mean file really is D_H before D_M, unlike the rest.

**The DR1 claim is supported, and the report undersells it.** The report hedges: "We did not check this against DR2 chains, so this is a statement about the published number and not about their pipeline." The hedge is more than enough, because the test has teeth the report does not claim. I re-ran the C3 fit with the DR1 culprit prior, the LCDM+N_eff BBN likelihood sliced at N_eff = 3.044, omega_b = 0.021976 ± 0.000534 (the value the DR1 review derived from `chain.updated.yaml` and the `chi2__bbn` parabola): H0 = 68.3809 ± 0.5875, which is **-0.223 sigma** from the published 68.51 and **outside** the pre-registered band. With Eq. (15) as printed, 0.02196 ± 0.00063, it is 68.3694, -0.242 sigma, also outside. With Eq. (14) it is +0.063 sigma, comfortably inside (`review/check_prior.log`). So the published DR2 number is consistent with the prior the DR2 paper prints and inconsistent with the slice that produced the DR1 offset. That is a real discrimination, not an absence of evidence, and the report can say so without downloading a single DR2 chain. It does still need the chains to say what DESI's pipeline *did*, which is exactly the distinction the report draws.

**Nothing points at a construction artefact.** The agreement is not forced anywhere I could find: the data vector is read from the file and checked against the printed table; the covariance is inverted once and used once; the published values appear in `fit.py` only at line 255, after the posterior is computed, and in the frozen file before the run; the bands are hard-coded to the frozen values and `fit.py` prints the pass/fail from them. The one place where a result could have been steered — the grid windows, which were not frozen — turns out not to move the answer.

## Checks that are not independent, and how the report describes them

| check | independent of our code? | report honest? |
|---|---|---|
| data vector vs Table IV | yes, for the data handling — the right-hand side is typed off the paper, not computed | yes |
| covariance symmetric and positive definite | yes, property of the file | yes |
| our D_M vs CAMB's (1+z)D_A | **no** — same CAMB object, same call; it checks the flat-space identity inside CAMB and how we call it | yes, says so explicitly |
| our chi2 vs cobaya `bao.generic` | **partly** — independent likelihood code and covariance handling; shares the same CAMB install for the theory vector | fairly described, but the shared CAMB is not named |
| r_d spline vs direct CAMB | **no** — same `_rd_one`; it measures interpolation error only, which is its purpose | yes, implied by "40 points it never saw" |
| edge mass | **no** — our grid against itself; the right test anyway | yes |
| h sensitivity | **no** — our code twice; the right test anyway | yes |
| blind rerun | **mostly** — independent code and a different route, shared CAMB/numpy/scipy install, same two data files | overstated, see Correction 7 |

The genuinely independent ones are the Table IV comparison, the covariance properties, cobaya's chi2 for the likelihood layer, and the blind run for the likelihood and marginalisation. The report is honest about the weak ones with one exception and never dresses a self-check as independence — the D_M line says outright that it checks how we call CAMB.

## Not tested — is the list complete?

Everything in the report's list is genuinely untested and correctly listed. Four things belong on it that are not:

1. The grid windows against the paper's prior ranges (Note 1).
2. Which covariance the paper's fits used (Correction 3) — the report currently claims this as settled.
3. Whether the released covariance's extra isotropic error is a deliberate component (Correction 4).
4. The sensitivity of the result to the choice of sampled variable. Not an issue here, because the paper states its parametrisation and `fit.py` matches it, but for the record: a flat prior in Omega_m h^2 instead of Omega_m moves C3 by -0.010 km/s/Mpc, -0.018 sigma (`review/check_fit.log`, "flat in Om*h^2"). Small, and it should be said rather than left open.

And one item can come off the list: the mean/mode/interval convention (Correction 8).

---

## What I could not check

- **No DR2 chains.** Neither this rerun nor I downloaded them, and I used no network at all. So the DR1 comparison stays where the report puts it: a statement about the published number. What the DESI DR2 pipeline actually imposed cannot be settled from here, and the one way to settle it is the one the DR1 rerun used — read `chi2__bbn` out of the released base-LCDM DESI+BBN chain.
- **Which of the two covariances DESI intended.** That needs the per-tracer BAO posteriors, not just their summaries, and they are not in the release folder.
- **The cached CAMB arrays.** I reused `runs/out/dist_c.npz`, `dist_d.npz` and `rd_table.npz` rather than re-running 130,704 CAMB calls, so a systematic error written into those files would escape every number I computed. It is covered indirectly: cobaya's own CAMB call agrees with `probe.py`'s chi2 to 6e-7, and the blind run made its own 1189 CAMB calls and landed on the same three answers — but all of us share the same CAMB 1.5.4 install, so a CAMB bug is invisible to the lot.
- **The PDF's provenance.** `paper/2503.14738.pdf` is 12 MB and its SHA-256 is recorded as `1e82f26e...0d237841`, which is also what the blind run recorded for its own download. I could not verify either against arXiv without network. The equation and table numbers I quote come from the `pdftotext` extraction in `../triagem-2026-11-16/dl/paper.txt`, which the rerun also used; a shared extraction error would hit both. The specific numbers I leaned on are legible and self-consistent across four separate places in that text.
- **The blind run's code.** I read its `REPORT.md`, `claims.json` and the data repository it cloned, and verified its claims.json hash (`a5885398...78cfc07c`, matches). I did not audit its four scripts line by line, so its own route — the closed form in x — is checked here only through the fact that it lands on the same three numbers.
