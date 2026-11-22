# Pre-registration — blind recount of Table 4, Afzal et al. 2023 (ApJL 951, L11)

Written 2026-11-21, before any chain file was opened. Frozen by sha256 (see FREEZE.txt).

Paper: Afzal et al., "The NANOGrav 15 yr Data Set: Search for Signals from New Physics",
ApJL 951, L11 (2023), arXiv:2306.16219. LaTeX source unpacked into `arxiv-src/`.

Target: the longtable labelled `tab:list`, printed as Table 4 — "Bayesian Estimators,
Maximum Posterior Values, and 68% Credible Intervals for the Parameters of the
New-physics Models".

## 1. What I will test

Every cell of Table 4, extracted mechanically from `arxiv-src/main.tex` by
`scripts/parse_table4.py` into `out/table4_printed.json` (71 parameter rows,
15 models). That JSON is the frozen record of the printed values; its sha256 is in
FREEZE.txt. The 15 models and their row counts:

igw 5, sigw-delta 4, sigw-gauss 5, sigw-box 5, pt-bubble 8, pt-sound 8,
stable-c 3, stable-k 3, stable-m 3, stable-n 3, meta-l 4, meta-ls 4, super 4,
dw-sm 6, dw-dr 6.

Per row the table prints up to 7 cells: Bayes estimator (NP), Bayes estimator
(NP+SMBHB), maximum posterior (NP), maximum posterior (NP+SMBHB), 68% credible
interval (NP), 68% credible interval (NP+SMBHB), K bound. The two SMBHB rows of each
model (log10_A_bhb, gamma_bhb) print `...` in the NP columns by construction — those
are not cells, they are blanks. Counting only cells that print a number:

- Bayes estimator NP: 41 cells (each carries a mean and a standard deviation)
- Bayes estimator NP+SMBHB: 71 cells (mean + sd)
- Maximum posterior NP: 41 cells
- Maximum posterior NP+SMBHB: 71 cells
- 68% credible interval NP: 41 cells (each carries two edges)
- 68% credible interval NP+SMBHB: 71 cells (two edges)
- K bound: 6 numeric cells (igw n_t = 5.72; stable-c -9.67; stable-k -9.87;
  stable-m -10.10; stable-n -9.71; super -9.97); every other K-bound cell prints
  `...` or `---`.

Total 336 numeric cells to be tested + 6 K-bound cells declared in advance as
**not checkable from posterior chains** (see §4).

## 2. The paper's own definitions (Appendix A, around main.tex lines 958-978)

The paper states, verbatim in substance:

- Bayes estimator: `<theta> = int dtheta theta P(theta|D,H)`, variance
  `sigma^2 = <theta^2> - <theta>^2`; and then: *"In practice, in a given analysis and
  for a given chain of MCMC samples, we compute the Bayes estimator and its standard
  deviation in terms of the corresponding sample mean and sample variance."*
- Maximum posterior estimator: the theta where the 1D marginalized posterior
  `P(theta|D,H)` reaches its global maximum across the predefined prior range.
- 68% credible interval `[theta_68_min, theta_68_max]`: integrating the posterior over
  the regions of highest posterior density such that the integral returns 0.68, with
  `P(theta|D,H) > P_68` for all theta inside. I.e. a highest-posterior-density (HPD)
  interval, not an equal-tailed quantile interval.
- K bound: `K(theta_K) = P(D|theta_K,H)/P(D|theta_0,H) = 1/10`, a **likelihood** ratio,
  explicitly "not defined in terms of a posterior probability distribution".
- Values marked `*` are at the boundary of the prior range (prior ranges are in
  Table 3, `tab:np_priors`, which I have read and recorded in `out/priors.json`).

## 3. How I will compute each quantity — decided now, not after seeing the numbers

Chains: `E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics\extraido\chains\stochastic\`.
`<model>.pkl.gz` is the NP analysis, `<model>_bhb.pkl.gz` is NP+SMBHB. The paper's
`dw-dr` is the deposit's `dw_ds` (the prior table calls the same model `dw-ds`).
There is also a `compare/` subdirectory holding a near-duplicate set with no `dw`
models; I will use the top-level files as primary and, for one model, check whether
`compare/` would give the same answer.

Loading: gzip + a `pickle.Unpickler` subclass whose `find_class` allows only the
handful of numpy names needed to rebuild an ndarray
(`numpy.core.multiarray._reconstruct`, `numpy._core.multiarray._reconstruct`,
`numpy.ndarray`, `numpy.dtype`) and raises on anything else. `pickle.load` is never
called on a downloaded file. The internal layout of the files is unknown at freeze
time; the mapping from paper symbol to chain column will be recorded in REPORT.md.

Samples: all samples as deposited, in file order, no extra burn-in, no thinning. If
the deposit itself carries a burn-in marker I will use it and say so. If the printed
numbers miss badly with the full array, I will additionally try discarding the first
25% as a diagnostic and report that separately as a secondary, post-hoc test — not as
the primary verdict.

**Bayes estimator**: `numpy.mean` of the parameter column. **Standard deviation**:
`numpy.std(ddof=0)`. I will also compute `ddof=1`; with chains of millions of samples
the two cannot differ at the printed precision, and if they do I will report it.

**68% credible interval (primary)**: the shortest contiguous interval containing 68%
of the samples — sort the column, and over `i` minimise `x[i+k]-x[i]` with
`k = round(0.68*n)`; report `[x[i], x[i+k]]`. For a unimodal posterior this is the HPD
interval the paper defines. **Secondary**: a level-set interval from the smoothed
density of §below — the min and max of `{theta : p(theta) > p_68}` where `p_68` is the
threshold enclosing 0.68 of the mass. Both are reported; the primary decides the
verdict.

**Maximum posterior**: a 1D density estimate is unavoidable and the paper does not say
which one it used, so this check is soft by construction. Primary estimator: bin the
column into 4000 equal bins over the prior range from Table 3, convolve with a
Gaussian kernel of bandwidth `h = sigma * n**(-1/5)` (Scott's rule; scipy is not
installed on this machine, so the KDE is done by binning + convolution with numpy),
evaluate on the bin centres, take the argmax. Secondary: the same with a fixed
`h = 0.02 * (prior range)`. Boundary cells (printed `X^*`) count as reproduced if the
argmax falls in the outermost 2% of the prior range on the correct side.

**Random subsampling**: none for mean, sd or the primary interval (full column). None
needed for the density either, since binning is linear in n.

## 4. Declared not checkable, in advance

- The 6 numeric **K bound** cells. K is a likelihood ratio at a fixed parameter value
  against the reference `theta_0`, computed outside the posterior; a posterior sample
  chain does not contain it. Unless the deposited files turn out to carry per-sample
  likelihoods *and* the reference point, I cannot recount these, and I will say so
  rather than guess.
- Anything whose chain file is absent, unreadable under the restricted unpickler, or
  whose parameter column I cannot map to the paper's symbol with confidence.

## 5. Tolerance — decided now

Let `d` be the number of decimals the table prints for that cell (2 for almost
everything; 1 for `meta-l` NP+SMBHB `-5.9 +- 1.2`; and `0.5`, `1`, `3`, `5` are printed
as prior-boundary markers).

- **reproduced**: `|mine - printed| <= 0.6 * 10^-d` (i.e. <= 0.006 at 2 dp,
  <= 0.06 at 1 dp). This is the rounding half-width plus a small allowance.
- **near miss**: `|mine - printed| <= 3 * 10^-d` (<= 0.03 at 2 dp). Reported as a
  miss, with the size of the gap.
- **not reproduced**: anything larger.
- **maximum posterior** only: reproduced if `|mine - printed| <= 0.1`, or if the
  printed value is a prior boundary and my argmax lands in the outermost 2% of the
  prior range on that side. A separate, looser band because the density estimator is
  not specified by the paper.
- An interval cell counts as reproduced only if **both** edges do.
- A Bayes cell counts as reproduced only if **both** mean and sd do.

## 6. Known oddity in the printed table, noted before computing

`dw-dr`, `log10 Delta N_eff`, 68% CI under NP+SMBHB prints `[-0.63, 0.41^*]`. The
prior range for that parameter is log-uniform `[-3, -0.41]`, so a positive `0.41` is
outside the prior; this is almost certainly a dropped minus sign in the paper. I will
test it against `-0.41` and record both verdicts.

## 7. Output

`out/measured.json` (raw numbers), `out/comparison.csv` (cell by cell), `REPORT.md`
(verdicts and reasons). Nothing is published anywhere; files on disk only.
