# Blind recount - EPTA DR2 III, Table 2 (common red signal power law)

Paper: EPTA Collaboration & InPTA Collaboration (Antoniadis et al.), "The second data release
from the European Pulsar Timing Array. III. Search for gravitational wave signals",
A&A 678, A50 (2023). Preprint arXiv:2306.16214.

Data: Zenodo record 10.5281/zenodo.8091568, file `chains.zip`, 649471499 bytes,
MD5 `b3180fb1e8560a875fa3de5be001c4aa` - the checksum the Zenodo API prints for the record.
My download matches it (`download/chains.zip.md5sum`). CC BY 4.0, no login needed.

`claims.json` was written and hashed before any of the downloaded data was opened.
SHA-256 `a9908ff122adfbfeb1f98dae1141d04c54080b6123932e328710230b21810628` (`claims.json.sha256`).

## Verdict

**Reproduced.** All six target numbers come back inside the tolerance I froze beforehand, and
so do their asymmetric 90% bounds. One bound in the published table, the lower error on gamma
for ENTERPRISE+GWB in DR2new, misses by 0.02, and I think the table has a typo there rather
than my pipeline being wrong; the reason is below. As a bonus the fourth row
(ENTERPRISE+CURN, DR2new) reproduces too, which I did not have to check.

## The six numbers

| Case | Parameter | Paper (Table 2) | Mine |
|---|---|---|---|
| ENTERPRISE+GWB, DR2full | log10 A_CRS | -14.54 (-0.41, +0.28) | **-14.536 (-0.406, +0.280)** |
| ENTERPRISE+GWB, DR2full | gamma_CRS | 4.19 (-0.63, +0.73) | **4.191 (-0.633, +0.732)** |
| ENTERPRISE+GWB, DR2new | log10 A_CRS | -13.94 (-0.48, +0.23) | **-13.935 (-0.483, +0.233)** |
| ENTERPRISE+GWB, DR2new | gamma_CRS | 2.71 (-0.71, +1.18) | **2.710 (-0.732, +1.184)** |
| ENTERPRISE+CURN, DR2full | log10 A_CRS | -14.53 (-0.44, +0.29) | **-14.528 (-0.439, +0.294)** |
| ENTERPRISE+CURN, DR2full | gamma_CRS | 4.13 (-0.59, +0.80) | **4.127 (-0.590, +0.797)** |

Not asked for, computed anyway as a control:

| Case | Parameter | Paper | Mine |
|---|---|---|---|
| ENTERPRISE+CURN, DR2new | log10 A_CRS | -14.00 (-0.77, +0.28) | -13.997 (-0.769, +0.278) |
| ENTERPRISE+CURN, DR2new | gamma_CRS | 2.91 (-0.87, +1.72) | 2.906 (-0.868, +1.720) |

Burn-in 25% discarded. Full table including the 0% burn-in run and the mode/HPD alternatives:
`out/comparison.txt`; the raw per-chain summaries are the JSON files in `out/`.

Largest central-value miss: 0.005 in log10A, 0.004 in gamma, well inside the 0.02 / 0.05 I
allowed. Largest bound miss: 0.022 in gamma (the DR2new GWB case), inside the 0.10 allowed.

## Where the paper's numbers came from, and how I read them

I did not read Table 2 off a rendered PDF. I pulled the arXiv e-print source
(`paper/2306.16214.tar.gz`), extracted it, and read the `tabular*` environment labelled
`tab:pl` in `eptadr2_gwb_25psr.tex` directly. That removes the step where a typeset
`$-14.54_{-0.41}^{+0.28}$` has to be decoded from an image, which is where this kind of
exercise usually goes wrong.

## Which chain is which row

The release unzips to `chains/{DR2full,DR2new,DR2full+,DR2new+}/<analysis>.tar.gz`, and each
tarball holds a PTMCMC pair: `chain_1.txt` plus `pars.txt`. The mapping is settled by the
parameter names, not by the directory name alone:

- `chains/DR2full/hd_pl` - last two entries of `pars.txt` are `gw_hd_gamma`, `gw_hd_log10_A`.
  `hd` is the Hellings-Downs correlated model, i.e. the GWB row; `pl` is the power law.
  So this is ENTERPRISE + GWB, DR2full.
- `chains/DR2new/hd_pl` - same two names. ENTERPRISE + GWB, DR2new.
- `chains/DR2full/crn_pl` - last two are `gw_crn_gamma`, `gw_crn_log10_A`. `crn` is the common
  uncorrelated red noise. ENTERPRISE + CURN, DR2full.

Two more pieces of corroborating evidence. First, the parameter count differs between the data
sets in the right direction: DR2full chains carry 74 sampled parameters, DR2new 67, which is
what you expect when the shorter data set drops per-pulsar noise components. Second, and more
convincing than any naming argument, the numbers themselves land on the published ones to the
third decimal in all four cases. A wrong assignment would not do that, because DR2full and
DR2new differ by 0.6 in log10A and the CURN and GWB rows differ in their error bars.

The release is ENTERPRISE output throughout; there are no FORTYTWO chains in it, so the
FORTYTWO rows of Table 2 are not checkable from this record. They were not targets anyway.

## What summary statistic the paper quotes

I tested three candidates on every chain rather than assuming one:

- median, with the 5th and 95th percentiles as the bounds (equal-tailed 90%);
- mode (100-bin histogram) with the 90% highest-posterior-density interval;
- mean with 5th/95th.

Only the first reproduces the paper. The clearest discriminator is DR2full GWB gamma: the
published central value is 4.19, my median is 4.191, and my mode is 4.06, off by 0.13, far
outside anything that burn-in or binning choices could explain. The DR2new GWB log10A case
says the same: published -0.48/+0.23, median/percentile gives -0.483/+0.233, mode/HPD gives
-0.416/+0.221. Mean is ruled out too (DR2full GWB log10A mean -14.561 vs published -14.54).

Independent support from the paper's own wording: the caption of Table 3 says "Median optimal
statistic amplitudes ... The uncertainties indicate the 90% credible region", and the ORF
appendix speaks of "central 95 and 99.7 % credible regions". Both point at median plus an
equal-tailed interval, which is what the arithmetic already showed.

## The one number that does not match, and what I ruled out

Table 2 prints gamma = 2.71 (-0.71, +1.18) for ENTERPRISE+GWB in DR2new. I get -0.732.
The 0.022 gap is inside my frozen tolerance, but it is the only bound that moves more than
0.01, so I chased it.

- **Burn-in.** Scanned 0, 5, 10, 15, 20, 25, 30, 40, 50, 60 and 70 percent
  (`out/burnscan_DR2new_hd.txt`). The lower error sits between 0.730 and 0.759 across all of
  them and never reaches 0.71. Burn-in does not explain it.
- **Sampling noise.** A block bootstrap (200 blocks, 400 resamples) of (median minus 5th
  percentile) gives mean 0.730, sd 0.012, 5-95% range 0.711-0.751. So 0.71 sits right at the
  edge of what this chain's own noise would produce: possible but unlikely, and the central
  value and every other bound of this same row land dead on.
- **Wrong chain or wrong column.** Ruled out: the same chain and the same two columns give
  2.710 and +1.184 against the published 2.71 and +1.18.
- **The paper disagreeing with itself.** This is the likely answer. Section 4 of the paper,
  in the sentence quoting the DR2new power-law parameters, and the conclusions both print
  2.71 with a lower error of 0.73. So the paper carries 0.73 twice in prose and 0.71 once in
  the table, and my chain gives 0.732. I read that as a slip in the table, not a disagreement
  about the data.

I flagged this inconsistency in `claims.json` before touching the chains, so it is not a
post-hoc rescue.

## The abstract's fixed-index amplitude

The abstract says that with the spectral index fixed at 13/3, both data sets give
2.5 +- 0.7 times 1e-15 at f = 1/yr. Section 4 states log10 A = -14.61 (-0.12, +0.11) and the
conclusions state -14.61 (-0.15, +0.11); the paper is again slightly inconsistent with itself.

The release contains no fixed-gamma run, so I could not repeat that analysis. But Section 4
says the number comes from slicing the posterior at gamma = 13/3, which I can do with the
released power-law chains (`scripts/slice13over3.py`, results in `out/slice13over3.json`):

| Slice | log10 A (median, 90%) | A / 1e-15 (median, 90% range) |
|---|---|---|
| DR2full GWB, abs(gamma - 13/3) < 0.05 | -14.603 (-0.118, +0.102) | 2.50 (1.90 - 3.16) |
| DR2full GWB, abs(gamma - 13/3) < 0.10 | -14.600 (-0.125, +0.110) | 2.51 (1.88 - 3.24) |
| DR2new GWB, abs(gamma - 13/3) < 0.10 | -14.612 (-0.164, +0.126) | 2.44 (1.68 - 3.26) |
| DR2full CURN, abs(gamma - 13/3) < 0.10 | -14.624 (-0.127, +0.110) | 2.38 (1.77 - 3.06) |

So: amplitude 2.4 to 2.5 times 1e-15 with a 90% range of roughly 0.6 to 0.8, against the
abstract's 2.5 +- 0.7. Reproduced. The two data sets do give the same answer, as claimed.
The slice also resolves the paper's internal inconsistency: DR2full gives -0.12 on the lower
side (Section 4's number) and DR2new gives -0.16 (close to the conclusions' -0.15). Both
round to "around -14.61".

This is a conditional slice, not a run with gamma held fixed in the sampler. Those are not the
same thing in general: a fixed-gamma run explores the amplitude at exactly 13/3 with the full
prior weight, while a slice reweights nothing and throws away all but a few percent of the
samples (794 of 22493 at the tightest slice for DR2full, 169 for DR2new). The numbers agree
well enough that the distinction does not matter here, but it is a judgement call and it is
the weakest link in this report.

## What I could not check

- **The FORTYTWO rows of Table 2.** The release contains only ENTERPRISE chains.
- **A genuine fixed gamma = 13/3 run.** Not in the release; substituted a posterior slice.
- **Whether the released chains are byte-for-byte the ones used to typeset the table.** The
  release ships no provenance file, no sampler configuration, no record of what burn-in or
  thinning the authors applied. The chains are 29990 rows each and already effectively
  post-burn-in: the log-posterior over the first 50 samples is within about 400 of the
  long-run value, and discarding 0% and 25% gives the same answer to 0.005. So the published
  numbers are insensitive to that choice. But I cannot prove the authors used these files.
- **Anything upstream of the chains**: the timing data, the noise models, the likelihood.
  This is a recount of the authors' posterior samples, not a re-analysis from the TOAs.

## Judgement calls

1. Treating the slice at gamma near 13/3 as a stand-in for a fixed-index run.
2. Choosing 25% burn-in as the headline, with 0% reported alongside. Both give the same
   answer, so nothing turns on it.
3. Reporting the DR2new gamma lower bound against Table 2's -0.71 rather than the prose's
   -0.73. Against the prose value my -0.732 is exact.
4. Judging the summary statistic empirically rather than taking the caption of Table 3 at its
   word. They agree, so this cost nothing, but it was the right order.

## Files

- `claims.json`, `claims.json.sha256` - frozen before the data was opened.
- `zenodo_record.json` - Zenodo metadata, including the published checksum.
- `download/chains.zip`, `download/chains.zip.md5sum` - the release and my verification of it.
- `extracted/` - unpacked archives. Untouched data; nothing was written back into it.
- `paper/` - the arXiv e-print tarball and its extracted LaTeX, source of the published numbers.
- `scripts/summarise.py` - per-chain summary statistics (median, mean, mode, percentiles, HPD).
- `scripts/compare.py` - side-by-side comparison against the published values.
- `scripts/slice13over3.py` - conditional amplitude at gamma = 13/3.
- `scripts/burnscan.py` - burn-in sensitivity and block bootstrap of the contested bound.
- `out/` - machine-readable results: `comparison.txt`, `slice13over3.json`,
  `burnscan_DR2new_hd.txt`, `burnin_check.txt`, and the eight per-chain JSON summaries.
- `venv/` - the Python 3.12 environment (numpy 2.5.5) used for everything above.

Boundary: I did not open `2023-antoniadis-epta-dr2` (the non-blind folder), `fila.md`,
`log.md`, `triagem-2026-11-18/` or anything under `E:\Ciencia\paper-rerun`. All work happened
inside this folder.

Nothing was published, committed, pushed or sent. Everything stayed on this machine.
