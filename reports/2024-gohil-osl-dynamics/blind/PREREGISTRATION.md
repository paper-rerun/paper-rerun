# Pre-registration - blind reproduction of Gohil et al. 2024, osl-dynamics (eLife 12:RP91949)

Written 2026-11-20, before any computation. Source of all quotes: Europe PMC full text
of PMC10945565 (saved here as fulltext.xml, sha256 recorded in FREEZE.txt).

Scope, as set by the task: the "dynamic network analysis" young-vs-old comparison on the
CTF rest MEG dataset (TDE-HMM state statistics), the DyNeMo-vs-HMM comparison, the group
sizes and the stated age ranges. The static-network section (Figure 6) is out of scope.

## What the deposit does and does not give me (established before freezing)

- training_data/networks/ has 65 subjects, 250 Hz, source-reconstructed parcel time courses.
- downloads/trained_tde_hmm.zip (= tde_hmm_notts_meguk_giles) is an **n_states: 12** model
  (config.yml, covs.npy shape (12,80,80)). The paper's own script asks for n_states: 8.
  So the deposit does NOT contain the model behind Figure 4.
- downloads/inf_tde_hmm_5subj.zip has an 8-state alp.pkl but for **5 subjects only**, not 65.
- downloads/tde_dynemo_20_runs.zip has covariances.npy of shape (20, 6, 80, 80) and
  free_energy.npy only: **6 modes**, no model weights, no alphas. The paper analyses a
  **7-mode** DyNeMo fit.

Consequence, declared in advance: to test the HMM claims I must train an 8-state TDE-HMM
myself, following examples/toolbox_paper/ctf_rest/tde_hmm_networks.py. HMM training is
stochastic (random init, the authors themselves pick the best of 10 runs by free energy),
so a single run of mine is one draw from that distribution, not a deterministic replay.
I declare before computing that I will train a small number of runs and report every one,
and that disagreement on an individual state label is weak evidence either way.

State indices are only defined up to permutation across runs. I therefore pre-register
**pattern-level primary readings** (how many states, which metric, which direction) and
treat the paper's state numbering (state 4, state 6, state 1, state 8) as secondary,
checkable only if I can independently identify the network from its power/coherence map.

## Claims

### C1 - group sizes
Quote: "we compared two groups: 27 subjects in a young group (18-34 years old) and 38
subjects in an old group (34-60 years)."
Test: apply the authors' own rule from tde_hmm_networks.py (if a > 34: old) to
training_data/demographics.csv and count. Primary: the two counts are 27 and 38.

### C2 - dataset size and age range
Quote: "This dataset contains 5 min recordings from 65 healthy participants."
Quote (Figure 4 caption): "a young (18-34 years old) and old (34-60 years old) group".
Test: number of subject files and demographics rows = 65; min and max age in the young
bin fall inside [18, 34]; min and max age in the old bin fall inside [34, 60]. Primary:
no subject's age falls outside [18, 60], and the realised bin edges match the stated ones.
Secondary: recording length of each networks/subjectNN.npy at 250 Hz is near 5 min.

### C3 - fractional occupancy of the sensorimotor state increased in old
Quote: "We see the fractional occupancy and switching rate of the sensorimotor network
(state 4) is increased in the older group (p<0.05)."
Primary reading: in my trained 8-state model there is **at least one state whose fractional
occupancy is significantly higher (p<0.05, max-statistic permutation over states and the
four metrics, as the paper states) in the old group**, with the old-minus-young contrast
positive. Secondary: that state is the sensorimotor network (beta-dominant, sensorimotor
parcels) and/or carries index 4.

### C4 - switching rate of the same state increased in old
Same quote as C3.
Primary reading: the **same** state as in C3 also shows a significantly higher switching
rate in the old group (p<0.05, same max-statistic correction).

### C5 - mean lifetime of the visual state decreased in old
Quote: "The mean lifetime of the visual network (state 6) is also decreased in the older
group (p<0.05)."
Primary reading: at least one state shows a significantly **lower** mean lifetime in old
(p<0.05, same correction), and it is a different state from C3/C4. Secondary: it is the
visual network and/or index 6.

### C6 - "wider distribution of mean intervals" for two states
Quote: "The older group also has a wider distribution of mean intervals for the default
mode network (state 1) and suppressed state (8) (p<0.05)."
This is the loose claim. Decided in advance:
- **Primary reading**: exactly two states show a significant (p<0.05, same max-statistic
  correction) group effect on **mean interval**. I treat the authors' own test - the one
  their script runs, a difference of group means via osl_dynamics.stats.group_diff -
  as the primary statistic, because that is what their asterisk marks.
- **Secondary reading**: for those states, sd(mean interval | old) / sd(mean interval |
  young) > 1, i.e. the old distribution is literally wider. Reported separately; a
  mismatch here is a wording problem in the paper, not a failed reproduction of the test.

### C7 - state lifetimes 50-100 ms
Quote: "with lifetimes of 50-100 ms" (Figure 4AIII).
Primary: the across-subject mean of mean lifetime, per state, lies in [0.050, 0.100] s for
the majority (>= 5 of 8) of states.

### C8 - DyNeMo mode 4 mean increased in old, p<0.01
Quote: "We can see an increased mode contribution (mean renormalized mode time course) for
the sensorimotor network (mode 4) ... We see DyNeMo is able to reveal a stronger effect
size with a p<0.01 compared to the TDE-HMM, which had a p<0.05."
Primary: at least one mode shows a significantly increased mean renormalized mode time
course in old at p<0.01.

### C9 - DyNeMo mode 5 standard deviation decreased in old, p<0.01
Quote: "DyNeMo also shows a decrease in the variability (standard deviation of the
renormalized mode time course) for the left temporal network (mode 5, p<0.01)."
Primary: at least one mode shows a significantly decreased sd of its renormalized mode
time course in old at p<0.01.

### C10 - DyNeMo beats the HMM on this downstream task
Quote: "We argue a better performance in the downstream task indicates a more useful model."
plus the p<0.01 vs p<0.05 sentence above.
Primary: the smallest corrected p-value over DyNeMo summary statistics is smaller than the
smallest corrected p-value over HMM summary statistics, on the same subjects and groups.

## Analysis choices fixed in advance

- Interpreter: E:\Ciencia\noturno\2024-gohil-osl-dynamics\venv\Scripts\python.exe, CPU only.
- Data prep, exactly as the authors' config: sampling_frequency 250, Giles 38-parcel
  parcellation, tde_pca {n_embeddings: 15, n_pca_components: 80}, standardize.
- HMM: n_states 8, learn_means False, learn_covariances True, otherwise osl-dynamics defaults
  (as the authors' config leaves them).
- Summary statistics from the Viterbi path (modes.argmax_time_courses on the inferred alpha),
  then modes.fractional_occupancies / mean_lifetimes / mean_intervals / switching_rates.
- Group test: osl_dynamics.stats.group_diff with n_perm 1000, assignments from the authors'
  age > 34 rule. This is the max-statistic permutation test the paper describes.
- Significance threshold 0.05 for the HMM claims, 0.01 for the DyNeMo claims, as quoted.
- If a verdict depends on which training run I look at, I report all runs and call the claim
  reproduced only if it holds in the run with the lowest variational free energy (the
  authors' own selection rule), noting the spread.

## Verdict vocabulary

reproduced / not reproduced / partially reproduced / not checkable, with the reason stated
for every not-checkable.
