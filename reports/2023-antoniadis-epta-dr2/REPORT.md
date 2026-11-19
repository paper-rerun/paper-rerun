# EPTA DR2 III — recount of the published posterior summaries

- Date: 2026-11-18

**Verdict on the frozen claims: Partially reproduced.** Seventeen of the eighteen numbers
land inside the band. The one that misses is the lower bound of the spectral index in
DR2new — and we now know why: **Table 2 misprints it.** The paper's own text gives
γ = 2.71 (+1.18/−0.73) twice, the released chain gives −0.732, and only Table 2 says −0.71.

Three things came out of this run that are worth more than the verdict:

1. **Table 2, ENTERPRISE + GWB, DR2new: the printed γ lower bound is wrong.** The body and
   the conclusions of the same paper both print −0.73. The chain agrees with the text, not
   with the table.
2. **Table A.1 is a 68% credible region under a caption that says 90%.** All eight
   ENTERPRISE numbers in it match our 68% equal-tailed bounds to within 0.005, and the
   best-fitting level is 67.5% to 68.8% on every one. At 90% they are too narrow by 0.11 to
   0.82.
3. **The DR2new ORF rows of Table 2 match no standard level.** The best fit is 85% to 87%,
   and the binned-ORF row is off by 0.157 on a bound and 0.022 on a median. We have no
   explanation for these three rows.

| Claim | Quantity | Ours | Paper (Table 2) | Δ median | Δ upper | Δ lower |
|---|---|---|---|---|---|---|
| C1 | log₁₀A, ENTERPRISE + GWB, DR2full | −14.5357 (+0.2802 / −0.4064) | −14.54 (+0.28 / −0.41) | +0.0043 | +0.0002 | −0.0036 |
| C1 | γ, same | 4.1914 (+0.7324 / −0.6330) | 4.19 (+0.73 / −0.63) | +0.0014 | +0.0024 | +0.0030 |
| C2 | log₁₀A, ENTERPRISE + GWB, DR2new | −13.9353 (+0.2329 / −0.4831) | −13.94 (+0.23 / −0.48) | +0.0047 | +0.0029 | +0.0031 |
| C2 | γ, same | 2.7103 (+1.1835 / −0.7322) | 2.71 (+1.18 / −0.71) | +0.0003 | +0.0035 | **+0.0222** |
| C3 | log₁₀A, ENTERPRISE + CURN, DR2full | −14.5278 (+0.2939 / −0.4391) | −14.53 (+0.29 / −0.44) | +0.0022 | +0.0039 | −0.0009 |
| C3 | γ, same | 4.1273 (+0.7969 / −0.5898) | 4.13 (+0.80 / −0.59) | −0.0027 | −0.0031 | −0.0002 |

Band as frozen: 0.01 on a median, 0.02 on a credible bound. The verdict follows the rule as
frozen, and the rule compares against Table 2. Against the value the paper's prose gives,
the same number is exact.

## What this run is, and what it is not

It is a recount. The EPTA published their MCMC chains, we read them and recomputed the
summary statistics that go into Table 2 and Table A.1. We did not re-run ENTERPRISE, we did
not re-run the Bayesian search, and we did not touch the timing data. Agreement here says
the summarising step is right. It says nothing about whether the inference behind it is
right. Same shape as the NANOGrav 15 yr rerun of 09/11, same ceiling.

## Finding 1 — the misprinted bound

Table 2 gives ENTERPRISE + GWB on DR2new as γ = 2.71 (+1.18 / **−0.71**). Our recount gives
2.7103 (+1.1835 / **−0.7322**), which rounds to −0.73.

The paper says −0.73 itself, in two places. From the arXiv LaTeX source of 2306.16214:

- Section 4 (`eptadr2_gwb_25psr.tex:455`): `$\gamma = 2.71_{-0.73}^{+1.18}$`
- Conclusions (`:868`): `$\gamma = 2.71_{-0.73}^{+1.18}$`
- Table 2 (`:357`, tabular `tab:pl`): `$2.71_{-0.71}^{+1.18}$`

So the released chain reproduces the paper. One digit in one cell of Table 2 does not match
the rest of the paper, and that single cell is the whole of our frozen failure. Everything
else in Table 2's ENTERPRISE rows for DR2full and DR2new, ORF rows aside, reproduces to
within 0.005.

This was found by the blind recount, which read the LaTeX source rather than a rendered PDF;
we confirmed it independently from our own `pdftotext` extraction, where the prose and the
conclusions both decode to −0.73 and the table to −0.71.

An earlier draft of this report spent three sections hunting for a processing choice that
would turn 0.732 into 0.71 — burn-in, percentile convention, HPD versus equal-tailed, and,
after the adversarial review, thinning. All four were eliminated or shown not to explain it
(`runs/logs/processing_scan.log`, `interval_shape.log`, `thinning_scan.log`). They were
eliminated because there was nothing to find: the number was never ours to recover.

## Finding 2 — Table A.1 quotes 68%, not 90%

Its caption reads "90% credible regions for the constraints of power law parameters in the
different Bayesian analyses with DE440 for both DR2full+ and DR2new+". Recounting the four
ENTERPRISE cells it contains at 90% gives bounds far wider than print, on all eight numbers,
always in the same direction. At 68% they match (`runs/logs/credible_level.log`):

| Cell | Quantity | Paper | Ours at 90% | Ours at 68% |
|---|---|---|---|---|
| DR2full+ CURN | log₁₀A | +0.17 / −0.20 | +0.276 / −0.361 | +0.169 / −0.202 |
| DR2full+ CURN | γ | +0.40 / −0.37 | +0.680 / −0.609 | +0.397 / −0.369 |
| DR2full+ GWB | log₁₀A | +0.18 / −0.20 | +0.285 / −0.351 | +0.180 / −0.197 |
| DR2full+ GWB | γ | +0.39 / −0.40 | +0.669 / −0.654 | +0.393 / −0.405 |
| DR2new+ CURN | log₁₀A | +0.33 / −0.52 | +0.471 / −0.934 | +0.327 / −0.520 |
| DR2new+ CURN | γ | +1.12 / −0.84 | +1.931 / −1.242 | +1.117 / −0.835 |
| DR2new+ GWB | log₁₀A | +0.25 / −0.44 | +0.368 / −0.820 | +0.254 / −0.436 |
| DR2new+ GWB | γ | +1.02 / −0.67 | +1.838 / −1.011 | +1.018 / −0.673 |

Scanning the equal-tailed level that best fits each printed pair, every one of the eight
lands between 67.5% and 68.8%, median 68.1%. For comparison the same scan puts the non-ORF
rows of Table 2 at exactly 90.0%. Eight numbers do not land on 68% by accident.

The four medians of Table A.1 reproduce to within 0.005, so the chains are the right ones
and the analysis behind them is fine. It is the interval that is labelled wrong. A reader
comparing Table 2 with Table A.1 is comparing a 90% region with a 68% one and would
conclude, wrongly, that adding the InPTA data tightened the constraint by about 40%.

## Finding 3 — the DR2new ORF rows match nothing standard

The three ORF rows of Table 2 in the DR2new column do not reproduce, and unlike Finding 2
there is no level that fixes them:

| Chain → row | Δ median log₁₀A | Δ bounds log₁₀A | Δ median γ | Δ bounds γ | best level |
|---|---|---|---|---|---|
| `bin_b10_orf` → Binned ORF | −0.0137 | +0.0128 / +0.0721 | +0.0215 | +0.1566 / +0.0566 | 85.2% |
| `chebyshev_orf` → Chebyshev ORF | −0.0081 | +0.0040 / +0.0351 | +0.0137 | +0.0892 / −0.0105 | 87.5% |
| `legendre_orf` → Legendre ORF | −0.0019 | −0.0042 / +0.0100 | +0.0075 | −0.0055 / +0.0192 | — |

Two of those medians would fail even the strict median band. The same three ORF chains in
DR2full reproduce to within 0.005 on all twelve numbers, so it is not the ORF machinery and
not our reading of those chains. It is specific to the DR2new column. 85% and 87% are not
levels anyone quotes, so the likeliest reading is that these three cells were produced from
a different run than the one in the release — but we cannot show that, and we are not going
to guess further.

Unlike Findings 1 and 2, this one has no second source in the paper: the ORF numbers appear
in Table 2 and nowhere else.

## Everything the release let us check

`scripts/survey_all_cells.py`, `runs/logs/survey_all_cells.log`: fourteen ENTERPRISE cells,
84 numbers. 25 of the 28 medians are within 0.005 of print; the 3 that are not are the
DR2new ORF rows of Finding 3. Of the 56 bounds, 22 fall outside the 0.02 band — 8 of them
are Table A.1 (Finding 2), 7 are the DR2new ORF rows (Finding 3), 1 is the misprint
(Finding 1), and the remaining 6 are in the DR2new ORF block as well.

The frozen claims picked three cells out of fourteen, and they were the quiet ones. The
adversarial review is what forced the survey, and the survey is where Findings 2 and 3 came
from. `crn_pl` in DR2new — six numbers, all within 0.004 — was available to the frozen
claims and we did not take it.

## The data

One file, `chains.zip`, 649.5 MB, Zenodo 10.5281/zenodo.8091568, CC BY 4.0, no login and no
terms to accept. Our md5 matches the one the Zenodo record prints,
`b3180fb1e8560a875fa3de5be001c4aa`. Inside are 28 tarballs under DR2full, DR2new, DR2full+
and DR2new+, the `+` meaning the InPTA data is included, and a `file_list.txt` that is a
directory tree and nothing else. No legend, no README, no note of which software or which
ephemeris produced which chain.

From `runs/logs/release_inventory.log`, three things worth knowing before reading anyone's
summary of this release: the four `os.tar.gz` hold no chain at all, only optimal-statistic
output; the free-spectrum chains have 50 frequency bins in DR2full and DR2full+ but 20 in
DR2new and DR2new+; and chain length is not uniform — most are 29,990 samples, DR2full+/hd_pl
is 34,420 and DR2new+/hd_pl is 44,190.

## Mapping each chain to its row

The triage expected this to be the hard part. It splits into two axes and the files settle
only one.

**The model axis is settled from inside the files.** Each tarball is a PTMCMCSampler pair,
`chain_1.txt` plus `pars.txt`, the sampled parameters in the order of `pars.txt` and then
four extra columns. The parameter names say what the common signal is: `hd_pl` carries
`gw_hd_log10_A` and `gw_hd_gamma`, Hellings–Downs correlated, the **GWB** row; `crn_pl`
carries `gw_crn_*`, common uncorrelated red noise, the **CURN** row; the ORF chains carry
`gw_bin_orf_*`, `gw_chebyshev_orf_*` and `gw_legendre_orf_*` beside their basis
coefficients. The mapping does not rest on reading `pl` as "power law".

**The data-set axis is not.** It comes from the directory name. We checked whether the
parameter lists could tell DR2full from DR2full+: they cannot. Both `hd_pl` chains carry the
same 74 parameters, and the only difference in the whole list is that DR2full models
J1600−3053 with a chromatic Gaussian process and DR2full+ with plain red noise. Nothing says
which of those is the InPTA-inclusive set. The medians back the directory names up — every
`+` cell reproduces its Table A.1 median to 0.005 — but that is a consistency check after
the fact, not an identification from the file. The same gap applies to the ephemeris: both
tables are explicitly the DE440 analysis and nothing in the zip names an ephemeris.

Every number here was read by parameter name, never by column index, which matters because
each of the 25 pulsars in the model also has a parameter whose name ends in `log10_A`.

What the release does not let us check at all: both tables have a FORTYTWO row beside every
ENTERPRISE row, and nothing in the zip identifies a chain as FORTYTWO.

## The abstract's fixed-index amplitude

(2.5 ± 0.7) × 10⁻¹⁵ at a reference frequency of 1 yr⁻¹ with the spectral index fixed at
13/3. We froze this as a secondary claim and reported it as not checkable, because the
release has no fixed-γ run: every power-law chain samples γ and the `fs` chains are free
spectra. The blind recount took a different view and sliced the posterior at |γ − 13/3| <
0.05, getting A = 2.50 × 10⁻¹⁵ for DR2full and 2.44 × 10⁻¹⁵ for DR2new, consistent with the
abstract. That is a reasonable thing to do and it agrees, but a conditional slice of a
sampled posterior is not the same object as a fit with the index held fixed, and the
tightest slice keeps 794 of 22,493 samples. We leave the claim as not checkable and record
the slice as supporting, not as a reproduction.

## A caveat about our own band

The tolerance we froze is tighter than these chains support (`runs/logs/tail_noise.log`).
Each of the three frozen chains is 29,990 samples, but the integrated autocorrelation time
of the post-burn-in portion runs from 12.9 to 27.5, so the effective sample size is 819 to
1,738. Resampling in blocks longer than the autocorrelation length moves the quantiles by:

| | p5 | median | p95 |
|---|---|---|---|
| C1 log₁₀A | 0.0133 | 0.0043 | 0.0050 |
| C1 γ | 0.0139 | 0.0087 | 0.0202 |
| C2 log₁₀A | 0.0349 | 0.0044 | 0.0036 |
| C2 γ | 0.0119 | 0.0111 | 0.0695 |
| C3 log₁₀A | 0.0148 | 0.0045 | 0.0043 |
| C3 γ | 0.0115 | 0.0100 | 0.0222 |

The upper bound of γ in DR2new is determined to ±0.07 by resampling and we matched it to
0.0035. That is luck. A 0.02 band on a tail quantile of a chain with 1,035 effective samples
was not much of a test, and this report says so rather than taking credit for eleven passes.
The medians are a different story: a 0.01 band against a bootstrap spread of 0.004 to 0.011
is a real test, and 25 of 28 medians across the whole survey pass it.

One more asymmetry, raised by the adversarial review and worth stating. We described the
medians as passing "with 0.005 to spare", which is exactly the rounding slack a two-decimal
figure carries — slack we granted the medians in the reasoning and never granted the bounds.
Finding 1 makes the point moot for the one failure, but the rule as frozen was uneven.

## Where the run departed from the frozen route

`claims.json` says the route drops "the burn-in the chain file itself declares (or the first
25% if it declares none)" and applies "sample weights if the file carries them".
`recount.py` cuts 25% flat and never looks for either. The result is right — the files
declare no burn-in and carry no weights — but that is a finding the run should have stated,
not a default it should have assumed.

The frozen self-check about refusing to summarise a chain with fewer than 10,000
post-burn-in samples lived only in `summarise.py`, a generic helper written before the
layout was known. That file matched parameters by substring and would have returned a
pulsar's `log10_A` under the label `log10_A`, the opposite of the guarantee above. It
produced none of the numbers in this report and has been deleted.

## Files

```
claims.json                  the three claims, the route, the band; frozen before any data was read
claims.sha256                still matches at the end of the run
data/README.txt              where the release is, and why it is not in this repository
data/file_list.txt           the tree that ships inside the zip
scripts/recount.py           the three frozen cases
scripts/survey_all_cells.py  all fourteen ENTERPRISE cells of Table 2 and Table A.1
scripts/credible_level.py    which credible level each printed pair actually corresponds to
scripts/interval_shape.py    equal-tailed against HPD
scripts/tail_noise.py        autocorrelation, effective sample size, block bootstrap
scripts/processing_scan.py   burn-in and percentile-method scan
scripts/thinning_scan.py     thinning scan, and the arithmetic of the rounding band
scripts/release_inventory.py what is actually in the 28 tarballs
runs/logs/                   one log per script, plus table2_check.log
runs/out/                    results.json, survey_all_cells.json, credible_level.json
REVIEW.md, review/           the adversarial review, its scripts and its logs
blind/                       the independent blind recount: its own frozen claims, code,
                             outputs and report, run as `2023-antoniadis-epta-dr2-cego`
```

Not in this repository: the 649.5 MB release and the 165 MB it unpacks to, the arXiv source
and the rendered paper, and the two Python environments. `data/README.txt` says where the
release is; the scripts read the tarballs straight out of the zip, so they run as they stand
once it is downloaded.

## Provenance

Targets were taken from Table 2 and Table A.1 of arXiv 2306.16214, read from the ar5iv HTML
and, after Finding 1, checked against the arXiv LaTeX source, where they agree on all
sixteen ENTERPRISE cells. They were not read from `pdftotext`, and
`runs/logs/table2_check.log` says why: `pdftotext -layout` shifts the row labels of Table 2
by one against their values, so a careless read hands −14.47 to FORTYTWO + GWB when it
belongs to ENTERPRISE + Binned ORF, and it interleaves superscript with subscript character
by character, to the point that the first row's digits admit +0.29/−0.44 and +0.49/−0.24
equally. The DESI DR2 run was bitten by the same class of bug in its Table III.

`claims.json` was frozen at the timestamp in `claims.frozen_at.txt` with SHA-256
`07aef135…c12e95`, before the zip finished downloading and before anything in it was read.
The hash still matches.

Environment: Python 3.12.10 with numpy 2.4.6 in `env/venv2`. The DESI venv could not be
reused — it was built under WSL and its `bin/python` does not run from the Windows side.

**Adversarial review** by a second agent: `REVIEW.md`. Three blockers and four corrections,
all applied. Its numbers, recomputed with its own code, agree with ours on all eighteen. It
forced the survey that produced Findings 2 and 3, and it caught an arithmetic slip of its
own on the way, which this report does not repeat.

**Blind recount** by a third agent that never saw any of this work, in
`../2023-antoniadis-epta-dr2-cego`. It froze its own claims file, downloaded the release
itself, mapped the chains on its own evidence, and determined empirically that the summary
statistic is the median with equal-tailed 5th and 95th percentiles before reading the
captions that confirm it. Its six numbers match ours to every digit we both printed, it
reproduced the DR2new CURN cell as a free control, and it is the one that found Finding 1.
Its one judgement call we did not adopt is the γ = 13/3 slice above.

Still outstanding: a human reading. Nothing here has been published, and the three findings
above have not been reported to the authors.
