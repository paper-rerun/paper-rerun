# DES Year 3 — the 3x2pt cosmological constraints

- Paper: DES Collaboration (T. M. C. Abbott et al.), *Dark Energy Survey Year 3 results: Cosmological constraints from galaxy clustering and weak lensing*, Phys. Rev. D 105, 023520 (2022). DOI 10.1103/PhysRevD.105.023520, arXiv:2105.13549.
- Data: the chains the collaboration published at `https://desdr-server.ncsa.illinois.edu/despublic/y3a2_files/chains/`. No login, no click-through, TLS verification on. Sizes and sha256 in `data/README.txt`.
- Code: none of the authors' is needed for this. The one script they ship in that folder, `read_chains_y3a2.py`, is examined in §4 but is not used to produce any number here.
- Target: the ten values frozen in `claims.json`, SHA-256 `3cda9babf5234a35c57e04960268f2228b06786e3d13755a94da4e91db3bd7f9`, frozen at 2026-11-20T03:13:24Z, before anything was computed.
- Verdict: **Partially reproduced** — 6 of 10 against the rule we froze, 10 of 10 against the rule the paper describes. All ten central values land on the printed number. Four of the published bounds miss, and they miss because we froze the wrong rule: we scored 16th/84th percentiles, and the paper says the bound is "68% of posterior volume around the mean", which is the highest-density interval. Under that reading every bound reproduces too, including w, where the percentile rule gets ±0.27 against a published +0.32 −0.20.
- Date: 2026-11-20
- Hardware: Ryzen 9 3900X, 64 GB, CPU only, `nice -n 19`. The GPU was not touched.
- Wall clock: 1.5 s to recount the 50.8 MB chain, 24 s to score all ten claims including the KDE, a few minutes to download 110 MB. Folder 149 KB plus the downloads.

## What this run is

The DES Y3 3x2pt analysis ran CosmoSIS with PolyChord over 31 varied parameters. Re-running
that inference is thousands of CPU hours and was never the plan. What the collaboration
published alongside the paper is the chains themselves, so the checkable step is the one
between the chain and the printed number: take their samples, apply their weights, and see
whether the summary in Eq. (17), Eq. (19) and Tables II and III comes back.

That checks the summarising step, not the inference. The same caveat was written into the
NANOGrav and EPTA reports and it holds here: if the sampler was wrong, this run cannot see it.

Ten targets, three chains, all of them fiducial rows:

- `chain_3x2pt_lcdm_SR_maglim.txt` — 3x2pt, flat ΛCDM, MagLim lenses. S_8, Ω_m, σ_8.
- `chain_3x2pt_wcdm_SR_maglim.txt` — the same in wCDM. S_8, Ω_m, σ_8, w.
- `chain_all_lcdm.txt` — DES 3x2pt + BAO + RSD + SNe Ia + Planck + CMB lensing. S_8, Ω_m, h.

S_8 is not a column: it is formed as σ_8·√(Ω_m/0.3), the way the authors' own script forms it.

## Verdict table

| claim | chain | param | published | frozen rule (mean, 16/84) | paper's rule (mean, HPD 68%) |
|---|---|---|---|---|---|
| C1 | 3x2pt ΛCDM | S_8 | 0.776 +0.017 −0.017 | 0.7760 +0.0178 −0.0178 ok | 0.7760 +0.0173 −0.0181 ok |
| C2 | 3x2pt ΛCDM | Ω_m | 0.339 +0.032 −0.031 | 0.3388 +0.0309 −0.0311 ok | 0.3388 +0.0312 −0.0317 ok |
| C3 | 3x2pt ΛCDM | σ_8 | 0.733 +0.039 −0.049 | 0.7330 +0.0449 −0.0450 **fails** | 0.7330 +0.0405 −0.0502 ok |
| C4 | 3x2pt wCDM | S_8 | 0.775 +0.026 −0.024 | 0.7745 +0.0250 −0.0247 ok | 0.7745 +0.0257 −0.0239 ok |
| C5 | 3x2pt wCDM | Ω_m | 0.352 +0.035 −0.041 | 0.3516 +0.0373 −0.0390 **fails** | 0.3516 +0.0352 −0.0421 ok |
| C6 | 3x2pt wCDM | σ_8 | 0.719 +0.037 −0.044 | 0.7185 +0.0419 −0.0404 **fails** | 0.7185 +0.0384 −0.0446 ok |
| C7 | 3x2pt wCDM | w | −0.98 +0.32 −0.20 | −0.9808 +0.2668 −0.2773 **fails** | −0.9808 +0.3282 −0.2052 ok |
| C8 | all, ΛCDM | S_8 | 0.812 +0.008 −0.008 | 0.8120 +0.0079 −0.0080 ok | 0.8120 +0.0077 −0.0081 ok |
| C9 | all, ΛCDM | Ω_m | 0.306 +0.004 −0.005 | 0.3062 +0.0043 −0.0044 ok | 0.3062 +0.0041 −0.0045 ok |
| C10 | all, ΛCDM | h | 0.680 +0.004 −0.003 | 0.6802 +0.0034 −0.0034 ok | 0.6802 +0.0035 −0.0034 ok |

Tolerance, frozen before the run: 0.001 on a central value printed with three decimals
(rounding alone allows 0.0005), 0.002 on each bound, and five times that on w, which is
printed with two.

## 1. Every central value reproduces

Ten out of ten, to the last printed digit: S_8 = 0.7760 against 0.776, Ω_m = 0.3062 against
0.306, h = 0.6802 against 0.680. The largest miss anywhere is 0.0005, on S_8 in wCDM, and the
paper prints three decimals, so that is rounding.

This is worth stating plainly because it is the part that could have gone wrong quietly. The
weight column of a PolyChord chain is not optional: ignore it and the 3x2pt ΛCDM S_8 comes out
at 0.7245, which still looks like a plausible number and is three published sigmas from the
printed one. Our `01_recount.py` applies it, reads every column by the header, and gets the
printed values back.

## 2. The bounds are highest-density intervals, and the sentence that defines them describes something else

Section V of the paper says: "We report the mean in each parameter, along with the 68%
confidence limit (CL) of posterior volume around the mean." That sentence is the whole rule,
it appears once, and it is the only place in the paper where the interval is defined: the
table captions, the figure captions and the abstract all say "68% CL" and stop there.

Taken literally it is a recipe: start at the mean, walk out until you have 34% of the
posterior volume on each side. We computed that recipe. On the two targets with a skewed
marginal it does not give the published bounds — it gives them backwards:

| param | published | literal: 34% of volume each side of the mean | highest-density 68% |
|---|---|---|---|
| σ_8, ΛCDM | +0.039 −0.049 | +0.0516 −0.0398 | +0.0405 −0.0502 |
| w, wCDM | +0.32 −0.20 | +0.2284 −0.3581 | +0.3282 −0.2052 |

The long tail swaps sides. Whatever produced the printed numbers, it was not the procedure
the sentence describes, and the difference is not subtle: on w the two readings disagree about
which direction the data prefer.

The highest-density interval is what reproduces. It does not use the mean at all — it is the
shortest interval holding 68% of the posterior — and the printed central value is not at its
centre. For w the interval runs from −1.186 to −0.653 and the published −0.98 sits 38% of the
way along it. So the printed line is two different statistics stitched together: a mean, and
the two endpoints of an interval that was found without reference to it.

We froze the percentile reading
instead, which is the reading most people take from "68% confidence limits" and the one the
abstract's wording invites.

Where the marginal is symmetric every reading agrees and nothing shows. Where it is skewed
they come apart:

| param | published | percentiles 16/84 | highest-density 68% |
|---|---|---|---|
| σ_8, ΛCDM | +0.039 −0.049 | +0.0449 −0.0450 | +0.0405 −0.0502 |
| σ_8, wCDM | +0.037 −0.044 | +0.0419 −0.0404 | +0.0384 −0.0446 |
| w, wCDM | +0.32 −0.20 | +0.2668 −0.2773 | +0.3282 −0.2052 |

Of the four frozen failures, one is marginal and should be read as such: Ω_m in wCDM misses by
0.0003 on the upper bound, against a tolerance of 0.002. The other three are not close.

The w row is the one that settles it. The published interval is strongly lopsided, +0.32 and
−0.20, and percentiles give almost exactly symmetric bounds of ±0.27. No amount of sampling
noise turns one into the other: it is a different definition. The highest-density interval
reproduces both sides at once, and does it again for σ_8 in both models.

So the four failures in the table are ours, not theirs. We report the frozen verdict anyway,
because the rule was fixed before the numbers were seen and moving it afterwards is how a
rerun talks itself into the answer it wants. The honest summary is the one in the header: 6 of
10 under the rule we froze, 10 of 10 under the rule the paper describes.

How much of this is the smoothing? The bound comes from a kernel density estimate, so it
depends on the bandwidth. We swept it from 0.6 to 2.0 times Silverman's rule. Between 0.6 and
1.0 every one of the seven published bounds in the two 3x2pt chains reproduces. At 1.5 — the
value the authors' own plotting script passes to ChainConsumer — σ_8 in ΛCDM and w drift out
of tolerance, by 0.0023 and 0.016. The published numbers sit at the narrow end of that range.

## 3. What a reader who takes the natural reading gets wrong

Someone recomputing w from the published chain with percentiles — `numpy.percentile` on the
weighted samples, or any of the summary helpers that default to quantiles — gets −0.98 ± 0.27
instead of −0.98 +0.32 −0.20. The upper error comes out 17%
too small, the lower one 39% too large, and the asymmetry that carries the physical statement
— that the data allow w well above −1 more than well below it — disappears entirely.

A sentence in the caption of Tables II and III saying which interval is used would cost one
line. The text has it; the tables, the figures and the abstract do not.

## 4. The reader script the release ships does not work on the files it ships with

`read_chains_y3a2.py` sits in the same directory as the chains. It takes σ_8 from column
index 30 and the weight from index 36, with comments stating so:

```
sigma8=float(words[30]) ## as described on the first line, sigma8 is the 31 entry in each line
w.append(float(words[36]))  #weight, it is column 37
```

Those indices are right only for a chain whose header has exactly 37 columns. We fetched the
header of all 29 chains in that folder. Three have 37 columns. The other 26 do not, and the
column counts run from 14 to 62.

In the fiducial 3x2pt ΛCDM chain, index 30 is `intrinsic_alignment_parameters--bias_ta` and
index 36 is `post`, the log-posterior. Run as published, the script therefore computes
S_8 = 0.93 (mean) instead of 0.776, weighted by a column whose values run from −960,191 to
5,869 and go negative 525 times.

It is worse in the file the script itself opens on line 12, `chain_2x2pt_wcdm_SR_maglim_NLbias.txt`,
which has 43 columns: index 30 is `bias_lens--b2e_sig8sq_bin4` and index 36 is σ_8 itself. The
offset there is exactly six, which is the number of `b2e_sig8sq_bin*` columns the nonlinear-bias
parametrisation adds. The example ships pointed at a file it mis-reads, and produces a mean S_8
of −0.42 where the header gives 0.849. A negative S_8 is not a number anyone would publish, so
that one would be caught — but the fiducial case would not: 0.93 with a plausible-looking
contour is exactly the kind of wrong number that survives a glance. Of the 38 columns in that
chain, the only index the script gets right is 0, `omega_m`.

The fix is three lines: read the first line, split on tabs, look the names up. Our
`01_recount.py` does exactly that and is 69 lines including the weighted quantiles.

## 5. Everything we checked

- All ten central values, against Eq. (17), Eq. (19) and the fiducial rows of Tables II and III.
- All twenty bounds, under seven summary rules: mean or median or KDE mode, crossed with
  percentiles, highest-density interval and a cumulative rule, plus the literal reading of the
  paper's own sentence — 34% of the volume on each side of the mean.
- The bandwidth dependence of the highest-density bounds, over a factor of three.
- The weight column: present, positive, and necessary. Dropping it moves S_8 by 0.052 and
  Ω_m by 0.004.
- The header of all 29 published chains against the published reader's hardcoded indices.
- The effective sample size: 6,310 for the 3x2pt ΛCDM chain out of 22,619 rows, 8,243 of
  45,932 for the combined one. Percentile noise at that size is a few units in the fourth
  decimal, which is why the tolerance on a bound is 0.002 and not 0.0005.

## 6. What we did not do

- We did not re-run CosmoSIS or PolyChord. The inference is out of scope and out of budget.
- We did not check the redMaGiC rows, the X_lens result, the p-values or any tension metric:
  they need the likelihood, not the chain.
- We did not read the published PDF from the journal. The targets were read from the ar5iv
  HTML of arXiv:2105.13549, because `pdftotext` interleaves the superscripts character by
  character — the layout version gave σ_8 = 0.719 +0.047 −0.034 for wCDM where the HTML says
  +0.037 −0.044. The EPTA and DESI DR2 runs hit the same bug.

## What the two checks caught

An adversarial review of the first draft and a blind recount ran on top of this report.

The review (`REVIEW.md`) raised five points and four were real. The one that mattered: the
draft claimed that dropping the weight column moves S_8 by 0.003. That number was never
computed — it was written from intuition. The measured shift is 0.052, three published sigmas.
A figure in a supporting clause is exactly where no table forces you to check.

The blind recount ran in a separate folder with no access to any of this, pre-registered its
own five candidate definitions before touching a chain, and sampled nothing from us. It agrees
on all ten central values and on the smoothed highest-density interval as the only rule that
reproduces all ten bounds. It found two things this report did not have:

- The literal reading of the paper's sentence inverts the asymmetry, which is now §2. We had
  only shown that percentiles disagree; the stronger statement is that the recipe the paper
  states gives the published numbers backwards.
- The six-column offset in the NLbias file, which names what went wrong in the authors' script
  rather than just that something did.

It also reports that the raw highest-density interval, computed on the weighted CDF without
smoothing, misses one target out of ten because at an effective sample size of 6,300 the
shortest-interval search chases noise; smoothing first fixes it. Our own sweep says the same
thing from the other side: the bounds are stable from 0.5 to 1.5 times the bandwidth rule and
only break down above that.

One difference between the two runs is worth stating. We froze percentiles as the primary rule
and it failed four bounds; the blind run froze the literal reading of the sentence and it
failed three. Neither of us guessed the rule that works. That is the finding, not our frozen
verdicts.

## Reproducing

```
python -P scripts/01_recount.py downloads/<chain>.txt runs/out/<chain>.json
python -P scripts/02_readings.py downloads/<chain>.txt runs/out/readings_<chain>.json
python -P scripts/03_bandwidth.py downloads/<chain>.txt runs/out/bw_<chain>.json
python -P scripts/04_header_audit.py runs/out/header_audit.json
python -P scripts/05_script_as_published.py downloads/<chain>.txt runs/out/script_<chain>.json
python -P scripts/06_score.py claims.json claims.sha256 runs/out/verdict.json
python -P scripts/07_volume_around_mean.py downloads/<chain>.txt runs/out/volume_<chain>.json
```

Python 3.12.10, numpy 2.5.0, nothing else.

## Notes for the authors

Four points, in the order they matter to someone using the release.

**1. The reader script in the chains folder does not work on the chains in that folder.**
`read_chains_y3a2.py` takes σ_8 at index 30 and the weight at index 36. Three of the 29 chains
have the 37-column layout that makes those indices right. In the fiducial 3x2pt ΛCDM chain it
reads `bias_ta` as σ_8 and the log-posterior as the weight, and returns a mean S_8 of 0.93
instead of 0.776 — no error, just a plausible wrong contour. In
`chain_2x2pt_wcdm_SR_maglim_NLbias.txt`, the file the script itself opens, the offset is six
columns and S_8 comes out at −0.42. Reading the header line instead is three lines of code.

**2. Please say in the table captions which interval the ± is.** The bounds reproduce as the
68% highest-density interval of the marginal and as nothing else we could construct. A reader
who takes percentiles — the natural reading of "68% confidence limits" — gets w = −0.98 ± 0.27
instead of −0.98 +0.32 −0.20, losing the asymmetry that carries the physical statement.

**3. The one sentence that does define it describes a different procedure.** Section V says
"the 68% confidence limit of posterior volume around the mean". Walking out from the mean
until 34% of the volume lies on each side gives, for w, +0.23 −0.36: the asymmetry inverted
relative to the printed +0.32 −0.20. The same inversion happens for σ_8 in ΛCDM. The printed
interval is also not centred on the printed value — for w it runs from −1.186 to −0.653, with
the mean 38% of the way along — so the line combines a mean with the endpoints of an interval
computed without it. That is a defensible choice, but the sentence does not describe it.

**4. Everything else reproduces.** All ten central values we checked come back to the last
printed digit from the deposited chains, including the combined-probe S_8 = 0.812 and
h = 0.680. Publishing the chains is what made any of this checkable, and it is not the norm.
