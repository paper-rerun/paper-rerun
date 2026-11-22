# Reproduction report: The NANOGrav 15 yr Data Set — Search for Signals from New Physics

- Paper: A. Afzal et al. (NANOGrav Collaboration), *The NANOGrav 15 yr Data Set: Search for Signals from New Physics*, The Astrophysical Journal Letters 951, L11 (2023). DOI 10.3847/2041-8213/acdc91, arXiv:2306.16219. Values read from the paper's own LaTeX source, not from the HTML rendering.
- Data: the authors' MCMC chains, `https://zenodo.org/records/8083620/files/chains.gz` (concept DOI 10.5281/zenodo.8010909). 22,440,020,155 bytes, md5 `464a0c2f2645aec4bd72cbd9f1bfb4cf` as published, which our copy matches; sha256 `c9a6db2a…` recorded by us because Zenodo publishes only md5. CC-BY-4.0, no login and no click-through.
- Code: none of the authors' is needed. This is arithmetic on their samples.
- Target: Table 4 (`tab:list`), the Bayes estimators of every new-physics model in both the NP and NP+SMBHB analyses. 112 claims, frozen in `claims.json`, SHA-256 `f0dffc49bb20c19ac03dcdc980f1f04db6fe55c798056f2b90c20f118525ed02`, frozen at 2026-11-21T15:58:29Z, before any chain was opened. 224 further claims (68% intervals and maximum posterior values) were frozen as secondary.
- Verdict: **Partially reproduced** — 103 of 112 primary claims come back under the rule we froze, and 108 under the rule the paper's own printing implies, four of those eight needing a corrupt block removed from one deposited file. Of the four that never come back, three carry a sign the chains do not support, and one misses by 0.005 for reasons we could not establish. A second, independent recount reached the same findings without seeing our scripts or results, and added a fourth sign error in a column we had frozen as secondary. Our own adversarial review then corrected this header: see §10.
- Date: 2026-11-21
- Hardware: Ryzen 9 3900X, CPU only, the GPU untouched.
- Wall clock: 3 h 44 min to download 22.4 GB, about 9 min to unpack the stochastic branch, roughly 25 min to recount all 30 chain files. Folder 40 GB, of which 40 GB is the deposit and nothing is redistributed.

## 1. What this run is

The paper searches the NANOGrav 15-year data for cosmological sources of the gravitational-wave
background — inflation, scalar-induced waves, phase transitions, cosmic strings, domain walls —
and reports, for each model, the posterior summaries of its parameters. Rerunning that inference
is weeks of CPU. What the collaboration deposited is the chains themselves, so the checkable
step is the one between the samples and the printed number.

That checks the summarising step, not the inference. The same caveat applied to our DES Y3 and
DESI reruns and it applies here.

**The reason this paper was picked over others on the same shelf is that it defines its own
estimator.** Appendix A states that the Bayes estimator is the expectation value of the 1D
marginal and its standard deviation the square root of the variance, computed in practice as the
sample mean and sample standard deviation of the chain. In our DES Y3 rerun the absence of
exactly that sentence was the central finding. Here it is present, so the recount is well posed
from the start, and our frozen rule is simply what the appendix says: unweighted sample mean and
sample standard deviation over the samples as deposited, nothing discarded, nothing thinned.

Tolerance, frozen in advance: Table 4 prints two decimals, so a claim reproduces when our value
rounds to the printed one, that is when the absolute difference is below 0.005. Between 0.005 and
0.05 we record a near miss rather than a failure, because sampling noise in a mean is real.

**That premise is false in one cell, and it is the cell where the rule reproves.** The metastable
string tension under NP+SMBHB is printed `-5.9 \pm 1.2`, with one decimal, alone among the 112. At
one decimal the matching tolerance is 0.06 and our value reproduces. We report the count both ways
rather than quietly rescoring, because changing a frozen rule after seeing which cell it fails is
the move the rule exists to prevent.

## 2. Which chains belong to which column

The deposit holds two parallel sets, `chains/stochastic/` and `chains/stochastic/compare/`, with
the same file names in both. Picking the wrong one would have produced a confident, wrong report,
so we resolved it from the parameter names inside the files rather than by guessing — reading the
pickle opcodes, without executing them:

| file | parameters it carries | what it is |
|---|---|---|
| `igw.pkl.gz` | the model's own parameters only | the **NP** column |
| `igw_bhb.pkl.gz` | the model's parameters plus `gw_bhb_np_0`, `gw_bhb_np_1` | the **NP+SMBHB** column |
| `compare/igw.pkl.gz` | adds a second black-hole-binary block, `gw_bhb_0`, `gw_bhb_1` | a hypermodel run |
| `compare/igw_bhb.pkl.gz` | carries both blocks | a hypermodel run |

The numbers settle it as well as the names. For super's log₁₀Gμ under NP the paper prints −11.67 ± 0.32;
the top-level file gives −11.6722 ± 0.3198 and the `compare/` file −11.6386 ± 0.5081. For igw's log₁₀r
the paper prints −14.06 ± 5.82; top-level gives −14.0607 ± 5.8187 and `compare/` −14.7254 ± 6.8971.

Table 4's NP column has no `A_BHB` row and its NP+SMBHB column has exactly one `A_BHB` and one
`gamma_BHB`; the root files match that one for one. The `compare/` set is the model-comparison
run behind the Bayes factors, which is outside our target. We also checked that `nmodel`, the
hypermodel index, is constant at 0 in every one of the thirty root files, so no chain we used pools
two hypotheses — while in `compare/igw.pkl.gz` it takes the value 0 in 331,687 samples and 1 in
2,916,938. The `compare/` files are hypermodel runs in fact and not only in name.

One naming note, and it is the paper's rather than the deposit's: Table 4 calls the dark-radiation
domain-wall model `dw-dr` while Table 3 and the deposit both call it `dw-ds`. The mapping is
unambiguous from the parameter names (`log10_N_eff` against the table's ΔN_eff row), but it is the
kind of mismatch that silently costs someone an afternoon.

**On loading the files at all.** They are gzipped Python pickles, and `pickle.load` runs whatever
the file asks it to. These came off the internet. Our scripts never call it: a restricted
unpickler allows only the three numpy names needed to rebuild an array and raises on anything
else. Nothing in the deposit tripped it, which is the expected and welcome outcome, but the check
costs five lines and the alternative is executing a stranger's code.

## 3. What reproduces

103 of the 112 primary claims reproduce directly, each landing within 0.005 of the printed value
on both the mean and the standard deviation. The first model we scored, inflationary
gravitational waves, is typical:

| | ours | printed |
|---|---|---|
| log₁₀T_rh (NP) | +0.0234 ± 1.6002 | +0.02 ± 1.60 |
| log₁₀r (NP) | −14.0607 ± 5.8187 | −14.06 ± 5.82 |
| n_t (NP) | +2.6145 ± 0.8486 | +2.61 ± 0.85 |
| log₁₀A_BHB (NP+SMBHB) | −15.6030 ± 0.5557 | −15.60 ± 0.56 |
| γ_BHB (NP+SMBHB) | +4.6130 ± 0.3681 | +4.61 ± 0.37 |

Sixteen numbers, all sixteen inside the tolerance. Eleven of the fifteen models reproduce in every one of
their cells, and the picture says the frozen rule is the right one: the appendix means what it says,
and the chains as deposited are the chains that were summarised.

## 4. Three cells carry a sign the chains do not support

α_* appears in four cells of Table 4, across the two phase-transition models. In three of them the
printed value is our value with the sign turned round, while the printed standard deviation
matches ours to the same precision:

| cell | our chain | printed | distance as printed | distance if the sign is flipped |
|---|---|---|---|---|
| pt-bubble, NP | +0.2634 ± 0.4658 | −0.26 ± 0.47 | 0.5234 | **0.0034** |
| pt-bubble, NP+SMBHB | +0.2256 ± 0.5183 | −0.23 ± 0.52 | 0.4556 | **0.0044** |
| pt-sound, NP | +0.2187 ± 0.4373 | −0.22 ± 0.44 | 0.4387 | **0.0013** |
| pt-sound, NP+SMBHB | +0.1354 ± 0.5592 | +0.14 ± 0.56 | **0.0046** | 0.2754 |

The fourth row is what makes this readable. That cell prints the positive value and reproduces
normally, so the chain-to-column mapping is right and the estimator is right; three cells of the
same parameter carry a minus the samples do not.

**In two of the three rows the paper's own table is at odds with the printed sign.** In the
pt-bubble NP row, alongside the Bayes estimator of −0.26, the same row prints a maximum posterior
of +1.0 and a 68% credible interval of [0.03, 1.0]. In the pt-bubble NP+SMBHB row the interval is
[0.01, 1.0], the maximum posterior +0.74, against a printed mean of −0.23.

That is not a theorem — a distribution with 68% of its mass in [0.03, 1.0] can still have a
negative mean if the remaining 32% sits far enough left. Taking the prior's floor of −2 as the
worst case, the lowest mean such a distribution could have is about −0.62, so −0.26 is not
arithmetically impossible. It is implausible, and it is implausible in exactly the direction the
chains already show. We state it as a tension, not a proof.

The third row, pt-sound NP, carries no internal contradiction at all: its maximum posterior is
−0.21 and its interval [−0.37, 1.0], both consistent with the printed −0.22. There the only
evidence is the chain, and the chain gives +0.2187.

One more check rules out a sign convention rather than a slip: the same parameter in the dw-sm model is
genuinely negative, −0.88, and reproduces as printed. So it is not that α_* is written with one sign in
the chains and another in the table.

The prior for α_* is log-uniform on [−2, 1] (Table 3), so both signs are inside it and nothing
about the prior forces the answer. About a third of the samples do sit below zero (30.5%, 32.1%
and 36.3% in the three cells), so the distribution genuinely straddles zero — the mean simply
comes out positive.

What we cannot say is where the sign was lost: in the table, in the script that filled it, or in
a step between. We can say that the deposited chains give the positive value and that two other
columns of the same rows agree with us.

## 5. One deposited chain ends in a corrupt block

All five NP+SMBHB cells of the sigw-gauss model missed, which is a suspicious pattern: one model,
one variant, every cell. The cause is in the file. In `sigw_gauss_bhb.pkl.gz` the `gamma_BHB`
column runs up to **13.53**, while across the other fourteen NP+SMBHB chains the largest value seen
anywhere is **6.45** (the fourteen maxima run from 6.14 to 6.45). 46,400 samples, 1.64% of the file,
sit above 6.22, which is where one of those other files happens to stop; the honest ceiling to
compare against is 6.45, and the finding is the same.

Drop exactly those samples and nothing else, and four of the model's five cells come back:

| | as deposited | without those 46,400 samples | printed |
|---|---|---|---|
| log₁₀A | −0.3610 ± 0.6047 | −0.3592 ± 0.6096 | −0.36 ± 0.61 |
| log₁₀f_peak | −6.2904 ± 0.7236 | −6.3006 ± 0.7252 | −6.30 ± 0.73 |
| Δ | +1.3236 ± 0.7064 | +1.3050 ± 0.6973 | +1.30 ± 0.70 |
| log₁₀A_BHB | −15.6814 ± 0.5683 | −15.7244 ± 0.4641 | −15.72 ± 0.46 |
| γ_BHB | +4.7993 ± 1.1759 | +4.6541 ± 0.3432 | +4.65 ± 0.34 |

γ_BHB is the clearest: 4.7993 ± 1.1759 as deposited, against a printed 4.65 ± 0.34, and
4.6541 ± 0.3432 once the bad rows go. The standard deviation is wrong by a factor of 3.4 before the
cut and right to three decimals after it.

The fifth cell, Δ, does not come back. At full precision it is 1.3050529 against a printed 1.30, a
difference of 0.00505, which rounds to 1.31 and so fails the frozen rule by five parts in a hundred
thousand. The table above prints it as 1.3050, which hides that. It is the one claim in this report
we cannot account for, and §6 says so.

So the published numbers are not in question — they are what the analysis produced. What is in
question is the file: the deposited chain for that one model and variant contains samples that
the summary behind Table 4 did not include. Anyone recounting from the deposit, as we did, gets a
different number and has no way to know why without noticing that one column outruns all the
others. A line in the deposit saying which samples were used, or a deposit that excludes them,
would close it.

## 6. What is left unexplained

The Δ parameter of sigw-gauss under NP+SMBHB, the fifth cell of §5. After the corrupt block is
removed it is 1.3050529 against a printed 1.30: 0.00505 away, where the rule allows 0.005. Cutting
on the damaged `log_posterior` rows and cutting on the out-of-range γ_BHB rows give 1.3050529 and
1.3050439, so the miss does not depend on which cut we use. Whatever the published number was
computed from, it was not either of those two sets of samples, and we cannot say what the
difference is. One claim of 112.

The cell we previously listed here, the metastable string tension, is no longer among them: it is
the one cell printed to a single decimal, and at that precision it reproduces. The mistake was
ours, and §10 records it.

## 7. What is out of scope, and why

**The Bayes factors.** The headline of the paper is that several cosmological models beat the
supermassive-black-hole-binary interpretation by factors of 10 to 100. Those come from the
evidence, not from the marginals, and no amount of arithmetic on a posterior chain recovers them.
Reproducing them means rerunning the inference. This report says nothing about them, in either
direction.

**The K bound column** of Table 4 is a likelihood ratio, not a property of the marginal, and is
excluded for the same reason.

**The maximum posterior and 68% interval columns** were frozen as secondary, not primary, because
the paper defines the Bayes estimator and does not define these two: a mode needs a density
estimate and a bandwidth, and an interval can be equal-tailed or highest-density. We declared
both readings in advance and report them as secondary evidence only — as in §4, where they tell
us the Bayes estimator column disagrees with its own neighbours.

## 8. The second recount

A blind recount ran against the same deposit, reading the chains from this folder but none of our
scripts, claims or results: its own pre-registration,
frozen (sha256 `c96313d2…`) before it opened a chain, its own parser, its own scripts. It scored more
widely than we did — 560 individual numbers across all four columns of Table 4, against our 112 — and
it reached both findings above on its own, with the same numbers to four decimals.

It also went further in three places, each verified here before being written down:

**It identified §5 as a corrupt block, not merely out-of-range samples.** We had found the γ_BHB
column of `sigw_gauss_bhb.pkl.gz` running past where every other chain stops. The blind run looked at
`log_posterior` and found those same rows carry values from 1.523e7 up to 1.308e12. The clean part of
that same file tops out at 8.845e6, and every one of the other twenty-nine files sits in a band of
about ten around 7.9728e6. We checked: the bad rows are indices 2,788,847 to 2,835,224 —
**one contiguous block at the very end of the file**, 46,378 rows of 2,835,225. That is a damaged tail,
not a sampler exploring somewhere odd, and it explains why removing exactly those rows restores every
cell of the model.

**It found a fourth dropped minus sign, in the interval column.** The dw-dr model's ΔN_eff row prints
its NP+SMBHB 68% interval as [−0.63, **+0.41***]. This one needs no chain at all to see. The asterisk
means, by the table's own caption, that the value sits at the boundary of the prior range; Table 3
gives that range as log-uniform on [−3, **−0.41**]. So the paper marks a number as sitting on a prior
edge that its own prior table puts at the opposite sign. The NP column of the same row prints −0.41,
correctly. The deposit agrees: the prior stored in the file is (−3.0, −0.4089) and the chain's largest
sample is −0.4089, on that edge, and against −0.41 the printed edge reproduces.

**It settled what the interval column actually is.** The paper never states its density estimator, so
neither run can hit those edges to the printed digit — a mode needs a bandwidth and an interval can be
equal-tailed or highest-density. Rather than stop there, the blind run measured the fraction of
deposited samples falling inside each printed interval: the median over all 112 intervals is **0.6806**,
with 92 of them within 0.01 of 0.68. So the printed intervals are genuine 68% highest-density regions
of these chains. Seventeen sit higher and three lower. The seventeen are the disjoint and boundary cases, where the
printed [θ⁻, θ⁺] spans a region holding more than 68%, which is what the paper's own definition
produces. The three below are not a separate puzzle: they are the ΔN_eff row of the sign error above
and the cells of the damaged file.

Two of its observations are about the limits of this kind of check rather than about the paper. Three
parameters are not reproducible in principle at the interval level — igw's log₁₀T_rh and log₁₀r, and
`b` in both domain-wall models — because the data barely constrains them: `b`'s Bayes estimator,
0.74 ± 0.14, is the mean and standard deviation of its own uniform prior to three decimals. Their means
reproduce; their interval edges are set by fluctuations of the order of the smoothing, and the paper
itself prints dw-dr's `b` upper edge as 0.97 under NP against 0.83 under NP+SMBHB from statistically
identical posteriors.

And it recorded a mistake of its own: its comparison script first scored the interval cells against its
secondary estimator rather than the primary one its pre-registration names. It caught the departure and
fixed it before its final numbers. The correction moved the interval column from 105 reproduced to 113,
so the error had been working against its own result, which is the direction that makes it easy to
miss.

## 9. What our own review corrected

A third pass read this draft against the files it cites and against the paper's LaTeX, with its own
parser, looking for numbers we had copied wrong or claims stronger than the evidence. It found four
things that mattered, and they are fixed above rather than hidden:

1. **The header said 108 of 112.** It said that by counting a cell that fails and failing a cell that
   passes, and the two cancelled. Δ in sigw-gauss misses by 0.00505 even after the corrupt block is
   removed, and the metastable string tension is printed to one decimal, where it reproduces. The
   honest count is 103 under the frozen rule and 108 under per-cell precision, and both are now in
   the header.
2. **"Every other chain stops at 6.22" was wrong.** That was one file's maximum, the one our script
   used as its reference. Across the fourteen others the maxima run from 6.14 to 6.45. The finding
   survives — 13.53 against a ceiling of 6.45 — and the sentence did not.
3. **"Every other file tops out at 8.8e6" was wrong**, and wrong in a way that understated the case.
   8.845e6 is the clean part of the damaged file itself; the other twenty-nine sit around 7.9728e6
   within about ten.
4. **"A mean of −0.26 cannot sit under an interval that starts at +0.03" is not a theorem.** The
   rigorous bound is about −0.62. The claim is now stated as a tension, and the one row that has no
   internal contradiction at all is named as such.

It also found that we had written the Δ miss as "1.3050" in a table, which rounds away the very digit
that decides it; that "fourteen of fifteen models" was eleven; that the dw-dr naming mismatch is
internal to the paper rather than a deposit quirk; and that the blind run reads its chains from this
folder, so "no access to this folder" had to become "no access to our scripts, claims or results".

This is the third report in a row where the review moved a number in the header. It is also the
second where the frozen rule turned out to be wrong about the paper rather than the paper being wrong
about itself.

## 10. Files

- `claims.json`, `claims.sha256`, `claims.frozen_at.txt` — frozen before any chain was opened
- `table4_extraido.json` — Table 4 as parsed from the paper's LaTeX, 15 models and 71 parameter rows
- `scripts/00_table4.py` — the parser
- `scripts/01_claims.py` — builds and freezes the claims
- `scripts/02_recount.py` — the recount, with the restricted unpickler
- `scripts/03_score.py` — scores the 112 primary claims against the chains
- `scripts/04_anomalias.py` — measures the findings of §4 and §5
- `REVIEW.md` — the adversarial review of this report
- `../2023-afzal-nanograv15-newphysics-cego/` — the second run, with its own frozen pre-registration
- `runs/out/` — one summary per chain file, plus `score_primary.json` and `anomalias.json`
- `data/README.txt` — where every byte came from, with sizes and checksums

The chains are not redistributed. Nothing here has been sent to the authors or published anywhere.
