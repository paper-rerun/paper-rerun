"""Summary statistics and the young-vs-old test, for one trained run.

This is compare_summary_stats from examples/toolbox_paper/ctf_rest/tde_hmm_networks.py,
with two things added, both declared in claims.json before anything was computed:

  - the permutation test is run three times, because it is random and group_diff takes no
    seed, and a claim only counts if all three land on the same side of the threshold;
  - the same statistics are also computed from the state probabilities directly instead of
    the Viterbi path, because the paper does not say which it used.

Usage: python scripts/04_stats.py <seed>
"""

import os
import sys
import json
import pickle

import numpy as np
import pandas as pd

from osl_dynamics import stats
from osl_dynamics.inference import modes

seed = int(sys.argv[1])
output_dir = f"runs/hmm/seed{seed:02d}"
SAMPLING_FREQUENCY = 250
N_PERM = 1000
N_REPEATS = 3

STAT_NAMES = ["fractional_occupancy", "mean_lifetime", "mean_interval", "switching_rate"]


def load_group_assignments():
	"""Their load_group_assignments, copied."""
	demographics = pd.read_csv("training_data/demographics.csv")
	age = demographics["age"].values
	assignments = np.ones_like(age)
	for i, a in enumerate(age):
		if a > 34:
			assignments[i] += 1
	return assignments


def summary_stats_from_time_courses(stc):
	"""The four statistics their script computes, in their order."""
	fo = modes.fractional_occupancies(stc)
	lt = modes.mean_lifetimes(stc, sampling_frequency=SAMPLING_FREQUENCY)
	intv = modes.mean_intervals(stc, sampling_frequency=SAMPLING_FREQUENCY)
	sr = modes.switching_rates(stc, sampling_frequency=SAMPLING_FREQUENCY)
	return np.swapaxes([fo, lt, intv, sr], 0, 1)


def test_groups(sum_stats, assignments, n_states):
	"""Run their group_diff call N_REPEATS times and keep every p-value."""
	runs = []
	for repeat in range(N_REPEATS):
		# group_diff takes no seed; seeding numpy covers it if it draws from the global
		# RNG, and if it does not, the repeats still measure the spread.
		np.random.seed(1000 + repeat)
		result = stats.group_diff(data=sum_stats, assignments=assignments, n_perm=N_PERM)
		runs.append({
			"pvalues": result.pvalues.reshape(4, n_states).tolist(),
			"copes": np.asarray(result.copes).reshape(4, n_states).tolist(),
		})
	return runs


assignments = load_group_assignments()
is_old = assignments == 2

alpha = pickle.load(open(f"{output_dir}/inf_params/alp.pkl", "rb"))
stc = modes.argmax_time_courses(alpha)
n_states = alpha[0].shape[-1]

readings = {}

# Primary reading: the Viterbi path, which is what their script uses
sum_stats = summary_stats_from_time_courses(stc)
readings["viterbi"] = {
	"group_means_old": np.asarray([s[is_old].mean(axis=0) for s in [sum_stats[:, i] for i in range(4)]]).tolist(),
	"group_means_young": np.asarray([s[~is_old].mean(axis=0) for s in [sum_stats[:, i] for i in range(4)]]).tolist(),
	"sd_ratio_old_over_young": np.asarray([
		sum_stats[:, i][is_old].std(axis=0, ddof=1) / sum_stats[:, i][~is_old].std(axis=0, ddof=1)
		for i in range(4)
	]).tolist(),
	"tests": test_groups(sum_stats, assignments, n_states),
}

# Secondary reading declared in advance: soft state probabilities, no hard assignment.
# Two statistics here, not four, so this gets its own loop instead of their reshape.
soft = np.swapaxes([
	np.asarray([a.mean(axis=0) for a in alpha]),   # expected occupancy
	np.asarray([a.std(axis=0) for a in alpha]),    # how much it moves
], 0, 1)
soft_tests = []
for repeat in range(N_REPEATS):
	np.random.seed(2000 + repeat)
	result = stats.group_diff(data=soft, assignments=assignments, n_perm=N_PERM)
	soft_tests.append({
		"pvalues": np.asarray(result.pvalues).tolist(),
		"copes": np.asarray(result.copes).tolist(),
	})
readings["soft_probabilities"] = {
	"stat_names": ["expected_occupancy", "sd_of_state_probability"],
	"shape": list(soft.shape),
	"tests": soft_tests,
}

# Levene on the mean intervals, the "wider distribution" reading
from scipy.stats import levene
intervals = sum_stats[:, 2]
readings["levene_on_mean_intervals"] = [
	{
		"state": int(s + 1),
		"statistic": float(levene(intervals[is_old, s], intervals[~is_old, s]).statistic),
		"pvalue": float(levene(intervals[is_old, s], intervals[~is_old, s]).pvalue),
		"sd_old": float(intervals[is_old, s].std(ddof=1)),
		"sd_young": float(intervals[~is_old, s].std(ddof=1)),
	}
	for s in range(n_states)
]

out = {
	"seed": seed,
	"n_states": int(n_states),
	"n_perm": N_PERM,
	"n_repeats": N_REPEATS,
	"stat_names": STAT_NAMES,
	"readings": readings,
}
with open(f"runs/out/stats_seed{seed:02d}.json", "w") as fh:
	json.dump(out, fh, indent=1)

# The contrast is Group_1 - Group_2, and group 1 is the young one, so a positive cope means young above old
# Print the four cells the paper names
print(f"seed {seed}, {n_states} states, p-values from {N_REPEATS} runs of the permutation test")
for name, state in [("fractional_occupancy", 4), ("switching_rate", 4), ("mean_lifetime", 6), ("mean_interval", 1), ("mean_interval", 8)]:
	i = STAT_NAMES.index(name)
	s = state - 1
	ps = [r["pvalues"][i][s] for r in readings["viterbi"]["tests"]]
	cope = readings["viterbi"]["tests"][0]["copes"][i][s]
	print(f"  state {state} {name}: cope(young-old) = {cope:+.5f}, p = {['%.4f' % p for p in ps]}")
