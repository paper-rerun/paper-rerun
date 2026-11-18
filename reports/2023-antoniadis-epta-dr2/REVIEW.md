# Adversarial review — 2023-antoniadis-epta-dr2

Reviewed 18/11. Everything below was recomputed with my own code, reading the tarballs
straight out of `data/chains.zip` in memory, never through `scripts/`. My scripts and logs
are in `review/`. Nothing else in the folder was touched.

Verdict on the verdict: "Partially reproduced" is the right label and the frozen rule was
not bent. Three things must change before the report goes out, and four more are wording.

---

## B1 (blocker). "No processing choice we have access to moves it there" is not true

The report rules out burn-in fraction and percentile method, then says no processing choice
reaches 0.71. Those are two knobs, not all of them. Thinning is a third, it lives entirely
inside the published file, and it reaches the printed value (`review/log_thin.txt`,
`review/thin_detail.py`):

```
k= 7  n= 3214  lower bound from 0.6998 to 0.7503   1 phase of 7 inside 0.705..0.715
k=10  n= 2250  lower bound from 0.7106 to 0.7462   1 phase of 10 inside
k=12  n= 1875  lower bound from 0.7063 to 0.7621   4 phases of 12 inside
```

I am not arguing the authors thinned by 10. The point is narrower and the report has to
make it: the eliminations cover the burn-in fraction and the interpolation rule, and the
bound is stable against both. Written as "no processing choice", it claims a search that
was never run. Say instead that neither of the two knobs available on the full file moves
it, and that thinning does — which is itself a hint about what the gap is.

I also tested a fourth route the report did not consider: quantiles off a Gaussian-KDE CDF
instead of off the samples (`review/log_kde.txt`). It is worse — summed over the twelve
bounds, 0.1115 against 0.0490 for the raw percentile. That one is a clean elimination and
deserves a line, because it closes the obvious "but papers plot smoothed posteriors"
objection.

## B2 (blocker). The report contradicts itself on whether this is the authors' sample, and omits the arithmetic that defuses the failure

Two sentences, four paragraphs apart:

- "the chain in the release is not byte for byte the sample the authors summarised"
- "we read the same samples the authors read, so our quantile and theirs should agree
  deterministically"

Both cannot stand. The second is the premise for chasing processing knobs; the first is the
conclusion the report reaches. As written the reader gets the drama of an unexplained
disagreement and no way to size it. The sizing is easy and the report already holds the
pieces:

- The paper prints median 2.71 and −0.71. Rounding alone allows a true lower bound anywhere
  in 0.705 to 0.715. We get 0.7322, so the distance to the nearest value consistent with
  print is **0.0119**, not 0.022.
- The report's own block bootstrap gives sd 0.0119 on that quantile. The gap is **1.0 sd**.
  Running a moving-block bootstrap on the bound statistic itself
  (`review/log_noise_check.txt`) gives sd 0.0126 and P(bound ≤ 0.715) = 0.11.
- The frozen band is asymmetric in its own reasoning: `claims.json` gives the median band
  0.005 of rounding slack plus 0.005 of noise, and gives the bound band no rounding slack at
  all. With the same allowance the single failure passes. The rule is the rule and I am not
  asking to move it after the fact — I am asking the report to tell the reader that the one
  failure sits 0.0022 outside a band drawn without the allowance its sibling band got.

Resolution I would accept: keep "Partially reproduced", drop the "deterministic" sentence,
state plainly that the published chain is evidently not the summarised one, and present the
gap as one bootstrap sd from the printed rounding window rather than as a residue nothing
explains.

## B3 (blocker). The mapping argument is tighter than the files allow, and the `claims.json` self-check was not honoured as written

The mapping is **correct** — I verified it numerically, see "What held up" — but the
argument the report gives covers half of it.

`pars.txt` settles the *model* axis: `gw_hd_*` is HD-correlated, `gw_crn_*` is the
uncorrelated common signal. It does not settle the *dataset* axis. DR2full and DR2full+ have
the same 74 parameters in both `hd_pl` and `crn_pl`; the only difference anywhere in those
files is that one pulsar's noise term is `J1600-3053_chrom_gp_*` in DR2full and
`J1600-3053_red_noise_*` in DR2full+ (`review/tarscan.py`). Nothing in the release says which
of the two is the InPTA-inclusive run. So "settled from inside the files rather than from
their names" is wrong: full vs new vs + rests on the directory name in the zip and on nothing
else. Self-check 2 of `claims.json` says a chain whose row cannot be established from the file
itself is reported unmapped and not used. Read strictly, all three chains fail it. Either the
report says the dataset axis comes from the path and the numbers confirm it, or the
self-check has to be restated.

Same gap on a second axis: Table 2 is explicitly the **DE440** analyses ("...in the different
Bayesian analyses with DE440 for both DR2full and DR2new"). Nothing in the zip names an
ephemeris, and the report never mentions DE440. The reader deserves that caveat: we assume
the released chains are the DE440 ones, and the agreement of the medians is the only
evidence for it.

## C1 (correction). Four more rows were checkable here and were not checked, and one of them breaks "whatever it is, it is small"

The report notes the release lines up with the ENTERPRISE rows, then claims three of them.
The other ENTERPRISE cells of Table 2 are all in the zip: `crn_pl` under DR2new, and
`bin_b10_orf` / `chebyshev_orf` / `legendre_orf` under both data sets. I ran all of them with
the same route and the same 25% burn-in (`review/log_recount_core.txt`,
`review/log_recount_orf.txt`):

| chain | Δ median | Δ upper | Δ lower |
|---|---|---|---|
| DR2new crn_pl log₁₀A | +0.0034 | −0.0018 | −0.0009 |
| DR2new crn_pl γ | −0.0040 | +0.0005 | −0.0017 |
| DR2full bin_b10 log₁₀A / γ | −0.0046 / −0.0047 | +0.0024 / −0.0031 | −0.0006 / −0.0016 |
| DR2full chebyshev log₁₀A / γ | +0.0019 / +0.0039 | +0.0020 / +0.0031 | −0.0014 / −0.0005 |
| DR2full legendre log₁₀A / γ | −0.0004 / +0.0010 | −0.0029 / −0.0033 | −0.0015 / −0.0018 |
| **DR2new bin_b10 log₁₀A** | −0.0137 | **+0.0128** | **+0.0721** |
| **DR2new bin_b10 γ** | **+0.0215** | **+0.1566** | **+0.0566** |
| **DR2new chebyshev γ** | +0.0137 | **+0.0892** | −0.0105 |
| DR2new legendre γ | +0.0075 | −0.0055 | +0.0192 |

Two consequences. First, ENTERPRISE + CURN DR2new is free evidence that the method works —
six more numbers, all inside 0.004 — and the run left it on the table with no stated reason.
Second, "whatever it is leaves the other five quantities inside 0.005 of print, so it is
small" is an artefact of having read three chains. Across the release, the DR2new chains miss
by up to 0.157 on an upper bound and 0.0215 on a median, which would fail even the median
band. The report's lone failure is the mild end of a pattern that is visible in the release
and that the report, as written, denies exists. This is the most useful thing the run could
add, and it costs one more loop over four tarballs.

## C2 (correction). The frozen route is not what the code does

`claims.json` route: "drop the burn-in the chain file itself declares (or the first 25% if it
declares none), apply sample weights if the file carries them". `scripts/recount.py` drops
25% unconditionally and never looks for a declared burn-in or a weight column. The outcome is
right — the tarballs are a bare `chain_1.txt` plus `pars.txt`, no header, no weights, four
extra PTMCMC columns — but the report should say it checked, because "the file declares none"
is a finding, not a default. Same for self-check 1: the "fewer than 10000 post-burn-in samples
is too short" guard lives in `summarise.py` and is absent from the script that produced the
results.

## C3 (correction). Small claims about the release that are not accurate

- "Each tarball holds a `chain_1.txt` and a `pars.txt`." The four `os.tar.gz` do not: they
  hold `hd_amp_sn.txt`, `dipole_amp_sn.txt`, `monopole_amp_sn.txt` and `os_cor.npy`.
- "`crn_fs` carries 50 `gw_crn_log10_rho_*`." True in DR2full and DR2full+; in DR2new and
  DR2new+ it is 20. The bin count differs per data set, which is itself a check on the
  mapping the report could have used.
- "Each chain is 29,990 samples." True of the three that were read and of most of the rest;
  DR2full+/hd_pl has 34,420 and DR2new+/hd_pl 44,190.
- "Each chain is 29,990 samples, but ... the effective sample size is 819 to 1,738." The ESS
  was computed on the 22,493 post-burn-in samples, not on 29,990 — 22,493/27.5 = 818. The
  numbers are fine, the sentence is not.

## C4 (correction). `summarise.py` ships a matching rule that contradicts the report's own guarantee

The report says parameters were read by name and never by index. `recount.py` does exactly
that and I verified it. But `summarise.py`, shipped in the same folder and listed in the file
table, matches with `name.lower() in p.lower()` and takes `idx[0]`. Called with its default
arguments on any of these chains it returns `J0030+0451_red_noise_log10_A` — a pulsar's noise
amplitude — labelled `log10_A`. It produced none of the results here. Delete it, or mark it
in the file table as superseded, because the next run that reuses it gets a wrong number
under a right-looking name.

Minor: the docstring of `tail_noise.py` says the miss is "0.0022". It is 0.0222.

---

## What held up

I tried to break these and could not.

**The six numbers.** My own loader — hand-written type-7 quantile, no `np.percentile`, read
from the zip instead of from `data/extracted/` — reproduces all six to the last printed digit:
−14.5357 +0.2802 −0.4064, 4.1914 +0.7324 −0.6330, −13.9353 +0.2329 −0.4831, 2.7103 +1.1835
−0.7322, −14.5278 +0.2939 −0.4391, 4.1273 +0.7969 −0.5898. The 18 deltas in the report's table
are right, the 0.0222 included.

**The targets.** Table 2 of the ar5iv HTML, fetched and parsed myself
(`review/table2_raw.txt`), gives exactly the three rows in `claims.json`, error bars included.
The caption confirms the columns are the EPTA-only DR2full and DR2new, and the text says the
+ sets come later, so the data-set choice is right.

**The pdftotext trap and the reason for going to the HTML.** I downloaded the PDF and ran
`pdftotext -layout` (`review/paper_layout.txt`). The labels do shift: the body prints
`FORTYTWO + GWB  -14.47...`, and −14.47 belongs to ENTERPRISE + Binned ORF, exactly as
`table2_check.log` says. The central values do agree between PDF and HTML on all eight rows
and all four value columns — I checked all 32. And the error bars really are unusable: the
straight character-by-character read gives +0.49/−0.24 for ENTERPRISE + CURN DR2full and
−0.43/+0.28 for ENTERPRISE + GWB DR2new, where the truth is +0.29/−0.44 and −0.48/+0.23. The
interleaving order flips inside a single cell. Going to the HTML was correct and the log's
account of why is accurate.

**The mapping, as a conclusion.** The + chains are nowhere near the Table 2 numbers:
DR2full+/hd_pl medians off by 0.062 and 0.127, DR2new+/hd_pl by 0.161 and 0.324, DR2new+/crn_pl
by 0.295 and 0.618 (`review/log_recount_plus.txt`). No other chain in the release can be
confused with the three that were used. B3 is about the argument, not the answer.

**The HPD elimination.** Reproduced independently: equal-tailed 0.0490 summed over the twelve
bounds against 0.9413 for HPD, and for γ in DR2new the HPD reading is +0.980/−0.831 against a
printed +1.18/−0.71. Equal-tailed percentiles it is.

**The ESS and the block bootstrap.** Sokal windowing is not the only estimator, so I ran two
more (`review/log_noise_check.txt`): Geyer initial-positive-sequence and batch means with 50
batches. τ comes out 13.9/13.3 against the report's 14.0, 27.5/25.9 against 27.5, 22.7/21.6
against 21.7. The ESS range of 819 to 1,738 is right to a few percent. The moving-block
bootstrap is the right instrument for the question it answers — how much this quantile moves
if the sampler is re-run — and the report is right that this is not the same question as "did
we read the same file". My complaint in B2 is that the report knows the answer to the second
question is "no" and still argues as if it were "yes".

**The frozen file.** `claims.sha256` still matches `claims.json`. `claims.json` says what the
report says it says, the asymmetric tolerance of B2 and the verdict ladder included, and
"Partially reproduced" follows that ladder. Its targets match the paper. The mtimes are
consistent with the stated order — `claims.json` and its hash at 14:17:16/17, `chains.zip`
finished at 14:24:13, extraction at 14:25:03 — so the freeze-before-download claim is
supported by everything a reviewer can see.

**The data.** md5 of `chains.zip` is `b3180fb1e8560a875fa3de5be001c4aa`, which is what the
Zenodo API returns for record 8091568, along with CC-BY-4.0 and open access. 28 tarballs in
four directories, matching `file_list.txt`. `data/extracted/` holds three tarballs and nothing
else, as claimed.

**Nothing published.** No git repository in the folder, no remote, no issue file for this
paper under `E:\Ciencia\issues`.

**S1.** The abstract's (2.5 ± 0.7)×10⁻¹⁵ at γ = 13/3 really has no chain behind it: every
power-law tarball samples γ, and the free spectra sample 20 or 50 ρ bins. Reporting it as not
checkable is right.
