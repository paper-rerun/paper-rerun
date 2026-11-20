# Notes on the deposit and the analysis code

Written while the HMM trained. Everything here is independent of my own results.

## 1. The deposited TDE-HMM is not the model behind Figure 4

`downloads/trained_tde_hmm.zip` unpacks to a model whose `config.yml` says
`n_states: 12`, and whose `covs.npy` has shape (12, 80, 80). The paper's own script,
`examples/toolbox_paper/ctf_rest/tde_hmm_networks.py`, trains with `n_states: 8`, and
Figure 4 shows 8 states. So the deposit's trained HMM cannot be the one that produced
Figure 4, and it cannot be used to reproduce the young-vs-old state statistics.

`downloads/inf_tde_hmm_5subj.zip` does contain an 8-state `alp.pkl`, but for 5 subjects
(shapes (72000, 8), (72000, 8), (74000, 8), (74000, 8), (74000, 8)). The group comparison
needs all 65. So that archive is a demo, not the inferred parameters behind Figure 4.

Net effect: reproducing Figure 4BI requires retraining. The authors train 10 runs and
analyse the one with the lowest variational free energy, so even an exact rerun is a
draw from a distribution, not a replay.

## 2. The deposited DyNeMo has the wrong number of modes and no model

`downloads/tde_dynemo_20_runs.zip` contains only `covariances.npy` of shape
(20, 6, 80, 80), `free_energy.npy` of shape (20,) and `pca_components.npy`. That is
**6 modes**, across 20 runs. The paper analyses a **7-mode** fit
(`tde_dynemo_networks.py` sets `n_modes: 7`, and the text says "the 7-mode fit in
Figure 5"). There are no model weights and no inferred mode time courses, so the
DyNeMo summary statistics (mean and standard deviation of the renormalized mode time
course) cannot be recovered from the deposit at all - not even for the 6-mode runs.

## 3. The published scripts swap the Young and Old labels on the figures

In both `tde_hmm_networks.py` and `tde_dynemo_networks.py`:

```python
assignments = np.ones_like(age)
# Subjects with age > 34 are assigned to the old group
# and age <= 34 are assigned to the young group
for i, a in enumerate(age):
    if a > 34:
        assignments[i] += 1
```

so `1` is young and `2` is old. Then, in `compare_summary_stats`:

```python
group = ["Old" if a == 1 else "Young" for a in assignments]
```

which labels the **young** subjects "Old" and the old subjects "Young". That list is
passed straight to `plotting.plot_summary_stats_group_diff(..., assignments=group)`,
where it becomes the seaborn `hue` column, i.e. the violin plot's legend. So the
Young/Old legend in Figure 4BI and Figure 5BI is inverted.

The swap is present in the v2.0.0 tag as well as current `main`, and the deposited
model reports `osl-dynamics version: 2.0.dev3`, so this is the code that made the
published figures, not a later regression.

This does not touch the p-values - `stats.group_diff` gets the numeric `assignments`,
not the string labels - but every directional statement in the paper's text
("increased in the older group", "decreased in the older group") appears to have been
read off those figures. If the legend is inverted, the stated directions are at risk of
being inverted too. My own `copes` are signed young-minus-old, computed from the numeric
assignments, so they settle the direction independently.

## 4. The ages in demographics.csv are banded, not the stated ranges

`training_data/demographics.csv` has 65 rows and exactly seven distinct ages:
21, 27, 33, 39, 45, 51, 60. These look like band midpoints from the MEGUK release, not
individual ages. Consequences for the paper's wording:

- "young (18-34 years old)": the realised young ages are 21 to 33. Nobody is 18, 19, 20,
  22-26, 28-32 or 34.
- "old (34-60 years old)": the realised old ages are 39 to 60. Nobody is 34 to 38.
- No subject sits on the 34 boundary, so the script's `age > 34` cut is unambiguous.

The counts the cut produces are 27 young and 38 old, matching the paper exactly.
