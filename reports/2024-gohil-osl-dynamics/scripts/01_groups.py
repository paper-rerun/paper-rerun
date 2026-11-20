"""Group sizes and age ranges, straight from the demographics file the data ships with.

Claim C6, plus the secondary reading declared in claims.json: the paper prints
"young (18-34 years old)" and "old (34-60 years old)", two ranges that both contain 34.
"""

import json
import numpy as np
import pandas as pd

DEMOGRAPHICS = "training_data/demographics.csv"
OUT = "runs/out/groups.json"

demographics = pd.read_csv(DEMOGRAPHICS)
age = demographics["age"].values

# This is their load_group_assignments, copied: old if over 34, young otherwise
assignments = np.ones_like(age)
for i, a in enumerate(age):
	if a > 34:
		assignments[i] += 1

is_old = assignments == 2
n_old = int(is_old.sum())
n_young = int((~is_old).sum())

result = {
	"n_subjects": int(len(age)),
	"n_young": n_young,
	"n_old": n_old,
	"published_n_young": 27,
	"published_n_old": 38,
	"C6_reproduces": n_young == 27 and n_old == 38,
	"young_age_range": [float(age[~is_old].min()), float(age[~is_old].max())],
	"old_age_range": [float(age[is_old].min()), float(age[is_old].max())],
	"published_young_range": [18, 34],
	"published_old_range": [34, 60],
	"n_subjects_aged_exactly_34": int((age == 34).sum()),
	"empty_gap_between_groups": [float(age[~is_old].max()), float(age[is_old].min())],
}

with open(OUT, "w") as fh:
	json.dump(result, fh, indent=1)
for k, v in result.items():
	print(f"{k}: {v}")
