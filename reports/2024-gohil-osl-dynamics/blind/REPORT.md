# Blind reproduction report

Gohil et al., "osl-dynamics, a toolbox for modeling fast dynamic brain activity",
eLife 12:RP91949 (2024), doi 10.7554/eLife.91949.

Done 2026-11-20 without looking at the parallel run. Claims were written down and frozen
in PREREGISTRATION.md (sha256 in FREEZE.txt) before anything was computed. Everything
below follows that pre-registration; where I had to decide something it was decided there.

## Headline

The dynamic young-vs-old analysis does reproduce numerically - same effects, same states,
same metrics, p-values in the same range - but every direction in the paper's text is the
opposite of what the data say. I traced that to a label swap in the authors' own published
script, and then confirmed it against the published Figure 4 itself: the violins printed
under "Young" hold the old subjects and vice versa, and their heights match my measured
group means to about three decimal places.

The DyNeMo claims could not be checked at all.

## What I ran

- Data: training_data/networks (65 subjects, 250 Hz, 38 Giles parcels), prepared exactly
  as the authors published it in examples/toolbox_paper/ctf_rest/tde_hmm_networks.py
  (tde_pca with n_embeddings 15 and n_pca_components 80, then standardize).
- Model: 8-state TDE-HMM, learn_means False, learn_covariances True, otherwise the
  toolbox defaults from train_hmm (sequence_length 200, batch_size 256, lr 0.01,
  20 epochs, 5 inits of 2 epochs). osl-dynamics 3.8.2, TensorFlow 2.19.1, CPU only.
- Three runs, seeds 1-3. Free energies 110.2028, 110.2020, 110.2018. The authors pick the
  best of ten by free energy; by that rule my best run is run03, reported as primary. All
  three runs found the same solution up to a permutation of state labels, with the same
  effects and the same directions, so the choice does not matter.
- Group test: osl_dynamics.stats.group_diff, 1000 permutations, max-statistic correction
  pooled over states and metrics (the default, and what the paper describes). Group
  assignment from the rule in the published script, age > 34 is old.
- States were named from the data, not from the state index: for each state I took the
  parcel time courses at the time points its Viterbi path occupies, computed a Welch PSD
  per parcel, and measured band power in anatomical ROIs defined from the MNI centroids of
  the Giles atlas. In every run exactly one state is strongly sensorimotor-beta
  (excess +0.08, PSD peak 19 Hz) and one is clearly visual-alpha (excess +0.20, peak
  10 Hz), so the identification is not ambiguous.

Files here: PREREGISTRATION.md, FREEZE.txt, DEPOSIT_NOTES.md, run_hmm.py,
identify_networks.py, summarize.py, deposit_model_check.py, runs/, figs/.

## Claim by claim

### C1 - group sizes: reproduced

Quote: "we compared two groups: 27 subjects in a young group (18-34 years old) and 38
subjects in an old group (34-60 years)."

Applying the age > 34 rule to demographics.csv: 27 young, 38 old. Exact.

### C2 - 65 participants, 5 min, stated age ranges: partially reproduced

Quote: "This dataset contains 5 min recordings from 65 healthy participants."
Quote: "a young (18-34 years old) and old (34-60 years old) group".

65 subject files and 65 demographics rows: correct. Recording lengths run 271 s to 305 s
(4.5 to 5.1 min), so "5 min" is fair.

The age ranges are not a description of the data. demographics.csv contains seven distinct
ages only - 21, 27, 33, 39, 45, 51, 60 - which look like band midpoints from the MEGUK
release rather than real ages. The realised young group is 21 to 33 and the realised old
group is 39 to 60. Nobody is 18, 19, 20, or anywhere from 34 to 38. The stated bounds do
not correspond to any subject. No subject sits on the 34 boundary, so the cut itself is
unambiguous and the counts come out right.

### C3 - sensorimotor fractional occupancy increased in the old group: not reproduced, direction reversed

Quote: "We see the fractional occupancy and switching rate of the sensorimotor network
(state 4) is increased in the older group (p<0.05)."

Pre-registered primary reading: at least one state shows a significantly higher fractional
occupancy in the old group.

Measured, best run (run03), state 5 = the sensorimotor-beta state (SM beta excess +0.081,
PSD peak 19 Hz):

| metric | young | old | p (max-stat) |
|---|---|---|---|
| fractional occupancy | 0.1556 | 0.1235 | 0.025 |

The effect is there, on the sensorimotor state, at the stated significance level - but it
goes down with age, not up. Same in the other two runs (0.1556 vs 0.1239, p=0.021;
0.1562 vs 0.1246, p=0.026). Continuous check with no binning: Pearson r between age and
that state's fractional occupancy = -0.381, p=0.0017.

Verdict: the statistical effect reproduces, the stated direction does not.

### C4 - switching rate of the same state increased in the old group: not reproduced, direction reversed

Same sentence as C3. Pre-registered primary reading: the same state also shows a
significantly higher switching rate in the old group.

Measured (run03, same state 5):

| metric | young | old | p |
|---|---|---|---|
| switching rate (Hz) | 2.447 | 1.964 | 0.043 |

Again the same state, again significant, again decreased in old. Runs 1 and 2:
2.444 vs 1.968, p=0.032; and 2.453 vs 1.979, p=0.043.

### C5 - visual mean lifetime decreased in the old group: not reproduced, direction reversed

Quote: "The mean lifetime of the visual network (state 6) is also decreased in the older
group (p<0.05)."

Pre-registered primary reading: at least one state, different from C3 and C4, shows a
significantly lower mean lifetime in old.

Measured (run03, state 7, the second visual state, visual alpha excess +0.081):

| metric | young | old | p |
|---|---|---|---|
| mean lifetime (s) | 0.0604 | 0.0675 | 0.028 |

A different state from the sensorimotor one, significant at p<0.05 - and increased in old.
Same in runs 1 and 2 (p=0.027 and p=0.043, both increases). The dominant visual-alpha
state (10 Hz peak, visual excess +0.20) shows no lifetime effect at all (p=0.95).

### C6 - old group has a wider distribution of mean intervals for two states: not reproduced

Quote: "The older group also has a wider distribution of mean intervals for the default
mode network (state 1) and suppressed state (8) (p<0.05)."

Pre-registered primary reading: exactly two states show a significant mean-interval effect
under the same test. That part holds. In every run exactly two states are starred on mean
interval, and one of them is unambiguously the suppressed state (the lowest-power state in
the model), matching "suppressed state (8)". The other is the highest-power broadband
state in my solution; I could not identify it as a default mode network, and the midline
DMN alpha excess of every state in my runs is near zero, so I can neither confirm nor deny
the "state 1 = DMN" half.

Measured (run03):

| state | young | old | p | sd(old)/sd(young) |
|---|---|---|---|---|
| highest-power state 2 | 2.069 s | 1.470 s | 0.012 | 0.420 |
| suppressed state 8 | 1.493 s | 0.988 s | 0.040 | 0.617 |

Pre-registered secondary reading, that the old distribution is literally wider: the sd
ratios are 0.42 and 0.62, so the old group distribution is narrower, not wider, and its
mean intervals are shorter. Both readings go against the paper.

### C7 - state lifetimes 50-100 ms: reproduced

Quote: "with lifetimes of 50-100 ms".

Across-subject mean of mean lifetime, run03, all eight states: 0.067, 0.087, 0.079, 0.067,
0.063, 0.056, 0.065, 0.083 s. 8 of 8 inside the 50-100 ms window, in all three runs. The
pre-registered bar was 5 of 8.

### C8, C9, C10 - the DyNeMo claims: not checkable

Quote: "We can see an increased mode contribution (mean renormalized mode time course) for
the sensorimotor network (mode 4) ... We see DyNeMo is able to reveal a stronger effect
size with a p<0.01 compared to the TDE-HMM, which had a p<0.05."
Quote: "DyNeMo also shows a decrease in the variability (standard deviation of the
renormalized mode time course) for the left temporal network (mode 5, p<0.01)."

Two independent reasons, both measured rather than assumed:

1. The deposit does not contain the fit. tde_dynemo_20_runs.zip holds only covariances.npy
   of shape (20, 6, 80, 80), free_energy.npy and pca_components.npy. That is 6 modes; the
   published script sets n_modes 7 and the text says "the 7-mode fit in Figure 5". There
   are no model weights and no inferred mode time courses, so the mean and standard
   deviation of the renormalized mode time course - the two statistics the claims are
   about - cannot be recovered from the deposit for any number of modes.

2. Retraining is out of budget on CPU. I started a 7-mode TDE-DyNeMo with the published
   config (40 epochs, 20 of them KL annealing, batch 128, 189 batches per epoch). It ran
   at roughly 11 s per batch, about 25 minutes per epoch, which projects to about 16 hours
   for one run on this machine, against a protocol that calls for the best of ten runs. I
   stopped it rather than occupy the machine for a day; the throughput measurement is in
   dynemo_throughput.txt.

So C8, C9 and C10 are honestly not checkable here. C10 in particular is a comparison of
two p-values, and since the HMM side of that comparison turns out to have its direction
reversed, the comparison would need re-reading even if the DyNeMo fit were available.

## Why the directions are reversed: the figure legend is swapped

This is the main finding, and it does not depend on my model at all.

### The code

In examples/toolbox_paper/ctf_rest/tde_hmm_networks.py, and identically in
tde_dynemo_networks.py, load_group_assignments returns 1 for young and 2 for old, as its
own comment says. Then compare_summary_stats does:

    group = ["Old" if a == 1 else "Young" for a in assignments]

which labels the young subjects "Old" and the old subjects "Young". That list goes
straight into plotting.plot_summary_stats_group_diff as the assignments argument, where it
becomes the seaborn hue column - that is, the violin plot legend. The swap is present in
the v2.0.0 tag as well as current main, and the deposited model reports
"osl-dynamics version: 2.0.dev3", so this is the code that made the published figures. It
does not affect the p-values, which are computed from the numeric assignments.

### The figure

I fetched Figure 4 and read panel B.I. The legend is blue = Young, orange = Old. Reading
the starred violins against my own measured group means:

| panel, starred state | published blue, labelled Young | published orange, labelled Old | my old | my young |
|---|---|---|---|---|
| fractional occupancy, state 4 | about 0.115 | about 0.155 | 0.124 | 0.156 |
| switching rate, state 4 | about 1.85 | about 2.4 | 1.96 | 2.44 |
| mean interval, states 1 and 8 | compact, centred about 1.3 and 0.8 | long tails to about 5.8 and 4.3 | 1.47 and 0.99, sd ratios 0.42 and 0.62 | 2.07 and 1.49 |

The violin printed as "Young" carries my old group numbers, and the violin printed as
"Old" carries my young group numbers, on all three panels. The published data and my data
are the same data; only the legend differs.

The text then reads the legend at face value: "increased in the older group", "decreased
in the older group", "the older group also has a wider distribution". All three are
inverted.

### A control that does not involve the HMM

Static sensorimotor beta power, computed directly from the raw parcel time courses with
the same group assignment, is higher in my old group: young 0.1428, old 0.1815, t-test
p=0.00086, Pearson r with age +0.433 (p=0.00031). That is the well-known ageing effect and
it matches the paper's own static result in Figure 6. So my old group really is the older
one, and the group labels in my analysis are the right way round.

### One consequence for the paper's argument

Section 2.5 explains the static increase in sensorimotor beta power with age as a longer
amount of time spent in the sensorimotor network, pointing at the increased fractional
occupancy of state 4. On the data as measured, static sensorimotor beta power goes up with
age (r=+0.43) while the sensorimotor state fractional occupancy goes down (r=-0.38). The
explanation as written does not follow. The paper's own alternative, that "the power
within a network could be altered", is the one left standing.

## Other things a reader of the paper would want to know

The deposited TDE-HMM is not the model behind Figure 4. trained_tde_hmm.zip, which is
tde_hmm_notts_meguk_giles, has n_states 12 in its config.yml and covs.npy of shape
(12, 80, 80). The published script trains 8 states and Figure 4 shows 8. The only 8-state
inferred parameters in the deposit, inf_tde_hmm_5subj.zip, cover 5 subjects, not 65. So
reproducing Figure 4BI requires retraining, and since the best of ten runs is selected by
free energy, no rerun is a replay. In my case it turned out not to matter - all three runs
converged to the same solution - but it is worth stating.

The deposited HMM cannot be applied to the deposited data. trained_tde_hmm.zip omits
pca_components.npy, which the Glasser archive m_tde_hmm_glasser.zip does include, so the
80-dimensional basis its covariances live in has to be re-derived. I tried: re-running the
prep gives a PCA whose subspace matches the one deposited alongside the DyNeMo runs almost
exactly (60 of 80 principal-angle cosines above 0.99, 78 above 0.9) but whose basis within
that subspace does not (median per-component absolute cosine 0.15, diagonal cosines 0.03
to 0.69). The eigenvalues are near-degenerate, so component identity and mixing differ
between osl-dynamics versions. A model covariance matrix is not portable across that
rotation, so deposit_model_check.py ran but its output is not usable and I am not
reporting it as evidence. Shipping pca_components.npy with every model archive would fix
this.

Reproducibility of the HMM solution itself is good. Three independent runs with different
seeds produced the same eight networks (identical ROI signatures to three decimals), the
same significant effects and the same directions, with free energies within 0.001 of each
other. That supports the reproducibility claim in the paper's supplementary figures.

## Summary table

| claim | verdict | note |
|---|---|---|
| C1 group sizes 27 and 38 | reproduced | exact |
| C2 65 subjects, 5 min, ages 18-34 and 34-60 | partially reproduced | 65 subjects and about 5 min fine; ages are 7 banded values from 21 to 60, nobody is 18-20 or 34-38 |
| C3 sensorimotor fractional occupancy up in old | not reproduced | same state, same p range (0.025), direction reversed: 0.1556 young vs 0.1235 old |
| C4 sensorimotor switching rate up in old | not reproduced | same state, p=0.043, direction reversed: 2.447 young vs 1.964 old |
| C5 visual mean lifetime down in old | not reproduced | a visual state is significant (p=0.028), direction reversed: 0.0604 young vs 0.0675 old |
| C6 mean intervals wider in old, two states | not reproduced | two states significant and one is the suppressed state, but intervals are shorter and narrower in old (sd ratios 0.42 and 0.62) |
| C7 lifetimes 50-100 ms | reproduced | 8 of 8 states, all runs |
| C8 DyNeMo mode mean up in old, p<0.01 | not checkable | deposit has 6 modes, no weights, no mode time courses; paper uses 7; retraining about 16 h per run on CPU |
| C9 DyNeMo mode sd down in old, p<0.01 | not checkable | same |
| C10 DyNeMo beats the HMM on this task | not checkable | same, and the HMM side of the comparison has its direction reversed |
