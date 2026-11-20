# osl-dynamics (Gohil et al. 2024) — reproduction report

- Paper: C. Gohil, R. Huang, E. Roberts, M. W. J. van Es, A. J. Quinn, D. Vidaurre, M. W. Woolrich, *osl-dynamics, a toolbox for modeling fast dynamic brain activity*, eLife 12:RP91949 (2024). DOI 10.7554/eLife.91949. Text read from the Europe PMC XML of PMC10945565, because eLife's own HTML returns a 232-byte bot challenge to automated fetches.
- Data: the authors' OSF deposit, `https://osf.io/by2tc/`. No login, no click-through, TLS verification on. Sizes and sha256 in `data/README.txt`.
- Code: the authors' own, `OHBA-analysis/osl-dynamics` (Apache-2.0), at 3.8.2, driven through `run_pipeline` with their config from `examples/toolbox_paper/ctf_rest/tde_hmm_networks.py`.
- Target: the seven claims frozen in `claims.json`, SHA-256 `e1df8bd22acf7a57271d2f4f44604a4291b79a6b360be36ec6108d0870a29a6c`, frozen at 2026-11-20T04:50:11Z, before anything was computed.
- Verdict: **Partially reproduced** — the effects reproduce, the directions do not. The four group differences of section 2.3 come out at the metrics and networks the paper names, at p<0.05, with every sign inverted relative to the text. The cause is a Young/Old label swap in the authors' own published script, the one the caption of Figure 4 links to. The group sizes reproduce exactly. The DyNeMo claims cannot be recomputed from the deposit.
- Date: 2026-11-20
- Hardware: Ryzen 9 3900X, 64 GB, CPU only, idle priority. The GPU was not touched.
- Wall clock: 1802 s to train one 8-state TDE-HMM, seconds for the permutation tests. Folder 367 KB plus a 684 MB download.

Two runs reached this independently, from the same public data: separate pre-registrations,
separate scripts, separate readings. The second had no access to the first; its own frozen
pre-registration is `blind/PREREGISTRATION.md`, sha256 `ed8343e5…`.

---

## 1. What the paper says

Section 2.3, the four quantitative statements:

> We see the fractional occupancy and switching rate of the sensorimotor network (state 4) is
> increased in the older group (p<0.05).

> The mean lifetime of the visual network (state 6) is also decreased in the older group (p<0.05).

> The older group also has a wider distribution of mean intervals for the default mode network
> (state 1) and suppressed state (8) (p<0.05).

Plus the group definition — 27 young (18–34) and 38 old (34–60), 65 subjects — and, in section
2.5, the interpretation they feed:

> Looking at the dynamic network perspective provided by the TDE-HMM, we see an increase in the
> fractional occupancy of state 4 (Figure 4BI) […] the increase in static β-power and
> connectivity with age can be linked to a larger fraction of time spent in the sensorimotor
> network.

## 2. What we measured

One 8-state TDE-HMM, trained with the authors' own config through `run_pipeline`, CPU only,
1802 s. Group test `osl_dynamics.stats.group_diff`, 1000 permutations, max-statistic over
states and metrics, as the paper describes. The function takes no seed, so every test was run
three times; the three runs agree on every verdict and move in the third decimal of p.

Contrast is Group_1 − Group_2, and group 1 is the **young** one.

| cell | young | old | young − old | p (3 runs) | paper says |
|---|---|---|---|---|---|
| fractional occupancy, state 4 | 0.1556 | 0.1239 | **+0.0317** | 0.029 / 0.026 / 0.022 | higher in old |
| switching rate, state 4 | 2.4442 | 1.9676 | **+0.4766** | 0.036 / 0.033 / 0.038 | higher in old |
| mean lifetime, state 6 | 0.0602 | 0.0672 | **−0.0069** | 0.032 / 0.033 / 0.032 | lower in old |
| mean interval, state 2 | 1.4797 | 0.9871 | **+0.4926** | 0.044 / 0.046 / 0.041 | — |
| mean interval, state 3 | 2.1361 | 1.4993 | **+0.6368** | 0.012 / 0.011 / 0.010 | — |

State identity was established from the data, not from the index: recomputing the per-parcel
Welch PSD over each state's Viterbi time points, state 4 is the sensorimotor-beta network
(excess +0.081, peak 19 Hz) and state 6 is the visual-alpha one. The first three rows are
therefore the paper's own three cells, at the paper's own networks, with the sign inverted.

The mean-interval claim reproduces as a **pattern** and not by index. The paper names states 1
and 8; our fit has exactly two significant mean-interval states, and they are numbered 2 and 3.
State numbering is arbitrary per fit, so that is the expected outcome. What matters is the
direction, and it is inverted there too: the intervals are *shorter* in the old group, not
wider. The blind run, identifying states anatomically, found the same thing — exactly two
significant states, one of them the suppressed state, 2.069→1.470 s (p=0.012, sd ratio 0.42)
and 1.493→0.988 s (p=0.040, sd ratio 0.62).

One honest mismatch of count: our fit has a sixth cell near threshold that the figure does not
star — switching rate of state 3, p = 0.047 / 0.053 / 0.044. Six cells against five stars.

The 8-state solution is stable across fits: free energies 110.2028 / 110.2020 / 110.2018, the
same eight networks to three decimals of their regional signature, the same significant cells,
the same directions.

## 3. Why the directions are inverted

### The code

`examples/toolbox_paper/ctf_rest/tde_hmm_networks.py`, line 48 at tag v2.0.0 and line 50 on
current `main`:

```python
group = ["Old" if a == 1 else "Young" for a in assignments]
```

`load_group_assignments`, directly above, builds `assignments` with `np.ones_like(age)` and
adds 1 where `age > 34`. So **1 is young and 2 is old**, and the line above names every young
subject "Old" and every old subject "Young". That list goes to
`plotting.plot_summary_stats_group_diff` as the seaborn `hue` column — it is the violin legend
and nothing else; neither tag's plotting function re-sorts or re-maps it. `tde_dynemo_networks.py`
carries the identical line at line 46.

The p-values are computed from the numeric `assignments`, not from this list, so they are
unaffected. Only the names are wrong.

Three things tie this to the published figure:

- The **caption of Figure 4 links to the script by URL**: "The script used to generate the
  results in this figure is here: …/examples/toolbox_paper/ctf_rest/tde_hmm_networks.py".
- The deposited model reports `osl-dynamics version: 2.0.dev3`, and the line is present at
  v2.0.0.
- The **colour order is derivable**. Seaborn orders hue levels by first appearance; subject00
  is 39 years old, so the first label emitted is "Young" (for an old subject), which makes
  "Young" level 0 and therefore blue. That is the order the published legend shows.

That is a strong inference, not a proof — the figure is consistent with this script, and we
cannot rule out that it was made from a different working copy.

### The authors' other script codes the groups the opposite way

`static_networks.py`, which makes Figure 6, assigns `old = 1, young = 2` in its own comment and
uses `if a < 34` to do it — the mirror image of `tde_hmm_networks.py`. Its contrast is labelled
"group 1 (old) minus group 2 (young)". So the two scripts in the same folder use opposite
conventions for the same two groups, which is the kind of thing a label swap grows out of. It
also means Figure 6 really is old−young, and the static result there is sound.

### The figure

Figure 4BI, fetched at 2400 px from the eLife IIIF endpoint. Legend: blue = Young, orange =
Old. Starred: fractional occupancy and switching rate at state 4, mean lifetime at state 6,
mean interval at states 1 and 8. At the starred state 4 of the fractional-occupancy panel the
orange half sits visibly above the blue half.

A violin plot does not support reading values to three decimals, so the comparison is made at
the level a violin can carry — where the body sits, and how far the tail runs:

| starred panel | the blue "Young" body sits at | our **old** group's median |
|---|---|---|
| fractional occupancy, state 4 | ≈0.115 | 0.1214 |
| switching rate, state 4 | ≈1.85 | 1.8932 |
| mean interval, state 1 | ≈1.3 | 1.3968 |
| mean interval, state 8 | ≈0.8 | 0.8395 |

and on the mean-interval panels the orange "Old" violins run out to long tails, ≈5.8 and ≈4.3,
in the range of our **young** group's longest intervals (maxima 5.152 and 3.323), while the
blue "Young" bodies are compact. The violin printed as "Young" carries the old group's
distribution and vice versa, on every starred panel.

### A control with no HMM in it

Static sensorimotor beta power, straight from the raw parcel time courses, same group
assignment, no model: young 0.1428, old 0.1815, p=0.000858, r(age) = **+0.4332**. That is the
well-known ageing effect, and it is the same direction the authors' own Figure 6 reports with
their old−young coding. So the group we call old really is the older one, and the inversion is
not ours.

## 4. What this does to the argument

Section 2.5 reads the static beta increase as more time spent in the sensorimotor network. As
measured, static sensorimotor beta rises with age (r = +0.43) while that network's fractional
occupancy falls with age (r = −0.38). The link the sentence draws runs the other way from the
data under it.

Two correlations on 65 subjects are not a strong instrument on their own; what makes this more
than a quibble is that both of them are *our* measurements of *their* data with *their* group
rule, and the second one is the quantity the sentence is about. The paper's own stated
alternative, one paragraph earlier — "the power within a network could be altered" — is the one
left standing.

This is a statement about the paper's text, not about the toolbox. The pipeline ran as
documented and the numbers it produces are stable.

## 5. What could not be checked, and why

**DyNeMo (the two claims about mode statistics and the p<0.01 comparison).** Not recomputable
from the deposit. `tde_dynemo_20_runs.zip` holds `covariances.npy` of shape (20, **6**, 80, 80)
— six modes, where the script sets `n_modes: 7` and the text analyses the 7-mode fit — plus
free energies and PCA components, and no model weights or mode time courses. The summary
statistics the claims are about cannot be recovered for any mode count. Training a 7-mode
TDE-DyNeMo from scratch measured at ≈34 min/epoch × 40 epochs ≈ 22 h per run on CPU, against a
protocol calling for the best of ten; we stopped it rather than hold the machine for a day.

That said, the claims are not beyond reach, because the same swap is in `tde_dynemo_networks.py`
and Figure 5BI is legible the same way: orange above blue at mode 4, below at mode 5 of the
standard-deviation panel. The mechanism reaches the DyNeMo sentences even though the numbers
behind them do not.

**The deposited TDE-HMM is not the model behind Figure 4.** `trained_tde_hmm.zip` is
`n_states: 12` with `covs.npy` of shape (12, 80, 80); the script trains 8 and the figure shows
8. The only 8-state inferred parameters in the deposit, `inf_tde_hmm_5subj.zip`, cover 5
subjects of 65. Figure 4BI therefore cannot be reproduced without retraining — and retraining
is stochastic, since the authors themselves fit ten models and analyse the lowest-free-energy
one.

**The deposited HMM cannot be applied to the deposited data.** `trained_tde_hmm.zip` omits
`pca_components.npy`, which the DyNeMo archive does include. Re-deriving the PCA recovers the
*subspace* almost exactly (60 of 80 principal-angle cosines above 0.99) but not the *basis
within it* (median per-component |cos| 0.15, against the DyNeMo deposit's basis), because the
eigenvalues are near-degenerate. Covariances do not survive that rotation. We did run the
12-state deposited model against the data anyway (`runs/deposit12/`); it returns a null result,
which is what a rotated basis produces whether or not there is an effect, so it is reported
here as uninformative rather than as evidence. Shipping `pca_components.npy` in every model
archive would close this.

**"State 1 = default mode network."** Unverified in both directions. No state in any of the
fits carries a meaningful midline-DMN alpha excess. The suppressed state was identified; its
partner was not.

## 6. What reproduces

- **Group sizes, exactly.** 27 young and 38 old from 65 subjects, applying the authors' own
  `age > 34` rule to `demographics.csv`.
- **Recording length.** 271–305 s per subject, against a stated 5 min.
- **Lifetimes in the 50–100 ms window.** 8 of 8 states, in all three fits.
- **The state solution itself.** Three fits, free energies within 0.001 of each other, the same
  eight networks. This supports the reproducibility supplements the paper shows.

## 7. One thing that does not reproduce quietly: the age ranges

The paper and the figure caption both say 18–34 and 34–60. `demographics.csv` holds seven
banded values — 21, 27, 33, 39, 45, 51, 60 — so the realised groups are **21–33** and
**39–60**. Nobody in the dataset is 18, nobody is 34, and there is an empty gap from 33 to 39.
Those are recruitment bands printed as if they described the sample. It changes nothing in the
statistics; it will mislead anyone sizing a replication.

## 8. Our own errors and limits, for the record

**An inverted label of our own.** The first pass of `04_stats.py` printed the contrast as
`cope(old-young)` when `group_diff` returns Group_1 − Group_2 and group 1 is the young one. The
number was right and the label was inverted — the same class of error as the one this report is
about, found in our own code, by the second run disagreeing with us on sign. Fixed; the table
in section 2 carries the corrected label.

**Three fits, not four.** Our run and the blind run's first run both called
`set_random_seed(1)` and produced the identical model: free energy 110.20281682757752 in both,
identical copes. The two runs are independent in protocol, scripts and reading, not in that
model. The blind run's other two fits are genuine separate draws and agree, so the finding does
not rest on the shared one — but the word "independent" applies to the analysis, not to four
models.

**The frozen claims assumed a replay we could not do.** They assumed the deposited model could
be loaded and scored. It cannot, for the reasons in section 5, so five of the seven frozen
claims are answered by retraining rather than by replay. That is a weaker test than the one we
froze and it is marked as such throughout.

**Version drift, unmeasured.** We ran osl-dynamics 3.8.2; the deposit was made with 2.0.dev3.
We did not measure what changed between them.

## 9. Files

- `claims.json`, `claims.sha256`, `claims.frozen_at.txt` — frozen before any analysis
- `scripts/01_groups.py` … `05_score.py` — groups, deposit audit, training, statistics, scoring
- `runs/out/` — `groups.json`, `model_audit.json`, `train_seed01.json`, `stats_seed01.json`
- `runs/logs/` — training and statistics logs
- `REVIEW.md` — adversarial review of this report's first draft
- `blind/` — the second run: its frozen `PREREGISTRATION.md` and `FREEZE.txt`, its `REPORT.md`,
  its `DEPOSIT_NOTES.md`, its scripts and its logs

Nothing here has been sent to the authors or published anywhere.
