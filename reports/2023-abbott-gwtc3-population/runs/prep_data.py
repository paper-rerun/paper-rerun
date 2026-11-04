# Turn the published 'original' per-event arrays (exactly likelihood.data + sampling_prior of the PP run)
# into the input format gwpopulation_pipe_analysis reads: <run_dir>/data/posteriors.pkl (list of DataFrames)
# and posteriors_posterior_files.txt (event ids). Also cross-check the prior file against result.json.
import json
import os
import sys
import h5py
import numpy as np
import pandas as pd
from bilby.core.prior import PriorDict

base = "/mnt/e/Ciencia/noturno/2023-abbott-gwtc3-population"
published = base + "/sources/analyses/PowerLawPeak/o1o2o3_mass_c_iid_mag_iid_tilt_powerlaw_redshift"
run_dir = sys.argv[1]
os.makedirs(run_dir + "/data", exist_ok=True)

# Load event names in the order of the arrays
with h5py.File(published + "_samples.hdf5", "r") as samples_file:
    names_attrs = samples_file["names"].attrs
    event_names = [names_attrs["i%d" % index].decode() for index in range(69)]
    original = samples_file["original"]
    columns = ["mass_1", "mass_2", "mass_ratio", "a_1", "a_2", "cos_tilt_1", "cos_tilt_2", "redshift", "prior"]
    arrays = {key: original[key][()] for key in columns}

with open(published + "_result.json") as result_file:
    result = json.load(result_file)
assert event_names == result["meta_data"]["event_ids"], "event order differs from result.json"

posteriors = [pd.DataFrame({key: arrays[key][index] for key in columns}) for index in range(69)]
pd.to_pickle(posteriors, run_dir + "/data/posteriors.pkl")
with open(run_dir + "/data/posteriors_posterior_files.txt", "w") as names_file:
    for name in event_names:
        names_file.write(f"{name}:published_samples_hdf5\n")
print("events", len(posteriors), "samples each", {len(post) for post in posteriors}, "max z", max(post.redshift.max() for post in posteriors))

# Compare our prior file with the priors stored in the published result
ours = PriorDict(filename=base + "/data/pp_published.prior")
for key, stored in result["priors"].items():
    if key.startswith("__"):
        continue
    kwargs = stored["kwargs"]
    mine = ours[key]
    for field in ["minimum", "maximum", "peak", "boundary"]:
        if field in kwargs:
            assert getattr(mine, field) == kwargs[field] or (kwargs[field] is None and getattr(mine, field) is None), (key, field, getattr(mine, field), kwargs[field])
    assert type(mine).__name__ == stored["__name__"], (key, type(mine).__name__, stored["__name__"])
assert set(k for k in result["priors"] if not k.startswith("__")) == set(ours.keys())
print("prior file matches result.json priors")
