# Adversarial review of the draft

Read the draft of `REPORT.md` against the files it cites and against the paper's LaTeX, with the
assumption that the author wants to publish a strong claim about a paper with a thousand
citations. Table 4 was re-extracted here with a separate parser, the sigw-gauss chain was
reloaded and recut, and every per-file maximum was taken from `runs/out/`.

Eleven things came back. Four are blockers: two numbers that the project's own files contradict,
one cell counted as restored when it is not, and one failure that is an artefact of the
tolerance rather than of the paper. The three headline findings survive, two of them stronger
than the draft makes them.

## 1. The Δ cell of sigw-gauss does not come back — blocker

§5 says "Drop exactly those samples and nothing else, and the model's five cells come back", and
the table prints Δ as **+1.3050 ± 0.6973** against a printed 1.30 ± 0.70.

Reloaded and recomputed at full precision
(`scratchpad/width_exact.py`, both cuts):

| cut | n | mean | \|mean − 1.30\| |
|---|---|---|---|
| none | 2,835,225 | 1.3235808945 | 0.02358 |
| drop the 46,378 log_posterior rows | 2,788,847 | 1.3050528665 | **0.00505** |
| drop the 46,400 gamma rows | 2,788,825 | 1.3050439313 | **0.00504** |

The frozen tolerance is "below 0.005". Both cuts land above it. Under the other half of the same
sentence — "our value rounds to the printed one" — 1.30505 rounds to 1.31, not 1.30. So the cell
fails under either reading of the frozen rule, and the draft's own table hides that by printing
four decimals: 1.3050 looks like it rounds to 1.30, 1.30505 does not.

The blind run's table has the same row (1.3051) and the same conclusion, so this came in from
there and was not caught here either.

Consequences: four of the five cells come back, not five. The header's **108 of 112** is 107.
§6's "Three other cells land in the near-miss band ... and all three reproduce once that block's
out-of-range samples are removed" is two of three.

## 2. The one unexplained failure is a tolerance artefact — blocker

§6 reports meta-l's NP+SMBHB string tension as the single unexplained claim: "our standard
deviation misses by 0.044 (1.1564 against 1.20)".

The paper does not print 1.20. Line 1161 of `main.tex` reads

```
$\log_{10}G\mu$   & $-5.80 \pm 0.78$  & $-5.9 \pm 1.2$   & ...
```

An independent re-extraction of the table here finds 112 Bayes cells, of which **exactly one** is
not printed to two decimals: this one. The frozen rule's premise — "Table 4 prints two decimals,
so a claim reproduces when our value rounds to the printed one" — is false for the only cell it
fails on, and `03_score.py` applies the flat 0.005 anyway. Round our 1.15635 to the printed
precision and you get 1.2, which is what the paper prints. The mean, −5.9032, rounds to −5.9.

The blind run got this right: it scores the cell with `dec=1, tol=0.06` and calls it reproduced
(`out/comparison.csv`). The draft quotes the paper's value as "1.20", which is a misquotation of
the source, and builds a whole section on it.

So the header's "one is unexplained" has no failure under the draft's own stated principle. If
the flat 0.005 is kept because it was frozen, that has to be said as what it is — a tolerance
mismatch on a one-decimal cell — and not as a property of the chain or of a heavy tail.

Taken with finding 1, the two errors partly cancel: 108 is arrived at by counting a cell that
misses and by failing a cell that does not. The honest line is 103 of 112 as deposited under the
frozen rule, 107 after the rows are removed, and one further cell that only fails because the
tolerance assumes a decimal the paper did not print.

## 3. "In every other chain of the deposit it stops at 6.22" — blocker

§5 rests the whole out-of-range argument on that ceiling. It is not the ceiling. From this
project's own `runs/out/*_npsmbhb.json`, the gamma_BHB maximum of the fifteen NP+SMBHB files:

```
sigw_box   6.1394   stable_c  6.1724   stable_n  6.1903   sigw_delta 6.2183
stable_k   6.2389   super     6.2487   dw_ds     6.2310   dw_sm      6.2526
pt_sound   6.2654   meta_l    6.2745   meta_ls   6.2871   stable_m   6.3553
igw        6.3777   pt_bubble 6.4452   sigw_gauss 13.5252
```

6.2183 is the maximum of **one** file, `sigw_delta_bhb.pkl.gz`, which is the file
`04_anomalias.py` happens to use as its reference. Ten of the fourteen other chains run past it,
up to 6.4452. "Every other chain stops at 6.22" is wrong, and the 46,400-sample cut it defines is
an arbitrary threshold drawn from a single comparison file.

The finding itself is not in danger — 13.53 against a ceiling of 6.45 is still four standard
deviations outside a normal(4.7, 0.346) prior. The sentence is.

## 4. "Every other file tops out at 8.8e6" — blocker

§8 says the corrupt rows carry log_posterior up to 1.308e12 "where the rest of that file, and
every other file, tops out at 8.8e6".

Half right. 8,845,129 is the maximum of the clean part of `sigw_gauss_bhb.pkl.gz`. Every other
file sits in a band 10 wide around 7.9728e6: across all 29, the minimum is 7,972,792.8 and the
maximum 7,972,867.5. Never 8.8e6.

The blind run states this correctly ("no other file shows a log_posterior outside 7.97e6 ± 10");
the draft merged two different numbers into one clause. The correct figure makes the finding
stronger, not weaker, and it adds something the draft does not use: the clean part of that file
already reaches 8.845e6, about 872,000 above every other chain's ceiling, and 20 of its "clean"
rows sit above 8e6. The contamination is not cleanly separated by the 1e7 line.

## 5. The row-contradiction argument is overstated, and does not cover the third cell — fix

Two problems in §4.

**"A mean of −0.26 cannot sit under an interval that starts at +0.03" is not a theorem.** With the
prior on log₁₀α_* running to −2 (Table 3, log-uniform [−2,1]) and 32% of the mass outside the
printed interval, the lowest mean arithmetically compatible with [0.03, 1] holding 68% is
0.68·0.03 + 0.32·(−2) = **−0.62**. A printed −0.26 is inside that. What rules it out is not the
interval alone but the interval together with a maximum posterior at the upper prior edge, and in
the end it is the chain. Say "would require the mass below 0.03 to average −0.88, which it does
not", not "cannot".

**The pt-sound NP row does not contradict itself.** Line 1137 of `main.tex`:

```
$\log_{10}\alpha_*$  & $-0.22 \pm 0.44$  & $0.14 \pm 0.56$  & $-0.21$  & $-0.15$
                     & $[-0.37, 1^*]$    & $[-0.34,0.73]$   & $...$
```

Maximum posterior −0.21, interval [−0.37, 1*]. A mean of −0.22 fits that row perfectly well. Only
the two pt-bubble rows carry the internal contradiction the section describes, and §4's bolded
claim sits over a table of three cells where a reader will take it to cover all three. For
pt-sound NP the only evidence is the chain, which is enough — but it has to be stated as one
piece of evidence, not two.

While there: "the same parameter in the dw-sm model" is the same symbol under a different prior,
log-uniform [−3, 0] (Table 3, line 1061), where it cannot be positive. The check still rules out
a blanket sign convention, but the sentence should say which prior it is run under.

## 6. "Our chains agree with the intervals and the maximum posteriors" was not measured here — fix

Nothing in `runs/out/` holds an interval or a mode. `04_anomalias.py` computes the four Bayes
cells and the gamma tail, and that is all. The statement comes from the blind run's
`out/comparison.csv`, which also qualifies it:

- pt-bubble NP maximum posterior: printed 1.0*, measured 0.80463 — **near miss**, not agreement.
- pt-bubble NP+SMBHB interval lower edge: printed 0.01, measured −0.00242 — near miss.
- pt-bubble NP interval: 0.02567 and 1.0 against a printed [0.03, 1.0] — this one does agree, and
  it is the load-bearing one, since a positive lower edge of the chain's own 68% region is what
  contradicts a negative mean.

The same applies to §2: the `compare/` figures (−11.6386 ± 0.5081, −14.7254 ± 6.8971) exist only
in the blind run's `out/cells_compare/`. Both numbers check out to the digit, but §2 presents them
in the first person six sections before the reader is told a second run exists.

## 7. "Eighteen that sit higher" — fix

§8 says the median sample mass inside the printed intervals is 0.6806 with 92 of 112 within 0.01
of 0.68, and "the eighteen that sit higher are the disjoint and boundary cases".

Recounted from `cego/out/diag.log`: median 0.6806 ✓, 92 within 0.01 ✓, and the remaining twenty
are **17 above and 3 below**. The three below are dw-dr NP log₁₀ΔN_eff (0.6479), dw-dr NP
log₁₀T_* (0.6682) and sigw-gauss NP+SMBHB gamma_BHB (0.6664). The first sits in the very row that
carries the fourth dropped sign and the third is the corrupt file, so dropping them from the
account quietly removes the two most interesting ones. The blind run makes the same count and the
same omission; the draft inherited it.

## 8. "Fourteen of the fifteen models" — fix

§3. Four models have at least one cell that does not reproduce: sigw-gauss (five), pt-bubble
(two), pt-sound (one), meta-l (one). Eleven of fifteen are clean, not fourteen.

## 9. §5 and §8 describe two different sets of rows — fix

They are presented as one finding. They are not the same cut:

- gamma > 6.2183: 46,400 rows, indices 2,788,825 to 2,835,224, contiguous.
- log_posterior > 1e7: 46,378 rows, indices 2,788,847 to 2,835,224, contiguous, reaching the last
  row of the file.

The second is a strict subset of the first. The 22 rows in the gap are log_posterior-clean, and
the single largest gamma_BHB value in the file — **13.5252, the 13.53 of §5's headline** — is one
of them. §8's criterion keeps the sample §5 leads with. Both cuts restore the same four cells and
fail the same fifth, so nothing turns on it, but the report should not hand a reader two row
counts for "exactly those rows".

## 10. The dw-dr / dw_ds mismatch is inside the paper — fix

§2: "Table 4 calls the dark-radiation domain-wall model `dw-dr` and the deposit calls it
`dw_ds`." Table 3 of the same paper calls it **dw-ds** (line 1066 of `main.tex`,
`\textbf{Domain walls} (\textsc{dw-ds})`). The deposit agrees with Table 3 and Table 4 disagrees
with both. Worth getting right, since the report is about the paper's own internal consistency.

## 11. "No access to this folder" — fix

§8. The blind run's scripts read the chains out of
`E:\Ciencia\noturno\2023-afzal-nanograv15-newphysics\extraido\chains\stochastic\` — this folder.
What it did not have was this run's parser, scripts, claims and results, which is the
independence that matters. Say that instead. It also means the two runs share one unpacking of
one download: if the extraction were damaged, both would be damaged the same way.

## What stands, and what got stronger

**The three sign cells stand.** Re-extracted from `main.tex` with a parser written for this
review: pt-bubble NP −0.26 ± 0.47, pt-bubble NP+SMBHB −0.23 ± 0.52, pt-sound NP −0.22 ± 0.44,
pt-sound NP+SMBHB +0.14 ± 0.56. The chains give +0.2634, +0.2256, +0.2187, +0.1354, each with a
standard deviation matching the printed one to better than 0.005. The fourth cell printing the
positive value and reproducing is the control, and it holds.

**The dropped sign in the dw-dr interval stands, and the draft under-argues it.** The printed
upper edge is `0.41^*`, and the table's own caption says values annotated with an asterisk "are at
the boundary of the prior range used in the analysis". Table 3 gives that boundary as log-uniform
[−3, **−0.41**]. So the asterisk itself says the number must be −0.41; +0.41 is not a boundary of
anything. The draft cites only the prior stored in the deposit file. Cite the caption and Table 3
— they are in the paper, and no reader has to trust our pickle reader for it.

**The corrupt block stands.** Verified here from the file: 46,378 rows, indices 2,788,847 to
2,835,224, contiguous, ending on the last row, log_posterior from 1.523e7 to 1.308e12 against
7.9728e6 everywhere else in the deposit.

**The chain-to-column mapping stands, and the strongest evidence is missing from the draft.**
§2 argues from parameter names and two means. The decisive one is in neither: `nmodel` is
constant at 0 in all 30 top-level files, while `compare/igw.pkl.gz` has it at 0 for 331,687
samples and 1 for 2,916,938, and `compare/igw_bhb.pkl.gz` at 0 for 313,361 and 1 for 2,485,339.
The `compare/` files are hypermodel runs that pool two hypotheses; the top-level files are not.
That is not a judgement call about naming. The parameter blocks check out too:
`compare/igw.pkl.gz` carries `gw_bhb_0`, `gw_bhb_1` and `compare/igw_bhb.pkl.gz` carries all four,
exactly as §2's table says.

**The freeze is intact.** `claims.json` hashes to the recorded
`f0dffc49bb20c19ac03dcdc980f1f04db6fe55c798056f2b90c20f118525ed02`, holds 112 primary and 224
secondary claims, and an independent re-extraction of Table 4 finds exactly 112 Bayes cells. The
blind run's `FREEZE.txt` carries the `c96313d2…` the draft quotes. The Bayes estimator really is
defined in Appendix A, as §1 says. The 560 comparisons and the 105→113 correction in §8 match
`out/comparison.csv` — though 113 is out of 224 interval edges, half of them, and the draft does
not give the denominator.

## What this review could not settle

**Whether the published Δ of 1.30 is reachable at all.** Every cut tried lands at 1.3050, which
rounds to 1.31. Either the authors' own summary used a slightly different sample set than any
criterion we can reconstruct from the file, or they rounded 1.305 down. One cell at 0.00005 past
a tolerance is not evidence of anything, and the report should not let it become the tail that
wags §5 in either direction.

**Where the three signs were lost.** Unchanged from the draft, and correctly left open there.

**Whether the near misses of §4's interval and maximum-posterior check are the paper's or our
bandwidth.** The blind run shows those columns are not reproducible to the printed digit by
anyone without the authors' density estimator — 113 of 224 edges — so the pt-bubble maximum
posterior reading 0.80 against a printed 1.0* says little on its own. The argument in §4 should
lean on the interval lower edge, which does reproduce, and not on the mode.

**Whether a third reading would agree.** Both runs read one unpacking of one download, with the
same restricted unpickler and the same assumption that the file is `[priors_dict,
samples_array]`. Nothing here tests that assumption independently.
