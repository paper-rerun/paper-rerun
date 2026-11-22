# Blind recount of Table 4 — Afzal et al. 2023, NANOGrav 15 yr New Physics

Independent recomputation. The parallel attempt's folder was not read: inside
E:/Ciencia/noturno/2023-afzal-nanograv15-newphysics only downloads/ and extraido/
were opened, and triagem-2026-11-21/ was not touched at all.

- Paper: Afzal et al., ApJL 951, L11 (2023), arXiv:2306.16219, doi 10.3847/2041-8213/acdc91
- Target: Table 4, the longtable labelled tab:list
- Data: the authors' Zenodo deposit, record 8083620, chains/stochastic/, CC-BY-4.0
- Pre-registration: PREREG.md, frozen before any chain was opened; hashes in FREEZE.txt
  (PREREG.md = c96313d2fd8d460fc244d77e7f4fd1edf20c693e3dc19d6d7c035f9779ebfe24,
  out/table4_printed.json = 16e5e19227ce9131502b98af07c0344706b9c451cbb822b9ce5f65929ba4a9bc)
- Nothing was published anywhere. Files on disk only.

## 1. The frozen cell list

out/table4_printed.json holds the whole of Table 4, pulled out of main.tex by
scripts/parse_table4.py: 71 parameter rows across 15 models (igw 5, sigw-delta 4,
sigw-gauss 5, sigw-box 5, pt-bubble 8, pt-sound 8, stable-c/k/m/n 3 each, meta-l 4,
meta-ls 4, super 4, dw-sm 6, dw-dr 6). The two SMBHB rows of every model print "..."
in the NP columns by construction, so those are blanks, not cells.

Numeric cells tested, as pre-registered:

| column | cells |
|---|---|
| Bayes estimator, NP (mean and sd) | 41 |
| Bayes estimator, NP+SMBHB (mean and sd) | 71 |
| Maximum posterior, NP | 41 |
| Maximum posterior, NP+SMBHB | 71 |
| 68% credible interval, NP (two edges) | 41 |
| 68% credible interval, NP+SMBHB (two edges) | 71 |
| total | 336 |

Scored as individual numbers that is 112 means, 112 standard deviations, 112
maximum-posterior values and 224 interval edges: 560 comparisons, which is what
out/comparison.csv holds.

Declared not checkable in advance, and still not checkable: the 6 numeric K-bound
cells (igw n_t = 5.72; stable-c -9.67; stable-k -9.87; stable-m -10.10; stable-n
-9.71; super -9.97). K is a likelihood ratio against a reference point, and the paper
itself says it is "not defined in terms of a posterior probability distribution". The
deposited chains do carry a log_likelihood column, but not the reference theta_0 nor
the marginalisation the K ratio needs, so a posterior chain cannot yield these.
Could not be checked.

## 2. What the paper says the numbers are, and what I did

Appendix A of the paper is explicit, and I followed it.

- Bayes estimator and its standard deviation: "we compute the Bayes estimator and its
  standard deviation in terms of the corresponding sample mean and sample variance" ->
  numpy.mean and numpy.std(ddof=0). ddof=1 is recorded too and never differs at the
  printed precision (the chains hold 1.7 to 5.2 million samples).
- Maximum posterior: the argmax of the 1D marginalized posterior over the prior range.
  The paper does not say how the density is estimated, so this check is soft by
  construction. Primary: a 4000-bin histogram over the prior range convolved with a
  Gaussian of Scott bandwidth sigma * n**(-1/5); a ladder of four further bandwidths
  (0.005, 0.01, 0.02 and 0.05 of the prior range) is reported for sensitivity. scipy is
  not installed on this machine, so the KDE is binning plus convolution in numpy.
- 68% credible interval: the paper defines a highest-posterior-density interval -
  integrate over "the regions of highest posterior density" with P > P_68. Primary, as
  pre-registered: the shortest contiguous interval containing 68% of the samples.
  Secondary: the min and max of the above-threshold level set of the smoothed density.
  Both are reported for every edge; the primary decides the verdict, as frozen.

Tolerance, pre-registered: reproduced if |delta| <= 0.6 * 10^-d where d is the number
of decimals printed (0.006 at two decimals), near-miss out to 3 * 10^-d, and 0.1 for
maximum posterior. Cells marked with a star count as reproduced if the argmax lands in
the outermost 2% of the prior range on the right side.

Mapping to the deposit. The paper's dw-dr is the deposit's dw_ds (the paper's own
prior table calls the same model dw-ds). Column names: log10_A_bhb -> gw_bhb_np_0,
gamma_bhb -> gw_bhb_np_1, log10_alpha_star -> log10_alpha, log10_HR -> log10_H_R,
log10_f_min/max -> log10_fmin/fmax, Delta -> width, log10_dNeff -> log10_N_eff, and
log10_f_* is log10_f_peak in sigw_delta but log10_fpeak in sigw_gauss. The rest match
by name.

File handling. Each file is a gzipped pickle holding a 2-element list - a dict mapping
parameter name to prior bounds, in column order, and a float64 (nsamples, ncols)
array. Five files hold a tuple at top level instead. The last five columns are nmodel,
log_posterior, log_likelihood, acceptance_rate, n_parall. pickle.load was never
called: scripts/safeload.py subclasses pickle.Unpickler and allows only
numpy.core.multiarray._reconstruct, numpy._core.multiarray._reconstruct,
numpy.ndarray and numpy.dtype, raising on anything else. A first pass with
pickletools.genops, which executes nothing, confirmed those are the only globals the
files refer to. The array is rebuilt as a read-only np.frombuffer view so no second
multi-GB copy is made. All 30 files loaded. CPU only, SetPriorityClass IDLE.

All samples were used as deposited, no burn-in and no thinning - and that turns out to
be right, since the Bayes estimators land on the printed values with the full array.

## 3. Headline result

| cell type | reproduced | near-miss | not reproduced | total |
|---|---|---|---|---|
| Bayes mean | 105 | 2 | 5 | 112 |
| Bayes sd | 108 | 2 | 2 | 112 |
| Maximum posterior | 96 | 12 | 4 | 112 |
| 68% CI, lower edge | 57 | 41 | 14 | 112 |
| 68% CI, upper edge | 56 | 43 | 13 | 112 |
| all | 422 | 100 | 38 | 560 |
| K bound | - | - | - | 6 not checkable |

Median absolute difference, measured minus printed:

| cell type | median | 90th pct | within 0.006 | within 0.01 | within 0.03 |
|---|---|---|---|---|---|
| Bayes mean | 0.0030 | 0.0047 | 105/112 | 106 | 107 |
| Bayes sd | 0.0025 | 0.0046 | 107/112 | 109 | 109 |
| Maximum posterior | 0.0185 | 0.1261 | 28/112 | 41 | 65 |
| CI lower edge | 0.0058 | 0.0443 | 57/112 | 76 | 98 |
| CI upper edge | 0.0058 | 0.0393 | 56/112 | 73 | 99 |

Read plainly: the Bayes-estimator column of Table 4 reproduces exactly from the
deposited chains. A median difference of 0.003 on numbers printed to two decimals is
rounding noise and nothing else. There are two concrete exceptions, both explained in
section 4 and both traceable. The maximum-posterior and credible-interval columns
reproduce in substance but not to the printed digit, because the paper does not state
how it estimated the 1D density and those two columns cannot be computed without that
choice.

Independent confirmation that the pipeline is right: the three 95% lower limits the
paper quotes in its Section 3 prose fall straight out of my own 95% HPD level sets -
log10 A > -1.5495 for sigw-delta (paper -1.55), -1.4345 for sigw-gauss (paper -1.43),
-1.8985 for sigw-box (paper -1.90).

Verdicts by model:

| model | reproduced | near-miss | not reproduced |
|---|---|---|---|
| igw | 23 | 6 | 11 |
| sigw-delta | 23 | 7 | 0 |
| sigw-gauss | 16 | 17 | 7 |
| sigw-box | 27 | 9 | 4 |
| pt-bubble | 54 | 13 | 3 |
| pt-sound | 56 | 10 | 4 |
| stable-c | 17 | 2 | 1 |
| stable-k | 14 | 5 | 1 |
| stable-m | 16 | 3 | 1 |
| stable-n | 16 | 3 | 1 |
| meta-l | 24 | 6 | 0 |
| meta-ls | 21 | 8 | 1 |
| super | 28 | 2 | 0 |
| dw-sm | 47 | 3 | 0 |
| dw-dr | 40 | 6 | 4 |

## 4. The two findings that are not about smoothing

### 4.1 A dropped minus sign on three log10 alpha_* Bayes estimators

| model | analysis | printed mean | measured mean | printed sd | measured sd |
|---|---|---|---|---|---|
| pt-bubble | NP | -0.26 | +0.26339 | 0.47 | 0.46584 ok |
| pt-bubble | NP+SMBHB | -0.23 | +0.22556 | 0.52 | 0.51832 ok |
| pt-sound | NP | -0.22 | +0.21866 | 0.44 | 0.43727 ok |
| pt-sound | NP+SMBHB | +0.14 | +0.13544 ok | 0.56 | 0.55916 ok |

The magnitude reproduces to 0.005 in all three, and the standard deviation printed in
the same cell reproduces exactly. Only the sign is wrong. The fourth cell of the same
row, pt-sound NP+SMBHB, prints a positive 0.14 and reproduces, so this is not a sign
convention; dw-sm's own log10 alpha_* is genuinely negative (-0.88) and reproduces.

The paper's own neighbouring cells settle it. For pt-bubble the printed maximum
posterior is 1* (NP) and 0.74 (NP+SMBHB), and the printed 68% intervals are [0.03, 1*]
and [0.01, 1*] - both entirely positive. A Bayes estimator of -0.26 cannot sit outside
its own 68% credible interval. So: a sign error in three cells of Table 4, not a
disagreement about the data.

### 4.2 sigw_gauss_bhb.pkl.gz has a corrupt tail block

This is the one defect in the deposit. The file holds 2,835,225 samples. The last
46,378 of them (1.64%), one contiguous block at the end, are garbage:

- log_posterior runs up to 1.308e12, where every other file in the deposit sits at
  7.97e6;
- gamma_bhb reaches 13.53, although its prior is normal(4.7, 0.346) - 25 sigma out;
- log10_A_bhb reaches -18.25, far outside anything the prior supports.

With the block included, four cells fail outright (gamma_bhb 4.799 +- 1.176 against a
printed 4.65 +- 0.34) and five more are near-misses. Dropping the block - a post-hoc
step, not part of the pre-registered method - puts every sigw-gauss NP+SMBHB cell on
the printed value, intervals included:

| param | printed | all samples | corrupt block dropped | printed 68% CI | my level-set 68% |
|---|---|---|---|---|---|
| log10_A_bhb | -15.72 +- 0.46 | -15.6814 +- 0.5683 | -15.7244 +- 0.4641 | [-16.14, -15.22] | [-16.138, -15.221] |
| gamma_bhb | 4.65 +- 0.34 | 4.7993 +- 1.1759 | 4.6542 +- 0.3441 | [4.32, 5.00] | [4.315, 4.999] |
| log10_A | -0.36 +- 0.61 | -0.3610 +- 0.6047 | -0.3592 +- 0.6096 | [-1.04, 0.24] | [-1.050, 0.236] |
| log10_f_* | -6.30 +- 0.73 | -6.2904 +- 0.7236 | -6.3006 +- 0.7252 | [-7.17, -5.57] | [-7.158, -5.551] |
| Delta | 1.30 +- 0.70 | 1.3236 +- 0.7064 | 1.3051 +- 0.6973 | [0.37, 1.92] | [0.361, 1.918] |

So the paper's numbers are right and the published file is not: the authors clearly
summarised a chain without that tail. The defect is confined to sigw_gauss_bhb.pkl.gz;
no other file shows a log_posterior outside 7.97e6 +- 10. This is the one thing worth
telling the authors - anyone who reads that file as deposited and takes a mean gets a
different answer from the paper, and nothing in the deposit flags it.

## 5. Why the maximum-posterior and credible-interval columns do not land on the digit

Neither column can be computed from a chain without choosing a density estimator, and
the paper states no choice: no bandwidth, no binning, no tool. That is the whole of the
explanation for the near-misses, and it is measurable rather than hand-waved.

Credible intervals. Of 224 edges, the pre-registered primary (shortest contiguous 68%
interval) lands within 0.006 on 113, and the pre-registered secondary (level set of the
smoothed density) on 106; 61 edges are hit by both, and 158 of 224 (71%) by at least
one. That last figure is post-hoc, since picking the better of two estimators per cell
is not a rule I froze. Which one wins is not random: it tracks whether the
above-threshold region is contiguous. Where my density makes it contiguous the two
agree; where my density splits it, the level set's min and max span a hole and widen
the interval. igw n_t is matched by the level set to within 0.002-0.006 and missed by
the shortest interval by 0.04-0.62; pt-bubble b is the reverse; stable-k/m/n
log10_A_bhb are matched by the level set (-15.694 against a printed -15.68, -15.698
against -15.67, -15.603 against -15.61) and missed by the shortest interval by 0.3-0.4.
That the paper's definition names "regions", plural, with a threshold P_68, says the
level set is the faithful reading - but reproducing its edges to two decimals needs
their bandwidth, which is not published.

An independent check that the printed intervals really are 68% HPD intervals of these
chains: the fraction of deposited samples inside each printed interval has median
0.6806 over all 112 intervals, and 92 of them are within 0.01 of 0.68. The 18 that are
not are all parameters whose HPD region is disjoint or runs into a prior edge - igw
log10_T_rh 0.741/0.723, igw log10_r 0.816/0.750, igw n_t 0.854/0.811, pt-sound
log10_alpha_* 0.906, sigw-box log10_f_min 0.749/0.744, dw-dr b 0.948, the four stable-*
log10_A_bhb 0.790-0.812. Those are exactly the cells my two estimators disagree on, and
they are the cells where the printed [theta_68_min, theta_68_max] is the span of a
region holding more than 68% of the mass - which is what the paper's own definition
produces, not an error.

Maximum posterior. 96 of 112 within the pre-registered 0.1, median difference 0.019.
The four outright failures are all broad or multimodal densities where the argmax
wanders with the bandwidth: sigw-gauss log10_f_* NP+SMBHB (printed -6.85, mine -5.67 at
Scott and -5.97 at the coarsest bandwidth - this is also the contaminated file),
pt-bubble c NP+SMBHB (2.93 against 2.60), meta-ls log10 G mu NP (-4.46 against -5.55, a
posterior with a long flat ridge), dw-dr log10_A_bhb NP+SMBHB (-15.59 against -14.56,
bimodal). I could not establish which density estimator the authors used, so I cannot
close those four. All I can say is that the discrepancy is of the size a bandwidth
change produces, and that the Bayes estimator and the interval for the same parameters
largely reproduce.

igw log10_T_rh and log10_r deserve a separate word, because together with n_t they hold
11 of the 38 failures. Both posteriors are nearly the prior: log10_T_rh has sd 1.60 on
a uniform prior over [-3, 3] whose own sd is 1.73, and log10_r has sd 5.82 on [-40, 0].
The Bayes estimators for both reproduce to 0.005. The HPD edges of an almost flat
density are set by fluctuations of order the smoothing, so no estimator choice
reproduces them - my two differ from each other by 3.1 on log10_r's lower edge in the
NP analysis. These cells are not reproducible from a chain in principle, not just in
this attempt. The same holds for b in both domain-wall models, whose Bayes estimator
0.74 +- 0.14 is the mean and sd of its own uniform prior on [0.5, 1] to three decimals:
the parameter is unconstrained, and its printed interval edge (0.97 under NP against
0.83 under NP+SMBHB, from statistically identical posteriors) is smoothing noise.

## 6. The deposit's compare/ subdirectory is a different chain set

chains/stochastic/compare/ holds a second, near-duplicate set of 26 files with no dw
models. As pre-registered I cross-checked two models against it, and it is not the
source of Table 4:

| model | analysis | param | printed | top-level | compare/ |
|---|---|---|---|---|---|
| super | NP | log10 G mu | -11.67 +- 0.32 | -11.6722 +- 0.3198 | -11.6386 +- 0.5081 |
| super | NP+SMBHB | log10 G mu | -11.68 +- 0.35 | -11.6837 +- 0.3479 | -11.6506 +- 0.5503 |
| igw | NP | log10 r | -14.06 +- 5.82 | -14.0607 +- 5.8187 | -14.7254 +- 6.8971 |
| igw | NP | n_t | 2.61 +- 0.85 | 2.6145 +- 0.8486 | 2.6646 +- 0.9896 |

The sample counts differ too (super NP: 3,677,925 at top level against 3,334,350 in
compare/). The top-level files are the ones Table 4 was made from, and the choice
frozen in the pre-registration was the right one.

## 7. Other notes a reader would want

- dw-dr, 68% CI for log10 Delta N_eff under NP+SMBHB, prints [-0.63, 0.41*]. The prior
  is log-uniform [-3, -0.41], so a positive 0.41 is outside the prior range: another
  dropped minus sign. Against -0.41 the edge reproduces (my shortest interval gives
  -0.4089, my level set -0.4103); against the printed +0.41 it fails by 0.82. This was
  flagged in the pre-registration before anything was computed.
- The paper names the same model two ways: dw-dr in Table 4, dw-ds in Table 3 and in
  the deposit. Not an error, but it costs a reader a minute.
- Chain sizes run from 1,746,900 samples (sigw-box NP+SMBHB) to 5,209,425 (dw-dr NP),
  142 to 149 columns each, 22 GB gzipped for the whole deposit.
- Five files store a top-level tuple where the other 25 store a list: stable_c,
  stable_c_bhb, stable_k, stable_k_bhb, stable_m. Harmless, but a reader writing a
  loader should expect both.
- nmodel is present in every file with values in [-0.5, 0.5]. No filtering on it is
  needed: the Bayes estimators reproduce with every sample included.
- The chain files are gzipped pickles from a download. They should not be opened with
  pickle.load. Everything here went through a find_class allowlist of four numpy names.

## 8. Files

- PREREG.md, FREEZE.txt - the pre-registration and its hashes
- out/table4_printed.json - the frozen printed values, 71 rows
- out/priors.json - prior ranges from Tables 2 and 3
- out/cells/*.json - measured estimators, one file per model and analysis
- out/cells_compare/*.json - the compare/ cross-check
- out/comparison.csv - the 560 comparisons, cell by cell, with both interval estimators
  and the bandwidth ladder in the note column
- out/report_tables.md - the full cell-by-cell verdict table
- out/mass/*.json - fraction of samples inside each printed interval
- out/diag_sigw_gauss_bhb.json - the corrupt-block diagnostic
- scripts/ - safeload.py (restricted unpickler), probe_ops.py and probe_tail.py (opcode
  walk), keydump.py, parse_table4.py, compute_one.py, compare.py, mass_in_printed.py,
  diag_sigw_gauss_bhb.py, make_report_tables.py
### Verdict counts by cell type

| cell type | reproduced | near-miss | not reproduced | total |
|---|---|---|---|---|
| bayes_mean | 105 | 2 | 5 | 112 |
| bayes_sd | 108 | 2 | 2 | 112 |
| maxpost | 96 | 12 | 4 | 112 |
| ci68_lo | 57 | 41 | 14 | 112 |
| ci68_hi | 56 | 43 | 13 | 112 |
| **all** | 422 | 100 | 38 | 560 |

### Verdict counts by model

| model | reproduced | near-miss | not reproduced |
|---|---|---|---|
| igw | 23 | 6 | 11 |
| sigw-delta | 23 | 7 | 0 |
| sigw-gauss | 16 | 17 | 7 |
| sigw-box | 27 | 9 | 4 |
| pt-bubble | 54 | 13 | 3 |
| pt-sound | 56 | 10 | 4 |
| stable-c | 17 | 2 | 1 |
| stable-k | 14 | 5 | 1 |
| stable-m | 16 | 3 | 1 |
| stable-n | 16 | 3 | 1 |
| meta-l | 24 | 6 | 0 |
| meta-ls | 21 | 8 | 1 |
| super | 28 | 2 | 0 |
| dw-sm | 47 | 3 | 0 |
| dw-dr | 40 | 6 | 4 |

### Every cell that is not "reproduced"

| model | param | analysis | cell | printed | measured | delta | verdict | detail |
|---|---|---|---|---|---|---|---|---|
| igw | log10_T_rh | NP | ci68_lo | -1.51 | -1.46536 | 0.04464 | not-reproduced | levelset_scott=-1.4512 (d=+0.0588, not-reproduced); best_ls=r0.02(-1.4632); pct16/84=-1.7141 |
| igw | log10_T_rh | NP | ci68_hi | 2.53 | 2.16753 | -0.36247 | not-reproduced | levelset_scott=2.8057 (d=+0.2757, not-reproduced); best_ls=r0.02(2.7172); pct16/84=1.9436 |
| igw | log10_T_rh | NPSMBHB | ci68_lo | -1.89 | -1.91195 | -0.02195 | near-miss | levelset_scott=-1.8442 (d=+0.0457, not-reproduced); best_ls=r0.02(-1.8547); pct16/84=-1.8246 |
| igw | log10_T_rh | NPSMBHB | ci68_hi | 2.11 | 1.78479 | -0.32521 | not-reproduced | levelset_scott=2.3543 (d=+0.2443, not-reproduced); best_ls=r0.02(2.3438); pct16/84=1.8748 |
| igw | log10_r | NP | maxpost | -10.14 | -9.915 | 0.225 | near-miss | best=r0.02(-10.1450) |
| igw | log10_r | NP | ci68_lo | -22.16 | -19.21714 | 2.94286 | not-reproduced | levelset_scott=-22.2750 (d=-0.1150, not-reproduced); best_ls=r0.02(-22.1050); pct16/84=-21.0193 |
| igw | log10_r | NP | ci68_hi | -6.58 | -6.72144 | -0.14144 | not-reproduced | levelset_scott=-6.5350 (d=+0.0450, not-reproduced); best_ls=scott(-6.5350); pct16/84=-8.1926 |
| igw | log10_r | NPSMBHB | maxpost | -10.59 | -10.765 | -0.175 | near-miss | best=r0.02(-10.6350) |
| igw | log10_r | NPSMBHB | ci68_lo | -23.03 | -21.9311 | 1.0989 | not-reproduced | levelset_scott=-23.1850 (d=-0.1550, not-reproduced); best_ls=r0.02(-23.1150); pct16/84=-23.1530 |
| igw | log10_r | NPSMBHB | ci68_hi | -7.21 | -7.73006 | -0.52006 | not-reproduced | levelset_scott=-7.1850 (d=+0.0250, near-miss); best_ls=scott(-7.1850); pct16/84=-8.7620 |
| igw | n_t | NP | ci68_lo | 1.53 | 1.48915 | -0.04085 | not-reproduced | levelset_scott=1.5248 (d=-0.0052, reproduced); best_ls=scott(1.5248); pct16/84=1.7783 |
| igw | n_t | NP | ci68_hi | 3.92 | 3.30286 | -0.61714 | not-reproduced | levelset_scott=3.9218 (d=+0.0018, reproduced); best_ls=scott(3.9218); pct16/84=3.6825 |
| igw | n_t | NPSMBHB | ci68_lo | 1.56 | 1.63121 | 0.07121 | not-reproduced | levelset_scott=1.5637 (d=+0.0037, reproduced); best_ls=r0.01(1.5623); pct16/84=1.7603 |
| igw | n_t | NPSMBHB | ci68_hi | 4.03 | 3.657 | -0.373 | not-reproduced | levelset_scott=4.0358 (d=+0.0057, reproduced); best_ls=r0.02(4.0267); pct16/84=3.8078 |
| igw | log10_A_bhb | NPSMBHB | ci68_lo | -16.2 | -16.22236 | -0.02236 | near-miss | levelset_scott=-16.2103 (d=-0.0103, near-miss); best_ls=r0.01(-16.2093); pct16/84=-16.1433 |
| igw | log10_A_bhb | NPSMBHB | ci68_hi | -15.14 | -15.15286 | -0.01286 | near-miss | levelset_scott=-15.1397 (d=+0.0003, reproduced); best_ls=scott(-15.1397); pct16/84=-15.0614 |
| igw | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 4.99174 | -0.00826 | near-miss | levelset_scott=4.9970 (d=-0.0030, reproduced); best_ls=r0.01(4.9987); pct16/84=4.9783 |
| sigw-delta | log10_A | NP | ci68_hi | -0.01 | -0.00068 | 0.00932 | near-miss | levelset_scott=-0.0015 (d=+0.0085, near-miss); best_ls=r0.01(-0.0055); pct16/84=-0.1682 |
| sigw-delta | log10_A | NPSMBHB | ci68_lo | -1.03 | -1.01947 | 0.01053 | near-miss | levelset_scott=-1.0215 (d=+0.0085, near-miss); best_ls=r0.01(-1.0275); pct16/84=-1.2490 |
| sigw-delta | log10_A | NPSMBHB | ci68_hi | -0.02 | -0.01324 | 0.00676 | near-miss | levelset_scott=-0.0135 (d=+0.0065, near-miss); best_ls=r0.01(-0.0165); pct16/84=-0.1791 |
| sigw-delta | log10_f_star | NP | ci68_lo | -6.17 | -6.17977 | -0.00977 | near-miss | levelset_scott=-6.1978 (d=-0.0278, near-miss); best_ls=scott(-6.1978); pct16/84=-6.5752 |
| sigw-delta | log10_f_star | NPSMBHB | maxpost | -5.0 | -5.20775 | -0.20775 | near-miss | best=r0.01(-5.1987) |
| sigw-delta | gamma_bhb | NPSMBHB | ci68_lo | 4.31 | 4.31711 | 0.00711 | near-miss | levelset_scott=4.3097 (d=-0.0003, reproduced); best_ls=scott(4.3097); pct16/84=4.3031 |
| sigw-delta | gamma_bhb | NPSMBHB | ci68_hi | 4.99 | 5.00302 | 0.01302 | near-miss | levelset_scott=4.9964 (d=+0.0064, near-miss); best_ls=scott(4.9964); pct16/84=4.9893 |
| sigw-gauss | log10_A | NP | maxpost | -0.34 | -0.4855 | -0.1455 | near-miss | best=r0.05(-0.3625) |
| sigw-gauss | log10_A | NP | ci68_hi | 0.2 | 0.21884 | 0.01884 | near-miss | levelset_scott=0.2115 (d=+0.0115, near-miss); best_ls=r0.01(0.2105); pct16/84=0.2390 |
| sigw-gauss | log10_A | NPSMBHB | maxpost | -0.29 | -0.4695 | -0.1795 | near-miss | best=r0.05(-0.4075) |
| sigw-gauss | log10_A | NPSMBHB | ci68_lo | -1.04 | -1.05207 | -0.01207 | near-miss | levelset_scott=-1.0445 (d=-0.0045, reproduced); best_ls=r0.02(-1.0405); pct16/84=-0.9994 |
| sigw-gauss | log10_A | NPSMBHB | ci68_hi | 0.24 | 0.22236 | -0.01764 | near-miss | levelset_scott=0.2295 (d=-0.0105, near-miss); best_ls=r0.02(0.2365); pct16/84=0.2790 |
| sigw-gauss | log10_f_star | NP | ci68_lo | -7.25 | -7.29681 | -0.04681 | not-reproduced | levelset_scott=-7.2837 (d=-0.0337, not-reproduced); best_ls=r0.02(-7.2342); pct16/84=-7.1136 |
| sigw-gauss | log10_f_star | NP | ci68_hi | -5.65 | -5.68981 | -0.03981 | not-reproduced | levelset_scott=-5.6833 (d=-0.0332, not-reproduced); best_ls=r0.02(-5.6412); pct16/84=-5.4914 |
| sigw-gauss | log10_f_star | NPSMBHB | bayes_mean | -6.3 | -6.29035 | 0.00965 | near-miss |  |
| sigw-gauss | log10_f_star | NPSMBHB | bayes_sd | 0.73 | 0.7236 | -0.0064 | near-miss | ddof1=0.72360 |
| sigw-gauss | log10_f_star | NPSMBHB | maxpost | -6.85 | -5.67425 | 1.17575 | not-reproduced | best=r0.05(-5.9668) |
| sigw-gauss | log10_f_star | NPSMBHB | ci68_lo | -7.17 | -7.14672 | 0.02328 | near-miss | levelset_scott=-7.1457 (d=+0.0243, near-miss); best_ls=scott(-7.1457); pct16/84=-7.0835 |
| sigw-gauss | log10_f_star | NPSMBHB | ci68_hi | -5.57 | -5.5584 | 0.0116 | near-miss | levelset_scott=-5.5633 (d=+0.0068, near-miss); best_ls=scott(-5.5633); pct16/84=-5.4906 |
| sigw-gauss | Delta | NP | maxpost | 1.6 | 1.71711 | 0.11711 | near-miss | best=r0.05(1.5895) |
| sigw-gauss | Delta | NP | ci68_hi | 2.07 | 2.06194 | -0.00806 | near-miss | levelset_scott=2.0687 (d=-0.0013, reproduced); best_ls=r0.02(2.0695); pct16/84=2.1080 |
| sigw-gauss | Delta | NPSMBHB | bayes_mean | 1.3 | 1.32358 | 0.02358 | near-miss |  |
| sigw-gauss | Delta | NPSMBHB | bayes_sd | 0.7 | 0.70638 | 0.00638 | near-miss | ddof1=0.70638 |
| sigw-gauss | Delta | NPSMBHB | ci68_lo | 0.37 | 0.34515 | -0.02485 | near-miss | levelset_scott=0.3556 (d=-0.0144, near-miss); best_ls=r0.005(0.3585); pct16/84=0.5130 |
| sigw-gauss | log10_A_bhb | NPSMBHB | bayes_mean | -15.72 | -15.68137 | 0.03863 | not-reproduced |  |
| sigw-gauss | log10_A_bhb | NPSMBHB | bayes_sd | 0.46 | 0.56831 | 0.10831 | not-reproduced | ddof1=0.56831 |
| sigw-gauss | log10_A_bhb | NPSMBHB | ci68_hi | -15.22 | -15.20459 | 0.01541 | near-miss | levelset_scott=-15.2167 (d=+0.0033, reproduced); best_ls=scott(-15.2167); pct16/84=-15.2418 |
| sigw-gauss | gamma_bhb | NPSMBHB | bayes_mean | 4.65 | 4.79927 | 0.14927 | not-reproduced |  |
| sigw-gauss | gamma_bhb | NPSMBHB | bayes_sd | 0.34 | 1.17588 | 0.83588 | not-reproduced | ddof1=1.17588 |
| sigw-gauss | gamma_bhb | NPSMBHB | ci68_lo | 4.32 | 4.30847 | -0.01153 | near-miss | levelset_scott=4.3072 (d=-0.0128, near-miss); best_ls=r0.005(4.3099); pct16/84=4.3158 |
| sigw-gauss | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 5.00756 | 0.00756 | near-miss | levelset_scott=5.0073 (d=+0.0073, near-miss); best_ls=scott(5.0073); pct16/84=5.0155 |
| sigw-box | log10_A | NP | ci68_lo | -1.72 | -1.71012 | 0.00988 | near-miss | levelset_scott=-1.7245 (d=-0.0045, reproduced); best_ls=scott(-1.7245); pct16/84=-1.5106 |
| sigw-box | log10_A | NP | ci68_hi | -0.82 | -0.85463 | -0.03463 | not-reproduced | levelset_scott=-0.8245 (d=-0.0045, reproduced); best_ls=scott(-0.8245); pct16/84=-0.6048 |
| sigw-box | log10_A | NPSMBHB | ci68_lo | -1.68 | -1.6993 | -0.0193 | near-miss | levelset_scott=-1.6945 (d=-0.0145, near-miss); best_ls=r0.05(-1.6835); pct16/84=-1.4983 |
| sigw-box | log10_A | NPSMBHB | ci68_hi | -0.74 | -0.7597 | -0.0197 | near-miss | levelset_scott=-0.7395 (d=+0.0005, reproduced); best_ls=scott(-0.7395); pct16/84=-0.5011 |
| sigw-box | log10_f_min | NP | ci68_lo | -8.01 | -7.76194 | 0.24806 | not-reproduced | levelset_scott=-8.0038 (d=+0.0062, near-miss); best_ls=scott(-8.0038); pct16/84=-7.7541 |
| sigw-box | log10_f_min | NP | ci68_hi | -6.97 | -6.91267 | 0.05733 | not-reproduced | levelset_scott=-6.9703 (d=-0.0003, reproduced); best_ls=scott(-6.9703); pct16/84=-6.9040 |
| sigw-box | log10_f_min | NPSMBHB | ci68_lo | -7.97 | -7.74389 | 0.22611 | not-reproduced | levelset_scott=-7.9722 (d=-0.0023, reproduced); best_ls=scott(-7.9722); pct16/84=-7.7205 |
| sigw-box | log10_f_min | NPSMBHB | ci68_hi | -6.84 | -6.82314 | 0.01686 | near-miss | levelset_scott=-6.8548 (d=-0.0148, near-miss); best_ls=r0.01(-6.8472); pct16/84=-6.7935 |
| sigw-box | log10_f_max | NP | ci68_lo | -6.42 | -6.42691 | -0.00691 | near-miss | levelset_scott=-6.4813 (d=-0.0613, not-reproduced); best_ls=scott(-6.4813); pct16/84=-6.8201 |
| sigw-box | log10_A_bhb | NPSMBHB | ci68_lo | -16.15 | -16.15882 | -0.00882 | near-miss | levelset_scott=-16.1479 (d=+0.0021, reproduced); best_ls=r0.01(-16.1488); pct16/84=-16.1822 |
| sigw-box | log10_A_bhb | NPSMBHB | ci68_hi | -15.21 | -15.22043 | -0.01043 | near-miss | levelset_scott=-15.2081 (d=+0.0019, reproduced); best_ls=scott(-15.2081); pct16/84=-15.2412 |
| sigw-box | gamma_bhb | NPSMBHB | ci68_lo | 4.31 | 4.31769 | 0.00769 | near-miss | levelset_scott=4.3083 (d=-0.0017, reproduced); best_ls=scott(4.3083); pct16/84=4.3017 |
| sigw-box | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 5.01234 | 0.01234 | near-miss | levelset_scott=5.0033 (d=+0.0033, reproduced); best_ls=scott(5.0033); pct16/84=4.9966 |
| pt-bubble | log10_T_star | NP | ci68_lo | -1.33 | -1.33971 | -0.00971 | near-miss | levelset_scott=-1.3310 (d=-0.0010, reproduced); best_ls=scott(-1.3310); pct16/84=-1.2335 |
| pt-bubble | log10_T_star | NP | ci68_hi | -0.39 | -0.39857 | -0.00857 | near-miss | levelset_scott=-0.3890 (d=+0.0010, reproduced); best_ls=scott(-0.3890); pct16/84=-0.2641 |
| pt-bubble | log10_T_star | NPSMBHB | ci68_lo | -1.34 | -1.35084 | -0.01084 | near-miss | levelset_scott=-1.3490 (d=-0.0090, near-miss); best_ls=scott(-1.3490); pct16/84=-1.2416 |
| pt-bubble | log10_T_star | NPSMBHB | ci68_hi | -0.34 | -0.35505 | -0.01505 | near-miss | levelset_scott=-0.3510 (d=-0.0110, near-miss); best_ls=r0.01(-0.3390); pct16/84=-0.2142 |
| pt-bubble | log10_alpha_star | NP | bayes_mean | -0.26 | 0.26339 | 0.52339 | not-reproduced |  |
| pt-bubble | log10_alpha_star | NP | maxpost | 1.0 | 0.80463 | -0.19537 | near-miss | best=r0.005(0.8054) |
| pt-bubble | log10_alpha_star | NPSMBHB | bayes_mean | -0.23 | 0.22556 | 0.45556 | not-reproduced |  |
| pt-bubble | log10_alpha_star | NPSMBHB | ci68_lo | 0.01 | -0.00242 | -0.01242 | near-miss | levelset_scott=-0.0249 (d=-0.0349, not-reproduced); best_ls=scott(-0.0249); pct16/84=-0.3039 |
| pt-bubble | a | NP | ci68_lo | 1.49 | 1.46737 | -0.02263 | near-miss | levelset_scott=1.4892 (d=-0.0008, reproduced); best_ls=scott(1.4892); pct16/84=1.5251 |
| pt-bubble | a | NP | ci68_hi | 2.54 | 2.5115 | -0.0285 | near-miss | levelset_scott=2.5293 (d=-0.0107, near-miss); best_ls=r0.005(2.5322); pct16/84=2.5711 |
| pt-bubble | a | NPSMBHB | ci68_lo | 1.54 | 1.5237 | -0.0163 | near-miss | levelset_scott=1.5268 (d=-0.0132, near-miss); best_ls=r0.05(1.5468); pct16/84=1.5335 |
| pt-bubble | a | NPSMBHB | ci68_hi | 2.63 | 2.61087 | -0.01913 | near-miss | levelset_scott=2.6088 (d=-0.0212, near-miss); best_ls=r0.05(2.6183); pct16/84=2.6211 |
| pt-bubble | b | NPSMBHB | maxpost | 1.0 | 1.10425 | 0.10425 | near-miss | best=scott(1.1042) |
| pt-bubble | c | NP | maxpost | 3.0 | 2.87325 | -0.12675 | near-miss | best=r0.005(2.8788) |
| pt-bubble | c | NPSMBHB | maxpost | 2.93 | 2.59575 | -0.33425 | not-reproduced | best=r0.05(2.6532) |
| pt-bubble | log10_A_bhb | NPSMBHB | ci68_lo | -16.17 | -16.17843 | -0.00843 | near-miss | levelset_scott=-16.1719 (d=-0.0019, reproduced); best_ls=scott(-16.1719); pct16/84=-16.1761 |
| pt-sound | log10_T_star | NP | ci68_lo | -2.33 | -2.34496 | -0.01496 | near-miss | levelset_scott=-2.3350 (d=-0.0050, reproduced); best_ls=r0.01(-2.3310); pct16/84=-2.2545 |
| pt-sound | log10_T_star | NP | ci68_hi | -1.48 | -1.49244 | -0.01244 | near-miss | levelset_scott=-1.4830 (d=-0.0030, reproduced); best_ls=scott(-1.4830); pct16/84=-1.3862 |
| pt-sound | log10_T_star | NPSMBHB | ci68_lo | -2.31 | -2.30398 | 0.00602 | near-miss | levelset_scott=-2.3190 (d=-0.0090, near-miss); best_ls=scott(-2.3190); pct16/84=-2.2155 |
| pt-sound | log10_alpha_star | NP | bayes_mean | -0.22 | 0.21866 | 0.43866 | not-reproduced |  |
| pt-sound | log10_alpha_star | NP | ci68_lo | -0.37 | -0.37757 | -0.00757 | near-miss | levelset_scott=-0.3901 (d=-0.0201, near-miss); best_ls=r0.02(-0.3774); pct16/84=-0.2772 |
| pt-sound | log10_alpha_star | NP | ci68_hi | 1.0 | 0.62297 | -0.37703 | not-reproduced | levelset_scott=0.9464 (d=-0.0536, not-reproduced); best_ls=r0.005(0.9606); pct16/84=0.7376 |
| pt-sound | log10_alpha_star | NPSMBHB | ci68_lo | -0.34 | -0.37144 | -0.03144 | not-reproduced | levelset_scott=-0.3654 (d=-0.0254, near-miss); best_ls=r0.02(-0.3534); pct16/84=-0.3369 |
| pt-sound | log10_alpha_star | NPSMBHB | ci68_hi | 0.73 | 0.68577 | -0.04423 | not-reproduced | levelset_scott=0.7754 (d=+0.0454, not-reproduced); best_ls=r0.05(0.7259); pct16/84=0.7218 |
| pt-sound | log10_HR | NP | ci68_hi | -0.57 | -0.58204 | -0.01204 | near-miss | levelset_scott=-0.5816 (d=-0.0116, near-miss); best_ls=r0.02(-0.5756); pct16/84=-0.3869 |
| pt-sound | log10_HR | NPSMBHB | ci68_lo | -1.26 | -1.26717 | -0.00717 | near-miss | levelset_scott=-1.2671 (d=-0.0071, near-miss); best_ls=r0.01(-1.2664); pct16/84=-1.2047 |
| pt-sound | log10_HR | NPSMBHB | ci68_hi | -0.45 | -0.46012 | -0.01012 | near-miss | levelset_scott=-0.4624 (d=-0.0124, near-miss); best_ls=r0.02(-0.4594); pct16/84=-0.3782 |
| pt-sound | c | NP | maxpost | 5.0 | 4.87975 | -0.12025 | near-miss | best=r0.005(4.9737) |
| pt-sound | log10_A_bhb | NPSMBHB | ci68_lo | -16.04 | -16.05472 | -0.01472 | near-miss | levelset_scott=-16.0514 (d=-0.0114, near-miss); best_ls=r0.05(-16.0464); pct16/84=-16.0004 |
| pt-sound | log10_A_bhb | NPSMBHB | ci68_hi | -14.94 | -14.95246 | -0.01246 | near-miss | levelset_scott=-14.9475 (d=-0.0075, near-miss); best_ls=r0.02(-14.9357); pct16/84=-14.8893 |
| stable-c | log10_Gmu | NPSMBHB | ci68_hi | -9.88 | -9.88796 | -0.00796 | near-miss | levelset_scott=-9.8690 (d=+0.0110, near-miss); best_ls=r0.005(-9.8750); pct16/84=-10.1756 |
| stable-c | log10_A_bhb | NPSMBHB | ci68_lo | -15.58 | -15.04201 | 0.53799 | not-reproduced | levelset_scott=-15.0433 (d=+0.5367, not-reproduced); best_ls=r0.05(-15.1379); pct16/84=-15.6357 |
| stable-c | gamma_bhb | NPSMBHB | ci68_hi | 4.66 | 4.66835 | 0.00835 | near-miss | levelset_scott=4.6627 (d=+0.0027, reproduced); best_ls=r0.005(4.6619); pct16/84=4.7281 |
| stable-k | log10_Gmu | NP | ci68_lo | -10.5 | -10.49058 | 0.00942 | near-miss | levelset_scott=-10.4950 (d=+0.0050, reproduced); best_ls=r0.005(-10.4970); pct16/84=-10.4766 |
| stable-k | log10_Gmu | NP | ci68_hi | -10.21 | -10.20271 | 0.00729 | near-miss | levelset_scott=-10.2070 (d=+0.0030, reproduced); best_ls=scott(-10.2070); pct16/84=-10.1861 |
| stable-k | log10_Gmu | NPSMBHB | ci68_hi | -10.04 | -10.05266 | -0.01266 | near-miss | levelset_scott=-10.0330 (d=+0.0070, near-miss); best_ls=r0.005(-10.0410); pct16/84=-10.3191 |
| stable-k | log10_A_bhb | NPSMBHB | ci68_lo | -15.68 | -15.31352 | 0.36648 | not-reproduced | levelset_scott=-15.6939 (d=-0.0139, near-miss); best_ls=r0.01(-15.6809); pct16/84=-15.7685 |
| stable-k | gamma_bhb | NPSMBHB | ci68_lo | 3.95 | 3.97134 | 0.02134 | near-miss | levelset_scott=3.9553 (d=+0.0053, reproduced); best_ls=r0.01(3.9512); pct16/84=4.0027 |
| stable-k | gamma_bhb | NPSMBHB | ci68_hi | 4.72 | 4.74006 | 0.02006 | near-miss | levelset_scott=4.7259 (d=+0.0059, reproduced); best_ls=r0.01(4.7235); pct16/84=4.7807 |
| stable-m | log10_Gmu | NPSMBHB | ci68_lo | -11.91 | -11.89013 | 0.01987 | near-miss | levelset_scott=-11.8830 (d=+0.0270, near-miss); best_ls=r0.02(-11.8870); pct16/84=-12.9045 |
| stable-m | log10_Gmu | NPSMBHB | ci68_hi | -10.27 | -10.26188 | 0.00812 | near-miss | levelset_scott=-10.2530 (d=+0.0170, near-miss); best_ls=r0.005(-10.2590); pct16/84=-10.5209 |
| stable-m | log10_A_bhb | NPSMBHB | ci68_lo | -15.67 | -15.3141 | 0.3559 | not-reproduced | levelset_scott=-15.6981 (d=-0.0281, near-miss); best_ls=r0.01(-15.6818); pct16/84=-15.7700 |
| stable-m | log10_A_bhb | NPSMBHB | ci68_hi | -14.34 | -14.33023 | 0.00977 | near-miss | levelset_scott=-14.3293 (d=+0.0107, near-miss); best_ls=r0.005(-14.3303); pct16/84=-14.5066 |
| stable-n | log10_Gmu | NPSMBHB | ci68_lo | -11.99 | -11.97776 | 0.01224 | near-miss | levelset_scott=-12.1490 (d=-0.1590, not-reproduced); best_ls=r0.02(-11.9670); pct16/84=-12.9456 |
| stable-n | log10_A_bhb | NPSMBHB | ci68_lo | -15.61 | -15.17189 | 0.43811 | not-reproduced | levelset_scott=-15.6034 (d=+0.0066, near-miss); best_ls=scott(-15.6034); pct16/84=-15.7073 |
| stable-n | gamma_bhb | NPSMBHB | ci68_lo | 3.93 | 3.92177 | -0.00823 | near-miss | levelset_scott=3.9348 (d=+0.0048, reproduced); best_ls=r0.02(3.9293); pct16/84=3.9880 |
| stable-n | gamma_bhb | NPSMBHB | ci68_hi | 4.69 | 4.67964 | -0.01036 | near-miss | levelset_scott=4.6934 (d=+0.0034, reproduced); best_ls=r0.01(4.6926); pct16/84=4.7554 |
| meta-l | log10_Gmu | NP | ci68_hi | -4.84 | -4.83148 | 0.00852 | near-miss | levelset_scott=-4.8328 (d=+0.0072, near-miss); best_ls=scott(-4.8328); pct16/84=-5.0568 |
| meta-l | sqrt_kappa | NP | ci68_lo | 7.81 | 7.79994 | -0.01006 | near-miss | levelset_scott=7.8016 (d=-0.0084, near-miss); best_ls=r0.005(7.8022); pct16/84=7.8346 |
| meta-l | sqrt_kappa | NP | ci68_hi | 8.0 | 7.97944 | -0.02056 | near-miss | levelset_scott=7.9847 (d=-0.0153, near-miss); best_ls=r0.01(7.9991); pct16/84=8.0553 |
| meta-l | sqrt_kappa | NPSMBHB | ci68_hi | 8.0 | 7.98613 | -0.01387 | near-miss | levelset_scott=7.9922 (d=-0.0078, near-miss); best_ls=r0.01(8.0028); pct16/84=8.0576 |
| meta-l | log10_A_bhb | NPSMBHB | ci68_lo | -16.18 | -16.19818 | -0.01818 | near-miss | levelset_scott=-16.1839 (d=-0.0039, reproduced); best_ls=scott(-16.1839); pct16/84=-16.2019 |
| meta-l | log10_A_bhb | NPSMBHB | ci68_hi | -15.25 | -15.26407 | -0.01407 | near-miss | levelset_scott=-15.2491 (d=+0.0009, reproduced); best_ls=scott(-15.2491); pct16/84=-15.2676 |
| meta-ls | log10_Gmu | NP | maxpost | -4.46 | -5.55469 | -1.09469 | not-reproduced | best=r0.05(-5.3609) |
| meta-ls | log10_Gmu | NPSMBHB | ci68_lo | -6.33 | -6.30359 | 0.02641 | near-miss | levelset_scott=-6.3172 (d=+0.0128, near-miss); best_ls=r0.01(-6.3422); pct16/84=-6.7551 |
| meta-ls | log10_Gmu | NPSMBHB | ci68_hi | -4.15 | -4.12735 | 0.02265 | near-miss | levelset_scott=-4.1328 (d=+0.0172, near-miss); best_ls=r0.01(-4.1422); pct16/84=-4.4432 |
| meta-ls | sqrt_kappa | NP | ci68_lo | 7.59 | 7.583 | -0.007 | near-miss | levelset_scott=7.5828 (d=-0.0072, near-miss); best_ls=r0.01(7.5891); pct16/84=7.6419 |
| meta-ls | sqrt_kappa | NPSMBHB | ci68_hi | 7.93 | 7.92392 | -0.00608 | near-miss | levelset_scott=7.9278 (d=-0.0022, reproduced); best_ls=scott(7.9278); pct16/84=8.0043 |
| meta-ls | log10_A_bhb | NPSMBHB | ci68_lo | -16.17 | -16.16109 | 0.00891 | near-miss | levelset_scott=-16.1716 (d=-0.0016, reproduced); best_ls=r0.005(-16.1707); pct16/84=-16.1918 |
| meta-ls | log10_A_bhb | NPSMBHB | ci68_hi | -15.23 | -15.21943 | 0.01057 | near-miss | levelset_scott=-15.2288 (d=+0.0012, reproduced); best_ls=scott(-15.2288); pct16/84=-15.2484 |
| meta-ls | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.29385 | -0.00615 | near-miss | levelset_scott=4.2961 (d=-0.0039, reproduced); best_ls=scott(4.2961); pct16/84=4.2911 |
| meta-ls | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 4.99382 | -0.00618 | near-miss | levelset_scott=4.9969 (d=-0.0031, reproduced); best_ls=r0.01(4.9986); pct16/84=4.9912 |
| super | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.31016 | 0.01016 | near-miss | levelset_scott=4.3058 (d=+0.0058, reproduced); best_ls=r0.02(4.2986); pct16/84=4.3001 |
| super | gamma_bhb | NPSMBHB | ci68_hi | 4.99 | 4.99721 | 0.00721 | near-miss | levelset_scott=4.9937 (d=+0.0037, reproduced); best_ls=scott(4.9937); pct16/84=4.9872 |
| dw-sm | log10_T_star | NP | ci68_lo | -0.96 | -0.95359 | 0.00641 | near-miss | levelset_scott=-0.9590 (d=+0.0010, reproduced); best_ls=scott(-0.9590); pct16/84=-0.9319 |
| dw-sm | gamma_bhb | NPSMBHB | ci68_lo | 4.32 | 4.32887 | 0.00887 | near-miss | levelset_scott=4.3212 (d=+0.0012, reproduced); best_ls=scott(4.3212); pct16/84=4.3095 |
| dw-sm | gamma_bhb | NPSMBHB | ci68_hi | 5.02 | 5.02822 | 0.00822 | near-miss | levelset_scott=5.0211 (d=+0.0011, reproduced); best_ls=scott(5.0211); pct16/84=5.0095 |
| dw-dr | log10_T_star | NPSMBHB | ci68_lo | -1.27 | -1.25604 | 0.01396 | near-miss | levelset_scott=-1.2810 (d=-0.0110, near-miss); best_ls=r0.005(-1.2690); pct16/84=-1.1647 |
| dw-dr | log10_T_star | NPSMBHB | ci68_hi | -0.67 | -0.66265 | 0.00735 | near-miss | levelset_scott=-0.6450 (d=+0.0250, near-miss); best_ls=r0.005(-0.6630); pct16/84=0.0345 |
| dw-dr | log10_dNeff | NPSMBHB | ci68_hi | 0.41 | -0.40894 | -0.81894 | not-reproduced | levelset_scott=-0.4103 (d=-0.8203, not-reproduced); best_ls=scott(-0.4103); pct16/84=-0.4307 |
| dw-dr | b | NP | ci68_hi | 0.97 | 0.82396 | -0.14604 | not-reproduced | levelset_scott=0.8599 (d=-0.1101, not-reproduced); best_ls=r0.005(0.8659); pct16/84=0.9096 |
| dw-dr | c | NP | maxpost | 3.0 | 2.88896 | -0.11104 | near-miss | best=scott(2.8890) |
| dw-dr | c | NPSMBHB | maxpost | 3.0 | 2.82281 | -0.17719 | near-miss | best=scott(2.8228) |
| dw-dr | log10_A_bhb | NPSMBHB | maxpost | -15.59 | -14.55381 | 1.03619 | not-reproduced | best=r0.05(-14.6155) |
| dw-dr | log10_A_bhb | NPSMBHB | ci68_lo | -16.03 | -15.75702 | 0.27298 | not-reproduced | levelset_scott=-16.0256 (d=+0.0044, reproduced); best_ls=r0.005(-16.0276); pct16/84=-16.0145 |
| dw-dr | log10_A_bhb | NPSMBHB | ci68_hi | -14.4 | -14.41751 | -0.01751 | near-miss | levelset_scott=-14.3914 (d=+0.0086, near-miss); best_ls=r0.005(-14.3924); pct16/84=-14.5733 |
| dw-dr | gamma_bhb | NPSMBHB | ci68_lo | 4.1 | 4.09269 | -0.00731 | near-miss | levelset_scott=4.0930 (d=-0.0070, near-miss); best_ls=scott(4.0930); pct16/84=4.1014 |

### Full cell-by-cell table

| model | param | analysis | cell | printed | measured | delta | verdict |
|---|---|---|---|---|---|---|---|
| igw | log10_T_rh | NP | bayes_mean | 0.02 | 0.02345 | 0.00345 | reproduced |
| igw | log10_T_rh | NP | bayes_sd | 1.6 | 1.60017 | 0.00017 | reproduced |
| igw | log10_T_rh | NP | maxpost | -0.53 | -0.47625 | 0.05375 | reproduced |
| igw | log10_T_rh | NP | ci68_lo | -1.51 | -1.46536 | 0.04464 | not-reproduced |
| igw | log10_T_rh | NP | ci68_hi | 2.53 | 2.16753 | -0.36247 | not-reproduced |
| igw | log10_T_rh | NPSMBHB | bayes_mean | -0.07 | -0.07058 | -0.00058 | reproduced |
| igw | log10_T_rh | NPSMBHB | bayes_sd | 1.61 | 1.61121 | 0.00121 | reproduced |
| igw | log10_T_rh | NPSMBHB | maxpost | -0.6 | -0.54975 | 0.05025 | reproduced |
| igw | log10_T_rh | NPSMBHB | ci68_lo | -1.89 | -1.91195 | -0.02195 | near-miss |
| igw | log10_T_rh | NPSMBHB | ci68_hi | 2.11 | 1.78479 | -0.32521 | not-reproduced |
| igw | log10_r | NP | bayes_mean | -14.06 | -14.06066 | -0.00066 | reproduced |
| igw | log10_r | NP | bayes_sd | 5.82 | 5.81866 | -0.00134 | reproduced |
| igw | log10_r | NP | maxpost | -10.14 | -9.915 | 0.225 | near-miss |
| igw | log10_r | NP | ci68_lo | -22.16 | -19.21714 | 2.94286 | not-reproduced |
| igw | log10_r | NP | ci68_hi | -6.58 | -6.72144 | -0.14144 | not-reproduced |
| igw | log10_r | NPSMBHB | bayes_mean | -15.97 | -15.97415 | -0.00415 | reproduced |
| igw | log10_r | NPSMBHB | bayes_sd | 7.27 | 7.27424 | 0.00424 | reproduced |
| igw | log10_r | NPSMBHB | maxpost | -10.59 | -10.765 | -0.175 | near-miss |
| igw | log10_r | NPSMBHB | ci68_lo | -23.03 | -21.9311 | 1.0989 | not-reproduced |
| igw | log10_r | NPSMBHB | ci68_hi | -7.21 | -7.73006 | -0.52006 | not-reproduced |
| igw | n_t | NP | bayes_mean | 2.61 | 2.61449 | 0.00449 | reproduced |
| igw | n_t | NP | bayes_sd | 0.85 | 0.84865 | -0.00135 | reproduced |
| igw | n_t | NP | maxpost | 2.02 | 2.00325 | -0.01675 | reproduced |
| igw | n_t | NP | ci68_lo | 1.53 | 1.48915 | -0.04085 | not-reproduced |
| igw | n_t | NP | ci68_hi | 3.92 | 3.30286 | -0.61714 | not-reproduced |
| igw | n_t | NPSMBHB | bayes_mean | 2.68 | 2.6826 | 0.0026 | reproduced |
| igw | n_t | NPSMBHB | bayes_sd | 0.97 | 0.97225 | 0.00225 | reproduced |
| igw | n_t | NPSMBHB | maxpost | 2.08 | 2.08575 | 0.00575 | reproduced |
| igw | n_t | NPSMBHB | ci68_lo | 1.56 | 1.63121 | 0.07121 | not-reproduced |
| igw | n_t | NPSMBHB | ci68_hi | 4.03 | 3.657 | -0.373 | not-reproduced |
| igw | log10_A_bhb | NPSMBHB | bayes_mean | -15.6 | -15.60298 | -0.00298 | reproduced |
| igw | log10_A_bhb | NPSMBHB | bayes_sd | 0.56 | 0.55573 | -0.00427 | reproduced |
| igw | log10_A_bhb | NPSMBHB | maxpost | -15.64 | -15.61735 | 0.02265 | reproduced |
| igw | log10_A_bhb | NPSMBHB | ci68_lo | -16.2 | -16.22236 | -0.02236 | near-miss |
| igw | log10_A_bhb | NPSMBHB | ci68_hi | -15.14 | -15.15286 | -0.01286 | near-miss |
| igw | gamma_bhb | NPSMBHB | bayes_mean | 4.61 | 4.61303 | 0.00303 | reproduced |
| igw | gamma_bhb | NPSMBHB | bayes_sd | 0.37 | 0.36813 | -0.00187 | reproduced |
| igw | gamma_bhb | NPSMBHB | maxpost | 4.64 | 4.62543 | -0.01457 | reproduced |
| igw | gamma_bhb | NPSMBHB | ci68_lo | 4.26 | 4.25694 | -0.00306 | reproduced |
| igw | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 4.99174 | -0.00826 | near-miss |
| sigw-delta | log10_A | NP | bayes_mean | -0.69 | -0.68714 | 0.00286 | reproduced |
| sigw-delta | log10_A | NP | bayes_sd | 0.47 | 0.47068 | 0.00068 | reproduced |
| sigw-delta | log10_A | NP | maxpost | -0.14 | -0.1805 | -0.0405 | reproduced |
| sigw-delta | log10_A | NP | ci68_lo | -1.0 | -0.99417 | 0.00583 | reproduced |
| sigw-delta | log10_A | NP | ci68_hi | -0.01 | -0.00068 | 0.00932 | near-miss |
| sigw-delta | log10_A | NPSMBHB | bayes_mean | -0.71 | -0.70819 | 0.00181 | reproduced |
| sigw-delta | log10_A | NPSMBHB | bayes_sd | 0.49 | 0.49228 | 0.00228 | reproduced |
| sigw-delta | log10_A | NPSMBHB | maxpost | -0.17 | -0.2055 | -0.0355 | reproduced |
| sigw-delta | log10_A | NPSMBHB | ci68_lo | -1.03 | -1.01947 | 0.01053 | near-miss |
| sigw-delta | log10_A | NPSMBHB | ci68_hi | -0.02 | -0.01324 | 0.00676 | near-miss |
| sigw-delta | log10_f_star | NP | bayes_mean | -5.9 | -5.89831 | 0.00169 | reproduced |
| sigw-delta | log10_f_star | NP | bayes_sd | 0.6 | 0.59752 | -0.00248 | reproduced |
| sigw-delta | log10_f_star | NP | maxpost | -5.0 | -5.07875 | -0.07875 | reproduced |
| sigw-delta | log10_f_star | NP | ci68_lo | -6.17 | -6.17977 | -0.00977 | near-miss |
| sigw-delta | log10_f_star | NP | ci68_hi | -5.0 | -5.00027 | -0.00027 | reproduced |
| sigw-delta | log10_f_star | NPSMBHB | bayes_mean | -5.93 | -5.92581 | 0.00419 | reproduced |
| sigw-delta | log10_f_star | NPSMBHB | bayes_sd | 0.67 | 0.67258 | 0.00258 | reproduced |
| sigw-delta | log10_f_star | NPSMBHB | maxpost | -5.0 | -5.20775 | -0.20775 | near-miss |
| sigw-delta | log10_f_star | NPSMBHB | ci68_lo | -6.19 | -6.19267 | -0.00267 | reproduced |
| sigw-delta | log10_f_star | NPSMBHB | ci68_hi | -5.0 | -5.00004 | -4e-05 | reproduced |
| sigw-delta | log10_A_bhb | NPSMBHB | bayes_mean | -15.77 | -15.76731 | 0.00269 | reproduced |
| sigw-delta | log10_A_bhb | NPSMBHB | bayes_sd | 0.46 | 0.45996 | -4e-05 | reproduced |
| sigw-delta | log10_A_bhb | NPSMBHB | maxpost | -15.71 | -15.70301 | 0.00699 | reproduced |
| sigw-delta | log10_A_bhb | NPSMBHB | ci68_lo | -16.18 | -16.17885 | 0.00115 | reproduced |
| sigw-delta | log10_A_bhb | NPSMBHB | ci68_hi | -15.29 | -15.28532 | 0.00468 | reproduced |
| sigw-delta | gamma_bhb | NPSMBHB | bayes_mean | 4.65 | 4.64582 | -0.00418 | reproduced |
| sigw-delta | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.34604 | -0.00396 | reproduced |
| sigw-delta | gamma_bhb | NPSMBHB | maxpost | 4.65 | 4.64897 | -0.00103 | reproduced |
| sigw-delta | gamma_bhb | NPSMBHB | ci68_lo | 4.31 | 4.31711 | 0.00711 | near-miss |
| sigw-delta | gamma_bhb | NPSMBHB | ci68_hi | 4.99 | 5.00302 | 0.01302 | near-miss |
| sigw-gauss | log10_A | NP | bayes_mean | -0.38 | -0.37634 | 0.00366 | reproduced |
| sigw-gauss | log10_A | NP | bayes_sd | 0.58 | 0.57857 | -0.00143 | reproduced |
| sigw-gauss | log10_A | NP | maxpost | -0.34 | -0.4855 | -0.1455 | near-miss |
| sigw-gauss | log10_A | NP | ci68_lo | -1.03 | -1.02455 | 0.00545 | reproduced |
| sigw-gauss | log10_A | NP | ci68_hi | 0.2 | 0.21884 | 0.01884 | near-miss |
| sigw-gauss | log10_A | NPSMBHB | bayes_mean | -0.36 | -0.36102 | -0.00102 | reproduced |
| sigw-gauss | log10_A | NPSMBHB | bayes_sd | 0.61 | 0.60475 | -0.00525 | reproduced |
| sigw-gauss | log10_A | NPSMBHB | maxpost | -0.29 | -0.4695 | -0.1795 | near-miss |
| sigw-gauss | log10_A | NPSMBHB | ci68_lo | -1.04 | -1.05207 | -0.01207 | near-miss |
| sigw-gauss | log10_A | NPSMBHB | ci68_hi | 0.24 | 0.22236 | -0.01764 | near-miss |
| sigw-gauss | log10_f_star | NP | bayes_mean | -6.32 | -6.31633 | 0.00367 | reproduced |
| sigw-gauss | log10_f_star | NP | bayes_sd | 0.71 | 0.71133 | 0.00133 | reproduced |
| sigw-gauss | log10_f_star | NP | maxpost | -7.03 | -7.06475 | -0.03475 | reproduced |
| sigw-gauss | log10_f_star | NP | ci68_lo | -7.25 | -7.29681 | -0.04681 | not-reproduced |
| sigw-gauss | log10_f_star | NP | ci68_hi | -5.65 | -5.68981 | -0.03981 | not-reproduced |
| sigw-gauss | log10_f_star | NPSMBHB | bayes_mean | -6.3 | -6.29035 | 0.00965 | near-miss |
| sigw-gauss | log10_f_star | NPSMBHB | bayes_sd | 0.73 | 0.7236 | -0.0064 | near-miss |
| sigw-gauss | log10_f_star | NPSMBHB | maxpost | -6.85 | -5.67425 | 1.17575 | not-reproduced |
| sigw-gauss | log10_f_star | NPSMBHB | ci68_lo | -7.17 | -7.14672 | 0.02328 | near-miss |
| sigw-gauss | log10_f_star | NPSMBHB | ci68_hi | -5.57 | -5.5584 | 0.0116 | near-miss |
| sigw-gauss | Delta | NP | bayes_mean | 1.35 | 1.35016 | 0.00016 | reproduced |
| sigw-gauss | Delta | NP | bayes_sd | 0.7 | 0.69687 | -0.00313 | reproduced |
| sigw-gauss | Delta | NP | maxpost | 1.6 | 1.71711 | 0.11711 | near-miss |
| sigw-gauss | Delta | NP | ci68_lo | 0.51 | 0.50774 | -0.00226 | reproduced |
| sigw-gauss | Delta | NP | ci68_hi | 2.07 | 2.06194 | -0.00806 | near-miss |
| sigw-gauss | Delta | NPSMBHB | bayes_mean | 1.3 | 1.32358 | 0.02358 | near-miss |
| sigw-gauss | Delta | NPSMBHB | bayes_sd | 0.7 | 0.70638 | 0.00638 | near-miss |
| sigw-gauss | Delta | NPSMBHB | maxpost | 1.54 | 1.61416 | 0.07416 | reproduced |
| sigw-gauss | Delta | NPSMBHB | ci68_lo | 0.37 | 0.34515 | -0.02485 | near-miss |
| sigw-gauss | Delta | NPSMBHB | ci68_hi | 1.92 | 1.91772 | -0.00228 | reproduced |
| sigw-gauss | log10_A_bhb | NPSMBHB | bayes_mean | -15.72 | -15.68137 | 0.03863 | not-reproduced |
| sigw-gauss | log10_A_bhb | NPSMBHB | bayes_sd | 0.46 | 0.56831 | 0.10831 | not-reproduced |
| sigw-gauss | log10_A_bhb | NPSMBHB | maxpost | -15.65 | -15.66653 | -0.01653 | reproduced |
| sigw-gauss | log10_A_bhb | NPSMBHB | ci68_lo | -16.14 | -16.14253 | -0.00253 | reproduced |
| sigw-gauss | log10_A_bhb | NPSMBHB | ci68_hi | -15.22 | -15.20459 | 0.01541 | near-miss |
| sigw-gauss | gamma_bhb | NPSMBHB | bayes_mean | 4.65 | 4.79927 | 0.14927 | not-reproduced |
| sigw-gauss | gamma_bhb | NPSMBHB | bayes_sd | 0.34 | 1.17588 | 0.83588 | not-reproduced |
| sigw-gauss | gamma_bhb | NPSMBHB | maxpost | 4.65 | 4.64937 | -0.00063 | reproduced |
| sigw-gauss | gamma_bhb | NPSMBHB | ci68_lo | 4.32 | 4.30847 | -0.01153 | near-miss |
| sigw-gauss | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 5.00756 | 0.00756 | near-miss |
| sigw-box | log10_A | NP | bayes_mean | -1.06 | -1.05925 | 0.00075 | reproduced |
| sigw-box | log10_A | NP | bayes_sd | 0.52 | 0.51612 | -0.00388 | reproduced |
| sigw-box | log10_A | NP | maxpost | -1.26 | -1.2595 | 0.0005 | reproduced |
| sigw-box | log10_A | NP | ci68_lo | -1.72 | -1.71012 | 0.00988 | near-miss |
| sigw-box | log10_A | NP | ci68_hi | -0.82 | -0.85463 | -0.03463 | not-reproduced |
| sigw-box | log10_A | NPSMBHB | bayes_mean | -1.02 | -1.01941 | 0.00059 | reproduced |
| sigw-box | log10_A | NPSMBHB | bayes_sd | 0.57 | 0.5714 | 0.0014 | reproduced |
| sigw-box | log10_A | NPSMBHB | maxpost | -1.25 | -1.2575 | -0.0075 | reproduced |
| sigw-box | log10_A | NPSMBHB | ci68_lo | -1.68 | -1.6993 | -0.0193 | near-miss |
| sigw-box | log10_A | NPSMBHB | ci68_hi | -0.74 | -0.7597 | -0.0197 | near-miss |
| sigw-box | log10_f_min | NP | bayes_mean | -7.34 | -7.33915 | 0.00085 | reproduced |
| sigw-box | log10_f_min | NP | bayes_sd | 0.48 | 0.47562 | -0.00438 | reproduced |
| sigw-box | log10_f_min | NP | maxpost | -7.5 | -7.49975 | 0.00025 | reproduced |
| sigw-box | log10_f_min | NP | ci68_lo | -8.01 | -7.76194 | 0.24806 | not-reproduced |
| sigw-box | log10_f_min | NP | ci68_hi | -6.97 | -6.91267 | 0.05733 | not-reproduced |
| sigw-box | log10_f_min | NPSMBHB | bayes_mean | -7.29 | -7.28788 | 0.00212 | reproduced |
| sigw-box | log10_f_min | NPSMBHB | bayes_sd | 0.55 | 0.55496 | 0.00496 | reproduced |
| sigw-box | log10_f_min | NPSMBHB | maxpost | -7.48 | -7.47275 | 0.00725 | reproduced |
| sigw-box | log10_f_min | NPSMBHB | ci68_lo | -7.97 | -7.74389 | 0.22611 | not-reproduced |
| sigw-box | log10_f_min | NPSMBHB | ci68_hi | -6.84 | -6.82314 | 0.01686 | near-miss |
| sigw-box | log10_f_max | NP | bayes_mean | -6.06 | -6.06462 | -0.00462 | reproduced |
| sigw-box | log10_f_max | NP | bayes_sd | 0.65 | 0.65214 | 0.00214 | reproduced |
| sigw-box | log10_f_max | NP | maxpost | -5.4 | -5.44025 | -0.04025 | reproduced |
| sigw-box | log10_f_max | NP | ci68_lo | -6.42 | -6.42691 | -0.00691 | near-miss |
| sigw-box | log10_f_max | NP | ci68_hi | -5.0 | -5.00008 | -8e-05 | reproduced |
| sigw-box | log10_f_max | NPSMBHB | bayes_mean | -6.12 | -6.12323 | -0.00323 | reproduced |
| sigw-box | log10_f_max | NPSMBHB | bayes_sd | 0.81 | 0.80856 | -0.00144 | reproduced |
| sigw-box | log10_f_max | NPSMBHB | maxpost | -5.36 | -5.40575 | -0.04575 | reproduced |
| sigw-box | log10_f_max | NPSMBHB | ci68_lo | -6.45 | -6.45207 | -0.00207 | reproduced |
| sigw-box | log10_f_max | NPSMBHB | ci68_hi | -5.0 | -5.00083 | -0.00083 | reproduced |
| sigw-box | log10_A_bhb | NPSMBHB | bayes_mean | -15.7 | -15.70186 | -0.00186 | reproduced |
| sigw-box | log10_A_bhb | NPSMBHB | bayes_sd | 0.49 | 0.48538 | -0.00462 | reproduced |
| sigw-box | log10_A_bhb | NPSMBHB | maxpost | -15.64 | -15.67896 | -0.03896 | reproduced |
| sigw-box | log10_A_bhb | NPSMBHB | ci68_lo | -16.15 | -16.15882 | -0.00882 | near-miss |
| sigw-box | log10_A_bhb | NPSMBHB | ci68_hi | -15.21 | -15.22043 | -0.01043 | near-miss |
| sigw-box | gamma_bhb | NPSMBHB | bayes_mean | 4.65 | 4.6495 | -0.0005 | reproduced |
| sigw-box | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.34951 | -0.00049 | reproduced |
| sigw-box | gamma_bhb | NPSMBHB | maxpost | 4.66 | 4.67067 | 0.01067 | reproduced |
| sigw-box | gamma_bhb | NPSMBHB | ci68_lo | 4.31 | 4.31769 | 0.00769 | near-miss |
| sigw-box | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 5.01234 | 0.01234 | near-miss |
| pt-bubble | log10_T_star | NP | bayes_mean | -0.76 | -0.75761 | 0.00239 | reproduced |
| pt-bubble | log10_T_star | NP | bayes_sd | 0.49 | 0.48585 | -0.00415 | reproduced |
| pt-bubble | log10_T_star | NP | maxpost | -0.9 | -0.825 | 0.075 | reproduced |
| pt-bubble | log10_T_star | NP | ci68_lo | -1.33 | -1.33971 | -0.00971 | near-miss |
| pt-bubble | log10_T_star | NP | ci68_hi | -0.39 | -0.39857 | -0.00857 | near-miss |
| pt-bubble | log10_T_star | NPSMBHB | bayes_mean | -0.71 | -0.71454 | -0.00454 | reproduced |
| pt-bubble | log10_T_star | NPSMBHB | bayes_sd | 0.7 | 0.70376 | 0.00376 | reproduced |
| pt-bubble | log10_T_star | NPSMBHB | maxpost | -0.89 | -0.869 | 0.021 | reproduced |
| pt-bubble | log10_T_star | NPSMBHB | ci68_lo | -1.34 | -1.35084 | -0.01084 | near-miss |
| pt-bubble | log10_T_star | NPSMBHB | ci68_hi | -0.34 | -0.35505 | -0.01505 | near-miss |
| pt-bubble | log10_alpha_star | NP | bayes_mean | -0.26 | 0.26339 | 0.52339 | not-reproduced |
| pt-bubble | log10_alpha_star | NP | bayes_sd | 0.47 | 0.46584 | -0.00416 | reproduced |
| pt-bubble | log10_alpha_star | NP | maxpost | 1.0 | 0.80463 | -0.19537 | near-miss |
| pt-bubble | log10_alpha_star | NP | ci68_lo | 0.03 | 0.02567 | -0.00433 | reproduced |
| pt-bubble | log10_alpha_star | NP | ci68_hi | 1.0 | 1.0 | -0.0 | reproduced |
| pt-bubble | log10_alpha_star | NPSMBHB | bayes_mean | -0.23 | 0.22556 | 0.45556 | not-reproduced |
| pt-bubble | log10_alpha_star | NPSMBHB | bayes_sd | 0.52 | 0.51832 | -0.00168 | reproduced |
| pt-bubble | log10_alpha_star | NPSMBHB | maxpost | 0.74 | 0.74388 | 0.00388 | reproduced |
| pt-bubble | log10_alpha_star | NPSMBHB | ci68_lo | 0.01 | -0.00242 | -0.01242 | near-miss |
| pt-bubble | log10_alpha_star | NPSMBHB | ci68_hi | 1.0 | 0.99949 | -0.00051 | reproduced |
| pt-bubble | log10_HR | NP | bayes_mean | -0.42 | -0.42035 | -0.00035 | reproduced |
| pt-bubble | log10_HR | NP | bayes_sd | 0.26 | 0.26066 | 0.00066 | reproduced |
| pt-bubble | log10_HR | NP | maxpost | 0.0 | -0.06937 | -0.06937 | reproduced |
| pt-bubble | log10_HR | NP | ci68_lo | -0.56 | -0.56165 | -0.00165 | reproduced |
| pt-bubble | log10_HR | NP | ci68_hi | 0.0 | -3e-05 | -3e-05 | reproduced |
| pt-bubble | log10_HR | NPSMBHB | bayes_mean | -0.47 | -0.47026 | -0.00026 | reproduced |
| pt-bubble | log10_HR | NPSMBHB | bayes_sd | 0.39 | 0.38958 | -0.00042 | reproduced |
| pt-bubble | log10_HR | NPSMBHB | maxpost | -0.06 | -0.07762 | -0.01762 | reproduced |
| pt-bubble | log10_HR | NPSMBHB | ci68_lo | -0.58 | -0.581 | -0.001 | reproduced |
| pt-bubble | log10_HR | NPSMBHB | ci68_hi | 0.0 | -0.00015 | -0.00015 | reproduced |
| pt-bubble | a | NP | bayes_mean | 2.04 | 2.03904 | -0.00096 | reproduced |
| pt-bubble | a | NP | bayes_sd | 0.48 | 0.47606 | -0.00394 | reproduced |
| pt-bubble | a | NP | maxpost | 1.97 | 1.96525 | -0.00475 | reproduced |
| pt-bubble | a | NP | ci68_lo | 1.49 | 1.46737 | -0.02263 | near-miss |
| pt-bubble | a | NP | ci68_hi | 2.54 | 2.5115 | -0.0285 | near-miss |
| pt-bubble | a | NPSMBHB | bayes_mean | 2.07 | 2.06759 | -0.00241 | reproduced |
| pt-bubble | a | NPSMBHB | bayes_sd | 0.49 | 0.49089 | 0.00089 | reproduced |
| pt-bubble | a | NPSMBHB | maxpost | 2.01 | 1.98425 | -0.02575 | reproduced |
| pt-bubble | a | NPSMBHB | ci68_lo | 1.54 | 1.5237 | -0.0163 | near-miss |
| pt-bubble | a | NPSMBHB | ci68_hi | 2.63 | 2.61087 | -0.01913 | near-miss |
| pt-bubble | b | NP | bayes_mean | 1.97 | 1.9716 | 0.0016 | reproduced |
| pt-bubble | b | NP | bayes_sd | 0.58 | 0.57692 | -0.00308 | reproduced |
| pt-bubble | b | NP | maxpost | 1.0 | 1.09825 | 0.09825 | reproduced |
| pt-bubble | b | NP | ci68_lo | 1.0 | 1.00052 | 0.00052 | reproduced |
| pt-bubble | b | NP | ci68_hi | 2.32 | 2.32449 | 0.00449 | reproduced |
| pt-bubble | b | NPSMBHB | bayes_mean | 1.98 | 1.97598 | -0.00402 | reproduced |
| pt-bubble | b | NPSMBHB | bayes_sd | 0.58 | 0.57667 | -0.00333 | reproduced |
| pt-bubble | b | NPSMBHB | maxpost | 1.0 | 1.10425 | 0.10425 | near-miss |
| pt-bubble | b | NPSMBHB | ci68_lo | 1.0 | 1.00005 | 5e-05 | reproduced |
| pt-bubble | b | NPSMBHB | ci68_hi | 2.33 | 2.32638 | -0.00362 | reproduced |
| pt-bubble | c | NP | bayes_mean | 2.03 | 2.03485 | 0.00485 | reproduced |
| pt-bubble | c | NP | bayes_sd | 0.57 | 0.57104 | 0.00104 | reproduced |
| pt-bubble | c | NP | maxpost | 3.0 | 2.87325 | -0.12675 | near-miss |
| pt-bubble | c | NP | ci68_lo | 1.69 | 1.69257 | 0.00257 | reproduced |
| pt-bubble | c | NP | ci68_hi | 3.0 | 2.99956 | -0.00044 | reproduced |
| pt-bubble | c | NPSMBHB | bayes_mean | 2.03 | 2.03277 | 0.00277 | reproduced |
| pt-bubble | c | NPSMBHB | bayes_sd | 0.57 | 0.57072 | 0.00072 | reproduced |
| pt-bubble | c | NPSMBHB | maxpost | 2.93 | 2.59575 | -0.33425 | not-reproduced |
| pt-bubble | c | NPSMBHB | ci68_lo | 1.69 | 1.68927 | -0.00073 | reproduced |
| pt-bubble | c | NPSMBHB | ci68_hi | 3.0 | 2.99993 | -7e-05 | reproduced |
| pt-bubble | log10_A_bhb | NPSMBHB | bayes_mean | -15.68 | -15.68228 | -0.00228 | reproduced |
| pt-bubble | log10_A_bhb | NPSMBHB | bayes_sd | 0.51 | 0.50575 | -0.00425 | reproduced |
| pt-bubble | log10_A_bhb | NPSMBHB | maxpost | -15.65 | -15.65457 | -0.00457 | reproduced |
| pt-bubble | log10_A_bhb | NPSMBHB | ci68_lo | -16.17 | -16.17843 | -0.00843 | near-miss |
| pt-bubble | log10_A_bhb | NPSMBHB | ci68_hi | -15.21 | -15.21305 | -0.00305 | reproduced |
| pt-bubble | gamma_bhb | NPSMBHB | bayes_mean | 4.64 | 4.63845 | -0.00155 | reproduced |
| pt-bubble | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.35479 | 0.00479 | reproduced |
| pt-bubble | gamma_bhb | NPSMBHB | maxpost | 4.65 | 4.65565 | 0.00565 | reproduced |
| pt-bubble | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.29554 | -0.00446 | reproduced |
| pt-bubble | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 5.00036 | 0.00036 | reproduced |
| pt-sound | log10_T_star | NP | bayes_mean | -1.84 | -1.84134 | -0.00134 | reproduced |
| pt-sound | log10_T_star | NP | bayes_sd | 0.41 | 0.41046 | 0.00046 | reproduced |
| pt-sound | log10_T_star | NP | maxpost | -2.0 | -2.033 | -0.033 | reproduced |
| pt-sound | log10_T_star | NP | ci68_lo | -2.33 | -2.34496 | -0.01496 | near-miss |
| pt-sound | log10_T_star | NP | ci68_hi | -1.48 | -1.49244 | -0.01244 | near-miss |
| pt-sound | log10_T_star | NPSMBHB | bayes_mean | -1.56 | -1.56387 | -0.00387 | reproduced |
| pt-sound | log10_T_star | NPSMBHB | bayes_sd | 1.06 | 1.0557 | -0.0043 | reproduced |
| pt-sound | log10_T_star | NPSMBHB | maxpost | -1.95 | -1.941 | 0.009 | reproduced |
| pt-sound | log10_T_star | NPSMBHB | ci68_lo | -2.31 | -2.30398 | 0.00602 | near-miss |
| pt-sound | log10_T_star | NPSMBHB | ci68_hi | -1.3 | -1.29569 | 0.00431 | reproduced |
| pt-sound | log10_alpha_star | NP | bayes_mean | -0.22 | 0.21866 | 0.43866 | not-reproduced |
| pt-sound | log10_alpha_star | NP | bayes_sd | 0.44 | 0.43727 | -0.00273 | reproduced |
| pt-sound | log10_alpha_star | NP | maxpost | -0.21 | -0.16738 | 0.04262 | reproduced |
| pt-sound | log10_alpha_star | NP | ci68_lo | -0.37 | -0.37757 | -0.00757 | near-miss |
| pt-sound | log10_alpha_star | NP | ci68_hi | 1.0 | 0.62297 | -0.37703 | not-reproduced |
| pt-sound | log10_alpha_star | NPSMBHB | bayes_mean | 0.14 | 0.13544 | -0.00456 | reproduced |
| pt-sound | log10_alpha_star | NPSMBHB | bayes_sd | 0.56 | 0.55916 | -0.00084 | reproduced |
| pt-sound | log10_alpha_star | NPSMBHB | maxpost | -0.15 | -0.23337 | -0.08337 | reproduced |
| pt-sound | log10_alpha_star | NPSMBHB | ci68_lo | -0.34 | -0.37144 | -0.03144 | not-reproduced |
| pt-sound | log10_alpha_star | NPSMBHB | ci68_hi | 0.73 | 0.68577 | -0.04423 | not-reproduced |
| pt-sound | log10_HR | NP | bayes_mean | -0.81 | -0.80969 | 0.00031 | reproduced |
| pt-sound | log10_HR | NP | bayes_sd | 0.36 | 0.3559 | -0.0041 | reproduced |
| pt-sound | log10_HR | NP | maxpost | -1.05 | -1.05412 | -0.00412 | reproduced |
| pt-sound | log10_HR | NP | ci68_lo | -1.28 | -1.28118 | -0.00118 | reproduced |
| pt-sound | log10_HR | NP | ci68_hi | -0.57 | -0.58204 | -0.01204 | near-miss |
| pt-sound | log10_HR | NPSMBHB | bayes_mean | -0.87 | -0.87398 | -0.00398 | reproduced |
| pt-sound | log10_HR | NPSMBHB | bayes_sd | 0.51 | 0.5077 | -0.0023 | reproduced |
| pt-sound | log10_HR | NPSMBHB | maxpost | -1.01 | -0.97313 | 0.03687 | reproduced |
| pt-sound | log10_HR | NPSMBHB | ci68_lo | -1.26 | -1.26717 | -0.00717 | near-miss |
| pt-sound | log10_HR | NPSMBHB | ci68_hi | -0.45 | -0.46012 | -0.01012 | near-miss |
| pt-sound | a | NP | bayes_mean | 3.58 | 3.5839 | 0.0039 | reproduced |
| pt-sound | a | NP | bayes_sd | 0.47 | 0.47283 | 0.00283 | reproduced |
| pt-sound | a | NP | maxpost | 3.0 | 3.05625 | 0.05625 | reproduced |
| pt-sound | a | NP | ci68_lo | 3.0 | 3.00001 | 1e-05 | reproduced |
| pt-sound | a | NP | ci68_hi | 3.72 | 3.72478 | 0.00478 | reproduced |
| pt-sound | a | NPSMBHB | bayes_mean | 3.74 | 3.745 | 0.005 | reproduced |
| pt-sound | a | NPSMBHB | bayes_sd | 0.54 | 0.53853 | -0.00147 | reproduced |
| pt-sound | a | NPSMBHB | maxpost | 3.0 | 3.06575 | 0.06575 | reproduced |
| pt-sound | a | NPSMBHB | ci68_lo | 3.0 | 3.00002 | 2e-05 | reproduced |
| pt-sound | a | NPSMBHB | ci68_hi | 3.98 | 3.97567 | -0.00433 | reproduced |
| pt-sound | b | NP | bayes_mean | 2.87 | 2.86546 | -0.00454 | reproduced |
| pt-sound | b | NP | bayes_sd | 0.57 | 0.56661 | -0.00339 | reproduced |
| pt-sound | b | NP | maxpost | 2.0 | 2.08075 | 0.08075 | reproduced |
| pt-sound | b | NP | ci68_lo | 2.0 | 2.00008 | 8e-05 | reproduced |
| pt-sound | b | NP | ci68_hi | 3.17 | 3.17026 | 0.00026 | reproduced |
| pt-sound | b | NPSMBHB | bayes_mean | 2.92 | 2.91694 | -0.00306 | reproduced |
| pt-sound | b | NPSMBHB | bayes_sd | 0.57 | 0.57309 | 0.00309 | reproduced |
| pt-sound | b | NPSMBHB | maxpost | 2.0 | 2.06575 | 0.06575 | reproduced |
| pt-sound | b | NPSMBHB | ci68_lo | 2.0 | 2.00034 | 0.00034 | reproduced |
| pt-sound | b | NPSMBHB | ci68_hi | 3.25 | 3.24535 | -0.00465 | reproduced |
| pt-sound | c | NP | bayes_mean | 4.16 | 4.15777 | -0.00223 | reproduced |
| pt-sound | c | NP | bayes_sd | 0.56 | 0.55866 | -0.00134 | reproduced |
| pt-sound | c | NP | maxpost | 5.0 | 4.87975 | -0.12025 | near-miss |
| pt-sound | c | NP | ci68_lo | 3.87 | 3.86998 | -2e-05 | reproduced |
| pt-sound | c | NP | ci68_hi | 5.0 | 4.99993 | -7e-05 | reproduced |
| pt-sound | c | NPSMBHB | bayes_mean | 4.09 | 4.09008 | 8e-05 | reproduced |
| pt-sound | c | NPSMBHB | bayes_sd | 0.57 | 0.56511 | -0.00489 | reproduced |
| pt-sound | c | NPSMBHB | maxpost | 5.0 | 4.92775 | -0.07225 | reproduced |
| pt-sound | c | NPSMBHB | ci68_lo | 3.77 | 3.7733 | 0.0033 | reproduced |
| pt-sound | c | NPSMBHB | ci68_hi | 5.0 | 4.99995 | -5e-05 | reproduced |
| pt-sound | log10_A_bhb | NPSMBHB | bayes_mean | -15.45 | -15.45094 | -0.00094 | reproduced |
| pt-sound | log10_A_bhb | NPSMBHB | bayes_sd | 0.55 | 0.54671 | -0.00329 | reproduced |
| pt-sound | log10_A_bhb | NPSMBHB | maxpost | -15.39 | -15.378 | 0.012 | reproduced |
| pt-sound | log10_A_bhb | NPSMBHB | ci68_lo | -16.04 | -16.05472 | -0.01472 | near-miss |
| pt-sound | log10_A_bhb | NPSMBHB | ci68_hi | -14.94 | -14.95246 | -0.01246 | near-miss |
| pt-sound | gamma_bhb | NPSMBHB | bayes_mean | 4.63 | 4.62562 | -0.00438 | reproduced |
| pt-sound | gamma_bhb | NPSMBHB | bayes_sd | 0.38 | 0.37663 | -0.00337 | reproduced |
| pt-sound | gamma_bhb | NPSMBHB | maxpost | 4.67 | 4.65331 | -0.01669 | reproduced |
| pt-sound | gamma_bhb | NPSMBHB | ci68_lo | 4.27 | 4.27447 | 0.00447 | reproduced |
| pt-sound | gamma_bhb | NPSMBHB | ci68_hi | 5.03 | 5.02567 | -0.00433 | reproduced |
| stable-c | log10_Gmu | NP | bayes_mean | -10.15 | -10.14752 | 0.00248 | reproduced |
| stable-c | log10_Gmu | NP | bayes_sd | 0.16 | 0.16093 | 0.00093 | reproduced |
| stable-c | log10_Gmu | NP | maxpost | -10.18 | -10.193 | -0.013 | reproduced |
| stable-c | log10_Gmu | NP | ci68_lo | -10.33 | -10.32693 | 0.00307 | reproduced |
| stable-c | log10_Gmu | NP | ci68_hi | -10.01 | -10.00971 | 0.00029 | reproduced |
| stable-c | log10_Gmu | NPSMBHB | bayes_mean | -11.41 | -11.40518 | 0.00482 | reproduced |
| stable-c | log10_Gmu | NPSMBHB | bayes_sd | 1.25 | 1.24946 | -0.00054 | reproduced |
| stable-c | log10_Gmu | NPSMBHB | maxpost | -10.22 | -10.219 | 0.001 | reproduced |
| stable-c | log10_Gmu | NPSMBHB | ci68_lo | -12.13 | -12.13446 | -0.00446 | reproduced |
| stable-c | log10_Gmu | NPSMBHB | ci68_hi | -9.88 | -9.88796 | -0.00796 | near-miss |
| stable-c | log10_A_bhb | NPSMBHB | bayes_mean | -14.95 | -14.94921 | 0.00079 | reproduced |
| stable-c | log10_A_bhb | NPSMBHB | bayes_sd | 0.58 | 0.57749 | -0.00251 | reproduced |
| stable-c | log10_A_bhb | NPSMBHB | maxpost | -14.56 | -14.55298 | 0.00702 | reproduced |
| stable-c | log10_A_bhb | NPSMBHB | ci68_lo | -15.58 | -15.04201 | 0.53799 | not-reproduced |
| stable-c | log10_A_bhb | NPSMBHB | ci68_hi | -14.31 | -14.30946 | 0.00054 | reproduced |
| stable-c | gamma_bhb | NPSMBHB | bayes_mean | 4.34 | 4.34094 | 0.00094 | reproduced |
| stable-c | gamma_bhb | NPSMBHB | bayes_sd | 0.38 | 0.37754 | -0.00246 | reproduced |
| stable-c | gamma_bhb | NPSMBHB | maxpost | 4.24 | 4.23683 | -0.00317 | reproduced |
| stable-c | gamma_bhb | NPSMBHB | ci68_lo | 3.91 | 3.91509 | 0.00509 | reproduced |
| stable-c | gamma_bhb | NPSMBHB | ci68_hi | 4.66 | 4.66835 | 0.00835 | near-miss |
| stable-k | log10_Gmu | NP | bayes_mean | -10.33 | -10.33165 | -0.00165 | reproduced |
| stable-k | log10_Gmu | NP | bayes_sd | 0.15 | 0.14687 | -0.00313 | reproduced |
| stable-k | log10_Gmu | NP | maxpost | -10.36 | -10.355 | 0.005 | reproduced |
| stable-k | log10_Gmu | NP | ci68_lo | -10.5 | -10.49058 | 0.00942 | near-miss |
| stable-k | log10_Gmu | NP | ci68_hi | -10.21 | -10.20271 | 0.00729 | near-miss |
| stable-k | log10_Gmu | NPSMBHB | bayes_mean | -11.34 | -11.34436 | -0.00436 | reproduced |
| stable-k | log10_Gmu | NPSMBHB | bayes_sd | 1.17 | 1.1656 | -0.0044 | reproduced |
| stable-k | log10_Gmu | NPSMBHB | maxpost | -10.38 | -10.385 | -0.005 | reproduced |
| stable-k | log10_Gmu | NPSMBHB | ci68_lo | -11.84 | -11.84551 | -0.00551 | reproduced |
| stable-k | log10_Gmu | NPSMBHB | ci68_hi | -10.04 | -10.05266 | -0.01266 | near-miss |
| stable-k | log10_A_bhb | NPSMBHB | bayes_mean | -15.04 | -15.04308 | -0.00308 | reproduced |
| stable-k | log10_A_bhb | NPSMBHB | bayes_sd | 0.61 | 0.60861 | -0.00139 | reproduced |
| stable-k | log10_A_bhb | NPSMBHB | maxpost | -14.56 | -14.55893 | 0.00107 | reproduced |
| stable-k | log10_A_bhb | NPSMBHB | ci68_lo | -15.68 | -15.31352 | 0.36648 | not-reproduced |
| stable-k | log10_A_bhb | NPSMBHB | ci68_hi | -14.34 | -14.34202 | -0.00202 | reproduced |
| stable-k | gamma_bhb | NPSMBHB | bayes_mean | 4.39 | 4.38604 | -0.00396 | reproduced |
| stable-k | gamma_bhb | NPSMBHB | bayes_sd | 0.38 | 0.38114 | 0.00114 | reproduced |
| stable-k | gamma_bhb | NPSMBHB | maxpost | 4.28 | 4.28944 | 0.00944 | reproduced |
| stable-k | gamma_bhb | NPSMBHB | ci68_lo | 3.95 | 3.97134 | 0.02134 | near-miss |
| stable-k | gamma_bhb | NPSMBHB | ci68_hi | 4.72 | 4.74006 | 0.02006 | near-miss |
| stable-m | log10_Gmu | NP | bayes_mean | -10.53 | -10.53098 | -0.00098 | reproduced |
| stable-m | log10_Gmu | NP | bayes_sd | 0.14 | 0.1361 | -0.0039 | reproduced |
| stable-m | log10_Gmu | NP | maxpost | -10.56 | -10.545 | 0.015 | reproduced |
| stable-m | log10_Gmu | NP | ci68_lo | -10.68 | -10.6803 | -0.0003 | reproduced |
| stable-m | log10_Gmu | NP | ci68_hi | -10.42 | -10.41541 | 0.00459 | reproduced |
| stable-m | log10_Gmu | NPSMBHB | bayes_mean | -11.47 | -11.46546 | 0.00454 | reproduced |
| stable-m | log10_Gmu | NPSMBHB | bayes_sd | 1.09 | 1.09451 | 0.00451 | reproduced |
| stable-m | log10_Gmu | NPSMBHB | maxpost | -10.6 | -10.591 | 0.009 | reproduced |
| stable-m | log10_Gmu | NPSMBHB | ci68_lo | -11.91 | -11.89013 | 0.01987 | near-miss |
| stable-m | log10_Gmu | NPSMBHB | ci68_hi | -10.27 | -10.26188 | 0.00812 | near-miss |
| stable-m | log10_A_bhb | NPSMBHB | bayes_mean | -15.05 | -15.04619 | 0.00381 | reproduced |
| stable-m | log10_A_bhb | NPSMBHB | bayes_sd | 0.61 | 0.60971 | -0.00029 | reproduced |
| stable-m | log10_A_bhb | NPSMBHB | maxpost | -14.58 | -14.58128 | -0.00128 | reproduced |
| stable-m | log10_A_bhb | NPSMBHB | ci68_lo | -15.67 | -15.3141 | 0.3559 | not-reproduced |
| stable-m | log10_A_bhb | NPSMBHB | ci68_hi | -14.34 | -14.33023 | 0.00977 | near-miss |
| stable-m | gamma_bhb | NPSMBHB | bayes_mean | 4.39 | 4.38585 | -0.00415 | reproduced |
| stable-m | gamma_bhb | NPSMBHB | bayes_sd | 0.38 | 0.38419 | 0.00419 | reproduced |
| stable-m | gamma_bhb | NPSMBHB | maxpost | 4.28 | 4.26067 | -0.01933 | reproduced |
| stable-m | gamma_bhb | NPSMBHB | ci68_lo | 3.96 | 3.95791 | -0.00209 | reproduced |
| stable-m | gamma_bhb | NPSMBHB | ci68_hi | 4.73 | 4.73274 | 0.00274 | reproduced |
| stable-n | log10_Gmu | NP | bayes_mean | -10.18 | -10.18026 | -0.00026 | reproduced |
| stable-n | log10_Gmu | NP | bayes_sd | 0.15 | 0.1531 | 0.0031 | reproduced |
| stable-n | log10_Gmu | NP | maxpost | -10.21 | -10.197 | 0.013 | reproduced |
| stable-n | log10_Gmu | NP | ci68_lo | -10.35 | -10.34782 | 0.00218 | reproduced |
| stable-n | log10_Gmu | NP | ci68_hi | -10.05 | -10.04546 | 0.00454 | reproduced |
| stable-n | log10_Gmu | NPSMBHB | bayes_mean | -11.34 | -11.34109 | -0.00109 | reproduced |
| stable-n | log10_Gmu | NPSMBHB | bayes_sd | 1.23 | 1.23192 | 0.00192 | reproduced |
| stable-n | log10_Gmu | NPSMBHB | maxpost | -10.25 | -10.249 | 0.001 | reproduced |
| stable-n | log10_Gmu | NPSMBHB | ci68_lo | -11.99 | -11.97776 | 0.01224 | near-miss |
| stable-n | log10_Gmu | NPSMBHB | ci68_hi | -9.9 | -9.89933 | 0.00067 | reproduced |
| stable-n | log10_A_bhb | NPSMBHB | bayes_mean | -14.99 | -14.99371 | -0.00371 | reproduced |
| stable-n | log10_A_bhb | NPSMBHB | bayes_sd | 0.59 | 0.59435 | 0.00435 | reproduced |
| stable-n | log10_A_bhb | NPSMBHB | maxpost | -14.56 | -14.56357 | -0.00357 | reproduced |
| stable-n | log10_A_bhb | NPSMBHB | ci68_lo | -15.61 | -15.17189 | 0.43811 | not-reproduced |
| stable-n | log10_A_bhb | NPSMBHB | ci68_hi | -14.32 | -14.31982 | 0.00018 | reproduced |
| stable-n | gamma_bhb | NPSMBHB | bayes_mean | 4.37 | 4.36506 | -0.00494 | reproduced |
| stable-n | gamma_bhb | NPSMBHB | bayes_sd | 0.38 | 0.37781 | -0.00219 | reproduced |
| stable-n | gamma_bhb | NPSMBHB | maxpost | 4.26 | 4.2464 | -0.0136 | reproduced |
| stable-n | gamma_bhb | NPSMBHB | ci68_lo | 3.93 | 3.92177 | -0.00823 | near-miss |
| stable-n | gamma_bhb | NPSMBHB | ci68_hi | 4.69 | 4.67964 | -0.01036 | near-miss |
| meta-l | log10_Gmu | NP | bayes_mean | -5.8 | -5.80476 | -0.00476 | reproduced |
| meta-l | log10_Gmu | NP | bayes_sd | 0.78 | 0.78083 | 0.00083 | reproduced |
| meta-l | log10_Gmu | NP | maxpost | -5.04 | -5.04531 | -0.00531 | reproduced |
| meta-l | log10_Gmu | NP | ci68_lo | -6.14 | -6.13593 | 0.00407 | reproduced |
| meta-l | log10_Gmu | NP | ci68_hi | -4.84 | -4.83148 | 0.00852 | near-miss |
| meta-l | log10_Gmu | NPSMBHB | bayes_mean | -5.9 | -5.90323 | -0.00323 | reproduced |
| meta-l | log10_Gmu | NPSMBHB | bayes_sd | 1.2 | 1.15635 | -0.04365 | reproduced |
| meta-l | log10_Gmu | NPSMBHB | maxpost | -5.05 | -5.04844 | 0.00156 | reproduced |
| meta-l | log10_Gmu | NPSMBHB | ci68_lo | -6.19 | -6.18446 | 0.00554 | reproduced |
| meta-l | log10_Gmu | NPSMBHB | ci68_hi | -4.83 | -4.82993 | 7e-05 | reproduced |
| meta-l | sqrt_kappa | NP | bayes_mean | 7.95 | 7.94564 | -0.00436 | reproduced |
| meta-l | sqrt_kappa | NP | bayes_sd | 0.13 | 0.12643 | -0.00357 | reproduced |
| meta-l | sqrt_kappa | NP | maxpost | 7.85 | 7.82906 | -0.02094 | reproduced |
| meta-l | sqrt_kappa | NP | ci68_lo | 7.81 | 7.79994 | -0.01006 | near-miss |
| meta-l | sqrt_kappa | NP | ci68_hi | 8.0 | 7.97944 | -0.02056 | near-miss |
| meta-l | sqrt_kappa | NPSMBHB | bayes_mean | 7.95 | 7.94567 | -0.00433 | reproduced |
| meta-l | sqrt_kappa | NPSMBHB | bayes_sd | 0.18 | 0.18236 | 0.00236 | reproduced |
| meta-l | sqrt_kappa | NPSMBHB | maxpost | 7.84 | 7.82531 | -0.01469 | reproduced |
| meta-l | sqrt_kappa | NPSMBHB | ci68_lo | 7.8 | 7.79966 | -0.00034 | reproduced |
| meta-l | sqrt_kappa | NPSMBHB | ci68_hi | 8.0 | 7.98613 | -0.01387 | near-miss |
| meta-l | log10_A_bhb | NPSMBHB | bayes_mean | -15.73 | -15.72592 | 0.00408 | reproduced |
| meta-l | log10_A_bhb | NPSMBHB | bayes_sd | 0.48 | 0.48453 | 0.00453 | reproduced |
| meta-l | log10_A_bhb | NPSMBHB | maxpost | -15.67 | -15.66598 | 0.00402 | reproduced |
| meta-l | log10_A_bhb | NPSMBHB | ci68_lo | -16.18 | -16.19818 | -0.01818 | near-miss |
| meta-l | log10_A_bhb | NPSMBHB | ci68_hi | -15.25 | -15.26407 | -0.01407 | near-miss |
| meta-l | gamma_bhb | NPSMBHB | bayes_mean | 4.64 | 4.64358 | 0.00358 | reproduced |
| meta-l | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.34836 | -0.00164 | reproduced |
| meta-l | gamma_bhb | NPSMBHB | maxpost | 4.66 | 4.66839 | 0.00839 | reproduced |
| meta-l | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.30106 | 0.00106 | reproduced |
| meta-l | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 4.99533 | -0.00467 | reproduced |
| meta-ls | log10_Gmu | NP | bayes_mean | -5.62 | -5.61837 | 0.00163 | reproduced |
| meta-ls | log10_Gmu | NP | bayes_sd | 1.01 | 1.00719 | -0.00281 | reproduced |
| meta-ls | log10_Gmu | NP | maxpost | -4.46 | -5.55469 | -1.09469 | not-reproduced |
| meta-ls | log10_Gmu | NP | ci68_lo | -6.26 | -6.25926 | 0.00074 | reproduced |
| meta-ls | log10_Gmu | NP | ci68_hi | -4.24 | -4.23967 | 0.00033 | reproduced |
| meta-ls | log10_Gmu | NPSMBHB | bayes_mean | -5.7 | -5.69898 | 0.00102 | reproduced |
| meta-ls | log10_Gmu | NPSMBHB | bayes_sd | 1.4 | 1.39771 | -0.00229 | reproduced |
| meta-ls | log10_Gmu | NPSMBHB | maxpost | -4.44 | -4.41406 | 0.02594 | reproduced |
| meta-ls | log10_Gmu | NPSMBHB | ci68_lo | -6.33 | -6.30359 | 0.02641 | near-miss |
| meta-ls | log10_Gmu | NPSMBHB | ci68_hi | -4.15 | -4.12735 | 0.02265 | near-miss |
| meta-ls | sqrt_kappa | NP | bayes_mean | 7.83 | 7.82592 | -0.00408 | reproduced |
| meta-ls | sqrt_kappa | NP | bayes_sd | 0.18 | 0.17524 | -0.00476 | reproduced |
| meta-ls | sqrt_kappa | NP | maxpost | 7.61 | 7.61156 | 0.00156 | reproduced |
| meta-ls | sqrt_kappa | NP | ci68_lo | 7.59 | 7.583 | -0.007 | near-miss |
| meta-ls | sqrt_kappa | NP | ci68_hi | 7.92 | 7.91709 | -0.00291 | reproduced |
| meta-ls | sqrt_kappa | NPSMBHB | bayes_mean | 7.82 | 7.82103 | 0.00103 | reproduced |
| meta-ls | sqrt_kappa | NPSMBHB | bayes_sd | 0.23 | 0.22542 | -0.00458 | reproduced |
| meta-ls | sqrt_kappa | NPSMBHB | maxpost | 7.61 | 7.59969 | -0.01031 | reproduced |
| meta-ls | sqrt_kappa | NPSMBHB | ci68_lo | 7.57 | 7.56808 | -0.00192 | reproduced |
| meta-ls | sqrt_kappa | NPSMBHB | ci68_hi | 7.93 | 7.92392 | -0.00608 | near-miss |
| meta-ls | log10_A_bhb | NPSMBHB | bayes_mean | -15.71 | -15.71073 | -0.00073 | reproduced |
| meta-ls | log10_A_bhb | NPSMBHB | bayes_sd | 0.49 | 0.48951 | -0.00049 | reproduced |
| meta-ls | log10_A_bhb | NPSMBHB | maxpost | -15.67 | -15.63772 | 0.03228 | reproduced |
| meta-ls | log10_A_bhb | NPSMBHB | ci68_lo | -16.17 | -16.16109 | 0.00891 | near-miss |
| meta-ls | log10_A_bhb | NPSMBHB | ci68_hi | -15.23 | -15.21943 | 0.01057 | near-miss |
| meta-ls | gamma_bhb | NPSMBHB | bayes_mean | 4.64 | 4.64181 | 0.00181 | reproduced |
| meta-ls | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.35128 | 0.00128 | reproduced |
| meta-ls | gamma_bhb | NPSMBHB | maxpost | 4.65 | 4.64434 | -0.00566 | reproduced |
| meta-ls | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.29385 | -0.00615 | near-miss |
| meta-ls | gamma_bhb | NPSMBHB | ci68_hi | 5.0 | 4.99382 | -0.00618 | near-miss |
| super | log10_Gmu | NP | bayes_mean | -11.67 | -11.6722 | -0.0022 | reproduced |
| super | log10_Gmu | NP | bayes_sd | 0.32 | 0.31977 | -0.00023 | reproduced |
| super | log10_Gmu | NP | maxpost | -11.94 | -11.937 | 0.003 | reproduced |
| super | log10_Gmu | NP | ci68_lo | -12.08 | -12.08362 | -0.00362 | reproduced |
| super | log10_Gmu | NP | ci68_hi | -11.5 | -11.50542 | -0.00542 | reproduced |
| super | log10_Gmu | NPSMBHB | bayes_mean | -11.68 | -11.68366 | -0.00366 | reproduced |
| super | log10_Gmu | NPSMBHB | bayes_sd | 0.35 | 0.34785 | -0.00215 | reproduced |
| super | log10_Gmu | NPSMBHB | maxpost | -11.96 | -11.973 | -0.013 | reproduced |
| super | log10_Gmu | NPSMBHB | ci68_lo | -12.09 | -12.08843 | 0.00157 | reproduced |
| super | log10_Gmu | NPSMBHB | ci68_hi | -11.49 | -11.49224 | -0.00224 | reproduced |
| super | log10_P | NP | bayes_mean | -2.23 | -2.22677 | 0.00323 | reproduced |
| super | log10_P | NP | bayes_sd | 0.55 | 0.54867 | -0.00133 | reproduced |
| super | log10_P | NP | maxpost | -3.0 | -2.92313 | 0.07687 | reproduced |
| super | log10_P | NP | ci68_lo | -3.0 | -2.99998 | 2e-05 | reproduced |
| super | log10_P | NP | ci68_hi | -2.01 | -2.01319 | -0.00319 | reproduced |
| super | log10_P | NPSMBHB | bayes_mean | -2.21 | -2.20658 | 0.00342 | reproduced |
| super | log10_P | NPSMBHB | bayes_sd | 0.57 | 0.57064 | 0.00064 | reproduced |
| super | log10_P | NPSMBHB | maxpost | -3.0 | -2.90287 | 0.09713 | reproduced |
| super | log10_P | NPSMBHB | ci68_lo | -3.0 | -2.99998 | 2e-05 | reproduced |
| super | log10_P | NPSMBHB | ci68_hi | -1.99 | -1.99276 | -0.00276 | reproduced |
| super | log10_A_bhb | NPSMBHB | bayes_mean | -15.76 | -15.7602 | -0.0002 | reproduced |
| super | log10_A_bhb | NPSMBHB | bayes_sd | 0.46 | 0.46252 | 0.00252 | reproduced |
| super | log10_A_bhb | NPSMBHB | maxpost | -15.7 | -15.71884 | -0.01884 | reproduced |
| super | log10_A_bhb | NPSMBHB | ci68_lo | -16.18 | -16.18582 | -0.00582 | reproduced |
| super | log10_A_bhb | NPSMBHB | ci68_hi | -15.28 | -15.28372 | -0.00372 | reproduced |
| super | gamma_bhb | NPSMBHB | bayes_mean | 4.64 | 4.64401 | 0.00401 | reproduced |
| super | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.34565 | -0.00435 | reproduced |
| super | gamma_bhb | NPSMBHB | maxpost | 4.65 | 4.61485 | -0.03515 | reproduced |
| super | gamma_bhb | NPSMBHB | ci68_lo | 4.3 | 4.31016 | 0.01016 | near-miss |
| super | gamma_bhb | NPSMBHB | ci68_hi | 4.99 | 4.99721 | 0.00721 | near-miss |
| dw-sm | log10_T_star | NP | bayes_mean | -0.73 | -0.732 | -0.002 | reproduced |
| dw-sm | log10_T_star | NP | bayes_sd | 0.21 | 0.20922 | -0.00078 | reproduced |
| dw-sm | log10_T_star | NP | maxpost | -0.79 | -0.787 | 0.003 | reproduced |
| dw-sm | log10_T_star | NP | ci68_lo | -0.96 | -0.95359 | 0.00641 | near-miss |
| dw-sm | log10_T_star | NP | ci68_hi | -0.56 | -0.55454 | 0.00546 | reproduced |
| dw-sm | log10_T_star | NPSMBHB | bayes_mean | -0.65 | -0.65434 | -0.00434 | reproduced |
| dw-sm | log10_T_star | NPSMBHB | bayes_sd | 0.49 | 0.49157 | 0.00157 | reproduced |
| dw-sm | log10_T_star | NPSMBHB | maxpost | -0.78 | -0.771 | 0.009 | reproduced |
| dw-sm | log10_T_star | NPSMBHB | ci68_lo | -0.97 | -0.96441 | 0.00559 | reproduced |
| dw-sm | log10_T_star | NPSMBHB | ci68_hi | -0.51 | -0.50958 | 0.00042 | reproduced |
| dw-sm | log10_alpha_star | NP | bayes_mean | -0.88 | -0.87749 | 0.00251 | reproduced |
| dw-sm | log10_alpha_star | NP | bayes_sd | 0.21 | 0.20702 | -0.00298 | reproduced |
| dw-sm | log10_alpha_star | NP | maxpost | -0.92 | -0.92062 | -0.00062 | reproduced |
| dw-sm | log10_alpha_star | NP | ci68_lo | -1.1 | -1.09528 | 0.00472 | reproduced |
| dw-sm | log10_alpha_star | NP | ci68_hi | -0.71 | -0.7121 | -0.0021 | reproduced |
| dw-sm | log10_alpha_star | NPSMBHB | bayes_mean | -0.87 | -0.86896 | 0.00104 | reproduced |
| dw-sm | log10_alpha_star | NPSMBHB | bayes_sd | 0.32 | 0.31725 | -0.00275 | reproduced |
| dw-sm | log10_alpha_star | NPSMBHB | maxpost | -0.9 | -0.89587 | 0.00413 | reproduced |
| dw-sm | log10_alpha_star | NPSMBHB | ci68_lo | -1.1 | -1.09939 | 0.00061 | reproduced |
| dw-sm | log10_alpha_star | NPSMBHB | ci68_hi | -0.66 | -0.65955 | 0.00045 | reproduced |
| dw-sm | b | NP | bayes_mean | 0.74 | 0.73976 | -0.00024 | reproduced |
| dw-sm | b | NP | bayes_sd | 0.14 | 0.1442 | 0.0042 | reproduced |
| dw-sm | b | NP | maxpost | 0.5 | 0.52344 | 0.02344 | reproduced |
| dw-sm | b | NP | ci68_lo | 0.5 | 0.5 | 0.0 | reproduced |
| dw-sm | b | NP | ci68_hi | 0.83 | 0.82619 | -0.00381 | reproduced |
| dw-sm | b | NPSMBHB | bayes_mean | 0.74 | 0.74254 | 0.00254 | reproduced |
| dw-sm | b | NPSMBHB | bayes_sd | 0.14 | 0.14421 | 0.00421 | reproduced |
| dw-sm | b | NPSMBHB | maxpost | 0.5 | 0.55806 | 0.05806 | reproduced |
| dw-sm | b | NPSMBHB | ci68_lo | 0.5 | 0.5 | 0.0 | reproduced |
| dw-sm | b | NPSMBHB | ci68_hi | 0.83 | 0.83054 | 0.00054 | reproduced |
| dw-sm | c | NP | bayes_mean | 2.01 | 2.0142 | 0.0042 | reproduced |
| dw-sm | c | NP | bayes_sd | 0.7 | 0.70146 | 0.00146 | reproduced |
| dw-sm | c | NP | maxpost | 3.0 | 2.90921 | -0.09079 | reproduced |
| dw-sm | c | NP | ci68_lo | 1.72 | 1.71757 | -0.00243 | reproduced |
| dw-sm | c | NP | ci68_hi | 3.0 | 3.0 | -0.0 | reproduced |
| dw-sm | c | NPSMBHB | bayes_mean | 1.92 | 1.91898 | -0.00102 | reproduced |
| dw-sm | c | NPSMBHB | bayes_sd | 0.74 | 0.73748 | -0.00252 | reproduced |
| dw-sm | c | NPSMBHB | maxpost | 3.0 | 2.90246 | -0.09754 | reproduced |
| dw-sm | c | NPSMBHB | ci68_lo | 1.57 | 1.57158 | 0.00158 | reproduced |
| dw-sm | c | NPSMBHB | ci68_hi | 3.0 | 2.99985 | -0.00015 | reproduced |
| dw-sm | log10_A_bhb | NPSMBHB | bayes_mean | -15.6 | -15.60211 | -0.00211 | reproduced |
| dw-sm | log10_A_bhb | NPSMBHB | bayes_sd | 0.5 | 0.49915 | -0.00085 | reproduced |
| dw-sm | log10_A_bhb | NPSMBHB | maxpost | -15.49 | -15.51549 | -0.02549 | reproduced |
| dw-sm | log10_A_bhb | NPSMBHB | ci68_lo | -16.06 | -16.0549 | 0.0051 | reproduced |
| dw-sm | log10_A_bhb | NPSMBHB | ci68_hi | -15.08 | -15.07939 | 0.00061 | reproduced |
| dw-sm | gamma_bhb | NPSMBHB | bayes_mean | 4.66 | 4.66015 | 0.00015 | reproduced |
| dw-sm | gamma_bhb | NPSMBHB | bayes_sd | 0.35 | 0.35195 | 0.00195 | reproduced |
| dw-sm | gamma_bhb | NPSMBHB | maxpost | 4.67 | 4.66065 | -0.00935 | reproduced |
| dw-sm | gamma_bhb | NPSMBHB | ci68_lo | 4.32 | 4.32887 | 0.00887 | near-miss |
| dw-sm | gamma_bhb | NPSMBHB | ci68_hi | 5.02 | 5.02822 | 0.00822 | near-miss |
| dw-dr | log10_T_star | NP | bayes_mean | -0.98 | -0.97593 | 0.00407 | reproduced |
| dw-dr | log10_T_star | NP | bayes_sd | 0.15 | 0.14505 | -0.00495 | reproduced |
| dw-dr | log10_T_star | NP | maxpost | -0.94 | -0.931 | 0.009 | reproduced |
| dw-dr | log10_T_star | NP | ci68_lo | -1.1 | -1.10305 | -0.00305 | reproduced |
| dw-dr | log10_T_star | NP | ci68_hi | -0.82 | -0.81616 | 0.00384 | reproduced |
| dw-dr | log10_T_star | NPSMBHB | bayes_mean | -0.62 | -0.62305 | -0.00305 | reproduced |
| dw-dr | log10_T_star | NPSMBHB | bayes_sd | 1.37 | 1.36702 | -0.00298 | reproduced |
| dw-dr | log10_T_star | NPSMBHB | maxpost | -0.94 | -0.947 | -0.007 | reproduced |
| dw-dr | log10_T_star | NPSMBHB | ci68_lo | -1.27 | -1.25604 | 0.01396 | near-miss |
| dw-dr | log10_T_star | NPSMBHB | ci68_hi | -0.67 | -0.66265 | 0.00735 | near-miss |
| dw-dr | log10_dNeff | NP | bayes_mean | -0.48 | -0.47976 | 0.00024 | reproduced |
| dw-dr | log10_dNeff | NP | bayes_sd | 0.06 | 0.06201 | 0.00201 | reproduced |
| dw-dr | log10_dNeff | NP | maxpost | -0.41 | -0.4168 | -0.0068 | reproduced |
| dw-dr | log10_dNeff | NP | ci68_lo | -0.49 | -0.49415 | -0.00415 | reproduced |
| dw-dr | log10_dNeff | NP | ci68_hi | -0.41 | -0.40894 | 0.00106 | reproduced |
| dw-dr | log10_dNeff | NPSMBHB | bayes_mean | -0.87 | -0.87427 | -0.00427 | reproduced |
| dw-dr | log10_dNeff | NPSMBHB | bayes_sd | 0.71 | 0.71199 | 0.00199 | reproduced |
| dw-dr | log10_dNeff | NPSMBHB | maxpost | -0.41 | -0.45112 | -0.04112 | reproduced |
| dw-dr | log10_dNeff | NPSMBHB | ci68_lo | -0.63 | -0.63011 | -0.00011 | reproduced |
| dw-dr | log10_dNeff | NPSMBHB | ci68_hi | 0.41 | -0.40894 | -0.81894 | not-reproduced |
| dw-dr | b | NP | bayes_mean | 0.74 | 0.73737 | -0.00263 | reproduced |
| dw-dr | b | NP | bayes_sd | 0.14 | 0.14441 | 0.00441 | reproduced |
| dw-dr | b | NP | maxpost | 0.5 | 0.51806 | 0.01806 | reproduced |
| dw-dr | b | NP | ci68_lo | 0.5 | 0.50003 | 3e-05 | reproduced |
| dw-dr | b | NP | ci68_hi | 0.97 | 0.82396 | -0.14604 | not-reproduced |
| dw-dr | b | NPSMBHB | bayes_mean | 0.74 | 0.74315 | 0.00315 | reproduced |
| dw-dr | b | NPSMBHB | bayes_sd | 0.14 | 0.14405 | 0.00405 | reproduced |
| dw-dr | b | NPSMBHB | maxpost | 0.5 | 0.59906 | 0.09906 | reproduced |
| dw-dr | b | NPSMBHB | ci68_lo | 0.5 | 0.50021 | 0.00021 | reproduced |
| dw-dr | b | NPSMBHB | ci68_hi | 0.83 | 0.83014 | 0.00014 | reproduced |
| dw-dr | c | NP | bayes_mean | 1.95 | 1.94927 | -0.00073 | reproduced |
| dw-dr | c | NP | bayes_sd | 0.68 | 0.68194 | 0.00194 | reproduced |
| dw-dr | c | NP | maxpost | 3.0 | 2.88896 | -0.11104 | near-miss |
| dw-dr | c | NP | ci68_lo | 1.62 | 1.61861 | -0.00139 | reproduced |
| dw-dr | c | NP | ci68_hi | 3.0 | 2.99999 | -1e-05 | reproduced |
| dw-dr | c | NPSMBHB | bayes_mean | 1.83 | 1.82605 | -0.00395 | reproduced |
| dw-dr | c | NPSMBHB | bayes_sd | 0.73 | 0.73442 | 0.00442 | reproduced |
| dw-dr | c | NPSMBHB | maxpost | 3.0 | 2.82281 | -0.17719 | near-miss |
| dw-dr | c | NPSMBHB | ci68_lo | 1.44 | 1.43821 | -0.00179 | reproduced |
| dw-dr | c | NPSMBHB | ci68_hi | 3.0 | 2.9998 | -0.0002 | reproduced |
| dw-dr | log10_A_bhb | NPSMBHB | bayes_mean | -15.33 | -15.32586 | 0.00414 | reproduced |
| dw-dr | log10_A_bhb | NPSMBHB | bayes_sd | 0.65 | 0.64625 | -0.00375 | reproduced |
| dw-dr | log10_A_bhb | NPSMBHB | maxpost | -15.59 | -14.55381 | 1.03619 | not-reproduced |
| dw-dr | log10_A_bhb | NPSMBHB | ci68_lo | -16.03 | -15.75702 | 0.27298 | not-reproduced |
| dw-dr | log10_A_bhb | NPSMBHB | ci68_hi | -14.4 | -14.41751 | -0.01751 | near-miss |
| dw-dr | gamma_bhb | NPSMBHB | bayes_mean | 4.51 | 4.50554 | -0.00446 | reproduced |
| dw-dr | gamma_bhb | NPSMBHB | bayes_sd | 0.39 | 0.39045 | 0.00045 | reproduced |
| dw-dr | gamma_bhb | NPSMBHB | maxpost | 4.52 | 4.52574 | 0.00574 | reproduced |
| dw-dr | gamma_bhb | NPSMBHB | ci68_lo | 4.1 | 4.09269 | -0.00731 | near-miss |
| dw-dr | gamma_bhb | NPSMBHB | ci68_hi | 4.9 | 4.89583 | -0.00417 | reproduced |
